# The two anchors at another position: the price the card carries is the penalty's and not the basis's

*2026-10-07. `experiments/e447_the_two_anchors_at_another_position.py` reads the **matched-random** anchor under the
reversed order. `e439` put that arm on the card's world beside the biological one and found the two **0.0063** apart on
the mean diagonal and **0.0042** apart at the newest task, so the trade `e438` measured is the penalty's and not the
basis's; `e446` then moved the biological arm to the reversed order and found its newest-task price is the position's and
not the task's. **Both readings are about one anchor each and neither pair has been put beside the other at a second
position.** This unit drives `e446`'s configuration with `--methods naive,ewc-block-rand,replay` alone differing, at the
same twenty replicates and the same order, so the corpus's headline pair can be read where the position's price is
known. Five claims, registered before the new run's reading was opened.*

## 1. The pair at one position

| roll | order | tasks in the order trained | the anchor over `naive`, by position |
|---|---|---|---|
| biological (`e446`) | reverse | `loop_odour_input>loop_heading>loop_odour_identity` | +0.0719 +0.0448 **-0.0917** |
| matched-random (`e447`) | reverse | `loop_odour_input>loop_heading>loop_odour_identity` | **-0.1010** at the last |

| the pair, paired over the twenty replicates | as-built (`e439`) | reversed (this unit) |
|---|---|---|
| the two anchors' newest-task costs | -0.1177 and -0.1135, **0.0042** apart | -0.0917 and **-0.1010**, **0.0094** apart |
| the basis contrast on the mean diagonal | **+0.0063** at **0.36** sigma | **+0.0108** at **0.54** sigma |
| the basis contrast on forgetting | -0.0245 at **1.24** sigma | -0.0208 at **0.80** sigma |
| each anchor's standing over `naive` | -0.0302 (1.77σ) and -0.0365 (**2.16**σ) | **+0.0083** (0.63σ) and **-0.0024** (0.14σ) |

| claim | measured | verdict |
|---|---|---|
| BY1 the run is one configuration under the reversed order | **55** fields agree with `e438`'s, the suite reversed, the shared arms **2 of 2** bit-identical to `e446`'s | **MET** |
| BY2 and the matched-random arm pays the newest task here too | **-0.1010** at **2.93** sigma | **MET** |
| BY3 and it pays about what the biological arm pays | **0.0094** apart | **MET** |
| BY4 and the basis contrast on the mean diagonal is a null here | **+0.0108** at **0.54** sigma | **MET** |
| BY5 and neither anchor's standing resolves | **0.63** and **0.14** sigma | **MET** |

## 2. What the pair says at a second position

**The price the card carries is the penalty's and not the basis's, at the position where the price is known.** On the
reversed order, where the last position holds `loop_odour_identity`, the biological anchor gives up **-0.0917** at
**3.38** sigma and the matched-random one **-0.1010** at **2.93** -- **0.0094** apart against a **0.05** bar, and of the
same size as the **0.0042** the two were apart at the as-built position. So `e446`'s finding and `e439`'s compose: the
newest-task price is the position's and not the task's, and it is anchoring's and not the basis's, and the card's ledger
clause may be carried without naming either an arm or a basis.

**And neither anchor's whole-diagonal standing resolves here, which is the strongest form that absence has taken.**
The matched-random arm reads **-0.0024** at **0.14** sigma over the baseline and the biological one **+0.0083** at
**0.63**; as-built the two read **-0.0302** at **1.77** and **-0.0365** at **2.16**, the only one of the pairs across
both positions that reaches two sigma, and `e439` read that as the matched-random arm being the resolved one. On the
reversed order it is **0.14** sigma -- the smallest number this line has recorded for either anchor -- so with four
rolls of the biological arm and two of the matched-random one, **no roll of either arm resolves the anchor's
whole-diagonal effect in either direction.**

**And the basis contrast is a null on the second position as it was on the first, on both currencies.** On the mean
diagonal it is **+0.0108** at **0.54** sigma against the as-built **+0.0063** at **0.36**, and on forgetting
**-0.0208** at **0.80** against **-0.0245** at **1.24** -- so the headline pair is a null at neither position and
neither currency, and the two positions' nulls do not merely repeat each other's sign by accident: the forgetting
contrast is negative at both and the accuracy contrast positive at both, at under a sigma and a third.

**And the control held at a fixed order again.** The new run's `naive` and `replay` are **2 of 2** bit-identical to
`e446`'s roll, which shares this run's order, so this unit's third arm cost a run and moved nothing -- the same reading
`e446` gave, and the two together make the corpus's control rule explicit: **adding an arm is free at its
configuration's order and a roll at another order is a different run.**

## 3. What it cannot settle

- **Two positions** of the three the suite has, with three of the biological arm's four rolls at one of them, so the
  position's price is a range over rolls and not an interval, and four of the six orders are unread.
- **And one cell**: the card's world at twenty replicates, so the other five draws and the three streams are not in the
  reading, and a **0.0094** gap between two arms at one position is not the margin a redraw would leave.
- **And one partition draw**: the matched-random partition is a draw of the same group sizes and not the family of them,
  so BY4 is a null at one draw, with the corpus's eleven audits and `e357` as what make it a null in general.
- **And the two rolls are two runs**: the basis contrast pairs replicate against replicate by the runner's
  `seed0 + 100 * r` schedule, which is a same-seed pairing and not the same run, so the **0.0108** carries whatever
  separates two runs beyond their seeds.
