# The boundary the world obeys: the mark is exact and the trial's label does not come back

*2026-10-11. `experiments/e491_the_boundary_the_world_obeys.py` makes the world **obey** the boundary `e489` gave the
episode: `--loop-episode-reset` drops the carried state at every trial's first step, so each trial starts from a
world at rest. **GB1 and GB2 MET and GB3's falsifier FIRED** -- the world's dependence on the earlier trials goes to
**exactly zero**, and the accuracy does not move: the carry `e489` measured was not what buries the label.*

## 1. The run and the rule

The card's command with `--loop-episode 3 --loop-boundary`, once with `--loop-episode-reset` and once without it.

| the arm | the reset run's accuracy diagonal | the carry run's | the change | sigma | the reset run's last row | the carry run's |
|---|---|---|---|---|---|---|
| `naive` | 0.2410 | 0.2476 | -0.0066 | -0.62 | 0.2333 | 0.2365 |
| `ewc-block` | 0.2476 | 0.2497 | -0.0021 | -0.35 | 0.2392 | 0.2455 |
| `replay` | 0.2479 | 0.2524 | -0.0045 | -0.46 | 0.2417 | 0.2441 |

and the world's own rule, driven by hand -- no model, no cue, two trajectories per example agreeing from the **last
trial's first step** onward and differing at every step before it:

| the world's rule | the state at the read step between the two pasts | sigma | the largest | the state's own scale |
|---|---|---|---|---|
| with the carry (`e489`'s run) | 0.0124 | **+13.21** | 0.0332 | 0.3369 |
| **with the reset** | **0.0000e+00** | **0.00** | **0.0000e+00** | 0.3368 |

| claim | measured | verdict |
|---|---|---|
| GB1 the one flag moved, and the world's rule is what it moved | **0** config fields differing past the inert rule with `loop_episode_reset` the one moved, the draw **26** fields with `['episode_reset']` added and **0** differing, **20** replicates | **MET** |
| GB2 the world's rule obeys the mark | **0.0000e+00**, largest **0.0000e+00**, with the reset against **0.0124** at **13.21** sigma without it | **MET** |
| GB3 the trial's label is recoverable once the world starts at rest | the diagonals are **0.2410**, **0.2476** and **0.2479** against **0.25**, with **0** of three arms over the bar and **all three** within **0.05** of chance | **FALSIFIER FIRED** |

## 2. What it says

**The world's share of the carry is gone, and it is gone exactly.** Driven by hand the two pasts give world states at
the read step that differ by **0.0124** at **13.21** sigma with the carry and by **exactly 0.0000e+00** with the
reset -- not "less", zero, because the reset cuts the dependence by construction and the measurement is the rule
itself rather than a training run's shadow of it. **So the flag does what it says**: the boundary is no longer merely
a signal over a carry, it is the step the world's state starts from, and the two runs are one configuration, one
world and one boundary channel apart from that one field.

**And the label does not come back.** Every arm sits at the four-class chance, and on every arm the reset run is
**below** the carry run's diagonal -- **0.0066**, **0.0021** and **0.0045**, at **-0.62**, **-0.35** and **-0.46**
sigma. **So the world's memory of the earlier trials was not what cost the label**, which is the one thing this unit
exists to test, and the claim that it would recover **fired its falsifier**.

**And the exclusion is the result.** `e489`'s own mechanism sentence -- *the earlier trials move the world's state at
the read step by its own scale, so a linear head on it finds the episode and not the label* -- is now a measured
**non**-explanation: that dependence is provably removed here and the accuracy does not move by a tenth of the bar.
What is left is the other half of the same carry and a window. **The other half is the model's**: the reset drops the
world's state and not the network's, so the earlier cues still reach the last trial's **actions** through the
recurrent state, and the read is the world's state driven by those actions. **And the window is three steps**: the
label's cue arrives at step **8** of the pass and the read is at step **11**, against the corpus's own eleven steps
from a cue at zero, so what the trial may be missing is time rather than memory. *Both are named and neither is
measured here.*

**And the structure is unedited, which is what makes the ablation one.** The one moved field is
`loop_episode_reset`; the draw adds the one field and disagrees in nothing else, the boundary channel, its eight
neurons, its gain and its marks are the ones `e489`'s run carries, and the two runs are the card's own command at the
card's own episode length. **So what moved is the world's rule and not the game.**

## 3. What it cannot do

- **One episode length and one reset**: three trials of four steps is the length `e489` read, and a sweep of two,
  three, four and six -- which is the window this unit's firing points at -- is not in the unit.
- **And the reset is the world's and not the agent's**: the model's recurrent state still carries the earlier trials
  into the last trial's actions, so a label buried in *that* is not touched here and is not measured either.
- **And one budget, one world and one seed stream**: the card's own setting, so the recovery that did not happen is
  not a recovery that cannot happen.
- **And the accuracy is the corpus's own metric on a task at chance**: a difference of **0.0021** to **0.0066** in a
  currency sitting on the floor is not a demonstration that the reset does nothing, and the sigmas are large numbers
  about small ones.
- **And the boundary channel is unedited**: what this unit changes is the world's rule, and what a **policy** would
  make of a boundary it can act on is `e488`'s question and not this one.

## RE-READ 2026-10-11

**The first rung of the sweep this unit named is measured, and it is flat.** This unit closed on *a sweep of two, three, four and six -- which is the window this unit's firing points at -- is not in the unit*. `e492` supplies its first rung: the episode at **two trials**, the pass's other split of the same twelve, the label's cue at step **6** instead of **8** and the read at the same step **11**, so the label gets **five** drive steps instead of three and the episode carries one distractor trial instead of two. Every arm is still at the four-class chance -- **0.2434**, **0.2424** and **0.2333** against **0.25**, each *below* this unit's two-trial counterpart run by **0.0042**, **0.0073** and **0.0191** -- while the label's own part of the read step's state rises from **0.0001** to **0.0377** against **0.9144** at one trial. So the window is not the cost either, and what this unit left as a candidate is what is left: the model's recurrent state, untouched, and the read itself.
