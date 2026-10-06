# The basis contrast where the effect is: a null at the width where one arm resolves, and two deficits the same size to a hundredth

*2026-10-07. `experiments/e451_the_basis_contrast_where_the_effect_is.py` reads the corpus's headline pair at the width
where one of its arms has a resolved effect. `e449` halved the card's world's width and found that at **four columns**
`ewc-block` reads **-0.0271** over the baseline at **2.29** sigma, the only roll in eight where the anchor's
whole-diagonal standing clears two; `e450` wrote that into the card's ninth revision. Every reading of the pair -- the
biological cell-class basis against its size-matched random partition -- has been taken where the pair is a null:
**+0.0063** at **0.36** sigma as-built (`e439`), **+0.0108** at **0.54** under the reversed order (`e447`), and eleven
audits of the state read-out before them. **The pair has never been read where one of its arms is doing something.**
This unit drives `e449`'s configuration with `--methods naive,ewc-block-rand,replay` alone differing, at the same twenty
replicates, width and order. Five claims, registered before the new run's reading was opened.*

## 1. The pair at four columns

| at four columns | the biological `ewc-block` | the matched-random `ewc-block-rand` |
|---|---|---|
| its mean diagonal over `naive` | **-0.0271** at **2.29** sigma | **-0.0170** at **1.16** sigma |
| its newest-task cost | -0.0937 at 2.81 sigma | **-0.0990** at **2.70** sigma |

| the basis contrast, paired over the twenty replicates | mean diagonal | mean forgetting |
|---|---|---|
| **at four columns** | **-0.0101** at **0.64** sigma | **+0.0281** at **1.38** sigma |
| at eight, as-built (`e439`) | +0.0063 at 0.36 sigma | -0.0245 at 1.24 sigma |
| at eight, reversed (`e447`) | +0.0108 at 0.54 sigma | -0.0208 at 0.80 sigma |

| claim | measured | verdict |
|---|---|---|
| CX1 the run is one configuration with the arm list moved | **50** fields agree with `e449`'s, the shared arms **2 of 2** bit-identical | **MET** |
| CX2 and the matched-random arm has a resolved deficit here too | **-0.0170** at **1.16** sigma | **FALSIFIER FIRED** |
| CX3 and the two anchors' deficits agree in size | **0.0101** apart | **MET** |
| CX4 and the basis contrast is a null at the width where the effect is | **-0.0101** at **0.64** sigma | **MET** |
| CX5 and the matched-random arm's newest-task price resolves here too | **-0.0990** at **2.70** sigma | **MET** |

## 2. What the pair says at the width where the effect is

**The corpus's headline is a null where one of its arms resolves, and that is a stronger null than the ones before it.**
The basis contrast at four columns is **-0.0101** at **0.64** sigma, so the twelfth null is taken where the biological
arm reads **-0.0271** at **2.29** -- at the width `e449` found the effect at, and where the same unit found the world
**hardest** of the three. At sixteen columns the anchor has no resolved effect at all and a null there would say nothing
about the basis; here it says that **the effect which is present is the pair's and not the basis's**, which is the
reading the corpus's eleven audits could not reach because they were all taken where neither arm was doing anything
resolved.

**And CX2's firing is what makes that reading careful rather than convenient.** The matched-random arm's deficit is
**-0.0170** at **1.16** sigma -- negative, unresolved -- while the biological arm's is **-0.0271** at **2.29**. CX3 read
the two point estimates as **0.0101** apart, a tenth of the **0.05** bar, so **the two arms' effects are the same size
to a hundredth and only one of them clears two sigma**; the standard errors are **0.0147** and **0.0118**, so what
separates the two is the runs' dispersion. A claim of the form *this arm's effect resolves and that arm's does not* is
therefore, when the two sizes agree, a claim about **noise** and not about the arms -- which is the reading CX2's own
falsifier fired to produce, and which `e447`'s **0.0094** between the two anchors' newest-task costs at eight columns
says from the other side.

**And the pair's own price accepts what the pair's diagonal does not.** Both arms pay the newest task at this width --
**-0.0937** at **2.81** for the biological and **-0.0990** at **2.70** for the matched-random, **0.0053** apart, both
resolved -- so the width at which the pair's *standing* separates by resolution is one at which its *price* does not
separate at all. The two anchors are one arm with two names on the newest task and two measurements of one effect on the
diagonal, and the card's ninth revision already records the third thing they share: the same drift ratio and the same
bias ratio to four thousandths, read at the as-built order in `e439` and `e440`.

**And the control held at a fixed configuration again.** The new run's `naive` and `replay` are **2 of 2** bit-identical
to `e449`'s, which is the same width and the same order, so this unit's third arm cost a run and moved nothing. That is
the fourth time this line has checked it -- `e438`, `e439`, `e446` and now here -- and the second time it has done so at
a width other than the card's.

## 3. What it cannot settle

- **One width**: four columns, so the pair is read where one arm has a deficit and not at eight or sixteen, and the two
  arms' standard errors at that width are two numbers and not a distribution.
- **And one cell**: the card's world at twenty replicates, so the other five draws and the three streams are not in the
  reading, and a deficit at **1.16** sigma against one at **2.29** is exactly the pair a redraw could reorder.
- **And one partition draw**: the matched-random partition is a draw of the same group sizes and not the family of them,
  so a null at this draw is the corpus's twelve audits and not its own general statement.
- **And the two rolls are two runs**: the pair pairs replicate against replicate by the runner's `seed0 + 100 * r`
  schedule, which is a same-seed pairing and not the same run, so the **-0.0101** carries whatever separates two runs
  beyond their seeds -- and the two standard errors above are what that separation looks like.
