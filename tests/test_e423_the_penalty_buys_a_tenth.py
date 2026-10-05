"""`e423` splits both arms of the one three-arm run against the same baseline, so the tests pin both faces of the five
claims, the refusal when the run is absent, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e423_the_penalty_buys_a_tenth as e423

#: the corpus's shape: the penalty's and the buffer's `(learning term, retention term)` over the three tasks
PENALTY = ((0.0000, -0.0750, -0.0771), (+0.0292, +0.0406, +0.0000))
BUFFER = ((0.0000, -0.0406, -0.0865), (+0.2844, +0.2896, +0.0000))
BASE = {"learned": [0.7917, 0.8292, 0.8469], "forgetting": [0.4542, 0.3656, 0.0000],
        "final": [0.3375, 0.4635, 0.8469]}


def _arm(learned, retention, reps=20):
    learned, retention = list(learned), list(retention)
    final = [BASE["final"][k] + learned[k] + retention[k] for k in range(e423.N_TASKS)]
    return {"replicates": reps, "learned": [BASE["learned"][k] + learned[k] for k in range(e423.N_TASKS)],
            "forgetting": [BASE["forgetting"][k] - retention[k] for k in range(e423.N_TASKS)], "final": final}


def _terms(learned, retention):
    learned, retention = list(learned), list(retention)
    return {"learned": learned, "retention": retention,
            "gain": [learned[k] + retention[k] for k in range(e423.N_TASKS)]}


def _doc(penalty=PENALTY, buffer=BUFFER, reps=20, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "artifact": None, "arms": {}, "terms": {}, "spans": {}}
    pl, pr = penalty
    bl, br = buffer
    arms = {e423.BASELINE: dict(BASE, replicates=reps),
            "ewc-block": _arm(pl, pr, reps), "replay": _arm(bl, br, reps)}
    terms = {"ewc-block": _terms(pl, pr), "replay": _terms(bl, br)}
    ratios = {str(k): (terms["replay"]["retention"][k] / terms["ewc-block"]["retention"][k])
              if terms["ewc-block"]["retention"][k] else None for k in (e423.OLDEST, e423.MIDDLE)}
    return {"ok": True, "reason": None, "artifact": "e356_earned_label_r32_20reps.json", "arms": arms, "terms": terms,
            "spans": {"replicates": sorted({v["replicates"] for v in arms.values()}), "ratios": ratios,
                      "worst_gap": max(abs(terms[a]["gain"][k] - terms[a]["learned"][k] - terms[a]["retention"][k])
                                       for a in e423.ARMS for k in range(e423.N_TASKS))}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e423.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: the penalty buying a small retention for the buffer's large one at the same price
    j = _judge()
    for cid in ("AX1", "AX2", "AX3", "AX4", "AX5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AX1: too few replicates
    assert _judge(reps=19)["AX1"].startswith("FALSIFIER")

    # AX2: a penalty whose oldest-task retention is not a gain
    assert _judge(penalty=((0.0000, -0.0750, -0.0771), (-0.0100, +0.0406, +0.0000)))["AX2"].startswith("FALSIFIER")

    # AX3: a gap between the arms' prices, and one over the falsifier bar
    assert _judge(penalty=((0.0000, -0.1200, -0.0771), PENALTY[1]))["AX3"].startswith("NULL")
    assert _judge(penalty=((0.0000, -0.2000, -0.0771), PENALTY[1]))["AX3"].startswith("FALSIFIER")

    # AX4: a penalty whose retention is a fifth of the buffer's, and one that is nearly half
    assert _judge(penalty=PENALTY[0:1] + ((0.2000, 0.2000, 0.0000),))["AX4"].startswith("FALSIFIER")
    assert _judge(penalty=PENALTY[0:1] + ((0.1000, 0.1000, 0.0000),))["AX4"].startswith("NULL")

    # AX5: a penalty whose middle trade pays, and a buffer whose middle gain is small
    assert _judge(penalty=((0.0000, -0.0750, -0.0771), (0.0292, 0.1500, 0.0000)))["AX5"].startswith("FALSIFIER")
    assert _judge(buffer=((0.0000, -0.0406, -0.0865), (0.0200, 0.0200, 0.0000)))["AX5"].startswith("FALSIFIER")

    #: the run's artifact absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e423.judge(_doc(ok=False)))


def test_the_run_and_the_thresholds_are_registered():
    #: the one cell that carries all three arms at twenty replicates, the cell `e415` read
    assert e423.RUN.name == "e356_earned_label_r32_20reps.json"
    assert e423.BASELINE == "naive" and e423.ARMS == ("ewc-block", "replay")
    assert e423.N_TASKS == 3 and (e423.OLDEST, e423.MIDDLE, e423.NEWEST) == (0, 1, 2)
    assert e423.MIN_REPS == 20
    assert (e423.PRICE, e423.PRICE_FIRES) == (0.05, 0.10)
    assert (e423.RATIO, e423.RATIO_FIRES) == (5.0, 2.0)
    assert (e423.BUFFER_GAIN, e423.BUFFER_FIRES, e423.PENALTY_GAIN) == (0.20, 0.10, 0.05)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e423_the_penalty_buys_a_tenth.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e423.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e423.judge(d)}
    #: the ledger being carried and the buffer buying the larger retention are structural facts
    assert verdicts["AX1"].startswith("MET") and verdicts["AX4"].startswith("MET"), verdicts
    assert sorted(d["arms"]) == ["ewc-block", "naive", "replay"], sorted(d["arms"])
    assert all(v["replicates"] >= e423.MIN_REPS for v in d["arms"].values()), d["arms"]
    for arm in e423.ARMS:
        t = d["terms"][arm]
        #: each arm's gain is the two terms, and the terms are the arms' own readings against the baseline
        for k in range(e423.N_TASKS):
            assert abs(t["gain"][k] - t["learned"][k] - t["retention"][k]) < 1e-12, (arm, k)
            assert abs(t["learned"][k] - (d["arms"][arm]["learned"][k] - d["arms"][e423.BASELINE]["learned"][k])) < 1e-9
    assert abs(d["spans"]["worst_gap"]) < 1e-9, d["spans"]["worst_gap"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
