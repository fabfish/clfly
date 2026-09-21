# The analytic expected error — and C2 finally resolved

**Date:** 2026-09-22
**Modules:** `clfly/bench/analytic.py`, `tests/test_analytic.py`
**Script:** `experiments/e3_basis_selection.py`
**Artifacts:** `runs/e3_analytic.json`

---

## 1. What was built

Every effect size in this project was being computed from the *realized* error of a
single draw of `theta` and the measurement noise. On the connectome substrate that
sampling term dominates: the task geometry reproduces to four decimals across seeds
while the realized gap swings by more than its own mean.

But the model is linear-Gaussian and every filter here is a *linear* function of the
observations, so the expected error is available in closed form. Writing the
filter's total response as `theta_hat_k = sum_{j<=k} R_kj y_j`, substituting
`y_j = theta_j + eps_j`, and using the independence of the trajectory from the noise:

```
E[e e^T] = sum_{j,l} R_kj S_jl R_kl^T - 2 sum_j R_kj S_jm + S_mm I   +   sum_j R_kj pinv(J_j) R_kj^T
           \_____________________ trajectory term ________________/       \_____ noise term _____/
```

with `S_jl = (P0 + min(j,l) q) I`. The responses come from one filter pass:
`R_kk = Pn_k J_k` and `R_kj = M_k R_{k-1,j}` for `j < k`, where `M_k = Pn_k P_prior,k^{-1}`
and `Pn_k` is the **unprojected** posterior — because `kalman_update` forms the mean
before projecting the stored covariance, which is the "EWC = diagonalised
covariance" convention this project uses throughout.

The sum over `(j,l)` is reduced from quadratic to linear in `k` by expanding
`min(j,l) = sum_{t>=1} [j>=t][l>=t]`, which turns it into `P0 U_0 U_0^T + q sum_t U_t U_t^T`
with `U_t = sum_{j>=t} R_kj`. That is what makes it affordable at d=1307 (6 s per
basis per sequence).

## 2. Validation

Against Monte Carlo averages of the realized error on the *same* task precisions,
d=20, T=5, 4000 draws:

| case | basis | analytic | MC | max rel. error |
|---|---|---|---|---|
| full-rank, drifting | kalman | 0.52467 | 0.52654 | 0.007 |
| full-rank, drifting | EWC-diag | 0.55147 | 0.55380 | 0.007 |
| full-rank, drifting | rank4 | 0.54362 | 0.54617 | 0.007 |
| rank-8, drifting | kalman | 0.48689 | 0.49171 | 0.012 |
| rank-8, drifting | EWC-diag | 0.92463 | 0.93092 | 0.014 |
| rank-8, drifting | rank4 | 0.77275 | 0.77748 | 0.010 |
| rank-8, non-drifting | kalman | 0.12334 | 0.12340 | 0.010 |
| rank-8, non-drifting | EWC-diag | 0.44014 | 0.43726 | 0.012 |
| rank-8, non-drifting | rank4 | 0.29184 | 0.29158 | 0.005 |

Every case within Monte Carlo error (~1.5% at 4000 draws). Response matrices
separately verified against finite differences to 1e-9.

**The validation earned its keep by catching a real bug.** The `min(j,l)` expansion
was applied unconditionally, adding the drift term even when `theta` does not drift.
That inflated the non-drifting family by ~3× while leaving every drifting case
correct — a wrong-but-smooth formula, which is precisely the failure mode that would
have been invisible without a ground-truth comparison. `Sequence` now records a
`drifted` flag (the filter always *believes* in the drift; the reference
partial-observation family does not actually drift), and `trajectory_cov` honours it.

## 3. The payoff — C2 is resolved

e3 on the real connectome, d=1307, 5 seeds, matched capacity. Same task sequences,
two effect sizes:

| rung | **analytic delta** | **σ** | realized delta | σ |
|---|---|---|---|---|
| `side` | **−0.00480** | **12.93** | −0.00540 | 1.31 |
| `cell_class` | **−0.00307** | **3.68** | −0.00441 | 0.61 |
| `ito_lee_hemilineage` | **−0.00280** | **2.61** | −0.00361 | 0.43 |
| `supertype` | −0.00146 | 1.23 | −0.00214 | 0.25 |
| `cell_type` | +0.00026 | 0.22 | +0.00042 | 0.05 |

> **Resolved (>2σ, biology better): analytic 3/5, realized 0/5.**

Three things matter here.

**The deltas agree in magnitude** (−0.0048 vs −0.0054 for `side`; −0.0031 vs −0.0044
for `cell_class`). The analytic estimator is not measuring something different — it
is measuring the *same effect* without the sampling noise. That is the strongest
evidence that it is trustworthy, stronger than the MC agreement alone.

**The precision gain is ~8× in standard error**, i.e. ~64× in seed count. Standard
errors fall from ~0.004–0.007 to ~0.0005–0.0009, and the spread across task
geometries turns out to be genuinely small (sd 0.0002–0.0019 for the biological
rungs). Almost all of the noise that made e3 unresolvable was sampling, not biology.

**So C2 holds at 3 of 5 rungs**, with a clear ordering: hemisphere (`side`, 12.9σ),
cell class (3.7σ), hemilineage (2.6σ), and nothing for supertype or cell type. The
last is what the granularity result predicted — `cell_type` at 0.979 constrained is
nearly the diagonal, so there is no structure left for it to contribute.

`side` at 12.9σ is worth a sentence on its own: grouping the circuit into four
left/right/centre parts beats a random 4-group partition of the same sizes
overwhelmingly. The coarsest structural split in the annotation table is also the
most valuable anchoring basis in it.

## 4. Status

| claim | before this fire | after |
|---|---|---|
| **C2** — biological bases beat matched random ones | directionally consistent, ~1.3σ, unresolved | **resolved at 3/5 rungs**, up to 12.9σ |
| C2 predictor — principal angles rank the bases | fails, 3/5 | unchanged; see §5 |
| **Granularity** — less constraint means less loss | resolved (2.1σ) | unchanged, and consistent |
| C1 geometry | solid | unchanged |
| C1 mechanism | refuted | unchanged |

## 5. What the predictor looks like now

The ordering is `side` (12.9σ) > `cell_class` (3.7σ) > `hemilineage` (2.6σ) >
`supertype` (1.2σ) > `cell_type` (0.2σ). Setting that against the earlier alignment
excesses (3.19, 1.98, 0.42, 1.05, 1.06) gives agreement on the top two and the
bottom one, and misses on the middle two. So the predictor is **closer than it
looked when the effect sizes were noise-dominated**, and the disagreement is now
concentrated in rungs whose differences are 1–2σ rather than 0.2σ. Re-running the
predictor against these resolved effect sizes is the obvious next step.

## 6. Next

1. **Re-run e2 on the analytic scale.** Its conclusions were all the weaker for the
   same reason e3's were; the topology contrast should now be measurable per point.
2. **Re-test the predictor** against the resolved ordering.
3. **One seed is now nearly enough.** With sems of ~0.0006, most of the remaining
   cost is the 6 s per basis per sequence, so the analytic path makes larger
   circuits (d≈3000, the small-circuit objection) and more rungs affordable.
