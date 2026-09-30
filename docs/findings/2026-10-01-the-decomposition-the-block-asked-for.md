# The decomposition the block asked for: the corpus stores half of its own forgetting, and the half it cannot see is the larger one

*2026-10-01 05:12. Runs: **none new** — `experiments/e304_the_decomposition_the_block_asked_for.py` reads every arm's
`retention` matrix through the new `clfly/lgcl/metrics.py`, writing
`runs/e304_the_decomposition_the_block_asked_for.json`. Seconds.*

## 1. The module the note deferred to did not exist

`e303` found that `clfly/lgcl/model.py`'s `summarize` ends with a note saying the conventional forgetting metric
*"rewards shrinkage bias"* and to *"use `clfly.lgcl.metrics.decompose_forgetting` when that matters"* — and that
`clfly/lgcl/metrics.py` was not on disk. **This unit writes it and asks the question the block's own reason implies.**

It can be asked because the corpus records more than the conventional measure. Every arm artifact carries a
lower-triangular **`retention`** matrix `R[t][j]` — the accuracy on task `j` right after the arm finished task `t` —
so for every task the level it reached (`R[j][j]`) and the level it ended at (`R[T-1][j]`) are both on disk, and the
shortfall against 1.0 splits **exactly and with no free parameter**:

```
1 - R[T-1][j]  =  (1 - R[j][j])  +  (R[j][j] - R[T-1][j])
   shortfall         unlearned            lost
```

**D1 MET — the split is exact.** Over **5581 arm-replicates on 301 arms** the largest residual is **0.0e+00**: not
small, zero, because both terms are differences of the same two recorded numbers. No arm was refused; all 301 carry a
matrix the reader can use.

## 2. The corpus already stored the lost term, and called it forgetting

**D2 MET, and exactly.** The stored `forgetting_per_task` equals the lost term in **every** arm-replicate and task, to
0.0e+00. So the conventional measure is not a *different* quantity from the one this unit computes — **it is half of
it**, and it is the half that only exists for a task the arm actually learned.

## 3. And the half it cannot see is the larger one

**D3 MET.** The median arm's shortfall is **59.7%** tasks it never learned and **40.3%** tasks it learned and lost.

## 4. The exhibit: what "no forgetting" looks like

**D4 MET.** Over the 301 arms, the rank correlation between the stored `mean_forgetting` and the arm's unlearned
share is **−0.751**: the arms the metric scores as forgetting least are the arms that learned least.

| what the metric says | arm | `mean_forgetting` | unlearned share | lost |
|---|---|---|---|---|
| **best** | `e135_r32_methods_plastic.json` / `replay` | **−0.01250** | **1.261** | −0.00833 |
| **best** | `e61_replay96_step8.json` / `replay` | **−0.01250** | **1.261** | −0.00833 |
| **best** | `e135_r32_methods_frozenbias.json` / `ewc` | −0.01042 | 1.085 | −0.00694 |
| worst | `e96_fisher_batches_128_1seed.json` / `ewc-block` | 0.27083 | 0.212 | 0.18056 |
| worst | `e177_probe_cs300_side_1rep.json` / `naive` | 0.26042 | 0.286 | 0.17361 |

The top row is the sharpest thing in this line's metric work: **eleven of the 301 arms have a negative lost term** —
they got *better* on the tasks they had learned, which is backward transfer — and their unlearned share therefore
exceeds one, because the whole shortfall is tasks they never had. `replay`'s −0.0125 is not a claim that it forgets
nothing; it is a claim that it **forgets nothing it ever knew**, over a shortfall two thirds of which it never knew.

That is the block's sentence — *the conventional forgetting metric rewards shrinkage and can be gamed* — measured
rather than asserted: not as an argument about what a metric *could* do, but as a rank correlation of −0.751 over
301 arms, with the metric's own best score belonging to arms whose lost term is negative.

## 5. What it cannot do

**The decomposition is of the shortfall against a ceiling of 1.0**, so a task's chance level counts as never learned.
That is the reading this unit wants — chance performance is nothing learned — and it is not the only one available; a
caller who wants chance-relative terms can pass a `ceiling` and the split stays exact. **`R[j][j]` is the level right
after task `j` was learned**, so a task that was unsolved then and improved later reads as unlearned even though the
arm ended higher; that is a property of what the runner records and not of this unit. **The arms are not
independent** — the same configuration recurs across runs, so a correlation over 301 arms is a description of the
corpus and not an estimate with a sampling error, and D4's magnitude should not be read as one. **And this is not
LGCL's decomposition**: LGCL separates an irreducible drift term from estimation degradation against a reference
estimator, which no artifact carries for its own arms, so what is split here is a *different* decomposition of the
same shortfall — exact, computable everywhere, and honest about being a proxy for the pair the block names.
