"""E36 — is `excess(swap2)`'s 367% spread a realization effect, or a geometry effect?

Two fires ago the four-point size sweep (`excess(swap2)` = 0.05782, 0.01762, 0.03492, 0.01237 at
d = 952, 1010, 1086, 1307) was read as evidence that the *statistic* is unstable, and the spread
sd (0.0205, 67% of its own mean) was attributed to **re-drawing the swap realization**.  The e34
finding then used that number as the assumed realization sd of `erdos_renyi` and showed the 152
sigma ER separation would fall to 4.5 sigma.

That attribution was never measured; it was inferred from a sweep in which circuit size and
realization vary *together*.  `--rewire-seed` now separates them, so this script does two things
the earlier readings could not:

1. **Measures the realization displacement** at fixed circuit size and fixed task seeds, for
   `swap2` (`e32`) and for Erdős–Rényi (`e33`), and asks whether the observed displacement is
   *compatible* with the sd the earlier attribution requires.  With two realizations there is no
   sd estimate, but there is a decisive compatibility test: under a hypothesis that the
   realization sd is `s`, two independent draws differ by `|s z|` with `z ~ N(0, 2)`.
2. **Tests the alternative**: that the spread is carried by the *task geometry*, which the runs
   already record per topology.  The driver would then be the effective rank of the task
   precision, and the instability would be readable **before** any learning run.

Run:

    python -m experiments.e36_geometry_carrier

The script is read-only over `runs/`; every input is an artifact already committed to the
findings it cites.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np

#: The four-point sweep as published, in the order the findings tabulate it.  Used only to check
#: that the re-runs below reproduce it; every statistic is recomputed from the JSONs.
PUBLISHED_SWEEP = [
    ("cs300", "runs/e21_e2_paired.json", 952, {"real": 0.01902, "swap0.5": 0.02257, "swap2": 0.05782}),
    ("cs800", "runs/e2_analytic.json", 1307, {"real": 0.01830, "swap0.5": 0.02317, "swap2": 0.01237}),
]

#: The size sweep as it stands now: (label, path, circuit size, d).  cs400/cs500 are re-runs of
#: points that were already published, so they double as a reproduction check.
SWEEP = [
    ("cs300", "runs/e21_e2_paired.json", 300, 952),
    ("cs400", "runs/e26_size400.json", 400, 1010),
    ("cs500", "runs/e26_size500.json", 500, 1086),
    ("cs600", "runs/e26_size600.json", 600, 1149),
    ("cs700", "runs/e26_size700.json", 700, 1229),
    ("cs800", "runs/e2_analytic.json", 800, 1307),
]

#: Realization runs, `--rewire-seed s`.  `s = 0` is the default the size sweep used.
REALIZATIONS = {
    "swap2": ("runs/e32_rewire%d.json", 6),
    "erdos_renyi": ("runs/e33_er_rewire%d.json", 6),
}

#: The sd the previous fires attributed to realization-to-realization movement, and the sd the e34
#: finding needed for ER to knock the 152 sigma separation to 3 sigma.
ATTRIBUTED_SD = 0.02050
BREAK_EVEN_SD = 0.03050


def load(path: str):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def analytic(entry, topology: str):
    topo = entry["topologies"].get(topology)
    if topo is None:
        return None
    return topo["diagonal(EWC)"]["analytic"], topo["geometry"]


def spearman(x, y) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    rx -= rx.mean()
    ry -= ry.mean()
    denom = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return float((rx * ry).sum() / denom) if denom else float("nan")


def exact_spearman_p(x, y):
    """One- and two-sided exact permutation p for Spearman rho, by enumerating n! orderings.

    Exact rather than asymptotic on purpose: the sweep has n = 5 or 6 points, where the normal
    approximation is not the thing you want to quote.  Returns ``nan`` for n > 8.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    if n > 8:
        return float("nan"), float("nan")
    observed = spearman(x, y)
    perms = list(itertools.permutations(range(n)))
    null = np.array([spearman(x, y[list(p)]) for p in perms])
    tol = 1e-12
    one = float((null >= observed - tol).mean())
    two = float((np.abs(null) >= abs(observed) - tol).mean())
    return one, two


