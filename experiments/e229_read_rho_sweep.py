"""E229 -- the assembly geometry against the ladder's top step: does `rho` move what the circuit size moves?

`e228` registered three claims before its runs and this reader decides them **against references recomputed from the
artifacts that measured them**, never against the registration's prose: the `rho = 0.9` cells at both sizes are on
disk (`e217_ladder_cs300.json`; `e208`'s `erdos_renyi`, `e212`/`e213`'s `alloy1` and `e216`'s `inalloy1` at cs 800),
and the new cells are `e228_rho{05,99}_cs{300,800}.json`.

The quantity, spelled out because the reader's first job is to say which denominator it used:

- the **one-side level** is the mean of the `alloy1` and `inalloy1` excesses -- the "one degree sequence destroyed"
  rung. Where one artifact carries both families (every `e2_topology_gap` cell does) the level is that artifact's own
  mean; where the references are drawn from different artifacts, each family is averaged over its own drawings and
  both spellings are printed beside the mean.
- the **top step** is (Erdős–Rényi excess) ÷ (the one-side level). **Erdős–Rényi ÷ `real` is a different quantity**
  and is printed as such: at cs 300/`rho` 0.5 it reads 109× while the top step reads 1.02×, because the `real` cell's
  own excess collapses by 135× when `rho` falls.

    python -m experiments.e229_read_rho_sweep
    python -m experiments.e229_read_rho_sweep --json-out runs/e229_read_rho_sweep.json

**What the reference recomputation is for.** The record quotes 1.28× at cs 300 and 2.76×/3.02× at cs 800. This reader
recomputes all three from the artifacts and prints them next to the quoted figures, so that a reader can see which
*spelling* each quoted figure is: **2.76× is ER ÷ `alloy1`'s mean over `e213`'s five drawings** and **3.02× is ER ÷
`inalloy1`'s mean over `e216`'s three**, i.e. they are the two families' spellings of one level rather than one level
and something else.

**What it cannot do**: one drawing per cell, so a single cell's level inherits the one-side families' own spread
(`alloy1` spans 3.34× across five drawings at cs 800 while ER spans 1.05×), and a claim whose margin is smaller than
that spread is refused rather than judged; `rho` rescales the whole weight matrix, so a mechanism read off it is not
a *depth* mechanism; two sizes and three `rho` values admit no interaction term; and nothing here speaks for the
realized arm or the network substrate.

The exit code is the number of claims **REFUSED** -- today, before the design is complete, that is the honest state,
and the verdicts (MET / FALSIFIER FIRED / null) are reported without making the code a statement about the science.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
ONE_SIDE = ("alloy1", "inalloy1")
#: the cells the sweep was registered to write, and the sizes it runs at
TEST_GLOB = "e228_rho*_cs*.json"
#: the `rho = 0.9` references, by the artifact each family's level comes from
REF_CS300 = ("e217_ladder_cs300.json",)
REF_CS800_ER = ("e208_hole_sweep_cs800_3seeds.json",)
REF_CS800_ONE_SIDE = {"alloy1": ("e212_alloy_analytic_rs0.json", "e212_alloy_analytic_rs1.json",
                                "e213_alloy_draws_rs0.json", "e213_alloy_draws_rs1.json",
                                "e213_alloy_draws_rs2.json", "e213_alloy_draws_rs3.json",
                                "e213_alloy_draws_rs4.json"),
                      "inalloy1": ("e216_inalloy_rs0.json", "e216_inalloy_rs1.json", "e216_inalloy_rs2.json")}
#: the quoted figures, and the spelling each is (printed beside the recomputation so a disagreement is visible)
QUOTED = {"cs300_top_step": 1.28, "cs800_alloy1": 2.76, "cs800_inalloy1": 3.02}
#: `rho` values the design registers per size, and the two bars the claims turn on
RHO_GRID = (0.5, 0.9, 0.99)
R1_COVER = 2.76   # R1: at cs 300 the top step's range covers [1.28x, 2.76x]
R1_FALSIFIER = 1.5
R3_BAR, R3_FALSIFIER = 1.5, 1.2
#: the one-side families' own drawing spread at cs 800, which is what a one-drawing cell inherits
ONE_SIDE_SPREAD = 3.34

CLAIMS = (
    ("R1", "the assembly geometry against the size gap",
     "At cs 300 the top step's range over rho in {0.5, 0.9, 0.99} covers [1.28x, 2.76x]",
     "falsifier: the cs-300 top step stays within 1.5x of itself at all three rho, which would leave the size "
     "dependence standing as a size effect; null: a range wider than 1.5x that does not reach cs 800's level"),
    ("R2", "the direction",
     "The top step falls as rho rises (0.5 > 0.9 > 0.99)",
     "falsifier: the reverse ordering, monotone increasing in rho; null: non-monotone, or a spread smaller than the "
     "drawing spreads"),
    ("R3", "the cs-800 headline",
     "The cs-800 top steps at rho != 0.9 are outside 1.5x of the on-disk 2.76x/3.02x, so the 7x jump is a "
     "rho = 0.9 statement",
     "falsifier: within 1.2x of the on-disk value, which would say the headline survives moving the geometry's one "
     "scalar; null: between 1.2x and 1.5x"),
)


def excess_of(block: dict) -> float | None:
    """One topology's analytic diagonalisation excess, or ``None`` when it was not computed."""
    v = ((block.get("diagonal(EWC)") or {}).get("analytic") or {}).get("excess_mean")
    return float(v) if isinstance(v, (int, float)) else None


