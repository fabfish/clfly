# How hard the map is paid: the map's own ascent rate, and the earning rises with it while the pass stays free

*2026-10-13. `experiments/e504_how_hard_the_map_is_paid.py` reads `e500`'s own two-trial, label-first, paid
episodic pass at the map's own ascent rate -- **0.001**, **0.003** (`e500`'s own `--lr`) and **0.01**, through the
runner's new **`--loop-earn-lr`** -- against the pass's own meter run. **UA1, UA2, UA3 and UA4 all MET.** The flag
moves the ascent and nothing else, the world pays more the harder the map is paid, the map travels further, and the
pass's accuracy stands at every point.*

## 1. The substrate, the three points and the meter run

Every earned run in this repository ascends the world's payout into the policy map **at the run's own `--lr`**, and
three units' *cannot do* say the same thing: *"the map's ascent runs at the run's own `--lr`, so how hard it is paid
is not swept."* The runner gains **`--loop-earn-lr`**, threaded to the map's own optimizer where `--loop-earn` sets
it and recorded in the run's `config` as `loop_earn_lr`; **`None` is exactly today's behaviour** -- the run's own
`--lr`. Two new runs are `e500`'s own earned command with the flag at **0.001** and **0.01**; the **0.003** point is
`e500`'s own earned artifact, and the **meter** run is `e498`'s paid run, the same configuration without the pair.

| the point | arm | the reward diagonal | the accuracy diagonal | the map's distance from the identity | its smallest replicate |
|---|---|---|---|---|---|
| **0.001** | `naive` | -4.6798 | 0.8319 | 3.0280 | 2.4683 |
| **0.001** | `ewc-block` | -4.7025 | 0.8233 | 2.9221 | 2.1537 |
| **0.001** | `replay` | -5.0680 | 0.8299 | 3.7398 | 2.8638 |
| **0.003** | `naive` | -4.5457 | 0.8281 | 5.8133 | 4.4082 |
| **0.003** | `ewc-block` | -4.5947 | 0.8153 | 5.2579 | 3.9475 |
| **0.003** | `replay` | -5.0295 | 0.8247 | 6.7272 | 5.4594 |
| **0.01** | `naive` | -4.4616 | 0.8344 | 10.5167 | 8.6043 |
| **0.01** | `ewc-block` | -4.4738 | 0.8191 | 9.8379 | 8.3803 |
| **0.01** | `replay` | -4.9611 | 0.8313 | 12.6430 | 10.1442 |
| **meter** | `naive` | -6.0542 | 0.8299 | -- | -- |
| **meter** | `ewc-block` | -6.0070 | 0.8139 | -- | -- |
| **meter** | `replay` | -6.1017 | 0.8267 | -- | -- |

the two new points against the run's-own-rate point, paired over the twenty replicate seeds:

| the point | arm | the reward diagonal less the 0.003 point's | sigma | the map's travel less the 0.001 point's | sigma |
|---|---|---|---|---|---|
| **0.001** | `naive` | -0.1342 | -4.54 | -- | -- |
| **0.001** | `ewc-block` | -0.1078 | -3.35 | -- | -- |
| **0.001** | `replay` | -0.0385 | -1.07 | -- | -- |
| **0.01** | `naive` | +0.0841 | +2.63 | +7.4887 | +19.41 |
| **0.01** | `ewc-block` | +0.1209 | +2.63 | +6.9158 | +27.42 |
| **0.01** | `replay` | +0.0684 | +1.53 | +8.9032 | +22.72 |

and each point's own shape, its reward diagonal against its own last row:

| the point | `naive` | sigma | `ewc-block` | sigma | `replay` | sigma |
|---|---|---|---|---|---|---|
| **0.001** | +0.5831 | +17.83 | +0.6339 | +18.88 | -0.1209 | -5.79 |
| **0.003** | +0.7061 | +18.68 | +0.7794 | +23.09 | -0.0964 | -4.21 |
| **0.01** | +0.7925 | +20.37 | +0.8185 | +24.56 | +0.0012 | +0.04 |

