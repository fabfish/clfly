"""`e439` reads the matched-random arm on the card's world, so the tests pin both faces of the five claims, the refusal
when a roll is absent, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from experiments import e439_the_matched_random_partition_on_the_card as e439

#: the shape of the four-arm ledger: fixed true values, so a mutation under test moves one of them
TASKS = ["t0", "t1", "t2"]
GAINS = {"ewc-naive": [0.0625, -0.0354, -0.1177],
         "ewcrand-naive": [0.0700, -0.0200, -0.1000],
         "replay-naive": [0.2896, 0.2490, -0.0604],
         "replay-naive-run": [0.2896, 0.2490, -0.0604],
         "ewc-replay": [-0.2271, -0.2844, -0.0573]}


def _paired(mean, sigma, n=20):
    se = abs(mean) / sigma if sigma else 0.0
    return {"n": n, "mean": mean, "sd": se * math.sqrt(n), "se": se, "sigma": sigma}


def _doc(gains=None, same_differ=None, bit_identical=True, reps=20, arms=e439.NEW_ARMS, basis=(0.0100, 0.45),
         forgetting=(0.0150, 0.60), ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "identical": {}, "gains": {},
                "paired": {}, "spans": {}}
    g = {k: list(v) for k, v in (GAINS if gains is None else gains).items()}
    run_arms = {a: {"replicates": reps, "final": [0.0] * e439.N_TASKS, "diagonal": [0.0] * reps,
                    "forgetting": [0.0] * reps, "mean_forgetting": 0.0, "records": []} for a in arms}
    same = {f"{lbl}.config.{k}": True for lbl in e439.RUNS for k in ("circuit_size", "iters", "lr", "lam")}
    same.update({f"{lbl}.env_draw.{k}": True for lbl in e439.RUNS for k in e439.DRAW_FIELDS})
    same.update({f"{lbl}.{k}": True for lbl in e439.RUNS for k in ("circuit", "readout", "tasks")})
    if same_differ:
        same[same_differ] = False
    bit = {f"{a}/{b}:{arm}": {"equal": bit_identical, "n": reps,
                              "first_differing": None if bit_identical else 0, "fields": []}
           for a, b in (("run", "penalty"), ("run", "base"), ("penalty", "base")) for arm in e439.SHARED_ARMS}
    return {"ok": True, "reason": None,
            "runs": {lbl: {"arms": run_arms, "tasks": TASKS, "task_order": "as-built"} for lbl in e439.RUNS},
            "same": same, "identical": bit, "gains": g,
            "paired": {"basis-accuracy": _paired(*basis), "basis-forgetting": _paired(*forgetting)},
            "spans": {"replicates": [reps], "arms": {lbl: len(run_arms) for lbl in e439.RUNS},
                      "same_fields": len(same), "last": {k: v[-1] for k, v in g.items()},
                      "last_tasks": TASKS[-1], "runs": len(e439.RUNS)}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e439.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: one configuration, the basis contrast a null, and the trade the penalty's rather than the basis's
    j = _judge()
    for cid in ("BQ1", "BQ2", "BQ3", "BQ4", "BQ5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BQ1: a field differing, a shared arm that is not bit-identical, thin replicates and a short arm list
    assert _judge(same_differ="run.config.iters")["BQ1"].startswith("FALSIFIER")
    assert _judge(bit_identical=False)["BQ1"].startswith("FALSIFIER")
    assert _judge(reps=19)["BQ1"].startswith("FALSIFIER")
    assert _judge(arms=("naive", "replay"))["BQ1"].startswith("FALSIFIER")

    # BQ2: a basis contrast at the falsifier and one between the bars
    assert _judge(basis=(0.1200, 3.0))["BQ2"].startswith("FALSIFIER")
    assert _judge(basis=(0.0700, 1.2))["BQ2"].startswith("NULL")

    # BQ3: a matched-random arm that is ahead on the last-taught task, and one between the bars
    assert _judge(gains={**GAINS, "ewcrand-naive": [0.0700, -0.0200, 0.1000]})["BQ3"].startswith("FALSIFIER")
    assert _judge(gains={**GAINS, "ewcrand-naive": [0.0700, -0.0200, 0.0200]})["BQ3"].startswith("NULL")

    # BQ4: two penalty arms that pay the last position very differently, and one between the bars
    assert _judge(gains={**GAINS, "ewcrand-naive": [0.0700, -0.0200, 0.0500]})["BQ4"].startswith("FALSIFIER")
    assert _judge(gains={**GAINS, "ewcrand-naive": [0.0700, -0.0200, -0.0400]})["BQ4"].startswith("NULL")

    # BQ5: a forgetting contrast at the falsifier and one between the bars
    assert _judge(forgetting=(0.1200, 3.0))["BQ5"].startswith("FALSIFIER")
    assert _judge(forgetting=(0.0700, 1.2))["BQ5"].startswith("NULL")

    #: a roll absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e439.judge(_doc(ok=False)))


def test_the_runs_and_the_thresholds_are_registered():
    #: the matched-random roll is this unit's, and the two beside it are the penalty's and the card's
    assert e439.RUNS["run"].name == "e439_earned_label_rand_20reps.json"
    assert e439.RUNS["penalty"].name == "e438_earned_label_three_arms_20reps.json"
    assert e439.RUNS["base"].name == "e380_earned_label_cue0_actionsource_20reps.json"
    assert e439.REFERENCE == "base"
    assert e439.ARMS == ("naive", "ewc-block", "ewc-block-rand", "replay")
    assert e439.NEW_ARMS == ("naive", "ewc-block-rand", "replay")
    assert e439.SHARED_ARMS == ("naive", "replay")
    assert e439.ORDER == "task_order" and e439.N_TASKS == 3 and e439.N_ARMS == 3 and e439.MIN_REPS == 20
    assert (e439.LAST_BAR, e439.LAST_FIRES) == (0.0, 0.05)
    assert (e439.NULL_BAR, e439.NULL_FIRES) == (0.05, 0.10)
    assert (e439.ALIKE, e439.ALIKE_FIRES) == (0.05, 0.10)
    assert set(e439.IGNORED) == {"json_out", "save_theta", "methods"}, e439.IGNORED


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e439_the_matched_random_partition_on_the_card.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e439.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: three rolls on one configuration with the matched-random arm among them is structural
    assert sorted(d["runs"]) == ["base", "penalty", "run"], sorted(d["runs"])
    arms = d["runs"]["run"]["arms"]
    assert sorted(arms) == ["ewc-block-rand", "naive", "replay"], sorted(arms)
    for arm, got in arms.items():
        assert got["replicates"] >= e439.MIN_REPS, arm
        assert len(got["final"]) == e439.N_TASKS, arm
    assert sorted(d["gains"]) == sorted(GAINS), sorted(d["gains"])
    for key, got in d["identical"].items():
        assert got["n"] >= e439.MIN_REPS, key
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
