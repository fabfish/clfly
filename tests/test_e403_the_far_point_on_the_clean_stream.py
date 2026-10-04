"""`e403` puts the stream axis at the far point, so the tests pin both faces of the five claims, the two lists, the
refusal when the five worlds' span is absent, and the live contrast with the world axis.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e403_the_far_point_on_the_clean_stream as e403

DRAWN_VALUES = {"readout_subset": "59926518137c", "cue_sha1": "3985fc4e3252", "feedback_sha1": "77963b921bc3",
                "action_sha1": "f379863d1cf4", "world_drive_sha1": "3d88340cf387",
                "world_read_sha1": "3a7ba76b3619", "world_coupling_sha1": "5326f4a0edb4"}
PINNED_VALUES = {"circuit": "mb+cx+al@n952", "circuit_size": 300, "readout_size": 32, "basis": "cell_class",
                 "support": 80, "task_names": ["loop_odour_identity", "loop_heading", "loop_odour_input"],
                 "task_readout_widths": [8], "loop_cue_at": 0, "loop_world_dims": 8, "loop_world_leak": 0.35,
                 "loop_world_modes": 0, "loop_world_nonlinear": False, "readout_from_world": True,
                 "closed_loop": True, "lr": 0.003, "batch": 32, "iters": 500, "repeats": 20, "n_cue": 12,
                 "n_action": 8, "drive_from_cue": False, "loop_drive_from_cue": False, "cue_seed": None}


def _settings(seed0, drawn=None):
    explicit = 0 if seed0 else None
    return {**PINNED_VALUES, **DRAWN_VALUES, **(drawn or {}), "seed0": seed0, "readout_seed": explicit,
            "loop_seed": explicit}


#: the corpus's shape: the card's world recovers and the two clean streams do too, tightly
GOOD_INIT = {"card": 0.6875, "1": 0.6875, "2": 0.6875}
GOOD_BODY = {"card": 0.7729, "1": 0.8000, "2": 0.7800}


def _doc(initial=GOOD_INIT, body=GOOD_BODY, settings=None, worlds_span=0.3344, ok=True, reason="absent"):
    if not ok:
        #: `reading` refuses the whole unit when a run or its weights is absent
        return {"ok": False, "streams": {}, "settings": {}, "worlds_span": None, "reason": reason}
    settings = settings if settings is not None else {n: _settings(0 if n == "card" else int(n))
                                                      for n in ("card", "1", "2")}
    streams = {n: {"artifact": f"{n}.json", "iters": 500, "initial_task_0": initial[n], "body_task_0": body[n],
                   "head_task_0": 0.75} for n in initial}
    initials = list(initial.values())
    bodies = list(body.values())
    return {"ok": True, "streams": streams, "settings": settings, "worlds_span": worlds_span,
            "spread": {"initial": max(initials) - min(initials), "body": max(bodies) - min(bodies)},
            "arm": e403.NAIVE, "reps": e403.REPS}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e403.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the card's draws held, every stream recovering, and the streams spanning under a third of the worlds
    j = _judge()
    for cid in ("AC1", "AC2", "AC3", "AC4", "AC5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AC1: a pinned field moved between two streams, and a field in neither list
    moved = {n: _settings(0 if n == "card" else int(n)) for n in ("card", "1", "2")}
    moved["1"] = {**moved["1"], "loop_world_leak": 1.0}
    assert _judge(settings=moved)["AC1"].startswith("FALSIFIER")
    extra = {n: {**_settings(0 if n == "card" else int(n)), "mystery": 1} for n in ("card", "1", "2")}
    assert _judge(settings=extra)["AC1"].startswith("FALSIFIER")

    # AC2: a stream whose world or read-out draw is not the card's
    other = {n: _settings(0 if n == "card" else int(n)) for n in ("card", "1", "2")}
    other["2"] = {**other["2"], "world_read_sha1": "aaaa"}
    assert _judge(settings=other)["AC2"].startswith("FALSIFIER")
    other["2"] = {**other["2"], "readout_subset": "bbbb"}
    assert _judge(settings=other)["AC2"].startswith("FALSIFIER")

    # AC3: a stream that does not recover, and one exactly at zero
    assert _judge(body={**GOOD_BODY, "1": 0.70})["AC3"].startswith("FALSIFIER")
    assert _judge(body={**GOOD_BODY, "1": 0.6875})["AC3"].startswith("FALSIFIER")

    # AC4: an initial reading that moves, and one between the bars
    assert _judge(initial={**GOOD_INIT, "1": 0.50})["AC4"].startswith("FALSIFIER")
    assert _judge(initial={**GOOD_INIT, "1": 0.60})["AC4"].startswith("NULL")

    # AC5: a stream spread over two thirds of the worlds', one between the bars, and the span absent
    assert _judge(body={"card": 0.7729, "1": 0.9000, "2": 0.4500})["AC5"].startswith("FALSIFIER")
    assert _judge(body={"card": 0.7729, "1": 0.8700, "2": 0.6700})["AC5"].startswith("NULL")
    assert _judge(worlds_span=None)["AC5"].startswith("REFUSED")

    #: a run or its weights absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e403.judge(_doc(ok=False)))


def test_the_two_lists_cover_the_card_and_the_stream():
    #: the pinned list carries the draws and the card's settings, and the stream list the seed and its two controls
    assert not set(e403.PINNED) & set(e403.STREAM), set(e403.PINNED) & set(e403.STREAM)
    for k in ("readout_subset", "world_drive_sha1", "basis", "repeats", "cue_seed"):
        assert k not in e403.STREAM, k
    for k in ("seed0", "readout_seed", "loop_seed"):
        assert k in e403.STREAM, k
    #: every field the module reads off a run is in one of them, so the closure claim has something to close over
    keys = set(_settings(1))
    assert keys <= set(e403.PINNED) | set(e403.STREAM), sorted(keys - set(e403.PINNED) - set(e403.STREAM))
    #: and the drawn identity is a subset of the pinned fields, so AC2 checks what AC1 has already held
    assert set(e403.DRAWN) <= set(e403.PINNED), sorted(set(e403.DRAWN) - set(e403.PINNED))


def test_the_live_contrast_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e403_the_far_point_on_the_clean_stream.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e403.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e403.judge(d)}
    #: the configuration and the pinned draws are structural facts, so the first two are read off the artifact
    for cid in ("AC1", "AC2"):
        assert verdicts[cid].split(" -- ")[0] in ("MET", "FALSIFIER FIRED"), verdicts[cid]
    assert sorted(d["streams"]) == ["1", "2", "card"], sorted(d["streams"])
    #: the card's own run is one of the three, and the worlds' span comes from `e396`'s artifact
    assert d["streams"]["card"]["artifact"].startswith("e380"), d["streams"]["card"]
    assert d["worlds_span"] and d["worlds_span"] > 0, d["worlds_span"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
