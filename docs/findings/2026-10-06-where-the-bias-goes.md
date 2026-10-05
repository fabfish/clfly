# Where the bias goes: the buffer holds it down and the penalty pushes it up

*2026-10-06. `experiments/e430_where_the_bias_goes.py` reads the bias's own trajectory -- the distance from zero after
each task and the step each task costs, per arm -- off two runs: the card's world at twenty replicates with `naive`,
`ewc-block` and `replay` in one run (the cell `e415` and `e423` read), and the plastic/frozen-bias pair at forty
replicates whose frozen side `e427` used as the control. No training, no probe. Five claims, registered before this
unit's pass over the runs.*

## 1. The bias, per arm

| roll | arm | from zero 0/1/2 | step 0/1/2 |
|---|---|---|---|
| **card's world, 20 reps** | `ewc-block` | +1.4010 +2.7761 **+4.0809** | +1.4010 +2.3750 +2.8436 |
| | `naive` | +1.4010 +2.1539 +2.7453 | +1.4010 +1.6240 +1.6050 |
| | `replay` | +1.4010 +1.9076 **+2.2946** | +1.4010 +1.2639 +1.1140 |
| **pair, frozen bias, 40 reps** | every arm | **0.0000** 0.0000 0.0000 | 0.0000 0.0000 0.0000 |
| **pair, plastic bias, 40 reps** | `ewc` | +1.1183 +1.8486 **+2.5027** | +1.1183 +1.4692 +1.6944 |
| | `ewc-block` | +1.1183 +1.6652 +2.1428 | +1.1183 +1.2364 +1.3758 |
| | `ewc-block-rand` | +1.1183 +1.6842 +2.1047 | +1.1183 +1.2394 +1.3273 |
| | `naive` | +1.1183 +1.6049 +2.0005 | +1.1183 +1.1767 +1.2256 |
| | `replay` | +1.1183 +1.6041 **+1.9721** | +1.1183 +1.1341 +1.1556 |

| claim | measured | verdict |
|---|---|---|
| BF1 the ledger is carried | **20** and **40** replicates, a distance and a step per task per arm | **MET** |
| BF2 and after the first task the arms are one arm | all three at **+1.400981** | **MET** |
| BF3 and the buffer ends closest to zero | **+2.2946** against **+2.7453** and **+4.0809** | **MET** |
| BF4 and the penalty ends furthest | **+4.0809** against **+2.7453** and **+2.2946** | **MET** |
| BF5 and the control's own reading is zero | **0.0000** on every arm at 40 replicates, beside a plastic side that is not | **MET** |

## 2. What the trajectory says

**The arm that forgets least also holds the bias closest to where the sequence started.** On the card's world the three
arms are one arm after the first task (**+1.4010** each) and then separate: after the third task the buffer's bias sits
at **+2.2946**, the arm that does nothing at **+2.7453** and the basis-matched penalty at **+4.0809**. The penalty's
steps grow with each task (**2.3750**, **2.8436**) while the buffer's shrink (**1.2639**, **1.1140**), so the two arms'
difference is not a constant offset but a divergence that widens as the sequence runs.

**And the pair shows the same ordering across five arms.** On the plastic side the final distance runs `ewc`
**+2.5027** > `ewc-block` **+2.1428** > `ewc-block-rand` **+2.1047** > `naive` **+2.0005** > `replay` **+1.9721**: the
buffer is nearest zero of the five and the diagonal penalty furthest, so the ordering `e415` and `e423` measured on
accuracy and retention reappears on the parameter `e427` found three quarters of the aid living in.

**And the control's own definition is visible in the same field.** The frozen side reads exactly **0.0000** on all five
arms' distances and steps at forty replicates, which is what a frozen bias means, and it is the ground the plastic side
above is measured against -- the same structural-zero pattern `e422` used for the task-0 learning term.

## 3. What it cannot settle

- **Two cells and one bias definition**: the three-arm reading is the card's world at `lam = 1.0`, whose world predates
  `e359`'s coupling, and the pair is one overlap-suite configuration, so the corpus's other configurations are not in
  this reading.
- **And a displacement is not a mechanism**: where the bias goes and what the arm forgets are two readings of one
  trajectory, and this unit intervenes on neither, so the ordering is a co-movement and not a cause.
- **And the distance is from the initialisation**: the corpus records the distance from zero, which for a
  zero-initialised bias is the same thing and for any other is not.
- **And the metric is the corpus's** where accuracies are quoted: `mean_forgetting` is the diagonal minus the last row,
  which `e305` showed cannot see the part an arm never learned.
- *And a trajectory is not a mechanism.*
