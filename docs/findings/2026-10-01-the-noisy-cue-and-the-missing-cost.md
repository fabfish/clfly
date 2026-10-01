# The environment gets a noisy cue, and the middling loop's cost does not come with it

*2026-10-01. Runs: `experiments/e8_rate_network.py --circuit-size 300 --iters 500 --readout-size 32 --repeats 5
--methods naive,ewc-block --closed-loop --loop-symbols 8 --loop-noise 1.0 --loop-scale {0.0, 0.5}` -- 246 s and
283 s, read by `experiments/e329_the_environment_gets_a_noisy_cue.py`.*

## 1. The ceiling three units named

`e325` measured the loop frozen and warned that the cue probed at **1.00** in both loops. `e327` swept the strength
at five replicates and found the ordering rested on **one replicate**. `e328` put the middling setting at **1.92
sigma** on forty replicates and ended on the sentence that ties all three together: *"every replicate learns every
task, so nothing here speaks to acquisition"* -- with deterministic cue patterns a two-symbol task is **two fixed
vectors** in twelve cue neurons, so every arm solves it and the only quantity left to move is whether a replicate
forgot at all.

**This unit adds the missing ingredient.** `CueActionEnv` gained a `noise` field, drawn once per example at step 0
and defaulting to zero so every earlier artifact's path is untouched, and the runner gained `--loop-noise`. The
environment here is **eight cue symbols per task** with **noise 1.0**: a **twenty-four-symbol** world read out from
a 32-neuron linear head over a single-step pulse.

**T1 MET.** Same circuit `mb+cx+al@n952`, same read-out `59926518137c`, the same three task names, five replicates
per arm in both runs, the environment draw identical in every field the strength does not name (`tau` 12, 24
symbols, twelve cue neurons, eight action, twelve feedback, gain 1.0, noise 1.0, and the same three population
fingerprints), and **no unexpected config or environment difference**.

**T2 MET, and this is what the last three units were missing.** `naive` reads **0.5292** against a chance of
**0.125** where the easy environment gave **0.9625**. The task is a measurement now: the arm learns a great deal and
is nowhere near solving it, so an accuracy contrast has room in both directions and a forgetting number is a graded
loss rather than a count of rare events.

**T3 MET.** The middling setting's five-replicate mean forgetting is **0.2354**, against **0.2188** at the open
setting -- an order of magnitude above the easy environment's 0.1297, and graded.

## 2. And the middling loop's cost does not reproduce here

| arm | open accuracy | mid accuracy | Δ | σ | open forgetting | mid forgetting | Δ | σ |
|---|---|---|---|---|---|---|---|---|
| `naive` | 0.5292 | 0.4931 | −0.0361 | **0.92** | 0.2188 | 0.2354 | +0.0167 | 0.29 |
| `ewc-block` | 0.5292 | 0.5417 | **+0.0125** | 0.87 | 0.1958 | 0.1500 | **−0.0458** | 1.44 |

**T4 landed on its NULL**: the registered claim was that the middling setting costs level by at least 0.05, and it
costs **0.0361 at 0.92 sigma** -- the same sign as `e328`'s accuracy observation (0.9625 against 0.9135) and not
resolved. **And the other arm moves the other way**, `ewc-block` reading **+0.0125 higher** under the loop and
forgetting **0.0458 less**, neither resolved either.

**So nothing in this table reproduces `e328`'s effect.** There, on the easy environment, the middling setting
roughly doubled the rate at which replicates forgot anything, at **1.92 sigma** on forty replicates. Here, on the
environment built to give that measurement room, **no arm resolves in either direction and the penalised arm leans
the opposite way.** The honest reading has two candidates and this design does not separate them: the effect is
**not there** on a task with headroom, or five replicates cannot see it -- `e328` needed forty to put a
forget-rate difference at 1.92 sigma, and this unit has five.

## 3. What it says

**The instrument the thread asked for now exists, and it arrived with the effect gone.** Three units ended by
naming a task whose read-out is not saturated as the missing piece; it is here (0.5292 against a chance of 0.125),
it does what it was supposed to do to the numbers (graded forgetting of 0.22 rather than a rare-event count), and
the middling-loop result that `e328` established on the saturated task does not appear in it.

**That is the shape of a caveat that mattered.** `e328`'s finding recorded that the task was at ceiling and said
what it cost -- only retention was in play. This unit is the first evidence about what that cost *was*: on the task
with room, the retention effect is not visible at five replicates, and the one arm that moves is the one with a
penalty.

**And the noise and the alphabet moved together.** Eight symbols per task and a noise of 1.0 arrived in one change,
so which of them produced the headroom -- the class geometry, the noisy cue, or both -- is not separated, and the
noise is on the **cue** only: the environment's action channel is noiseless and deterministic.

## 4. What it cannot do

**Five replicates**, where `e328` needed forty to resolve a rate difference: T4's null is a null and not an
absence, and the honest statement is that the accuracy cost is **0.0361 plus or minus 0.039**. *Two settings, one
noise level, one alphabet and one cue width*: none of the four is swept, and the alphabet and the noise arrived
together. *Two arms*: `replay` and `ewc-block-rand` are not run, so whether the leaning of `ewc-block` is its
penalty is not something this pair can say. *The cue is noisy and the world is not*: what this measures is a noisy
measurement, not a stochastic environment. *And there is still no reward*: the label is the cue, delivered at step
0, and the agent's action is an input rather than a decision.
