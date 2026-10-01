# The seed stream is three draws at once

*2026-10-02. Nothing runs: `experiments/e339_is_the_ordering_immune_to_the_redraw.py` reads four artifacts already
on disk -- `e331`'s five-arm run and this thread's own at `--seed0 4`, and `e333`'s two-world run against `e337`'s.
Seconds. Writes `runs/e339_is_the_ordering_immune_to_the_redraw.json`.*

## 1. The unit was registered to test the ordering, and its T1 came back fired

`e337` ran `e333`'s two worlds on a **second seed stream** (`--seed0 4` in place of 0) and the effect **reversed**:
+0.0375 at 2.45 sigma one way, -0.0771 at 3.36 the other. `e338` then asked one trained body both questions and
found the manipulation moves **nothing** (0.0000 on a sem of 0.0022). So the calibration the thread reached is that
the **redraw dominates** a configuration-against-configuration comparison at five replicates.

**This unit was registered to put the same question to `e331`'s ordering** -- five arms on `--seed0 4`, the same
circuit, read-out, tasks, arms and settings, differing in the seed stream alone. **And its T1 is FALSIFIER FIRED**,
on the first pair it looked at: the runs are **not** one configuration in two seed streams.

**The reason is the unit.** `--seed0` is not only the training seed stream:

- it draws the **read-out subset**, because `--readout-seed` defaults to it;
- and it seeds `fly_env.build`, so it draws the environment's **three populations** -- cue, action and feedback.

So a run at `--seed0 4` differs from the same command at `--seed0 0` in **three draws at once**, which is a property
of every seed-stream comparison in this thread -- `e337`'s included.

**T2 MET** and **T3 MET**, on **both pairs**: the read-out fingerprint is `59926518137c` at seed 0 and
`5bca012cb139` at seed 4, and the cue population is `3985fc4e3252` against `81c609ba5206`, in `e331`'s pair and in
`e337`'s. The action and feedback populations move with them.

**T4's falsifier fired too**, and it is the other half of the same problem: **no clean seed-stream pair exists in
this corpus**. `e331`'s pair differs in `loop_world_modes` and `loop_world_leak` as well, because `e331` was run
before those flags existed, and `e337`'s pair differs in `methods` (`naive,replay` against `replay`), because
`e333` ran two arms and its replication ran one.

## 2. What it says

**`e337`'s conclusion survives and its label does not.** The sign did flip, the redraw does dominate, and `e338`
settled that the manipulation itself moves nothing -- all three stand. What does **not** stand is calling the two
runs *two seed streams*: they were a different read-out subset, a different set of three populations and a different
seed stream, in one command. `e337`'s own "what it cannot do" wrote *"one circuit, one read-out width and one pair of
worlds"* as a caveat; the read-out width was the same 32 and the **subset** was not, which is the sharper version of
the same worry and is now measured rather than admitted.

**And the fix is two flags, one of which does not exist.** `--readout-seed 0` holds the decoder's draw fixed and is
already there; the environment's population seed is `--seed0` with no flag of its own, so a clean pair needs
**`--loop-seed`** -- or a run whose read-out and populations are recorded and re-supplied, which is what
`--readout-seed` does for one of the three. Until then every seed-stream claim in this thread is a claim about three
draws, and the number of runs that would separate them is small: hold two fixed, vary one.

**And the confound is not specific to the loop.** It applies to every unit in this corpus that compares two
`--seed0` settings and calls the difference a seed effect, which includes `e337` and, by construction, any future
one -- `e331`'s own ordering evidence is not affected, since its two runs share a seed.

## 3. What it cannot do

**Two pairs, both at `--seed0 0` against 4**, and nothing here varies the read-out draw and the populations
**independently** -- which is the experiment that would attribute the flip: hold the read-out and the populations
fixed and vary only the training seeds, then hold the seeds and vary only the read-out. *The numbers are read and not
re-measured*: this unit reports what the four artifacts' fingerprints say, so its evidence is their own records and
it re-runs nothing. *And it says nothing about the ordering's stability*, which was the registered question: that
needs a pair of runs whose read-out draw and populations are held fixed, and no such pair exists in this corpus.
