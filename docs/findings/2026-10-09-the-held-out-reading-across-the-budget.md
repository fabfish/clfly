# The held-out reading across the budget: the remainder arrives in three steps, none of which resolves

*2026-10-09. `experiments/e472_the_held_out_reading_across_the_budget.py` walks the axis `e471` left between its two
points: four more rolls of the same configuration with the same world at **200** and **350** updates, both anchors,
twenty replicates each, read beside `e471`'s two at 100 and `e469`'s two at 500. Four claims: **YA1, YA2 and YA4 MET**
and **YA3's falsifier FIRED**.*

## 1. The curve

| the budget | the baseline's trained reading | the step from the one before | that step's sigma | its change from the initial body | sigma |
|---|---|---|---|---|---|
| 100 | **0.7594** | -- | -- | **+0.0719** | **4.89** |
| 200 | **0.7625** | **+0.0031** | **0.14** | **+0.0750** | **5.91** |
| 350 | **0.7708** | **+0.0083** | **0.59** | **+0.0833** | **10.42** |
| 500 | **0.7719** | **+0.0010** | **0.08** | **+0.0844** | **10.11** |

| the eight rolls | 100 | 200 | 350 | 500 |
|---|---|---|---|---|
| `ewc-block` | 0.7198 | 0.7479 | **0.7708** | 0.7625 |
| `replay` | 0.7438 | 0.7542 | 0.7688 | 0.7677 |
| against the baseline | **-0.0396** | -0.0146 | **0.0000** | -0.0094 |
| that difference's sigma | **-1.76** | -0.96 | **0.00** | -0.86 |

| claim | measured | verdict |
|---|---|---|
| YA1 the new budgets are one configuration with the update count moved | **102** fields compared, **8** rolls at **20** replicates, one held-out cue set on all of them | **MET** |
| YA2 and the trained reading does not fall as the budget grows | no budget below its predecessor, on either roll | **MET** |
| YA3 and the first doubling carries at least half of the whole change | **0.0031** of **0.0125**, a share of **0.248** | **FALSIFIER FIRED** |
| YA4 and the anchoring does not move it at any budget | **-1.76** to **0.00** sigma, none resolving | **MET** |

## 2. What the four points say

**The remainder arrives in three steps and not one of them resolves.** From a hundred updates to five hundred the
baseline's reading goes **0.7594** to **0.7719**, **+0.0125**, and the three increments are **+0.0031** at **0.14** sigma,
**+0.0083** at **0.59** sigma and **+0.0010** at **0.08** sigma: the largest sits **between two hundred and three
hundred and fifty updates** and even that one is under the bar. **So `e471`'s sentence survives and its reason does not.**
*What the rest of the budget adds is not separable from a redraw* is true of the whole remainder -- and it is true of
every step of it -- while *the reading is bought early* is a statement about the **share** of the total (**85%** arrives
by a hundred updates) and not about where the rest is bought, which turns out to be the middle.

**And the reading's own change from the initial body is resolved at every budget, increasingly so.** The paired
trained-minus-initial contrast runs **4.89**, **5.91**, **10.42** and **10.11** sigma: the curve's *level* is carried by
four strongly resolved readings while its *shape* above a hundred updates is not carried at all. So the honest form of
`e471`'s finding is two sentences with different standing -- the sequence raises the unseen cue set's decodability, at
ten sigma; and what the rest of the budget adds is under a sigma per step.

**And the biological anchor meets the baseline exactly once, at three hundred and fifty updates.** Its trained reading
there is **0.7708** against the baseline's **0.7708**, a paired difference of **0.0000** at **0.00** sigma -- the only
exact tie in the table -- where at a hundred updates it is **0.0396** behind at **1.76** sigma and at five hundred
**0.0094** behind at **0.86**. **So the partition's cost on the unseen cue set is a curve with a zero in the middle and
it is under the bar at every point**, which is the `basis` clause's null read at four places instead of two.

**And the eight rolls are one configuration.** All **102** compared fields agree except the update count, the output
path and the saved weights, the held-out cue set is `loop_holdout` on every arm of all eight, and its counts are **96**
train and **48** eval on every one of them -- so the four points differ in the budget and in nothing else, and the same
cue set is being read four times.

**And the two rolls of each budget are the same to four decimals on the baseline.** The `bio` and `rand` rolls' `naive`
readings are **0.7594**, **0.7625**, **0.7708** and **0.7719** on both, which is the check that the flag draws one world
for both anchors and that the probe is deterministic given a body.

## 3. What it cannot do

- **Four budgets are a curve and not a mechanism**: the axis is the number of updates and the corpus carries no run that
  separates it from the training it buys.
- **And a probe is not a task**: every point is of **linear readability** from the frozen body.
- **And one held-out draw**: the flag's own draw of the fourth cue set, so all four points are one cue set's and a
  redraw of it is not measured.
- **And one ridge**: **1e-2** is `e469`'s, and a different one would move every point.
- **And four points are not a step function**: the largest increment is between two hundred and three hundred and fifty
  updates and it is under the bar, so *the remainder arrives there* is a statement about four points and not about a
  place between them.

## RE-READ 2026-10-09: the bullet is closed, and the curve is one draw's levels

The third bullet of *what it cannot do* says *one held-out draw*, so all four budgets this unit walked are one cue
set's. `e473` drew that cue set again: the initial body reads **0.5625** against **0.6875** and the trained body
**0.6312** against **0.7594**, **0.1281** apart, while the two draws' changes agree to **-0.0031** at **0.19** sigma.
**So this unit's four-point curve is a curve of one draw's *levels*** -- and its shape, the three steps of **+0.0031**,
**+0.0083** and **+0.0010** at **0.14**, **0.59** and **0.08** sigma, is the change's and not the level's. Nothing in
this unit's numbers moves: the eight rolls it read are its own
(`docs/findings/2026-10-09-the-held-out-task-at-a-second-draw.md`).
