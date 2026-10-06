# The matched-random partition on the card's world: the trade `e438` measured is the penalty's and not the basis's -- the basis contrast is a null at 0.36 sigma

*2026-10-06. `experiments/e439_the_matched_random_partition_on_the_card.py` reads the **matched-random arm** on the card's
world. `e438` put the first penalty arm there and found it is not a buffer; it named its own gap, that `ewc-block-rand`
-- the size-matched random partition the corpus's headline actually compares against -- was absent, so it said the
*penalty* is not a buffer and not whether the *basis* is what makes it one. This unit drove that arm: the same
configuration with `--methods naive,ewc-block-rand,replay` alone differing from `e438`'s, at the same twenty replicates
on the same as-built order. Five claims, registered before the new run's reading was opened.*

## 1. The four arms on one configuration

| arm | first | middle | last | mean | mean forgetting |
|---|---|---|---|---|---|
| `naive` | +0.3240 | +0.4292 | +0.8042 | **+0.5191** | 0.3750 |
| `ewc-block` | +0.3865 | +0.3937 | +0.6865 | +0.4889 | 0.3276 |
| `ewc-block-rand` | +0.3615 | +0.3958 | +0.6906 | +0.4826 | 0.3521 |
| `replay` | **+0.6135** | **+0.6781** | +0.7438 | **+0.6785** | **0.0906** |

| gain over `naive`, by position | first | middle | last |
|---|---|---|---|
| `replay` | **+0.2896** | **+0.2490** | **-0.0604** |
| `ewc-block` | +0.0625 | -0.0354 | **-0.1177** |
| `ewc-block-rand` | +0.0375 | -0.0333 | **-0.1135** |

| paired contrast over the twenty replicates | mean diagonal | mean forgetting |
|---|---|---|
| `ewc-block` minus `ewc-block-rand` | **+0.0063** at **0.36** sigma | **-0.0245** at **1.24** sigma |
| `ewc-block-rand` minus `naive` | **-0.0365** at **2.16** sigma | -0.0229 at **1.32** sigma |
| `ewc-block-rand` minus `replay` | **-0.1958** at **15.33** sigma | **+0.2615** at **11.27** sigma |

| claim | measured | verdict |
|---|---|---|
| BQ1 and the run is one configuration | **168** compared fields agreeing across three rolls, **6 of 6** shared-arm comparisons **bit-identical**, twenty replicates | **MET** |
| BQ2 and the basis contrast is a null on this world | the paired contrast on the mean diagonal is **+0.0063**, unresolved at **0.36** sigma | **MET** |
| BQ3 and the matched-random arm pays the last position too | `ewc-block-rand` over `naive` on the last-taught task is **-0.1135** | **MET** |
| BQ4 and the two penalty arms pay it alike | the two costs are **-0.1135** and **-0.1177**, **0.0042** apart | **MET** |
| BQ5 and the matched-random arm's stability is the penalty's too | the paired forgetting contrast is **-0.0245**, unresolved at **1.24** sigma | **MET** |

## 2. What the four arms say

**The basis does not matter on this world; the penalty does.** The corpus's headline contrast -- the biological
cell-class basis against a size-matched random partition of it -- reads **+0.0063** on the mean diagonal, unresolved at
**0.36** sigma, and **-0.0245** on forgetting, unresolved at **1.24** sigma. That is the null eleven audits left on the
state read-out and `e357` left on the earned label, now read on the card's own world at the tightest resolution this
line has given it. **What the two arms share, they share almost exactly**: over `naive` the biological arm reads
**+0.0625**, **-0.0354**, **-0.1177** by position and the matched-random one **+0.0375**, **-0.0333**, **-0.1135** -- at
the last position **0.0042** apart -- and both sit *below* the naive baseline on the mean diagonal while both buy back
forgetting. So `e438`'s trade is not a property of the coordinate basis: **any anchoring of this shape on this world
pays the newest task and buys back the oldest, and neither anchoring's accuracy is better than not anchoring at all.**

**And the matched-random arm is the one that resolves below the baseline.** `ewc-block`'s deficit against `naive` is
**-0.0302**, unresolved at **1.77** sigma; the matched-random arm's is **-0.0365** at **2.16** sigma, so of the two
penalty arms it is the *random* partition whose failing to be a buffer is the resolved one. By position its newest-task
cost is **-0.1135** at **4.49** sigma, its middle-position **-0.0333** at **1.49** and its first-position gain
**+0.0375** at **1.32** -- the only resolved thing about either anchoring arm on this world is the price it pays for
the last task.

**And `replay` is a different object and the gap is enormous.** The matched-random arm is **-0.1958** behind `replay`
on the mean diagonal at **15.33** sigma and forgets **+0.2615** more at **11.27** sigma, so where `e276`'s headline
contrast survives this substrate (`e438`: `replay` over `ewc-block` at **10.89** sigma) the *size* of it is the arm's
and not the basis's: a buffer reads at **+0.6785** and both anchors read below the baseline they are meant to beat.

**And the run's control held across three rolls at once.** `naive`'s and `replay`'s twenty replicate records are
**bit-identical** between this run and `e438`'s, between this run and `e380`'s, and between `e438`'s and `e380`'s --
**6 of 6** comparisons -- and **168** other recorded fields agree across the three. Three separate runs with three
different arm lists produced the arms they share exactly, so a unit that wants a fourth arm on this configuration pays
for the arm and for nothing else.

## 3. What it cannot settle

- **One order**: the as-built one, so no penalty arm here has a second position for any task and the cliff is read at
  three positions in one order rather than across orders as `e437` read the buffer's.
- **And one partition draw**: `e379`-style matched-random partitions are a draw of the same group sizes and not the
  family of them, so BQ2 is a null at one draw; the corpus's eleven audits are what make it a null in general.
- **And one cell**: the card's world at twenty replicates, so the other five draws and the three streams are not in the
  reading, and BQ4's **0.0042** between two arms is not the margin a redraw would leave.
- **And an arm is not a mechanism**: that both anchors pay the newest task alike does not say they pay it by the same
  route, and `e432`'s split of interference into its weight and bias halves has still not been asked of this world.
