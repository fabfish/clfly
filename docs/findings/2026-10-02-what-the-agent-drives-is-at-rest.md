# What the agent drives is at rest: the trained closed loop is bit-identical to the read-step run, and the world's own recorded spread says why

*2026-10-02. `experiments/e367_the_world_the_agent_drives.py` trains the one cell of `e363`'s grid no run had
trained -- the closed loop whose world listens to the agent's **own action population**, with the cue one step from
the read-out -- and reads it against `e365`'s cue-source run at the same step and `e362`'s action-source run at the
read step. The run is `runs/e367_earned_label_cue10_actionsource_20reps.json`, twenty replicates, two arms,
eighteen minutes; the reader is `runs/e367_the_world_the_agent_drives.json`. Five claims, registered before the
run's reading was opened.*

## 1. The result, in one line

**The closed loop is empty, not weak.** The trained action-source body at `cue@10` reads **0.2361**, which is
**0.0139 below** a chance of 0.25, and its per-replicate record is **bit-identical** to `e362`'s action-source run at
the read step -- all twenty replicates, both arms -- which is what a task whose read-out does not depend on the cue
at all looks like. **T3 fired and T5 fired**: the agent did not build the channel.

## 2. The five claims

| | claim | measured | verdict |
|---|---|---|---|
| T1 | one configuration except where the drive is read | every recorded field equal to the read-step run's with the cue's step the only difference; against the cue-source run the seven fields the drive's source moves, and nothing else | **MET** |
| T2 | the frozen floor of this cell is chance | `e363`'s `action@10` is **0.2578**, **+0.0078** above chance | **MET** |
| T3 | the agent can build the channel | trained `naive` diagonal **0.2361**, **-0.0139** above chance | **FALSIFIER FIRED** |
| T4 | being handed the channel beats building it | cue source **0.5337** against the closed loop's **0.2361**, **+0.2976** on a sem of **0.0156** (**19.04 sigma**) paired | **MET** |
| T5 | the answer is earned in the closed loop | `naive` **+0.0010** at **0.16 sigma**, `replay` **-0.0028** at **0.31 sigma** | **FALSIFIER FIRED** |

**T1's seven fields are the whole of the manipulation.** The drive's source moves the action population itself
(`action_sha1`, `n_action`), and after it in the environment's own draw the drive map, the read map and the coupling
matrix. Everything else -- the cue and feedback populations, the circuit, the tasks and their read-out widths, the
basis, the seed stream, the replicate count -- agrees across all three runs. The action-source runs share the
coupling fingerprint `5326f4a0edb4`; the cue-source run is `1b7d09f2b469`. This is the pair `e364`'s T1 **fired** on;
here it is registered as expected before the run, so the check is about everything else.

## 3. What the reader found that the claims did not ask for

**The trained run and the read-step run are the same numbers.** Not close: equal. Both arms' twenty replicates
compare equal field by field, and the two artifacts differ in `timing_s` and in the cue's step and nowhere else.
`e363`'s frozen grid put the two cells **0.0000** apart as well. Six cells of one world, four of them now trained,
and the cue's step is worth nothing to the action source at either of the two late steps.

**And the corpus already held the number that says why.** `e363` recorded `world_sd` for every cell, the standard
deviation of the world's final state, and for the action source at both late steps it is **exactly 0.0**:

| source | cue step | accuracy | `world_sd` |
|---|---|---|---|
| action | 0 | 0.6602 | 0.2029 |
| action | 10 | 0.2578 | **0.0** |
| action | 11 | 0.2578 | **0.0** |
| cue | 0 | 0.7891 | 0.2156 |
| cue | 10 | 0.8555 | 0.0719 |
| cue | 11 | 0.2578 | **0.0** |

**A read-out with no spread cannot be decoded, by anything.** The two "chance" cells of the action source are not a
floor a body failed to clear; they are a constant, and 0.2578 is what a decoder on a constant reads. The trained run
does not change that, and it **cannot**: the trained diagonal is the same function of the same constant.

