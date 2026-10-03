# The card on three more streams: the stream moves the body a third as much as the world does

*2026-10-04. `experiments/e394_the_card_on_three_more_streams.py` draws the card's cell three more times at the
clean stream `e340` established -- `--seed0` **1**, **2**, **3** with `--readout-seed 0 --loop-seed 0`, which holds
the read-out draw and the environment while the training seeds move -- at the card's canonical near point: the wide
step, cue at 0, the action source, **20** updates, **20** replicates. The card's own 20-update artifact is the fourth
stream. Five claims, registered before any of the new runs' readings was opened.*

## 1. Four streams

| stream | connectome's own reading | body after 20 updates | what the twenty updates cost | trained head, task 0 |
|---|---|---|---|---|
| the card's | **0.6875** | **0.5740** | **0.1135** | 0.2500 |
| **1** | **0.6875** | **0.5938** | **0.0938** | 0.2708 |
| **2** | **0.6875** | **0.5677** | **0.1198** | 0.3125 |
| **3** | **0.6875** | **0.5542** | **0.1333** | 0.2083 |

chance 0.2500. The head column is the first replicate's own accuracy, not a mean.

| claim | measured | verdict |
|---|---|---|
| O1 one configuration except the stream, and the draws are pinned | 29 pinned, 3 of the stream, **none** in neither list, **no** pinned field moved | **MET** |
| O2 the streams are four streams | `seed0` takes **0, 1, 2, 3** | **MET** |
| O3 the draws are the card's own | the read-out draw and all six environment fingerprints take **1** value | **MET** |
| O4 neither the connectome's reading nor the body's moves | **0.0000** and **0.0396** | **MET** |
| O5 the headline replicates | costs **0.0938, 0.1198, 0.1333** against the card's 0.1135 | **MET** |

## 2. What the four streams say

**The stream is the smallest axis the card has.** The four bodies read 0.5740, 0.5938, 0.5677 and 0.5542 -- a spread
of **0.0396** -- where `e393`'s four **worlds** spread **0.0906**. Same cell, same instrument, same budget: the draw
the benchmark never varied moves the trained body **2.3 times** as much as the draw `--seed0` names. The cost of
twenty updates is likewise tight across streams -- 0.0938, 0.1198, 0.1333 against the card's 0.1135, a spread of
0.0395 -- while across worlds it ran 0.1135 to 0.2042, a spread of 0.0907. So the headline the card carries is
**stable on both axes and the world is the axis that moves it**, which is the useful direction for the card: the
benchmark's numbers are more nearly a property of the game than of the seeds.

**And the connectome's own reading is 0.6875 on nine draws.** Four streams here and five worlds in `e393`, all
**0.6875** -- 33 of 48 -- for a spread of **0.0000** on both axes. The stream half of that is now explained: the
initial reading is fitted on the untrained body, against a world and a task the stream does not move, so a probe on
it returns the same number for the same reason `e340`'s clean stream returned one configuration. The world half is
**not** explained, and `e393` left it that way: there the cue population itself is redrawn and the reading still does
not move, which is the observation that needs a unit rather than a sentence.

**And both halves of the card's worst clause are now measured.** `e392`'s M5 said the cell carries one world and one
stream, so every number the line has published is conditional on both. `e393` redrew the world four times and this
unit redrew the stream three, and the answer is the same on both: the **effect** survives and the **level** moves by
a tenth of the reading at most. That is enough for the card's second revision, which should carry the two spreads
beside the numbers they bound rather than the word "conditional".

## 3. What it cannot settle

- **Three streams are three samples**, at one budget, at the card's near point. The far point at five hundred is
  redrawn on neither axis.
- **The control is a fingerprint and not an argument.** `--support-seed` and `--partition-seed` default to `seed0`, so
  the claim that only the training seeds moved rests on the seven fingerprints of O3 being identical -- which they
  are, and which is evidence and not a proof that no other draw followed the seed.
- **And the invariance is bounded, not explained.** Nine draws at 0.6875 says the reading does not depend on either
  axis; it does not say what the number is, and a unit that varies the cue population alone -- which the environment
  cannot do today, since `--loop-seed` moves all three populations and all three maps at once -- is what would.
- *And a probe is not a mechanism.*
