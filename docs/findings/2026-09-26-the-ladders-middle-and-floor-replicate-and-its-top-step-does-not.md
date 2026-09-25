# The ladder's middle and floor replicate at every size, and its top step does not

*2026-09-26 04:06, `runs/e217_ladder_cs300.json` and `_cs400.json` — four cells each, 8–10 min per size, read by
`e218_ladder_replication_read.py`, exit 0. The registration is
`docs/findings/2026-09-26-registered-does-the-ladder-survive-at-another-circuit-size.md`.*

## 1. The three ladders

| level | destroyed | cs 300 | cs 400 | cs 800 |
|---|---|---|---|---|
| `real` | 0 | 0.02978 | 0.02436 | 0.01830 |
| `alloy1` | 1 | 0.12247 | 0.13859 | 0.05136 |
| `inalloy1` | 1 | 0.12233 | 0.13249 | 0.04668 |
| `erdos_renyi` | 2 | 0.15668 | 0.15015 | 0.14187 |
| **top step** (ER ÷ larger one-side) | | **1.28×** | **1.08×** | **2.76× / 3.02×** |
| **middle ratio** (the two one-side nulls) | | **1.00×** | **1.05×** | 1.09× |

## 2. The verdicts

- **Z1 — the top step — FALSIFIER FIRED at cs 400** (1.08×, within the 1.25× bound) and in its **null band at
  cs 300** (1.28×). **So the top step is a cs-800 property and not a property of the substrate.**
- **Z2 — the middle is ONE level — MET at both sizes**, and the agreement is *sharper* than cs 800's: the two
  one-side nulls differ by **0.1% at cs 300** (0.12247 against 0.12233) and **5% at cs 400**, against 9% at cs 800.
- **Z3 — the floor — MET at both sizes**: `real` is below both one-side nulls at every size measured.

## 3. What the top step's size dependence actually is

The three ladders say more than a failed claim:

- **the one-side level rises steeply as the circuit shrinks** — 0.047–0.051 at cs 800, **0.122–0.139 at cs 300–400**,
  a factor of 2.6–2.9;
- **the two-side level is nearly flat** — 0.142 / 0.150 / 0.157 across the same range, a factor of 1.1;
- **and the floor rises mildly** — 0.018 → 0.024 → 0.030.

So **the ladder's levels converge from below as the circuit shrinks**: destroying one side gets you 78% of the way to
Erdős–Rényi at cs 300 and 92% of the way at cs 400, against 36% at cs 800. The top step is not a constant being lost or
gained; it is **the distance between a level that moves with the circuit and one that does not**.

The candidate reading, recorded as a hypothesis and not as a result: at smaller circuits a task's support is a larger
fraction of the neuron set, so a single-sided scramble damages the structure the propagation relies on more
thoroughly, and the second side has less left to destroy. Nothing in this design tests that — it needs the support
fraction varied independently of the circuit size, which is not what the 10%-of-circuit convention does.

## 4. What this does to the week's headline

**The ladder must now be quoted in two parts.** What replicates: *destroying a graph's degree structure raises the
diagonalisation penalty, the floor is ordered (the intact connectome is lowest), and freeing either side alone gives
the same penalty as freeing the other* — at cs 300, 400 and 800, with the two one-side nulls agreeing to 0.1–9%. What
does **not**: *"a 7× top step"*, which is cs 800's value (2.8–3.0×) and is **1.28× at cs 300 and 1.08× at cs 400**.

That is a real demotion of this week's strongest new structural claim, found by applying the project's own
more-than-one-circuit-size standard to it before quoting it in the paper. C3's status note carries both halves, and the
"top step" phrasing is marked as size-specific.

## 5. What this does not do

Three sizes and **one realization per cell at cs 300 and cs 400** — the alloy's own five-drawing spread at cs 800 was
**3.34×**, so a single drawing at a new size is a point and not a level, and the cs 300/400 top steps (1.28×, 1.08×)
could move with drawings in either direction. The cs 800 level values are five- and three-drawing means while the new
sizes are single drawings, which is a real asymmetry in the comparison and the first thing a replication with drawings
would fix. The support fraction is held at the 10% convention throughout, so size and support are not separated.