**The account, and it is exact rather than statistical.** `fn(x, t)` gives the world the state *before* step `t`'s
update. The trial starts at rest and the only input before step 10 is nothing, so the state stays at rest through
step 9. At step 10 the cue is written on the cue population, so the state entering step 11 is nonzero on the cue
population and **zero everywhere else** -- the action population's input at step 10 is `W @ x_10`, and `x_10` is the
zero vector, so `x_11[action] = 0` **whatever the weights are**. The world's drive at step 11 is
`tanh(x_11[action]) = 0`, so `w_11 = 0.65 * w_10 + 0.35 * 0 = 0`. Every drive before step 11 is zero by the same
induction, so the world's final state is zero, the read-out is a constant, and the training is the *same
optimisation* wherever the cue sits -- which is why the two trained runs are bit-identical and not merely close.
**Training cannot touch this**, because the quantity training would have to move is zero for every setting of the
weights it is allowed to choose. It is not an interface the body fails to exploit; it is an empty read-out.

**This is reported and not claimed.** It was read *after* the five claims above were registered, so it is a
measurement and not a registration, and the unit that would establish it is named below. The reproduction is one
roll of the frozen net, recorded here rather than asserted: with `drive_from_cue=False`, `cue_at` 10 and 11 give
`last_world` identical to the last digit and `abs().max()` equal to **0.0**, while the two input arrays differ by
**3.96** at their largest entry; with the cue source the same comparison moves the world by **0.1876**.

## 4. What it means

**`e363`'s T5 and `e364`'s headline both get their mechanism, and it is not the one they implied.** `e363` read
*"the timing is the hard limit"* with one step of margin costing the action source everything, and `e364` read
*"training cannot beat the interface"* from a body free to do anything. Both are right about the reading and neither
said what the reading was of: in the action-source cells at steps 10 and 11 the world is **at rest**, so the
measurement is of an empty channel and not of an expensive one. The distinction matters for what a game can ask: a
body that fails on a weak channel is a body to train harder; a body facing a channel that is identically zero at the
step it is read has nothing to train against, and the fix is in the timing and not in the optimiser.

**And the interface stays the interface.** T4 is the sharpest number this unit has: with everything else equal, the
world listening to the cue population reads **0.5337** trained where the world listening to the agent's own action
reads **0.2361** -- **19.04 sigma** paired -- so at one step of margin the wiring decides whether the task exists at
all. `e365`'s cue-source cell is a working task; this cell is an empty one; the difference is which population the
world listens to and nothing else in the configuration.

**The eleven-step cell says the channel is real, in time.** `action@0` frozen reads **0.6602** with a world spread of
**0.2029**, so the agent's own action does carry the cue to the world once it has eleven steps to carry it. What the
action source lacks at step 10 is not a channel but the **time** to fill it, and the one step it has is provably not
enough for the population the world reads.

## 5. What it cannot do

*One cell*: the action source at `cue@10`, so the trained grid is four of `e363`'s six cells and the two untrained
ones are `cue@0` and `action@0`. *One world and one coupling*: eight dimensions at `leak = 0.35` with `e359`'s
matrix, and the action source's own draw rather than the cue source's. *And the mechanism above is reported, not
established*: the induction that puts the action population at rest at the step the world reads is an argument from
the module's arithmetic, checked against two frozen cells with zero spread and one pair of bit-identical trained
runs, and it is the unit this one points at -- the measurement that would establish it is a registered claim about
`world_sd` across the sources and the steps, with the falsifier being any cell of the action source whose world has
spread at a late step. *And T4 is a between-artifact pairing*: `e367`'s run and `e365`'s share the recorded seed
stream and the read-out draw, which is what makes the pairing legitimate, but they are two files and two coupling
matrices and not one run of two arms.
