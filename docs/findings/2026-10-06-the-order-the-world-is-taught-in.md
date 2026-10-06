# The order the benchmark's world is taught in: the position effect is the world's, but the reversal does not cost the buffer here

*2026-10-06. `experiments/e436_the_order_the_world_is_taught_in.py` reads the card's world rolled **both ways**. `e380`
rolled it with the as-built order at twenty replicates; this unit drove the missing roll -- the same circuit, read-out
draw, environment draw, task set, iteration budget and arm pair, with **`--task-order reverse`** alone differing, at the
same twenty replicates -- because `e425` and `e426` measured the position effect on the overlap and assembly suites and
both registered that the benchmark's own world was not in the reading. Five claims, registered before the new run's
reading was opened.*

## 1. The two rolls

| roll | order | tasks | gain by position | mean |
|---|---|---|---|---|
| **as-built** | as-built | `loop_odour_identity>loop_heading>loop_odour_input` | **+0.2896** +0.2490 **-0.0604** | +0.1594 |
| **reverse** | reverse | `loop_odour_input>loop_heading>loop_odour_identity` | **+0.3385** +0.2333 **-0.0208** | **+0.1837** |

| the same task, taught first against taught last | at first | at last | margin |
|---|---|---|---|
| `loop_odour_identity` | +0.2896 | -0.0208 | **+0.3104** |
| `loop_odour_input` | +0.3385 | -0.0604 | **+0.3990** |

| claim | measured | verdict |
|---|---|---|
| BL1 the pair is carried | **28** shared fields equal, `task_order` alone differing, the suite reversed | **MET** |
| BL2 and the position effect holds on the benchmark's own world | the first-over-last margin is **+0.3500** and **+0.3594** | **MET** |
| BL3 and the last-taught task is cost under the reversed order | **-0.0208** | **MET** |
| BL4 and the reversal costs the buffer on this world | the mean gain **rises** by **+0.0243** | **FALSIFIER FIRED** |
| BL5 and the same task moves with its position here too | **+0.3104** and **+0.3990** | **MET** |

## 2. What the two rolls say

**The position effect is the benchmark's own world's, and far larger than on the suites that carried the clause.** The
first-taught task over the last-taught one is **+0.3500** as-built and **+0.3594** reversed; the same task is worth
**+0.3104** and **+0.3990** more when it is taught first. `e425` measured the same contrasts at **+0.0583** to
**+0.3000** on the overlap and assembly suites, so on the earned-label cell the effect is at the top of that range and
above it -- the one thing the card's order clause could not say, now measured on the world the card is about.

**And the reversal does not cost the buffer here: it gains, and the claim registered against that is refuted.** BL4
predicted the reversed roll's mean gain would be *below* the as-built one's, on the strength of `e425`'s **-0.0028**,
**-0.0618** and **-0.0694** on the other three configurations. Measured, the mean rises from **+0.1594** to **+0.1837**,
**+0.0243**. The falsifier fired, and the reading under it is worth stating: on this world the reversal *raises* the
oldest task's gain (**+0.3385** against **+0.2896**) and *halves* the newest task's loss (**-0.0208** against
**-0.0604**), so the reversal is not a manipulation that costs the buffer in general -- what costs it is the case that
puts the task it recovers least first.

**And the position effect is therefore the sequence's and not the suite's, while the reversal's price is the
configuration's.** `e425`'s third finding is now bounded to the configurations it was measured on, and the card's order
clause should say so: the direction of the trade is the order's, its size belongs to the world.

## 3. What it cannot settle

- **One permutation**: `reverse` alone, so the other four permutations of a three-task suite are not in this reading.
- **And one cell**: the card's world at twenty replicates, so the other five draws and the three streams are not either,
  and the reversal's price on them is what `e425` measured on other suites rather than what this measures here.
- **And one arm pair**: `naive` and `replay`, so the penalty arms are absent.
- **And a permutation is not a mechanism**: that the order moves the numbers does not say which of the corpus's
  instruments the movement runs through.
- *And a roll is not a mechanism.*
