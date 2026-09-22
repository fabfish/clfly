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
| `side → pool4` | −0.00407 | 2.58 | 15.2 | **1.4** | **4.95** |
| `pool2 → cell_class` | +0.00482 | 2.99 | 11.6 | **1.0** | **5.46** |
| `pool128 → pool32` | −0.00289 | 1.83 | 9.8 | **2.9** | 3.48 |
| `pool8 → side` | +0.00208 | 1.32 | 7.4 | 6.0 | 2.52 |
| `pool64 → pool16` | −0.00217 | 1.36 | 6.6 | 5.8 | 2.57 |
| `pool32 → pool64` (true Δ = 0) | +0.00150 | 0.95 | 4.7 | 16.4 | 1.78 |
| `ito_lee_hemilineage → supertype` | +0.00152 | 3.20 | 3.3 | 0.2 | 3.24 |
| `supertype → pool1` | +0.00164 | 2.65 | 2.7 | infeasible | 2.67 |
| `pool16 → pool8` | +0.00080 | 0.50 | 2.7 | infeasible | 0.96 |
| **`pool4 → pool2`** | +0.00084 | 0.52 | **2.2** | **infeasible** | 0.96 |
| `cell_class → ito_lee_hemilineage` | +0.00023 | 0.19 | 0.5 | infeasible | 0.33 |
| `pool1 → cell_type` (true Δ = 0) | +0.00007 | 0.11 | 0.1 | infeasible | 0.11 |

> **These numbers were wrong once, by a factor of two, and the error is worth reading.** The first
> version of `draws_needed` took a ``contrast`` flag and multiplied by ``sqrt(2)`` itself, while the
> caller had *already* combined the two rungs in quadrature — so the factor was applied twice, every
> ``K`` came out ~2× too large, and `ito_lee_hemilineage → supertype` was reported **infeasible**
> when its floor is 3.3σ and it is in fact settled by the single draw it has. The symptom was
> visible in the published table: a row whose floor (3.3σ) was above the target while its ``K``
> column said "infeasible". Nothing in the project checks that invariant, and nobody looked. It is a
> test now, and the flag is gone — the function takes the claim's two error terms already combined,
> which removes the chance of double-counting at the source.

Three things follow.

**The two large steps are testable at K ≈ 1–1.4.** `side → pool4` (the claim that a pooled
partition beats the annotation vocabulary's own best rung) and `pool2 → cell_class` (the biggest
single drop in the curve) clear 3σ with **two** draws per rung — one draw already gets them to
2.6σ and 3.0σ. `pool128 → pool32` needs three. This is the first time those claims have been
anything other than a guess, and they are cheaper than the first estimate said.

**The plateau's internal structure is not testable.** `pool4 → pool2`, the contrast the earlier
fire read the plateau from, has a floor of **2.2σ** at 12 seeds: even with the draw noise removed
it cannot reach 3σ, and removing draw noise entirely is impossible. Its neighbours `pool16 →
pool8` (2.7σ) and `supertype → pool1` (2.7σ) and `cell_class → ito_lee_hemilineage` (0.5σ) are in
the same position. So "a plateau spanning 0.32–0.67" is not a resolution problem that more compute
fixes — with this seed budget it is **not a resolvable claim at all**, and the region should be
reported as a broad band rather than as a curve with internal structure.

**Two contrasts have a known true value of zero, and both behave.** `pool32 → pool64` and
`pool1 → cell_type` are duplicate partitions; the model puts the first at 0.95σ and the second at
0.11σ. The seed-only method called them 4.7σ and 0.13σ — overstating one by five-fold and correct
on the other, exactly as the sign of the correlation with granularity would predict.

## 5. The concrete next experiment

**Run the ladder with `--control-draws 4`.** Cost is 5× the control arm (8 biological + 32
controls + one diagonal ≈ 41 bases versus 17), or 12 seeds × 41 bases ≈ 5 h at the measured
37 s per base-seed. The biological arm need not be recomputed if the seeds are matched, which
halves it. However, K=4 is more than either of the two claims needs (§4: K ≈ 1–1.4), so the
targeted version — three rungs, K=4, 15 bases ≈ 1.9 h — is the better buy
(`docs/findings/2026-09-22-artifacts-and-targeted-rungs.md`).

The prediction to test is specific, and stated in advance, from the last column of §4: at K=4 the
two biggest steps come out at **5.46σ** (`pool2 → cell_class`) and **4.95σ** (`side → pool4`),
`pool128 → pool32` at 3.48σ, and **every small step stays at 0.96σ or below** — `pool4 → pool2` at
0.96σ, `pool16 → pool8` at 0.96σ. If instead the small steps
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

## 7. Sensitivity: which verdicts can be overturned by measuring `sd_draw`?

