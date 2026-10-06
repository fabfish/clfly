# Three orders on the benchmark's world: the last position's loss is the position's, and the first position's value clears its bar by eight ten-thousandths

*2026-10-06. `experiments/e437_three_orders_on_the_world.py` reads the card's world rolled **three** ways. `e436` drove
the reversed order and found the position effect on the benchmark's own world while the reversal gained there; it left
one of the suite's six permutations in the ledger as what it could not settle. This unit drove a **third** -- the same
circuit, read-out draw, environment draw, task set, iteration budget and arm pair, with **`--task-order 1,0,2`** alone
differing -- at the same twenty replicates, so that every task of the suite sits in at least two of the three positions
and the gain of a position can be read against the gain of a task. Five claims, registered before the new run's reading
was opened.*

## 1. The three rolls

| roll | order | tasks in the order trained | gain by position | mean |
|---|---|---|---|---|
| **as-built** | as-built | `loop_odour_identity>loop_heading>loop_odour_input` | **+0.2896** +0.2490 **-0.0604** | +0.1594 |
| **reverse** | reverse | `loop_odour_input>loop_heading>loop_odour_identity` | **+0.3385** +0.2333 **-0.0208** | +0.1837 |
| **rotate** | 1,0,2 | `loop_heading>loop_odour_identity>loop_odour_input` | **+0.3688** +0.3104 **-0.0552** | **+0.2080** |

| each task's gain by the position it sat in | first | middle | last |
|---|---|---|---|
| `loop_odour_identity` | +0.2896 | +0.3104 | **-0.0208** |
| `loop_heading` | **+0.3688** | +0.2490 and +0.2333 | -- |
| `loop_odour_input` | +0.3385 | -- | **-0.0604** and **-0.0552** |

| claim | measured | verdict |
|---|---|---|
| BM1 the three rolls are carried | **28** shared fields equal, `task_order` alone differing, each order a permutation, twenty replicates | **MET** |
| BM2 and the position effect holds in all three | the first-over-last margin is **+0.3500**, **+0.3594** and **+0.4240** | **MET** |
| BM3 and the last-taught task is cost in all three | **-0.0604**, **-0.0208** and **-0.0552** | **MET** |
| BM4 and the last position's value is the position's | the three last-taught gains span **0.0396** | **MET** |
| BM5 and the first position's value is the position's too | the three first-taught gains span **0.0792** against the **0.08** bar | **MET** |

## 2. What the three rolls say

**All five claims come back MET, and the one battery `e436` fired does not fire here.** The first thing the third order
buys is a reading that the position effect is the sequence's *at both ends of the sequence on a world the card is
about*, rather than a fact about the one pair of orders that had been run. The first-taught task over the last-taught
one is **+0.3500**, **+0.3594** and **+0.4240**; the last-taught gain is **-0.0604**, **-0.0208** and **-0.0552**;
and every order's suite is the same three tasks in a different arrangement over twenty replicates with both arms.

**And the last position's loss is the position's rather than the task's, which is what the three orders together can
now say.** The last position is held by `loop_odour_input` in the as-built order (**-0.0604**) and in this unit's
(**-0.0552**) and by `loop_odour_identity` in the reversed one (**-0.0208**). Two different tasks hold the position and
the three values span **0.0396**; within the task that holds it twice, the two values are **0.0052** apart. So the loss
at the last position travels with the position and not with which task is put there -- the reading the third order was
driven to make.

**And the first position's value is the position's too, but it clears its bar by eight ten-thousandths.** The three
orders put three *different* tasks first -- `loop_odour_identity` **+0.2896**, `loop_odour_input` **+0.3385**,
`loop_heading` **+0.3688** -- so this is the test with the discriminating power, and the span is **0.0792** against the
bar of **0.08** this unit registered in advance. A reader should read that as the first position's value being
consistent to within a tenth of a point and no more: had the bar been set at **0.075** instead of **0.08** the same
measurement would have fired, and the two-place trend (a first position worth more the later its order was run) is not
something this unit's design separates from the draw.

**Beyond the claims, the ledger says the effect is a cliff at the last position rather than a slope through it.** The
gains are **+0.2896** to **+0.3688** at the first position and **+0.2333** to **+0.3104** at the middle one, so those
two ranges *overlap* and no task separates them; only the last position, at **-0.0604** to **-0.0208**, stands apart
from both. `loop_odour_identity` is the task that can say it directly, since all three orders position it: taught first
it gains **+0.2896**, taught in the middle **+0.3104** (a little *more*), and taught last **-0.0208**. The order of the
suite moves a task's gain by roughly **+0.33** when it moves the task into the last position and by nothing measurable
when it moves it between the first two. That reading is not one of the five registered claims and is offered as a
reading of the ledger, not as a measured claim.

**And on this world the three orders' means are all distinct, the third the highest.** **+0.1594**, **+0.1837** and
**+0.2080**: `e436`'s finding that the reversal does *not* cost the buffer is not a fact about reversal but about the
orders in the corpus, since the order that puts `loop_heading` first -- the middle task of the as-built suite -- is
worth more to the buffer again. The trade's direction is the sequence's, its size belongs to the world, and here the
sequence moves the size by **+0.0486**.

## 3. What it cannot settle

- **Three of six permutations**: a three-task suite has six orders and this reading carries half of them, so the
  sequence's own ordering as a mechanism is not separated from the orders chosen.
- **And one cell**: the card's world at twenty replicates, so the other five draws and the three streams are not in the
  reading, and the **0.0792** span clearing a **0.08** bar is exactly the kind of margin a different draw could move.
- **And one arm pair**: `naive` and `replay`, so the penalty arms are absent and the account of *where* the last
  position's loss spends the buffer is not in this reading.
- **And a permutation is not a mechanism**: that the order moves the numbers does not say which of the corpus's
  instruments the movement runs through.
- *And the bars are this unit's own*: **0.05** and **0.08**, registered before the run was read, and a reading that
  lands **0.0008** inside one of them bounds what it can support.
