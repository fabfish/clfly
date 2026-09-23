# `e124`: the barrier over all 66 pairs of a dozen seeds — one connected set at read-out 128, and the barrier is not the disagreement

**Date:** 2026-09-24

> **Qualified 2026-09-24 by `e130`, which ran this finding's own P1 at read-out 32 and saw it fail.** Every
> claim below is about **read-out 128** and stands there. At read-out 32 — the narrowest read-out, where this
> axis's per-repeat spread is largest — **21 of the 66 final-checkpoint pairs exceed the 25% threshold**, the
> worst chord peaks at **0.4419** of chance against 0.1252 here, and the margin to a wall thins from **7.99×**
> below chance to **2.26×** (12.52% of chance to 44.19%). The falsifier did not fire at either read-out (nothing reached 50%), so the
> connected-set claim is **qualified and not overturned**: the set is connected where the seeds differ least and
> comes closest to not being so where they differ most, which is the ordering the geometry predicts
> (`docs/findings/2026-09-24-the-connected-set-claim-is-read-out-dependent.md`). The sentence this paragraph
> qualifies — *"every one of the 132 pair-checkpoints"* — is kept below as written because the numbers are right;
> **the scope is a read-out, not the benchmark.**
**Script:** `experiments/e124_barrier_distribution.py` (new; imports `e122`'s chord instrument rather than
reimplementing it); artifact `runs/e124_barrier_12seeds.json`.
**Comparators:** `runs/e122_path_geometry.json` (C0), `runs/e116_r128_40reps.json` (the free extension control).
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, chance 0.25, `--methods naive --shared-head
--input-overlap 0.0 --noise 1.0 --iters 500 --lr 3e-3 --batch 32 --test 48 --readout-size 128 --circuit-size 800`,
**twelve seeds `0 + 100k`**, every checkpoint saved; the whole solution (`theta`, the recurrent bias and the
decoder) interpolated along 21-point chords, evaluated on the full train split, for all **66 unordered pairs**
at the first and last checkpoints.
**Pre-registration:** `docs/findings/2026-09-24-the-barrier-over-all-pairs-preregistered.md`, committed before the
run. **§5 reports a deviation from it.**
**Context:** `docs/findings/2026-09-24-the-seeds-solutions-are-connected.md`, whose finding says the two seeds'
solutions are connected and whose own §5 lists *"one seed pair, one read-out, one task order"* as the first
weakness — and whose seed 100 was not chosen for the question but was simply the second replicate on disk.

---

## 1. The result: P1 holds for every pair, and the falsifier does not fire

**Every one of the 132 pair-checkpoints has a fit-task barrier below 25% of the chance level.** The
distribution of the barrier as a fraction of `ln 4 = 1.386`:

| unit | n | min | q1 | median | q3 | **max** |
|---|---|---|---|---|---|---|
| all fit-task chords | 132 | 0.0108 | — | 0.0361 | — | **0.1252** |
| checkpoint after task 1 | 66 | 0.0108 | 0.0212 | 0.0284 | 0.0392 | 0.1221 |
| checkpoint after task 3 | 66 | 0.0148 | 0.0310 | 0.0445 | 0.0657 | 0.1252 |

**The worst chord in the whole grid has a peak at 12.5% of the chance level — 7.99× below the loss
of a solution that has learned nothing** — and the median is **3.6%**, which is `e122`'s single pair almost
exactly (`0.05399 / 1.386 = 3.9%`). So **`e122`'s pair was typical, not lucky**, and the answer to *"is the
multi-basin explanation dead?"* no longer rests on one draw from the seed set: it is dead for all 66 pairs, and
the falsifier's own threshold is a factor of four above the worst of them.

Two smaller readings the distribution gives for free:

- **The median barrier grows with the number of tasks** — 0.0284 after task 1, 0.0445 after task 3, a factor of
  **1.57** — which is what more interference between more tasks should do to the path between two solutions.
- **The distribution has a tail**: 26 of 132 chords (20%) are within a factor of two of the worst. So "every pair
  is below 25%" is true and "every pair is equally connected" would not be — the pairs differ by an order of
  magnitude, from 0.011 to 0.125.

