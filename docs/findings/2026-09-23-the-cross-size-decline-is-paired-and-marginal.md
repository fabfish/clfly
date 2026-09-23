# The cross-size decline is paired, and it is marginal — the two forms disagree again

**Date:** 2026-09-23
**Script:** `experiments/e92_grid_report.py` §8; artifact `runs/e92_grid_report.json` under
`cross_size_paired`.
**Data:** cs = 300 and cs = 800 complete at **20 of 20 cells each**; cs = 1500 at 8, all `flat`.
**Context:** `docs/findings/2026-09-23-p6s-falsifier-fired-and-a-size-trend-appears.md` §3, which recorded
the trend and refused to read it; `docs/findings/2026-09-23-the-three-size-decay-is-not-resolved.md` (`e87`).

---

## 1. The comparison is paired and the interval must be too

The grid's twenty profiles are **the same objects at every circuit size** — that is the whole point of
choosing cells by concentration rather than by label. So the cross-size comparison of the partial spread
statistic is **paired on the profile**, and the unit to resample is the profile, with **one index set used at
both sizes**. Bootstrapping the two partials independently would report an interval for a comparison nobody
made, and it would be the wrong one in the direction that flatters the claim.

| comparison, 20 shared profiles | partial, absolute form | difference | **paired bootstrap** | at or below zero |
|---|---|---|---|---|
| d = 952 → d = 1307 | +0.919 → +0.618 | **−0.301** | **[−0.638, −0.006]** | **97.75%** |
| d = 952 → d = 1307, relative form | +0.955 → +0.713 | −0.242 | [−0.779, **+0.044**] | 96.10% |

**So the decline is resolved for the absolute form by a hair and not resolved for the relative form.** The
absolute interval's upper end is **−0.006**: 2.25% of resamples put the difference above zero. The relative
interval crosses zero with 3.90% above it. **The two forms disagree, for the third time in this thread** —
they disagreed on the nine's raw correlations at d = 952, they disagreed on the grid's per-seed partials,
and now they disagree on whether the cross-size decline exists.

**And that is the same shape `e87` found for the co-movement**, which is why it is worth stating before the
grid completes rather than after: `e82`'s apparent **3.29σ** decline across the three sizes became **0.75σ
with an interval spanning zero** once the shared draws were resampled instead of the nine partitions. The
mechanism was that nine partitions measured on one set of six relabellings are not nine independent
observations. Here the units are the twenty profiles and they *are* the shared unit, so the correction
available is the opposite one — pairing, which **tightens** rather than widens — and it still leaves the
absolute form at the edge and the relative form unresolved.

## 2. What this licenses about the trend

The trend recorded one fire ago was **+0.919 → +0.618** between two *complete* grids and **+0.120** on a
partial third. The paired test settles the first step only:

- **The first step is real but marginal for the absolute form** (2.25% of resamples above zero) and
  **unresolved for the relative form** (3.90%). It should not be reported as a resolved decline.
- **The second step cannot be tested yet.** cs = 1500 shares only **8 of its 20** profiles with the others,
  so its intervals are `[−1.638, +0.848]` and `[−1.376, +1.017]` — the width of the sampling noise at eight
  profiles swallows any effect. Those rows are in the artifact and are **not** results.
- **Therefore the sentence the paper can write is unchanged in strength.** "The statistic works at two sizes
  and there is a hint that it works less well at the larger one" is what the complete data support; "it
  declines with size" needs the last twelve cells and may well need more than that.

## 3. A prediction, recorded before the grid completes

**Prediction.** With all 20 cells at cs = 1500, the paired d = 952 → d = 1874 difference will be **negative
in sign** and its interval will **still contain zero** for at least one of the two forms — because the
partial at d = 1874 will have to fall from +0.120 to about −0.3 for the interval to clear zero at n = 20
with the spread these profiles show, and the d = 952 → d = 1307 step, which is a *smaller* size step, is
itself only at the edge.

**Falsifier.** A paired interval at d = 952 → d = 1874 that excludes zero for **both** forms. That would
make the trend a resolved size dependence, and it would then need reconciling with `e87`'s finding that the
co-movement's decline is *not* resolved — two measurements of one mechanism disagreeing about whether the
mechanism is size-dependent would be the more interesting outcome, and the reconciliation would have to be
in the resampling units, not in the statistics.

## 4. Why this was worth doing before the run finished

The previous fire recorded the trend and explicitly refused to read it. This fire **converts that refusal
into a number**: the first step is −0.301 with a paired interval that just excludes zero. Had the trend been
written up at 60 of 60 as "the partial declines from 0.919 through 0.618 to 0.120", it would have been
quoting (a) two point estimates whose difference is marginal and form-dependent, and (b) a third that is
eight profiles of a partial set. **The paired form of the test is what makes the difference between those
two write-ups, and it costs one index set.**
