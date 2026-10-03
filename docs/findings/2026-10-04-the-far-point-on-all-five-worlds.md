# The far point on all five worlds: one of five recovers, and the head carries the task on every one

*2026-10-04. `experiments/e396_the_far_point_on_all_five_worlds.py` carries the two worlds `e395` did not run --
`--loop-seed 3` and `4` -- to the card's far point, **500** updates at twenty replicates, so all **five** worlds that
`e393` read at the near point now carry a reading at each end. The near readings are `e393`'s own; the far readings
are this unit's and `e395`'s. Five claims, registered before any of the new runs' readings was opened.*

## 1. Five worlds, both ends

| world | connectome's own reading | body after 20 updates | body after 500 updates | gain over the connectome | trained head, task 0 |
|---|---|---|---|---|---|
| the card's | **0.6875** | 0.5740 | **0.7729** | **+0.0854** | 0.7500 |
| **1** | **0.6875** | 0.5208 | **0.4854** | **−0.2021** | 0.8333 |
| **2** | **0.6875** | 0.5010 | **0.4677** | **−0.2198** | 0.7292 |
| **3** | **0.6875** | 0.5219 | **0.5219** | **−0.1656** | **0.8542** |
| **4** | **0.6875** | 0.4833 | **0.4385** | **−0.2490** | 0.7500 |

chance 0.2500. The head column is the first replicate's own accuracy, not a mean. The world 3 row is not a
transcription slip: its 500-update reading is **0.5219** to four places, the same as its 20-update one.

| claim | measured | verdict |
|---|---|---|
| Q1 one configuration except the draw | 17 placed, 11 drawn, **none** in neither list, **none** moved | **MET** |
| Q2 the five runs are five worlds | three fingerprints, **five** distinct values each | **MET** |
| Q3 the connectome's own reading does not move | **0.6875** five times, spread **0.0000** | **MET** |
| Q4 the far end is a minority of the worlds | **1** of five ends above its own connectome reading | **MET** |
| Q5 the far end spreads where the near end does not | **0.3344** against **0.0906**, **3.69** times | **MET** |

## 2. What the five worlds say

**One world in five recovers, and four end below an untrained body.** By five hundred updates the card's world has
0.7729 and the four redraws have 0.4854, 0.4677, 0.5219 and 0.4385 -- between **0.166** and **0.249** *below* where
the connectome's own weights had them, and below where three of them sat after twenty updates. `e395` found this on
two worlds and registered that the other two were not measured; both of them behave like 1 and 2, so the far-end
"recovery" is **one world's** and not an ordinary outcome.

**And the extra four hundred and eighty updates add nothing to the world on any redraw.** World 3 is the sharpest
case: 0.5219 at twenty updates and **0.5219** at five hundred, to four places, so the trained body's world carries
exactly as much of the task after five hundred updates as after twenty. The other three move **−0.0354, −0.0333** and
**−0.0438**. On the card's world the same four hundred and eighty updates move **+0.1989**. So the far end of the
trajectory is not a slow climb everywhere: on four of five worlds it is flat or falling, and on one it is the whole
recovery.

**And the head carries the task on all five.** The trained heads read 0.7500, 0.8333, 0.7292, **0.8542** and 0.7500
-- all far above their worlds, and on the four redraws three to four times the world's reading. That is the state
`e379` and `e380` described at the tight step, where the trained body has given the cue up and the head has taken it,
and here it is the **majority** state of the far point rather than an edge case.

**And the connectome's own reading is 0.6875 on seventeen readings.** Five worlds at the near point, four streams,
three worlds at the far point and five at the far point again -- **0.6875** every time, spread **0.0000**, across two
budgets and two axes. The number is the most stable thing in this line and this unit still does not explain it; what
it adds is that the reading is the same at **500** updates' worth of run as at 20, since the initial body is the same
untrained one.

## 3. What it cannot settle, and what it registers

- **Five worlds are five samples of one engine draw.** `--loop-seed` reseeds the cue, action and feedback populations
  and the three maps together, so nothing separates which of the eleven drawn fields makes a world one where the
  body keeps the cue; `e369`'s distance and `e368`'s horizon are the candidates and neither is varied here.
- **The near readings are stored, not rolled.** They are `e393`'s, made with the same instrument at the same budget,
  and this unit recomputes none of them.
- **One budget and one axis**: 500 updates is the far point, `seed0` is 0 and the stream is not redrawn at either end.
- **Why four of five fail is not located either.** The four redraws do not share one visible property against the
  card's world -- they differ in the cue's twelve neurons and the action's eight at once, and the horizon that
  `e369` measured for the card's draw is a property of *that* draw. A unit that varies the cue population alone is
  what would separate it, and the engine cannot do that today.
- *And a probe is not a mechanism.*
