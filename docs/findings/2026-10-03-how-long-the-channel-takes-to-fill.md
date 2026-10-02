# How long the channel takes to fill: the action source stops two steps before the read-out where the cue source stops one, and `e367`'s invariance is exact only to float32

*2026-10-03. `experiments/e368_how_long_the_channel_takes_to_fill.py` rolls `e363`'s instrument at **every** cue step
from 0 to 11 and both drive sources rather than at three steps, and rolls the two late steps under **nine bodies** --
the connectome's own weights with a zero bias, plus eight draws on the same mask. Five seconds. Writes
`runs/e368_how_long_the_channel_takes_to_fill.json`. Four claims, registered before any cell of the curve was read.*

## 1. The curve

One circuit, one world of eight dimensions at `leak = 0.35`, four symbols, 512 examples in half and half, the
corpus's own least-squares probe on the world's **final state**. `cue acc` is that probe; `sd` is `e363`'s own
`world_sd`.

| cue at | cue acc | cue sd | action acc | action sd |
|---|---|---|---|---|
| 0 | 0.7891 | 0.2156 | **0.6602** | 0.2029 |
| 1 | 0.7773 | 0.2000 | 0.6367 | 0.1980 |
| 2 | 0.7109 | 0.1833 | 0.6602 | 0.1936 |
| 3 | 0.6758 | 0.1658 | 0.6797 | 0.1867 |
| 4 | 0.7930 | 0.1534 | 0.6914 | 0.1754 |
| 5 | 0.8320 | 0.1377 | 0.7148 | 0.1571 |
| 6 | 0.8789 | 0.1141 | 0.7578 | 0.1328 |
| 7 | 0.8672 | 0.0876 | 0.7422 | 0.0952 |
| 8 | **0.8906** | 0.0600 | 0.7617 | 0.0478 |
| 9 | 0.8594 | 0.0580 | **0.2578** | **0.0000** |
| 10 | 0.8555 | 0.0719 | **0.2578** | **0.0000** |
| 11 | **0.2578** | **0.0000** | **0.2578** | **0.0000** |

**Both sources read better when the cue is later, and the action source stops two steps earlier.** The cue source
climbs from **0.7891** at the first step to **0.8906** at step 8 and holds above 0.85 to step 10; the action source
climbs from **0.6602** to **0.7617** over the same range and is a **constant** from step 9 on. `e363` read three of
these cells and two of them are the cliffs; what the curve adds is that the cliffs are **sharp and separated by one
step** -- the cue source's last clearing step is **10**, the action source's is **8** -- and that the rise before
them is real, so a later cue is worth about **0.10** of accuracy to the cue source and about the same to the action
one.

**The `sd` column is the mechanism.** The world's spread decays smoothly as the cue arrives later -- 0.2156 at the
first step, 0.0600 at step 8 -- and then is **exactly 0.0** at the three late action cells and at `cue@11`. A world
with no spread is a constant, so those four cells are not floors a decoder failed to clear; they are read-outs with
nothing in them, and 0.2578 is what a linear probe on a constant returns.

## 2. The four claims

**W1 MET**: the untrained body's action-source world has a spread of **exactly 0.0** at `cue@10` and `cue@11`, and
`e363` records **0.0** for the same two cells. Three fires after that unit read those numbers as "chance", this
instrument reproduces them as what they are.

**W2 FIRED, and the firing is a precision effect that the claim registered a bar too small to see.** The claim was
that the world's final state is *identical* across all 512 examples for every body, with a bar of **1e-12**; the
falsifier was any body whose world moves with the trial. Eight of the nine bodies move with the trial, by
**1.5e-08 to 3.0e-08** -- and the ninth, the untrained one, is exactly **0.0**. The untrained body has a zero bias,
so its state is exactly the zero vector and every product in the pass is exactly zero; a draw with a nonzero bias
has a nonzero state, and then the trials' different cues enter the same floating-point sums and land in the low
bits. **The invariance is exact in the arithmetic and absent in the float**, and the bar the claim chose sits below
the precision the module computes in: float32 carries about seven decimal digits, and the world's own values are of
order 0.1, so 1e-8 is the floor rather than a measurement. **What survives is the scale**: 3.0e-08 of across-trial
movement against the cue-fed world's **0.9700** across-trial range at the first step, a ratio of **3.1e-08**, and a
probe on those worlds reads **0.2578**, which is chance. This is reported as a fired falsifier and not excused, and
the claim a next unit would register puts the bar **relative to the world's own scale** so that the statement is
about the arithmetic rather than about the float.

**W3 MET**: the action source at `cue@0` reads **0.6602**, **+0.4102** over chance, on a world with a spread of
**0.2029**. The agent's own action does fill the world -- it needs the time to do it.

**W4 MET**: the population's price is time, and it is **one step** of it: the last cue step that still clears chance
by 0.05 is **10** for the world listening to the cue and **8** for the world listening to the agent's own action.

## 3. What it means

**`e363`'s two points are the edges of a curve with two different cliffs, and the action source's is the earlier
one.** The unit read *"the timing is the hard limit"* from the read step being chance in both sources and from one
step of margin separating them; this says the source that the world reads directly keeps working one step from the
read, the source the agent has to write into stops two steps out, and **both are best a step or two earlier than
their own cliff** because the cue is fresher. A game that reads the agent's own action therefore has a window of
about **steps 0 to 8** and not the whole trial, and the window is a property of the circuit's wiring rather than of
the decoder -- `sd` falls to zero at the same two steps in both.

**`e367`'s bit-identity gets its second half.** That unit trained the action source at `cue@10` and at `cue@11` and
got the same twenty replicates twice, and reported the account rather than claiming it. The account has two parts
and this unit measures both: the world is at rest there (`world_sd` exactly 0.0, W1), and a body that is **not** at
rest still cannot see the trial (the across-trial movement is round-off, W2). The trained runs' biases do move, so
the bodies in them are the second kind, and the reason their training is identical is that the quantity training
would have to move differs between the two cues only in the low bits of a float32 sum.

**And one coincidence worth recording rather than claiming.** The gap between the two sources' readings is
**0.1289** at the first step and **0.1289** at step 8 -- the same number at both ends of the ramp, in a grid whose
resolution is about 0.002. Six steps apart, two different dynamics, one split of 512 examples: it is more likely a
coincidence of this grid than a conservation law, and it is written down because it is the kind of thing a later
unit would otherwise rediscover and believe.

## 4. What it cannot do

*A frozen probe on one world draw*: the curve is the corpus's linear decoder on one coupling matrix at
`leak = 0.35`, and a different drive map, a different dimension or the nonlinear world of `e360` is not measured
here. *Nine bodies and not every body*: the invariance is structural -- the state entering the world's last step is
a function of the state before the cue arrived -- and nine draws check the argument rather than prove it, and the
check is what the fired W2 shows is weaker than it looked. *And the cliff is measured, not explained*: the action
source stops two steps out and the cue source one, and this unit says nothing about **why**; the shape of the curve
is what a shortest path from the cue population to the action population would produce, and that is a claim about
the connectome's own edges, which is the unit this one points at. *And "clears chance" is one linear read-out at one
split*: 512 examples in half and half put the resolution near 0.02, so a step within 0.05 of chance is unresolved.
