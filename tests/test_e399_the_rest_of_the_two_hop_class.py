"""`e399` runs the other two cue draws at distance 2 to the far point, so the tests pin both faces of the five
claims, the refusal when the search or a run is absent, and the live class the unit measures in full.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e399_the_rest_of_the_two_hop_class as e399

CARD_DRAW = {"cue_sha1": "card-cue", "action_sha1": "A", "feedback_sha1": "F", "world_drive_sha1": "D",
             "world_read_sha1": "R", "world_coupling_sha1": "K"}


def _draw(cue, driven=None):
    return {"cue_sha1": cue, **{f: (driven or {}).get(f, CARD_DRAW[f]) for f in e399.DRIVEN}}


def _world(cueseed, initial, body, head=0.8, cue=None, driven=None):
    return {"artifact": "r.json", "cueseed": cueseed, "iters": 500, "initial_task_0": initial,
            "body_task_0": body, "head_task_0": head,
            "draw": _draw(cue if cue is not None else ("card-cue" if cueseed is None else f"c{cueseed}"), driven)}


def _search(n=16, twos=(3, 9, 14)):
    return {str(s): {"cue_to_action": 2 if s in twos else 1, "cue_sha1": f"c{s}"} for s in range(1, n + 1)}


#: the corpus's shape: three distance-2 cue draws and only the card's world recovers
GOOD_WORLDS = {"card": _world(None, 0.6875, 0.7729, cue="card-cue"),
               "cue3": _world(3, 0.6875, 0.5240),
               "cue9": _world(9, 0.6875, 0.5000),
               "cue14": _world(14, 0.6875, 0.5100),
               "cue1": _world(1, 0.6875, 0.5062)}


def _doc(search=None, worlds=None, card_draw=None, ok=True, reason="absent"):
    if not ok:
        #: `reading` refuses the whole unit when the search or a run is absent
        return {"ok": False, "worlds": {}, "search": {}, "two_hop": [], "spread": {}, "reason": reason}
    search = search if search is not None else _search()
    worlds = worlds if worlds is not None else {k: v for k, v in GOOD_WORLDS.items()}
    initials = [w["initial_task_0"] for w in worlds.values()]
    return {"ok": True, "circuit": "mb+cx+al@n952", "edges": 20079,
            "card_draw": card_draw if card_draw is not None else dict(CARD_DRAW),
            "search": search,
            "two_hop": sorted(int(s) for s in search if search[s]["cue_to_action"] == e399.TWO_HOP),
            "worlds": worlds, "spread": {"initial": max(initials) - min(initials)}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e399.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: three distance-2 cue draws, one of them recovering, and two distance-1 worlds that do not
    j = _judge()
    for cid in ("V1", "V2", "V3", "V4", "V5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # V1: a driven field that moved with the cue, and a cue that is the card's
    for name in ("cue9", "cue14"):
        moved = {k: v for k, v in GOOD_WORLDS.items()}
        moved[name] = _world(int(name[3:]), 0.6875, 0.5000, driven={"world_read_sha1": "OTHER"})
        assert _judge(worlds=moved)["V1"].startswith("FALSIFIER")
    same = {k: v for k, v in GOOD_WORLDS.items()}
    same["cue9"] = _world(9, 0.6875, 0.5000, cue="card-cue")
    assert _judge(worlds=same)["V1"].startswith("FALSIFIER")

    # V2: a search whose distance-2 set is not the three, a search under the bound, and a new run at one hop
    assert _judge(search=_search(twos=(3, 9)))["V2"].startswith("FALSIFIER")
    assert _judge(search=_search(n=4, twos=(3,)))["V2"].startswith("FALSIFIER")
    wrong = {k: v for k, v in GOOD_WORLDS.items()}
    wrong["cue14"] = {**wrong["cue14"], "cueseed": 4}
    assert _judge(worlds=wrong)["V2"].startswith("FALSIFIER")

    # V3: one new draw that recovers, and one that lands exactly on the bar
    assert _judge(worlds={**GOOD_WORLDS, "cue9": _world(9, 0.6875, 0.7000)})["V3"].startswith("FALSIFIER")
    assert _judge(worlds={**GOOD_WORLDS, "cue14": _world(14, 0.6875, 0.6500)})["V3"].startswith("FALSIFIER")

    # V4: an initial reading that moves, and one between the bars
    assert _judge(worlds={**GOOD_WORLDS, "cue9": _world(9, 0.50, 0.4000)})["V4"].startswith("FALSIFIER")
    assert _judge(worlds={**GOOD_WORLDS, "cue9": _world(9, 0.60, 0.5000)})["V4"].startswith("NULL")

    # V5: two of the four distance-2 draws recovering, and all four
    assert _judge(worlds={**GOOD_WORLDS, "cue9": _world(9, 0.6875, 0.8000)})["V5"].startswith("FALSIFIER")
    assert _judge(worlds={n: _world(w["cueseed"], 0.6875, 0.78) for n, w in GOOD_WORLDS.items()})["V5"].startswith(
        "FALSIFIER")

    #: the search or a run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e399.judge(_doc(ok=False)))


def test_the_class_is_the_searchs_and_the_two_new_seeds_are_registered():
    #: the criterion is the distance and the two new draws are the rest of that class, registered as constants
    assert e399.TWO_HOP == 2 and e399.NEW_SEEDS == (9, 14), (e399.TWO_HOP, e399.NEW_SEEDS)
    search = _search()
    twos = sorted(int(s) for s in search if search[s]["cue_to_action"] == e399.TWO_HOP)
    assert twos == [3, 9, 14], twos
    assert set(e399.NEW_SEEDS) <= set(twos), (e399.NEW_SEEDS, twos)
    #: and the five trained worlds are the card's, the two `e398` ran and the two this unit adds
    assert set(e399.WORLDS) == {"card", "cue3", "cue9", "cue14", "cue1"}, sorted(e399.WORLDS)
    for k, v in (("n_symbols", 12), ("tau", e399.TAU), ("world_leak", 0.35), ("world_dims", 8),
                 ("world_coupled", True), ("cue_at", 0), ("drive_from_cue", False)):
        assert e399.ENGINE[k] == v, (k, e399.ENGINE[k])


def test_the_live_class_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e399_the_rest_of_the_two_hop_class.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e399.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e399.judge(d)}
    #: the environment control and the class's membership are structural, so those two are demanded
    assert verdicts["V1"].startswith("MET") and verdicts["V2"].startswith("MET"), verdicts
    assert sorted(d["worlds"]) == ["card", "cue1", "cue14", "cue3", "cue9"], sorted(d["worlds"])
    #: the search is at least as wide as the bound and carries both geometries
    assert len(d["search"]) >= e399.MIN_SEARCH, len(d["search"])
    assert {v["cue_to_action"] for v in d["search"].values()} == {1, 2}, d["search"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
