# `e123`: the loss-valued retention matrix buys **nothing** — 2.2× noisier, or identical, depending on the units

**Date:** 2026-09-24
**Script:** `experiments/e123_loss_metric.py` (new); artifacts `runs/e123_r128_test480.json` (40 replicates,
read-out 128, `--test 480`, run after the pre-registration) and `runs/e123_analysis.json`.
**C0's comparator:** `runs/e119_r128_test480.json` — the identical configuration from an earlier epoch.
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, chance 0.25, `--methods naive --shared-head
--input-overlap 0.0 --noise 1.0 --iters 500 --lr 3e-3 --batch 32 --test 480 --readout-size 128 --circuit-size
800 --repeats 40`.
**Pre-registration:** `docs/findings/2026-09-24-the-loss-metric-preregistered.md`, committed before the run.
**Context:** `docs/findings/2026-09-24-the-metric-is-thirty-times-noisier.md` — the reported metric is measured to
**74–134% of its own value** against `theta_drift`'s 2.6–3.5%, a **thirty-fold** handicap that `e118` attributed
partly to the estimator's **granularity of 1/240**, and which `e119`'s tenfold test set cut to eighteenfold,
leaving a residual that is "not noise to be removed but a floor under the estimator".

---

## 1. C0 is bit-identity, and then the registered hypothesis fails

**C0 passes exactly.** The per-repeat accuracy forgetting of this run equals `e119`'s forty replicates with
**max |difference| = 0.000e+00** and the per-task rows identical — so recording `retention_loss[k][j]` in the
training loop changed what is *recorded* and nothing about what is *trained*, which is what the registration
claimed and all that makes the comparison below a paired one.

The registered predictions then fail, and the falsifier fires:

| | registered as | result |
|---|---|---|
| **P1** | `sd_loss / sd_acc < 1` | **FAILS** — the ratio is **2.163** |
| **P2** | `sd_loss / sd_acc < 0.71` | **FAILS** |
| **falsifier** | `sd_loss / sd_acc >= 1` | **FIRED** |

So the loss-valued retention matrix is **2.16× noisier** than the accuracy metric it was meant to improve —
the opposite of the prediction, and the falsifier's own stated consequence follows: *"the loss-valued retention
matrix is not an improvement, the accuracy metric's floor is not its estimator's granularity."*

## 2. But the ratio is cross-unit, and the like-for-like form says something different and better

`sd_loss / sd_acc = 2.163` divides **0.04790 nats** by **0.02215 accuracy**. Those are different units, and the
whole ratio is a comparison of two quantities that were never commensurable — which the registration itself said,
in P3: *"the registered claim is about the precision of each quantity against itself, never about agreement
between them."* **P1, P2 and P3 therefore disagree with each other, and that inconsistency is mine**: P1 and P2
are written as a cross-unit sd ratio while P3 says the claim is a within-quantity precision.

Read the way P3 says it should be read:

| estimator | mean | sd | **sd / mean** |
|---|---|---|---|
| accuracy forgetting | 0.04021 | 0.02215 | **55.1%** |
| loss forgetting (nats) | 0.09561 | 0.04790 | **50.1%** |
| log-ratio companion | 3.9165 | 0.4932 | *(1.64× multiplicative — see §4)* |

**`relative-sd(loss) / relative-sd(accuracy) = 0.910`.** The loss metric is **9% better**, i.e. the same thing.

Both readings agree on the verdict — **no improvement** — which is why the conclusion survives the flaw in the
threshold: the falsifier's *number* was cross-unit, but its *conclusion* is what the registered intent gives too
(0.91 is nowhere near the registered 0.71). **A cross-unit threshold that happens to reach the right verdict is
still a threshold that should not have been registered**, and the like-for-like figure is the one to quote.

## 3. The granularity floor is real, measured, and irrelevant

This is the most useful part of the fire, because it tests `e118`'s mechanism directly rather than its
conclusion:

- **the floor exists**: the accuracy-valued forgetting takes **30 distinct values out of 40** replicates, the
  loss-valued one takes **40 of 40**. So there *are* ties to break, and the continuous quantity breaks them;
- **removing it changes the relative spread by 9%**: 55.1% against 50.1%.

**And the two metrics rank the seeds almost identically** — across the forty replicates,
`r(loss forgetting, accuracy forgetting) = +0.785` Pearson and **+0.800 Spearman**, with the log-ratio companion
at +0.695. So the loss adds a finer scale without adding a different signal: it measures the same thing, on the
same seeds, with the same relative precision.

**Which refutes `e118`'s granularity diagnosis as the explanation of the handicap.** The floor was measured, it
was there, and taking it away did nothing — so the thirty-fold gap against the drift is **not** the forgetting's
estimator. It is the *quantity*: "how much did this task's retained performance change" varies between seeds by
about half its own value, and it does so whether you measure it as an accuracy, as an absolute loss, or as a log
ratio. **A quantity can be intrinsically coarse, and no re-expression of it is more precise than the thing it
re-expresses.**

