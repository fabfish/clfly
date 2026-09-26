"""E244 -- the drawing spread by construction KIND: does destroying more degree structure also make a penalty more reproducible?

The ladder says the *level* of the penalty follows how many degree sequences a construction destroys (0 for `swap*`
and `signshuffle`, 1 for `alloy*`/`inalloy*`, 2 for `erdos_renyi`), and the last four fires established that a
cross-family comparison in this corpus is a **draw** while a level measured over a few drawings is a **number**. Those
two facts together raise a question nobody has asked, and the corpus can answer it without new runs:

    is the SPREAD of the penalty across drawings itself ordered by the same axis as its level?

At cs 800/support 80/`rho` 0.9 alone there are drawings of `swap0.5`, `swap2`, `swap8`, `swap16`, `swap32`, `swap64`,
`signshuffle`, `alloy0.25`…`alloy1`, `inalloy1` and `erdos_renyi` -- seven or more constructions with two or more
drawings each, inside one cell. Seven cells carry a group with two drawings in total.

    python -m experiments.e244_drawing_spread_by_kind
    python -m experiments.e244_drawing_spread_by_kind --json-out runs/e244_drawing_spread_by_kind.json

The **kind** of a construction is declared from its name and its own definition in `clfly/connectome/rewiring.py`:

| kind | destroy 0 degree sequences | destroy 1 | destroy 2 |
|---|---|---|---|
| names | `swap*`, `signshuffle` | `alloy*`, `inalloy*` | `erdos_renyi` |

`real` is **not** a construction and is reported separately as a control: it is never redrawn, so its spread across
drawings is exactly 1.00 by construction and it cannot be a member of any kind. (The first run of this module did
include it and that alone moved kind 0's pooled median from 1.45x to 1.26x.)

Three registered claims. **K1** and **K2** pool over cells and were fixed before the first run; **K3** is the
discriminating one and was written after the first run's pooled output, which is disclosed here and in the finding
because a pooled ordering can survive on cell composition alone:

- **K1 -- the pooled spread orders with the destruction count.** Over the (cell, family) groups with at least two
  drawings, the **median** excess spread is smallest for kind 2 and largest for kind 0, with kind 1 between them **and
  the kind-2 and kind-0 ranges not overlapping**. **Falsifier**: kind 2's median at or above kind 0's; **null**: the
  medians ordered but the ranges overlapping.
- **K2 -- it is not only the level.** The same ordering holds for the **scale-free** relative spread
  `(max - min) / mean` of each group, so a kind is not merely higher or lower but tighter or looser. **Falsifier**: the
  relative spreads unordered. (The first implementation divided the ratio spread by the mean, which is dominated by the
  mean and not scale-free; it is replaced here and the change is disclosed in the finding.)
- **K3 -- the ordering is not an artifact of pooling cells.** Within **every** cell in which two kinds both have at
  least two drawings, the kind that destroys more degree sequences has the smaller **median** spread. **Falsifier**:
  any cell-pair in which that fails -- which would mean the pooled K1 orders cells rather than constructions.

The exit code is the number of claims **REFUSED** because a kind has no group with two drawings; a claim whose
falsifier fired is a result, not an error, and exits 0.

**What it cannot do**: the drawings are the corpus's accidental ones and they are unevenly distributed across kinds
(kind 0 exists at two cells, three families at each, and kind 2 is only ever `erdos_renyi`); kind and level are
**collinear** across this corpus, since `erdos_renyi` has both the highest excess and the tightest spread, so nothing
here separates "destroys more degree structure" from "sits at a higher penalty"; a level near zero cannot spread far in
absolute terms; and nothing here is
a new measurement.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import median

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
KIND_NAMES = {0: ("swap", "signshuffle"), 1: ("alloy", "inalloy"), 2: ("erdos_renyi",)}
CONTROL = "real"
CLAIMS = (
    ("K1", "the pooled spread orders with the destruction count",
     "Over the (cell, family) groups with two or more drawings, the median excess spread is smallest for kind 2 and "
     "largest for kind 0, with kind 1 between, and the kind-2 and kind-0 ranges do not overlap",
     "falsifier: kind 2's median at or above kind 0's; null: the medians ordered but the ranges overlapping"),
    ("K2", "it is not only the level",
     "The same ordering holds for the scale-free relative spread (max - min)/mean of each group",
     "falsifier: the relative spreads unordered"),
    ("K3", "the ordering is not an artifact of pooling cells",
     "Within every cell in which two kinds both have two or more drawings, the kind that destroys more degree "
     "sequences has the smaller median spread",
     "falsifier: any cell-pair in which that fails"),
)


def kind_of(family: str) -> int | None:
    """Which of the three rungs a construction belongs on, read off its name and its definition in `rewiring.py`."""
    if family == CONTROL:
        return None
    if family == "erdos_renyi":
        return 2
    if family.startswith(("alloy", "inalloy")):
        return 1
    if family.startswith("swap") or family == "signshuffle":
        return 0
    return None


def _draws(root: Path) -> dict:
    """Every artifact keyed by (cell, family, drawing): the excesses and ranks it carries."""
    cells: dict = defaultdict(lambda: defaultdict(dict))
    for p in sorted(glob.glob(str(root / "*.json"))):
        try:
            d = json.loads(Path(p).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        cfg = d.get("config") or {}
        if not cfg or cfg.get("seeds") is None:
            continue
        rho = cfg.get("rho", 0.9)
        rho = 0.9 if rho is None else float(rho)
        rw = cfg.get("rewire_seed")
        rw = 0 if rw is None else int(rw)
        for topo, b in (d.get("topologies") or {}).items():
            if not isinstance(b, dict) or (kind_of(topo) is None and topo != CONTROL):
                continue
            key = (cfg.get("circuit_size"), cfg.get("support"), round(rho, 4))
            slot = cells[key][topo]
            if rw not in slot:                        # one artifact per (cell, family, drawing)
                slot[rw] = {"excess": ((b.get("diagonal(EWC)") or {}).get("analytic") or {}).get("excess_mean"),
                            "rank": (b.get("geometry") or {}).get("effective_rank"),
                            "artifact": Path(p).name}
    return cells


def groups(root: Path = RUNS) -> tuple[list[dict], list[dict]]:
    """The (cell, family) groups with two or more drawings, and the control's -- separately, because `real` is not drawn."""
    cells = _draws(root)
    out, control = [], []
    for cell, fams in sorted(cells.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1]), kv[0][2])):
        for family, draws in sorted(fams.items()):
            ex = [v["excess"] for v in draws.values() if isinstance(v["excess"], (int, float))]
            rk = [v["rank"] for v in draws.values() if isinstance(v["rank"], (int, float))]
            if len(ex) < 2 and len(rk) < 2:
                continue
            mean_ex = (sum(ex) / len(ex)) if ex else None
            row = {"cell": cell, "family": family, "kind": kind_of(family), "drawings": len(draws),
                   "excess_spread": (max(ex) / min(ex)) if len(ex) > 1 and min(ex) > 0 else None,
                   "excess_mean": mean_ex,
                   "excess_rel_range": ((max(ex) - min(ex)) / mean_ex) if len(ex) > 1 and mean_ex else None,
                   "rank_spread": (max(rk) / min(rk)) if len(rk) > 1 and min(rk) > 0 else None,
                   "artifacts": sorted(v["artifact"] for v in draws.values())}
            (control if row["kind"] is None else out).append(row)
    return out, control


