# The penalty has two regimes and a hole between them, which is what C3 has been missing

*2026-09-26 00:05. Code: `experiments/e207_penalty_driver_join.py` (analysis only, reads `runs/`), tests:
`tests/test_e207_penalty_driver_join.py` (4 tests). Data: the 42 (artifact, topology) cells in the record that carry
both a `geometry` block and an analytic diagonalisation penalty — 25 artifacts, circuit sizes 300 to 800.*

## 1. The join nobody had made

C3 is this plan's only claim with no measurement behind it, and its status note says the mechanism it assumed was
refuted and that what remains *"is not yet well enough understood to state as a testable prediction"*. The plan also
records what the penalty does **not** track: across the degree-preserving swap family it moves *opposite* to task
overlap.

But every topology in that family is written with a **`geometry` block** — eight measured statistics of the task
subspaces, including how far from orthogonal they are (`all_pairs_alignment` against `chance_alignment`), the
effective rank, and the share of the top eigenvalue — and the same artifact carries the penalty for that topology. So
the question *which measured geometry does the penalty track?* was answerable from disk, at six circuit sizes, and had
never been asked.

## 2. The correlational answer is: nothing, consistently

Rank association between the penalty and each statistic, inside each artifact's own family (three to five topologies):

| statistic | families | + | − | signs |
|---|---|---|---|---|
| `all_pairs_alignment` | 7 | 5 | 2 | +1.0 −0.5 +1.0 +0.5 −0.5 +0.4 +0.4 |
| `consecutive_alignment` | 7 | 5 | 2 | +1.0 −0.5 +1.0 +0.5 −0.5 +0.4 +0.4 |
| `effective_rank` | 7 | 4 | 3 | −0.5 +0.5 −1.0 −0.5 +0.5 +0.1 +0.4 |
| `flattening` | 7 | 4 | 3 | −0.5 +0.5 −1.0 −0.5 +0.5 +0.1 +0.4 |
| `top_eig_share` | 7 | 3 | 4 | +0.5 −0.5 +1.0 +0.5 −0.5 −0.6 −0.8 |

**All five change sign across circuit sizes.** The alignment statistics are positive at cs 300, 500 and 600 and
negative at cs 400 and 700; the sign is a property of the size, not of the substrate. This is C1's own history
reproduced in a second quantity: the plan records that *"the sign alternates, and every step is decisive" was a
property of having exactly four points*, and here three-point families produce the same alternation.

**And the Pearson coefficients were a trap I nearly reported**: across `e2_analytic`'s five topologies the alignment
correlation is `r = +0.971` — but `rho = +0.400`, because Erdős–Rényi is a different regime. The module prints the
rank correlation (which decides), the Pearson, and the Pearson with ER removed, so the outlier's leverage is visible
rather than argued about. A first version printed only Pearson.

## 3. The sorted table is where the shape lives

Sorted by alignment, the 42 cells are not a gradient — they are **two blocks with nothing between them**:

| regime | cells | alignment | × chance | penalty |
|---|---|---|---|---|
| the biological axis (`real`, `swap0.1`, `swap0.5`, `swap2`, and the rewire families) | **34** | 0.00444 – **0.08475** | 0.07 – 1.53 | **0.01101 – 0.05782** (span 0.04681) |
| Erdős–Rényi | **8** | **0.27135** – 0.29039 | 4.89 – 5.23 | **0.14134 – 0.14897** (span 0.00763) |

- **The gap between the two penalty ranges is 0.08352**, with no cell inside it.
- **The alignment hole is a factor 3.2 wide** (0.08475 → 0.27135, i.e. 0.18660 of alignment) with no cell in it.
- **The high regime is tight**: eight independent rewiring realizations and two circuit sizes give a penalty band
  0.0076 wide, while the 34 in-axis cells — at a third of that penalty — span six times as much.
- **Within the axis the penalty is flat and even falls**: the `swap2` cells at 1.09–1.15× chance have the *lowest*
  penalties in the record (0.01237, 0.01255, 0.01255), i.e. at the point where the tasks become as aligned as chance
  the penalty does not rise — the plan's "the gap moves opposite to interference", restated in geometry terms.

## 4. What this does to C3

**C3 gets a testable form and a named missing measurement.** The restatement the plan asked for, in the record's own
units:

> **The penalty is flat at ≈0.02 across the biological axis at every degree of rewiring that keeps the tasks'
> alignment below ~1.5× chance, and it is tight at ≈0.142 once alignment exceeds ~5× chance.** Whether the transition
> is a threshold or a steep gradient is **unmeasured**: the record has no cell with alignment between 0.085 and 0.271.

**The test that would settle it** is a family sweeping that hole — a densification or rewiring axis reaching 0.1–0.25
alignment. Its falsifier is precise: **a cell inside the hole with a penalty in between (≈0.08) makes the response
graded, while a cell inside the hole at ≈0.02 leaves the jump as a property of the ER construction** (degree
distribution, densification) rather than of the tasks' alignment at all. Both outcomes are informative, which is what
C3 lacked.

**What this cannot do**: it is a join across families measured once each, so every sign is descriptive; it cannot
separate alignment from effective rank and `top_eig_share`, which move together along a swap axis by construction;
the 8 high-regime cells are all ER and 6 of them are rewiring realizations of one construction, so the regime's
tightness is a statement about that construction; and nothing here speaks for the network substrate, whose penalty is
a different instrument.
