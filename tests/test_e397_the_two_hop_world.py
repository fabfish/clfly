"""`e397` measures the cue's path to the action population on all five of the card's worlds, so the tests pin both
faces of the five claims, the refusal when the geometry or the readings are absent, and the live separation.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e397_the_two_hop_world as e397


def _world(seed, d, initial, far, feedback=1):
    return {"seed": seed, "cue_to_action": d, "cue_to_feedback": feedback, "n_cue": 12, "n_action": 8,
            "initial_task_0": initial, "far_task_0": far}


#: the corpus's shape: the card's world is two hops from the action population and the only one that recovers
GOOD_D = {"card": 2, "1": 1, "2": 1, "3": 1, "4": 1}
GOOD_INIT = {n: 0.6875 for n in GOOD_D}
GOOD_FAR = {"card": 0.7729, "1": 0.4854, "2": 0.4677, "3": 0.5219, "4": 0.4385}


def _doc(ds=GOOD_D, initial=GOOD_INIT, far=GOOD_FAR, agrees=True, ok=True, reason="absent"):
    if not ok:
        #: `reading` refuses the whole unit when the geometry or the readings are not on disk
        return {"ok": False, "worlds": {}, "draws": {}, "spread": {}, "reason": reason}
    worlds = {n: _world(0 if n == "card" else int(n), ds[n], initial[n], far[n]) for n in ds}
    draws = {n: {"seed": 0 if n == "card" else int(n), "record": f"{n}.json",
                 "fingerprints": {f: "x" for f in e397.FINGERPRINTS},
                 "recorded": {f: ("x" if agrees else "y") for f in e397.FINGERPRINTS}, "agrees": agrees}
             for n in ds}
    initials = list(initial.values())
    fars = list(far.values())
    return {"ok": True, "circuit": "mb+cx+al@n952", "edges": 20079, "worlds": worlds, "draws": draws,
            "spread": {"initial": max(initials) - min(initials), "far": max(fars) - min(fars)}}


def _judge(**kw):
    return {row["id"]: row for row in e397.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the card's world is two hops and recovers; the four one-hop worlds lose the cue by a fifth of the reading
    j = _judge()
    for cid in ("R1", "R2", "R3", "R4", "R5"):
        assert j[cid]["verdict"].startswith("MET"), (cid, j[cid])

    # R1: a fingerprint that does not agree with its run's
    assert _judge(agrees=False)["R1"]["verdict"].startswith("FALSIFIER")

    # R2: the card's world measured at one hop, and at three
    assert _judge(ds={**GOOD_D, "card": 1})["R2"]["verdict"].startswith("FALSIFIER")
    assert _judge(ds={**GOOD_D, "card": 3})["R2"]["verdict"].startswith("FALSIFIER")

    # R3: every world the same distance
    assert _judge(ds={n: 2 for n in GOOD_D})["R3"]["verdict"].startswith("FALSIFIER")

    # R4: a loser at the card's distance, and a loser farther than it
    assert _judge(ds={**GOOD_D, "3": 2})["R4"]["verdict"].startswith("FALSIFIER")
    assert _judge(ds={**GOOD_D, "3": 3})["R4"]["verdict"].startswith("FALSIFIER")
    #: and if the card's world stops recovering, the claim is about the losers that remain
    assert _judge(far={**GOOD_FAR, "card": 0.40})["R4"]["verdict"].startswith("MET")
    assert _judge(far={n: 0.40 for n in GOOD_FAR})["R4"]["verdict"].startswith("MET")

    # R5: a draw already visible before training, and one between the bars
    assert _judge(initial={**GOOD_INIT, "3": 0.40, "4": 0.30})["R5"]["verdict"].startswith("FALSIFIER")
    assert _judge(initial={**GOOD_INIT, "3": 0.66, "4": 0.62})["R5"]["verdict"].startswith("NULL")

    #: the geometry or the readings absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e397.judge(_doc(ok=False)))


def test_the_engine_parameters_are_the_runs():
    #: an environment here is the one a run had only if every parameter the draw consumes is the run's
    e = e397.ENGINE
    for k, v in (("n_symbols", 12), ("tau", e397.TAU), ("scale", 1.0), ("gain", 1.0), ("noise", 1.0),
                 ("world_modes", 0), ("world_leak", 0.35), ("world_dims", 8), ("world_coupled", True),
                 ("cue_at", 0), ("drive_from_cue", False)):
        assert e[k] == v, (k, e[k])
    #: and the five worlds are five distinct seeds, with the card's the one its run defaulted to
    seeds = {n: spec["seed"] for n, spec in e397.WORLDS.items()}
    assert seeds == {"card": 0, "1": 1, "2": 2, "3": 3, "4": 4}, seeds


def test_the_live_separation_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e397_the_two_hop_world.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e397.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e397.judge(d)}
    #: the control is structural -- the environments reproduce the runs' own fingerprints -- so R1 is demanded
    assert verdicts["R1"].startswith("MET"), verdicts["R1"]
    assert sorted(d["worlds"]) == ["1", "2", "3", "4", "card"], sorted(d["worlds"])
    #: and every world's distance is an integer hop count, or the walk past the cap
    for w in d["worlds"].values():
        assert w["cue_to_action"] is None or isinstance(w["cue_to_action"], int), w
    #: the readings come from `e396`'s artifact rather than from constants
    assert d["spread"]["far"] > d["spread"]["initial"], d["spread"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
