# `e121`: the benchmark interpolates its training data at every read-out, so its variation lives among interpolants

**Date:** 2026-09-24
**Method:** the final minibatch training losses recorded per replicate in every forty-replicate run of the
read-out series, plus the seed-level correlations between those losses and the held-out metrics.
**Artifacts:** `runs/e115_r{300,512}_40reps.json`, `runs/e116_r{1307,900,700,128,32}_40reps.json`,
`runs/e119_r128_test480.json`, `runs/e120_r128_test480_2000iters.json`.
**Context:** `docs/findings/2026-09-24-four-times-the-training-does-not-help.md`, which closed the *measurement*
routes and left the limit intrinsic — and `docs/findings/2026-09-24-the-axis-is-a-plateau.md`, which is the
shape that limit prevents from being resolved further.

---

## 1. Every read-out fits its training data, and 32× better at the wide end than the narrow

The runner records the loss at the **last training step** of each task — a minibatch of 32 samples from that
task's 96 — so it is a direct measure of how well the body has fitted its data. For four classes the
chance-level loss is **ln 4 = 1.386**:

| read-out | forgetting | accuracy | **final training loss (task 0 / 1 / 2)** |
|---|---|---|---|
| **1307** | +0.0357 | 0.9387 | **0.00014 / 0.00014 / 0.00015** |
| **900** | +0.0219 | 0.9408 | 0.00022 / 0.00020 / 0.00022 |
| **700** | +0.0221 | 0.9439 | 0.00028 / 0.00028 / 0.00029 |
| **512** | +0.0250 | 0.9486 | 0.00035 / 0.00037 / 0.00038 |
| **300** | +0.0232 | 0.9398 | 0.00067 / 0.00071 / 0.00065 |
| **128** | +0.0370 | 0.9313 | 0.00158 / 0.00142 / 0.00135 |
| **32** | +0.0750 | 0.9125 | 0.00451 / 0.00527 / 0.00564 |

**So the model fits its training data at every read-out the paper uses, by a factor of 300 to 10,000 against
chance** — including read-out 32, the narrowest, where the tasks are still fitted to 0.005. **No read-out tested
is capacity-limited.** With 96 training samples per task and 26,568 body parameters plus the read-out, the
benchmark sits at roughly **300 parameters per training sample**: this is an interpolating regime, and the fit is
near-perfect everywhere.

**And the fit depth is itself monotone in the read-out** — 0.00014 → 0.00451, a factor of 32 from the whole
state to 32 — which makes it **a fourth quantity that is monotone along this axis while the forgetting is a
plateau**, alongside the drift (`e116`), the load-bearing gap, and the first-order interference term.

## 2. So the seed-to-seed variation is variation among interpolants, and the fit depth does not explain it

All forty seeds of one configuration drive the training loss to ~10⁻⁴ while their **held-out** metrics differ by
0.0196 (accuracy) and 0.0221 (forgetting). **The seeds agree on the fit and disagree on the generalization**,
which is what an interpolating regime predicts: there are many solutions that fit, and they differ off the
training set.

**And how well a seed fits carries no information about what it retains.** Across the forty replicates:

| correlation (n = 40, 5% threshold ≈ 0.31) | 500 iterations | 2000 iterations |
|---|---|---|
| loss(task 0) vs forgetting(task 0) | −0.05 | +0.03 |
| loss(task 1) vs forgetting(task 1) | +0.34 | +0.06 |
| total loss vs mean forgetting | +0.11 | +0.02 |
| total loss vs final accuracy | −0.19 | +0.02 |

**Nothing.** The two losing-task correlations disagree in sign between budgets and neither is stable, and the
aggregate correlations are zero. **So "how well you fit" is not the mechanism either** — which is a *fifth*
quantity tested against this forgetting and a fifth failure, and the first one that is not a trajectory
quantity at all but a property of the endpoint.

**The one seed-level structure that did appear is a weak trade-off between the two tasks' fits**: loss(0) against
loss(1) correlates **−0.35** at 500 iterations and **−0.31** at 2000, both at the ~5% threshold for n = 40 and
**agreeing in sign across two budgets**. Seeds that fit one task worse fit the other better — a capacity
allocation story rather than a trajectory one. **It is the first seed-level correlation this sequence has found
and it is about the two tasks competing**, and at n = 40 with r ≈ −0.33 it is a lead rather than a result.

## 3. What this says about the paper's design principle, and it is a qualifier

§4.2's principle is that a **narrow** read-out makes the recurrent body load-bearing, and the frozen-body control
is its evidence: freezing the body eliminates forgetting (0.0000 at every read-out) and costs accuracy, so the
plastic body is doing the work. **What this measurement adds is that the body is not *strained* while doing it.**
At read-out 32 the body still fits its training data to 0.005, so "load-bearing" means the **read-out cannot carry
the task** — a statement about the bottleneck — and not that the body is near its capacity. **The benchmark is
over-parameterised at every read-out the paper uses**, and the design principle should say so, because it is the
same fact that produces the plateau: in a regime where every seed interpolates, the forgetting is a property of
*which interpolant* the run lands in, and a trajectory-level quantity has no purchase on that.

**And it makes the earlier failures one story rather than five.** The drift is a property of the walk, the gap is
a property of the bottleneck, the interference terms are properties of the loss landscape at the endpoint, and
the fit depth is a property of the endpoint — **and none of them can say which of many interpolants a seed will
land in**, because the thing that determines that is the seed.

## 4. What this cannot settle

- **`losses[k]` is a single minibatch's loss at the last training step**, not the full training-set loss, so
  "fits its training data" is measured on 32 of 96 samples; a per-seed full-set loss would be stronger and is
  cheap to add.
- **The trade-off correlation is at the significance threshold** and is the kind of thing 40 seeds can produce by
  chance once; two budgets agreeing is evidence but not much of it, and 120 seeds would be the natural test.
- **It does not change the axis's shape or the intrinsic limit** — it explains *why* the limit is intrinsic, in
  the language of the regime rather than of the optimiser: there is nothing to converge to.
