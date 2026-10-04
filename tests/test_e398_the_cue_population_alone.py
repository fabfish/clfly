"""`e398` moves the cue population alone and trains the two cue draws a pre-registered geometric criterion selects,
so the tests pin both faces of the five claims, the refusal when the search or a run is absent, and the live result.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e398_the_cue_population_alone as e398

CARD_DRAW = {"cue_sha1": "card-cue", "action_sha1": "A", "feedback_sha1": "F", "world_drive_sha1": "D",
             "world_read_sha1": "R", "world_coupling_sha1": "K"}


def _draw(cue, driven=None):
    return {"cue_sha1": cue, **{f: (driven or {}).get(f, CARD_DRAW[f]) for f in e398.DRIVEN}}


def _world(initial, near_body, far_body, near_head=0.25, far_head=0.75, cue="x"):
    return {"20": {"artifact": "n.json", "iters": 20, "initial_task_0": initial, "body_task_0": near_body,
                   "head_task_0": near_head, "draw": _draw(cue)},
            "500": {"artifact": "f.json", "iters": 500, "initial_task_0": initial, "body_task_0": far_body,
                    "head_task_0": far_head, "draw": _draw(cue)}}


def _search(n=16, twos=(3, 9, 14)):
    return {str(s): {"cue_to_action": 2 if s in twos else 1, "cue_sha1": f"c{s}"} for s in range(1, n + 1)}


#: the corpus's shape: seed 3 is the first two-hop draw, seed 1 the first one-hop, and the outcome follows
GOOD_WORLDS = {"card": _world(0.6875, 0.5740, 0.7729, cue="card-cue"),
               "cue2": _world(0.6875, 0.5208, 0.8030, cue="c3"),
               "cue1": _world(0.6875, 0.5250, 0.4500, cue="c1")}


def _doc(search=None, chosen=None, worlds=None, card_draw=None, ok=True, reason="absent"):
    if not ok:
        #: `reading` refuses the whole unit when the search or a run is absent
        return {"ok": False, "worlds": {}, "search": {}, "chosen": {}, "spread": {}, "reason": reason}
    search = search if search is not None else _search()
    chosen = chosen if chosen is not None else {"2": 3, "1": 1}
    worlds = worlds if worlds is not None else {k: v for k, v in GOOD_WORLDS.items()}
    initials = [w["20"]["initial_task_0"] for w in worlds.values()]
    return {"ok": True, "circuit": "mb+cx+al@n952", "edges": 20079,
            "card_draw": card_draw if card_draw is not None else dict(CARD_DRAW),
            "search": search, "chosen": chosen, "worlds": worlds,
            "spread": {"initial": max(initials) - min(initials)}}


def _judge(**kw):
    return {row["id"]: row for row in e398.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the first two-hop cue draw recovers and the first one-hop draw does not, while their near readings agree
    j = _judge()
    for cid in ("T1", "T2", "T3", "T4", "T5"):
        assert j[cid]["verdict"].startswith("MET"), (cid, j[cid])

    # T1: a driven field that moved with the cue, and a cue that is the card's
    moved = {k: v for k, v in GOOD_WORLDS.items()}
    moved["cue2"] = _world(0.6875, 0.5208, 0.8030, cue="c3")
    moved["cue2"]["20"]["draw"] = _draw("c3", {"world_read_sha1": "OTHER"})
    assert _judge(worlds=moved)["T1"]["verdict"].startswith("FALSIFIER")
    same = {k: v for k, v in GOOD_WORLDS.items()}
    same["cue1"] = _world(0.6875, 0.5250, 0.4500, cue="card-cue")
    assert _judge(worlds=same)["T1"]["verdict"].startswith("FALSIFIER")

    # T2: a search with only one of the two geometries, and one under the bound
    assert _judge(search=_search(twos=()))["T2"]["verdict"].startswith("FALSIFIER")
    assert _judge(search={str(s): {"cue_to_action": 2 if s == 3 else 1, "cue_sha1": f"c{s}"} for s in range(1, 5)})[
        "T2"]["verdict"].startswith("FALSIFIER")
    #: and a search where the chosen seed is not the first of its class
    assert _judge(chosen={"2": 9, "1": 1})["T2"]["verdict"].startswith("FALSIFIER")

    # T3: both draws on the same side of the bar
    assert _judge(worlds={**GOOD_WORLDS, "cue1": _world(0.6875, 0.5250, 0.7000, cue="c1")})["T3"][
        "verdict"].startswith("FALSIFIER")
    assert _judge(worlds={**GOOD_WORLDS, "cue2": _world(0.6875, 0.5208, 0.6900, cue="c3")})["T3"][
        "verdict"].startswith("FALSIFIER")

    # T4: an initial reading that moves, and one between the bars
    assert _judge(worlds={**GOOD_WORLDS, "cue1": _world(0.55, 0.5250, 0.4500, cue="c1")})["T4"][
        "verdict"].startswith("FALSIFIER")
    assert _judge(worlds={**GOOD_WORLDS, "cue1": _world(0.62, 0.5250, 0.4500, cue="c1")})["T4"][
        "verdict"].startswith("NULL")

    # T5: a near point that separates them, and a far point that does not
    assert _judge(worlds={**GOOD_WORLDS, "cue1": _world(0.6875, 0.4000, 0.4500, cue="c1")})["T5"][
        "verdict"].startswith("FALSIFIER")
    assert _judge(worlds={**GOOD_WORLDS, "cue1": _world(0.6875, 0.5250, 0.7600, cue="c1")})["T5"][
        "verdict"].startswith("FALSIFIER")

    #: the search or a run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e398.judge(_doc(ok=False)))


def test_the_selection_is_the_first_of_each_class():
    #: the criterion is geometric and registered: the first draw at each distance, not the best-performing one
    assert e398.WANT == (2, 1), e398.WANT
    assert e398.MIN_SEARCH >= 8, e398.MIN_SEARCH
    search = _search()
    first2 = sorted([int(s) for s in search if search[s]["cue_to_action"] == 2])[0]
    first1 = sorted([int(s) for s in search if search[s]["cue_to_action"] == 1])[0]
    assert (first2, first1) == (3, 1), (first2, first1)
    #: and the engine parameters are the runs', so an environment here is the one a run had
    for k, v in (("n_symbols", 12), ("tau", e398.TAU), ("world_leak", 0.35), ("world_dims", 8),
                 ("world_coupled", True), ("cue_at", 0), ("drive_from_cue", False)):
        assert e398.ENGINE[k] == v, (k, e398.ENGINE[k])


def test_the_live_result_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e398_the_cue_population_alone.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e398.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e398.judge(d)}
    #: the environment control and the search are structural, so those two are demanded
    assert verdicts["T1"].startswith("MET") and verdicts["T2"].startswith("MET"), verdicts
    assert sorted(d["worlds"]) == ["card", "cue1", "cue2"], sorted(d["worlds"])
    #: the search is at least as wide as the bound, and both geometries are in it
    assert len(d["search"]) >= e398.MIN_SEARCH, len(d["search"])
    assert {v["cue_to_action"] for v in d["search"].values()} == {1, 2}, d["search"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
