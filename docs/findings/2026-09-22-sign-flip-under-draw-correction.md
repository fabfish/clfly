# E18 — the "advantage flips sign under rewiring" claim, and the draw correction applied to it

**Date:** 2026-09-22
**Script:** analysis over `runs/e2_analytic.json` (no new compute for the correction) + `experiments/e12_control_spread.py --column cell_class` (launched)
**Artifacts:** `runs/e2_analytic.json`, `runs/e17_cell_class_drawsd.json` (in flight)

---

## 1. The claim and where it is load-bearing

The paper's abstract and the README both say: **"the advantage flips sign once the wiring is
randomised, so it is a property of the connectome rather than of the vocabulary."** That inference
is the interpretation of claim C2 — that a biological grouping is not *intrinsically* good for
anchoring, but good because it matches the connectome. If the sign flip fails, the surviving
statement is only "biology beats a random partition of the same size on this wiring", with the
attribution unexplained.

It is also the one place where the paper contained an internal disagreement, and the disagreement
was never resolved: `2026-09-22-stable-scale-recheck.md` says of the same contrast that **"the sign
flip is not resolved point-by-point"**, on standard errors of ~0.023 carried by a total span of
0.0147. Two documents, opposite verdicts, no reconciliation.

## 2. First, the disagreement is about the metric

The two use different estimators. The recheck's numbers are **realized** excess (SE ≈ 0.023–0.028);
the paper's table is **analytic** excess from `runs/e2_analytic.json`, which reproduces
bit-exactly:

| topology | `real` | `swap0.1` | `swap0.5` | `swap2` | `erdos_renyi` |
|---|---|---|---|---|---|
| delta (published) | −0.00276 | −0.00202 | +0.00102 | +0.00042 | +0.00213 |
| σ (published) | 2.52 | 2.27 | 2.42 | 2.75 | 2.43 |

So the recheck's verdict was a statement about the metric, not about the effect — the same
"budget, not effect" pattern as the 3-of-5 → 4-of-5 rungs case. **That disagreement is now closed.**
Point-by-point resolution is real on the analytic estimator.

## 3. But the σ are seed-only, and `cell_class` is a coarse partition

`cell_class` has concentration **0.171** at d = 1307, which sits inside the **unmeasured knee** of
the concentration→draw-sd relation (measured points at 0.020 and 0.325, nothing between). Log-linear
interpolation gives a draw sd of **1.9e-4**, and adding it in quadrature to each point:

| topology | delta | σ seed-only | **σ with the draw component** |
|---|---|---|---|
| `real` | −0.00276 | 2.52 | **2.48** |
| `swap0.1` | −0.00202 | 2.27 | **2.22** |
| `swap0.5` | +0.00102 | 2.42 | **2.21** |
| `swap2` | +0.00042 | 2.75 | **1.75** |
| `erdos_renyi` | +0.00213 | 2.43 | **2.38** |

**`swap2` falls below 2σ, so "every point is individually resolved" is false under the correction.**
Every remaining σ is 2.2–2.5 — the whole claim was always marginal, and it was marginal enough that
one added component moves one point across the line.

## 4. What survives, and the form to state it in

The *sign pattern* survives, and with two resolved points on each side:

> the advantage is **negative on the real connectome and on mildly rewired versions** (2.22σ and
> 2.48σ) and **positive on substantially rewired and Erdős–Rényi wiring** (2.21σ and 2.38σ). The
> sign change is supported; that *every* point resolves individually is not, and `swap2` is the
> point that does not.

That is enough for the inference the paper draws — a sign change with resolved points on both sides
is not a null — but the sentence "every point is individually resolved, so the sign flip is the
claim" is no longer true as written, and has been corrected.

## 5. The claim is highly sensitive to an unmeasured quantity

Because the correction rests on an *interpolated* draw sd, it is worth saying what happens if the
interpolation is wrong by a factor:

| assumed `cell_class` draw sd | points resolved at 2σ | which |
|---|---|---|
| 1.9e-4 (the estimate) | **4 of 5** | all but `swap2` |
| 3.8e-4 (×2) | **3 of 5** | `real`, `swap0.1`, `erdos_renyi` — **only one negative point left** |
| 7.5e-4 (×4) | **1 of 5** | `real` only — no sign flip to speak of |

So at twice the estimated draw sd the pattern reduces to a single resolved negative point, which
would not support "it is a property of the connectome". **This inference now depends on a number
that has never been measured.** That is measured now: `e12_control_spread --column cell_class
--draws 5` is running, and `cell_class` is a partition the script can build directly, so no new
machinery is needed.

## 6. The knee is now load-bearing three times over

This is the third independent claim in the project that rests on the interpolated region between
concentration 0.020 and 0.325:

1. the predictor's matched-pair count (`2026-09-22-predictor-survives-draw-correction.md` §4),
   where the 2σ line falls between `baseline/supertype` at 1.94 and `wider-tasks/supertype` at 2.17;
2. the sign flip here, which loses its pattern at ×2;
3. `cell_class` in general, which is a *coarse* partition at a concentration the measurements do
   not bracket.

The measurements were designed for the `cell_type` pooling family, and that family cannot produce
concentrations of 0.05–0.25 — but `cell_class` (0.171) and `ito_lee_hemilineage` (0.032) are
partitions of exactly those concentrations, so the gap is closed by measuring *columns* rather than
by constructing new partitions. The first of those is in flight.

## 7. Limits

- The correction treats the draw component as independent of the seed component and adds it in
  quadrature; that is the same construction used everywhere else in this line of work, and it is
  what the `paired_delta` machinery computes from per-seed data.
- `e2_analytic.json` has **3 seeds** per topology, so the seed sems are themselves weak, and the
  paired column cannot be used on it (this is the ≥12-seed limit established in
  `2026-09-22-e13-averaged-controls.md` §3). A properly powered version would need more seeds and
  averaged controls, and no such run exists.
- The five points are not independent draws: the same circuit is rewired along one swap family, so
  the topologies are nested by construction and the σ are not independent across rows.
