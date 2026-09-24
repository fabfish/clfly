# The aggregate and the newest task's accuracy are complements by construction, not by luck — and this metric is a lower bound on the literature's

**Date:** 2026-09-24
**Script:** `experiments/e154_retention_matrix_audit.py` — **an audit, no runs**, over every artifact that carries
a retention matrix: **129 artifacts, 243 method-arms, 486 forgetting terms**. Artifact written:
`runs/e154_retention_structure.json`.
**Why it exists:** two of today's findings recommend the newest task's accuracy as a column and call the
aggregate one-sided. Both claims were argued from *measurements*; this asks whether they are instead *structural*,
by reading what the runner computes and then checking it on the corpus rather than on the reading.

---

## 1. Three identities, holding to the last digit

| identity | worst difference | verdict |
|---|---|---|
| `learned[j] == R[j, j]` (the diagonal) | **0** | holds over all 243 method-arms |
| `learned[T-1] == final_per_task[T-1]` | **0** | holds over all 243 |
| **`forgetting_per_task[j] == learned[j] - final_per_task[j]`** | **0** | holds over all 243 |

**The third one is the interesting one, and it is not obvious from the code.** The runner computes
`nanmax(R[: j+1, j]) - R[T-1, j]` — a **max over checkpoints 0..j** — which *looks* like the standard
"best accuracy the task ever had" form. But the matrix is filled for `j <= k` only, so in column `j` the rows
`0..j` contain **exactly one finite entry: the diagonal**. The window is therefore decorative, and what the
project calls forgetting is precisely

    forgetting_per_task[j] = (accuracy right after learning task j) - (accuracy at the end)

i.e. **acquisition minus final**, for `j < T-1`.

## 2. What that makes each printed number

| printed quantity | what it is | can it contain interference? |
|---|---|---|
| `mean_forgetting` | **pure retention** — the mean of `learned[j] - final[j]` over the first `T-1` tasks | yes, entirely |
| the **newest task's accuracy** | **pure acquisition** — identical to the diagonal, because nothing is trained after it | **no, by construction** |
| `final_accuracy` | a **mixture** — `T-1` retention terms and one acquisition term | partly |
| `learned[j]` for `j < T-1` | the acquisition point of a task that was later interfered with | no — but it is not a final value either |

**So the column §8 item 7 recommends and the aggregate it recommends it beside are complements by
construction**: one is the mean of the retention terms, the other is the acquisition term those terms are
measured *from*. That upgrades the empirical statement of the two findings that used it — "the aggregate cannot
show what the constraints cost" is true of the aggregate **for a structural reason**, and no re-weighting of it
can recover the column.

## 3. And the metric is a lower bound on the conventional one

The continual-learning literature's accuracy forgetting takes the max over the **later** checkpoints,
`nanmax(R[j:, j]) - R[T-1, j]`, which can only be **larger** than this record's diagonal form. The gap is a
measurement, not an argument:

| `nanmax(R[j:, j]) - R[j, j]`, over **5,762** (task, replicate) observations | |
|---|---|
| strictly positive | **15.2%** of them |
| mean | **0.00449** |
| median | 0.00000 |
| 90th percentile | **0.02083** |
| max | **0.10417** |

**So every forgetting number in this paper is a lower bound on the statistic a reader from the continual-learning
literature would compute**, by up to 0.104 on a single (task, replicate) and 0.021 at the 90th percentile, on
15% of observations. A three-task benchmark with three checkpoints is exactly the setting where a later
checkpoint can beat the diagonal, and it does so on one task in seven.

**This is a fact about the *definition*, not about any result**: the paper's contrasts are all computed the same
way on both sides, so no comparison inside it moves. What moves is a comparison *across papers* — and the honest
sentence is that the numbers here are the diagonal form, and that the conventional form would be larger.

## 4. And the loss-valued metric uses the *other* convention, which this audit also measures

The two forgetting metrics in this project are not mirrors of each other in their windows:

| metric | its expression | the window does what? |
|---|---|---|
| accuracy forgetting | `nanmax(R[:j+1, j]) - R[T-1, j]` | **decorative** — the filled matrix makes it the diagonal |
| loss forgetting | `L[T-1, j] - nanmin(L[j:, j])` | **load-bearing** — `min` over all **later** checkpoints |

And the second window is not decorative in practice: over **3,060** observations,
`L[j, j] - nanmin(L[j:, j])` is **off-diagonal in 5.8%** of them (mean gap **0.000234**, max **0.00651**), i.e.
in one observation in seventeen a *later* checkpoint has a lower training loss on task `j` than the checkpoint
that trained it. **So of the project's two metrics, the accuracy one is the diagonal form and the loss one is
already the conventional form** — a convention mismatch between two quantities the paper sometimes quotes side by
side. `e123` had measured that the loss form is unaffected by its window *on one configuration*; over the corpus
it is affected in 5.8% of observations, and the effect is small (5.8% × 2.3e−4 mean).

## 5. What this cannot settle

- **It does not say the diagonal form is wrong.** It is a choice, and `e123`'s docstring records that the
  alternative accuracy window was measured to differ (up to 0.0073 per replicate, 0.00057 on the mean) — this
  audit re-measures that gap over the whole corpus rather than one configuration and finds it positive in 15.2%
  of observations.
- **The 5,762 observations are not independent**: 129 artifacts hold 243 method-arms and many share seeds, and
  the distribution is heavily zero-inflated (median 0), so the mean is not a summary of a typical case — the
  share and the percentiles are.
- **It says nothing about *which* tasks have their peaks later**: the peak's timing is a separate question,
  reported here only in aggregate, and a per-task breakdown would be the next step if a claim needed it.
- The corpus it reads is **the artifacts that exist**, which is the C2b network line at one read-out and three
  tasks; the identity is structural (it follows from the fill pattern) but the 15.2% and 5.8% are measurements of
  *this* benchmark's dynamics.