| claim | measured | verdict |
|---|---|---|
| UA1 the flag moves the ascent and nothing else | **0** config fields differing past the inert rule over **62** on each new run -- the fields the rule covers being `loop_earn_lr`, the output path, the saved weights and `loop_reward_on_action` -- with `loop_earn_lr` recorded **0.001** and **0.01**; the draw **28** fields with **0** differing, **0** added and **0** missing; **20** replicates | **MET** |
| UA2 paying harder earns more | at **0.01** the reward diagonal is above the **0.003** point's on **2 of 3** arms (`naive` **+0.0841** at **+2.63** sigma, `ewc-block` **+0.1209** at **+2.63**, `replay` **+0.0684** at **+1.53**); at **0.001** it is above it on **0** arms (**-0.1342**, **-0.1078**, **-0.0385**) | **MET** |
| UA3 the pass is free at every point | the accuracy diagonals **0.8319**, **0.8233** and **0.8299** at **0.001**, **0.8281**, **0.8153** and **0.8247** at **0.003**, **0.8344**, **0.8191** and **0.8313** at **0.01** against the meter run's **0.8299**, **0.8139** and **0.8267**: **3 of 3** arms in the band at every point and **0** arms within **0.05** of the chance of **0.25** | **MET** |
| UA4 the map travels further when paid harder | the distance from the identity at **0.01** less its distance at **0.001**: **+7.4887**, **+6.9158** and **+8.9032** on **3 of 3** arms at **+19.41**, **+27.42** and **+22.72** sigma, from the means **3.0280**, **2.9221** and **3.7398** to **10.5167**, **9.8379** and **12.6430** | **MET** |

## 2. What it says

**And how hard the map is paid is a real axis, and it is not flat.** The three rates order the world's payout on
**every** arm: **-4.6798**, **-4.5457** and **-4.4616** for `naive`, **-4.7025**, **-4.5947** and **-4.4738** for
`ewc-block`, and **-5.0680**, **-5.0295** and **-4.9611** for `replay`, so the level rises with the rate in the same
order the rates themselves take. Against the run's-own-rate point the two new points are opposite and both resolved:
at **0.01** the payout is above it on **two** of three arms (**+0.0841** and **+0.1209** at **+2.63** sigma each,
`replay` **+0.0684** at **+1.53** and unresolved), and at **0.001** it is **below** it on all three (**-0.1342** at
**-4.54**, **-0.1078** at **-3.35**, **-0.0385** at **-1.07**). So a third of the default rate earns less and three
times the default earns more, which is what `e488`'s *"the strength of the earning is not swept"* left open.

**And the map's travel is the axis the rate moves most.** The distance from the identity is **3.0280**, **2.9221**
and **3.7398** at **0.001**, **5.8133**, **5.2579** and **6.7272** at **0.003**, and **10.5167**, **9.8379** and
**12.6430** at **0.01**, above zero on **60 of 60** replicates at every point, with the **0.01**-less-**0.001**
travel **+7.4887**, **+6.9158** and **+8.9032** at **+19.41**, **+27.42** and **+22.72** sigma. The payout's own rise
across the same span is **0.2182** (`naive`), **0.2287** (`ewc-block`) and **0.1069** (`replay`) -- so a tenfold
ascent rate buys the map **3.37** to **3.47** times more travel and less than a quarter of a unit more payout, and
the two currencies do not scale together.

**And the reward's shape is the two-arms-up signature at every rate.** The diagonal sits above its own last row on
`naive` and `ewc-block` at all three points (**+0.5831** and **+0.6339** at **0.001**, **+0.7061** and **+0.7794** at
**0.003**, **+0.7925** and **+0.8185** at **0.01**) and below it on `replay` at the two slower rates (**-0.1209**,
**-0.0964**) -- though `replay`'s own contrast shrinks toward zero as the rate rises and does not resolve at **0.01**
(**+0.0012** at **+0.04**). That is the same two-arms-up shape `e488`, `e500`, `e501` and `e502` found, and the rate
does not change which arms carry it.

