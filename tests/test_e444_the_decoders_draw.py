"""`e444` reads the ledger under a second decoder, so the tests pin both faces of the five claims and the refusal when a
roll is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e444_the_decoders_draw as e444

#: the shape of the two ledgers: fixed true values, so a mutation under test moves one of them
GAIN = [0.2896, 0.2490, -0.0604]
MEAN = 0.1594
SIGMA = 11.97
FORG = {"naive": 0.3750, "ewc-block": 0.3276, "replay": 0.0906}


def _doc(gain=None, same_differ=None, env_moved=None, readout_moved=True, mean=MEAN, reps=20, arms=e444.ARMS,
         ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "moved": {}, "gains": {}, "paired": {},
                "spans": {}}
    g = list(GAIN if gain is None else gain)
    margin = g[0] - g[-1]
    run_arms = {a: {"replicates": reps} for a in arms}
    same = {f"config.{k}": True for k in ("circuit_size", "iters", "lr", "lam")}
    same.update({f"env_draw.{k}": True for k in e444.DRAW_FIELDS})
    same.update({"circuit": True, "tasks": True, "readout.size": True})
    if same_differ:
        same[same_differ] = False
    env = {k: (k == env_moved) for k in e444.DRAW_FIELDS}
    if env_moved:
        same[f"env_draw.{env_moved}"] = False
    return {"ok": True, "reason": None,
            "runs": {label: {"arms": run_arms} for label in e444.RUNS},
            "same": same,
            "moved": {"environment": env,
                      "readout": {"subset_sha1": "0f3a1c8de912" if readout_moved else "59926518137c",
                                  "card": "59926518137c", "moved": readout_moved, "size": 32},
                      "seed": {"new": 1, "card": None}},
            "gains": {"new.replay-naive": g, "new.ewc-naive": [0.0625, -0.0354, -0.1177],
                      "new.ewc-replay": [-0.2271, -0.2846, -0.0573]},
            "paired": {label: {"replay-naive": {"n": reps, "mean": mean, "sd": 0.05, "se": 0.01, "sigma": SIGMA},
                               "ewc-naive": {"n": reps, "mean": -0.0302, "sd": 0.07, "se": 0.02, "sigma": -1.77}}
                       for label in e444.RUNS},
            "spans": {"replicates": [reps], "arms": {label: len(run_arms) for label in e444.RUNS},
                      "same_fields": len(same), "runs": len(e444.RUNS),
                      "margins": {"new": margin, "card": e444.CARD_MARGIN},
                      "card_margin": e444.CARD_MARGIN, "move": margin - e444.CARD_MARGIN,
                      "forgetting": {label: dict(FORG) for label in e444.RUNS}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e444.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: the decoder redrawn, the environment held, and the ledger reading the same way
    j = _judge()
    for cid in ("BV1", "BV2", "BV3", "BV4", "BV5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BV1: an unexpected field differing, an environment fingerprint that moved, a read-out that did not, thin
    # replicates and a short arm list
    assert _judge(same_differ="config.iters")["BV1"].startswith("FALSIFIER")
    assert _judge(env_moved="cue_sha1")["BV1"].startswith("FALSIFIER")
    assert _judge(readout_moved=False)["BV1"].startswith("FALSIFIER")
    assert _judge(reps=19)["BV1"].startswith("FALSIFIER")
    assert _judge(arms=("naive", "replay"))["BV1"].startswith("FALSIFIER")

    # BV2: a buffer with no first-position gain, and one between the bars
    assert _judge(gain=[0.0000, 0.2490, -0.0604])["BV2"].startswith("FALSIFIER")
    assert _judge(gain=[0.0200, 0.2490, -0.0604])["BV2"].startswith("NULL")

    # BV3: a last position that is not cost, and one between the bars
    assert _judge(gain=[0.2896, 0.2490, 0.1000])["BV3"].startswith("FALSIFIER")
    assert _judge(gain=[0.2896, 0.2490, 0.0200])["BV3"].startswith("NULL")

    # BV4: a margin a long way from the card's, and one between the bars
    assert _judge(gain=[0.6000, 0.2000, -0.1000])["BV4"].startswith("FALSIFIER")
    assert _judge(gain=[0.5000, 0.2000, -0.0500])["BV4"].startswith("NULL")

    # BV5: a buffer whose whole-diagonal advantage does not survive, and one between the bars
    assert _judge(mean=0.0100)["BV5"].startswith("FALSIFIER")
    assert _judge(mean=0.0500)["BV5"].startswith("NULL")

    #: a roll absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e444.judge(_doc(ok=False)))


def test_the_runs_and_the_thresholds_are_registered():
    #: the redrawn decoder is this unit's run, and the card's own three-arm roll is what it is read against
    assert e444.RUNS["new"].name == "e444_earned_label_readoutseed1_20reps.json"
    assert e444.RUNS["card"].name == "e438_earned_label_three_arms_20reps.json"
    assert e444.ARMS == ("naive", "ewc-block", "replay")
    assert (e444.BASELINE, e444.BUFFER, e444.ANCHOR) == ("naive", "replay", "ewc-block")
    assert e444.DRAW_FIELD == "readout_seed" and e444.DRAW_FIELD in e444.IGNORED
    assert len(e444.DRAW_FIELDS) == 6, "the six fingerprints `e443` corrected this line's field list to"
    assert "feedback_sha1" in e444.DRAW_FIELDS
    assert e444.N_TASKS == 3 and e444.N_ARMS == 3 and e444.MIN_REPS == 20
    assert (e444.FIRST_BAR, e444.FIRST_FLOOR) == (0.05, 0.0)
    assert (e444.LAST_BAR, e444.LAST_FIRES) == (0.0, 0.05)
    assert (e444.MEAN_BAR, e444.MEAN_FLOOR) == (0.10, 0.02)
    assert e444.CARD_MARGIN == 0.3500, "the card's own margin BV4 is registered against"
    assert (e444.MARGIN_MOVES, e444.MARGIN_FIRES) == (0.15, 0.25)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e444_the_decoders_draw.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e444.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: three arms at twenty replicates on two rolls is structural
    assert sorted(d["runs"]) == ["card", "new"], sorted(d["runs"])
    arms = d["runs"]["new"]["arms"]
    assert sorted(arms) == ["ewc-block", "naive", "replay"], sorted(arms)
    for arm, got in arms.items():
        assert got["replicates"] >= e444.MIN_REPS, arm
        assert len(got["final"]) == e444.N_TASKS, arm
    assert sorted(d["gains"]) == ["card.ewc-naive", "card.ewc-replay", "card.replay-naive",
                                  "new.ewc-naive", "new.ewc-replay", "new.replay-naive"], sorted(d["gains"])
    assert sorted(d["moved"]["environment"]) == sorted(e444.DRAW_FIELDS), sorted(d["moved"]["environment"])
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