**C0 is bit-identity, not agreement.** The chord through seeds 0 and 100 — pair (0, 1) of this set, at the same
configuration — reproduces `runs/e122_path_geometry.json` **exactly**: peak 0.05399 against 0.05399 and barrier
+0.05217 against +0.05217 at the first checkpoint's task 0, and 0.04394 / +0.04270 at the last checkpoint's task
2. The three saved checkpoints also pass `e122`'s endpoint control **6 of 6**, so the instrument reconstructs the
runner's own recorded retention loss on every task at every checkpoint.

**And a free extension control, which is the strongest evidence in the fire about the code.** `e116` trained
forty replicates at read-out 128 with `seed0 + 100r`, so this run's twelve seeds are its first twelve — and all
twelve reproduce it **bit-identically** (+0.0208, +0.0625, +0.0208, +0.0000, +0.0625, +0.0625, +0.0521,
+0.0833, +0.0312, +0.0312, −0.0312, +0.0104), with the 12-seed sd at **0.0324** against the 40-replicate
**0.0325**. Two independent runs of the same configuration agree to the last bit, which also settles what this
session's three `e8` additions were: **`retention_loss`, `bias_norms` and the per-task checkpoint are recording
changes, not behavioural ones.**

## 2. The barrier is a property of the pair, and it is not the pair's disagreement

Registered as P3 and now computed as registered: across the **66 pairs**, the correlation between a pair's
fit-task barrier and that pair's own **forgetting difference** `|mean_forgetting_i − mean_forgetting_j|` is
**r = +0.144**. Squared, that is 2% of the variance. The three worst chords make the point without any
statistic:

| pair | barrier / chance | pair's `abs(delta forgetting)` |
|---|---|---|
| 400, 1000 | **0.1252** | 0.0938 |
| 0, 700 | 0.1221 | 0.0625 |
| **400, 600** | **0.1138** | **0.0104** |
| 400, 700 | 0.1109 | 0.0208 |
| 700, 1000 | 0.0984 | 0.1146 |

**The third-worst chord in the grid joins two seeds whose forgetting differs by 0.0104** — nearly the same
retention — and the pair with the *largest* difference (700/1000, 0.1146) is fifth. So the barrier between two
solutions is **not** how much they disagree about what they kept, which is the one thing a "which interpolant"
story would most naturally have been about.

**Which leaves the fire where the last five left the trajectory quantities.** The drift, the load-bearing gap,
the first-order term, the second-order quadratic form, the fit depth, and now the barrier's own relation to
retention disagreement: **six quantities measured, none of which orders or explains the forgetting.** And the
geometry result sharpens the shape of the gap rather than filling it: the seeds' solutions are **one connected
set** (§1), they are **not interchangeable** (`e122`: holding one seed's decoder fixed, the other's body is 135×
worse), and **nothing measured so far says which point of the set a seed lands on.**

## 3. Two seeds out of twelve end with negative forgetting, and all twelve interpolate

The twelve seeds' own numbers, which the run recorded and which are worth stating because they bound what "the
seed-to-seed spread" means at n = 12:

| seed | 0 | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 1000 | 1100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| forgetting | +0.0208 | +0.0625 | +0.0208 | **+0.0000** | +0.0625 | +0.0625 | +0.0521 | +0.0833 | +0.0312 | +0.0312 | **−0.0312** | +0.0104 |
| accuracy | 0.9375 | 0.9097 | 0.9306 | 0.9514 | 0.9375 | 0.9306 | 0.9444 | 0.8889 | 0.9444 | 0.9167 | **0.9722** | 0.9444 |

Mean +0.0339, sd 0.0324, range **[−0.0312, +0.0833]** — an ordinary draw from the distribution `e116` measured
at forty replicates at this read-out (mean **+0.0370**, per-repeat sd **0.0325**), spanning **−2.1 to +1.4 sd**.
**Two of twelve seeds have forgetting at or below zero**: seed 1000 ends **better on the old tasks than it was
immediately after learning them** (−0.0312) *and* has the best final accuracy of the twelve (0.9722), and seed
300 is exactly 0.0000 with the **second-best** accuracy (0.9514). So "forgetting" on this benchmark is not a
positive quantity that every seed pays: it is a signed difference with a seed-dependent sign, and a twelve-seed
sample contains both signs. **All twelve fit the last task to 0.00118–0.00157**, so every seed interpolates,
which is `e121`'s result reproduced on a disjoint seed block.

