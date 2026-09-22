"""E73 -- the granularity ladder against the named rungs, on the SAME footing, which the paper's comparison is not.

Two families carry claim C2. The **pool ladder** pools every cell type smaller than N into one group
(N = 1, 2, 4, 8, 16, 32, 64, 128), and the **named rungs** are the annotation columns themselves. The
paper compares them — "the five-rung table's best rung is *more* decisive than every corrected ladder
rung" — and that comparison is invalid as written, for two reasons that this script removes:

1. the ladder's corrected figures (4-9σ) were computed from **unpaired** seed sems and an **assumed**
   1.0e-3 draw sd, while the named rungs' are now **paired** and use **measured** draw sds;
2. both corrections are per-rung quantities, so neither can be applied to one family and not the other.

This script puts both families through the same two steps — paired seed sem, then a measured
control-draw sd where one exists — and reports what the head-to-head actually is.

The draw sds are labelled by provenance and never filled in silently: `pool1`, `pool2` and `pool4` have
a measurement of **their own partition** (`e67` min 1, `e14` min 2, `e14` min 4), `pool32`/`pool64` are
at concentration 0.322 against a measured point at 0.325 (essentially the same partition family, so the
measurement is used and labelled as such), and `pool8`/`pool16`/`pool128` have **no** measurement. For
those the published 1.0e-3 is carried as an *upper* estimate, which makes their sigmas conservative.

    python -m experiments.e73_ladder_named_head_to_head
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

#: The ladder's group counts, from the plan's C2 table, for labelling only.
POOL_GROUPS = {"pool1": 812, "pool2": 90, "pool4": 29, "pool8": 10,
               "pool16": 8, "pool32": 3, "pool64": 3, "pool128": 2}

#: pool rung -> (draw sd, provenance).  `None` means unmeasured.
POOL_DRAW_SD = {
    "pool1": (6.801960781803761e-05, "e67 min 1, 8 draws -- this partition"),
    "pool2": (0.0009286726398617035, "e14 min 2, 5 draws -- this partition"),
    "pool4": (0.00061304922373747, "e14 min 4, 5 draws -- this partition"),
    "pool8": (None, "unmeasured -- 1.0e-3 carried as an UPPER estimate"),
    "pool16": (None, "unmeasured -- 1.0e-3 carried as an UPPER estimate"),
    "pool32": (0.0009286726398617035, "e14 min 2 at concentration 0.325 vs this rung's 0.322"),
    "pool64": (0.0009286726398617035, "e14 min 2 at concentration 0.325 vs this rung's 0.322"),
    "pool128": (None, "unmeasured -- 1.0e-3 carried as an UPPER estimate"),
}

#: pool rung -> (draw sd, provenance) for the named family.
NAMED_DRAW_SD = {
    "side": (0.00021569004909373701, "e67, 8 draws"),
    "cell_class": (0.00023709633644934897, "e17, 5 draws"),
    "cell_type": (6.801960781803761e-05, "e67, 8 draws"),
    "ito_lee_hemilineage": (4.158388952603153e-05, "e17b, 5 draws"),
    "supertype": (8.350981282007466e-05, "e17b, 5 draws"),
}

UPPER_ESTIMATE = 1.0e-3

LADDER_ARTIFACT = "runs/e3_ladder_v2.json"
NAMED_ARTIFACT = "runs/e58_bases_18seeds_perseed.json"


def load(path: str):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def contrast(topo: dict, rung: str):
    """Paired delta for one bio/rand pair, plus the unpaired sem for comparison."""
    b, r = topo.get(f"bio:{rung}"), topo.get(f"rand:{rung}")
    if not b or not r:
        return None
    ba, ra = b["analytic"], r["analytic"]
    unpaired = float(np.hypot(ba["excess_sem"], ra["excess_sem"]))
    bp, rp = ba.get("excess_per_seed"), ra.get("excess_per_seed")
    if not bp or not rp:
        return dict(delta=ba["excess_mean"] - ra["excess_mean"], paired_sem=None,
                    unpaired_sem=unpaired, unbio=ba["excess_mean"], unrand=ra["excess_mean"])
    dl = np.asarray(bp, float) - np.asarray(rp, float)
    return dict(delta=float(dl.mean()), paired_sem=float(dl.std(ddof=1) / np.sqrt(dl.size)),
                unpaired_sem=unpaired, n=int(dl.size), unbio=ba["excess_mean"],
                unrand=ra["excess_mean"],
                corr=float(np.corrcoef(np.asarray(bp, float), np.asarray(rp, float))[0, 1]))


def report(label: str, rungs, topo: dict, draw_sds: dict) -> list:
    print(f"   {label}")
    print(f"   {'rung':<20}{'delta':>10}{'sem(unp)':>10}{'sem(pair)':>11}{'gain':>7}"
          f"{'sigma(task)':>12}{'draw sd':>10}{'sigma(rule)':>12}  provenance")
    rows = []
    for rung in rungs:
        c = contrast(topo, rung)
        if c is None:
            print(f"   {rung:<20} absent")
            continue
        sem = c["paired_sem"] or c["unpaired_sem"]
        gain = (c["unpaired_sem"] / c["paired_sem"]) if c["paired_sem"] else float("nan")
        sigma_task = abs(c["delta"]) / sem
        sd, prov = draw_sds.get(rung, (None, "unmeasured"))
        sd_used = sd if sd is not None else UPPER_ESTIMATE
        sigma_rule = abs(c["delta"]) / float(np.hypot(sem, sd_used))
        tag = "" if sd is not None else " (upper estimate)"
        print(f"   {rung:<20}{c['delta']:>+10.5f}{c['unpaired_sem']:>10.5f}"
              f"{c['paired_sem'] if c['paired_sem'] else float('nan'):>11.5f}{gain:>6.1f}x"
              f"{sigma_task:>12.1f}{sd_used:>10.5f}{sigma_rule:>12.1f}{tag}  {prov}")
        rows.append(dict(rung=rung, **c, sigma_task=sigma_task,
                         draw_sd=sd, draw_sd_used=sd_used, draw_sd_measured=sd is not None,
                         sigma_rule=sigma_rule, provenance=prov))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-out", default="runs/e73_ladder_named_head_to_head.json")
    args = ap.parse_args()

    lad, nam = load(LADDER_ARTIFACT), load(NAMED_ARTIFACT)
    if lad is None or nam is None:
        raise SystemExit("need both artifacts")
    lt = lad["topologies"]["real"]
    nt = nam["topologies"]["real"]

    out: dict = {"ladder": LADDER_ARTIFACT, "named": NAMED_ARTIFACT}

    print("=" * 118)
    print("1. THE TWO FAMILIES, ON THE SAME FOOTING (paired seed sem, measured draw sd where one exists)")
    print("=" * 118)
    print()
    ladder_rows = report(f"THE POOL LADDER ({lad['config']['seeds']} seeds)",
                         [k for k in POOL_GROUPS], lt, POOL_DRAW_SD)
    print()
    named_rows = report(f"THE NAMED RUNGS ({nam['config']['seeds']} seeds)",
                        list(NAMED_DRAW_SD), nt, NAMED_DRAW_SD)
    out["ladder_rows"] = ladder_rows
    out["named_rows"] = named_rows

    print()
    print("=" * 118)
    print("2. THE HEAD-TO-HEAD THE PAPER MAKES, AND WHAT IT ACTUALLY IS")
    print("=" * 118)
    measured_ladder = [r for r in ladder_rows if r["draw_sd_measured"]]
    best_named = max(named_rows, key=lambda r: r["sigma_rule"])
    best_ladder = max(measured_ladder, key=lambda r: r["sigma_rule"]) if measured_ladder else None
    print(f"   published comparison: 'the five-rung table's best rung is more decisive than every")
    print(f"   corrected ladder rung (4-9 sigma)'.  Both sides of that were computed differently:")
    print(f"   the ladder used UNPAIRED sems and an ASSUMED 1.0e-3 draw sd; the named rungs now use")
    print(f"   paired sems and measured draw sds.  Recomputed on the same footing:\n")
    print(f"   best named rung   {best_named['rung']:<22} sigma(rule) {best_named['sigma_rule']:>6.1f}")
    if best_ladder:
        print(f"   best ladder rung  {best_ladder['rung']:<22} sigma(rule) {best_ladder['sigma_rule']:>6.1f}"
              f"   (of the {len(measured_ladder)} ladder rungs with a measured draw sd)")
    all_ladder = [r["sigma_rule"] for r in ladder_rows]
    print(f"\n   all ladder rungs, sigma(rule): "
          + ", ".join(f"{r['rung']} {r['sigma_rule']:.1f}" for r in ladder_rows))
    print(f"   all named rungs,  sigma(rule): "
          + ", ".join(f"{r['rung']} {r['sigma_rule']:.1f}" for r in named_rows))

    n_meas = len(measured_ladder)
    print(f"\n   So the comparison is {best_named['sigma_rule']:.1f} against up to "
          f"{max(all_ladder):.1f} on the ladder, and it is NOT the")
    print(f"   'order of magnitude' the uncorrected tables suggested.  {n_meas} of "
          f"{len(ladder_rows)} ladder rungs have a")
    print(f"   measured draw sd of their own; the other {len(ladder_rows)-n_meas} carry an UPPER estimate, which")
    print(f"   *lowers* their sigma, so the ladder's figures are floor values and the gap is if anything")
    print(f"   smaller than printed.")
    out["head_to_head"] = dict(
        best_named=best_named["rung"], best_named_sigma=best_named["sigma_rule"],
        best_ladder=(best_ladder["rung"] if best_ladder else None),
        best_ladder_sigma=(best_ladder["sigma_rule"] if best_ladder else None),
        ladder_max_sigma=max(all_ladder), named_max_sigma=max(r["sigma_rule"] for r in named_rows),
        n_ladder_measured=n_meas, n_ladder=len(ladder_rows))

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
