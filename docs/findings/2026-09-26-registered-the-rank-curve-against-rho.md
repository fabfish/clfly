# Registered: the rank curve against `rho` on a grid the corpus does not have — and the measurement is the corpus's own

*2026-09-26 09:40. Runs: `e231_rank_versus_rho.py --grid 0.5,0.7,0.8,0.9,0.95,0.98,0.99,0.995,0.999 --sizes 300,800`,
**~30 min**, to be written as `e231_rank_versus_rho.json` under `runs/` when it finishes. The `cs 300` points at
`rho` {0.5, 0.9, 0.95} were measured before this registration was written and are in §4; the other fifteen cells are
not.*

## 1. What is open

`e227`-`e230` left one phenomenon standing and one account of it:

- the task geometry's **effective rank collapses as `rho` rises** — 26.17 → 9.41 → 1.07 (cs 300, one-side nulls) over
  `rho` 0.5/0.9/0.99 — and `e230` established that this is **resolvable at cs 300 for all four topologies**
  (contrasts of 7.68× to 25.25× against within-`rho` drawing scatters of 1.06× to 2.73×), **resolvable at cs 800 for
  `inalloy1`** (44.79× against 4.14×), and **not resolvable at cs 800 for `alloy1`** (3.01× against 16.44×);
- consequently the *directional* reading — that destroying the out-structure collapses the geometry while destroying
  the in-structure does not — rests on **one drawing per cell at cs 800**.

The corpus's `rho` grid has three values and one drawing per cell, so the **shape** of the curve is unmeasured:
monotone steepening, a threshold, or a turnover are all consistent with the three points.

## 2. Why this instrument is the corpus's own measurement, not a surrogate

`effective_rank` is the participation ratio `1/Σw²` of each task's normalised precision spectrum
(`clfly.bench.oracle.task_geometry`). It is a property of the tasks alone — **no basis appears in it** — so it can be
measured without the analytic arm, the geometric alignment nulls or the realized arm, at the cost of the task builds.
At cs 300 that is ~13 s per (topology, three seeds), which is what makes nine `rho` values affordable where the
runner's cells cost minutes each.

**And it is verified against the corpus rather than asserted.** `e231` rebuilds the circuit, applies the same null
with the same `rng`, builds the same three seeds with the same support and `q`, and averages the same function; on the
`rho` values that already have artifacts it reproduces them **exactly** (§4). A mismatch there is a defect in this
instrument, not a finding about the substrate, and the check is printed with the run.

## 3. The registered predictions

- **P1 — every curve falls monotonically.** All four topologies at both sizes, across all nine `rho` values, are
  non-increasing in `effective_rank`. **Falsifier**: any rise, at any step, in any family. A rise would mean the
  collapse is not a monotone function of the propagation's spectral radius at all, and would make the three-point
  reading an accident of which three points were taken.
- **P2 — the family ORDER is stable at cs 300.** Through the steep region, `alloy1` < `inalloy1` < `erdos_renyi` <
  `real`. **Falsifier**: a crossing between families (any two whose order inverts between two `rho` values).
  **Null**: an order that holds but with two families within the scatter `e230` measured.
- **P3 — the cs-800 separation is systematic, not one drawing.** The `alloy1`/`inalloy1` rank ratio at cs 800 exceeds
  **4.14×** — `inalloy1`'s own drawing scatter, the tightest of the two — at **more than one** `rho` value.
  **Falsifier**: it exceeds 4.14× at exactly one `rho` (the 0.99 cell the claim came from) and is below it everywhere
  else, which would say the cs-800 directional reading was that drawing; **null**: it exceeds at two values.

**Reported**: the full table of `effective_rank`, `flattening` and `mean_rank` per (size, topology, `rho`); the
`alloy1`/`inalloy1` ratio at each `rho`; and the verification lines. The verdicts are the reader's business: this
module's exit code is the number of **unmeasurable** cells, so an instrument that cannot measure a cell says so
instead of reporting a number.

## 4. The three cs-300 points measured before registration, and the instrument's verification

| cs 300 | `rho` 0.5 | 0.9 | 0.95 |
|---|---|---|---|
| `real` | 27.25 | 22.11 | 19.43 |
| `alloy1` | 26.52 | 7.20 | **2.44** |
| `inalloy1` | 25.82 | 11.62 | **4.32** |
| `erdos_renyi` | 26.75 | 16.31 | 8.22 |

**Every one of the eight cells at `rho` {0.5, 0.9} reproduces a stored `geometry` block exactly** — the 0.5 row
matches `e228_rho05_cs300.json` in all four topologies, and the 0.9 row matches `e217_ladder_cs300.json` (and
`e219_draws_cs300_rs0.json`, the same drawing) in all four. So the new `rho` = 0.95 column is the same measurement as
the corpus's, one grid point finer.

Two things the 0.95 column already says, and they are the reason P2 and P3 are registered as they are:

- `alloy1` falls **7.20 → 2.44** between `rho` 0.9 and 0.95, a steeper step than the 26.52 → 7.20 before it, so the
  collapse is *accelerating* in this range rather than asymptoting;
- the `alloy1`/`inalloy1` ratio at cs 300 is **1.03× at `rho` 0.5, 0.62× at 0.9 and 0.56× at 0.95** — a stable
  factor, not a growing separation. That is the **opposite** of the single cs-800/`rho` 0.99 cell, where the ratio is
  16.3× in the other direction, which is exactly the contrast P3 is registered to settle.

## 5. What it cannot do

- **One statistic.** A curve here is not a statement about the penalty or the top step; `effective_rank` and the
  excess are two quantities, and `e229`'s penalty cells cost minutes each for that reason.
- **One drawing per cell** (`--rewire-seed` defaults to `seed0`, as the runner does), so a family whose drawing
  scatter is wide cannot be read from a single curve — `e230` measured `alloy1` at cs 800 at **16.44×** across twelve
  drawings, and P3 is written to be judged *against* that number rather than around it.
- **`rho` rescales the whole weight matrix**, so the curve mixes propagation depth with weight scale and nothing here
  separates them.
- **Nine points on two sizes**, so a size × `rho` interaction is described, not estimated.
