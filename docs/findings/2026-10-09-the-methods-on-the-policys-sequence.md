# The methods on the policy's sequence: on the agent both methods cost the diagonal and buy the last row, and the penalty stops learning

*2026-10-09. `experiments/e479_the_methods_on_the_policys_sequence.py` asks the corpus's flagship method question --
does a **replay buffer** beat a **penalty** -- of the thing that acts: three tasks of four cue symbols each, `e477`'s
64-number policy, and three arms (`naive`, `replay`, `penalty`) whose retention matrices are read in **reward**.
**TA1 MET**, **TA2's falsifier FIRED**, **TA3 MET** and **TA4 is a NULL**.*

## 1. The three arms

The mean retention matrix in reward over the eight replicates; row 0 is the identity policy, which is the
environment's own rule, and row `k + 1` is the policy after task `k`.

| the arm | row | task 0 | task 1 | task 2 |
|---|---|---|---|---|
| the identity policy (all three) | 0 | -9.6771 | -8.9894 | -9.5160 |
| `naive` | 1 | **-7.5970** | -- | -- |
| | 2 | -9.5293 | **-7.1650** | -- |
| | 3 | **-10.2037** | -8.9470 | **-7.6850** |
| `replay` | 1 | **-7.5970** | -- | -- |
| | 2 | -8.0539 | **-7.9652** | -- |
| | 3 | **-8.4436** | -8.1580 | **-8.6239** |
| `penalty` | 1 | **-7.5970** | -- | -- |
| | 2 | -7.6420 | **-8.7888** | -- |
| | 3 | **-7.8142** | -8.7983 | **-9.4927** |

| | `naive` | `replay` | `penalty` |
|---|---|---|---|
| the mean **diagonal** | **-7.4823** | -8.0620 | -8.6261 |
| the mean **last row** | -8.9452 | **-8.4085** | -8.7017 |

| the paired contrast | diagonal | sigma | last row | sigma |
|---|---|---|---|---|
| `replay` minus `penalty` | **+0.5641** | **+10.45** | +0.2932 | +8.65 |
| `replay` minus `naive` | **-0.5797** | **-9.00** | **+0.5367** | **+9.47** |
| `penalty` minus `naive` | **-1.1438** | **-14.94** | +0.2435 | +3.14 |

| claim | measured | verdict |
|---|---|---|
| TA1 the three arms are one configuration | **24** cells, seeds **0** to **7**, the identity policy bit-identical on **24 of 24** with a worst difference of **0.0e+00**, and task 0 **bit-identical** across the three arms | **MET** |
| TA2 and every arm learns every task | the penalty's gains at tasks 1 and 2 are **+0.2007** at **1.00** sigma and **+0.0233** at **0.10** | **FALSIFIER FIRED** |
| TA3 and the buffer beats the penalty on the diagonal | **+0.5641** at **+10.45** sigma | **MET** |
| TA4 and it does not pay for it in retention | **+0.2932** at **+8.65** sigma | **NULL** |

## 2. What the three arms say

**The penalty stops the policy learning, and the unit registered that risk before its arms ran.** `lam = 1.0` with a
unit-mean diagonal Fisher is the card's own strength, and at it the penalty arm's gain over the identity policy is
**+2.0802** on the first task, **+0.2007** on the second and **+0.0233** on the third -- unresolved on both. **So the
arm that TA2 compares against is not an arm that retained something; it is an arm that stopped moving.** TA2's own
claim text says what that means: *"a penalty so strong it stops the policy learning would otherwise win the
comparisons below."* **And it does**: TA3's **MET** is `replay` minus `penalty` on the diagonal, so the **+0.5641** at
**10.45** sigma it reports is carried by the penalty's failure and is **not evidence about retaining a policy**. The
verdict stands as registered and the reading is that.

**And against the baseline the arms that *work*, neither method wins the diagonal.** `naive` leads it --
**-7.4823** against `replay`'s **-8.0620** and `penalty`'s **-8.6261** -- so `replay` is **-0.5797** at **-9.00** sigma
and `penalty` **-1.1438** at **-14.94** sigma **below the arm that does nothing but train**. That is the reverse of
the decoder's ordering, where `e476` found `replay` **+0.1085** at **13.96** sigma above `naive`: **on the agent, a
method costs the level it reaches.**

**And what both methods buy is the last row.** There `replay` leads `penalty` and `penalty` leads `naive`:
**-8.4085**, **-8.7017** and **-8.9452**, so `replay` is **+0.5367** at **+9.47** sigma above `naive` and `penalty`
**+0.2435** at **+3.14** sigma above it. **So the trade the corpus measured on the decoder -- a penalty buying
retention at a price -- is here too, and on the agent the price is the level**: both arms end up worse on the tasks
they are still training and better on the ones they are not.

**And the three arms are one configuration to the bit, including the first task.** All **24** cells put the identity
policy's world bit-identical to the environment's own rule (worst difference **0.0e+00**), and the after-task-0 row is
**bit-identical across the three arms** at every replicate (**-6.721004**, **-9.461185**, **-7.967314**, **-5.430179**,
**-6.951163**, **-3.895038**, **-7.811899**, **-12.537831**). That is the check the comparison needs: on task 0 there
is no buffer and no Fisher, so the arms must agree, and they do, so the divergence below is what the arm's training
adds and nothing else.

## 3. What it cannot do

- **One strength and one penalty**: a diagonal Fisher at `lam = 1.0`, the card's own number, and a ladder over it is
  not run -- so *the penalty stops the policy learning* is a statement about that strength, and a weaker one is the
  first thing a later unit should sweep.
- **And one buffer setting**: 64 pairs per task and 64 per step, not a sweep.
- **And the tasks share a circuit and a cue population**: they differ in four cue symbols and one target block, so
  the sequence is easier than the benchmark's and the forgetting here is a 64-parameter linear map's.
- **And no body is trained**: the body is frozen, so nothing here says how a policy and the recurrent weights would
  share a sequence.
- **And the comparison with the decoder is across configurations**: `e476`'s **+0.1085** is a different subject, a
  different task structure and a different budget, so the reversal named above is a contrast between two units and
  not a paired measurement.
- **And eight replicates are not the population**: the sigma is the paired one over the worlds the replicates share.
