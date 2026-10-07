# The neuron read-out at eight columns: the anchor's price is the head's width's and not its source's, and `e455`'s reading is refuted

*2026-10-07. `experiments/e458_the_neuron_readout_at_eight_columns.py` holds the width and moves the source. `e455` moved
the card's world's head from the **world's own state** to the **circuit's own neurons** and found the biological anchor's
one resolved effect gone -- its newest-task cost **-0.0115** at **0.78** sigma against **-0.1177** at **3.71** -- and read
it as *the price is the earned label's*; `e457` wrote both read-outs into the card's eleventh revision and named the gap
it could not close, that the two differ in **what they read** *and* in **width**, **8** against **32**. On the earned
label the two dials cannot be separated at all, since `--readout-from-world` makes the head's input the world's state.
**This unit takes the other road**: `e438`'s configuration with the read-out off the world and its width set to the
world's own **eight**, so the roll differs from the card's in the **source** alone. Five claims, registered before the new
run's reading was opened.*

## 1. Three heads of one world

| the head reads | width | the anchor over `naive`, standing | sigma | its newest-task cost | sigma |
|---|---|---|---|---|---|
| the world's own state | 8 | -0.0302 | 1.77 | **-0.1177** | **3.71** |
| the circuit's neurons | **32** | +0.0187 | 1.03 | **-0.0115** | **0.78** |
| **the circuit's neurons** | **8** | **+0.0017** | **0.12** | **-0.0615** | **4.48** |

| the buffer over `naive` by position | first | middle | last | over the anchor |
|---|---|---|---|---|
| the world's state, 8 | +0.2896 | +0.2490 | -0.0604 | +0.1896 (10.89σ) |
| the neurons, 32 | +0.2323 | +0.1812 | -0.0302 | +0.1090 (7.66σ) |
| **the neurons, 8** | **+0.3281** | **+0.2958** | **-0.0833** | **+0.1785** (10.48σ) |

| claim | measured | verdict |
|---|---|---|
| DE1 the run is one configuration with the source moved at the card's width | **48** fields agree with `e438`'s, the read-out **8** off the world against the card's **8** on it | **MET** |
| DE2 and with the width held, the price does not resolve | **-0.0615** at **4.48** sigma | **FALSIFIER FIRED** |
| DE3 and its standing does not resolve either | **+0.0017** at **0.12** sigma | **MET** |
| DE4 and the buffer's own ledger holds at this width | **+0.3281** and **-0.0833** | **MET** |
| DE5 and the buffer is ahead of the anchor here too | **+0.1785** at **10.48** sigma | **MET** |

## 2. What the third head says

**The anchor's price is the head's width's and not its source's, and `e455`'s reading is refuted by the roll that holds
the width and moves the source.** Against the earned label the price is **-0.1177** at **3.71** sigma; against the neurons
at **eight** columns it is **-0.0615** at **4.48** -- **resolved**, and resolved harder -- while at **thirty-two** columns
it is **-0.0115** at **0.78**. Two clean contrasts fall out and they point the same way: **moving the width with the
source held** (neurons, 8 against 32) takes the price from **4.48** to **0.78** sigma, and **moving the source with the
width held** (world against neurons, both 8) takes it from **3.71** to **4.48** -- so the dial that removes the price is
the **width** and the dial that changes its size is the source. `e455`'s sentence, that the price is the earned label's
rather than the anchoring's, is therefore wrong: what the earned label was giving the anchor was **eight columns** and
not the world.

**And the anchor's standing is unresolved at all three heads, which is what makes the price the interesting one.** It
reads **-0.0302** at **1.77**, **+0.0187** at **1.03** and **+0.0017** at **0.12** -- the smallest number this line has
recorded for either anchor on any head, and a span of **0.0319** across a fourfold width and two sources. So the
standing's absence is neither the source's nor the width's in the sense the price's is: it is what is left when neither
dial moves it, and the clause revisions 8 to 11 carry about that arm's standing is the one part of them that travels.

**And the buffer's ledger is largest at this head on two of its three positions.** The first and middle positions read
**+0.3281** and **+0.2958**, against **+0.2896**/**+0.2490** on the world's state and **+0.2323**/**+0.1812** on the
thirty-two column neurons, and its newest-task cost is the largest as well (**-0.0833** against **-0.0604** and
**-0.0302**). So the buffer's advantage grows where the anchor's shrinks -- **+0.1785** at **10.48** sigma over the anchor
here against **+0.1090** at **7.66** there -- which is the stability-plasticity trade read at its two ends: a narrower
head is where the arm that stores is worth most and the arm that anchors is worth least.

**And the one contrast `e457`'s clause carries is unaffected, while its reading of it is not.** DD5 of revision 11 had the
read-out separating the two anchors' prices -- **0.0042** on the earned label against **0.0208** on the neurons -- and
this roll says which dial does the separating (**the width**) and which does not (**the source**, since the earned label's
and the neurons' prices at eight columns differ by **0.0562** while both resolve). The clause needs no correction and
revision 12 should carry the third head beside the other two.

## 3. What it cannot settle

- **Two of the three corners**: **world's state at thirty-two columns** is not constructible, because
  `--readout-from-world` makes the head's input the world's state and a thirty-two column world state is a different task
  rather than the same one read differently -- so the source's own effect is measured at one width and the width's at one
  source.
- **And one cell each**: the card's world at twenty replicates, so the other five draws and the three streams are not in
  the reading, and a price at **0.78** sigma against one at **4.48** is a pair two redraws could narrow.
- **And one anchor**: `ewc-block-rand` is absent from this head, so whether the width moves the matched-random arm's price
  the way it moves the biological one -- `e456` found they separate at thirty-two columns -- is not asked here.
- **And a width is not a mechanism**: that eight columns make the anchor pay the newest task does not say which of
  `e440`'s two parameters does it, and neither of those is read on this head.
