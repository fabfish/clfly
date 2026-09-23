"""E93 -- the predictor's cs = 300 denominators, which were borrowed from d = 1307, replaced by measurement.

`e64`'s per-pair analysis is the artifact behind the paper's §5 headline: **21 of 25 pairs clear 2σ once the
control-draw component is folded in, and the predictor calls 20 of them correctly**. Its `draw_source` field
says where each pair's draw sd came from, and reading it across all 25 pairs shows something the paper
describes differently:

| source | pairs | measured at |
|---|---|---|
| `e67, 8 draws` | 10 | **d = 1307** |
| `e17, 5 draws` | 5 | **d = 1307** |
| `e17b, 5 draws` | 5 | **d = 1307** |

Every one of the 25 uses a d = 1307 draw sd, **including the twenty pairs of the four cs = 300 conditions**
(`baseline`, `wider-tasks`, `faster-drift`, `rewired-swap2`). So those rows did not have *interpolated*
denominators, as §5 says; they had the **other circuit size's measured** ones — a borrowed denominator rather
than a fitted one, which is a different error with a different fix: borrowings can be replaced by measurement
where the configuration matches, interpolations cannot.

`e86` supplies the missing measurement for one condition. Its cs = 300 half ran at **support 30, q = 0.02,
`real`**, which is `baseline` exactly, for all nine partitions, five draws each:

| rung | cs = 300 measured (`e86`) | d = 1307, used by `e64` | ratio |
|---|---|---|---|
| `side` | 3.246e-4 | 2.157e-4 | 1.50× |
| `cell_class` | 1.247e-3 | 2.371e-4 | **5.26×** |
| `cell_type` | 9.128e-5 | 6.802e-5 | 1.34× |
| `ito_lee_hemilineage` | 2.050e-4 | 4.158e-5 | **4.93×** |
| `supertype` | 1.865e-4 | 8.351e-5 | 2.23× |

So this script re-derives `baseline`'s five σ(rule) from the measured cs = 300 sds, using `e64`'s own
arithmetic, and reports whether the 21-of-25 count moves. The other three cs = 300 conditions cannot be
repaired by `e86`, because it did not run their width, drift rate or topology.

    python -m experiments.e93_cs300_draw_sd_upgrade
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

#: The four conditions of `e64` that ran at cs = 300, and what `e86` would have to have matched to repair
#: each. Only `baseline` is matched; the config columns are what makes that mechanical rather than a guess.
CS300_CONDITIONS = {
    "baseline": dict(support=30, q=0.02, topology="real"),
    "wider-tasks": dict(support=60, q=0.02, topology="real"),
    "faster-drift": dict(support=30, q=0.10, topology="real"),
    "rewired-swap2": dict(support=30, q=0.02, topology="swap2"),
}

#: what `e86`'s cs = 300 half actually ran
E86_CONFIG = dict(support=30, q=0.02, topology="real")

#: `e64`'s rung names -> the artifact `e86` wrote for that partition at cs = 300
E86_ARTIFACT = {
    "side": "runs/e86_drawsd_cs300_side_min1.json",
    "cell_class": "runs/e86_drawsd_cs300_cell_class_min1.json",
    "cell_type": "runs/e86_drawsd_cs300_cell_type_min1.json",
    "ito_lee_hemilineage": "runs/e86_drawsd_cs300_ito_lee_hemilineage_min1.json",
    "supertype": "runs/e86_drawsd_cs300_supertype_min1.json",
}


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


#: The five numbers `e64`'s shared rung table held, read from the **same primary source artifacts it read
#: them from** — `e67`/`e17`/`e17b`, all measured at cs = 800 / support 80.
#:
#: They are looked up here rather than taken from `runs/e64_predictor_per_seed_analysis.json`, because that
#: artifact has since been **corrected** to carry the cs = 300 measurements per condition, so reading it for
#: the "borrowed" column returns the measured ones and every ratio becomes 1.00 — a diagnostic that reads a
#: live artifact from the producer it documents goes blind the moment the producer is fixed.  This script's
#: own pre-fix output was overwritten by the same re-run, so `runs/` was not a fallback either.  **Reading
#: the primary sources is the durable form**, and it is what the defect consisted of being wrong about.
BORROWED_SOURCES = {
    "side": ("runs/e67_drawsd_side_min1.json", "e67, 8 draws"),
    "cell_class": ("runs/e17_cell_class_drawsd.json", "e17, 5 draws"),
    "ito_lee_hemilineage": ("runs/e17b_ito_lee_hemilineage_drawsd.json", "e17b, 5 draws"),
    "supertype": ("runs/e17b_supertype_drawsd.json", "e17b, 5 draws"),
    "cell_type": ("runs/e67_drawsd_cell_type_min1.json", "e67, 8 draws"),
}


def borrowed_sd(rung: str):
    """``(value, source_label)`` the shared table would have given this rung, from its own source."""
    entry = BORROWED_SOURCES.get(rung)
    if entry is None:
        return None, None
    a = load(entry[0])
    return (float(a["control_sd_across_draws"]) if a else None), entry[1]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", default="runs/e93_cs300_draw_sd_upgrade.json")
    args = ap.parse_args()

    analysis = load("runs/e64_predictor_per_seed_analysis.json")
    if analysis is None:
        raise SystemExit("runs/e64_predictor_per_seed_analysis.json is required")

    pairs = analysis["pairs"]
    print("=" * 108)
    print("1. WHERE EVERY PAIR'S DRAW SD CAME FROM, AND FROM WHICH CIRCUIT SIZE")
    print("=" * 108)
    sources = {}
    for p in pairs:
        sources.setdefault(p["draw_source"], []).append(p["condition"])
    for src, conds in sources.items():
        print(f"   {src:<22} {len(conds):>3} pairs   conditions: {sorted(set(conds))}")
    cs300 = [p for p in pairs if p["condition"] in CS300_CONDITIONS]
    print(f"\n   pairs belonging to a cs = 300 condition: {len(cs300)}")
    print(f"   of those, how many use a draw sd measured at cs = 300: "
          f"**{sum(1 for p in cs300 if 'cs300' in str(p['draw_source']))}**")
    print(f"   so {len(cs300)} pairs of the predictor's headline count carry a d = 1307 denominator.")

    print()
    print("=" * 108)
    print("2. THE MEASURED cs = 300 DRAW SDS, AGAINST THE ONES `e64` USED")
    print("=" * 108)
    print(f"   {'rung':<24}{'e86 cs=300':>14}{'|':>3}{'e64 used (d=1307)':>20}{'ratio':>9}"
          f"{'draws':>7}{'seeds':>7}")
    measured = {}
    for rung, path in E86_ARTIFACT.items():
        d = load(path)
        if d is None:
            print(f"   {rung:<24} absent ({path})")
            continue
        used, used_src = borrowed_sd(rung)
        measured[rung] = float(d["control_sd_across_draws"])
        print(f"   {rung:<24}{measured[rung]:>14.4g}{'|':>3}{used:>20.4g}"
              f"{measured[rung] / used:>9.2f}{d['config']['draws']:>7}{d['config']['seeds']:>7}"
              f"   {used_src}")

    print()
    print("=" * 108)
    print("3. `baseline` RE-DERIVED FROM THE MEASURED sds, USING `e64`'s OWN ARITHMETIC")
    print("=" * 108)
    print("   sigma(rule) = |delta| / hypot(seed_sem, draw_sd), exactly as e64 computes it.\n")
    print(f"   {'rung':<24}{'seed sem':>11}{'draw used':>12}{'sigma, used':>13}"
          f"{'draw measured':>15}{'sigma, measured':>17}{'verdict':>12}")
    rows = []
    for p in pairs:
        if p["condition"] != "baseline":
            continue
        rung = p["rung"]
        delta, seed_sem = abs(float(p["delta"])), float(p["seed_sem"])
        sigma_used = delta / float(np.hypot(seed_sem, p["draw_sd"]))
        new_sd = measured.get(rung)
        sigma_new = delta / float(np.hypot(seed_sem, new_sd)) if new_sd else None
        verdict = ("unchanged" if (sigma_used > 2) == (sigma_new > 2) else "**MOVES**") if sigma_new else "no measurement"
        rows.append(dict(rung=rung, seed_sem=seed_sem, draw_used=p["draw_sd"],
                         sigma_used=sigma_used, draw_measured=new_sd, sigma_measured=sigma_new,
                         ver_draft=verdict, delta=float(p["delta"]), call=p["call"]))
        print(f"   {rung:<24}{seed_sem:>11.3g}{p['draw_sd']:>12.4g}{sigma_used:>13.2f}"
              f"{(new_sd if new_sd else float('nan')):>15.4g}"
              f"{(sigma_new if sigma_new else float('nan')):>17.2f}{verdict:>12}")

    print()
    print("=" * 108)
    print("4. DOES THE HEADLINE COUNT MOVE?")
    print("=" * 108)
    #: **Both** columns are recomputed from primary sources here, not read from the producer's artifact.
    #: The "borrowed" column is `|delta| / hypot(seed_sem, borrowed_sd)` with `borrowed_sd` from
    #: `BORROWED_SOURCES`, and the "measured" column uses the cs = 300 runs.  Reading `p["sigma_rule"]` for
    #: the borrowed column would now return the CORRECTED value, because `e64` has been fixed to carry the
    #: cs = 300 measurements per condition -- which is the point of this script and also the reason it can no
    #: longer ask the producer what it used to say.  The convention is unchanged: a pair with no denominator
    #: is counted as resolved, which is what produced 21 rather than 20.
    def sigma_from(p, sd):
        return abs(float(p["delta"])) / float(np.hypot(p["seed_sem"], sd)) if sd else None

    n_rule_used = 0
    for p in pairs:
        used, _ = borrowed_sd(p["rung"]) if p["condition"] in CS300_CONDITIONS else (p["draw_sd"], None)
        s = sigma_from(p, used)
        if s is None or s > 2.0:
            n_rule_used += 1
    fixed = {}
    for p in pairs:
        if p["condition"] == "baseline":
            sd = load(E86_ARTIFACT[p["rung"]])
            fixed[p["rung"]] = float(sd["control_sd_across_draws"]) if sd else None
    n_rule_new = 0
    detail = []
    for p in pairs:
        if p["condition"] == "baseline":
            sigma = sigma_from(p, fixed[p["rung"]])
        elif p["condition"] in CS300_CONDITIONS:
            #: **Deliberately kept borrowed.** This column is the *baseline-only* correction, so the other
            #: three cs = 300 conditions must keep their original denominators — otherwise the column would
            #: silently become the full four-condition correction (which is `e94`'s 20 of 25), because `e64`
            #: now writes the corrected values into `sigma_rule`.
            b, _ = borrowed_sd(p["rung"])
            sigma = sigma_from(p, b)
        else:
            sigma = p["sigma_rule"]
        if sigma is None or sigma > 2.0:
            n_rule_new += 1
        elif p["condition"] == "baseline":
            detail.append((p["rung"], sigma, p["call"]))
    print(f"   pairs clearing 2 sigma with the d = 1307 denominators `e64` used: **{n_rule_used} of 25**")
    print(f"   pairs clearing 2 sigma with `baseline`'s five replaced by measurement:  **{n_rule_new} of 25**")
    print(f"   (the full four-condition correction is `e94`, which reports 20 of 25 and 19 of 20 called)")
    print(f"\n   `baseline`'s pairs that do NOT clear 2 sigma, before and after:")
    for rung, sigma, call in detail:
        meas = next(r["delta"] for r in rows if r["rung"] == rung)
        right = call == (1 if meas > 0 else -1)
        print(f"      {rung:<24} sigma {sigma:.3f}   the predictor calls it "
              f"{'RIGHT' if right else 'WRONG'} (its call {call:+d}, measured delta {meas:+.2e})")
    moved = [r for r in rows if r["ver_draft"] == "**MOVES**"]
    print(f"\n   pairs whose verdict changes among `baseline`'s five: {len(moved)}"
          + (f" -> {[r['rung'] for r in moved]}" if moved else " (neither of the two possible directions)"))
    print(f"\n   THE COUNT IS {'UNCHANGED' if n_rule_new == n_rule_used else 'CHANGED'}.")

    out = dict(config=vars(args), n_pairs=len(pairs), n_cs300_pairs=len(cs300),
               n_cs300_pairs_with_a_cs300_denominator=sum(
                   1 for p in cs300 if "cs300" in str(p["draw_source"])),
               sources={k: len(v) for k, v in sources.items()},
               measured_draw_sd=measured, baseline_rows=rows,
               n_rule_2sigma_used=n_rule_used, n_rule_2sigma_measured=n_rule_new,
               e64_recorded=analysis["conservative"],
               e86_config=E86_CONFIG, conditions=CS300_CONDITIONS)
    write_json(args.json_out, out)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    raise SystemExit(main())
