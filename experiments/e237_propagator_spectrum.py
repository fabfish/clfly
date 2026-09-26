"""E237 -- the propagator's own spectrum, with no support in it: how rank-one does `G = (I - W)^-1` become as `rho` -> 1?

`e235` measured the propagator's rank on the assemblies' **union** support and `e236` showed that column is not
comparable to a task's (a task is a quadratic form in ONE assembly's columns). Both readings are slices of `G`. This
module measures `G` itself -- the whole `n x n` operator, no support anywhere -- and asks three things that the slices
cannot answer:

- **does the whole operator collapse**, and by how much: the participation ratio of `G`'s squared singular values and
  the share carried by its leading one;
- **is the collapse ordered by how many columns you take** -- `G`'s own 952 (or 1307) columns, the 148-column union,
  a 30-column assembly slice -- which would unify `e235`'s union artifact and `e236`'s "the two agree at the same
  support" into one size ladder;
- **why a narrow slice escapes the collapse**: if the leading right-singular vector's mass sits mostly *outside* the
  assemblies' support, then the slice's rank-one component is diluted while the whole matrix's is not, which is a
  mechanism rather than a restatement.

    python -m experiments.e237_propagator_spectrum --grid 0.7,0.9,0.95,0.99 --sizes 300,800
    python -m experiments.e237_propagator_spectrum --json-out runs/e237_propagator_spectrum.json

The instrument is cheap -- one `splu` factorisation, `n` solves and one dense SVD per (size, topology, `rho`), measured
at 0.3-0.6 s per cell at cs 300 -- because it needs no tasks, no seeds and no analytic arm. The exit code is the number
of cells that could **not** be measured (a failed factorisation, a non-finite statistic).

**What it cannot do**: `rho` rescales the whole weight matrix, so the ladder is a statement about the *rescaled*
operator and not about a propagation depth alone; one drawing per cell (`seed0`, as everywhere in this line), and
`e232` measured that the in/out comparison is drawing-dependent; the participation ratio is a single summary of a
spectrum; and nothing here is about the penalty.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
TOPOLOGIES = ("real", "alloy1", "inalloy1", "erdos_renyi")
SIZES = {300: 30, 400: 40, 800: 80, 1500: 150}


def participation_ratio(values: np.ndarray) -> float:
    w = np.asarray(values, dtype=float)
    w = w[w > 1e-12 * max(1.0, float(w.max()))] if w.size else w
    if w.size == 0:
        return float("nan")
    w = w / w.sum()
    return float(1.0 / np.sum(w ** 2))


def measure(size: int, support: int, rho: float, topologies=TOPOLOGIES, seeds: int = 3, seed0: int = 0,
            q: float = 0.02) -> dict:
    """One (size, rho) row: the whole propagator's spectrum, and the assemblies' share of its leading direction."""
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
            G = solver.solve(np.eye(n))
            U, sv, Vt = np.linalg.svd(G, full_matrices=False)
            energy = sv ** 2
            # the assemblies' neurons, so the slice's escape can be attributed to where the leading direction sits
            rng = np.random.default_rng(seed0)
            sup_union = set()
            for asm in tasks.TASK_ASSEMBLIES:
                sup, _ = tasks.assembly_support(circ, asm, support, None, rng)
                sup_union.update(int(i) for i in sup)
            v1 = Vt[0]
            share = float(np.sum(v1[np.fromiter(sorted(sup_union), dtype=int)] ** 2))
            row = {"pr_G": participation_ratio(energy), "top_share": float(energy[0] / energy.sum()),
                   "condition_number": float(sv[0] / max(sv[-1], 1e-300)),
                   "sv_head": [float(x / sv[0]) for x in sv[:5]],
                   "support_share_of_leading_direction": share, "union_support": len(sup_union)}
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"[:120]
        row["error"] = error
        out["topologies"][topo] = row
    return out


def slice_ranks(runs: Path = RUNS) -> dict:
    """The two slice measurements to compare the ladder against: the union (`e235`) and one assembly (`e236`)."""
    out = {}
    for p, key in ((runs / "e235_propagator_rank.json", "propagator_effective_rank"),
                   (runs / "e236_task_spectra.json", None)):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        for r in d.get("rows", []):
            for topo, cell in (r.get("topologies") or {}).items():
                if key:
                    v = cell.get(key)
                else:
                    v = cell.get("mean_pr_gs")
                if isinstance(v, (int, float)):
                    out.setdefault((r["size"], topo, round(r["rho"], 4)), {})[
                        "union" if key else "assembly"] = float(v)
    return out


def report(rows: list[dict], slices: dict | None = None) -> int:
    print("== the whole propagator's spectrum (no support in it) ==")
    print("   `pr_G` is the participation ratio over `G`'s squared singular values, `top` the leading share, `cond` the")
    print("   condition number, `v1 on support` the share of the leading right-singular vector's mass that sits on the")
    print("   assemblies' neurons -- the quantity that decides whether a slice of `G` escapes the collapse")
    for size in sorted({r["size"] for r in rows}):
        cells = sorted([r for r in rows if r["size"] == size], key=lambda r: r["rho"])
        print(f"\n   cs {size}  ({cells[0]['neurons']} neurons)")
        print(f"      {'topology':12} {'rho':>7} {'pr_G':>7} {'top':>7} {'cond':>10} {'v1 on support':>14} "
              f"{'sv head':>26}")
        for r in cells:
            for topo in TOPOLOGIES:
                c = r["topologies"].get(topo, {})
                if c.get("pr_G") is None:
                    print(f"      {topo:12} {r['rho']:>7.4g}   UNMEASURABLE {c.get('error') or ''}")
                    continue
                head = " ".join(f"{x:.3f}" for x in c["sv_head"])
                print(f"      {topo:12} {r['rho']:>7.4g} {c['pr_G']:>7.2f} {c['top_share']:>7.3f} "
                      f"{c['condition_number']:>10.3g} {c['support_share_of_leading_direction']:>14.4f} {head:>26}")
    if slices:
        print("\n== the size ladder: how many columns of `G` you take sets how soon its rank collapses ==")
        print(f"      {'size':>5} {'topology':12} {'rho':>7} {'whole G':>9} {'union (148)':>12} {'assembly (30/80)':>17}")
        for r in sorted(rows, key=lambda r: (r["size"], r["rho"])):
            for topo, c in sorted(r["topologies"].items()):
                if c.get("pr_G") is None:
                    continue
                s = slices.get((r["size"], topo, round(r["rho"], 4)), {})
                print(f"      {r['size']:>5} {topo:12} {r['rho']:>7.4g} {c['pr_G']:>9.2f} "
                      f"{s.get('union', float('nan')):>12.2f} {s.get('assembly', float('nan')):>17.2f}")
    bad = sum(1 for r in rows for c in r["topologies"].values() if c.get("pr_G") is None)
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
            print(f"   cs {size} rho {rho:<6.4g} " + " ".join(
                f"{t} pr {row['topologies'][t].get('pr_G') or float('nan'):.2f}"
                f"/top {row['topologies'][t].get('top_share') or float('nan'):.3f}"
                for t in TOPOLOGIES), flush=True)
    if args.json_out:
        write_json(args.json_out, {"rows": rows, "grid": grid})
        print(f"wrote {args.json_out}")
    return report(rows, slice_ranks())


if __name__ == "__main__":
    sys.exit(main())
