"""E92 -- the report: partial rank correlations on the concentration-matched grid, at three sizes.

Reads the artifacts `experiments/e92_grid_profiles.py` writes (one per grid cell) and scores the
pre-registered clauses in `docs/findings/2026-09-23-the-concentration-matched-grid-preregistered.md`.
The statistic that matters is the **partial** Spearman correlation of the pressure spread against the
measured draw spread, **controlling for concentration**: a raw rank correlation cannot distinguish "the
pressure spread predicts the control's draw spread" from "both grow with concentration", which is exactly
the confound `e86` could not remove.

The nine named partitions of `e80`/`e86` are scored with the same statistic, from
`runs/e86_spread_at_other_sizes.json`, so the grid's answer can be read against the defective design's.

    python -m experiments.e92_grid_report
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, spearmanr
from scipy.stats import t as tdist

from experiments.e92_grid_profiles import K_GRID, SHAPES

#: size label -> (circuit size, the nine-partition assembly from `e86`)
SIZES = [
    ("d = 952", 300, "runs/e86_spread_at_other_sizes.json"),
    ("d = 1307", 800, "runs/e86_spread_at_other_sizes.json"),
    ("d = 1874", 1500, "runs/e86_spread_at_other_sizes.json"),
]

#: The pre-registered clauses.
PREDICTED_PARTIAL_AT_1307 = 0.5
PREDICTED_PER_SEED_POSITIVE = (7, 9)


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def relative_per_seed(d: dict) -> list:
    """Per-seed relative spread, derived from the raw pressure values the artifact keeps.

    The absolute and relative forms ask different questions -- the relative one is meant to remove the
    *level* of the pressure, which differs across partitions by an order of magnitude -- so the per-seed
    discipline has to be applied to both, and deriving it here keeps the measurement script from having to
    be edited while the grid is running.
    """
    pv = np.asarray(d["pressure_values"], float)
    si = np.asarray(d["seed_index"], int)
    out = []
    for s in range(len(d["pressure_sd_per_seed"])):
        vals = pv[si == s]
        mean = float(vals.mean())
        out.append(float(vals.std(ddof=1) / mean) if mean else float("nan"))
    return out


def partial_spearman(x, y, z) -> tuple[float, float]:
    """Spearman of ``x`` with ``y``, partialling ``z`` out of both, on ranks.

    The rank transform is applied first and the linear residualisation second, so this is the
    partialling out of the *rank* of the confound — which is what a Spearman partial correlation is, and
    is the right object here because concentration's relation to the target is not known to be linear.
    Returns ``(rho, p)`` with the p-value from the Pearson test on the residuals, ``n - 3`` df.
    """
    x, y, z = (rankdata(np.asarray(v, float)) for v in (x, y, z))
    rx = x - np.polyval(np.polyfit(z, x, 1), z)
    ry = y - np.polyval(np.polyfit(z, y, 1), z)
    if rx.std() == 0 or ry.std() == 0:
        return float("nan"), float("nan")
    r = float(np.corrcoef(rx, ry)[0, 1])
    n = len(rx)
    if n < 4 or abs(r) >= 1:
        return r, float("nan")
    t = r * np.sqrt((n - 3) / (1 - r ** 2))
    return r, float(2 * tdist.sf(abs(t), n - 3))


def score(rows: list, xkey: str = "pressure_sd", per_seed_key: str = "pressure_sd_per_seed") -> dict:
    """The correlations and their per-seed and leave-one-out companions, for one set of rows.

    ``xkey`` selects which form of the spread is scored -- the absolute pressure sd or the relative one.
    Both are reported everywhere, because `e80`'s falsifier turned on the absolute form winning *only*
    while the relative form was said to be a size restatement, and `e92`'s grid is the design that can
    settle that: it has cells at concentrations that are set rather than found.
    """
    x = [r[xkey] for r in rows]
    y = [r["measured_sd"] for r in rows]
    z = [r["concentration"] for r in rows]
    raw_x, p_raw_x = spearmanr(x, y)
    raw_z, p_raw_z = spearmanr(z, y)
    par, p_par = partial_spearman(x, y, z)
    par_rev, _ = partial_spearman(y, x, z)      #: symmetric check: target | spread
    conc_given_x, p_conc_given_x = partial_spearman(z, y, x)

    #: per-seed: the same two spreads with the task geometry held fixed
    per_seed = []
    first = rows[0].get(per_seed_key)
    if first and first[0] is not None:
        for s in range(len(first)):
            xs = [r[per_seed_key][s] for r in rows]
            ys = [r["measured_sd_per_seed"][s] for r in rows]
            rr, _ = spearmanr(xs, ys)
            pp, _ = partial_spearman(xs, ys, z)
            per_seed.append(dict(seed=s, raw=float(rr), partial=float(pp)))

    #: leave one profile out, to see whether any single cell carries the statistic
    loo = []
    for i in range(len(rows)):
        keep_x = [v for j, v in enumerate(x) if j != i]
        keep_y = [v for j, v in enumerate(y) if j != i]
        keep_z = [v for j, v in enumerate(z) if j != i]
        loo.append(float(partial_spearman(keep_x, keep_y, keep_z)[0]))

    return dict(n=len(rows),
                raw_pressure=float(raw_x), p_raw_pressure=float(p_raw_x),
                raw_concentration=float(raw_z), p_raw_concentration=float(p_raw_z),
                partial=float(par), p_partial=float(p_par),
                partial_symmetric=float(par_rev),
                concentration_given_pressure=float(conc_given_x),
                p_concentration_given_pressure=float(p_conc_given_x),
                per_seed=per_seed,
                loo_min=float(np.nanmin(loo)), loo_max=float(np.nanmax(loo)),
                loo_sign_flips=int(sum(1 for v in loo if v <= 0)) if par > 0
                else int(sum(1 for v in loo if v >= 0)),
                loo=loo)


def bootstrap_partial(rows: list, n_boot: int = 4000, seed: int = 0,
                      xkey: str = "pressure_sd") -> dict:
    """Interval for the partial correlation, resampling the **profiles**.

    The profiles of one size share their task seeds, so resampling profiles does not by itself remove
    every shared source of variation; the per-seed column is the companion that holds the geometry fixed.
    Both are reported rather than one being chosen.
    """
    rng = np.random.default_rng(seed)
    n = len(rows)
    vals = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        vals[i] = partial_spearman([rows[j][xkey] for j in idx],
                                   [rows[j]["measured_sd"] for j in idx],
                                   [rows[j]["concentration"] for j in idx])[0]
    vals = vals[np.isfinite(vals)]
    return dict(mean=float(vals.mean()), lo=float(np.percentile(vals, 2.5)),
                hi=float(np.percentile(vals, 97.5)), frac_le_zero=float((vals <= 0).mean()),
                n_boot=int(vals.size))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", default="runs/e92_grid_report.json")
    ap.add_argument("--n-boot", type=int, default=4000)
    args = ap.parse_args()

    out: dict = {"sizes": {}}
    grid_by_size: dict[str, list] = {}
    nine_by_size: dict[str, list] = {}

    for label, cs, nine_path in SIZES:
        rows = []
        for shape in SHAPES:
            for k in K_GRID:
                path = f"runs/e92_grid_cs{cs}_{shape}_k{k}.json"
                d = load(path)
                if d is None:
                    continue
                rows.append(dict(label=f"k{k} {shape}", k=k, shape=shape, d=d["d"],
                                 n_groups=d["n_groups"], concentration=d["concentration"],
                                 pressure_mean=d["pressure_mean"], pressure_sd=d["pressure_sd"],
                                 relative_sd=d["relative_sd"], measured_sd=d["measured_sd"],
                                 pressure_sd_per_seed=d["pressure_sd_per_seed"],
                                 relative_sd_per_seed=relative_per_seed(d),
                                 measured_sd_per_seed=d["measured_sd_per_seed"]))
        grid_by_size[label] = rows

        nine = load(nine_path)
        nrows = []
        if nine is not None:
            for r in nine.get("sizes", {}).get(label, {}).get("rows", []):
                #: The nine carry one spread per set, not per seed -- `e80`/`e86` stored the draw sd and
                #: not its seed decomposition -- so their per-seed columns are marked absent rather than
                #: filled with a repeated value, which would have produced three zero-variance rows and a
                #: nan that reads like a result.
                nrows.append(dict(label=r["label"], concentration=r["concentration"],
                                  pressure_sd=r["pressure_sd"], relative_sd=r["relative_sd"],
                                  measured_sd=r["measured_sd"],
                                  pressure_sd_per_seed=[None] * 3,
                                  relative_sd_per_seed=[None] * 3,
                                  measured_sd_per_seed=[None] * 3))
        nine_by_size[label] = nrows

    print("=" * 112)
    print("1. THE GRID, CELL BY CELL")
    print("=" * 112)
    for label, rows in grid_by_size.items():
        if not rows:
            print(f"\n   {label:<9} no grid artifacts on disk")
            continue
        print(f"\n   {label}  (cs = {[s[1] for s in SIZES if s[0] == label][0]}, "
              f"{len(rows)} of {len(K_GRID) * len(SHAPES)} cells)")
        print(f"   {'cell':<14}{'groups':>7}{'conc':>9}{'pressure mean':>15}{'pressure sd':>13}"
              f"{'rel sd':>9}{'measured sd':>13}")
        for r in sorted(rows, key=lambda r: -r["concentration"]):
            print(f"   {r['label']:<14}{r['n_groups']:>7}{r['concentration']:>9.4f}"
                  f"{r['pressure_mean']:>15.5f}{r['pressure_sd']:>13.5f}{r['relative_sd']:>9.4f}"
                  f"{r['measured_sd']:>13.4g}")
        concs = [round(r["concentration"], 6) for r in rows]
        dupes = sorted({c for c in concs if concs.count(c) > 1})
        if dupes:
            print(f"   duplicate concentrations among cells: {dupes}")
        print(f"   concentration range {min(concs):.4f} to {max(concs):.4f}")

    print()
    print("=" * 112)
    print("2. THE PRE-REGISTERED STATISTIC, ON THE GRID AND ON THE NINE")
    print("=" * 112)
    print("   partial = Spearman(spread, measured sd | concentration), ranks throughout.")
    print("   `abs` is the absolute pressure sd, `rel` the sd divided by the mean, which is what")
    print("   `e80` offered as the form that is not a level effect.\n")
    print(f"   {'size':<10}{'set':<7}{'form':<5}{'n':>4}{'raw spread':>12}{'raw conc':>10}"
          f"{'PARTIAL':>10}{'p':>9}{'conc|spread':>13}")
    for label, _, _ in SIZES:
        for setname, rows in (("grid", grid_by_size[label]), ("nine", nine_by_size[label])):
            if len(rows) < 5:
                print(f"   {label:<10}{setname:<7}{'':<5}{len(rows):>4}   too few rows to score")
                continue
            for form, xkey, pkey in (("abs", "pressure_sd", "pressure_sd_per_seed"),
                                     ("rel", "relative_sd", "relative_sd_per_seed")):
                st = score(rows, xkey, pkey)
                print(f"   {label:<10}{setname:<7}{form:<5}{st['n']:>4}{st['raw_pressure']:>+12.3f}"
                      f"{st['raw_concentration']:>+10.3f}{st['partial']:>+10.3f}"
                      f"{st['p_partial']:>9.3f}{st['concentration_given_pressure']:>+13.3f}")
                out["sizes"].setdefault(label, {}).setdefault(setname, {})[form] = st

    print()
    print("=" * 112)
    print("3. PER-SEED AND LEAVE-ONE-OUT, ON THE GRID")
    print("=" * 112)
    for form in ("abs", "rel"):
        print(f"\n   form = {form}")
        print(f"   {'size':<10}{'n':>4}{'per-seed partial':>28}{'positive':>10}"
              f"{'LOO partial min..max':>26}{'LOO sign flips':>16}")
        for label, _, _ in SIZES:
            rows = grid_by_size[label]
            if len(rows) < 5:
                continue
            st = out["sizes"].get(label, {}).get("grid", {}).get(form)
            if st is None:
                continue
            ps = [p["partial"] for p in st["per_seed"]]
            span = f"{st['loo_min']:+.3f} .. {st['loo_max']:+.3f}"
            print(f"   {label:<10}{st['n']:>4}"
                  f"{('  '.join(f'{v:+.3f}' for v in ps)):>28}"
                  f"{sum(1 for v in ps if v > 0):>7}/{len(ps):<3}"
                  f"{span:>26}{st['loo_sign_flips']:>16}")

    print()
    print("=" * 112)
    print("4. THE VERDICT, ON THE CLAUSES WRITTEN BEFORE THE RUN")
    print("=" * 112)
    print("   The clauses are gated on the ABSOLUTE spread, for continuity with `e86`, whose headline")
    print("   figure (+0.767 against concentration's +0.617) was the absolute form; the relative form is")
    print("   reported beside it because it is the one `e80` offered as not being a level effect.\n")
    grid = {label: out["sizes"].get(label, {}).get("grid", {}) for label, _, _ in SIZES}
    have = {k: v["abs"] for k, v in grid.items() if v.get("abs")}
    rel = {k: v["rel"] for k, v in grid.items() if v.get("rel")}
    p1 = all(v["partial"] > 0 for v in have.values()) and len(have) == 3
    p2 = all(v["raw_pressure"] > v["raw_concentration"] for v in have.values())
    p3 = grid.get("d = 1307", {}).get("abs", {}).get("partial", -9) >= PREDICTED_PARTIAL_AT_1307
    n_seed = sum(1 for v in have.values() for p in v["per_seed"] if p["partial"] > 0)
    n_seed_tot = sum(len(v["per_seed"]) for v in have.values())
    f1 = sum(1 for v in have.values() if v["partial"] <= 0) >= 2
    f2 = not all(v["raw_pressure"] > v["raw_concentration"] for v in have.values())
    print(f"   P1 partial > 0 at every size: "
          + ", ".join(f"{k} {v['partial']:+.3f}" for k, v in have.items())
          + f"   -> {'PASS' if p1 else 'FAIL'}   ({len(have)} of 3 sizes scored)")
    if rel:
        print(f"      the relative form, for the record: "
              + ", ".join(f"{k} {v['partial']:+.3f}" for k, v in rel.items()))
    print(f"   P2 raw spread beats raw concentration at every size: "
          f"-> {'PASS' if p2 else 'FAIL'}")
    print(f"   P3 partial >= {PREDICTED_PARTIAL_AT_1307:+.1f} at d = 1307: "
          f"-> {'PASS' if p3 else 'FAIL'}")
    print(f"   P4 per-seed partials positive: {n_seed}/{n_seed_tot} "
          f"(predicted >= {PREDICTED_PER_SEED_POSITIVE[0]}/{PREDICTED_PER_SEED_POSITIVE[1]}) "
          f"-> {'PASS' if n_seed >= PREDICTED_PER_SEED_POSITIVE[0] else 'FAIL'}")
    print(f"\n   F1 FIRES (partial <= 0 at two or more sizes): {'YES' if f1 else 'no'}")
    print(f"   F2 FIRES (the raw ordering reverses at some size): {'YES' if f2 else 'no'}")
    print(f"\n   P1 is the clause that matters: it is the only form of the claim that a concentration")
    print(f"   restatement cannot fake, and `e86` could not compute it because its partitions were not")
    print(f"   the same objects across sizes.")
    out["verdict"] = dict(p1=bool(p1), p2=bool(p2), p3=bool(p3), p4=bool(n_seed >= PREDICTED_PER_SEED_POSITIVE[0]),
                          per_seed_positive=[n_seed, n_seed_tot], f1_fires=bool(f1), f2_fires=bool(f2),
                          n_sizes_scored=len(have))

    print()
    print("=" * 112)
    print("5. THE SAME PROFILES AT EVERY SIZE, SO THE SIZES ARE COMPARABLE")
    print("=" * 112)
    for form in ("abs", "rel"):
        print(f"\n   form = {form}")
        for label in [s[0] for s in SIZES]:
            rows = grid_by_size[label]
            if not rows or form not in out["sizes"].get(label, {}).get("grid", {}):
                continue
            xkey = "pressure_sd" if form == "abs" else "relative_sd"
            boot = bootstrap_partial(rows, n_boot=args.n_boot, xkey=xkey)
            st = out["sizes"][label]["grid"][form]
            print(f"   {label:<10} partial {st['partial']:+.3f}   "
                  f"bootstrap over profiles (n = {len(rows)}): {boot['mean']:+.3f} "
                  f"[{boot['lo']:+.3f}, {boot['hi']:+.3f}], {boot['frac_le_zero'] * 100:.2f}% at or below zero")
            st["bootstrap"] = boot

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
