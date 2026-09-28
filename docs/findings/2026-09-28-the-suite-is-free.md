# The suite is free: a held-out decision costs less than the noise of a thirty-second run

*2026-09-28 19:50. Runs: **two, one replicate each** — `e8_rate_network` at cs 300 with `--methods naive --repeats 1`
and everything else fixed, run once with `--test 48` and once with `--test 366`, so the suites are 3 × 48 = **144**
decisions (what the whole corpus reads at) and 3 × 366 = **1098** (`runs/e269_suite144_1rep.json`,
`runs/e269_suite1098_1rep.json`). Fifty seconds of machine time in total, plus
`experiments/e269_the_price_of_a_held_out_item.py` (`runs/e269_the_price_of_a_held_out_item.json`).*

## 1. The item: a cost that was reported instead of measured

`e267` turned the benchmark's own noise block into the suite each configuration would need, found **three** that cannot
see their own spread, and reported rather than claimed that the fix is a task-suite regeneration and not a retraining —
"the cost of the fix is a statement about the generator and not a measurement". This module makes it a measurement,
with the smallest pair of runs that can make one: the same configuration twice, one replicate of one arm each, differing
in `--test` alone.

| run | held-out decisions | test per task | train per task | clock |
|---|---|---|---|---|
| `e269_suite144_1rep` | **144** | 48 | 96 | **30.47 s** |
| `e269_suite1098_1rep` | **1098** | 366 | 96 | **23.38 s** |

**1098 is the suite the worst of `e267`'s three configurations needs** (it computed 1096, from a fraction of 7.61), so
this pair is the case that matters and not a proxy for it.

## 2. The registered claims (T1-T3, all MET)

| claim | what it says | measured |
|---|---|---|
| **T1** | the larger suite is real and the runner records it | `n_eval` 1098 against 144, test per task 366 against 48, **training unchanged** at 96 per task, everything else equal |
| **T2** | and the extra decisions cost less than the difference between the two clocks | 954 extra decisions; the clocks are 30.47 s against 23.38 s, so the **larger suite ran faster** by 7.08 s — charging the whole difference to those decisions prices one at **0.0074 s** |
| **T3** | so the suite costs under 1% of a real run | the extra decisions charged the whole 7.08 s are **0.25%** of the 47 minutes a real sixteen-replicate four-arm run of that cell takes |

**The honest reading of T2 is a bound and not an estimate.** The larger suite ran *faster*, which cannot be the extra
work; it is machine noise between the two runs. So the difference is charged to the extra items in the conservative
direction — the whole 7.08 s — and even that prices a decision at under a hundredth of a second. The sign of the
difference is itself the finding: **954 extra decisions are smaller than one run's worth of noise.**

## 3. What follows

**The benchmark's 144-item floor is not a cost constraint.** The suite is generated with the training data in one pass
by the propagator, and evaluating more held-out decisions is free next to the training that produced them: the three
configurations `e267` found could be re-run with the suites they need for **under 1% of the clock** of the runs they
are already part of. That turns `e267`'s consequence from "the fix is cheap in principle" into "the fix is free in
practice", and it moves the binding cost of this line where it belongs — on training, which is why `e259` priced a
219.5-replicate re-run of the `side` rung at **40.5 hours** while the whole of this unit cost fifty seconds.

## 4. What it cannot do

**Two single-replicate runs give one timing draw each**, so the difference has no error bar and T2's bound is a bound:
a second pair would price the decision properly rather than bracketing it. The test items are generated in the same
pass as the training data, so an item's marginal cost is not separable from the setup both runs pay — which is exactly
why the measured difference is the honest quantity and an extrapolated per-item rate is not. **1098 items is the
requirement of the worst of three configurations and not of a suite forty times larger**, so nothing here says a much
larger suite stays free; and the runs carry **one arm**, while a four-arm run evaluates the suite four times over,
which is the direction that would show a cost.