## 4. Four corrections to my own analysis, each found by auditing it against the runner

The pre-registration was a contract and the analysis did not keep it in three places. All four are recorded
because a "measurement" that quietly used a different statistic is worse than no measurement:

1. **The cross-unit threshold** of §2 — the registration's own P1/P2 against its own P3.
2. **The wrong window, and a mis-statement of the runner's convention.** The registration wrote the accuracy
   forgetting as `max_{k in [j, T-1]} R[k][j]`, and the runner computes `nanmax(R[: j + 1, j])` — the window
   **0..j** (`experiments/e8_rate_network.py:517`). The implementation mirrored the mis-statement, and the two
   windows differ by up to **0.0073 per replicate** (0.00057 on the mean). Fixed to the runner's convention.
   **The conclusion is unaffected, and the reason is exact**: the loss-valued form is *identical* under both
   windows, because a task's loss is lowest at `k = j`, right after it was trained, and high at every earlier
   checkpoint where the task had not been trained at all — so the window moves the accuracy side from 55.1% to
   53.5% and the loss side by nothing, and the relative-sd ratio is **0.91 either way**.
3. **`sd / mean` on a log scale is an artifact.** The first version reported the log-ratio companion's precision
   as `0.4932 / 3.9165 = 12.6%`, which read as **four times better than either metric** — and is meaningless:
   adding 10 to every value would divide it by five while changing nothing about the estimator. The invariant
   form is multiplicative, `exp(sd) = 1.64×`, i.e. **the ratio of a seed's retained loss to its just-fitted loss
   typically differs between seeds by a factor of 1.6** — slightly *worse* than both linear forms, not better.
   The lesson is the cheapest one in this finding and it generalises: **a "relative" precision is only
   comparable on a linear scale.**
4. **Both sides have to be computed the same way for a comparison to be paired.** Correction 2 is an instance;
   it is listed separately because it is the reason the fire's numbers changed after the run rather than before
   it, and because the fix cost a re-analysis of a stored artifact rather than a re-run.
5. **The two forms are not mirror images, and the registration said they were.** It wrote that the loss
   forgetting is *"the same expression with the roles of the two directions swapped"*, and the swap is not
   faithful in a way that matters: `loss_forgetting` takes its `min` over `k in [j, T-1]`, which **includes the
   final checkpoint**, so it is **non-negative by construction**; the runner's accuracy form takes its `max` over
   `k in [0, j]`, which **excludes** the final checkpoint for every `j < T-1`, so it is **signed** — a later task
   can leave task `j` better than it was right after `j` was learned. **Measured, not argued**: 2 of 40
   replicates at read-out 128 have task 0's accuracy *higher* at the final checkpoint than immediately after
   learning it (0.9438 → 0.9500 and 0.9542 → 0.9604), the aggregate forgetting is negative in **5 of 40**
   replicates at a test set of 48 against **1 of 40** at 480, and `e124`'s seed 1000 already ends at **−0.0312**
   *with the best accuracy of its twelve*. So the coarse test set does not merely add noise to the forgetting —
   it **manufactures negative values** at five times the rate, because a one-sample move is 0.0208 of accuracy
   when there are 48 decisions and 0.0021 when there are 480. The test that found this is now a test in both
   directions: the loss form must be non-negative on a random matrix and the accuracy form must be able to go
   negative, because if it ever stops being able to, the convention has changed and **every quoted forgetting in
   the record needs revisiting**.

## 5. What this settles, and what it does not

**Settled, and in the paper's favour in one respect and against it in another.** `e118`'s and `e119`'s
unchanged conclusion stands — the reported forgetting is measured to about **half its own value**, and no
re-expression of it is better. What does not stand is the *explanation*: the granularity floor is real, was
removed, and moved the relative spread by 9%. **The eighteenfold handicap against the drift is intrinsic to the
quantity**, so the honest form of §4.7's sentence is stronger than before: it is not that this benchmark's
metric is badly chosen, it is that *forgetting* is a coarse thing to measure here, whichever way it is measured.

**Cannot settle, in advance:**

- **One read-out.** The registration names 128 **and 300**, and only 128 has run. The 300 arm is launched and its
  comparison is *within* that run, so it needs no comparator of its own — but read-out 300's own per-repeat sd
  differs from 128's, and a ratio that is 0.91 at one read-out is a point rather than a law.
- **The loss is measured on the training split**, whose 96 samples are the ones every seed interpolates
  (`e121`), so its sampling floor is not something a bigger test set can remove; the ratio is a comparison of two
  precisions, not a decomposition into components the way `e119`'s variance budget was.
- **Three tasks, one draw, one circuit.** The forgetting averages two tasks, so its own `n` is two numbers per
  replicate; a benchmark with more tasks would lower this measurement's noise for reasons having nothing to do
  with the estimator.
- **And nothing here says the accuracy metric is the right one to report** — only that the loss-valued matrix,
  which was the cheapest candidate for replacing it, is not.
