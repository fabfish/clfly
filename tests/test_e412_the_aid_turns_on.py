"""`e412` reads the corpus's own budget ladder on the card's world, so the tests pin both faces of the five claims, the
refusal when a budget's artifact is absent, the rank correlation the fifth claim rests on, and the live re-framing the
unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e412_the_aid_turns_on as e412

#: the corpus's shape: the card's world's `naive` and `replay` arms along the ladder, twenty replicates at each budget
#: (`budget`, naive accuracy, naive mean forgetting, gain, cut)
LADDER = [
    (1, 0.2438, 0.0063, +0.0000, +0.0089), (2, 0.2455, -0.0026, +0.0052, +0.0031),
    (3, 0.2580, -0.0089, +0.0076, +0.0188), (4, 0.2684, 0.0010, -0.0149, -0.0109),
    (5, 0.2764, 0.0036, -0.0194, -0.0042), (6, 0.2681, 0.0307, -0.0056, -0.0000),
    (8, 0.2576, 0.0344, +0.0056, +0.0141), (11, 0.2792, 0.0349, -0.0042, +0.0260),
    (14, 0.2743, 0.0469, +0.0031, +0.0286), (17, 0.2882, 0.0578, -0.0045, +0.0391),
    (20, 0.2969, 0.0536, -0.0045, +0.0307), (30, 0.2990, 0.1099, +0.0174, +0.0620),
    (45, 0.3187, 0.1224, +0.0413, +0.0995), (65, 0.3517, 0.1135, +0.0632, +0.0901),
    (85, 0.3993, 0.1281, +0.0521, +0.1245), (100, 0.3833, 0.1547, +0.0736, +0.1401),
    (150, 0.3858, 0.2323, +0.1094, +0.2141), (275, 0.4694, 0.2906, +0.1184, +0.2505),
    (425, 0.5111, 0.3755, +0.1441, +0.2724), (500, 0.5191, 0.3750, +0.1594, +0.2844),
]
RHO = 0.740


def _doc(rows=None, reps=20, rho=RHO, differs=(), bad_field=False, revisions=4, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "budgets": [], "arms": list(e412.ARMS), "shared": None, "spans": {}}
    rows = rows if rows is not None else [dict(zip(("budget", "naive_acc", "naive_mf", "gain", "cut"), r))
                                          for r in LADDER]
    out = []
    for r in rows:
        flat = {"budget": r["budget"], "artifact": f"iters{r['budget']}.json",
                "arms": {"naive": {"replicates": reps, "final_accuracy": r["naive_acc"],
                                   "mean_forgetting": r["naive_mf"], "final": [r["naive_acc"]] * e412.N_TASKS,
                                   "forgetting": [r["naive_mf"]] * e412.N_TASKS},
                         "replay": {"replicates": reps, "final_accuracy": r["naive_acc"] + r["gain"],
                                    "mean_forgetting": r["naive_mf"] - r["cut"],
                                    "final": [r["naive_acc"] + r["gain"]] * e412.N_TASKS,
                                    "forgetting": [r["naive_mf"] - r["cut"]] * e412.N_TASKS}},
                "gain": r["gain"], "cut": r["cut"]}
        out.append(flat)
    gains = [r["gain"] for r in out]
    accs = [r["arms"]["naive"]["final_accuracy"] for r in out]
    return {"ok": True, "reason": None, "budgets": out, "arms": list(e412.ARMS),
            "shared": {"circuit": "mb+cx+al@n952"},
            "shared_differs_at": list(differs),
            "budget_field": {str(e["budget"]): (e["budget"] + 1 if bad_field else e["budget"]) for e in out},
            "revisions": {f"commit{i}": [] for i in range(revisions)},
            "spans": {"budgets": len(out), "gain_min": min(gains), "gain_max": max(gains),
                      "naive_accuracy_first": accs[0], "naive_accuracy_last": accs[-1],
                      "rho_level_vs_gain": rho}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e412.judge(_doc(**kw))}


def _with(gains=None, accs=None):
    rows = [dict(zip(("budget", "naive_acc", "naive_mf", "gain", "cut"), r)) for r in LADDER]
    if gains is not None:
        for r, g in zip(rows, gains):
            r["gain"] = g
    if accs is not None:
        for r, a in zip(rows, accs):
            r["naive_acc"] = a
    return rows


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: the ladder carried, the sign unstable at the small budgets, and the ramp above the knee
    j = _judge()
    for cid in ("AT1", "AT2", "AT3", "AT4", "AT5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AT1: too few replicates, too few budgets, a shared field differing, and a budget field that is not the budget
    assert _judge(reps=19)["AT1"].startswith("FALSIFIER")
    assert _judge(rows=_with()[:10])["AT1"].startswith("FALSIFIER")
    assert _judge(differs=[500])["AT1"].startswith("FALSIFIER")
    assert _judge(bad_field=True)["AT1"].startswith("FALSIFIER")

    # AT2: one sign only at the small budgets
    both_positive = [g if r[0] > e412.SMALL else (abs(g) if g else 0.01) for g, r in zip([x[3] for x in LADDER], LADDER)]
    assert _judge(rows=_with(gains=both_positive))["AT2"].startswith("FALSIFIER")

    # AT3: a flat ladder, and one whose lift sits between the bars
    assert _judge(rows=_with(gains=[0.02] * len(LADDER)))["AT3"].startswith("FALSIFIER")
    graded = [0.02 if r[0] <= e412.RAMP_BAND else 0.055 for r in LADDER]
    assert _judge(rows=_with(gains=graded))["AT3"].startswith("NULL")

    # AT4: the top band inverted
    inverted = [x[3] for x in LADDER]
    inverted[-1], inverted[-2] = inverted[-2], inverted[-1]
    assert _judge(rows=_with(gains=inverted))["AT4"].startswith("FALSIFIER")

    # AT5: a correlation under the bar, and one between the bars
    assert _judge(rho=0.31)["AT5"].startswith("FALSIFIER")
    assert _judge(rho=0.55)["AT5"].startswith("NULL")

    #: a budget's artifact absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e412.judge(_doc(ok=False)))


def test_the_rank_correlation_is_the_unit_s_own():
    assert e412.spearman([1, 2, 3, 4], [10, 20, 30, 40]) == 1.0
    assert e412.spearman([1, 2, 3, 4], [40, 30, 20, 10]) == -1.0
    assert e412.spearman([1, 2, 3, 4], [1, 1, 2, 2]) < 1.0
    #: the ladder's own two series, which the fifth claim is about
    rho = e412.spearman([r[1] for r in LADDER], [r[3] for r in LADDER])
    assert abs(rho - RHO) < 0.005, rho


def test_the_ladder_and_the_thresholds_are_registered():
    #: the card's world's ladder: `e389` (1-20), `e390` (30-100), `e391` (150-425) and `e380` (500)
    assert sorted(e412.LADDER) == [r[0] for r in LADDER], sorted(e412.LADDER)
    assert len(e412.LADDER) == 20
    for b in (1, 5, 20):
        assert "e389" in e412.LADDER[b].name, b
    for b in (30, 100):
        assert "e390" in e412.LADDER[b].name, b
    for b in (150, 425):
        assert "e391" in e412.LADDER[b].name, b
    assert e412.LADDER[500].name == "e380_earned_label_cue0_actionsource_20reps.json"
    assert all("cue0_actionsource" in p.name for p in e412.LADDER.values())
    assert e412.ARMS == ("naive", "replay") and e412.N_TASKS == 3
    assert (e412.MIN_BUDGETS, e412.MIN_REPS, e412.SMALL) == (15, 20, 20)
    assert (e412.RAMP_BAND, e412.RAMP, e412.RAMP_FIRES) == (100, 0.05, 0.03)
    assert (e412.RHO, e412.RHO_FIRES) == (0.7, 0.4)
    assert e412.ORDER_BUDGETS == (100, 150, 275, 425, 500)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e412_the_aid_turns_on.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e412.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e412.judge(d)}
    #: the ladder being carried and the sign being unstable at the small budgets are structural facts
    assert verdicts["AT1"].startswith("MET") and verdicts["AT2"].startswith("MET"), verdicts
    budgets = [e["budget"] for e in d["budgets"]]
    assert budgets == sorted(budgets) and len(budgets) == 20, budgets
    assert budgets[0] == 1 and budgets[-1] == 500
    #: every budget carries both arms at the full replicate count and the full per-task lists
    for e in d["budgets"]:
        for arm in e412.ARMS:
            a = e["arms"][arm]
            assert a["replicates"] >= e412.MIN_REPS, (e["budget"], arm)
            assert len(a["final"]) == len(a["forgetting"]) == e412.N_TASKS, (e["budget"], arm)
        assert abs(e["gain"] - (e["arms"]["replay"]["final_accuracy"] - e["arms"]["naive"]["final_accuracy"])) < 1e-12
    assert -1.0 <= d["spans"]["rho_level_vs_gain"] <= 1.0, d["spans"]["rho_level_vs_gain"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
