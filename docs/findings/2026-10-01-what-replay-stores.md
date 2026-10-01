# What replay stores, and the second account it rules out

*2026-10-01. Nothing runs: `experiments/e335_what_replay_stores.py` builds two environments on a 64-neuron stand-in
circuit, reads `experiments/e8_rate_network.py`'s source, and reads `runs/e334_replay_{instant,carry}.json`. Seconds.
Writes `runs/e335_what_replay_stores.json`.*

## 1. There is nothing to dump, because the buffer holds inputs

`e334` read the loss on `replay`'s stored features out, found **the mechanism `e333` named refuted in the form it was
named** -- the two worlds' retention differs by 0.0375 at 2.45 sigma and the loss the arm actually minimises is the
same to within **0.32 sigma** -- and named the next unit: comparing the stored activations **themselves**, which
*"needs a feature dump and not a loss"*.

**This unit finds the dump unnecessary, because there are no stored activations.** `run_method` fills its buffer with

    replay.extend((task.u_train[i], int(task.y_train[i]), k) for i in idx)

-- a task **input**, its label and its task index. The features `e334` measured the loss on are **recomputed by the
current body at replay time**, which is what makes them features *of the body* and not of the buffer.

**T1 MET.** The arrays a buffer is filled from are **byte-identical** between the two worlds: eight train and eight
test examples built under `leak = 1.0` and `leak = 0.35`, identical on `u_train`, `u_test`, `y_train` and `y_test`.
That is structural rather than lucky -- `CueActionEnv` adds the world's channel **inside the feedback closure at roll
time**, and never writes it into the array `make_env_task` returns -- and it is the premise the rest of this unit
rests on.

**T2 MET.** And what the buffer holds is an input: the source line above, read out of the runner rather than
asserted from memory.

## 2. And the body that moved less retained less

| run | drift, task 0 | task 1 | task 2 | mean | `replay`'s forgetting |
|---|---|---|---|---|---|
| instantaneous (`leak = 1.0`) | 0.06725 | 0.05924 | 0.05751 | **0.06134** | 0.0479 |
| carried (`leak = 0.35`) | 0.06628 | 0.05798 | 0.05435 | **0.05954** | **0.0854** |

**T3 MET**: the two bodies differ by **2.93%** of the instantaneous run's own drift, so the worlds are not the same
body and the retention difference cannot be dismissed as one object measured twice. **T4's falsifier FIRED**: the
carried body moved **2.93% less** while its retention is the **worse** one, where `e333` measured it worse by 0.0375.

**So the second natural account is out as well.** If the retention difference lived in the body, the body that
retained less should be the one that moved more; it moved less. Put beside `e334`, the account now has **three**
exclusions in a row: not the stored features fitting worse (0.32 sigma), not the buffer's contents differing (byte-
identical), and not the body drifting further (2.93% less).

**And `e335`'s own "what it cannot do" writes the next reading before the data does**, in the same words `e334` used
about the loss:

> *"Drift is a norm and not a direction: a body that moved the same distance in a different direction is invisible
> to T3 and T4, and the metric the artifacts record is `||theta - theta_before|| / ||theta_before||`."*

What is left is that the carried body moved **differently** -- and the quantity that would separate that from the
three exclusions is the direction, which no artifact in this corpus records.

## 3. What it says

**The thread's most robust fact is `replay`'s retention moving with the world's channel, and three units have now
failed to find it in the places it looked.** That is worth more than it sounds: `e334` and `e335` each killed a
mechanism that was the obvious one at the time, and both of them said in advance what the kill would imply. The
surviving candidate is a directed account of the body's movement -- the same distance in a different direction --
and the instrument that would test it is a **per-task direction of `theta_final - theta_before`**, which the
artifacts record as a norm and not as a vector.

**And one negative is now pinned rather than described.** The claim that the world's change never enters the stored
objects is not an argument about this environment's design: it is eight train and eight test arrays compared
element by element, and it would catch a future environment that wrote the world into `u`.

## 4. What it cannot do

**Two artifacts, one arm and one pair of worlds**: `naive`, `ewc` and the block arms are not read, and `e332`'s other
sign -- retention *improving* when the response became a state -- is not asked. *Drift is a norm and not a
direction*, which is the whole of what remains. *T4 is a claim about two runs*, which is why its falsifier is stated
on the same 1% as T3's rather than on a sigma, and a two-run claim has no interval. *The buffer comparison is on a
64-neuron stand-in circuit* and not on the 952-neuron one the runs used, so it establishes the environment's
behaviour rather than re-measuring those runs; the arrays that mattered -- the cue templates, the noise stream and
the task seeds -- are the same code path at any circuit size, and that is an argument and not a measurement.
*And the source scan reads one line*: a future runner that filled its buffer elsewhere would be found by it only if
the same call name were used.
