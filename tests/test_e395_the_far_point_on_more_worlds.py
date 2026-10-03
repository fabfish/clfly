"""`e395` redraws the card's world at its far point, 500 updates, on two of the worlds `e393` drew at the near one,
so the tests pin both faces of the five claims, the refusal when a run or its weights is absent, and the live
replication of the recovery.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e395_the_far_point_on_more_worlds as e395

PLACED_VALUES = {"loop_cue_at": 0, "loop_world_leak": 0.35, "readout_from_world": True, "loop_world_dims": 8,
                 "closed_loop": True, "loop_world_modes": 0, "loop_world_nonlinear": False, "repeats": 20,
                 "circuit_size": 300, "readout_size": 32, "basis": "cell_class", "seed0": 0,
                 "task_names": ["loop_odour_identity", "loop_heading", "loop_odour_input"],
                 "task_readout_widths": [8], "iters": 500, "lr": 0.003, "batch": 32}


def _settings(seed):
    return {**PLACED_VALUES, "loop_seed": seed, "cue_sha1": f"c{seed}", "feedback_sha1": f"f{seed}", "n_cue": 12,
            "action_sha1": f"a{seed}", "n_action": 8, "drive_from_cue": False, "loop_drive_from_cue": False,
            "world_drive_sha1": f"d{seed}", "world_read_sha1": f"r{seed}", "world_coupling_sha1": f"k{seed}"}


#: the corpus's shape: the connectome reads 0.6875 on every world and 500 updates leave the body above it
GOOD_INIT = {"card": 0.6875, "1": 0.6875, "2": 0.6875}
GOOD_BODY = {"card": 0.7729, "1": 0.75, "2": 0.80}


def _doc(initial=GOOD_INIT, body=GOOD_BODY, settings=None, ok=True, reason="absent"):
    if not ok:
        #: `reading` refuses the whole unit when a run's weights are absent
        return {"ok": False, "worlds": {}, "settings": {}, "reason": reason}
    settings = settings if settings is not None else {n: _settings(0 if n == "card" else int(n))
                                                      for n in ("card", "1", "2")}
    worlds = {n: {"artifact": f"{n}.json", "iters": 500, "repeats": 20, "initial_task_0": initial[n],
                  "body_task_0": body[n], "head_task_0": 0.75} for n in initial}
    initials = list(initial.values())
    bodies = list(body.values())
    draws = {f: sorted({str(s.get(f)) for s in settings.values()}) for f in e395.WORLD_FIELDS}
    return {"ok": True, "worlds": worlds, "settings": settings,
            "spread": {"initial": max(initials) - min(initials), "body": max(bodies) - min(bodies)},
            "draws": draws, "arm": e395.NAIVE, "reps": e395.REPS}


def _judge(**kw):
    return {row["id"]: row for row in e395.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: two redraws whose readings and whose gain over the connectome's own both land near the card's
    j = _judge()
    for cid in ("P1", "P2", "P3", "P4", "P5"):
        assert j[cid]["verdict"].startswith("MET"), (cid, j[cid])

    # P1: a placed field moved between two runs, and a field in neither list
    moved = {n: _settings(0 if n == "card" else int(n)) for n in ("card", "1", "2")}
    moved["1"] = {**moved["1"], "loop_world_leak": 1.0}
    assert _judge(settings=moved)["P1"]["verdict"].startswith("FALSIFIER")
    extra = {n: {**_settings(0 if n == "card" else int(n)), "mystery": 1} for n in ("card", "1", "2")}
    assert _judge(settings=extra)["P1"]["verdict"].startswith("FALSIFIER")

    # P2: a redraw that reproduces the card's world, and two redraws sharing one
    same = {n: _settings(0 if n == "card" else int(n)) for n in ("card", "1", "2")}
    same["2"] = {**same["2"], "world_drive_sha1": same["card"]["world_drive_sha1"]}
    assert _judge(settings=same)["P2"]["verdict"].startswith("FALSIFIER")
    twin = {n: _settings(0 if n == "card" else int(n)) for n in ("card", "1", "2")}
    twin["2"] = {**twin["2"], "world_coupling_sha1": twin["1"]["world_coupling_sha1"]}
    assert _judge(settings=twin)["P2"]["verdict"].startswith("FALSIFIER")

    # P3: a substrate reading that moves with the world, and one between the bars
    assert _judge(initial={"card": 0.6875, "1": 0.68, "2": 0.50})["P3"]["verdict"].startswith("FALSIFIER")
    assert _judge(initial={"card": 0.6875, "1": 0.68, "2": 0.58})["P3"]["verdict"].startswith("NULL")

    # P4: a far point that spreads with the world, and one between the bars
    assert _judge(body={"card": 0.7729, "1": 0.75, "2": 0.40})["P4"]["verdict"].startswith("FALSIFIER")
    assert _judge(body={"card": 0.7729, "1": 0.75, "2": 0.66})["P4"]["verdict"].startswith("NULL")

    # P5: a world where 500 updates leave the body where the connectome left it
    assert _judge(body={"card": 0.7729, "1": 0.69, "2": 0.80})["P5"]["verdict"].startswith("FALSIFIER")

    #: a run or its weights absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e395.judge(_doc(ok=False)))


def test_the_two_lists_cover_the_card_and_the_draw():
    #: the placed list carries the field `e393`'s omitted, and the drawn list the environment's own draw
    assert "loop_cue_at" in e395.PLACED, "the field e393 fired on"
    assert not set(e395.PLACED) & set(e395.DRAWN), set(e395.PLACED) & set(e395.DRAWN)
    for k in ("world_drive_sha1", "cue_sha1", "action_sha1", "loop_seed"):
        assert k in e395.DRAWN, k
    #: every field the module reads off a run is in one of them, so the closure claim has something to close over
    keys = set(_settings(1))
    assert keys <= set(e395.PLACED) | set(e395.DRAWN), sorted(keys - set(e395.PLACED) - set(e395.DRAWN))


def test_the_live_replication_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e395_the_far_point_on_more_worlds.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e395.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e395.judge(d)}
    #: the configuration and the two worlds are structural facts, so those claims are read off the artifact
    for cid in ("P1", "P2"):
        assert verdicts[cid].split(" -- ")[0] in ("MET", "FALSIFIER FIRED"), verdicts[cid]
    assert sorted(d["worlds"]) == ["1", "2", "card"], sorted(d["worlds"])
    assert all(len(v) == 3 for v in d["draws"].values()), d["draws"]
    #: the card's own run is one of the three, so the comparison is against an artifact and not a constant
    assert d["worlds"]["card"]["artifact"].startswith("e380"), d["worlds"]["card"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
