# The read the world loses: the model's own columns are worth five to seven hundredths and not the task

*2026-10-11. `experiments/e493_the_read_the_world_loses.py` swaps the read inside the episode: `e492`'s own command
with `--readout-from-world` **off**, so the head reads the model's own thirty-two neurons at the last step instead of
the world's eight. **JB1 MET and JB2 and JB3 both FIRED** -- every arm gains **0.0521** to **0.0698** at **4.07** to
**7.29** sigma over the same episode's world read, and every arm is still short of the four-class chance by more than
the bar.*

## 1. The run, the shares and the corpus's own read

`e492`'s command at two trials with `--loop-episode 2 --loop-boundary`, once reading the world's eight numbers and
once reading the model's thirty-two.

| the arm | the model-read run's accuracy diagonal | the world-read run's | the change | sigma | the model-read run's last row | the world-read run's |
|---|---|---|---|---|---|---|
| `naive` | **0.3104** | 0.2434 | **+0.0670** | **+7.00** | **0.2892** | 0.2507 |
| `ewc-block` | **0.2944** | 0.2424 | **+0.0521** | **+4.07** | **0.2802** | 0.2583 |
| `replay` | **0.3031** | 0.2333 | **+0.0698** | **+7.29** | **0.2896** | 0.2420 |

and the label's own part of the read, at the card's own body with the cues deterministic and the earlier trials held
fixed, at the two trials this unit runs and at one trial beside it:

| the pass | the read | the across-symbol spread | the read's own scale | the spread as a share of the scale | the width |
|---|---|---|---|---|---|
| two trials | the world's | 0.0377 | 0.6600 | **0.0571** | 8 |
| two trials | the model's | **0.1648** | 4.2687 | **0.0386** | 32 |
| one trial | the world's | 0.9144 | 0.6232 | **1.4673** | 8 |
| one trial | the model's | 4.2793 | 4.0780 | **1.0494** | 32 |

and the corpus's own two one-trial readings of this world, carried beside them: `e438` at the world's eight
(**0.7691**, **0.7073**, **0.7389**) and `e455` at the model's own thirty-two (**0.8642**, **0.8559**, **0.8503**).

| claim | measured | verdict |
|---|---|---|
| JB1 the read is the one flag moved | **0** config fields differing past the inert rule with `readout_from_world` the one moved, the draw **26** fields with **0** differing, the read-out's own draw the same subset of the same seed at both, **20** replicates | **MET** |
| JB2 the label is in the model's own columns | at two trials the world's share is **0.0571** and the model's **0.0386**; at one trial **1.4673** and **1.0494** | **FALSIFIER FIRED** |
| JB3 the label comes back when the head reads the model | the diagonals are **0.3104**, **0.2944** and **0.3031** against **0.25**, with **0** of three arms over the bar and `ewc-block` within **0.05** of chance | **FALSIFIER FIRED** |

## 2. What it says

**The read is the one flag moved, over one world and one boundary channel.** **0** config fields past the inert rule,
the environment's draw agreeing on all **26** fields, and the read-out's own draw -- the same size, the same seed and
the same subset fingerprint -- identical in the two runs. **So the two runs differ in which numbers the head sees and
in nothing else**, which is what makes the gains below the head's and not the world's.

**And the model's own columns are worth five to seven hundredths, at four to seven sigma.** Every arm gains --
**+0.0670**, **+0.0521** and **+0.0698** -- and the corpus's two one-trial readings say the same thing at the
corpus's own pass: the model's thirty-two beat the world's eight by **0.0951**, **0.1486** and **0.1114** there.
**So the read is a bottleneck and the world's eight numbers are where the episode's label is lost first** -- and it is
not *the* bottleneck, because every arm is still between **0.2944** and **0.3104** where the bar is **0.35**, and
`ewc-block` does not clear chance by the width the unit registered against.

**And the share that ranked the splits does not rank the reads.** The instrument that measured the label's part of the
world's state across `e489`'s, `e492`'s and this unit's passes says the **world's** read carries the larger *share* at
both lengths -- **0.0571** against **0.0386** at two trials and **1.4673** against **1.0494** at one -- while the
accuracy says the model's read is better at both, by **0.0521** to **0.0698** here and by **0.0951** to **0.1486**
there. **So the firing of JB2 is a fact about the instrument and not about the read**: a head reads a vector's
*displacement* and not its share of the vector's norm, and a share is a scale-free quantity that is not a
dimension-free one -- thirty-two columns carry more of everything, including more of the past. *This is the first
instrument in this line whose ranking disagrees with the training, and the disagreement is the useful part.*

**And three exclusions now stand beside a partial fourth.** `e491` removed the world's share of the earlier trials
exactly and the accuracy did not move; `e492` lengthened the label's window and thinned the episode and the accuracy
did not move; this unit handed the head the model's own state and the accuracy moved -- by a twentieth of the task and
not into it. **So the episode is not paying for its split, its carry or its read alone**: what is left is the pass's
own shape, a label that reaches the read through three to five steps of recurrence however wide the read is, and
`e455`'s own reading says the same read at one trial is where the corpus's **0.86** lives.

## 3. What it cannot do

- **One episode length and one read**: two trials against the corpus's one, and thirty-two model neurons against
  eight world numbers, with the widths the corpus's own flags fix.
- **And two things change with the read**: its **source** and its **width**, and no flag separates them -- `e458`'s
  eight model neurons are the same source at the world's width, and are one trial's.
- **And the instrument is at an untrained body and the wrong denominator**: the share is scale-free and not
  dimension-free, so its firing here is a reading of the instrument and the trained gains are the reading of the read.
- **And one budget, one world and one seed stream**: the card's own setting, so the five to seven hundredths are one
  configuration's.
- **And the bar was registered in advance**: every arm is **0.0521** to **0.0698** short of learning the task, and what
  a longer budget, a wider head or a read taken at every trial would buy is a different unit.

## RE-READ 2026-10-11

**The read is a bottleneck the loop is not.** This unit closed on *what is left is the pass's own shape, a label that reaches the read through three to five steps of recurrence however wide the read is*, and `e494` sharpened it by taking the loop out entirely: the label's own part of the read **doubles** without the world (**0.0386** to **0.0895**, in absolute spread **0.1648** to **0.3600**) and every arm **loses** -- **-0.0306**, **-0.0208** and **-0.0292** at **-3.03**, **-1.85** and **-2.87** sigma. So the read this unit moved is worth **+0.0521** to **+0.0698** and the loop this unit left wired is worth **+0.0208** to **+0.0306** against its own removal, which makes the closed loop a small asset and the pass the cost. This unit's numbers stand.
