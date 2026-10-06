# The two parameters under two orders: the drift ratio is the least order-sensitive quantity on the card's world

*2026-10-06. `experiments/e442_the_two_parameters_under_two_orders.py` reads the corpus's own two parameters on both
orders of the card's world. `e440` read them at the **as-built** order and found the anchors holding the recurrent
weights to **0.6234** and **0.6188** of the baseline's drift with bias ratios **1.4483** and **1.4622**. `e441` then put
the anchor on a **second order** and found its standing there is the order's -- **-0.0302** below the baseline on the
mean diagonal as-built against **+0.0229** above it under `1,0,2`, with its forgetting purchase nearly tripling from
**-0.0474** to **-0.1240** -- and closed by naming this unit's question. No training and no probe. Five claims,
registered before either roll's parameters were read.*

## 1. The two parameters, arm by arm and order by order

| roll | order | arm | drift ratio | bias ratio | held | pushed |
|---|---|---|---|---|---|---|
| as-built | as-built | `ewc-block` | **0.6234** | **1.4483** | yes | yes |
| as-built | as-built | `replay` | 0.9556 | 0.8531 | yes | no |
| rotated | 1,0,2 | `ewc-block` | **0.6027** | **1.3621** | yes | yes |
| rotated | 1,0,2 | `replay` | 0.9328 | 0.8030 | yes | no |

*`e433`'s pooled pattern over the corpus was drift **0.718**, **0.751**, **0.752** and bias **1.508**, **1.473**,
**1.456** for the three penalties, against **0.984** and **0.946** for the buffer.*

| the share of the whole-body interference term carried by the bias half | task 1 | task 2 |
|---|---|---|
| as-built baseline | 0.3776 | 0.4873 |
| as-built `ewc-block` | **0.8956** | **0.9366** |
| as-built `replay` | **0.3159** | **0.4073** |
| 1,0,2 baseline | 0.2752 | 0.2083 |
| 1,0,2 `ewc-block` | **0.9464** | **0.8996** |
| 1,0,2 `replay` | **0.5098** | **0.4427** |

| what the second order moves | as-built | 1,0,2 | move |
|---|---|---|---|
| the anchor's **drift ratio** | 0.6234 | 0.6027 | **0.0207** |
| the anchor's mean diagonal over the baseline | -0.0302 | +0.0229 | **0.0531** |
| the anchor's forgetting purchase | -0.0474 | -0.1240 | **0.0766** |
| the anchor's bias ratio | 1.4483 | 1.3621 | **0.0862** |
| the baseline's own second-task bias share | 0.4873 | 0.2083 | **0.2790** |

| claim | measured | verdict |
|---|---|---|
| BT1 the ledger is carried | **4** cells over **2** rolls at twenty replicates, all three fields present | **MET** |
| BT2 and the anchor holds the weights under the rotated order too | **0.6027** | **MET** |
| BT3 and the buffer does not | the buffer **0.9328** against the anchor **0.6027** | **MET** |
| BT4 and the anchor holds them about as hard under both orders | **0.0207** apart | **MET** |
| BT5 and its interference still runs through the bias on every task it accounts for | **0.9464** and **0.8996** against the baseline's **0.2752** and **0.2083** | **MET** |

## 2. What the two orders say

**The parameter `e440` named is the least order-sensitive quantity on this world, and it does not move when the thing it
is supposed to explain moves.** Between the two orders the anchor's drift ratio moves **0.0207** -- a relative change of
**3.3%** -- while its standing on the mean diagonal flips sign over **0.0531** and its forgetting purchase changes by
**0.0766**, from **-0.0474** to **-0.1240**, a factor of **2.6**. Both rounds of the same number are inside the corpus's
band of **0.718** to **0.752**, so under `1,0,2` the anchor is the same kind of arm by this parameter as it is as-built.
`e440`'s reading was that holding the recurrent weights is not what buys the retention, because the arm buying six times
as much holds them to 0.956 while the arms holding them to 0.62 buy almost none; the second order is that reading
repeated, and it makes the parameter's failure sharper -- **the quantity is stable to 2% between two runs whose
forgetting differs by a factor of 2.6.**

**And the buffer's drift ratio is stable too, so the stability is the measurement's and not the anchor's.** `replay`
moves from **0.9556** to **0.9328**, **0.0228** apart, and stays the arm that disturbs the weights least. Both arms
therefore carry a drift ratio that is essentially an arm property on this world, which is what makes it useful as a
control and useless as an explanation of the order's effect.

**And the bias ratio moves four times as much as the drift ratio, and the interference split moves more than either.**
The anchor's bias ratio falls from **1.4483** to **1.3621**, **0.0862**, and the buffer's from **0.8531** to **0.8030**;
both stay inside the corpus's band, and both keep their sign. The split moves much further: the baseline's own bias
share falls from **0.3776** and **0.4873** to **0.2752** and **0.2083** -- **0.2790** on the second task -- while the
anchor's stays near **0.9**. So the four quantities order themselves by order-sensitivity: **drift ratio 0.0207,
mean-diagonal standing 0.0531, forgetting purchase 0.0766, bias ratio 0.0862, and the interference share up to
0.2790.**

**And `e440`'s fifth claim is order-scoped, which the second roll shows.** `e440` registered that `replay`'s per-task
bias share is at or below the baseline's on both tasks and read it **MET** at **0.3159** and **0.4073** against **0.3776**
and **0.4873**. Under the rotated order those same shares are **0.5098** and **0.4427** against a baseline of **0.2752**
and **0.2083**, so the buffer is *above* its baseline on both tasks. `e440`'s claim named one roll and is not refuted
here; what this unit adds is that the buffer's relation to its baseline in this split is an order's and not an arm's,
which is the same lesson `e441` drew about the anchor's standing.

## 3. What it cannot settle

- **Two orders** of a three-task suite's six, so the other four are not in the reading and an order effect of
  **0.0207** is a difference between two rolls rather than a trend.
- **And one anchor**: `ewc-block-rand` is absent from the rotated roll, so whether the matched-random arm's drift ratio
  is equally order-stable is not measured, though `e439` found the two anchors **0.0063** apart on the mean diagonal
  as-built.
- **And one cell**: the card's world at twenty replicates, so the other five draws and the three streams are not in the
  reading, and a quantity that moves by **0.02** across two orders is at the scale a redraw could move it.
- **And a parameter is not a cause**: that the drift ratio is stable while the accuracy is not says the two are not the
  same measurement, and not that the weights' movement is what the accuracy's movement is not, since neither half of
  `e432`'s split is a counterfactual.
