"""`e401` takes the heaviest untrained cue draw of a 32-draw search and runs it at both ends, so the tests pin both
faces of the five claims, the selection's own rule, and the live lead.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e401_the_heaviest_untrained_draw as e401


def _search(n=32, weight=80.0, chosen=6):
    out = {}
    for s in range(1, n + 1):
        out[str(s)] = {"path_weight": weight + (5.0 if s == chosen else 0.0) + 0.01 * s,
                       "cue_to_action": 1 if s % 2 else 2}
    return out


def _world(seed, gain, initial=0.6875, head=0.8, body=None):
    return {"cueseed": seed, "artifact": "r.json", "initial_task_0": initial,
            "body_task_0": initial + gain if body is None else body, "gain": gain, "head_task_0": head}


#: the corpus's shape: five worlds from `e398`/`e399` and the heaviest untrained draw the unit runs
GOOD_WORLDS = {"card": _world(None, 0.0854), "cue3": _world(3, -0.1635), "cue9": _world(9, -0.2250),
               "cue14": _world(14, -0.1479), "cue1": _world(1, -0.1813), "chosen": _world(6, 0.0700)}


def _doc(search=None, worlds=None, chosen=6, correlation=None, ok=True, reason="absent"):
    if not ok:
        #: `reading` refuses the whole unit when the search or a run is absent
        return {"ok": False, "worlds": {}, "search": {}, "chosen_seed": None, "reason": reason}
    search = search if search is not None else _search(chosen=chosen)
    worlds = worlds if worlds is not None else {k: v for k, v in GOOD_WORLDS.items()}
    order = sorted(worlds, key=lambda n: worlds[n]["gain"])
    weights = {}
    for n in order:
        seed = worlds[n]["cueseed"]
        weights[n] = (e401.CARD_WEIGHT if seed is None
                      else search.get(str(seed), {}).get("path_weight", 0.0))
    #: the correlation is the unit's own reading of the artifact; the mock supplies the value the corpus has
    correlation = 0.85 if correlation is None else correlation
    initials = [v["initial_task_0"] for v in worlds.values()]
    return {"ok": True, "circuit": "mb+cx+al@n952", "edges": 20079, "search": search, "chosen_seed": chosen,
            "worlds": worlds, "order": order, "weight_values": weights, "correlation": correlation,
            "spread": {"initial": max(initials) - min(initials)}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e401.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the heaviest untrained draw, heavier than the card's world, and its gain positive
    j = _judge()
    for cid in ("Y1", "Y2", "Y3", "Y4", "Y5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # Y1: another draw heavier than the chosen one, and a search under the bound
    heavier = _search()
    heavier["20"] = {"path_weight": 999.0, "cue_to_action": 1}
    assert _judge(search=heavier)["Y1"].startswith("FALSIFIER")
    assert _judge(search=_search(n=8))["Y1"].startswith("FALSIFIER")

    # Y2: a chosen draw under the card's weight
    light = _search(weight=1.0)
    assert _judge(search=light)["Y2"].startswith("FALSIFIER")

    # Y3: a chosen draw that does not gain, and one exactly at zero
    assert _judge(worlds={**GOOD_WORLDS, "chosen": _world(6, -0.02)})["Y3"].startswith("FALSIFIER")
    assert _judge(worlds={**GOOD_WORLDS, "chosen": _world(6, 0.0)})["Y3"].startswith("FALSIFIER")
    assert _judge(worlds={**GOOD_WORLDS, "chosen": _world(6, 0.02)})["Y3"].startswith("FALSIFIER")

    # Y4: an initial reading that moves, and one between the bars
    assert _judge(worlds={**GOOD_WORLDS, "chosen": _world(6, 0.0700, initial=0.50)})["Y4"].startswith("FALSIFIER")
    assert _judge(worlds={**GOOD_WORLDS, "chosen": _world(6, 0.0700, initial=0.60)})["Y4"].startswith("NULL")

    # Y5: a correlation that breaks the ordering, and one between the bars
    assert _judge(correlation=-0.4)["Y5"].startswith("FALSIFIER")
    assert _judge(correlation=0.6)["Y5"].startswith("NULL")

    #: the search or a run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e401.judge(_doc(ok=False)))


def test_the_selection_rule_is_registered_and_excludes_the_trained():
    #: the criterion is the heaviest draw outside the four `e398`/`e399` trained, and the bound is registered
    assert set(e401.TRAINED) == {1, 3, 9, 14}, e401.TRAINED
    assert e401.MIN_SEARCH >= 16, e401.MIN_SEARCH
    assert e401.GAIN == 0.05 and e401.KEEPS == 0.7 and e401.BREAKS == 0.5
    #: and the search is wider than the class `e398` opened, so the heaviest draw is a fresh population
    assert len(e401.SEARCH) >= 32, len(e401.SEARCH)
    assert not (set(e401.TRAINED) & set()) and len(set(e401.SEARCH) & set(e401.TRAINED)) == 4, "the four are inside"


def test_the_live_lead_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e401_the_heaviest_untrained_draw.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e401.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e401.judge(d)}
    #: the selection and the published readings are structural facts
    assert verdicts["Y1"].startswith("MET") and verdicts["Y4"].startswith("MET"), verdicts
    assert sorted(d["worlds"]) == ["card", "chosen", "cue1", "cue14", "cue3", "cue9"], sorted(d["worlds"])
    assert len(d["search"]) >= e401.MIN_SEARCH, len(d["search"])
    #: the chosen seed is the heaviest one outside the trained four, recomputed from the artifact's own search
    pool = {s: v for s, v in d["search"].items() if int(s) not in e401.TRAINED}
    assert int(max(pool, key=lambda s: pool[s]["path_weight"])) == d["chosen_seed"], d["chosen_seed"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
