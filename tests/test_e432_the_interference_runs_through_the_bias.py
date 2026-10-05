"""`e432` reads the corpus's own interference account on three rolls, so the tests pin both faces of the five claims,
the refusal when a roll is absent, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e432_the_interference_runs_through_the_bias as e432

#: the corpus's shape: per roll, each arm's two per-task halves and the whole-body total
ROLLS = {
    "cell": (20, {"ewc-block": ((0.1410, 0.0792), (0.4352, 0.7086), (0.5762, 0.7878)),
                  "naive": ((0.7185, 0.6277), (0.4713, 0.6037), (1.1898, 1.2314)),
                  "replay": ((0.3960, 0.2945), (0.2971, 0.2045), (0.6931, 0.4990))}),
    "pair/frozen": (40, {"ewc": ((0.0108, 0.0326), (0.0, 0.0), (0.0108, 0.0326)),
                         "ewc-block": ((0.0914, 0.0435), (0.0, 0.0), (0.0914, 0.0435)),
                         "ewc-block-rand": ((0.1261, 0.0646), (0.0, 0.0), (0.1261, 0.0646)),
                         "naive": ((0.2142, 0.1087), (0.0, 0.0), (0.2142, 0.1087)),
                         "replay": ((0.0004, 0.0007), (0.0, 0.0), (0.0004, 0.0007))}),
    "pair/plastic": (40, {"ewc": ((0.0052, 0.0280), (0.3204, 0.3195), (0.3257, 0.3474)),
                          "ewc-block": ((0.1594, 0.0920), (0.2987, 0.1534), (0.4581, 0.2453)),
                          "ewc-block-rand": ((0.1605, 0.1204), (0.2517, 0.2549), (0.4122, 0.3753)),
                          "naive": ((0.2336, 0.1474), (0.1930, 0.1139), (0.4266, 0.2614)),
                          "replay": ((0.0004, 0.0004), (0.0005, 0.0012), (0.0009, 0.0017))}),
}


def _roll(reps, arms):
    out = {}
    for a, (theta, bias, whole) in arms.items():
        theta, bias, whole = list(theta), list(bias), list(whole)
        out[a] = {"replicates": reps, "tasks": len(theta), "theta": theta, "bias": bias, "whole": whole,
                  "share": [abs(bias[j]) / abs(whole[j]) if whole[j] else None for j in range(len(theta))]}
    return {"artifact": "x.json", "arms": out}


def _doc(rolls=None, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "rolls": {}, "spans": {}}
    rolls = ROLLS if rolls is None else rolls
    got = {lbl: _roll(reps, arms) for lbl, (reps, arms) in rolls.items()}
    frozen = got["pair/frozen"]["arms"]
    plastic = got["pair/plastic"]["arms"]
    comparisons = sum(r["arms"][e432.BUFFER]["tasks"] for r in got.values())
    below = sum(1 for roll in got.values() for j in range(roll["arms"][e432.BUFFER]["tasks"])
                if abs(roll["arms"][e432.BUFFER]["whole"][j]) < abs(roll["arms"][e432.BASELINE]["whole"][j]))
    return {"ok": True, "reason": None, "rolls": got,
            "spans": {"rolls": len(got),
                      "replicates": sorted({v["replicates"] for r in got.values() for v in r["arms"].values()}),
                      "frozen_bias_max": max((abs(x) for a in frozen for x in frozen[a]["bias"]), default=None),
                      "frozen_theta_max": max((abs(x) for a in frozen for x in frozen[a]["theta"]), default=None),
                      "diagonal_shares": [round(v, 4) for v in plastic.get(e432.DIAGONAL, {}).get("share", [])],
                      "shares": {lbl: {a: v["share"] for a, v in r["arms"].items()} for lbl, r in got.items()},
                      "buffer_below_baseline": below, "comparisons": comparisons}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e432.judge(_doc(**kw))}


def _with(roll, arm, half, values):
    """A copy of the corpus with one arm's half replaced, its share recomputed."""
    out = {lbl: (reps, {a: (tuple(t), tuple(b), tuple(w)) for a, (t, b, w) in arms.items()})
           for lbl, (reps, arms) in ROLLS.items()}
    reps, arms = out[roll]
    theta, bias, whole = arms[arm]
    vals = list(values)
    if half == "bias":
        bias = tuple(vals)
    elif half == "theta":
        theta = tuple(vals)
    else:
        whole = tuple(vals)
    arms[arm] = (theta, bias, whole)
    return out


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: the control's bias half zero, every penalty's share above the baseline's, the buffer below
    j = _judge()
    for cid in ("BH1", "BH2", "BH3", "BH4", "BH5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BH1: too few replicates on the cell, and too few on the pair
    assert _judge(rolls={**ROLLS, "cell": (19, ROLLS["cell"][1])})["BH1"].startswith("FALSIFIER")
    assert _judge(rolls={**ROLLS, "pair/plastic": (39, ROLLS["pair/plastic"][1])})["BH1"].startswith("FALSIFIER")

    # BH2: a non-zero bias half on the frozen side, and a flat weight half there
    assert _judge(rolls=_with("pair/frozen", "naive", "bias", (0.01, 0.0)))["BH2"].startswith("FALSIFIER")
    flat = {lbl: v for lbl, v in ROLLS.items()}
    flat["pair/frozen"] = (40, {a: ((0.0, 0.0), tuple(b), tuple(w))
                                for a, (t, b, w) in ROLLS["pair/frozen"][1].items()})
    assert _judge(rolls=flat)["BH2"].startswith("FALSIFIER")

    # BH3: a penalty whose share is not above the baseline's on one task
    assert _judge(rolls=_with("pair/plastic", "ewc-block", "bias", (0.10, 0.1534)))["BH3"].startswith("FALSIFIER")

    # BH4: the diagonal penalty's share between the bars, and under the falsifier
    assert _judge(rolls=_with("pair/plastic", "ewc", "bias", (0.28, 0.3195)))["BH4"].startswith("NULL")
    assert _judge(rolls=_with("pair/plastic", "ewc", "bias", (0.20, 0.3195)))["BH4"].startswith("FALSIFIER")

    # BH5: a roll where the buffer's whole term is not below the baseline's
    assert _judge(rolls=_with("cell", "replay", "whole", (2.0, 0.4990)))["BH5"].startswith("FALSIFIER")

    #: a roll absent or carrying no interference record refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e432.judge(_doc(ok=False)))


def test_the_rolls_and_the_thresholds_are_registered():
    #: the three-arm cell `e415`, `e423` and `e430` read, and the pair `e427` read
    assert e432.CELL.name == "e356_earned_label_r32_20reps.json"
    assert [p.name for p in e432.PAIR] == ["e140_r32_methods_frozenbias_40reps.json",
                                           "e140_r32_methods_plastic_40reps.json"]
    assert e432.BASELINE == "naive" and e432.BUFFER == "replay"
    assert e432.PENALTIES == ("ewc", "ewc-block", "ewc-block-rand")
    assert (e432.MIN_REPS, e432.PAIR_REPS) == (20, 40) and e432.ZERO == 1e-6
    assert (e432.DIAGONAL, e432.DIAGONAL_SHARE, e432.DIAGONAL_FIRES) == ("ewc", 0.90, 0.80)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e432_the_interference_runs_through_the_bias.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e432.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e432.judge(d)}
    #: the ledger being carried and the control's bias half being zero are structural facts
    assert verdicts["BH1"].startswith("MET") and verdicts["BH2"].startswith("MET"), verdicts
    assert len(d["rolls"]) == 3, sorted(d["rolls"])
    for lbl, roll in d["rolls"].items():
        for a, v in roll["arms"].items():
            assert v["replicates"] >= e432.MIN_REPS, (lbl, a)
            assert len(v["theta"]) == len(v["bias"]) == len(v["whole"]) == v["tasks"], (lbl, a)
            #: each arm's share is its own two halves
            for j in range(v["tasks"]):
                if v["whole"][j]:
                    assert abs(v["share"][j] - abs(v["bias"][j]) / abs(v["whole"][j])) < 1e-9, (lbl, a, j)
    assert abs(d["spans"]["frozen_bias_max"]) < e432.ZERO, d["spans"]["frozen_bias_max"]
    assert d["spans"]["buffer_below_baseline"] == d["spans"]["comparisons"], d["spans"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
