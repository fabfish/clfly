# The reward in a second world: the reversal reproduces and the improvement does not

*2026-10-09. `experiments/e487_the_reward_in_a_second_world.py` redraws the world under the payout: the card's own
command with `--loop-seed 1`, both with `--loop-reward` and without it, read beside `e485`'s world-0 run. **RA1, RA3
and RA4 MET** and **RA2's falsifier FIRED**.*

## 1. The second world

| the arm | the reward diagonal | the reward last row | the contrast | sigma | the accuracy diagonal | the accuracy last row |
|---|---|---|---|---|---|---|
| `naive` | -4.3200 | -4.3553 | +0.0353 | **0.87** | **0.7892** | 0.5097 |
| `ewc-block` | -4.2864 | -4.2516 | -0.0348 | **-0.93** | 0.7677 | 0.5295 |
| `replay` | -4.2609 | -4.2685 | +0.0077 | **0.46** | 0.7674 | 0.6854 |

and world 0's, from `e485`, for the comparison the unit exists for:

| the arm | the reward contrast, world 0 | sigma | the reward contrast, world 1 | sigma |
|---|---|---|---|---|
| `naive` | **-0.3218** | **-4.91** | +0.0353 | 0.87 |
| `ewc-block` | **-0.3503** | **-4.98** | -0.0348 | -0.93 |
| `replay` | **-0.1877** | **-3.46** | +0.0077 | 0.46 |

| claim | measured | verdict |
|---|---|---|
| RA1 the three runs are one configuration with the world and the payout moved | **51** config fields, **0** differing past the inert rule; the draw **22** fields between the two world-1 runs, **0** differing; **20** replicates each | **MET** |
| RA2 the reward keeps its shape in the second world | the contrasts are **+0.0353**, **-0.0348** and **+0.0077** at **0.87**, **-0.93** and **0.46** sigma | **FALSIFIER FIRED** |
| RA3 the payout does not touch the accuracy | the two world-1 runs' `learned` and `final_per_task` vectors agree **record for record** on all three arms | **MET** |
| RA4 the two currencies disagree in the second world too | the accuracy orders them `naive`, `ewc-block`, `replay` and the reward **`replay`, `ewc-block`, `naive`** | **MET** |

## 2. What the second world says

**The reversal reproduces, and the improvement does not.** In world 1 the accuracy still orders the arms `naive`
(**0.7892**), `ewc-block` (**0.7677**), `replay` (**0.7674**) and the reward orders them **exactly the other way**
(**-4.2609**, **-4.2864**, **-4.3200**) -- so `e485`'s sentence *the arm the benchmark calls best is the arm the world
pays least* **is not a world's**. **And `e485`'s other half is**: the reward's diagonal being below its last row on
every arm, at **-4.91** to **-3.46** sigma in world 0, is **+0.0353**, **-0.0348** and **+0.0077** at **0.87**,
**-0.93** and **0.46** sigma in world 1 -- **unresolved on every arm and of mixed sign**. **So the game's own
currency is flat in the second world where the accuracy still forgets** by **0.2795**, **0.2382** and **0.0820**.

**And the two worlds' currencies are not the same currency.** World 1's reward cells run about **-4.3** where world
0's run about **-6.9**, so the payout's level is a property of the world and not of the sequence -- which is why
`e485`'s *the sequence raises what the world pays* was readable there and is not here. **A reward whose units move by
half between two draws of the same command** is a currency a comparison must be drawn within, and this unit draws its
comparison within world 1.

**And the payout touches nothing the accuracy sees.** The two world-1 runs -- the payout on and off, the same world,
the same seeds, one flag apart -- have **identical** `learned` and `final_per_task` vectors on all three arms,
**record for record**. **So the flag is inert for the training** and the reward matrices of the two are two readings
of one body, which is what makes RA3 a check rather than a formality: the payout is drawn last and enters no loss.

**And the three runs are one configuration, in the fields and in the draw.** **51** config fields with **none**
differing past the inert rule, the moved fields being `loop_seed` (`1`, `1`, `null`) and `loop_reward` (**true**,
**null**, **true**), and the environment's own draw agreeing on all **22** fields between the two world-1 runs -- the
payout's map being the one the payout adds. **So the two world-1 runs differ in the payout and nothing else**, which
is what lets RA3 compare them and RA4 read one body's two currencies.

## 3. What it cannot do

- **Two worlds are not a population**: a second world is one more sample of the environment, and the reversal holding
  in it is two worlds and not a family.
- **And one budget and one seed stream**: both worlds are the card's own setting, so a budget or a stream is not in it.
- **And the reward is the corpus's noisiest currency**: `e484` found its cue-share under its own scatter, so RA2's
  firing is a statement about **-0.32** to **+0.04** in cells running about **-4.3**, which is a coarse instrument.
- **And the head is never paid**: what the reward says is the body's, and the accuracy's is the head's and the body's.
- **And nothing here optimizes the payout**: it is recorded and not played for, which is a different unit.
