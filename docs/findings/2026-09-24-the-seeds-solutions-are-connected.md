# `e122`: the seeds' solutions are connected, and the connecting path's worst point is a factor of thirty — not a wall

**Date:** 2026-09-24
**Script:** `experiments/e122_path_geometry.py`, one run; artifact `runs/e122_path_geometry.json`
(read-out 128, 21 points, two seeds: 0 and 100).
**Artifacts:** the above plus `runs/e116_r128_40reps.json` (the reproduction reference) and
`runs/e122_fulltrainloss_check.json` (the full-train-set loss, three replicates, added to `e8` this fire).
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, `--iters 500 --lr 3e-3 --batch 32 --readout-size 128`, 96
training and 48 test samples per task, read-out draw = seed0. The chord interpolates the **whole solution**
(`theta`, the recurrent bias, and the shared decoder) in `float64` between seed 0's and seed 100's checkpoint,
and evaluates the full-train-set loss at 21 equally spaced points, on every task the checkpoint has seen.
**Pre-registration:** **none.** This fire is instrumentation plus a first measurement, and §5 says what that
costs the claim.
**Context:** `docs/findings/2026-09-24-four-times-the-training-does-not-help.md`, which closes the "improve the
measurement" family and names this as the one remaining question that is about the *geometry* rather than the
noise — *"it does not distinguish 'multi-basin landscape' from 'same basin, different direction'"*.

---

## 1. The result: one smooth maximum, thirty-fold, and twenty-six times below chance

The two seeds' solutions are connected by a path that leaves the low-loss region by a **factor** and never
approaches the loss scale at which a task is *not* solved. The cleanest case is the chord through the
checkpoint after the **first** task, where nothing has been retained yet and the only question is the one task
that was just fitted:

| `t` | 0.00 | 0.10 | 0.20 | 0.30 | 0.40 | **0.45** | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| task 0 loss | 0.0017 | 0.0039 | 0.0116 | 0.0256 | 0.0510 | **0.0540** | 0.0425 | 0.0337 | 0.0218 | 0.0089 | 0.0037 | 0.0018 |

The endpoints are **0.00172** and **0.00182** — the two seeds' own recorded full-train-set loss on the task
they had just fitted, and they agree to 5%. The interior maximum is **0.05399**, a **factor of 30 above the
worse of the two endpoints** (and 31× above the better one, so the reading is not an artefact of which end is
called the reference), reached at the midpoint, on a curve that is smooth and symmetric. **And 0.05399 is 3.9%
of the chance level `ln 4 = 1.386`** — the loss at which the task is not solved at all. So:

- **there is a barrier** — the maximum is strictly above *both* endpoints, so neither is a minimum along the
  path and the path is not monotone;
- **it is not a wall** — the path never gets within a factor of 26 of the loss of a solution that has learned
  nothing, so it stays in the region where the task is fitted throughout.

**A multi-basin landscape would need the connecting path to cross a ridge at the scale of a bad solution**,
because that is what separates basins: to get from one to the other you must pass through configurations that
do not solve the task. This path does not. **In the operational sense the question was asked in, the two seeds'
solutions are in one connected set, and "which basin" is not what the seeds are choosing between** — what they
choose between is which point of a connected, over-parameterised, interpolating set they land on.

The other three chords say the same thing in less clean configurations, and they should be quoted because two
of them are dominated by retention rather than by fit:

| chord | task | endpoints | peak (at `t`) | barrier | peak / worse endpoint | peak / chance |
|---|---|---|---|---|---|---|
| after_task_0 | 0 | 0.00172 / 0.00182 | 0.05399 (0.45) | +0.05217 | **30×** | 3.9% |
| final | 2 | 0.00118 / 0.00124 | 0.04394 (0.55) | +0.04270 | **35×** | 3.2% |
| final | 1 | 0.05885 / 0.01719 | 0.10705 (0.25) | +0.04820 | 1.8× | 7.7% |
| final | 0 | 0.09678 / 0.17250 | 0.17513 (0.95) | +0.00264 | 1.02× | 12.6% |

**The task that was just trained has a single interior maximum like the first-task chord (×37, 3.2% of
chance); the two retained tasks do not.** Task 1's chord rises to 0.107 at a quarter of the way along and then
falls monotonically to 0.017 — the maximum is a shoulder rather than a ridge, and the two ends differ by 3.4×,
which is retention, not geometry. Task 0's chord is essentially **monotone** (barrier 1.5%, peak at `t = 0.95`).
So the barrier is a property of the chord's *fit* and disappears into a monotone slope once the chord's ends
differ by a large retained loss. That is a reading of four chords, one of them with a strict barrier of 1.5%,
and it is the honest description rather than a law.

## 2. Two bugs, and the control that now catches both

The first version of this instrument reported endpoint losses of **0.105** for a body whose own recorded loss
was **0.0017** — a factor of sixty, on the endpoint, which is the loudest place a bug can be. There were **two**
independent defects, and they were found by two different controls:

1. **A mid-run body was paired with a final decoder.** `run_method` saved the decoders only once, at the end,
   so the chord through the checkpoint after task 0 evaluated *that body* with the decoder from after task 2 —
   a configuration the benchmark never produces. Fixed in `e8` by saving the decoder per task
   (`head_{i}_{p}_after_task_{k}`).
2. **The recurrent bias was never saved at all.** `train_task` optimises `[model.theta, model.bias]`
   (`experiments/e8_rate_network.py:72`), and `--save-theta` wrote `theta` and the decoders. Every point on the
   chord, both endpoints included, was therefore evaluated on top of a **zero bias** — an untrained network's
   bias under a trained network's weights. Fixed by saving `bias_after_task_{k}`, and the chord now interpolates
   `theta`, the bias and the decoder together.

