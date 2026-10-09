# The held-out reading in a second world: the change is the world's too, at one matched seed

*2026-10-09. `experiments/e475_the_held_out_reading_in_a_second_world.py` redraws the **environment** under the held-out
task -- `--loop-seed 1` against the default `0`, the same circuit, read-out draw, net seed and label sequences -- at the
same four held-out draws and the same hundred updates. **BA1 MET** and **BA2, BA3 and BA4 all FIRED**.*

## 1. The two worlds

| the world | the held-out draw | the initial body | the trained body | the change | sigma |
|---|---|---|---|---|---|
| **0** | 3 | 0.6875 | **0.7594** | **+0.0719** | **4.89** |
| **0** | 7 | 0.5625 | **0.6312** | **+0.0688** | **5.77** |
| **0** | 11 | 0.6042 | **0.7073** | **+0.1031** | **9.08** |
| **0** | 19 | 0.6875 | **0.6948** | **+0.0073** | **0.53** |
| **1** | 3 | 0.6667 | 0.7260 | **+0.0594** | **4.53** |
| **1** | 7 | 0.6250 | 0.7240 | **+0.0990** | **8.07** |
| **1** | 11 | 0.7500 | 0.7833 | **+0.0333** | **2.54** |
| **1** | 19 | 0.7500 | 0.7500 | **-0.0000** | **-0.00** |

| the matched held-out seed | the change, world 1 less world 0 | sigma |
|---|---|---|
| 3 | +0.0125 | 0.64 |
| 7 | -0.0302 | -1.60 |
| 11 | **+0.0698** | **+5.15** |
| 19 | +0.0073 | 0.47 |

| the pairs of draws **within world 1** | their changes differ by | sigma |
|---|---|---|
| 3 against 7 | **-0.0396** | **-3.01** |
| 3 against 11 | +0.0260 | 1.49 |
| 3 against 19 | **+0.0594** | **+3.31** |
| 7 against 11 | **+0.0656** | **+3.83** |
| 7 against 19 | **+0.0990** | **+5.81** |
| 11 against 19 | +0.0333 | 1.84 |

| the two spreads | world 0 | world 1 |
|---|---|---|
| the four **levels** | **0.1281** | 0.0594 |
| the four **changes** | 0.0958 | **0.0990** |

| claim | measured | verdict |
|---|---|---|
| BA1 the second world is one configuration with the first except the world's own seed | **102** fields compared within world 1 and **408** between the worlds, world seeds **{null, 1}**, held-out seeds **3, 7, 11, 19**, **6 of 6** arms bit-identical within world 1 and **0 of 24** between the worlds | **MET** |
| BA2 and every draw's change resolves in the second world | **4.53**, **8.07**, **2.54** and **-0.00** sigma | **FALSIFIER FIRED** |
| BA3 and the change is not the world's | **5.15** sigma at the seed **11** | **FALSIFIER FIRED** |
| BA4 and the draws disagree in the second world too | four of the six pairs resolve, up to **5.81** sigma | **FALSIFIER FIRED** |

## 2. What the second world says

**The change is the world's too, and the proof is one matched seed.** At the held-out seed **11** the world-0 change is
**+0.1031** at **9.08** sigma and the world-1 change is **+0.0333** at **2.54**: a difference of **+0.0698** at **5.15**
sigma across the twenty replicates the two rolls share. At the other three seeds the two worlds' changes agree --
**+0.0125** at **0.64**, **-0.0302** at **-1.60** and **+0.0073** at **0.47**. **So the sentence `e474` published --
*both the level and the change are the draw's* -- is not the whole of it**: the change is also the **environment's**,
and a redraw that leaves the cue set, the circuit, the head and the training schedule alone moves it by more than five
sigma on one of the four cue sets the line has drawn.

