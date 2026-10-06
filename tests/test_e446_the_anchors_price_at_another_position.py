"""`e446` reads the anchor's price at another position, so the tests pin both faces of the five claims and the refusal
when a roll is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e446_the_anchors_price_at_another_position as e446

#: the shape of the two rolls: fixed true values, so a mutation under test moves one of them
AS_BUILT = ["t0", "t1", "t2"]
REVERSED = ["t2", "t1", "t0"]
LAST_NEW = -0.1050
LAST_BASE = -0.1177
LAST_SIGMA = -3.20
STANDING = 0.0150
STANDING_SIGMA = 1.40


def _doc(last=LAST_NEW, last_sigma=LAST_SIGMA, standing=STANDING, standing_sigma=STANDING_SIGMA,
         same_differ=None, bit_identical=True, reversal=True, reps=20, arms=e446.ARMS, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "identical": {}, "reversed": {},
                "contrasts": {}, "spans": {}}
    run_arms = {a: {"replicates": reps} for a in arms}
    same = {f"config.{k}": True for k in ("circuit_size", "iters", "lr", "lam", "loop_world_coupled")}
    same.update({f"env_draw.{k}": True for k in e446.DRAW_FIELDS})
    same.update({"circuit": True, "readout": True, "tasks": True})
    if same_differ:
        same[same_differ] = False
    bit = {f"new/control:{a}": {"equal": bit_identical, "n": reps,
                                "first_differing": None if bit_identical else 0, "fields": []}
           for a in e446.SHARED_ARMS}
    return {"ok": True, "reason": None,
            "runs": {label: {"arms": run_arms} for label in e446.RUNS},
            "same": same, "identical": bit,
            "reversed": {"new": REVERSED if reversal else AS_BUILT, "asbuilt": AS_BUILT,
                         "is_the_reversal": reversal,
                         "orders": {"new": "reverse", "asbuilt": "as-built", "control": "reverse"}},
            "contrasts": {"new": {"anchor_last": {"n": reps, "mean": last, "sd": 0.05, "se": 0.01, "sigma": last_sigma},
                                  "anchor_diagonal": {"n": reps, "mean": standing, "sd": 0.07, "se": 0.02,
                                                      "sigma": standing_sigma}},
                          "asbuilt": {"anchor_last": {"n": reps, "mean": LAST_BASE, "sd": 0.05, "se": 0.01,
                                                      "sigma": -3.71},
                                      "anchor_diagonal": {"n": reps, "mean": -0.0302, "sd": 0.07, "se": 0.02,
                                                          "sigma": -1.77}}},
            "spans": {"replicates": [reps], "arms": {label: len(run_arms) for label in e446.RUNS},
                      "same_fields": len(same),
                      "orders": {"new": "reverse", "asbuilt": "as-built", "control": "reverse"},
                      "last": {"new": last, "asbuilt": LAST_BASE, "move": last - LAST_BASE, "new_sigma": last_sigma,
                               "last_tasks": {"new": "t2", "asbuilt": "t2"}},
                      "standing": {"new": standing, "new_sigma": standing_sigma,
                                   "asbuilt": -0.0302, "asbuilt_sigma": -1.77}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e446.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: one configuration reversed, the anchor paying the same way at a different task's position
    j = _judge()
    for cid in ("BX1", "BX2", "BX3", "BX4", "BX5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BX1: a field differing, a shared arm that is not bit-identical, a suite that is not the reversal, thin
    # replicates and a short arm list
    assert _judge(same_differ="config.iters")["BX1"].startswith("FALSIFIER")
    assert _judge(bit_identical=False)["BX1"].startswith("FALSIFIER")
    assert _judge(reversal=False)["BX1"].startswith("FALSIFIER")
    assert _judge(reps=19)["BX1"].startswith("FALSIFIER")
    assert _judge(arms=("naive", "replay"))["BX1"].startswith("FALSIFIER")

    # BX2: an anchor that is ahead on the newest task, and one between the bars
    assert _judge(last=0.1000)["BX2"].startswith("FALSIFIER")
    assert _judge(last=0.0200)["BX2"].startswith("NULL")

    # BX3: a price that does not resolve
    assert _judge(last_sigma=1.20)["BX3"].startswith("FALSIFIER")

    # BX4: a price that moved with the task, and one between the bars
    assert _judge(last=0.0500)["BX4"].startswith("FALSIFIER")
    assert _judge(last=-0.0400)["BX4"].startswith("NULL")

    # BX5: a standing that resolves on this order
    assert _judge(standing_sigma=2.50)["BX5"].startswith("FALSIFIER")

    #: a roll absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e446.judge(_doc(ok=False)))


def test_the_runs_and_the_thresholds_are_registered():
    #: the reversed anchor roll is this unit's, and the two beside it are the anchor's own and the buffer's
    assert e446.RUNS["new"].name == "e446_earned_label_anchor_reverse_20reps.json"
    assert e446.RUNS["asbuilt"].name == "e438_earned_label_three_arms_20reps.json"
    assert e446.RUNS["control"].name == "e436_earned_label_cue0_reverse_20reps.json"
    assert e446.ARMS == ("naive", "ewc-block", "replay") and e446.SHARED_ARMS == ("naive", "replay")
    assert (e446.ANCHOR, e446.BASELINE, e446.BUFFER) == ("ewc-block", "naive", "replay")
    assert e446.ORDER == "task_order" and e446.ORDER in e446.IGNORED
    assert e446.N_TASKS == 3 and e446.N_ARMS == 3 and e446.MIN_REPS == 20
    assert (e446.LAST_BAR, e446.LAST_FIRES) == (0.0, 0.05)
    assert e446.SIGMA == 2.0
    assert (e446.MOVES, e446.MOVES_FIRES) == (0.05, 0.10)
    assert e446.AS_BUILT_LAST == -0.1177, "the as-built figure BX4 is registered against"


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e446_the_anchors_price_at_another_position.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e446.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: three arms at twenty replicates on three rolls is structural
    assert sorted(d["runs"]) == ["asbuilt", "control", "new"], sorted(d["runs"])
    arms = d["runs"]["new"]["arms"]
    assert sorted(arms) == ["ewc-block", "naive", "replay"], sorted(arms)
    for arm, got in arms.items():
        assert got["replicates"] >= e446.MIN_REPS, arm
        assert len(got["final"]) == e446.N_TASKS, arm
    assert sorted(d["identical"]) == ["new/control:naive", "new/control:replay"], sorted(d["identical"])
    for key, got in d["identical"].items():
        assert got["n"] >= e446.MIN_REPS, key
    assert d["spans"]["orders"]["new"] != d["spans"]["orders"]["asbuilt"], d["spans"]["orders"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
