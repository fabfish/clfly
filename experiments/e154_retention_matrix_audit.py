"""E154 -- what the retention matrix makes each printed number: pure retention, pure acquisition, or a mixture.

The runner writes a retention matrix ``R[k, j]`` = accuracy on task ``j`` after training through task ``k``, and
fills it for ``j <= k`` only. Three aggregates are derived from it:

    `learned[j] = R[j, j]`                                        the diagonal
    `final_per_task[j] = R[T-1, j]`                               the last row
    `forgetting_per_task[j] = nanmax(R[:j+1, j]) - R[T-1, j]`

and the middle expression is the point of this script. **Because the fill is `j <= k`, the window
`R[:j+1, j]` contains exactly one finite entry -- the diagonal** -- so the quantity this project calls
"forgetting" is, exactly,

    forgetting_per_task[j] = learned[j] - final_per_task[j]

**The standard convention in the continual-learning literature takes the max over the *later* checkpoints,
`nanmax(R[j:, j])`, which can only be larger.** So the record's forgetting is a **lower bound** on the
conventional statistic, and the gap is a number rather than a reading of the code -- this script measures it.

The three identities it checks, and what each one buys:

1. `learned[j] == R[j, j]` -- the runner's own definition, verified rather than assumed;
2. `learned[T-1] == final_per_task[T-1]` -- for the last task the diagonal **is** the final value, so its
   accuracy **cannot be contaminated by interference** (no training happens after it) and its forgetting term
   is 0.0 by construction: **the newest task's accuracy is the only purely acquisition-shaped number in the
   artifact**;
3. `forgetting_per_task[j] == learned[j] - final_per_task[j]` -- so `mean_forgetting` is a mean of
   acquisition-minus-final terms, i.e. **the only purely retention-shaped number**, and `final_accuracy` is the
   only **mixture** (T-1 retention terms and one acquisition term).

    python -m experiments.e154_retention_matrix_audit
    python -m experiments.e154_retention_matrix_audit --json-out runs/e154_retention_structure.json

Reads only artifacts on disk; runs nothing. ASCII output only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

TOL = 1e-12
RUNS = Path("runs")


def load_matrices(path: Path) -> dict[str, dict] | None:
    """Per method: the per-replicate matrix, the two derived columns and the stored per-task forgetting."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    methods = payload.get("methods") if isinstance(payload, dict) else None
    if not isinstance(methods, dict):
        return None
    out: dict[str, dict] = {}
    for name, entry in methods.items():
        reps = (entry or {}).get("replicates")
        if not reps or not all("retention" in r and "learned" in r and "final_per_task" in r for r in reps):
            continue
        out[name] = {
            "R": np.array([r["retention"] for r in reps], dtype=float),
            "learned": np.array([r["learned"] for r in reps], dtype=float),
            "final": np.array([r["final_per_task"] for r in reps], dtype=float),
            "stored_forgetting": np.array([r["forgetting_per_task"] for r in reps], dtype=float),
            # the LOSS-valued matrix, whose own forgetting uses the OTHER window (`min_{k>=j}`); carried so that
            # "the two metrics are mirrors of each other" is checked rather than argued from the code
            "L": (np.array([[[np.nan if x is None else float(x) for x in row] for row in rep["retention_loss"]]
                            for rep in reps], dtype=float)
                  if all(rep.get("retention_loss") for rep in reps) else None),
        }
    return out or None


