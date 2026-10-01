# The latch hypothesis: the loop helps at 94% accuracy, at 78%, and at 51% -- at none of them

*2026-10-02. `experiments/e344_the_latch_hypothesis.py` reads three closed-loop runs of the `e8` runner, differing
only in the step the cue is delivered at (`--loop-cue-at` 0, 11 and 10). Training only. Writes
`runs/e344_the_latch_hypothesis.json`, from `runs/e344_cue_memory.json`, `runs/e344_cue_none.json` and
`runs/e344_cue_near.json`.*

## 1. The one explanation left standing

`e343` closed the read-out's escape: a decoder fitted inside one loop and read inside the other loses **one
decision in ninety-six** while the state moves by **117% of the peak**, so the loop's divergence is in directions the
task does not use. That left the **latch**: the loop is a self-exciting memory, its state keeps whatever the task
needs kept, and that is why the state moves and the answer does not.

**The latch makes a prediction nobody had tested.** If the channel works by holding the cue across the gap, it
should help exactly when something must be held. The world `clfly` builds is already *a delayed report of a cue that
is gone*: the cue arrives at **step 0** and the read-out happens at the **last step**. Move that cue one integer
later and the trial stops needing memory -- and the prediction becomes a difference between two numbers.

## 2. Three conditions, one integer apart

The same run three times at feedback strength 1.0 and five replicates, identical in every field the runs record
except `cue_at`: **0** (hold across eleven steps), **11** (the cue on the drive at the step the decoder reads), and
**10** (one recurrent step from the read-out -- added after the third section below, with its claim registered
before its artifact was read). Each condition is read with `e338`'s **paired channel** instrument: every task's final
accuracy is taken twice on the *one body the replicate trained*, once through the loop and once with it unwired, so
the difference is the channel's effect on a fixed model rather than a difference between two models.

**T1 MET.** One configuration: the same circuit `mb+cx+al@n952`, the same read-out draw `59926518137c`, the same
three tasks and 96 train and 48 test examples each, the same seeds, the same world `leak = 0.35` with two modes, the
same cue, action and feedback populations, the same settings -- and `cue_at` = 0, 11, 10.

## 3. The answer

| condition | cue at step | loop-on accuracy | paired difference | sem | sigma |
|---|---|---|---|---|---|
| memory | 0 | **0.9389** | **-0.0014** | 0.0014 | 1.00 |
| late cue | 11 | 0.5069 | **+0.0000** | 0.0000 | inf |
| near cue | 10 | **0.7778** | **+0.0000** | 0.0000 | inf |

chance 0.500 (two classes). **T2 FALSIFIER FIRED.** Where the cue must be held for eleven steps the channel does
not help: **-0.0014 at 1.00 sigma**, and the sign is the wrong way. Its five per-replicate means are
`[0.0000, -0.0069, 0.0000, 0.0000, 0.0000]` -- fourteen of the fifteen task readings are **exactly identical** with
the world wired and unwired, and the fifteenth is **one held-out decision in 144**. **T5 MET.** The corrected
control is a real task -- the cue one step from the read-out is read at **0.7778** against a chance of 0.500, more
than 0.10 above it -- and the channel's paired effect on it is **+0.0000**, identical in all fifteen readings.

**So the latch is dead, and it died twice.** With eleven steps of memory the effect is negative and a hundredth of a
point; with one step it is exactly zero; with none it is exactly zero. The channel's help does not depend on whether
memory is needed, because at this strength, in this world and on this body architecture, there is no help to depend
on anything. What `e342` and `e343` found standing was an account that **predicts** the state divergence while the
accuracy stays put; this unit measured the prediction and the accuracy did not move even when it should have.

## 4. The cue at the read step cannot be read -- a mechanism, not a task

**T3 MET, and its own verdict says why it is not evidence.** The `cue_at = 11` run is at **0.5069**, which is
chance, so its zero paired difference is a floor. The reason is mechanical and worth keeping: the environment adds
the cue to the step's **drive** and only on `cue_neurons`, the read-out is a fixed 32-neuron draw of the circuit, and
the connectome weights are what carry activity from one neuron to another. So the cue's effect reaches the read-out's
own neurons **one recurrent step after it is injected**, and a cue injected on the step that is read never gets
there. **`cue_at = 10` is therefore the tightest no-memory control this world admits**, and it is the one T5 uses --
learnable at 0.7778, and still not helped.

**T4 FALSIFIER FIRED, with the caveat its own name now carries.** The registered comparison `0` against `11` gives
**-0.0014**, under the 0.01 that fires. That verdict's stated reading, "the help does not depend on memory", is not
what this pair shows on its own, because the second condition is a floor; T5 is the valid comparison and it says the
same thing on a task that is at 0.7778.

## 5. What it cannot do, and what is next

*Five replicates and three tasks* give fifteen paired numbers that share a body and a head, so the sigma is the
across-replicate spread of a per-replicate mean and not fifteen independent draws -- but the invariance is not a
resolution failure: fourteen of fifteen readings are *bit-identical* across the two loops, which is a stronger
statement than any sigma. *One strength, one world, one architecture*: `scale = 1.0`, `leak = 0.35`, two symbols per
task, and the corpus's 32-neuron read-out; `e342` measured the answer not moving across an eight-fold range of
strength, but not with the cue moved. *The trial still has eleven recurrent steps in every condition*, so these
conditions differ in how much recurrence is asked for as well as how much holding is asked for, and a cue at step 10
is one step of margin and not a memory-free trial in the strict sense.

**What is left of the loop, given that it changes neither the answer nor anything the answer is read along, is the
state itself.** The chain's two resolving measurements -- `e342`'s frozen divergence and `e343`'s cross-loop decoder
-- both read the state, and every measurement that reads the answer has failed to see the channel. That is the shape
of a channel that is real in the dynamics and absent from the task, and the open unit it points at is the one the
runner already half-supports: **a label the agent has to earn rather than be given**, so that the loop is load
bearing for a reason the current read-out cannot supply.
