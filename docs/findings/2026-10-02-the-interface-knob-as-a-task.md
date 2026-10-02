# The interface knob is a working task, and training reads less of it than a frozen probe

*2026-10-02. One runner invocation -- `e364`'s exact flags with `--loop-cue-at 10`, `--methods naive,replay`,
`--repeats 20` -- into `runs/e365_earned_label_cue10_cuesource_20reps.json`, paired against `e364`'s cue-source run
at the read step and against `e363`'s frozen cell for this configuration. Nineteen minutes. Read by
`experiments/e365_the_interface_knob_as_a_task.py`.*

## 1. The cell `e363` and `e364` left open

`e363`'s frozen grid found the knob and read it: a world whose drive listens to the cue's own neurons reads a cue
**one step old** at **0.8555** against **0.2578** for a world listening to the action population, while both read
chance at the step the world is read. `e364` trained that last cell and found training cannot beat the interface
(**0.2326**, below chance). Both closed on the same missing piece: *the trained version of the `cue@10` cell*, the
one where the probe saw signal.

## 2. The answer

| cue at step | arm | final accuracy | diagonal | `mean_forgetting` | paired channel | sigma |
|---|---|---|---|---|---|---|
| 11 (the read step) | `naive` | 0.2531 | 0.2326 | -0.0307 | +0.0083 | 0.83 |
| 11 (the read step) | `replay` | 0.2517 | 0.2410 | -0.0161 | +0.0059 | 0.49 |
| **10** | `naive` | 0.4722 | **0.5337** | 0.0922 | **+0.2236** | **9.93** |
| **10** | `replay` | 0.4625 | 0.5062 | 0.0656 | **+0.2135** | **14.01** |

chance 0.2500. **T1 MET, and this is the cleanest pairing in the line**: both runs are cue-source, so their drive
maps have the same width, the draws align, and the **coupling fingerprints are identical** (`1b7d09f2b469`) -- no
field differs but the cue's step, which is what `e364` could not manage.

**T2 MET: the knob is a working task.** Trained, the cue-one-step-old cue-source world reads **0.5337, +0.2837 above
chance**. **T3 MET**: and the answer is **earned** there, at **+0.2236 (9.93 sigma)** and **+0.2135 (14.01 sigma)**
-- so the knob `e363` found in a frozen roll is a task a body can learn, which is the positive result `e364` did not
have.

**T4 FALSIFIER FIRED, and it is the interesting number: the trained body reads *less* than the frozen probe.**
`naive`'s diagonal is **0.5337** where `e363`'s probe read the same cell at **0.8555** -- training is **0.3218
below** it, and the registration allowed 0.10. **T5 NULL**: the buffer's effect is -0.0266 on a sem of 0.0196,
unresolved.

**So the frozen probe is not a lower bound on what training achieves.** Everything in this line has treated `e348`'s
and `e363`'s frozen readings as *floor* statements about what is there; this says they can be **ceiling** statements
instead: a linear decoder on a frozen net can read more of the substrate than a body trained on the same task
manages.

## 3. What T4's gap is and is not

**The comparison mixes two protocols and must be read as such.** `e363`'s cell is **one** four-symbol task with 512
examples rolled on a **frozen** network and decoded by a least-squares probe; `e365`'s diagonal is the mean of
**three** tasks trained **sequentially** with 96 examples each, on a body that is being changed. So the 0.3218 gap
carries the multi-task protocol, the smaller training splits and the training itself, and the honest statement is
narrower than "training loses a third of the signal": **on this cell, a trained body's three-task diagonal is 0.3218
below a frozen probe's single-task reading**, and separating the three causes is the next unit.

**What is not mixed is the pair of late-cue cells.** Both are trained, both are 20 replicates on one world, and one
is at chance (**0.2326**, the read step) while the other is at **0.5337** (one step earlier). **The interface knob is
worth 0.3011 of diagonal as a task**, and it is worth it in exactly the place `e363`'s frozen grid pointed at.

## 4. What it cannot do

*One cell*: `cue@10` in the cue source, so the knob's value across gaps is two points and not a curve. *One world and
one coupling*: eight dimensions at `leak = 0.35`. *The probe comparison mixes protocols*, as above, which is why T4's
fired falsifier is reported with its confound rather than as a clean loss. *And the trained task is not at ceiling*:
0.5337 leaves room, so a better optimiser or a longer run could close part of the 0.3218 -- nothing here says the gap
is a property of the interface rather than of this training budget.
