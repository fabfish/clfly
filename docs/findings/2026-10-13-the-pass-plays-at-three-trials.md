# The pass plays at three trials: the earning survives the pass's second rung

*2026-10-13. `experiments/e501_the_pass_plays_at_three_trials.py` runs `e500`'s paid, label-first episodic pass at
**three trials** -- `--loop-episode 3` with **`--loop-policy --loop-earn`** on -- and reads it against its own
**meter** run, the same configuration without the pair. **RA1, RA2 and RA3 all MET.** The payout reaches the map at
the second rung too: the world pays **+1.01** to **+1.46** more on every arm at **19.7** to **36.4** sigma, and the
pass is learned unchanged -- so the earning `e500` measured at two trials is not a property of the smallest pass.*

## 1. The run, the map and the two currencies

`e500`'s own command with `--loop-episode 3` added: `--loop-policy`, which the runner turns into a map per replicate
initialized at the environment's own action rule, and `--loop-earn`, which gives that map an optimizer of its own and
ascends the world's payout into it. Both runs carry the same world, the same pass, the same read and the same
label-first placement; the meter run turns the two flags off and is what the earned run's two currencies are read
against.

| the arm | the earned run's reward diagonal | the meter run's | the gain | sigma | the earned run's accuracy diagonal | the meter run's | the change | sigma | the map's distance from the identity |
|---|---|---|---|---|---|---|---|---|---|
| `naive` | **-4.4878** | -5.9440 | **+1.4562** | **+22.92** | 0.8563 | 0.8538 | +0.0024 | +0.40 | 5.3064 |
| `ewc-block` | **-4.5730** | -5.9315 | **+1.3586** | **+36.39** | 0.8358 | 0.8392 | -0.0035 | -0.51 | 5.0752 |
| `replay` | **-4.9706** | -5.9837 | **+1.0131** | **+19.68** | 0.8542 | 0.8580 | -0.0038 | -0.75 | 6.6939 |

and each run's own shape in the currency, which is what the payout did to the level and to the diagonal:

| the arm | the earned run's reward diagonal | its last row | the contrast | sigma | the meter run's contrast | sigma |
|---|---|---|---|---|---|---|
| `naive` | -4.4878 | -5.0945 | **+0.6067** | **+13.41** | -0.0407 | -1.54 |
| `ewc-block` | -4.5730 | -5.2453 | **+0.6723** | **+20.85** | -0.1150 | -2.89 |
| `replay` | -4.9706 | -4.9039 | **-0.0667** | **-3.22** | -0.0457 | -1.59 |

the map's distance from the identity, per replicate, beside `e500`'s own two-trial figure:

| the arm | the three-trial run's mean | its smallest replicate | `e500`'s own two-trial mean | replicates above zero |
|---|---|---|---|---|
| `naive` | **5.3064** | **4.4312** | 5.8133 | **20 of 20** |
| `ewc-block` | **5.0752** | **4.1854** | 5.2579 | **20 of 20** |
| `replay` | **6.6939** | **5.4646** | 6.7272 | **20 of 20** |

| claim | measured | verdict |
|---|---|---|
| RA1 the pair at three trials is two flags apart and the pass is the three-trial one | **0** config fields differing past the inert rule over **60** with `loop_policy` and `loop_earn` the two moved, the draw **28** fields with **0** differing, **0** added and **0** missing, both runs at `loop_episode` **3** and `episode_len` **3**, and **20** replicates | **MET** |
| RA2 the payout reaches the map at three trials | the map is above zero on **60 of 60** replicates, the smallest **4.1854**; the reward's diagonal is above the meter run's on **3 of 3** arms -- **+1.4562**, **+1.3586** and **+1.0131** at **+22.92**, **+36.39** and **+19.68** sigma | **MET** |
| RA3 the pass is still learned while the map is paid | the diagonals are **0.8563**, **0.8358** and **0.8542** against the meter run's **0.8538**, **0.8392** and **0.8580**, every arm at least **0.10** above the chance of **0.25** and none more than **0.10** under | **MET** |

## 2. What it says

