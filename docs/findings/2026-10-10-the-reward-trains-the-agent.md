# The reward trains the agent: the payout moves the map, and the task pays for it

*2026-10-10. `experiments/e488_the_reward_trains_the_agent.py` gives the loop's policy an optimizer of its own and
ascends the world's **payout** into it, then reads the run beside the same command with the map trained by the **task
loss**. **XB1, XB2, XB3 and XB4 all MET** -- and the earning is **+2.75** to **+3.64** in a currency whose cells run
about **-8.5**, while the accuracy falls on every arm.*

## 1. The two runs

The card's neutral roll with `--loop-policy --loop-reward`, once with `--loop-earn` and once without it. The paid run
is the map trained by the world's payout; the loss run is the map trained by the task loss, which is every policy run
this corpus holds.

| the arm | the paid run's reward diagonal | the loss run's | the earning | sigma | the paid run's accuracy diagonal | the loss run's | the change | sigma |
|---|---|---|---|---|---|---|---|---|
| `naive` | **-4.9116** | -8.5564 | **+3.6449** | **+40.01** | 0.7649 | **0.7969** | -0.0319 | -2.64 |
| `ewc-block` | **-4.9383** | -8.5214 | **+3.5831** | **+35.63** | 0.7281 | **0.7691** | -0.0410 | **-3.30** |
| `replay` | **-5.6984** | -8.4516 | **+2.7531** | **+21.16** | 0.7240 | **0.7524** | -0.0285 | -1.67 |

and each run's own shape in the two currencies, which is what the diagonal is a mean of:

| the run | the arm | the reward diagonal | the reward last row | the contrast | the accuracy diagonal | the accuracy last row |
|---|---|---|---|---|---|---|
| paid | `naive` | -4.9116 | -5.3752 | **+0.4636** | 0.7649 | 0.4733 |
| paid | `ewc-block` | -4.9383 | -5.4276 | **+0.4893** | 0.7281 | 0.4535 |
| paid | `replay` | -5.6984 | -5.5576 | -0.1408 | 0.7240 | 0.6149 |
| loss | `naive` | -8.5564 | -7.9428 | -0.6136 | 0.7969 | 0.5045 |
| loss | `ewc-block` | -8.5214 | -7.9388 | -0.5826 | 0.7691 | 0.5340 |
| loss | `replay` | -8.4516 | -8.3177 | -0.1339 | 0.7524 | 0.6608 |

| claim | measured | verdict |
|---|---|---|
| XB1 the two runs are one configuration with only what trains the map moved | **53** config fields, **0** differing past the inert rule; the draw **23** fields, **0** differing; **20** replicates each | **MET** |
| XB2 the payout moves the map on every replicate | **60 of 60** replicates above zero, the smallest **4.2209**, the mean **5.09** to **5.63** | **MET** |
| XB3 being paid earns more than being trained on the task | **all three** arms over the bar **0.25**: **+3.6449**, **+3.5831**, **+2.7531** at **40.01**, **35.63** and **21.16** sigma | **MET** |
| XB4 being paid does not buy the task | no arm rises; all three **fall**, `ewc-block` by **0.0410** at **-3.30** sigma | **MET** |

## 2. What the paid map does

**The game's own currency is a signal now, and it is a strong one.** Taking the map out of the body's optimizer and
ascending the payout into it lifts what the world pays on **every** arm by **+3.64**, **+3.58** and **+2.75** at
**40.01**, **35.63** and **21.16** sigma -- against a bar registered at **0.25**, which is the smallest difference
this currency had been shown to carry. **So `e487`'s third claim, that the payout is inert for the training, was a
statement about a map nobody was paying**: the same flag that measured the payout as a meter, with one more flag
beside it, makes it the thing that moves the agent.

**And the map the task trains is worse than no map at all.** The loss run's reward cells run about **-8.5**, and
`e485`'s run -- the same world and the same payout with no map at all -- ran about **-6.85**. **That comparison is
not one configuration** (the policy flags differ, so it is not this unit's pairing and this unit registers no claim
about it) but the direction is the one the win is built on: the task loss has no term in it for what the world pays,
so a map it trains walks the world's state away from the cue's target, and the payout is where that shows.

**And being paid is paid for in the task.** The accuracy falls on **every** arm -- **0.0319**, **0.0410** and
**0.0285** -- and on `ewc-block` it **resolves downward** at **-3.30** sigma. So the paid map is not a better map:
it is a map that earns, and the benchmark's own metric is what it costs. The two currencies had already been found
disagreeing (`e485`, `e487`); here one of them is the training signal and the disagreement has a price.

**And the payout's own shape is not a constant of the game.** In `e485`'s run the reward's diagonal sat **below** its
last row on every arm, and in the loss run it still does (**-0.6136**, **-0.5826** and **-0.1339**) -- but in the
paid run the diagonal sits **above** its last row on **two** of the three arms (**+0.4636** and **+0.4893**). The
unit registered no claim about that and it is a reading rather than a result: what it says is that *the sequence's
early tasks pay less than its last one*, which `e485` read as the currency's signature, is a property of the map
rather than of the world.

**And the paid map's optimum sits closer to the identity than the task loss's.** The map is handed its freedom at
the environment's own action rule and, trained by the payout, ends **4.2209** to **5.6252** away from it; trained by
the task loss it ends **6.7094** to **9.2607** away. So the thing the world pays for is nearer the loop the
environment already runs than the thing the labels pay for.

**And the two runs are one world and one payout.** **53** config fields with **none** differing past the inert rule,
the one moved field being `loop_earn` (`true`, `false`), and every **23** draw fields equal -- including the payout's
own map. So the earning is measured against one ablation of what trains the map and not against a sweep of it.

## 3. What it cannot do

- **One configuration**: the card's neutral roll at one world, one budget and one seed stream, so the ablation is a
  single one -- the task loss -- and a stronger or weaker one is not in the unit.
- **And one learning rate**: the map's ascent runs at the run's own `--lr`, so how hard it is paid is not swept.
- **And the payout is the corpus's noisiest currency**: `e484` found its cue-share under its own scatter and `e487`
  found the currency's level moving by half between two worlds, so the **+2.75** to **+3.64** are large differences
  in cells running about **-8.5** and the sigmas are large for that reason.
- **And the head is never paid**: the map drives the world and the world pays, while the labels train the body and the
  decoders, so the accuracy's fall is a cost and not a measurement of the paid agent's own quality.
- **And the map is linear over one population**, covered by no penalty, with the recurrent weights on the other side
  of the loop -- so what is paid is one parameter set and not the agent.
- **And nothing here says what an episode is**: the card's `absent` list still carries **an episode boundary**, and
  this unit does not touch it.
