# The rho sweep's first cell: the top step tracks rho, the ladder's order inverts, and the registration's direction claim was written from the wrong denominator

*2026-09-26 08:22, `runs/e229_read_rho_sweep.json` through `e229_read_rho_sweep.py`, reading 1 of the registered
16 cells (`runs/e228_rho05_cs300.json`, 521 s) against the `rho = 0.9` references recomputed from the artifacts that
measured them. The verdicts are REFUSED until the design is complete; what follows is what the first cell already
says, plus a defect in the registration itself.*

## 1. Two ratios, two orders of magnitude apart — and only one of them is the claim

The registered claims are about the **top step**: (Erdős–Rényi excess) ÷ (**the one-side level**, the mean of the
`alloy1` and `inalloy1` excesses). The smoke test that shaped the registration measured a *different* quantity,
Erdős–Rényi ÷ `real`, and on this cell the two read:

| quantity | at cs 300, `rho` 0.5 |
|---|---|
| top step (ER ÷ one-side mean) | **1.018×** |
| Erdős–Rényi ÷ `real` | **109.41×** |

Both are correct; they are not the same number, and the whole reason they diverge is that the **`real` cell's own
excess collapses by a factor of 135** between `rho` 0.9 and 0.5 (0.02978 → **0.00022**) while the one-side level
falls 5.1× and Erdős–Rényi falls 6.4×. The reader prints both, names which one each claim is about, and this
paragraph exists because the first version of the registration did not.

## 2. The references, recomputed — and the record's two spellings turn out to be one level

`e229` recomputes the `rho = 0.9` references from the artifacts rather than from the record's prose, and that
immediately settled a naming question the record leaves implicit:

| reference | ER | one-side level | top step |
|---|---|---|---|
| cs 300 (`e217_ladder_cs300.json`) | 0.15668 | **0.12240** (0.12247 alloy1, 0.12233 inalloy1 — one artifact, both families) | **1.280×** |
| cs 800 (`e208` + `e212`/`e213` + `e216`) | 0.14187 | alloy1 **0.05697** over 7 drawings, inalloy1 **0.04671** over 3 | alloy1 spelling **2.490×**, inalloy1 spelling **3.037×**, mean **2.737×** |

So the record's quoted **2.76×/3.02×** are the *two families' spellings* of one level — 3.02× is Erdős–Rényi over
`inalloy1`'s three drawings (recomputed here as 3.037×) and 2.76× is Erdős–Rényi over `alloy1`'s five `e213`
drawings (2.762×; over all seven `alloy1` artifacts the spelling is 2.490×) — rather than one level and something
else. The cs-300 reference has no such ambiguity: one artifact carries both families and they agree to 0.1%
(0.12247 against 0.12233).

## 3. The first cell: `rho` 0.5 at cs 300

| | `rho` 0.9 (reference, `e217`) | `rho` 0.5 (`e228`) | factor |
|---|---|---|---|
| `real` | 0.02978 | **0.00022** | **÷135** |
| `alloy1` | 0.12247 | 0.02940 | ÷4.2 |
| `inalloy1` | 0.12233 | 0.01876 | ÷6.5 |
| one-side mean | 0.12240 | 0.02408 | ÷5.1 |
| Erdős–Rényi | 0.15668 | 0.02452 | ÷6.4 |
| **top step** | **1.280×** | **1.018×** | |
| ER ÷ `real` | 5.26× | 109.41× | |

Two things in that table are already substantive, and neither needs the other fifteen cells:

- **The top step moves with `rho`, and it moves *down* when `rho` falls** (1.280× → 1.018×), at a fixed circuit
  size. That is the direction question `e228` was registered to ask.
- **The ladder's order inverts.** At `rho` 0.5, Erdős–Rényi's excess (0.02452) is **below** `alloy1`'s (0.02940):
  ER ÷ `alloy1` is **0.83×**. The rung that destroys *both* degree sequences is no longer the worst one, so
  *"destroying more of the degree structure costs more"* is a `rho = 0.9` statement as much as a size-800 one.

## 4. The registration's defect, stated plainly

**R2 registered the direction "the top step falls as `rho` rises (0.5 > 0.9 > 0.99)" and justified it from the smoke
test's arithmetic — "the floor is the more `rho`-sensitive level". But the claim's denominator is the one-side
level, not the floor**: the smoke test's denominator was `real` (that is how it read 4.85× and 76.2×), and `real` is
exactly the level that collapses 135× here while the one-side level falls 5.1×. So the justification does not
support the claim as written, and the first cell **contradicts** it: 0.9 → 1.280× and 0.5 → 1.018× is a *fall* of
the top step as `rho` falls, i.e. the top step *rises* with `rho`.

The claim stays in the registration as written — a registered claim is judged as registered, and the reader will
report R2's verdict against the three `rho` values when the design completes. What this records is that the
*reason* behind R2 was measured on a different ratio, which is the failure mode the registration discipline exists
to make visible: a claim inherited from a smoke test inherits the smoke test's quantity too, unless the unit is
written out.

## 5. What is still open

- **Fifteen cells.** At the time of writing, `runs/e228_rho05_cs300.json` is 1 of 4 runs (cs 300 × `rho` {0.5,
  0.99}; cs 800 × `rho` {0.5, 0.99}); R1 needs the cs-300 `rho` 0.99 cell and R3 needs both cs-800 cells, and the
  reader refuses all three claims until they are on disk rather than judging a partial design.
- **One drawing per cell**, against the one-side families' own spread: `alloy1` spans 3.34× over five drawings at
  cs 800. At cs 300 the reference's two families agree to 0.1%, so a cs-300 *cell* is the tighter test — which is
  the opposite of what a reader would assume from the cs-800 spread alone.
- **`rho` is not a depth knob**: `stable_weights` rescales the whole weight matrix to the target spectral radius,
  so scale moves with depth, and nothing here separates them.
