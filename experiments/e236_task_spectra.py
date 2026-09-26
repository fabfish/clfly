"""E236 -- auditing `e235`'s crossing: are the tasks really higher-dimensional than the propagation they are built from?

`e235` measured the task geometry's `effective_rank` and the propagator's own rank on the assemblies' union support,
found them crossing (at cs 300 the propagator spreads the support into 137.5 effective dimensions while the tasks use
26.2 at `rho` 0.7; by `rho` 0.98 the propagator is *below* the task, 1.3 against 11.8), and read that as *"the tasks
keep more dimensions near criticality than the propagation of their own supports provides"*.

**That sentence cannot be true of the algebraic rank**, and the construction says so in one line:

    S = task_covariance(solver, support, weights) = (Gs * weights) @ Gs.T,   Gs = G[:, support]

so every task's covariance is a quadratic form in the *same* propagator columns, its column space is contained in
`span(Gs)`, and `rank(S) <= rank(Gs)` must hold at every cell. What *can* exceed is the **participation ratio**: `S`'s
normalised spectrum can be flatter than `Gs`'s, and a flatter spectrum is a higher effective rank with no extra
dimension. This module measures which of the two it is, per (size, topology, `rho`) and per assembly:

- **the algebraic ranks** with a declared threshold, and the **containment residual** `||S - Q Q^T S||_F / ||S||_F`
  with `Q` an orthonormal basis of `span(Gs)` -- the construction's own property, which must be ~0 and whose failure
  would mean this module reads the construction wrongly rather than that the substrate does something;
- **the participation ratios** of `S` and of `Gs` at the same support, so the two sides of the crossing are compared
  on the same columns;
- the mean over tasks and seeds, which must reproduce `e235`'s task column (`task_geometry`'s `effective_rank`).

    python -m experiments.e236_task_spectra --grid 0.9,0.98 --sizes 300
    python -m experiments.e236_task_spectra --json-out runs/e236_task_spectra.json

The exit code is the number of cells that could **not** be measured, as in `e235`.

**What it cannot do**: it audits one sentence of `e235` and not its control experiment; the threshold that decides an
algebraic rank is a declared convention rather than a fact about the matrix (the participation ratio is the reading
without one); `rho` still mixes depth with weight scale; and nothing here is about the penalty.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
TOPOLOGIES = ("real", "alloy1", "inalloy1", "erdos_renyi")
SIZES = {300: 30, 400: 40, 800: 80, 1500: 150}
#: relative threshold for the algebraic rank, the builder's own convention (`task_covariance`'s rank helper uses
#: `1e-10 * trace`), and the containment residual above which the construction is being read wrongly
RANK_RTOL = 1e-10
CONTAINMENT_TOL = 1e-6


def participation_ratio(values: np.ndarray) -> float:
    w = np.asarray(values, dtype=float)
    w = w[w > 1e-12 * max(1.0, float(w.max()))] if w.size else w
    if w.size == 0:
        return float("nan")
    w = w / w.sum()
    return float(1.0 / np.sum(w ** 2))


def measure(size: int, support: int, rho: float, topologies=TOPOLOGIES, seeds: int = 3, seed0: int = 0,
            q: float = 0.02) -> dict:
    """One cell: per task, `Gs`'s and `S`'s own spectra, ranks and the containment residual."""
    from clfly.connectome import annotate, circuits, graph, rewiring, tasks

    conn = graph.build()
    ann = annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    W0 = circ.net.weights()
    n = int(circ.net.n_neurons)
    out = {"size": int(size), "support": int(support), "rho": float(rho), "neurons": n, "topologies": {}}
    for topo in topologies:
        W = rewiring.apply_null(W0, topo, np.random.default_rng(seed0))
        circ.net = graph.Connectome(circ.net.n_neurons, circ.net.root_ids, W.tocsr())
        row, error = {}, None
        try:
            Ws = tasks.stable_weights(circ.net, rho=rho)
            solver = tasks.propagator_solver(Ws)
            tasks_rows = []
            for seed in range(seed0, seed0 + seeds):
                rng = np.random.default_rng(seed)
                for asm in tasks.TASK_ASSEMBLIES:
                    sup, weights = tasks.assembly_support(circ, asm, support, None, rng)
                    E = np.zeros((n, len(sup)))
                    E[np.asarray(sup, dtype=int), np.arange(len(sup))] = 1.0
                    Gs = solver.solve(E)                                    # (n, s) -- the same columns S is built from
                    S = tasks.task_covariance(solver, sup, weights)
                    q_basis = np.linalg.qr(Gs)[0]                           # orthonormal basis of span(Gs)
                    resid = float(np.linalg.norm(S - q_basis @ (q_basis.T @ S)) / max(np.linalg.norm(S), 1e-300))
                    s_sv = np.linalg.svd(Gs, compute_uv=False)
                    e_s = np.linalg.eigvalsh(S)
                    e_s = e_s[e_s > 0]
                    tasks_rows.append({
                        "assembly": asm.name, "seed": seed, "support": int(len(sup)),
                        "rank_gs": int(np.sum(s_sv > RANK_RTOL * max(s_sv.max(), 1e-300))),
                        "rank_s": int(np.sum(e_s > RANK_RTOL * max(e_s.max(), 1e-300))) if e_s.size else 0,
                        "pr_gs": participation_ratio(s_sv ** 2), "pr_s": participation_ratio(e_s),
                        "top_gs": float((s_sv ** 2).max() / max(np.sum(s_sv ** 2), 1e-300)),
                        "top_s": float(e_s.max() / max(e_s.sum(), 1e-300)) if e_s.size else float("nan"),
                        "containment": resid})
            row = {"tasks": tasks_rows,
                   "mean_pr_s": float(np.mean([r["pr_s"] for r in tasks_rows])),
                   "mean_pr_gs": float(np.mean([r["pr_gs"] for r in tasks_rows])),
                   "mean_rank_s": float(np.mean([r["rank_s"] for r in tasks_rows])),
                   "mean_rank_gs": float(np.mean([r["rank_gs"] for r in tasks_rows])),
                   "mean_top_s": float(np.mean([r["top_s"] for r in tasks_rows])),
                   "mean_top_gs": float(np.mean([r["top_gs"] for r in tasks_rows])),
                   "max_containment": float(np.max([r["containment"] for r in tasks_rows])),
                   "max_support": int(np.max([r["support"] for r in tasks_rows]))}
            row["pr_ratio"] = row["mean_pr_s"] / row["mean_pr_gs"] if row["mean_pr_gs"] else float("nan")
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"[:120]
        row["error"] = error
        out["topologies"][topo] = row
    return out


def stored_task_ranks(runs: Path = RUNS) -> dict:
    """`e235`'s own task column, keyed by (size, topology, rho), so the reproduction is checked against it."""
    out = {}
    for p in (runs / "e235_propagator_rank.json",):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        for r in d.get("rows", []):
            for topo, cell in (r.get("topologies") or {}).items():
                v = cell.get("effective_rank")
                if isinstance(v, (int, float)):
                    out[(r["size"], topo, round(r["rho"], 4))] = float(v)
    return out


