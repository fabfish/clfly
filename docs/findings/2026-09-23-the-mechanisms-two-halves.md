# E86 / E87 / E88 — of the mechanism's two halves, the **co-movement is robust** and the **spread statistic is not**

**Date:** 2026-09-23
**Scripts:** `experiments/e87_paired_co_movement_bootstrap.py`, `experiments/e86_spread_at_other_sizes.py`
**Artifacts:** `runs/e87_paired_co_movement_bootstrap.json`, `runs/e86_drawsd_cs300_*.json`, `runs/e88_alignment_perseed_rerun.json`
**Context:** `2026-09-23-pressure-spread-predicts-the-draw-spread.md` (e80), `2026-09-23-the-pressure-mechanism.md` (e81), `2026-09-23-the-three-size-decay-is-not-resolved.md` (e87)

---

## 1. The two halves, and why they need separate checks

`e80` and `e81` established two different things about `projection_pressure`, and the project has been
quoting them together ever since:

* **the co-movement** — pressure and the control's excess move together *on the same relabelling*:
  *r* = 0.906, *r*² = 0.828, against 0.170 / 0.066 for the bare alignment on the identical design (`e81`);
* **the spread statistic** — the **size** of pressure's own draw-to-draw variation ranks the **size** of the
  excess's: Spearman **+0.767 (p = 0.016)** against concentration's +0.617, with an independence check at
  +0.317 (`e80`).

The second is the one a *predictor* would use. It is also the one that had no replication, because its
target — nine measured draw sds — was a d = 1307 quantity. `e86` supplies the targets at two more sizes.

## 2. The co-movement survives the shared-draw correction, at 5.15σ

`e82`'s size comparison was corrected by `e87` because its nine partitions share their six relabellings.
`e81`'s headline has the same structure — nine partitions, a sign record of nine of nine, p = 0.0039 — **but
a different protection**: both arms are measured on the *same* draws, so a draw-favourability effect that
moves both correlations should cancel in their difference. That was a claim, not a measurement, and the
check could not be run from disk: `e75`'s first version had filtered its per-(draw, seed) alignment values
out of the artifact to save bytes. `e88` re-ran it (reproducing `e75`'s *r* to three decimals on all nine
partitions, `side` differing in the fourth), which makes the check possible.

| | value |
|---|---|
| paired mean difference (`pressure − alignment`) | **+0.7364** |
| independent-partition sem | 0.0607 → 12.14σ (sign p = 0.0039) |
| **shared-draw bootstrap** | **0.1400 → 5.15σ** |
| **95% interval** | **[+0.4184, +0.9808]** |
| **resamples above zero** | **100.0%** (4000 replicates) |

**So the shared-draw component is real but partial, and the comparison is protected.** The interval is
**2.31×** the partition sem — the correction is not negligible, because resampling draws moves each
correlation differently even when both are computed on the same relabel — and it still **excludes zero by a
wide margin**. The mechanism's central claim holds under the same scrutiny that turned `e82`'s 3.29σ into
0.75σ. That contrast is the useful part: **it is the *design* of the comparison, not its subject, that
decides whether a shared-draw correction bites.**

## 3. The spread statistic does not replicate at d = 952, and the falsifier fires

`e86` ran the nine draw-sd measurements at cs = 300 (d = 952) at `e14`/`e74`'s protocol. The d = 952 half is
complete; the cs = 1500 half is still running.

| size | **absolute** pressure sd vs measured sd | **concentration** vs measured sd | relative pressure sd |
|---|---|---|---|
| **d = 952** | **+0.412** (p = 0.27) | **+0.832** (p = 0.005) | +0.882 (p = 0.002), but **+0.950** with concentration |
| d = 1307 | **+0.767** (p = 0.016) | +0.617 (p = 0.077) | +0.850 (p = 0.004), +0.767 with concentration |

**At d = 952 the absolute pressure spread is +0.412 — below the pre-registered +0.70 and well below
concentration's +0.832.** The falsifier named in the plan's `e86` row fires. And the form that *does* score
well there, the relative spread at +0.882, correlates **+0.950 with concentration**, so it is a size
restatement rather than an independent predictor — the same failure mode `e80` diagnosed at d = 1307 when
the relative form hit +0.767 with concentration.

So `e80`'s headline — *the absolute pressure spread outranks concentration and is not a size scalar* — was
a **d = 1307 event**. At a second circuit size the ordering reverses and concentration wins.

## 4. What this leaves, stated plainly

**Robust:** the co-movement. It holds at three circuit sizes (mean *r* 0.923 / 0.906 / 0.810; all 81
seed-level correlations positive; the alignment beaten everywhere by 4.8× in *r*²), and its paired
comparison against the alignment survives the shared-draw bootstrap at **5.15σ with 100% of resamples above
zero**. The paper's §4.3 mechanism sentence rests on this and is unaffected.

**Not robust:** the spread statistic. One size in its favour (+0.767 against +0.617), one against
(+0.412 against +0.832). At n = 9 with a target carrying 20–50% error, a single size's ordering was never
much evidence, and `e80`'s own finding said so — "four candidates one at p = 0.016 is not a discovery on
its own". What this run adds is that the second size **contradicts** rather than merely fails to confirm.

**Consequence for how the mechanism is described.** The predictor-shaped use of pressure — "compute the
partition's pressure spread and you know the size of its control's spread" — is not supported away from
d = 1307. The *explanatory* use — "the draw spread is about the precision-weighted projected deficit rather
than subspace geometry" — is supported, because that is the co-movement claim.

## 5. Limits

- **d = 1874's spread targets are still running**, so the spread statistic has two sizes rather than three;
  the verdict above is a 1–1 split and could become 1–2 or 2–1.
- **`e81`'s bootstrap resamples only the draw.** The nine partitions also share the circuit, the task suite
  and the seed set, so if a partition-independent nuisance varies, even this interval understates the
  uncertainty. The direction of the correction is right; the magnitude is a floor.
- **`e88` is a re-run, not the original.** Its *r* values reproduce `e75`'s to three decimals, with `side`
  differing by 0.001 — consistent with rule 21's fourth-digit thread sensitivity — so the alignment arm of
  the paired check is the same quantity measured again rather than the same numbers.
- **Nine partitions, n = 9 everywhere.** Every Spearman in §3 is on nine points, where the two-sided 0.05
  critical value is 0.683; +0.832 clears it and +0.412 does not, which is why the reversal is reportable
  and the *individual* support at either size is weak.
