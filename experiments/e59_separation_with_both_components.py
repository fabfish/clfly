"""E59 — the ER separation with BOTH variance components, which is neither 152σ nor 244σ.

The paper's most dramatic quantity is the Erdős–Rényi separation: `excess(ER)` against `excess(swap2)`
at cs = 800, published at **152σ**. That figure is the *seed* sem of a single realization of each
graph, and `e39` since measured the missing component — the realization-to-realization sd, 0.00320 for
ER and 0.00377 for `swap2` over six realizations each.

A single realization's variance is the sum of its within-realization (seed) variance and its
across-realization variance, so both belong in the error bar. This script composes them, and does the
same for the `swap0.5 → swap2` contrast so the two headline figures are on one footing.

    python -m experiments.e59_separation_with_both_components
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

#: The six-seed cs = 800 run with per-seed storage, and the two six-realization sweeps.
REFERENCE = "runs/e48_cs800_perseed.json"
REALIZATIONS = {"swap2": "runs/e32_rewire%d.json", "erdos_renyi": "runs/e33_er_rewire%d.json"}
N_REAL = 6


def load(path: str):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def per_seed(entry, topo: str):
    t = entry["topologies"].get(topo)
    if t is None:
        return None
    return np.array(t["diagonal(EWC)"]["analytic"]["excess_per_seed"], dtype=float)


def realization_means(pattern: str, topo: str) -> np.ndarray:
    out = []
    for s in range(N_REAL):
        e = load(pattern % s)
        if e is None:
            continue
        t = e["topologies"].get(topo)
        if t is None:
            continue
        out.append(float(t["diagonal(EWC)"]["analytic"]["excess_mean"]))
    return np.array(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-out", default="runs/e59_separation_components.json")
    args = ap.parse_args()

    ref = load(REFERENCE)
    if ref is None:
        print(f"{REFERENCE} absent (runs/ is gitignored); nothing to do")
        return

    tops = ("swap2", "erdos_renyi", "swap0.5")
    summary = {}
    print("=" * 100)
    print("1. THE TWO VARIANCE COMPONENTS, PER TOPOLOGY, AT cs = 800")
    print("=" * 100)
    print("   seed variance comes from six seeds of one wiring; realization variance from six")
    print("   wirings at the same circuit size.  A single point carries both.\n")
    print(f"   {'topology':<14}{'mean':>10}{'seed sem':>10}{'realization sd':>17}"
          f"{'total sd':>11}{'seed share':>12}")
    for topo in tops:
        ps = per_seed(ref, topo)
        rm = realization_means(REALIZATIONS.get(topo, ""), topo) if topo in REALIZATIONS else np.array([])
        if ps is None:
            continue
        seed_sem = float(ps.std(ddof=1) / np.sqrt(len(ps)))
        real_sd = float(rm.std(ddof=1)) if len(rm) > 1 else float("nan")
        total = float(np.sqrt(seed_sem ** 2 + real_sd ** 2)) if np.isfinite(real_sd) else seed_sem
        share = float(seed_sem ** 2 / total ** 2) if total else float("nan")
        print(f"   {topo:<14}{ps.mean():>10.5f}{seed_sem:>10.5f}{real_sd:>17.5f}"
              f"{total:>11.5f}{share:>11.0%}")
        summary[topo] = dict(mean=float(ps.mean()), seed_sem=seed_sem, realization_sd=real_sd,
                             total_sd=total, seed_variance_share=share, n_seeds=len(ps),
                             n_realizations=len(rm))

    print()
    print("=" * 100)
    print("2. THE TWO HEADLINE FIGURES, RE-SIGMAED — AND THE QUESTION EACH σ ANSWERS")
    print("=" * 100)
    print("   both endpoints come from the same six task seeds of one wiring, so there are two")
    print("   legitimate error bars and they answer different questions:\n")
    print("     about THESE TWO GRAPHS   the paired sem of the within-seed difference, which")
    print("                              cancels the task draw but not the wiring")
    print("     about the REWIRING RULE  the same, composed with each endpoint's realization sd")
    pairs = [("erdos_renyi", "swap2", "the ER separation"),
             ("swap0.5", "swap2", "the C1 contrast")]
    for a, b, label in pairs:
        if a not in summary or b not in summary:
            continue
        ps_a, ps_b = per_seed(ref, a), per_seed(ref, b)
        if ps_a is None or ps_b is None:
            continue
        n = min(len(ps_a), len(ps_b))
        delta = ps_b[:n] - ps_a[:n]          # b minus a, paired on the seed
        gap = float(delta.mean())
        paired = float(delta.std(ddof=1) / np.sqrt(n))
        across = float(np.hypot(summary[a]["total_sd"], summary[b]["total_sd"]))
        print(f"   {label}: {b} minus {a}")
        print(f"     gap                                  {gap:+.5f}")
        print(f"     sigma about THESE GRAPHS (paired, n={n}) {abs(gap) / paired:>8.1f}"
              f"   [published figure was the unpaired seed-only one]")
        print(f"     sigma about the REWIRING RULE        {abs(gap) / across:>8.1f}"
              f"   ({paired / across:.2f}x the within-graph figure)")
        summary[label] = dict(gap=gap, paired_sem=paired, across_sd=across,
                              sigma_within_graph=abs(gap) / paired,
                              sigma_across_graph=abs(gap) / across,
                              ratio=paired / across)
        print()

    print("   The 152σ in the paper is the seed-only, unpaired figure for two single realizations.")
    print("   The honest pair of statements is a few tens of sigma about these graphs and about")
    print("   twenty-six sigma about the rewiring rule for ER — and, for the C1 contrast, a")
    print("   resolved within-graph difference that is at best marginal once the wiring draw is")
    print("   included.  That is exactly the distinction e34 introduced and e36-e40 spent four")
    print("   experiments sharpening: a σ about a graph is not a σ about a rule.")
    print("\n   Note what this does NOT change: `e42`'s and `e56`'s finding that the RELATIVE gap can")
    print("   be a statement about the oracle.  That is a different pathology — the denominator — and")
    print("   the figures above are in absolute excess throughout.")
    print("\n   And one gap this exposes: `swap0.5` has NO realization sweep, so its realization sd is")
    print("   unmeasured and enters as zero.  The across-graph σ above is therefore a LOWER BOUND on")
    print("   the uncertainty, and a six-realization sweep of `swap0.5` is the one run that would")
    print("   settle the C1 contrast's magnitude.")

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
