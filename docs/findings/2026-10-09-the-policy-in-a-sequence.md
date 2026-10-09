# The agent's policy in a sequence: the policy forgets the first task, and ends below where it started

*2026-10-09. `experiments/e478_the_policy_in_a_sequence.py` asks the benchmark's own retention question of the thing
that **acts**: three tasks in sequence, `e477`'s 64-number policy trained on each in turn, and the retention matrix
read in **reward**. **All four claims MET**.*

## 1. The retention matrix

The mean over the eight replicates, in reward (higher is better). Row 0 is the identity policy, which is the
environment's own rule; row `k + 1` is the policy after task `k`, read on the tasks it has seen.

| | task 0 | task 1 | task 2 |
|---|---|---|---|
| the identity policy | -9.7313 | -8.9013 | -9.0916 |
| after task 0 | **-8.2059** | -- | -- |
| after task 1 | -9.9891 | **-7.3110** | -- |
| after task 2 | **-10.4024** | -8.8557 | **-7.8089** |

| claim | measured | verdict |
|---|---|---|
| SA1 every replicate starts from the environment's own rule, bit for bit | **8 of 8** bit-identical, the worst absolute difference **0.0e+00** | **MET** |
| SA2 every task in the sequence is learned | **+1.5254** at **9.77**, **+1.5903** at **8.18** and **+1.2827** at **5.32** sigma | **MET** |
| SA3 the policy forgets the first task | a paired drop of **+2.1965** at **10.65** sigma | **MET** |
| SA4 the retention matrix says what the benchmark's does | the mean diagonal exceeds the mean last row by **+1.2471** at **14.54** sigma | **MET** |

## 2. What the sequence says

**The agent forgets, and the benchmark's own instrument reads it.** The corpus's whole retention apparatus -- the
sequence, the diagonal, the last row, the paired sigmas -- is built for a **decoder**; this is that shape with the
same diagonal-and-last-row statement, measured on the policy that decides what the agent does. Every task is learned
on the way in -- **+1.5254**, **+1.5903** and **+1.2827** over the identity policy, at **9.77**, **8.18** and
**5.32** sigma -- and the first one is then lost: after the whole sequence its reward is **+2.1965** below what it
was right after the first task, at **10.65** sigma, and the diagonal sits **+1.2471** above the last row at
**14.54** sigma.

**And the loss is not to the identity policy's level but past it.** The first task's mean reward is **-8.2059** right
after it is trained, **-10.4024** after the sequence, and **-9.7313** for a policy that was never trained at all --
so the sequence leaves the policy **0.6711 worse on the first task than never training it**, which is negative
backward transfer and not merely forgetting. **This unit registered no claim about that comparison**, and it is
reported here as the three means the matrix carries rather than as a decided result; what it shows is that the
policy's first task is not a floor the sequence returns to.

**And the same configuration reproduces `e477` to the bit.** The identity row is `e477`'s **initial** reward on the
same worlds and the after-task-0 row is `e477`'s **trained** reward, **bit-identical** at all eight replicates
(**-7.946362**, **-11.442831**, **-8.821856**, **-5.343964**, **-7.147279**, **-3.547538**, **-7.794079**,
**-13.603028**) -- so this unit's instrument is `e477`'s, its first row is the untouched loop and its second is the
trained policy the earlier unit read, and the sequence's later rows are the same policy moved on. **No claim is
registered on this either**; it is the check that the two units are one measurement and not two.

**And every replicate's first step is the corpus's rule, exactly.** With `policy = I` the world is bit-identical to
the one the environment computes with no policy at all on all eight replicates, a worst difference of exactly
**0.0e+00**, so the sequence starts from the loop every other unit of this line runs rather than from a second rule.

## 3. What it cannot do

- **Three tasks and one target rule**: the reward is a squared distance to a drawn point, so a sparse, saturating or
  action-side reward is not in it, and the sequence is three targets rather than the odour, heading and antennal-lobe
  tasks the card's sequence is built from.
- **And the tasks share one cue set**: they differ in the target and not in what the agent is shown, which is the
  conflicting-objective case and not the benchmark's disjoint cue sets.
- **And the policy is linear over one population with the body frozen**: 64 numbers, so the repertoire is small and
  what is forgotten here is a linear map's.
- **And no method is compared**: this is the `naive` arm of a policy sequence, and whether a buffer or a penalty
  helps a **policy** the way it helps a decoder is a different unit.
- **And eight replicates are not the population**: the sigma is the paired one over the worlds the replicates share,
  the body and the circuit are held, and the world is the replicate.
