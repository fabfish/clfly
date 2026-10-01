# What replay is scored on, and the mechanism that is not there

*2026-10-01. Runs: `experiments/e8_rate_network.py --circuit-size 300 --iters 500 --readout-size 32 --repeats 5
--methods replay --closed-loop --loop-symbols 8 --loop-noise 1.0 --loop-scale 1.0 --loop-world-modes 2
--loop-world-leak {1.0, 0.35}` -- 140 s and 146 s, read by `experiments/e334_what_replay_is_scored_on.py`.*

## 1. The mechanism `e333` named and could not test

`e333` gave the world a transition rule and measured `replay`'s retention moving in **opposite directions** under
the thread's last two changes to the world's channel -- **falling 0.0292 at 2.89 sigma** when the response became a
*state* (`e332`) and **rising 0.0375 at 2.45 sigma** when that state acquired a *rule* (`e333`). Both were the only
resolved moves in their tables and both were `replay`'s, and `e333`'s finding named what it could not test:

> *"`replay` carries replayed activations, so its stored features are features of a world; change the world's
> response and the features are stale in a new way, which can cost retention (the rule) or -- less obviously --
> help it (the state). Both signs are measurements, neither is a mechanism, and separating them needs the stored
> features read out, which nothing here does."*

**This reads them out, in the units the arm is trained in.** `train_task` now takes a `replay_probe` dict and
records the loss on the stored replay features at the **first** and the **last** training iteration of each task;
`run_method` keeps it per task as `replay_loss`. That is the staleness as the arm itself sees it, at two floats per
task, and it is recorded for every method and empty for the ones that store nothing.

Two runs, `replay` alone, five replicates, on the two worlds `e333` compared -- `leak = 1.0` and `leak = 0.35` --
with the same seeds, so every contrast is paired by replicate and by task.

**T1 MET.** Same circuit `mb+cx+al@n952`, same read-out `59926518137c`, the same three task names, five replicates
each, the environment draw identical in every field the leak does not name, and **no unexpected config or
environment difference**.

## 2. And the mechanism is not there

| world | replay loss, first step | replay loss, last step | rise | accuracy | forgetting |
|---|---|---|---|---|---|
| instantaneous (`leak = 1.0`) | 0.0436 | 0.0320 | **−0.0116** | 0.6264 | 0.0479 |
| carried (`leak = 0.35`) | 0.0425 | 0.0301 | **−0.0124** | 0.6042 | 0.0854 |

**T4's falsifier FIRED.** The registered claim was that the loss on the stored features **rises** within a task in
both worlds; it **falls** in both, by 0.0116 and 0.0124. **T2 landed on its NULL**: the carried world's last-step
loss is lower by **0.0019 at 0.32 sigma**, so the stored features are **not** more stale in the world with a rule.
**T3's** rise difference is **−0.0008 at 0.13 sigma**.

**So the mechanism is refuted in the form it was named.** The two worlds' retention differs by 0.0375 -- `e333`'s
2.45 sigma -- and the loss `replay` actually minimises is **the same to within a third of a sigma** and falls in
both. `replay` satisfies its own objective equally well in a world with a rule and in one without, so where its
retention differences come from is **not** that its stored features fit worse.

**And the unit's own "what it cannot do" predicted this reading before the data arrived**: *"the stored features are
not read out: this measures how well they are fitted, and not what they are, so a change that makes them different
without making them worse fitted is invisible to it."* The features can be different -- the world's channel is a
different function of the agent's history in the two runs, so the activations `replay` re-feeds are different
objects -- while being equally well fitted, which is exactly what the table shows.

**Two things follow.** The registered direction was a guess and it was wrong in a way worth recording: a replay loss
that **falls** over training is what a working replay buffer looks like, and a unit that predicts a rise is
predicting that the arm is failing at its own objective. And the magnitude is small -- 0.03 to 0.04 -- against
per-replicate standard errors of 0.006, so the quantity had the resolution to see a staleness of `e333`'s size
(0.0375) at about **six sigma** and saw a thirty-second of it.

## 3. What it says

**The thread's only resolved moves are `replay`'s retention, and they are not where its own loss is.** The arm
stores activations, the world's channel changes, the retention moves by 0.03 to 0.04 in both directions -- and the
loss on the stored features does not move at all. So the account has to be about something other than fit: the
features being *different* (which this unit does not measure), the interaction between replayed gradients and the
current task's, or the body's own drift under a different input distribution.

**That is a narrower and more useful statement than `e333`'s.** Its mechanism was plausible and it is now excluded
in its most natural form, which leaves a short list rather than an open one -- and the next unit that would shrink
it further has to compare the stored activations **themselves** between the two worlds, which needs `--save-theta`
or a feature dump and not a loss.

## 4. What it cannot do

**One arm and one pair of worlds**: `naive`, `ewc` and the block arms are not run, and only `e333`'s two leaks are
compared -- so the **other** sign `e332` measured, retention *improving* when the world's response became a state,
is not asked here at all. *Two scalars per task*: the loss is recorded at the first and the last iteration and not
through training, so a non-monotone history is invisible. *The probe is the training loss itself*, measured on the
same batch schedule the arm trains on and not on a held-out replay set, so it is partly a statement about that
schedule. *And the stored features are still not read out*: this measures how well they are fitted and not what
they are, so a change that makes them different without making them worse fitted remains invisible -- which is now
the reading and not a caveat.
