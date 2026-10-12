# The pass plays for the payout: the map earns inside the episode, and the pass is free

*2026-10-12. `experiments/e500_the_pass_plays_for_the_payout.py` runs the paid, label-first, two-trial episodic pass
with **`--loop-policy --loop-earn`** on -- the map the agent acts through is taken out of the body's optimizer and
trained by ascent on the world's payout -- and reads it against `e498`'s paid **meter** run. **QA1, QA2 and QA3 all
MET.** The payout reaches the map: the world pays **+1.07** to **+1.51** more on every arm at **15.5** to **22.7**
sigma, and the pass is learned unchanged -- so `e498`'s flat currency was flat because nothing was playing for it.*

## 1. The run, the map and the two currencies

`e498`'s own command with two flags added: `--loop-policy`, which the runner turns into a map per replicate
initialized at the environment's own action rule, and `--loop-earn`, which gives that map an optimizer of its own and
ascends the world's payout into it. `--loop-earn` needs `--loop-policy` for the map and `--loop-reward` for the
payout, and the runner's own **sixteen** refusal messages name the ascent twice and the episode or the placement
**zero** times, so the pair runs.

| the arm | the earned run's reward diagonal | the meter run's | the gain | sigma | the earned run's accuracy diagonal | the meter run's | the change | sigma | the map's distance from the identity |
|---|---|---|---|---|---|---|---|---|---|
| `naive` | **-4.5457** | -6.0542 | **+1.5086** | **+22.74** | 0.8281 | 0.8299 | -0.0017 | -0.25 | 5.8133 |
| `ewc-block` | **-4.5947** | -6.0070 | **+1.4123** | **+22.57** | 0.8153 | 0.8139 | +0.0014 | +0.17 | 5.2579 |
| `replay` | **-5.0295** | -6.1017 | **+1.0722** | **+15.54** | 0.8247 | 0.8267 | -0.0021 | -0.36 | 6.7272 |

and each run's own shape in the currency, which is what the payout did to the level and to the diagonal:

| the arm | the earned run's reward diagonal | its last row | the contrast | sigma | the meter run's contrast | sigma |
|---|---|---|---|---|---|---|
| `naive` | -4.5457 | -5.2518 | **+0.7061** | **+18.68** | +0.0104 | +0.27 |
| `ewc-block` | -4.5947 | -5.3741 | **+0.7794** | **+23.09** | -0.0123 | -0.31 |
| `replay` | -5.0295 | -4.9331 | **-0.0964** | **-4.21** | +0.0547 | +1.78 |

the map's distance from the identity, per replicate, beside `e488`'s own earn run at one trial per pass:

| the arm | the new run's mean | its smallest replicate | `e488`'s own mean | replicates above zero |
|---|---|---|---|---|
| `naive` | **5.8133** | 4.4082 | 5.0935 | **20 of 20** |
| `ewc-block` | **5.2579** | 3.9475 | 5.3670 | **20 of 20** |
| `replay` | **6.7272** | 5.4594 | 5.6252 | **20 of 20** |

| claim | measured | verdict |
|---|---|---|
| QA1 the pair runs and is two flags apart | **0** config fields differing past the inert rule over **60** with `loop_policy` and `loop_earn` the two moved, the draw **28** fields with **0** differing, **0** added and **0** missing, **20** replicates, and **0** of the runner's **16** refusal messages naming the pair | **MET** |
| QA2 the payout reaches the map | the map is above zero on **60 of 60** replicates, the smallest **3.9475**; the reward's diagonal is above the meter run's on **3 of 3** arms -- **+1.5086**, **+1.4123** and **+1.0722** at **+22.74**, **+22.57** and **+15.54** sigma | **MET** |
| QA3 the pass is still learned while the map is trained by the payout | the diagonals are **0.8281**, **0.8153** and **0.8247** against the meter run's **0.8299**, **0.8139** and **0.8267**, every arm at least **0.10** above the chance of **0.25** and none more than **0.10** under | **MET** |

## 2. What it says

**And the payout reaches the map inside the episode.** The map ends **3.9475** to **8.0630** from the identity it was
handed, above zero on **every one of the sixty** replicates, and what the world pays rises on **every arm**: **+1.5086**,
**+1.4123** and **+1.0722** at **+22.74**, **+22.57** and **+15.54** sigma, in cells running about **-6.05** on the
meter run. **So `e498`'s flat currency was flat because nothing was playing for it**: the same pass, the same world,
the same read, the same placement and the same payout gave contrasts of **+0.0104**, **-0.0123** and **+0.0547** at
**+0.27**, **-0.31** and **+1.78** sigma with the map a meter, and with the map paid they are **+0.7061**, **+0.7794**
and **-0.0964**. `e488` found the same thing at one trial per pass (**+2.75** to **+3.64**); this is the episodic
pass, and the earning is there too.

