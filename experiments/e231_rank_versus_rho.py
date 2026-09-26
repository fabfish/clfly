"""E231 -- the task geometry's effective rank against `rho`, on a grid the corpus does not have, measuring the quantity it already does.

`e229`/`e230` left one phenomenon standing and one open question:

- the task geometry's `effective_rank` collapses as `rho` rises (one-side nulls 26.17 -> 9.41 -> 1.07 at cs 300 over
  `rho` 0.5/0.9/0.99), and at cs 800 the **out-structure-destroying** null (`inalloy1`) collapses to 1.29 while the
  in-structure one (`alloy1`) does not — a contrast `e230` showed is resolvable for `inalloy1` (44.79x against a 4.14x
  drawing scatter) and **not** for `alloy1` (3.01x against 16.44x);
- and the corpus's `rho` grid has exactly **three** values and **one** drawing per cell, so the *shape* of that
  collapse — monotone steepening, a threshold, or a turnover — is unmeasured.

This module measures the curve directly. `effective_rank` is the participation ratio of each task's normalised
precision spectrum (`clfly.bench.oracle.task_geometry`), which does not depend on any basis, so it can be measured
without the analytic arm, the geometric alignment nulls or the realized arm: the cost is the task builds alone. That
is what makes a nine-point `rho` grid affordable where the runner's cells cost minutes each.

**The measurement is the corpus's, not a surrogate.** It rebuilds the circuit, applies the same null with the same
`rng`, builds the same three seeds with the same support, `q` and `rho`, and averages `task_geometry` over them —
exactly the runner's code path for its `geometry` block. `--verify` prints the comparison against the artifacts that
carry a `geometry` block at the same (size, topology, `rho`, support, seeds), and a mismatch there is a defect in this
instrument rather than a finding about the substrate.

    python -m experiments.e231_rank_versus_rho --grid 0.5,0.7,0.8,0.9,0.95 --sizes 300
    python -m experiments.e231_rank_versus_rho --json-out runs/e231_rank_versus_rho.json

The exit code is the number of cells that could **not** be measured (a build that fails, a non-finite rank): with the
propagator `(I - W)^-1` approaching singularity as `rho -> 1`, an instrument that cannot say "this cell is
unmeasurable" would report a number anyway.

**What it cannot do**: it measures one statistic (`effective_rank`) and not the penalty, so a curve here is not a
statement about the top step; one drawing per cell (`--rewire-seed` defaults to `seed0`, as in the runner), so a
family whose drawing scatter is wide — `alloy1` at cs 800 is 16.44x (`e230`) — cannot be read from a single curve;
and `rho` rescales the whole weight matrix, so the curve mixes propagation depth with weight scale.

**Its artifact is not a benchmark cell.** The payload is `{"rows": …, "verify": …, "grid": …}` with **no `config`
block**, deliberately: a cell of this corpus is a run of a benchmark whose tasks carry an analytic arm, a realized arm
and a `real`/null block, and this is a measurement of the task geometry alone. Artifacts without a `config` are
skipped by the audits that enumerate cells (`e103`'s loader requires one), which is what keeps this instrument's
output out of censuses it does not belong to — and it means a reader of this file has to read `rows`, not `topologies`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from clfly.bench.oracle import task_geometry

RUNS = Path("runs")
TOPOLOGIES = ("real", "alloy1", "inalloy1", "erdos_renyi")
#: the corpus's convention: support is a tenth of the circuit's budget, three seeds from `seed0`
SIZES = {300: 30, 400: 40, 800: 80, 1500: 150}
DEFAULT_GRID = (0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 0.99, 0.995, 0.999)
#: the rho values the corpus already has, where this instrument has to reproduce its own numbers
VERIFY_AT = (0.5, 0.9, 0.99)


def measure(size: int, support: int, rho: float, topologies=TOPOLOGIES, seeds: int = 3, seed0: int = 0,
            q: float = 0.02, rewire_seed: int | None = None) -> dict:
    """One (size, rho) row: every topology's task geometry, measured the way the runner measures it.

    `rewire_seed` seeds the null's own stream (the runner's `--rewire-seed`); without it `seed0` drives both the
    null and the tasks, which is the corpus's convention and the reason a single curve is one DRAWING of the null.
    """
    from clfly.connectome import annotate, circuits, graph, rewiring, tasks

    conn = graph.build()
    ann = annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    W0 = circ.net.weights()
    rw = seed0 if rewire_seed is None else rewire_seed
    out = {"size": int(size), "support": int(support), "rho": float(rho), "rewire_seed": int(rw),
           "neurons": int(circ.net.n_neurons), "topologies": {}}
    for topo in topologies:
        W = rewiring.apply_null(W0, topo, np.random.default_rng(rw))
        circ.net = graph.Connectome(circ.net.n_neurons, circ.net.root_ids, W.tocsr())
        geos, error = [], None
        try:
            for seed in range(seed0, seed0 + seeds):
                wt = tasks.build_tasks(circ, support_size=support, q=q, seed=seed, rho=rho)
                geos.append(task_geometry(wt.sequence, wt.ranks))
        except Exception as exc:                                      # a singular propagator, a failed solve
            error = f"{type(exc).__name__}: {exc}"[:120]
        keys = ("effective_rank", "flattening", "mean_rank", "top_eig_share")
        row = {k: (float(np.mean([g[k] for g in geos])) if geos else None) for k in keys}
        row["seeds_measured"] = len(geos)
        row["error"] = error
        out["topologies"][topo] = row
    return out


def stored_geometry(runs: Path = RUNS) -> dict:
    """The corpus's own `geometry` blocks, keyed by (size, topology, rho), from `e230`'s census rows."""
    from experiments.e230_rank_draw_census import rows_of

    out = {}
    for r in rows_of(runs):
        out.setdefault((r["circuit_size"], r["topology"], round(r["rho"], 4)), []).append(
            {"artifact": r["artifact"], "rank": r["rank"], "flattening": r["flattening"]})
    return out


def verify(rows: list[dict], runs: Path = RUNS) -> list[dict]:
    """Does this instrument reproduce the corpus's `geometry` blocks at the `rho` values where they exist?"""
    stored = stored_geometry(runs)
    out = []
    for row in rows:
        if round(row["rho"], 4) not in [round(v, 4) for v in VERIFY_AT]:
            continue
        for topo, cell in row["topologies"].items():
            got = cell.get("effective_rank")
            hits = [s for s in stored.get((row["size"], topo, round(row["rho"], 4)), [])
                    if got is not None and abs(s["rank"] - got) <= 1e-6 * max(abs(got), 1e-12)]
            out.append({"size": row["size"], "topology": topo, "rho": row["rho"], "measured": got,
                        "matches": [h["artifact"] for h in hits],
                        "stored_values": [round(s["rank"], 4) for s in
                                          stored.get((row["size"], topo, round(row["rho"], 4)), [])]})
    return out


