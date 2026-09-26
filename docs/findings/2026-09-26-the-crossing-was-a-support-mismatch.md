# The crossing was a support mismatch: at the same support the tasks ARE their propagation (0.92–1.00)

*2026-09-26 12:20, `runs/e236_task_spectra.json` through `e236_task_spectra.py` — an audit of `e235`'s headline, run on
the same circuits, nulls, seeds and `rho` grid. **`e235`'s crossing is an artifact of comparing two different objects**,
and the mechanism statement that survives is simpler and stronger than the one it replaces.*

## 1. What `e235` claimed, and the one line that constrained it

`e235` measured the task geometry's `effective_rank` and the propagator's rank **on the union of the three assemblies'
supports**, found them crossing (cs 300: 137.5 against 26.2 at `rho` 0.7, collapsing to 1.3 against 11.8 at 0.98 for
`real`), and read it as *"the tasks keep more dimensions near criticality than the propagation of their own supports
provides"*.

The construction cannot support that reading:

    S = task_covariance(solver, support, weights) = (Gs * weights) @ Gs.T,   Gs = G[:, support]

Every task's covariance is a quadratic form in the **same** propagator columns, so `rank(S) <= rank(Gs)` and
`span(S) ⊆ span(Gs)` at every cell. The only quantity that can exceed is the **participation ratio** — a flatter
spectrum is a higher effective rank with no extra dimension — so the claim has to be tested with `S` and `Gs` measured
**at the same support**, which `e236` does per assembly and per seed.

## 2. The audit: at the same support there is no gap

| cs 300 | `pr_s` (task) | `pr_gs` (its own propagation) | ratio | `top_s` | `top_gs` | rank (s / gs) | containment |
|---|---|---|---|---|---|---|---|
| `real`, `rho` 0.9 | 22.11 | 23.79 | **0.93** | 0.159 | 0.149 | 29.6 / 29.6 | 1.2e-15 |
| `alloy1`, `rho` 0.9 | 7.20 | 7.40 | **0.97** | 0.345 | 0.341 | 29.6 / 29.6 | 8.5e-16 |
| `erdos_renyi`, `rho` 0.9 | 16.31 | 16.95 | **0.96** | 0.150 | 0.148 | 29.6 / 29.6 | 9.0e-16 |
| `real`, `rho` 0.98 | 11.78 | 12.45 | **0.95** | 0.409 | 0.406 | 29.6 / 29.6 | 1.3e-15 |
| `alloy1`, `rho` 0.98 | 1.21 | 1.21 | **1.00** | 0.911 | 0.911 | 29.6 / 29.6 | 8.4e-16 |
| `erdos_renyi`, `rho` 0.98 | 4.16 | 4.14 | **1.00** | 0.466 | 0.467 | 29.6 / 29.6 | 8.9e-16 |

Over the whole grid — six `rho` values at both sizes, four topologies, **48 cells** — **`pr_s / pr_gs` runs 0.92 to
1.01** (cs 300: 0.923–1.004, cs 800: 0.932–1.011): the task
is systematically 0–8% *below* the propagation it is built from, never above. The algebraic ranks are **equal**
(29.6 against 29.6 at cs 300, the support size; the same holds at cs 800), the leading shares agree to three decimals,
and the **containment residual is 1e-15** at every cell — the construction's own property, checked rather than
assumed. The task column also reproduces `e235`'s numbers exactly, so the two modules measure the same tasks.

**So the tasks are a faithful quadratic read-out of the propagation they are built from, and there is no crossing.**

## 3. Where `e235`'s crossing came from, in one comparison

| cs 300, `real` | `rho` 0.9 | `rho` 0.98 |
|---|---|---|
| one assembly's 30-column propagation (`e236`) | 23.79 | **12.45** |
| the **148-column union**'s propagation (`e235`) | 23.89 | **1.34** |
| union ÷ own | 1.00 | **0.11** |

At `rho` 0.9 the union and a single assembly agree to 0.4%; at `rho` 0.98 they differ by **9.3×**. The union's leading
share is what moves: 0.193 at `rho` 0.9 against **0.864** at 0.98, where a single assembly's own leading share goes
0.159 → 0.406. **The participation ratio is not size-normalised, and concatenating blocks that share a leading
direction concentrates the spectrum** — so the union's collapse is a fact about the union, not about the tasks. `e235`
compared a 148-column object with 30-column (and at cs 800, 80-column) ones and called the difference a crossing.

## 4. What survives, and it is the mechanism statement

- **The mechanism question reduces to one object**: the geometry's rank *is* the propagation's rank at the same
  support (0.92–1.00), so *"why does the geometry's rank collapse with `rho`"* and *"why does the propagator's action
  collapse with `rho`"* are the same question, and `e235`'s answer to the second — that it is `G`'s and not the
  support's, from its matched-random control (0.75–1.38 over 48 cells against `rho`'s 75×–295×) — transfers to the
  first.
- **The union is itself a finding, correctly labelled**: the propagation's rank on the *union* support collapses far
  earlier and further than on any of its parts (9.3× apart at `rho` 0.98), i.e. the shared leading mode is what the
  near-critical propagation concentrates.
- **And the 0–8% deficit is the quadratic form's own cost** — a stable, systematic number, not noise: `top_s` exceeds
  `top_gs` at every cell, which is what a trace-normalised quadratic form does to a spectrum.

## 5. What this cannot do

- **It audits one sentence**, not `e235`'s control experiment, which stands as published.
- **The threshold that defines the algebraic ranks is a declared convention** (`1e-10 × max`), not a fact about the
  matrix; the participation ratio is the reading that needs no threshold, and it is the one the verdict turns on.
- **Six `rho` values, two sizes, one drawing per cell** — and `e232`'s lottery applies to any cross-family comparison.
- **`rho` still mixes propagation depth with weight scale**, and nothing here separates them.
