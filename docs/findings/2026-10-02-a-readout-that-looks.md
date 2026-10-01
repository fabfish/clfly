# A read-out that looks: 117% of the state moves and the decoder does not notice

*2026-10-02. Nothing trains: `experiments/e343_a_readout_that_looks.py` rolls the frozen connectome network on one
two-symbol task under both loops at four strengths and fits four decoders at each. Minutes. Writes
`runs/e343_a_readout_that_looks.json`.*

## 1. The instrument `e342` asked for

`e342` measured the dissociation across an eight-fold range of feedback strength: at `scale = 4.0` the frozen
network's closed and open trajectories differ by **85.05% of the peak state** and **19.83%** of it on the decoder's
own 32 neurons, while a body trained in that world reads its tasks exactly as well with the world switched off, by
**+0.0028 at 0.78 sigma**. And its own "what it cannot do" named the gap: that was measured **on accuracy**, which
is a decoder fitted *and* read inside one loop, so it cannot say whether the invariance lives in the divergence being
orthogonal to the task or in the read-out being insensitive to a divergence that is not.

**This unit separates the two by the cheapest possible instrument: fit the decoder inside one loop and read it
inside the other.** If the divergence lies anywhere the labels are separable along, a decoder fitted closed and read
open must lose accuracy. If it reads the same, the divergence is in directions the task does not use.

**T1 MET.** One configuration across the four strengths -- the same circuit `mb+cx+al@n952`, the same read-out draw,
the same 96 train and 96 test examples, one world with `leak = 0.35` and two modes, and the same peak state at every
strength.

**T2 MET, and the positive control is larger than `e342`'s.** At `scale = 4.0` the two rolls differ by **1.1445**,
which is **116.83% of the peak state** -- and **61.49%** of it on the decoder's own neurons. (Larger than `e342`'s
85% and 19.83% because the task here is two-symbol rather than twenty-four-way, so the same channel moves a state
that is doing less.)

## 2. And the decoder crosses the loops without noticing

| strength | divergence, of peak | on the decoder's own neurons | within-loop accuracy | cross-loop accuracy | worst gap |
|---|---|---|---|---|---|
| 0.5 | 28.31% | 10.64% | 0.9479 | 0.9479 | **0.0000** |
| 1.0 | 52.94% | 19.12% | 0.9479 | 0.9479 | **0.0000** |
| 2.0 | 86.81% | 30.66% | 0.9479 | 0.9479 | **0.0104** |
| 4.0 | **116.83%** | **61.49%** | 0.9375 / 0.9479 | 0.9479 / 0.9375 | **0.0104** |

**T3 MET**: the worst cross-loop gap is **0.0104** at every strength -- **one held-out decision in 96** -- against a
falsifier at 0.10. **T4 MET**: the gap grows from **0.0000** at `scale = 0.5` to **0.0104** at `scale = 4.0`, and the
registration allowed 0.10.

**So the answer to `e342`'s question is the first of its two branches: the divergence is orthogonal to the task.**
At the strongest channel the two loops put the state **61% of the peak apart on the very neurons the decoder reads**,
and a decoder fitted in one loop reads the label out of the other **one decision worse in 96**. There is nothing for
a better read-out to see: a read-out that "looks harder" would have to read a direction the labels are not along.

**And `e342`'s latch hypothesis is left standing on its own.** Its finding wrote that a channel which helps the state
hold what a task requires would show up as divergence in the state **and** invariance in accuracy, because the two
are one mechanism seen from two sides. This unit shows the invariance is not a read-out's blindness -- and does not
show it is a latch's help, which remains the one account in this chain that predicts the invariance rather than
explaining it away.

## 3. What it says

**The closed loop is a change of coordinates and not of task.** A world whose next input is the agent's last action
moves the state further than the state's own peak and leaves the label on the same side of every decision boundary
the decoder draws. That is why five units of cross-configuration measurements kept returning nothing: the quantity
they were measuring -- what a trained body reads -- is a function of the task's directions, and the channel writes in
the others.

**And it reframes what the loop is for.** A benchmark built on this channel cannot expect it to show up in accuracy
at all; what it changes is the state, so the unit that would test it has to read something about the state -- its
drift, its dimensionality, or how much of a task's information it holds. `e342`'s T4 and this unit's T2 are that kind
of measurement, and they are the only ones in this chain that resolve.

**What is untouched is everything measured within a run**: `e331`'s ordering, `e328`'s within-stream rates and
`e325`'s frozen divergence are measurements of arms inside one sample or of the state, and this unit agrees with all
of them.

## 4. What it cannot do

**The network is frozen**, so this is the substrate's insensitivity and not a trained model's -- `e342`'s trained
bodies are the evidence for those, and nothing here says a trained decoder would behave the same. *The probe is
linear*, fitted by least squares with a fixed ridge, which is the weakest decoder the task admits; a non-linear one
might see a divergence this does not, and that is the natural next instrument. *One task, one read-out draw and one
circuit*: the read-out is the corpus's 32-neuron draw, and whether a wider or narrower one would see it is `e286`'s
axis and not this unit's. *The divergence is a maximum over neurons and steps*, not a norm and not a projection, so
it says how far the farthest neuron moves and not how much of the state is engaged. *And the two loops see the same
examples*: the cross-loop decoder is tested on the same inputs under the other loop, so this is insensitivity to the
channel and not generalisation across data. **Two symbols**: the task is two-way because a frozen linear probe on
this read-out is at chance on a twenty-four-way one, and a probe at chance cannot be compared with anything.
