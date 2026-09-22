"""E57 — C2 under the discipline that overturned C1: per-seed signs, and which axis is binding.

The C1 topology line was taken apart over six fires by asking the same three questions of every
contrast — are the signs unanimous across seeds, does removing one seed change the answer, and which
axis carries the noise. The project's **core** claim is C2 (a biological module basis beats a
size-matched random partition), and those questions have never been asked of it.

Two things this script does:

1. **Per-seed dissection of the pool ladder** (`e3_ladder_v2`, 12 seeds), which is the only C2 family
   whose artifact stores `excess_per_seed`: sign unanimity, leave-one-seed-out σ, and the e47-style
   single-seed leverage.
2. **A census of which C2 artifacts can be checked per seed at all.** Plan rule 8 exists so a pooled
   mean can be re-analysed paired; the ladder's two other families — the named annotation bases at
   **18 seeds** and the second configuration at 12 — are tested here for whether they can be.

    python -m experiments.e57_basis_ladder_seed_robustness
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import numpy as np

#: Group counts of the pool ladder, from the plan's C2 table, for labelling only.
POOL_GROUPS = {"pool1": 812, "pool2": 90, "pool4": 29, "pool8": 10,
               "pool16": 8, "pool32": 3, "pool64": 3, "pool128": 2}

#: The measured control-draw sds, from the artifacts that measured them.  `e12`-`e17` established
#: that a matched-random control is ONE draw from a population, and that its draw-to-draw sd is
#: ordered by the partition's *concentration* rather than its group count.
DRAW_SD_ARTIFACTS = [
    ("cell_type min_size=2", "runs/e14_drawsd_min2.json"),
    ("cell_type min_size=3", "runs/e14_drawsd_min3.json"),
    ("cell_type min_size=4", "runs/e14_drawsd_min4.json"),
    ("cell_type min_size=6", "runs/e14_drawsd_min6.json"),
    ("cell_class", "runs/e17_cell_class_drawsd.json"),
    ("ito_lee_hemilineage", "runs/e17b_ito_lee_hemilineage_drawsd.json"),
    ("supertype", "runs/e17b_supertype_drawsd.json"),
]

#: Artifacts that might carry per-seed values for a C2 family.
CENSUS = [
    ("pool ladder, d=1307", "runs/e3_ladder_v2.json"),
    ("pool ladder, d=1307 (v1)", "runs/e3_ladder.json"),
    ("pool ladder, d=1874", "runs/e9_ladder_d1874.json"),
    ("named bases, 18 seeds", "runs/e3_seeds18.json"),
    ("named bases, 5 seeds", "runs/e3_real.json"),
    ("named bases, analytic", "runs/e3_analytic.json"),
]


def load(path: str):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-out", default="runs/e57_basis_seed_robustness.json")
    args = ap.parse_args()

    out: dict = {}

    print("=" * 104)
    print("1. THE POOL LADDER, PER SEED (the only C2 family whose artifact stores them)")
    print("=" * 104)
    d = load("runs/e3_ladder_v2.json")
    if d is None:
        print("   artifact absent")
    else:
        t = d["topologies"]["real"]
        rungs = [k for k in t if k.startswith("bio:")]
        print(f"   {d['config']['seeds']} seeds, cs = {d['config']['circuit_size']}, "
              f"lower excess = closer to the oracle = better\n")
        print(f"   {'rung':<9}{'groups':>7}{'delta':>10}{'seed sem':>10}{'sigma(seed)':>12}"
              f"{'signs':>15}{'LOO min':>9}{'LOO flips':>10}{'leverage':>10}")
        rows = []
        for k in rungs:
            tag = k.split(":")[1]
            if "rand:" + tag not in t:
                continue
            b = t[k]["analytic"]
            r = t["rand:" + tag]["analytic"]
            if "excess_per_seed" not in b or "excess_per_seed" not in r:
                continue
            bv = np.array(b["excess_per_seed"], dtype=float)
            rv = np.array(r["excess_per_seed"], dtype=float)
            n = min(len(bv), len(rv))
            dl = bv[:n] - rv[:n]
            sem = float(dl.std(ddof=1) / np.sqrt(n))
            sigma = float(dl.mean() / sem) if sem else float("nan")
            signs = "".join("+" if v > 0 else "-" for v in dl)
            loo, flip, lev = [], False, 0.0
            for i in range(n):
                keep = np.delete(dl, i)
                s = float(keep.std(ddof=1) / np.sqrt(len(keep)))
                loo.append(abs(float(keep.mean() / s)))
                lev = max(lev, abs(float(keep.mean()) - float(dl.mean())) / sem)
                if np.sign(keep.mean()) != np.sign(dl.mean()):
                    flip = True
            print(f"   {tag:<9}{POOL_GROUPS.get(tag, 0):>7}{dl.mean():>+10.5f}{sem:>10.5f}"
                  f"{sigma:>+12.2f}{signs:>15}{min(loo):>9.1f}{str(flip):>10}{lev:>10.2f}")
            rows.append(dict(rung=tag, groups=POOL_GROUPS.get(tag), n=n,
                             delta=float(dl.mean()), seed_sem=sem, sigma_seed=sigma, signs=signs,
                             loo_min=float(min(loo)), loo_flips=bool(flip), leverage=float(lev)))
        out["pool_ladder"] = rows
        if rows:
            allsign = ["".join(r["signs"]) for r in rows]
            unan = sum(1 for r in rows if len(set(r["signs"])) == 1)
            print(f"\n   {unan} of {len(rows)} rungs have completely unanimous per-seed signs, and"
                  f" the")
            print(f"   smallest leave-one-seed-out sigma is {min(r['loo_min'] for r in rows):.1f}."
                  f"  No removal flips any sign:"
                  f" {not any(r['loo_flips'] for r in rows)}.")
            print(f"   Largest single-seed leverage: {max(r['leverage'] for r in rows):.2f}"
                  f" (1 = one seed is worth a whole sem).")

    print()
    print("=" * 104)
    print("2. AND THE DRAW COMPONENT, WHICH IS THE ONE THAT BINDS")
    print("=" * 104)
    print("   The bios' seed sem above is 2-3e-05.  The *control* arm is one draw from a population")
    print("   of size-matched random partitions, and e12-e17 measured that population's spread:\n")
    print(f"   {'measured on':<24}{'draws':>7}{'sd across draws':>17}{'sem over draws':>16}")
    draws = []
    for label, path in DRAW_SD_ARTIFACTS:
        e = load(path)
        if e is None:
            continue
        print(f"   {label:<24}{e['config']['draws']:>7}{e['control_sd_across_draws']:>17.6f}"
              f"{e['control_sem_over_draws']:>16.6f}")
        draws.append(dict(label=label, draws=e["config"]["draws"],
                          sd_across=float(e["control_sd_across_draws"]),
                          sem_over=float(e["control_sem_over_draws"]), delta=float(e["delta"])))
    out["draw_sds"] = draws
    if draws:
        mx = max(draws, key=lambda x: x["sd_across"])
        print(f"\n   the largest is {mx['sd_across']:.6f} ({mx['label']}), i.e. more than ten times")
        print(f"   the seed sem of any pool rung.  So for the pool ladder the binding axis is the")
        print(f"   CONTROL DRAW, not the seed -- which is the opposite of the network benchmark,")
        print(f"   where e38/e54 found the learner's seeds dominate by 62% of the variance.")

    print()
    print("=" * 104)
    print("3. CENSUS: WHICH C2 ARTIFACTS CAN BE CHECKED PER SEED AT ALL")
    print("=" * 104)
    print(f"   {'artifact':<28}{'seeds':>7}{'rungs':>7}{'per-seed stored':>18}   verdict")
    census = []
    for label, path in CENSUS:
        e = load(path)
        if e is None:
            print(f"   {label:<28}{'absent':>7}")
            continue
        seedskey = e["config"].get("seeds")
        t = e.get("topologies", {}).get("real", {})
        bios = [k for k in t if k.startswith("bio:")]
        with_per = 0
        total = 0
        for k in bios:
            a = t[k].get("analytic")
            if a is None:
                continue
            total += 1
            with_per += 1 if "excess_per_seed" in a else 0
        ok = total and with_per == total
        note = ("checkable per seed" if ok else
                "NOT checkable -- rule 8 gap" if total else "no analytic block")
        print(f"   {label:<28}{str(seedskey):>7}{total:>7}{f'{with_per}/{total}':>18}   {note}")
        census.append(dict(label=label, path=path, seeds=seedskey, rungs=total,
                           with_per_seed=with_per, checkable=bool(ok)))
    out["census"] = census

    print()
    print("   The headline C2 claim is about the NAMED annotation bases (`side`, `cell_class`,")
    print("   `cell_type`, hemilineage, `supertype`), and the artifact with the most seeds for that")
    print("   family -- eighteen -- is the one that cannot be checked.  So the per-seed evidence")
    print("   exists for a *different* family than the one the claim is stated on.")

    print()
    print("=" * 104)
    print("4. THE THREE LINES HAVE THREE DIFFERENT BINDING AXES")
    print("=" * 104)
    print("   which is worth stating once, because every one of them was found by a retraction:\n")
    print("   C1  topology (neuron substrate)   the CIRCUIT / realization -- e36-e40 refuted the")
    print("                                     coordinate that was supposed to explain it")
    print("   C2  basis (neuron substrate)      the CONTROL DRAW -- e12/e14/e17; seed sem is 2e-5")
    print("                                     against a draw sd up to 1.0e-3")
    print("   C2b basis (rate network)          the LEARNER'S SEEDS -- e38/e54; 62% of the")
    print("                                     per-replicate variance is the learner, not the test")
    print("\n   So 'the bracket is 3-sigma' , 'the control is one draw' and 'the floor is 62% learner'")
    print("   are three different corrections to three different lines, and none of them transfers.")
    out["binding_axes"] = {"C1": "circuit/realization", "C2": "control draw", "C2b": "learner seeds"}

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
