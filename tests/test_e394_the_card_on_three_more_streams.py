"""`e394` redraws the card's training stream three times with the read-out draw and the environment pinned, so the
tests pin both faces of the five claims, the refusal when a run or its weights is absent, and the live replication.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e394_the_card_on_three_more_streams as e394

PINNED_VALUES = {"circuit": "mb+cx+al@n952", "circuit_size": 300, "readout_subset": "59926518137c",
                 "readout_size": 32, "basis": "cell_class", "support": 80,
                 "task_names": ["loop_odour_identity", "loop_heading", "loop_odour_input"],
                 "task_readout_widths": [8], "loop_cue_at": 0, "loop_world_dims": 8, "loop_world_leak": 0.35,
                 "loop_world_modes": 0, "loop_world_nonlinear": False, "readout_from_world": True,
                 "closed_loop": True, "lr": 0.003, "batch": 32, "iters": 20, "repeats": 20,
                 "cue_sha1": "3985fc4e3252", "feedback_sha1": "77963b921bc3", "n_cue": 12,
                 "action_sha1": "f379863d1cf4", "n_action": 8, "drive_from_cue": False,
                 "loop_drive_from_cue": False, "world_drive_sha1": "3d88340cf387",
                 "world_read_sha1": "3a7ba76b3619", "world_coupling_sha1": "5326f4a0edb4"}


def _settings(seed0):
    #: the card's own run leaves the two control flags unset, defaulting them to its seed0; the new ones set them
    explicit = 0 if seed0 else None
    return {**PINNED_VALUES, "seed0": seed0, "readout_seed": explicit, "loop_seed": explicit}


#: the corpus's shape: the connectome reads 0.6875 on every stream and twenty updates cost each at least 0.05
GOOD_INIT = {"card": 0.6875, "1": 0.6875, "2": 0.6875, "3": 0.6875}
GOOD_BODY = {"card": 0.5740, "1": 0.58, "2": 0.55, "3": 0.60}


def _doc(initial=GOOD_INIT, body=GOOD_BODY, settings=None, ok=True, reason="absent"):
    if not ok:
        #: `reading` refuses the whole unit when a run's weights are absent
        return {"ok": False, "streams": {}, "settings": {}, "reason": reason}
    settings = settings if settings is not None else {n: _settings(0 if n == "card" else int(n))
                                                      for n in ("card", "1", "2", "3")}
    streams = {n: {"artifact": f"{n}.json", "initial_task_0": initial[n], "body_task_0": body[n],
                   "head_task_0": 0.25} for n in initial}
    initials = list(initial.values())
    bodies = list(body.values())
    return {"ok": True, "streams": streams, "settings": settings,
            "spread": {"initial": max(initials) - min(initials), "body": max(bodies) - min(bodies)},
            "arm": e394.NAIVE, "reps": e394.REPS}


def _judge(**kw):
    return {row["id"]: row for row in e394.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: three clean streams whose readings and whose cost of twenty updates all land near the card's
    j = _judge()
    for cid in ("O1", "O2", "O3", "O4", "O5"):
        assert j[cid]["verdict"].startswith("MET"), (cid, j[cid])

    # O1: a pinned field moved between two streams, and a field in neither list
    moved = {n: _settings(0 if n == "card" else int(n)) for n in ("card", "1", "2", "3")}
    moved["2"] = {**moved["2"], "basis": "side"}
    assert _judge(settings=moved)["O1"]["verdict"].startswith("FALSIFIER")
    extra = {n: {**_settings(0 if n == "card" else int(n)), "mystery": 1} for n in ("card", "1", "2", "3")}
    assert _judge(settings=extra)["O1"]["verdict"].startswith("FALSIFIER")

    # O2: two streams sharing a seed0, and a pinned field that moves
    twin = {n: _settings(0 if n == "card" else int(n)) for n in ("card", "1", "2", "3")}
    twin["2"] = _settings(1)
    assert _judge(settings=twin)["O2"]["verdict"].startswith("FALSIFIER")
    assert _judge(settings=moved)["O2"]["verdict"].startswith("FALSIFIER")

    # O3: a stream whose world or read-out draw is not the card's
    other = {n: _settings(0 if n == "card" else int(n)) for n in ("card", "1", "2", "3")}
    other["3"] = {**other["3"], "world_read_sha1": "aaaa"}
    assert _judge(settings=other)["O3"]["verdict"].startswith("FALSIFIER")
    other["3"] = {**other["3"], "readout_subset": "bbbb"}
    assert _judge(settings=other)["O3"]["verdict"].startswith("FALSIFIER")

    # O4: an initial reading that moves with the stream, one between the bars, and a body that moves
    assert _judge(initial={"card": 0.6875, "1": 0.68, "2": 0.50, "3": 0.69})["O4"][
        "verdict"].startswith("FALSIFIER")
    assert _judge(initial={"card": 0.6875, "1": 0.68, "2": 0.58, "3": 0.69})["O4"]["verdict"].startswith("NULL")
    assert _judge(body={"card": 0.5740, "1": 0.58, "2": 0.40, "3": 0.60})["O4"]["verdict"].startswith("FALSIFIER")

    # O5: a stream where twenty updates cost the body nothing
    assert _judge(body={"card": 0.5740, "1": 0.58, "2": 0.68, "3": 0.60})["O5"]["verdict"].startswith("FALSIFIER")

    #: a run or its weights absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e394.judge(_doc(ok=False)))


def test_the_two_lists_cover_the_card_and_the_stream():
    #: the pinned fields are the draws and the card's settings, the stream is the seed and its two controls
    assert not set(e394.PINNED) & set(e394.STREAM), set(e394.PINNED) & set(e394.STREAM)
    for k in ("readout_subset", "world_drive_sha1", "cue_sha1", "basis", "repeats"):
        assert k not in e394.STREAM, k
    for k in ("seed0", "readout_seed", "loop_seed"):
        assert k in e394.STREAM, k
    #: every field the module reads off a run is in one of them, so the closure claim has something to close over
    keys = set(_settings(1))
    assert keys <= set(e394.PINNED) | set(e394.STREAM), sorted(keys - set(e394.PINNED) - set(e394.STREAM))
    #: and the drawn identity is a subset of the pinned fields, so O3 checks what O1 has already held
    assert set(e394.DRAWN_IDENTITY) <= set(e394.PINNED), sorted(set(e394.DRAWN_IDENTITY) - set(e394.PINNED))


def test_the_live_replication_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e394_the_card_on_three_more_streams.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e394.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e394.judge(d)}
    #: the configuration and the pinned draws are structural facts, so the first three claims are read off the
    #: artifact rather than demanded
    for cid in ("O1", "O2", "O3"):
        assert verdicts[cid].split(" -- ")[0] in ("MET", "FALSIFIER FIRED"), verdicts[cid]
    assert sorted(d["streams"]) == ["1", "2", "3", "card"], sorted(d["streams"])
    #: the card's own run is one of the four, so the comparison is against an artifact and not a constant
    assert d["streams"]["card"]["artifact"].startswith("e389"), d["streams"]["card"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
