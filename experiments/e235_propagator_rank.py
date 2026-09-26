"""E235 -- where does the task geometry's rank come from? The PROPAGATOR's own rank, at the same `rho` grid.

`e231` measured the task geometry's `effective_rank` collapsing with `rho` (one-side nulls 26.2 -> 1.1 at cs 300; a
cs-800 plateau at ~21 for `alloy1` and a collapse to ~1.3 for `inalloy1`), and `e233`/`e234` then showed the *penalty*
does not follow it. Neither said **why** the rank moves, and the one candidate that needs no new substrate is the
object the tasks are actually made of:

    the tasks are built from `S = task_covariance(solver, support, weights)`,
    where `solver` factorises `I - W` -- so `G = (I - W)^-1` is the propagator
    and every task is a quadratic form in the columns of `G` at an assembly's support.

As `rho -> 1` the spectral radius of `W` approaches 1, `G` approaches singularity, and its action on any support is
dominated by fewer and fewer directions. If that is where the geometry's rank comes from, then **the effective rank of
`G`'s action on the assembly supports should track the geometry's rank across (topology, `rho`) cells** -- including
the two facts `e231` found and could not explain: that `erdos_renyi` plateaus at ~3.2 effective dimensions instead of
collapsing to 1, and that at cs 800 `alloy1` plateaus at ~21 while `inalloy1` collapses.

**The measurement is the corpus's own statistic, twice.** For the *task* side this module rebuilds the tasks exactly
as the runner does -- same `stable_weights`, same `propagator_solver`, same `assembly_support` in the same order,
same `task_covariance`, same three seeds -- and computes `task_geometry`'s `effective_rank`, so `--verify` can check
it against `e231`'s artifacts bit for bit. For the *propagator* side it solves `G x = e_i` for every neuron `i` of the
assemblies' union support, giving the propagated support matrix `P`, and reports the participation ratio of `P`'s
squared singular values -- the same kind of reading, one level down.

    python -m experiments.e235_propagator_rank --grid 0.7,0.9,0.99 --sizes 300
    python -m experiments.e235_propagator_rank --json-out runs/e235_propagator_rank.json

The exit code is the number of cells that could **not** be measured (a failed solve, a non-finite statistic): as
`rho -> 1` the factorisation can fail or the solve can blow up, and an instrument that cannot say "unmeasurable" would
report a number anyway.

**What it cannot do**: it measures the propagator's *action on the assembly supports*, not its spectrum or its
condition number, so "the propagator's rank" is a statement about those columns; one drawing per cell (the null's
stream is `seed0`, as everywhere in this line) and `e232` measured that the **in/out comparison** is drawing-dependent,
so a cross-family contrast here inherits that while a single family's `rho` curve does not; and `rho` rescales the whole
weight matrix, so the module cannot separate propagation depth from weight scale.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from clfly.bench.oracle import task_geometry

RUNS = Path("runs")
TOPOLOGIES = ("real", "alloy1", "inalloy1", "erdos_renyi")
SIZES = {300: 30, 400: 40, 800: 80, 1500: 150}


def participation_ratio(values: np.ndarray) -> float:
    """`1 / sum(w^2)` over normalised non-negative weights -- `task_geometry`'s own reading."""
    w = np.asarray(values, dtype=float)
    w = w[w > 1e-12 * max(1.0, float(w.max()))] if w.size else w
    if w.size == 0:
        return float("nan")
    w = w / w.sum()
    return float(1.0 / np.sum(w ** 2))


def propagator_rank(solver, support: np.ndarray, n: int) -> dict:
    """The rank of `G`'s action on one support: solve `G x = e_i` for every `i` in it and read the spectrum.

    `P = G[:, support]` is what every task's covariance is a quadratic form in, so its participation ratio is the
    propagator-side counterpart of the geometry's `effective_rank`.
    """
    cols = []
    for i in support:
        e = np.zeros(n)
        e[int(i)] = 1.0
        cols.append(solver.solve(e))
    P = np.asarray(cols).T                                     # n x |support|
    s = np.linalg.svd(P, compute_uv=False)
    return {"propagator_effective_rank": participation_ratio(s ** 2),
            "propagator_top_share": float((s ** 2).max() / max(np.sum(s ** 2), 1e-300)),
            "support_size": int(len(support))}


