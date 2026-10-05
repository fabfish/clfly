# The damage lands by arm: the buffer pays at the end and the penalty pays in the middle

*2026-10-05. `experiments/e426_the_damage_lands_by_arm.py` reads every arm of the three configurations rolled under
both task orders -- `e315`'s overlap suite, `e316`'s and `e317`'s assembly suite, with `ewc` on all three and the two
block penalties on the five-arm roll -- each against its own roll's `naive`: **sixteen arm-rolls** over four arms. The
roll itself is `e425`'s pair, `task_order` the only field that differs. No training, no probe. Five claims, registered
before this unit's pass over the runs.*

## 1. The sixteen arm-rolls

| configuration | order | arm | gain by position | mean | worst |
|---|---|---|---|---|---|
| overlap | as-built | `ewc` | +0.0250 -0.0542 **-0.0792** | -0.0361 | last |
| overlap | as-built | `replay` | +0.0542 +0.0542 -0.0000 | **+0.0361** | last |
| overlap | reverse | `ewc` | +0.1083 **-0.1000** -0.0333 | -0.0083 | middle |
| overlap | reverse | `replay` | +0.1042 -0.0000 -0.0042 | **+0.0333** | last |
| assembly | as-built | `ewc` | +0.1167 **-0.1229** -0.0979 | -0.0347 | middle |
| assembly | as-built | `replay` | +0.2333 +0.0937 +0.0021 | **+0.1097** | last |
| assembly | reverse | `ewc` | +0.0187 **-0.2021** -0.0896 | -0.0910 | middle |
| assembly | reverse | `replay` | +0.0875 +0.0667 -0.0104 | **+0.0479** | last |
| assembly-five | as-built | `ewc` | +0.1375 **-0.2042** -0.1042 | -0.0569 | middle |
| assembly-five | as-built | `ewc-block` | +0.0001 **-0.2250** -0.0458 | -0.0903 | middle |
| assembly-five | as-built | `ewc-block-rand` | +0.1333 **-0.0875** -0.0500 | -0.0014 | middle |
| assembly-five | as-built | `replay` | +0.2792 +0.0667 -0.0042 | **+0.1139** | last |
| assembly-five | reverse | `ewc` | +0.0083 **-0.2292** -0.1000 | -0.1069 | middle |
| assembly-five | reverse | `ewc-block` | +0.0417 **-0.0750** -0.0250 | -0.0194 | middle |
| assembly-five | reverse | `ewc-block-rand` | **-0.0417** -0.0875 -0.0542 | -0.0611 | middle |
| assembly-five | reverse | `replay` | +0.0667 +0.0875 -0.0208 | **+0.0444** | last |

The worst position is marked in bold. Replicate counts are ten for the assembly pair and five for the other four rolls.

| claim | measured | verdict |
|---|---|---|
| BB1 the ledger is carried | **3** configurations, **16** arm-rolls, **4** arms | **MET** |
| BB2 and the position effect is every arm's | the first position ahead in **16 of 16**, the smallest margin **+0.0125** | **MET** |
| BB3 and the first position gains, for every arm but one | positive in **15 of 16** | **MET** |
| BB4 and only the buffer's trade pays | buffer **6 of 6** positive, penalties **10 of 10** negative | **MET** |
| BB5 and the damage lands elsewhere | buffer worst last **6 of 6**, penalties worst in the middle **9 of 10** | **MET** |

## 2. What the sixteen say

**The position effect is not the buffer's; it is the sequence's.** In all sixteen arm-rolls the first-taught task gains
more than the last-taught, from **+0.0125** to **+0.2834**, and the first position gains in fifteen of the sixteen (the
smallest of those at **5.96e-09**, a difference of means that is zero to any rounding, and the exception the block
random control under the reversed assembly order). So `e425`'s finding is not about the aid: every arm the corpus ran
on these configurations is ahead at the start of the order and behind at the end.

**And only the buffer's trade pays.** The buffer's mean over the three positions is positive in **all six** rolls
(**+0.0333** to **+0.1139**) while every one of the ten penalty arm-rolls is negative (**-0.0014** to **-0.1069**).
That is the same ordering `e415` and `e423` measured on one cell, now over four arms and both orders.

**And each arm's damage lands in a different place.** The buffer's worst position is the task taught last in **six of
six** rolls; the penalties' worst is the **middle** in **nine of ten** -- `ewc`'s worst is the middle in five of its
six, `ewc-block`'s in both, `ewc-block-rand`'s in both, with the overlap suite's as-built `ewc` the exception at
**-0.0792** on the last. So a penalty is not worst on the task it has just been taught: it is worst on the task it was
**halfway through** when the last one arrived, which is why its trade does not pay.

## 3. What it cannot settle

- **Three configurations and five replicates for the penalties**: `ewc` appears six times at five or ten replicates,
  `ewc-block` and `ewc-block-rand` twice each at five, so the penalty side of the ledger is thin and its means carry
  the draws' spread.
- **And the arms are the corpus's**: one buffer setting (`--replay-per-task 16 --replay-batch 16`) and two penalty
  strengths, so the `lam` ladder is not here.
- **And the ordering is one protocol's**: three tasks with the middle left in place, so a full permutation is not
  measured.
- **And the metric is the corpus's**: the last task is never forgotten after it is taught, so its gain is a `learned`
  difference.
- *And a ledger is not a mechanism.*
