# E23 — the C4 interference prior's significance was overstated by a factor of 83, and the design has a hard floor

**Date:** 2026-09-22
**Script:** `clfly/bench/analytic.py` (`task_permutation_test`), `experiments/e7_interference.py` (now reports it)
**Artifacts:** `runs/e7_interference.json` (re-analysed), `runs/e23_e7_permcheck.json` (wiring)

---

## 1. The claim and the problem with its test

C4's surviving result is that **the propagated representation predicts interference at
ρ = +0.939**, leave-one-out [+0.917, +0.983], and that the anatomical overlap carries no signal.
The stated limitation was "ten pairs from five tasks", i.e. that more tasks would be better — with
no statement of what the ten pairs are actually worth.

They are not ten independent observations. Every pair shares a task with four others, so the
sample has an effective size nearer **five**, and any test that treats the pairs as exchangeable
is far too narrow. The published figure's *precision* is therefore overstated even though the
correlation itself is exactly right.

## 2. The test the design implies

Permuting the **pairs** is the obvious test and it is wrong. Permuting the **task labels** is the
one that matches the design: it preserves the within-task dependence exactly, and there are
``T!`` such permutations, so it is exact rather than asymptotic. `task_permutation_test` does it.

On `runs/e7_interference.json` (recomputing ρ = +0.9394, matching the artifact to four decimals):

| test | p-value | null sd | what it assumes |
|---|---|---|---|
| permutation over the 10 pairs (20,000 draws) | **0.00020** | — | the pairs are independent — **false** |
| **exact task-label permutation (all 120)** | **0.0165** | 0.466 | the design as it stands |

The observed ρ = +0.9394 sits at the **99.2nd percentile** of the task-level null, and exactly one
of the 120 labelings attains it. So **the naive test overstates the significance by 83×.**

The claim survives — p = 0.017 is significant at 5% — but not at the level it was implied to be, and
the leave-one-out range [+0.917, +0.983] inherits the same optimism.

## 3. The part worth carrying to the benchmark: a hard floor

``T!`` permutations means the smallest attainable p-value is ``1/(T!+1)`` **no matter how perfect
the association is**:

| tasks | labelings | floor on p |
|---|---|---|
| 5 (as run) | 120 | 0.0083 |
| 6 | 720 | 0.0014 |
| **7** | 5,040 | **0.0002** |

So **claiming p < 0.001 for a pair-level prior requires at least 7 tasks**, and that is the floor
with a perfect association — in practice more. The plan's C4 limitation said "a benchmark with more
tasks would test the prior on more pairs"; it can now say how many, and why: the constraint is not
the number of *pairs* (T(T−1)/2 grows fast) but the number of independent *labelings*, which grows
as T!.

That is a design requirement for FlyCL rather than a criticism of the present run, and it is
recorded in the benchmark section of the plan.

## 4. What this does not say

- It does not dispute ρ = +0.939, which reproduces exactly. The measurement is right; the
  inference's precision was.
- It does not make the current result unusable. p = 0.017 with a leave-one-out range that never
  approaches zero is a real association on five tasks, and it is the strongest prior this benchmark
  has produced.
- The task-label permutation assumes the tasks are exchangeable under the null, which is the
  standard construction for this design. An alternative null that modeled task difficulty would be
  more conservative still, not less.

## 5. A second result from the same fire: the fine-column draw sds are complete

`e17b` finished with `ito_lee_hemilineage`, so every annotation column the predictor uses now has a
**measured** draw sd at d = 1307:

| column | concentration | measured | interpolated | ratio |
|---|---|---|---|---|
| `cell_class` | 0.171 | 2.371e-4 | 1.881e-4 | 1.26× |
| `supertype` | 0.026 | 8.35e-5 | 4.14e-5 | **2.03×** |
| `ito_lee_hemilineage` | 0.032 | **4.16e-5** | 4.44e-5 | 0.94× |

Two things follow, and they pull in opposite directions:

- **The interpolation is not reliable in the knee** (0.94× to 2.03×, with no ordering in
  concentration: `supertype` at 0.026 is *twice* `ito` at 0.032). This is one more measurement
  showing that concentration orders **fine versus coarse** and nothing finer — the same conclusion
  the coarse range gave independently.
- **Substituting every measurement for every interpolation leaves the predictor's matched-pair
  count unchanged at 13 of 13**, because each of these columns has a seed sem an order of magnitude
  larger than its draw sd. The headline is indifferent to the error, which is the useful thing to
  know and is not the same as the interpolation being good.

## 6. Limits

- The permutation test uses the exact ``T!`` enumeration, so there is no Monte Carlo error, but with
  ``T = 5`` the p-value is quantised: it can only take values in ``{1/121, 2/121, ...}``. The reported
  0.0165 is ``2/121``, and the next attainable value is 0.0083.
- The null treats the 10 interference and propagation values as fixed and permutes only the task
  labelling. A null that also resampled the tasks would have additional variance, so this test is
  the *less* conservative of the two — it is the right one for "does this labelling explain the
  association", not for "would this recur on new tasks".
- `runs/e23_e7_permcheck.json` validates the wiring at 3 tasks; the 5-task number above is computed
  from the stored artifact by the committed function, and the experiment now prints it too.

## 7. A misnamed flag, and what it means for the "7 tasks" requirement

Wiring the test into `e7_interference.py` crashed on the first attempt:

```
ValueError: expected 3 pair values for 3 tasks
```

The cause is that `--tasks` does **not** control the number of tasks in the pair analysis. It is
passed to `controlled_sweep`, where it sets the number of overlap-controlled supports. The pair
analysis calls `build_tasks(circ, support_size=..., q=..., seed=...)` with **no** `assemblies`
argument, so it uses the module default `TASK_ASSEMBLIES`, which has **5** tasks — and `T` is then
read off the sequence, not off the flag.

Two consequences:

- **The flag is a footgun** and now carries a help string saying what it actually does. A reader who
  set `--tasks 7` expecting a seven-task prior would get a five-task one and no warning. (Passing
  `args.tasks` to the test is what surfaced it, which is the useful part: the exercise of wiring it
  up is what found the misnomer.)
- **The "7 tasks" requirement is a statement about a design, not about this script.** The present
  analysis cannot demonstrate the improvement, because it cannot vary `T` at all. The requirement
  belongs in the benchmark section of the plan — where it now is — and it is a reason to extend the
  task suite rather than a criticism of the current run.

Also worth recording: running the 3-task configuration reproduced **p = 0.0165 exactly**, because
the pair analysis ignores `--tasks` entirely. That is a stronger validation of the wiring than a
3-task number would have been — it is the 5-task computation reproduced on a second invocation — but
it is not the independent check the run was intended to be.
