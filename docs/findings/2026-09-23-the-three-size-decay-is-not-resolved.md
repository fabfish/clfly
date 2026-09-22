# E87 — the three-size decay is **not resolved**: the nine partitions share their draws, and the sign record was never independent evidence

**Date:** 2026-09-23
**Script:** `experiments/e87_paired_co_movement_bootstrap.py`, `experiments/e82_three_sizes.py`
**Artifacts:** `runs/e87_paired_co_movement_bootstrap.json`, `runs/e82_three_sizes.json`
**Context:** `2026-09-23-the-pressure-mechanism-at-three-sizes.md` (the finding this corrects), `2026-09-23-the-pressure-mechanism.md` (e81)

---

## 1. What the previous finding claimed, and the assumption underneath it

`2026-09-23-the-pressure-mechanism-at-three-sizes.md` reported the mechanism's decay from d = 1307 to
d = 1874 as **3.29σ with eight of nine partitions declining**, and called it "measured rather than
inferred". That combined two things: a paired difference of −0.0962 in mean *r*, and a sign record of
8/9. The σ came from `sd(d_i)/√9` over the nine partition-level differences `d_i`.

**That σ treats the nine partitions as nine independent observations of the difference. They are not.**
All nine partitions of one run see the **same six relabellings**, so any draw-level effect — "these six
draws happen to be favourable or not" — moves every partition's correlation in the same direction and
therefore every difference. And an eight-of-nine sign pattern is *exactly* what a shared-draw effect
produces, so it was never the independent confirmation it read as.

## 2. The right resampling unit, and the result

The unit is the **draw**. Resample the six draw slots with replacement, independently within each run
(their relabellings are different objects), recompute all nine correlations on that resample, average, and
take the difference. 4000 replicates:

| comparison | mean | independent-partition sem | **draw bootstrap sd** | σ, partition / **draw** | 95% interval | % below zero |
|---|---|---|---|---|---|---|
| d = 1307 − d = 952 | −0.0166 | 0.0198 | **0.0790** | 0.84 / **0.45** | [−0.2303, +0.0728] | 65.2% |
| **d = 1874 − d = 1307** | **−0.0962** | 0.0293 | **0.1165** | **3.29 / 0.75** | **[−0.3110, +0.1468]** | 80.5% |

**The draw-level interval is 4.0× the partition sem in both comparisons, and both include zero.** So:

> **The decay is a point estimate, not a measurement.** The mean *r* does fall from 0.906 to 0.810 and
> eight of nine partitions do decline, but with the correct resampling unit the difference is **0.75σ**
> with a 95% interval from −0.31 to +0.15.

The point estimate is unchanged and still worth reporting — the mechanism's strength at the largest size
is 0.810 against 0.906, and any future design should assume it may be real — but the word *measured* is
withdrawn, and the 8/9 sign record loses its evidentiary force.

## 3. What survives, and what the correction costs

**Survives entirely:** the mechanism holds at three circuit sizes. Mean *r* 0.923 / 0.906 / 0.810, mean
*r*² 0.854 / 0.828 / 0.676, **all 81 seed-level correlations positive**, and the bare alignment's +0.170
beaten at every size by 4.8× in *r*². The paper's §4.3 statement that the draw spread is about the
precision-weighted projected deficit is untouched; the honest form of "68–85% depending on circuit size"
becomes **"68–85%, with the size dependence not resolved"**.

**Withdrawn:** "the mechanism is not size-invariant" as a *measured* claim. It is a difference in point
estimates whose interval spans zero.

**And the explanation-test the previous finding proposed is now less urgent** — it was going to separate
"the decay is a property of the design" from "of the quantity", but there is no resolved decay to explain.
It becomes a power question: six draws × three seeds × nine partitions cannot resolve a 0.10 difference in
*r*, and the bootstrap says how much more would be needed (the interval is ±0.23 at the current design).

## 4. The distinction that decides which comparisons are protected

Not every sign record across partitions has this problem, and the difference is worth stating precisely:

* **A comparison of two runs at different configurations** (d = 1874 against d = 1307) has no protection:
  the two runs' draw effects are independent, so they add rather than cancel, and the partition-level sem
  is wrong by 4×.
* **A comparison of two quantities measured on the same draws** — `e81`'s paired
  `projection_pressure − alignment`, reported at +0.736 ± 0.061 with nine of nine positive and p = 0.0039 —
  *should* be protected, because a draw-favourability effect that inflates or deflates both correlations
  cancels in their difference.

**That second claim is untested and the check cannot be run from disk.** `e75`'s first version filtered its
per-(draw, seed) alignment values out of the artifact to keep the file small; the script was fixed
immediately, but a fix does not add fields back to an artifact already written, and `e87` reports the gap
rather than computing a number from something else. `e88` re-runs `e75` so the check becomes possible —
and until it runs, **`e81`'s paired 9-of-9 stands unexamined for shared draws**, which the paper currently
quotes as its strongest single piece of mechanism evidence.

## 5. Limits

- **4000 bootstrap replicates over six draws.** Resampling six slots gives a coarse but honest
  distribution; the interval's endpoints carry Monte-Carlo error of order 0.01, well below the widths
  reported.
- **The bootstrap captures the draw as the only shared factor.** The nine partitions also share the
  circuit, the task suite and the seed set, so if some *partition-independent* nuisance varies between the
  two runs, even the bootstrap interval understates the uncertainty. It is a correction in the right
  direction, not a complete accounting.
- **A 0.75σ difference is not evidence of *no* difference.** The correct statement is that this design
  cannot resolve one of this size, which is a statement about six draws rather than about the mechanism.
- **The correction is to my own claim from earlier the same day**, and it was found by asking what the
  resampling unit should be rather than by any new measurement. That is the same shape as `e66`'s
  correction to `e63`: a σ computed under an assumption that the data do not satisfy.
