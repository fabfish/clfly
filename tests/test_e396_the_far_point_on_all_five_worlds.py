"""`e396` carries all five of the card's worlds to the far point, so the tests pin both faces of the five claims, the
refusal when a run or the near readings are absent, and the live contrast between the two ends.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e396_the_far_point_on_all_five_worlds as e396

PLACED_VALUES = {"loop_cue_at": 0, "loop_world_leak": 0.35, "readout_from_world": True, "loop_world_dims": 8,
                 "closed_loop": True, "loop_world_modes": 0, "loop_world_nonlinear": False, "repeats": 20,
                 "circuit_size": 300, "readout_size": 32, "basis": "cell_class", "seed0": 0,
                 "task_names": ["loop_odour_identity", "loop_heading", "loop_odour_input"],
                 "task_readout_widths": [8], "iters": 500, "lr": 0.003, "batch": 32}


def _settings(seed):
    return {**PLACED_VALUES, "loop_seed": seed, "cue_sha1": f"c{seed}", "feedback_sha1": f"f{seed}", "n_cue": 12,
            "action_sha1": f"a{seed}", "n_action": 8, "drive_from_cue": False, "loop_drive_from_cue": False,
            "world_drive_sha1": f"d{seed}", "world_read_sha1": f"r{seed}", "world_coupling_sha1": f"k{seed}"}


#: the corpus's shape: five worlds, the connectome reading 0.6875 on each, and one of them recovering
GOOD_INIT = {"card": 0.6875, "1": 0.6875, "2": 0.6875, "3": 0.6875, "4": 0.6875}
GOOD_BODY = {"card": 0.7729, "1": 0.4854, "2": 0.4677, "3": 0.55, "4": 0.50}
GOOD_NEAR = {"card": 0.5740, "1": 0.5208, "2": 0.5010, "3": 0.5219, "4": 0.4833}


def _doc(initial=GOOD_INIT, body=GOOD_BODY, near=GOOD_NEAR, settings=None, ok=True, reason="absent"):
    if not ok:
        #: `reading` refuses the whole unit when a run, its weights or the near readings are absent
        return {"ok": False, "worlds": {}, "settings": {}, "near": None, "reason": reason}
    names = list(initial)
    settings = settings if settings is not None else {n: _settings(0 if n == "card" else int(n)) for n in names}
    worlds = {n: {"artifact": f"{n}.json", "initial_task_0": initial[n], "body_task_0": body[n],
                  "head_task_0": 0.75} for n in names}
    initials = list(initial.values())
    bodies = list(body.values())
    nears = list(near.values())
    draws = {f: sorted({str(s.get(f)) for s in settings.values()}) for f in e396.WORLD_FIELDS}
    return {"ok": True, "worlds": worlds, "settings": settings,
            "near": {"artifact": "e393.json", "readings": dict(near)},
            "spread": {"initial": max(initials) - min(initials), "body": max(bodies) - min(bodies),
                       "near": max(nears) - min(nears)},
            "draws": draws, "arm": e396.NAIVE, "reps": e396.REPS}


def _judge(**kw):
    return {row["id"]: row for row in e396.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: five worlds, one of them recovering: the shape e395 found on three and this unit completes on five
    j = _judge()
    for cid in ("Q1", "Q2", "Q3", "Q4", "Q5"):
        assert j[cid]["verdict"].startswith("MET"), (cid, j[cid])

    # Q1: a placed field moved between two runs, and a field in neither list
    moved = {n: _settings(0 if n == "card" else int(n)) for n in GOOD_INIT}
    moved["3"] = {**moved["3"], "loop_world_leak": 1.0}
    assert _judge(settings=moved)["Q1"]["verdict"].startswith("FALSIFIER")
    extra = {n: {**_settings(0 if n == "card" else int(n)), "mystery": 1} for n in GOOD_INIT}
    assert _judge(settings=extra)["Q1"]["verdict"].startswith("FALSIFIER")

    # Q2: two worlds sharing a fingerprint
    twin = {n: _settings(0 if n == "card" else int(n)) for n in GOOD_INIT}
    twin["4"] = {**twin["4"], "world_read_sha1": twin["3"]["world_read_sha1"]}
    assert _judge(settings=twin)["Q2"]["verdict"].startswith("FALSIFIER")

    # Q3: a substrate reading that moves with the world, and one between the bars
    assert _judge(initial={**GOOD_INIT, "3": 0.50})["Q3"]["verdict"].startswith("FALSIFIER")
    assert _judge(initial={**GOOD_INIT, "3": 0.58})["Q3"]["verdict"].startswith("NULL")

    # Q4: three of the five worlds ending above their own connectome reading, and all five
    assert _judge(body={**GOOD_BODY, "3": 0.80})["Q4"]["verdict"].startswith("MET")
    assert _judge(body={**GOOD_BODY, "3": 0.80, "4": 0.78})["Q4"]["verdict"].startswith("FALSIFIER")
    assert _judge(body={n: 0.78 for n in GOOD_BODY})["Q4"]["verdict"].startswith("FALSIFIER")

    # Q5: a far end that spreads no more than the near one, and one between the bars
    assert _judge(body={n: 0.55 for n in GOOD_BODY})["Q5"]["verdict"].startswith("FALSIFIER")
    assert _judge(body={**GOOD_BODY, "1": 0.60, "2": 0.60, "3": 0.60, "4": 0.60})["Q5"]["verdict"].startswith("NULL")

    #: a run, its weights or the near readings absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e396.judge(_doc(ok=False)))


def test_the_two_lists_cover_the_card_and_the_draw():
    #: the placed list carries the field `e393` omitted, and the drawn list the environment's own draw
    assert "loop_cue_at" in e396.PLACED, "the field e393 fired on"
    assert not set(e396.PLACED) & set(e396.DRAWN), set(e396.PLACED) & set(e396.DRAWN)
    for k in ("world_drive_sha1", "cue_sha1", "action_sha1", "loop_seed"):
        assert k in e396.DRAWN, k
    #: every field the module reads off a run is in one of them, so the closure claim has something to close over
    keys = set(_settings(1))
    assert keys <= set(e396.PLACED) | set(e396.DRAWN), sorted(keys - set(e396.PLACED) - set(e396.DRAWN))


def test_the_live_contrast_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e396_the_far_point_on_all_five_worlds.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e396.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e396.judge(d)}
    #: the configuration and the five worlds are structural facts, so those claims are read off the artifact
    for cid in ("Q1", "Q2"):
        assert verdicts[cid].split(" -- ")[0] in ("MET", "FALSIFIER FIRED"), verdicts[cid]
    assert sorted(d["worlds"]) == ["1", "2", "3", "4", "card"], sorted(d["worlds"])
    assert all(len(v) == 5 for v in d["draws"].values()), d["draws"]
    #: the near end comes from `e393`'s artifact, so the contrast is between two readings and not against constants
    assert d["near"]["artifact"].startswith("e393"), d["near"]
    assert sorted(d["near"]["readings"]) == sorted(d["worlds"]), (d["near"], sorted(d["worlds"]))
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
