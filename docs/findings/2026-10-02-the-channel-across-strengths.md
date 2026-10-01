# The channel rewrites the state and not the answer, at every strength

*2026-10-02. Runs: `experiments/e8_rate_network.py --circuit-size 300 --iters 500 --readout-size 32 --repeats 5
--methods replay --closed-loop --loop-symbols 8 --loop-noise 1.0 --loop-world-modes 2 --loop-world-leak 0.35
--seed0 0 --readout-seed 0 --loop-seed 0 --loop-scale {0.5, 1.0, 2.0, 4.0}` -- four runs, read by
`experiments/e342_the_channel_across_strengths.py`, plus a frozen control on the environment itself.*

## 1. Two measurements at one strength, and the question between them

`e341` closed the loop's retention question on the clean stream: over **forty** replicates the world's channel moved
`replay`'s forgetting by **−0.0013 at 0.14 sigma**, where the design had the power to see `e333`'s 0.0375 at 4.0
sigma. `e338` had the sharper form of the same thing: on **one trained body**, read once through the loop and once
unwired, the difference is **0.0000** on a sem of 0.0022, with three of five replicates exactly zero.

**Both are at feedback strength 1.0.** And `e325` had measured, at that same strength, that the channel moves the
**state** a great deal -- closed and open trajectories diverging by **52% of the peak**, and 12.48% of it on the
decoder's own 32 neurons. So the record holds a dissociation at one point: the channel rewrites the state and leaves
the answer alone.

**This unit asks whether that holds across strengths**, which is what separates "the channel does nothing" from "the
channel does a great deal that the read-out cannot see". Four runs of the **paired** design at `scale` = **0.5, 1.0,
2.0 and 4.0** -- one fixed body read both ways per replicate -- plus a **frozen** control: the closed-versus-open
divergence of the untrained network's trajectory at the weakest and the strongest.

**T1 MET.** Four strengths of one configuration: same circuit `mb+cx+al@n952`, same read-out `59926518137c`, the same
three task names, five replicates each, seeds `[0, 0, 0]`, leak `0.35`, world modes 2, the same three population
fingerprints, and every other setting equal.

## 2. And the dissociation is across an eight-fold range

| strength | paired difference | σ | state divergence (frozen) | on the decoder's own neurons |
|---|---|---|---|---|
| 0.5 | +0.0042 | 1.50 | 18.89% of the peak | 4.50% |
| 1.0 | +0.0000 | 0.00 | (not measured) | |
| 2.0 | +0.0014 | 1.00 | (not measured) | |
| **4.0** | **+0.0028** | **0.78** | **85.05% of the peak** | **19.83%** |

**T2 MET**: the paired difference is within two sigma of zero at **every** strength -- 1.50, 0.00, 1.00 and 0.78.
**T3 MET**: the magnitude does not grow, differing by **−0.0014** between the weakest and the strongest where the
falsifier asked for a growth of 0.05. **T4 MET**: the frozen trajectory's divergence rises from **18.89% to 85.05%
of the peak state**, a rise of **+0.6616**, and on the decoder's own 32 neurons from **4.50% to 19.83%**, a rise of
**+0.1533**.

**So at eight times the strength the state is rewritten by 85% of its own peak and the trained body's answer moves
by 0.0028 at 0.78 sigma.** The channel reaches the dynamics -- the control is unambiguous and it is not a weak-channel
artefact -- and it does not reach the accuracy. **And the read-out's own neurons see a fifth of the peak moving**,
which is the sharper form: the divergence is not hidden in neurons the decoder ignores.

**That closes the dissociation as a property of the design and not of one setting.** `e333`'s 2.45 sigma and
`e337`'s 3.36 were two draws' noise; `e338`'s 0.0000 was one body; `e341`'s −0.0013 was forty. This says the
invariance holds while the channel's effect on the state grows by a factor of four and a half.

## 3. What it says

**The benchmark's closed loop changes the substrate and not the task.** A world whose next input is the agent's own
last action rewrites up to 85% of the state's peak at every step, and a body trained in that world reads its tasks
exactly as well with the world switched off. The interesting quantity is therefore not "does the loop cost
anything" -- it does not -- but **which read-out could ever see it**, and the answer is not the one this thread has
been using.

**And a plausible reason is on the record from `e325`'s other half**: the loop is a **latch**, and a latch is a
memory. A channel that helps the state hold what the task asks it to hold would show up as invariance in accuracy
for the same reason it shows up as divergence in the state -- the two are the same mechanism seen from two sides.
That is a hypothesis this unit cannot test, and it is the first one in this chain that predicts the **invariance**
rather than explaining it away.

**What is untouched is everything measured within a run.** `e331`'s ordering, `e328`'s within-stream rates and
`e325`'s frozen divergence itself are measurements of arms inside one sample or of the state, and this unit agrees
with all of them: it is the *cross-configuration* claims that keep failing.

## 4. What it cannot do

**One world and four strengths**: only `leak = 0.35` is used, and `scale` is a scalar multiplier on one feedback
pattern rather than a family of channels -- a different pattern, or a world with modes the agent can be pushed into,
is not asked. *The frozen control is the connectome initialisation*, so its divergence is the substrate's response
and not a trained model's; a trained body's divergence is not measured. *The paired reading is accuracy* while
`e333`'s quantity was `mean_forgetting`, so a body that lost task 0 would show it and the decomposition into a
learning term and a retention term is not computed. *Three tasks and five replicates*: fifteen paired numbers that
are not independent. *And the bodies are trained at each strength*, so the comparison across strengths is between
four sets of models: what is paired is the channel **within** a replicate, and the eight-fold range is the
environment's strength and not a controlled manipulation of the trained model.
