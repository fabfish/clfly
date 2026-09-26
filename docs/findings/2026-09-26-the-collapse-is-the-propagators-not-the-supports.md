# The collapse is the propagator's, not the support's: the matched-random control moves the rank by at most 1.4× where `rho` moves it by 75×

*2026-09-26 11:35, `runs/e235_control_propagator_rank.json` — the same six-point `rho` grid at both sizes as `e235`,
with **three matched-random controls** per cell: supports of the *same size* (148 neurons) drawn uniformly from the
circuit. The task side reproduces `e231` again, and the control is the check the project's own rule owes every
biological partition.*

## 1. Why this control, and what it can decide

`e235` found that the propagator's rank collapses with `rho` and **crosses** the task geometry's — at `rho` 0.7 the
propagator spreads the assemblies' union support into **137.5** effective dimensions while the tasks use 26.2, and by
`rho` 0.98 the propagator is *below* the task (1.3 against 11.8). That reading rests on **one support**: the union of
the three assemblies' neurons. If the collapse were a property of *those* neurons — a sparse, well-connected,
anatomically-chosen set — the mechanistic story would be about the analysis's selection rather than about `G`.

The control is therefore **size-matched and otherwise unmatched**: `control_draws` uniformly drawn supports of exactly
the biological support's size, measured through the same solver.

## 2. The result: the support barely matters

| cell group | control ÷ biological |
|---|---|
| all 48 cells (two sizes × six `rho` × four topologies) | **0.75 to 1.38** |
| cs 800, all 24 cells | **0.98 to 1.30** |
| cs 800 `real` | 0.98, 0.98, 1.01, 1.02, 1.01, 1.00 across `rho` 0.7…0.99 |
| cs 300 `real` | 0.98, 0.89, 0.76, 0.81, 0.94, 0.98 |
| cs 800 `alloy1` | 1.09, 1.15, 1.18, 1.18, 1.17, 1.17 |
| cs 300 `inalloy1` | 1.07, 1.07, 1.16, 1.38, 1.14, 1.04 |

Against that, `rho` moves the same quantity by **orders of magnitude**: `real` at cs 800 falls from **324.0** to
**1.1** (a factor of 295) and `alloy1` at cs 300 from **78.7** to **1.05** (75×). So **which 148 neurons the support
contains changes the propagator's rank by at most a factor of 1.4; where the propagation sits changes it by a factor
of 75 to 295.** The collapse is a property of `G`.

## 3. Where the control does deviate, and it is family-specific

The deviations are small but systematic, and they point the same way as `e232`'s drawing lesson — they are about the
family, not about the measurement:

- **`alloy1` at cs 800** sits at 1.09–1.18 across the whole grid: the *random* supports are consistently ~15%
  higher-rank than the biological one, which is the opposite of the intuition that a biologically chosen set would be
  the more structured one;
- **`inalloy1`** is above 1 at low `rho` at both sizes (1.30 at cs 800/`rho` 0.7, 1.38 at cs 300/`rho` 0.95) and
  converges to ~1.02 as `rho` → 1;
- **`real`** is the tightest (0.98–1.02 at cs 800), i.e. the unrewired graph's assemblies are the least distinguishable
  from a random set of the same size.

## 4. What this changes, and what it does not

- **`e235`'s crossing is now on a matched-budget footing.** "The tasks keep more dimensions near criticality than the
  propagation of their own supports provides" is a statement about `G` and the task covariances, not about the union
  support's idosyncratic shape.
- **The 1.4× spread is not nothing**: it is larger than several effects this line has quoted (the support-share
  effect was 1.16× at cs 400), so a future claim whose margin is below ~1.5× on this quantity should carry the control
  it was measured against.
- **It does not touch the task-side curve**: the control measures the propagator only, and the geometry's own
  `effective_rank` has no random-support analogue in this design — a matched *task* control would need the same
  assemblies' supports redrawn, which is a different experiment.

## 5. What this cannot do

- **Three control draws** per cell and one support per draw: the 0.75–1.38 range is a sample, not a distribution, and
  the extremes (0.75, 1.38) are single cells.
- **Size-matched, otherwise unmatched**: the control is not matched for degree, cell type or distance, so a deviation
  could be any of those rather than "structure" in general.
- **One drawing of the null per cell**, so the cross-family ratios inherit `e232`'s lottery while the within-family
  `rho` curves do not.
- **`rho` mixes propagation depth with weight scale**, as everywhere in this line.
