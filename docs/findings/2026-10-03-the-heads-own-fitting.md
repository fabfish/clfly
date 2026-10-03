# The head's own fitting: ten times the step size is worth 0.1965 at 64.92 sigma, and the shortfall splits again

*2026-10-03. `experiments/e376_the_heads_own_fitting.py` runs the same frozen body at the same cell as `e375` with
the head's learning rate at **0.03** instead of the corpus's **0.003**, everything else held. 1065 s; the reader is
`runs/e376_the_heads_own_fitting.json`. Five claims, registered before the run's reading was opened.*

## 1. The result

| run | lr | arm | diagonal | forgetting | paired channel |
|---|---|---|---|---|---|
| **stepped** | **0.03** | naive | **0.6455** | 0.0000 | **+0.4083** (146.52 sigma) |
| **stepped** | **0.03** | replay | 0.6462 | 0.0000 | +0.4090 (197.49 sigma) |
| base | 0.003 | naive | **0.4490** | 0.0000 | +0.2128 (204.33 sigma) |
| base | 0.003 | replay | 0.4472 | 0.0000 | +0.2111 (180.32 sigma) |

chance 0.2500. The closed-form probe on the **same** frozen body reads **0.7617** (`e368`).

| claim | measured | verdict |
|---|---|---|
| V1 one configuration except the learning rate | fields differing `{'lr': [0.03, 0.003]}` and nothing else | **MET** |
| V2 the world is live at this step | **+0.5117** over chance, spread **0.0478** | **MET** |
| V3 the head was short of steps | **+0.1965** on a sem of **0.0030**, **64.92 sigma** paired | **MET** |
| V4 it still does not reach the closed form | short by **0.1162** | **MET** |
| V5 the answer is still earned | **+0.4083 at 146.52 sigma** and **+0.4090 at 197.49 sigma** | **MET** |

## 2. The gap, in three parts

**The shortfall `e375` left splits again.** That unit put the gap between the probe and the plastic body at **0.5284**
and accounted for **0.2156** of it with the body's own training. This one accounts for another **0.1965** with the
head's step size. What remains is **0.1162**:

| part | value | what it is |
|---|---|---|
| the body's own training | **0.2156** | measured by `e375` at 229.59 sigma |
| the head's step size | **0.1965** | measured here at 64.92 sigma |
| still unexplained | **0.1162** | reported, this unit's V4 |

So **63%** of the head-versus-probe half was where the steps were, and **37%** of it is not. Ten times the step size
on eight features and 96 examples still does not reach one ridge solve, and the remaining 0.1162 is a difference
between a `Linear(8, 4)` under Adam and cross-entropy for 500 iterations and a closed-form least-squares fit on
one-hot targets -- which this unit does not separate into its parts.

**And the scale account this unit was built on is what the direction shows.** Adam moves a coordinate by about `lr`
per step, so 500 steps at `3e-3` move the weights about **1.5**, and with the world's state at `cue@8` carrying a
spread of **0.0478**, a logit is then of order **0.2**; at `0.03` the same 500 steps move the weights about **15**
and the logits are of order **2**. The corpus's default is not too small in general -- at `cue@0` the same world
puts out a spread of **0.2029**, four times larger, and 500 steps at `3e-3` there already reach **0.7691**, above
that step's probe -- so **the step size is too small exactly where the world is small**, which is what the tight end
of the window is.

## 3. What else the run says

**The sharper head leans on the loop twice as hard.** The paired channel reading goes from **+0.2128** to
**+0.4083** under `naive` when the step size rises: the eight world numbers carry more of the answer to a head that
can build bigger logits, so the loop is more load-bearing and not less. That is the check V5 was registered for, and
it is the opposite of what a head sharpened into reading a static body would have looked like.

**And the probe at the runner's own resolution is 0.7500.** `e368`'s cell is 512 examples in two halves of 256; the
head is trained on 96 and read on 48. A design check run before this unit's claims were written -- one roll of the
untrained body, the corpus's own probe, the runner's split -- puts the probe at **0.7500** there, so the stepped head
is short by **0.1045** against a closed-form fit at the same resolution rather than by 0.1162 against a wider one.
Reported and not claimed: it is a measurement this unit's reader does not carry and the numbers above are `e368`'s.

**And it names the more important open question.** `e374`'s plastic body at `cue@8` trained to **0.2333** -- chance
-- with the corpus's `lr = 3e-3`, and this unit shows that at this step that step size leaves a head **0.1965** short
of what a slightly larger one reaches. **So part of what `e374` read as "the body's training loses the reading" may
also be the step size**, and the run that would separate them is the plastic body at `cue@8` with the larger step:
if it learns, the game is playable at the tight end of the window after all, and if it does not, the loss is where
`e375` put it. Nothing here decides that, and the two units that bracketed it were both frozen.

## 4. What it cannot do

*One lever at one value*: ten times the default is a direction and not a dose, so what is established is that the
step size matters at this step and something about its size, not where it stops mattering. *One cell and one draw*:
`cue@8` on this draw, whose world's small spread is what the account turns on, so `cue@0` and the boundary are not
walked and neither is another draw's. *And it is the corpus's own head*: a different parameterisation, a warm start
or a closed-form read-out would be different interventions on the same 0.1162, and this unit turned the one knob the
runner exposes. *And the remaining 0.1162 is not decomposed*: it is the difference between two fitting procedures,
and which part of it is the objective, which the parameterisation and which the regularisation is the unit this one
points at.
