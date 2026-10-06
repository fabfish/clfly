# The anchor's price at another position: the one resolved effect the card carries is the position's, and the standing is still absent on a fifth roll

*2026-10-06. `experiments/e446_the_anchors_price_at_another_position.py` reads the anchor under the **reversed** order.
Revision 8 of the card carries the anchor's newest-task price as the one thing about that arm that resolves on every
roll this line has driven -- **-0.1177**, **-0.0906**, **-0.0552** and **-0.0615** at **3.71**, **3.56**, **2.57** and
**2.62** sigma -- while its whole-diagonal standing resolves on none of the four. **In every one of those rolls the last
position held `loop_odour_input`**, and `e445` named exactly that as what its own clause could not settle. This unit
drives `e438`'s configuration with `--task-order reverse` alone differing, at the same three arms and twenty replicates,
so the suite is trained `loop_odour_input`, `loop_heading`, `loop_odour_identity` and the anchor's price is asked at a
position holding `loop_odour_identity`. `e436` drove that order with `naive` and `replay` alone, which is the control.
Five claims, registered before the new run's reading was opened.*

## 1. The two rolls

| roll | order | tasks in the order trained | the anchor over `naive` by position | its mean diagonal |
|---|---|---|---|---|
| as-built | as-built | `loop_odour_identity>loop_heading>loop_odour_input` | **+0.0625** **-0.0354** **-0.1177** | -0.0302 (1.77σ) |
| new | reverse | `loop_odour_input>loop_heading>loop_odour_identity` | **+0.0719** +0.0448 **-0.0917** | **+0.0083** (0.63σ) |

| per position, paired over the twenty replicates | first | middle | last |
|---|---|---|---|
| the anchor over `naive`, new roll | **+0.0719** (4.18σ) | +0.0448 (1.44σ) | **-0.0917** (-3.38σ) |
| the buffer over `naive`, new roll | +0.3385 (12.00σ on the mean) | +0.2333 | -0.0208 |

| claim | measured | verdict |
|---|---|---|
| BX1 the run is one configuration with the order reversed | **55** fields agree with `e438`'s, the suite the as-built one reversed, the shared arms **2 of 2** bit-identical to `e436`'s | **MET** |
| BX2 and the anchor pays the newest task here too | **-0.0917** | **MET** |
| BX3 and that price resolves | **-0.0917** at **3.38** sigma | **MET** |
| BX4 and the price is the position's and not the task's | **0.0260** from the as-built one's | **MET** |
| BX5 and the anchor's whole-diagonal standing is still not there | **+0.0083** at **0.63** sigma | **MET** |

## 2. What the fifth roll says

**The one effect the card carries about the anchor is the position's and not the task's.** The last position held
`loop_odour_input` in all four rolls revision 8 was written from and holds `loop_odour_identity` here, and the cost is
**-0.0917** at **3.38** sigma against the as-built **-0.1177** at **3.71** -- **0.0260** apart, against a bar of
**0.05**. So the clause's number is a statement about the last position and a reader may carry it without naming a task,
which is what `e445` closed on being unable to say.

| roll | the task the last position held | the anchor's newest-task cost | sigma | its mean diagonal | sigma |
|---|---|---|---|---|---|
| as-built (`e438`) | `loop_odour_input` | -0.1177 | 3.71 | -0.0302 | 1.77 |
| rotated (`e441`) | `loop_odour_input` | -0.0906 | 3.56 | +0.0229 | 1.21 |
| environment redrawn (`e443`) | `loop_odour_input` | -0.0552 | 2.57 | +0.0198 | 1.30 |
| decoder redrawn (`e444`) | `loop_odour_input` | -0.0615 | 2.62 | -0.0111 | 0.59 |
| **reversed (`e446`)** | **`loop_odour_identity`** | **-0.0917** | **3.38** | **+0.0083** | **0.63** |

**And the standing is still absent, on a fifth roll.** The anchor's mean diagonal over the baseline is **+0.0083** at
**0.63** sigma, the smallest of the five, so across five rolls it reads **-0.0302**, **+0.0229**, **+0.0198**,
**-0.0111** and **+0.0083** at **1.77**, **1.21**, **1.30**, **0.59** and **0.63** sigma -- a span of **0.0531** and not
one of the five reaching two sigma -- while its newest-task price resolves on all five at **2.57** to **3.71**. The
card's clause as written is therefore not a statement about four rolls: a fifth, whose last position holds another task
and whose middle position too, leaves both of its numbers where they were.

**And the control came back exact at a fixed order, which is `e441`'s lesson applied.** `e441` registered a
bit-identical control across *two* orders and its falsifier fired, because a roll at another order is a different run.
Here the control is `e436`'s roll at **this** order, and all **2 of 2** shared arms are bit-identical to it, replicate
for replicate. So the two units together bound the finding: **adding an arm to a configuration is free at that
configuration's order and is not a comparison across orders**, and this unit's third arm is free.

**And the anchor's forgetting purchase is the largest of the five rolls while its accuracy standing is the smallest.**
It buys **-0.0813** of forgetting against the baseline at **4.92** sigma -- the four earlier rolls read **-0.0474**,
**-0.1240**, **-0.0620** and **-0.0443** -- while its whole-diagonal accuracy contrast stays inside its own standard
error. So the arm pays the newest task and buys forgetting back with it, and nothing in five rolls makes the *net* of
that trade resolve on the diagonal.

## 3. What it cannot settle

- **One more order** of the suite's six, so `loop_odour_identity` is the only other task the price is asked of, and four
  of the six orders are still unread.
- **And one cell**: the card's world at twenty replicates, so the other five draws and the three streams are not in the
  reading, and a **0.0260** move at a changed task is not a distribution.
- **And one anchor**: `ewc-block-rand` is absent, though `e439` found the two anchors **0.0042** apart at the last
  position as-built and `e440` found the two holding the weights **0.0046** apart.
- **And a price is not a purchase**: this measures what the anchor gives up at the newest task and not what it buys with
  it, and the forgetting contrasts above are the corpus's account of the purchase rather than a mechanism for it.
