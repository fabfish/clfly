# The gap is chaotic — a metric correction that qualifies e2, e3 and e5

**Date:** 2026-09-22
**Scripts:** `experiments/e5_anisotropy_axis.py`, `clfly/bench/oracle.py`
**Artifacts:** `runs/e5_anisotropy.json`

---

## 0. Summary

The quantity every experiment in this project has been reporting — the *relative*
gap between EWC's error and the Kalman oracle's — turns out not to be a usable
statistic on this substrate. Its standard deviation across seeds reaches **1.06
while its mean is 0.87**, and it moves by ±0.04 under a **1e-15 relative** change
in a single model parameter. Trends read off it, including the U-shape reported in
the previous fire, are not established.

This fire was supposed to explain e5's U-shape. It found the U-shape is a property
of the metric, not of the system, and fixed the measurement.

## 1. First: a reproducibility failure, found and fixed

`e5` re-run with identical arguments gave different gap values while the task
*geometry* was bit-identical to four decimals. Tracing it:

| stage | bit-identical across calls? |
|---|---|
| `stable_weights` (`spla.eigs`) | **No** — `max|ΔW| = 1.1e-16` |
| `build_tasks` (from `W`) | No — `max|ΔJ| = 9.7e-13` |
| `gap_vs_oracle` on a *fixed* seq | Yes — identical to 6 decimals |

Cause: `scipy.sparse.linalg.eigs` starts from a **random vector** when `v0` is not
given, so the converged spectral radius varies in its last bits and the rescaling
factor with it. One ULP in `W` became ~1e-12 in `J`, which moved the reported gap
by several percent.

Fixed by passing a deterministic start vector. `stable_weights` and `build_tasks`
are now bit-identical across calls, and the gap on a fixed sequence reproduces
exactly. **This was a real bug and it is now closed.**

## 2. Second, and worse: fixing the bug did not make the metric stable

With bit-identical inputs, varying one parameter by an absurdly small amount:

| relative change in ρ | change in reported gap |
|---|---|
| 1e-15 | **+0.024** |
| 1e-13 | +0.017 |
| 1e-11 | +0.044 |
| 1e-9 | −0.008 |

A 1e-15 relative perturbation is four ULPs. The gap responds by ±0.04. So this is
not a numerical defect to be removed — the gap is a chaotic functional of its
inputs, and *any* change of environment (different BLAS, different machine,
different scipy) will move it.

Equally damning across seeds, at **fixed settings** — same circuit, same support
size, same κ, only the task seed varies:

| κ | gap at seed 0 | seed 1 | seed 2 | **gap spread** | flattening spread |
|---|---|---|---|---|---|
| 0 | +0.062 | +0.576 | +0.370 | **0.514** | 0.009 |
| 0.25 | +0.105 | +0.225 | +0.367 | 0.262 | 0.006 |
| 0.5 | +0.077 | +0.267 | +0.330 | 0.252 | 0.012 |
| 1 | +0.134 | +0.149 | +0.189 | 0.056 | 0.052 |
| 1.75 | +0.240 | +0.338 | +0.580 | 0.340 | 0.052 |
| 2.5 | +0.365 | +0.297 | +1.509 | **1.212** | 0.038 |
| 4 | +1.208 | +1.393 | +0.009 | **1.384** | 0.021 |

The gap moves by **up to 1.38** across seeds while the task geometry it is supposed
to be a function of moves by at most 0.012. The task construction is stable; the
gap is not a function of it in any usable sense.

Row-wise means are `+0.336, +0.232, +0.225, +0.157, +0.386, +0.724, +0.870`:
non-monotone, and dominated by two very large values at κ=2.5 and κ=4. A
separate diagnostic at a different circuit size and support (400 neurons, support
40, 3 seeds) reproduced the same behaviour and gave gap standard deviations up to
1.06 against a mean of 0.87, with the oracle's own error stable to 0.0013.

**Three seeds is not enough to resolve anything at this noise level.** The
`runs/e5_anisotropy.json` from this fire records the per-seed points (which is what
matters) but its `pooled` block is `n=1` — an indentation bug put the pooling
inside the seed loop, so each seed overwrote the previous pool with a
single-sequence one whose sem is trivially zero. Fixed in the script; the corrected
pooled run is queued as the next step rather than reported here as if it existed.

## 3. Why — and what to report instead

The gap is a **ratio of two small, close numbers**. At κ=0 the EWC error is 0.072
and the oracle's is 0.038, so the excess is 0.033 and the ratio is 0.87. The ratio
therefore inherits the *relative* variance of the EWC error, which is ~53%
(sd 0.038 on mean 0.072). Propagating: `sd[ewc/oracle] ≈ sd_ewc/oracle ≈ 1.0`,
exactly as measured.