**And the earning survives the pass's second rung.** The map ends **4.1854** to **6.6939** from the identity it was
handed, above zero on **every one of the sixty** replicates, and what the world pays rises on **every arm**:
**+1.4562**, **+1.3586** and **+1.0131** at **+22.92**, **+36.39** and **+19.68** sigma, in cells running about
**-5.93** on the meter run. `e500` found the same at two trials (**+1.0722** to **+1.5086** at **+15.54** to
**+22.74** sigma), so **the earning is a property of the pair and not of the pass's length**: the same two flags lift
the level inside a two-trial episode and inside a three-trial one, and the four- and six-trial splits are the rungs
above this reading and not measured here.

**And the currency's shape is the map's rather than the world's.** In the meter run no arm's diagonal separates from
its last row (**-0.0407**, **-0.1150** and **-0.0457**, none resolved); in the earned run the diagonal sits **above**
its last row on two arms (**+0.6067** at **+13.41** and **+0.6723** at **+20.85** sigma) and **below** it on the
third (**-0.0667** at **-3.22**). That is `e500`'s own reading of its paid map at two trials -- the diagonal above its
last row on the same two arms -- replicated at the rung above, and it says the *the sequence's early tasks pay less*
signature is a property of **what is driving the world** and not of the world.

**And here the pass is free, exactly as `e500` found it at two trials.** Every arm's accuracy is within **0.0038** of
the meter run's -- **+0.0024**, **-0.0035** and **-0.0038** at **+0.40**, **-0.51** and **-0.75** sigma, none of them
resolved -- and all three still sit **0.5858** to **0.6063** above the four-class chance. **So the price `e488` found
at one trial per pass (`0.0285` to `0.0410` of accuracy) is not paid inside an episode of three trials either**: the
map the payout trains is a map the head's own metric does not see, and the two currencies `e485` and `e487` found
disagreeing are held together on the level the benchmark reports.

**And the map travels the same distance at three trials as at two.** **5.0752** to **6.6939** against `e500`'s own
two-trial **5.2579** to **6.7272**, with the single smallest replicate at **4.1854**. The unit registers no claim
about it -- a second pass in a second run is not that pairing -- but it is the reading the two artifacts give side by
side, and it says the longer loop leaves the map no more and no less room to use than the shorter one.

**And the pair is two flags and one world.** **60** config fields with **none** differing past the inert rule, the two
moved being `loop_policy` and `loop_earn`; the environment's draw **28** fields field for field, with **none** added,
**none** missing and **none** differing; both runs at **20** replicates and at three trials. **So the earning is
measured against one ablation of what trains the map** -- the task loss -- over one world, one pass, one read, one
placement and one payout.

## 3. What it cannot do

- **One payout shape**: the environment's own linear read of the cue, scored one step after the label's cue, so a
  non-linear payout or a second shape is a different unit.
- **And the payout is on the map and not on the world's carry**: what is ascended is the world's own currency and not
  the episode's carried state, so what the earning does to what the world carries at the read step is not in the unit.
- **And two rungs and not a sweep**: three trials against the two `e500` ran, so the **four- and six-trial splits**
  and the passes with the label at an **interior trial** are not in it.
- **And one world, one budget, one learning rate and one seed stream**: the card's own setting, with the map's ascent
  at the run's own `--lr`, so how hard it is paid is not swept and the **+1.01** to **+1.46** are one configuration's.
- **And three arms is a small population**: a claim over arms is not a claim about the world, and the two arms that
  carry the diagonal over the last row here are the same two `e488` and `e500` found.

## RE-READ 2026-10-13

**The payout this pass is paid for is read on the world's carry, and the reader can be the action instead.** This
unit's *cannot do* closed on *the payout is on the map and not on the world's carry*; `e502` takes `e500`'s own
two-trial pass with a new `--loop-reward-on-action`, so the same target at the same step is scored against the
world's **one-step response to the action** rather than against its carried state. The world pays **+4.0860**,
**+4.1356** and **+3.0381** more on every arm at **+21.68**, **+23.62** and **+15.12** sigma, the map above the
identity on **60 of 60** replicates, and the accuracy unchanged to **0.0101** -- the same pair this unit read, with
the reader moved from the carry to the action. This unit's numbers stand.
