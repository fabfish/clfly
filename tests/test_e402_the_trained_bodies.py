"""`e402` measures the six trained bodies' movement and their mutual alignment, so the tests pin both faces of the
five claims, the refusal when a body is absent, and the live screen the unit closes.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e402_the_trained_bodies as e402

#: the corpus's shape: six bodies from one starting point, moving alike and near-orthogonally, with the card's inside
GOOD_MOVE = {"card": 0.0777, "cue1": 0.0774, "cue3": 0.0776, "cue9": 0.0771, "cue14": 0.0730, "cue6": 0.0757}
GOOD_COS = {"card": 0.0389, "cue1": 0.0385, "cue3": 0.0376, "cue9": 0.0403, "cue14": 0.0368, "cue6": 0.0414}
GOOD_HEAD = {"card": 0.7500, "cue1": 0.7500, "cue3": 0.8333, "cue9": 0.8125, "cue14": 0.8333, "cue6": 0.5208}
GOOD_GAIN = {"card": 0.0854, "cue1": -0.1813, "cue3": -0.1635, "cue9": -0.2250, "cue14": -0.1479, "cue6": -0.2083}


def _doc(move=None, cos=None, head=None, one_initial=True, ok=True, reason="absent"):
    if not ok:
        #: `reading` refuses the whole unit when a body's weights are absent
        return {"ok": False, "bodies": {}, "movement": {}, "alignment": {}, "heads": {}, "gains": {},
                "one_initial_body": None, "replicates": 20, "reason": reason}
    move = move if move is not None else dict(GOOD_MOVE)
    cos = cos if cos is not None else dict(GOOD_COS)
    head = head if head is not None else dict(GOOD_HEAD)
    return {"ok": True, "replicates": 20, "one_initial_body": one_initial,
            "movement": {n: {"mean": v, "sem": 0.0013, "min": v - 0.008, "max": v + 0.008}
                         for n, v in move.items()},
            "alignment": {n: {"mean_cosine": v, "max_cosine": v + 0.08, "min_cosine": v - 0.01}
                          for n, v in cos.items()},
            "heads": head, "gains": dict(GOOD_GAIN),
            "bodies": {n: {"mean_movement": move[n], "mean_cosine": cos[n], "head_task_0": head[n],
                           "gain": GOOD_GAIN[n]} for n in move}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e402.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: six bodies from one starting point, moving alike, near-orthogonally, with the card's inside every range
    j = _judge()
    for cid in ("AB1", "AB2", "AB3", "AB4", "AB5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AB1: an initial body that differs on some replicate
    assert _judge(one_initial=False)["AB1"].startswith("FALSIFIER")

    # AB2: a card's world that moved well clear of the failing range, and one between the bars
    assert _judge(move={**GOOD_MOVE, "card": 0.12})["AB2"].startswith("FALSIFIER")
    assert _judge(move={**GOOD_MOVE, "card": 0.0835})["AB2"].startswith("NULL")

    # AB3: a world whose movement is aligned with the others, and one between the bars
    assert _judge(cos={**GOOD_COS, "cue14": 0.9})["AB3"].startswith("FALSIFIER")
    assert _judge(cos={**GOOD_COS, "cue14": 0.4})["AB3"].startswith("NULL")

    # AB4: the card's body as an outlier of alignment
    assert _judge(cos={**GOOD_COS, "card": 0.5})["AB4"].startswith("FALSIFIER")
    assert _judge(cos={**GOOD_COS, "card": 0.0})["AB4"].startswith("FALSIFIER")

    # AB5: a head that separates it, above the failing range and below it
    assert _judge(head={**GOOD_HEAD, "card": 0.95})["AB5"].startswith("FALSIFIER")
    assert _judge(head={**GOOD_HEAD, "card": 0.25})["AB5"].startswith("FALSIFIER")

    #: a body absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e402.judge(_doc(ok=False)))


def test_the_bodies_and_the_readings_are_registered():
    #: the six worlds are the ones whose 500-update bodies are on disk, and the readings are the ones published
    assert sorted(e402.BODIES) == ["card", "cue1", "cue14", "cue3", "cue6", "cue9"], sorted(e402.BODIES)
    assert len(e402.REPLICATES) == 20 and e402.REPLICATES[0] == 0, e402.REPLICATES[:3]
    assert sorted(e402.HEADS) == sorted(e402.GAINS) == sorted(e402.BODIES), "one reading per body"
    #: and the thresholds are the registered ones
    assert (e402.NEAR, e402.FIRES) == (0.005, 0.010), (e402.NEAR, e402.FIRES)
    assert (e402.NULL_ALIGNED, e402.ALIGNED) == (0.3, 0.5), (e402.NULL_ALIGNED, e402.ALIGNED)


def test_the_live_screen_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e402_the_trained_bodies.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e402.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e402.judge(d)}
    #: the control is structural -- the six bodies start from one body -- so it is demanded
    assert verdicts["AB1"].startswith("MET"), verdicts["AB1"]
    assert sorted(d["bodies"]) == ["card", "cue1", "cue14", "cue3", "cue6", "cue9"], sorted(d["bodies"])
    #: every body carries its own movement, alignment, head and gain, and the four agree with each other
    for name, v in d["bodies"].items():
        assert v["mean_movement"] == d["movement"][name]["mean"], name
        assert v["mean_cosine"] == d["alignment"][name]["mean_cosine"], name
        assert v["head_task_0"] == d["heads"][name] and v["gain"] == d["gains"][name], name
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
