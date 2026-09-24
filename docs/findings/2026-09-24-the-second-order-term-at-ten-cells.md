# The second-order term at ten cells: a rank correlation built out of cell means that are mostly zero

**Date:** 2026-09-24
**Script:** `experiments/e156_channel_resolved_ordering.py`, **extended with the second-order forms** — analysis
only. Artifact: `runs/e156_ordering.json` (regenerated).
**Artifacts read:** the same two five-method runs as the first-order test (`e140` plastic and frozen), forty paired
seeds each, so the ten cells are identical and the comparison is like for like.
**Why it is worth a unit:** `e109` established that the **second-order** term (`d'Hd` by exact double backward)
does not order the forgetting, on one configuration, and this project has quoted that negative ever since. The
five-method table has now been run twice, so the same statistic can be asked of **ten** cells instead of one — and
the answer is not "the term fails to order" but something sharper about how the question has to be asked.

---

## 1. The same statistic, eight forms, ten cells

| form | Spearman ρ | p | pairwise | **cells whose own value resolves from zero at 2σ** | median σ from zero | ρ with any one cell removed |
|---|---|---|---|---|---|---|
| **`whole_body`** (θ+bias, first order) | **+0.927** | 1.1e−4 | 41/45 | **10 of 10** | **11.80σ** | +0.900 .. +0.950 |
| θ-only (first order) | +0.721 | 0.019 | 36/45 | — | — | — |
| bias-only (first order) | +0.679 | 0.031 | 27/45 | — | — | — |
| `whole_body`, task 1 | +0.952 | 2.3e−5 | 42/45 | — | — | — |
| **`quad_exact`** (second order) | **+0.564** | 0.090 | 33/45 | **2 of 10** | **1.21σ** | **+0.400 .. +0.867** |
| `curvature_exact` | +0.612 | 0.060 | 35/45 | — | — | — |
| `quad_fd01` (finite difference 0.01) | +0.709 | 0.022 | 34/45 | — | — | — |

**The two rows that matter are the first and the fifth, and what separates them is not the correlation
coefficient.** The first-order form computes its ρ over ten cells whose own values are resolved from zero at a
median of **11.8σ**; the second-order form computes its ρ over ten cells whose median resolution is **1.21σ**, with
**only 2 of the 10 resolved at all** (plastic `naive` at 2.29σ and plastic `ewc-block` at **2.96σ**). **Removing
any single cell moves the second-order ρ between +0.400 and +0.867**; removing any single cell moves the
first-order ρ between +0.900 and +0.950.

**And the cell that carries most of it is the one that cannot be measured.** Plastic `ewc-block-rand` has
`quad = 5.43` where every other cell is between −0.13 and 0.98 — and its own sem is **3.78**, i.e. **70% relative**
and **1.44σ from zero**. The per-cell relative sems across the ten run from **34% to 366%**, median about **82%**.

## 2. So `e109`'s negative is confirmed, and its mechanism is now measured

`e109` reported that the second-order term does not order the forgetting on one configuration. **At ten cells it is
worse than every first-order form (+0.564 against +0.927, +0.721, +0.679), and the reason is not that the term is
anti-correlated — it is that its per-cell estimate is too noisy for any rank statistic over cells.** A ρ of +0.56
computed from eight cells that cannot be distinguished from zero is not a weak ordering; it is an ordering of
noise, and the same arithmetic would have produced a similar number from cells that contain no signal at all.

**That is a statement about the instrument and not about the mechanism**, and it is the honest form of the
negative: *the second-order term's per-cell uncertainty (34–366% relative) makes the ten-cell rank correlation
uninformative, so `e109`'s failure is not evidence that the curvature carries nothing — it is evidence that this
measurement of it cannot see anything smaller than itself.*

## 3. And it produced rule 43

**A rank statistic over cells is uninterpretable unless the cells' own values are resolved**: the coefficient must
be printed with the count of cells resolved from zero and with the leave-one-out range, because a ρ is a function
of the inputs and this project prints the coefficient without them. **This is the same defect rule 40 names one
level up** — 40 requires a dominance claim to carry its pairwise resolutions, this requires a rank correlation to
carry its *inputs'* resolutions — and it was nearly missed here: the first draft of this finding said *"the
second-order term orders the cells at +0.564, weaker than the first-order forms"*, which reads like a result about
curvature and is really a result about the sem.

## 4. What this cannot settle

- **It does not say the second-order term carries nothing.** It says the ten-cell estimate of it is dominated by
  its own noise; a configuration with more seeds, a larger quadratic signal or a lower-variance estimator would
  test the mechanism, and none of those exists here.
- **Ten cells, one suite, one statistic**: Spearman over non-independent cell means, and the leave-one-out range is
  the honest interval rather than a sampling distribution.
- **The `fd_0.01` variant's higher ρ (+0.709) is not evidence for it**: a finite-difference estimate with a step
  ten times larger than `fd_0.001` trades the truncation error for a smoothing that also shrinks its spread, and
  this script does not compute its per-cell precision — so it is quoted as a *third* second-order form and not as
  the better one.
- And the first-order forms' own caveats stand as they were written: ten non-independent cells, one read-out, and
  the θ-only form orders *worse* rather than not at all.
