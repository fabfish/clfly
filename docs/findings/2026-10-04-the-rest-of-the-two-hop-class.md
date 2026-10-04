# The rest of the two-hop class: one of four cue draws at distance 2 recovers, so the geometry carries no more than a coincidence

*2026-10-04. `experiments/e399_the_rest_of_the_two_hop_class.py` runs the two remaining distance-2 cue draws of
`e398`'s sixteen-draw search -- seeds **9** and **14** -- to the card's far point, five hundred updates at twenty
replicates, with the card's world and cue seed 3 read from `e380`'s and `e398`'s artifacts through the same probe. The
whole distance-2 class is therefore measured, and the one distance-1 world `e398` ran comes with it. Five claims,
registered before any of the new runs' readings was opened.*

## 1. The class, at the far point

| world | cue seed | cue to action | connectome's own reading | body after 500 updates | gain | trained head |
|---|---|---|---|---|---|---|
| the card's | -- | **2** | 0.6875 | **0.7729** | **+0.0854** | 0.7500 |
| **9** | 9 | **2** | 0.6875 | **0.4625** | **−0.2250** | 0.8125 |
| **3** | 3 | **2** | 0.6875 | 0.5240 | **−0.1635** | 0.8333 |
| **14** | 14 | **2** | 0.6875 | **0.5396** | **−0.1479** | 0.8333 |
| **1** | 1 | 1 | 0.6875 | 0.5062 | −0.1813 | 0.7500 |

chance 0.2500. The head column is the first replicate's own accuracy, not a mean. The three new rows are this unit's
and `e398`'s; the card's is `e380`'s run.

| claim | measured | verdict |
|---|---|---|
| V1 only the cue population moved | **0** of four moved a driven field; all four differ in the cue's | **MET** |
| V2 the two new draws are the other two at distance 2 | the distance-2 seeds over 16 draws are **3, 9, 14** | **MET** |
| V3 neither of them recovers | **−0.2250** and **−0.1479** | **MET** |
| V4 the initial reading does not move | **0.6875** five times, spread **0.0000** | **MET** |
| V5 the two-hop class is not the recovering class | **1 of 4** | **MET** |

## 2. What the whole class says

**The distance-2 geometry carries no more than a coincidence.** All four cue draws whose neurons stand two hops from
the action population are now measured at the far end: the card's recovers by **+0.0854** and the other three **lose**
by **0.1479, 0.1635** and **0.2250** -- the same range as the single distance-1 draw's **0.1813**. `e397` found a
perfect separation between the one draw at distance 2 and the four at distance 1, and `e398` showed a second
distance-2 draw failing; this unit closes the class and shows the separation was **one member's**. The two-hop class
contains one world that keeps the cue and three that lose it by as much as the one-hop world does.

**And the three failures cluster tightly, the recovery stands alone.** −0.1479, −0.1635, −0.1813 and −0.2250 span
**0.0771** across two classes and two geometries, while the card's world sits **0.23** above the nearest of them. So
what separates the card's world from the rest is not a difference of degree within a class: it is a single world
against eight others measured at this end -- four engine redraws (`e395`, `e396`), three other cue populations at the
same distance, and one at the other distance.

**And the initial reading is 0.6875 five times more.** The card's world, the three other two-hop cue populations and
the one-hop one all read **0.6875** from the connectome's own weights, a spread of **0.0000** -- every trained world
this line has put through the probe now, across two budgets, five engine draws, four streams and four cue
populations, and the reading has never moved.

## 3. What it cannot settle, and what it registers

- **One member of the four keeps the cue and three do not**, so the question `e398` left is now sharp and still
  open: what makes the card's cue population the one? It is not its size (twelve on all), not its distance (two on
  three others), and not anything the trained head shows (0.7500 against 0.8125, 0.8333 and 0.8333, so the failing
  worlds' heads are *better*).
- **The distance-1 class has one trained member.** Seed 1 is the only one-hop draw run at the far point, from
  `e398`, so the contrast is four two-hop draws against one.
- **Sixteen draws are sixteen draws**: a distance-2 cue population outside the search is not measured, and the
  thirteen one-hop ones are measured for their distance and not trained.
- *And a probe is not a mechanism*: the readings say how much of the label a linear fit recovers from the world's
  eight numbers, so "the body keeps the cue" is a statement about recoverability.
