# The tightest step: the price of acting is 0.2035 there against 0.0708 at the wide step, and the action source does not learn at all where a frozen probe still reads 0.7617

*2026-10-03. `experiments/e374_the_tightest_step.py` trains both drive sources at `cue@8` -- the last step where
`e368`'s curve says both channels are alive on this draw -- at `e371`'s and `e372`'s exact flags, twenty replicates
each, and prices acting there against the same quantity at `cue@0`. Two runs, 1003 s and 1110 s; the reader is
`runs/e374_the_tightest_step.json`. Five claims, registered before either run's reading was opened.*

## 1. The two steps

| cue at | source | diagonal | forgetting | paired channel | frozen | frozen sd |
|---|---|---|---|---|---|---|
| 0 | cue | **0.8399** | 0.4094 | +0.3115 (18.74 sigma) | 0.7891 | 0.2156 |
| 0 | action | **0.7691** | 0.3750 | +0.2642 (18.08 sigma) | 0.6602 | 0.2029 |
| 8 | cue | **0.4368** | 0.0563 | +0.1535 (8.81 sigma) | 0.8906 | 0.0600 |
| 8 | action | **0.2333** | -0.0094 | **-0.0083 (0.92 sigma)** | **0.7617** | 0.0478 |

cost of acting: **+0.0708** at `cue@0`, **+0.2035** at `cue@8` (11.99 sigma on a sem of 0.0170). chance 0.2500.

| claim | measured | verdict |
|---|---|---|
| T1 one configuration at both steps | four runs, shared fields differing `{}` in the pair and `{}` across the steps, couplings the two sources' own | **MET** |
| T2 both channels are live at this step | cue **+0.6406** over chance, action **+0.5117**, both worlds with spread | **MET** |
| T3 both games are learnable | cue **+0.1868**, action **-0.0167** | **FALSIFIER FIRED** |
| T4 the price is larger where the margin is tighter | **+0.1326** more at `cue@8` than at `cue@0` | **MET** |
| T5 the answer is earned in both sources | cue **+0.1535 at 8.81 sigma**, action **-0.0083 at 0.92 sigma** | **FALSIFIER FIRED** |

## 2. What fired, and why it is the unit's real result

**At `cue@8` the action source does not learn the suite at all.** Its `naive` diagonal is **0.2333**, **0.0167 below**
a chance of 0.25, over twenty replicates; its paired channel is **-0.0083 at 0.92 sigma**, so nothing about the
answer is coming through the loop; and its forgetting is **-0.0094**, which is what a run with nothing to lose
records. `T3` and `T5` fired exactly as registered and are reported as fired.

**And the frozen probe reads 0.7617 at the same step.** `e368`'s curve, rolled on the untrained body in the same
configuration, puts the action source's world at `cue@8` at **0.7617**, **+0.5117** over chance, with a spread of
**0.0478** -- the reading this unit's T2 rests on and which is what made the step worth training. So on this step
**a frozen body is readable and a trained body is not**: the same configuration that a least-squares probe decodes
from an untrained network is one that twenty replicates of training take to chance.

**That is the reversal of `e371` and `e372`.** At the wide step the trained bodies read **above** their frozen probes
(**+0.0509** and **+0.1089**); here both read far **below** them (cue **-0.4538**, action **-0.5284**), which is the
sign `e364` and `e365` found at the late steps. So the phenomenon those two units reported is not a property of
training in this substrate: **it is a property of the margin**. Where the trial has room, training beats a probe;
where the world's drive sees the population for a single step, training loses to one -- and in the action source's
case loses everything.

**The mechanism is available and this unit does not measure it.** At `cue@8` the world's last update is the **only**
one whose drive can carry the cue, so the body must hold the symbol in its action population at exactly one time
step and the gradient reaches it through exactly one step; at `cue@0` the same population holds the cue for eleven
steps. A gradient that is one step long is a candidate explanation for both the failure and the probe's success --
a probe fitted on the frozen population exploits a representation that is *already there*, and nothing in the
trainer's objective asks for that representation to survive. **That is reported as a hypothesis and not claimed**,
and the unit that would test it is named below.

## 3. The price

**T4 MET, and it is the number `e373` could not get.** The paired cost of acting is **+0.0708** at `cue@0` and
**+0.2035** at `cue@8`, a growth of **+0.1326** as the margin shrinks from eleven steps of room to one. So the
answer to the question `e372` and `e373` left open is: **the price of acting does grow as the window narrows**, by
about a factor of **2.9**, and it grows because the action source's own task becomes unlearnable while the cue
source's only becomes harder.

**And the two sources' curves cross the probe line in opposite directions.** The cue source is still above chance at
`cue@8` (**0.4368**, **+0.1868**) and still earning the answer through the loop (**+0.1535 at 8.81 sigma**), so the
tight step costs it accuracy and not the task; the action source loses the task. With `cue@0`, `cue@8` and `cue@10`
now trained at both sources, the shape is: the action source learns at the wide step, fails to learn at `cue@8` even
though its world is still live there, and from `cue@9` on its world is at rest and there is nothing to learn from.

## 4. What it cannot do

*One draw, and the boundary is this draw's*: `e370` showed the distance moves with the draw, so another draw's last
live step is another cell, and both the failure and the 0.2035 belong to this one. *Two points in the window and
still not a curve*: `cue@0` and `cue@8` are a line, and where between them the action source stops learning is not
walked. *And the probe's 0.7617 is not paired*: it comes from `e368`'s roll on the untrained body at 512 examples
once, while the trained diagonals come from twenty replicates, so the reversal is a comparison of a probe with a
body and not of two bodies. *And the mechanism is a hypothesis*: this unit measured that training fails where a
probe succeeds, and named the one-step gradient as what would explain it; the unit that would establish it has to
intervene on the gradient's length or on the probe's object, which is a different experiment from this one.
