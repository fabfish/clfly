# The card on four more worlds: the headline replicates, and the card's own world is the mildest of the five

*2026-10-04. `experiments/e393_the_card_on_four_more_worlds.py` redraws the closed loop's environment four times --
`--loop-seed 1` to `4`, which reseeds the cue, action and feedback populations and the three maps after them and
nothing else -- and measures the card's canonical near point on each: the wide step, cue at 0, the action source,
**20** updates, **20** replicates, read through the same probe. The card's own 20-update artifact is the fifth world,
so the two ends are one instrument. Five claims, registered before any of the new runs' readings was opened.*

## 1. Five worlds

| world | connectome's own reading | body after 20 updates | what the twenty updates cost | trained head, task 0 |
|---|---|---|---|---|
| the card's | **0.6875** | **0.5740** | **0.1135** | 0.2500 |
| **1** | **0.6875** | **0.5208** | **0.1667** | 0.4792 |
| **2** | **0.6875** | **0.5010** | **0.1865** | 0.2917 |
| **3** | **0.6875** | **0.5219** | **0.1656** | 0.1042 |
| **4** | **0.6875** | **0.4833** | **0.2042** | 0.1875 |

chance 0.2500. The head column is the first replicate's own accuracy, not a mean.

| claim | measured | verdict |
|---|---|---|
| N1 one configuration except the draw | 16 placed, 11 drawn, and **`loop_cue_at` in neither list** | **FALSIFIER FIRED** |
| N2 the four are four different worlds | three fingerprints, **four** distinct values each, **none** the card's | **MET** |
| N3 the connectome's own reading is not the world's | a spread of **0.0000** | **MET** |
| N4 the body after twenty updates replicates | a spread of **0.0906** | **MET** |
| N5 the headline itself replicates | costs **0.1667, 0.1865, 0.1656, 0.2042**, all above the 0.05 bar | **MET** |

## 2. What fired, and what it is

**N1 fired on my own field list, for the fourth unit in a row.** `loop_cue_at` is a field `_facts` returns, it is
the card's own (the cue is at step 0 in all five runs), and my two lists did not contain it. Nothing substantive
moves -- the field is constant across the five worlds, so it belongs to the placed list and the closure claim was
false only as written -- but the defect is the same one `e381`'s head row, `e383`'s missing rate and `e386`'s
read-out widths each paid for, and the count is now four. The falsifier is reported as **FIRED** and the reading
below is the one it produced.

**And four of the eleven drawn fields do not move.** `drive_from_cue`, `loop_drive_from_cue`, `n_action` and `n_cue`
take one value each across the five worlds, so the redraw changes *which* neurons carry the populations and the three
maps but not how many; the unit reports that rather than counting it as a manipulation.

## 3. What the five worlds say

**The headline replicates, and it is larger on four of them.** The card's own world loses **0.1135** to twenty
updates; the four redraws lose **0.1667, 0.1865, 0.1656** and **0.2042**. So the effect the card's cell is about --
that training at the interface takes the cue out of the body faster than it fits a head -- is not a property of the
card's draw, and the card's draw is the **mildest of the five**. That is the opposite of the usual worry: a single
world did not flatter the effect, it understated it.

**And the substrate's own reading did not move at all.** The connectome's own weights read task 0 at **0.6875** --
**33 of 48** -- on every one of the five worlds, a spread of **0.0000**. The cue is written into a different set of
twelve neurons on each draw and the read-out is the world's eight numbers, and the reading is *identical* five times.
That is reported and not claimed: the unit registered a band, not an invariance, so what it found is a fact that
needs its own registration and its own explanation. It is the strongest invariance in this finding and it is not
disturbed by the draw that moves the body by a fifth of its reading.

**And the body's four redraws all sit below the card's.** 0.5208, 0.5010, 0.5219 and 0.4833 against 0.5740, a spread
of **0.0906** inside the pre-registered 0.10 band but near its edge, and every one of them lower than the card's
world. So the card's cell is one draw of a *family* whose bodies land between 0.48 and 0.57 after twenty updates,
and the card's numbers are near the top of that family rather than in the middle.

## 4. What it cannot settle, and what it registers

- **A redraw moves the whole draw.** `--loop-seed` reseeds the three populations and the three maps together, so
  nothing here separates which of the eleven drawn fields carries the effect: the cue's twelve neurons, the action
  population, or the drives. Separating them is what a per-map seed would be for, and the environment has one seed.
- **One budget.** Twenty updates is the card's near point. Whether the far point at five hundred replicates across
  worlds is not measured, and the valley's depth is where the redraws differ most, so the far point is the next
  thing to redraw.
- **The seed stream is still one.** `seed0` is 0 in all five worlds, so this discharges half of `e392`'s M5 -- the
  world -- and leaves the other half, the training seeds, exactly where it was.
- *And a probe is not a mechanism*: a reading says how much of the label a linear fit recovers from the world's
  eight numbers, so a replicated cost is a replicated shape in what is recoverable and not a named process.
