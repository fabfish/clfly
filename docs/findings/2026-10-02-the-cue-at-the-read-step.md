# The cue at the read step: the world read-out has the same one-step limit, and the registered prediction was wrong

*2026-10-02. One runner invocation -- `e359`'s exact flags with `--loop-cue-at 11`, `--methods naive,replay`,
`--repeats 20` -- into `runs/e362_earned_label_latecue_20reps.json`, paired against `e359`'s cue-at-zero world at the
same seeds and the same coupling draw. Nineteen minutes. Read by
`experiments/e362_the_cue_at_the_read_step.py`.*

## 1. What this unit predicted, and why it seemed safe

`e344` mapped the **state** read-out's one-step limit exactly: a cue delivered at the step the decoder reads is
**invisible** -- that run came back at chance, 0.5069 -- because the environment writes the cue onto `cue_neurons`
and the connectome's weights carry it to the decoder's own neurons only one recurrent step later.

**The world read-out looks like it should not have that limit.** The head reads the environment's own state, the
world's drive is a function of the state at the step it is read, and the cue at that step is in the state. So the
prediction was that a cue at the read step is **readable**, and that a task whose cue arrives there needs nothing
held and is therefore **easier** -- a resolution the recent runs' nulls made attractive.

## 2. The answer: the prediction is false

| cue at step | arm | final accuracy | diagonal | `mean_forgetting` | paired channel | sigma |
|---|---|---|---|---|---|---|
| 0 | `naive` | 0.5191 | **0.7691** | 0.3750 | +0.2642 | 18.08 |
| 0 | `replay` | 0.6785 | 0.7389 | 0.0906 | +0.4247 | 31.65 |
| **11** | `naive` | 0.2514 | **0.2361** | -0.0229 | **+0.0010** | 0.16 |
| **11** | `replay` | 0.2483 | **0.2375** | -0.0161 | **-0.0028** | 0.31 |

chance 0.2500. **T1 MET**: one configuration except the cue's step -- coupling `5326f4a0edb4` on both sides, world
read `3a7ba76b3619`, cue steps `[0, 11]`, and no other field differing.

**T2 FALSIFIER FIRED.** The late-cue `naive` diagonal is **0.2361 -- 0.0139 *below* chance**. **T3 FALSIFIER
FIRED.** Its paired channel reading is **+0.0010 at 0.16 sigma** and `replay`'s is **-0.0028**: the answer is not
earned because there is nothing to earn. **T4 FALSIFIER FIRED, and hard**: the late cue is **0.5330 *harder* at
47.90 sigma**, not 0.05 easier. **T5 NULL**: with nothing to learn, the buffer does nothing either.

## 3. Why, and what it means for the two lines

**The world's drive is one step behind the input too, for a reason of the same shape.** The environment reads its
action off `action_neurons` and delivers the cue onto `cue_neurons`, two disjoint populations, and the read-out's
columns are `feedback_neurons`, a third. So the cue written into the input at step 11 is in the state at step 11 on
the cue neurons and nowhere else, while the world's drive at step 11 is computed from the state **carried into** that
step, which has not seen the cue. **Nothing about the cue reaches the world's state at the step the world is read**,
which is exactly `e344`'s limit with the populations renamed.

**So the one-step limit is a property of the environment's interface and not of a read-out.** `e344` found it for the
32-neuron decoder reading the state; this finds it for a decoder reading the environment; `e349`'s whole line exists
because a read-out can be moved into the environment, and this says what does not move with it. The two units now
disagree with nothing: the cue is delivered to one population, every read-out reads another, and the weights are what
carry it across -- **one step, always.**

**And the registration did its job.** This unit was written with a prediction the corpus's own record made plausible,
and the prediction was wrong in the sharpest way available: the manipulation did not merely fail to help, it took the
suite to chance and the channel reading to zero. What is left standing is the negative result with its mechanism,
which is what the unit is worth.

## 4. What it cannot do

*One late step and one early step*: `cue_at` 11 against 0, with 1 to 10 unrun -- and the interesting middle is where
the body has *some* time to write into the world, which is the region `e344` walked on the state read-out and this
unit does not walk here. *The reference is a different artifact*, paired by the recorded fingerprints and the
per-replicate seed stream. *One world and one coupling*: `e359`'s own matrix at `leak = 0.35`, so nothing here says
whether a world with a different drive map -- one that read the cue's own population, for instance -- would have the
limit. *And the late-cue arms are at chance*, so their forgetting and their buffer value are measurements of a task
that was never learned and are not evidence about either.
