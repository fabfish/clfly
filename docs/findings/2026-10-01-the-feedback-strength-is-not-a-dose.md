# The feedback strength is not a dose

*2026-10-01. Runs: `experiments/e8_rate_network.py --circuit-size 300 --iters 500 --readout-size 32 --repeats 5
--methods naive --closed-loop --loop-scale {0.0, 0.25, 0.5, 1.0}` -- four commands, 585 s each in total, read by
`experiments/e327_the_feedback_is_a_dose.py` against `e326`'s unwired run.*

## 1. The knob `e326` left un-turned

`e326` trained through the loop at one strength and found the direction its registration did not predict: `naive`
reached **1.0000** accuracy and **exactly 0.0000** forgetting, and `ewc-block` improved too. Its finding gave both
the mechanism and the caveat in one sentence -- a channel whose input at step ``t`` is a monotone function of the
state at step ``t - 1`` is a **latch**, and a latch is a memory, so *hold a value across a gap* is a task a
self-exciting channel can hold -- and named the strength as **a knob and not a sweep**, with a latch's effect
expected to grow with it.

This unit turns it: **0.0, 0.25, 0.5, 1.0**, `naive`, five replicates each, same circuit, read-out, task names, cue
sets and seeds. The first level is the control that makes the sweep readable, and a feedback of zero is the world
disconnected.

**T1 MET.** Same circuit `mb+cx+al@n952`, same read-out `59926518137c`, the same three task names, five replicates
at every level, and **no unexpected difference** in the configs or in the environment draws once the strength itself
is excluded.

**T4 MET, and it is the sharp result.** The scale-0.0 run's five replicates reproduce `e326`'s **unwired** run
**exactly**, replicate for replicate, on accuracy and on forgetting. A feedback of zero is not a small loop; it is
the same computation, to the last digit -- which is the check that says the sweep's zero point and the closed loop's
off switch are one object.

## 2. And the sweep is not a dose

| feedback strength | final accuracy | mean forgetting | replicates that forget |
|---|---|---|---|
| 0.00 (the unwired run) | 0.9708 | 0.0437 | **1 of 5** |
| 0.25 | 1.0000 | 0.0000 | 0 of 5 |
| 0.50 | 0.9333 | **0.1000** | **2 of 5** |
| 1.00 | 1.0000 | 0.0000 | 0 of 5 |

**T2's falsifier FIRED.** The registered ordering was that forgetting never rises along the sweep; it rises by
**0.1000** between 0.25 and 0.5. **T3 MET** -- the ends differ by 0.0437, above the 0.02 bar -- but the table is
what the unit is about.

**Every replicate at every strength learns every task perfectly.** `learned` is `[1.0, 1.0, 1.0]` on all twenty
arms across the four levels, so the level is not in play at all here: the sweep's whole signal is **whether a
replicate forgets anything**, and that count runs **1, 0, 2, 0 of five**. The means above are those counts divided
by five. So the registered shape is not refuted by a graded effect but by **one replicate** -- and with five
replicates a rate of 1-in-5 cannot be separated from 2-in-5: at those proportions a 2 sigma separation needs about
**40** replicates per level and 3 sigma about **90**.

**What the four points do say**, at the resolution they have: two of the four settings (0.25, 1.0) retain
perfectly on every replicate, the unwired run misses once, and 0.50 misses twice. A loop that is either absent or
strong is at least as good as one that is middling -- which is the *opposite* of a dose and the opposite of what
the strength knob was expected to do. Whether 0.50 is a real worst case is not settled by this grid; the run that
would settle it is the same sweep at forty replicates per level, and the honest expectation from these rates is
that it is a coin's difference.

## 3. What it cannot do

**Five replicates, and forgetting here is a count.** As above, the sweep resolves nothing about the ordering of
0.25, 0.5 and 1.0, and T3's 0.0437 rests on the same single replicate that the unwired run missed. **The task is at
ceiling**: every arm learns all three tasks perfectly, so the sweep measures retention only, and an accuracy
dose-response would have no room at all. **One arm**: `replay` and the block arms are not swept. **One circuit, one
read-out width and one gain**: only the strength moves, and a latch at another gain or another action-population
size is not measured. **And there is still no reward**: the label is the cue, delivered at step 0, and the agent's
action is an input rather than a decision. **Nothing here explains why 0.50 would be worst**: the candidate is a
strength large enough to perturb the trajectory and too small to latch the cue, and this grid cannot separate that
from a coin.
