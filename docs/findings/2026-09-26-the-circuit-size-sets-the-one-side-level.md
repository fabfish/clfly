# The circuit size sets the one-side level; the share only nudges it

*2026-09-26 06:07, `runs/e223_cs400_support80_rs{0,1}.json` — two drawings, eight cells, ~12 min. Read by
`e224_share_vs_size_read.py`, exit 0, with both references recomputed from the artifacts that measured them. The
registration is `docs/findings/2026-09-26-registered-the-share-against-the-size.md`.*

## 1. The verdicts: S1 and S2 both land in their null bands

| | claim | verdict |
|---|---|---|
| **S1** | at cs 400 the one-side level at support 80 is ≥1.5× below its mean at support 40 | **null band** — **1.16×** lower (0.11434 against 0.13267) |
| **S2** | the level lies below the midpoint (0.09114) of the two shares it sits between | **null band** — **0.11434**, moved toward the larger share but not past halfway |

## 2. The cells

| drawing | `alloy1` | `inalloy1` | `erdos_renyi` | one-side mean | top step | `real` |
|---|---|---|---|---|---|---|
| rs0 | 0.12062 | 0.11839 | 0.13711 | 0.11950 | 1.14× | **0.01774** |
| rs1 | 0.10788 | 0.11047 | 0.14002 | 0.10918 | 1.27× | **0.01774** |

**And the answer to the two-candidate question is the size.** At cs 400 a **7.9%** share gives 0.11434 while cs 800
at a **6.1%** share gives 0.04962 — a factor of **2.3×** between two nearly equal shares at different circuit sizes.
Within a size, a larger share lowers the level mildly: **1.16×** for a doubling at cs 400, against the **1.42×** an
eightfold change produced at cs 800. So the one-side level is **a size effect with a mild share effect on top**, not
a share effect with a size correction.

**And the top step at this support is 1.14–1.27×** — below 1.5×, as at the cs-400 convention (1.11×), so the small
top step at cs 400 is not a support artifact either. Together with `e221` (where support 20 and 160 at cs 800 gave
1.96× and 2.10×, both *below* the convention's 2.76×), the top step's size dependence has now survived tests of
every variable this line can vary cheaply: **share, support, the sign pattern (`e215`), and the number of destroyed
degree sequences (`e216`)**. None of them explains it, and the honest state of the mechanism question is that it is
**open on a variable nobody has varied**.

## 3. Two details worth keeping

- **`real` reproduced exactly across the two drawings** — 0.01774 in both, to five decimals — because the rewiring
  does not touch the connectome. That is a same-configuration reproduction datum for the `real` cell and an internal
  consistency check on the sweep: only the three rewired levels move.
- **This is the tightest drawing spread any of the one-side constructions has shown**: 1.09× across two drawings,
  against `alloy1`'s **3.34×** over five at cs 800/convention support and **1.49×** at cs 300. So the volatility the
  earlier fires measured is not a property of "the one-side null" in general — it depends on the cell.

## 4. What the record now says about the mechanism

| variable | tested by | effect on the one-side level | effect on the top step |
|---|---|---|---|
| the share of neurons engaged | `e221`, `e223` | **mild** (1.42× over an 8× change; 1.16× over a 2× change) | **none** (non-monotone) |
| the circuit size | `e217`, `e219` | **dominant** (2.6–2.9× between cs 800 and cs 300–400) | **the whole effect** (2.76× → 1.18×) |
| the sign pattern | `e215` | none (0.028 at the axis's level) | not tested |
| degree sequences destroyed | `e216` | the ladder's own structure | not tested |

**So the one-side level is a size effect with a mild share effect, and the top step's size dependence is
unexplained** — the mechanism question is open on a variable this line has not varied (the assembly geometry, the
propagation depth, the circuit's edge density, or something about how a smaller circuit's neurons divide into
assemblies).

## 5. What this cannot do

Two drawings per cell, with the small spreads quoted above; the share and the neuron count still move together
across circuit sizes even though this design held the size fixed and moved the share; the support at cs 400 is
varied at exactly two values (40 and 80) so the 1.16× is a two-point slope; and the assembly geometry
(`TASK_ASSEMBLIES`, `rho`, the propagation depth) and the edge density are held at their defaults throughout —
which is where the remaining candidates live.
