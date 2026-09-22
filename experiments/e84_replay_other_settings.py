"""E84 -- the two pool-96 replay settings `e61` does not cover, and the fingerprint that says which one is a restoration.

`e62`'s census found `replay_per_task: 96` in **exactly one** of the artifacts carrying a `naive` arm —
`e61`'s own recreated run. So of the four replay numbers the paper's §4.7 carries, one is now recreated
(the hardened class-IL setting, at 6.73σ with sixteen replicates) and **two have no artifact at all**:
the task-incremental and the class-incremental settings at pool 96 / per-step 8. This script analyses
their recreation.

**The two arms are not equally trustworthy, and the `naive` fingerprint is what separates them.** `naive`
carries no basis and no penalty, so it is fixed by the configuration alone — `e54` used exactly that to
group artifacts by computation rather than by an assumed config key. The settled finding reports:

* **task-IL**: naive **+0.101**, which matches `e10_rung_*`'s stored naive **0.8241 / +0.1007** exactly.
  So a recreation whose `naive` reproduces that *is* the same computation, and its replay arm is a
  **restoration** of the missing number.
* **class-IL**: naive **+0.059 ± 0.028**, which matches **no** stored artifact. The closest stored
  class-IL naive is `e8_class_incremental`'s **0.9361 / +0.0437**, and it is not equal. So that arm can be
  **re-measured but not confirmed**, and its number is a fresh measurement under the best-matching
  configuration rather than the original.

That distinction is the whole reason this script prints the naive fingerprint first and refuses to call a
remeasured arm a restoration.

    python -m experiments.e84_replay_other_settings
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

#: The two recreations, and the stored naive each one's configuration should reproduce.
SETTINGS = [
    ("task-IL", "runs/e84_replay96_taskIL_5reps.json", "runs/e10_rung_cell_class.json"),
    ("class-IL", "runs/e84_replay96_classIL_5reps.json", "runs/e8_class_incremental.json"),
]

#: What the settled finding claims, at three replicates.
CLAIMED = {"task-IL": dict(naive_acc=0.824, naive_acc_sem=0.036, naive_forget=0.101, naive_f_sem=0.049,
                           replay_acc=0.921, replay_forget=-0.056, contrast=-0.157, sigma=3.1),
           "class-IL": dict(naive_acc=0.928, naive_acc_sem=0.016, naive_forget=0.059, naive_f_sem=0.028,
                            replay_acc=0.975, replay_forget=-0.010, contrast=-0.069, sigma=2.2)}


def load(path: str):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def paired_stats(dl: np.ndarray) -> dict:
    n = dl.size
    mean = float(dl.mean())
    sem = float(dl.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    loo, flip = [], False
    for i in range(n):
        keep = np.delete(dl, i)
        s = float(keep.std(ddof=1) / np.sqrt(keep.size))
        loo.append(abs(float(keep.mean() / s)) if s else float("inf"))
        if np.sign(keep.mean()) != np.sign(mean):
            flip = True
    pos, neg = int((dl > 0).sum()), int((dl < 0).sum())
    p = float(binomtest(pos, pos + neg).pvalue) if (pos + neg) else float("nan")
    return dict(n=int(n), delta=mean, sem=sem, sigma=(abs(mean) / sem if sem else float("inf")),
                signs="".join("+" if v > 0 else ("0" if v == 0 else "-") for v in dl),
                sign_p=p, loo_min=float(min(loo)), loo_flips=bool(flip), n_pos=pos, n_neg=neg)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-out", default="runs/e84_replay_other_settings.json")
    args = ap.parse_args()

    out: dict = {"settings": {}}

    print("=" * 108)
    print("1. THE NAIVE FINGERPRINT -- WHICH RECREATION IS A RESTORATION")
    print("=" * 108)
    print("   `naive` carries no basis and no penalty, so the configuration fixes it exactly; `e54` used")
    print("   that property to group artifacts by computation rather than by an assumed config key.\n")
    print(f"   {'setting':<10}{'recreated naive':>18}{'stored naive':>16}{'identical':>11}"
          f"   verdict")
    fingerprints = {}
    for name, path, ref_path in SETTINGS:
        d, ref = load(path), load(ref_path)
        if d is None:
            print(f"   {name:<10}{'absent':>18}")
            continue
        na = d["methods"]["naive"]
        rec = (float(na["final_accuracy"]), float(na["mean_forgetting"]))
        if ref is None:
            sto, verdict = None, "no stored comparison"
        else:
            nr = ref["methods"]["naive"]
            sto = (float(nr["final_accuracy"]), float(nr["mean_forgetting"]))
            verdict = ("RESTORATION -- same computation" if abs(rec[0] - sto[0]) < 1e-9
                       and abs(rec[1] - sto[1]) < 1e-9 else "NOT the same computation")
        fingerprints[name] = dict(recreated=rec, stored=sto, verdict=verdict)
        print(f"   {name:<10}{rec[0]:>10.4f}/{rec[1]:+.4f}{'':>3}"
              f"{(f'{sto[0]:.4f}/{sto[1]:+.4f}' if sto else 'absent'):>16}"
              f"{str(sto is not None and verdict.startswith('RESTORATION')):>11}   {verdict}")
    out["fingerprints"] = fingerprints

    print()
    print("=" * 108)
    print("2. EACH SETTING AGAINST ITS CLAIM, ON THE SAME FIVE REPLICATES")
    print("=" * 108)
    for name, path, _ in SETTINGS:
        d = load(path)
        if d is None:
            print(f"\n   {name}: absent ({path})")
            continue
        cl = CLAIMED[name]
        na, rp = d["methods"]["naive"], d["methods"]["replay"]
        print(f"\n   {name}  (n = {len(na['replicates'])})")
        print(f"   {'':<16}{'recreated':>18}{'claimed (3 reps)':>20}")
        print(f"   {'naive accuracy':<16}{na['final_accuracy']:>10.4f} +/- {na['final_sem']:.4f}"
              f"{cl['naive_acc']:>13.3f} +/- {cl['naive_acc_sem']:.3f}")
        print(f"   {'naive forgetting':<16}{na['mean_forgetting']:>+10.4f} +/- {na['forgetting_sem']:.4f}"
              f"{cl['naive_forget']:>+13.3f} +/- {cl['naive_f_sem']:.3f}")
        print(f"   {'replay accuracy':<16}{rp['final_accuracy']:>10.4f} +/- {rp['final_sem']:.4f}"
              f"{cl['replay_acc']:>13.3f}")
        print(f"   {'replay forgetting':<16}{rp['mean_forgetting']:>+10.4f} +/- {rp['forgetting_sem']:.4f}"
              f"{cl['replay_forget']:>+13.3f}")

        res = {}
        for metric in ("mean_forgetting", "final_accuracy"):
            a = np.asarray([r[metric] for r in rp["replicates"]])
            b = np.asarray([r[metric] for r in na["replicates"]])
            n = min(a.size, b.size)
            st = paired_stats(a[:n] - b[:n])
            res[metric] = st
            print(f"\n   replay - naive, {metric}: {st['delta']:+.5f} +/- {st['sem']:.5f} = "
                  f"{st['sigma']:.2f}sigma   signs {st['signs']}   LOO min {st['loo_min']:.2f}   "
                  f"flips {st['loo_flips']}")
            print(f"      claimed contrast {cl['contrast']:+.3f} at {cl['sigma']:.1f}sigma "
                  f"(forgetting), 3 replicates")
            print(f"      detection floor (2 sems) {2 * st['sem']:.4f}")
        out["settings"][name] = dict(fingerprint=fingerprints.get(name), results=res)

    print()
    print("=" * 108)
    print("3. WHAT EACH ARM CAN BE CALLED")
    print("=" * 108)
    for name in ("task-IL", "class-IL"):
        fp = fingerprints.get(name)
        if fp is None:
            continue
        if fp["verdict"].startswith("RESTORATION"):
            print(f"   {name:<10} a RESTORATION: its naive reproduces the stored value, so the")
            print(f"   {'':<10} configuration is the one the claim was made under.")
        else:
            print(f"   {name:<10} a RE-MEASUREMENT, not a restoration: its naive does")
            print(f"   {'':<10} not reproduce the stored value, so the claim's own configuration is")
            print(f"   {'':<10} not the one measured here.  The number below is usable but is not the")
            print(f"   {'':<10} published one.")

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
