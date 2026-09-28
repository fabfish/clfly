# One configuration does not fix the ordering: `e265`'s unrecorded setting was sampling noise

*2026-09-28 21:25. Runs: **two, now landed** — `e8_rate_network` at cs 300 with `--readout-size 32 --shared-head
--basis side --lam 1.0 --fisher-batches 32 --support 80 --repeats 16 --methods naive,ewc,ewc-block,ewc-block-rand`,
twice, differing in `--seed0` alone (`0` against `100`), at `runs/e266_matched_side_seed0_16reps.json` and
`runs/e266_matched_side_seed100_16reps.json`; 47 minutes each. Read by
`experiments/e266_matched_settings_read.py` (`runs/e266_matched_settings_read.json`).*

## 1. What the pair was bought for

`e265` found that the ordering `e264` read over the corpus does not reproduce — the pair that differs only in its
basis leads in 21 of 50 readable matrices — and read that disagreement as an **unrecorded setting**, because three of
the five `fb8` runs name thread counts no artifact records, while the corpus's one fixed-settings repeat
(`e153`/`e159`) is bit-identical and so gives no disagreement and no power. **The alternative was that a correlation
at sixteen replicates is too noisy to order three pairs**, and the corpus could not separate the two. So two runs of
one configuration were made, differing in `seed0` alone, with the environment recorded and **four** arms — the plain
`ewc` arm at sixteen replicates for the first time in this neighbourhood.

**The pair answers it, and the answer is the alternative.**

## 2. The result (M1's falsifier fired)

| run | accuracy | forgetting |
|---|---|---|
| `seed0 0` | `naive`-`rand` **0.596** > `ewc-block`-`rand` 0.473 > `naive`-`ewc` 0.409 | `naive`-`rand` **0.562** > `naive`-`ewc` 0.394 > `ewc-block`-`rand` 0.364 |
| `seed0 100` | `ewc-block`-`rand` **0.589** > `naive`-`rand` 0.090 > `naive`-`ewc` −0.168 | `ewc-block`-`rand` **0.573** > `naive`-`rand` 0.026 > `naive`-`ewc` −0.303 |

The basis pair sits at **rank 1 and rank 2** in the first run and at **rank 0 in both metrics** in the second. **One
configuration, two seeds, three orderings.**

**M2 MET, and it is what makes M1's failure informative**: every pair's two correlations differ by **less than the 95%
band of the Fisher transform** — deltas of 0.116, 0.577 and 0.506 on accuracy against bands of 0.765, 0.981 and 0.901,
and 0.209, 0.697 and 0.535 on forgetting against 0.818, 0.990 and 0.925. So the two runs are **consistent with each
other while ordering the pairs differently**: the differences are noise-sized and the ordering is not resolved at this
budget. That is the mechanism `e265` was missing, and it was available all along — **a 16-replicate correlation has a
standard error near 0.25, which is larger than the gaps it is being asked to rank.**

**And the corpus's best-powered estimate of the same cell family agrees with the smaller ones being draws**: the
144-replicate matrix reads the basis pair at **0.317** on accuracy and **0.282** on forgetting, *below* both
sixteen-replicate estimates (0.473–0.589 and 0.364–0.573).

## 3. The other three claims

**M3's falsifier also fired, and it retires a reading of its own.** The pair that shares the **penalty form only**
(`ewc` against `ewc-block`) is above both naive pairs in the second run (0.433 against −0.168 and 0.090) and **not** in
the first (0.478 against 0.409 and **0.596**) — so the penalty form is not a property of the arm and the question
`e264`/`e265` left open cannot be settled at sixteen replicates either. **The plain `ewc` arm is here at sixteen and it
says the same thing the basis pair does: the statistic is a draw at this budget.**

**M4 MET — the ceiling device applies at this cell.** Every arm's test-set floor sits below its own spread in both runs
(fractions 0.06 to 0.52), unlike the frozen-bias configuration `e265` found, so the item ceiling can be formed and the
excesses above it are readable: the penalty-only pair's excess is +0.048 on accuracy in the first run and +0.170 in the
second, against naive pairs within ±0.02 of their ceilings in the second.

## 4. What this does to `e265`

**It removes `e265`'s mechanism and keeps its finding.** The two runs were made precisely to separate "an unrecorded
setting" from "sampling noise", and they come out for sampling noise: a fixed setting is not a fixed ordering at this
budget. `e265`'s W2 — over 50 readable matrices the basis pair leads 21 times, middle 14, lowest 15 — therefore stands
as the right reading of the corpus, and its W3 (`one configuration, no single ordering`) stands too, with its
**attributed cause corrected**: the `fb8` group's disagreement does not need a changed thread count to explain it.
The unrecorded-setting observation itself remains true — the `fb8` artifacts record no thread count — it is simply not
what moved the ordering.

## 5. What it cannot do

**Two seeds are two draws.** The pair shows that ordering is unresolved at sixteen replicates on this cell; it does not
estimate the budget at which it would resolve, which needs more seeds than two. Both runs share the machine, the torch
version and the thread count, so neither can see an environmental change — a *fixed* setting is not a *recorded* one,
and only the environment block makes it the second. The one-directional M3 was tested on one cell. And the pair is at
cs 300 with λ 1.0, the cell of the corpus's best-powered matrix, so nothing here says a **larger** budget behaves the
same way: `e178`'s own 0.317 is a single 144-replicate draw of the quantity the two runs disagree about.
