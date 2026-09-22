# E8j — the network line, settled: content memory wins across settings, regularisation wins narrowly

**Date:** 2026-09-22
**Script:** `experiments/e8_rate_network.py` (all settings, tuned hyperparameters)
**Setup:** circuit `mb+cx+al@n1307`, 3 tasks, 3 replicates, chance 0.25, λ = 0.003, 8 Fisher batches, replay pool 96 / per-step 8

---

## 1. Why this run closes the question

Two fires ago the project concluded that "replay is setting-dependent" — it resolved on the
task-incremental benchmark and not on the class-incremental one. The last fire showed that
conclusion was confounded: **every** replay result in the project's history had been taken at
16 stored stimuli per task and 16 replayed samples per step, which merely ties naive. EWC's λ
had been swept; replay's two parameters had never been touched.

This fire re-runs the three settings with **every method tuned**: λ = 0.003 and 8 Fisher
batches (EWC's best from the hardened sweeps), replay at pool 96 / per-step 8 (its best).

## 2. The table

| setting | method | final accuracy | mean forgetting | vs naive |
|---|---|---|---|---|
| **task-IL**<br>*(per-task heads)* | naive | 0.824 ± 0.036 | +0.101 ± 0.049 | — |
| | EWC, diagonal | 0.824 ± 0.046 | +0.128 ± 0.061 | +0.027 (worse) |
| | **replay** | **0.921 ± 0.015** | **−0.056 ± 0.009** | **−0.157 (3.1σ)** |
| **class-IL**<br>*(shared head, whole state)* | naive | 0.928 ± 0.016 | +0.059 ± 0.028 | — |
| | EWC, diagonal | 0.912 ± 0.016 | +0.063 ± 0.010 | +0.004 (tie) |
| | **replay** | **0.975 ± 0.006** | **−0.010 ± 0.016** | **−0.069 (2.2σ)** |
| **class-IL, hardened**<br>*(shared head, 32-neuron read-out)* | naive | 0.917 ± 0.022 | +0.066 ± 0.019 | — |
| | **EWC, diagonal** | 0.926 ± 0.020 | **+0.010 ± 0.010** | **−0.056 (2.6σ)** |
| | **replay** | **0.968 ± 0.013** | **−0.010 ± 0.006** | **−0.076 (4.2σ)** |

## 3. What it settles

**Replay resolves in all three settings** — 3.1σ, 2.2σ, 4.2σ — always with the best accuracy
and always with forgetting driven **negative**, i.e. earlier tasks end up better than when
they were learned. The "setting-dependent" claim is **withdrawn in full**: at a tuned budget,
content memory is robust across tasks-incremental and class-incremental, hardened or not.

**EWC resolves in exactly one setting** — the hardened class-IL — and is *worse than naive* on
task-IL (+0.027). Its usefulness is narrow and it requires the plastic weights to be
load-bearing, which is the condition the previous fires established ('a benchmark whose
frozen-body control matches its trained accuracy contains no CL problem'). On the two settings
where the body is not load-bearing, the diagonal anchor does nothing.

**Replay beats EWC wherever both work** — 4.2σ against 2.6σ on the hardened configuration, and
on the other two settings replay resolves while EWC does not.

**And this is what the project's theory predicted.** LGCL v7 measured content memory to be
**12.7× more valuable than regularisation** in the partially-observed regime, and every one of
these tasks is partially observed by construction (each drives a small input population, so its
measurement is low-rank). The prediction was that replay should dominate, and after eight fires
of not having tuned replay, it does.

## 4. The memory trade, which no CL paper should omit

At their tuned optima:

| method | stored per finished task | floats | bytes | forgetting on class-IL-hard |
|---|---|---|---|---|
| EWC, diagonal Fisher | 26,568 | 2.7e4 | **0.2 MB** | +0.010 ± 0.010 (2.6σ vs naive) |
| replay, pool 96 | 96 × 12 × 1307 | 1.5e6 | **6.0 MB** | −0.010 ± 0.006 (4.2σ vs naive) |

Replay is stronger in absolute terms and uses **30× the memory**. Per byte the diagonal anchor
is the better buy. Both statements are true and a comparison that reports only the first is
hiding the trade.

## 5. The network line in one paragraph

A connectome-constrained rate network with the fly's sign pattern as a fixed mask and 27k
trainable synapse strengths, three behavioural tasks on distinct circuits, ~0.92–0.97 accuracy
against 0.25 chance. On it: **replay (96 stored stimuli per task) reduces
forgetting to zero or below in every setting tested, at 2.2–4.2σ; a diagonal-Fisher EWC penalty
helps only when the read-out is narrow enough to make the plastic weights load-bearing, at
2.6σ; the biological synapse partition never beats its size-matched random control; and a
better-estimated Fisher makes EWC worse, not better.** The honest caveats are the 30× memory
asymmetry, the one narrow setting in which EWC works at all, and the fact that eight fires of
earlier network conclusions were measured with one method's hyperparameters swept and the
other's untouched.

## 6. What remains

1. **The predictor's one failure** — on heavily rewired wiring the biological-vs-random sign is
   called wrongly with a large margin, in the linear substrate. That is the last open question
   with a specific, answerable form.
2. **Paper consolidation.** The draft's §4.6 needs to carry this table, and §7's limitations
   need the memory asymmetry and the hyperparameter-tuning lesson.