def _pool(gs: list[dict], field: str) -> dict[int, list[float]]:
    by_kind: dict[int, list[float]] = defaultdict(list)
    for g in gs:
        v = g[field]
        if v is not None:
            by_kind[g["kind"]].append(v)
    return by_kind


def _cell_kinds(gs: list[dict], field: str) -> dict:
    """Per cell, per kind, the list of its families' spreads -- a kind is usually a single family in a cell."""
    cells: dict = defaultdict(lambda: defaultdict(list))
    for g in gs:
        if g[field] is not None:
            cells[g["cell"]][g["kind"]].append(g[field])
    return cells


def _spelling(out: list[dict], cid: str, by_kind: dict, ok: bool, met: str) -> None:
    """Append a claim's row: the pooling it was measured over, then its verdict -- REFUSED when a kind is absent."""
    measured = ", ".join(
        f"kind {k}: n={len(v)} median {median(v):.4g} range [{min(v):.4g}, {max(v):.4g}]"
        for k, v in sorted(by_kind.items()))
    out.append({"id": cid, "verdict": "REFUSED -- a kind has no group with two drawings"} if not ok
               else {"id": cid, "measured": measured, "verdict": met})


def judge(gs: list[dict]) -> list[dict]:
    """K1 pooled, K2 scale-free, K3 within-cell -- in that order."""
    out: list[dict] = []
    by_kind = _pool(gs, "excess_spread")
    ok = all(by_kind.get(k) for k in KIND_NAMES)
    met = "REFUSED -- a kind has no group with two drawings"
    if ok:
        med = {k: median(v) for k, v in by_kind.items()}
        ordered = med[2] < med[1] < med[0]
        disjoint = max(by_kind[2]) < min(by_kind[0])
        met = ("FALSIFIER FIRED -- the medians are not ordered kind 2 < 1 < 0" if not ordered else
               "MET -- ordered and the kind-2 and kind-0 ranges are disjoint" if disjoint else
               "null band -- ordered but the kind-2 and kind-0 ranges overlap")
    _spelling(out, "K1", by_kind, ok, met)

    rel = _pool(gs, "excess_rel_range")
    ok2 = all(rel.get(k) for k in KIND_NAMES)
    met2 = "REFUSED -- a kind has no group with two drawings"
    if ok2:
        med_r = {k: median(v) for k, v in rel.items()}
        met2 = ("MET -- the relative spreads order the same way" if med_r[2] < med_r[1] < med_r[0]
                else "FALSIFIER FIRED -- the relative spreads are unordered")
    _spelling(out, "K2", rel, ok2, met2)

    cells = _cell_kinds(gs, "excess_spread")
    pairs, support, reversals = [], 0, []
    for cell, ks in sorted(cells.items(), key=lambda kv: str(kv[0])):
        med = {k: median(v) for k, v in ks.items()}
        for hi, lo in ((2, 1), (1, 0)):
            if hi in med and lo in med:
                pairs.append((cell, hi, lo))
                if med[hi] < med[lo]:
                    support += 1
                else:
                    reversals.append(f"cs {cell[0]}/sup {cell[1]}: kind {hi} {med[hi]:.2f}x >= kind {lo} {med[lo]:.2f}x")
    if not pairs:
        out.append({"id": "K3", "verdict": "REFUSED -- no cell carries two kinds with two drawings each"})
    else:
        out.append({"id": "K3",
                    "measured": f"{support} of {len(pairs)} cell-pairs support the ordering"
                                + ("; reversed: " + "; ".join(reversals) if reversals else ""),
                    "verdict": "MET -- every cell-pair supports it" if support == len(pairs) else
                               "FALSIFIER FIRED -- a cell reverses the pooled ordering"})
    return out


