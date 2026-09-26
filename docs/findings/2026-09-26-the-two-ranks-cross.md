# Where the rank comes from: the propagator's own rank collapses with `rho` too — and the two CROSS at `rho` ≈ 0.95

*2026-09-26 11:15, `runs/e235_propagator_rank.json` through `e235_propagator_rank.py` — the same circuits, nulls, seeds
and `rho` grid as `e231`, with the propagator's rank measured one level down. **The task side reproduces `e231`'s
stored numbers on 48 of 48 cells**, so the instrument is the corpus's own statistic and the new column is the only
thing added. No cells were unmeasurable.*

## 1. What was asked

`e231` established that the task geometry's `effective_rank` collapses as `rho` → 1, and `e233`/`e234` showed the
*penalty* does not follow it. Neither said **why** the rank moves. The one candidate needing no new substrate is the
object the tasks are built from: every task is a quadratic form in the columns of the propagator
`G = (I − W)^-1` at an assembly's support, so as `rho` → 1 and `G` approaches singularity, its action on those
supports should be dominated by fewer directions.

**The prediction this module registers is that the propagator's rank is the geometry's rank's source** — and it is
**partly refuted**, in a way that is more interesting than a confirmation.

## 2. The two ranks, side by side

`task` is `task_geometry`'s `effective_rank` (verified against `e231`); `prop` is the participation ratio of the
propagated support matrix's squared singular values; the third row is `prop / task`.

| cs 300 | 0.7 | 0.8 | 0.9 | 0.95 | 0.98 | 0.99 |
|---|---|---|---|---|---|---|
| `real` task / prop | 26.2 / 137.5 | 24.3 / 106.3 | 22.1 / 23.9 | 19.4 / 4.0 | 11.8 / 1.3 | 7.3 / 1.1 |
| ratio | **5.24** | 4.37 | 1.08 | **0.21** | 0.11 | 0.15 |
| `alloy1` task / prop | 23.0 / 78.7 | 17.5 / 41.5 | 7.2 / 10.1 | 2.4 / 2.7 | 1.2 / 1.2 | 1.1 / 1.1 |
| ratio | 3.43 | 2.36 | 1.40 | 1.10 | 1.01 | 1.00 |
| `inalloy1` task / prop | 22.9 / 78.4 | 19.8 / 48.1 | 11.6 / 13.3 | 4.3 / 3.1 | 1.4 / 1.3 | 1.1 / 1.1 |
| ratio | 3.43 | 2.43 | 1.15 | 0.72 | 0.88 | 0.97 |
| `erdos_renyi` task / prop | 25.2 / 104.2 | 23.1 / 75.7 | 16.3 / 30.6 | 8.2 / 10.1 | 4.2 / 4.4 | 3.5 / 3.7 |
| ratio | 4.13 | 3.28 | 1.87 | 1.23 | 1.07 | 1.05 |

| cs 800 | 0.7 | 0.8 | 0.9 | 0.95 | 0.98 | 0.99 |
|---|---|---|---|---|---|---|
| `real` ratio | **5.12** | 3.67 | 0.58 | **0.11** | 0.08 | 0.09 |
| `alloy1` ratio | 2.27 | 1.64 | 1.39 | 1.34 | 1.32 | 1.31 |
| `inalloy1` ratio | 0.92 | 0.46 | 0.75 | 0.92 | 0.96 | 0.97 |
| `erdos_renyi` ratio | 3.50 | 2.59 | 1.54 | 1.10 | 0.98 | 0.98 |

## 3. Three results, and the prediction is only the first of them

- **Both ranks collapse with `rho`, monotonically, in every family** — so the propagator is indeed the right object to
  look at, and `e235` gives `e231`'s curve a mechanistic counterpart. The two also agree on the two facts `e231`
  could not explain: `erdos_renyi`'s plateau appears in both columns (3.5 against 3.7 at cs 300/`rho` 0.99), and the
  cs-800 `alloy1` plateau does too (21.0 against 27.6).
- **But the relation is not a compression: the two ranks CROSS.** At `rho` 0.7 the propagator spreads a 148-neuron
  support into **137.5** effective dimensions while the tasks use **26.2** — a ratio of 5.2 — and by `rho` 0.98 the
  propagator's rank is **below** the task's (1.3 against 11.8, a ratio of 0.11) in three of the four cs-300 families
  and in `real` at cs 800 (0.08 at `rho` 0.98). So the task geometry's rank is *higher* than the propagation's near
  criticality: the tasks keep more dimensions than `G`'s action on their own supports provides. A "the geometry
  inherits the propagator's rank" reading is refuted at exactly the `rho` where the geometry's collapse happens.
- **The ratio is family-specific and almost constant where the family plateaus.** `alloy1` at cs 800 sits at a ratio
  of **1.31–1.39** across four `rho` values in which both ranks move only from ~46 to ~21 — i.e. it tracks the
  propagator by a nearly fixed factor. `inalloy1` sits below 1 everywhere at cs 800 (0.46–0.97) while at cs 300 it
  sits *above* 1 until `rho` 0.95 (3.43 → 0.72). So the compression factor is not a property of the propagator alone
  but of (family, size) jointly — which is the same shape of statement the task-side curves already demanded.

## 4. What this cannot do

- **One drawing per cell**, and the in/out contrast here inherits exactly what `e232` measured: the cs-800
  `alloy1`/`inalloy1` *rank* contrast is drawing-dependent (10.10×, 1.06×, 0.23× across three drawings), and this
  module measures one of them. The `rho` curves within one family are drawing-robust; the cross-family ratios are not.
- **`prop` is the propagator's action on ONE union support** (the assemblies' supports at `seed0`), not its spectrum
  or its condition number: "the propagator's rank" is a statement about those 148 columns, and a different union would
  give a different number.
- **The task column's reproduction is exact but its `effective_rank` is an average over three seeds and three
  assemblies** (`e231`'s convention), so the cross at `rho` ≈ 0.95 is a statement about those means.
- **`rho` mixes propagation depth with weight scale** (`stable_weights` rescales the whole matrix), so the collapse
  cannot be attributed to depth rather than to the scale the propagation is fed.
- **No mechanism is claimed for the crossing**: this measures that it happens, at which `rho`, and in which families.