**And the second world has its own null draw, and it is a different draw's.** At seed **19** in world 1 the baseline
reads **0.7500** before the sequence and **0.7500** after: **-0.0000** at **-0.00** sigma, a tie to four decimals where
at seed **3** the same world's change is **+0.0594** at **4.53**. World 0's null draw was seed **19** as well
(**+0.0073** at **0.53**), but the two nulls are not the same measurement: world 1's initial body already reads
**0.7500** on that cue set against world 0's **0.6875**, so what the second world adds on the draw the first could not
move is nothing at all. **So `e474`'s *positive on three of the four cue sets* is not an accident of one world**: a
second environment is null on one of its four as well.

**And the draws still disagree one world over.** Within world 1 the six pairs of draws run from **-0.0396** at **-3.01**
sigma to **+0.0990** at **+5.81** and **four of the six** resolve -- the same count `e474` got at world 0. **So the
draw's share of the change is not the first world's either**, and the sharpest pair in each world is **7 against 19**
(**+0.0615** at **4.65** at world 0, **+0.0990** at **+5.81** at world 1).

**And the level's own spread reverses the ranking `e474`'s fourth claim was about.** World 0's four levels spread
**0.1281** against its changes' **0.0958**; world 1's four levels spread **0.0594** against its changes' **0.0990** --
so *the level moves more between draws than the change does* holds in the world it was measured in and **does not
reproduce** in the world beside it, where the change's spread is the larger by **1.67** to one. **This unit registered
no claim about the direction of that inequality**, and it is reported here as the two spreads the artifact carries
rather than as a decided result -- what it shows is that the ordering of the two is itself a world's.

**And the world moved the sequence, which is what makes the comparison a comparison.** The sequence's own replicates are
**bit-identical** across the four draws **within** world 1 -- **6 of 6** shared arms, record for record -- and **0 of
24** arms are identical **between** the worlds. So the flag draws the held-out cue set and nothing else **inside** a
world, exactly as `e473` and `e474` found, while the environment's own seed redraws the sequence completely, which is
the manipulation working rather than a confound.

**And the anchoring is a null in the second world at all four draws.** `ewc-block` runs from **-0.0354** at **-1.57**
sigma to **-0.0115** at **-0.64** and `ewc-block-rand` from **-0.0292** at **-1.24** to **-0.0042** at **-0.22**, none
resolving, so the partition's cost on a task outside the sequence is a null in a second environment, which is the
`basis` clause's null read a sixth time.

## 3. What it cannot do

- **Two worlds are not a population**: a second world is one more sample of the environment and not its sd, and the
  **5.15** sigma at seed 11 is one difference rather than the world's spread -- the same trap `e473` fell into and
  `e474` corrected for the draw.
- **And a probe is not a task**: every level and every change is of **linear readability** from the frozen body.
- **And one ridge**: **1e-2** is `e469`'s, and a different ridge would move every cell in the tables above.
- **And one budget**: all sixteen rolls are at a hundred updates, so the crossings `e467` and `e468` found on the
  sequence's own diagonal are not measured in either world.
- **And the world is one field**: `--loop-seed` redraws the environment's three populations, its cue templates and its
  three maps together, so which of them the movement rides on is not separated -- and the null draw is likewise one
  field's.

## RE-READ 2026-10-09: `e474`'s fourth claim is one world's, and its own table mis-stated the initial body

Two corrections ride with this unit, both surfaced by reading the same eight world-0 rolls again.

**The first is a defect in `e474`'s table.** Its section 1 reports the baseline's **initial** body as **0.6875** at all
four draws. `e474`'s own artifact -- and this unit, reading the same four rolls -- has **0.6875**, **0.5625**,
**0.6042** and **0.6875** for draws **3**, **7**, **11** and **19**, and only the first and the last are consistent with
the changes that table prints beside them (**+0.0719** and **+0.0073** against **0.6875**). The two cells are corrected
in place; no other number in that finding moves.

**The second is a scope.** `e474`'s **AA4** -- *the level moves more between draws than the change does* -- **MET** on
its four draws and is a statement about **one world**: in world 1 the level's spread is **0.0594** and the change's is
**0.0990**, the reverse. What survives is the sentence `e474`'s first three claims built: both the level and the change
are the draw's, and both are the world's as well
(`docs/findings/2026-10-09-the-held-out-level-across-four-draws.md`).
