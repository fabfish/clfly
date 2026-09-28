# The test set the benchmark would need: 165, 300 and 1096 items against the 144 in use

*2026-09-28 19:20. Runs: **none new** — `experiments/e267_the_test_set_the_benchmark_would_need.py` reads the
`evaluation_noise` block of every method-comparison artifact in the corpus (49 of them, 98 matrices), writing
`runs/e267_the_test_set_the_benchmark_would_need.json`. Seconds.*

## 1. The item: the block already holds the answer

The benchmark measures every arm's accuracy on the same **144** held-out decisions (three tasks of 48), prints the
binomial floor of that measurement beside each arm's own run-to-run spread, and says in its own note that the
test-set part is *removable* — the floor falls as `sqrt(p(1-p)/n_eval)` and enlarging the suite costs task generation
rather than training. What it never prints is **how large the suite would have to be** for a configuration to see its
own spread at all.

The two numbers the block already holds fix it: if the floor is `f` times an arm's own variance then the same floor is
reached at `n_eval * f`. So the suite a configuration would need is the size it is read at times the fraction it
carries, computable for every artifact in the record with no run at all. The census is restricted to
**method-comparison artifacts** — one carrying `naive` and at least one other arm — because a single-arm run or a
probe has no method contrast whose resolvability this prices.

## 2. What the census says

Of **49** method-comparison artifacts and **98** (artifact, metric) matrices, all at 144 items:

| replicate count | matrices | worst fraction | median | matrices with an arm at or above its own floor |
|---|---|---|---|---|
| 3 | 8 | 1.54 | 0.50 | 1 |
| 5 | 46 | 7.61 | 0.85 | **21** |
| 16 | 6 | 1.47 | 0.55 | 1 |
| 40 | 36 | 2.09 | 0.60 | **8** |
| 144 | 2 | 0.25 | 0.25 | 0 |

**S1 MET — an arm inside its own floor is not an edge case: 31 of the 98 matrices (32%) have one.** So the
readability precondition `e265` applied to the item ceiling is a property of the record and not of one run: any
reading that forms a ceiling from a pair has to check it, and a third of the record would fail that check on at least
one arm.

**S2 MET — but a whole configuration inside it is rare, and those are the configurations that cannot see themselves at
all.** Three matrices have **every** arm at or above its own floor:

| artifact | metric | n | worst fraction | suite it would need | multiple of the 144 in use |
|---|---|---|---|---|---|
| `e84_replay96_taskIL_5reps` | accuracy | 5 | **7.61** | **1096** | **7.6×** |
| `e140_r32_methods_frozenbias_40reps` | accuracy | 40 | **2.09** | **300** | **2.1×** |
| `e167_r32_noise2.0_lam3e-4` | accuracy | 40 | **1.14** | **165** | **1.1×** |

**S3 MET — and the requirement is a bounded multiple of the suite in use.** 1096 items is six times the current
suite, not an unbounded ask, and the arithmetic is exact rather than modelled: the floor scales as `1/sqrt(n_eval)`
and the block holds every term.

**The second of the three is the case `e265` found**, so this unit both generalises `e265`'s W1 — from one
configuration to three — and prices it: that configuration's own spread would become visible at 300 held-out
decisions instead of 144.

## 3. The consequence, reported and not claimed

**The fix is a task-suite regeneration and not a retraining.** The held-out samples come from the propagator over the
connectome, so a suite of 1096 items is task-generation time, not the 40 hours `e259` priced for a re-run of the
`side` rung. That is the direction the benchmark's own note calls cheap, and it is the one thing here that would
change what the *method* line can claim: a configuration whose entire run-to-run spread sits inside its test-set floor
cannot support a comparison between methods at that budget, whatever the arms' means do.

**One caveat on the largest requirement.** `e84_replay96_taskIL_5reps` has five replicates, so its spread is
estimated on four degrees of freedom and the 7.61 fraction inherits that noise — the 1096-item figure is the
requirement *if* the spread it measured is the true one, and a re-run at a larger budget is the only thing that would
settle it. The other two are at forty replicates, where the estimate is firmer.

## 4. What it cannot do

The fraction is the model's own split of each arm's variance and inherits its assumption that the held-out decisions
are independent, which the benchmark's own print flags when a fraction exceeds 100%. `n_eval * f` is the size at which
the floor **equals** the spread, so a configuration would want more than that to resolve anything above it. The census
is over artifacts that record an `evaluation_noise` block, so a run without one is invisible rather than fine, and the
methods filter is by the arm names this corpus uses, so a differently-named control is invisible. And nothing here
enlarges a suite or checks that a larger one would be generated the same way — the cost of the fix is a claim about
the generator, not a measurement.
