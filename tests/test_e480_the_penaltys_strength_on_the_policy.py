"""`e480` walks a ladder of penalty strengths on the policy's sequence, so the tests pin both faces of the four
claims, the shape of the ladder, and the refusal when it was not walked.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

from experiments import e480_the_penaltys_strength_on_the_policy as e480

LAMS = e480.LAMS
KEYS = [e480.key(l) for l in LAMS]
ZERO, TOP = KEYS[0], KEYS[-1]
SMALL = KEYS[1]
REPS = (0, 1, 2, 3)
#: a ladder whose diagonal falls and whose last row rises, so the four claims have a shape to read
DIAG = {-7.48: None}
DIAG_BY_KEY = {"0": -7.48, "0.0003": -7.50, "0.003": -7.60, "0.03": -7.90, "0.3": -8.30, "1": -8.63}
LAST_BY_KEY = {"0": -8.95, "0.0003": -8.90, "0.003": -8.72, "0.03": -8.50, "0.3": -8.42, "1": -8.41}


def _paired(mean, sigma, n=len(REPS)):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.02, "sigma": sigma}


def _cell(seed, k):
    j = 0.1 * ((seed + len(k)) % 4)
    diag = DIAG_BY_KEY[k] + j
    last = LAST_BY_KEY[k] + j
    R = [[-9.0, -8.0, -7.0], [None] * 3, [None] * 3, [None] * 3]
    for i in range(3):
        R[i + 1][i] = diag - 0.2 * i
        for jj in range(i):
            R[i + 1][jj] = last
    return {"seed": seed, "arm": "penalty", "n_act": 8, "identity_bitwise": True, "identity_max_abs": 0.0,
            "R": R, "policy_move": 12.0, "targets_sha1": f"t{seed}"}


def _doc(ok=True, identity_all=True, identity_worst=0.0, naive_present=True, naive_bitwise=True, naive_worst=0.0,
         diagonal=None, last_row=None, free=None, seeds=None, targets=None):
    if not ok:
        return {"ok": False, "reason": "the ladder was not walked", "cells": [], "mean_R": {}, "diagonal": {},
                "last_row": {}, "learned": {}, "ladder": {}, "naive_check": {}, "spans": {}, "worlds": {}}
    diagonal = dict(diagonal or DIAG_BY_KEY)
    last_row = dict(last_row or LAST_BY_KEY)
    zero, top, small = ZERO, TOP, SMALL
    nonzero = KEYS[1:]
    free = [k for k in nonzero if diagonal[k] >= diagonal[zero] - e480.FREE] if free is None else free
    return {
        "ok": True, "reason": None, "cells": [_cell(s, k) for s in REPS for k in KEYS],
        "mean_R": {k: [[-9.0, -8.0, -7.0], [diagonal[k], None, None], [last_row[k], last_row[k], None],
                       [last_row[k], last_row[k], diagonal[k]]] for k in KEYS},
        "diagonal": {k: [diagonal[k]] * len(REPS) for k in KEYS},
        "last_row": {k: [last_row[k]] * len(REPS) for k in KEYS},
        "learned": {k: {f"task{i}": _paired(1.5, 6.0) for i in range(3)} for k in KEYS},
        "ladder": {"zero": zero, "top": top, "smallest_nonzero": small, "nonzero": nonzero,
                   "diagonal": diagonal, "last_row": last_row,
                   "cost_top_over_smallest": _paired(diagonal[small] - diagonal[top], 9.0),
                   "retention_top_over_zero": _paired(last_row[top] - last_row[zero], 8.0),
                   "cost_by_strength": {k: _paired(diagonal[zero] - diagonal[k], 10.0) for k in nonzero},
                   "free": free, "free_none": len(free) == 0},
        "naive_check": {"present": naive_present, "worst_abs": naive_worst if naive_present else None,
                        "bitwise": naive_bitwise if naive_present else None},
        "spans": {"lams": KEYS, "replicates": len(REPS), "tasks": 3, "n_act": 8, "identity_all": identity_all,
                  "identity_worst": identity_worst, "cells": len(KEYS) * len(REPS),
                  "seeds": list(seeds if seeds is not None else REPS),
                  "targets": list(targets if targets is not None else sorted({f"t{s}" for s in REPS})),
                  "moves": {k: [12.0] * len(REPS) for k in KEYS}},
        "worlds": {"chance": 0.25},
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e480.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: one configuration, a cost that grows with the strength, a strength at which it is free, and a
    #: retention bought at the top
    j = _judge()
    for cid in ("LA1", "LA2", "LA3", "LA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # LA1: a first step that is not the corpus's rule, a zero point that does not reproduce e479's naive arm, a
    # missing artifact, and a seed or target draw that does not match
    assert _judge(identity_all=False)["LA1"].startswith("FALSIFIER")
    assert _judge(identity_worst=1e-09)["LA1"].startswith("FALSIFIER")
    assert _judge(naive_bitwise=False, naive_worst=1.8)["LA1"].startswith("FALSIFIER")
    assert _judge(naive_present=False)["LA1"].startswith("REFUSED")
    assert _judge(seeds=(0, 1, 2))["LA1"].startswith("FALSIFIER")
    assert _judge(targets=("t0",))["LA1"].startswith("FALSIFIER")

    # LA2: a top strength that costs what the smallest one does -- flat fires it, and a gap between the bands is a null
    flat = {k: -7.5 for k in KEYS}
    assert _judge(diagonal=flat)["LA2"].startswith("FALSIFIER")
    mid = dict(DIAG_BY_KEY); mid[TOP] = DIAG_BY_KEY[SMALL] - 0.35
    assert _judge(diagonal=mid)["LA2"].startswith("NULL")

    # LA3: no strength free -- every non-zero one at least the bar below the zero point
    steep = {ZERO: -7.0, **{k: -8.6 for k in KEYS[1:]}}
    assert _judge(diagonal=steep)["LA3"].startswith("FALSIFIER")
    #: none free but none that far below is the null
    middling = {ZERO: -7.0, **{k: -7.35 for k in KEYS[1:]}}
    assert _judge(diagonal=middling)["LA3"].startswith("NULL")
    assert _judge(diagonal=mid)["LA3"].startswith("MET")

    # LA4: a top strength that retains no more than the zero point fires it, and a gap between the bands is a null
    no_ret = dict(LAST_BY_KEY, **{TOP: LAST_BY_KEY[ZERO]})
    assert _judge(last_row=no_ret)["LA4"].startswith("FALSIFIER")
    small_ret = dict(LAST_BY_KEY, **{TOP: LAST_BY_KEY[ZERO] + 0.35})
    assert _judge(last_row=small_ret)["LA4"].startswith("NULL")

    #: a ladder that was not walked refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e480.judge(_doc(ok=False)))


def test_the_ladder_the_bars_and_the_reused_arm_are_registered():
    assert e480.LAMS == (0.0, 3e-4, 3e-3, 0.03, 0.3, 1.0), e480.LAMS
    assert (e480.SIGMA, e480.BAR, e480.FLOOR, e480.FREE) == (2.0, 0.50, 0.20, 0.20)
    assert e480.TASKS == 3 and e480.REPLICATES == (0, 1, 2, 3, 4, 5, 6, 7)
    assert e480.E479.name == "e479_the_methods_on_the_policys_sequence.json"
    #: the arm this ladder drives is e479's own, and its strength is a parameter of it
    import inspect
    from experiments import e479_the_methods_on_the_policys_sequence as e479m
    sig = inspect.signature(e479m.one_arm)
    assert "lam" in sig.parameters, sorted(sig.parameters)
    assert sig.parameters["lam"].default == e479m.LAM == 1.0, sig.parameters["lam"]


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e480_the_penaltys_strength_on_the_policy.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e480.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    keys = [e480.key(l) for l in e480.LAMS]
    assert d["spans"]["lams"] == keys, d["spans"]["lams"]
    assert d["spans"]["replicates"] == len(e480.REPLICATES), d["spans"]["replicates"]
    assert d["spans"]["cells"] == len(keys) * len(e480.REPLICATES), d["spans"]["cells"]
    assert d["spans"]["identity_all"] is True and d["spans"]["identity_worst"] == 0.0, d["spans"]
    assert sorted(d["mean_R"]) == sorted(keys), sorted(d["mean_R"])
    for k in keys:
        rows = d["mean_R"][k]
        assert len(rows) == e480.TASKS + 1, (k, len(rows))
        for i, row in enumerate(rows):
            assert len(row) == e480.TASKS, (k, i, row)
            for j, x in enumerate(row):
                assert (x is not None) == ((i == 0) or (j <= i - 1)), (k, i, j, x)
    assert d["ladder"]["zero"] == keys[0] and d["ladder"]["top"] == keys[-1], d["ladder"]
    assert d["ladder"]["nonzero"] == keys[1:], d["ladder"]["nonzero"]
    assert d["ladder"]["smallest_nonzero"] == keys[1], d["ladder"]["smallest_nonzero"]
    assert d["naive_check"]["present"] is True, d["naive_check"]
    assert set(d["ladder"]["cost_by_strength"]) == set(keys[1:]), sorted(d["ladder"]["cost_by_strength"])
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
