# `e120`, pre-registered: four times the training, to see whether the substrate's residual is under-convergence

**Date:** 2026-09-24
**Script:** `experiments/e8_rate_network.py`, one run; artifact `runs/e120_r128_test480_2000iters.json` (in
flight).
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, `--seed0 0`, read-out 128, **`--test 480 --repeats 40
--iters 2000`** against the 500 iterations of every run so far.
**Context:** `docs/findings/2026-09-24-the-metric-noise-is-mostly-the-substrates.md`, which showed that a
tenfold test set captures **94%** of the removable noise and leaves the forgetting's per-repeat sd at **0.0221**,
**40% of whose variance is the training trajectory's** — and named as the next step *"four times the iterations
at forty replicates, the first next step this sequence has proposed that aims at the substrate rather than at the
axis, the metric or the statistic"*.

---

## 1. The rationale for a directional prediction, and it is a diagnostic the sequence already has

**The distance the body travels is already reproducible to 2.9%** while its consequence varies by 55%. At
read-out 128, test 480, 500 iterations, forty replicates:

| quantity | mean | per-repeat sd | relative |
|---|---|---|---|
| **`theta_drift`** — how far the body moved | 0.0395 | 0.00116 | **2.9%** |
| **forgetting** — what that cost | +0.0402 | 0.0221 | **55%** |
| final accuracy | 0.9215 | 0.0196 | 2.1% |

**So the forty seeds agree on how far the body travels to within 3% and disagree on the forgetting by 55%.**
That is a **direction** difference rather than a **step-size** one, and the prediction that follows is that more
steps of the same kind will not fix it: the seeds are not stopping in the same place because they are not *going*
to the same place, and a longer walk in a different direction is still a different direction.

**The prediction is therefore that the residual does *not* fall**, and the falsifier is what would change the
benchmark's configuration.

## 2. And a diagnostic that makes the forgetting's residual predictable from the accuracy's

The forgetting is `max_k R[k,j] − R[T−1,j]` — a **difference of two accuracies**, each of which varies across
seeds with sd ≈ 0.018 at test 480. If they varied independently the difference would have sd √2·0.018 = 0.026;
the measured 0.0221 implies a seed-to-seed correlation of **ρ ≈ 0.14** between the two. **So the forgetting's
residual is the final accuracy's seed-to-seed variation, transmitted with a factor of √(2(1−ρ)) ≈ 1.31**, and
the two must move together: a change that does not reduce the arm's seed-to-seed accuracy spread cannot reduce
the forgetting's.

> **Amended 2026-09-24, after the run, as an amendment rather than an edit.** The `ρ ≈ 0.14` above **does not
> follow from the formula's own inputs**. `ρ = 1 − (sd_forgetting / sd_accuracy)² / 2`, and on this
> paragraph's own rounded input (`sd_accuracy ≈ 0.018`, `sd_forgetting = 0.0221`) that gives **0.246**; on the
> artifacts' exact values — the accuracy's per-replicate sd **0.01963** and the forgetting's **0.02215**, both
> from `runs/e119_r128_test480.json` at forty replicates — it gives **0.364**. So the stated 0.14 was out by a
> factor of 1.8 against its own inputs and 2.6 against the measurement, and **the prediction it fed (P2, below)
> is unaffected in direction and understated in size**: the corrected propagation is
> `√(2(1 − 0.364)) = 1.128`, which is what the forgetting's sd actually shows (`0.02215/0.01963 = 1.128`).
> The `≈ 0.018` for the accuracy was also a slight understatement of 0.01963, which is where part of the drift
> entered. Nothing else in the registration changes, and the run's own result is reported against the corrected
> value (`docs/findings/2026-09-24-rule-34-had-a-second-instance.md`).

**That gives this fire a second read on its own result**, and it is why the run's `final_sem` matters as much as
its `forgetting_sem`.

## 3. The predictions, and the falsifier, written before the run finishes

| | prediction |
|---|---|
| **P1** | at 2000 iterations the **final accuracy's per-replicate sd does not fall substantially** — by a factor below **1.3×** — because the distance travelled is already reproducible to 2.9% and the disagreement is directional |
| **P2** | consequently the **forgetting's sd stays near 0.022**, following the accuracy's through √(2(1−ρ)) with ρ ≈ 0.14 *(**corrected to 0.36 by the amendment in §2**; the direction of the prediction — that the two move together — is unaffected, and the run's own result is read against 0.36)*; a fall of ≥1.3× in the forgetting *without* one in the accuracy would contradict the propagation and be a finding in itself |
| **C1, the manipulation check** | the **drift** should grow — roughly doubling or more, since four times the iterations is four times the walk in the same direction — and stay reproducible in relative terms (≤5%). If the drift does **not** grow, the manipulation did not change the trajectory and the run cannot test anything |
| **Falsifier** | the accuracy's sd falls **≥1.3×**. The substrate's residual is then **under-convergence**, the benchmark at 500 iterations is **under-trained**, and §4.7's *"the binding limit is the benchmark's own per-repeat spread"* becomes an artefact of a mis-specified training budget rather than a property of the connectome |

**The mean is explicitly *not* predicted**, because four times the training is a different trajectory: it may
forget more (a longer walk), or less (a better solution). **What is predicted is that the *spread* does not
improve**, and that is the only quantity this fire can be wrong about in an interesting way.

## 4. What this cannot settle

- **One read-out, one seed block.** Read-out 128 at test 480; a convergence effect elsewhere, or at read-out 32
  where the spread is largest (0.0556), is not tested — and 32 is where a fall would matter most.
- **Two iteration counts is a line, not a curve.** If the sd falls by 1.2× (inside the band where no prediction
  is made) the honest answer is *"the residual depends weakly on the budget"* and the next count is 8000, not a
  conclusion.
- **It does not touch the mechanism question.** Whatever happens to the spread, the axis's shape — a plateau
  with the narrow end resolved higher — is a separate claim, measured at whatever precision this fire leaves.
