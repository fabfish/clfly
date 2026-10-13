# The world pays the action: the payout read on the agent's own one-step response, and the pass is still learned

*2026-10-13. `experiments/e502_the_world_pays_the_action.py` reads `e500`'s own two-trial, label-first, paid
episodic pass with **`--loop-reward-on-action`** added -- the same target, the same step and the same payout, read on
the world's **one-step response to the action** instead of on the state it has carried -- and reads the earned run
against its own meter run and against `e500`'s carried-state run. **TA1, TA2 and TA3 all MET.** The action's currency
is alive (**+3.04** to **+4.14** more on every arm at **15.1** to **23.6** sigma, the map above the identity on
**60 of 60** replicates) and the pass is still learned (every arm over the bar, none more than **0.10** under).*

## 1. The substrate, the two runs and the two currencies

`CueActionEnv` gains **`reward_on_action`**, a rule and not a draw: off is the carried state every artifact holds, on
is the world's **one-step response to the action** -- the `drive` the step already hands the world, before the carry
-- scored against the same target at the same step. The runner gains **`--loop-reward-on-action`**, recorded in the
run's `config` as `loop_reward_on_action`; the flag consumes nothing from the environment's generator, so the draw is
the one `e500` wrote field for field. Two runs: `e500`'s own two-trial, label-first, paid command with the flag
added, the **meter** run and the same plus `--loop-policy --loop-earn`, the **earned** run.

| the arm | the action run's reward diagonal | the meter run's | the gain | sigma | the action run's accuracy diagonal | the meter run's | the change | sigma | the map's distance from the identity | `e500`'s carried-state map |
|---|---|---|---|---|---|---|---|---|---|---|
| `naive` | **-3.8024** | -7.8884 | **+4.0860** | **+21.68** | 0.8288 | 0.8299 | -0.0010 | -0.15 | 3.3914 | 5.8133 |
| `ewc-block` | **-3.8560** | -7.9915 | **+4.1356** | **+23.62** | 0.8170 | 0.8139 | +0.0031 | +0.55 | 3.5436 | 5.2579 |
| `replay` | **-4.8238** | -7.8619 | **+3.0381** | **+15.12** | 0.8167 | 0.8267 | -0.0101 | -1.61 | 4.1694 | 6.7272 |

and each run's own shape in its own currency, which is what the payout did to the level and to the diagonal:

| the arm | the action run's reward diagonal | its last row | the contrast | sigma | the meter run's contrast | sigma |
|---|---|---|---|---|---|---|
| `naive` | -3.8024 | -5.0846 | **+1.2822** | **+16.07** | +0.2280 | +1.81 |
| `ewc-block` | -3.8560 | -5.1561 | **+1.3002** | **+19.20** | +0.2337 | +2.55 |
| `replay` | -4.8238 | -4.7242 | **-0.0996** | **-2.29** | +0.0711 | +1.25 |

the map's distance from the identity, per replicate, beside `e500`'s own carried-state run:

| the arm | the action run's mean | its smallest replicate | `e500`'s own mean | replicates above zero |
|---|---|---|---|---|
| `naive` | **3.3914** | 2.5798 | 5.8133 | **20 of 20** |
| `ewc-block` | **3.5436** | 2.7274 | 5.2579 | **20 of 20** |
| `replay` | **4.1694** | 3.4034 | 6.7272 | **20 of 20** |

| claim | measured | verdict |
|---|---|---|
| TA1 the new flag moves the payout and nothing else | **0** config fields differing past the inert rule over **61** with `loop_reward_on_action` the one moved, the draw **28** fields with **0** differing, **0** added and **0** missing, **20** replicates | **MET** |
| TA2 the action's currency is alive | the map is above zero on **60 of 60** replicates, the smallest **2.5798**; the reward's diagonal is above the meter run's on **3 of 3** arms -- **+4.0860**, **+4.1356** and **+3.0381** at **+21.68**, **+23.62** and **+15.12** sigma | **MET** |
| TA3 the pass is still learned | the diagonals are **0.8288**, **0.8170** and **0.8167** against the meter run's **0.8299**, **0.8139** and **0.8267**, every arm at least **0.10** above the chance of **0.25** and none more than **0.10** under | **MET** |

## 2. What it says

**And the world's one-step response is a currency an agent can be paid in.** On the same pass, the same world, the
same read, the same placement and the same target, reading the payout on the action's own one-step response rather
than on the world's carry lifts what the world pays by **+4.0860**, **+4.1356** and **+3.0381** on every arm at
**+21.68**, **+23.62** and **+15.12** sigma, and the map the agent acts through ends **2.5798** to **4.1694** from
the identity it was handed, above zero on **every one of the sixty** replicates. So `e500`'s **-4.5457**, **-4.5947**
and **-5.0295** were the carry's level and not the payout's: the same ascent, paid in the action's currency, sits at
**-3.8024**, **-3.8560** and **-4.8238**.

