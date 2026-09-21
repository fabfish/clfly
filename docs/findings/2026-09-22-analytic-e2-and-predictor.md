# e2 on the analytic scale, and a working predictor for C2

**Date:** 2026-09-22
**Scripts:** `experiments/e2_topology_gap.py`, `experiments/e6_predictor.py`
**Artifacts:** `runs/e2_analytic.json`, `runs/e6_predictor.json`

---

## 1. e2 with the analytic effect size

d=1307, 3 seeds, 5 topologies, the same task sequences under both effect sizes.

| topology | overlap | /chance | **a:EWC** | a_sem | r:EWC | r_sem | **a:bio−rand** | σ |
|---|---|---|---|---|---|---|---|---|
| `real` | 0.0075 | 0.135 | +0.01830 | 0.00115 | +0.03212 | 0.02169 | **−0.00276** | 2.52 |
| `swap0.1` | 0.0105 | 0.190 | +0.02087 | 0.00091 | +0.03213 | 0.02627 | **−0.00202** | 2.27 |
| `swap0.5` | 0.0230 | 0.414 | +0.02317 | 0.00031 | +0.02357 | 0.00903 | +0.00102 | 2.42 |
| `swap2` | 0.0594 | 1.069 | +0.01237 | 0.00011 | +0.00943 | 0.00217 | +0.00042 | 2.75 |
| `erdos_renyi` | 0.2892 | 5.207 | +0.14187 | 0.00084 | +0.15236 | 0.01769 | +0.00213 | 2.43 |

**Standard errors fall by ~20×** at every point, and the adjacent contrasts become
decisive where they were previously unreadable:

| contrast | Δ excess | significance |
|---|---|---|
| `real` → `swap0.1` | +0.00257 | 1.7σ |
| `swap0.1` → `swap0.5` | +0.00230 | 2.4σ |
| `swap0.5` → `swap2` | **−0.01079** | **32.7σ** |
| `swap2` → `erdos_renyi` | **+0.12949** | **152σ** |

Two things follow.

**The interference mechanism is refuted, now decisively.** Task overlap rises
monotonically 0.0075 → 0.2892 across the family, and the EWC excess does not follow
it: it rises slightly, then *falls* by a resolved **32.7σ** between `swap0.5` and
`swap2` while overlap doubles. The diagonal's penalty is not tracking interference.

**Erdős–Rényi is a categorically different regime**, separated from `swap2` by
152σ. It is not the end of the swap axis; it changes the conditioning of `(I − W)`.
Reporting it as a monotone endpoint would be a mistake, and it is now excluded from
the monotonicity claims by measurement rather than by argument.

**The biological advantage now has resolved signs.** `bio − rand` is negative on
`real` (−0.00276, 2.5σ) and `swap0.1` (−0.00202, 2.3σ), and positive on `swap0.5`
(+0.00102, 2.4σ), `swap2` (+0.00042, 2.8σ) and Erdős–Rényi (+0.00213, 2.4σ). Every
point is resolved at >2.2σ, and the **sign flips between `swap0.1` and `swap0.5`.**

So the claim is not "the biological advantage decays monotonically" (it does not —
`real` is *more* negative than `swap0.1`) but something sharper and better supported:

> The biological anchoring advantage exists on the real connectome and on mildly
> rewired versions of it, and **reverses to a small penalty** once the wiring is
> substantially randomised. Every one of the five points is resolved.

That is the version to report. It also gives a mechanistic reading consistent with
the predictor in §2: on the real connectome the cell-class partition happens to sit
near the eigenstructure of the propagated task covariances, and randomising the
wiring moves it away.

## 2. A working predictor for C2

C2's weakness has been that it had no a-priori predictor: the project could measure
that one partition beat another but could not say in advance which would be good, and
the principal-angle scalar failed at the job (3 of 5, with or without spectral
truncation).

`clfly.bench.analytic.projection_pressure` is the LGCL mechanism stated directly. Run
the **exact** filter — whose prior trajectory is basis-independent, so this is
computable before any anchored filter exists — and measure how much of each predicted
prior the basis would discard, weighted by the task's measurement information:

    pressure = sum_k  || J_k^{1/2} disc_k J_k^{1/2} ||_F^2 / || J_k^{1/2} P_pred,k J_k^{1/2} ||_F^2

The information weighting is what makes it more than a restatement of
`constrained_fraction`: without it the predictor could not separate a biological
partition from its size-matched random control, because those have identical
`constrained_fraction` by construction.

