# `e131`: the third geometry point — the barrier orders like how much the body carries, not like the read-out's noise

**Date:** 2026-09-24
**Script:** `experiments/e124_barrier_distribution.py` (unchanged); artifact `runs/e131_barrier_r1307.json`.
**C0's comparator:** `runs/e116_r1307_40reps.json`.
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, chance 0.25, `--methods naive --shared-head
--input-overlap 0.0 --noise 1.0 --iters 500 --lr 3e-3 --batch 32 --test 48 --readout-size 1307 --circuit-size
800`, twelve seeds `0 + 100k`, 66 pairs, 21-point whole-solution chords at the first and last checkpoints.
**Pre-registration:** `docs/findings/2026-09-24-the-third-geometry-point-preregistered.md`, committed before the
run, with `e124`'s thresholds reused verbatim.
**Context:** `docs/findings/2026-09-24-the-connected-set-claim-is-read-out-dependent.md`, which found `e124`'s P1
failing at read-out 32 and said that with two read-outs *"the barrier is a property of the geometry"* and *"the
barrier is a monotone function of the read-out"* are **two claims the data cannot separate**.

---

## 1. P1 holds at the third read-out, and the grid is nearly flat

| fit-task barrier / chance | read-out 32 | read-out 128 | **read-out 1307** |
|---|---|---|---|
| checkpoint 0 — min / median / max | 0.0158 / 0.0550 / 0.1342 | 0.0108 / 0.0284 / 0.1221 | **0.0003 / 0.0013 / 0.0399** |
| checkpoint 2 — min / median / max | 0.0900 / 0.2187 / **0.4419** | 0.0148 / 0.0445 / 0.1252 | **0.0005 / 0.0169 / 0.1915** |
| **median over the grid** | 0.1157 | 0.0361 | **0.0054** |
| pair-checkpoints above the 0.25 threshold | **21 of 132** | 0 of 132 | **0 of 132** |
| worst chord, **as a % of chance** | **44.19%** | **12.52%** | **19.15%** |

**P1 holds** — all 132 pair-checkpoints below 25% of chance — and the falsifier does not fire. **The grid is very
nearly flat**: the median chord's worst point is **0.54%** of chance and the best is **0.03%**, so at the whole
state two seeds' solutions are connected by paths that essentially do not leave the fitted region at all. The
**retained**-task chords agree: median **0.0000**, max 0.0553 — after two further tasks, at this read-out, the
seeds' solutions have not moved relative to each other in a way any task can see.

## 2. P2 holds, and it separates the two explanations — which is what the fire was for

P2 was registered as an **ordering**, and the ordering came out as registered:

