# The aid turns on: the rehearsal is worth nothing until the body has learned something, and then a sixth of accuracy

*2026-10-05. `experiments/e412_the_aid_turns_on.py` reads the corpus's own budget ladder on the card's world. `e389`,
`e390`, `e391` and `e380` rolled one configuration -- `cue0` with the action source, twenty replicates, the same
circuit, read-out draw, environment draw and task list -- at **twenty** update budgets from 1 to 500, and every one of
the twenty artifacts carries both the `naive` and the `replay` arm. No training, no probe. Five claims, registered
before this unit's pass over the ladder.*

## 1. The aid along the budget

| budget | naive acc | replay acc | gain | naive mf | cut |
|---|---|---|---|---|---|
| 1 | 0.2438 | 0.2438 | +0.0000 | 0.0063 | +0.0089 |
| 2 | 0.2455 | 0.2507 | +0.0052 | -0.0026 | +0.0031 |
| 3 | 0.2580 | 0.2656 | +0.0076 | -0.0089 | +0.0188 |
| 4 | 0.2684 | 0.2535 | **-0.0149** | 0.0010 | -0.0109 |
| 5 | 0.2764 | 0.2569 | **-0.0194** | 0.0036 | -0.0042 |
| 6 | 0.2681 | 0.2625 | -0.0056 | 0.0307 | -0.0000 |
| 8 | 0.2576 | 0.2632 | +0.0056 | 0.0344 | +0.0141 |
| 11 | 0.2792 | 0.2750 | -0.0042 | 0.0349 | +0.0260 |
| 14 | 0.2743 | 0.2774 | +0.0031 | 0.0469 | +0.0286 |
| 17 | 0.2882 | 0.2837 | -0.0045 | 0.0578 | +0.0391 |
| 20 | 0.2969 | 0.2924 | -0.0045 | 0.0536 | +0.0307 |
| 30 | 0.2990 | 0.3163 | +0.0174 | 0.1099 | +0.0620 |
| 45 | 0.3187 | 0.3601 | +0.0413 | 0.1224 | +0.0995 |
| 65 | 0.3517 | 0.4149 | +0.0632 | 0.1135 | +0.0901 |
| 85 | 0.3993 | 0.4514 | +0.0521 | 0.1281 | +0.1245 |
| 100 | 0.3833 | 0.4569 | +0.0736 | 0.1547 | +0.1401 |
| 150 | 0.3858 | 0.4951 | +0.1094 | 0.2323 | +0.2141 |
| 275 | 0.4694 | 0.5878 | +0.1184 | 0.2906 | +0.2505 |
| 425 | 0.5111 | 0.6552 | +0.1441 | 0.3755 | +0.2724 |
| 500 | 0.5191 | 0.6785 | **+0.1594** | 0.3750 | **+0.2844** |

| claim | measured | verdict |
|---|---|---|
| AT1 the ladder is carried | **20** budgets, **20** replicates on both arms, one configuration except the budget | **MET** |
| AT2 the sign is not the world's at the small budgets | **5** positive and **6** negative at or below 20 | **MET** |
| AT3 and the aid ramps | lift **+0.0858** over the best small-budget gain | **MET** |
| AT4 and above the knee the order is monotone | **+0.0736 < +0.1094 < +0.1184 < +0.1441 < +0.1594** | **MET** |
| AT5 and the aid's worth tracks the level | rank correlation **+0.740** | **MET** |

## 2. What the ladder says

**At the small budgets the aid has no sign.** Below and at twenty updates the gain is positive at five budgets and
negative at six -- `-0.0194` at 5, `+0.0076` at 3 -- and the naive arm itself sits between 0.2438 and 0.2969, around
the four-way chance level of a task that has not been learned. The `replay` arm's buffer protects something there is
nothing to protect, and the sign of what it does is the draw's.

**And it turns on between twenty and forty-five, then ramps without a step.** From budget 30 to 500 all nine gains are
positive, and over the top five of them the gain is strictly increasing in the budget: +0.0174, +0.0413, +0.0632,
+0.0521, +0.0736, +0.1094, +0.1184, +0.1441, +0.1594. The naive arm's own mean forgetting rises with the budget too
(0.0536 at 20, 0.1547 at 100, 0.3750 at 500), and the aid's cut rises with it: the ladder's forgetting cut goes from
**+0.0307** at 20 to **+0.2844** at 500. So what the aid is worth is what there is to lose, and at these budgets there
is nothing to lose until the body has learned the task.

**And `e411`'s six worlds sit at the top of this ladder.** `e411` measured the aid at **+0.1330** to **+0.1594** on six
worlds at budget 500 and named the single setting it could not settle. This is that setting's own axis: 500 is the
last rung, where the aid is worth most, and the reading `e411` made is the top of a nine-fold rise from budget 30.
The rise from **100 to 500** is part of this ramp rather than a step, which is what `e408` named as the open question
about the widening.

**And the corpus's own budget ladder was rolled at four code revisions.** The twenty artifacts carry four different
`code_revision` commits, so what the ladder holds fixed is the recorded configuration and not one process; the
machine calibration moves between executions of one configuration.

## 3. What it cannot settle

- **One world and one arm pair**: `cue0` with the action source and the `naive`/`replay` pair only, so the ladder is
  one world's and the penalty arms are absent from all twenty artifacts. `e276`'s replay-over-penalty contrast is not
  available here.
- **And the budget is not the level**: the naive arm's accuracy rises 0.2438 to 0.5191 along the same axis, so the
  +0.740 is a correlation over a joint ramp and not an intervention -- the ladder cannot separate "the aid needs a
  learned task" from "the aid needs updates".
- **And the metric is the corpus's**: `mean_forgetting` is the retention matrix's diagonal minus its last row, which
  `e305` showed cannot see the part an arm never learned.
- *And a probe is not a mechanism.*
