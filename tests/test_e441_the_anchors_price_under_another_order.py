"""`e441` reads the anchor on the card's world under a second order, so the tests pin both faces of the five claims, the
refusal when a roll is absent, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e441_the_anchors_price_under_another_order as e441

#: the shape of the two ledgers: fixed true values, so a mutation under test moves one of them
TASKS = ["t0", "t1", "t2"]
GAINS = {"asbuilt.ewc-naive": [0.0625, -0.0354, -0.1177],
         "new.ewc-naive": [0.0500, -0.0400, -0.1100],
         "asbuilt.replay-naive": [0.2896, 0.2490, -0.0604],
         "new.replay-naive": [0.3100, 0.2200, -0.0500],
         "asbuilt.ewc-replay": [-0.2271, -0.2844, -0.0573],
         "new.ewc-replay": [-0.2600, -0.2600, -0.0600]}


def _doc(gains=None, same_differ=None, bit_identical=True, reps=20, arms=e441.ARMS, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "identical": {}, "gains": {},
                "by_task": {}, "orders": {}, "spans": {}}
    g = {k: list(v) for k, v in (GAINS if gains is None else gains).items()}
    run_arms = {a: {"replicates": reps, "final": [0.0] * e441.N_TASKS, "diagonal": [0.0] * reps,
                    "forgetting": 0.0, "records": []} for a in arms}
    same = {f"config.{k}": True for k in ("circuit_size", "iters", "lr", "lam", "loop_world_coupled")}
    same.update({f"env_draw.{k}": True for k in e441.DRAW_FIELDS})
    same.update({"circuit": True, "readout": True, "tasks": True})
    if same_differ:
        same[same_differ] = False
    bit = {f"new/{o}:{a}": {"equal": bit_identical, "n": reps,
                            "first_differing": None if bit_identical else 0, "fields": []}
           for o in ("control", "asbuilt") for a in e441.SHARED_ARMS}
    last_new, last_base = g["new.ewc-naive"][-1], g["asbuilt.ewc-naive"][-1]
    return {"ok": True, "reason": None,
            "runs": {lbl: {"arms": run_arms, "tasks": TASKS, "task_order": "1,0,2" if lbl == "new" else "as-built"}
                     for lbl in e441.RUNS},
            "same": same, "identical": bit, "gains": g, "by_task": {},
            "orders": {"new": "1,0,2", "asbuilt": "as-built", "control": "1,0,2"},
            "spans": {"replicates": [reps], "arms": {lbl: len(run_arms) for lbl in e441.RUNS},
                      "same_fields": len(same),
                      "last": {"new": last_new, "asbuilt": last_base, "move": last_new - last_base},
                      "middle": {"new": g["new.ewc-naive"][1]},
                      "means": {}, "orders": {"new": "1,0,2", "asbuilt": "as-built"},
                      "last_tasks": {"new": TASKS[-1], "asbuilt": TASKS[-1]},
                      "middle_tasks": {"new": TASKS[1], "asbuilt": TASKS[1]}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e441.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: one configuration, and the anchor paying the same way at a second order
    j = _judge()
    for cid in ("BS1", "BS2", "BS3", "BS4", "BS5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BS1: a field differing, a shared arm that is not bit-identical, thin replicates and a short arm list
    assert _judge(same_differ="config.iters")["BS1"].startswith("FALSIFIER")
    assert _judge(bit_identical=False)["BS1"].startswith("FALSIFIER")
    assert _judge(reps=19)["BS1"].startswith("FALSIFIER")
    assert _judge(arms=("naive", "replay"))["BS1"].startswith("FALSIFIER")

    # BS2: an anchor that is ahead on the last-taught task, and one between the bars
    assert _judge(gains={**GAINS, "new.ewc-naive": [0.0500, -0.0400, 0.1000]})["BS2"].startswith("FALSIFIER")
    assert _judge(gains={**GAINS, "new.ewc-naive": [0.0500, -0.0400, 0.0200]})["BS2"].startswith("NULL")

    # BS3: a last-position cost that moves with the order, and one between the bars
    assert _judge(gains={**GAINS, "new.ewc-naive": [0.0500, -0.0400, 0.0500]})["BS3"].startswith("FALSIFIER")
    assert _judge(gains={**GAINS, "new.ewc-naive": [0.0500, -0.0400, -0.0400]})["BS3"].startswith("NULL")

    # BS4: an anchor that is ahead at the middle position, and one between the bars
    assert _judge(gains={**GAINS, "new.ewc-naive": [0.0500, 0.1000, -0.1100]})["BS4"].startswith("FALSIFIER")
    assert _judge(gains={**GAINS, "new.ewc-naive": [0.0500, 0.0200, -0.1100]})["BS4"].startswith("NULL")

    # BS5: a buffer that is not above the anchor at the last position
    assert _judge(gains={**GAINS, "new.replay-naive": [0.3100, 0.2200, -0.2000]})["BS5"].startswith("FALSIFIER")

    #: a roll absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e441.judge(_doc(ok=False)))


def test_the_runs_and_the_thresholds_are_registered():
    #: the rotated roll is this unit's, and the two beside it are the anchor's own and the buffer's
    assert e441.RUNS["new"].name == "e441_earned_label_anchor_order102_20reps.json"
    assert e441.RUNS["asbuilt"].name == "e438_earned_label_three_arms_20reps.json"
    assert e441.RUNS["control"].name == "e437_earned_label_cue0_order102_20reps.json"
    assert e441.ARMS == ("naive", "ewc-block", "replay") and e441.SHARED_ARMS == ("naive", "replay")
    assert (e441.ANCHOR, e441.BASELINE, e441.BUFFER) == ("ewc-block", "naive", "replay")
    assert e441.ORDER == "task_order" and e441.ORDER in e441.IGNORED, "the order is the field that differs"
    assert e441.N_TASKS == 3 and e441.N_ARMS == 3 and e441.MIN_REPS == 20
    assert (e441.LAST_BAR, e441.LAST_FIRES) == (0.0, 0.05)
    assert (e441.MOVES, e441.MOVES_FIRES) == (0.05, 0.10)
    assert (e441.MIDDLE_BAR, e441.MIDDLE_FIRES) == (0.0, 0.05)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e441_the_anchors_price_under_another_order.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e441.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: three arms at twenty replicates on one configuration is structural
    assert sorted(d["runs"]) == ["asbuilt", "control", "new"], sorted(d["runs"])
    arms = d["runs"]["new"]["arms"]
    assert sorted(arms) == ["ewc-block", "naive", "replay"], sorted(arms)
    for arm, got in arms.items():
        assert got["replicates"] >= e441.MIN_REPS, arm
        assert len(got["final"]) == e441.N_TASKS, arm
    assert sorted(d["identical"]) == ["new/asbuilt:naive", "new/asbuilt:replay",
                                      "new/control:naive", "new/control:replay"], sorted(d["identical"])
    for key, got in d["identical"].items():
        assert got["n"] >= e441.MIN_REPS, key
    assert d["orders"]["new"] != d["orders"]["asbuilt"], d["orders"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
