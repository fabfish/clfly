# E49 — the concentration knob is **inert at `swap2`/cs = 800**, so the test the mechanism needed cannot be run there

**Date:** 2026-09-22
**Script:** `experiments/e49_kappa_leverage_by_topology.py`
**Artifacts:** `runs/e49_kappa_leverage.json`, `runs/e37_kappa_real_cs{800,300}.json`
**Context:** `2026-09-22-geometry-mechanism-refuted-on-the-realization-axis.md` §6b, `e36`–`e40`

---

## 1. The test three findings have been circling, and the prior question nobody asked

The `e36` mechanism was: *`swap2`'s excess tracks the rank collapse of its task precision*. The
natural test is `e5`'s concentration knob — vary the drive's concentration `kappa` at fixed wiring and
see whether the excess moves the way the collapse does — and `e37` ran it, at `real` and at `swap2`,
at cs = 800 and cs = 300.

Before reading any sign out of that, this script asks whether **the knob moves the proposed carrier
at all, where it is applied.** It does not:

| section | knob travel in `flattening` (κ 0 → 4) | across-seed sd at κ = 0 | **travel / noise** | `effective_rank` κ0 → κmax |
|---|---|---|---|---|
| `real` cs = 800 | +0.710, +0.730, +0.715 | 0.0050 | **142, 146, 143** | 55 → 2.0–3.5 |
| `real` cs = 300 | +0.678, +0.701, +0.693 | 0.0026 | **262, 270, 268** | 48 → 1.9–3.1 |
| **`swap2` cs = 800** | **+0.0039, +0.0084, +0.0022** | 0.00042 | **9.4, 20.2, 5.3** | **1.70 → 1.1–1.5** |

At `swap2`/cs = 800 the knob travels **0.4–0.8% of the range it travels at `real`** — a factor of
~90 — and the carrier starts at `effective_rank` **1.70 against `real`'s 55**. That is not a
coincidence: `swap2`'s task precision is *already* rank-collapsed, so concentrating the drive further
has almost nothing left to act on. Its precision is also 99% off-diagonal (`offdiag` 0.989 against
`real`'s 0.27), which is the same statement from another side.

**So a correlation between `gap_EWC` and `flattening` computed at `swap2`/cs = 800 is a correlation
over a flattening range barely wider than the seed-to-seed spread.** Its sign means nothing either
way. Measured against the seed noise, two of the three seeds are formally inert (9.4× and 5.3×) and
the third is marginal (20.2×) — so the verdict is itself seed-dependent, which is what straddling a
threshold looks like.

## 2. And where it does have any leverage, it points the wrong way

Per-seed only — plan rule 17 forbids pooling a run whose last seed is still being written, and the
verdict above is per seed anyway:

| section | seed | n | ρ(gap, flattening) | p | informative? |
|---|---|---|---|---|---|
| `real` cs = 800 | 0 / 1 / 2 | 7 | −0.964 / −0.321 / +0.107 | 0.0005 / 0.48 / 0.82 | yes |
| `real` cs = 300 | 0 / 1 / 2 | 7 | −0.321 / −0.893 / −0.179 | 0.48 / 0.0068 / 0.70 | yes |
| `swap2` cs = 800 | 0 | 7 | −0.126 | 0.79 | **over noise** |
| `swap2` cs = 800 | 1 | 7 | **−0.786** | **0.036** | yes (marginal) |
| `swap2` cs = 800 | 2 | 4 | −0.800 | 0.20 | over noise, and partial |

The one `swap2` seed with both leverage and a resolved correlation is **seed 1, at ρ = −0.786
(p = 0.036)** — which is the **`e5` direction**, i.e. *more concentration, larger gap*. The `e36`
mechanism requires the opposite sign there (its claim is that at `swap2` a higher effective rank goes
with a higher excess, so concentrating the drive should *lower* the excess). So the one place the
intervention has leverage at `swap2`/cs = 800, it contradicts the mechanism — the same direction as
the cs = 300 smoke test and the same direction as `e39`'s realization-axis refutation.

## 3. The structural point, which is the generalisable one

> **the mechanism was stated in terms of the rank collapse, and the rank collapse is what pins the
> carrier at the configuration that motivated it.**

`e36` proposed the mechanism *because* `swap2`'s precision collapses. That collapse is exactly what
removes the knob's ability to move the carrier. So the mechanism is **inert where it was proposed and
testable only where the collapse has not happened** — and the one such configuration (cs = 300,
`effective_rank` 15.4) gave the opposite sign.

This is not a fact about this mechanism. It is a fact about testing a mechanism with an intervention:
**measure the intervention's travel on its own target variable, at each configuration, before
interpreting its result, and report the configurations where it is inert as *untested* rather than as
null.** Every one of the four prior findings in this sequence read a correlation and argued about its
sign; none of them checked whether the knob had moved anything.

## 4. What this settles

| statement | status |
|---|---|
| `e36`'s mechanism (rank collapse causes the excess) | **withdrawn** — now contradicted on three independent axes: cross-family slopes 13.6σ/6.06σ apart, a 0.019 out-of-sample miss inside the fitted range, and a 10σ sign-rule failure above its bracket |
| the `kappa` intervention as a *test* of that mechanism at `swap2`/cs = 800 | **cannot be run** — the knob is inert there; report it as untested |
| the `kappa` intervention at `real` | works as intended, and does not address the mechanism (it is the `e5` experiment, whose own status is `e45`'s) |
| the `kappa` intervention at `swap2`/cs = 300 | the one informative case, and it **contradicts** the mechanism |

## 5. Limits

- **The leverage floor (10× the seed noise) is arbitrary**, and the `swap2` seeds straddle it (9.4,
  20.2, 5.3). Read §1 as "the knob is 15–30× weaker at `swap2` than at `real`", which is true
  regardless of where the floor sits, rather than as a clean binary.
- **`swap2`/cs = 800's seed 2 is incomplete** (4 of 7 `kappa` points), and a partial sweep
  *understates* travel because it has fewer points to reach its extremes with — so its 5.3× is a
  lower bound and is not evidence of inertness on its own. That direction is pinned in the tests,
  because it is the direction that would overstate the claim.
- **`swap2`/cs = 800 and `swap2`/cs = 300 have different `d`** (1307 against 952) as well as
  different task draws, so "testable only where the collapse has not happened" is supported by the
  collapse measurement itself (§1) rather than by the circuit-size comparison.
- The knob's travel at `swap2` is not zero (0.004–0.008), so "inert" is a statement about the
  signal-to-noise of the correlation, not about a literally constant carrier. A much larger
  concentration range might still give leverage there; `e5`'s grid is `kappa` ≤ 4 and was not
  designed for a collapsed precision.
