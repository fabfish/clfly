# The competing explanation is not excluded, and the reason is the benchmark's own spread

**Date:** 2026-09-23
**Method:** the three configurations of `e99`/`e100` tested against the "easier benchmark compresses every
gap" hypothesis, using each arm's own sem.
**Context:** `docs/findings/2026-09-23-the-lower-rank-task-family.md` §4, which recorded that hypothesis as
*the strongest competing explanation* and as *not addressed by anything measured here*.

---

## 1. I tried to exclude it from existing data, and could not

The hypothesis is that the block-minus-diagonal gap shrank because the *overall forgetting level* fell — an
easier benchmark compressing all the gaps — rather than because the block's Fisher got better estimated. It
predicts **gap proportional to level**. The three configurations:

| configuration | level (`naive`'s forgetting) | block − diagonal gap |
|---|---|---|
| 4 classes, cs = 800 | +0.0729 ± 0.0151 | +0.0396 ± 0.0250 |
| 4 classes, cs = 300 | +0.0875 ± 0.0194 | +0.0167 ± 0.0432 |
| 2 classes, cs = 800 | +0.0167 ± 0.0107 | +0.0021 ± 0.0151 |

The pair that *isolates* the hypothesis is cs = 800 → cs = 300, because there the circuit changes and the
task rank does not: **the level rises +0.0146 and the gap falls −0.0229, which is the opposite of what the
hypothesis predicts.** That looked like a refutation available for free.

**It is not, and the reason is arithmetic I had not done.** Both movements are **unresolved**:

| movement | difference | its σ | resolved? |
|---|---|---|---|
| level, cs = 800 → 300 | +0.0146 ± 0.0246 | **0.59σ** | no |
| gap, cs = 800 → 300 | −0.0229 ± 0.0499 | **0.46σ** | no |

**So the pair that was supposed to isolate the hypothesis contains no resolved movement in either quantity.**
I had compared point estimates and treated their *signs* as findings — the same error this project has a rule
about and the one that produced `e86`'s one-loss reading and `e82`'s 3.29σ decay. The correction is that the
hypothesis is **not excluded**; it stands exactly as `e100` recorded it.

## 2. And the level-normalised ratio is unusable, which closes the other route

The fallback is to divide the gap by the level, which needs the level to be well measured. It is not:

| configuration | ratio | the ratio's own relative error |
|---|---|---|
| 4 classes, cs = 800 | 0.543 | **66%** |
| 4 classes, cs = 300 | 0.190 | **260%** |
| 2 classes, cs = 800 | 0.125 | **725%** |

At 2 classes the ratio is a quotient of two small numbers whose relative errors are 64% and 725%, so it
carries a ± larger than itself. **A monotone reading across those three is not available**, and the
temptation to report "the normalised gap still falls monotonically" has to be resisted: it falls because
both numerator and denominator are falling faster than their errors.

## 3. What would separate them, quantified

The benchmark's own per-repeat spread is the binding constraint. From the observed sems, resolving the level
movement at 2σ needs the difference's sem to fall from 0.0246 to 0.0073, a factor of **3.4**, i.e. **~11×
the replicates — about 57 per arm**. At the measured 5.1–22.9 minutes per arm-replicate that is
**6–44 hours for this one contrast**, which is the same order as the rung question's own price and therefore
not an afternoon's control.

**So the honest position is not "the account is confirmed" and not "the account is untested": it is that
both candidate explanations are beyond this benchmark's resolution.** The estimation-noise account's gaps are
0.39σ and 0.14σ, and the level hypothesis's movement is 0.59σ. **Two explanations, three configurations,
five replicates, and no resolved difference between either explanation and zero.**

## 4. What this changes in the two findings it follows

- `e100`'s §4 caveat stands and is now **quantified** rather than flagged: the hypothesis predicts what was
  observed, nothing measured here excludes it, and excluding it costs ~57 replicates per arm.
- `e99`'s §5 and `e100`'s §2 both say the account is "resolved in direction and unresolved in size". **That
  remains true and is now sharper**: its *direction* is three consistent point estimates whose individual
  movements are all inside their own σ. A reader should take "two independent confirmations in direction" to
  mean **two consistent signs**, not two resolved effects — which is how the findings wrote it and is worth
  saying plainly because the phrase "confirmed twice" invites the stronger reading.

**And the third time this week the answer has been the benchmark's spread rather than the effect**: the
`naive` per-repeat sd of 0.048 against mean forgettings of 0.017–0.088 means that **every** network-line gap
this project has reported is a fraction of one replicate's own variation, however many replicates are
averaged. The sem shrinks; the spread does not. That is the single most important sentence about the network
line, and it is now the conclusion of three separate findings.
