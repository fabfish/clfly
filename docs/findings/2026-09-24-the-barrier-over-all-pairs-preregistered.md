# `e124` pre-registered: the barrier over **all** pairs of a dozen seeds, not one pair

**Date:** 2026-09-24
**Status:** pre-registered **before** the run. Committed as its own commit; the run is launched after it.
**Script:** `experiments/e124_barrier_distribution.py`, which imports `e122`'s chord instrument rather than
reimplementing it (`checkpoint`, `lerp`, `apply_state`, `barrier`, `chord_profile`, `endpoint_control`), so there
is exactly one definition of the chord in this project.
**Planned artifact:** `runs/e124_barrier_12seeds.json`.
**Configuration:** read-out 128, `--iters 500 --test 48`, the rest at the house defaults
(`--circuit-size 800 --lr 3e-3 --batch 32 --lam 3e-3 --train 96 --noise 1.0 --classes 4 --shared-head
--input-overlap 0.0 --methods naive`), **training seeds `0 + 100k` for k = 0..11**.
**C0's comparator:** `runs/e122_path_geometry.json` — the chord through seeds 0 and 100, which is pair (0, 1) of
this run's seed set.
**Context:** `docs/findings/2026-09-24-the-seeds-solutions-are-connected.md`, whose §1 and §5 say the same thing
from two directions: the barrier through the **one** seed pair measured is 3.9% of the chance level, which rules
out a wall **for that pair**, and *"one seed pair, one read-out, one task order"* is the first of its listed
weaknesses. Seed 100 was not even chosen for the question — it was the second replicate already on disk.

## What is measured, and why it is cheap now

`e122` paid for a full training run per chord. `e124` trains **12 seeds once**, saves every checkpoint
(`--save-theta`), and then evaluates **all 66 unordered pairs** — because once the checkpoints exist, a chord is
forward passes and nothing else. 1,386 chord evaluations at checkpoint 0 and 4,158 at the final checkpoint,
against 12 training runs.

For every pair `{i, j}` and every checkpoint `k` the pair has seen, the whole-solution chord is evaluated at 21
points on every task `j <= k` the checkpoint has seen; the reported statistics are the barrier
(`max - max(both ends)`, `e122`'s definition, unchanged), the barrier **as a fraction of the chance level**
`ln 4 = 1.386`, and the two endpoint losses.

The pair statistic the fire is about is on the **fit task** — task `k` at checkpoint `k`, where both ends are
configurations that have *just* solved it and the barrier is therefore about geometry alone. Retained tasks
(`j < k` at checkpoint `k`) are reported too, and they answer a different question: their ends differ because the
two seeds retained differently, so their "barrier" is mostly that difference, which `e122` found to be 1.8× and
3.4× on the two retained tasks of its pair.

## The predictions

- **C0, equality against the previous fire.** Pair (0, 1) of this run **is** seeds 0 and 100 of `e122`, at the
  same configuration with the same `--save-theta` semantics, so its chord must reproduce
  `runs/e122_path_geometry.json` **exactly**: the endpoint losses at checkpoint 0's task 0 must be 0.00172 and
  0.00182 (recorded `retention_loss`, so this is the runner's own number recomputed), the peak 0.05399 and the
  barrier +0.05217; and for the final checkpoint task 2, endpoints 0.00118 / 0.00124, peak 0.04394, barrier
  +0.04270. **If this fails, the script's re-use of the chord is not the chord** and no distribution below is
  comparable to the measurement it is generalising.
- **P1, and it is the fire.** **Every one of the 66 pairs** has a barrier on the fit task **below 25% of the
  chance level**, at both checkpoint 0 and the final checkpoint.
- **Falsifier.** **Any** pair above **50%** of the chance level on a fit task. Then "the seeds land in one
  connected set" is false as a general statement, `e122`'s pair was unrepresentative, and the multi-basin
  explanation is back on the table for some pairs — which is a result and would be reported as one.
- **P2, and it is a count rather than a threshold.** The distribution is reported in full — all 66 values per
  task, not a mean and a spread — because the claim "no wall anywhere" is a claim about the **maximum** of a
  distribution, and a maximum cannot be inferred from a mean. The number of pairs within a factor of 2 of the
  worst one is reported as the measure of how close the worst is to the others.
- **P3, exploratory and flagged as such.** Whether the fit-task barrier of a pair correlates with that pair's own
  **forgetting difference** (`|mean_forgetting_i - mean_forgetting_j|`) — i.e. whether the seeds that disagree
  most about what they kept are also the ones with the highest wall between them. Reported with its `n` and
  **not** used to support C0/P1: at n = 66 with three tasks this is a lead, and `e121`'s two-task trade-off at
  r = −0.35 was exactly the kind of lead that came apart at higher `n`.

## Why 25% and 50%, and what the gap between them is for

The thresholds are stated as a **band with a gap** deliberately. A wall in linear mode connectivity means the
interpolated configuration *fails the task*, so the natural scale is the loss of a solution that has learned
nothing (`ln 4`), and the question is how far below it the worst point along a chord stays. A barrier at 25% of
chance is four times below that scale; 50% is two times below, and it is where the interpolant's accuracy is
expected to start degrading measurably rather than marginally. **The gap exists so that a value landing between
them is a stated "neither" rather than a rounding argument** — `e115`'s lesson that a design landing exactly on
its own 2σ criterion cannot answer the question it is asked.

## What this cannot settle, in advance

- **One read-out, one task order, one circuit.** Read-out 32 has the largest per-repeat spread on this axis and
  is untested here; the barrier may be a property of the read-out the way the drift and the fit depth are
  (monotone, `e118`/`e121`). A distribution at read-out 32 is the natural successor and is not this fire.
- **The chord is still through checkpoints, not through minimisers** (`e122` §5), so the fit task is read and the
  retained tasks are not comparable to it.
- **21 points can miss a ridge**, so every barrier is a lower bound and the *minimum* of the distribution is the
  least trustworthy value in it. The maximum — the number P1 and the falsifier are about — is the most
  trustworthy, because missing a ridge can only make it larger.
- **12 seeds is a sample of the seed distribution, not the distribution.** 66 pairs is a lot of pairs and only
  12 independent seeds, so the pair values are heavily dependent and the effective `n` for any statement about
  seeds is 12. Anything the fire says about *pairs* is exact for those 66 pairs.
