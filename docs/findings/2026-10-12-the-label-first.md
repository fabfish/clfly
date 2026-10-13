# The label first: the pass's cost was the label's window, and the episode works

*2026-10-12. `experiments/e495_the_label_first.py` moves the cue the label names from the episode's **last** trial to
its **first** and puts the episode's other symbol after it, so the label's window is the whole twelve-step pass
instead of five steps. **LB1, LB2 and LB3 all MET**: the label's own part of the read goes from **0.0386** to
**1.0551**, and every arm's accuracy goes from the four-class chance to **0.81** to **0.83**, at **40.52** to
**62.79** sigma.*

## 1. The run and the instrument

`e493`'s command at two trials -- the model's own thirty-two columns at the last step -- with the label placed last
and placed first.

| the arm | the label-first run's accuracy diagonal | the label-last run's | the change | sigma | the label-first run's last row | the label-last run's |
|---|---|---|---|---|---|---|
| `naive` | **0.8299** | 0.3104 | **+0.5194** | **+62.79** | **0.5900** | 0.2892 |
| `ewc-block` | **0.8139** | 0.2944 | **+0.5194** | **+40.52** | **0.5893** | 0.2802 |
| `replay` | **0.8267** | 0.3031 | **+0.5236** | **+48.18** | **0.5870** | 0.2896 |

and the label's own part of the read at the last step, at the card's own body with deterministic cues and the
episode's other symbol held fixed -- **one width, one world, two placements**:

| the placement | the across-symbol spread | the read's own scale | the spread as a share of the scale |
|---|---|---|---|
| the label **last** (step 6, five drive steps to the read) | 0.1648 | 4.2687 | **0.0386** |
| the label **first** (step 0, the whole pass to the read) | **4.2967** | 4.0724 | **1.0551** |

| claim | measured | verdict |
|---|---|---|
| LB1 the placement is the one flag moved | **0** config fields differing past the inert rule with `loop_label_first` the one moved, the draw with `['label_first']` added and **0** differing, **20** replicates | **MET** |
| LB2 the label's part of the read grows when its window does | **0.0386** last against **1.0551** first, the spreads **0.1648** and **4.2967** | **MET** |
| LB3 the label comes back when it gets the pass | the diagonals are **0.8299**, **0.8139** and **0.8267** against **0.25**, with **3** of three arms over the bar and **0** within **0.05** of chance | **MET** |

## 2. What it says

**The placement is one flag over one world, one pass and one read.** **0** config fields past the inert rule, the
draw adding `label_first` and disagreeing in nothing else, and the two runs carrying the same read, the same episode
length and the same boundary channel. **So the numbers below are the label's step and nothing else**, which is what
the four units before this one were designed to make possible.

**And the label's own part of the read goes up by a factor of twenty-seven.** **0.0386** against **1.0551** -- and a
share above one is the corpus's own single-trial reading (**1.4673**), where the read *is* the label's response.
**So the label is as present in a two-trial pass read first as it is in a one-trial pass**, and the same instrument
that could not rank the reads (`e493`'s second claim fired on the model against the world) ranks the placements and
agrees with the training this time: what the instrument measures here is a window and not a width.

**And the pass is learned, at 0.81 to 0.83.** Every arm clears the bar by more than half the task -- **+0.5194**,
**+0.5194** and **+0.5236** at **62.79**, **40.52** and **48.18** sigma -- where the same pass with the label last
sat at the four-class chance, and the corpus's own one-trial runs read **0.76** to **0.86**. **So the episode's cost
was the window its label got and not the pass**: `e489` measured the last trial's label as unreadable, `e491` to
`e494` removed the carry, the split, the read and the loop and none of them was the cause, and **where the label sits
is worth half the task**.

**And it is the trajectory and not the recency.** The label first is the **oldest** cue in the pass -- a distractor
arrives after it and the read is eleven steps from it -- and it is the one that survives, while the label last, five
steps from the read and the newest cue in the pass, is the one that does not. **So what a cue needs here is a
**trajectory long enough for the recurrence to hold it while the rest of the pass goes by** -- which is the corpus's
own single-trial situation extended by one distractor, and not the shortest gap to the read. **And it makes the
benchmark's episodic mode work**: a two-trial episode whose label is its first cue is learned at **0.82** across all
three arms, and that is one flag from the card's own roll.

**And the pass's five parts have now each been moved alone.** The carry (`e491`, removed exactly, no change), the
split and its window (`e492`, five steps against three, no change), the read (`e493`, **+0.0521** to **+0.0698**),
the loop (`e494`, **-0.0208** to **-0.0306** against its removal) and **the label's position (this unit,
**+0.5194** to **+0.5236**)**. **Four of the five are worth less than a tenth of the task and the fifth is worth
half of it**, and the one that is worth half is the one no unit in this line had moved.

