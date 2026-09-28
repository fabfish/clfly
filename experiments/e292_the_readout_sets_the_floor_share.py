"""E292 -- the read-out sets the floor's share: the noise block against the corpus's own read-out ladder.

`e290` read the variance fraction as a ratio of two noises and found it above one in 85 of 269 arms, with an implied
effective count that is arm-level. What it did not ask is where the *share* comes from. The corpus has a manipulation
for this and it is the oldest one in the basis study: the **read-out width** -- the population the decoder reads, with
a ladder from 32 neurons to the whole circuit, built to test whether a wide read-out solves the tasks without the
recurrent weights doing the routing.

The claim the ladder implies is directional. A wide read-out gives the decoder enough to solve a task by itself, so
the trained weights move less between seeds, so the **across-replicate spread** shrinks -- and the fraction, which is
the test set's nominal noise over that spread, **rises**. A frozen body is the extreme of the same mechanism: with no
training at all, the spread is nearly pure measurement noise and the fraction should be enormous.

Three claims, all **confirmatory** and computed in the exploration that wrote the module:

- **S1 -- the share rises with the read-out width.** Among the corpus's *plastic* arms, the fraction is larger, and
  more often above one, at read-outs of 128 or more than at 32 or fewer. **Falsifier**: the wide arms' share is not
  higher.
- **S2 -- and a frozen body sits in a different regime.** The frozen arms' median fraction is more than an order of
  magnitude above the plastic arms'. **Falsifier**: within a factor of two of them.
- **S3 -- and it is a level difference and not a law.** The per-width medians are not monotone in the width: the
  corpus's widest read-outs do not carry the largest medians. **Falsifier**: the medians are non-decreasing across
  the widths that carry enough arms to have one.

**What the three add up to.** The fraction is not a property of the benchmark alone: it moves by a factor of ~2 in
its median and by a factor of ~2.3 in its rate above one when the read-out moves from the corpus's narrow setting to
its wide ones, and by an order of magnitude when the body stops training. So `e267`'s requirement -- the suite a
configuration needs -- is **read-out-specific**, which is the same conclusion `e290` reached from the arm-level
spread of the effective count, arrived at from the other end of the same statistic: one says the number is arm-level,
this one says *which* arm property moves it.

**What it cannot do.** *The read-out width is confounded with everything else that changes between artifacts* -- the
circuit size, the method set, the code epoch and the suite size all move with it, and nothing here holds them fixed;
the corpus has no artifact family that varies the read-out alone. *The wide end is thin*: 40 plastic arms beyond
read-out 32 against 219 at or below it, and only 2 to 4 arms at each of the widest settings, so S3's non-monotonicity
rests on widths with four arms each and could be small-sample. *The frozen arms are 10*, and they are not one
configuration: five read-out widths contribute one to six artifacts each. *The fraction's own formula changed across
the corpus's four days*, so a fraction from an earlier `evaluation_noise` is in the population. *And a share is not a
cause*: that the fraction rises with the read-out width is consistent with the routing story and does not establish
it, because a wide read-out also raises the accuracy, and `p(1-p)` in the numerator moves with the accuracy.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
#: The corpus's narrow and wide read-outs, as the exploration found them: 0 and 32 against 128 and above.
NARROW_MAX = 32
WIDE_MIN = 128
#: The minimum number of arms a width needs before its median is read.
MIN_ARMS = 4
#: How far the frozen median has to sit above the plastic one for S2.
ORDER = 10.0
CLAIMS = (
    ("S1", "the share rises with the read-out width",
     "Among plastic arms, the fraction is larger and more often above one at read-outs of 128 or more than at 32 or "
     "fewer",
     "falsifier: the wide arms' share is not higher"),
    ("S2", "and a frozen body sits in a different regime",
     f"The frozen arms' median fraction is more than a factor of {ORDER:g} above the plastic arms'",
     "falsifier: within a factor of two of them"),
    ("S3", "and it is a level difference and not a law",
     "The per-width medians are not monotone in the width",
     "falsifier: the medians are non-decreasing across the widths that carry enough arms"),
)


def arms(root: Path = RUNS) -> list[dict]:
    """Every (artifact, arm) the corpus gives both a read-out width and a variance fraction."""
    out = []
    for p in sorted(root.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        c = d.get("config") or {}
        ev = d.get("evaluation_noise")
        if not isinstance(ev, dict) or not isinstance(c.get("readout_size"), int):
            continue
        for arm, v in ev.items():
            if not isinstance(v, dict):
                continue
            f = v.get("variance_fraction")
            if not isinstance(f, (int, float)) or f <= 0:
                continue
            out.append({"artifact": p.name, "arm": arm, "readout": c["readout_size"],
                        "circuit_size": c.get("circuit_size"), "frozen": bool(c.get("frozen_body")),
                        "n_eval": ev.get("n_eval"), "fraction": float(f)})
    return out


def pooled(rows: list[dict]) -> dict:
    """The median and the rate above one for a set of arms."""
    fs = [r["fraction"] for r in rows]
    return {"arms": len(fs), "median": statistics.median(fs) if fs else None,
            "above_one": sum(1 for x in fs if x > 1), "rate": (sum(1 for x in fs if x > 1) / len(fs)) if fs else None}


def by_width(rows: list[dict], minimum: int = MIN_ARMS) -> list[dict]:
    by: dict[int, list[float]] = defaultdict(list)
    for r in rows:
        if not r["frozen"]:
            by[r["readout"]].append(r["fraction"])
    return [{"readout": k, "arms": len(v), "median": statistics.median(v)} for k, v in sorted(by.items())
            if len(v) >= minimum]


def monotone(readouts: list[dict]) -> bool:
    medians = [x["median"] for x in readouts]
    return all(b >= a for a, b in zip(medians, medians[1:]))


def judge(r: dict) -> list[dict]:
    if not r or not r.get("noise_arms"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no arm carries both a width and a fraction"}
                for c in CLAIMS]

    narrow, wide = r["narrow"], r["wide"]
    out = [{"id": "S1", "measured": f"plastic arms at read-out at or below {NARROW_MAX}: {narrow['arms']}, median "
                                    f"fraction {narrow['median']:.3f}, above one {100 * narrow['rate']:.0f}%; at or "
                                    f"above {WIDE_MIN}: {wide['arms']}, median {wide['median']:.3f}, above one "
                                    f"{100 * wide['rate']:.0f}%",
            "verdict": "MET -- the share rises with the read-out width" if wide["median"] > narrow["median"]
            and wide["rate"] > narrow["rate"] else "FALSIFIER FIRED -- the wide arms' share is not higher"}]

    frozen = r["frozen"]
    ratio = frozen["median"] / wide["median"] if wide["median"] else float("inf")
    out.append({"id": "S2", "measured": f"frozen arms: {frozen['arms']}, median fraction {frozen['median']:.2f}, "
                                        f"above one in {frozen['above_one']} of them, against the plastic arms' "
                                        f"{wide['median']:.3f} at the same end of the ladder (x{ratio:.1f})",
                "verdict": "MET -- a frozen body is a different regime" if ratio > ORDER else
                           f"FALSIFIER FIRED -- only x{ratio:.2f}"})

    widths = r["widths"]
    meds = ", ".join(f"r{x['readout']} {x['median']:.3f}" for x in widths)
    out.append({"id": "S3", "measured": f"the per-width medians, narrowest first: {meds}; monotone: "
                                        f"{monotone(widths)}",
                "verdict": "MET -- a level difference and not a law" if widths and not monotone(widths) else
                           "FALSIFIER FIRED -- the medians rise with the width throughout"})
    return out


def report(r: dict) -> int:
    rows = r["noise_arms"]
    print("== the corpus's read-out ladder against the noise block ==")
    print(f"   arms carrying both a read-out width and a variance fraction: {len(rows)} over "
          f"{len({x['artifact'] for x in rows})} artifacts")
    print(f"   {'readout':>8} {'arms':>5} {'median fraction':>16}  {'above one':>10}")
    by: dict = {}
    for x in rows:
        if not x["frozen"]:
            by.setdefault(x["readout"], []).append(x["fraction"])
    for k in sorted(by):
        fs = by[k]
        print(f"   {k:>8} {len(fs):5} {statistics.median(fs):16.3f}  "
              f"{sum(1 for f in fs if f > 1):4} of {len(fs)}")
    print(f"   {'frozen':>8} {r['frozen']['arms']:5} {r['frozen']['median']:16.3f}  "
          f"{r['frozen']['above_one']:4} of {r['frozen']['arms']}   (every read-out width pooled)")

    print("\n== the two pools the claim is read on ==")
    for label, key in (("narrow", "narrow"), ("wide", "wide")):
        p = r[key]
        print(f"   {label:7} {p['arms']:5} arms  median {p['median']:.3f}  above one {p['above_one']} "
              f"({100 * p['rate']:.0f}%)")

    print("\n== the registered claims, S1-S3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the fraction is read-out-specific as well as arm-level, so e267's requirement is too -- and the")
    print("    non-monotone widest widths say the relation is a level difference rather than a law)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    rows = arms(args.runs)
    plastic = [x for x in rows if not x["frozen"]]
    frozen = [x for x in rows if x["frozen"]]
    r = {"noise_arms": rows,
         "narrow": pooled([x for x in plastic if x["readout"] <= NARROW_MAX]),
         "wide": pooled([x for x in plastic if x["readout"] >= WIDE_MIN]),
         "frozen": pooled(frozen),
         "widths": by_width(rows)}
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
