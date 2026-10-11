# The episode without the world: taking the loop out doubles the label's share and lowers the accuracy

*2026-10-11. `experiments/e494_the_episode_without_the_world.py` runs `e493`'s own command with `--no-feedback` on,
so the episode's two cues reach the model through the input and nothing comes back. **KB1 and KB2 MET and KB3's
falsifier FIRED**: the label's own part of the read goes from **0.0386** to **0.0895** when the loop is out, and
every arm's accuracy goes **down**, not up.*

## 1. The run and the instrument

`e493`'s command at two trials -- the model's own thirty-two columns at the last step -- with the loop wired and with
it unwired.

| the arm | the unwired run's accuracy diagonal | the wired run's | the change | sigma | the unwired run's last row | the wired run's |
|---|---|---|---|---|---|---|
| `naive` | 0.2799 | 0.3104 | -0.0306 | -3.03 | 0.2865 | 0.2892 |
| `ewc-block` | 0.2736 | 0.2944 | -0.0208 | -1.85 | 0.2795 | 0.2802 |
| `replay` | 0.2740 | 0.3031 | -0.0292 | -2.87 | 0.2698 | 0.2896 |

and the label's own part of the read at the last step, at the card's own body with deterministic cues and the earlier
trials held fixed -- **one width, two worlds**, which is the comparison this instrument can make:

| the read | the across-symbol spread | the read's own scale | the spread as a share of the scale |
|---|---|---|---|
| the model's thirty-two, **loop wired** | 0.1648 | 4.2687 | **0.0386** |
| the model's thirty-two, **loop unwired** | **0.3600** | 4.0237 | **0.0895** |

| claim | measured | verdict |
|---|---|---|
| KB1 the loop is the one flag moved | **0** config fields differing past the inert rule with `no_feedback` the one moved, the draw **26** fields with **0** differing, **20** replicates | **MET** |
| KB2 the label's part of the read survives without the world | **0.0386** wired against **0.0895** unwired, the spreads **0.1648** and **0.3600** | **MET** |
| KB3 without the world the label comes back | the diagonals are **0.2799**, **0.2736** and **0.2740** against **0.25**, all **three** within **0.05** of chance and below the wired run's | **FALSIFIER FIRED** |

## 2. What it says

**The loop is one flag and one world.** **0** config fields past the inert rule, the environment's draw agreeing on
all **26** fields -- the same world built, the same two trials, the same boundary channel -- and one of the two runs
does not wire it. So the difference below is the feedback channel's and nothing else's.

**And taking the loop out doubles what the label is worth in the read.** The label's own part of the model's read at
the last step goes from **0.0386** to **0.0895** of that read's scale -- **2.3 times** -- and in absolute terms from
**0.1648** to **0.3600**. **So the world's feedback is what compresses the label** and the loop-less pass carries more
of it, which is the one direction this unit's own question could have gone to make the loop the culprit.

**And the accuracy does not come back, it falls.** Every arm is **lower** without the world -- **0.0306**, **0.0208**
and **0.0292** at **-3.03**, **-1.85** and **-2.87** sigma -- and all three stay within **0.05** of the four-class
chance. **So the closed loop is worth something and the episode is what costs**, which is the opposite of what the
instrument alone would have suggested: a read that carries **2.3 times** more of the label buys **no** accuracy at
all. *The feedback is a regulariser here and not a distorter -- a world that answers the agent's own action is
teaching the network something the labels are not.*

**And the pass's four parts are now all measured, and none of them is the cause.** `e491` removed the world's share
of the earlier trials exactly and the accuracy did not move; `e492` lengthened the label's window and thinned the
episode and it did not move; `e493` handed the head the model's own columns and every arm gained **0.0521** to
**0.0698** at four to seven sigma without reaching the bar; and this unit removed the world entirely and every arm
**lost** **0.0208** to **0.0306**. **So the cost is the episode as a pass** -- a label that is one of two cues in the
same twelve steps, with a distractor trial's worth of drive and the whole of the recurrence between it and the read --
and the corpus's own one-trial runs (**0.76** to **0.86** with the loop wired) are what a pass with one cue and no
distractor looks like. **The loop, the carry, the split and the read are each worth something and none of them is
what the episode is paying.**

## 3. What it cannot do

- **No world is not a world**: with `--no-feedback` the head reads the model and the environment's state is never
  consulted, so this is the corpus's loop-less reading and not a game.
- **And two things change with the flag**: the feedback channel and, through the runner's own rule, the read's
  source -- which `e493` moved once already; the comparison here is between runs whose reads are the same and whose
  worlds are not.
- **And the instrument is at an untrained body**: a doubled share is where a body that has never been trained puts
  the label, and the direction the trained arms went is the measurement.
- **And one episode length, one read and one budget**: two trials of six steps, the model's thirty-two columns and
  the card's own world, budget and seed stream.
- **And the pass's shape is not swept**: a label first and a distractor after, a third cue, a longer pass and a read
  at every trial are four different passes and none of them is here.

## RE-READ 2026-10-12

**The first of the four passes this unit named is measured, and it is learned.** This unit closed on *a label first and a distractor after, a third cue, a longer pass and a read at every trial are four different passes and none of them is here*. `e495` supplies the first: the label at the pass's first trial, with the same read, the same world, the same two trials and the same distractor, reads **0.8299**, **0.8139** and **0.8267** where this unit's own pass reads **0.3104**, **0.2944** and **0.3031** -- changes of **+0.5194**, **+0.5194** and **+0.5236** at **+62.79**, **+40.52** and **+48.18** sigma. So the pass's shape this unit left as the cost is the label's **position**, worth half the task, and a third cue, a longer pass and a read at every trial are the parts still unmeasured. This unit's numbers stand.
