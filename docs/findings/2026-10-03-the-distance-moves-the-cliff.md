# The distance moves the cliff: eleven of sixteen draws are one hop, not two, and the cliff follows the walk every time

*2026-10-03. `experiments/e370_the_distance_moves_the_cliff.py` draws **sixteen** configurations -- eight population
seeds at each of two circuit sizes -- measures each one's cue-to-action distance in the mask, and rolls both drive
sources at every cue step of every draw. Twenty-three seconds. Writes
`runs/e370_the_distance_moves_the_cliff.json`. Four claims, registered before any distance and any curve was read.*

## 1. The result

**Sixteen of sixteen cliffs are their own draw's distance, and the distance is not always two.**

| distance | configurations | direct cue-to-action edges | measured last clearing step |
|---|---|---|---|
| **1** | **11** | 1, 2 or 4 | **9** (all eleven) |
| **2** | **5** | **0** | **8** (all five) |

| claim | measured | verdict |
|---|---|---|
| Q1 the sweep moves the distance | distances `[1 x11, 2 x5]`, none unreachable | **MET** |
| Q2 every cliff is its own draw's distance | 16 of 16 measured steps equal `tau - 2 - d` | **MET** |
| Q3 a shorter walk buys exactly the step it saves | distance 1 clears at 9, distance 2 at 8 | **MET** |
| Q4 the control does not move | the cue source clears at **10** in all sixteen | **MET** |

**The direct-edge count is the whole of it.** Each of the five two-hop draws has **zero** direct edges from the cue
population into the action population; the eleven one-hop draws have one, two or four. The distance is one when a
direct edge exists and two when it does not, so the formula's `d` is a count the mask answers directly.

**And the control holds the instrument still.** The cue source's distance is **0** in every draw by construction --
`drive_from_cue` makes the drive population the cue population itself -- and its cliff is **10** in all sixteen
configurations at both sizes, while its own internal edge count ranges over 0 to 7 and its curve above the cliff
ranges from 0.69 to 0.89. What the sweep moves is the action population's walk and not the draw.

## 2. What it revises

**`e369`'s headline was a fact about one draw.** That unit measured the distance at the corpus's default population
seed, found **2**, and wrote *"the cue population is two hops from the action"*. This sweep says the two-hop case is
the **minority**: eleven of sixteen draws are one hop, and the default seed is in the five that are not. The
**formula** survives untouched -- `tau - 2 - d` predicts sixteen cliffs out of sixteen -- and what does not survive
is the number: for a world listening to the agent's own action the typical cliff is **9**, and the corpus has spent
four units on the draw whose cliff is 8.

That is not a defect in those units, and it is worth being exact about why: `e363`, `e367`, `e368` and `e369` all
roll the same configuration, `seed0 = 0` with `loop_seed` following it, so they are four measurements of one draw
and they agree with each other to the digit. What none of them could see from inside is that the draw is
unrepresentative, and the only way to see it is the sweep this unit ran.

**The step the extra hop buys is the weakest one.** At distance 1 the last clearing step is 9 and it reads
**0.3438** in one draw and **0.5312** in another, against **0.7617** at step 8 in a two-hop draw: the cliff moves by
exactly one step and the step it moves to carries a trace that has had one world-update to arrive instead of two.
So Q3's "exactly the step it saves" is about the **step** and not about the accuracy at it, which is the same split
`e369` registered and did not resolve.

## 3. What it means

**The horizon is a distribution and not a number.** A closed-loop task on this world that reads the agent's own
action has about **steps 0 to 9** in the modal draw and **steps 0 to 8** in the default one, and which of the two it
is depends on whether the three drawn populations happen to contain a direct edge. Both numbers are computable from
the mask before anything is rolled, and `e369`'s formula is what makes them computable; this unit is what says the
number it produces has a spread.

**And it makes the corpus's own default a stated choice.** Anything built on this line inherits `seed0 = 0` and
therefore the two-hop draw unless it says otherwise, and a game whose horizon depends on a population draw should
either report which draw it is on or average over them. That is the operational content of the sweep.

## 4. What it cannot do

*Distances one and two*: sixteen draws produced two values, and a hop count of three or more is possible in
principle -- it needs both a missing direct edge and no route through a third population -- and is not what this
sweep produced, so the formula is checked where it lives and not at its extremes. *Two circuit sizes, one
extraction each*: the mask is one connectome's, so nothing here is a statement about a different annotation or a
different circuit-selection rule. *And Q2 is an equality of numbers, not a derivation*: the formula is about the
trace **existing** and the measurement is about a least-squares probe at 512 examples **clearing chance**, so the
sixteen agreements are evidence for the identification rather than a proof of it, and the accuracy at the last
clearing step -- 0.3438 at its weakest -- is where the two would part first.