## 3. What it cannot do

- **One placement pair and one episode length**: first against last at two trials of six steps, with the three-cue,
  four-cue and longer passes not in it.
- **And the placement and the window are the same flag**: the first trial is the longest window a two-trial pass has,
  so a window of three or four trials is a different pass and not a separable axis here.
- **And one read**: the model's own thirty-two columns, which `e493` showed is the better of the corpus's two; the
  world's eight numbers at the label's first trial are not measured.
- **And the payout is not on these runs**: the runner refuses `--loop-label-first` with `--loop-reward`, since the
  environment's target is read off the pass's last cue.
- **And one budget, one world and one seed stream**: the card's own setting, so **0.82** is one configuration's --
  and the corpus's single-trial runs span **0.76** to **0.86** across their arms, which is the width a redraw would
  have to beat.

## RE-READ 2026-10-12

**The pass's length is a free parameter at least to three trials.** This unit's *cannot do* closed on *the placement and the window are the same flag, so a window of three or four trials is a different pass and not a separable axis here*. `e497` takes that different pass -- three trials of four steps, the label at step **0** and its distractors at steps **4** and **8** -- with the same read, the same placement, the same world and the same boundary channel, and every arm reads **higher**: **0.8538**, **0.8392** and **0.8580** against this unit's **0.8299**, **0.8139** and **0.8267**, changes of **+0.0240**, **+0.0253** and **+0.0312** at **+3.78**, **+3.38** and **+5.93** sigma, while the label's own part of the read is unchanged (**1.0551** against **1.0571**, a factor of **1.0019**). So the placement is not a property of the smallest pass, and the four- and six-trial splits are the rungs above it. This unit's numbers stand.

## RE-READ 2026-10-12

**The refusal is gone and the paid pair is one flag.** This unit's *cannot do* closed on *the payout is not on these runs: the runner refuses `--loop-label-first` with `--loop-reward`, since the environment's target is read off the pass's last cue*. `e498` makes the target follow **the cue the label names** -- step **1** with the label first and **7** with it last at two trials -- and the pair runs: the rewarded pass agrees with this unit's own on every `learned` and `final_per_task` vector **record for record**, so the payout does not touch the training, and the label-first target moves by **exactly 0** when the episode's other symbols are redrawn. This unit's placement has the last cue as its label, so its own target step is the one it always was, and its numbers stand.

## RE-READ 2026-10-13

**The placement is an axis, and its interior is measured.** This unit's *cannot do* closed on *one placement pair and one episode length ... the placement and the window are the same flag*. `e505` puts the label's cue at trial **0**, **1** and **2** of the same three-trial pass with the runner's new `--loop-label-at` and moves nothing else: the pass reads **0.8538**, **0.8392** and **0.8580** with the label first, **0.3257**, **0.3069** and **0.3274** at trial **1** and **0.2566**, **0.2576** and **0.2542** at trial **2**, the end-to-end move **+0.5972**, **+0.5816** and **+0.6038** at **+74.23**, **+66.33** and **+88.97** sigma, and the label's own part of the read **1.0571** against **0.0489** and **0.0314**. So the pair this unit moved -- the label first against the label last -- is the working end of a step, and at three trials the only placement that works is the pass's first. This unit's numbers stand.
