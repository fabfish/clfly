# The episode at two trials: the label's path collapses with the first trial and the split is not the knob

*2026-10-11. `experiments/e492_the_episode_at_two_trials.py` shortens `e489`'s episode from three trials to **two**,
which is the pass's other split of the same twelve: the label's cue then arrives at step **6** instead of **8** and the
read is at the same step **11**, so the label gets **five** drive steps instead of three. **HB1 and HB2 MET and HB3's
falsifier FIRED**: the label's own part of the read is **0.0377** at two trials against **0.9144** at one, and the
accuracy is still the four-class chance.*

## 1. The run and the instrument

The card's command with `--loop-episode --loop-boundary`, once at two trials and once at three.

| the arm | the two-trial run's accuracy diagonal | the three-trial run's | the change | sigma | the two-trial run's last row | the three-trial run's |
|---|---|---|---|---|---|---|
| `naive` | 0.2434 | 0.2476 | -0.0042 | -0.60 | 0.2507 | 0.2365 |
| `ewc-block` | 0.2424 | 0.2497 | -0.0073 | -0.92 | 0.2583 | 0.2455 |
| `replay` | 0.2333 | 0.2524 | -0.0191 | -1.94 | 0.2420 | 0.2441 |

and the label's own part of the world's state at the read step, at the card's own body, with the cues deterministic
and the earlier trials **held fixed across the examples** so that what varies from one symbol to the next is the
label and nothing else:

| the pass | the across-symbol spread | the within-symbol spread | the state's own scale | the spread as a share of the scale |
|---|---|---|---|---|
| **one trial** (the corpus) | **0.9144** | 2.5e-08 | 0.6232 | **147%** |
| **two trials** | **0.0377** | 1.4e-08 | 0.6600 | **5.7%** |
| **three trials** | **0.0001** | 9.3e-10 | 0.6607 | **0.008%** |

| claim | measured | verdict |
|---|---|---|
| HB1 the pass's split is the one flag moved | **0** config fields differing past the inert rule with `loop_episode` the one moved, the draw **25** fields with **0** differing and `episode_len` moving `[3, 2]`, **20** replicates | **MET** |
| HB2 the label's own part of the read grows when the trial does | the across-symbol spread is **0.9144**, **0.0377** and **0.0001** at one, two and three trials, the within-symbol spread at the float's floor throughout | **MET** |
| HB3 the label comes back when the trial is longer | the diagonals are **0.2434**, **0.2424** and **0.2333** against **0.25**, with **0** of three arms over the bar and **all three** within **0.05** of chance | **FALSIFIER FIRED** |

## 2. What it says

**The two runs differ in the split and in nothing else.** **0** config fields past the inert rule with
`loop_episode` the one moved, and the draw's **25** fields agreeing with **0** differing except `episode_len` itself:
the boundary channel is the same channel, the world is the same world, the three tasks are the same three. **So the
episode's cardinality is an ablation and not a change of game**, which is what makes the two faces below readable
against each other.

**And the label's path to the read collapses at the first trial.** With the past held fixed, the label's own part of
the world's state at the read step is **0.9144** when the pass is one trial -- more than the state's own scale, since
there the state *is* the label's response -- **0.0377** at two trials, and **0.0001** at three. **So an episode costs
the label a factor of 24 the moment it has one trial before it**, and a further factor of 683 when it has two: the
read step's state is the past's, with the label a perturbation of **5.7%** of it at two trials and **0.008%** at
three. *That is the instrument's own answer at an untrained body and it ranks the splits; it does not say what a head
can find in them.*

**And the accuracy does not come back, so the split is not the knob.** Every arm is at the four-class chance at two
trials as well -- **0.2434**, **0.2424**, **0.2333** -- and all three sit **below** the three-trial run's, by
**0.0042**, **0.0073** and **0.0191** at **-0.60**, **-0.92** and **-1.94** sigma. **So a five-step window is worth
nothing measurable where a three-step one was**, which is the claim this unit registered and it fired: **what the
corpus's read-out is paying is not the length of the episode.**

**And three exclusions now stand where `e489` had one mechanism.** `e489` measured the pass at three trials and
every arm came out at chance; `e491` removed the **world's** share of the earlier trials entirely and the accuracy did
not move; this unit lengthened the label's window and thinned the episode and the accuracy did not move either. **Two
candidates are left and neither is measured here**: the **model's** recurrent state, which carries the earlier trials
into the last trial's actions and which nothing in this line has touched, and the **read** itself -- eight world
numbers and a linear head, at a body whose label residue is 5.7% of the state at two trials and may be a function of
the past rather than of the label. *The instrument's collapse between one trial and two is the sharpest fact this unit
has: the trial's own time axis is where the label lives, and an episode takes it away before its length can matter.*

## 3. What it cannot do

- **Two splits are not a sweep**: the pass offers four (two, three, four and six trials) and this unit carries two of
  them against the corpus's one, so the collapse is located between one and two and not measured across the family.
- **And the two changes travel together**: two trials is a longer window **and** one fewer distractor trial, and no
  split of a fixed twelve-step pass separates them.
- **And the model's carry is untouched**: the cues still reach the last trial's actions through the recurrent state,
  which `e491` neither removed nor measured.
- **And the instrument is at an untrained body**: the label's share of the read is measured before any training, so it
  ranks the splits and does not say what a trained head can find in them -- and a trained arm's chance accuracy at a
  5.7% residue is a statement about the head as much as about the residue.
- **And one budget, one world and one seed stream**: the card's own setting.

## RE-READ 2026-10-11

**The instrument's share ranks the pass's splits and not the reads.** This unit's *cannot settle* closed on the instrument being at an untrained body -- *it ranks the splits and does not say what a trained head can find in them* -- and `e493` measured the same quantity on the model's own thirty-two columns and found the accuracy going the other way. The world's read carries the larger **share** at both lengths (**0.0571** against **0.0386** at two trials, **1.4673** against **1.0494** at one), and the head that reads the model gains **+0.0670**, **+0.0521** and **+0.0698** at **+7.00**, **+4.07** and **+7.29** sigma over the same episode's world read. So the share is a scale-free quantity and not a dimension-free one, and what it ranks is the pass's splits at one width: the collapse from **0.9144** to **0.0377** stands as this unit's reading, and the between-read ranking is the instrument's and not the head's.