| | read-out 32 | read-out 128 | read-out 1307 | ordering |
|---|---|---|---|---|
| **median barrier / chance** | 0.1157 | 0.0361 | **0.0054** | **32 > 128 > 1307** |
| **per-repeat spread** (`e116`) | 0.0556 | 0.0325 | 0.0423 | **32 > 1307 > 128** |
| **load-bearing gap** (`e104`'s frozen sweep) | +0.1000 | +0.0167 | −0.0111 | **32 > 128 > 1307** |

**The barrier's ordering is the load-bearing gap's and not the per-repeat spread's**, and the two differ in the
middle: the spread puts read-out 1307 second because its per-repeat sd (0.0423) is *between* the other two,
while the barrier puts it **last** by a factor of **6.7** below read-out 128. **That is the separation the
pre-registration promised and the reason it was stated as an ordering rather than a magnitude.**

The gaps are read from artifacts rather than quoted: `e104_frozen_whole_{plastic,frozen}` give 0.9333 and 0.9444
(**−0.0111**, negative — freezing the body *helps* at the whole state), `e104_frozen_r128_*` give 0.9333 and
0.9167 (**+0.0167**), and `e104_frozen_r32_*` give 0.9139 and 0.8139 (**+0.1000**).

**So the geometry result is about how much the body carries.** At the whole state, where the plastic weights are
not needed — the frozen body is *better* — two seeds find essentially the same solution and the connecting path
is flat to 0.03% of chance. At the narrowest read-out, where the body carries +0.10 of accuracy, the same
comparison puts 21 of 66 pairs above the 25% threshold and the worst chord at **44.2% of chance** —
**2.26×** below it rather than 7.99×. **The barrier is
not the read-out's noise; it is the read-out's load.**

## 3. What does *not* come out cleanly

- **The growth with the number of tasks is not monotone in the read-out**: **13×** at read-out 1307
  (0.0013 → 0.0169), **1.57×** at 128, **3.98×** at 32. Two read-outs suggested this factor grows as the read-out
  narrows, and the third breaks that: at the whole state the checkpoint-0 barrier is *almost zero* (0.0013) so a
  13× rise is still small in absolute terms. **The ratio is the wrong statistic here**, and the raw medians in §1
  are the honest form.
- **The worst chord is not monotone in the read-out either**: 0.4419 (32), 0.1252 (128), **0.1915** (1307). Read-out
  1307's worst pair is worse than read-out 128's, so *"the barrier rises as the read-out narrows"* holds for the
  **median** and not for the **maximum**. Reported because the maximum is what the falsifier is about.
- **P3 is a third null with a third sign**: r = **+0.009** here against +0.144 (128) and −0.108 (32). Three
  near-zero correlations of inconsistent sign are three samples of nothing, and the barrier is not the pair's
  disagreement at any read-out tested.

## 4. Controls

**C0a is bit-identity** — the twelve seeds reproduce `runs/e116_r1307_40reps.json`'s first twelve with **max
|difference| 0.000e+00**, the third read-out at which this control has delivered. **C0b passes 6 of 6.** And the
fit losses are the fourth reading of `e121`: **0.00011–0.00015** at read-out 1307 against **0.0050–0.0058** at
read-out 32, so the whole state interpolates its training data two orders of magnitude better — which is the same
fact as the gap being negative there.

## 5. A unit error in three documents, found while writing this one

The table in §1 was first written with a **"factor below chance"** column reading **3.14× / 11.07× / 7.24×**, and
all three were wrong. `barrier_over_chance` is already **a fraction of `ln 4`**, so dividing `ln 4` by it divides
beyond by `ln 4` a second time. The correct figures are **2.26× / 7.99× / 5.22×**, i.e. the fractions
**44.19% / 12.52% / 19.15% of chance** — and "2.26× below chance" is *not* the same statement as "44.19% of
chance" until it is written beside it.

**Three documents carried the error** (`e124`'s, `e130`'s and this one's) plus the paper's §4.2 paragraph, and all
four are corrected with dates. **A systematic sweep of every "below chance" figure in the corpus found exactly
two that were right, and they show what the convention costs**: the `e124` registration wrote *"25% of chance is
four times below that scale"* — **the fraction first** — and `e122`'s "26× below chance" divides by an *absolute*
loss of 0.05399 nats, where the division is the right one. So the pre-registration that established the
thresholds used the safe form and the results that quoted them did not.

**And it is `e123`'s cross-unit defect in a second costume** — an sd in nats divided by an sd in accuracy there,
a dimensionless ratio divided into a loss here. The repair is the same: **state both numbers**, fraction and
factor, because a sentence writing *"12.52% of chance, 7.99× below it"* cannot contain this error while one
writing *"a factor of 11.07 below chance"* can. That is now rule 35, and the check it licenses is the cheapest
one available: **every "factor below" figure must sit beside the fraction or the loss it was divided from.**

## 6. And the hard cases do not persist across read-outs, which is stronger than "one read-out"

The three grids used the **same 66 pairs**, so they can be compared directly, and they do not agree about which
pair is hard: the per-pair barriers correlate at **−0.224, −0.142 and −0.046** across the three read-out pairs,
and the **worst ten overlap by one of ten pairwise and ZERO of ten across all three**. Nor is it the seed: each
seed's mean barrier over its eleven pairs gives a 12-vector per read-out, and those are negatively correlated too
(**−0.337, −0.135, −0.201**). **What organises each read-out is one seed, and it is a different one each time** —
**0** at read-out 32, **400** at 128, **100** at 1307 — with the worst seed's ratio to the median seed rising
**1.30× → 1.61× → 3.77×** as the read-out widens. Where the barrier is large every seed is hard to connect;
where it is nearly absent the pairs that rise involve one seed that landed somewhere anomalous. **So the "three
read-outs is a curve on three points" caveat is not the whole of it**: the *identity* of the hard cases does not
survive a change of read-out either, and a single-read-out geometry study cannot be read as a statement about the
seeds (`docs/findings/2026-09-24-the-hard-cases-do-not-persist.md`).

## 7. What this settles and what it cannot

**Settles the fire's question**: across three read-outs the barrier's ordering follows the load-bearing gap and
**not** the per-repeat spread, so the two explanations the two-read-out data could not separate are separated, and
the geometry reading is the one that survives. **It also gives the design principle a second consequence**: the
connectedness of the seeds' solutions is not a property of the output dimension but of **what the body is doing
there** — a benchmark can be at its most geometrically benign exactly where its body is least needed.

**Cannot settle:**

- **Three read-outs is still a curve on three points**, and the ordering test compares medians of 66 heavily
  dependent values (each seed appears in 11 pairs, so the effective `n` for anything about seeds is 12).
- **The load-bearing gap is measured on 5 replicates** (`e104`), and the gap's ordering is used as the
  comparator's ordering — so a mis-ordered gap at 128 or 1307 would invert the conclusion. The gap's own values
  are far apart (+0.1000, +0.0167, −0.0111) relative to a 5-replicate sem, but that is an argument and not this
  fire's measurement.
- **Read-out 1307 is the whole state, which is the configuration the paper says "contains no continual-learning
  problem"** — so the flattest grid is at the read-out where the benchmark is least interesting, and the result
  should not be read as *"this benchmark is easy to connect"* but as *"the connection cost tracks the body's
  load"*.
- **`--readout-size 0` and `--readout-size 1307` are the same read-out in this codebase and appear as different
  config values**, so an artifact's `readout_size` is not a reliable way to tell them apart; this run used 1307 to
  match its comparator exactly.
