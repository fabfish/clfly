# The penalty's strength on the policy: a dose that turns on between 3e-3 and 0.03, and the card's own 1.0 is past the optimum

*2026-10-09. `experiments/e480_the_penaltys_strength_on_the_policy.py` walks the ladder `e479` named: `e479`'s own
penalty arm on the agent's 64-number policy at **six strengths** -- `0`, `3e-4`, `3e-3`, `0.03`, `0.3` and `1.0` --
eight replicates each. **LA1, LA2 and LA3 MET** and **LA4 is a NULL**.*

## 1. The ladder

| the strength | the mean diagonal | the mean last row | the cost against `0` | sigma |
|---|---|---|---|---|
| **0** | **-7.4823** | -8.9452 | -- | -- |
| 3e-4 | -7.4732 | -8.9830 | -0.0092 | -1.73 |
| 3e-3 | -7.4781 | -8.8579 | -0.0042 | -0.45 |
| 0.03 | -7.6704 | -8.6925 | **+0.1880** | **+5.55** |
| 0.3 | -8.2886 | **-8.5798** | **+0.8063** | **+14.11** |
| **1.0** | -8.6261 | -8.7017 | **+1.1438** | **+14.94** |

Two contrasts this unit measured and registered no claim about:

| the pair | on the diagonal | sigma | on the last row | sigma |
|---|---|---|---|---|
| `0.3` against `1.0` | **+0.3375** | **+7.83** | **+0.1220** | **+17.48** |
| `0.3` against `0` | -- | -- | **+0.3655** | +4.90 |

| claim | measured | verdict |
|---|---|---|
| LA1 the six points are one configuration with the strength moved | **48** cells, the identity policy bit-identical on **48 of 48** (worst **0.0e+00**), and the **`lam = 0` point against `e479`'s `naive` arm at a worst difference of `0.0e+00`** | **MET** |
| LA2 and the cost is a dose | the largest strength below the smallest non-zero by **+1.1530** at **+14.90** sigma | **MET** |
| LA3 and there is a strength at which the penalty is free | free at **3e-4**, **3e-3** and **0.03**, within **0.20** of the zero-strength point | **MET** |
| LA4 and the retention is bought | **+0.2435** at **+3.14** sigma at the largest strength | **NULL** |

## 2. What the ladder says

**The penalty's cost is a dose and not a cliff, and it turns on between `3e-3` and `0.03`.** At `3e-4` and `3e-3` the
arm's mean diagonal is **-7.4732** and **-7.4781** against the unpenalised **-7.4823** -- costs of **-0.0092** at
**-1.73** sigma and **-0.0042** at **-0.45** -- so at the corpus's own convention the penalty on the policy is
**free**, and at `0.03` it is **+0.1880** at **+5.55** sigma. **So `e479`'s *the penalty stops the policy learning* is
not a property of the penalty**: it is a property of the strength the card happens to carry, and three orders of
magnitude below it the same penalty costs nothing measurable.

**And the card's own strength is past the optimum on both axes at once.** `0.3` costs **0.3375** less than `1.0` on
the diagonal (**+7.83** sigma) and retains **0.1220** more on the last row (**+17.48** sigma): **`0.3` dominates
`1.0`**, buying more retention for less level, and the retention axis even reverses -- the last row is **-8.5798** at
`0.3` and **-8.7017** at `1.0`. **So on this subject `lam = 1.0` is past the point where a stronger penalty buys
anything**: above `0.3` the arm pays more and keeps less. *This unit registered no claim about the two and reports
them as the ladder's own numbers.*

**And the retention the penalty does buy is modest at every strength.** The last row runs **-8.9830**, **-8.8579**,
**-8.6925**, **-8.5798** and **-8.7017** against the unpenalised **-8.9452** -- a best gain of **+0.3655** at `0.3`
(**+4.90** sigma) and a loss at the smallest strength -- so **LA4's NULL is the ladder's own summary**: the strongest
strength does **+0.2435** at **3.14** sigma, between the floor and the bar. **The penalty's value on the agent is
therefore bought at a middle strength and is not large**, and the arm the card carries is on the wrong side of that
middle.

**And the six points are one configuration, including the one that has to be none.** All **48** cells put the identity
policy's world bit-identical to the environment's own rule (worst **0.0e+00**), the identity row is the same across
the six, and the **`lam = 0` point reproduces `e479`'s `naive` arm bit for bit** -- a worst absolute difference of
exactly **0.0e+00** over the whole retention matrix at every replicate. That is the check a ladder over a strength
needs: **a zero penalty is no penalty**, and the code says so to the bit, so the six columns differ in the penalty's
strength and in nothing else.

## 3. What it cannot do

- **One penalty and one family**: a diagonal Fisher with eight batches, so a block penalty, a KL anchor or a
  different Fisher estimator is not in it.
- **And no buffer is on the ladder**: this is the penalty alone, so nothing here says where `e479`'s `replay` arm
  would sit between the six points.
- **And the tasks share a circuit and a cue population**: they differ in four cue symbols and one target block, so
  the sequence is easier than the benchmark's and the anchor covers 64 numbers.
- **And six strengths are a ladder and not a curve**: the turn-on is located to the interval between `3e-3` and
  `0.03` and to no value inside it, and the optimum between `0.3` and `1.0` is not walked at all.
- **And the body is frozen**: the only thing the penalty anchors is the policy, so nothing here says how a penalty on
  a policy and one on the recurrent weights would interact.
- **And eight replicates are not the population**: every sigma is the paired one over the worlds the replicates share.
