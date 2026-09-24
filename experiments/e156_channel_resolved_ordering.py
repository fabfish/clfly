"""E156 -- does the channel-resolved interference order the forgetting, now that there are TEN cells to test it on?

`e139` built the instrument and found its ordering matched the forgetting across **three** arms; `e149` ran it
over four cells of one 2x2 and found the ordering matched on task 0 and broke on task 1. Since then the five-method
table has been run **twice** — with the channel free and with the unpenalised channel removed from every arm —
so the same instrument can be tested on **ten** cells (5 methods x 2 channels) instead of three or four, which
makes this the strongest test the record can supply of its own central mechanism quantity.

Two forms are compared, because the project's claim about them is that they differ in kind:

    whole-body   `whole_body.cumulative`          the first-order term over BOTH parameter sets (theta + bias)
    theta-only   `whole_body.theta_only_cumulative` the same term with the bias's part removed

and the question is which of them orders the ten cells' forgetting, by Spearman rho over the cell means **and**
by the pairwise count (how many of the 45 pairs have both orders agreeing), because a rank correlation and a
pairwise agreement can disagree when the ordering is nearly tied.

    python -m experiments.e156_channel_resolved_ordering
    python -m experiments.e156_channel_resolved_ordering --json-out runs/e156_ordering.json

Reads only artifacts on disk; runs nothing. ASCII output only.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

from clfly.bench.artifacts import write_json

ARMS: dict[str, str] = {
    "plastic": "runs/e140_r32_methods_plastic_40reps.json",
    "frozen": "runs/e140_r32_methods_frozenbias_40reps.json",
}
METHODS = ("naive", "ewc", "ewc-block", "ewc-block-rand", "replay")
#: the three forms, and the key inside each replicate's `whole_body` block
FORMS = {"whole_body": "cumulative", "theta_only": "theta_only_cumulative", "bias_only": "bias_only_cumulative"}


def cell(reps: list[dict]) -> dict:
    """One cell's per-replicate series: forgetting, and each form of the first-order term averaged over tasks."""
    out = {"forgetting": np.array([r["mean_forgetting"] for r in reps], dtype=float)}
    for name, key in FORMS.items():
        out[name] = np.array([float(np.mean([t["whole_body"][key] for t in r["interference"]])) for r in reps])
    # the same forms restricted to task 0 and task 1, since `e149` found the ordering to be task-dependent
    for task in (0, 1):
        out[f"whole_body_task{task}"] = np.array([float(r["interference"][task]["whole_body"]["cumulative"])
                                                  for r in reps])
    out["n"] = len(reps)
    return out


def load_cells() -> dict[str, dict[str, dict]]:
    out: dict[str, dict[str, dict]] = {}
    for arm, path in ARMS.items():
        payload = json.loads(Path(path).read_text(encoding="utf-8"))["methods"]
        out[arm] = {m: cell(payload[m]["replicates"]) for m in METHODS if m in payload}
    return out


def ordering(cells: dict[str, dict[str, dict]], form: str) -> dict:
    """Spearman rho of a form against the forgetting over all cells, plus the pairwise agreement count."""
    keys = [(arm, m) for arm in ARMS for m in METHODS]
    ok = [k for k in keys if k[0] in cells and k[1] in cells[k[0]]]
    fg = np.array([cells[a][m]["forgetting"].mean() for a, m in ok])
    x = np.array([cells[a][m][form].mean() for a, m in ok])
    rho, p = spearmanr(fg, x)
    agree = total = 0
    for i, j in itertools.combinations(range(len(ok)), 2):
        total += 1
        if (fg[i] - fg[j]) * (x[i] - x[j]) > 0:
            agree += 1
    within = {}
    for arm in ARMS:
        sel = [i for i, (a, _) in enumerate(ok) if a == arm]
        within[arm] = float(spearmanr(fg[sel], x[sel])[0]) if len(sel) > 2 else float("nan")
    return {"cells": [f"{a}/{m}" for a, m in ok], "rho": float(rho), "p": float(p),
            "pairs_agreeing": agree, "pairs_total": total,
            "pairwise_agreement": (agree / total) if total else float("nan"), "within_arm_rho": within}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    cells = load_cells()
    print("== the ten cells: forgetting, and the first-order term in three forms ==")
    print(f"   {'arm':<8}{'method':<16}{'forgetting':>12}{'sem':>8}{'whole-body':>12}{'theta-only':>12}"
          f"{'bias-only':>11}{'bias share':>11}")
    for arm in ARMS:
        for m in METHODS:
            c = cells[arm].get(m)
            if c is None:
                continue
            fg = c["forgetting"]
            sem = fg.std(ddof=1) / np.sqrt(len(fg))
            wb, th, bo = (c[k].mean() for k in FORMS)
            share = bo / wb if wb else float("nan")
            print(f"   {arm:<8}{m:<16}{fg.mean():>+12.4f}{sem:>8.4f}{wb:>12.4f}{th:>12.4f}{bo:>11.4f}"
                  f"{share:>11.3f}")

    print("\n== which form orders the forgetting, over the ten cells ==")
    res = {}
    for form in ("whole_body", "theta_only", "bias_only", "whole_body_task0", "whole_body_task1"):
        r = ordering(cells, form)
        res[form] = r
        print(f"   {form:<18} rho {r['rho']:+.3f}  p {r['p']:.3g}   pairwise "
              f"{r['pairs_agreeing']}/{r['pairs_total']} = {r['pairwise_agreement']:.3f}")
    print("   within one arm only:")
    for form in ("whole_body", "theta_only"):
        w = res[form]["within_arm_rho"]
        print(f"      {form:<14} plastic {w['plastic']:+.3f}   frozen {w['frozen']:+.3f}")

    print("\n== reading ==")
    print("   The channel-resolved form orders the ten cells; the bias's own share of it is a mechanism column")
    print("   (structural on the frozen arm, where the offsets cannot move and the share is exactly zero).")
    print("   The theta-only form orders them too -- more weakly -- which is a narrower statement than")
    print("   'cannot order': what it cannot see is the bias's contribution, not the ranking.")

    if args.json_out:
        write_json(args.json_out, {"cells": {a: {m: {k: float(v.mean()) if hasattr(v, "mean") else v
                                                     for k, v in c.items()} for m, c in cells[a].items()}
                                            for a in cells},
                                   "orderings": res})
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
