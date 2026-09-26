# The rank curve, cs 300 half: it falls monotonically to 1, `erdos_renyi` plateaus at 3.2, and the in/out asymmetry only appears above `rho` ≈ 0.75

*2026-09-26 09:35, measured by `e231_rank_versus_rho.py --grid 0.5…0.999 --sizes 300`. The cs-300 half is written as
`e231_cs300_rank_curve.json` (in the runs directory) with its verification table attached. Nine `rho` values, four
topologies, the corpus's own statistic, one drawing per cell. Registration:
`docs/findings/2026-09-26-registered-the-rank-curve-against-rho.md`.*

## 1. The curve

`effective_rank` of the task geometry (the participation ratio of each task's precision spectrum, averaged over the
corpus's three seeds), cs 300, support 30:

| `rho` | `real` | `alloy1` (in destroyed) | `inalloy1` (out destroyed) | `erdos_renyi` (both) |
|---|---|---|---|---|
| 0.5 | 27.25 | 26.52 | 25.82 | 26.75 |
| 0.7 | 26.24 | 22.96 | 22.86 | 25.23 |
| 0.8 | 24.31 | 17.54 | 19.77 | 23.08 |
| 0.9 | 22.11 | 7.20 | 11.62 | 16.31 |
| 0.95 | 19.43 | 2.44 | 4.32 | 8.22 |
| 0.98 | 11.78 | 1.21 | 1.43 | 4.16 |
| 0.99 | 7.25 | 1.05 | 1.10 | 3.48 |
| 0.995 | 5.95 | 1.01 | 1.02 | 3.28 |
| 0.999 | 1.48 | 1.00 | 1.00 | **3.18** |

## 2. P1 is MET: every curve falls monotonically, at every step

No family rises anywhere across the nine points. The collapse is a monotone function of the propagation's spectral
radius at this size, and the three-point reading it extends (26.17 → 9.41 → 1.07) was a sampling of a curve rather
than a coincidence of three values.

## 3. P2's FALSIFIER FIRED, and the crossing is the result

P2 registered that the cs-300 family order would be stable: `alloy1` < `inalloy1` < `erdos_renyi` < `real`. The
measured order is:

| `rho` | order | `alloy1` ÷ `inalloy1` |
|---|---|---|
| 0.5 | `inalloy1` 25.82 < `alloy1` 26.52 < `erdos_renyi` 26.75 < `real` 27.25 | **1.03×** |
| 0.7 | `inalloy1` 22.86 < `alloy1` 22.96 < `erdos_renyi` 25.23 < `real` 26.24 | 1.00× |
| 0.8 | `alloy1` 17.54 < `inalloy1` 19.77 < `erdos_renyi` 23.08 < `real` 24.31 | 0.89× |
| 0.9 | `alloy1` 7.20 < `inalloy1` 11.62 < … | 0.62× |
| 0.99 | `alloy1` 1.05 < `inalloy1` 1.10 < … | 0.95× |
| 0.999 | `alloy1` 1.00 = `inalloy1` 1.00 < … | 1.00× |

**The two one-side families cross between `rho` 0.7 and 0.8** — so the asymmetry `e229` read at high `rho` does not
exist below it. The reading that survives is sharper than "the asymmetry is directional": **below `rho` ≈ 0.75 the two
sides are interchangeable (within 0-3%), and above it the out-structure-destroyed family keeps more rank than the
in-structure-destroyed one** — 0.89× at 0.8, 0.62× at 0.9, and converging again at the end because both have hit 1.
So the *direction* of the asymmetry is a property of the **high-`rho` regime**, not of the null construction.

## 4. `erdos_renyi` does not collapse at all, and that is the other half of the result

The three families whose task geometry is a *single* destruction or none (`real`, `alloy1`, `inalloy1`) all reach
**1.00–1.48** dimensions at `rho` 0.999 — the propagation's leading mode carries essentially all of the task's
precision. `erdos_renyi` — both degree sequences destroyed — **plateaus at 3.18** and is still 3.18 at 0.999, after
falling 26.75 → 3.28 between `rho` 0.5 and 0.995 and then barely moving.

So the quantity that decides whether a task's geometry survives near-critical propagation is **not** how much of the
degree structure was destroyed (`alloy1` and `inalloy1` destroy a full side each and collapse to 1), but whether the
destruction was **edge-wise random on both sides**: the ER graph's tasks keep three effective dimensions where a
one-side null's keep one. That is a statement about what survives the propagator, and it is the first reading in this
thread that separates the two destruction *kinds* rather than the two sides.

## 5. What this cannot do

- **One statistic**: this is the task geometry, not the penalty. Whether the excess follows this curve is unmeasured
  here (and costs minutes per cell).
- **One drawing per cell**, and `alloy1` at cs 800 spans 16.44× across drawings (`e230`) — so the *cs-800* half of this
  grid may not be readable for that family, which is what P3 is written against.
- **The last two points are near-singular**: at `rho` 0.995 and 0.999 the propagator `(I − W)^-1` is close to
  singular, the tasks' supports are dominated by one mode, and `1.00` means "as concentrated as the participation
  ratio can express", not a measured dimension.
- **cs 300 only here.** The cs-800 half of the same grid is running; P3 waits on it.
