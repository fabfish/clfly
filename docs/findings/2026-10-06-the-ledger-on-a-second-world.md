# The ledger on a second world: the buffer's is the benchmark's and the anchor's is the draw's, and `--loop-seed` redraws six fingerprints and not three

*2026-10-06. `experiments/e443_the_ledger_on_a_second_world.py` reads the card's world **redrawn**. Every number this
line has published about the card's arms is conditional on one draw of it; `e393` redrew the environment four times and
wrote that sentence itself, but at **twenty updates** with `naive` and `replay`, so the ledger `e437` measured
(**+0.2896**, **+0.2490**, **-0.0604**, a first-over-last margin of **+0.3500**) and that `e438` extended to an anchor
(**+0.0625**, **-0.0354**, **-0.1177**) had never been read on a second world at the card's own horizon. This unit drove
`e438`'s configuration with `--loop-seed 1` alone differing, at the same twenty replicates on the same as-built order.
Five claims, registered before the new run's reading was opened.*

## 1. What the redraw moved

| roll | loop seed | cue | action | feedback | world read | drive | coupling |
|---|---|---|---|---|---|---|---|
| card | none | `3985fc4e3252` | `f379863d1cf4` | `77963b921bc3` | `3a7ba76b3619` | `3d88340cf387` | `5326f4a0edb4` |
| new | 1 | `65369deff0eb` | `2c2405b55485` | `83c8d7fe4a22` | `56280aec0560` | `09a3d37a255a` | `d37fbe59839d` |

| the buffer's gain over `naive` | first | middle | last | mean diagonal | mean forgetting |
|---|---|---|---|---|---|
| card | **+0.2896** (10.53σ) | **+0.2490** (9.50σ) | **-0.0604** (-3.18σ) | **+0.1594** (11.97σ) | **-0.2844** (-14.37σ) |
| new | **+0.3198** (10.52σ) | **+0.2552** (8.74σ) | **-0.0479** (-2.93σ) | **+0.1757** (11.66σ) | **-0.2964** (-13.65σ) |

| the anchor's gain over `naive` | first | middle | last | mean diagonal | mean forgetting |
|---|---|---|---|---|---|
| card | +0.0625 | -0.0354 | -0.1177 | **-0.0302** (1.77σ) | -0.0474 (2.77σ) |
| new | +0.0979 | +0.0167 | **-0.0552** | **+0.0198** (1.30σ) | -0.0620 (3.02σ) |

| claim | measured | verdict |
|---|---|---|
| BU1 and the two rolls are one configuration with the world redrawn | **55** compared fields, the three world fingerprints all redrawn, and the cue and action fingerprints **also** moved | **FALSIFIER FIRED** |
| BU2 and the buffer's ledger replicates at the first position | **+0.3198** | **MET** |
| BU3 and the last position is cost on the new world too | **-0.0479** | **MET** |
| BU4 and the first-taught task is ahead of the last-taught one | the margin is **+0.3677** | **MET** |
| BU5 and the size of the position effect is the world's | **+0.3677** against the card's **+0.3500**, **0.0177** apart | **MET** |

## 2. What the second world says

**The buffer's ledger is the benchmark's, and it replicates to a thirty-first of a point.** Every one of the three
positions reads within **0.031** of the card's, the first-over-last margin is **+0.3677** against **+0.3500** --
**0.0177** apart, against a bar this unit set at **0.15** -- and **all five** of the buffer's contrasts resolve on both
worlds with the same signs and at **8.74** to **11.97** sigma on the new one. So the shape `e437` measured and the
sentence `e438` drew from it -- the ledger is `replay`'s, the first two positions are its advantage and the last is a
cost -- can be quoted without naming a world.

**And the anchor's is the draw's, which is the third time this line has reached that sentence from a different
direction.** Its mean diagonal is **-0.0302** below the baseline on the card and **+0.0198** above it on the new world,
neither resolved, and its last-position cost is **-0.1177** on one and **-0.0552** on the other -- a factor of **2.1**
between two draws. `e441` found the same contrast moving with the *order* and `e438`'s own control clause turned out to
be order-scoped; this says it moves with the *draw* too, so of the four claims `e438` made the one that does not travel
is the one about the anchor and not the ones about the buffer.

**And BU1 fired on the unit's own enumeration of the redraw.** It registered that the environment's **three world**
fingerprints would move and that `cue_sha1` and `action_sha1` would be held, on `e393`'s phrasing that the redraw is of
the world. Measured, `--loop-seed 1` moves **six**: the cue, the action, the **feedback** population and the world's
three maps. `fly_env.build` draws all three populations and the cue templates from **one** seed, and the runner passes
`--loop-seed` into that seed, so the manipulation reseeds which neurons the cue, the action and the feedback are written
on as well as the world's drive and answer maps. The firing is a mis-specified claim and it corrects a field list three
units have used: **`--loop-seed` is a redraw of the environment, not of the world**, and a unit that wants to move the
world's maps alone has no flag for it.

**And the forgetting ledger replicates alongside the accuracy one.** `naive`, `ewc-block` and `replay` read **0.3750**,
**0.3276** and **0.0906** on the card and **0.4193**, **0.3573** and **0.1229** on the new world: every arm forgets more
there, the buffer's own advantage is **-0.2844** then **-0.2964** (**14.37** and **13.65** sigma), and the anchor's is
**-0.0474** then **-0.0620**. So the second world is a little harder for all three arms and the ordering of the arms by
forgetting is the same on both -- which is what a redraw that dominates a configuration-against-configuration
comparison, as `e339` found one does, would *not* be expected to leave alone by accident.

## 3. What it cannot settle

- **Two worlds**: one redraw, so a spread between two draws cannot be told from a spread between two arms, and the
  **0.0177** by which the buffer's margin moved is not a distribution.
- **And one manipulation**: `--loop-seed` moves six fingerprints together, so nothing here separates the cue and action
  populations from the world's maps, and no flag in the runner moves the maps alone.
- **And one cell**: the card's horizon, one order, three arms, twenty replicates, so `e393`'s four more worlds are at
  another horizon and the anchor's second order is not redrawn.
- **And the read-out subset is held**: `--readout-seed` defaults to `--seed0`, which does not move, so the decoder's own
  draw is the card's on both worlds and the redraw is entirely the environment's.
