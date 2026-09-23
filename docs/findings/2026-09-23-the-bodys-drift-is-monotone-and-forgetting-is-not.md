# `e107`: the body's drift is monotone in the read-out, and forgetting is not monotone in either

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py` (now recording `theta_drift`), four runs; artifacts
`runs/e107_drift_r{0,128,32}.json` and `runs/e107_drift_r32_frozen.json`.
**Artifacts:** the four above.
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, 5 replicates, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, read-out 0 / 128 / 32; all four record the same environment
(`torch_num_threads: 20`, `OMP_NUM_THREADS` unset).
**Context:** `docs/findings/2026-09-23-the-plastic-forgetting-series-is-not-monotone.md`, which measured plastic
forgetting as **+0.0479 → +0.0333 → +0.0729** with run-to-run sd zero and named two candidates for why read-out
128 forgets less than the whole state — *an unused body drifts unmeasured*, or *128 is simply an easier
regime*. Neither had been tested because **no run in this project had ever recorded how far the recurrent body
moved.**

---

## 1. The instrument, and its control

`theta_drift` is `||θ_after − θ_before|| / ||θ_before||` per task: the body is 26,568 numbers, so the distance
it travelled is one subtraction. Relative rather than absolute, because the connectome's weight scale is a
property of the circuit rather than of the training.

**The frozen-body control is the instrument's validation, and it is exact**: a body that cannot be trained
gives `0.0000 / 0.0000 / 0.0000`, against 0.0197 / 0.0424 / 0.0510 for the plastic body at the same read-outs.
A measurement whose zero is not zero is not a measurement, and here it is zero to four decimals.

## 2. Three series, and only two of them are monotone

| read-out | **mean θ drift** | **mean forgetting** | accuracy gap (plastic − frozen) | frozen accuracy |
|---|---|---|---|---|
| **0** (whole, 1307) | **0.0195** | **+0.0479** | **−0.0111** | 0.9444 |
| **128** | **0.0391** | **+0.0333** | **+0.0167** | 0.9167 |
| **32** | **0.0493** | **+0.0729** | **+0.1000** | 0.8139 |

**The drift is monotone in the read-out** — 0.0195 → 0.0391 → 0.0493, a factor of **2.5** from the whole state
to 32 — and so is the accuracy gap. **And forgetting is monotone in neither**, which refutes the first
candidate and leaves the second without support:

- **"An unused body drifts unmeasured" is refuted, in the opposite direction.** The body drifts **least**
  where it is least needed (0.0195 at the whole state, where training actively *hurts* — the frozen body is
  +0.0111 accuracy better there) and **most** where it is most needed (0.0493 at read-out 32). So the body is
  not drifting freely in the slack the read-out leaves; it moves *more* when the task has fewer ways to
  compensate, which is what a gradient does when the loss can only be reduced through the body.
- **And the quantity that would make "drift ⇒ forgetting" work is not the drift.** At read-out 128 the body
  moves **twice as far** as at the whole state (0.0391 against 0.0195) and the benchmark forgets **less**
  (0.0333 against 0.0479). At read-out 32 it moves 2.5× as far as at the whole state and forgets **more**
  (0.0729 against 0.0479). **A 2× change in drift moves forgetting in one direction across one step and the
  other direction across the next**, so displacement alone does not order it.

**So two candidates that are both monotone in the read-out — how far the body moves, and how much the task
needs it — both fail to order forgetting**, and the failure is at different steps: the drift series fails
between 0 and 128, the load-bearing series fails between 128 and 32. That is a stronger statement than either
candidate failing alone, because it rules out the family rather than a member: **forgetting here is not a
monotone function of either "the body moved" or "the body mattered".**

## 3. What the per-task structure adds, and one regularity worth having

| read-out | drift per task | forgetting per task |
|---|---|---|
| 0 | 0.0197 / 0.0187 / 0.0201 | +0.0833 / +0.0125 / +0.0000 |
| 128 | 0.0424 / 0.0379 / 0.0368 | +0.0583 / +0.0083 / +0.0000 |
| 32 | 0.0510 / 0.0477 / 0.0493 | +0.0833 / +0.0625 / +0.0000 |

**The drift is near-constant across tasks within a configuration** — a spread of 0.0014, 0.0056 and 0.0033 —
even though *forgetting* varies by a factor of seven across those same tasks (+0.0833 against +0.0125 at the
whole state). So the body moves about the same distance on every task it is given, and **what differs is how
much of that motion costs an earlier task**, which is a property of the read-out and not of the task. That is a
regularity this project has not had before: the three tasks do not differ in how far they move the body, so
"task difficulty" is not what the per-task forgetting column is showing.

**And the last task always forgets exactly zero**, in every configuration, which is the metric's construction
rather than a result — the task that has just been trained cannot yet be forgotten — and is worth naming here
only because it is what makes the per-task column's sevenfold spread a two-point comparison.

## 4. What this does not do, and the question it sharpens

- **It does not identify what does order forgetting.** It removes two candidates. The surviving family is
  something *interaction-shaped*: the drift is comparable across tasks and across configurations, so what
  varies must be the **overlap between what a task changes and what an earlier task uses** — the
  interference quantity the *linear* line has measured all along (`e7`, the interference prior) and which the
  network line has never measured. That is a new instrument rather than a reading, and it is now the named
  next step.
- **Three read-outs, one seed-block each.** The drifts are means over five replicates and their spread is not
  reported here; the forgetting values they sit beside reproduce with sd zero (`e106`), and the drift itself
  has not been re-run.
- **It says nothing about the frozen arm beyond the control**, which is what a control is for.