Two things are stable, and they are the ones to report:

- **The oracle's error** (sd 0.0013 on mean 0.038 — a 3% relative spread). It is
  well conditioned because it *does not project anything*, so there is no
  cancellation to amplify.
- **The absolute excess** `ewc_mean − oracle_mean` averaged over seeds. Its
  per-seed spread is dictated by the EWC estimator's own variance, so it must come
  with a standard error across ≥3 seeds. At these settings the standard error is
  ~0.02, which means **differences below roughly 0.05 are not resolvable.**

`paired_excess` in `clfly/bench/oracle.py` now returns the excess with its sem,
the ratio for continuity, and — the calmest form if a ratio is wanted —
`gap_of_means`, the excess divided by the *averaged* oracle error.

## 4. Retraction: e5's U-shape was a metric artefact

E5 reported a U-shaped gap in task spectral concentration with a minimum at
κ≈0.5. On the stable scale, the excess declines monotonically:

    excess:  +0.0335  +0.0371  +0.0354  +0.0239  +0.0237  +0.0034  +0.0072

No intermediate minimum. The dip was the ratio metric's noise.

**And the direction reverses again.** On the ratio, e5 concluded "more anisotropy →
larger gap" (ρ = −0.93 against flattening). On the excess, the trend is downward in
κ, i.e. **more anisotropy → smaller excess** — back in the direction e2 had. So the
sign of the headline relationship depends entirely on which metric is used, and one
of the two metrics is unusable.

Given the standard errors, even the monotone decline is only marginally resolved
(a total change of 0.026 against a per-point sem near 0.02). Stated plainly: **the
anisotropy–gap relationship on this substrate is not yet established in either
direction.** That supersedes what e5 claimed.

## 5. Two further corrections

**`gain_mismatch_excess` is identically zero for these filters.** The LGCL appendix
identity prices a *single* covariance compression as a gain error. A recursively
projected filter's prior already lives inside the basis family, so re-projecting it
changes nothing and the per-step cost is exactly 0. Measured: a flat array of zeros
for `basis=Diagonal`. This is not a bug — it is the quantitative form of LGCL v8's
lemma that *all* of the diagonalisation penalty is cumulative. Its docstring now
says so, and `diagonalisation_pressure` reports it knowing it will be zero.

**`task_subspaces` at the numerical rank returns the full range space.** For these
rank-deficient tasks that space is determined by *which* neurons the assembly
recruited and is independent of how strongly each is driven: the subspaces came out
**bit-identical** across a 15× change in drive concentration that moves the
effective rank from 55 to 3.5. A predictor built on that space cannot see the
spectral structure it is meant to test — which is the most likely reason the
principal-angle alignment scalar failed to rank the anchoring bases in e3.

This also explains an anomaly left open last fire: the constant cross-task
`overlap` of 0.0061 across every κ. The subspaces really do not move; they are
range spaces of the propagator's columns on fixed supports. `task_subspaces` now
takes a `top` argument for a spectrally *selected* subspace.

## 6. Consequences for previously reported results

| result | status after this fire |
|---|---|
| e3: gap is 45–63% on wiring tasks vs <1% synthetic | **Directionally safe.** The effect is large (excess 0.033 on an oracle error of 0.038) and far above the noise floor. **Corrected 2026-09-23:** the 45–63% range matched no artifact — the contrast is +33.5% analytic / +35.8% realized at 5 seeds (`docs/findings/2026-09-23-the-realization-range-has-no-artifact.md`). |
| e3: bio beats matched random at 4/5 rungs | **At risk.** Deltas 0.05–0.12 against a resolvable threshold near 0.05; `supertype`'s 0.049 is not resolvable. Needs re-running on the excess scale. |
| e3: the alignment predictor fails | **Strengthened**, with a mechanism now identified (range-space degeneracy). |
| e2: geometry degrades monotonically under rewiring | **Safe.** Geometry is computed from eigenvectors, not from the ratio, and is bit-reproducible. |
| e2: gap moves opposite to overlap | **At risk.** The trajectory 0.634 → 0.226 spans more than the noise floor in total but not point-to-point. Needs re-running. |
| e2: bio−rand flips sign under rewiring | **At risk**, same reason. |
| e5: U-shape in concentration | **Retracted.** |

Next fire: re-run e2 and e3 on the excess scale with ≥3 seeds and standard errors,
and replace the failed alignment predictor with a spectrally selected one.