def report(rows: list[dict], checks: list[dict] | None = None) -> int:
    rho_values = sorted({r["rho"] for r in rows})
    # a row is one (size, rho) measured at ONE drawing of the null; with more than one drawing in play the curves
    # have to be printed per drawing, or the second drawing of a cell silently overwrites the first in the table
    groups = sorted({(r["size"], r.get("rewire_seed", 0)) for r in rows})
    print("== the effective rank of the task geometry against rho (the corpus's own statistic) ==")
    for size, rw in groups:
        sub = [r for r in rows if r["size"] == size and r.get("rewire_seed", 0) == rw]
        print(f"\n   cs {size}  ({sub[0]['neurons']} neurons, support {sub[0]['support']}, rewire seed {rw})")
        print(f"      {'topology':12} " + " ".join(f"{rho:>7.4g}" for rho in rho_values) + "   verdict")
        for topo in TOPOLOGIES:
            cells = {r["rho"]: r["topologies"].get(topo, {}) for r in sub}
            ranks = [cells.get(rho, {}).get("effective_rank") for rho in rho_values]
            if any(v is None for v in ranks):
                print(f"      {topo:12} " + " ".join(
                    "      -" if v is None else f"{v:7.2f}" for v in ranks) + "   UNMEASURABLE")
                continue
            rises = [b > a for a, b in zip(ranks, ranks[1:])]
            verdict = ("falls monotonically" if not any(rises) else
                       f"RISES at {[f'{rho_values[i + 1]:.3g}' for i, up in enumerate(rises) if up]}")
            print(f"      {topo:12} " + " ".join(f"{v:7.2f}" for v in ranks) + f"   {verdict}")
    if rows:
        print("\n   the asymmetry the curve is about (in-structure destroyed vs out-structure destroyed), by drawing:")
        for size in sorted({r["size"] for r in rows}):
            for rw in sorted({r.get("rewire_seed", 0) for r in rows if r["size"] == size}):
                sub = [r for r in rows if r["size"] == size and r.get("rewire_seed", 0) == rw]
                parts = []
                for rho in rho_values:
                    r = next((x for x in sub if x["rho"] == rho), None)
                    if r is None:
                        continue
                    a = r["topologies"].get("alloy1", {}).get("effective_rank")
                    b = r["topologies"].get("inalloy1", {}).get("effective_rank")
                    parts.append(f"{rho:g}: {'-' if not (a and b) else f'{a / b:.2f}x'}")
                print(f"      cs {size} rewire seed {rw:<3} ratio alloy1/inalloy1   " + "  ".join(parts))
    if checks:
        print("\n== does this instrument reproduce the corpus's own geometry blocks? ==")
        for c in checks:
            got = "-" if c["measured"] is None else f"{c['measured']:.4f}"
            tag = (f"matches {', '.join(c['matches'])}" if c["matches"]
                   else f"NO MATCH (stored {c['stored_values']})")
            print(f"      cs {c['size']} {c['topology']:12} rho {c['rho']:<5.4g} measured {got}   {tag}")
    bad = sum(1 for r in rows for cell in r["topologies"].values() if cell.get("effective_rank") is None)
    print(f"\n   unmeasurable cells: {bad}")
    return bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grid", default=",".join(str(r) for r in DEFAULT_GRID),
                    help="comma-separated rho values")
    ap.add_argument("--sizes", default="300,800")
    ap.add_argument("--support", type=int, default=None, help="override the corpus's convention (size / 10)")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--seed0", type=int, default=0)
    ap.add_argument("--rewire-seed", type=int, default=None,
                    help="seed the null's own stream separately from the tasks (the runner's flag); without it "
                         "`seed0` drives both, so a curve is ONE drawing of the null")
    ap.add_argument("--q", type=float, default=0.02)
    ap.add_argument("--no-verify", action="store_true", help="skip the comparison against the corpus's blocks")
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)

    grid = [float(x) for x in args.grid.split(",") if x.strip()]
    rows = []
    for size in [int(s) for s in args.sizes.split(",") if s.strip()]:
        support = args.support or SIZES.get(size, max(1, size // 10))
        for rho in grid:
            row = measure(size, support, rho, seeds=args.seeds, seed0=args.seed0, q=args.q,
                          rewire_seed=args.rewire_seed)
            row["rho"] = rho
            rows.append(row)
            ranks = {t: c.get("effective_rank") for t, c in row["topologies"].items()}
            print(f"   cs {size} rho {rho:<6.4g} rw {row['rewire_seed']} " + "  ".join(
                f"{t} {'-' if v is None else f'{v:6.2f}'}" for t, v in ranks.items()), flush=True)
    checks = None if args.no_verify else verify(rows)
    if args.json_out:
        write_json(args.json_out, {"rows": rows, "verify": checks, "grid": grid})
        print(f"wrote {args.json_out}")
    return report(rows, checks)


if __name__ == "__main__":
    sys.exit(main())
