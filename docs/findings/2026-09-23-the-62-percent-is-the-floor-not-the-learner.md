# E71 — "62% of the variance is the learner" is the *test set's* share, and three documents state it backwards

**Date:** 2026-09-23
**Script:** `experiments/e71_variance_share_audit.py`
**Artifacts:** `runs/e71_variance_share_audit.json`, `runs/e38_variance_budget.json`, `runs/e54_naive_seed_pool.json`
**Context:** `2026-09-22-network-variance-is-learner-variability.md` (e38), `2026-09-22-naive-arm-census.md` (e54), `2026-09-22-c2-passes-the-per-seed-discipline.md` (e57)

---

## 1. The sentence, which is in three places with the same number and the same direction

The project's summary of the network line's binding axis, and the one figure that carries it:

> C2b — basis, rate network — the **learner's seeds**: **62% of the per-replicate variance is the
> learner, not the test set** (e38/e54).

It appears verbatim in `e57`'s binding-axes table, in `docs/research_plan.md`'s binding-axes
paragraph, and in the paper's retraction section — and in a fourth place, shortened to "the floor is
62% learner", alongside "the bracket is a bracket" and "the control is one draw" as one of the
project's three hard-won corrections.

## 2. The number comes from a field that says the opposite

`runs/e38_variance_budget.json` records, for every arm, a field named **`floor_share_of_variance`**:
the share of that arm's per-replicate variance accounted for by the **test set's binomial sampling
floor**. For the `naive` arm of the nine-replicate run its value is

```
naive, n = 9, sd 0.03889, binomial_floor 0.03059, floor_share_of_variance 0.619
```

**0.619.** The "62%" is the *test set's* share of the variance. The learner is what is left over, and
the same artifact has a `training_sd` for it.

So the sentence is not a rounding question or a reporting convention: it is an inverted reading of an
explicitly named field, and the number it attributes to the learner is the number for the measurer.

## 3. The decomposition, recomputed from the artifacts at both sample sizes

The floor is `sqrt(p(1−p)/n_eval)` with `n_eval` = 144 (three tasks × 48 test items) and `p` the arm's
own mean; the remainder is everything the test set cannot explain.

| pool | n | mean | sd | floor | floor share | **learner share** | learner sd |
|---|---|---|---|---|---|---|---|
| `e38` naive, nine reps | 9 | 0.8395 | 0.03889 | 0.03059 | 61.9% | **38.1%** | 0.02402 |
| `e54` pool, sixteen reps | 16 | 0.8411 | 0.04111 | 0.03046 | 54.9% | **45.1%** | 0.02761 |

**At sixteen replicates the learner contributes 45% of the `naive` arm's per-replicate spread, with a
95% interval of [0%, 77%]** propagated from the sd's own interval rather than assumed. So the honest
form is a range, not a point — and the range does not contain 62%.

## 4. And the contrast, which is the quantity the claims are actually about

The axis argument in `e38` is not made on the `naive` arm's own spread, it is made on the **paired
contrast** — `ewc-block` minus `ewc-block-rand` at λ = 0.003 / `cell_class`, nine replicates, sd 0.06118.
There the floor enters twice and independently, so its contribution is bounded by `2·floor²`:

| quantity | value |
|---|---|
| sd of the paired contrast | 0.06118 |
| its variance | 0.003743 |
| the floor's contribution, `2·floor²` (both arms) | 0.001720 |
| **binomial share of the contrast** | **45.9%** (43.3% if one arm's floor is used twice, which is what `e38` did) |
| removing 90% of it | **1.31×** (`e38` reports 1.28×) |

**So the two numbers point in opposite directions, and both are correct about their own quantity:**
measurement is the *majority* (55%) of the `naive` arm's own spread and a *minority* (43–46%) of the
contrast's. The sentence in §1 takes the arm's number and attaches it to the contrast's axis.

## 5. The corrected sentence, and why the conclusion underneath it is untouched

The claim the number was doing work for — that the C2b line's binding constraint is **seeds** — survives
its own correction, for a reason the documents state backwards:

* the test-set floor is **55%** of the `naive` arm's spread, but it is cheaply removable only to a
  point: ten times the test set divides it by `sqrt(10)`, taking 0.04111 down to **0.02924 — a 1.41×
  gain and no more**;
* the learner's share is **45%** of the arm and at least **54%** of the contrast, and more seeds remove
  it *entirely* — which is why 12–16 replicates is the answer and a bigger test set is not.

> The evaluation floor is **55%** of the `naive` arm's per-replicate variance and at most **46%** of the
> contrast's, so the learner contributes **45% of the arm** and **at least 54% of the contrast** — which
> is why seeds, not test size, is the lever.

That is a weaker statement than "62% is the learner" and a *more* useful one, because it is the
contrast's share, not the arm's, that the replicate count has to be planned against.

## 6. What this does not touch

- **`e38`'s `--test 480` bound.** Its arithmetic reproduces to within 6%: `e38` used `2·floor²` =
  0.00162 (one arm's floor twice) where using both arms' floors gives 0.00172, and the 90%-removal gain
  is 1.31× against its 1.28×. Neither the direction nor the conclusion moves.
- **`e54`'s own §3, which is right.** It reports "floor 62% of the variance, so 38% is the learner" and
  "the learner contributes 38–45%". The inversion is downstream of it, in the three summary places that
  quote the number without the field name.
- **The programme.** The replicate counts `e46` bought are planned against the contrast, where the
  measurement share is the minority — so nothing about the run plan changes.

## 7. Limits

- **The learner's share is not tightly determined.** Its 95% interval at n = 16 is [0%, 77%]; the point
  estimate of 45% should always be quoted with that. What *is* well determined is the direction, because
  the floor is computed from `n_eval` and the arm's mean and is not estimated.
- **The floor is treated as known**, which it is — it is a binomial sd at a measured accuracy — but the
  split is then a one-sided subtraction, so `rest_var` inherits whatever error the sd carries.
- **One configuration.** cs = 800, 96/48 train/test, 3 tasks, the `naive` arm for the arm-level figures
  and one λ/basis pair for the contrast. `e54` records that the arms' spreads differ from each other by
  more than the interval on this estimate, so the arm-level 45% is `naive`'s and not the benchmark's.
- **A fourth document has the correct form** (`docs/research_plan.md`'s programme-table row for `e54`:
  "floor 62% of the variance, so 38% is the learner"), which is how the inversion was caught — the same
  number stated in both directions in the same repository.
