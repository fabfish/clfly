# E34 — the 152σ Erdős–Rényi separation has the same exposure the 32.7σ refutation had, and the arithmetic says it matters

**Date:** 2026-09-22
**Script:** analysis over the four sweep points; `e33` launched
**Context:** `2026-09-22-swap2-unstable-not-scale-dependent.md`, `2026-09-22-c1-refutation-does-not-replicate.md`

---

## 1. The realisation-sd is now measurable, for one topology

The four-point sweep gives `excess(swap2)` at four (circuit-size, swap-realization) draws:

```
0.05782   0.01762   0.03492   0.01237        mean 0.03068   sd 0.02050   (CV 67%)
```

The two control topologies hold to 6.2% and 18% across the same four circuits, so this sd is not a
size effect and is best read as **the sd of `excess(swap2)` across realizations** — the first
estimate the project has of how much a rewired-topology statistic moves when you re-draw the
rewiring.

## 2. What that implies for the other single-realization number

The project's most dramatic quantity is the Erdős–Rényi separation:

| | value |
|---|---|
| `excess(ER)` at d = 1307 | +0.14187 |
| `excess(swap2)` at d = 1307 | +0.01237 |
| gap | +0.12949 |
| reported significance | **152σ** |

**Both endpoints are single realizations**, so that σ measures the seed noise within one draw of each
graph and says nothing about drawing another graph. Substituting realization sd for seed sem:

| assumed sd of `excess(ER)` | combined sd of the gap | the separation becomes |
|---|---|---|
| 0.0102 (½ × swap2) | 0.0145 | 8.9σ |
| **0.0205 (= swap2's)** | 0.0290 | **4.5σ** |
| 0.0410 (2 × swap2) | 0.0580 | 2.2σ |

**At the realisation sd that `swap2` demonstrably has, the 152σ separation becomes 4.5σ**, and it
needs only **1.5×** that sd — 0.0305 — to fall to 3σ.

This is a *bound*, not a measurement: `excess(ER)`'s own realization sd is unmeasured, and ER is a
different regime (it destroys the degree sequence and makes `(I − W)` near-singular, which is why the
project already treats it separately). ER's sd could be much smaller than swap2's — it could also be
larger, since ER is a more violent transform. What the arithmetic establishes is that **the 152σ is
not robust to the same check that retired the 32.7σ**, and that the margin is not large.

## 3. The scope statement this supports

Every scientific claim in the `e2` topology line rests on **one realization per topology**:

| claim | endpoints | examined for realization sensitivity? |
|---|---|---|
| the interference refutation (32.7σ) | `swap0.5`, `swap2` | **yes — and it did not survive** |
| the ER separation (152σ) | `swap2`, `erdos_renyi` | **no** — `e33` is doing so |
| the `bio − rand` sign flip | five topologies | no |
| monotonicity of overlap along the family | five topologies | no (and it is geometry, so more robust) |

**One of those four has been checked and it failed.** The honest scope for the whole line is
therefore: *these are statements about the particular graphs drawn*, until a realization sweep says
otherwise — and the check is cheap, roughly twelve minutes per realization per topology, because
`--rewire-seed` now separates the realization from the tasks.

## 4. Why this is a scope statement and not a retraction

The separation is between regimes that differ by a factor of eleven in excess (0.142 against
0.0124), and ER's other properties — near-singularity of `(I − W)`, the destroyed degree sequence —
are structural rather than statistical. A factor-of-eleven gap surviving a realization sweep is the
likely outcome even at 4.5σ rather than 152σ. What changes is the *number quoted* and the reason it
is quoted: "152σ" reads as a property of the physics, and it is a property of two graphs plus a
within-graph standard error.

## 5. Limits

- The realization sd of 0.0205 is from **four** draws, so its own uncertainty is large (a four-point
  sd carries roughly 40% relative error), and it conflates realization with circuit composition —
  the sweep varies both. `e32`, running now, isolates the realization at fixed size.
- §2's substitution assumes the two topologies have comparable realization sensitivity, which is the
  thing under test. The table is a sensitivity analysis, not a correction.
- ER's near-singular `(I − W)` may make its excess *more* variable than swap2's, in which case the
  separation is weaker than 4.5σ and the structural reading ("a separate regime") is the one that
  survives rather than the numerical one.
