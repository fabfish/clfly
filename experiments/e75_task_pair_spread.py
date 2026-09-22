"""E75 -- does the control's excess MOVE WITH the partition's task alignment when the labels are reshuffled?

`e67` refuted the project's one-scalar model of the control's draw spread and `e72` refuted its
pre-registered replacement: the spread of `alignment_of`'s *excess over random subspaces* turned out to
be a monotone re-expression of the partition's span size (ρ = −0.904 with the span dimension), so it
carried almost nothing the scalar did not. Three candidates have now failed — group count, concentration
and the alignment spread — and all three are **functions of the partition alone**, while the draw spread
is a property of the *(partition, task)* pair.

`e72`'s diagnosis also says what to do differently in two ways, and this script does both:

* **no chance denominator.** `alignment_of` reports `raw / chance` with a *generic* random subspace as
  the denominator, which strips each partition's free size advantage and, on that measurement, the task
  information with it. Here the quantity is the bare `alignment_score` — mean `cos²θ` over principal
  angles between the indicator span and the task's own spectrally truncated subspace.
* **co-movement rather than spread.** The question is not whether the alignment *varies* across draws; it
  is whether the **control's excess** varies *with* it. A quantity can have a large spread and no
  relationship to the excess at all, which is exactly what `e72` found.

**The task draw must be held fixed or it swamps the measurement.** Both the alignment and the excess move
a great deal with the task geometry — that is what the seed sem measures — so a raw correlation across
pooled `(draw, seed)` pairs would be dominated by the seed dimension and would answer a question about
the tasks. Every correlation here is therefore computed **within a seed**, across draws, after centring
each variable by its own seed mean: that isolates the dimension a relabelling actually moves.

    python -m experiments.e75_task_pair_spread
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from clfly.bench.analytic import analytic_excess, spearman
from clfly.bench.control import concentration
from clfly.bench.oracle import task_subspaces
from clfly.connectome import annotate, circuits, graph, tasks
from clfly.lgcl.bases import alignment_score, random_partition

from experiments.e3_basis_selection import _pool_small_groups

#: The same nine partitions `e72` scored, with their measured excess draw sds (`e14`, `e17`, `e17b`,
#: `e67`, `e74`) so the new statistic is compared against a target already on disk.
PARTITIONS = [
    ("cell_type min 1", "cell_type", 1, 6.801960781803761e-05),
    ("cell_type min 2", "cell_type", 2, 0.0009286726398617035),
    ("cell_type min 3", "cell_type", 3, 0.0010104197596728626),
    ("cell_type min 4", "cell_type", 4, 0.00061304922373747),
    ("cell_type min 6", "cell_type", 6, 0.0007275845573211113),
    ("side", "side", 1, 0.00021569004909373701),
    ("cell_class", "cell_class", 1, 0.00023709633644934897),
    ("ito_lee_hemilineage", "ito_lee_hemilineage", 1, 4.158388952603153e-05),
    ("supertype", "supertype", 1, 8.350981282007466e-05),
]

#: The pre-registered numbers, from the plan's `e75` row.
PREDICTED_RHO = 0.8
PREDICTED_WITHIN = 0.5
CONCENTRATION_OF_ALIGNMENT_SPREAD = 0.850   # what `e72`'s normalised version achieved


def residualise(x: np.ndarray, seeds: np.ndarray) -> np.ndarray:
    """Remove each seed's own mean, so only the across-draw variation is left."""
    out = x.astype(float).copy()
    for s in np.unique(seeds):
        m = seeds == s
        out[m] -= out[m].mean()
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--circuit-size", type=int, default=800)
    ap.add_argument("--support", type=int, default=80)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--draws", type=int, default=6)
    ap.add_argument("--top", type=int, default=16)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--json-out", default="runs/e75_task_pair_spread.json")
    args = ap.parse_args()

    t0 = time.time()
    conn = graph.build()
    ann = annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=args.circuit_size)
    seqs, ranks = [], []
    for s in range(args.seeds):
        wt = tasks.build_tasks(circ, support_size=args.support, q=0.02, seed=s)
        seqs.append(wt.sequence)
        ranks.append(wt.ranks)
    U = [task_subspaces(seqs[s], ranks[s], top=args.top) for s in range(args.seeds)]
    print(f"circuit {circ.n_neurons} neurons, {args.seeds} task seeds, {args.draws} draws "
          f"({time.time()-t0:.0f}s)\n")

    specs = PARTITIONS[:args.limit] if args.limit else PARTITIONS
    rows = []
    for label, column, min_size, measured_sd in specs:
        if column not in circ.labels:
            print(f"  {label:<22} column absent")
            continue
        labels = np.asarray(circ.labels[column])
        if min_size > 1:
            labels = _pool_small_groups(labels, min_size)
        A, E, D, S = [], [], [], []
        for d in range(args.draws):
            rng = np.random.default_rng(20_000 + d)
            P = random_partition(labels, rng)
            Q = P.indicator_span()
            for s in range(args.seeds):
                A.append(float(np.mean([alignment_score(Q, V) for V in U[s]])))
                E.append(float(analytic_excess([seqs[s]], P)["excess_mean"]))
                D.append(d)
                S.append(s)
        A, E, D, S = map(np.asarray, (A, E, D, S))
        #: within-seed residual co-movement -- the only dimension a relabelling moves
        ar, er = residualise(A, S), residualise(E, S)
        pear = float(np.corrcoef(ar, er)[0, 1]) if ar.std() > 0 and er.std() > 0 else float("nan")
        spear = spearman(ar.tolist(), er.tolist())
        #: and per seed, so a single seed's pattern cannot carry the pooled number
        per_seed = []
        for s in np.unique(S):
            m = S == s
            if ar[m].std() > 0 and er[m].std() > 0:
                per_seed.append(float(np.corrcoef(ar[m], er[m])[0, 1]))
        conc = concentration(labels)
        rows.append(dict(label=label, column=column, min_size=min_size,
                         concentration=conc, measured_sd=measured_sd,
                         pearson=pear, spearman=spear, per_seed=per_seed,
                         n_pos_seed=sum(1 for v in per_seed if v > 0),
                         n_seed=len(per_seed),
                         #: Kept in the artifact rather than filtered out.  The first version of this
                         #: script dropped these four fields to keep the JSON small, which threw away
                         #: two hours of `analytic_excess` calls and made a later question -- does the
                         #: pressure co-move with the excess on the same (draw, seed) pairs? --
                         #: unanswerable without re-running the whole thing.  Storage is cheap here; a
                         #: recomputation is not, and this project has now lost a field three times.
                         alignment_values=A.tolist(), excess_values=E.tolist(),
                         draw_index=D.tolist(), seed_index=S.tolist()))
        print(f"  {label:<22} conc {conc:.3f}  alignment {A.mean():.4f}  excess {E.mean():.5f}  "
              f"within-seed co-movement: r {pear:+.3f}  rho {spear:+.3f}  "
              f"({rows[-1]['n_pos_seed']}/{rows[-1]['n_seed']} seeds positive)  "
              f"({time.time()-t0:.0f}s)")

    if len(rows) < 3:
        print("\n  too few partitions to order")
        return

    print()
    print("=" * 112)
    print("THE PRE-REGISTERED TEST")
    print("=" * 112)
    y = [r["measured_sd"] for r in rows]
    rho_cm = spearman([r["spearman"] for r in rows], y)
    rho_conc = spearman([r["concentration"] for r in rows], y)
    within_pos = sum(1 for r in rows if r["spearman"] > 0)
    print(f"   n = {len(rows)} partitions\n")
    print(f"   the co-movement itself is positive in {within_pos} of {len(rows)} partitions; "
          f"mean Spearman {np.mean([r['spearman'] for r in rows]):+.3f}")
    print(f"   Spearman(co-movement, measured excess draw sd)  ** {rho_cm:+.3f} **   "
          f"predicted >= {PREDICTED_RHO:+.2f}")
    print(f"   Spearman(concentration, measured sd)              {rho_conc:+.3f}   "
          f"<- the scalar this must not merely re-express")
    print(f"\n   predicted within-partition co-movement >= {PREDICTED_WITHIN:+.2f}; "
          f"observed mean {np.mean([r['spearman'] for r in rows]):+.3f}")
    print(f"   and the diagnostic: the *normalised* alignment spread scored "
          f"{CONCENTRATION_OF_ALIGNMENT_SPREAD:+.3f} with concentration in `e72`.")

    print()
    print("=" * 112)
    print("THE FALSIFIER: A CO-MOVEMENT AT OR BELOW ZERO")
    print("=" * 112)
    neg = [r for r in rows if r["spearman"] <= 0]
    if neg:
        print(f"   {len(neg)} of {len(rows)} partitions have a non-positive co-movement:")
        for r in neg:
            print(f"     -> {r['label']:<22} rho {r['spearman']:+.3f}  "
                  f"({r['n_pos_seed']}/{r['n_seed']} seeds positive)")
    else:
        print(f"   none: every partition's excess moves with its alignment within a seed")

    out = {"config": vars(args), "rows": rows,
           "n": len(rows), "spearman_comovement_vs_sd": rho_cm,
           "spearman_concentration_vs_sd": rho_conc,
           "within_positive": within_pos, "predicted_rho": PREDICTED_RHO,
           "predicted_within": PREDICTED_WITHIN}
    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
