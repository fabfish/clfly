# The first in-hole penalty does not replicate: two drawings of `alloy1` differ by 2.4×

*2026-09-26 02:25, `runs/e212_alloy_analytic_rs0.json` and `_rs1.json` — stage 2 complete, four cells. Registered at
two realizations precisely so this could be asked. The registration is
`docs/findings/2026-09-26-registered-an-alloy-between-the-two-null-families.md`.*

## 1. The four cells

| drawing | cell | alignment | × chance | analytic excess | sem |
|---|---|---|---|---|---|
| rs0 | `alloy0.75` | 0.04314 | 0.78× | +0.02973 | 0.00023 |
| rs1 | `alloy0.75` | 0.05260 | 0.95× | +0.02415 | 0.00025 |
| rs0 | `alloy1` | **0.14179** | **2.55×** | **+0.10067** | 0.00057 |
| rs1 | `alloy1` | **0.12815** | **2.31×** | **+0.04130** | 0.00070 |

## 2. The verdict on P2, which is a partial one and has to be read carefully

P2 said: *"taking stage 2's cells in alignment order, the analytic penalty is non-decreasing in alignment, and the
cell nearest the ER end is at or above 0.06."*

- **In alignment order the penalties are 0.02973 (0.78×), 0.02415 (0.95×), 0.04130 (2.31×), 0.10067 (2.55×)** — a
  **drop at the first step**, so the monotonicity clause fails.
- The bar clause is met — **0.10067 ≥ 0.06** — but by **one drawing of two**, and the other gives 0.04130.
- That is the registration's own **null**: *"penalties that rise but not monotonically, unresolved at ≤4 cells."*

**And the size of the disagreement is the finding.** The two `alloy1` drawings sit at **2.55× and 2.31× chance** —
alignments 0.14179 and 0.12815, a ratio of 1.11× — and their penalties differ by **a factor of 2.44×**
(0.10067 against 0.04130, span 0.05937). Two drawings of `alloy0.75` at 0.78× and 0.95× agree far better
(0.02973 and 0.02415, span 0.00558).

## 3. The comparison that makes it structural

| population | drawings | penalty | spread |
|---|---|---|---|
| the in-axis cells (34 of them, cs 300–800) | 34 | 0.01101 – 0.05782 | 5.3× across *different* constructions |
| **`alloy1`** (one construction, two drawings) | 2 | 0.04130 – 0.10067 | **2.44× at the SAME construction** |
| Erdős–Rényi (cs 800) | 9 | 0.14134 – 0.14897 | **1.05× across nine drawings** |

**The high regime is the tightest thing in the record and the transitional regime is the loosest.** Nine drawings of
the ER construction agree to 5%, while two drawings of the alloy at 2.3–2.55× chance differ by 144%. So the penalty
near the transition is **draw-dominated**: it depends on the individual graph's idiosyncrasies in a way it does not at
either end. That is a statement about the *quantity*, not about the assay, and it is exactly why the single in-hole
cell published an hour ago could not be quoted as `alloy1`'s value.

## 4. What this does to the previous hour's two findings

- **`docs/findings/2026-09-26-the-hole-has-a-penalty-and-it-is-graded.md` is partially retracted in place**: its
  headline number (0.10067, and the "71% of the way to ER" reading built on it) is **one drawing**, and the second
  drawing is 0.04130. The *existence* of a penalty inside the hole stands (both drawings are far above the in-axis
  regime's lower end and far below ER); the *graded* reading does not.
- **C3's transition is not yet located, and the reason is now measured rather than assumed**: at 2.3–2.55× chance the
  penalty varies by 2.4× between drawings, so a design with one cell per alignment band cannot say whether the
  response is graded or stepped. What the next design needs is **several drawings per alignment band**, with the
  penalty regressed on the *measured* alignment of each drawing — since the drawings' alignments also move (2.55× vs
  2.31× here), a design that fixes the requested fraction and hopes the alignment repeats will confound the two.

## 5. What survives, stated as the honest summary

1. **The hole has penalties** — 0.02973/0.02415 at 0.78–0.95× chance and 0.10067/0.04130 at 2.31–2.55× — where the
   record had nothing a few hours ago, and all four are far above the in-axis floor (0.01237) and far below ER
   (0.14134–0.14897).
2. **The alloy is a monotone alignment axis** (fraction 0.25 → 1 gives 0.24× → 2.55× chance), which the swap strength
   never was.
3. **The transition region is draw-dominated**, and that is the design constraint C3 now carries: quote a band, not a
   cell, and average drawings inside it.
