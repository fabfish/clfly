"""E259 -- what C2b's cross-rung null RULES OUT: the power statement `e76` measured the floors for but never stated.

`e76` closed C2b's last outstanding figure and found it a **null**: the paired `side - cell_class` contrast at
lambda = 0.1, sixteen replicates on both rungs, is **-0.01910 +- 0.02161 = 0.88 sigma** on accuracy and
**+0.03516 +- 0.02907 = 1.21 sigma** on forgetting, where the published three-replicate figure had been **+0.0718 at
2.13 sigma**. It also tabulated each figure's detection floor at sixteen replicates. What it did not state is the thing
a null needs in order to be worth anything:

    **was sixteen replicates enough to have seen the effect it replaced?**

That is computable from `e76`'s own artifact without a new run, because the sem the run achieved and the effect the
line published together fix the number of replicates the published effect would need:

    sigma(n) = |effect_published| / (sem_16 * sqrt(16 / n))      ->      n(2 sigma) = 64 * sem_16^2 / effect^2

    python -m experiments.e259_c2b_null_power
    python -m experiments.e259_c2b_null_power --json-out runs/e259_c2b_null_power.json

Four registered claims, all computed in the exploration that wrote this module and disclosed as **confirmatory**:

- **P1 -- the null is powered for the claim it replaced.** The published cross-rung effect (0.0718 on accuracy) would
  have been detected at sixteen replicates at **at least 2.5 sigma**. **Falsifier**: below **2 sigma**, i.e. the
  sixteen-replicate run could not have seen the effect it is used to refute; **null**: 2.0 to 2.5 sigma.
- **P2 -- the line's three-replicate claims are of very different detectability.** The replicates each would need
  differ by **more than 20x** across the three figures. **Falsifier**: within **5x**, which would make "the run was
  underpowered" a uniform statement instead of one about a particular rung.
- **P3 -- and the two statements are the same statement.** The published `side` claim was **never detectable at
  sixteen replicates** (its implied sigma is below 1) while the published `cross_rung` and `cell_class` claims are
  excluded at **3 sigma or more**. **Falsifier**: either side reverses.
- **P4 -- reported.** The full table: each figure's published effect, the measured sem at sixteen, the implied sigma,
  the replicates needed at 2 sigma, and the floor `e76` measured -- plus the same floor at n = 3, 6, 16 and 40 under
  the assumed `sem ~ 1/sqrt(n)` scaling, which is an assumption and not a measurement.

The exit code is the number of claims **REFUSED** because the artifact is missing.

**What it cannot do**: the scaling `sem ~ 1/sqrt(n)` is assumed, so the floors at n other than 16 are extrapolations
from one n; the published effects come from **three** replicates, so they are themselves draws and the "replicates
needed" figure inherits their noise -- a published effect that is really zero would need infinitely many; the two
rungs' runs are compared as `e76` left them (identical in 23 of 23 config fields with bit-identical `naive` arms), and
nothing here re-checks that; a claim is stated for **accuracy** where the published figure was, and the forgetting
metric's published counterpart does not exist in the same form; and no run is made, so no new measurement enters the
record.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e76_c2b_cross_rung_powered import PUBLISHED_3REP

ARTIFACT = Path("runs/e76_c2b_cross_rung_powered.json")
NS = (3, 6, 16, 40)
CLAIMS = (
    ("P1", "the null is powered for the claim it replaced",
     "The published cross-rung effect (0.0718 on accuracy) would have been detected at sixteen replicates at 2.5 "
     "sigma or more",
     "falsifier: below 2 sigma, i.e. the run could not have seen what it is used to refute; null: 2.0 to 2.5"),
    ("P2", "the line's three-replicate claims are of very different detectability",
     "The replicates each would need differ by more than 20x across the three figures",
     "falsifier: within 5x [confirmatory]"),
    ("P3", "and the two statements are the same statement",
     "The published side claim was never detectable at sixteen replicates, while the published cross-rung and "
     "cell_class claims are excluded at 3 sigma or more",
     "falsifier: either side reverses [confirmatory]"),
)


def table() -> list[dict]:
    """Each figure's published effect against the sigma the sixteen-replicate run would have given it."""
    d = json.loads(ARTIFACT.read_text(encoding="utf-8")) if ARTIFACT.exists() else None
    if d is None:
        return []
    sem = {"side": d["rungs"]["side/final_accuracy"]["sem"],
           "cell_class": d["rungs"]["cell_class/final_accuracy"]["sem"],
           "side - cell_class": d["cross_rung"]["final_accuracy"]["sem"]}
    out = []
    for name, (effect, published_sigma) in PUBLISHED_3REP.items():
        s16 = sem[name]
        implied = abs(effect) / s16 if s16 else float("nan")
        needed = (64 * s16 ** 2 / effect ** 2) if effect else float("inf")
        out.append({"figure": name, "published_effect": effect, "published_sigma": published_sigma, "sem_16": s16,
                    "implied_sigma_at_16": implied, "replicates_needed_2sigma": needed,
                    "floor_at_16": 2 * s16,
                    "floors": {n: 2 * s16 * math.sqrt(16 / n) for n in NS}})
    return out


