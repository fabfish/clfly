# The environment pays a reward: it is the agent's to earn, and its own noise is larger than the cue's share of it

*2026-10-09. `experiments/e483_the_environment_pays_a_reward.py` gives `CueActionEnv` the other half of `e325`'s
sentence: a **`reward_map`**, drawn from the environment's seed behind a new `reward` flag, against which the **cue
itself** sets a target, with the trial's reward the **negative squared distance** from the world's final state to it.
**RA1 and RA4 MET**, **RA2's falsifier FIRED** and **RA3 is a NULL**.*

## 1. The payout

| the replicate | across symbols | within a symbol | identity | trained | the gain | the target's spread |
|---|---|---|---|---|---|---|
| 0 | 1.5348 | 1.3415 | -3.1322 | -2.1758 | **+0.9564** | 0.1023 |
| 1 | 0.9088 | 1.5618 | -2.9831 | -2.1583 | **+0.8248** | 0.0851 |
| 2 | 1.1044 | 1.9082 | -4.3386 | -3.5214 | **+0.8171** | 0.0762 |
| 3 | 2.2136 | 1.7240 | -4.8319 | -2.9644 | **+1.8674** | 0.1408 |
| 4 | 2.8916 | 2.6910 | -6.6546 | -4.1161 | **+2.5385** | 0.2846 |
| 5 | 1.9142 | 2.2791 | -4.7994 | -3.6522 | **+1.1473** | 0.1063 |
| 6 | 1.2939 | 2.6483 | -6.2149 | -4.0140 | **+2.2009** | 0.1381 |
| 7 | 1.3580 | 1.6010 | -3.7390 | -2.4113 | **+1.3277** | 0.1975 |

| claim | measured | verdict |
|---|---|---|
| RA1 the payout is the only field the flag draws | **17** draw fields, **0** differing, the payout's map recorded on **8 of 8** | **MET** |
| RA2 and the cue sets the payout | a paired margin of **-0.3169** at **-1.47** sigma, **5 of 8** replicates not separating | **FALSIFIER FIRED** |
| RA3 and the payout is the agent's to earn | **+1.4600** at **+6.24** sigma | **NULL** |
| RA4 and the goal is the cue's, read one step after it arrives | the target's spread at least **0.0762** at the first step and exactly **0.0e+00** at the read step, where the payout is **0** on every replicate | **MET** |

## 2. What the payout says

**The environment pays a reward, and the agent earns some of it.** A 64-number linear policy at the identity, trained
by ascent on the payout through the loop, earns **+1.4600** more than the identity policy on cues it was **not**
trained on, at **+6.24** sigma, and **every one of the eight worlds gains** (**+0.8171** to **+2.5385**). **So the
reward is real and it is the agent's**: what it is paid depends on what its action population does to the world, and
the loop carries the gradient that improves it. **RA3's NULL is the bar's and not the effect's**: I registered
**2.00** and the gain is **1.46**, resolved at six sigma, so the payout is earned by less than the number I wrote down
in advance.

**And the cue's share of the payout is smaller than the payout's own noise.** The mean reward differs across the four
cue symbols by **0.9088** to **2.8916**, and within a symbol the rewards spread **1.3415** to **2.6910** -- so the
margin is **-0.3169** at **-1.47** sigma and **five of the eight** replicates do not separate them at all. **So the
payout depends on the cue and its dependence is not dominant over its own scatter**, which is what the cue's noise
(`noise = 1.0`, the corpus's own setting) and the noise the world's dynamics add together do to a target read off the
state. **A reward whose cue-share is under its own noise is a reward an agent can only average over**, and that is a
property of the payout as the environment builds it rather than of the agent.

**And the goal is the cue's, read where the cue is, and nowhere else.** At the first cue step the target's own spread
across symbols is at least **0.0762**, and at a cue delivered at the **read step** it is exactly **0.0e+00** -- the
zero vector, because the state it is read from is at rest -- with the payout there **0** on every replicate, since a
world the agent can never move pays the distance from zero to zero. **So the payout's channel is the cue's own
activity and not a label**: the environment never sees one, and this control is what says the target is read where the
cue is legible and nowhere else.

**And the flag draws the payout and nothing else.** **17** recorded draw fields -- the three populations, the cue
templates, the drive's map, the read map, the coupling, the world's dimensions and leak, the cue's step and the drive's
source -- agree between two environments at one seed with the flag and without it, and the payout's own map is
recorded on all eight replicates. **So the reward is an addition to the game and not a change to it**, which is the
same check `e477`'s policy field and `e481`'s flag each passed.

## 3. What it cannot do

- **The payout is not the benchmark's**: the runner does not carry the flag, so no artifact in the corpus records a
  reward and the card's `absent` list still names one. A runner change and a revision are different units, which is
  the order `e477`, `e481` and `e482` followed for the policy.
- **And the goal is a linear read of the cue**: a payout on the label, on the action, or sparse in time is not in it.
- **And the reward is bounded above by zero**: a squared distance, so its scale is the world's and not a designer's,
  and "earns +1.46" is a number about one world's units.
- **And the body is frozen on the frozen rolls**: the policy is 64 numbers over the action population.
- **And the cue's noise is one setting**: `noise = 1.0` is the corpus's own, and a noisier or quieter cue would move
  the margin RA2 fired on, which is a sweep this unit does not run.
- **And eight replicates are not the population**: the sigma is the paired one over the worlds the replicates share.
