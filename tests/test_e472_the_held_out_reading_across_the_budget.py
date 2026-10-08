"""`e472` reads the held-out task across four budgets, so the tests pin both faces of the four claims, the shape of the
curve, and the refusal when a roll is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e472_the_held_out_reading_across_the_budget as e472

SIDES = e472.SIDES
BUDGETS = e472.BUDGETS
#: the shape: no budget below its predecessor, and the first doubling carrying most of the whole change
TRAINED = {100: 0.7594, 200: 0.7680, 350: 0.7700, 500: 0.7719}
INITIAL = 0.6875


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.01, "sigma": sigma}


def _doc(same_differ=None, trained=None, versus_sigma=-0.86, counts_differ=None, thin=False, short=False, ok=True,
         reason="a roll is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "curve": {}, "steps": {}, "spans": {}}
    seq = dict(TRAINED if trained is None else trained)
    curve = {}
    for b in BUDGETS:
        curve[str(b)] = {}
        for side in SIDES:
            anchor = e472.ANCHOR_OF[side]
            arms = {}
            for arm in (e472.BASELINE, anchor, e472.BUFFER):
                trained_v = seq[b] if arm == e472.BASELINE else seq[b] - 0.005
                arms[arm] = {"initial": INITIAL, "trained": trained_v,
                             "change": _paired(trained_v - INITIAL, 8.0),
                             "against_baseline": _paired(0.0 if arm == e472.BASELINE else -0.005,
                                                         0.0 if arm == e472.BASELINE else versus_sigma)}
            curve[str(b)][side] = {"budget": b, "side": side, "anchor": anchor, "initial": INITIAL,
                                   "trained": seq[b], "change": _paired(seq[b] - INITIAL, 8.0), "arms": arms}
    same = {f"{side}.{k}": True for side in SIDES for k in ("circuit_size", "readout_size", "repeats")}
    same.update({f"{side}.circuit": True for side in SIDES})
    same.update({f"{side}.tasks": True for side in SIDES})
    if same_differ:
        same[same_differ] = False
    task, n_train, n_eval, ridge = ["loop_holdout"], [96], [48], [0.01]
    base = {"task": task, "n_train": n_train, "n_eval": n_eval, "ridge": ridge}
    alt = {"task": ["loop_other"], "n_train": [48], "n_eval": [24], "ridge": [1e-3]}["n_train"]
    if counts_differ:
        alt = {"task": ["loop_other"], "n_train": [48], "n_eval": [24], "ridge": [1e-3]}[counts_differ]
    reps = 19 if thin else 20
    steps = {}
    for side in SIDES:
        vals = [seq[b] for b in BUDGETS]
        steps[side] = {"trained": vals, "first": vals[0], "total": vals[-1] - vals[0],
                       "steps": [vals[i + 1] - vals[i] for i in range(len(vals) - 1)],
                       "step_paired": {f"{BUDGETS[i]}-{BUDGETS[i + 1]}": _paired(vals[i + 1] - vals[i], 0.6)
                                       for i in range(len(BUDGETS) - 1)},
                       "whole_paired": _paired(vals[-1] - vals[0], 0.9),
                       "non_decreasing": all(vals[i + 1] >= vals[i] for i in range(len(vals) - 1))}
    return {"ok": True, "reason": None, "runs": {}, "same": same, "curve": curve, "steps": steps,
            "spans": {"budgets": list(BUDGETS), "sides": list(SIDES), "runs": 8, "same_fields": len(same),
                      "thin": {"x": reps} if thin else {}, "replicates": [reps], "tasks": task[:1] if counts_differ
                      else task,
                      "counts": {f"{b}/{side}/{arm}.{k}": (tuple(alt) if (counts_differ == k and b in (350, 500))
                                                          else tuple(base[k]))
                                 for b in BUDGETS for side in SIDES
                                 for arm in (e472.BASELINE, e472.ANCHOR_OF[side], e472.BUFFER)
                                 for k in ("task", "n_train", "n_eval", "ridge")},
                      "short": {"x": ["naive"]} if short else {}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e472.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: a non-decreasing curve whose first doubling carries most of the change, with the anchors null
    j = _judge()
    for cid in ("YA1", "YA2", "YA3", "YA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # YA1: another field differing, counts that differ between the budgets, thin replicates, a short arm list
    assert _judge(same_differ="bio.circuit_size")["YA1"].startswith("FALSIFIER")
    assert _judge(counts_differ="n_train")["YA1"].startswith("FALSIFIER")
    assert _judge(counts_differ="task")["YA1"].startswith("FALSIFIER")
    assert _judge(thin=True)["YA1"].startswith("FALSIFIER")
    assert _judge(short=True)["YA1"].startswith("FALSIFIER")

    # YA2: a budget below its predecessor, and one that plateaus
    assert _judge(trained={100: 0.7594, 200: 0.7550, 350: 0.7700, 500: 0.7719})["YA2"].startswith("FALSIFIER")
    assert _judge(trained={100: 0.7594, 200: 0.7594, 350: 0.7594, 500: 0.7594})["YA2"].startswith("MET")

    # YA3: a change that is back-loaded, and one between the bars
    assert _judge(trained={100: 0.7594, 200: 0.7614, 350: 0.7664, 500: 0.7719})["YA3"].startswith("FALSIFIER")
    assert _judge(trained={100: 0.7594, 200: 0.7632, 350: 0.7687, 500: 0.7719})["YA3"].startswith("NULL")
    assert _judge(trained={100: 0.7594, 200: 0.7680, 350: 0.7700, 500: 0.7719})["YA3"].startswith("MET")

    # YA4: an anchor that resolves against its own baseline, in either direction
    assert _judge(versus_sigma=-2.40)["YA4"].startswith("FALSIFIER")
    assert _judge(versus_sigma=2.40)["YA4"].startswith("FALSIFIER")
    assert _judge(versus_sigma=-1.90)["YA4"].startswith("MET")

    #: a roll that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e472.judge(_doc(ok=False)))


def test_the_runs_the_budgets_and_the_bounds_are_registered():
    assert e472.RUNS["200/bio"].name == "e472_earned_label_neurons_holdout_iters200_20reps.json"
    assert e472.RUNS["200/rand"].name == "e472_earned_label_rand_neurons_holdout_iters200_20reps.json"
    assert e472.RUNS["350/bio"].name == "e472_earned_label_neurons_holdout_iters350_20reps.json"
    assert e472.RUNS["350/rand"].name == "e472_earned_label_rand_neurons_holdout_iters350_20reps.json"
    assert e472.RUNS["100/bio"].name == "e471_earned_label_neurons_holdout_iters100_20reps.json"
    assert e472.RUNS["500/bio"].name == "e469_earned_label_neurons_holdout_20reps.json"
    assert e472.BUDGETS == (100, 200, 350, 500), e472.BUDGETS
    assert e472.BK == ("100", "200", "350", "500"), e472.BK
    assert e472.NEW == ("200", "350"), e472.NEW
    assert e472.ANCHOR_OF == {"bio": "ewc-block", "rand": "ewc-block-rand"}, e472.ANCHOR_OF
    assert (e472.BASELINE, e472.BUFFER, e472.SIGMA) == ("naive", "replay", 2.0)
    assert (e472.FRONT_LOADED, e472.FRONT_FLOOR) == (0.5, 0.25)
    assert set(e472.IGNORED) == {"iters", "json_out", "save_theta"}, e472.IGNORED
    assert (e472.N_ARMS, e472.MIN_REPS) == (3, 20)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e472_the_held_out_reading_across_the_budget.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e472.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: eight rolls at twenty replicates is structural; the counts that grow with the corpus are read as floors
    assert sorted(d["curve"]) == list(e472.BK), sorted(d["curve"])
    for b, sides in d["curve"].items():
        assert sorted(sides) == sorted(SIDES), (b, sorted(sides))
        for side, cell in sides.items():
            assert cell["budget"] == int(b) and cell["side"] == side, (b, side)
            assert set(cell["arms"]) == {e472.BASELINE, e472.ANCHOR_OF[side], e472.BUFFER}, (b, side)
            for arm, got in cell["arms"].items():
                assert 0.0 <= got["initial"] <= 1.0 and 0.0 <= got["trained"] <= 1.0, (b, side, arm)
    assert sorted(d["steps"]) == sorted(SIDES), sorted(d["steps"])
    for side, got in d["steps"].items():
        assert len(got["trained"]) == len(BUDGETS) and len(got["steps"]) == len(BUDGETS) - 1, (side, got)
    assert d["spans"]["tasks"] == ["loop_holdout"], d["spans"]["tasks"]
    assert d["spans"]["same_fields"] >= 20, d["spans"]["same_fields"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
