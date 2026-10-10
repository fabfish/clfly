# The cue's noise on the payout's cue-share: `e483`'s falsifier fired because of the cue and not because of the payout

*2026-10-09. `experiments/e484_the_cues_noise_on_the_payouts_share.py` walks the sweep `e483` named as what it could
not run: the same payout, the same world and the same eight replicates with the cue's noise at **five levels**,
three of them quieter than the setting that unit's falsifier fired at. **All four claims MET**.*

## 1. The ladder

| the cue's noise | the across-minus-within margin | sigma | the replicates that separate them | the payout, identity | trained | the gain | sigma |
|---|---|---|---|---|---|---|---|
| **0** | **+2.9086** | **+6.33** | **8 of 8** | -3.5370 | -1.3592 | **+2.1779** | **5.06** |
| 0.25 | +1.9474 | +6.75 | 8 of 8 | -3.6400 | -1.8010 | +1.8390 | 5.28 |
| 0.5 | +1.0812 | +4.33 | 8 of 8 | -3.8837 | -2.2773 | +1.6064 | 5.31 |
| **1.0** (the corpus's own) | -0.3169 | -1.47 | **3 of 8** | -4.5867 | -3.1267 | +1.4600 | 6.24 |
| 2.0 | -1.8376 | -9.88 | **0 of 8** | -5.7600 | -4.1947 | +1.5653 | 8.57 |

| claim | measured | verdict |
|---|---|---|
| SA1 the level is the only field the sweep moves | **17** draw fields at **8** replicates over five levels, **0** differing within or across, and the payout's map **one draw across every level** | **MET** |
| SA2 and a quieter cue carries more of the payout | **+3.2255** at **+7.60** sigma | **MET** |
| SA3 and at a quiet cue the cue sets the payout | **8 of 8** replicates at `noise = 0`, against **3 of 8** at the corpus's own | **MET** |
| SA4 and the payout is still earned where the cue is exact | **+2.1779** at **+5.06** sigma | **MET** |

## 2. What the sweep says

**`e483`'s falsifier fired because of the cue and not because of the payout, and the sweep says so at seven sigma.**
The across-minus-within margin runs **+2.9086**, **+1.9474**, **+1.0812**, **-0.3169** and **-1.8376** -- strictly
falling as the cue gets noisier -- and the quiet cue's is **+3.2255** above the corpus's own at **+7.60** sigma.
**So the sentence `e483` published is true of the cue's amplitude and not of the payout**: *the cue's share of the
payout is under the payout's own noise* holds at `noise = 1.0` and fails at every quieter level the unit now carries.

**And at an exact cue the within-symbol spread is exactly zero.** At `noise = 0` the four symbols' mean rewards
differ by **1.2236** to **5.5410** while the rewards **inside** a symbol do not vary at all -- the spread is
**0.0** on all eight replicates -- so the payout is exactly the symbol's and the cue carries **all** of it.
**That is the mechanism in one number**: the goal is a linear read of the cue's activity one step after the cue
arrives, so with the cue exact the goal is exact and the only scatter left is the world's own, and with the cue noisy
the goal inherits the noise. **The three intermediate levels are a ladder and not a curve**: 8 of 8, 8 of 8, 8 of 8,
then 3 of 8, then 0 of 8, so the separation does not fade gradually but holds until the corpus's own setting and
breaks there.

**And the payout is earned at every level.** The policy's gain over the identity runs **+2.1779**, **+1.8390**,
**+1.6064**, **+1.4600** and **+1.5653**, all resolved between **5.06** and **8.57** sigma, so **what the cue's noise
moves is the share of the payout that belongs to the symbol and not what the agent can earn of it**. The identity's
own payout gets *worse* as the cue gets noisier (**-3.5370** to **-5.7600**), which is the goal becoming harder to
hit, while the trained policy's rises to meet part of it every time.

**And the sweep moves the level and nothing else.** **17** recorded draw fields, at eight replicates and five levels,
differ within no level and across none, and the payout's own map is **one draw across every level** -- because the
cue's noise is an **amplitude on one realisation** and not a redraw, which is what makes the five columns one
configuration with one number moved.

## 3. What it cannot do

- **One payout and one map**: the goal is a linear read of the cue through one drawn map, so a nonlinear or sparser
  goal is not in it.
- **And one axis**: the noise is the cue's; the world's own dynamics add scatter that this sweep does not move, and
  the fall from 8 of 8 to 3 of 8 to 0 of 8 holds the world fixed.
- **And five levels are a ladder and not a curve**: the crossing sits between `0.5` and `1.0` and is located to an
  interval, not to a value.
- **And the body is frozen**: the policy is 64 numbers over the action population.
- **And the payout is not the benchmark's**: the runner carries no reward, so the card still names one.
- **And eight replicates are not the population**: every sigma is the paired one over the worlds the replicates share.
