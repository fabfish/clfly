# The grid is complete: the clause passes at all three sizes, and the "decline" was the subset talking

**Date:** 2026-09-23
**Script:** `experiments/e92_grid_report.py`; artifact `runs/e92_grid_report.json`
**Data:** all three circuit sizes complete at **20 of 20 cells** — the last one, `cs1500/harmonic/k160`, had to
be re-measured after the sweep's four-hour task timeout killed it.
**Context:** `docs/findings/2026-09-23-p6s-falsifier-fired-and-a-size-trend-appears.md` §3, which recorded the
trend and refused to read it; `docs/findings/2026-09-23-the-cross-size-decline-is-paired-and-marginal.md`,
which turned the refusal into a paired interval and recorded prediction **P7**.

---

## 1. The verdict, with every clause pre-registered

| clause | outcome |
|---|---|
| **P1** partial > 0 at every size | **PASS** — +0.919, +0.618, +0.872 |
| **P2** raw spread beats raw concentration at every size | **FAIL** — at d = 1307 concentration wins (+0.923 against +0.582) |
| **P3** partial ≥ +0.5 at d = 1307 | **PASS** (+0.618) |
| **P4** ≥ 7 of 9 per-seed partials positive | **PASS** — **9 of 9** |
| **P5** the absolute spread's cross-size behaviour is a level artefact | **PASS** — median level **6.18×** against median target **0.24×**, and on **20 of 20** cells the level drifts by more than 1.5× while the relative form is closer to 1 |
| **P6** the second shape decorrelates the confound at d = 1307 | **FAILED and its falsifier fired** (coupling +0.923, not below +0.80) |
| **P7** the d = 952 → d = 1874 paired difference is negative with an interval containing zero | **PASS** — −0.048 [−0.253, +0.138] absolute, −0.081 [−0.282, +0.094] relative |
| **F1** partial ≤ 0 at two or more sizes | **does not fire** |
| **F2** the raw ordering reverses at some size | **fires** (d = 1307) |

And the supporting structure, which is what makes P1 more than a sign test:

| circuit size | partial | per-seed | leave-one-cell-out | profile bootstrap |
|---|---|---|---|---|
| d = 952 | **+0.919** (p = 2.7e-08) | 3 of 3 | +0.896 to +0.951, no flip | **+0.892 [+0.718, +0.977]**, 0.00% below zero |
| d = 1307 | **+0.618** (p = 0.005) | 3 of 3 | +0.552 to +0.669, no flip | **+0.573 [+0.272, +0.813]**, 0.20% below zero |
| d = 1874 | **+0.872** (p = 1.2e-06) | 3 of 3 | +0.846 to +0.888, no flip | **+0.835 [+0.641, +0.940]**, 0.00% below zero |

**So the predictor-shaped use of pressure holds at all three circuit sizes** on a design whose concentrations
are set rather than found, with the confound partialled out of both ranks, and it survives every robustness
check this project uses.

## 2. And the "declining trend" was the subset talking

One fire ago this document recorded, and explicitly refused to read:

> partial **+0.919 → +0.618 → +0.120**, with the third row at **8 of 20 cells of one shape**, "not yet a
> result and must not be read as one"

**The completed third row is +0.872, not +0.120.** The eight `flat` cells that existed then were not a noisy
version of the twenty; they were a *different set*, and the difference is 0.75 in a partial correlation — the
whole apparent trend. **This is the cleanest self-inflicted demonstration of rule 17's third shape the project
has**: the refusal to read it was correct, the number it refused to read was wrong by an amount larger than
every effect this line is arguing about, and the honest alternative — waiting eleven cells — cost under an hour.

**And the shape it exposed is better than the trend it replaced.** Paired on the same twenty profiles:

| comparison | absolute | relative |
|---|---|---|
| d = 952 → d = 1307 | **−0.301 [−0.645, −0.015]**, 98.15% at or below zero | −0.242 [−0.794, **+0.049**], 95.08% |
| d = 952 → d = 1874 | −0.048 [−0.253, +0.138], 76.68% | −0.081 [−0.282, +0.094], 85.92% |
| d = 1307 → d = 1874 | **+0.254 [−0.021, +0.581]**, 3.05% at or below zero | +0.161 [−0.123, +0.669], 11.97% |

The weakest size is the **middle** one, and it is the size whose concentration–target coupling is strongest —
**+0.923** at d = 1307 against +0.677 and +0.571. **The statistic is weaker exactly where the confound it
removes is stronger**, which is a property of that circuit's task geometry and not of circuit size. That also
explains why the relative form's step is the one that fails to resolve at 952 → 1307: it is the form whose
residual is thinnest there.

## 3. What is *not* claimed

- **P2 fails, and it is a real failure of the raw form.** On concentration-set cells the raw pressure spread
  does *not* beat raw concentration at every size; at d = 1307 it loses badly (+0.582 against +0.923). The
  statistic's case rests entirely on the partial — which is the form the grid was built to test, and which is
  also the form that a reader suspicious of the confound should want.
- **P6 failed**, and the design's justification changed as a result: the two shapes are complementary at
  d = 952 and *not* at d = 1307, where the second shape's contribution is the ten extra cells. The claim
  "the second shape is what makes the statistic readable" is a d = 952 result.
- **The three sizes share three task seeds and one circuit each.** The profile bootstrap resamples profiles
  and does not remove shared seed or circuit variation, so each interval is a lower bound in the sense rule 23
  describes. The companion is the per-seed column, which is 9 of 9 positive with no leave-one-cell-out flip
  anywhere — a count, not a calibrated test.
- **`shape adds information beyond concentration` holds at all three sizes** (F = 121/82/153, 5.7/17.1/32.8,
  45/44/103; p ≤ 0.03 throughout), but the *magnitudes* differ by a factor of twenty between d = 952 and
  d = 1307, so the claim is qualitative at this sample size even though it is significant everywhere.

## 4. The paper

§4.3's standing sentence — *"the predictor-shaped use of pressure is therefore supported at exactly one
circuit size and untested elsewhere"*, then *"passes at two of three sizes"* — is now replaced by the table
above and the dip-not-trend reading. That is the third revision of that sentence in two days, and the first
one written against a completed grid.
