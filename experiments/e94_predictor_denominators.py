"""E94 -- the predictor's three remaining cs = 300 denominators, measured.

`e93` found that `e64`'s headline count gave **20 of its 25 pairs a d = 1307 draw sd while those pairs ran
at cs = 300**, because `DRAW_SD_SOURCES` is keyed by rung and not by circuit size. `e86`'s cs = 300 half
matched one of the four borrowed conditions exactly (`baseline`: support 30, q 0.02, `real`) and supplied
its five measurements; replacing them left the count at 21 of 25. The other three conditions were left
borrowed, and the reason was that no existing artifact had their configuration:

| condition | cs | support | q | topology | denominators before this script |
|---|---|---|---|---|---|
| `baseline` | 300 | 30 | 0.02 | `real` | **measured** (`e86`, cs = 300) |
| `wider-tasks` | 300 | 60 | 0.02 | `real` | borrowed from d = 1307 |
| `faster-drift` | 300 | 30 | 0.10 | `real` | borrowed from d = 1307 |
| `rewired-swap2` | 300 | 30 | 0.02 | `swap2` | borrowed from d = 1307 |
| `larger-circuit` | 800 | 80 | 0.02 | `real` | correct — `e64`'s sources are cs = 800 / support 80 |

So this script measures the draw sd of each of those three conditions' **five rungs** at cs = 300, at
`e86`'s protocol (3 task seeds, 5 relabellings), and then re-derives all four cs = 300 conditions' σ(rule)
with `e64`'s own arithmetic. Only the predictor's own five rungs are measured — `e86` also ran
`cell_type min 2/3/4/6`, which `e64`'s pairs do not contain.

    python -m experiments.e94_predictor_denominators                 # measure (about 30 min)

Each run is its own artifact, so the sweep is resumable and a partial progress survives.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e12_control_spread import run as e12_run

#: (condition label, support, q, topology) -- `e6_predictor.py`'s CONDITIONS minus the two `e93` calls
#: covered already, and the rungs are `e64`'s five
CONDITIONS = [
    ("wider-tasks", 60, 0.02, "real"),
    ("faster-drift", 30, 0.10, "real"),
    ("rewired-swap2", 30, 0.02, "swap2"),
]
RUNGS = [("cell_type", 1), ("side", 1), ("cell_class", 1),
         ("ito_lee_hemilineage", 1), ("supertype", 1)]


def artifact_path(cond: str, column: str, min_size: int) -> Path:
    return Path(f"runs/e94_drawsd_{cond}_{column}_min{min_size}.json")


def measure(args) -> int:
    t0 = time.time()
    todo = []
    for cond, support, q, topology in CONDITIONS:
        for column, min_size in RUNGS:
            path = artifact_path(cond, column, min_size)
            if path.exists() and not args.overwrite:
                print(f"   {cond:<15}{column} min{min_size}   present, skipped")
                continue
            todo.append((cond, support, q, topology, column, min_size))
    print(f"   {len(todo)} runs to do (of {len(CONDITIONS) * len(RUNGS)})\n")

    for i, (cond, support, q, topology, column, min_size) in enumerate(todo, 1):
        path = artifact_path(cond, column, min_size)
        print(f"=== {i}/{len(todo)}  {cond}  {column} min{min_size}  "
              f"(support {support}, q {q}, {topology})")
        ns = argparse.Namespace(circuit_size=300, support=support, seeds=args.seeds, seed0=0,
                                q=q, column=column, min_size=min_size, draws=args.draws,
                                topology=topology, json_out=path)
        res = e12_run(ns)
        res["condition"] = cond
        res["topology"] = topology
        write_json(path, res)
        print(f"    -> {path}   sd {res['control_sd_across_draws']:.4g}   "
              f"({time.time() - t0:.0f}s elapsed)\n")
    return 0


def report(args) -> int:
    e64 = json.load(open("runs/e64_predictor_per_seed_analysis.json", encoding="utf-8"))
    pairs = e64["pairs"]
    print("=" * 112)
    print("1. THE MEASURED cs = 300 DENOMINATORS")
    print("=" * 112)
    print(f"   {'condition':<15}{'rung':<24}{'cs=300 measured':>17}{'borrowed (d=1307)':>19}{'ratio':>8}")
    measured = {}
    for cond, support, q, topology in CONDITIONS:
        for column, min_size in RUNGS:
            path = artifact_path(cond, column, min_size)
            if not path.exists():
                print(f"   {cond:<15}{column:<24} absent")
                continue
            d = json.load(open(path, encoding="utf-8"))
            new = float(d["control_sd_across_draws"])
            used = next((p["draw_sd"] for p in pairs
                         if p["condition"] == cond and p["rung"] == column), None)
            measured[(cond, column)] = new
            print(f"   {cond:<15}{column:<24}{new:>17.4g}"
                  f"{(used if used else float('nan')):>19.4g}"
                  f"{(new / used if used else float('nan')):>8.2f}")

    print()
    print("=" * 112)
    print("2. EVERY cs = 300 CONDITION RE-DERIVED, WITH `e64`'s OWN ARITHMETIC")
    print("=" * 112)
    print("   sigma(rule) = |delta| / hypot(seed_sem, draw_sd)\n")
    cs300 = ["baseline", "wider-tasks", "faster-drift", "rewired-swap2"]
    print(f"   {'condition':<15}{'rung':<24}{'sigma used':>12}{'sigma measured':>16}"
          f"{'verdict':>14}{'source of the measurement':>28}")
    rows, n_used, n_measured, n_pending = [], 0, 0, 0
    for p in pairs:
        cond, rung = p["condition"], p["rung"]
        delta, seed_sem = abs(float(p["delta"])), float(p["seed_sem"])
        sigma_used = delta / float(np.hypot(seed_sem, p["draw_sd"]))
        if cond == "baseline":
            src = "e86, cs = 300"
            new_sd = measured.get((cond, rung)) or load_e86(rung)
        elif cond in cs300:
            src = "e94, cs = 300"
            new_sd = measured.get((cond, rung))
        else:
            src = "already cs = 800"
            new_sd = p["draw_sd"]
        #: A pair whose measurement is not on disk yet is PENDING, not resolved-false.  Counting a missing
        #: denominator as "fails 2 sigma" is the same misreading the grid report's verdict block had, and it
        #: is worse here because it would make the count move in the direction of the hypothesis under test.
        if new_sd is None:
            verdict = "pending"
            n_pending += 1
            counted = sigma_used
            sigma_new = None
        else:
            sigma_new = delta / float(np.hypot(seed_sem, new_sd))
            n_measured += 1
            moved = (sigma_used > 2) != (sigma_new > 2)
            verdict = "**MOVES**" if moved else "unchanged"
            counted = sigma_new
        if sigma_used > 2:
            n_used += 1
        rows.append(dict(condition=cond, rung=rung, seed_sem=seed_sem, draw_used=p["draw_sd"],
                         sigma_used=sigma_used, draw_measured=new_sd, sigma_measured=sigma_new,
                         source=src, verdict=verdict, call=p["call"], delta=float(p["delta"]),
                         counted_sigma=counted))
        if cond in cs300 or cond == "larger-circuit":
            print(f"   {cond:<15}{rung:<24}{sigma_used:>12.2f}"
                  f"{(sigma_new if sigma_new is not None else float('nan')):>16.2f}"
                  f"{verdict:>14}{src:>28}")
    n_new = sum(1 for r in rows if r["counted_sigma"] is not None and r["counted_sigma"] > 2)
    print()
    print(f"   pairs clearing 2 sigma with the borrowed denominators: {n_used} of {len(pairs)}")
    print(f"   pairs clearing 2 sigma with cs = 300 measured where possible: {n_new} of {len(pairs)}"
          + (f"   ({n_pending} denominator(s) still unmeasured)" if n_pending else ""))
    moved = [r for r in rows if r["verdict"] == "**MOVES**"]
    print(f"   pairs whose verdict changes: {len(moved)}"
          + (f" -> {[(r['condition'], r['rung']) for r in moved]}" if moved else ""))
    out = dict(config=vars(args), measured={f"{k[0]}|{k[1]}": v for k, v in measured.items()}, rows=rows,
               n_rule_2sigma_used=n_used, n_rule_2sigma_measured=n_new, n_pending=n_pending,
               n_moved=len(moved), conditions=[c[0] for c in CONDITIONS],
               rungs=[r[0] for r in RUNGS])
    write_json(args.json_out, out)
    print(f"\nwrote {args.json_out}")
    return 0


def load_e86(rung: str):
    path = Path(f"runs/e86_drawsd_cs300_{rung}_min1.json")
    if not path.exists():
        return None
    return float(json.load(open(path, encoding="utf-8"))["control_sd_across_draws"])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--report-only", action="store_true",
                   help="skip the measurements and read the artifacts already on disk")
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--seeds", type=int, default=3, help="e86's protocol, so the numbers are comparable")
    p.add_argument("--draws", type=int, default=5)
    p.add_argument("--json-out", default="runs/e94_predictor_denominators.json")
    args = p.parse_args(argv)
    if not args.report_only:
        measure(args)
    return report(args)


if __name__ == "__main__":
    raise SystemExit(main())
