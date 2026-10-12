# The label first at three trials: the working pass is a family, and one more cue helps

*2026-10-12. `experiments/e497_the_label_first_at_three_trials.py` puts a **second** distractor in `e495`'s
label-first pass -- three trials of four steps, the label at step **0** and its cues at steps **4** and **8**, the
read at step **11** as before. **NB1, NB2 and NB3 all MET**: the label's own part of the read is **1.0571** against
**1.0551** at two trials, a factor of **1.0019**, and every arm reads **higher** -- **+0.0240**, **+0.0253** and
**+0.0312** at **3.38** to **5.93** sigma.*

## 1. The run and the instrument

`e495`'s own command at three trials instead of two -- the same read, the same placement, the same world and the same
boundary channel.

| the arm | the three-trial run's accuracy diagonal | the two-trial run's | the change | sigma | the three-trial run's last row | the two-trial run's |
|---|---|---|---|---|---|---|
| `naive` | **0.8538** | 0.8299 | **+0.0240** | **+3.78** | **0.6162** | 0.5900 |
| `ewc-block` | **0.8392** | 0.8139 | **+0.0253** | **+3.38** | **0.6118** | 0.5893 |
| `replay` | **0.8580** | 0.8267 | **+0.0312** | **+5.93** | **0.6135** | 0.5870 |

and the label's own part of the read at the last step, at the card's own body with deterministic cues and the
episode's other symbols held fixed -- one width, one read, one placement, two splits:

| the pass | the across-symbol spread | the read's own scale | the spread as a share of the scale |
|---|---|---|---|
| **two trials**, one distractor after the label | 4.2967 | 4.0724 | **1.0551** |
| **three trials**, two distractors after it | **4.3099** | 4.0771 | **1.0571** |

| claim | measured | verdict |
|---|---|---|
| NB1 the pass's split is the one flag moved | **0** config fields differing past the inert rule with `loop_episode` the one moved, the draw **26** fields with **0** differing and `episode_len` moving `[2, 3]`, **20** replicates | **MET** |
| NB2 the label keeps its place in the read under one more cue | **1.0551** at two trials against **1.0571** at three -- a factor of **1.0019**, the spreads **4.2967** and **4.3099** | **MET** |
| NB3 the pass is still learned with two distractors | the diagonals are **0.8538**, **0.8392** and **0.8580** against a chance of **0.25**, changes of **+0.0240**, **+0.0253** and **+0.0312** at **+3.78**, **+3.38** and **+5.93** sigma, with **3** of three arms over the bar and **0** within **0.05** of chance | **MET** |

## 2. What it says

**The split is one flag over one read, one placement, one world and one boundary channel.** **0** config fields past
the inert rule, the draw agreeing on all **26** fields except `episode_len` itself, and the read, the placement and
the channel the same in both runs. **So the pass's shape is what moved and nothing else.**

**And the label's place in the read is not affected by a second cue at all.** **1.0551** against **1.0571** -- a
factor of **1.0019** -- with the spreads **4.2967** and **4.3099** and the scales **4.0724** and **4.0771**. **So the
recurrence that holds the label holds it across the second distractor exactly as across the first**, which is the
reading `e495` established at the smallest pass extended by one rung: the label's part of the read is a function of
**where** the label is and not of how much follows it.

**And the pass is not merely held: it is learned a little better.** Every arm reads **higher** at three trials --
**+0.0240**, **+0.0253** and **+0.0312** at **+3.78**, **+3.38** and **+5.93** sigma -- and every arm's last row rises
with it (**0.6118** to **0.6162** against **0.5870** to **0.5900**). **So one more cue in the same window costs the
label first nothing and buys it two to three hundredths**, which is the opposite of crowding and is what the second
rung of the sweep `e495` and `e496` both named as open says. *What the second cue adds is not measured here: the pass
carries one more example of the label's own drive pattern through the same eleven steps, and whether that is the
mechanism or the longer training signal is a different unit.*

**And the card's clause is a family and not a point.** `e496` wrote the label-first pass into the card as the
configuration the episode's label has to be in, read from the two-trial runs; this unit says the same clause holds at
three trials -- the same read, the same placement, a second distractor, and **0.8392** to **0.8580** against the
two-trial **0.8139** to **0.8299**. **So the working episodic mode is the pass's label being first**, with the pass's
length a free parameter at least over the two rungs measured, and the revision that carries the second rung is the
next unit and not this one.

## 3. What it cannot do

- **One rung**: three trials against two, with the four- and six-trial splits and the passes whose label is at an
  interior trial not in it.
- **And the split moves two things**: one more trial is one more **cue** and a shorter **trial**, and no split of a
  fixed twelve-step pass separates them, so the **+0.024** to **+0.031** is the pass's shape and not a crowding
  constant.
- **And the instrument is at an untrained body**: a share is where a body that has never been trained puts the label,
  and the trained arms are the measurement.
- **And one read**: the model's own thirty-two columns, which `e493` showed is the better of the corpus's two, with
  the world's eight numbers at three trials not measured.
- **And one budget, one world and one seed stream**: the card's own setting, so the two to three hundredths are one
  configuration's and a redraw would have to beat the corpus's own arm spread.
