# The benchmark carries a policy: the agent uses its freedom, the game is still learned, and one arm's diagonal moves

*2026-10-09. `experiments/e481_the_benchmark_carries_a_policy.py` reads the first runner artifact that carries a
**policy**: `--loop-policy` gives the loop's agent a trainable identity-initialized map from its action population to
the world's drive, trained by the task loss through the loop in the same optimizer as the body and the head, and the
new run is the card's own neutral roll (`e438`) with that flag alone. **QA1, QA2 and QA3 MET** and **QA4's falsifier
FIRED**.*

## 1. The two runs

| the arm | the diagonal, policy | card | contrast | sigma | the last row, policy | card | contrast | sigma |
|---|---|---|---|---|---|---|---|---|
| `naive` | 0.8187 | 0.8042 | +0.0146 | 0.63 | 0.5045 | 0.5191 | -0.0146 | -0.86 |
| `ewc-block` | 0.7573 | 0.6865 | **+0.0708** | **+2.40** | 0.5340 | 0.4889 | +0.0451 | 1.71 |
| `replay` | 0.7313 | 0.7438 | -0.0125 | -0.80 | 0.6608 | 0.6785 | -0.0177 | -1.26 |

| claim | measured | verdict |
|---|---|---|
| QA1 the flag is the only field moved | **51** keys compared, **0** differing past the inert rule and **1** admitted by it (`loop_holdout`, which the older roll lacks), the flag `[None, True]`, the circuit equal, **20** replicates each | **MET** |
| QA2 the agent's freedom is used | the policy's distance from the identity is recorded on **60 of 60** replicates, the smallest **6.7094**, the mean **7.7980** | **MET** |
| QA3 the benchmark still learns with a policy on | the `naive` diagonal is **0.8187**, **+0.5687** above a chance of **0.25** | **MET** |
| QA4 it does not move what the benchmark measures | `ewc-block`'s diagonal resolves at **+2.40** sigma | **FALSIFIER FIRED** |

## 2. What the run says

**The agent uses the freedom and the game is still learned.** The policy starts at the identity, which is the
environment's own action rule, and ends **6.7094 to far more** away from it on **every one of the sixty replicates**
(the mean distance is **7.7980**), while the `naive` arm's diagonal is **0.8187** -- **+0.5687** above chance. **So a
benchmark whose agent chooses its own action through something the benchmark trained is a benchmark that still learns
its tasks**, which is the precondition the whole step needed.

**And the flag is the only thing that moved.** **51** keys compared and **none** differing past the inert rule, with
one admitted by it (`loop_holdout`, a key `e438` predates and the new run holds at its default), the flag
`[None, True]`, the circuit equal and twenty replicates on both sides. **So the comparison is the flag and nothing
else**, and the older roll's generation gap is printed rather than waived.

**And five of the six contrasts are nulls, with one firing just past the bar.** `naive`'s diagonal is **+0.0146** at
**0.63** sigma and `replay`'s **-0.0125** at **-0.80**, and the last rows are **-0.86**, **1.71** and **-1.26** --
**while `ewc-block`'s diagonal is `+0.0708` at `+2.40` sigma**, the one contrast of the six past the bar. **So the
honest reading is that the benchmark's numbers are nearly independent of the policy, and the arm that moves is the
penalised one** -- and that this is **one of six tests at 2.40 sigma**, where the chance of at least one such
firing under the null is about **9%**. **It is a hint and not a result**, and this unit registered no claim about
which arm would move.

**And the arm that moves is the one with the most to gain.** `ewc-block` is the arm whose reading is anchored toward
a basis the connectome's own partition defines; a policy that routes the cue into the world **through a map the agent
owns** is a channel such an arm can hold, and it gains **+0.0708** where the arm that stores nothing gains **+0.0146**
and the arm that replays gains nothing. **That is a story about `e423`'s reading and not this unit's measurement**,
and it is named here because the firing is on that arm and on no other.

## 3. What it cannot do

- **One configuration**: the card's neutral roll at one world, one budget and one seed stream, so another world or
  another budget is not in it, and the comparison is against a roll made before the flag existed.
- **And the policy is linear over one population**: 64 numbers from the action population to the world's drive, not
  covered by any penalty in this project, and the recurrent weights are not part of it.
- **And a reward is still absent**: the policy is trained by the **task loss**, so the game has no reward of its own
  and the card's `absent` list still names one -- and it still names a policy, since the benchmark's own runs do not
  carry one by default; a card revision is a different unit.
- **And six contrasts at one bar are not six results**: exactly one resolves, at **2.40** sigma, and the family-wise
  chance of that under the null is about **9%**.
- **And twenty replicates are one body and one circuit**: every sigma is the paired one over the seeds the two runs
  share, and the two runs are one draw each.