def judge(rows: list[dict]) -> list[dict]:
    if not rows:
        return [{"id": cid, "verdict": f"REFUSED -- {ARTIFACT} is missing"} for cid, *_ in CLAIMS]
    by = {r["figure"]: r for r in rows}
    out: list[dict] = []

    cr = by["side - cell_class"]["implied_sigma_at_16"]
    if cr >= 2.5:
        v = "MET -- the published effect would have been seen"
    elif cr < 2.0:
        v = "FALSIFIER FIRED -- sixteen replicates could not have seen it"
    else:
        v = "null band -- between 2.0 and 2.5 sigma"
    out.append({"id": "P1", "measured": f"the published cross-rung effect 0.0718 against the measured sem "
                                        f"{by['side - cell_class']['sem_16']:.5f} gives {cr:.2f} sigma at n = 16",
                "verdict": v})

    needed = [r["replicates_needed_2sigma"] for r in rows if math.isfinite(r["replicates_needed_2sigma"])]
    ratio = (max(needed) / min(needed)) if len(needed) > 1 and min(needed) > 0 else float("nan")
    out.append({"id": "P2", "measured": "; ".join(f"{r['figure']} needs {r['replicates_needed_2sigma']:.1f}"
                                                  for r in rows) + f" (a {ratio:.0f}x spread)",
                "verdict": "MET -- more than 20x" if ratio > 20 else
                           "FALSIFIER FIRED -- within 5x, so underpower is a uniform statement"
                           if ratio <= 5 else "null band -- between 5x and 20x"})

    side, cr2, cc = (by["side"]["implied_sigma_at_16"], by["side - cell_class"]["implied_sigma_at_16"],
                     by["cell_class"]["implied_sigma_at_16"])
    ok = side < 1.0 and cr2 >= 3.0 and cc >= 3.0
    out.append({"id": "P3",
                "measured": f"implied sigma at n = 16: side {side:.2f}, cell_class {cc:.2f}, cross-rung {cr2:.2f}",
                "verdict": "MET -- one never detectable, two excluded at 3 sigma or more" if ok else
                           "FALSIFIER FIRED -- the pattern does not hold"})
    return out


def report(rows: list[dict]) -> int:
    print("== C2b's cross-rung null: what it rules out, from `e76`'s own artifact ==")
    if not rows:
        print(f"   {ARTIFACT} is missing")
        return len(CLAIMS)
    d = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    print(f"   the two runs' configurations are identical across every compared field (differing: "
          f"{d['differing_fields'] or 'none'}), and their naive arms are bit-aligned: {d['naive_aligned']}")
    print(f"\n   {'figure':18} {'published':>10} {'at sigma':>9} {'sem at 16':>10} {'sigma at 16':>12} "
          f"{'n for 2 sigma':>14} {'floor at 16':>12}")
    for r in rows:
        print(f"   {r['figure']:18} {r['published_effect']:>10.4f} {r['published_sigma']:>9.2f} "
              f"{r['sem_16']:>10.5f} {r['implied_sigma_at_16']:>12.2f} {r['replicates_needed_2sigma']:>14.1f} "
              f"{r['floor_at_16']:>12.5f}")

    print("\n   the measured contrast itself, at sixteen replicates:")
    for metric, v in sorted(d["cross_rung"].items()):
        print(f"      {metric:16} delta {v['delta']:+.5f} +- {v['sem']:.5f} = {v['sigma']:.2f} sigma "
              f"({v['n_pos']} positive / {v['n_neg']} negative, sign p = {v['sign_p']:.2f}, "
              f"leave-one-out min {v['loo_min']:.2f})")

    print("\n   and at other replicate counts, on the ASSUMED scaling sem ~ 1/sqrt(n):")
    print(f"      {'figure':18} " + " ".join(f"{'n=' + str(n):>10}" for n in NS))
    for r in rows:
        print(f"      {r['figure']:18} " + " ".join(f"{r['floors'][n]:>10.5f}" for n in NS))
    print("      (the published effects are 0.0069, 0.0648 and 0.0718 -- so at n = 16 the floors clear the second and")
    print("       third and never the first, which is `e76`'s 0.27x / 2.0x / 1.7x in another form)")

    print("\n== the registered claims, P1-P3 ==")
    j = judge(rows)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (the scaling is assumed, the published effects are themselves three-replicate draws, and no run is made")
    print("    -- this turns `e76`'s floors into the statement a null needs and measures nothing new)")
    return sum("REFUSED" in r["verdict"] for r in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    rows = table()
    if args.json_out:
        write_json(args.json_out, {"artifact": str(ARTIFACT), "figures": rows, "claims": judge(rows)})
        print(f"wrote {args.json_out}")
    return report(rows)


if __name__ == "__main__":
    sys.exit(main())
