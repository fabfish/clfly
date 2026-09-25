"""E224 -- the share against the size: is the one-side level set by the share of the circuit engaged, or by the circuit?

`e221` moved the support at cs 800 and answered one half of the ladder: the one-side level is **1.42x** higher at a
1.53% share than at a 12.24% share, while the top step is not organised by the share at all. But every cell in that
comparison is at ONE circuit size, where the support count and the share move together — so the circuit-size
dependence of the one-side level (0.047–0.051 at cs 800 against 0.122–0.139 at cs 300–400) still has two candidate
explanations. `e223` runs **cs 400 at support 80**, a **7.9% share** (80/1010) that sits between cs 800's 6.1% and
cs 400's own convention of 4.0%, and this reader decides two claims against the references it computes **from the
artifacts** rather than from the registration's prose:

    python -m experiments.e224_share_vs_size_read
    python -m experiments.e224_share_vs_size_read --json-out runs/e224_share_vs_size_read.json

  * **S1 — the share, at a second circuit size**: the one-side level's mean at cs 400/support 80 is below its mean at
    cs 400/support 40 by at least **1.5x** (i.e. at or below ≈0.0877). Falsifier: at or above the support-40 level,
    which would say the share does not lower the one-side level at cs 400 at all; null: a drop smaller than 1.5x.
  * **S2 — which candidate wins**: the level lies **below the midpoint** of the two shares it sits between — cs 400's
    4.0% and cs 800's 6.1% — so it tracks the **share** more than the **size**. Falsifier: at or above the cs-400/
    support-40 level, which would say the level is set by the circuit; null: between the midpoint and that level.

The two references are recomputed here from the artifacts that measured them
(`e217_ladder_cs400.json` plus `e219_draws_cs400_rs*.json` for cs 400/support 40, `e213_alloy_draws_rs*.json` for
`alloy1` and `e216_inalloy_rs*.json` for `inalloy1` at cs 800/support 80), and the registration's own numbers are
printed beside them so a disagreement is visible instead of silent.

**What it cannot do**: one new support at one new size is a two-point test of two candidates and not a share axis;
it does not explain the top step; the drawing spreads at cs 800 (1.29x and 1.67x) are the same order as the effect,
so a mean of two drawings per cell is what the claims rest on; and cs 300 and cs 500–700 are not part of this test.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
#: the cells whose one-side levels the claims are stated against, by artifact-name patterns
TEST_PREFIX = "e223_cs400_support80_rs"
REF_400_40 = ("e217_ladder_cs400.json", "e219_draws_cs400_rs0.json", "e219_draws_cs400_rs1.json",
              "e219_draws_cs400_rs2.json")
REF_800_80 = ("e213_alloy_draws_rs0.json", "e213_alloy_draws_rs1.json", "e213_alloy_draws_rs2.json",
              "e213_alloy_draws_rs3.json", "e213_alloy_draws_rs4.json", "e216_inalloy_rs0.json",
              "e216_inalloy_rs1.json", "e216_inalloy_rs2.json")
ONE_SIDE = ("alloy1", "inalloy1")
#: the design's own drawing count, and the two registered figures the reader checks itself against
EXPECTED_DRAWINGS = 2
REGISTERED = {"cs400_support40": 0.1315, "cs800_support80": 0.0490}
#: S1's bar and the midpoint S2 turns on
S1_BAR = 1.5

CLAIMS = (
    ("S1", "the share, with a second circuit size holding the size fixed",
     "At cs 400, the one-side level's mean at support 80 is below its mean at support 40 by at least 1.5x",
     "falsifier: at or above the support-40 level, which would say the share does not lower the one-side level at "
     "cs 400 at all and that the cs-800 support effect was a cs-800 peculiarity; null: a drop smaller than 1.5x"),
    ("S2", "which candidate wins",
     "The one-side level at cs 400/support 80 lies below the midpoint of the levels at the two shares it sits "
     "between (cs 400's 4.0% and cs 800's 6.1%)",
     "falsifier: at or above the cs-400/support-40 level, which would say the level is set by the circuit; null: "
     "between the midpoint and that level"),
)


def excess_of(block: dict) -> float | None:
    """One topology's analytic diagonalisation excess, or ``None`` when it was not computed.

    NOTE the two levels of naming: a **topology** is `real`/`swap2`/`alloy1`/`erdos_renyi`/…, and an **arm** inside
    it is `diagonal(EWC)`/`bio:cell_class`/`rand:cell_class`. The one-side nulls ARE topologies, so a cell's level is
    the excess of the topology named `alloy1` or `inalloy1` — not a key inside a block. The first version of this
    reader looked for `block["alloy1"]`, which no artifact has, and reported both references unreadable.
    """
    v = ((block.get("diagonal(EWC)") or {}).get("analytic") or {}).get("excess_mean")
    return float(v) if isinstance(v, (int, float)) else None


def level_of(path: Path) -> float | None:
    """The one-side level of one artifact: the mean excess of the topologies it names `alloy1` and `inalloy1`."""
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, FileNotFoundError):
        return None
    vals = [excess_of(b) for name, b in (d.get("topologies") or {}).items()
            if name in ONE_SIDE and isinstance(b, dict)]
    vals = [v for v in vals if v is not None]
    return float(sum(vals) / len(vals)) if vals else None


def mean_level(directory: Path, names: tuple[str, ...]) -> tuple[float | None, int]:
    """The mean one-side level over a named set of artifacts, and how many of them contributed."""
    vals = [v for v in (level_of(directory / n) for n in names) if v is not None]
    return (float(sum(vals) / len(vals)) if vals else None, len(vals))


def drawings(directory: Path = RUNS) -> list[dict]:
    """Every cs-400/support-80 drawing, with its levels and its one-side mean."""
    out = []
    for path in sorted(directory.glob(f"{TEST_PREFIX}*.json")):
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        cells = {t: excess_of(b) for t, b in (d.get("topologies") or {}).items() if isinstance(b, dict)}
        ones = [cells.get(t) for t in ONE_SIDE]
        if any(not isinstance(v, (int, float)) for v in ones) or not isinstance(cells.get("erdos_renyi"),
                                                                               (int, float)):
            continue
        out.append({"artifact": path.name, "rewire_seed": (d.get("config") or {}).get("rewire_seed"),
                    "levels": {k: v for k, v in cells.items() if isinstance(v, (int, float))},
                    "one_side_mean": float(sum(ones)) / 2,
                    "top_step": float(cells["erdos_renyi"]) / max(ones)})
    return out


def judge(rows: list[dict], ref_400_40: float | None, ref_800_80: float | None) -> list[dict]:
    """S1-S2 as verdicts, refused rather than guessed when the cells or the references are absent."""
    if not rows:
        return [{"id": c[0], "verdict": f"REFUSED -- no {TEST_PREFIX}*.json artifact carries the two one-side nulls"}
                for c in CLAIMS]
    if len(rows) < EXPECTED_DRAWINGS:
        return [{"id": c[0], "verdict": f"REFUSED -- the design registers {EXPECTED_DRAWINGS} drawings and "
                                        f"{len(rows)} are on disk"} for c in CLAIMS]
    if ref_400_40 is None or ref_800_80 is None:
        missing = "cs 400/support 40" if ref_400_40 is None else "cs 800/support 80"
        return [{"id": c[0], "verdict": f"REFUSED -- the reference for {missing} could not be read from its own "
                                        f"artifacts, and a claim against a remembered number is not a claim"}
                for c in CLAIMS]
    mean = sum(r["one_side_mean"] for r in rows) / len(rows)
    drop = ref_400_40 / mean
    out = [{"id": "S1", "measured": f"one-side mean {mean:.5f} at cs 400/support 80 against {ref_400_40:.5f} at "
                                    f"cs 400/support 40 = {drop:.2f}x lower",
            "verdict": "MET" if drop >= S1_BAR else "FALSIFIER FIRED" if mean >= ref_400_40 else "null band"}]
    midpoint = (ref_400_40 + ref_800_80) / 2
    out.append({"id": "S2", "measured": f"{mean:.5f} against a midpoint of {midpoint:.5f} "
                                        f"(from {ref_400_40:.5f} and {ref_800_80:.5f})",
                "verdict": "MET" if mean < midpoint else
                           "FALSIFIER FIRED -- at or above the support-40 level" if mean >= ref_400_40 else
                           "null band -- moved toward the larger share but not past halfway"})
    return out


def report(rows: list[dict], ref_400_40: float | None, ref_800_80: float | None) -> int:
    print("== cs 400 at support 80 (a 7.9% share) ==")
    for r in sorted(rows, key=lambda r: r["rewire_seed"] if r["rewire_seed"] is not None else -1):
        lv = r["levels"]
        print(f"   seed {r['rewire_seed']}: alloy1 {lv.get('alloy1', float('nan')):.5f}  "
              f"inalloy1 {lv.get('inalloy1', float('nan')):.5f}  "
              f"erdos_renyi {lv.get('erdos_renyi', float('nan')):.5f}   "
              f"one-side mean {r['one_side_mean']:.5f}  top step {r['top_step']:.2f}x"
              + (f"   real {lv['real']:.5f}" if "real" in lv else ""))
    if rows:
        vals = [r["one_side_mean"] for r in rows]
        print(f"   the drawings' one-side means span {min(vals):.5f}-{max(vals):.5f} "
              f"({max(vals) / max(min(vals), 1e-12):.2f}x)")
    print("\n   and the two references, RECOMPUTED here from the artifacts that measured them:")
    for label, got, want in (("cs 400 / support 40", ref_400_40, REGISTERED["cs400_support40"]),
                             ("cs 800 / support 80", ref_800_80, REGISTERED["cs800_support80"])):
        if got is None:
            print(f"      {label}: NOT READABLE from its artifacts")
            continue
        note = "" if abs(got - want) <= 0.02 * want else f"   NOTE: the registration quotes {want:.4f}"
        print(f"      {label}: {got:.5f}{note}")
    print("      (shares: support 40 at cs 400 is 4.0% of 1010 neurons, support 80 at cs 400 is 7.9%, and support 80")
    print("       at cs 800 is 6.1% of 1307 -- so the test cell sits between the two references in SHARE and at the")
    print("       same circuit size as one of them)")
    print("\n== the registered claims, S1-S2 ==")
    refused = 0
    for c, row in zip(CLAIMS, judge(rows, ref_400_40, ref_800_80)):
        print(f"        {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"             the claim was: {c[2]}")
        print(f"             and its {c[3]}")
        if "REFUSED" in row["verdict"]:
            refused += 1
    return refused


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    rows = drawings(args.runs)
    r40, n40 = mean_level(args.runs, REF_400_40)
    r80, n80 = mean_level(args.runs, REF_800_80)
    if args.json_out:
        write_json(args.json_out, {"drawings": rows, "cs400_support40": r40, "cs800_support80": r80,
                                   "claims": judge(rows, r40, r80)})
        print(f"wrote {args.json_out}")
    return report(rows, r40, r80)


if __name__ == "__main__":
    sys.exit(main())
