# The screen's three claims are all met, and its own premise is refuted for the second time

*2026-09-26 01:39, `runs/e209_screen_rs0.json` … `rs4.json` — five runs, 2428.5 s in total (40.5 min, **121.4 s per
cell** against the registered 112 s). Read by `e210_alignment_screen_read.py`, exit 0. The registration is
`docs/findings/2026-09-26-registered-screening-by-alignment-then-paying-for-the-band.md`.*

## 1. The verdicts

| | claim | verdict |
|---|---|---|
| **S1** | every cell has an alignment and no arm, twenty cells under 45 min | **MET** — 20 cells, 0 carrying an arm, 40.5 min |
| **S2** | at least one cell inside `[0.09101, 0.27135]` | **MET** — **2 cells**, both at the floor |
| **S3** | the span at a fixed strength is ≥ 1.5× for at least two of four strengths | **MET** — **all four**, 1.60× to 2.05× |

## 2. S2 is met by the thinnest possible margin, and that is the finding

The two cells inside the band are `swap8` at **0.09101** (rs0) and **0.09120** (rs3) — 1.64× chance, and **the
largest alignment anywhere in the twenty cells**. Nothing in the screen is above 1.64× chance; the Erdős–Rényi family
at the same circuit size sits at 0.27135–0.29039 (**4.89–5.23× chance**, nine cells). So the screen's own shopping
list for stage 2 is **two cells, both standing on the hole's floor**, and the interval's interior stays empty.

## 3. And the premise both this screen and the last one rested on is refuted

The registration said the alignment axis "grows roughly 2.4–2.8× per 5× of swap strength", extrapolated from
`real` / `swap0.1` / `swap0.5` / `swap2`. Twenty cells now say otherwise — the **means** by strength are

| strength | five realizations | mean | span |
|---|---|---|---|
| `swap8` | 0.09101, 0.04929, 0.05502, 0.09120, 0.06374 | **0.07005** | 1.85× |
| `swap16` | 0.04146, 0.07104, 0.08035, 0.05089, 0.03911 | **0.05657** | 2.05× |
| `swap32` | 0.04161, 0.03978, 0.03851, 0.05499, 0.03427 | **0.04183** | 1.60× |
| `swap64` | 0.03596, 0.04596, 0.03633, 0.04731, 0.06144 | **0.04540** | 1.71× |

**The mean alignment does not grow with strength — it falls from `swap8` to `swap32` and then is flat**, across an
8× range of strengths. Six of the twenty cells are *below* chance (0.65–0.99×), and the highest is 1.64×. So:

- **the strength axis is not an alignment axis** at the high end, and adding strengths cannot fill the interval
  (this was `e208`'s lesson, now confirmed on 20 cells rather than 3);
- **the alignment hole is a difference between two kinds of null**, not a location on a rewiring continuum: the
  degree-preserving swap walk saturates near chance while the edge-count-matched Erdős–Rényi ensemble sits at
  ~5× chance, and the two ranges are disjoint by a factor of 3.0.

That is what `e211` — registered an hour ago, running now — tests directly: `swap256` and `swap1024` at the same
realization, with V1 asking whether the walk climbs past 0.09120 at all and V2 asking whether it stays below 0.20.

## 4. S3's MET is the design fact worth carrying forward

**Every** strength's five realizations span 1.60–2.05×, where the earlier reading from `e207`'s join had 1.68× at
`swap0.5` and 2.60× at `swap2`. So the realization spread is not a property of the low end of the family: at
strengths 8 through 64, one drawing per strength is **never** an adequate measurement of that strength — it is
±40% on a quantity the whole C3 argument is indexed by. The registered null for S3 ("no strength above 1.5×, which
would rehabilitate the strength axis as an x-axis") did not merely fail to land; it is refuted at four strengths out
of four.

## 5. What this changes

- **Stage 2's shopping list is two floor cells.** Whether they are worth 225 s each is now a real question: they
  would put the penalty at 1.64× chance, which `e208` already measured at 0.00598 — the lowest value in the record —
  so paying for more cells at that same alignment would be paying twice for one point. The honest use of stage 2 is
  therefore **not** the screen's floor cells but whatever `e211` finds above 0.0912, if anything.
- **C3's restatement is unchanged in its numbers and sharper in its structure**: the penalty is flat at 0.006–0.023
  for every cell up to 1.64× chance and tight at 0.141–0.149 at 4.89–5.23× chance, and **the interval between the two
  regimes is not reachable by rewiring harder** if `e211`'s V1 falsifier lands. The transition would then be a
  property of the *null's construction* rather than of any alignment value in between.

## 6. What this cannot do

It has no penalty measurements at all (the mode has no arms by construction), so nothing here says where the penalty
changes; it cannot separate `top_eig_share` and `effective_rank` from alignment; it holds the task draw fixed at
`seed0` 0; and twenty cells in four strengths is not a distribution — the spans are ranges over five drawings, which
is exactly the statistic that says a distribution is what the design still lacks.
