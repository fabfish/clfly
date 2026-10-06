# The anchor's price under another order: `e438`'s *not a buffer* is the order's, and the unit's own control clause fired

*2026-10-06. `experiments/e441_the_anchors_price_under_another_order.py` reads the anchor on the card's world under a
**second order**. `e437` read the buffer's ledger there under three orders and found the position effect to be the
position's; `e438` then put the first anchor on that world under the **as-built** order alone and found it is not a
buffer; and `e438`, `e439` and `e440` all closed on the same gap, *one order*, so no anchor on that world had a second
position for any task. This unit drove it: the same configuration with `--task-order 1,0,2` alone differing from
`e438`'s, at the same twenty replicates with `naive`, `ewc-block` and `replay`. Under `1,0,2` the suite is trained
`loop_heading`, `loop_odour_identity`, `loop_odour_input`, so the last position holds the same task as the as-built roll
and the **middle position holds a different one**. Five claims, registered before the new run's reading was opened.*

## 1. The anchor's two ledgers

| roll | order | tasks in the order trained | anchor over `naive` by position | mean diagonal | forgetting |
|---|---|---|---|---|---|
| as-built | as-built | `loop_odour_identity>loop_heading>loop_odour_input` | **+0.0625** **-0.0354** **-0.1177** | **-0.0302** (1.77 sigma) | -0.0474 (2.77 sigma) |
| new | 1,0,2 | `loop_heading>loop_odour_identity>loop_odour_input` | **+0.1083** **+0.0510** **-0.0906** | **+0.0229** (1.21 sigma) | **-0.1240** (4.54 sigma) |

| the anchor's gain over `naive`, task by task against the position it sat in | first | middle | last |
|---|---|---|---|
| `loop_odour_identity` | +0.0625 | +0.0510 | -- |
| `loop_heading` | +0.1083 | **-0.0354** | -- |
| `loop_odour_input` | -- | -- | **-0.1177** and **-0.0906** |

| for comparison, the buffer over `naive` | first | middle | last |
|---|---|---|---|
| as-built (`e438`) | +0.2896 | +0.2490 | -0.0604 |
| 1,0,2 (`e437`) | +0.3688 | +0.3104 | -0.0552 |

| claim | measured | verdict |
|---|---|---|
| BS1 and the run is one configuration | **55** compared fields agree with `e438`'s, **2 of 4** shared-arm comparisons bit-identical | **FALSIFIER FIRED** |
| BS2 and the anchor pays the last position under this order too | **-0.0906** | **MET** |
| BS3 and it pays about what it paid under the as-built order | **0.0271** apart | **MET** |
| BS4 and the anchor is behind the baseline at the middle position too | **+0.0510** | **FALSIFIER FIRED** |
| BS5 and its price is not the buffer's under this order either | the buffer **-0.0552** against the anchor **-0.0906** | **MET** |

## 2. What the two orders say

**The firing on BS1 is the unit's own mis-specification, and the meaningful half of the control held.** BS1 asked for the
new roll's `naive` and `replay` to be bit-identical to `e437`'s rotated roll **and to `e438`'s as-built one**, and it
could not be: `e438`'s arms train in a *different order*, so their replicate records differ by construction, and the
claim was written as though the control were order-free. Measured, **2 of 4** comparisons are bit-identical -- the two
against `e437`'s roll, which shares this run's order -- and the two against `e438`'s are not. So the firing does not
qualify anything about the anchor; what it settles is the reach of `e438`'s and `e439`'s control: **adding an arm to an
existing configuration is free at that configuration's order, and a roll at another order is a different run.** It is
reported as FIRED because that is what the claim as registered did.

**And the anchor's standing on this world is the order's.** `e438` measured `ewc-block` at **-0.0302** below the baseline
on the mean diagonal and concluded it is not a buffer there. Under `1,0,2` the same arm reads **+0.0229** *above* the
baseline -- unresolved at **1.21** sigma, as the as-built figure was at 1.77 -- and its forgetting purchase nearly
triples, from **-0.0474** at **2.77** sigma to **-0.1240** at **4.54** sigma. Neither mean-diagonal contrast resolves,
so what the two orders together say is that **the anchor's deficit is not a property of the world**: the sign moves with
the order and the amount of stability it buys moves with it, and `e438`'s sentence should be scoped to the order it was
measured in.

**And BS4 fired at the one position where the two orders disagree about the task, which is the same fact read per
position.** The middle position holds `loop_heading` as-built and `loop_odour_identity` under `1,0,2`; the anchor is
**-0.0354** behind the baseline there in the first and **+0.0510** ahead in the second, a sign flip of **0.0864** at a
position whose task changed. The task-by-position table shows the two halves of that: `loop_odour_identity` reads
**+0.0625** at the first position and **+0.0510** at the middle -- nearly the same -- while `loop_heading` reads
**-0.0354** at the middle and **+0.1083** at the first, a difference of **0.1437**. So the anchor's ledger is not
positional the way the buffer's is and not the task's either: one of the three tasks moves with its position by
**0.14** and another by **0.01**.

**And the two positions the orders share agree, which is what BS2 and BS3 buy.** The last position holds
`loop_odour_input` in both orders, and the anchor's cost there is **-0.1177** and **-0.0906**, **0.0271** apart -- so the
one cell that can be read twice is read the same way twice, and the anchor pays the newest task under both orders while
the buffer is again the less-penalised of the two (**-0.0552** against **-0.0906**).

**And across the two positions each roll holds, the anchor's three positions separate where the buffer's did not.**
`e437` found the buffer's first and middle positions to *overlap* -- **+0.2896** to **+0.3688** at the first and
**+0.2490** to **+0.3104** at the middle -- and only the last position to stand apart. The anchor's ranges are
**+0.0625** to **+0.1083**, **-0.0354** to **+0.0510** and **-0.1177** to **-0.0906**, which do not overlap anywhere:
for the anchor the ledger is ordered by position, and for the buffer it is a cliff at the last position with the first
two indistinguishable. That is a reading of two orders and not a claim, and it is the first place the two arms' shapes
differ in kind rather than in size.

## 3. What it cannot settle

- **Two orders** of a three-task suite's six, so the other four are not in the reading and the middle position is read
  under two tasks rather than three.
- **And one anchor**: `ewc-block-rand` is absent, so whether the matched-random arm's standing also moves with the order
  is not measured here, though `e439` found the two anchors **0.0042** apart at the last position as-built.
- **And one cell**: the card's world at twenty replicates, so the other five draws and the three streams are not in the
  reading, and a sign flip between two unresolved contrasts (**-0.0302** at 1.77 sigma and **+0.0229** at 1.21) is
  exactly what a redraw could produce from no effect at all.
- **And an order is not a mechanism**: that the order moves the anchor's standing does not say which of the corpus's
  instruments moves it, though `e440`'s two parameters were read at the as-built order only and could be read here.
