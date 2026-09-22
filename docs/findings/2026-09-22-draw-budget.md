# E13 — which claims this substrate can actually answer: a draw-budget analysis

**Date:** 2026-09-22
**Script:** `clfly/bench/control.py` (`delta_sem`, `draws_needed`, `averaged_random_control`), `experiments/e3_basis_selection.py --control-draws`
**Artifacts:** `runs/e13_control3_d952.json` (wiring validation, in flight); the tables below are derived from `runs/e3_ladder.json` and `runs/e3_seeds18.json`

---

## 1. Turning "the shape is unresolved" into a number

E12 established that the matched-random control is a **single draw**, and that for coarse
partitions the draw-to-draw sd (~1.1e-3) is several times the seed sem (~2e-4). "The curve's
shape is unresolved" is a true but useless statement. The useful one is: *how many control draws
would each claim need, and is that affordable?*

The relation is simple and easy to get wrong, because seeds and draws are not the same kind of
axis. For a delta ``biological - control``,

    Var = sem_seed^2  +  sd_draw^2 / K

where ``sem_seed`` is the seed sem of the difference and ``sd_draw`` is the draw-to-draw sd of
**one** control's mean. The draw term is a **per-observation spread**, not a standard error: it is
divided by ``sqrt(K)`` for the draws averaged and **not** by ``sqrt(n_seeds)``. More seeds do not
make one control draw less arbitrary. For a contrast between two rungs the draw term counts
twice, since each rung has its own control. ``draws_needed`` inverts this, and returns ``inf``
when no number of draws suffices — that is, when the seed budget alone puts the claim out of
reach.

## 2. The model self-validates on a case whose true answer is zero

`pool32` and `pool64` are *the same partition*, so their true delta difference is **exactly
zero**. Anything observed there is noise, which makes it a calibration probe:

| quantity | value |
|---|---|
| observed difference in delta | **0.00150** |
| seed-only sem | 0.00032 |
| model's predicted K=1 noise scale, ``sqrt(2) * sd_draw`` | **0.00156** |

The model reproduces the observed noise to within 4%. That is the strongest evidence available
that the draw-sd of ~1.1e-3 is real and correctly placed, and it is worth noting that the
seed-only column called this difference **4.7σ** when the truth is 0.95σ — a five-fold
overstatement, on a pair whose answer was known in advance.

## 3. Single-rung claims: already fine, no averaging needed

Does the biological partition beat a size-matched random one at this rung? Group counts are the
annotation's; ``sd_draw`` is measured for ≤12 and ≥200 groups and interpolated between (see §6).

| rung | groups | delta | σ at K=1 | K needed for 3σ |
|---|---|---|---|---|
| `pool128` | 2 | −0.00409 | 3.6 | ≤1 |
| `pool32` / `pool64` | 3 | −0.00699 / −0.00548 | 6.3 / 4.8 | ≤1 |
| `pool16` | 8 | −0.00765 | 6.8 | ≤1 |
| `pool8` | 10 | −0.00685 | 6.1 | ≤1 |
| `side` | 4 | −0.00477 | 4.3 | ≤1 |
| `pool4` | 29 | −0.00884 | 7.9 | ≤1 |
| `pool2` | 90 | −0.00801 | 7.0 | ≤1 |
| `cell_class` | 12 | −0.00319 | **2.8** | 1.1 |
| `ito_lee_hemilineage` | 212 | −0.00296 | 9.2 | ≤1 |
| `supertype` | 508 | −0.00145 | 4.2 | ≤1 |
| `pool1` / `cell_type` | 812 | +0.00019 / +0.00026 | 0.4 / 0.7 | infeasible |

**The rung-level claim needs no new compute.** Every coarse rung is 2.8–7.9σ with the single
draw it already has, and averaging would add nothing. The ladder's headline survives as a
statement about *which* granularities help, at 3–8σ rather than 20–42σ. `cell_class` at 2.8σ is
the weakest and should be quoted as marginal; `pool1`/`cell_type` is a confirmed null.

## 4. Shape claims: the curve has coarse structure that is testable and fine structure that is not

Does rung X differ from rung Y? ``σ at K=1`` is with the single draw the ladder used; ``floor`` is
the best achievable with the **current 12-seed budget** if the draw noise were eliminated
entirely (``|Δ| / (sqrt(2) sem_seed)`` — the sqrt(2) because a contrast has two arms). If the
floor is below 3σ, no number of draws helps. The last column is the prediction for the
experiment in §5.

