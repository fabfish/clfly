# The benchmark has an episode: the world carries it, the boundary marks it, and the last trial is buried in it

*2026-10-11. `experiments/e489_the_benchmark_has_an_episode.py` gives the closed loop's pass an **episode** of
`--loop-episode` trials -- one cue each, the world's state the episode's -- and the episode a **boundary** channel
that marks where it opens. **FA1, FA2, FA3 and FA5 MET and FA4's falsifier FIRED**: the episode is carried at
**12.62** sigma, the boundary carries its sign at the episode's opening and at every continuing trial and zero
elsewhere, and the **last trial's label is not there to be read** -- every arm sits at the four-class chance.*

## 1. The two runs

The card's neutral roll with `--loop-episode 3`, once with `--loop-boundary` and once without it; and `e438`, the
corpus's own roll at one trial per pass, which the endpoint is read against.

| the arm | the boundary run's accuracy diagonal | the plain run's | the change | sigma | the boundary run's accuracy last row | the plain run's |
|---|---|---|---|---|---|---|
| `naive` | **0.2476** | 0.2476 | -0.0000 | **-0.00** | 0.2365 | 0.2420 |
| `ewc-block` | **0.2497** | 0.2451 | +0.0045 | 0.61 | 0.2455 | 0.2559 |
| `replay` | **0.2524** | 0.2413 | +0.0111 | 1.02 | 0.2441 | 0.2441 |

and the episode itself, built rather than read: the world's state at the read step for two episodes that share the
last trial's cue and the cue's noise and differ only in the **earlier** trials' cues, over the run's own sixty-four
examples at the card's own circuit and body.

| the pass | the two states' difference | sigma | the largest | the state's own scale |
|---|---|---|---|---|
| **one trial** | **0.0000e+00** | **0.00** | 0.0000e+00 | 0.7856 |
| **three trials** | **0.7601** | **+12.62** | 1.7013 | 0.7727 |

| claim | measured | verdict |
|---|---|---|
| FA1 the endpoint is exact, and only the episode moved | the draw **22** fields with **0** added and **0** missing, `cue_input` bit-identical; the configs **0** differing past the inert rule with `loop_episode` and `loop_boundary` the fields moved; the draws the card's plus `episode_len` (plain) and plus the four episode fields (boundary) | **MET** |
| FA2 the world's state at the read step is the episode's | **0.7601** at **12.62** sigma over **64** episodes, the largest **1.7013** against a state scale of **0.7727**; at one trial the same manipulation moves **exactly 0** | **MET** |
| FA3 the boundary is a channel of its own | the marker is **`+1, 0, 0, 0, -1, 0, 0, 0, -1, 0, 0, 0`** at gain **1.0**, **8** neurons, **0** overlapping the three populations, inside the task's input set, and none drawn at the endpoint | **MET** |
| FA4 the episodic task is learned | the plain run's diagonals are **0.2476**, **0.2451** and **0.2413** against a chance of **0.25** | **FALSIFIER FIRED** |
| FA5 the boundary does not buy the task | **-0.0000**, **+0.0045** and **+0.0111** at **-0.00**, **0.61** and **1.02** sigma | **MET** |

## 2. What the episode is

**The environment has an episode, and the endpoint is exact.** With the flags off the environment is the one the
corpus holds: its draw is `e438`'s own `env_draw` **field for field**, **22** fields with **nothing** added and
nothing missing, no `episode_len` and no `boundary_sha1`, and `cue_input` is **bit-identical** to the single-pulse
array it has always returned. The two runs carry the card's config with **no** field differing past the inert rule,
the only fields moved being `loop_episode` and `loop_boundary`, and their draws are the card's plus exactly
`episode_len` (the plain run) and plus `episode_len`, `boundary_sha1`, `n_boundary` and `boundary_gain` (the
boundary run). **So the episode is an addition to the environment and not a change to it**, and a reader comparing
these runs with any earlier one is comparing one thing.

**And the world's state at the read step is the episode's and not the last trial's.** Two episodes that share the
last trial's cue -- and the cue's own noise, so the difference is the earlier trials and nothing else -- leave world
states that differ by **0.7601** at **12.62** sigma over sixty-four episodes, with the largest difference
**1.7013** against a state scale of **0.7727**: **the earlier trials move the read as much as the state itself
is**, which is what "the state is the episode's" means as a number. At one trial per pass the same manipulation
moves **exactly nothing**, because the earlier trials are not in the input at all -- and that zero is the control
that says the difference at three trials is the episode and not the measurement.

**And the boundary is a channel of its own.** Eight neurons drawn from the environment's own seed, disjoint from
the cue's, the action's and the feedback's, inside the task's own input set, carry `+1.0` at the step the episode
opens and `-1.0` at each continuing trial's first step and **zero at every other step** -- the
`+1, 0, 0, 0, -1, 0, 0, 0, -1, 0, 0, 0` of the declaration. **The cue cannot carry that**: it pulses at every
trial's first step whatever the trial's position, so which trial a step belongs to is exactly the thing the input
did not say and this channel does.

**And the last trial is buried in the episode it is the last of.** Every arm's accuracy sits at the four-class
chance -- **0.2476**, **0.2451** and **0.2413** against **0.25** -- so the claim that the episodic task is learned
**fired its falsifier**. The mechanism is not a mystery and is the previous paragraph: if the earlier trials move
the world's state by its own scale, then at the read step the label is a small part of an eight-number vector whose
larger part is the episode's own history, and a linear head on it finds the history. **So the episode is carried so
well that the trial it ends with is not readable from it**, and the benchmark's read-out -- the world's state at the
pass's **last** step -- is what turns the structure into a chance-level task.

**And the boundary buys nothing, because there is nothing to buy.** On no arm does the boundary run's accuracy rise
above the plain run's: **-0.0000**, **+0.0045** and **+0.0111** at **-0.00**, **0.61** and **1.02** sigma. The
channel is information about the world's state and not about the label, and with every arm at chance an effect on
the accuracy is not what it would show up as. **So the flag's bearing is the structure it marks**, and whether a
boundary is worth anything to an agent that has to *act* on it is a question this unit does not reach.

## 3. What it cannot do

- **One episode length**: three trials is the longest a twelve-step pass gives a cue room for, and a sweep of two,
  three, four and six is not in the unit.
- **And chance accuracy means the accuracy face says nothing here**: what a boundary would be worth at a length the
  head can read is not measured, and this unit registers no claim about it either way.
- **And the read is at the pass's last step**: a read inside the last trial, or a read at every trial, is what the
  firing asks for and is a different unit -- the label is in the input at step **8** of the twelve and the read is at
  step **11**, so what is missing is a window and not a signal.
- **And no payout rides on these runs**: `reward_retention` is `None` on every replicate, so the episode's own
  currency -- what the world pays inside an episode -- is not in the unit.
- **And three trials of four steps is a short carry** at the world's own leak, which is what lets the earlier trials
  dominate; a second leak, or a nonlinear world, is not in it.
- **And the card still names an episode boundary**: a clause in the card is a revision and this unit is the
  environment, the runner and the reading, so the `absent` list is untouched.
