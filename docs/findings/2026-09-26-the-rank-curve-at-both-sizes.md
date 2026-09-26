# The rank curve, both sizes: P3 is MET, the asymmetry's sign inverts with size, and `erdos_renyi`'s plateau is the size-invariant thing

*2026-09-26 09:50, `runs/e231_rank_versus_rho.json` — the complete nine-point `rho` grid at cs 300 **and** cs 800,
four topologies, ~30 min. The instrument's own check is attached and passes on **24 of 24** cells: every (size,
topology) cell at `rho` {0.5, 0.9} reproduces a stored `geometry` block exactly. Registration:
`docs/findings/2026-09-26-registered-the-rank-curve-against-rho.md`; the cs-300 half was read first in
`docs/findings/2026-09-26-the-rank-curve-at-cs-300.md`.*

## 1. The curves

`effective_rank` of the task geometry; `alloy1` destroys the **in**-structure (keeping out-degree), `inalloy1` destroys
the **out**-structure, `erdos_renyi` both.

| `rho` | cs 300 `real` / `alloy1` / `inalloy1` / ER | cs 800 `real` / `alloy1` / `inalloy1` / ER |
|---|---|---|
| 0.5 | 27.25 / 26.52 / 25.82 / 26.75 | 66.54 / 63.14 / 57.56 / 64.39 |
| 0.7 | 26.24 / 22.96 / 22.86 / 25.23 | 63.30 / 45.83 / 36.75 / 57.97 |
| 0.8 | 24.31 / 17.54 / 19.77 / 23.08 | 57.44 / 32.78 / 15.19 / 49.07 |
| 0.9 | 22.11 / 7.20 / 11.62 / 16.31 | 50.24 / 24.28 / **2.40** / 27.92 |
| 0.95 | 19.43 / 2.44 / 4.32 / 8.22 | 37.30 / 22.09 / 1.40 / 11.84 |
| 0.98 | 11.78 / 1.21 / 1.43 / 4.16 | 16.88 / 21.24 / 1.28 / 5.27 |
| 0.99 | 7.25 / 1.05 / 1.10 / 3.48 | 11.80 / 21.01 / 1.29 / 4.20 |
| 0.995 | 5.95 / 1.01 / 1.02 / 3.28 | 11.00 / 20.90 / 1.30 / 3.88 |
| 0.999 | 1.48 / 1.00 / 1.00 / **3.18** | 10.03 / 20.81 / 1.32 / **3.73** |

## 2. P1: MET at cs 300, and the falsifier FIRES at cs 800 for one family — by a saturation, not a reversal

Seven of the eight curves are monotone at every step. The exception is **cs 800 `inalloy1`**, which falls 2.40 → 1.40
→ 1.28 and then **rises to 1.32** at `rho` 0.999 — a 3% uptick. The registered falsifier said "any rise, at any step,
in any family", so it fired, and the honest reading is that this family's collapse **saturates at about 1.3
dimensions** and then moves within a few per cent, rather than continuing to one. Nothing in the grid reverses; but a
prediction of strict monotonicity is not what the data says.

## 3. P3 is MET: the cs-800 separation is systematic in `rho`

`e230` had shown that the cs-800 directional reading rested on **one drawing per cell**: `alloy1`'s twelve drawings at
`rho` 0.9 span 16.44×, more than the 3.01× contrast the record quoted. P3 registered that if the separation is real it
would appear at **more than one** `rho`. Measured, the `alloy1`/`inalloy1` ratio at cs 800:

| `rho` | 0.5 | 0.7 | 0.8 | 0.9 | 0.95 | 0.98 | 0.99 | 0.995 | 0.999 |
|---|---|---|---|---|---|---|---|---|---|
| ratio | 1.10× | 1.25× | 2.16× | **10.10×** | **15.82×** | **16.66×** | **16.35×** | **16.05×** | **15.73×** |

**Six of the nine grid points are above the 4.14× bar**, and the curve is unambiguous in shape: the separation is
absent at low `rho` (1.10×), grows through the middle (2.16× at 0.8), and then **saturates at 15.7–16.7×** from `rho`
0.95 onwards. So the separation is a property of the family at cs 800 and not of the one cell that first showed it.

**Two caveats that keep this from being more than it is.** The curve is **one drawing** at each `rho`
(`--rewire-seed` = `seed0`), and `alloy1`'s own scatter across drawings at cs 800 is 16.44× (`e230`) — the *same
size* as the saturated separation. A different drawing could therefore show a much smaller ratio; what P3 establishes
is that **within** a drawing the separation is systematic in `rho`, and what remains open is whether it survives the
drawing lottery.

## 4. The two new results the completed grid gives

- **The asymmetry's SIGN inverts with circuit size.** At cs 800 the ratio runs 1.10× → 15.7×, i.e. the family whose
  **out**-structure is destroyed (`inalloy1`) collapses to ~1.3 dimensions while the family whose **in**-structure is
  destroyed (`alloy1`) plateaus at ~21. At cs 300 the ratio runs 1.03× → **0.56×** at `rho` 0.95, i.e. the
  out-destroyed family keeps *more* rank than the in-destroyed one, and it is the in-destroyed family that collapses
  furthest. **The two sizes disagree about which side matters**, and the cs-300 crossing (`rho` 0.7 → 0.8) is the
  point where its asymmetry appears at all.
- **`erdos_renyi`'s near-critical plateau is the size-invariant quantity.** At `rho` 0.999 the two-side random null
  sits at **3.18** (cs 300) and **3.73** (cs 800) — a 17% difference across a 2.7× change in circuit size — while
  `real` collapses to **1.48** at cs 300 and **10.03** at cs 800 (a factor of 6.8) and the one-side nulls sit at
  1.00–1.32 at both sizes. So of the four constructions, the one whose survival is *not* a function of the circuit's
  size is the two-side edge-wise random null: the others' near-critical rank is a size-dependent number.

## 5. What this cannot do

- **One statistic.** Whether the *penalty* follows these curves is unmeasured; the excess needs the analytic arm and
  costs minutes per cell.
- **One drawing per cell**, with `alloy1`'s scatter at cs 800 equal to the separation it is being used to demonstrate
  (§3).
- **The last points are near-singular**: at `rho` 0.995 and 0.999 the propagator `(I − W)^-1` is close to singular and
  the reported ranks are participation ratios of a one-mode-dominated spectrum — `1.00` means "as concentrated as the
  statistic can express", not a measured dimension.
- **Two sizes**, so a size × `rho` interaction is described rather than estimated, and the sign inversion in §4 is one
  drawing per cell at two circuit sizes.
- **`rho` mixes propagation depth with weight scale** (`stable_weights` rescales the whole matrix).
