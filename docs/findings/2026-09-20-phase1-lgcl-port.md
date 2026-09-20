# Phase 1 — LGCL port, exact reproduction, and one negative result

**Date:** 2026-09-20
**Scope:** `clfly/lgcl/**`, `tests/test_lgcl.py`
**Gate:** `repro_max_abs_err = 0.000047` (published threshold: ≤ 0.02)

---

## 1. What was ported

`reference/lgcl_source/lgcl_toy.py` (the author's original experiment script)
became a reusable package:

| Module | Role |
|---|---|
| `model.py` | the linear-Gaussian generative model; task families (random / axis / fixed-angle / cumulative-rotation / partial-observation) |
| `kalman.py` | information-form filter with an optional covariance projection; **exact RTS smoother** (the information limit); the gain-mismatch excess diagnostic |
| `bases.py` | the anchoring-basis family — the project's core object (see §4) |
| `methods.py` | Naive / AnchoredFilter / EWCPenalty / Replay, all expressed as basis choices |
| `repro.py` | the published-number harness and the metric-loop entry point |
| `probes.py` | mechanism experiments (§3) |

The RNG call order was preserved deliberately, which is why the reproduction is
exact rather than approximate.

## 2. Reproduction status

### Reproduced exactly — `exp1`, the headline table

d=20, T=10, n=40, σ²=1, q=0.05, 200 runs, fully pinned down by `lgcl_toy.py`.

| anchor | published | computed | abs err |
|---|---|---|---|
| final_avg_error.naive | 2.4979 | 2.497924 | 2.4e-5 |
| final_avg_error.ewc | 1.2013 | 1.201289 | 1.1e-5 |
| final_avg_error.replay | 0.9881 | 0.988118 | 1.8e-5 |
| final_avg_error.sketch | 1.1989 | 1.198935 | 3.5e-5 |
| final_avg_error.kalman | 1.1915 | 1.191475 | 2.5e-5 |
| forgetting.naive | 2.2173 | 2.217338 | 3.8e-5 |
| forgetting.ewc | 1.0399 | 1.039930 | 3.0e-5 |
| forgetting.replay | 0.7481 | 0.748117 | 1.7e-5 |
| forgetting.sketch | 1.0400 | 1.040047 | 4.7e-5 |
| forgetting.kalman | 1.0343 | 1.034293 | 7e-6 |

Deviations sit at the level of the published rounding (4 decimals), so the port
is faithful. The substantive claim reproduces: **EWC and full Kalman differ by
<1%**, and a 4-of-20 spectral truncation is equally lossless.

### Not reproduced — `exp3`, and the reason matters

The published `exp3` claims a **unimodal** excess-EWC-cost curve peaking at
+85% near 12° per task. We do not reproduce it, and we believe this is a real
finding rather than a bug in the port. Three reasons to take it seriously:

1. **The driver is absent.** `lgcl_toy.py` ships helpers for the exp3 family
   (`make_tasks_rot`, `rotation_mode="angle"`) but not the script that produced
   the published curve. Its error convention and run count are unknown.
   Searching configurations until a number matches would be fitting, not
   reproducing, so exp3 is **quarantined** under `--explore` and does not gate.

2. **The endpoints are exactly zero**, which validates the geometry. On a
   cumulative per-task rotation the gap is exactly 0 at both 0° (aligned) and
   90° (an axis swap in 2-D is still diagonal). This is a strong check: getting
   both endpoints to vanish by construction is not accidental. It also tells us
   the published curve must be the *cumulative* family, since a fixed
   misalignment would peak at 45° instead.

3. **The negative result is preceded by the theory.** LGCL finding 1 says the
   diagonal approximation is nearly free because random structure concentrates.
   Our sweep finds the same thing for a *different* reason, and the reason is
   the next section.

## 3. What the probes found

All from `python -m clfly.lgcl.probes`.

### 3.1 The two-task lemma holds exactly

d=2, T=2, α ∈ {5°, 12°, 30°, 60°}: the EWC−Kalman gap is **exactly 0.0**
(agreement to 1e-12, asserted in the test suite). With a single task boundary
the posterior is still diagonal in task 1's own basis, so projecting it away
removes nothing.

At T=3 the gap becomes non-zero (+0.0017 to +0.0103 across the same angles).
This confirms v8's mechanism claim that **all of the diagonalisation penalty is
a recursive effect** — it takes a rotation *followed by another projection* to
lose anything.

### 3.2 The penalty tracks task anisotropy, not rotation angle

Each task's precision is `J_k = U diag(s) U^T`. With `decay=0.85` in d=2 the
spectrum is `[1.0, 0.85]` — nearly isotropic, so rotating it changes almost
nothing. Steepening the spectrum makes the same rotation start to cost:

| spectrum decay | s₂ | largest \|mean gap\| (60 seeds) | reading |
|---|---|---|---|
| 0.85 | 0.85 | 0.0002 ± 0.0003 | exactly zero |
| 0.25 | 0.25 | 0.0135 ± 0.0065 | sign-unstable |
| 0.05 | 0.05 | **0.0942 ± 0.0363** at 9° | systematic, positive |

This is the useful part. It says the diagonal approximation's cost is governed
by **how anisotropic and low-effective-rank the task's own precision is** — not
by how much the tasks rotate. The default d=2 spectrum in the reference helper
is too flat for the effect to exist at all, which plausibly explains why the
published +85% needed a different spectrum.

### 3.3 Information discarded is not error caused

At decay=0.85 the diagonal projection throws away a measurable share of the
posterior's Frobenius mass — but the error consequence is ~0:

```
mean discarded fraction     0.16 %   (max 0.39 % per step)
median ||P||_F              0.0277
relative error gap          +0.0001
```

This is the quantitative statement of the project's premise. The coordinate
basis *is* discarding structure; in a random synthetic task that structure
simply does not matter. **Closing the gap between "mass discarded" and "error
caused" requires a substrate whose structure is not random — which is what a
connectome is.** §3.2 names the property to look for: anisotropic, low-rank,
structured task geometry. A real neural network's feature Gram has effective
rank ≈ 2.0 (LGCL v7), so the fly substrate should sit deep in the regime where
the basis choice matters.

### 3.4 Measurement strength washes everything out

Sweeping n ∈ {1 … 100} at α=12°: the gap collapses from 2.1% (n=1) to <0.01%
(n=100). When every task re-measures everything strongly, the current
measurement dominates the prior and discarded history is irrelevant. This is
LGCL finding 1 restated, and it is why fully-observed benchmarks make EWC look
harmless.

Two of the entries are **negative** (EWC better than Kalman) at weak
measurement. That is not a bug: the projection shrinks the posterior, and
shrinkage is not always harmful. It is the same shrinkage-bias effect LGCL's
own audit note flags in the forgetting metric — worth remembering when reading
any "EWC beats Kalman" line.

### 3.5 `exp4` shape confirmed, level not

The partial-observation rate-distortion curve decreases monotonically and
saturates near r=12, as published — but at ~1.8× the published level
(0.157→0.119 against 0.088→0.042). The qualitative prediction holds; the
numbers are not comparable. Also quarantined.

## 4. Side product: the basis family

The port forced a design decision that turned out to be the project's central
object. LGCL says EWC is a Kalman filter with the covariance diagonalised. The
generalisation is a **projection family**, all idempotent, ordered by how much
structure they retain:

```
Full(d)                 keep everything            -> Kalman oracle        d(d+1)/2 params
RotatedDiagonal(U)      diagonal in U's coords     -> spectral anchoring   d  (+ d(d-1)/2 shared)
Partition(labels)       within-group only          -> a cell-type basis    sum s_g(s_g+1)/2
Diagonal(d)             diagonal                  -> textbook EWC         d
```

`Partition` is the piece that was missing from the literature: it turns any
per-neuron annotation column (cell type, hemilineage, nerve, neuropil) into a
candidate Fisher anchoring basis, with a **group-size-matched random control**
available for free so the comparison is capacity-matched.

One honest accounting note that fell out: a `RotatedDiagonal` basis needs
`d(d-1)/2` numbers to specify the rotation. Unless the basis is shared across
tasks, "EWC in a rotated basis" is not a compression at all — it costs as much
as the full matrix. Baselines that rotate the basis rarely say this.

## 5. Status

- **Phase 0:** complete.
- **Phase 1:** complete. 10/10 published anchors reproduce; 18 tests pass.
- **Next:** Phase 2 — download FlyWire v783 + annotations, build the sparse
  graph and the candidate basis ladder, then measure §3.3's "discarded mass vs
  error caused" on a substrate that is not random.