def report(rows: list[dict], stored: dict | None = None) -> int:
    print("== the tasks' own spectra beside the propagation they are built from ==")
    print("   `pr_s` is the participation ratio of a task's covariance (`task_geometry`'s reading, per task),")
    print("   `pr_gs` the same over the propagator columns it is built from, `r_s`/`r_gs` the algebraic ranks,")
    print("   `cont` the containment residual `||S - Q Q^T S||_F / ||S||_F` -- which must be ~0 by construction")
    for size in sorted({r["size"] for r in rows}):
        cells = sorted([r for r in rows if r["size"] == size], key=lambda r: r["rho"])
        print(f"\n   cs {size}  ({cells[0]['neurons']} neurons, support budget {cells[0]['support']})")
        print(f"      {'topology':12} {'rho':>7} {'pr_s':>8} {'pr_gs':>8} {'pr cr':>7} {'r_s':>6} {'r_gs':>6} "
              f"{'top_s':>7} {'top_gs':>7} {'cont':>9}")
        for r in cells:
            for topo in TOPOLOGIES:
                c = r["topologies"].get(topo, {})
                if c.get("error") or c.get("mean_pr_s") is None:
                    print(f"      {topo:12} {r['rho']:>7.4g}   UNMEASURABLE {c.get('error') or ''}")
                    continue
                print(f"      {topo:12} {r['rho']:>7.4g} {c['mean_pr_s']:>8.2f} {c['mean_pr_gs']:>8.2f} "
                      f"{c['pr_ratio']:>7.2f} {c['mean_rank_s']:>6.1f} {c['mean_rank_gs']:>6.1f} "
                      f"{c['mean_top_s']:>7.3f} {c['mean_top_gs']:>7.3f} {c['max_containment']:>9.1e}")
    if stored:
        print("\n== does the task column reproduce e235? ==")
        checked = bad = 0
        for r in rows:
            for topo, c in r["topologies"].items():
                v = stored.get((r["size"], topo, round(r["rho"], 4)))
                if v is None or c.get("mean_pr_s") is None:
                    continue
                checked += 1
                hit = abs(v - c["mean_pr_s"]) <= 1e-6 * max(abs(v), 1e-12)
                bad += 0 if hit else 1
                print(f"      cs {r['size']} {topo:12} rho {r['rho']:<5.4g} {c['mean_pr_s']:8.4f}  "
                      f"{'matches' if hit else f'NO MATCH (e235 has {v:.4f})'}")
        print(f"   {checked - bad} of {checked} cells match e235's task column")
    worst = max((c["max_containment"] for r in rows for c in r["topologies"].values()
                 if c.get("max_containment") is not None), default=None)
    if worst is not None:
        print(f"\n   the largest containment residual anywhere: {worst:.2e} (a cell above {CONTAINMENT_TOL:g} would "
              f"mean")
        print("   this module reads `task_covariance` wrongly rather than that the substrate does something)")
    bad_cells = sum(1 for r in rows for c in r["topologies"].values() if c.get("mean_pr_s") is None)
    print(f"   unmeasurable cells: {bad_cells}")
    return bad_cells


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grid", default="0.9,0.95,0.98")
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
            print(f"   cs {size} rho {rho:<6.4g} " + " ".join(
                f"{t} {row['topologies'][t].get('mean_pr_s') or float('nan'):.1f}"
                f"/{row['topologies'][t].get('mean_pr_gs') or float('nan'):.1f}"
                for t in TOPOLOGIES), flush=True)
    if args.json_out:
        write_json(args.json_out, {"rows": rows, "grid": grid})
        print(f"wrote {args.json_out}")
    return report(rows, stored_task_ranks())


if __name__ == "__main__":
    sys.exit(main())
