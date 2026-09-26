# Registered: the register's own number gets a designed interval

*2026-09-26 13:55. Runs: `e2_topology_gap` at cs 800, support 80, `rho` 0.9 (the builder's default),
`--topologies alloy1,inalloy1,erdos_renyi --no-realized --rewire-seed {6,7,8}` — **three runs, three cells each,
~36 min**, to be written as `e243_convention_rs{6,7,8}.json`. Nothing else changes; the seeds 6–8 are unused at this
cell by anything on disk.*

## 1. Why the convention cell, and why now

`e242` bracketed the register's headline figures with the drawings behind them and found that the convention cell is
**the only cell where that can be done at all**: supports 20 and 160 have 2 drawings per family, every `rho` above 0.9
at support 80 has one, and `real` never has two different drawings. Its bracket rested on runs that some experiment
happened to make — 5 drawings of `alloy1`, 3 of `inalloy1`, 6 of `erdos_renyi` — and gave:

    2.76x quoted by the record, at the 20th percentile of its own 30 drawing pairs
    a median of 3.45x over those pairs, quartiles [3.02, 3.90], range [1.40, 4.95]

Three new drawings on a designed axis (`rewire_seed` 6, 7, 8) take the cell to **8, 6 and 9 drawings** and therefore
**72 and 54 drawing pairs** — the first headline quantity in this project to get an interval drawn on purpose.

## 2. The registered claims

- **H1 — the designed addition does not move the central value.** The ER ÷ `alloy1` median over the enlarged base
  stays within **1.25×** of the accidental base's **3.45×**. **Falsifier**: it moves by more than **1.5×**, which
  would say the accidental five were a biased draw of the cell; **null**: a move between 1.25× and 1.5×.
- **H2 — the register's figure stays a low draw.** With the enlarged base its **2.76×** remains **below the 25th
  percentile**. **Falsifier**: it lands inside the central half, which would make the quoted number typical after all;
  **null**: exactly at q25.
- **H3 — the quantity stays one whose dispersion dwarfs the register's two spellings.** The enlarged base's
  **interquartile range over the median stays above 20%**, against the 9% gap between the two quoted spellings
  (`e242`'s R2). **Falsifier**: below **15%**, which would make the two-spelling presentation defensible.

**Reported**: every drawing's `alloy1`, `inalloy1` and `erdos_renyi` excess at this cell; the pairwise top-step
distribution before and after; each family's own drawing mean, median and spread; and where the register's 2.76× and
3.02× fall in the enlarged distributions.

## 3. What it cannot do

- **Three new drawings on a four-family cell**: `real` is omitted (it is not rewired, so a fifth "drawing" of it would
  be the same value, and `e221`'s cells omit it too), which means this base can say nothing new about the unrewired
  graph.
- **A mixed base**: the enlarged interval is over eight and nine drawings of which three are designed and five or six
  are accidental, so a move in the median could come from either part.
- **One cell, one size, one `rho`** — the designed axis is `rewire_seed` at a fixed configuration, which is exactly
  what the register's figure is a number *of*, and nothing more.
- **No mechanism**: this measures how well the quoted number is bracketed, not why the two-side null is ahead there.