**And the pass is free at every rate.** Every arm's accuracy at every
point is within **0.0094** of the meter run's and none of the changes resolves: **+0.0021**, **+0.0094** and
**+0.0031** at **0.001**, **-0.0017**, **+0.0014** and **-0.0021** at **0.003**, **+0.0045**, **+0.0052** and
**+0.0045** at **0.01**, against the meter run's **0.8299**, **0.8139** and **0.8267**. All three points sit
**0.5653** to **0.5844** above the four-class chance. So the price `e488` measured at one trial per pass is not what
a harder map costs inside the episode: the head's own metric does not move at any of the three rates.

**And the flag is one field and one world.** Against `e500`'s own earned run each new run's config differs in
**nothing** past the inert rule over **62** fields: the fields the rule covers are `loop_earn_lr`, the output path,
the saved weights and `loop_reward_on_action` -- the last of them the flag the corpus gained after `e500`'s own
artifact was written, recorded **`False`** there where the older run has no such field at all, a pair the corpus's
own rule reads as one run -- with the recorded rate **0.001** and **0.01** as asked, and the environment's draw is
`e500`'s own
**28** fields field for field, with **none** added, **none** missing and **none** differing, so the three points are
one world, one pass, one read, one placement, one payout and one seed stream at three ascent rates. The default is
inert: `e500`'s, `e501`'s, `e502`'s and `e503`'s readings, re-read through the changed runner, come back byte for
byte as their artifacts carry them.

## 3. What it cannot do

- **Three rates are not a curve's shape**: **0.001**, **0.003** and **0.01** are three points, so a peak, a knee or
  a turnover inside or outside them is not in the unit -- the payout's rise is small and monotone over exactly this
  span, and nothing here says what **0.03** or **0.0001** does.
- **And one episode length and one placement**: two trials of six steps with the label first, `e495`'s own pass; the
  three- and four-trial splits and the passes with the label at an interior trial are not in it.
- **And two currencies, one of them measured elsewhere**: the payout here is the world's own linear read of the cue,
  scored on the **carried** state; `e502` reads the same pass on the agent's **one-step action response** and its
  rate is not swept there, so what the action's currency does under a harder map is a different unit.
- **And the map's ascent rate is not the body's**: `--loop-earn-lr` moves the map's own optimizer and nothing else,
  so the body and the decoders still train at the run's `--lr` and nothing here says what the body's rate does with
  the earning.
- **And one world, one budget and one seed stream**: the card's own setting at `--seed0 0`, so a second world, a
  second budget or a second stream is not in the unit, and `e487` found this corpus's currency level moving by half
  between two worlds.
- **And three arms is a small population**: a claim over arms is not a claim about the world, and the two arms whose
  accuracy dips at the default rate here are the two that carry the payout gain at the high one.

## RE-READ 2026-10-13

**The interior placements this unit left are measured.** This unit's *cannot do* closed on *one episode length and one placement ... the three- and four-trial splits and the passes with the label at an interior trial are not in it*. `e505` reads the placement with the pass's length held at three trials and no payout: the pass falls **0.8538**, **0.8392** and **0.8580** to **0.3257**, **0.3069** and **0.3274** to **0.2566**, **0.2576** and **0.2542**, the end-to-end move **+0.5972**, **+0.5816** and **+0.6038** at **+74.23**, **+66.33** and **+88.97** sigma, and the label's own part of the read **1.0571**, **0.0489** and **0.0314**. So the rate this unit swept is swept at the placement axis's working end, and the earning at an interior placement is a different unit. This unit's numbers stand.
