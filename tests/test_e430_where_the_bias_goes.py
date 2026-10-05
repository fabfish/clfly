"""`e430` reads the per-arm bias trajectory of the three-arm cell and the plastic/frozen-bias pair, so the tests pin
both faces of the five claims, the refusal when a run is absent, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e430_where_the_bias_goes as e430

#: the corpus's shape: per roll, each arm's per-task distance from zero and step
CELL = {"ewc-block": ([1.4010, 2.7761, 4.0809], [1.4010, 2.3750, 2.8436]),
        "naive": ([1.4010, 2.1539, 2.7453], [1.4010, 1.6240, 1.6050]),
        "replay": ([1.4010, 1.9076, 2.2946], [1.4010, 1.2639, 1.1140])}
FROZEN = {a: ([0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
          for a in ("ewc", "ewc-block", "ewc-block-rand", "naive", "replay")}
PLASTIC = {"ewc": ([1.1183, 1.8486, 2.5027], [1.1183, 1.4692, 1.6944]),
           "ewc-block": ([1.1183, 1.6652, 2.1428], [1.1183, 1.2364, 1.3758]),
           "ewc-block-rand": ([1.1183, 1.6842, 2.1047], [1.1183, 1.2394, 1.3273]),
           "naive": ([1.1183, 1.6049, 2.0005], [1.1183, 1.1767, 1.2256]),
           "replay": ([1.1183, 1.6041, 1.9721], [1.1183, 1.1341, 1.1556])}


def _arms(spec, reps):
    return {a: {"replicates": reps, "from_zero": list(fz), "step": list(st), "final_from_zero": fz[-1]}
            for a, (fz, st) in spec.items()}


def _doc(cell=None, frozen=None, plastic=None, reps=20, pair_reps=40, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "cell": None, "pair": {}, "spans": {}}
    cell = CELL if cell is None else cell
    frozen = FROZEN if frozen is None else frozen
    plastic = PLASTIC if plastic is None else plastic
    carms, farms, parms = _arms(cell, reps), _arms(frozen, pair_reps), _arms(plastic, pair_reps)
    ordered = sorted(carms, key=lambda a: carms[a]["final_from_zero"])
    return {"ok": True, "reason": None, "cell": {"artifact": "e356.json", "arms": carms},
            "pair": {"frozen": {"artifact": "e140_frozen.json", "arms": farms},
                     "plastic": {"artifact": "e140_plastic.json", "arms": parms}},
            "spans": {"cell_arms": sorted(carms), "replicates": sorted({v["replicates"] for v in carms.values()}),
                      "pair_replicates": sorted({v["replicates"] for v in list(farms.values()) + list(parms.values())}),
                      "cell_by_final": {a: round(carms[a]["final_from_zero"], 4) for a in ordered},
                      "cell_first": {a: round(carms[a]["from_zero"][0], 4) for a in sorted(carms)},
                      "frozen_nonzero": {a: [v for v in (farms[a]["from_zero"] + farms[a]["step"]) if abs(v) > 0]
                                         for a in sorted(farms)},
                      "plastic_first": {a: round(parms[a]["from_zero"][0], 4) for a in sorted(parms)}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e430.judge(_doc(**kw))}


def _cell(arm, values):
    out = {k: (list(v[0]), list(v[1])) for k, v in CELL.items()}
    out[arm] = (list(values), out[arm][1])
    return out


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: the arms one arm after task 0, the buffer nearest zero, the penalty furthest, the control flat
    j = _judge()
    for cid in ("BF1", "BF2", "BF3", "BF4", "BF5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BF1: a missing arm, too few replicates on the cell, and too few on the pair
    assert _judge(cell={k: v for k, v in CELL.items() if k != "ewc-block"})["BF1"].startswith("FALSIFIER")
    assert _judge(reps=19)["BF1"].startswith("FALSIFIER")
    assert _judge(pair_reps=39)["BF1"].startswith("FALSIFIER")

    # BF2: an arm that is not the same arm after the first task
    assert _judge(cell=_cell("replay", [1.30, 1.9076, 2.2946]))["BF2"].startswith("FALSIFIER")

    # BF3: a buffer that does not end nearest zero, and one that ties
    assert _judge(cell=_cell("replay", [1.4010, 2.50, 3.50]))["BF3"].startswith("FALSIFIER")

    # BF4: a penalty that does not end furthest
    assert _judge(cell=_cell("ewc-block", [1.4010, 2.0, 2.0]))["BF4"].startswith("FALSIFIER")

    # BF5: a non-zero reading on the frozen side, and a plastic side that is flat
    moved = {**FROZEN, "naive": ([0.0, 0.0, 0.01], [0.0, 0.0, 0.01])}
    assert _judge(frozen=moved)["BF5"].startswith("FALSIFIER")
    flat = {a: ([0.0, 0.0, 0.0], [0.0, 0.0, 0.0]) for a in PLASTIC}
    assert _judge(plastic=flat)["BF5"].startswith("FALSIFIER")

    #: a run absent or carrying no bias reading refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e430.judge(_doc(ok=False)))


def test_the_runs_and_the_thresholds_are_registered():
    #: the three-arm cell `e415` and `e423` read, and the pair `e427` read
    assert e430.CELL.name == "e356_earned_label_r32_20reps.json"
    assert [p.name for p in e430.PAIR] == ["e140_r32_methods_frozenbias_40reps.json",
                                           "e140_r32_methods_plastic_40reps.json"]
    assert e430.BASELINE == "naive" and e430.BUFFER == "replay" and e430.N_TASKS == 3
    assert (e430.MIN_REPS, e430.PAIR_REPS) == (20, 40) and e430.ZERO == 1e-3


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e430_where_the_bias_goes.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e430.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e430.judge(d)}
    #: the ledger being carried and the buffer ending nearest zero are structural facts
    assert verdicts["BF1"].startswith("MET") and verdicts["BF3"].startswith("MET"), verdicts
    arms = d["cell"]["arms"]
    assert sorted(arms) == ["ewc-block", "naive", "replay"], sorted(arms)
    assert all(v["replicates"] >= e430.MIN_REPS for v in arms.values()), arms
    for a, v in arms.items():
        assert len(v["from_zero"]) == len(v["step"]) == e430.N_TASKS, a
        assert abs(v["final_from_zero"] - v["from_zero"][-1]) < 1e-9, a
    assert arms["replay"]["final_from_zero"] < arms["naive"]["final_from_zero"] < arms["ewc-block"]["final_from_zero"]
    #: the frozen side is the control's own definition and the plastic side is not
    assert all(abs(v) < e430.ZERO for a in d["pair"]["frozen"]["arms"]
               for v in (d["pair"]["frozen"]["arms"][a]["from_zero"] + d["pair"]["frozen"]["arms"][a]["step"]))
    assert any(abs(v) > e430.ZERO for a in d["pair"]["plastic"]["arms"]
               for v in (d["pair"]["plastic"]["arms"][a]["from_zero"] + d["pair"]["plastic"]["arms"][a]["step"]))
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
