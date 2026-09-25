"""E222 -- the support sweep read: does the share of the circuit a task engages move the one-side level?

The two fires that demoted the ladder's top step left a mechanism candidate, and the registration that follows it
started by correcting its direction: this line holds `--support` at 10% of the circuit **size** while the neuron count
is not proportional, so the share of the *neurons* a task engages is **3.2% at cs 300** (30/952), **4.0% at cs 400**
(40/1010) and **6.1% at cs 800** (80/1307) — smallest where the one-side level is highest. So if the share is the
variable, a smaller share goes with a higher one-side level, and that is testable at one circuit size by varying the
support (`e221`: supports 20 and 160 at cs 800, two drawings each).

    python -m experiments.e222_support_read
    python -m experiments.e222_support_read --json-out runs/e222_support_read.json

  * **U1 -- the share moves the one-side level, with the sign the correction implies**: the level's mean at support
    20 exceeds its mean at support 160 by at least **1.3x**. Falsifier: at or below **1.05x** — no difference, which
    would leave the circuit-size dependence of the one-side level with **no tested explanation**; null 1.05-1.3x.
  * **U2 -- the top step follows the same variable**: the top step is below **1.5x** at support 20 and at or above
    **1.5x** at support 160. Falsifier: the **reverse** ordering, which would refute the share reading rather than
    merely fail to support it; null both below 1.5x.

**What it cannot do**: separate the support count from the share at one circuit size (they move together there),
resolve a 1.3x effect against a 3.34x drawing spread with two drawings per support, say anything about the assembly
geometry, or speak for the network substrate.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
PREFIX = "e221_support"
#: the levels the ratios need, and the two one-side ones
LEVELS = ("alloy1", "inalloy1", "erdos_renyi")
ONE_SIDE = ("alloy1", "inalloy1")
#: how many drawings per support the design registered
EXPECTED_DRAWINGS = 2
#: the neuron counts, for the share (the corpus stores `d` in the topology block's own dims; these are the sizes this
#: line has measured and are used only to report the share)
NEURONS = {300: 952, 400: 1010, 800: 1307}
#: U1's and U2's registered boundaries
U1_BARS = (1.3, 1.05)
U2_SUPPORT_20, U2_SUPPORT_160 = 1.5, 1.5
#: how much larger support 20's top step must be before the reverse ordering counts as a refutation
U2_REVERSE_MARGIN = 1.2
#: the support-80 reference at cs 800, quoted from `e213` and `e216`
REFERENCE_80 = {"alloy1": 0.05136, "inalloy1": 0.04668, "erdos_renyi": 0.14187,
                "note": "e213 five drawings and e216 three drawings"}

CLAIMS = (
    ("U1", "the share moves the one-side level, with the sign the correction implies",
     "The one-side level's mean at support 20 exceeds its mean at support 160 by at least 1.3x",
     "falsifier: at or below 1.05x -- no difference, which would leave the circuit-size dependence of the one-side "
     "level without any tested explanation; null: 1.05-1.3x"),
    ("U2", "the top step follows the same variable",
     "The top step is below 1.5x at support 20 and at or above 1.5x at support 160",
     "falsifier: the REVERSE ordering, which would refute the share reading rather than merely fail to support it; "
     "null: both below 1.5x"),
)


def penalty(block: dict) -> float | None:
    v = ((block.get("diagonal(EWC)") or {}).get("analytic") or {}).get("excess_mean")
    return float(v) if isinstance(v, (int, float)) else None


def sweep(directory: Path = RUNS) -> dict[int, list[dict]]:
    """Every drawing, grouped by support, each with its levels, its one-side mean and its top step."""
    out: dict[int, list[dict]] = {}
    for path in sorted(directory.glob(f"{PREFIX}*.json")):
        m = re.search(r"support(\d+)", path.name)
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        vals = {t: penalty(b) for t, b in (d.get("topologies") or {}).items() if isinstance(b, dict)}
        vals = {t: v for t, v in vals.items() if v is not None and t in LEVELS}
        if not m or set(vals) != set(LEVELS):
            continue
        ones = [vals[t] for t in ONE_SIDE]
        hi = max(ones)
        out.setdefault(int(m.group(1)), []).append(
            {"artifact": path.name, "rewire_seed": (d.get("config") or {}).get("rewire_seed"),
             "levels": vals, "one_side_mean": sum(ones) / 2, "one_side_ratio": hi / min(ones),
             "top_step": vals["erdos_renyi"] / hi if hi else float("nan")})
    return dict(sorted(out.items()))


def judge(by_support: dict[int, list[dict]]) -> list[dict]:
    """U1-U2 as verdicts, refused rather than guessed when a support the claims name is short of its drawings."""
    if not by_support:
        return [{"id": c[0], "verdict": f"REFUSED -- no {PREFIX}*.json artifact carries all three levels"}
                for c in CLAIMS]
    short = {s: len(d) for s, d in by_support.items() if len(d) < EXPECTED_DRAWINGS}
    if short or not {20, 160} <= set(by_support):
        missing = sorted({20, 160} - set(by_support))
        return [{"id": c[0], "verdict": (f"REFUSED -- the design registers {EXPECTED_DRAWINGS} drawings at each of "
                                         f"supports 20 and 160; "
                                         + (f"support(s) {missing} absent" if missing
                                            else f"support {sorted(short)[0]} has {short[sorted(short)[0]]}"))}
                for c in CLAIMS]
    means = {s: sum(d["one_side_mean"] for d in rows) / len(rows) for s, rows in by_support.items()}
    ratio = means[20] / means[160]
    out = [{"id": "U1", "measured": f"one-side mean {means[20]:.5f} at support 20 against {means[160]:.5f} at "
                                    f"support 160 = {ratio:.2f}x",
            "verdict": "MET" if ratio >= U1_BARS[0] else "FALSIFIER FIRED" if ratio <= U1_BARS[1] else "null band"}]
    t20 = sum(d["top_step"] for d in by_support[20]) / len(by_support[20])
    t160 = sum(d["top_step"] for d in by_support[160]) / len(by_support[160])
    # The registration's U2 wording lets its falsifier and its null CO-OCCUR: "the reverse ordering" is a
    # falsifier while "both below 1.5x" is the null, and two ratios 1.30x and 1.20x satisfy both sentences. This
    # judge resolves it with a declared margin -- the reverse ordering counts as a refutation only when support 20
    # is at least U2_REVERSE_MARGIN times support 160 -- so noise around equality is the null rather than a
    # refutation. The ambiguity is recorded here and in the finding rather than hidden by the code.
    if t160 >= U2_SUPPORT_160 and t20 < U2_SUPPORT_20:
        v = "MET"
    elif t20 >= U2_REVERSE_MARGIN * t160:
        v = f"FALSIFIER FIRED -- support 20's top step {t20:.2f}x is {t20 / t160:.2f}x support 160's {t160:.2f}x"
    else:
        v = "null band -- the ordering is not reversed by the margin and the two are within a factor 1.5 of each other"
    out.append({"id": "U2", "measured": f"top step {t20:.2f}x at support 20, {t160:.2f}x at support 160",
                "verdict": v})
    return out


def report(by_support: dict[int, list[dict]]) -> int:
    print("== the support sweep at cs 800 ==")
    for sup, rows in by_support.items():
        share = sup / NEURONS[800]
        print(f"   support {sup} ({share:.1%} of the {NEURONS[800]} neurons):")
        for d in sorted(rows, key=lambda r: r["rewire_seed"] if r["rewire_seed"] is not None else -1):
            lv = d["levels"]
            print(f"      seed {d['rewire_seed']}: alloy1 {lv['alloy1']:.5f}  inalloy1 {lv['inalloy1']:.5f}  "
                  f"erdos_renyi {lv['erdos_renyi']:.5f}   one-side mean {d['one_side_mean']:.5f}  "
                  f"top step {d['top_step']:.2f}x")
        means = [d["one_side_mean"] for d in rows]
        tops = [d["top_step"] for d in rows]
        print(f"      one-side mean range {min(means):.5f}-{max(means):.5f} "
              f"(ratio {max(means) / max(min(means), 1e-12):.2f}x), top step {min(tops):.2f}x-{max(tops):.2f}x")
    share80 = 80 / NEURONS[800]
    print(f"\n   and the convention's own support, quoted from the artifacts that measured it: ")
    print(f"      support 80 ({share80:.1%} of the neurons): alloy1 {REFERENCE_80['alloy1']:.5f}, "
          f"inalloy1 {REFERENCE_80['inalloy1']:.5f}, erdos_renyi {REFERENCE_80['erdos_renyi']:.5f}   "
          f"one-side mean {(REFERENCE_80['alloy1'] + REFERENCE_80['inalloy1']) / 2:.5f}   "
          f"top step {REFERENCE_80['erdos_renyi'] / REFERENCE_80['alloy1']:.2f}x  "
          f"({REFERENCE_80['note']})")
    print("   and across circuit sizes the shares are 3.2% at cs 300 (30/952), 4.0% at cs 400 (40/1010) and 6.1% at")
    print("   cs 800 (80/1307) -- smallest where the one-side level is highest, which is the correction this design")
    print("   starts from")
    print("\n== the registered claims, U1-U2 ==")
    refused = 0
    for c, row in zip(CLAIMS, judge(by_support)):
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
    got = sweep(args.runs)
    if args.json_out:
        write_json(args.json_out, {"supports": {str(k): v for k, v in got.items()}, "claims": judge(got)})
        print(f"wrote {args.json_out}")
    return report(got)


if __name__ == "__main__":
    sys.exit(main())