def read(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, FileNotFoundError):
        return None


def levels_of(payload: dict) -> dict:
    """Every topology's excess in one artifact, keyed by topology name."""
    return {t: v for t, b in (payload.get("topologies") or {}).items()
            if isinstance(b, dict) and (v := excess_of(b)) is not None}


def rho_of(payload: dict, name: str) -> float | None:
    """The `rho` a cell ran at, read from its config and cross-checked against its file name."""
    cfg = payload.get("config") or {}
    v = cfg.get("rho", 0.9)
    v = 0.9 if v is None else float(v)
    tagged = name.rsplit("_cs", 1)[0].replace("e228_rho", "").replace("e228_", "").lstrip("0")
    return v


def cell(path: Path) -> dict | None:
    """One sweep cell: its levels, its own one-side mean, and the top step in all three spellings."""
    payload = read(path)
    if payload is None:
        return None
    lv = levels_of(payload)
    if any(t not in lv for t in ("real", "erdos_renyi")) or not all(t in lv for t in ONE_SIDE):
        return None
    ones = [lv[t] for t in ONE_SIDE]
    mean = sum(ones) / len(ones)
    return {"artifact": path.name, "rho": rho_of(payload, path.name),
            "circuit_size": (payload.get("config") or {}).get("circuit_size"),
            "levels": lv, "one_side_mean": mean,
            "top_step": lv["erdos_renyi"] / mean if mean else float("nan"),
            "top_step_by_family": {t: lv["erdos_renyi"] / lv[t] for t in ONE_SIDE},
            "er_over_real": lv["erdos_renyi"] / lv["real"] if lv["real"] else float("nan")}


def references(directory: Path = RUNS) -> dict:
    """The `rho = 0.9` references, RECOMPUTED from the artifacts that measured them."""
    out = {"cs300": None, "cs800": None, "cs300_artifacts": 0, "cs800_drawings": {}}
    for name in REF_CS300:
        c = cell(directory / name)
        if c is not None:
            out["cs300"] = c
            out["cs300_artifacts"] += 1
    payload = read(directory / REF_CS800_ER[0])
    er = levels_of(payload).get("erdos_renyi") if payload else None
    fams = {}
    for topo, names in REF_CS800_ONE_SIDE.items():
        vals = []
        for n in names:
            p = read(directory / n)
            if p is None:
                continue
            v = levels_of(p).get(topo)
            if v is not None:
                vals.append(v)
        fams[topo] = vals
        out["cs800_drawings"][topo] = len(vals)
    if er is not None and all(fams.values()):
        means = {t: sum(v) / len(v) for t, v in fams.items()}
        level = sum(means.values()) / len(means)
        out["cs800"] = {"erdos_renyi": er, "family_means": means, "one_side_mean": level,
                        "top_step": er / level,
                        "top_step_by_family": {t: er / means[t] for t in means},
                        "top_step_alloy1_over_all_drawings":
                            er / (sum(fams["alloy1"]) / len(fams["alloy1"]))}
    return out


