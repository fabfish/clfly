"""E230 -- is the task geometry's `effective_rank` a `rho` effect or a DRAWING effect, and which of the record's contrasts survive?

`e229`'s mechanism cross-tab read a rho dependence off the task geometry's shape: the one-side nulls' effective rank
running 26.17 -> 9.41 -> 1.07 at cs 300 and 21.01 against 1.29 at cs 800, a "rank contrast" that orders like the
penalty. Every one of those points is **one drawing**. The corpus already carries enough drawings to ask whether that
is enough, and this audit asks it with the same artifacts the claim came from:

- **within**: for one (circuit size, topology, `rho`) the spread of `effective_rank` across the drawings on disk --
  the family's own scatter, which a single-drawing contrast has to beat;
- **between, as the record read it**: the ratio of the largest to the smallest rank over the `rho` values that carry a
  single drawing (which is what a one-drawing-per-`rho` grid quotes);
- **between, on family means**: the same ratio computed from each `rho` group's mean, which is the quantity a design
  with drawings per cell would have.

    python -m experiments.e230_rank_draw_census
    python -m experiments.e230_rank_draw_census --json-out runs/e230_rank_draw_census.json

The verdict per family is **RESOLVABLE** when the between-`rho` contrast exceeds the family's own within-`rho`
scatter, and **NOT RESOLVABLE** when it does not -- a negative result about a claim, which is the useful kind. The exit
code is the number of families that are not resolvable **and** are not declared in `DECLARED_UNRESOLVABLE` with a
reason; a declared family is one whose volatility is now part of the corpus's preconditions rather than a surprise for
the next claim. A family with fewer than two `rho` groups has **no contrast** and owes no verdict, and the report
states the audit's reach.

**The verdict moved to the MEANS column at 2026-09-26 21:00, and this is why.** The contrast was read from the
single-drawing `rho` cells the record quotes, which is the reading that made this audit a claim about *design* rather
than about the substrate. `e255` and `e256` then drew the whole `rho` grid at both sizes, so the ladder families -- the
ones whose `rho` contrasts the mechanism readings are made of -- have **no single-drawing rho group left**: the as-read
column is undefined for them, they left the table, and the audit silently absorbed an unresolvable family
(cs 800 `alloy1`) for a session before `e257` re-read the same families on the means and found it again. So the
**means** column is now the verdict -- it reaches 11 of the 42 families against the as-read column's 5 -- and the
as-read column is kept, printed and no longer judged, as a diagnostic and as a record of what the corpus once
supported. The declarations are re-derived on the means: cs 800 `alloy1` (7.84 against 16.44, a ratio of 0.48), and
the two cs-300 swap rungs (0.92 and 0.73).

**What it cannot do**: it audits one statistic (`effective_rank`) and not the penalty, so "the rank is unresolvable"
does not by itself say a *penalty* contrast is; the within-scatter is computed at `rho = 0.9` only, because that is
where the drawings are, so a family could in principle be tighter at another `rho`; `flattening` and the alignment
statistics carry their own scatters that this audit does not measure; and the drawings are not independent of when
they were written, so a family whose drawings straddle a code epoch inherits that (see `e227`).
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
REF_RHO = 0.9
#: families whose single-drawing rho contrast is inside their own drawing scatter, with the reason. Declared rather
#: than counted: the corpus now knows the scatter, and the entry is what makes the next claim on that family a
#: decision rather than an accident.
DECLARED_UNRESOLVABLE: dict[tuple, str] = {
    # cs 800 alloy1 was declared on the as-read column on 2026-09-26 18:20, un-declared at 19:20 when e256's
    # drawings took its last single-drawing rho group away -- and re-declared at 21:00 on the MEANS column, which is
    # now the verdict: its contrast is 7.84x against its own scatter 16.44x, a ratio of 0.48, so it fails BOTH readings
    (800, "alloy1"): "its between-rho contrast on the means is 7.84x against its own 16.44x scatter at rho 0.9 -- the "
                     "two-sided family fails both readings, which is why its 19:20 un-declaration was bookkeeping "
                     "rather than a resolution (see e257)",
    (300, "swap0.5"): "its rho contrast on the means is 8.10x against its own within-scatter 8.77x",
    (300, "swap2"): "its rho contrast on the means is 5.65x against its own within-scatter 7.77x",
}
# and THREE entries have been removed as the corpus thickened, which is this audit's third state (see the module's
# notes): cs 300 alloy1 and inalloy1 were un-declared when e255 drew rho 0.5, 0.7 and 0.8, and cs 800 alloy1 at
# 2026-09-26 20:20 when e256 did the same at cs 800 -- all of them now have EVERY rho group at two or more drawings,
# so `between_single` is undefined for them and they leave the table rather than staying declared. A declaration is a
# statement about the corpus's current drawings and not a verdict about the family, and this audit's scope is emptied
# as its cells are drawn: five of its forty-two families are still auditable.
# and two entries were REMOVED 2026-09-26 19:05: cs 300 alloy1 and inalloy1 were declared at 18:20 (their contrasts had
# collapsed to 1.51x and 1.31x) and e255's drawings at rho 0.5, 0.7 and 0.8 took away the last single-drawing rho
# groups at cs 300, so this audit's as-read column is not computable for them at all and they leave the table rather
# than staying declared. A declaration is not permanent: it is a statement about the corpus's current drawings.


def rows_of(root: Path = RUNS) -> list[dict]:
    """Every (artifact, topology) pair that carries a geometry block, with the fields the families are built from."""
    out = []
    for p in sorted(glob.glob(str(root / "*.json"))):
        try:
            d = json.loads(Path(p).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        cfg = d.get("config") or {}
        rho = cfg.get("rho", REF_RHO)
        for topo, block in (d.get("topologies") or {}).items():
            geo = (block or {}).get("geometry") if isinstance(block, dict) else None
            if not isinstance(geo, dict) or "effective_rank" not in geo:
                continue
            excess = ((block.get("diagonal(EWC)") or {}).get("analytic") or {}).get("excess_mean")
            out.append({"artifact": Path(p).name, "topology": topo, "circuit_size": cfg.get("circuit_size"),
                        "rho": REF_RHO if rho is None else float(rho),
                        "rewire_seed": cfg.get("rewire_seed"),
                        "rank": float(geo["effective_rank"]), "flattening": geo.get("flattening"),
                        "excess": float(excess) if isinstance(excess, (int, float)) else None})
    return out


def families(rows: list[dict]) -> list[dict]:
    """Per (circuit size, topology): the within-`rho` scatter and the two between-`rho` contrasts."""
    groups: dict[tuple, dict] = {}
    for r in rows:
        groups.setdefault((r["circuit_size"], r["topology"]), {}).setdefault(r["rho"], []).append(r)
    out = []
    for (size, topo), by_rho in groups.items():
        within = {}
        for rho, rs in by_rho.items():
            ranks = [r["rank"] for r in rs]
            within[rho] = {"n": len(ranks), "min": min(ranks), "max": max(ranks),
                           "spread": max(ranks) / min(ranks) if min(ranks) > 0 else float("inf")}
        singles = {rho: g["max"] for rho, g in within.items() if g["n"] == 1}
        means = {rho: sum(r["rank"] for r in rs) / len(rs) for rho, rs in by_rho.items()}
        ref = within.get(REF_RHO, {"n": 0, "spread": None})
        between_single = (max(singles.values()) / min(singles.values())) if len(singles) > 1 else None
        between_mean = (max(means.values()) / min(means.values())) if len(means) > 1 else None
        out.append({"circuit_size": size, "topology": topo,
                    "rho_groups": {rho: g for rho, g in sorted(within.items())},
                    "within_at_ref": ref["spread"], "drawings_at_ref": ref["n"],
                    "between_single": between_single, "between_mean": between_mean,
                    # the VERDICT is the means column since 2026-09-26 21:00 (see the docstring): the as-read column
                    # needs a single-drawing rho group, and drawing the grid took that away for the families that
                    # matter most, so it is kept as a diagnostic and judged no longer
                    "resolvable": (None if between_mean is None or ref["spread"] is None
                                   else between_mean > ref["spread"]),
                    "as_read_resolvable": (None if between_single is None or ref["spread"] is None
                                           else between_single > ref["spread"])})
    out.sort(key=lambda f: (str(f["circuit_size"]), str(f["topology"])))
    return out


def report(fams: list[dict]) -> int:
    print("== the task geometry's effective rank: within-rho scatter against the between-rho contrasts ==")
    print(f"   ({len(fams)} (size, topology) families; `within` is the spread across drawings at rho = {REF_RHO} and")
    print("    the between-rho contrast is the ratio of the largest to the smallest rank over the rho values, taken")
    print("    ON MEANS -- that is the verdict since 2026-09-26 21:00; 'as read' uses the single-drawing cells the")
    print("    record quotes and is kept as a diagnostic, because drawing the grid took those cells away)")
    print(f"   {'size':>5} {'topology':12} {'rhos':>4} {'drawings':>8} {'within':>9} {'between(means)':>15} "
          f"{'between(as read)':>17}  verdict")
    offenders, no_contrast = [], []
    for f in fams:
        declared = (f["circuit_size"], f["topology"]) in DECLARED_UNRESOLVABLE
        if f["between_mean"] is None:
            verdict = "NO CONTRAST"
            no_contrast.append(f)
        else:
            verdict = "RESOLVABLE" if f["resolvable"] else "NOT RESOLVABLE"
        single = f"{f['between_single']:.2f}" if f["between_single"] is not None else "-"
        print(f"   {f['circuit_size']:>5} {f['topology']:12} {len(f['rho_groups']):>4} {f['drawings_at_ref']:>8} "
              f"{(f['within_at_ref'] if f['within_at_ref'] is not None else float('nan')):>9.2f} "
              f"{(f['between_mean'] if f['between_mean'] is not None else float('nan')):>15.2f} {single:>17}  "
              f"{verdict}" + ("  [DECLARED]" if declared else ""))
        if verdict == "NOT RESOLVABLE" and not declared:
            offenders.append(f)
    for f in offenders:
        print(f"   NOT RESOLVABLE AND NOT DECLARED: cs {f['circuit_size']} {f['topology']} -- its between-rho contrast "
              f"on the means {f['between_mean']:.2f}x is inside its own scatter {f['within_at_ref']:.2f}x")
    print(f"   ({len(no_contrast)} of {len(fams)} families carry a single rho group, so neither reading applies to "
          f"them and no verdict is owed; the audit's reach is {len(fams) - len(no_contrast)} of {len(fams)})")
    for key, why in DECLARED_UNRESOLVABLE.items():
        if not any((f["circuit_size"], f["topology"]) == key for f in fams):
            print(f"   NOTE: declared family cs {key[0]} {key[1]} is not in the corpus")
        else:
            print(f"   declared cs {key[0]} {key[1]}: {why}")
    print("\n   (a family that IS resolvable here is not thereby correct: this asks only whether the design that")
    print("    quoted it could see an effect that large, and a contrast inside its own scatter is a number about the")
    print("    drawing as much as about `rho`)")
    return len(offenders)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    rows = rows_of(args.runs)
    fams = families(rows)
    if args.json_out:
        write_json(args.json_out, {"rows": len(rows), "families": fams,
                                   "declared_unresolvable": {f"cs{k[0]}_{k[1]}": v
                                                             for k, v in DECLARED_UNRESOLVABLE.items()}})
        print(f"wrote {args.json_out}")
    return report(fams)


if __name__ == "__main__":
    sys.exit(main())
