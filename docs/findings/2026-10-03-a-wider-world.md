# A wider world at the tight step: it starts higher and ends at the same floor, so the read-out's width buys nothing the update spares

*2026-10-03. `experiments/e386_a_wider_world.py` runs `e379`'s cell with `--loop-world-dims 32` -- the action source
at `cue@8`, the corpus's larger rate, twenty replicates, the body kept -- and reads the world before training and
after task 0 with the corpus's own probe on all thirty-two numbers, against that unit's readings for the
eight-dimensional world at the same cell. 1125 s; the reader is `runs/e386_a_wider_world.json`. Five claims,
registered before the run's reading was opened.*

## 1. The two widths

| cell | 32-dimensional world, task 0 | 32 dimensions, mean over tasks | 8-dimensional world, task 0 |
|---|---|---|---|
| connectome's own weights | **0.7500** | 0.6944 | 0.6597 |
| after task 0 | **0.2115** | 0.2413 | 0.2361 |
| trained head | 0.2083 | 0.2778 | 0.2437 |

chance 0.2500.

| claim | measured | verdict |
|---|---|---|
| G1 one configuration except the world's dimension | `loop_world_dims`, the three world draws, **and `task_readout_widths`** | **FALSIFIER FIRED** |
| G2 the wider world is live at this step | **+0.5000** over chance | **MET** |
| G3 a wider read-out survives the collapse | **0.2115**, which is **0.0385 below** chance | **FALSIFIER FIRED** |
| G4 it beats the narrow world's floor | **-0.0247** against 0.2361 | **FALSIFIER FIRED** |
| G5 the head tracks the world down here too | **+0.0031** apart | **MET** |

## 2. What fired, and what it answers

**A wider read-out does not survive the collapse.** The claim was that a thirty-two-number world keeps at least 0.10
above chance where an eight-number one is emptied; it reads **0.2115**, which is **below** chance, and it is
**0.0247 below** the narrow world's floor rather than 0.10 above it. Both claims fired against the prediction, and
their direction is the same: **the update takes the label out of a wide world as completely as out of a narrow one.**

**And the width does buy something before the update.** The connectome's own weights read **0.7500** on the
thirty-two-number world against **0.6597** on the eight-number one, so a linear fit recovers **0.0903 more** of task 0
from the wider world at the frozen level -- which is `e286`'s read-out axis appearing as a property of the **world the
agent acts in** rather than of a decoder. What the update costs is then larger in absolute terms, **0.5385** against
**0.4236**, because there was more to lose; where it ends is the same floor either way.

**So the tight step's failure is not the read-out's narrowness.** That is the answer to the question this unit was
built for, and it separates the two halves of this line's story about width: the width sets **how much of the label a
probe recovers from an untrained body**, and it does not set **whether training keeps it**. The first is `e286`'s
variable; the second is the drive's timing at `cue@8`, which `e369` and `e370` priced and `e382` found destroyed in
one update.

**And the head tracks the world down at this width too.** The trained head reads **0.2083** against the probe's
**0.2115**, **0.0031** apart -- the third cell in which the two agree once the body has been trained, after `e379`
at 8 dimensions and `e380` at the wide end. So the agreement is a property of this training and not of the width.

## 3. The field list this unit got wrong

**G1 fired because my registration named three fields the dimension moves and there are four.** The world's
dimension is the head's input width -- the runner sets every task's `readout_neurons` to
`arange(loop_world_dims)` when the read-out is the world -- so **`task_readout_widths` follows from the manipulation
by construction**, and the measurement reports it as a difference in the configuration. What fired is the **list**
and not the configuration: the run differs from `e379`'s in the dimension and in the four fields that follow from it,
which is one configuration with consequences, and the claim's falsifier was written for consequences I had not
enumerated. **This is the third time in three units** -- `e381`'s head-row field, `e383`'s missing learning rate, and
now this -- that the defect has been an incomplete field list, and the lesson is cheap to state and easy to forget:
**a configuration check is only as strong as the list it is given, and the list has to include every consequence of
the manipulation, including the ones the runner's own code makes.**

## 4. What it cannot do

*One width against one other*: eight against thirty-two, so a trend is not established and a third width is a run of
its own -- and the direction is open, since a wider world starts higher and ends lower. *And the draws follow the
manipulation*: the drive map, the read map and the coupling matrix all change with the dimension, so this is two
worlds and not one world read two ways, which is the limit `e363`'s source manipulation had as well. *One cell, one
source, one draw*: the action source at `cue@8` at the corpus's larger rate, so the wide end and the cue source are
not compared at this width. *And a probe is not a mechanism*: 0.2115 says a linear fit recovers nothing of task 0
from the world's thirty-two numbers, not that the label is absent in every form.
