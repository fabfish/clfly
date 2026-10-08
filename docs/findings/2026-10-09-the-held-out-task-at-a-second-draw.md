# The held-out task at a second draw: the level is the sample's and the change is the task's

*2026-10-09. `experiments/e473_the_held_out_task_at_a_second_draw.py` reads the held-out task at a **second draw** of it:
the runner's held-out cue set is built with a seed of its own (`--loop-holdout-seed`, defaulting to the suite's own
length, which is what every artifact written before the flag carries), so two more rolls at the same hundred updates and
the same head redraw its **examples and cue noise** and nothing else. Four claims, all four **MET**.*

## 1. The two draws

| the draw and roll | the initial body | the trained body | the change | sigma | the anchor | sigma | the buffer | sigma |
|---|---|---|---|---|---|---|---|---|
| **3**, `bio` | **0.6875** | **0.7594** | **+0.0719** | **4.89** | -0.0396 | -1.76 | -0.0156 | -0.90 |
| **3**, `rand` | **0.6875** | **0.7594** | **+0.0719** | **4.89** | -0.0146 | -0.73 | -0.0156 | -0.90 |
| **7**, `bio` | **0.5625** | **0.6312** | **+0.0688** | **5.77** | -0.0240 | -1.16 | -0.0125 | -0.70 |
| **7**, `rand` | **0.5625** | **0.6312** | **+0.0688** | **5.77** | **+0.0323** | **+1.50** | -0.0125 | -0.70 |

| the two draws, paired across the replicates they share | difference | sigma |
|---|---|---|
| the baseline's **change** | **-0.0031** | **-0.19** |
| the baseline's initial reading | **-0.1250** | |
| the baseline's trained reading | **-0.1281** | |

| claim | measured | verdict |
|---|---|---|
| ZA1 the new flag draws the held-out task and nothing else | **104** fields compared, seeds **3** and **7**, **6 of 6** trained arms bit-identical between the draws | **MET** |
| ZA2 and the sequence raises the decodability at the second draw too | **+0.0719** at **4.89** sigma and **+0.0688** at **5.77** | **MET** |
| ZA3 and the two draws agree | **-0.0031** at **-0.19** sigma | **MET** |
| ZA4 and the anchoring does not move it at either draw | **-1.76** to **+1.50** sigma | **MET** |

## 2. What the second draw says

**The level of the held-out reading is the sample's and the change is the task's, and that is the sharpest thing this
line has said about its own held-out task.** The two draws put the **initial** body at **0.6875** and **0.5625** -- the
second cue set is a fifth of the way harder for a body that has not trained on anything -- and the trained body at
**0.7594** and **0.6312**, **0.1281** apart. The **changes**, though, are **+0.0719** and **+0.0688**: **-0.0031** apart
at **0.19** sigma. **So every number this line has published about its held-out task is a level and one of them is a
draw's**, and the sentence *the sequence raises the unseen cue set's decodability by 0.0844* is the task's in a way the
sentence *the probe reads 0.7719* is not.

**And every finding of this line has closed on the same bullet, which this measurement closes.** `e469`, `e471` and
`e472` each end by saying that the held-out cue set is the flag's own draw and that a redraw of it is not measured; the
redraw is measured here, and what it moves is the level and not the change.

**And the flag draws the held-out task and nothing else, arm by arm.** All **104** compared config fields agree except
the held-out seed, the output path and the saved weights, the seeds are **3** and **7**, and the sequence's own
replicates are **bit-identical** between the two draws: `naive`, the anchor and `replay` on both rolls, six of six arms,
record for record. **So the held-out task is a fourth cue set whose own draw is independent of the world, the suite and
the training** -- which is what makes the bullet's closure a measurement rather than an argument.

**And the anchoring is a null at both draws with its sign moving between them.** `ewc-block` is **0.0396** below the
baseline at **-1.76** sigma at the first draw and **0.0240** below at **-1.16** at the second, and
`ewc-block-rand` is **0.0146** below at **-0.73** and **0.0323** **above** at **+1.50** -- so the partition's cost on a
task outside the sequence changes sign between two draws of that task and resolves at neither, which is the `basis`
clause's null read a fifth time.

**And the second draw is hard for the initial body in a way the first is not, and both are well above chance.**
**0.5625** against **0.6875**, four classes so a chance of **0.25**: the unseen cue set is legible to an untrained body
either way, and what the two draws share is what the sequence adds to it.

## 3. What it cannot do

- **Two draws are not a population**: the reading's spread over the family of fourth cue sets is estimated from two of
  them, so **0.1281** between their levels is one difference and a third draw could sit anywhere the two do not.
- **And a probe is not a task**: both draws are of **linear readability** from the frozen body.
- **And one ridge**: **1e-2** is `e469`'s, and a different one would move every level here.
- **And one budget**: both draws are at a hundred updates, so the crossings `e467` and `e468` found on the sequence's own
  diagonal are not measured at either draw.
- **And a redraw is not a new task**: the fourth cue set is the same four symbols in the same world with its own
  examples, so *another draw* means another sample of one task and not another task.
