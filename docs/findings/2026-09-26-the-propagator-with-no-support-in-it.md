# The propagator with no support in it: `G`'s own rank falls 510 → 1.04, `erdos_renyi` stops at 4.14, and the ladder inverts at high `rho`

*2026-09-26 12:45, `runs/e237_propagator_spectrum.json` through `e237_propagator_spectrum.py` — the whole `n × n`
operator `G = (I − W)^-1`, its own singular spectrum, **no support anywhere in the measurement**. Six `rho` values at
both sizes, four topologies, ~0.5 s per cell. The registration's three claims get verdicts: V1's falsifier fires for
one family, V2 is MET, V3's falsifier fires.*

## 1. The whole operator, and it collapses

`pr_G` is the participation ratio over `G`'s squared singular values — the rank of the *entire* propagator.

| `pr_G` | 0.7 | 0.8 | 0.9 | 0.95 | 0.98 | 0.99 | monotone |
|---|---|---|---|---|---|---|---|
| cs 300 `real` | **510.57** | 147.06 | 12.63 | 2.53 | 1.19 | **1.04** | yes |
| cs 300 `alloy1` | 109.34 | 39.04 | 8.14 | 2.44 | 1.21 | 1.05 | yes |
| cs 300 `inalloy1` | 184.38 | 70.73 | 12.92 | 3.36 | 1.32 | 1.08 | yes |
| cs 300 `erdos_renyi` | 269.63 | 143.73 | 43.03 | 12.43 | 5.09 | **4.14** | yes |
| cs 800 `real` | **873.50** | 328.92 | 28.61 | 4.13 | 1.34 | 1.08 | yes |
| cs 800 `alloy1` | 132.62 | 61.66 | 37.06 | 32.18 | 30.41 | **29.94** | yes |
| cs 800 `inalloy1` | 55.25 | 9.35 | 1.94 | 1.33 | 1.25 | **1.26** | **no** |
| cs 800 `erdos_renyi` | 344.34 | 172.11 | 48.12 | 14.54 | 5.62 | 4.35 | yes |

- **V1 is MET for seven of eight families and its falsifier fires for cs-800 `inalloy1`** — which falls to 1.25 and
  then *rises* to 1.26, a 0.8% uptick, exactly the saturation `e231` saw on the support side (there, 1.28 → 1.32).
- **The extent is family-specific**: `real` falls by a factor of **491** at cs 300 and 809 at cs 800, while
  `erdos_renyi` stops at **4.14** and cs-800 `alloy1` barely moves past `rho` 0.9 (**29.94**, a plateau that mirrors
  the one its *task* rank showed). The condition number of `G` for `real` runs 8.7 → **414.6** (cs 300) and 7.9 →
  351.5 (cs 800).
- **So the collapse is a property of the operator itself**, measured with no support, no seeds and no tasks: the
  question "why does the geometry's rank collapse with `rho`" now has a support-free counterpart, and the answer is
  that the propagation *becomes rank-one* — its leading singular share reaches 0.978 (`real`, cs 300/`rho` 0.99).

## 2. The size ladder: monotone at low `rho`, and it INVERTS at high `rho`

| cs 300, `rho` 0.98 | whole `G` (952 cols) | union (148) | one assembly (30) |
|---|---|---|---|
| `real` | **1.19** | 1.34 | **12.45** |
| `alloy1` | 1.21 | 1.22 | 1.21 |
| `inalloy1` | 1.32 | 1.26 | 1.44 |
| `erdos_renyi` | 5.09 | 4.44 | 4.14 |

At `rho` 0.7 the ladder is the obvious one — `real` reads 510.57 whole, 137.49 union, 28.38 assembly: **more columns,
more rank**. By `rho` 0.98 it has **inverted for `real`**: the whole operator is at 1.19 while a 30-column slice of it
is at 12.45 (10×). **V2 is MET** (the whole is below a slice in some families and not in others): `real` 1.04 against
7.68 and `inalloy1` 1.08 against 1.10 at `rho` 0.99 escape; `alloy1` (1.05 against 1.05) and `erdos_renyi` (4.14
against 3.47) do not.

**This is what `e236` needed to complete its own correction.** `e235`'s union column collapsed sooner than an
assembly's, and `e236` showed the union is not what the tasks use; this measurement shows *why the union looked
pathological*: near criticality a wider slice of `G` is a *less* rich object than a narrower one, because the leading
direction is shared across columns and the narrow slice happens to miss most of it.

## 3. Why a narrow slice escapes: the assemblies hold 9–35% of the leading direction

The leading right-singular vector's mass on the assemblies' neurons, at `rho` 0.99:

| cs 300 | `real` 0.088 | `alloy1` 0.146 | `inalloy1` 0.166 | `erdos_renyi` 0.172 |
|---|---|---|---|---|
| cs 800 | 0.275 | 0.284 | 0.350 | 0.292 |

So the assemblies carry **at most a third** of the mode that dominates `G` — which is the mechanism by which a slice
can be richer than the whole. **V3's falsifier fires**: the escape ordering (cs 300, assembly ÷ whole at `rho` 0.99:
`real` **7.4×**, `erdos_renyi` 0.84×, `inalloy1` 1.02×, `alloy1` 1.00×) follows the share ordering only for `real`
(smallest share, by far the largest escape); among the other three the shares are 0.146/0.166/0.172 and the escapes
1.00/1.02/0.84 do **not** order with them. The honest reading is that `erdos_renyi` is not a slice effect at all: its
whole-`G` is not near rank-one (4.14) in the first place, so its slice inherits a genuinely richer operator rather
than escaping a collapsed one.

## 4. What this cannot do

- **`rho` rescales the whole weight matrix**, so the ladder is a statement about the rescaled operator and not about
  propagation depth alone; nothing here separates the two.
- **One drawing per cell** (`seed0`), and `e232` measured that the in/out comparison is drawing-dependent — cs-800
  `alloy1`'s plateau (29.94) and `inalloy1`'s collapse are single drawings.
- **The participation ratio is one summary** of a spectrum, and the whole-`G` measurement is *not* what the tasks use:
  tasks use slices, so this is the operator's own behaviour and an upper bound on what the geometry can inherit.
- **The assemblies' share uses `seed0`'s supports** (three assemblies, `seed0` 0), so it is a sample of one draw of
  those supports rather than the population — the same convention every other cell in this line uses.