def report(gs: list[dict], control: list[dict]) -> int:
    print("== the drawing spread of the excess, by (cell, family) ==")
    print(f"   {'cell':>22} {'family':16} kind {'draw':>4} {'excess spread':>13} {'rel range':>10} {'rank spread':>12} {'mean excess':>12}")
    for g in sorted(gs, key=lambda g: (g["cell"], g["kind"], g["family"])):
        cell = f"cs {g['cell'][0]}/sup {g['cell'][1]}/rho {g['cell'][2]:g}"
        print(f"   {cell:>22} {g['family']:16} {g['kind']:>4} {g['drawings']:>4} "
              f"{(g['excess_spread'] if g['excess_spread'] is not None else float('nan')):>13.2f} "
              f"{(g['excess_rel_range'] if g['excess_rel_range'] is not None else float('nan')):>10.3f} "
              f"{(g['rank_spread'] if g['rank_spread'] is not None else float('nan')):>12.2f} "
              f"{(g['excess_mean'] if g['excess_mean'] is not None else float('nan')):>12.5f}")
    print("\n== the same, collapsed per cell: a kind's spread is the median over its families there ==")
    print("   (this is where K3 bites; kind 2 is always the single family `erdos_renyi`)")
    cells = _cell_kinds(gs, "excess_spread")
    for cell, ks in sorted(cells.items(), key=lambda kv: str(kv[0])):
        parts = [f"kind {k}: {median(v):.2f}x (n={len(v)} fam)" for k, v in sorted(ks.items())]
        print(f"   cs {cell[0]}/sup {cell[1]}/rho {cell[2]:g}".ljust(28) + "   ".join(parts))
    print("\n== the same axis on the RANK spread, which reaches the stronger swaps the excess never did ==")
    rk = _cell_kinds(gs, "rank_spread")
    for cell, ks in sorted(rk.items(), key=lambda kv: str(kv[0])):
        parts = [f"kind {k}: {median(v):.2f}x (n={len(v)})" for k, v in sorted(ks.items())]
        print(f"   cs {cell[0]}/sup {cell[1]}/rho {cell[2]:g}".ljust(28) + "   ".join(parts))
    print("   (the excess rung stops at `swap2`/`signshuffle`: `e209`'s screens are `--geometry-only` runs, so the")
    print("    excess is absent for `swap8` up -- the rank rung reaches all six swap strengths)")
    print("\n== the control: `real` is not a construction and must not be redrawn ==")
    for g in control:
        print(f"   {g['artifacts'][0]:>46}  excess spread {g['excess_spread']}  rank spread {g['rank_spread']}  "
              f"over {g['drawings']} artifacts")
    print("   -> spread exactly 1.0 means the two artifacts carry the same number: `real` is invariant across drawings.")
    print("\n== the registered claims, K1-K3 ==")
    j = judge(gs)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (kind and level are collinear across this corpus -- `erdos_renyi` has both the highest excess and the")
    print("    tightest spread -- so nothing here separates the destruction count from the penalty's height)")
    return sum("REFUSED" in r["verdict"] for r in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    gs, control = groups(args.runs)
    if args.json_out:
        write_json(args.json_out, {"groups": [{**g, "cell": list(g["cell"])} for g in gs],
                                   "control": [{**g, "cell": list(g["cell"])} for g in control],
                                   "claims": judge(gs)})
        print(f"wrote {args.json_out}")
    return report(gs, control)


if __name__ == "__main__":
    sys.exit(main())