**The control that catches both is now built in and is an equality, not a tolerance.** At `t = 0` the
interpolated state *is* seed A's checkpoint, so the loss there must equal a number the runner wrote down while
training; the same at `t = 1` for seed B. That requires the runner to record the right number, and this fire
added it: **`retention_loss[k][j]`, the full-train-set loss on task `j` at checkpoint `k`** — the retention
matrix in loss rather than accuracy, which is the first loss-valued retention record in this project. Before it
existed the control could only be run on the checkpoint's own last task, because `full_train_loss[j]` is
recorded at checkpoint `j` — a different body for every `j < T-1` — and the control's first version demanded
agreement between two configurations and reported a failure where there was none. **A control has to compare
like with like, and the thing to compare with had to be recorded before it could be compared.**

The result is **6 of 6 task-endpoints agreeing exactly** across all three checkpoints (1 + 2 + 3), plus the
independent reproduction of `e116_r128_40reps.json` replicate 0 (forgetting +0.0208, accuracy 0.9375, to four
decimals) by a setup this script rebuilds rather than imports. `tests/test_e122_checkpoint.py` makes the
stronger version of the check permanent: reload a checkpoint into a fresh module and require the runner's own
recorded loss, for every task at every checkpoint, for both the shared and the per-task decoder. **A key-list
assertion would pass the moment somebody adds a new trainable parameter and forgets it in the same way; the
loss equality cannot**, which is why the test is the control rather than a list of names.

## 3. Connected as solutions, not interchangeable as parts

Holding seed A's decoder fixed while the body moves gives the other half of the answer, and it is the opposite:
on the final task, seed B's body read through seed A's decoder rises **monotonically from 0.00118 to 0.16010, a
factor of 136**, with no interior maximum at all. So the same pair of endpoints is connected when the decoder
interpolates with the body and **not** connected when it does not.

That is what "the seed decides" means here, and it is worth stating precisely: **the recurrent body and its
decoder are jointly determined by the run, and neither is transportable on its own.** It also says the
whole-solution chord is the right instrument for the question and the body-only chord is not a weaker version
of it but a different question — *"can one seed's read-out read another seed's body"*, to which the answer is no.

And the two seeds illustrate the interpolant story in three numbers. On the task they had just trained they
agree to 5% (**0.00118** against **0.00124**); on the retained task 0 they differ by **1.8×**
(**0.09678** against **0.17250**) and on task 1 by **3.4×** (**0.05885** against **0.01719**). Both seeds
interpolate the task in front of them; they disagree about what they kept. **`e121` said the seeds agree on the
fit and disagree on the generalization; this is that statement as a ratio, and it is the first time this project
has had the retained loss rather than only the retained accuracy.**

## 4. The instrument the run produced for free, and why it is registered rather than claimed

`retention_loss` is a continuous quantity where the reported metric is not: `e118` measured the accuracy-based
forgetting's relative precision at 74–134% of its own value against the drift's 2.6–3.5%, and named the
estimator's granularity (`1/240`) as the structural half of that gap. **A loss-valued retention matrix has no
such floor** — it is a mean of cross-entropies over 96 samples, and it is already recorded at no cost.

**That makes it a candidate fix for the thirty-fold handicap, and this fire does not claim it.**
Two seeds is not a distribution, and the ratio the two seeds give (a factor of 1.8 apart in loss against 3.0
apart in accuracy) points the *other* way at n = 2 — which is exactly the size of sample that produced every
retracted claim on this line. The test is `e119`'s configuration re-run with the new key: 40 replicates at
read-out 128 and 300 with `--test 480`, comparing the per-repeat sd of the loss-valued forgetting against the
accuracy-valued one, which is one hour of compute and a pre-registered band.

## 5. What this cannot settle

- **Nothing here was pre-registered, and the criterion was not fixed in advance.** The criterion is the
  literature's — a barrier is read against the loss scale of a solution that has failed, not against zero — but
  *which* scale (chance level, the worse endpoint, the retained loss) changes the sentence, and only the first
  of those makes the answer "connected". Stating it after the fact is a weakness of this run and the reason §1
  quotes the raw curves rather than the verdict alone.
- **One seed pair, one read-out, one task order.** Seed 100 was chosen because it was already the second
  replicate of `e122_fulltrainloss_check.json`; it is not the pair with the largest forgetting gap. Whether the
  barrier is 3% or 30% of chance for a *different* pair — or at read-out 32, where the spread is largest — is
  untested, and `--seed-b` is the knob.
- **A grid of 21 points can miss a ridge**, so every barrier here is a lower bound; and "connected" is
  established at the resolution of that grid.
- **The chords are through *checkpoints*, not through minimisers.** Standard linear mode connectivity
  interpolates converged solutions of the same objective; these are points on a training trajectory, and the
  ends of the "final" chord are solutions to a *different* set of tasks than the ends of the "after_task_0"
  chord. The comparison across the four chords is therefore a comparison of four different objective functions,
  which is why §1 reads the first-task chord as the clean one.
- **It does not say where the retained loss comes from.** That two seeds' retained losses differ by 1.8× while
  their fitted losses agree to 5% is a statement about the endpoints; the five failed trajectory quantities are
  still failed, and this fire replaces one explanation ("many basins") with another ("one connected set, many
  interpolants") without measuring the selecting mechanism.