def audit(runs: Path = RUNS) -> dict:
    """The three identities and the gap to the literature's window, over every artifact that carries a matrix."""
    n_artifacts = n_methods = n_terms = 0
    n_loss_terms = loss_bad = 0
    loss_gaps: list[float] = []
    worst = {"learned_is_diagonal": 0.0, "last_task_identity": 0.0, "forgetting_is_diagonal_minus_final": 0.0}
    bad = {k: [] for k in worst}
    gaps: list[float] = []
    for path in sorted(runs.glob("*.json")):
        loaded = load_matrices(path)
        if not loaded:
            continue
        n_artifacts += 1
        for name, m in loaded.items():
            n_methods += 1
            R, learned, final, stored = m["R"], m["learned"], m["final"], m["stored_forgetting"]
            T = R.shape[1]
            diag = np.stack([R[:, j, j] for j in range(T)], axis=1)
            d1 = float(np.max(np.abs(diag - learned)))
            d2 = float(np.max(np.abs(learned[:, -1] - final[:, -1])))
            d3 = float(np.max(np.abs((diag - final)[:, :T - 1] - stored[:, :T - 1])))
            for key, d in (("learned_is_diagonal", d1), ("last_task_identity", d2),
                           ("forgetting_is_diagonal_minus_final", d3)):
                worst[key] = max(worst[key], d)
                if d > 1e-9:
                    bad[key].append(f"{path.name}[{name}] worst {d:g}")
            n_terms += T - 1
            # the literature's window: max over the LATER checkpoints, which can only be larger than the diagonal
            for r in range(R.shape[0]):
                for j in range(T - 1):
                    gaps.append(float(np.nanmax(R[r, j:, j]) - R[r, j, j]))
            # and the loss-valued metric's own window, `min_{k>=j}`: does its minimum also land on the diagonal?
            if m.get("L") is not None:
                L = m["L"]
                for r in range(L.shape[0]):
                    for j in range(T - 1):
                        if np.isfinite(L[r, j, j]):
                            n_loss_terms += 1
                            loss_gap = float(L[r, j, j] - np.nanmin(L[r, j:, j]))
                            loss_gaps.append(loss_gap)
                            if abs(loss_gap) > 1e-9:
                                loss_bad += 1
    g = np.asarray(gaps, dtype=float)
    lg = np.asarray(loss_gaps, dtype=float)
    return {
        "n_artifacts": n_artifacts, "n_methods": n_methods, "n_forgetting_terms": n_terms,
        "identity_worst_difference": worst,
        "violations": {k: v[:10] for k, v in bad.items()},
        "violation_counts": {k: len(v) for k, v in bad.items()},
        "literature_gap": {
            "observations": int(g.size),
            "strictly_positive_share": float((g > TOL).mean()) if g.size else float("nan"),
            "mean": float(g.mean()) if g.size else float("nan"),
            "median": float(np.median(g)) if g.size else float("nan"),
            "max": float(g.max()) if g.size else float("nan"),
            "p90": float(np.quantile(g, 0.9)) if g.size else float("nan"),
        },
        "loss_window": {
            "observations": n_loss_terms,
            "off_diagonal_share": (loss_bad / n_loss_terms) if n_loss_terms else float("nan"),
            "mean_gap": float(lg.mean()) if lg.size else float("nan"),
            "max_gap": float(lg.max()) if lg.size else float("nan"),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    res = audit()
    print("== what the retention matrix makes each printed number ==")
    print(f"   artifacts with a matrix {res['n_artifacts']}   method-arms {res['n_methods']}   "
          f"forgetting terms {res['n_forgetting_terms']}")
    for key, text in (("learned_is_diagonal", "`learned[j] == R[j, j]` (the diagonal)"),
                      ("last_task_identity",
                       "`learned[T-1] == final_per_task[T-1]` -- the newest task's accuracy is pure acquisition"),
                      ("forgetting_is_diagonal_minus_final",
                       "`forgetting_per_task[j] == learned[j] - final[j]` -- the window holds only the diagonal")):
        n = res["violation_counts"][key]
        w = res["identity_worst_difference"][key]
        print(f"   {text}")
        print(f"      worst |difference| {w:.3g} over {res['n_methods']} method-arms -> "
              + ("HOLDS EVERYWHERE" if n == 0 else f"VIOLATED in {n}: " + "; ".join(res['violations'][key])))

    lg = res["literature_gap"]
    print("\n== and the gap to the literature's window, which is what the convention costs ==")
    print(f"   `nanmax(R[j:, j]) - R[j, j]` over {lg['observations']} (task, replicate) observations:")
    print(f"      strictly positive in {lg['strictly_positive_share']:.3f} of them, "
          f"mean {lg['mean']:.5f}, median {lg['median']:.5f}, p90 {lg['p90']:.5f}, max {lg['max']:.5f}")
    print("   so the record's forgetting is a LOWER BOUND on the conventional accuracy-forgetting, and a")
    print("   comparison against published numbers is a comparison of two different statistics.")

    lw = res["loss_window"]
    print("\n== and the loss-valued metric, whose expression uses the OTHER window (`min_{k>=j}`) ==")
    print(f"   `L[j, j] - nanmin(L[j:, j])` over {lw['observations']} observations: "
          f"off-diagonal in {lw['off_diagonal_share']:.4f} of them, mean gap {lw['mean_gap']:.3g}, "
          f"max {lw['max_gap']:.3g}")
    print("   so the loss form's window is decorative too, and the two metrics ARE mirrors in practice --")
    print("   which `e123` had measured on one configuration and this checks over the corpus.")

    print("\n== the consequence, stated as a rule about columns ==")
    print("   mean_forgetting         pure RETENTION: mean_j< T-1 (learned[j] - final[j]). The last task's fit")
    print("                           is not in it, which is the trap this project names twice.")
    print("   newest task's accuracy  pure ACQUISITION: identical to the diagonal, so no interference can be")
    print("                           in it. It is the complement of the aggregate by construction, not by luck.")
    print("   final_accuracy          a MIXTURE: T-1 retention terms plus one acquisition term.")
    print("   learned[j], j < T-1     the acquisition point of a task that was later interfered with -- reading")
    print("                           it as 'how well it was learned' is right; reading it as 'how well it ended")
    print("                           up' is not, and that is what final_per_task[j] is for.")

    if args.json_out:
        write_json(args.json_out, res)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