def measure(size: int, support: int, rho: float, topologies=TOPOLOGIES, seeds: int = 3, seed0: int = 0,
            q: float = 0.02) -> dict:
    """One (size, rho) row: the task geometry's rank and the propagator's, for every topology."""
    from clfly.connectome import annotate, circuits, graph, rewiring, tasks

    conn = graph.build()
    ann = annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    W0 = circ.net.weights()
    out = {"size": int(size), "support": int(support), "rho": float(rho), "neurons": int(circ.net.n_neurons),
           "topologies": {}}
    for topo in topologies:
        W = rewiring.apply_null(W0, topo, np.random.default_rng(seed0))
        circ.net = graph.Connectome(circ.net.n_neurons, circ.net.root_ids, W.tocsr())
        row, error = {}, None
        try:
            Ws = tasks.stable_weights(circ.net, rho=rho)
            solver = tasks.propagator_solver(Ws)
            geos, supports = [], []
            for seed in range(seed0, seed0 + seeds):
                rng = np.random.default_rng(seed)
                sigmas, ranks = [], []
                for asm in tasks.TASK_ASSEMBLIES:
                    sup, weights = tasks.assembly_support(circ, asm, support, None, rng)
                    S = tasks.task_covariance(solver, sup, weights)
                    sigmas.append(S)
                    ranks.append(int(np.sum(np.linalg.eigvalsh(S) > 1e-10 * np.trace(S)) if np.trace(S) else 0))
                    if seed == seed0:
                        supports.append(np.asarray(sup, dtype=int))
                J = np.stack([S for S in sigmas])
                seq = type("Seq", (), {"T": len(sigmas), "d": int(circ.net.n_neurons), "J": J})()
                geos.append(task_geometry(seq, ranks))
            row = {k: float(np.mean([g[k] for g in geos]))
                   for k in ("effective_rank", "flattening", "mean_rank")}
            union = np.unique(np.concatenate(supports)) if supports else np.array([], dtype=int)
            row.update(propagator_rank(solver, union, int(circ.net.n_neurons)))
            row["seeds_measured"] = seeds
        except Exception as exc:                                  # a singular factorisation, a failed solve
            error = f"{type(exc).__name__}: {exc}"[:120]
        row["error"] = error
        out["topologies"][topo] = row
    return out


def stored_ranks(runs: Path = RUNS) -> dict:
    """`e231`'s ranks, keyed by (size, topology, rho) -- the numbers this module's task side should reproduce."""
    out = {}
    for p in sorted(glob.glob(str(runs / "e231_*.json"))):
        try:
            d = json.loads(Path(p).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        for row in d.get("rows", []):
            for topo, cell in (row.get("topologies") or {}).items():
                v = cell.get("effective_rank")
                if isinstance(v, (int, float)):
                    out.setdefault((row["size"], topo, round(row["rho"], 4)), []).append(v)
    return out


def report(rows: list[dict], stored: dict | None = None) -> int:
    print("== the task geometry's rank and the propagator's, by (size, topology, rho) ==")
    print("   `task` is `task_geometry`'s effective_rank (the corpus's statistic), `prop` the participation ratio of")
    print("   the propagated support matrix's squared singular values, `top` its leading share")
    for size in sorted({r["size"] for r in rows}):
        cells = sorted([r for r in rows if r["size"] == size], key=lambda r: r["rho"])
        print(f"\n   cs {size}  ({cells[0]['neurons']} neurons, support {cells[0]['support']})")
        print(f"      {'topology':12} {'rho':>7} {'task':>8} {'prop':>8} {'top':>7} {'support':>8}")
        for r in cells:
            for topo in TOPOLOGIES:
                c = r["topologies"].get(topo, {})
                if not c or c.get("effective_rank") is None:
                    print(f"      {topo:12} {r['rho']:>7.4g}   UNMEASURABLE {c.get('error') or ''}")
                    continue
                print(f"      {topo:12} {r['rho']:>7.4g} {c['effective_rank']:>8.2f} "
                      f"{c['propagator_effective_rank']:>8.2f} {c['propagator_top_share']:>7.3f} "
                      f"{c['support_size']:>8}")
    if stored is not None:
        print("\n== does the task side reproduce e231's own numbers? ==")
        checked = mismatched = 0
        for r in rows:
            for topo, c in r["topologies"].items():
                vals = stored.get((r["size"], topo, round(r["rho"], 4)))
                if not vals or c.get("effective_rank") is None:
                    continue
                checked += 1
                hit = any(abs(v - c["effective_rank"]) <= 1e-6 * max(abs(v), 1e-12) for v in vals)
                mismatched += 0 if hit else 1
                print(f"      cs {r['size']} {topo:12} rho {r['rho']:<5.4g} {c['effective_rank']:8.4f}  "
                      f"{'matches e231' if hit else f'NO MATCH (e231 has {[round(v, 4) for v in vals]})'}")
        print(f"   {checked - mismatched} of {checked} cells match, so the task side is the corpus's own statistic")
    bad = sum(1 for r in rows for c in r["topologies"].values() if c.get("effective_rank") is None)
    print(f"\n   unmeasurable cells: {bad}")
    return bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grid", default="0.7,0.8,0.9,0.95,0.98,0.99")
    ap.add_argument("--sizes", default="300,800")
    ap.add_argument("--support", type=int, default=None)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--seed0", type=int, default=0)
    ap.add_argument("--q", type=float, default=0.02)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    grid = [float(x) for x in args.grid.split(",") if x.strip()]
    rows = []
    for size in [int(s) for s in args.sizes.split(",") if s.strip()]:
        support = args.support or SIZES.get(size, max(1, size // 10))
        for rho in grid:
            row = measure(size, support, rho, seeds=args.seeds, seed0=args.seed0, q=args.q)
            rows.append(row)
            print(f"   cs {size} rho {rho:<6.4g} " + "  ".join(
                f"{t} task {(row['topologies'][t].get('effective_rank') or float('nan')):.1f}"
                f"/prop {(row['topologies'][t].get('propagator_effective_rank') or float('nan')):.1f}"
                for t in TOPOLOGIES), flush=True)
    if args.json_out:
        write_json(args.json_out, {"rows": rows, "grid": grid})
        print(f"wrote {args.json_out}")
    return report(rows, stored_ranks())


if __name__ == "__main__":
    sys.exit(main())
