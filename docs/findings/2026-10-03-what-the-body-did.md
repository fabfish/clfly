# What the body did: the training removed the cue from the world, and on the trained body a probe reads exactly what the head reads

*2026-10-03. `experiments/e379_what_the_body_did.py` runs `e377`'s cell -- the action source at `cue@8` with the
head's step size at `0.03`, twenty replicates, two arms -- with `--save-theta`, and then, for every replicate and
every task, rolls the task's own examples through the **saved** recurrent weights and fits the corpus's own
least-squares probe on the world's final state, for the body **before** training and after each task. 1026 s for the
run and 9.7 s for the reading; the reader is `runs/e379_what_the_body_did.json`. Five claims, registered before the
run's reading was opened.*

## 1. The result

| arm | probe, initial body | probe, trained body | trained head | world's spread |
|---|---|---|---|---|
| naive | **0.6597** | **0.2361** | 0.2437 | 0.0479 to **0.1667** |
| replay | **0.6597** | **0.2361** | 0.2521 | 0.0479 to **0.1667** |

chance 0.2500; the same probe on the untrained body at `e368`'s wider roll reads 0.7617.

| claim | measured | verdict |
|---|---|---|
| Z1 the reconstruction is faithful | the saved head reproduces the artifact's own per-replicate `learned`, **0.0000** apart over **120** replicate-tasks | **MET** |
| Z2 the initial body reproduces the curve's cell | **0.6597** against **0.7617**, **-0.1020** apart | **NULL** |
| Z3 the trained body still carries the cue | **0.2361**, **0.0139 below** chance | **FALSIFIER FIRED** |
| Z4 it carries less than it did | **+0.4236** on a sem of **0.0068** over 60 paired replicate-tasks | **MET** |
| Z5 a probe on the trained body beats the trained head | **-0.0076** on a sem of **0.0065** | **FALSIFIER FIRED** |

## 2. What the two fired claims say

**The body's training removed the cue from the world.** A closed-form probe on the trained body reads **0.2361**,
which is **below** chance, where the same probe on the same examples and the same world **before** training reads
**0.6597**. The loss is **+0.4236**, paired over sixty replicate-tasks at a sem of 0.0068, and it is not a
degradation: Z3 asked whether the trained body reads at least 0.10 above chance and the answer is that it reads
less than chance.

**And nothing readable is left for the head to have missed.** On the body the run actually trained, the probe reads
**0.2361** and the head reads **0.2437** -- a difference of **-0.0076**, unresolved. Z5 is the claim the
readable-but-not-learnable thread had been asking for, and it fires in the direction that closes the thread rather
than continuing it.

**And the world did not go quiet: it got louder and empty.** The world's final state has a spread of **0.0479** on
the initial body and **0.1667** on the trained one, **3.5 times larger**, while the label's recoverability went from
0.6597 to chance. So the training did not leave the world at rest and stop carrying the cue; it drove the drive
population -- and the bias behind it -- into a large state that has nothing to do with the trial. That is the
mechanism `e367` derived for the *untrained* body's rest, arriving here in its other form: at `cue@8` the cue
reaches the world through a single step, and a body that moves its biases fills that step with its own activity
instead.

## 3. What it means

**Every comparison this window has made of "a trained head against a frozen probe" was across two different bodies.**
`e374` read the trained body at chance where a probe on the **untrained** body read 0.7617; `e375` froze the body and
priced the difference at 0.2156; `e376` and `e377` and `e378` all moved the head and read diagonals. This unit is
the first like-for-like measurement in that list, and it says the comparison was not measuring what it looked like
it was measuring: **on the trained body there is no probe-versus-head gap at all.**

**So the head is not the problem at this cell, and neither is the fitting.** The order is the other way round from
what a diagonal reading suggests: the body's training **first** removes the cue from the world, and then the head
reads chance because chance is all there is. That is why `e375`'s frozen body recovers 0.2156 and why `e376`'s
larger step size is worth 0.1965 on a frozen body and `e377` found it worth 0.0104 on a plastic one: **there is
nothing for a better-fitted head to fit.** The one thing this line turned that changes the outcome at this cell is
whether the recurrent weights are allowed to move.

**And it re-reads `e371` and `e372` from the wide end.** Those units found trained bodies reading *above* the frozen
probe at `cue@0` (0.7691 against 0.6602, and 0.8399 against 0.7891) -- also a comparison across two bodies, and in
the opposite direction. So at the wide step the trained body reads **more** than the untrained one does and at the
tight step it reads **nothing** where the untrained one read 0.66, and both of those are statements about the body
and not about the head. Whether a plastic body at `cue@0` carries more cue in its world than the connectome's
initialisation does is the measurement this unit's method makes possible and does not take.

## 4. What it cannot do

*One cell and one draw*: `cue@8` on this draw, with the drive on the agent's own action, at the corpus's own head
and its larger step size. *And Z2's null is a warning about the roll*: the probe on the initial body here reads
**0.6597** where `e368` recorded **0.7617**, because this unit rolls each task's own 96 and 48 examples drawn at
that task's seed while the frozen grid rolled 512 at one draw -- so the two are the same world and not the same
examples, and the comparison is registered as a null rather than pressed into service. *And a probe is not a
decomposition*: it says how much of the label a linear fit can recover from the world's eight numbers and not which
directions moved or when, so a body that has lost the label to a linear fit may still hold it nonlinearly, and
nothing here says whether the loss happened gradually over the 500 iterations or at a particular one.