**And the currency's shape is the map's rather than the world's.** In the meter run no arm's diagonal separates from
its last row; in the earned run the diagonal sits **above** its last row on two arms (**+0.7061** at **+18.68** and
**+0.7794** at **+23.09** sigma) and **below** it on the third (**-0.0964** at **-4.21**). That is `e488`'s own
reading of its paid map -- the diagonal above its last row on two of three arms, **+0.4636** and **+0.4893** --
replicated at a second pass, and it says the *the sequence's early tasks pay less* signature the one-trial corpus read
as the currency's is a property of **what is driving the world** and not of the world.

**And here the pass is free, where at one trial it was paid for.** Every arm's accuracy is within **0.0021** of the
meter run's -- **-0.0017**, **+0.0014** and **-0.0021** at **-0.25**, **+0.17** and **-0.36** sigma, none of them
resolved -- and all three still sit **0.5653** to **0.5781** above the four-class chance. `e488`'s one-trial paid run
lost accuracy on **every** arm instead, by **0.0285** to **0.0410**, with `ewc-block` resolving at **-3.30** sigma and
closing on *being paid is paid for in the task*. **So the price is the pass's and not the earning's**: inside a
two-trial episode the map the payout trains is a map the head's own metric does not see, and the two currencies `e485`
and `e487` found disagreeing can be made to agree on the level the benchmark reports.

**And the map travels further inside the episode than at one trial.** **5.2579** to **6.7272** on average against
`e488`'s one-trial **5.0935** to **5.6252**, with the single smallest replicate at **3.9475**. The unit registers no
claim about it -- a different pass in a different run is not this pairing -- but it is the reading the two artifacts
give side by side, and it says the episode's longer loop leaves the map more room to use.

**And the pair is two flags and one world.** **60** config fields with **none** differing past the inert rule, the two
moved being `loop_policy` and `loop_earn`; the environment's draw **28** fields field for field, with **none** added,
**none** missing and **none** differing -- including the payout's own map, which `e498` had just put the boundary's
draw before; and both runs at **20** replicates. **So the earning is measured against one ablation of what trains the
map** -- the task loss -- over one world, one pass, one read, one placement and one payout.

## 3. What it cannot do

- **One episode length and one placement**: two trials of six steps with the label first, `e495`'s own pass; the
  three- and four-trial splits and the passes with the label at an interior trial are not in it.
- **And one map and one payout shape**: a linear map over one action population, covered by no penalty, ascending
  the environment's own linear read of the cue. A non-linear map, a penalty on the map, or a second payout shape is
  a different unit.
- **And the payout is read on the map and not on the action**: what is ascended is the negative squared distance
  from the world's final state to the target the cue sets one step after it arrives, so the earning is a
  state-matching currency and not an action's reward. A reward on the action, or one sparse in time, is a different
  unit.
- **And one world, one budget, one learning rate and one seed stream**: the card's own setting, with the map's
  ascent at the run's own `--lr`, so how hard it is paid is not swept and the **+1.07** to **+1.51** are one
  configuration's.
- **And the head is never paid**: the labels train the body and the decoders while the payout trains the map, so an
  agent that earns more is not thereby one that classifies better -- here it classifies the same, which is a
  measurement of the two currencies on one run and not of the paid agent's own quality.
- **And a claim over arms is not a claim about the world**: three arms is a small population to read a currency's
  shape from, and the two arms that carry the diagonal over the last row here are the same two `e488` found.

## RE-READ 2026-10-13

**The pass's second rung is paid, and the earning survives it.** This unit's *cannot do* closed on *one episode
length and one placement ... the three- and four-trial splits and the passes with the label at an interior trial
are not in it*; `e501` takes the three-trial rung: this unit's own command with `--loop-episode 3` and
`--loop-policy --loop-earn`, read against its own meter run. The map ends **4.1854** to **6.6939** from the identity
on **60 of 60** replicates and the world pays **+1.0131**, **+1.3586** and **+1.4562** more at **+19.68**,
**+36.39** and **+22.92** sigma -- the same two flags, the same world and the same payout at a longer pass -- with
the accuracy unchanged to **0.0038**. So the **+1.07** to **+1.51** this unit measured at two trials are a property
of the pair and not of the pass's length, and the four-trial split remains the rung above. This unit's numbers
stand.