`sd_draw` is the one quantity in §4 that is **interpolated** for rungs of 29–212 groups, which is
exactly where the two claims worth buying live. So the obvious question is which conclusions would
move if the interpolation is wrong. Scaling each contrast's **own** two-rung draw sd by a factor:

| contrast | floor | ×0.27 | ×0.5 | **×1** | ×2 |
|---|---|---|---|---|---|
| `pool128 → pool32` | 9.8 | 0.2 | 0.7 | 2.9 | 11.5 |
| `pool32 → pool64` (true Δ = 0) | 4.7 | 1.2 | 4.1 | 16.4 | 65.6 |
| `pool64 → pool16` | 6.6 | 0.4 | 1.5 | 5.8 | 23.4 |
| `pool8 → side` | 7.4 | 0.4 | 1.5 | 6.0 | 24.1 |
| `side → pool4` | 15.2 | 0.1 | 0.3 | **1.4** | 5.5 |
| `pool2 → cell_class` | 11.6 | 0.1 | 0.3 | **1.0** | 4.0 |
| `pool16 → pool8` | 2.7 | inf | inf | inf | inf |
| `pool4 → pool2` | 2.2 | inf | inf | inf | inf |
| `cell_class → ito_lee_hemilineage` | 0.5 | inf | inf | inf | inf |
| `ito_lee_hemilineage → supertype` | 3.3 | 0.0 | 0.0 | 0.2 | 0.7 |
| `supertype → pool1` | 2.7 | inf | inf | inf | inf |
| `pool1 → cell_type` (true Δ = 0) | 0.1 | inf | inf | inf | inf |

**The infeasible verdicts are immune to this parameter.** The floor is ``|Δ| / sem_seed`` — the
claim's two arms already combined — and it contains no ``sd_draw`` at all: it is the best the
**seed budget** can deliver once the draw noise is gone entirely. So "the curve's internal steps
are not a resolvable claim" cannot be overturned by measuring the draw sd better; it would take
more seeds, and §6 notes what
that would cost. This is the main conclusion of the analysis, and it is now known to rest on the
seed sems alone. (An earlier version of this table wrote the floor with a spurious ``sqrt(2)``, the
same double-count as §4, which made the floors depend on ``sd_draw`` only through an arithmetic
error — the five ``inf`` rows were invariant then too, for the right reason, by accident.)

**The two claims worth buying are robust too.** ``side → pool4`` and ``pool2 → cell_class`` need
``K ≤ 5.5`` even if the interpolation is wrong by a factor of two in the unfavourable direction, and
``K ≈ 0.2`` — i.e. one draw already suffices — at the low end. Their required K scales as
``sd_draw^2``, as the formula says, so the planned ``K = 4`` run is comfortably above what either
claim needs at the central estimate and still enough at the pessimistic one.

**One row is fragile, and it is not a real claim.** ``pool32 → pool64`` moves from ``K = 1.2`` to
``K = 66`` across the same range. Its true Δ is zero — it is the noise probe — so the number is
meaningless as a requirement, but it is the clearest illustration of why a claim whose floor is
just above the target is not a claim: the cost of settling it is set by how far above the floor it
sits, divided by everything else.

## 8. First measurement replacing the interpolation

`e14` measures the draw sd **at d = 1307, on the same circuit as the ladder**, by varying the
pooling threshold — a direct check of the one quantity §4 had to interpolate. First result
(`runs/e14_drawsd_min2.json`, min_size 2 → 90 groups, 3 seeds, 5 draws):

| quantity | value |
|---|---|
| across-draw sd | **0.000929** |
| interpolated value used in §4 | 0.0011 |
| per-draw control means | 0.01141, 0.01253, 0.01213, 0.01285, 0.01392 |
| spread of those means | **0.00251** |

Two things follow.

**The interpolation was good to 15%**, and the verdicts are unchanged: the honest σ for the
`pool2` rung becomes 8.2σ rather than 7.0σ, and its required K stays below 1.

**The spread of the control means is 0.00251, on the same scale as every shape contrast in §4**
(0.0008–0.0048). That is the finding stated as a single number: the arbitrariness of *which*
random partition you draw is as large as the differences three fires were arguing about.

The `--seeds 3` in this run is deliberate but worth flagging: the draw sd is estimated from
per-draw means that each average 3 seeds, so it carries a ``sigma_epsilon^2/3`` term that more
seeds would shrink. It is therefore an *upper* estimate of the pure draw sd, which is the safe
direction for a budget calculation.

The remaining measurements (51, 29 and 12 groups) are in the same run. `side` is **not** covered —
it is a balanced 4-group partition rather than an unbalanced pooled one, and §4 of
`docs/findings/2026-09-22-artifacts-and-targeted-rungs.md` says why that may matter.
