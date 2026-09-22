"""E66 -- the NAMED annotation bases under the per-seed discipline that overturned C1.

`e57` asked the three C1-discipline questions (unanimous signs, leave-one-out stability, single-seed
leverage) of C2 and could only ask them of the **pool ladder**, because that was the only C2 family
whose artifact stored `excess_per_seed`.  The claim itself is stated on the **named annotation rungs**
-- `side`, `cell_class`, `cell_type`, hemilineage, `supertype` -- and the artifact with the most seeds
for that family, `e3_seeds18.json` at eighteen, was precisely the one that could not be checked.  That
is a rule-8 gap on the project's headline number, and `e58` closed it by re-running the same
configuration with per-seed storage.

This script is the analysis of that re-run.  For each matched `bio:`/`rand:` pair it reports:

* the paired difference per seed, its sign string, and the seed sem -- ``sigma(task)``, which is a
  statement about **these eighteen task draws**;
* ``sigma(rule)``, the same difference divided by the measured **control-draw** sd instead, which is a
  statement about the **partition population** the control is one draw from;
* leave-one-seed-out sigma and flags, and the single-seed leverage.

The second sigma is the one `e59` showed to be the real one for the C1 family, so both are printed side
by side and the smaller is not treated as the answer.

The four `extras` bases (`rank4`, `rank16`, `rank64`, `eigbasis`) are handled in a second section
against `diagonal(EWC)`: they have no random partner and, unlike a partition, no draw at all -- they
are deterministic functions of the circuit, so their only axis here is the task draw.

    python -m experiments.e66_named_bases_seed_robustness
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

#: rung -> candidate source artifacts for the measured control-draw sd, most direct first.  When `e67`
#: finished its `side` arm there was no named rung left without a measurement except `cell_type`, whose
#: direct measurement was still running; the pooled fallback is kept for that case and labelled as a
#: proxy rather than passed off as the column's own.
DRAW_SD_SOURCES = {
    "side": (("runs/e67_drawsd_side_min1.json", "side, 8 draws"),),
    "cell_class": (("runs/e17_cell_class_drawsd.json", "cell_class, 5 draws"),),
    "ito_lee_hemilineage": (("runs/e17b_ito_lee_hemilineage_drawsd.json",
                             "ito_lee_hemilineage, 5 draws"),),
    "supertype": (("runs/e17b_supertype_drawsd.json", "supertype, 5 draws"),),
    "cell_type": (("runs/e67_drawsd_cell_type_min1.json", "cell_type, 8 draws"),
                  ("runs/e14_drawsd_min4.json", "cell_type POOLED at min group size 4 -- a proxy")),
}

#: The deterministic non-partition bases, and the reference they are contrasted against.
EXTRAS = ("rank4", "rank16", "rank64", "eigbasis")
REFERENCE = "diagonal(EWC)"


def load(path: str):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def sign_test(per: np.ndarray) -> tuple[int, int, int, float]:
    """Two-sided sign test dropping ties, returning (n_positive, n_negative, n_tied, p).

    The convention is `e56`'s: a difference of exactly zero is not a sign, and counting it either way
    moves p.
    """
    pos = int((per > 0).sum())
    neg = int((per < 0).sum())
    tied = int((per == 0).sum())
    n = pos + neg
    p = float(binomtest(pos, n).pvalue) if n else float("nan")
    return pos, neg, tied, p


def per_seed_stats(dl: np.ndarray) -> dict:
    n = dl.size
    mean = float(dl.mean())
    sem = float(dl.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    loo, flip, lev = [], False, 0.0
    for i in range(n):
        keep = np.delete(dl, i)
        s = float(keep.std(ddof=1) / np.sqrt(keep.size))
        loo.append(abs(float(keep.mean() / s)) if s else float("inf"))
        if sem:
            lev = max(lev, abs(float(keep.mean()) - mean) / sem)
        if np.sign(keep.mean()) != np.sign(mean):
            flip = True
    pos, neg, tied, p = sign_test(dl)
    return dict(n=n, delta=mean, seed_sem=sem,
                sigma_task=abs(mean) / sem if sem else float("inf"),
                signs="".join("+" if v > 0 else ("0" if v == 0 else "-") for v in dl),
                n_pos=pos, n_neg=neg, n_tied=tied, sign_p=p,
                loo_min=float(min(loo)), loo_flips=bool(flip), leverage=float(lev),
                delta_min=float(dl.min()), delta_max=float(dl.max()))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--artifact", default="runs/e58_bases_18seeds_perseed.json")
    ap.add_argument("--json-out", default="runs/e66_named_bases_seed_robustness.json")
    args = ap.parse_args()

    art = load(args.artifact)
    if art is None:
        raise SystemExit(f"artifact absent: {args.artifact}")
    topo = art["topologies"]["real"]
    n_seeds = art["config"].get("seeds")

    out: dict = {"config": art["config"], "artifact": args.artifact}

    print("=" * 108)
    print(f"1. THE NAMED ANNOTATION RUNGS, PER SEED ({n_seeds} seeds, "
          f"cs = {art['config'].get('circuit_size')})")
    print("=" * 108)
    print("   lower excess = closer to the oracle.  delta = excess(bio) - excess(rand) at the SAME")
    print("   task seed, so the two arms are matched and the paired sem is the right one.\n")

    rows = []
    for key in list(topo):
        if not key.startswith("bio:"):
            continue
        rung = key.split(":", 1)[1]
        if f"rand:{rung}" not in topo:
            continue
        b = topo[key].get("analytic") or {}
        r = topo[f"rand:{rung}"].get("analytic") or {}
        bp, rp = b.get("excess_per_seed"), r.get("excess_per_seed")
        if bp is None or rp is None:
            print(f"   {rung:<22} no per-seed storage -- still a rule-8 gap")
            rows.append(dict(rung=rung, checkable=False))
            continue
        bv, rv = np.asarray(bp, float), np.asarray(rp, float)
        n = min(bv.size, rv.size)
        dl = bv[:n] - rv[:n]
        st = per_seed_stats(dl)

        draw, source = None, None
        for path, lab in DRAW_SD_SOURCES.get(rung, ()):
            draw = load(path)
            if draw is not None:
                source = lab
                break
        sd = float(draw["control_sd_across_draws"]) if draw else None
        if sd is not None:
            denom = float(np.hypot(st["seed_sem"], sd))
            sigma_rule = abs(st["delta"]) / denom
            which_binds = "draw" if sd > st["seed_sem"] else "seed"
        else:
            sigma_rule, which_binds = None, "unmeasured"

        tied = f"/{st['n_tied']}tied" if st["n_tied"] else ""
        print(f"   {rung:<22} delta {st['delta']:+.5f}  seed sem {st['seed_sem']:.5f}  "
              f"sigma(task) {st['sigma_task']:6.1f}")
        print(f"   {'':<22} signs {st['signs']}   {st['n_pos']}+/{st['n_neg']}-{tied}  "
              f"sign p = {st['sign_p']:.4f}")
        print(f"   {'':<22} LOO min sigma {st['loo_min']:.1f}   LOO flips {st['loo_flips']}   "
              f"leverage {st['leverage']:.2f}   range [{st['delta_min']:+.5f}, {st['delta_max']:+.5f}]")
        if sd is not None:
            print(f"   {'':<22} control-draw sd {sd:.6f} ({source}) -> sigma(rule) "
                  f"{sigma_rule:.1f}   binding axis: {which_binds}")
        else:
            print(f"   {'':<22} control-draw sd NOT MEASURED for this rung -> sigma(rule) is a "
                  f"LOWER BOUND, unbounded below")
        print()
        rows.append(dict(rung=rung, checkable=True, **st,
                         draw_sd=sd, sigma_rule=sigma_rule, binding_axis=which_binds))
    out["named"] = rows

    ok = [r for r in rows if r.get("checkable")]
    if ok:
        unan = [r for r in ok if len(set(r["signs"].replace("0", ""))) == 1]
        print("   SUMMARY")
        print(f"   {len(unan)} of {len(ok)} checkable rungs have completely unanimous per-seed signs.")
        print(f"   smallest LOO sigma {min(r['loo_min'] for r in ok):.1f}; no LOO flip: "
              f"{not any(r['loo_flips'] for r in ok)}; largest leverage "
              f"{max(r['leverage'] for r in ok):.2f}.")
        for r in ok:
            if r["sigma_rule"] is not None:
                print(f"   {r['rung']:<22} sigma(task) {r['sigma_task']:6.1f} -> sigma(rule) "
                      f"{r['sigma_rule']:6.1f}")
            else:
                print(f"   {r['rung']:<22} sigma(task) {r['sigma_task']:6.1f} -> UNMEASURED draw")
        out["summary"] = dict(n_checkable=len(ok), n_unanimous=len(unan),
                              loo_min=min(r["loo_min"] for r in ok),
                              no_loo_flip=not any(r["loo_flips"] for r in ok),
                              leverage_max=max(r["leverage"] for r in ok))

    print()
    print("=" * 108)
    print(f"2. THE NON-PARTITION EXTRAS AGAINST {REFERENCE}")
    print("=" * 108)
    print("   These are deterministic functions of the circuit -- no control draw exists, so the task")
    print("   draw is the ONLY axis this artifact samples.  A large sigma here is not automatically")
    print("   weaker evidence; it is evidence about a narrower population.\n")
    ref = (topo.get(REFERENCE) or {}).get("analytic") or {}
    ref_per = ref.get("excess_per_seed")
    if ref_per is None:
        print(f"   {REFERENCE} has no per-seed storage -- cannot form a paired contrast")
    else:
        rv = np.asarray(ref_per, float)
        erows = []
        for name in EXTRAS:
            a = (topo.get(name) or {}).get("analytic") or {}
            ap_ = a.get("excess_per_seed")
            if ap_ is None:
                print(f"   {name:<22} no per-seed storage")
                continue
            av = np.asarray(ap_, float)
            n = min(av.size, rv.size)
            dl = av[:n] - rv[:n]
            st = per_seed_stats(dl)
            print(f"   {name:<22} delta {st['delta']:+.5f}  seed sem {st['seed_sem']:.5f}  "
                  f"sigma(task) {st['sigma_task']:6.1f}  signs {st['signs']}  p = {st['sign_p']:.4f}")
            print(f"   {'':<22} LOO min sigma {st['loo_min']:.1f}   LOO flips {st['loo_flips']}   "
                  f"leverage {st['leverage']:.2f}")
            erows.append(dict(basis=name, reference=REFERENCE, **st))
        out["extras"] = erows

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
