"""`e438` reads the penalty arm on the card's world, so the tests pin both faces of the five claims, the refusal when a
run is absent, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from experiments import e438_the_penalty_arm_on_the_card as e438

#: the shape of the three-arm roll: fixed true values, so a mutation under test moves one of them
TASKS = ["t0", "t1", "t2"]
GAINS = {"replay-naive": [0.2895, 0.2489, -0.0604],
         "ewc-naive": [0.2400, 0.2100, -0.0330],
         "ewc-replay": [-0.0495, -0.0389, 0.0274]}


def _paired(mean, sigma, n=20):
    se = abs(mean) / sigma if sigma else 0.0
    return {"n": n, "mean": mean, "sd": se * math.sqrt(n), "se": se, "sigma": sigma}


def _doc(gains=None, same_differ=None, bit_identical=True, reps=20, arms=e438.ARMS, paired=(0.0200, 3.0),
         ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "identical": {}, "gains": {},
                "positions": {}, "paired": {}, "spans": {}}
    g = {k: list(v) for k, v in (GAINS if gains is None else gains).items()}
    run_arms = {a: {"replicates": reps, "final": [0.0] * e438.N_TASKS, "diagonal": [0.0] * reps,
                    "forgetting": 0.0, "records": []} for a in arms}
    same = {f"config.{k}": True for k in ("circuit_size", "iters", "lr", "lam", "loop_world_coupled")}
    same.update({f"env_draw.{k}": True for k in e438.DRAW_FIELDS})
    same.update({"circuit": True, "readout": True, "tasks": True})
    if same_differ:
        same[same_differ] = False
    bit = {a: {"equal": bit_identical, "n": reps, "first_differing": None if bit_identical else 0, "fields": []}
           for a in e438.SHARED_ARMS}
    return {"ok": True, "reason": None,
            "runs": {"run": {"arms": run_arms, "tasks": TASKS, "task_order": "as-built"},
                     "base": {"arms": run_arms, "tasks": TASKS, "task_order": "as-built"}},
            "same": same, "identical": bit, "gains": g, "positions": {},
            "paired": {"replay-minus-ewc-block": _paired(*paired)},
            "spans": {"replicates": [reps], "arms": len(run_arms), "same_fields": len(same),
                      "last": {k: v[-1] for k, v in g.items()},
                      "early": {k: g[k][:-1] for k in ("replay-naive", "ewc-naive")},
                      "last_tasks": TASKS[-1], "first_tasks": TASKS[0]}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e438.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: one configuration, the penalty arm paying the last position as the buffer does
    j = _judge()
    for cid in ("BN1", "BN2", "BN3", "BN4", "BN5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BN1: a field differing, a shared arm that is not bit-identical, thin replicates and a missing arm
    assert _judge(same_differ="config.iters")["BN1"].startswith("FALSIFIER")
    assert _judge(bit_identical=False)["BN1"].startswith("FALSIFIER")
    assert _judge(reps=19)["BN1"].startswith("FALSIFIER")
    assert _judge(arms=("naive", "replay"))["BN1"].startswith("FALSIFIER")

    # BN2: a penalty arm that is ahead on the last-taught task, and one between the bars
    assert _judge(gains={**GAINS, "ewc-naive": [0.2400, 0.2100, 0.1000]})["BN2"].startswith("FALSIFIER")
    assert _judge(gains={**GAINS, "ewc-naive": [0.2400, 0.2100, 0.0200]})["BN2"].startswith("NULL")

    # BN3: two buffers that pay the last position very differently, and one between the bars
    assert _judge(gains={**GAINS, "ewc-naive": [0.2400, 0.2100, 0.0800]})["BN3"].startswith("FALSIFIER")
    assert _judge(gains={**GAINS, "ewc-naive": [0.2400, 0.2100, 0.0000]})["BN3"].startswith("NULL")

    # BN4: a penalty arm with no advantage at an early position, and one between the bars
    assert _judge(gains={**GAINS, "ewc-naive": [-0.01, 0.2100, -0.0330]})["BN4"].startswith("FALSIFIER")
    assert _judge(gains={**GAINS, "ewc-naive": [0.0300, 0.2100, -0.0330]})["BN4"].startswith("NULL")

    # BN5: the contrast resolving the other way, and the right direction under two sigma
    assert _judge(paired=(-0.0200, 3.0))["BN5"].startswith("FALSIFIER")
    assert _judge(paired=(0.0100, 1.0))["BN5"].startswith("NULL")

    #: a run absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e438.judge(_doc(ok=False)))


def test_the_runs_and_the_thresholds_are_registered():
    #: the three-arm roll is this unit's, and the two-arm one is the card's own
    assert e438.RUNS["run"].name == "e438_earned_label_three_arms_20reps.json"
    assert e438.RUNS["base"].name == "e380_earned_label_cue0_actionsource_20reps.json"
    assert e438.ARMS == ("naive", "ewc-block", "replay") and e438.SHARED_ARMS == ("naive", "replay")
    assert e438.ORDER == "task_order" and e438.N_TASKS == 3 and e438.N_ARMS == 3 and e438.MIN_REPS == 20
    assert (e438.LAST_BAR, e438.LAST_FIRES) == (0.0, 0.05)
    assert (e438.ALIKE, e438.ALIKE_FIRES) == (0.05, 0.10)
    assert (e438.EARLY_BAR, e438.EARLY_FLOOR) == (0.05, 0.02)
    assert e438.SIGMA == 2.0
    assert set(e438.IGNORED) == {"json_out", "save_theta", "methods"}, e438.IGNORED


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e438_the_penalty_arm_on_the_card.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e438.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: three arms at twenty replicates on one configuration is structural
    arms = d["runs"]["run"]["arms"]
    assert sorted(arms) == ["ewc-block", "naive", "replay"], sorted(arms)
    for arm, got in arms.items():
        assert got["replicates"] >= e438.MIN_REPS, arm
        assert len(got["final"]) == e438.N_TASKS, arm
    assert sorted(d["identical"]) == ["naive", "replay"], sorted(d["identical"])
    assert sorted(d["gains"]) == ["ewc-naive", "ewc-replay", "replay-naive"], sorted(d["gains"])
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
