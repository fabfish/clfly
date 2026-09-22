"""E3 — which anchoring basis should the Fisher live in?

The core experiment.  For a circuit-constrained LGCL problem built from the
wiring (see :mod:`clfly.connectome.tasks`), measure the excess error of EWC in
each candidate anchoring basis relative to the exact Kalman oracle, at matched
capacity, and against group-size-matched random partitions.

Two questions, in order:

**Q1 (why do we need interaction at all).** Does the coordinate basis actually
lose anything here?  If the excess is ~0 in every basis, the fly's wiring has
already made the question moot -- which is a result, and the modularity
explanation for it is testable.

**Q2 (which basis).** Among the rungs of the annotation ladder, does the ranking
track the principal angles between each partition's indicator span and the tasks'
precision subspaces?  The biological rungs must beat their matched random
controls, or the answer is "any partition of this granularity does" and the
biology is decoration.

    python -m experiments.e3_basis_selection --circuit-size 1500 --seeds 2
    python -m experiments.e3_basis_selection --topology real,degree_swap
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

from clfly.bench.analytic import (
    analytic_excess,
    contrast_of_contrasts,
    paired_delta,
    projection_pressure,
    spearman,
)
from clfly.bench.artifacts import write_json
from clfly.bench.control import averaged_random_control
from clfly.bench.oracle import (
    oracle_errors,
    paired_excess,
    task_subspaces,
)
from clfly.connectome import annotate, circuits, graph, rewiring, tasks
from clfly.lgcl.bases import (
    Diagonal,
    Partition,
    Rank,
    RotatedDiagonal,
    alignment_score,
    random_partition,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "runs"

#: Biological rungs to test, in the order they appear on the ladder.
BIOLOGICAL_BASES = ("side", "cell_class", "cell_type", "ito_lee_hemilineage", "supertype")


def _pool_small_groups(labels: np.ndarray, min_size: int) -> np.ndarray:
    """Merge every group smaller than ``min_size`` into one shared group.

    The annotation vocabulary supplies five discrete rungs, and they are badly
    distributed: `side` 0.50, `cell_class` 0.83, then hemilineage/supertype/cell_type
    crowded at 0.967–0.979. Whether the biological advantage is monotone in granularity
    or has an optimum cannot be read off five points, four of which sit at one end.
    Pooling the rarest cell types by size traces the interval in between continuously,
    which is the same device the rate-network work uses to reach mid-granularity
    partitions the vocabulary does not provide.
    """
    counts = np.bincount(labels)
    keep = counts >= min_size
    remap = np.cumsum(keep) - 1
    pooled_id = int(remap.max()) + 1
    return np.where(keep, remap, pooled_id)[labels]


def candidate_bases(circ: circuits.Circuit, rng: np.random.Generator,
                    extras: bool = False, ladder: bool = False,
                    ladder_sizes=(1, 2, 4, 8, 16, 32, 64, 128)) -> dict:
    """Every anchoring basis to be compared, biological and control.

    ``extras`` adds **non-partition** candidates, which turn the anchoring question
    from "which partition?" into "which structure?": spectral truncation to the top
    ``r`` directions of the posterior (state-dependent, so it re-picks its basis every
    step), and the diagonal in the **connectome's own eigenbasis** (a fixed structural
    rotation).  Both are handled by the same machinery, and
    :func:`clfly.bench.analytic.projection_pressure` applies to them unchanged —
    which is what lets one run test the predictor's generality alongside the
    partition comparison.

    ``ladder`` replaces the five annotation rungs with a **granularity curve**: pooled
    cell-type partitions at ``ladder_sizes`` minimum-group sizes, each with its own
    group-size-matched random control, spanning roughly 0.30 to 0.999 constrained.  That
    makes "is the advantage monotone in granularity, or is there an optimum?" answerable
    rather than a matter of four crowded points.
    """
    bases = {"diagonal(EWC)": Diagonal(circ.n_neurons)}
    if ladder:
        lab = circ.labels["cell_type"]
        for m in ladder_sizes:
            pooled = _pool_small_groups(lab, m)
            bases[f"bio:pool{m}"] = Partition(pooled)
            bases[f"rand:pool{m}"] = random_partition(pooled, rng)
        return bases
    for col in BIOLOGICAL_BASES:
        if col not in circ.labels:
            continue
        lab = circ.labels[col]
        bases[f"bio:{col}"] = Partition(lab)
        bases[f"rand:{col}"] = random_partition(lab, rng)
    if extras:
        for r in (4, 16, 64):
            if r < circ.n_neurons:
                bases[f"rank{r}"] = Rank(circ.n_neurons, r)
        bases["eigbasis"] = RotatedDiagonal(circ.net.symmetrised_eigenbasis())
    return bases


def alignment_of(partition: Partition, seq, ranks, rng: np.random.Generator,
                 n_null: int = 8, top: int | None = None) -> dict:
    """Alignment between a partition's indicator span and the task subspaces.

    Raw alignment is not interpretable on its own: a finer partition has a
    *larger* indicator span, so it overlaps every subspace more and scores higher
    for free.  The first version of this function reported the raw number, and it
    came out anti-correlated with the anchoring benefit -- the finest biological
    rung scored highest and lost the most.

    So we also report ``excess``, the ratio to an empirically measured chance
    level: the mean alignment this same partition achieves against random
    subspaces of the same dimension.  Measuring the null rather than deriving it
    keeps the comparison honest if the indicator spans are not generic.

    ``top`` selects a spectrally *truncated* task subspace.  Without it the
    subspace is the task's entire range space, which is set by support membership
    alone and is bit-identical across large changes in drive strength -- so the
    predictor cannot see the structure it is supposed to be testing.  This is the
    most likely reason the untruncated version failed to rank the bases in e3.
    """
    Q = partition.indicator_span()
    p = Q.shape[1]
    V = task_subspaces(seq, ranks, top=top)
    raw, chance = [], []
    for k in range(seq.T):
        U = V[k]
        raw.append(alignment_score(Q, U))
        nulls = []
        for _ in range(n_null):
            Z = np.linalg.qr(rng.standard_normal((seq.d, U.shape[1])))[0]
            nulls.append(alignment_score(Q, Z))
        chance.append(float(np.mean(nulls)))
    raw_m, chance_m = float(np.mean(raw)), float(np.mean(chance))
    return {
        "alignment": raw_m,
        "alignment_chance": chance_m,
        "excess": raw_m / chance_m if chance_m > 0 else float("nan"),
        "span_dim": int(p),
        "align_top": int(V[0].shape[1]),
    }


def run(args) -> dict:
    """Paired design: one set of task sequences per seed, every basis scored on all of them.

    This is what makes the comparison interpretable.  Building tasks inside the
    basis loop would give each basis its own task draw, so basis differences would
    be contaminated by task differences -- and on this substrate the task-to-task
    spread is larger than most of the effects (see the metric-instability findings).
    """
    t0 = time.time()
    conn = graph.build()
    ann = annotate.load_annotations()

    results = {"config": vars(args), "topologies": {}, "timing": {}}
    for topology in args.topologies:
        circ = circuits.extract(conn, ann, hops=0, max_neurons=args.circuit_size)
        if topology != "real":
            rng_top = np.random.default_rng(args.seed0)
            W0 = circ.net.weights()
            W = rewiring.apply_null(W0, topology, rng_top)
            results.setdefault("topology_notes", {})[topology] = {
                "edges_before": int(W0.nnz), "edges_after": int(W.nnz),
                "swap_fraction": rewiring.swap_fraction(W0, W),
            }
            circ.net = graph.Connectome(circ.net.n_neurons, circ.net.root_ids, W.tocsr())
            print(f"  topology {topology}: edges {W0.nnz:,} -> {W.nnz:,}")

        # scores: name -> metric -> value, pooled across seeds
        seqs, ranks = [], []
        for seed in range(args.seed0, args.seed0 + args.seeds):
            wt = tasks.build_tasks(circ, support_size=args.support, q=args.q, seed=seed)
            seqs.append(wt.sequence)
            ranks.append(wt.ranks)
            print(f"    built tasks for seed {seed} ({time.time()-t0:.0f}s)  d={wt.sequence.d}")
        rank_ref = ranks[0]

        rng = np.random.default_rng(args.seed0)
        agg = {}
        # the biological partition's labels per rung, so the matched-random control can be
        # re-drawn from them when more than one draw is asked for
        pooled_labels: dict[str, np.ndarray] = {}
        for name, basis in candidate_bases(circ, rng, extras=args.extra_bases,
                                           ladder=args.ladder).items():
            if isinstance(basis, Partition) and name.startswith("bio:"):
                pooled_labels[name[4:]] = np.asarray(basis.labels)
            if (args.control_draws > 1 and name.startswith("rand:")
                    and name[5:] in pooled_labels):
                # average the control over independent draws: one draw is a single sample from
                # the population of size-matched random partitions, and for coarse partitions
                # its spread is several times the seed sem (see clfly/bench/control.py)
                row = {"analytic": averaged_random_control(
                    seqs, pooled_labels[name[5:]], rng, draws=args.control_draws)}
            else:
                row = {"analytic": analytic_excess(seqs, basis)}
            if not args.no_realized:
                row["realized"] = paired_excess(seqs, basis)
            # candidate a-priori predictor: available before any anchored filter runs
            row["pressure"] = float(np.mean([projection_pressure(s, basis) for s in seqs]))
            row["n_parameters"] = basis.n_parameters
            total = seqs[0].d * (seqs[0].d + 1) // 2
            row["constrained_fraction"] = 1.0 - basis.n_parameters / total
            if isinstance(basis, Partition):
                # spectrally selected subspace, not the full range space: taking the
                # numerical rank returns the whole range, which is blind to drive
                # strength and cannot see the structure the predictor is about.
                row.update(alignment_of(basis, seqs[0], rank_ref, rng,
                                        top=args.align_top))
            agg[name] = row
            a = row["analytic"]
            extra = (f"  draws={a['control_draws']}"
                     f" sd_across={a['sd_across_draws']:.5f}"
                     if a.get("control_draws", 1) > 1 else "")
            print(f"    {name:26} analytic={a['excess_mean']:+.5f}"
                  f"+-{a['excess_sem']:.5f}  "
                  f"pressure={row['pressure']:.4f}"
                  + extra
                  + (f"  realized={row['realized']['excess_mean']:+.5f}"
                     f"+-{row['realized']['excess_sem']:.5f}" if "realized" in row else "")
                  + f"  ({time.time()-t0:.0f}s)")

        agg["_abs"] = {
            "oracle_final": float(np.mean([oracle_errors(s)["final_avg_error"] for s in seqs])),
            "oracle_final_analytic": agg["diagonal(EWC)"]["analytic"]["oracle_mean"],
            "d": seqs[0].d,
            "n_seeds": len(seqs),
        }
        results["topologies"][topology] = agg

    results["timing"]["total_s"] = time.time() - t0
    return results


def report(results: dict) -> None:
    for topology, agg in results["topologies"].items():
        if not agg or "diagonal(EWC)" not in agg:
            continue
        absl = agg.get("_abs", {})
        print(f"\n=== topology: {topology} ===")
        print(f"d={absl.get('d', '?')}  seeds={absl.get('n_seeds', '?')}  "
              f"oracle: realized {absl.get('oracle_final', float('nan')):.5f}  "
              f"analytic {absl.get('oracle_final_analytic', float('nan')):.5f}")
        has_realized = "realized" in agg["diagonal(EWC)"]
        print(f"{'basis':26} {'constr':>7} | {'a_excess':>10} {'a_sem':>8} "
              f"{'a_sd':>8} {'pressure':>9} {'align':>7}"
              + (f" | {'r_excess':>10} {'r_sem':>8}" if has_realized else ""))
        print("-" * (116 if has_realized else 92))
        for name in sorted(agg):
            if name.startswith("_"):
                continue
            d = agg[name]
            a = d["analytic"]
            line = (f"{name:26} {d['constrained_fraction']:7.4f} | "
                    f"{a['excess_mean']:+10.5f} {a['excess_sem']:8.5f} {a['excess_sd']:8.5f} "
                    f"{d.get('pressure', float('nan')):9.4f} "
                    f"{d.get('excess', float('nan')):7.4f}")
            if has_realized:
                r = d["realized"]
                line += f" | {r['excess_mean']:+10.5f} {r['excess_sem']:8.5f}"
            print(line)

        print("\n  paired contrast (biological minus size-matched random):")
        hdr = f"  {'rung':24} {'analytic delta':>15} {'sigma':>7} {'sigma_p':>8} {'corr':>6}"
        if has_realized:
            hdr += f" | {'realized delta':>15} {'sigma':>7}"
        print(hdr)
        wins_a = wins_r = 0
        rungs = [n[4:] for n in agg
                 if n.startswith("bio:") and f"rand:{n[4:]}" in agg]
        # ordered by granularity, finest first -- the alphabetical order is meaningless
        # for a curve, and the adjacent-rung contrasts below depend on this being right
        rungs.sort(key=lambda c: -agg[f"bio:{c}"]["constrained_fraction"])
        deltas = {}
        for col in rungs:
            b, r = agg.get(f"bio:{col}"), agg.get(f"rand:{col}")
            if not b or not r:
                continue
            pc = paired_delta(b["analytic"], r["analytic"])
            deltas[col] = pc
            da, za = pc["delta"], pc["sigma_unpaired"]
            zp = pc.get("sigma_paired", float("nan"))
            corr = pc.get("corr", float("nan"))
            wins_a += bool(da < 0 and za > 2)
            line = f"  {col:24} {da:+15.5f} {za:7.2f} {zp:8.2f} {corr:6.2f}"
            if has_realized:
                dr = b["realized"]["excess_mean"] - r["realized"]["excess_mean"]
                sr = float(np.hypot(b["realized"]["excess_sem"], r["realized"]["excess_sem"]))
                zr = abs(dr) / sr if sr else float("inf")
                wins_r += bool(dr < 0 and zr > 2)
                line += f" | {dr:+15.5f} {zr:7.2f}"
            print(line)
        extra = f", realized {wins_r}/{len(BIOLOGICAL_BASES)}" if has_realized else ""
        print(f"  -> resolved (>2 sigma, biology better): "
              f"analytic {wins_a}/{len(rungs)}{extra}")
        print("     sigma assumes independent arms; sigma_p is paired on the seed. Both are SEED")
        print("     axes only: a fixed control draw is a per-rung offset, so the draw component is")
        print("     in neither -- and for a contrast that does NOT combine the two rungs, the draw")
        print("     axis is what usually dominates. See")
        print("     docs/findings/2026-09-22-paired-ladder-and-two-axes.md")

        # Does the curve have a *shape*? A rung's delta resolving from zero is a different
        # claim from two rungs' deltas differing, and only the second supports an optimum.
        # NOTE: both columns are the SEED axis. A fixed control draw shifts each delta by a
        # per-rung offset and contributes nothing to this variance, so the draw axis has to be
        # added separately -- for a contrast it is hypot(sd_draw(c1), sd_draw(c2)), and at the
        # measured draw sds it exceeds the paired sem several-fold for every internal step.
        if len(deltas) > 1:
            print(f"\n  adjacent-rung contrasts in delta (does the curve have a shape?)")
            print(f"    SEED axis only -- the independent draw axis is not in these columns, and")
            print(f"    for every internal step it is the larger of the two")
            cols = [c for c in rungs if c in deltas]
            for c1, c2 in zip(cols, cols[1:]):
                cc = contrast_of_contrasts(deltas[c1], deltas[c2])
                sp = cc.get("sigma_paired", float("nan"))
                print(f"    delta({c1:10}) - delta({c2:10}) = {cc['delta']:+.5f}"
                      f"  unpaired {cc['sigma_unpaired']:5.1f}  paired {sp:5.1f} sigma")

        # Does the a-priori predictor recover the ordering and the matched-pair signs?
        # Reported separately for partitions and non-partition bases: the predictor
        # was derived for a projection onto a fixed grouping and there is no reason
        # to assume it transfers to a state-dependent truncation.
        def group_of(n):
            return "partition" if (n.startswith("bio:") or n.startswith("rand:")
                                   or n.startswith("diagonal")) else "other"

        names = [n for n in sorted(agg) if not n.startswith("_")]
        for grp in ("partition", "other", "all"):
            sel = [n for n in names if grp == "all" or group_of(n) == grp]
            if len(sel) < 3:
                continue
            ex = [agg[n]["analytic"]["excess_mean"] for n in sel]
            pr = [agg[n].get("pressure", float("nan")) for n in sel]
            print(f"\n  a-priori predictor over {grp} bases ({len(sel)}): "
                  f"Spearman vs analytic excess = {spearman(pr, ex):+.3f}")
            for n in sel:
                print(f"      {n:26} excess={agg[n]['analytic']['excess_mean']:+.5f}  "
                      f"pressure={agg[n].get('pressure', float('nan')):9.4f}")
        agree = tot = 0
        for col in rungs:
            b, r = f"bio:{col}", f"rand:{col}"
            if b not in names or r not in names:
                continue
            ib, ir = names.index(b), names.index(r)
            agrees = (agg[b]["analytic"]["excess_mean"] - agg[r]["analytic"]["excess_mean"] < 0) \
                == (agg[b]["pressure"] - agg[r]["pressure"] < 0)
            agree += bool(agrees)
            tot += 1
        print(f"\n  matched-pair signs (partition bases only): {agree}/{tot}")
        print("  (a predictor that only recovered constrained_fraction scores 0 here,")
        print("   since matched pairs share constrained_fraction exactly)")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--circuit-size", type=int, default=1500)
    p.add_argument("--support", type=int, default=150, help="neurons driven per task")
    p.add_argument("--seeds", type=int, default=1)
    p.add_argument("--seed0", type=int, default=0)
    p.add_argument("--q", type=float, default=0.02)
    p.add_argument("--topologies", default="real")
    p.add_argument("--align-top", type=int, default=16,
                   help="spectral truncation for the alignment predictor; the "
                        "numerical rank would return the degener"
                        "ate full range space")
    p.add_argument("--ladder", action="store_true",
                   help="sweep a smooth granularity curve of pooled cell-type "
                        "partitions instead of the five annotation rungs")
    p.add_argument("--control-draws", type=int, default=1,
                   help="average the group-size-matched random control over this many "
                        "independent draws. One draw is a single sample from the population "
                        "of random partitions and its spread is a per-observation sd, not a "
                        "standard error -- see clfly/bench/control.py")
    p.add_argument("--extra-bases", action="store_true",
                   help="also test non-partition candidates: spectral truncation "
                        "and the connectome eigenbasis")
    p.add_argument("--json-out", type=Path, default=None)
    p.add_argument("--report-from", type=Path, default=None,
                   help="re-print the report for a finished run's JSON instead of "
                        "recomputing it; a full ladder is hours of compute and the "
                        "analysis of its shape should not require re-running it")
    p.add_argument("--no-realized", action="store_true",
                   help="skip the realized-error arm; it is a cross-check already "
                        "done at d=1307 and costs about half the runtime")
    args = p.parse_args(argv)
    args.topologies = tuple(t for t in args.topologies.split(",") if t)

    if args.report_from:
        results = json.loads(args.report_from.read_text())
        report(results)
        return 0

    results = run(args)
    report(results)

    if args.json_out:
        write_json(args.json_out, results)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
