# The two-hop world: the cue's distance to the action population separates the world that keeps the cue from the four that do not

*2026-10-04. `experiments/e397_the_two_hop_world.py` measures `e369`'s directed distance -- the shortest path from
the cue population to the action population in the circuit's own mask -- on all five of the card's worlds, and sets
it beside their readings at both ends from `e396`'s artifact. **No training is run**: the environment's draw is a
seed, the mask is the circuit's, and each environment built here reproduces the six fingerprints its own run
recorded. Five claims, registered before any distance or any reading was opened.*

## 1. Five worlds, and where the cue is

| world | engine seed | cue to action | cue to feedback | connectome's own reading | body after 500 updates | gain |
|---|---|---|---|---|---|---|
| the card's | 0 | **2** | 1 | 0.6875 | **0.7729** | **+0.0854** |
| **1** | 1 | **1** | 1 | 0.6875 | 0.4854 | −0.2021 |
| **2** | 2 | **1** | 1 | 0.6875 | 0.4677 | −0.2198 |
| **3** | 3 | **1** | 1 | 0.6875 | 0.5219 | −0.1656 |
| **4** | 4 | **1** | 1 | 0.6875 | 0.4385 | −0.2490 |

| claim | measured | verdict |
|---|---|---|
| R1 the geometry is the runs' | five environments, six fingerprints each, **0** disagree | **MET** |
| R2 the card's world reproduces `e369`'s distance | exactly **2** | **MET** |
| R3 the draw moves the distance | **2, 1, 1, 1, 1** | **MET** |
| R4 the distance separates the one that recovers | the card's is **strictly longer** than all four losers' | **MET** |
| R5 the draw is invisible until training | **0.000** of the far spread | **MET** |

## 2. What the separation says, and what it does not

**The one world that keeps the cue is the one where the cue is two hops from the action population.** The card's
world is at distance **2** and the four that lose the cue by a fifth to a quarter of the reading are all at **1** --
a perfect separation of five draws by a graph property computable from the circuit before anything is rolled.

**And it points the other way from the formula the line published.** `e369`'s `tau - 2 - d` gives the card's world a
horizon of **8** and each redraw **9**, so on that formula the *four redraws* are the ones with more room to hold the
trace. The world with the shorter horizon is the one that recovers. So the distance is **not acting through the
horizon** here -- at a cue step of 0 every world has at least eight steps of margin, and the horizon is binding for
none of them. What the distance is a correlate of is whatever makes training keep the cue, and this unit cannot say
what that is.

**And the draw is invisible until training.** The five worlds' initial readings span **0.0000** -- the same 0.6875
five times -- against a span of **0.3344** after five hundred updates, so the entire spread the redraw series has
been measuring appears **only after the weights move**. A property of the draw that is worth a third of the reading
at the far end is worth nothing at all before the first update, which is why every earlier unit could redraw the
world without disturbing the connectome's own number.

## 3. What it cannot settle, and what it registers

- **Five points are five points, and one of them recovers.** The separation is on five draws with one positive case,
  so it is an association and not a mechanism; a redraw that moved the cue population alone -- which the engine
  cannot do, since `--loop-seed` moves the three populations and the three maps together -- is what would turn it
  into one.
- **And the distance is one of eleven fields the draw moves.** A world at a different distance is also a world with
  different populations and different maps, so nothing here says the path is the cause rather than a marker of the
  draw that happened to carry it.
- **One distance of four.** The cue-to-feedback path is measured and reported (1 on all five, so it does not
  separate them); the action-to-feedback and cue-to-read-out paths are not measured.
- **Near geometry only.** The distance is a property of the circuit and the draw, not of the trained body, so it
  cannot say how a gradient update uses the extra hop.
- *And a probe is not a mechanism*: the far-point readings say how much of the label a linear fit recovers from the
  world's eight numbers.
