# Training through the loop

*2026-10-01. Runs: `experiments/e8_rate_network.py --circuit-size 300 --iters 500 --readout-size 32 --repeats 5
--methods naive,ewc-block --closed-loop` (263 s) and the same with `--no-feedback` (263 s), read by
`experiments/e326_training_through_the_loop.py`.*

## 1. What `e325` left and this trains

`e325` built the closed loop and measured it **frozen**. It ended by naming what was missing: *"nothing here trains
on the loop, so all four claims are the frozen substrate's behaviour"*, and *"a reward and a policy"*. This is the
first of those.

`e8_rate_network` gained `--closed-loop`, which builds the suite out of `clfly.network.env` -- three cue sets in
**one** world, so one feedback function serves the whole suite -- and `--no-feedback`, which runs the identical
tasks, cue sets, seeds and read-out with the world disconnected. **The feedback reaches every forward pass by
wrapping the module**, `fly_env.ClosedLoop`, rather than by editing the dozen call sites: training, evaluation, the
Fisher blocks and the replay features all call ``model(U, None)`` and all get the loop, so no arm can be training a
different dynamical system from the one it is measured on. The wrapper's pass-through is asserted by test, including
that ``theta`` and ``bias`` are the module's own objects rather than copies an optimiser would miss.

**T1 MET.** Same circuit `mb+cx+al@n952`, same read-out fingerprint `59926518137c`, the same three task names, the
same environment draw (`cue_sha1 3985fc4e3252`, `action_sha1 f379863d1cf4`, `feedback_sha1 77963b921bc3`, twelve cue
neurons, eight action neurons, twelve feedback neurons, scale and gain both 1.0), five replicates per arm in both
runs, and **no config field differing** once the feedback switch and the output path are excluded.

**T2 MET.** The loop trains: `naive`'s final accuracy under the closed loop is **1.0000** against a chance of
**0.50**, so backprop-through-time crosses the loop without destabilising it.

## 2. And then the loop made the task easier, not harder

| arm | open accuracy | closed accuracy | Δ | σ | open forgetting | closed forgetting | Δ | σ |
|---|---|---|---|---|---|---|---|---|
| `naive` | 0.9708 | **1.0000** | **+0.0292** | 1.00 | 0.0437 | **0.0000** | **-0.0437** | 1.00 |
| `ewc-block` | 0.9042 | 0.9625 | +0.0583 | 1.00 | 0.1437 | 0.0563 | -0.0875 | 1.00 |

**T3 landed on its NULL**: the closed loop reads **+0.0292 higher**, inside the 0.05 band, so the registered claim
that a self-driven input channel costs *level* is neither confirmed nor refuted at this bar. **T4's falsifier FIRED**:
the closed loop forgets **0.0437 less**, and `naive`'s forgetting is **exactly zero** -- the whole of what the open
loop lost, given back.

**Both arms move the same way and by more than the bar**, which is not noise at a hair's breadth: the direction is
consistent across two arms with different mechanisms (`naive` has no penalty and `ewc-block` carries a Fisher
anchor), and it is the **opposite** of what was registered.

**And the plausible mechanism is the same thing that makes the measurement weak.** The agent's action is a
``tanh`` of the mean activity over eight neurons, shown back at twelve: a channel whose input at step ``t`` is a
monotone function of the state at step ``t - 1`` is a **latch**, and a latch is a memory. The environment's cue is a
single pulse at step 0 and then nothing, so the task is exactly *hold a value against a gap* -- and a self-exciting
feedback channel is a way to hold it. `e325` warned about the other half of this: the cue probed at **1.00** in both
loops on the frozen network.

**So neither T3 nor T4 can carry much here.** The open loop already reads **0.9708**, so there is almost no room for
the closed loop to cost anything, and `naive`'s closed-loop forgetting is at zero so there is no room at all to
measure retention in. What this unit establishes is the **capability** -- a trained arm whose gradient crosses its
own output, with a config diff that says the two runs differ in the loop and nothing else -- and a **direction** that
the next unit has to test on a task with headroom rather than a bar it cannot reach.

## 3. What it cannot do

**Two arms and five replicates**: `replay` and the two block arms were not run, and five replicates put one standard
error of a paired accuracy difference near 0.02 -- both contrasts here resolve at **1.00 sigma**, so the signs rest
on agreement across arms and not on an interval. **The task is at or near ceiling in both runs**, which is the
limitation that matters: with the open loop at 0.9708 and the closed loop at 1.0000, T3 and T4 have almost no room,
and a task whose read-out is not saturated is the unit that would settle the direction. **One circuit, one read-out
width, one scale and one gain** -- the feedback strength is a knob and not a sweep here, and a latch's effect should
grow with it. **The action is smooth**, so the gradient crosses it; a hard threshold would make the loop
non-differentiable and is not measured. **And there is still no reward**: the label is the cue, delivered at step 0,
and the agent's action is an input rather than a decision -- so this is the first training run through a closed loop
in this repository, and it is not yet a game.
