# E16 — the control-draw correction applied to the predictor's matched-pair record, and it survives

**Date:** 2026-09-22
**Script:** analysis over `runs/e6_predictor_6.json` (no new compute)
**Context:** `docs/findings/2026-09-22-control-drawn-once.md`, `2026-09-22-draw-budget.md`, `2026-09-22-draw-sd-mechanism.md`

---

## 1. Why this was checked

The predictor's headline is that it identifies the better of each biological-versus-matched-random
pair, on **13 of 13 pairs whose difference clears 2σ**. Every "clears 2σ" in that sentence was
computed from the **seed-only** sem — the same quantity the control-draw work has since shown
understates the uncertainty several-fold for coarse partitions. The 13 is the *denominator*: if the
draw component pushes pairs below the 2σ line, the claim becomes a smaller claim.

This is the one headline the control-draw correction had not been applied to. Seven other claims
were retracted in this line of work; the predictor is the most-cited surviving result, and it was
worth finding out whether it belonged with them.

`e6_predictor.json` / `e6_predictor_6.json` store every pair's `excess_delta`, `excess_sem` and
`sign_ok`, across five conditions (baseline, wider-tasks, faster-drift, rewired-swap2,
larger-circuit), so the correction is arithmetic — no filter is re-run. The draw sd per rung is
taken from the concentration→sd relation, with log-linear interpolation between the measured
points of the matching circuit.

## 2. Result: 13 of 13 holds, and the denominator moves by at most one

| fine-column ``sd_draw`` multiplier | resolvable pairs | correct sign | closest pair to the 2σ line |
|---|---|---|---|
| ×0.1 | 13 | **13/13** | baseline/`supertype` at 1.95 |
| ×0.5 | 13 | **13/13** | baseline/`supertype` at 1.94 |
| **×1 (the estimate)** | **13** | **13/13** | baseline/`supertype` at 1.94 |
| ×2 | 13 | **13/13** | baseline/`supertype` at 1.93 |
| ×4 | **12** | **12/12** | wider-tasks/`supertype` at 2.00 |
| ×10 | 12 | **12/12** | rewired-swap2/`cell_class` at 1.74 |

**The sign record is perfect at every multiplier from 0.1 to 10.** The count is 13 up to a
multiplier of about 3 and 12 beyond it — so the honest statement is *"13 of 13, or 12 of 12 if the
interpolated draw sd for the fine annotation columns is four times the estimate"*, and in neither
case is a pair mis-ranked.

## 3. What did move: `side`'s individual sigmas

| condition / rung | σ seed-only | σ with the draw component |
|---|---|---|
| larger-circuit / `side` | 15.53 | **4.47** |
| wider-tasks / `side` | 18.25 | **13.36** |
| baseline / `side` | 7.48 | 6.73 |
| larger-circuit / `cell_class` | 4.49 | 4.33 |
| larger-circuit / `ito_lee_hemilineage` | 3.27 | 3.27 |

`side` is the worst case because its concentration (0.498) makes it a *coarse* partition, so its
single-draw σ was inflated more than any other rung's — exactly the same reason `side` was the
one rung whose "robustly strong at both scales" claim had to be qualified in the limits section.
The pattern is consistent: **wherever a claim was read off a `side` σ, it was read off the most
inflated number in the study.**

## 4. The sensitivity that matters, stated plainly

The 2σ cut sits between `baseline/supertype` at 1.94 (excluded) and `wider-tasks/supertype` at 2.17
(included) — a gap of one pair. So the count is not razor-stable: it is 13 ± 1 depending on the
draw sd of the fine columns, which is the one quantity in this analysis that is **interpolated
across a 25× range with no measurement inside it** (`2026-09-22-draw-sd-mechanism.md` §5). The
result to quote is therefore:

> The predictor ranks the correct arm on every pair that clears 2σ, for any plausible draw sd
> (13 of 13 at the estimate, 12 of 12 at an unfavourable one).

## 5. What this does not establish

- It does not validate the interpolated draw sd for `cell_type`, `ito_lee_hemilineage` or
  `supertype`; it shows the conclusion does not depend on it, up to a factor of about three.
- It says nothing about the predictor's *ranking* quality (Spearman +0.984/+0.983), which was never
  a thresholded claim and so is untouched by where a 2σ line falls.
- The 13 pairs are 5 conditions × 5 rungs minus the non-resolvable ones, so they are **not
  independent**: the same rungs appear in every condition. A paired-across-conditions analysis
  would be the stricter test, and has not been done.
- `rewired-swap2` contributes **zero** resolvable pairs at any multiplier, and it is the one
  condition where a pair has the wrong sign (a non-resolvable one). That condition is a null for
  this purpose, and it is also the condition that makes the "the advantage flips sign when the
  wiring is randomised" claim — two readings of the same data that would be worth reconciling
  explicitly.
