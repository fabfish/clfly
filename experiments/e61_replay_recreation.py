"""E61 -- the network line's headline replay result, recreated and checked against the claim.

`e62` established that the network line's one surviving positive result -- *replay at pool 96 /
per-step 8 reduces forgetting to -0.010 +- 0.006 against naive's +0.066 +- 0.019, 4.2 sigma, at
0.968 +- 0.013 accuracy* -- has **no artifact anywhere on disk**: every one of the 77 stored runs
uses `replay_per_task 16` and `replay_batch 16`.  The nearest instance that exists gives the contrast
at -1.17 sigma.  `e62` closed by launching this sweep; this script is its analysis.

It reports, for each per-step draw:

* naive's and replay's own forgetting and accuracy, against the numbers the claim states;
* the **paired** replay-minus-naive contrast, per replicate, with its sign string, its leave-one-out
  sigma range and its single-replicate leverage -- the disciplines `e47`/`e57` apply everywhere else;
* the same contrast **unpaired**, so the pairing's contribution is visible rather than assumed.

The claim contains two separable assertions, and they are checked separately: that the effect is real
at per-step 8, and that **more replay is worse** (per-step 8 -> -0.010, 16 -> +0.017, 48 -> +0.007).

    python -m experiments.e61_replay_recreation
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

#: per-step draw -> artifact
ARTIFACTS = {
    8: "runs/e61_replay96_step8.json",
    16: "runs/e61_replay96_step16.json",
    48: "runs/e61_replay96_step48.json",
}

#: What the claim states, verbatim from `2026-09-22-replay-budget-inversion.md`: naive forgetting,
#: replay forgetting, replay accuracy, and the contrast's sigma.
CLAIM = dict(naive_forgetting=(0.066, 0.019), replay_forgetting=(-0.010, 0.006),
             replay_accuracy=(0.968, 0.013), contrast_sigma=4.2,
             budget_inversion={8: -0.010, 16: 0.017, 48: 0.007})


def load(path: str):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def per_replicate(blk: dict) -> np.ndarray:
    return np.asarray([r["mean_forgetting"] for r in blk["replicates"]], dtype=float)


def paired_stats(dl: np.ndarray) -> dict:
    n = dl.size
    mean = float(dl.mean())
    sem = float(dl.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    loo = []
    flip, lev = False, 0.0
    for i in range(n):
        keep = np.delete(dl, i)
        s = float(keep.std(ddof=1) / np.sqrt(keep.size))
        loo.append(abs(float(keep.mean() / s)) if s else float("inf"))
        if sem:
            lev = max(lev, abs(float(keep.mean()) - mean) / sem)
        if np.sign(keep.mean()) != np.sign(mean):
            flip = True
    pos = int((dl > 0).sum())
    neg = int((dl < 0).sum())
    tied = int((dl == 0).sum())
    p = float(binomtest(pos, pos + neg).pvalue) if (pos + neg) else float("nan")
    return dict(n=n, delta=mean, sem=sem, sigma=abs(mean) / sem if sem else float("inf"),
                signs="".join("+" if v > 0 else ("0" if v == 0 else "-") for v in dl),
                n_pos=pos, n_neg=neg, n_tied=tied, sign_p=p,
                loo_min=float(min(loo)), loo_max=float(max(loo)), loo_flips=bool(flip),
                leverage=float(lev))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-out", default="runs/e61_replay_recreation_analysis.json")
    args = ap.parse_args()

    out: dict = {"claim": {k: (dict(v) if isinstance(v, dict) else v) for k, v in CLAIM.items()},
                 "per_step": {}}

    print("=" * 104)
    print("1. EACH PER-STEP DRAW AGAINST THE CLAIM")
    print("=" * 104)
    print(f"   the claim: naive forgetting {CLAIM['naive_forgetting'][0]:+.3f} "
          f"+- {CLAIM['naive_forgetting'][1]:.3f}, replay "
          f"{CLAIM['replay_forgetting'][0]:+.3f} +- {CLAIM['replay_forgetting'][1]:.3f}, "
          f"replay accuracy {CLAIM['replay_accuracy'][0]:.3f} +- "
          f"{CLAIM['replay_accuracy'][1]:.3f}, contrast {CLAIM['contrast_sigma']} sigma\n")
    print(f"   {'per-step':>9}{'n':>4}{'naive':>12}{'replay':>12}{'replay acc':>13}"
          f"{'delta':>11}{'sem(paired)':>12}{'sigma(paired)':>14}{'sigma(unpaired)':>16}")
    for step, path in ARTIFACTS.items():
        d = load(path)
        if d is None:
            print(f"   {step:>9}   -- artifact absent ({path})")
            continue
        nv = per_replicate(d["methods"]["naive"])
        rv = per_replicate(d["methods"]["replay"])
        n = min(nv.size, rv.size)
        dl = rv[:n] - nv[:n]
        st = paired_stats(dl)
        sem_un = float(np.hypot(d["methods"]["naive"]["forgetting_sem"],
                                d["methods"]["replay"]["forgetting_sem"]))
        print(f"   {step:>9}{n:>4}{nv.mean():>+12.5f}{rv.mean():>+12.5f}"
              f"{d['methods']['replay']['final_accuracy']:>13.4f}{st['delta']:>+11.5f}"
              f"{st['sem']:>12.5f}{st['sigma']:>14.2f}{abs(st['delta'])/sem_un:>16.2f}")
        print(f"   {'':>9}    own sigma of replay's forgetting: "
              f"{abs(rv.mean())/d['methods']['replay']['forgetting_sem']:.2f} "
              f"(claim's implicit: {abs(CLAIM['replay_forgetting'][0])/CLAIM['replay_forgetting'][1]:.2f})")
        print(f"   {'':>9}    paired per-replicate delta: "
              + " ".join(f"{v:+.5f}" for v in dl))
        print(f"   {'':>9}    signs {st['signs']}  {st['n_pos']}+/{st['n_neg']}-"
              f"{tied_suffix(st)}  sign p = {st['sign_p']:.4f}")
        print(f"   {'':>9}    LOO sigma range [{st['loo_min']:.2f}, {st['loo_max']:.2f}]  "
              f"LOO flips {st['loo_flips']}  leverage {st['leverage']:.2f}")
        print()
        out["per_step"][str(step)] = dict(
            artifact=path,
            naive_forgetting=float(nv.mean()),
            replay_forgetting=float(rv.mean()),
            replay_accuracy=float(d["methods"]["replay"]["final_accuracy"]),
            sigma_unpaired=abs(st["delta"]) / sem_un, **st)

    got = out["per_step"]
    print("=" * 104)
    print("2. THE BUDGET INVERSION -- is more replay worse?")
    print("=" * 104)
    print(f"   {'per-step':>9}{'replay forgetting':>20}{'claimed':>11}{'agrees':>9}")
    inv_ok = True
    for step in sorted(ARTIFACTS):
        k = str(step)
        claimed = CLAIM["budget_inversion"][step]
        if k not in got:
            print(f"   {step:>9}{'absent':>20}{claimed:>+11.3f}")
            inv_ok = False
            continue
        m = got[k]["replay_forgetting"]
        ok = abs(m - claimed) < 0.02
        inv_ok &= ok
        print(f"   {step:>9}{m:>+20.5f}{claimed:>+11.3f}{str(ok):>9}")
    if len(got) >= 2:
        order = sorted(int(k) for k in got)
        vals = [got[str(s)]["replay_forgetting"] for s in order]
        print(f"\n   measured forgetting across the sweep: "
              + ", ".join(f"{s} -> {v:+.5f}" for s, v in zip(order, vals)))
        print(f"   the claim's shape (best at the SMALLEST per-step draw) holds: "
              f"{vals[0] < min(vals[1:]) if len(vals) > 1 else 'n/a'}")
        out["inversion"] = dict(claim_agrees=bool(inv_ok),
                                measured=dict(zip(map(str, order), vals)))

        #: The inversion is itself a contrast, and the per-step arms within one configuration run on
        #: the SAME replicate seeds -- so it is paired, and its sigma is a fact about the sweep rather
        #: than about two independent numbers.  `e46`'s lesson was that a pooled three-seed figure can
        #: reverse; here every arm has five replicates and they share seeds, so the right test is
        #: available and there is no reason to compare means unpaired.
        print()
        print("=" * 104)
        print("3. THE INVERSION AS A PAIRED CONTRAST")
        print("=" * 104)
        print("   all per-step arms of one configuration share their replicate seeds, so the")
        print("   difference between two per-step amounts is a paired quantity on 5 replicates.\n")
        per_rep = {}
        for step in sorted(ARTIFACTS):
            d = load(ARTIFACTS[step])
            if d is None:
                continue
            per_rep[step] = np.asarray([r["mean_forgetting"] for r in d["methods"]["replay"]["replicates"]])
        print(f"   {'contrast':<24}{'delta':>11}{'sem(paired)':>13}{'sigma':>8}{'signs':>9}{'p':>9}")
        inv_rows = []
        steps = sorted(per_rep)
        for s_a, s_b in zip(steps, steps[1:]):
            va, vb = per_rep[s_a], per_rep[s_b]
            n = min(va.size, vb.size)
            dl = vb[:n] - va[:n]
            st = paired_stats(dl)
            print(f"   {f'{s_b} - {s_a}':<24}{st['delta']:>+11.5f}{st['sem']:>13.5f}"
                  f"{st['sigma']:>8.2f}{st['signs']:>9}{st['sign_p']:>9.4f}")
            print(f"   {'':<24}LOO sigma [{st['loo_min']:.2f}, {st['loo_max']:.2f}]  flips "
                  f"{st['loo_flips']}  leverage {st['leverage']:.2f}")
            inv_rows.append(dict(contrast=f"{s_b} - {s_a}", **st))
        out["inversion_paired"] = inv_rows
        if inv_rows:
            best = max(inv_rows, key=lambda r: r["sigma"])
            print(f"\n   the inversion's strongest adjacent contrast is {best['contrast']} at "
                  f"{best['sigma']:.2f} sigma")
    else:
        print("\n   only one per-step draw has landed -- the inversion is not yet checkable")

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {args.json_out}")


def tied_suffix(st: dict) -> str:
    return f"/{st['n_tied']}tied" if st["n_tied"] else ""


if __name__ == "__main__":
    main()