| contrast | Δ of deltas | σ at K=1 | floor | **K for 3σ** | σ at K=4 |
|---|---|---|---|---|---|
| `side → pool4` | −0.00407 | 2.58 | 10.8 | **2.8** | **3.50** |
| `pool2 → cell_class` | +0.00482 | 2.99 | 8.2 | **2.2** | **3.86** |
| `pool128 → pool32` | −0.00289 | 1.83 | 7.0 | **6.4** | 2.46 |
| `pool8 → side` | +0.00208 | 1.32 | 5.2 | 15.0 | 1.78 |
| `pool64 → pool16` | −0.00217 | 1.36 | 4.7 | 15.8 | 1.82 |
| `pool32 → pool64` (true Δ = 0) | +0.00150 | 0.95 | 3.3 | 109 | 1.26 |
| `ito_lee_hemilineage → supertype` | +0.00152 | 3.20 | **2.3** | infeasible | 2.29 |
| `supertype → pool1` | +0.00164 | 2.65 | 1.9 | infeasible | 1.89 |
| `pool16 → pool8` | +0.00080 | 0.50 | 1.9 | infeasible | 0.68 |
| **`pool4 → pool2`** | +0.00084 | 0.52 | **1.5** | **infeasible** | **0.68** |
| `cell_class → ito_lee_hemilineage` | +0.00023 | 0.19 | 0.4 | infeasible | 0.23 |
| `pool1 → cell_type` (true Δ = 0) | +0.00007 | 0.11 | 0.1 | infeasible | 0.08 |

Three things follow.

**The two large steps are testable at K ≈ 2–3.** `side → pool4` (the claim that a pooled
partition beats the annotation vocabulary's own best rung) and `pool2 → cell_class` (the biggest
single drop in the curve) both come inside 3σ with three draws per rung; `pool128 → pool32` needs
six. This is the first time those claims have been anything other than a guess.

**The plateau's internal structure is not testable.** `pool4 → pool2`, the contrast the earlier
fire read the plateau from, has a floor of **1.5σ** at 12 seeds: even with the draw noise removed
it cannot reach 3σ, and removing draw noise entirely is impossible. Its neighbours `pool16 →
pool8` (1.9σ) and `supertype → pool1` (1.9σ) are in the same position. So "a plateau spanning
0.32–0.67" is not a resolution problem that more compute fixes — with this seed budget it is
**not a resolvable claim at all**, and the region should be reported as a broad band rather than
as a curve with internal structure.

**Two contrasts have a known true value of zero, and both behave.** `pool32 → pool64` and
`pool1 → cell_type` are duplicate partitions; the model puts the first at 0.95σ and the second at
0.11σ. The seed-only method called them 4.7σ and 0.13σ — overstating one by five-fold and correct
on the other, exactly as the sign of the correlation with granularity would predict.

## 5. The concrete next experiment

**Run the ladder with `--control-draws 4`.** Cost is 5× the control arm (8 biological + 32
controls + one diagonal ≈ 41 bases versus 17), or 12 seeds × 41 bases ≈ 5 h at the measured
37 s per base-seed. The biological arm need not be recomputed if the seeds are matched, which
halves it.

The prediction to test is specific, and stated in advance, from the last column of §4: at K=4 the
two biggest steps come out at **3.86σ** (`pool2 → cell_class`) and **3.50σ** (`side → pool4`),
`pool128 → pool32` at 2.46σ (it needs K=6.4 to clear 3σ), and **every small step stays at 0.68σ
or below** — `pool4 → pool2` at 0.68σ, `pool16 → pool8` at 0.68σ. If instead the small steps
resolve, the draw-sd estimate is too large and E12 needs revisiting; if the large steps fail to
resolve, the seed budget is the binding constraint and the rung-level claim is weaker than §3
says. Either outcome is informative, which is the point of writing the prediction down first.

**Deferred, not blocked.** The machine is running three long jobs using ~17 of 20 cores, so a
fifth compute-bound job would slow all of them; the run is scheduled for when cores free up.

## 6. Limits

- `sd_draw` is **measured** at ≤12 groups (1.06e-3 at 3 groups, 1.08e-3 at 8) and at ≥200 groups
  (4e-5 at 812, 9e-5 at 812 on a second circuit), and **interpolated** at 29, 90, 141 and 212
  groups. Every rung in §4 with a large required K sits in the interpolated region, so the
  ranking of K is more trustworthy than any individual value. The e12-per-rung measurement
  (`e12_control_spread --min-size N`) settles one rung at a time.
- The ``floor`` column is conditioned on **12 seeds**; more seeds lower it, so "infeasible"
  means "infeasible at this seed budget", and the fine contrasts could be bought with seeds
  instead. They would then not be *free* claims, which is the practical content of the column.
- "3σ" is a convention, not a law. Every K in §4 scales as ``1/target_sigma^2``, so a 2σ bar is
  ~2.3× cheaper and a 4σ bar ~1.8× dearer.
- The biological arm's own seed sem varies by rung (0.00005 at `pool4` to 0.00051 at `pool1`),
  so the floor is not uniform across the curve and the small-Δ rows are not all limited by the
  same thing.
