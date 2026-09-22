# E12 — the matched-random control is drawn once, and for coarse partitions that omission inflates the sigma several-fold

**Date:** 2026-09-22
**Script:** `experiments/e12_control_spread.py` (new)
**Artifacts:** `runs/e3_ladder.json` + `runs/e3_seeds18.json` (re-analysed), two e12 runs

---

## 1. The problem

Every biological partition in this project is scored against a **group-size-matched random
partition**, because a partition could otherwise "win" merely by having larger groups. The
control is drawn **once**, and the delta carries the *seed* standard error — the spread across
task geometries for that one draw.

That sem says nothing about how much the delta would move had a **different** random partition
been drawn. The claim — "biological groupings beat random partitions of matched size" — is about
the *population* of random partitions, so the draw-to-draw spread belongs in the error bar. It
has never been included.

## 2. Two duplicate partitions were sitting in the ladder, and they disagree

`bio:pool32` and `bio:pool64` are not merely similar: they are the **same partition**, verified
directly — `_pool_small_groups(cell_type, 32)` and `_pool_small_groups(cell_type, 64)` return
bit-identical label arrays, because only two cell types on this circuit have ≥32 neurons, so
raising the threshold from 32 to 64 moves nothing. Identical group sizes, identical biological
excess (+0.00115 both). Their **controls** differ:

| rung | groups | biological excess | control excess | delta | reported σ |
|---|---|---|---|---|---|
| `pool32` | 3 | +0.00115 | +0.00814 ± 0.00018 | −0.00699 | 37.9 |
| `pool64` | 3 | +0.00115 | +0.00664 ± 0.00026 | −0.00548 | 20.9 |

Difference in delta **0.00150** at 4.7σ. Two draws of the same control design for the same
partition, disagreeing by more than any rung's reported sem.

The mirror case is also on disk. `pool1` and `cell_type` are likewise the same partition
(`_pool_small_groups(lab, 1) == lab`), measured in two different runs:

| control | groups | excess | n |
|---|---|---|---|
| `rand:pool1` (ladder run) | 812 | +0.01723 ± 0.00036 | 12 |
| `rand:cell_type` (18-seed run) | 812 | +0.01729 ± 0.00025 | 18 |

Difference **−0.00006** at 0.13σ. Here two control draws agree almost exactly.

## 3. So the draw component is not a constant — it is a function of coarseness

`experiments/e12_control_spread.py` draws many controls for a **fixed** partition on a **fixed
seed set**, so the task-geometry noise is common to every draw and what is left is the draw
noise. Two runs, `d = 952`, `support 30`, 2 seeds:

| partition | groups | constrained | across-draw sd | within-draw sem | ratio |
|---|---|---|---|---|---|
| `cell_type`, no pooling | 812 | 0.993 | **0.00009** | 0.00147 | **0.1×** |
| `cell_type` pooled at 4 | 8 | 0.245 | **0.00108** | 0.00030 | **3.6×** |

Together with the two implied estimates from §2 — 3.9e-5 at 812 groups (`d = 1307`, n = 2 draws)
and 1.06e-3 at 3 groups (`d = 1307`, n = 2 draws) — the picture is consistent across two
circuits and four measurements:

- **coarse** partitions (2–10 groups): draw sd ≈ **1.1e-3**, i.e. **3–6× the seed sem**;
- **near-diagonal** partitions (hundreds of groups): draw sd ≈ **4e-5–9e-5**, i.e. **0.1× the
  seed sem**, negligible.

The mechanism is straightforward once seen: permuting labels barely changes a partition made of
singletons, and barely-pooled groups are mostly singletons. With 2–10 groups, a permutation
reshuffles which neurons land in the one giant group, and that changes the projection a great
deal. The rungs in between (29, 90 groups) were not measured; all of them have one giant group
(723–1062 neurons) in the same way, so ≈1e-3 is the reasonable interpolation, and it should be
measured rather than assumed.

## 4. What this does to the published numbers

Recomputing with a coarse-partition draw sd of 1.0e-3 added in quadrature (the seed sems are
0.0002–0.0005, so the draw term dominates):