## 4. What this establishes about the geometry claim

Together with `e122` the geometry question is now closed for this benchmark, at the resolution this grid has:

- **the seeds' solutions are one connected set, for 66 of 66 pairs**, with the worst connecting path's peak at
  **3.9%–12.5% of chance** and a **median of 3.6%** — so far below a wall that "which basin" is not a
  description of what the seeds differ by;
- the set is **reachable but not decomposable**: the whole solution is transportable along the chord, and neither
  the body nor the decoder is transportable alone;
- and **the barrier itself is not the quantity that would explain it**, because within this grid it is unrelated
  to how much the pairs disagree about retention.

**So the honest form of the conclusion is a narrowing rather than an answer.** `e122` said the multi-basin
explanation is dead for one pair; `e124` says it is dead for the population. What remains is a **selection
problem inside a connected set** — which point a seed lands on — and this fire's contribution to it is negative:
the barrier is not a proxy for it.

## 5. A deviation from the pre-registration, and the repair

**P3 as registered is not what the script first computed.** The registration says: *"whether the fit-task barrier
of a pair correlates with that pair's own forgetting difference (`|mean_forgetting_i - mean_forgetting_j|`)"* —
**one point per pair, 66 of them**. The script correlated the retained-task **endpoint loss ratio** instead,
which is a different quantity on a different unit (**132 rows**, one per pair per retained task), and printed it
under the name `P3`. The two differ in their `n` *and* in what they measure, so the substitution is not a
rounding: **+0.060 at 132 rows against +0.144 at 66 pairs.**

Both point the same way (nothing), and that is luck rather than vindication. The repair is in three parts, and
the third is the one that matters: the registered quantity is now computed and printed under its own name
(`p3_registered`); the substituted one is kept and **labelled as not the registered quantity** rather than
deleted, because deleting it would hide the substitution instead of correcting it; and the script gained
`--reanalyse PATH`, which recomputes the distributions and both P3 values **from a stored artifact with no
training**, because the statistics are a function of the stored rows and scalars. The artifact on disk was
corrected that way and its distributions are unchanged (min 0.0108, median 0.0361, max 0.1252 before and after),
so the re-analysis is verifiably non-destructive. **A pre-registration whose statistic can be swapped and then
quietly re-run is not a registration**, and the flag exists so that the next substitution costs one command
rather than being invisible.

## 6. What this cannot settle

- **One read-out, one task order, one circuit.** Read-out 32 has the largest per-repeat spread on this axis
  (`e116`: sd 0.0556 against 0.0325 here) and the barrier there is untested. The drift, the load-bearing gap and
  the fit depth are all monotone in the read-out, so a barrier that is a property of the geometry *and* a
  monotone function of the read-out would be two claims where this fire supports one.
- **12 seeds is a sample, and 66 pairs are 12 observations.** The pair values are heavily dependent — each seed
  appears in 11 of them — so the effective `n` for anything about *seeds* is 12, and the pair-level statements
  are exact only for those 66 pairs. That is 20% of the seed range `e116` measured at forty replicates, and the
  twelve reproduce it bit-identically, so the *sample* is not the weakness; the dependence is.
- **21 points per chord can miss a ridge**, so every barrier is a lower bound — which is the safe direction for
  P1 and the unsafe one for the *spread*: the true distribution's tail could be longer than the measured one.
- **The tail is unexplained.** 26 chords within a factor of two of the worst, and the worst joins two seeds
  whose retention agrees to 0.0104. This fire says the barrier is not the disagreement; it does not say what it
  is, and the four worst pairs are not a large enough set to look for it.
- **And it cannot distinguish "connected" from "connected *and* flat"** — the barrier is a maximum along a
  straight line, which is a lower bound on the connectivity of the region, not a characterisation of it.
