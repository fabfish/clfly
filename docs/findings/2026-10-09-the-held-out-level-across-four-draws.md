# The held-out level across four draws: the change is the draw's too, and two draws agreed by coincidence

*2026-10-09. `experiments/e474_the_held_out_level_across_four_draws.py` draws the held-out cue set twice more -- seeds
**11** and **19** at the same hundred updates and the same head, both anchors -- and reads all four draws together.
**AA1 and AA4 MET** and **AA2 and AA3 both FIRED**.*

## 1. The four draws

| the draw | the baseline's initial body | its trained body | its change | sigma | the level's rank |
|---|---|---|---|---|---|
| **3** | 0.6875 | **0.7594** | **+0.0719** | **4.89** | highest |
| **7** | 0.6875 | **0.6312** | **+0.0688** | **5.77** | lowest |
| **11** | 0.6875 | **0.7073** | **+0.1031** | **9.08** | second |
| **19** | 0.6875 | **0.6948** | **+0.0073** | **0.53** | third |

| the pairs of draws | their changes differ by | sigma |
|---|---|---|
| 3 against 7 | +0.0031 | 0.19 |
| 3 against 11 | -0.0313 | -1.59 |
| 3 against 19 | **+0.0646** | **4.17** |
| 7 against 11 | **-0.0344** | **-2.38** |
| 7 against 19 | **+0.0615** | **4.65** |
| 11 against 19 | **+0.0958** | **5.07** |

| the two spreads | at 8 columns | |
|---|---|---|
| the four **levels** | **0.1281** | sd **0.0527** |
| the four **changes** | **0.0958** | sd **0.0401** |

| claim | measured | verdict |
|---|---|---|
| AA1 the four draws are one configuration with the held-out seed moved | **104** fields compared, seeds **3, 7, 11, 19**, **6 of 6** shared trained arms bit-identical | **MET** |
| AA2 and every draw's change resolves | **4.89**, **5.77**, **9.08** and **0.53** sigma | **FALSIFIER FIRED** |
| AA3 and the four draws' changes agree | four of the six pairs resolve, up to **5.07** sigma | **FALSIFIER FIRED** |
| AA4 and the level moves more between draws than the change does | **0.1281** against **0.0958** | **MET** |

## 2. What the third and fourth draws say

**The change is the draw's too, and `e473`'s agreement was a coincidence of the pair it had.** At two draws the baseline
changes were **+0.0719** and **+0.0688**, **-0.0031** apart at **0.19** sigma, and this line read that as *the change is
the task's*. With four draws they run **+0.0073** at **0.53** sigma -- **unresolved**, so at that draw the sequence's
contribution to the unseen cue set cannot be separated from nothing -- to **+0.1031** at **9.08**, a spread of
**0.0958**, and **four of the six pairs resolve**, the widest at **5.07** sigma. **So the sentence `e473` published is
withdrawn: both the level and the change are the draw's**, and what two draws agreed on was two draws.

**And the level's own spread is only a third larger than the change's.** **0.1281** against **0.0958** (**0.0527** and
**0.0401** in sd), so the claim that survived is true and much weaker than the sentence it came with: the level is
*more* the draw's than the change is, by a factor of **1.34**, and the change is far from a constant. **So the card's
`holdout` clause -- which carries the change as its bearing -- carries one draw's change**, and a reader who wants the
task's own number needs the four.

**And the fourth draw is the first on which the sequence's contribution does not resolve.** Its baseline reads **0.6875**
before the sequence and **0.6948** after, **+0.0073** at **0.53** sigma, with its anchor at **-1.16** and its buffer at
**-0.94** -- so on that cue set the sequence neither raises nor lowers the reading by anything this unit can see, and
the three draws that do resolve are between **4.89** and **9.08** sigma. **The held-out reading is therefore not
*always* positive**: it is positive on three of the four cue sets this unit drew and null on the fourth.

**And the flag still draws nothing else, on all four draws at once.** All **104** compared config fields agree except
the held-out seed, the output path and the saved weights, the seeds are **3**, **7**, **11** and **19**, and the
sequence's own replicates are **bit-identical across all four draws** -- `naive`, the anchor and `replay` on both rolls,
six of six arms, record for record. **So the four columns above differ in the held-out cue set and in nothing else**,
which is what makes the spread a measurement of that and not of the training.

## 3. What it cannot settle

- **Four draws are not the population**: the spread is the range of four samples and not their family's sd, and two of
  the four seeds (**11** and **19**) were chosen by this unit rather than drawn at random, so **0.1281** and **0.0958**
  are upper bounds on what two draws can show and not estimates of a distribution.
- **And a probe is not a task**: every level and every change is of **linear readability** from the frozen body.
- **And one ridge**: **1e-2** is `e469`'s, and a different one would move every cell above.
- **And one budget**: all four draws are at a hundred updates, so nothing here says whether the **changes**' spread is the
  budget's as well -- `e472`'s steps were measured on one draw only.
- **And one world**: four cue sets inside one world, so a redraw of the world is a different axis.
