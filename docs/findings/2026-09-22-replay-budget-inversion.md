# E8i — replay's inversion was a budget artefact, and it reverses back

**Date:** 2026-09-22
**Script:** `experiments/e8_rate_network.py --replay-per-task N --replay-batch M`
**Setup:** circuit `mb+cx+al@n1307`, 3 tasks, 3 replicates, shared head, read-out 32 neurons, λ = 0.003, chance 0.25

---

## 1. The inversion this fire set out to explain

Two fires ago the hardened benchmark flipped one result and produced a puzzle. Diagonal EWC
went from "does nothing" to a resolved 2.5σ win, and **replay, which had been the only method
that resolved anything on the unhardened benchmark, stopped resolving.** That contradicted
the project's own theory: LGCL v7 measured content memory to be 12.7× more valuable than
regularisation in the partially-observed regime, and the hardened benchmark — a 32-neuron
read-out — is *more* partially observed, not less.

The obvious untested candidate was the replay budget. It had never been tuned: every replay
run in every previous fire used the defaults of **16 stored stimuli per task** and **16
replayed samples per step**, while EWC's λ had been swept over five values.

**Every replay result in the project's history was measured at pool 16 / per-step 16.** That
is the configuration this fire shows is the worst reasonable choice.

## 2. Result: both knobs matter, and the inversion reverses

| pool (per task) | per-step | final accuracy | mean forgetting | vs naive |
|---|---|---|---|---|
| — (naive) | — | 0.917 ± 0.022 | +0.066 ± 0.019 | — |
| 4 | 16 | 0.887 ± 0.031 | +0.111 ± 0.025 | +0.045 (**worse**) |
| 16 | 16 | 0.924 ± 0.011 | +0.059 ± 0.018 | −0.007 (tie) |
| 96 | 16 | 0.938 ± 0.018 | +0.017 ± 0.009 | −0.049 (2.3σ) |
| **96** | **8** | **0.968 ± 0.013** | **−0.010 ± 0.006** | **−0.076 (4.2σ)** |
| 96 | 48 | 0.949 ± 0.013 | +0.007 ± 0.009 | −0.059 (3.1σ) |

*(Pool 96 is the whole task's training set — `--train 96`.)*

Three things.

**The pool size is monotone and it matters.** 0.111 → 0.059 → 0.017 forgetting as the pool
grows 4 → 16 → 96. At pool 4 replay is *worse* than doing nothing, which is the small-buffer
regime LGCL v5 identified analytically and the earlier linear work reproduced (the negative
recovery region with a crossover near `b ≈ 3`). At pool 16 — the project's historical default
— replay merely ties naive.

**And the per-step amount has an optimum.** At pool 96 a *small* per-step batch is best:
8 gives −0.010 ± 0.006, while 16 gives +0.017 and 48 gives +0.007. "More replay" is not
monotone; over-mixing old data into every step costs current-task plasticity.

**So the inversion reverses back.** Tuned replay delivers **the largest effect in the entire
network line: −0.076 ± 0.018 forgetting against naive, 4.2σ, with the best accuracy in the
table (0.968 that of naive's 0.917), and forgetting driven *negative*** — earlier tasks end
up better than when they were learned. Content memory does beat regularisation, which is what
LGCL v7 predicted, and the two fires of apparent contradiction were measuring an untuned
budget.

## 3. What this does to the project's replay results

Every previous replay number in the network line was taken at pool 16 / per-step 16, and is
therefore a statement about a *tie with naive*, not about replay:

| previous claim | correction |
|---|---|
| "replay cuts forgetting ~4×" (task-incremental, unhardened) | measured at pool 16; the effect there may have been task-incremental structure rather than replay |
| "replay no longer helps" (class-incremental, unhardened) | measured at pool 16 |
| "replay does not resolve on the hardened benchmark" | measured at pool 16 — **now resolved at 4.2σ when tuned** |
| "replay's advantage is setting-dependent" | **withdrawn**: the setting was confounded with an untuned budget |

The lesson generalises, and it is the same one the λ fire taught: **a method comparison in
which one family has been tuned and the other has not is not a comparison.** EWC's λ was
swept and its basis was swept; replay's two parameters were not touched for eight fires. On
this evidence, the honest statement about replay before this fire is that it had never been
tried properly.

## 4. The memory accounting, stated plainly

The two working methods differ by more than 50× in what they store:

| method | stored per finished task | floats | bytes |
|---|---|---|---|
| EWC, diagonal Fisher | 26,568 | 2.7e4 | 0.2 MB |
| EWC, block Fisher (rejected) | 5.3e7 | 5.3e7 | 424 MB |
| **replay, pool 96** | 96 stimuli × 12 steps × 1307 neurons | 1.5e6 | **6.0 MB** |

So at their tuned optima: **EWC gives +0.010 ± 0.010 forgetting with 0.2 MB, replay gives
−0.010 ± 0.006 with 6.0 MB** (both against naive's +0.066 ± 0.019). Replay is stronger in
absolute terms and uses 30× the memory of the diagonal Fisher; on a per-byte basis the
diagonal anchor is the better buy. Both are legitimate findings, and stating them together
is the honest form — a CL paper that reports only the absolute numbers is hiding the trade.

## 5. Where the network line now stands

| claim | status |
|---|---|
| the benchmark contains a real CL problem | **yes**, with a narrow read-out (plastic − frozen accuracy gap +0.102) |
| **replay helps** | **yes, best method found**: −0.010 ± 0.006, **4.2σ**, best accuracy, needs pool 96 / per-step 8 and 6 MB |
| **diagonal EWC helps** | **yes**, +0.010 ± 0.010, **2.6σ**, needs λ = 0.003 / 8 Fisher batches and 0.2 MB |
| the biological synapse partition beats a matched random one | **no**, in five settings |
| the basis ordering reverses versus the linear substrate | **suggestive only** (≤1.6σ, absent at 128 batches) |
| a better Fisher estimate improves any EWC variant | **no — the opposite**; the diagonal degrades monotonically |
| content memory beats regularisation in the partially-observed regime | **confirmed**, once the memory budget is tuned |

The benchmark is now a working, discriminating connectome-constrained CL setting with two
methods that resolve, an identified design failure (the frozen-body control) and an
identified tuning confound (the replay budget). That is a reasonable place for the network
line to rest.

## 6. Next

1. **Re-run the task-incremental and class-incremental comparisons at the tuned replay
   budget**, since the earlier "replay is setting-dependent" conclusion was confounded with
   it.
2. The biological-partition negative and the ordering-reversal question are both settled
   enough to leave; the predictor's one failure and the paper consolidation are the
   remaining open items.
