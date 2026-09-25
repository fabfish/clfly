# The swap walk does not converge to the Erdős–Rényi alignment, so the transition is not on the rewiring axis

*2026-09-26 01:51, `runs/e211_convergence_probe.json` — 481.5 s for two cells (240 s per cell against the screen's
121 s: the swap operation itself gets slower as the edge set is scrambled further). The registration is
`docs/findings/2026-09-26-registered-does-the-swap-walk-converge-to-the-erdos-renyi-alignment.md`.*

## 1. The verdicts

| | claim | verdict |
|---|---|---|
| **V1** | at least one cell above **0.09120** (does the walk climb?) | **MET, by one cell and one only — which is the registered null** |
| **V2** | both cells **below 0.20** (is the walk's level below the ER family's?) | **MET** |

| cell | alignment | × chance | `top_eig_share` | effective rank |
|---|---|---|---|---|
| `swap256` | **0.09560** | **1.72×** | 0.506 | 4.51 |
| `swap1024` | 0.06901 | 1.24× | 0.386 | 10.28 |

`swap256`'s 0.09560 is **the highest alignment the swap family has produced anywhere in this record** — above the
screen's maximum (0.09120) — and `swap1024` falls back to 0.06901. The V1 null was written as *"exactly one of the two
climbs and the other does not, which is unresolved ordering at two cells"*, and that is precisely what happened, so
V1's bar is met while its **pattern is the null**: one cell rising 4.8% over the screen's maximum, and a 16× larger
scramble landing *lower*.

## 2. What that decides

**Across strengths 8 → 1024 — a 128× range — and 22 cells, the swap family's alignment never leaves 0.65–1.72×
chance and does not trend upward.** The Erdős–Rényi family sits at **4.89–5.23× chance** (nine cells), so V2's MET
puts the walk **at least 1.36× below the lowest ER cell and in practice 2.8× below it**.

- **H2 survives, H1 is not supported.** The degree-preserving swap walk does not converge to the edge-count-matched
  Erdős–Rényi alignment. They are different **kinds** of null: one saturates around chance and one sits five times
  above it.
- **The interval [0.09101, 0.27135] is therefore not reachable by rewiring harder**, and the transition between the
  two penalty regimes (flat at 0.006–0.023 up to 1.72× chance, tight at 0.141–0.149 at 4.89–5.23×) is a difference
  between two **constructions**, not an alignment value on a rewiring axis.
- **C3's statement changes accordingly**: what has to be interpolated is *between ensembles* — a construction whose
  alignment can be placed anywhere between chance and 5× — and no further swap strength will do it. That is a sharper
  claim than "the transition is unmeasured", and it is a negative result of exactly the kind this line has been
  producing: the design everyone reaches for (more rewiring) cannot answer the question.

## 3. The cost datum, which is its own small finding

Two cells cost **481.5 s, i.e. 240 s per cell**, where the screen's four cells per run cost 121.4 s each. The mode is
identical and the circuit, tasks and seeds are identical, so **the difference is the swap operation itself**: scrambling
an edge set 256 or 1024 times costs more than scrambling it 8 to 64 times, and it is the only term in the pipeline that
scales with the strength. Rule 49's price for this family therefore has to be quoted **per strength**, not per cell —
which is the same defect the `e193` cost work found in whole-command averages two days ago, in a new place.

## 4. What this cannot do

It is two cells at one realization and one circuit size, so it bounds the walk's level rather than mapping it; it has
no penalty measurements at all (`--geometry-only`), so nothing here says where the penalty changes; it cannot rule out
a slow approach needing 10⁴× rather than 128× (that is what V1's falsifier wording is for, and a null result is a
statement about the range tested); and it cannot separate `top_eig_share` and `effective_rank` from alignment — note
that `swap256`'s `top_eig_share` (0.506) and `effective_rank` (4.51) sit *between* the screen's and the ER family's,
so the statistics are not converging to the ER values either, which is a second, independent sign that these are two
ensembles rather than two points on one axis.
