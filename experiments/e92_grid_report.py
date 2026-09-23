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

from clfly.bench.artifacts import write_json
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
    #: A clause whose scope is "every size" cannot FAIL while a size is unscored -- it is PENDING. The first
    #: version of this block printed FAIL for P1 and P4 whenever fewer than three sizes were on disk, which
    #: reads as a refutation when the data simply is not there yet. **The second version had the opposite
    #: flaw and it is the worse one**: it gated on each size having at least five cells, so a size with 8 of
    #: its 20 on disk counted as scored and P1 printed PASS on a partial set -- which is the precise mistake
    #: (a truncated set treated as the set) this project spent the day auditing in other people's tables.
    #: The gate is now the grid's own expected size, and every clause line prints each size's cell count.
    expected = len(K_GRID) * len(SHAPES)
    all_sizes_scored = len(have) == len(SIZES)
    grid_complete = all(len(grid_by_size[s[0]]) == expected for s in SIZES)
    counts = ", ".join(f"{s[0]} {len(grid_by_size[s[0]])}/{expected}" for s in SIZES)

    def gate(value, scoped=False):
        if scoped:
            return "PASS" if value else "FAIL"
        if not grid_complete:
            return f"PENDING ({counts})"
        return "PASS" if value else "FAIL"

    print(f"   P1 partial > 0 at every size: "
          + ", ".join(f"{k} {v['partial']:+.3f}" for k, v in have.items())
          + f"   -> {gate(p1)}")
    if rel:
        print(f"      the relative form, for the record: "
              + ", ".join(f"{k} {v['partial']:+.3f}" for k, v in rel.items()))
    print(f"   P2 raw spread beats raw concentration at every size: -> {gate(p2)}")
    print(f"   P3 partial >= {PREDICTED_PARTIAL_AT_1307:+.1f} at d = 1307: -> {gate(p3, scoped=True)}")
    print(f"   P4 per-seed partials positive: {n_seed}/{n_seed_tot} "
          f"(predicted >= {PREDICTED_PER_SEED_POSITIVE[0]}/{PREDICTED_PER_SEED_POSITIVE[1]}) "
          f"-> {gate(n_seed >= PREDICTED_PER_SEED_POSITIVE[0])}")
    print(f"\n   F1 FIRES (partial <= 0 at two or more sizes): "
          f"{'YES' if f1 else 'no'}")
    print(f"   F2 FIRES (the raw ordering reverses at some size): "
          f"{'YES' if f2 else 'no'}"
          + ("" if grid_complete else "   <- but a grid is incomplete, so read this as PENDING"))
    print(f"\n   P1 is the clause that matters: it is the only form of the claim that a concentration")
    print(f"   restatement cannot fake, and `e86` could not compute it because its partitions were not")
    print(f"   the same objects across sizes.")
    out["verdict"] = dict(p1=bool(p1), p2=bool(p2), p3=bool(p3), p4=bool(n_seed >= PREDICTED_PER_SEED_POSITIVE[0]),
                          per_seed_positive=[n_seed, n_seed_tot], f1_fires=bool(f1), f2_fires=bool(f2),
                          n_sizes_scored=len(have), all_sizes_scored=bool(all_sizes_scored),
                          grid_complete=bool(grid_complete),
                          cells={s[0]: len(grid_by_size[s[0]]) for s in SIZES}, expected_cells=expected)

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

    print()
    print("=" * 112)
    print("6. THE CROSS-SIZE LEVEL CHECK (pre-registered clause P5, added after the launch)")
    print("=" * 112)
    print("   Is the absolute spread even a cross-size quantity?  For each cell measured at two sizes,")
    print("   the ratio pressure_mean(d) / pressure_mean(d0) is the level drift, and it is compared")
    print("   with the ratio of the TARGET and with the ratio of the relative form.  A level that")
    print("   drifts while the target does not is a scale artefact of the absolute form.\n")
    pairs = [("d = 952", "d = 1307"), ("d = 1307", "d = 1874"), ("d = 952", "d = 1874")]
    level = {}
    for lo, hi in pairs:
        a = {r["label"]: r for r in grid_by_size[lo]}
        b = {r["label"]: r for r in grid_by_size[hi]}
        shared = sorted(set(a) & set(b), key=lambda lab: (a[lab]["shape"], a[lab]["k"]))
        if not shared:
            print(f"   {lo} -> {hi}: no cell measured at both")
            continue
        print(f"   {lo} -> {hi}  ({len(shared)} cells)")
        print(f"   {'cell':<14}{'level ratio':>13}{'target ratio':>14}{'rel-sd ratio':>14}")
        rows_out = []
        for lab in shared:
            rl = b[lab]["pressure_mean"] / a[lab]["pressure_mean"]
            rt = b[lab]["measured_sd"] / a[lab]["measured_sd"]
            rr = b[lab]["relative_sd"] / a[lab]["relative_sd"]
            rows_out.append(dict(label=lab, level=rl, target=rt, relative=rr))
            print(f"   {lab:<14}{rl:>13.2f}{rt:>14.2f}{rr:>14.2f}")
        med_level = float(np.median([r["level"] for r in rows_out]))
        med_target = float(np.median([r["target"] for r in rows_out]))
        med_rel = float(np.median([r["relative"] for r in rows_out]))
        n_level_far = sum(1 for r in rows_out if r["level"] > 1.5 or r["level"] < 1 / 1.5)
        n_rel_closer = sum(1 for r in rows_out
                           if abs(np.log(r["relative"])) < abs(np.log(r["level"])))
        print(f"   -> median level {med_level:.2f}x, median target {med_target:.2f}x, "
              f"median relative {med_rel:.2f}x")
        print(f"      cells whose level drifts by more than 1.5x: {n_level_far} of {len(rows_out)};"
              f"  cells where the RELATIVE form is closer to 1 than the level is: {n_rel_closer} of {len(rows_out)}")
        level[f"{lo} -> {hi}"] = dict(n=len(rows_out), median_level=med_level,
                                      median_target=med_target, median_relative=med_rel,
                                      n_level_far=n_level_far, n_relative_closer=n_rel_closer,
                                      rows=rows_out)
    #: the clause is gated on 952 -> 1874, the widest size step, and needs at least five cells before it
    #: can say anything -- with one cell a median is a single number and a PASS would be meaningless
    key = "d = 952 -> d = 1874"
    if key in level:
        enough = level[key]["n"] >= 5
        p5 = bool(enough and level[key]["median_level"] > 3.0 and level[key]["median_target"] < 1.5)
        verdict = ("PASS" if p5 else "FAIL") if enough else f"PENDING (n = {level[key]['n']} of the 20 cells)"
        print(f"\n   P5 (median level > 3x while the median target fails to follow, at the widest step):"
              f" {verdict}")
        out["p5_level_check"] = dict(passed=bool(p5), decidable=bool(enough), **level[key])
    out["cross_size_level"] = level

    #: the shape analysis: does the group-size *shape* carry information concentration does not?  This is
    #: the question the two-shape design exists to ask, and the same-k pairs are its crudest form while a
    #: joint log-log fit is the form that can separate the two coordinates.
    print()
    print("=" * 112)
    print("7. DOES THE SHAPE CARRY INFORMATION BEYOND CONCENTRATION? (the two-shape design's own question)")
    print("=" * 112)
    for label in [s[0] for s in SIZES]:
        rows = grid_by_size[label]
        shapes = sorted({r["shape"] for r in rows})
        if len(shapes) < 2:
            print(f"   {label:<10} only {len(rows)} cells of one shape ({shapes}) -- the question needs both")
            continue
        print(f"\n   {label}  ({len(rows)} cells)")
        print(f"   {'k':<6}{'conc harm':>11}{'conc flat':>11}{'measured harm':>15}{'measured flat':>15}"
              f"{'ratio':>8}")
        ratios = []
        for k in sorted({r["k"] for r in rows}):
            h = next((r for r in rows if r["k"] == k and r["shape"] == "harmonic"), None)
            f = next((r for r in rows if r["k"] == k and r["shape"] == "flat"), None)
            if h and f:
                ratio = h["measured_sd"] / f["measured_sd"]
                ratios.append(ratio)
                print(f"   {k:<6}{h['concentration']:>11.4f}{f['concentration']:>11.4f}"
                      f"{h['measured_sd']:>15.4g}{f['measured_sd']:>15.4g}{ratio:>8.2f}")
        if not ratios:
            print("   no same-k pairs")
            continue
        print(f"   -> {len(ratios)} same-k pairs, ratios {min(ratios):.2f}x to {max(ratios):.2f}x, "
              f"all in the same direction: **{all(v > 1 for v in ratios)}**")
        print("      BUT the harmonic profile also has higher concentration in every pair, so the ratio is")
        print("      confounded.  The joint fit is what separates them:\n")

        import numpy as _np
        from scipy.stats import f as _fdist
        for target_key, tname in (("measured_sd", "log measured sd"),
                                  ("pressure_sd", "log pressure sd"),
                                  ("relative_sd", "log relative sd")):
            y = _np.log([r[target_key] for r in rows])
            lc = _np.log([r["concentration"] for r in rows])
            sh = _np.array([1.0 if r["shape"] == "harmonic" else 0.0 for r in rows])
            n = len(y)

            def fit(cols):
                X = _np.column_stack([_np.ones(n)] + cols)
                beta, *_ = _np.linalg.lstsq(X, y, rcond=None)
                resid = y - X @ beta
                return 1 - resid.var() / y.var(), beta, X.shape[1]

            r2c, bc, _ = fit([lc])
            r2s, bs, _ = fit([sh])
            r2b, bb, np_ = fit([lc, sh])
            F = ((r2b - r2c) / 1) / ((1 - r2b) / (n - np_))
            pv = float(_fdist.sf(F, 1, n - np_))
            print(f"      {tname:<18} conc alone R2 {r2c:.3f} ({bc[1]:+.3f})   shape alone R2 {r2s:.3f}"
                  f"   both R2 {r2b:.3f}   shape beyond conc: F {F:.1f}, p {pv:.4f}")
            out.setdefault("shape_fit", {}).setdefault(label, {})[target_key] = dict(
                r2_concentration=float(r2c), r2_shape=float(r2s), r2_both=float(r2b),
                slope_concentration=float(bb[1]), offset_harmonic=float(bb[2]),
                F_shape_beyond_concentration=float(F), p=pv, n=n)
        print(f"      -> shape adds information beyond concentration: "
              f"**{out['shape_fit'][label]['measured_sd']['p'] < 0.05}** (on the target)")

    #: The cross-size comparison of the partials is PAIRED: the same twenty profiles are measured at every
    #: size, so the unit to resample is the profile and the indices must be shared across sizes.  Comparing
    #: two independently-bootstrapped partials instead would throw away the pairing and report an interval
    #: for a comparison nobody made -- and it is the comparison this grid exists to make.  (This is rule 23
    #: one level down: there the shared unit was the draw within a size, here it is the profile across them.)
    print()
    print("=" * 112)
    print("8. THE CROSS-SIZE COMPARISON, PAIRED ON THE SAME TWENTY PROFILES")
    print("=" * 112)
    pairs = [s[0] for s in SIZES]
    for i in range(len(pairs) - 1):
        for j in range(i + 1, len(pairs)):
            a_lab, b_lab = pairs[i], pairs[j]
            a = {r["label"]: r for r in grid_by_size[a_lab]}
            b = {r["label"]: r for r in grid_by_size[b_lab]}
            shared = sorted(set(a) & set(b))
            if len(shared) < 8:
                print(f"   {a_lab} vs {b_lab}: only {len(shared)} profiles on both -- not computable")
                continue
            print(f"\n   {a_lab} vs {b_lab}  ({len(shared)} shared profiles)")
            for form, xkey in (("abs", "pressure_sd"), ("rel", "relative_sd")):
                xa = [a[l][xkey] for l in shared]; xb = [b[l][xkey] for l in shared]
                ya = [a[l]["measured_sd"] for l in shared]; yb = [b[l]["measured_sd"] for l in shared]
                z = [a[l]["concentration"] for l in shared]
                pa = partial_spearman(xa, ya, z)[0]
                pb = partial_spearman(xb, yb, z)[0]
                rng = np.random.default_rng(args.n_boot)
                n = len(shared)
                diffs = np.empty(args.n_boot)
                for t in range(args.n_boot):
                    idx = rng.integers(0, n, n)          #: ONE index set, used at both sizes
                    p1 = partial_spearman([xa[k] for k in idx], [ya[k] for k in idx],
                                          [z[k] for k in idx])[0]
                    p2 = partial_spearman([xb[k] for k in idx], [yb[k] for k in idx],
                                          [z[k] for k in idx])[0]
                    diffs[t] = p2 - p1
                diffs = diffs[np.isfinite(diffs)]
                lo, hi = np.percentile(diffs, [2.5, 97.5])
                print(f"      form {form}: partial {pa:+.3f} -> {pb:+.3f}   difference {pb - pa:+.3f}"
                      f"   paired bootstrap [{lo:+.3f}, {hi:+.3f}]"
                      f"   {(diffs <= 0).mean() * 100:.2f}% at or below zero")
                out.setdefault("cross_size_paired", {}).setdefault(f"{a_lab}|{b_lab}", {})[form] = dict(
                    n=int(n), partial_a=float(pa), partial_b=float(pb), difference=float(pb - pa),
                    lo=float(lo), hi=float(hi), frac_le_zero=float((diffs <= 0).mean()))
            print(f"      -> read the paired interval, not the two point estimates: the pairing is what makes")
            print(f"         this the comparison the grid exists to make, and the two partials share every")
            print(f"         profile, every concentration and every task seed.")

    #: through `write_json` rather than `json.dump`, so a non-finite value in any of these statistics lands
    #: as `null` rather than as a bare `NaN` that `pandas.read_json` and `JSON.parse` both refuse.  This
    #: script wrote with `json.dump` directly until `e98` counted how many still did.
    write_json(args.json_out, out)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
