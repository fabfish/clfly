# `e128`: the nominal removable share is not the achievable one — 85% becomes 29%, and the held-out decisions are not independent

**Date:** 2026-09-24
**Script:** none — this is a **two-point analysis of two stored artifacts**, and that is the point: the
measurement needed no new run.
**Artifacts:** `runs/e116_r128_40reps.json` (read-out 128, `--test 48`, 40 replicates) and
`runs/e123_r128_test480.json` (read-out 128, `--test 480`, 40 replicates). **Their configs differ in exactly one
field**, `test` — verified field by field, and the two `json_out` paths.
**Context:** `docs/paper/clfly-v1.md` §4.2 and `docs/findings/2026-09-24-the-metric-noise-is-mostly-the-substrates.md`,
which read `evaluation_noise` for the accuracy (**85% removable at read-out 128**) and for the forgetting
(**60%**) and explained the difference structurally: the forgetting is a difference of two accuracies on the same
test set, so their errors correlate and partly cancel, and *"the binomial arithmetic that governs a single
accuracy therefore overstates what a bigger test set can do for a difference of them."*

---

## 1. The pair, and the one number that changes the story

Two same-seed artifacts, ten times apart in test-set size, nothing else different:

| | test 48 (`e116`) | test 480 (`e123`) | ratio |
|---|---|---|---|
| `n_eval` | 144 | 1,440 | 10× |
| **nominal binomial sem** | 0.02109 | 0.00709 | **2.98** |
| **accuracy's per-replicate sd** | 0.02283 | 0.01963 | **1.163** |
| `evaluation_noise`'s `variance_fraction` | **0.8528** | 0.1302 | — |

The nominal sem falls by 2.98 against the 3.16 a genuinely independent tenfold set would give, so **the
binomial formula is internally consistent**. The observed sd falls by **1.16**. **That is the whole finding**:
if 85% of the accuracy's variance were sampling noise that a tenfold test set divides by ten, the sd would fall
by `1/sqrt(0.8528·0.1 + 0.1472) = 2.07×`. It fell by 1.16×.

Solving the two equations for the effective binomial sem — the one piece the pair can identify, taking the
training component as constant:

    s_eff² + t²      = 0.02283²      (test 48)
    s_eff²/10 + t²   = 0.01963²      (test 480)
    => s_eff = 0.01229   against a nominal 0.02109   (1.72x smaller)
    => effective n_eval = 144 / 1.72² = 48.9  against a nominal 144
    => achievable removable share = 0.01229² / 0.02283² = 29%  against a nominal 85%

So **the accuracy's 144 held-out decisions behave like about 49 independent ones**, and the removable share is
**29%, not 85%**. The runner's own else-branch already carried the caveat — *"a fraction above 100% is a signal,
not a number … short training, or the 144 held-out decisions are not independent"* — and this is the first time
that clause has been measured rather than invoked.

## 2. And the paper's explanation belongs to the other quantity

The sentence in §4.2 attributes the over-prediction to the **difference** of two accuracies. The measurement says
the opposite:

| quantity | nominal share at test 48 | sd fall predicted | sd fall measured |
|---|---|---|---|
| **accuracy** (`evaluation_noise`, measured directly) | **85%** | **2.07×** | **1.16×** |
| **forgetting** (solved for, assuming the √10 scaling) | 60% | 1.47× | **1.47×** |

The forgetting behaves exactly as its own decomposition says — but **that is a tautology, not a test**: the 60%
split was *solved for* by assuming the removable component falls by √10, so of course it does. What is a test is
the accuracy, whose 85% is computed directly from the binomial formula and whose predicted fall is **not**
observed. **So the binomial model fails for the single accuracy, and the correlation between two accuracies is
not the mechanism** — the mechanism is upstream of it, in the held-out decisions themselves.

## 3. The paper's `2.6×` was stitched from a second artifact, and it is wrong as arithmetic too

§4.2 said *"85% predicted a 2.6× fall and the fall was 1.47×"*. **2.6× is not what 85% predicts** — it is what
**94.7%** predicts, and 0.9467 is `runs/e102_rate_fb8_omp1.json`'s accuracy `variance_fraction` of **0.9461**.
That artifact is at **read-out 32 with five replicates**, against the **read-out 128 / forty** the 85% comes
from.

**So a sentence paired a statistic from one run with a prediction computed from another's** — the same defect as
rule 28's *"a column whose comparator is not one number"*, in prose rather than in a table, and therefore
invisible to `e105`, which reads tables, and to `e97`, which reads artifact existence. It survived because both
halves are real numbers from real artifacts and neither is wrong on its own.

Repaired in the paper and dated in the source finding. **The corrected arithmetic is 2.07×**, and the honest
sentence is one line shorter: the predicted fall is 2.07× for the accuracy (against 1.16× measured) and the
forgetting's is 1.47× *by construction*, so there is no contrast between them to report.

## 4. What this changes, and what it does not

**Changes.** §4.2's account of the noise now runs: the accuracy's *nominal* floor overstates by a factor of
three, because the effective number of independent held-out decisions is ~49 rather than 144; the forgetting's
removable component does scale as √10, but that is definitional; and **the explanation the section gives is
attached to the wrong quantity**. Two of the section's numbers change: **85% → 29%** for the achievable share,
and the **2.6× → 2.07×** prediction — with the second now computed from the artifact its share comes from.

**Does not change.** The section's *conclusion* is untouched and in fact strengthened by the correction: the
test-set route is **more exhausted** than it looked. `e119` captured 94% of the removable variance and reported
it as such; if only 29% of the accuracy's variance is removable at all, then the tenfold test set captured even
more of what was available, and the residual is even more clearly the substrate's. **The eighteenfold handicap
against the drift is intrinsic to the quantity**, which is what `e123`'s simultaneous refutation of the
granularity diagnosis says from the other direction.

## 5. What this cannot settle

- **Two points identify one parameter.** The two-point solve assumes the training component is constant between
  test 48 and test 480. That is a good assumption — the training data is identical and the seeds are identical —
  but a *third* test-set size would over-determine it and show whether the effective `n_eval` scales the way the
  solve assumes. It scales as if the held-out decisions were ~49 independent ones; **what makes them dependent
  is not measured here.**
- **It is one read-out.** `e119` also ran read-out 300; the same two-point solve there is a second measurement
  and has not been done. Read-out 32 has the largest spread on this axis and is the natural third.
- **The test sets are not provably nested**, so the two accuracies are two estimates of the same quantity on
  different samples rather than nested estimates. That is sufficient for the comparison (both are unbiased) and
  not sufficient to say anything about which items are hard.
- **`variance_fraction` above 1 is in the record and is not a defect**: `runs/e111_readout900_frozen.json`
  reports **43.06** for a frozen-body arm, where the replicates are nearly identical and the test-set floor
  dominates. The runner prints that case as *"cannot separate them"* rather than as a number, which is why the
  comprehension of this block matters beyond the one sentence corrected here.
