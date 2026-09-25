# Across the widest alignment gap the penalty falls, and across the narrowest it triples

*2026-09-26 03:03. `e207_penalty_driver_join.py` gained a **coverage census** — the record's cells sorted by measured
alignment, with the gaps between consecutive cells and the two penalities either side of each. It reads 60 cells
(25 artifacts plus the alloy work of the last hour) from alignment 0.00444 to 0.29039.*

## 1. The census

| gap in alignment | from | penalty there | to | penalty there | penalty change across the gap |
|---|---|---|---|---|---|
| **0.09059** | `e213` rs0 `alloy1` (0.14179) | +0.10067 | `e213` rs2 `alloy1` (0.23632) | +0.04704 | **−0.05363** (falls by 53%) |
| **0.03897** | `e213` rs2 `alloy1` (0.23632) | +0.04704 | `e33` `erdos_renyi` (0.27135) | +0.14897 | **+0.10193** (triples) |
| 0.01454 | `e208` `swap8` (0.09101) | +0.00598 | `e213` rs2 `alloy0.9` (0.10555) | +0.03812 | +0.03214 |
| 0.01364 | `e213` rs1 `alloy1` (0.12815) | +0.04130 | `e212` rs0 `alloy1` (0.14179) | +0.10067 | +0.05937 |

**The record's widest alignment gap hides a *fall*, and its second-widest — half the width — hides a *tripling*.**

That is the whole argument against reading the penalty off alignment, and it needs no new runs: it is a statement about
cells that have all been measured. Across 0.09059 of alignment the penalty drops by more than half; across 0.03897 it
more than triples. A monotone function of alignment cannot do both, and neither can a single-valued function of
alignment with any shape.

## 2. What the two cells at the ends of the narrow gap actually are

- `e213` rs2 `alloy1`: alignment 0.23632 (**4.25× chance**), excess **+0.04704 ± 0.00066**.
- `e33_er_rewire2`: alignment 0.27135 (**4.89× chance**), excess **+0.14897**.

So at **87% of the ER alignment** the alloy's penalty is **32% of the ER penalty**. If the penalty were a function of
alignment, 4.25× chance would already be most of the way up the transition; it is not — it is roughly where the
in-axis cells are (0.012–0.058).

**And the widest gap's pair says the same thing from the other side**: two `alloy1` drawings — the SAME construction,
the SAME fraction — sit 0.09059 apart in alignment with penalties 0.10067 and 0.04704. That is the draw-dominated
result of the previous fire, now visible as a *coverage* fact: the construction's own drawings scatter across more
alignment than any design would have bet on, and the penalty moves with *something else*.

## 3. What this does to C3

C3's transition cannot be located on the alignment axis by any design that indexes cells by alignment and hopes the
penalty follows — the two largest gaps in the record's own coverage already break monotonicity. What the census
implies instead:

- **the driver is a property of the construction** that alignment only partly reflects: the degree-preserving walk
  (≤1.72× chance), the alloy (2.3–4.3× chance, both degrees of freedom moving), and the edge-count-matched
  Erdős–Rényi (4.9–5.2× chance, no structure at all) are three *kinds* of null, and the penalty's jump sits between
  the second and the third even where their alignments nearly overlap;
- **the interval a design should aim at is `[0.23632, 0.27135]`** — 0.039 of alignment where a 3.2× penalty change
  has to happen, and the only interval in the record where two measured cells bracket a change of that size;
- **and any claim about the transition must be made between constructions, not along an alignment axis**, because the
  alloy's own drawings move 0.09 in alignment without the penalty following.

## 4. What this cannot do

The census is a description of 60 measured cells and not a curve: the gaps are *between specific samples*, the cells
are from six circuit sizes and three topologies with one or three seeds each, and nothing here separates alignment from
`top_eig_share` and `effective_rank` (the census prints only alignment). It also cannot say *which* construction
property drives the penalty — that is the question the alloy work has now made askable and has not yet answered.
