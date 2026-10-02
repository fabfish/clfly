# Class-incremental on the earned label: the shared head costs 0.0208 and the buffer is worth 0.2667 at 11.38 sigma

*2026-10-02. `experiments/e353_the_class_incremental_earned_label.py` runs `e352`'s suite with one shared head over
all twelve classes. Five seeds, two arms, four minutes. Writes `runs/e353_the_class_incremental_earned_label.json`.*

## 1. The harder protocol `e352` named

`e352` made the earned label sequential and closed with the boundary of what it had built: *"the head is per task, so
this is task-incremental: which task the trial belongs to is given to the read-out, and a shared head over one world
is a different and harder benchmark."*

**This takes the task's identity away from the read-out.** The suite is `e352`'s exactly -- and that is measured, not
asserted: this run's world fingerprints are `['3a7ba76b3619']` against the task-incremental artifact's
`['3a7ba76b3619']`, the same world to the digit -- and the only change is **one shared head over twelve classes**,
each task's four in a slice of its own, with the loss taken over the current task's slice so no future class is ever
shown.

## 2. The answer

| read | mean over 5 seeds | sem | per-seed |
|---|---|---|---|
| `naive`, diagonal | 0.8028 | | |
| `naive`, `mean_forgetting` | **0.3542** | 0.0399 | 0.3750, 0.3542, 0.2188, 0.4688, 0.3542 |
| `replay`, diagonal | 0.7806 | | |
| `replay`, `mean_forgetting` | **0.0875** | | 0.1250, 0.0833, -0.0521, 0.1250, 0.1562 |

chance 0.2500. **T1 MET**: one world and one set of populations across both arms, one distinct fingerprint each, and
the same world as the task-incremental unit. **T2 MET**: the suite is learned in the harder protocol too -- the worse
arm's diagonal mean is **+0.5306 above chance**. **T4 MET**: the buffer is worth **0.2667** of forgetting -- paired
within a seed the five deltas are `[-0.2500, -0.2708, -0.2708, -0.3437, -0.1979]`, **all five negative, 11.38
sigma**, the strongest method contrast anywhere in this line -- and task 0's final accuracy is **0.3042** under
`naive` against **0.6458** under `replay`.

**T3 NULL, and it is the interesting one.** `naive` forgets **0.3542** here against **0.3333** in the
task-incremental suite: taking the task's identity away from the read-out costs **+0.0208**, over the 0.02 the
falsifier needed and under the 0.05 the claim asked for. **So the difficulty of this benchmark is in the body and
not in the read-out**: with the answer living in the world, giving the head the task's identity is worth about one
fiftieth of a point, because the head was never where the forgetting happened -- a twelve-class head over an
eight-number world is a small linear object, and the body is what loses the world.

## 3. The two protocols side by side

| suite | arm | diagonal | forgetting |
|---|---|---|---|
| task-incremental (`e352`) | `naive` | 0.8153 | 0.3333 |
| task-incremental (`e352`) | `replay` | 0.7875 | 0.1146 |
| class-incremental (this unit) | `naive` | 0.8028 | **0.3542** |
| class-incremental (this unit) | `replay` | 0.7806 | **0.0875** |

The diagonal moves by 0.0125 and 0.0069; the forgetting by 0.0208 and 0.0271. So the corpus's own hardest protocol
is nearly free on the earned label, and `replay`'s value survives it -- and one seed even improves the old task
under the buffer (`-0.0521` of forgetting, backward transfer). **That is the opposite of what this benchmark would
do if the read-out were the model's state**, where the class-incremental protocol is where the corpus's own
catalogue puts its hardest numbers; the difference is that here the shared object is the world and the head is
three-quarters of a hundredth of it.

## 4. What it cannot do

*The protocol comparison is against one number on disk*, `e352`'s 0.3333 over five seeds, so T3 is a difference of
two estimates with their own spreads and not a paired contrast; the paired version would need both protocols in one
module, which is the natural next unit. *A bespoke loop and two arms*, with `ewc`, the block penalties, the
matched-random control and the frozen controls unrun, so this is a benchmark's shape and not a method comparison.
*Three tasks and five seeds*, with a six-entry lower-left block. *One world, one leak and one width*: `leak = 0.35`,
eight dimensions and four symbols per task. *And the shared head is linear over one world*, so a wider or non-linear
read-out is `e345`'s and `e350`'s axis and not this unit's.
