# Registered: the no-destruction rung at a second cell, and whether `e244`'s reversal is the pattern

*2026-09-26 14:43, registered before its runs. Runs: `e2_topology_gap` at `--circuit-size 300 --support 30 --seeds 3
--seed0 0 -q 0.02 --topologies swap0.5,swap2,signshuffle --no-realized --rewire-seed {3,4}` — **two runs, one cell
each**, to be written as `e245_cs300_kind0_rs3.json` and `_rs4.json`. Two runs, not one, because a spread needs two
drawings and one run is one drawing.*

## 1. What `e244` left standing, and why it needs a second cell

`e244` asked whether the **spread** of the penalty across drawings is ordered by the same axis as its **level** — how
many of a graph's two degree sequences a construction destroys. Pooled over the corpus it is: kind 0
(`swap*`/`signshuffle`) 1.449×, kind 1 (`alloy*`/`inalloy*`) 1.234×, kind 2 (`erdos_renyi`) 1.029×, the last two
ranges disjoint — **K1 and K2 MET**. But the within-cell test **K3 fired its falsifier at 6 of 7 cell-pairs**, and the
one pair it could not support is the only pair that compares kind 1 with kind 0:

    cs 800/support 80/rho 0.9     kind 0: 1.45x (3 families)   kind 1: 2.29x (4 families)   kind 2: 1.05x

The no-destruction constructions — the ones destroying nothing at all — are the **tightest** there, and the
one-side families the loosest. That is what K1's top rung rests on: **kind 0 exists at exactly ONE cell in the whole
census**. The other five cells vote for kind 1 while carrying no kind 0 at all, and the same reversal breaks K1 too
once those five are removed (pinned by a test in `tests/test_e244_drawing_spread_by_kind.py`).

So the reversal is currently a **one-cell statement**, and it is the only thing standing between `e244`'s K1 and the
verdict "the pooled ordering is cell composition". One more cell carrying both kinds decides which.

## 2. Why cs 300/support 30

- **A different size, by 2.7×.** The convention cell is cs 800; this project's standing standard after C1 is that a
  claim is not a property of the substrate until it holds at more than one circuit size, and the ladder itself needed
  `e217` for exactly this reason.
- **It is the size where the kind-1 and kind-2 levels are highest** (0.122 and 0.157 against cs 800's 0.047 and
  0.144), so if the reversal is an artifact of the penalty being near the floor, its chance to fail is here.
- **The cell is already populated on the other two rungs**: kind 1 has three drawings (`e217_ladder_cs300.json`,
  `e219_draws_cs300_rs1.json`, `_rs2.json`) and kind 2 the same, all at seeds 3/seed0 0/q 0.02, so only the kind-0
  half has to be bought. `rewire_seed` 3 and 4 are unused at this cell by anything on disk.
- **Cost.** cs 300's cell times are in this record twice: 372 s for four cells (≈93 s per cell) and 120 s for four
  topologies at one `rho` (≈2 min per `rho`). Three topologies at one cell, twice, is therefore **≈5–10 min**. Where
  the run is faster than that, the difference is CPU sharing with the gate suite rather than a different kind of run.

## 3. The registered claims

- **M1 — the discriminating one: does the reversal replicate?** At cs 300/support 30, kind 0's median excess spread
  over its three families is **below** kind 1's median — i.e. the **pooled** ordering (K1) holds inside the cell and
  the convention cell's reversal was a one-cell accident. **Falsifier**: kind 0 at or above kind 1, a second
  reversal, which would make the reversal the pattern and K1's top rung the exception. **Null**: the two medians
  within 10% of each other, which would leave the ordering undecided at this cell.
- **M2 — the two-side rung again.** At this cell kind 2's median spread is **below** kind 1's, as it is in all six
  cells measured so far. **Falsifier**: kind 2 at or above kind 1.
- **M3 — reported, not claimed.** The three kind-0 families' excesses, effective ranks and spreads beside kind 1's
  and kind 2's at this cell, so that the **level confound** `e244` named ("the two-side kind is both the tightest and
  the highest, so tightness cannot be separated from height") is stated with numbers rather than hidden.
- **M4 — reported, and it is the first of its kind.** These are the **first kind-0 drawings at any size other than
  cs 800**: the ladder's floor has only ever been drawn at one circuit size, where `swap0.5`, `swap2` and
  `signshuffle` read 0.0217, 0.0153 and 0.0285. Whether the floor's *level* replicates at cs 300 is a bonus the
  design buys.

## 4. What it cannot do

Two drawings per family at one cell is a range and not a distribution, and the three kind-0 families share those two
drawings, so their spreads are not independent; the level confound survives the design, since kind 0's excess will
sit near the floor (~0.03) whatever the cell and kind 1's at 0.12–0.14; cs 300/support 30 is one point in the size and
support grid; `rho` is the builder's default and every one of these artifacts records `config.rho: None`; and the
comparison is of **spreads**, so it says nothing directly about the levels `e217` measured.

## 5. What the reader will be

`e244` re-run on the enlarged census (`uv run python -m experiments.e244_drawing_spread_by_kind --json-out
runs/e244_drawing_spread_by_kind.json`) — the module already keys drawings by (size, support, `rho`, `rewire_seed`)
and takes the median over families within a cell, so the new cell enters K3 as a second (1, 0) pair with no code
change. `e242`'s reader is not involved.