**And the currency's shape is the map's, as it was for the carry.** In the action's currency the earned run's
diagonal sits **above** its last row on two arms (**+1.2822** at **+16.07** and **+1.3002** at **+19.20** sigma) and
**below** it on the third (**-0.0996** at **-2.29**), the same two-arms-up signature `e488`, `e500` and `e501` found
in the carried currency. The meter run's own shape in the action's currency is small and positive on all three arms
(**+0.2280**, **+0.2337** and **+0.0711**) and resolves on one (**ewc-block**, **+2.55** sigma), where `e500`'s
carried-state meter run was flat (**+0.0104**, **-0.0123** and **+0.0547** at **+0.27**, **-0.31** and **+1.78**).
So what separates the diagonal from the last row is still **what is driving the world** and not the world.

**And the pass is free in the action's currency too.** Every arm's accuracy is within **0.0101** of the meter run's
-- **-0.0010**, **+0.0031** and **-0.0101** at **-0.15**, **+0.55** and **-1.61** sigma, none of them resolved --
and all three still sit **0.5667** to **0.5788** above the four-class chance. So the price `e488` measured at one
trial per pass does not return when the payout reads the action: the two currencies are two ways to read the same
payout, and on this pass both leave the head's own metric where it was.

**And the read is one field and one world.** Against `e500`'s own earned run the config differs in **nothing** past
the inert rule over **61** fields -- `loop_reward_on_action` the only field moved, the output path and the saved
weights the run's own bookkeeping -- and the environment's draw is the carried-state run's **28** fields field for
field, with **none** added, **none** missing and **none** differing, the payout's own map among them. **So what
changed when the currency moved from the carry to the action is the quantity the reward is scored on and nothing
else**: one world, one pass, one read, one placement, one target and one seed stream.

**And the map travels less far in the action's currency.** **2.5798** to **4.1694** against `e500`'s carried-state
**3.9475** to **8.0630**, with the means **3.3914**, **3.5436** and **4.1694** against **5.8133**, **5.2579** and
**6.7272**. The unit registers no claim about it -- a different currency in a different run is not this pairing -- but
it is the reading the two artifacts give side by side, and it says the action's payout leaves the map closer to the
rule the agent started from while the world pays more.

## 3. What it cannot do

- **One episode length and one placement**: two trials of six steps with the label first, `e495`'s own pass; the
  three- and four-trial splits and the passes with the label at an interior trial are not in it.
- **And one threshold, not a score and not a sparse reward**: the payout is the action's **one-step response** to
  the target the cue sets one step after it arrives, a continuous squared distance read at the last step. A score, a
  reward sparse in time, or the action's response read at another step is a different unit.
- **And one world, one budget, one learning rate and one seed stream**: the card's own setting, with the map's ascent
  at the run's own `--lr`, so how hard it is paid is not swept and the **+3.04** to **+4.14** are one
  configuration's.
- **And three arms is a small population**: a claim over arms is not a claim about the world, and the two arms that
  carry the diagonal over the last row here are the same two `e488`, `e500` and `e501` found.
- **And the carry is not removed from the world, only from the currency**: the world still integrates the agent's
  whole action history and the agent still acts on that state, so what this unit moves is what the payout **reads**
  and not what the loop **is** -- the world's own dynamics, the action's own map to the drive and the feedback the
  agent sees are unchanged.
- **And what is scored is the drive and not the world's state it is projected into**: `drive` is the action
  population through the agent's own policy, of width `n_action`, while the cue's target is the payout map's read,
  of width `world_dims` -- so `-||drive - target||^2` is a comparison of two vectors of **different widths** whose
  coordinates only line up because this run has `n_action = world_dims = 8`. The same flag at another
  `--loop-world-dims` does not compare, and a currency that scores the world's state **one step into the recursion**
  rather than its drive is a different unit. So the reward is read on the agent's own action vector, which is what
  the unit is named for, and the coincidence of widths is a property of the card's configuration rather than of the
  currency.

## RE-READ 2026-10-13

**The rate this unit's earning ran at is swept for the currency the two readers share.** This unit's *cannot do* closed on *one world, one budget, one learning rate and one seed stream, with the map's ascent at the run's own `--lr`, so how hard it is paid is not swept*. `e504` gives the map its own ascent rate through the runner's new `--loop-earn-lr` and reads `e500`'s own two-trial, label-first, **carried-state** pass at **0.001**, **0.003** and **0.01**: the world pays **-4.6798**, **-4.5457** and **-4.4616** on `naive`, **-4.7025**, **-4.5947** and **-4.4738** on `ewc-block` and **-5.0680**, **-5.0295** and **-4.9611** on `replay`, the map travels **3.0280** to **12.6430** from the identity, and every arm's accuracy is within **0.0094** of the meter run's. So the rate the carried-state currency was paid at is a real axis, and the action's own currency at another rate is still a different unit. This unit's numbers stand.

## RE-READ 2026-10-13 (second)

**The interior placements this unit left are measured.** This unit's *cannot do* closed on *the three- and four-trial splits and the passes with the label at an interior trial are not in it*. `e505` reads the placement with the pass's length held at three trials: the pass falls **0.8538**, **0.8392** and **0.8580** to **0.3257**, **0.3069** and **0.3274** to **0.2566**, **0.2576** and **0.2542**, with the label's own part of the read **1.0571**, **0.0489** and **0.0314**. So the pass the action's currency was read on is the placement axis's working end, and the action's currency at an interior placement is a different unit. This unit's numbers stand.
