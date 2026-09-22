"""E41 — does `e5`'s anisotropy association survive its own artifact, its other seeds, and the metric rule?

`e5` is the experiment that "corrects `e2`'s confounded trend", and the plan uses it as the project's
*replacement* mechanism: varying the task's spectral concentration directly, more anisotropy gives a
larger gap, Spearman **-0.75**, with a U-shaped dip at ``kappa ~ 0.5`` before a steep rise to +1.20.

Three things are checked against the artifact the finding cites, `runs/e5_anisotropy.json`:

1. **Reproduction.** The finding's table is compared cell by cell. Every geometry column matches to
   the published precision; the `gap:EWC` column does not, and the finding's own header says
   "1 seed" while the artifact contains three.
2. **The headline's provenance.** Substituting the *published* value of the one discrepant cell into
   the stored row is tested for whether it reproduces the published Spearman exactly, and for what it
   does to the U-shape's location.
3. **Robustness.** The association is recomputed pooled, on kappa means, and **per seed** — each seed
   is a complete repeat of the same kappa sweep, so it is the honest unit — and under both the
   relative gap (what `e5` reports) and the **absolute excess** that the plan's measurement rule 3
   requires (`absolute = gap x oracle_final`, since ``gap_vs_oracle`` is the relative excess of final
   average error).

    python -m experiments.e41_anisotropy_seed_fragility
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

#: The published table, exactly as it appears in `2026-09-22-e5-anisotropy-axis.md` section 2.
#: (kappa: flattening, effective rank, top-eig share, overlap, gap:EWC, bio-rand)
PUBLISHED = {
    0.0: (0.759, 55.1, 0.105, 0.0061, 0.139, -0.030),
    0.25: (0.710, 51.5, 0.111, 0.0061, 0.105, -0.023),
    0.5: (0.586, 42.6, 0.127, 0.0061, 0.075, 0.030),
    1.0: (0.322, 23.3, 0.181, 0.0061, 0.132, -0.039),
    1.75: (0.145, 10.5, 0.295, 0.0061, 0.240, -0.072),
    2.5: (0.088, 6.4, 0.393, 0.0061, 0.365, -0.105),
    4.0: (0.049, 3.5, 0.528, 0.0061, 1.203, -0.056),
}

#: The published Spearman.
PUBLISHED_RHO = -0.75

#: Per-column tolerance for calling a published cell reproduced: half a unit in the last published
#: decimal place.  `effective_rank` is quoted to 1 dp and the rest to 3-4 dp, so a single tolerance
#: would either flag every rounded value or miss a real difference.
TOL = {
    "flattening": 0.0005,
    "effective rank": 0.05,
    "top_eig_share": 0.0005,
    "overlap": 0.00005,
    "gap:EWC": 0.0005,
    "bio-rand": 0.0005,
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", default="runs/e5_anisotropy.json")
    ap.add_argument("--json-out", default="runs/e41_anisotropy_seed_fragility.json")
    args = ap.parse_args()

    with open(args.json, encoding="utf-8") as fh:
        d = json.load(fh)
    pts = d["points"]
    seeds = sorted({p["seed"] for p in pts})
    ks = sorted({p["kappa"] for p in pts})
    out: dict = {"n_points": len(pts), "seeds": seeds, "kappas": ks,
                 "config_seeds": d["config"].get("seeds")}

    print("=" * 100)
    print("1. DOES THE ARTIFACT REPRODUCE THE PUBLISHED TABLE?")
    print("=" * 100)
    print(f"   artifact: {len(pts)} points, seeds {seeds}, config seeds = "
          f"{d['config'].get('seeds')}")
    print("   the finding's header says '1 seed' and cites this file\n")
    print(f"   {'kappa':>6}{'column':>16}{'published':>11}{'stored s0':>11}{'diff':>10}")
    mismatches = []
    s0 = {p["kappa"]: p for p in pts if p["seed"] == 0}
    for k in ks:
        p = s0[k]
        f, e, t, o, g, br = PUBLISHED[k]
        cells = (
            ("flattening", f, p["flattening"]),
            ("effective rank", e, p["effective_rank"]),
            ("top_eig_share", t, p["top_eig_share"]),
            ("overlap", o, p["overlap"]),
            ("gap:EWC", g, p["gap_ewc"]),
            ("bio-rand", br, p["gap_bio_cc"] - p["gap_rand_cc"]),
        )
        for name, want, have in cells:
            diff = have - want
            bad = abs(diff) > TOL[name]
            if bad:
                mismatches.append(dict(kappa=k, column=name, published=want, stored=float(have),
                                       diff=float(diff), rel=float(diff / want) if want else None))
            print(f"   {k:>6}{name:>16}{want:>11.4f}{have:>11.4f}{diff:>+10.4f}"
                  + ("   <- MISMATCH" if bad else ""))
    print(f"\n   {len(mismatches)} of {len(ks) * 6} cells disagree beyond the published precision")
    by_col: dict[str, int] = {}
    for m in mismatches:
        by_col[m["column"]] = by_col.get(m["column"], 0) + 1
    print(f"   by column: {by_col}")
    print("   the split is exactly the plan's rule 5 -- geometry (eigenvector-derived) is")
    print("   bit-reproducible and reproduces everywhere; the realized error columns do not.")
    out["mismatches"] = mismatches
    out["mismatches_by_column"] = by_col

    print()
    print("=" * 100)
    print("2. WHERE THE HEADLINE NUMBER COMES FROM")
    print("=" * 100)
    flat = np.array([s0[k]["flattening"] for k in ks])
    gap = np.array([s0[k]["gap_ewc"] for k in ks])
    absx = np.array([s0[k]["gap_ewc"] * s0[k]["oracle_final"] for k in ks])
    rho_stored = float(spearmanr(flat, gap)[0])
    print(f"   stored seed 0, gap:EWC          = {np.round(gap, 4)}")
    print(f"   Spearman(flattening, gap)       = {rho_stored:+.4f}")
    bad = [m for m in mismatches if m["column"] == "gap:EWC"]
    if bad:
        m = bad[0]
        sub = gap.copy()
        sub[ks.index(m["kappa"])] = m["published"]
        rho_sub = float(spearmanr(flat, sub)[0])
        print(f"   substituting only the published {m['column']}(kappa={m['kappa']:g}) = "
              f"{m['published']:.3f} for the stored {m['stored']:.4f}:")
        print(f"   Spearman(flattening, gap)       = {rho_sub:+.4f}"
              f"   (published: {PUBLISHED_RHO:+.2f})")
        print(f"   -> the published number is reproduced EXACTLY by that one cell: "
              f"{'YES' if abs(rho_sub - PUBLISHED_RHO) < 1e-9 else 'NO'}")
        i_stored, i_sub = int(np.argmin(gap)), int(np.argmin(sub))
        print(f"\n   the U-shape's location:")
        print(f"     stored   : minimum at kappa = {ks[i_stored]:g} (gap {gap[i_stored]:+.4f})")
        print(f"     published: minimum at kappa = {ks[i_sub]:g} (gap {sub[i_sub]:+.4f})")
        print(f"   -> the 'dips to a minimum at kappa ~ 0.5' headline IS that one cell: "
              f"{'YES' if i_stored != i_sub else 'NO'}")
        out["single_cell"] = dict(kappa=m["kappa"], published=m["published"], stored=m["stored"],
                                  rho_stored=rho_stored, rho_substituted=rho_sub,
                                  argmin_kappa_stored=float(ks[i_stored]),
                                  argmin_kappa_published=float(ks[i_sub]))

    print()
    print("=" * 100)
    print("3. ROBUSTNESS: THREE SEEDS AND TWO METRICS")
    print("=" * 100)
    print("   `e5` reports the RELATIVE gap.  Plan rule 3 forbids that bare -- it has a standard")
    print("   deviation comparable to its own mean and moves ~0.04 under a 1e-15 relative change in")
    print("   the spectral radius -- and prescribes the ABSOLUTE excess.  Both are computed here;\n"
          "   absolute = gap x oracle_final, which is exact because gap_vs_oracle is a relative\n"
          "   excess of final average error.\n")
    print(f"   {'scope':<28}{'n':>3}{'rho(gap, flatten)':>20}{'p':>9}"
          f"{'rho(abs, flatten)':>20}{'p':>9}")
    rows = []

    def add(scope, fl, gv, av):
        r1, p1 = spearmanr(fl, gv)
        r2, p2 = spearmanr(fl, av)
        print(f"   {scope:<28}{len(fl):>3}{r1:>+20.3f}{p1:>9.3f}{r2:>+20.3f}{p2:>9.3f}")
        rows.append(dict(scope=scope, n=int(len(fl)), rho_gap=float(r1), p_gap=float(p1),
                         rho_abs=float(r2), p_abs=float(p2)))

    add("pooled, all points", np.array([p["flattening"] for p in pts]),
        np.array([p["gap_ewc"] for p in pts]),
        np.array([p["gap_ewc"] * p["oracle_final"] for p in pts]))
    add("kappa means", np.array([np.mean([p["flattening"] for p in pts if p["kappa"] == k])
                                 for k in ks]),
        np.array([np.mean([p["gap_ewc"] for p in pts if p["kappa"] == k]) for k in ks]),
        np.array([np.mean([p["gap_ewc"] * p["oracle_final"] for p in pts if p["kappa"] == k])
                  for k in ks]))
    for s in seeds:
        m = [p for p in pts if p["seed"] == s]
        add(f"seed {s} alone", np.array([p["flattening"] for p in m]),
            np.array([p["gap_ewc"] for p in m]),
            np.array([p["gap_ewc"] * p["oracle_final"] for p in m]))
    out["robustness"] = rows

    print("\n   per-seed spread of the relative gap, the quantity the plan calls chaotic:")
    print(f"   {'kappa':>6}{'gap per seed':>28}{'sd/mean':>10}"
          f"{'abs per seed':>34}{'sd/mean':>10}")
    ratio_rows = []
    for k in ks:
        g = np.array([p["gap_ewc"] for p in pts if p["kappa"] == k])
        a = np.array([p["gap_ewc"] * p["oracle_final"] for p in pts if p["kappa"] == k])
        rg = float(np.std(g, ddof=1) / np.mean(g))
        ra = float(np.std(a, ddof=1) / np.mean(a))
        print(f"   {k:>6}{np.array2string(np.round(g, 3), separator=' '):>28}{rg:>10.2f}"
              f"{np.array2string(np.round(a, 4), separator=' '):>34}{ra:>10.2f}")
        ratio_rows.append(dict(kappa=float(k), gap=g.tolist(), abs_excess=a.tolist(),
                               cv_gap=rg, cv_abs=ra))
    out["per_kappa_spread"] = ratio_rows

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