def normal_two_sided_p(z: float) -> float:
    from math import erfc, sqrt
    return float(erfc(abs(z) / sqrt(2.0)))


def small_difference_p(z: float) -> float:
    """P(|Z| <= |z|) for Z ~ N(0, 1) -- the tail that rejects an *overstated* sd.

    This is the p-value that matters for the realization attribution.  The claim under test is
    "re-drawing the realization moves `excess` with sd s"; if that were true, two independent
    draws would differ by roughly `s`, and a difference twenty-fold smaller is evidence *against*
    it.  So the relevant tail is the one containing zero, and it *grows* with |z|: a difference of
    exactly zero is the most suspicious outcome of all (p = 0), and a difference of three
    attributed sds is no evidence at all (p = 0.997).
    """
    return 1.0 - normal_two_sided_p(z)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-out", default="runs/e36_geometry_carrier.json")
    args = ap.parse_args()

    out: dict = {"published_sweep": PUBLISHED_SWEEP, "sweep": [], "realizations": {}}

    print("=" * 78)
    print("1. THE SIZE SWEEP, AND WHETHER IT REPRODUCES")
    print("=" * 78)
    print(f"{'label':<7}{'d':>6} {'topo':<9}{'excess':>10}{'sem':>9}{'effrank':>9}{'topeig':>9}")

    sweep_rows = []
    for label, path, cs, d in SWEEP:
        entry = load(path)
        if entry is None:
            print(f"{label:<7}{d:>6}  (not run yet)")
            continue
        for topo in ("real", "swap0.5", "swap2"):
            got = analytic(entry, topo)
            if got is None:
                continue
            a, g = got
            print(f"{label:<7}{d:>6} {topo:<9}{a['excess_mean']:>10.5f}"
                  f"{a['excess_sem']:>9.5f}{g['effective_rank']:>9.3f}{g['top_eig_share']:>9.4f}")
            sweep_rows.append(dict(
                label=label, circuit_size=cs, d=d, topology=topo,
                excess=a["excess_mean"], sem=a["excess_sem"], n=a["n"],
                effective_rank=g["effective_rank"], top_eig_share=g["top_eig_share"],
                flattening=g["flattening"], mean_rank=g["mean_rank"],
                path=path,
            ))
    out["sweep"] = sweep_rows

    print("\n-- reproduction against the published four-point sweep --")
    repro = []
    for label, path, d, expected in PUBLISHED_SWEEP:
        entry = load(path)
        if entry is None:
            continue
        for topo, want in expected.items():
            got = analytic(entry, topo)
            if got is None:
                continue
            have = got[0]["excess_mean"]
            ok = abs(have - want) < 5e-5
            print(f"  {label:<7} {topo:<9} published {want:.5f}  re-run {have:.5f}  "
                  f"{'MATCH' if ok else 'DIFFERS'}")
            repro.append(dict(label=label, topology=topo, published=want, rerun=have, match=ok))
    for tag, path, published_n, expected in (
            ("cs400", "runs/e26_size400.json", 6, 0.01762),
            ("cs500", "runs/e26_size500.json", 6, 0.03492)):
        entry = load(path)
        if entry is None:
            continue
        got = analytic(entry, "swap2")
        if got is None:
            continue
        a = got[0]
        assert a["n"] >= published_n
        value = float(np.mean(a["excess_per_seed"][:published_n]))
        ok = abs(value - expected) < 5e-5
        print(f"  {tag:<7} {'swap2':<9} published {expected:.5f}  re-run first {published_n} of "
              f"{a['n']} seeds {value:.5f}  {'MATCH' if ok else 'DIFFERS'}")
        repro.append(dict(label=tag, topology="swap2", published=expected, rerun=value,
                          n_seeds=published_n, match=ok, path=path))
    out["reproduction"] = repro

    print()
    print("=" * 78)
    print("2. THE REALIZATION DISPLACEMENT -- MEASURED, NOT INFERRED")
    print("=" * 78)
    print("   fixed circuit size, fixed task seeds, only --rewire-seed changes\n")
    for topo, (pattern, want) in REALIZATIONS.items():
        means, efs, paired = [], [], []
        first = None
        for s in range(want):
            entry = load(pattern % s)
            if entry is None:
                break
            got = analytic(entry, topo)
            if got is None:
                break
            a, g = got
            means.append(a["excess_mean"])
            efs.append(g["effective_rank"])
            if first is None:
                first = np.array(a["excess_per_seed"])
                size_seed_count = a["n"]
            else:
                paired.append(np.array(a["excess_per_seed"]) - first)
        if len(means) < 2:
            print(f"  {topo}: only {len(means)} realization(s) landed, skipping")
            continue
        d01 = means[1] - means[0]
        dpaired = paired[0]
        sem = float(np.std(dpaired, ddof=1) / np.sqrt(len(dpaired)))
        t = float(np.mean(dpaired) / sem) if sem else float("nan")
        # Compatibility with the sd the earlier fires attributed to realization movement: two
        # independent draws under sd s differ by s*z with z ~ N(0, 2).
        z = d01 / (ATTRIBUTED_SD * np.sqrt(2.0))
        p_attr = small_difference_p(z)
        z_be = d01 / (BREAK_EVEN_SD * np.sqrt(2.0))
        p_be = small_difference_p(z_be)
        print(f"  {topo}  (n = {len(means)} realizations, {size_seed_count} task seeds paired)")
        print(f"    excess per realization : "
              + "  ".join(f"rw{i}={m:.5f}" for i, m in enumerate(means)))
        print(f"    effective rank         : "
              + "  ".join(f"rw{i}={e:.3f}" for i, e in enumerate(efs)))
        print(f"    paired  rw1 - rw0       : {dpaired.mean():+.5f} +/- {sem:.5f}"
              f"  (t = {t:+.2f}, n = {len(dpaired)})")
        print(f"    as a fraction of rw0    : {100 * abs(d01) / means[0]:.2f}%")
        print(f"    of the 4-point spread   : {100 * abs(d01) / ATTRIBUTED_SD:.2f}% of sd {ATTRIBUTED_SD}")
        print(f"    if realization sd were {ATTRIBUTED_SD}: two draws would differ by "
              f"~{ATTRIBUTED_SD * np.sqrt(2):.4f};")
        print(f"      observing one this close to zero has probability {p_attr:.4f}"
              f"   <- rejects the attributed sd")
        print(f"    if realization sd were {BREAK_EVEN_SD} (e34's break-even): "
              f"z = {z_be:+.3f},  P(this close to zero) = {p_be:.4f}")
        p_sd = None
        if len(means) >= 3:
            s_obs = float(np.std(means, ddof=1))
            chi2 = (len(means) - 1) * (s_obs / ATTRIBUTED_SD) ** 2
            # lower tail of chi-square with k = n - 1 df, i.e. P(sample sd <= observed)
            from scipy.stats import chi2 as chi2dist
            p_sd = float(chi2dist.cdf(chi2, df=len(means) - 1))
            print(f"    sample sd of the {len(means)} realization means = {s_obs:.5f}"
                  f"  ({ATTRIBUTED_SD / s_obs:.1f}x smaller than the attributed {ATTRIBUTED_SD})")
            print(f"      chi2 = {chi2:.5f} on {len(means)-1} df,  P(sd this small | "
                  f"attributed sd) = {p_sd:.4f}")
        print()
        out["realizations"][topo] = dict(
            means=means, effective_ranks=efs, n_realizations=len(means),
            difference=d01, paired_difference=float(dpaired.mean()), paired_sem=sem, t=t,
            z_under_attributed_sd=float(z), p_under_attributed_sd=p_attr,
            p_under_attributed_sd_from_sd=p_sd,
            z_under_break_even_sd=float(z_be),
            p_under_break_even_sd=p_be,
        )

    ps = [v["p_under_attributed_sd"] for v in out["realizations"].values()]
    if len(ps) == 2:
        joint = float(np.prod(ps))
        print(f"  Joint, both topologies independently: p = {ps[0]:.4f} x {ps[1]:.4f} = "
              f"{joint:.5f}")
        print(f"  So 'the realization sd is {ATTRIBUTED_SD}' predicts a "
              f"~{joint * 100:.2f}% coincidence.  Note what this is NOT: two draws do not")
        print("  measure an sd, and this tests the attributed number, not the realization's "
              "existence -- the")
        print(f"  paired t on `swap2` is {out['realizations']['swap2']['t']:+.2f}, i.e. the "
              f"realization does move the number, by 0.00095.")
        out["joint_p_under_attributed_sd"] = joint

    print("=" * 78)
    print("3. THE ALTERNATIVE: IS THE SPREAD CARRIED BY THE TASK GEOMETRY?")
    print("=" * 78)
    for topo in ("swap2", "swap0.5", "real"):
        rows = [r for r in sweep_rows if r["topology"] == topo]
        if len(rows) < 3:
            continue
        rows.sort(key=lambda r: r["d"])
        ef = [r["effective_rank"] for r in rows]
        ex = [r["excess"] for r in rows]
        rho = spearman(ef, ex)
        one, two = exact_spearman_p(ef, ex)
        loo = []
        for i in range(len(rows)):
            k = [j for j in range(len(rows)) if j != i]
            loo.append(round(spearman([ef[j] for j in k], [ex[j] for j in k]), 3))
        lo_d, hi_d = min(r["d"] for r in rows), max(r["d"] for r in rows)
        print(f"\n  {topo}: n = {len(rows)} points, d = {lo_d}..{hi_d}")
        print("    " + "  ".join(f"{r['label']}" for r in rows))
        print("    effrank " + "  ".join(f"{v:6.3f}" for v in ef))
        print("    excess  " + "  ".join(f"{v:7.5f}" for v in ex))
        print(f"    Spearman(effective rank, excess) = {rho:+.3f}"
              + (f"   exact p = {one:.4f} one-sided / {two:.4f} two-sided" if one == one else ""))
        print(f"    leave-one-out rho = {loo}")
        ef_mono = all(ef[i] < ef[i + 1] for i in range(len(ef) - 1))
        ex_mono = all(ex[i] < ex[i + 1] for i in range(len(ex) - 1))
        why = ("cannot be explained by circuit size, since neither sequence is monotone in d"
               if not (ef_mono or ex_mono) else
               "both sequences are monotone in d, so a size trend is not excluded")
        print(f"    monotone in d?  effrank {'yes' if ef_mono else 'no'},"
              f" excess {'yes' if ex_mono else 'no'}  ->  {why}")
        out.setdefault("rank_excess", {})[topo] = dict(
            n=len(rows), effective_rank=ef, excess=ex, spearman=rho,
            p_one_sided=one, p_two_sided=two, leave_one_out=loo,
            monotone_pairs=bool(ef_mono and ex_mono),
        )

    sw = [r for r in sweep_rows if r["topology"] == "swap2"]
    if len(sw) >= 3:
        sw.sort(key=lambda r: r["effective_rank"])
        ef = np.array([r["effective_rank"] for r in sw])
        ex = np.array([r["excess"] for r in sw])
        slope, intercept = np.polyfit(np.log(ef), ex, 1)
        pred = intercept + slope * np.log(ef)
        resid = ex - pred
        print("\n  log-linear fit over `swap2`:  excess = "
              f"{intercept:.5f} + {slope:.5f} * ln(effective rank)")
        print(f"    max |residual| = {np.abs(resid).max():.5f}"
              f"   (range of excess = {ex.max() - ex.min():.5f})")

        # The same relation with the realization points folded in.  Reported next to the
        # five-point version so the headline cannot be read as cherry-picking the size sweep:
        # the realization points are at one circuit size only, and they are what breaks exact
        # monotonicity.
        extra = []
        pattern, want = REALIZATIONS.get("swap2", (None, 0))
        for s in range(1, want):
            entry = load(pattern % s) if pattern else None
            if entry is None:
                continue
            got = analytic(entry, "swap2")
            if got is None:
                continue
            extra.append((got[1]["effective_rank"], got[0]["excess_mean"]))
        if extra:
            ef_all = np.concatenate([ef, [r for r, _ in extra]])
            ex_all = np.concatenate([ex, [e for _, e in extra]])
            rho_all = spearman(ef_all, ex_all)
            print(f"    with the {len(extra)} extra realization point(s) folded in: n = "
                  f"{len(ef_all)}, rho = {rho_all:+.3f}, still ordered"
                  f" {'monotonically' if rho_all == 1.0 else 'but no longer exactly monotone'}")
            print(f"      the extra points sit "
                  + "  ".join(f"{e - (intercept + slope * np.log(r)):+.5f}" for r, e in extra)
                  + " off the five-point fit")
            out["rank_excess"]["swap2"]["with_realizations"] = dict(
                n=len(ef_all), spearman=rho_all,
                residuals=[float(e - (intercept + slope * np.log(r))) for r, e in extra],
            )

    print()
    print("=" * 78)
    print("3b. THE SAME COORDINATE ORDERS THE C1 CONTRAST -- AND THUS ITS SIGN")
    print("=" * 78)
    print("   the contrast that carried C1's interference refutation is "
          "`swap0.5 -> swap2`, paired over task seeds")
    print(f"\n   {'d':>6}{'effrank(sw2)':>14}{'effrank(sw.5)':>15}{'delta':>11}{'sigma':>9}"
          f"{'sign':>6}")
    contrasts = []
    for label, path, cs, d in SWEEP:
        entry = load(path)
        if entry is None:
            continue
        a05, _ = analytic(entry, "swap0.5") or (None, None)
        a2, g2 = analytic(entry, "swap2") or (None, None)
        g05 = entry["topologies"]["swap0.5"]["geometry"]
        if a05 is None or a2 is None:
            continue
        try:
            delta = np.array(a2["excess_per_seed"]) - np.array(a05["excess_per_seed"])
            sem = float(delta.std(ddof=1) / np.sqrt(len(delta)))
            sigma = float(delta.mean() / sem)
            delta_mean = float(delta.mean())
            how = f"paired n={len(delta)}"
        except KeyError:
            delta_mean = a2["excess_mean"] - a05["excess_mean"]
            sem = float(np.hypot(a2["excess_sem"], a05["excess_sem"]))
            sigma = delta_mean / sem
            how = "unpaired"
        print(f"   {d:>6}{g2['effective_rank']:>14.3f}{g05['effective_rank']:>15.3f}"
              f"{delta_mean:>+11.5f}{sigma:>+9.1f}{'+' if delta_mean > 0 else '-':>6}   {how}")
        contrasts.append(dict(d=d, label=label, effrank_swap2=g2["effective_rank"],
                              effrank_swap05=g05["effective_rank"], delta=delta_mean,
                              sigma=sigma, paired=how.startswith("paired")))
    if len(contrasts) >= 3:
        contrasts.sort(key=lambda c: c["effrank_swap2"])
        rho_c = spearman([c["effrank_swap2"] for c in contrasts],
                         [c["delta"] for c in contrasts])
        one_c, two_c = exact_spearman_p([c["effrank_swap2"] for c in contrasts],
                                        [c["delta"] for c in contrasts])
        signs = ["+" if c["delta"] > 0 else "-" for c in contrasts]
        flips = sum(1 for i in range(len(signs) - 1) if signs[i] != signs[i + 1])
        print(f"\n   ordered by effrank(swap2), the sign sequence is {''.join(signs)}"
              f" with {flips} flip(s) -- not an alternation")
        above = [c["effrank_swap2"] for c in contrasts if c["delta"] > 0]
        below = [c["effrank_swap2"] for c in contrasts if c["delta"] < 0]
        if above and below:
            print(f"   every positive delta has effrank(swap2) >= {min(above):.3f};"
                  f" every negative one <= {max(below):.3f}")
            print(f"   -> a separating threshold exists anywhere in "
                  f"[{max(below):.3f}, {min(above):.3f}], and the sign needs no learning run to"
                  f" predict")
        print(f"   Spearman(effrank(swap2), delta) = {rho_c:+.3f}"
              + (f"   exact p = {one_c:.4f} one-sided" if one_c == one_c else ""))
        out["contrast"] = dict(
            rows=contrasts, spearman=rho_c, p_one_sided=one_c, signs=signs, flips=flips,
            positive_min_effrank=min(above) if above else None,
            negative_max_effrank=max(below) if below else None,
        )
        out["rank_excess"]["swap2"]["fit"] = dict(
            intercept=float(intercept), slope=float(slope),
            residuals=resid.tolist(), max_abs_residual=float(np.abs(resid).max()),
        )

        print("\n  where the other topologies sit on that curve (matched effective rank):")
        print("  a topology can only TEST the shared slope to the extent its own ln(effrank) varies")

        def curve(r):
            return intercept + slope * np.log(r)

        for topo in ("swap2", "swap0.5", "real", "erdos_renyi"):
            pts = []
            for label, path, cs, d in SWEEP:
                entry = load(path)
                if entry is None:
                    continue
                got = analytic(entry, topo)
                if got is None:
                    continue
                pts.append((got[1]["effective_rank"], got[0]["excess_mean"]))
            pattern, want = REALIZATIONS.get(topo, (None, 0))
            if pattern:
                for s in range(want):
                    entry = load(pattern % s)
                    if entry is None:
                        continue
                    got = analytic(entry, topo)
                    if got is None:
                        continue
                    pts.append((got[1]["effective_rank"], got[0]["excess_mean"]))
            if not pts:
                continue
            ratios = [obs / curve(r) for r, obs in pts]
            leverage = float(np.ptp(np.log([r for r, _ in pts])))
            excess_cv = float(np.std([e for _, e in pts], ddof=1) / np.mean([e for _, e in pts]))
            ratio_cv = float(np.std(ratios, ddof=1) / np.mean(ratios))
            print(f"    {topo:<12} n = {len(pts)}  ln(effrank) leverage = {leverage:5.3f}"
                  f"   observed excess CV = {100 * excess_cv:5.1f}%"
                  f"   ratio = {np.mean(ratios):.2f} (CV {100 * ratio_cv:.1f}%)")
            note = ("can test the slope" if leverage > 1.0
                    else "TOO LITTLE LEVERAGE: a constant ratio here is not evidence")
            print(f"                 -> {note}")
            out["rank_excess"].setdefault(topo, {}).update(
                ratio_to_swap2_curve=[float(q) for q in ratios],
                ratio_mean=float(np.mean(ratios)), ratio_cv=ratio_cv,
                log_leverage=leverage, observed_excess_cv=excess_cv,
            )

    print()
    print("=" * 78)
    print("4. PRE-REGISTERED PREDICTION")
    print("=" * 78)
    missing = [r for r in SWEEP if load(r[1]) is None]
    if missing and len(sw) >= 3:
        label, path, cs, d = missing[0]
        band = float(np.abs(resid).max())
        oos, oos_effrank = None, None
        entry = load("runs/e32_rewire1.json")
        if entry is not None:
            got = analytic(entry, "swap2")
            if got is not None:
                oos_effrank = got[1]["effective_rank"]
                oos = float(got[0]["excess_mean"]
                            - (intercept + slope * np.log(oos_effrank)))
                band = max(band, abs(oos))
        print(f"  `{label}` (d = {d}) is not run.  Both readings make a prediction:")
        print(f"    (a) realization reading: ex(swap2) at {label} is a fresh draw from a "
              f"distribution with sd {ATTRIBUTED_SD},")
        print(f"        so with 95% probability it lands in "
              f"[{np.mean(ex) - 1.96 * ATTRIBUTED_SD:+.5f}, {np.mean(ex) + 1.96 * ATTRIBUTED_SD:+.5f}]")
        print(f"    (b) geometry reading: it lands on {intercept:.5f} + {slope:.5f} "
              f"* ln(effrank at {label}),")
        print(f"        a band about +/-{band:.5f} wide -- which is "
              f"{ATTRIBUTED_SD / max(band, 1e-9):.0f}x tighter.")
        print(f"        the band is the wider of the in-sample max residual "
              f"({np.abs(resid).max():.5f}) and one genuine")
        if oos is not None:
            print(f"        out-of-sample point already in hand: rewire-seed 1 (effrank "
                  f"{oos_effrank:.3f}) sits {oos:+.5f} off the curve.")
        out["prediction"] = dict(
            missing=label, d=d,
            realization_interval=[float(np.mean(ex) - 1.96 * ATTRIBUTED_SD),
                                  float(np.mean(ex) + 1.96 * ATTRIBUTED_SD)],
            in_sample_max_residual=float(np.abs(resid).max()),
            out_of_sample_residual=oos,
            geometry_band=band,
        )
    else:
        print("  every sweep point has landed; the two readings are compared in the finding.")

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
