# The representation's retention matrix: the world forgets 0.2406 where the head forgets 0.4188, and the buffer cuts the world's loss to 0.0625

*2026-10-03. `experiments/e381_the_representations_retention_matrix.py` reads the bodies `e379` and `e380` saved and
rolls **every** task's examples against **every** checkpoint -- the connectome's own weights and then the body after
each of the three tasks -- with the corpus's own probe fitted on the world's final state. No new run: the columns
those two units did not read were on disk. Twenty seconds; the reader is
`runs/e381_the_representations_retention_matrix.json`. Five claims, registered before any of these cells was opened.*

## 1. Two matrices, and the head's beside them

The wide step, `cue@0`, action source, `naive` -- rows are the body's state, columns the task, and the last three
rows are the same matrix as the **head** saw it:

| body | task 0 | task 1 | task 2 |
|---|---|---|---|
| initial | 0.6875 | 0.6250 | 0.7083 |
| after task 0 | **0.7729** | 0.6208 | 0.5312 |
| after task 1 | 0.6021 | **0.7771** | 0.5771 |
| after task 2 | 0.5323 | 0.6271 | **0.8063** |
| head after 0 | 0.7427 | | |
| head after 1 | 0.5625 | 0.5208 | |
| head after 2 | **0.3240** | 0.3750 | 0.8333 |

The tight step, `cue@8`, same source and arm:

| body | task 0 | task 1 | task 2 |
|---|---|---|---|
| initial | 0.6875 | 0.6458 | 0.6458 |
| after task 0 | 0.2083 | 0.2083 | 0.2917 |
| after task 1 | 0.2083 | 0.2083 | 0.2917 |
| after task 2 | 0.2083 | 0.2083 | 0.2917 |
| head after 2 | 0.2083 | 0.2083 | 0.2500 |

| claim | measured | verdict |
|---|---|---|
| R1 the diagonal is what the two units recorded | **0.0000** apart on both runs | **MET** |
| R2 the representation forgets | task 0: **0.7729** to **0.5323**, a drop of **+0.2406** on a sem of **0.0236** | **MET** |
| R3 the world forgets at least what the head forgets | world **+0.2406**, head **+0.4188**, a difference of **-0.1781** on a sem of **0.0327** | **FALSIFIER FIRED** |
| R4 nothing to forget at the tight step | **+0.0000** on a sem of **0.0000** | **MET** |
| R5 the buffer changes the world's forgetting | **0.2406** under `naive`, **0.0625** under `replay` | **MET** |

## 2. What the fired claim says

**The head forgets what the world still holds.** Task 0's label is recoverable from the trained body at the end of
the sequence at **0.5323**, and the head that was trained through all three tasks reads **0.3240**. The head loses
**0.4188** over the sequence where the world loses **0.2406**: **0.1781** of the head's forgetting is the head's and
not the world's.

**And that puts `e380`'s saturation claim in its place.** That unit found the probe and the head agreeing on the
**diagonal** -- what a task reads at the checkpoint where it was learned -- and fired its claim that the probe beats
the head. This matrix says the agreement is a property of that checkpoint: **the head is saturated at learning and
not at retention.** The two instruments read the same number when the task is fresh and diverge as the sequence goes
on, which is exactly the off-diagonal.

**And the buffer protects the representation, not only the head.** `replay`'s world keeps task 0 at **0.7104** where
`naive`'s keeps it at **0.5323** -- a drop of **0.0625** against **0.2406**, paired at a sem of 0.0239. So `e276`'s
replay-over-penalty result, which this line has now replicated on four substrates, has a counterpart in the world:
the arm that forgets less in accuracy also forgets less in what a linear fit can recover from the body.

## 3. What the two matrices say that the claims did not ask for

**The connectome's own weights already carry all three labels at the wide step, and one task's training destroys that
at the tight step.** The initial body reads **0.6875, 0.6250 and 0.7083** at `cue@0` and **0.6875, 0.6458, 0.6458**
at `cue@8` -- all far above a chance of 0.25 and all *before* any training. At the wide step the training improves
each diagonal to 0.77 to 0.81, which is the **+0.1118** `e380` measured. At the tight step it takes the same three
labels to **0.2083** in one task's worth of training, which is the **0.4236** `e379` measured, and from there the
matrix is **frozen**: after task 1 and after task 2 it is the same three numbers, because there is nothing left to
lose. **The tight step's failure is not forgetting; it is a single collapse during the first task's training that
never recovers and never worsens.**

**And the matrices have the shape the corpus's own metric assumes.** The diagonal rises as each task is learned
(0.7729, 0.7771, 0.8063) and the off-diagonal falls, so the corpus's retention matrix is not an artefact of reading
through a head: the representation does the same thing.

**Reported and not claimed**: R3's **-0.1781** and R5's **-0.1781** are numerically the same figure at the fourth
decimal and are not the same quantity -- one is the world's naive drop against the head's, the other the world's
`replay` drop against the world's `naive` one. The raw accuracies move in steps of 1/48, so this is an arithmetic
coincidence of the grid and is written down because a reader will notice it.

## 4. What it cannot do

*Two cells, one draw*: the action source at `cue@0` and at `cue@8` on this draw, so the cue source and the steps
between are not measured and `e370` showed the boundary moves with the draw. *And a probe is not a mechanism*: a cell
of this matrix says how much of a task's label a linear fit recovers from the world's eight numbers at that point in
the sequence, so "the head forgets 0.1781 the world still holds" is about recoverability and not about what the
recurrent weights changed. *And four checkpoints are four*: the bodies are kept at task boundaries, so nothing here
says how the world moved inside a task -- and the tight step's collapse is exactly the case where that matters, since
the matrix cannot tell a collapse in the first few iterations from one spread across all five hundred.
