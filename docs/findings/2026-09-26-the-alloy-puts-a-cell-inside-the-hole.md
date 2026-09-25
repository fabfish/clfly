# The alloy puts a cell inside the hole: 2.55× chance, the first one the record has ever had

*2026-09-26 02:09, `runs/e212_alloy_screen_rs0.json` — the geometry-only screen, 451.9 s (7.5 min) for four cells at
~113 s each. Stage 2 (the penalty cells) is in flight. The registration is
`docs/findings/2026-09-26-registered-an-alloy-between-the-two-null-families.md`.*

## 1. The screen's table

| alloy fraction | alignment | × chance | `top_eig_share` | effective rank | in the hole |
|---|---|---|---|---|---|
| `alloy0.25` | 0.01354 | 0.24× | 0.150 | 42.79 | no |
| `alloy0.5` | 0.02294 | 0.41× | 0.242 | 21.82 | no |
| `alloy0.75` | 0.04314 | 0.78× | 0.513 | 4.21 | no |
| **`alloy1`** | **0.14179** | **2.55×** | 0.167 | 24.28 | **YES** |

**P1 is met in its first clause and its registered null landed in the second.** One fraction is inside
`[0.09101, 0.27135]` — the **first cell the record has ever placed strictly inside the hole**, where 22 swap cells
had reached only 1.72× chance and the Erdős–Rényi family sits at 4.89–5.23× — but none of the four is above 0.20, so
P1's null ("a fraction inside the band but none above 0.20, which would still allow the lower half of the transition
to be read") is what happened. The upper half of the hole, `[0.20, 0.271]`, is still empty.

## 2. And the alloy is a monotone axis, which the swap family never was

**The alignment rises with the fraction at every step** — 0.01354 → 0.02294 → 0.04314 → 0.14179 — whereas the swap
family's means fell from `swap8` to `swap32` and were flat across a 128× range of strengths. That is the difference
the two operations predict: a swap conserves in-degree *and* out-degree, so it cannot move the tasks' subspaces; the
alloy frees the in-degree, and alignment responds to it monotonically.

Note what else moves with it: `effective_rank` collapses (42.8 → 21.8 → 4.2) and then *recovers* (24.3) at the last
step, and `top_eig_share` peaks at 0.513 in the middle. So the alloy is not a one-parameter family either — the
statistics are not co-monotone at `alloy1`, which is the same caution the swap family's cells produced.

## 3. What stage 2 will read, and what it will decide

Stage 2 pays for full analytic cells at `alloy0.75` and `alloy1` at **two realizations each** (`rewire-seed` 0 and 1),
which is four cells at 225–240 s ≈ 16 min. That design is not decoration: the swap family's realization spread was
**1.60–2.05× at every strength**, so a single drawing of `alloy1` would not be a measurement of `alloy1`, and P2's
"non-decreasing in alignment" needs at least two cells with a penalty each.

**P2's bar is the one `e208`'s T2 registered** — the cell nearest the ER end at or above **0.06** is graded, at or
below **0.035** is the falsifier, which would say the hole behaves like the in-axis regime and the jump happens only
at the Erdős–Rényi construction itself. If the falsifier lands, **alignment is a correlate rather than the driver**
and C3 needs the construction's other properties; if the bar is met, the record has its first graded reading across
the transition and C3's statement becomes a measurement rather than a plan.

## 4. What this cannot do yet

The screen has no arms, so nothing here is a penalty; the upper half of the hole `[0.20, 0.271]` is still empty and
`alloy1` is the ceiling of this family by construction (a fraction cannot exceed 1), so reaching it needs a *third*
construction — an alloy that also randomises a fraction of the **sources**, or a direct mix with the Erdős–Rényi edge
set; and the task draw is fixed at `seed0` 0 as everywhere in this axis.
