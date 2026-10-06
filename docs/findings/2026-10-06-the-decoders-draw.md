# The decoder's draw: the ledger replicates under it, and over the four rolls of the card's world the anchor's only resolved effect is its price at the newest task

*2026-10-06. `experiments/e444_the_decoders_draw.py` reads the card's world with the **decoder redrawn**. `e339` found
that `--seed0` is **three draws at once** and that no clean seed-stream pair exists in the corpus; `e443` took the
environment's apart and gave this line the corrected field list, closing on *the read-out subset is held, so the
decoder's own draw is the card's on both worlds*. This unit drives the third draw: `e438`'s configuration with
`--readout-seed 1` alone differing, at the same three arms, twenty replicates and as-built order. Five claims,
registered before the new run's reading was opened.*

## 1. What the decoder's draw moved

| roll | read-out subset | cue | action | feedback | world read | drive | coupling |
|---|---|---|---|---|---|---|---|
| card | `59926518137c` | `3985fc4e3252` | `f379863d1cf4` | `77963b921bc3` | `3a7ba76b3619` | `3d88340cf387` | `5326f4a0edb4` |
| new | `5f15abf8ccb5` | `b77487da508c` | `191d6b68dcae` | `45adc0b748d7` | `3a7ba76b3619` | `3d88340cf387` | `5326f4a0edb4` |

| the buffer's gain over `naive` | first | middle | last | mean diagonal | mean forgetting |
|---|---|---|---|---|---|
| card | +0.2896 (10.53σ) | +0.2490 (9.50σ) | **-0.0604** (-3.18σ) | **+0.1594** (11.97σ) | -0.2844 (-14.37σ) |
| new | +0.2740 (10.62σ) | +0.2312 (6.78σ) | **-0.0542** (-2.29σ) | **+0.1503** (7.66σ) | -0.2687 (-13.75σ) |

| claim | measured | verdict |
|---|---|---|
| BV1 and the two rolls are one configuration with the read-out draw moved | the read-out subset moved, and the cue, action and feedback fingerprints moved with it | **FALSIFIER FIRED** |
| BV2 and the buffer's ledger replicates under a second decoder | **+0.2740** at **10.62** sigma | **MET** |
| BV3 and the last position is cost under it too | **-0.0542** at **-2.29** sigma | **MET** |
| BV4 and the size of the position effect is the decoder's too | **+0.3281** against the card's **+0.3500**, **0.0219** apart | **MET** |
| BV5 and the buffer's advantage on the whole diagonal survives it | **+0.1503** at **7.66** sigma | **MET** |

## 2. What the three rolls together say

**BV1 fired on a manipulation that cannot be made alone, and that is a structural result rather than a mis-specified
claim.** It registered the mirror of `e443` -- the decoder moved and the environment's six fingerprints held -- and
measured, `--readout-seed 1` moves the **cue, action and feedback** fingerprints while the world's three maps stay
exactly where they were. The reason is in `fly_env.build`: the three populations are drawn from
`np.setdiff1d(all_neurons, readout_subset)`, so **changing which neurons the decoder reads changes the pool the cue,
the action and the feedback are drawn from**, while the maps, drawn later from a stream whose consumption is unchanged,
come out identical. So `e339`'s *three draws at once* is really two manipulations, and the first of them bleeds into
the second: **the world's maps move only with `--loop-seed`, and the three populations move with either flag.** A unit
that wants the decoder alone, or the populations alone, has no configuration for it.

**And the ledger replicates under the second decoder as it did under the second world.** Every position reads within
**0.021** of the card's, the first-over-last margin is **+0.3281** against **+0.3500** -- **0.0219** apart against a
**0.15** bar -- and the buffer's whole-diagonal advantage is **+0.1503** at **7.66** sigma against the card's **+0.1594**
at **11.97**. Two different redraws, moving disjoint things, leave the buffer's three-position ledger where they found
it.

**And the four rolls of the card's world this line has driven now read together, and they separate the two arms
completely.**

| roll | what moved | the anchor over `naive`, mean diagonal | its last position | the buffer over `naive`, mean diagonal |
|---|---|---|---|---|
| as-built (`e438`) | nothing | -0.0302 (**1.77**σ) | **-0.1177** (3.71σ) | **+0.1594** (11.97σ) |
| rotated (`e441`) | the order | +0.0229 (**1.21**σ) | **-0.0906** (3.56σ) | **+0.2080** (13.51σ) |
| environment redrawn (`e443`) | `--loop-seed 1` | +0.0198 (**1.30**σ) | **-0.0552** (2.57σ) | **+0.1757** (11.66σ) |
| decoder redrawn (`e444`) | `--readout-seed 1` | -0.0111 (**0.59**σ) | **-0.0615** (2.62σ) | **+0.1503** (7.66σ) |

**The anchor's standing on the whole diagonal is unresolved in all four** -- **1.77**, **1.21**, **1.30** and **0.59**
sigma, spanning **0.0531** and changing sign -- while **its price at the newest task resolves in all four**, at
**-0.1177** to **-0.0552**, **2.57** to **3.71** sigma, always the same sign. The buffer resolves in all four too, at
**+0.1503** to **+0.2080**, **7.66** to **13.51** sigma. So `e441`'s and `e443`'s sentence -- that the anchor's standing
is the order's and the draw's -- is better said the other way round: **the anchor's standing is not there.** What the
anchor has on this world, in every roll this line has driven, is one resolved effect: it pays the newest task, and the
smaller numbers that got read as its standing are a sign wandering inside its own standard error.

**And the three rolls say it without needing a fifth.** `e438`'s `-0.0302` at **1.77** sigma was written up as *not a
buffer* and `e441`'s `+0.0229` at **1.21** as the sign flipping; read together with `e443` and this unit they are four
draws of a number that is zero, and the sentence the card should carry is the one about the newest-task price.

## 3. What it cannot settle

- **Two draws of each kind**: one environment redraw and one decoder redraw, so a spread between two draws cannot be
  told from a spread between two arms, and four rolls are four points and not a distribution.
- **And the two are not separable**: `--readout-seed` moves the three populations, so this unit's decoder redraw is a
  decoder redraw *and* a population redraw, and nothing here isolates the subset's own effect on the ledger.
- **And one cell**: the card's horizon, one order for each roll but the rotated one, three arms, twenty replicates.
- **And a draw is not an axis**: `--readout-size` is held at 32, so this is which neurons and not how many, which is
  `e286`'s axis and not this unit's; and the four rolls' newest-task cost for the anchor is a price with no measurement
  of what it buys.
