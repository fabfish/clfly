# The ledger at a wider world: the buffer's survives at twice the columns and the anchor's price does not

*2026-10-07. `experiments/e448_the_ledger_at_a_wider_world.py` reads the card's world at **twice its width**. `e286`
named the read-out width as the real variable behind the corpus's numbers, `e292` found the share of the variance the
read-out explains rising from a median of **0.637** to **1.160** across the corpus's ladder, and `e345` fitted four
nested decoders to one roll. Every reading this line has published about the card's world was taken at **one** width:
`loop.world_dims` is **8**, `--readout-from-world` makes the read-out the world's own state, and revision 8's four rolls,
`e446`'s reversed one and `e447`'s matched-random one are all eight columns. This unit drives `e438`'s configuration with
`--loop-world-dims 16` alone differing, at the same three arms and twenty replicates. Five claims, registered before the
new run's reading was opened.*

## 1. The two widths

| roll | world dims | each task's read-out | tasks |
|---|---|---|---|
| card | **8** | **8** | `loop_odour_identity>loop_heading>loop_odour_input` |
| new | **16** | **16** | the same three names |

| the buffer over `naive` | first | middle | last | mean diagonal | mean forgetting |
|---|---|---|---|---|---|
| 8 columns | **+0.2896** (10.53σ) | **+0.2490** (9.50σ) | **-0.0604** (-3.18σ) | **+0.1594** (11.97σ) | **-0.2844** (-14.37σ) |
| 16 columns | **+0.2500** (7.40σ) | **+0.2135** (7.73σ) | **-0.0667** (-4.46σ) | **+0.1323** (9.29σ) | **-0.2505** (-12.60σ) |

| the anchor over `naive` | mean diagonal | newest task | mean forgetting |
|---|---|---|---|
| 8 columns | -0.0302 (1.77σ) | **-0.1177** (3.71σ) | -0.0474 (2.77σ) |
| 16 columns | +0.0073 (**0.44**σ) | **-0.0292** (**1.68**σ) | -0.0391 (**1.66**σ) |

| claim | measured | verdict |
|---|---|---|
| BZ1 the run is one configuration with the world widened | `loop_world_dims` 8 to 16, **50** compared fields, the three task names held, each read-out the world's own | **MET** |
| BZ2 and the buffer's ledger holds at the first position | **+0.2500** | **MET** |
| BZ3 and the last position is cost at the wider world | **-0.0667** | **MET** |
| BZ4 and the size of the position effect is the width's too | **+0.3167** against **+0.3500**, **0.0333** apart | **MET** |
| BZ5 and the anchor pays there too | **-0.0292** at **1.68** sigma | **FALSIFIER FIRED** |

## 2. What the wider world says

**The buffer's ledger survives the doubling and the anchor's price does not.** At sixteen columns the buffer's three
positions read **+0.2500**, **+0.2135** and **-0.0667** -- every one within **0.040** of the card's and every one
resolving at **7.40** to **9.29** sigma -- its first-over-last margin is **+0.3167** against **+0.3500**, and its
forgetting advantage is **-0.2505** at **12.60** sigma. The anchor's newest-task cost falls from **-0.1177** at **3.71**
sigma to **-0.0292** at **1.68** -- under the bar, the first roll this line has driven where that price does not resolve
-- and its mean diagonal and its forgetting purchase fall under two sigma with it, at **0.44** and **1.66**.

**So the one thing the card's eighth revision commits to about the anchor is the width's.** `e445` wrote the clause from
four rolls that all held eight columns and it carried the newest-task price as the arm's one resolved effect; the fifth
roll (`e446`, another task at the last position) kept it, and the sixth (sixteen columns) does not. Read beside `e442`,
which found the anchor's drift ratio stable to **2%** across two orders whose forgetting differed by a factor of **2.6**,
this is the second time the arm's movement has been held constant while its effect moved: **the parameter and the width
are two different things and the effect tracks the width.**

**And that is `e286`'s and `e292`'s account arriving on the card's own world.** A wider read-out leaves the weights less
to do, and the anchor regularises the **weights**; at sixteen columns the decoder reads the world's state directly and the
body's regularisation is worth less. The arm whose whole ledger is the newest-task price is the arm whose price is the
body's, and the body matters less when the head has twice as much to read. The claim registered against this was BY-style
in shape -- *the anchor pays there too* -- and it fired, which is the first time a claim about the anchor's price has
fired in this line.

**And the width moves the environment in the inverse of what `--readout-seed` moves.** The three **world** fingerprints
-- read, drive, coupling -- all changed and the **cue, action and feedback** populations were all held, which is the
mirror of `e444`, where `--readout-seed` moved the three populations and held the three maps. So the two manipulations
partition the environment's six fingerprints between them: the pool the populations come from is the decoder's and the
maps are the world's, which is what `fly_env.build` does with `np.setdiff1d` and with `world_dims`.

**And the buffer's newest-task cost is the one number that moved the other way.** It reads **-0.0604** at eight columns
and **-0.0667** at sixteen, resolving harder at **-4.46** sigma against **-3.18** -- so the wider world costs the buffer
more at the last position and the anchor less, and the card's clause about the buffer's newest-task cost is the stronger
of its two at the width where the anchor's has gone.

## 3. What it cannot settle

- **One width** against the card's one: **16** is a single point on `e286`'s axis and the ladder that gave `e292` its
  medians is not here, so a price that falls from **3.71** to **1.68** sigma says the effect shrank and not by how much
  per column.
- **And a width is not a decoder**: widening the world's state changes what the three tasks **are** as well as how many
  columns the decoder has, so this is a manipulation of the game and not of the decoder alone -- which `--readout-size`
  would be, and which `--readout-from-world` makes inert.
- **And one cell**: the card's world at twenty replicates, so the other five draws and the three streams are not in the
  reading, and a price at **1.68** sigma is the kind of number a redraw could put above the bar.
- **And one run**: no second order, no redraw and no matched-random arm at sixteen columns, so whether the **basis**
  contrast survives a widening -- which is the corpus's headline -- is not measured here.