def judge(cells: list[dict], refs: dict) -> list[dict]:
    """R1-R3 as verdicts, REFUSED rather than guessed whenever THAT claim's own requirements are unmet.

    The three claims do not need the same cells: R1 and R2 are statements about the cs-300 grid (where the
    `rho = 0.9` member is the reference artifact), and only R3 needs the cs-800 cells. Refusing all three together
    would let an incomplete half of the design hide a verdict the other half can already carry.
    """
    by_size = {}
    for c in cells:
        by_size.setdefault(c["circuit_size"], {})[c["rho"]] = c
    if refs["cs300"] is None or refs["cs800"] is None:
        absent = "cs 300" if refs["cs300"] is None else "cs 800"
        return [{"id": c[0], "verdict": f"REFUSED -- the rho = 0.9 reference for {absent} could not be read from "
                                        f"its own artifacts, and a claim against a remembered number is not a "
                                        f"claim"} for c in CLAIMS]
    # the rho = 0.9 cell of BOTH sizes is the reference artifact, not a cell of the sweep
    missing300 = sorted(set(RHO_GRID) - (set(by_size.get(300, {})) | {0.9}))
    missing800 = sorted(set(RHO_GRID) - (set(by_size.get(800, {})) | {0.9}))
    need300 = f"cs 300: rho {missing300}" if missing300 else None
    need800 = f"cs 800: rho {missing800}" if missing800 else None
    out = []
    if need300:
        out += [{"id": two[0], "verdict": f"REFUSED -- this claim needs {need300} and the design is incomplete"}
                for two in CLAIMS[:2]]
    if need800:
        out.append({"id": "R3", "verdict": f"REFUSED -- this claim needs {need800} and the design is incomplete"})
    if not need300:
        grid300 = {rho: by_size[300][rho]["top_step"] for rho in RHO_GRID if rho in by_size[300]}
        grid300[0.9] = refs["cs300"]["top_step"]
        order = [grid300[r] for r in RHO_GRID]                 # rho ascending: 0.5, 0.9, 0.99
        lo, hi = min(order), max(order)
        span = hi / lo if lo else float("inf")
        out.append({"id": "R1",
                    "measured": f"cs-300 top steps {', '.join(f'{r}: {grid300[r]:.3f}x' for r in RHO_GRID)} "
                                f"(span {span:.2f}x)",
                    "verdict": "MET -- the range covers cs 800's level" if hi >= R1_COVER else
                               "FALSIFIER FIRED -- within 1.5x of itself at all three rho" if span < R1_FALSIFIER
                               else f"null band -- spans {span:.2f}x, wider than 1.5x but short of cs 800's "
                                    f"{R1_COVER:.2f}x"})
        monotone_fall = all(order[i] > order[i + 1] for i in range(len(order) - 1))
        monotone_rise = all(order[i] < order[i + 1] for i in range(len(order) - 1))
        out.append({"id": "R2",
                    "measured": f"rho ascending -> {', '.join(f'{v:.3f}x' for v in order)}",
                    "verdict": "MET -- the top step falls as rho rises" if monotone_fall else
                               "FALSIFIER FIRED -- the reverse ordering: it rises with rho" if monotone_rise else
                               "null band -- non-monotone across the three rho"})
    if not need800:
        ref800 = refs["cs800"]["top_step"]
        ratios = {rho: by_size[800][rho]["top_step"] / ref800 for rho in (0.5, 0.99)}
        off = min(abs(r - 1.0) for r in ratios.values())
        out.append({"id": "R3",
                    "measured": f"cs-800 new cells "
                                f"{', '.join(f'{r}: {by_size[800][r]['top_step']:.3f}x' for r in (0.5, 0.99))} "
                                f"against the reference {ref800:.3f}x",
                    "verdict": (f"MET -- the new cells are {min(ratios.values()):.2f}x-{max(ratios.values()):.2f}x "
                                f"of the reference" if off >= R3_BAR - 1 else
                                "FALSIFIER FIRED -- within 1.2x of the on-disk value" if off < R3_FALSIFIER - 1 else
                                "null band -- between 1.2x and 1.5x of the reference")})
    return sorted(out, key=lambda r: r["id"])


