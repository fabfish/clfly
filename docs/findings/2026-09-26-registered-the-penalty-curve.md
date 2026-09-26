# Registered: the penalty curve at the rank curve's own grid — does the excess follow the geometry?

*2026-09-26 10:07. Runs: `e2_topology_gap` at cs {300,800} with `--rho` {0.7, 0.8, 0.95, 0.98}, four topologies
(`real`, `alloy1`, `inalloy1`, `erdos_renyi`), `--seeds 3 --seed0 0 --q 0.02 --no-realized`, **eight runs, ~24 min**,
to be written as `e233_cs{300,800}_rho{07,08,095,098}.json` in the runs directory. The `rho` {0.5, 0.9, 0.99} cells of
the same grid already exist (`e217`, `e228_rho{05,099}_cs{300,800}.json`), so this fills the same nine-point grid
`e231` measured the *rank* on.*

## 1. Why the penalty curve is the missing half

`e231` measured the task geometry's `effective_rank` over nine `rho` values at both sizes and gave three verdicts
(monotone collapse; a cs-300 crossing between `rho` 0.7 and 0.8; a systematic 15.7×-saturating `alloy1`/`inalloy1`
separation at cs 800). Every one of those is a statement about the **geometry**. The quantity the project is about —
the analytic diagonalisation excess, the "penalty" — has been measured at **three** `rho` values only, and the curve
between them is what would connect the two: **does the penalty move with the geometry, or independently of it?**

The corpus already hints at co-movement at the two extreme points: at cs 300 the one-side nulls' rank falls
26.5 → 7.2 → 1.05 over `rho` 0.5/0.9/0.99 while their excess falls 0.0294 → 0.1225 → 0.0055 — **not** the same shape
(the penalty *rises* from 0.5 to 0.9 and then collapses, where the rank only falls). So a co-movement claim is
already in doubt, and that is why it is registered rather than assumed.

## 2. The registered claims

- **E1 — the penalty and the rank co-move in SIGN at every step, for every topology.** For each of the four
  topologies at each size, the sequence of the analytic excess over `rho` ∈ {0.7, 0.8, 0.9, 0.95, 0.98, 0.99} and the
  sequence of `effective_rank` (from `e231`'s own cells) *both fall or both rise* at every step. **Falsifier**: any
  step where one rises and the other falls — and the corpus already contains one candidate (0.5 → 0.9 at cs 300),
  which is why the test starts at 0.7. **Null**: co-movement at every step but with the two quantities' relative
  changes differing by more than a factor of three at some step (a shared direction without a shared scale).
- **E2 — `erdos_renyi`'s penalty advantage over the one-side nulls persists at high `rho`.** At cs 300, the
  ER/`alloy1` excess ratio is **above 3×** at `rho` ∈ {0.95, 0.98, 0.99}. It is 14.8× at 0.99 already; the claim asks
  whether the *middle* of the high-`rho` region keeps a comparable advantage. **Falsifier**: any of those three
  points at or below 3×, which would say the ER advantage is a one-point effect. **Null**: above 3× at some points and
  below at others.

**Reported**: the full table of excesses (four topologies × six `rho` values × two sizes), the one-side mean, the ER
÷ one-side top step, each artifact's `timing_s` (rule 49), and the rank from `e231`'s cells beside each excess so the
co-movement can be read without opening two documents.

## 3. What it cannot do

- **One drawing per cell** (`--rewire-seed` defaults to `seed0`): `e232`'s lottery is running on the *rank* and its
  lesson — that the in/out asymmetry's sign is drawing-dependent at cs 300 — applies here too, so a single-drawing
  penalty curve cannot separate a `rho` effect from a drawing effect.
- **Six `rho` values, one size pair**, so the co-movement test is a set of same-sign comparisons and not a
  regression; a shared direction is not evidence of a shared cause.
- **`rho` mixes propagation depth with weight scale**, and the analytic excess's own dependence on the weight scale
  is not held fixed anywhere in this design.
- **Nothing about the network substrate or the realized arm** (`--no-realized`, as in every cell of this line).