| claim | reported | with the draw component |
|---|---|---|
| `pool4` delta resolves from zero | 42.2σ | **≈ 8.7σ** |
| `pool16` / `pool8` | 39.1σ / 30.1σ | ≈ 7.5σ / ≈ 6.7σ |
| `pool32` / `pool64` / `pool128` | 37.9σ / 20.9σ / 17.8σ | ≈ 6.8σ / ≈ 5.3σ / ≈ 4.0σ |
| `pool1 → pool2` (the fine-end collapse) | 13.6σ | **≈ 7σ — survives** |
| `pool2 → cell_class` | 11.6σ | ≈ 3.3σ |
| `side → pool4` (`side` is 4 groups) | 15.2σ | ≈ 2.8σ |
| `pool2 → pool4` (peak versus plateau) | 2.2σ | **≈ 0.6σ — dead** |

Two things follow.

**The rung-level result survives.** Biological groupings do beat matched random partitions over
0.32–0.67 constrained; the deltas there are 0.005–0.009, i.e. 4–9× the draw sd. They are
resolved at roughly 4–9σ rather than 20–42σ, which is still a result.

**Every *shape* claim is at risk.** The plateau, the location of the optimum, "`side` is a hole
in the envelope" and the headline "granularity sets where you are on the curve, biology sets the
height" all rest on differences between deltas of 0.0015–0.004 — the same order as the
coarse-partition draw sd. Three fires have now argued about the shape of a curve whose
point-to-point differences sit at the noise level of a component that had never been measured.
The one shape claim that holds is the fine-end collapse, and it holds precisely because one of
its two rungs (812 groups) has a precise control.

## 5. A second defect found in the same check

The ladder's **coarse end is degenerate**, because the pooling threshold is a *count* and the
median cell type has one neuron. Exact group structure at `d = 1307`:

| rung | groups | sizes (descending) | constrained |
|---|---|---|---|
| `pool1` | 812 | 140, 105, … | 0.980 |
| `pool2` | 90 | 723, 140, … | 0.674 |
| `pool4` | 29 | 867, 140, … | 0.541 |
| `pool8` | 10 | 952, 140, … | 0.450 |
| `pool16` | 8 | 968, 140, … | 0.432 |
| `pool32` | 3 | 1062, 140, 105 | 0.322 |
| `pool64` | 3 | **identical to `pool32`** | 0.322 |
| `pool128` | 2 | 1167, 140 | 0.191 |

One group grows monotonically (723 → 867 → 952 → 968 → 1062 → 1167) while a persistent
140-neuron cell type never merges. So the ladder is **not** a uniform granularity sweep: it
contains **six distinct partitions**, two rungs are duplicates, and its two coarsest points are
2- and 3-group blunt instruments. "7 of 8 rungs resolve" counts 8 rungs and 6 partitions.

## 6. The remedy

- **Average the control over K draws** in `candidate_bases` and report the draw component
  separately from the seed component. Cost scales with K, and the fine rungs are cheap.
- **A free confirmation is already in flight.** `runs/e3_ladder_v2.json` stores per-seed
  excesses, so `rand:pool32` versus `rand:pool64` can be contrasted **paired** on the same 12
  seeds at `d = 1307` — a clean, zero-extra-compute estimate of the draw sd at the standard
  configuration. It should be the first thing computed when that run lands.
- Measure the draw sd **per rung** before any shape claim is restated. `e12_control_spread
  --min-size N --json-out ...` does it for one rung at a time.
- Do **not** re-litigate the curve's shape until then.

## 7. Limits

- The two `d = 1307` estimates rest on **one pair of draws each** (n = 2 for a variance); the two
  `d = 952` estimates rest on 4 and 5 draws at a different circuit and threshold. The
  coarse/fine contrast is large and reproducible across configurations, but the intermediate
  rungs (29, 90 groups) are interpolated, not measured.
- The full-scale measurement is scripted but not yet run: the machine is already running three
  long jobs and adding a fourth would slow all of them. That is a scheduling choice, not a
  blocker.
- Results that use **no** random control are untouched: the `e2` topology family, the
  eigenbasis comparison, and the network line's method comparison.
- `e12`'s own arithmetic is unaffected — it is the instrument, and it reports both components.
- The `ratio` line in e12's output is below 1 for fine partitions. That is the correct reading
  (the seed sem dominates there), not a bug; the label is "how much a single-draw sem overstates
  the evidence", so below 1 means it does not overstate it at all.
