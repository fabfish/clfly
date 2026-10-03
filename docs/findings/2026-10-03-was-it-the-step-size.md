# Was it the step size: no. The plastic body moves by 0.0104 at 1.78 sigma where the frozen one moves by 0.1965 at 64.92 sigma

*2026-10-03. `experiments/e377_was_it_the_step_size.py` runs the plastic body at `cue@8` -- the cell `e374` read as
chance -- with the head's step size at `0.03`, which is what `e376` found worth **+0.1965** on a frozen body at the
same cell. 1139 s; the reader is `runs/e377_was_it_the_step_size.json`. Five claims, registered before the run's
reading was opened.*

## 1. The two-by-two

One cell, one drive source, one draw, one head: the body's plasticity crossed with the head's step size.

| body | lr | arm | diagonal | forgetting | paired channel |
|---|---|---|---|---|---|
| plastic | 0.003 | naive | **0.2333** | -0.0094 | -0.0083 (0.92 sigma) |
| plastic | **0.03** | naive | **0.2437** | -0.0094 | **-0.0031 (0.32 sigma)** |
| plastic | **0.03** | replay | 0.2521 | 0.0078 | -0.0045 (0.44 sigma) |
| frozen | 0.003 | naive | **0.4490** | 0.0000 | +0.2128 (204.33 sigma) |
| frozen | **0.03** | naive | **0.6455** | 0.0000 | +0.4083 (146.52 sigma) |

chance 0.2500; the closed-form probe on the untrained body reads **0.7617**.

| claim | measured | verdict |
|---|---|---|
| W1 one configuration on two pairs | vs `e374` differing `{'lr': [0.03, 0.003]}`, vs `e376` differing `{'frozen_body': [False, True]}` | **MET** |
| W2 the world is live at this step | **+0.5117** over chance, spread **0.0478** | **MET** |
| W3 the step size was what `e374` was short of | **+0.0104** on a sem of **0.0059**, **1.78 sigma** | **FALSIFIER FIRED** |
| W4 the body's plasticity still costs something | **+0.4017** at **60.75 sigma** paired | **MET** |
| W5 the answer is earned | **-0.0031 at 0.32 sigma** and **-0.0045 at 0.44 sigma** | **FALSIFIER FIRED** |

## 2. What fired, and what it settles

**It was not the step size.** Ten times the learning rate moves the plastic body by **0.0104**, which is **1.78
sigma** over twenty paired replicates -- unresolved, and a tenth of the **0.10** the claim asked for. `e374`'s
reading, that the action source at `cue@8` does not learn the suite, is **the body's own**, and `e376`'s hypothesis
that part of it might be where the steps were is refuted in the direction it was raised. W3's falsifier fired
exactly as registered and is reported as fired.

**And the account it was testing is not merely intact but stronger.** At the **same** step size the frozen body
reads **0.6455** against the plastic one's **0.2437**: **+0.4017 at 60.75 sigma**, twice the **0.2156** `e375`
measured at the smaller step size. So the cost of a plastic body at this cell is not a constant to be priced once --
it **grows with how well the head is fitted**, because a head that can build bigger logits is a head that can lose
more when the features it reads are being overwritten.

**The step size is worth something only when the body is held.** On the frozen body the same change is
**+0.1965 at 64.92 sigma**; on the plastic one it is **+0.0104 at 1.78 sigma**. That is an interaction rather than
two effects: the head's fitting is worth a fifth of an accuracy point when the representation underneath it is
fixed, and nothing when that representation is moving. **The head is not what fails here.**

**And the channel says the same thing from the other side.** The plastic body's paired channel is **-0.0031 at 0.32
sigma** at the larger step size -- still nothing, and no better than the -0.0083 it read at the smaller one -- where
the frozen body's is **+0.4083 at 146.52 sigma**. A head that leans on the loop cannot lean on a loop whose
population is being trained away from the answer.

## 3. What it means

**`e374`'s headline stands, with one of its two candidate explanations eliminated.** That unit trained both sources
at the tight step and found the action source at chance where the frozen probe reads 0.7617; `e375` priced the
body's plasticity at 0.2156 and `e376` priced the head's step size at 0.1965 on a frozen body; this unit shows the
second does not transfer. So the shape over the window is: the cue source still works at `cue@8` (**0.4368**, and
**+0.1535 at 8.81 sigma** through the loop) and the action source does not work there by any of the three knobs this
line has turned. **The game is playable at the wide end and not at this end, and the difference is what the body
does to its own representation while it is being trained.**

**And it re-prices the body's cost as a function of the head.** 0.2156 at `lr = 3e-3` and 0.4017 at `lr = 0.03`, both
on the same cell and the same seeds. Whatever a later unit quotes as "what acting costs at the tight step" has to
say what the head was doing, in the same way `e366` made this line say what its example count and its arrangement
were worth.

## 4. What it cannot do

*One lever at one value*: ten times the default is a direction and not a dose, and a plastic body that does not move
at `0.03` is bounded between two values rather than shown to be immovable -- a larger one is not ruled out, though
the direction of the frozen run's own gain makes a step-size rescue look unlikely. *One cell and one draw*: `cue@8`
on this draw, whose world's small spread is what the account turns on. *And the interaction is measured, not
decomposed*: that the body's cost grows with the head's fitting is a number in this table, and how a better-fitted
head makes a plastic body lose more -- a larger gradient into the recurrent weights, a sharper objective, or the
head and the body competing for the same eight numbers -- is the unit this one points at.