On the real connectome it ranks 11 candidate bases against the analytic excess with
**Spearman +0.991**, and gets the sign right at **all five** matched bio/random pairs
— including the one pair where biology *loses* (`cell_type`, where biology is
very slightly worse and the predictor says so).

| basis | excess | pressure | predicted worse than random? |
|---|---|---|---|
| `bio:side` | +0.00386 | 0.0824 | no ✓ |
| `rand:side` | +0.00857 | 0.1419 | — |
| `bio:cell_class` | +0.01086 | 0.1545 | no ✓ |
| `rand:cell_class` | +0.01390 | 0.3892 | — |
| `bio:ito_lee_hemilineage` | +0.01354 | 0.2983 | no ✓ |
| `rand:ito_lee_hemilineage` | +0.01614 | 0.5520 | — |
| `bio:supertype` | +0.01490 | 0.4037 | no ✓ |
| `rand:supertype` | +0.01635 | 0.5525 | — |
| `bio:cell_type` | +0.01649 | 0.5748 | **yes ✓** |
| `rand:cell_type` | +0.01624 | 0.5561 | — |
| `diagonal(EWC)` | +0.01655 | 0.5793 | — |

By contrast the principal-angle alignment scores +0.336 over all 11 and +0.900 over
the biological five — visibly worse, and it gets the `cell_type` sign wrong.

**This is in sample**, on the same data that suggested the predictor, so it is
promising rather than established. `experiments/e6_predictor.py` tests it out of
sample across task width, drift rate, topology and circuit size; results in §3.

## 3. Out-of-sample: the predictor generalises

`experiments/e6_predictor.py` evaluates the predictor on five conditions it was not
tuned on, spanning task width (support 30 → 60), drift rate (q 0.02 → 0.10), topology
(real → swap2) and circuit size (d 952 → 1307):

| condition | d | Spearman | sign | per-pair |
|---|---|---|---|---|
| `baseline` | 952 | +0.982 | 5/5 | `+++++` |
| `wider-tasks` | 952 | +0.982 | 5/5 | `+++++` |
| `faster-drift` | 952 | +0.982 | 5/5 | `+++++` |
| `rewired-swap2` | 952 | +0.991 | **4/5** | `+-+++` |
| `larger-circuit` | 1307 | +0.973 | 5/5 | `+++++` |

> **Mean Spearman +0.982; matched-pair sign agreement 24/25.**

This is the test that matters, because the sign test is one a predictor that merely
recovers `constrained_fraction` **must fail**: matched pairs have identical
`constrained_fraction` by construction, so such a predictor would score 0/25. Scoring
24/25 means `projection_pressure` is capturing something beyond granularity — which
is exactly the claim C2 needed and previously lacked.

**The one failure, recorded rather than smoothed over.** On `rewired-swap2` the
`cell_class` pair goes the wrong way, and it is a *confident* miss: pressure says
biology should be much better (`pressure_delta = −0.971`) while biology is slightly
worse (`excess_delta = +0.0031`). So the predictor has at least one real failure
mode, on heavily rewired wiring, for a mid-granularity rung.

**What the predictor is and is not.** It ranks and signs correctly; it is not
calibrated. Its dynamic range varies enormously across conditions — the `cell_class`
pressure margin is −0.041 at baseline and −0.971 on `rewired-swap2` — while the
corresponding excess deltas are all of order 0.003–0.010. Reading a magnitude off
`pressure` would be a mistake; reading an ordering off it is well supported.

## 4. Where the claims stand after this fire

| claim | status |
|---|---|
| **C1 geometry** — the connectome separates task subspaces, rewiring destroys it | **Solid.** Deterministic, monotone 0.0075 → 0.2892, 7× vs chance. |
| **C1 mechanism** — the gap is driven by interference | **Refuted, decisively.** The excess *falls* by 32.7σ between `swap0.5` and `swap2` while overlap doubles. |
| **Erdős–Rényi as the axis endpoint** | **Refuted by measurement.** Separated from `swap2` by 152σ; it is a conditioning regime, not more rewiring. |
| **C2** — biological bases beat matched random ones | **Resolved at 3/5 rungs** (up to 12.9σ), and out of sample the sign holds at 24/25 matched pairs. |
| **C2 mechanism/predictor** | **Works.** `projection_pressure` ranks at ρ = +0.98 and signs at 24/25 out of sample, where the principal-angle scalar scored 3/5. |
| **Granularity** — less constraint means less loss | **Resolved**, and now understood as the dominant term the predictor also captures. |

