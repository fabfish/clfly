# The same body asked both questions: the channel moves nothing

*2026-10-02. Run: `experiments/e8_rate_network.py --circuit-size 300 --iters 500 --readout-size 32 --repeats 5
--methods replay --closed-loop --loop-symbols 8 --loop-noise 1.0 --loop-scale 1.0 --loop-world-modes 2
--loop-world-leak 0.35` -- one run, 144 s, read by `experiments/e338_the_same_body_asked_both_questions.py`.*

## 1. Removing the redraw instead of sampling it

`e333` measured `replay`'s retention rising **0.0375 at 2.45 sigma** under a world with a transition rule. `e337` ran
the same two worlds on a second seed stream and found it **reversed: 0.0771 the other way at 3.36 sigma**. Both
resolved, both the same manipulation -- so the **redraw dominates** every unpaired measurement of it.

**The way to remove a redraw is a pairing, and this unit builds the cheapest one there is: ask the *same* body both
questions.** `run_method` now keeps the **unwrapped** module alongside the loop-wrapped one, and at the end of a
replicate it reads every task's final accuracy **twice on that one trained body** -- once through the loop and once
with it unwired. The body, the heads, the seed and the trajectory are shared by construction, so the difference
carries no model-to-model variation at all.

One run, `replay`, five replicates, on the **carried** world.

**T1 MET.** Same circuit `mb+cx+al@n952`, same read-out `59926518137c`, the same three task names, five replicates
each carrying both numbers for all three tasks.

## 2. And the difference is nil

| replicate | with the loop | without it | Δ |
|---|---|---|---|
| 0 | 0.375 0.667 0.729 | 0.375 0.667 0.729 | **+0.0000** |
| 1 | 0.438 0.521 0.625 | 0.438 0.542 0.625 | **−0.0069** |
| 2 | 0.542 0.604 0.667 | 0.542 0.604 **0.646** | **+0.0069** |
| 3 | 0.500 0.729 0.771 | 0.500 0.729 0.771 | **+0.0000** |
| 4 | 0.542 0.688 0.667 | 0.542 0.688 0.667 | **+0.0000** |

**T2's falsifier FIRED.** The paired difference is **+0.0000 on a sem of 0.0022** -- **0.00 sigma**. **T3's fired
too**, and for a reason worth reading: three of the five replicates are **exactly zero** and the two that are not
lean **opposite ways**, so the claim that all five share a sign is not merely unmet, it is unmet because the
quantity is mostly zero.

**And both non-zero differences are one decision.** 0.0069 is **1/144** -- the evaluation is 144 held-out decisions
per replicate, so the largest effect the world's channel has on a trained body's accuracy, anywhere in this table,
is **a single decision**.

**T4 MET, and it is the unit's conclusion.** A fixed body moves **0.0000** where the two unpaired redraws gave
**+0.0375** and **−0.0771**. So those two numbers are **not the channel's effect**: they are the variation between
models, and the channel's own effect on a trained body is nil to within one decision in 144.

## 3. What it says

**The thread's headline effect is the redraw's and not the world's, and this unit says so directly rather than by
inference.** `e333`'s 2.45 sigma and `e337`'s 3.36 sigma are both real statements about the pairs of runs they
measured, and neither is a statement about what the world's channel does -- which this unit can now say because it
took the model-to-model variation out and the effect went with it.

**And the five units before it are reframed by one number.** `e334` to `e337` spent themselves excluding mechanisms
for that effect: the stored features fitting worse, the buffer's contents, the drift's size, the update's direction.
All four exclusions stand as measurements. But there was **no effect of the channel to explain** -- the quantity they
were accounting for was a difference between two models, and each of them measured it on the same single stream.

**What this does not touch is the rest of the loop's record.** `e325`'s frozen divergence (52% of the peak state) and
`e331`'s ordering (4.4 to 7.6 sigma, arm against arm within a stream) are untouched: they are measurements of the
loop's effect on a **state** or of arms **within** one sample, and neither is the kind of quantity this unit found to
be a redraw. The lesson is narrow and it is worth stating narrowly: **a manipulation applied to two separately
trained models, at five replicates, on this task, is a coin.**

## 4. What it cannot do

**One direction only**: the body was trained **under** the carried channel and then read both ways, so this is what
*removing* that channel does to a model that learned with it; a body trained unwired and read with the loop on is
not run, so the two directions are not compared and a body adapted to the channel could differ from one that never
saw it. *One arm*: `naive`, `ewc` and the block arms are not read. *Accuracy is not retention*: this reads each
task's **final** accuracy, so a body that lost task 0 would show it, but the decomposition into a learning term and
a retention term is not computed and `e333`'s quantity was `mean_forgetting`. *Three tasks and five replicates*:
fifteen paired numbers that are not independent -- three tasks share a body and a head -- so the sem is the
across-replicate one and the task variation inside a replicate is averaged and not modelled. *And a nil effect here
is a nil effect at this channel strength, this task and this read-out*: the feedback is `scale = 1.0` and the world
is `leak = 0.35`, and nothing in this unit says a different channel would also move nothing.

## 5. The artifact this unit writes is a reading and not a result

`e309`'s conformance contract counts eleven fields in every artifact, and the first version of this unit's artifact
carried **two** of them -- a `config` and an `env`, copied from the run it summarises. That made it read as a
**run that failed the contract**, and `e309`'s K4 fired: *"no artifact carries between two and four of the eight
fields"* was falsified by one artifact, this one, at exactly two.

**The artifact is a reading, so the fields are renamed rather than the claim re-based**: `config` became
`run_settings` and `env` became `environment_draw`, and the artifact now carries **zero** of the contract's eleven --
the same as every other reader artifact in this corpus. The distinction matters more than the rename: a *subset* of a
run's config under the name `config` is a result-shaped record that would fail a result's contract, and the corpus's
audits are right to count it as one. `e309`'s K4 is MET again, for the reason it was written for: the record comes in
blocks and not in degrees.

**And the same unit's artifact carried a top-level `tasks` key** -- a list of **task-name strings** where the runner
puts a list of **task-summary dicts**, which is the name `e187` reads from every artifact. It crashed that reader
(`'str' object has no attribute 'get'`) and it is the second time in two units: `e334`'s first artifact did exactly
this with a list of indices. The key is gone; the per-replicate task names live inside the rows where they belong.
