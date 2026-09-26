# Registered: a second equal-count-three base, at the corpus's flattest kind-1 geometry

*2026-09-26 16:40, registered before its runs. Runs: `e2_topology_gap` at `--circuit-size 400 --support 40 --seeds 3
--seed0 0 -q 0.02 --topologies swap0.5,swap2,signshuffle --no-realized --rewire-seed {3,4,5}` — **three runs, one cell
each**, to be written as `e250_cs400_sup40_kind0_rs{3,4,5}.json`. Three runs because the base being matched has three
drawings per family.*

## 1. Why this cell, and what makes it comparable

`e248` built an **equal-count-three** base at cs 300/support 30 — six families, three drawings each — and read its
(1, 0) margin as **1.008**, a tie. `e249` then put the same quantity at two more cells and found it rises with the
cell's kind-1 **rank contrast** (0.851, 0.935, 1.660 against rank spreads of 2.4×, 3.4×, 11×), while noting that the
margin moves 1.95× where the contrast moves 5.16×.

The relation has no point at the bottom of its range, and **cs 400/support 40 is that point**: its kind-1 rank spreads
are **1.53×** and **1.59×**, the smallest in the corpus (against cs 300/support 30's 2.73× and 2.08×, whose base is the
only other one at count three). Its kind-1 and kind-2 families carry **exactly three excess drawings each**
(`rewire_seed` 0, 1, 2) and it has **no kind-0 family at all**, so three runs at seeds 3, 4 and 5 give a base that is
**equal-count-three — the same footing as `e248`'s** — and the two margins are directly comparable rather than
count-matched after the fact.

    cs 300/support 30   count-3 base   margin 1.008   kind-1 rank spreads 2.73x, 2.08x
    cs 400/support 40   count-3 base   margin ?       kind-1 rank spreads 1.53x, 1.59x

## 2. The registered claims

- **U1 — the prediction.** At cs 400/support 40 with three drawings per family the (1, 0) margin is **below 1.008**,
  the value the same statistic takes at cs 300/support 30 on the same footing — i.e. **the flatter geometry gives the
  smaller margin**, and specifically the no-destruction rung is the looser of the two (margin below 1). **Falsifier**:
  the margin at or above **1.10**, which would be a reversal at the cell whose kind-1 geometry is the flattest in the
  corpus and would break the relation rather than extend it; **null**: 1.008 to 1.10.
- **U2 — the survivor.** With three drawings per family `erdos_renyi` is the tightest family at this cell, as it is in
  every cell, at every count and under every leave-one-out subset measured so far.
- **U3 — reported, not claimed.** The three kinds' levels at this cell (kind 0 is expected near the floor, 0.02 to
  0.06, against kind 1's 0.12 to 0.14), so the confound is stated beside the result as it has been in every fire since
  `e244`.
- **U4 — reported, not claimed.** The two count-three bases side by side — margins, kind-1 rank contrasts, and each
  family's three drawings — which is the low end of the relation `e249` left as a three-point trend.

## 3. Cost, and what it cannot do

**Cost**: cs 300's cells measured 372 s for four cells and cs 400 was similar, so three topologies are ≈5 min per run
and **three runs ≈15 min** — about one fire.

It cannot: turn a trend into a relation — four points with a **simulated** driver that is read off **the same
drawings** as the quantity it is meant to explain, so the correlation is not evidence of mechanism; fix the confound
that the two kinds sit at different levels (kind 0 near the floor, kind 1 at 0.12–0.14 here); speak for any cell whose
kind-0 rung is still unmeasured; avoid the corpus's noisiest regime, since the *other* two count-3 bases in the record
are `e248`'s and this one and both are single cells at one `rho` (the builder's default); or make the base
equally **drawn** — its kind-1 and kind-2 drawings come from `e217`/`e219`, its kind-0 drawings from these runs.
