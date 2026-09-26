# Does the penalty follow the geometry? No: the excess peaks at `rho` ≈ 0.9 where the rank has no feature, and the two-side advantage is late-onset

*2026-09-26 10:52, `runs/e233_cs300_rho{07,08,095,098}.json` (four runs, ~30 min) merged with the existing `rho`
{0.5, 0.9, 0.99} cells and `e231`'s rank curve by `e234_read_penalty_curve.py`. **Both registered claims are refuted**
— `e234`'s exit is 0 because it *could* judge them, and the verdicts are E1 FALSIFIER FIRED and E2 FALSIFIER FIRED.
Registration: `docs/findings/2026-09-26-registered-the-penalty-curve.md`. The cs-800 half of the grid is still being
measured.*

## 1. The two curves at cs 300, side by side

| `rho` | `real` rank / excess | `alloy1` rank / excess | `inalloy1` rank / excess | `erdos_renyi` rank / excess |
|---|---|---|---|---|
| 0.7 | 26.24 / 0.0015 | 22.96 / 0.0842 | 22.86 / 0.0610 | 25.23 / 0.0770 |
| 0.8 | 24.31 / 0.0066 | 17.54 / 0.1199 | 19.77 / 0.1004 | 23.08 / 0.1226 |
| 0.9 | 22.11 / 0.0298 | 7.20 / 0.1225 | 11.62 / 0.1223 | 16.31 / 0.1567 |
| 0.95 | 19.43 / **0.0332** | 2.44 / 0.0693 | 4.32 / 0.0839 | 8.22 / 0.1322 |
| 0.98 | 11.78 / 0.0227 | 1.21 / 0.0167 | 1.43 / 0.0255 | 4.16 / 0.0925 |
| 0.99 | 7.25 / 0.0159 | 1.05 / 0.0055 | 1.10 / 0.0083 | 3.48 / 0.0808 |

**E1 FALSIFIER FIRED.** The rank falls monotonically in `rho` for all four topologies (that is `e231`'s verdict, now
reproduced over six grid points). The **excess rises** from `rho` 0.7 to 0.9 in all four — `real` 0.0015 → 0.0066 →
0.0298, `alloy1` 0.0842 → 0.1199 → 0.1225, `inalloy1` 0.0610 → 0.1004 → 0.1223, `erdos_renyi` 0.0770 → 0.1226 →
0.1567 — and only then falls. So the seven steps of the registered grid contain **eight sign disagreements** (the four
0.7→0.8 and 0.8→0.9 rises, plus `real` 0.9→0.95), and the two quantities peak in **different places**:

- the **rank** has no maximum inside the grid: it falls from the first point to the last;
- the **excess** has a maximum at `rho` ≈ 0.9 for the nulls (`alloy1` 0.1225, `inalloy1` 0.1223, ER 0.1567) and at
  `rho` ≈ 0.95 for `real` (0.0332).

**The penalty is therefore not a function of the task geometry's rank** — not merely "not a simple function": the two
curves' shapes disagree at the first two steps, where the rank is still ~20 dimensions and the excess climbs by a
factor of 2–20.

## 2. And the two-side advantage is a LATE effect, not a high-`rho` one

**E2 FALSIFIER FIRED.** The Erdős–Rényi ÷ `alloy1` excess ratio at cs 300 is **1.91×** at `rho` 0.95, **5.53×** at
0.98 and **14.77×** at 0.99 — the registered bar was 3× at all three points, and the 0.95 point is below it. So the
ER advantage is not a property of "the high-`rho` region": it switches on **between 0.95 and 0.98**, and at 0.95 the
two-side null is only twice the one-side level.

That onset is the sharpest feature in the whole penalty curve, and it sits **above** the point where the rank curve's
own steepest fall happens (`rho` 0.8 → 0.9, 17.5 → 7.2 for `alloy1`). Two different onsets, two different quantities.

## 3. What is monotone, and it is the ratio rather than the levels

The **top step** — ER ÷ the one-side mean — is monotone increasing across the whole grid, in the same artifacts:

| `rho` | 0.7 | 0.8 | 0.9 | 0.95 | 0.98 | 0.99 |
|---|---|---|---|---|---|---|
| top step | **1.06×** | 1.11× | 1.28× | 1.73× | 4.38× | **11.77×** |

So the levels are non-monotone and the ratio is monotone. That is a statement about the **denominator**: the one-side
level rises to 0.1224 at `rho` 0.9 and then collapses to 0.0069 at 0.99 (a factor of 18), while ER only halves — which
is `e229`'s finding at one point, now visible as a curve.

## 4. What this cannot do

- **One drawing per cell** for every penalty point, and `e232`'s lottery measured that the in/out *comparison* is
  drawing-dependent at both sizes (its cs-800 ratio read 10.10×, 1.06× and 0.23× across three drawings). So the E1
  verdict is safe — it is about each topology's own curve against its own rank, which the lottery showed *is*
  drawing-robust — while **any point-to-point comparison between two topologies at one `rho` inherits the drawing
  lottery** and is not resolved by this design.
- **The cs-800 half is unmeasured as this is written** (four runs in flight), so E1's "both sizes" clause is judged on
  the cs-300 families plus the two cs-800 points that exist.
- **`rho` mixes propagation depth with weight scale**, and the excess's dependence on weight scale is not held fixed.
- **Six points, one size pair**: a peak location of "≈ 0.9" is bracketed by 0.8 and 0.95, not resolved.
