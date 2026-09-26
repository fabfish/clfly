"""E239 -- the cs-800 counterexample's exposure: is the 24x gap between two families with the SAME second eigenvalue a property of the families or of the drawing?

`e238` found two things at cs 800 that cannot both be about the spectra: `alloy1` and `inalloy1` have the same second
eigenvalue (1.0000 to four decimals) while their whole-`G` ranks differ by **24x** (29.94 against 1.26). `e232` had
just measured, on the *task* side, that the in/out comparison is **drawing-dependent** — its cs-800 ratio read 10.10x,
1.06x and 0.23x across three drawings — so the honest question about the counterexample is whether it survives a
second and third drawing.

This module re-runs `e237`'s whole-matrix rank and `e238`'s second eigenvalue at three `rewire_seed` values, changing
nothing else, and judges two claims:

- **W1**: at cs 800 and `rho` in {0.9, 0.95, 0.99} the `alloy1 ÷ inalloy1` whole-`G` rank ratio exceeds **4x** in
  **all three** drawings — i.e. the 24x is a property of the two constructions, not of the drawing that showed it.
  **Falsifier**: any drawing at or below 4x.
- **W2**: the two families' second eigenvalues stay **equal** (within 0.01) at cs 800 in all three drawings — i.e. the
  degeneracy that makes the counterexample a counterexample is itself drawing-robust. **Falsifier**: any drawing where
  they differ by more than 0.01, which would dissolve the counterexample (the ranks would differ because the spectra
  do).

Both are cheap: `e237`'s measurement is one factorisation, `n` solves and one dense SVD per cell (seconds at cs 800),
`e238`'s is two ARPACK calls plus one dense SVD per (size, topology).

    python -m experiments.e239_weight_spectrum_drawings --sizes 800 --rhos 0.9,0.95,0.99 --seeds 0,1,2
    python -m experiments.e239_weight_spectrum_drawings --json-out runs/e239_weight_spectrum_drawings.json

The exit code is the number of claims **REFUSED** because a drawing or a statistic is missing.

**What it cannot do**: three drawings are a sample and not a distribution; it repeats `e237`/`e238`'s own conventions
(one `seed0`-driven task stream, the corpus's support size, the whole-matrix measurement) rather than adding a new
one; and it says nothing about the task side, where `e232`'s lottery was measured.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e237_propagator_spectrum as e237
from experiments import e238_weight_spectrum as e238

RUNS = Path("runs")
#: the claims' thresholds, registered before the runs
W1_RATIO_BAR = 4.0
W2_GAP_TOLERANCE = 0.01
CLAIMS = (
    ("W1", "alloy1 over inalloy1 whole-G rank, across drawings",
     "At cs 800 and rho in {0.9, 0.95, 0.99} the alloy1/inalloy1 whole-G rank ratio exceeds 4x in ALL THREE drawings",
     "falsifier: any drawing at or below 4x, which would say the 24x was that drawing's; null: above in two of three"),
    ("W2", "the second eigenvalues' degeneracy, across drawings",
     "At cs 800 the two families' second eigenvalues stay equal within 0.01 in ALL THREE drawings",
     "falsifier: any drawing where they differ by more than 0.01, which would dissolve the counterexample"),
)


def drawings(sizes=(800,), rhos=(0.9, 0.95, 0.99), seeds=(0, 1, 2)) -> list[dict]:
    """One row per (size, drawing): the whole-G ranks and the second eigenvalues of every topology."""
    out = []
    for size in sizes:
        support = e237.SIZES.get(size, max(1, size // 10))
        for seed in seeds:
            spec = e238.normalised_spectrum(size, topologies=e237.TOPOLOGIES, seed0=seed, k=8)
            row = {"size": size, "drawing": seed, "neurons": spec["neurons"], "rhos": {}, "lambda2": {}}
            for topo in e237.TOPOLOGIES:
                la = (spec["topologies"].get(topo) or {}).get("lambda_abs") or []
                row["lambda2"][topo] = la[1] if len(la) > 1 else None
            for rho in rhos:
                m = e237.measure(size, support, rho, topologies=e237.TOPOLOGIES, seed0=seed)
                row["rhos"][rho] = {t: (c or {}).get("pr_G") for t, c in m["topologies"].items()}
            out.append(row)
            print(f"   drawing {seed}: " + "  ".join(
                f"{t} {row['rhos'][rhos[-1]].get(t) if row['rhos'][rhos[-1]].get(t) is None else round(row['rhos'][rhos[-1]][t], 2)}"
                f" (lam2 {row['lambda2'][t] if row['lambda2'][t] is None else round(row['lambda2'][t], 4)})"
                for t in e237.TOPOLOGIES), flush=True)
    return out


def judge(rows: list[dict]) -> list[dict]:
    out = []
    if not rows:
        return [{"id": c[0], "verdict": "REFUSED -- no drawing was measured"} for c in CLAIMS]
    ratios, gaps = {}, {}
    for row in rows:
        for rho, vals in row["rhos"].items():
            a, b = vals.get("alloy1"), vals.get("inalloy1")
            if a is not None and b:
                ratios[(row["size"], row["drawing"], round(rho, 4))] = a / b
        a, b = row["lambda2"].get("alloy1"), row["lambda2"].get("inalloy1")
        if a is not None and b is not None:
            gaps[(row["size"], row["drawing"])] = abs(a - b)
    below = [k for k, v in ratios.items() if v <= W1_RATIO_BAR]
    measured_rhos = {round(r, 4) for row in rows for r in row["rhos"]}
    if len(measured_rhos) < 3:
        out.append({"id": "W1", "verdict": f"REFUSED -- only {len(measured_rhos)} of the three registered rho values "
                                           f"were measured"})
    elif below:
        out.append({"id": "W1", "measured": ", ".join(f"{k[1]}/{k[2]:g}: {v:.2f}x" for k, v in sorted(ratios.items())
                                                     if v <= W1_RATIO_BAR),
                    "verdict": f"FALSIFIER FIRED -- at or below {W1_RATIO_BAR:g}x in {len(below)} of "
                               f"{len(ratios)} (drawing, rho) cells"})
    else:
        out.append({"id": "W1", "measured": f"{min(ratios.values()):.2f}x to {max(ratios.values()):.2f}x over "
                                            f"{len(ratios)} cells",
                    "verdict": f"MET -- the ratio is above {W1_RATIO_BAR:g}x everywhere"})
    big = [k for k, v in gaps.items() if v > W2_GAP_TOLERANCE]
    if not gaps:
        out.append({"id": "W2", "verdict": "REFUSED -- the second eigenvalues are missing"})
    elif big:
        out.append({"id": "W2", "measured": ", ".join(f"drawing {k[1]}: {gaps[k]:.4f}" for k in big),
                    "verdict": f"FALSIFIER FIRED -- the two families' second eigenvalues differ by more than "
                               f"{W2_GAP_TOLERANCE} in {len(big)} drawing(s)"})
    else:
        out.append({"id": "W2", "measured": f"largest gap {max(gaps.values()):.5f} over {len(gaps)} drawings",
                    "verdict": f"MET -- equal within {W2_GAP_TOLERANCE}"})
    return out


def report(rows: list[dict]) -> int:
    print("== the cs-800 counterexample across drawings ==")
    for row in rows:
        rhos = sorted(row["rhos"])
        print(f"\n   drawing {row['drawing']}  ({row['neurons']} neurons)")
        print(f"      {'topology':12} {'lam2':>8} " + " ".join(f"{rho:>9.4g}" for rho in rhos))
        for topo in e237.TOPOLOGIES:
            l2 = row["lambda2"].get(topo)
            ranks = [row["rhos"][rho].get(topo) for rho in rhos]
            print(f"      {topo:12} {'-' if l2 is None else f'{l2:8.4f}'} "
                  + " ".join("        -" if v is None else f"{v:9.2f}" for v in ranks))
        a = row["rhos"][rhos[-1]].get("alloy1")
        b = row["rhos"][rhos[-1]].get("inalloy1")
        if a is not None and b:
            print(f"      alloy1 / inalloy1 at rho {rhos[-1]:g}: {a / b:.2f}x")
    print("\n== the claims, W1-W2 ==")
    refused = 0
    for c, row in zip(CLAIMS, judge(rows)):
        print(f"      {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
        if "REFUSED" in row["verdict"]:
            refused += 1
    print("\n   (three drawings are a sample, and this repeats e237/e238's own conventions rather than adding one)")
    return refused


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sizes", default="800")
    ap.add_argument("--rhos", default="0.9,0.95,0.99")
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    rows = drawings(sizes=tuple(int(s) for s in args.sizes.split(",") if s.strip()),
                    rhos=tuple(float(r) for r in args.rhos.split(",") if r.strip()),
                    seeds=tuple(int(s) for s in args.seeds.split(",") if s.strip()))
    if args.json_out:
        write_json(args.json_out, {"rows": rows, "claims": judge(rows),
                                   "bars": {"W1": W1_RATIO_BAR, "W2": W2_GAP_TOLERANCE}})
        print(f"wrote {args.json_out}")
    return report(rows)


if __name__ == "__main__":
    sys.exit(main())