def report(cells: list[dict], refs: dict) -> int:
    print("== the e228 cells ==")
    for c in sorted(cells, key=lambda c: (c["circuit_size"], c["rho"])):
        lv = c["levels"]
        print(f"   cs {c['circuit_size']} rho {c['rho']:<5} real {lv['real']:.5f}  alloy1 {lv['alloy1']:.5f}  "
              f"inalloy1 {lv['inalloy1']:.5f}  erdos_renyi {lv['erdos_renyi']:.5f}")
        print(f"        one-side mean {c['one_side_mean']:.5f}  top step {c['top_step']:.3f}x "
              f"(by family {c['top_step_by_family']['alloy1']:.3f}x / {c['top_step_by_family']['inalloy1']:.3f}x)  "
              f"ER/real {c['er_over_real']:.2f}x")
    print("\n== the rho = 0.9 references, RECOMPUTED here from the artifacts that measured them ==")
    if refs["cs300"] is None:
        print("   cs 300: NOT READABLE from e217_ladder_cs300.json")
    else:
        c = refs["cs300"]
        note = "" if abs(c["top_step"] - QUOTED["cs300_top_step"]) <= 0.05 * QUOTED["cs300_top_step"] else \
            f"   NOTE: the record quotes {QUOTED['cs300_top_step']:.2f}x"
        print(f"   cs 300 (): one-side mean {c['one_side_mean']:.5f}  top step {c['top_step']:.3f}x"
              .replace("()", f"`{c['artifact']}`") + note)
    r8 = refs["cs800"]
    if r8 is None:
        print("   cs 800: NOT READABLE from e208/e212/e213/e216")
    else:
        print(f"   cs 800: erdos_renyi {r8['erdos_renyi']:.5f}  family means "
              f"{', '.join(f'{t} {v:.5f}' for t, v in r8['family_means'].items())} "
              f"({refs['cs800_drawings']} drawings)")
        print(f"           one-side mean {r8['one_side_mean']:.5f}  top step {r8['top_step']:.3f}x "
              f"(by family {r8['top_step_by_family']['alloy1']:.3f}x / "
              f"{r8['top_step_by_family']['inalloy1']:.3f}x) -- so the record's "
              f"{QUOTED['cs800_alloy1']:.2f}x and {QUOTED['cs800_inalloy1']:.2f}x are the two FAMILIES' spellings "
              f"of one level, and the mean spelling is {r8['top_step']:.3f}x")
    print("\n== the registered claims, R1-R3 ==")
    refused = 0
    for c, row in zip(CLAIMS, judge(cells, refs)):
        print(f"        {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"             the claim was: {c[2]}")
        print(f"             and its {c[3]}")
        if "REFUSED" in row["verdict"]:
            refused += 1
    print(f"\n   (one drawing per cell, against one-side spreads of {ONE_SIDE_SPREAD:.2f}x at cs 800: a cell whose")
    print("    margin is smaller than that spread is not resolved by this design, whatever its verdict says)")
    return refused


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    cells = [c for c in (cell(Path(p)) for p in sorted(glob.glob(str(args.runs / TEST_GLOB)))) if c is not None]
    refs = references(args.runs)
    if args.json_out:
        write_json(args.json_out, {"cells": cells, "references": refs, "claims": judge(cells, refs)})
        print(f"wrote {args.json_out}")
    return report(cells, refs)


if __name__ == "__main__":
    sys.exit(main())
