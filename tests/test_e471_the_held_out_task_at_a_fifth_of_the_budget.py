"""`e471` reads the held-out task at two budgets, so the tests pin both faces of the four claims, the counts both
budgets must share, and the refusal when a roll is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e471_the_held_out_task_at_a_fifth_of_the_budget as e471

SIDES = e471.SIDES
BUDGETS = e471.BUDGETS
#: the shape: at a hundred updates the sequence still raises the unseen cue set's reading, and the far point more so
CELL = {100: {"initial": 0.6500, "trained": 0.7000, "change": 0.0500, "change_sigma": 5.00, "versus": -0.0050,
              "versus_sigma": -0.50},
        500: {"initial": 0.6875, "trained": 0.7719, "change": 0.0844, "change_sigma": 10.11, "versus": -0.0094,
              "versus_sigma": -0.86}}
GROW = 0.0700
GROW_SIGMA = 6.00


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.01, "sigma": sigma}


def _doc(same_differ=None, change_sigma=None, grow_sigma=GROW_SIGMA, versus_sigma=None, counts=None, thin=False,
         short=False, counts_differ=False, ok=True, reason="a roll is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "curve": {}, "paired": {}, "spans": {}}
    curve = {}
    for b in BUDGETS:
        cell = dict(CELL[b])
        sigma = cell["change_sigma"] if change_sigma is None else change_sigma
        vs = cell["versus_sigma"] if versus_sigma is None else versus_sigma
        curve[str(b)] = {}
        for side in SIDES:
            anchor = e471.ANCHOR_OF[side]
            arms = {}
            for arm in (e471.BASELINE, anchor, e471.BUFFER):
                arms[arm] = {"initial": cell["initial"], "trained": cell["trained"],
                             "change": _paired(cell["change"] if arm == e471.BASELINE else cell["change"] - 0.005,
                                               sigma),
                             "against_baseline": _paired(0.0 if arm == e471.BASELINE else cell["versus"],
                                                         0.0 if arm == e471.BASELINE else vs)}
            curve[str(b)][side] = {"budget": b, "side": side, "anchor": anchor,
                                   "initial": cell["initial"], "trained": cell["trained"],
                                   "change": _paired(cell["change"], sigma), "arms": arms}
    same = {f"{side}.{k}": True for side in SIDES for k in ("circuit_size", "readout_size", "repeats")}
    same.update({f"{side}.circuit": True for side in SIDES})
    same.update({f"{side}.tasks": True for side in SIDES})
    if same_differ:
        same[same_differ] = False
    c = counts or {"task": ["loop_holdout"], "n_train": [96], "n_eval": [48], "ridge": [0.01]}
    reps = 19 if thin else 20
    return {"ok": True, "reason": None, "runs": {}, "same": same, "curve": curve,
            "paired": {side: {"trained": _paired(GROW, grow_sigma),
                              "initial": _paired(0.0375, 1.0)} for side in SIDES},
            "spans": {"budgets": list(BUDGETS), "sides": list(SIDES), "runs": 4, "same_fields": len(same),
                      "thin": {"x": reps} if thin else {},
                      "replicates": [reps],
                      "tasks": ["loop_holdout"],
                      "counts": {f"{b}/{side}/{arm}.{k}": ((("loop_other",) if k == "task" else (48,))
                                                          if (counts_differ and b == 100 and k == counts_differ)
                                                          else tuple(c[k]))
                                 for b in BUDGETS for side in SIDES
                                 for arm in (e471.BASELINE, e471.ANCHOR_OF[side], e471.BUFFER)
                                 for k in ("task", "n_train", "n_eval", "ridge")},
                      "short": {"x": ["naive"]} if short else {}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e471.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: one configuration at two budgets, the sequence raising the reading at both, and the far point more
    j = _judge()
    for cid in ("XA1", "XA2", "XA3", "XA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # XA1: another field differing, a held-out task whose counts differ between the budgets, thin replicates, short arms
    assert _judge(same_differ="bio.circuit_size")["XA1"].startswith("FALSIFIER")
    assert _judge(counts_differ="n_train")["XA1"].startswith("FALSIFIER")
    assert _judge(counts_differ="task")["XA1"].startswith("FALSIFIER")
    assert _judge(thin=True)["XA1"].startswith("FALSIFIER")
    assert _judge(short=True)["XA1"].startswith("FALSIFIER")

    # XA2: a change at a hundred updates that does not resolve
    assert _judge(change_sigma=1.20)["XA2"].startswith("FALSIFIER")

    # XA3: a growth that does not resolve
    assert _judge(grow_sigma=1.40)["XA3"].startswith("FALSIFIER")
    assert _judge(grow_sigma=-6.00)["XA3"].startswith("FALSIFIER")

    # XA4: an anchor that resolves against its own baseline, in either direction
    assert _judge(versus_sigma=-2.40)["XA4"].startswith("FALSIFIER")
    assert _judge(versus_sigma=2.40)["XA4"].startswith("FALSIFIER")
    assert _judge(versus_sigma=-1.90)["XA4"].startswith("MET")

    #: a roll that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e471.judge(_doc(ok=False)))


def test_the_runs_the_budgets_and_the_bounds_are_registered():
    assert e471.RUNS["100/bio"].name == "e471_earned_label_neurons_holdout_iters100_20reps.json"
    assert e471.RUNS["100/rand"].name == "e471_earned_label_rand_neurons_holdout_iters100_20reps.json"
    assert e471.RUNS["500/bio"].name == "e469_earned_label_neurons_holdout_20reps.json"
    assert e471.RUNS["500/rand"].name == "e469_earned_label_rand_neurons_holdout_20reps.json"
    assert e471.BUDGETS == (100, 500), e471.BUDGETS
    assert e471.BK == ("100", "500"), e471.BK
    assert e471.ANCHOR_OF == {"bio": "ewc-block", "rand": "ewc-block-rand"}, e471.ANCHOR_OF
    assert (e471.BASELINE, e471.BUFFER, e471.SIGMA) == ("naive", "replay", 2.0)
    #: the update count is the only field a budget may move in, and the counts are read as equalities
    assert set(e471.IGNORED) == {"iters", "json_out", "save_theta"}, e471.IGNORED
    assert (e471.N_ARMS, e471.MIN_REPS) == (3, 20)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e471_the_held_out_task_at_a_fifth_of_the_budget.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e471.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: four rolls at twenty replicates is structural; the counts that grow with the corpus are read as floors
    assert sorted(d["curve"]) == list(e471.BK), sorted(d["curve"])
    for b, sides in d["curve"].items():
        assert sorted(sides) == sorted(SIDES), (b, sorted(sides))
        for side, cell in sides.items():
            assert cell["budget"] == int(b) and cell["side"] == side, (b, side)
            assert set(cell["arms"]) == {e471.BASELINE, e471.ANCHOR_OF[side], e471.BUFFER}, (b, side)
            for arm, got in cell["arms"].items():
                assert 0.0 <= got["initial"] <= 1.0 and 0.0 <= got["trained"] <= 1.0, (b, side, arm)
    assert d["spans"]["tasks"] == ["loop_holdout"], d["spans"]["tasks"]
    assert sorted(d["paired"]) == sorted(SIDES), sorted(d["paired"])
    assert d["spans"]["same_fields"] >= 20, d["spans"]["same_fields"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
