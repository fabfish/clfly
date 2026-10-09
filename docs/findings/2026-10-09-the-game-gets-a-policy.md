# The game gets a policy: the loop's own gradient plays it, and the reward is not the benchmark's metric

*2026-10-09. `experiments/e477_the_game_gets_a_policy.py` gives the environment the thing `e325` and `e361` both closed
on -- **a reward and a policy** -- and trains it. `CueActionEnv` gains a `policy` field that replaces the world's drive
`tanh(gain * x[:, action_neurons])` with `tanh(gain * (x[:, action_neurons] @ policy))`, `None` being every artifact
this repository holds; the reward is a **cue-dependent target** the world's final state is driven to; and the policy is
initialized at the **identity**, which is the corpus's own rule exactly, and trained by gradient ascent **through the
loop**. **QA1, QA2 and QA3 MET** and **QA4 is a NULL**.*

## 1. The eight worlds

| the replicate | the reward, identity | trained | the gain | the decoder, identity | trained | \|move\| | the gradient's norm | the finite difference's worst gap |
|---|---|---|---|---|---|---|---|---|
| 0 | -9.7671 | -7.9464 | **+1.8207** | 0.6250 | 0.6328 | 13.35 | 0.9760 | 9.18e-04 |
| 1 | -13.2293 | -11.4428 | **+1.7865** | 0.6328 | 0.6172 | 22.14 | 0.5859 | 1.11e-03 |
| 2 | -10.0432 | -8.8219 | **+1.2213** | 0.5781 | 0.6172 | 23.21 | 0.5073 | 9.88e-04 |
| 3 | -7.4596 | -5.3440 | **+2.1157** | 0.6328 | 0.6953 | 16.91 | 1.0397 | 6.04e-04 |
| 4 | -8.9619 | -7.1473 | **+1.8146** | 0.6641 | 0.6719 | 13.21 | 0.8029 | 6.74e-04 |
| 5 | -4.2926 | -3.5475 | **+0.7451** | 0.6328 | 0.6719 | 19.06 | 0.3742 | 3.87e-04 |
| 6 | -9.0620 | -7.7941 | **+1.2679** | 0.5781 | 0.6094 | 18.57 | 0.6502 | 9.68e-04 |
| 7 | -15.0347 | -13.6030 | **+1.4317** | 0.6094 | 0.5469 | 18.90 | 0.9207 | 1.12e-03 |

| claim | measured | verdict |
|---|---|---|
| QA1 the policy's identity is the environment's own rule, bit for bit | **8 of 8** replicates bit-identical, the worst absolute difference **0.0e+00** | **MET** |
| QA2 and the reward's gradient is the loop's | the smallest gradient norm **0.3742**, the worst finite-difference gap **1.12e-03** over **64** coordinates in each of 8 replicates | **MET** |
| QA3 and the game can be played | a paired gain of **+1.5254** at **+9.77** sigma | **MET** |
| QA4 and acting pays the read-out | **+0.0137** at **+0.99** sigma | **NULL** |

## 2. What the policy says

**The loop plays the game and its own gradient is what plays it.** A policy of **64** numbers -- a linear map from the
action population to the world's eight-dimensional drive, the body frozen -- trained for three hundred ascent steps on
one set of cues raises the reward on cues it was **not** trained on by **+1.5254** at **9.77** sigma, and **every one
of the eight worlds gains** (**+0.7451** to **+2.1157**). **So the sentence two units of this line closed on is now
half measured**: the environment has a reward, the agent has a policy, and what carries the gradient between them is
the loop the corpus already runs.

**And the gradient is the loop's and not an artefact of the arithmetic.** Backprop through the environment agrees with
a **central finite difference** at `eps = 1e-3` at **every one of the 64 coordinates** in every replicate, the worst
disagreement being **1.12e-03** against a bar of **5e-03**, with the gradient's norm never below **0.3742**. So the
reward is a function of the policy **through the world**, which is what makes "train a policy on the loop" a measured
possibility rather than a claim about a differentiable path.

**And the policy's identity *is* the corpus's rule, to the bit.** With `policy = I` the world's final state is
**bit-identical** on all eight replicates to the one the environment computes with no policy at all -- a worst
difference of exactly **0.0** -- **so the trained game starts from the loop every other unit in this corpus runs** and
not from a second rule that happens to look like it. That is the check the new field is worth having: the policy is a
strict generalization of the environment's own action rule, and turning it on changes nothing.

**And the reward is not the benchmark's metric.** The decoder on the world's final state runs **0.5781** to **0.6641**
under the identity policy -- well above a chance of **0.25**, which is `e367`'s channel reading on this world -- and
**0.5469** to **0.6953** under the trained one, a paired difference of **+0.0137** at **0.99** sigma: **a null**. **So
optimizing the agent to drive its world to a drawn point is orthogonal to the benchmark's own question at this scale**:
the game's objective neither buys nor costs the cue's decodability, and a reader cannot argue from one to the other.
Whether that is the reward's choice or a property of the world is what the null leaves open.

## 3. What it cannot do

- **One target rule**: the reward is a squared distance to a cue-dependent point drawn from a fixed seed, so a sparse,
  saturating or action-side reward is not in it.
- **And the policy is linear over one population**: 64 numbers from the action population to the world's drive with the
  body frozen, so nothing here trains the recurrent weights, and the policy cannot see the cue population directly.
- **And the policy is not the benchmark's**: the runner does not carry one and does not optimize a reward, so the
  card's `absent` list still names **a policy** and this unit does not revise the card.
- **And eight replicates are not the population**: the sigma is the paired one over the worlds the two policies share,
  the body and the circuit are held, and the world is the replicate.
- **And a reward is not a task**: driving a state to a drawn point is not the olfaction, heading and antennal-lobe
  tasks the card's sequence is built from, and nothing here says the reward could be learned by the same head.
