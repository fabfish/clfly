# The world gets a nonlinearity: a bounded state with fixed points, and the benchmark cannot see it

*2026-10-02. One runner invocation -- `e359`'s exact flags plus `--loop-world-nonlinear`, `--methods naive,replay`,
`--repeats 20` -- into `runs/e360_earned_label_nonlinear_20reps.json`, paired against `e359`'s linear coupled arms at
the same seeds. Nineteen minutes. Read by `experiments/e360_the_world_gets_a_nonlinearity.py`.*

## 1. The other half of the sentence `e359` answered

`e359` gave the world its own dynamics and found the earned label surviving it with every property intact. Its own
"what it cannot do" closed on what was left: *"the rule stays linear, so the world cannot yet be pushed into a state
and trapped there, which is the next thing `e333`'s sentence asks for."*

**This gives the world a saturation.** `CueActionEnv` gained `world_nonlinear`: with a coupling drawn and the flag
on, the world's own carry is `w_t = (1 - leak) * tanh(w_{t-1} @ K.T) + leak * drive_t`, so the state is **bounded**
and has its own fixed points -- a system the agent's actions can in principle push into a corner. The flag draws
nothing, so **the two runs' couplings are the same matrix to the fingerprint** (`5326f4a0edb4`), and the change is one
manipulation apart from `e359`.

## 2. The answer

| world | arm | final accuracy | diagonal | `mean_forgetting` | paired channel | sigma |
|---|---|---|---|---|---|---|
| linear coupled | `naive` | 0.5191 | **0.7691** | 0.3750 | +0.2642 | 18.08 |
| linear coupled | `replay` | 0.6785 | 0.7389 | 0.0906 | +0.4247 | 31.65 |
| **nonlinear** | `naive` | 0.5066 | **0.7715** | **0.3974** | +0.2524 | 20.28 |
| **nonlinear** | `replay` | 0.6687 | 0.7354 | **0.1000** | +0.4201 | 28.90 |

chance 0.2500. **T1 MET**: one configuration except the saturation -- the coupling fingerprint **5326f4a0edb4** on
both sides, the world read `3a7ba76b3619`, the populations unchanged, and no other field differing.

**T2 MET**: the nonlinear world is learnable -- the `naive` diagonal is **+0.5215 above chance**. **T3 MET**: and
the answer is still **earned**, at **+0.2524 (20.28 sigma)** and **+0.4201 (28.90 sigma)**. **T5 MET**: the buffer is
worth **0.2974 at 10.97 sigma**.

**T4 FALSIFIER FIRED, and it is the finding: the saturation is free.** The `naive` diagonal differs from the linear
coupled world's by **+0.0024 on a sem of 0.0173 -- 0.14 sigma**, inside the 0.02 that fired. The forgetting moves
from 0.3750 to 0.3974 and `replay`'s from 0.0906 to 0.1000; the final accuracies fall by 0.013 and 0.010. **So the
world got richer -- bounded, with its own fixed points -- and the benchmark did not notice.**

## 3. What it means

**The earned label is insensitive to the world's rule and sensitive to the world's width.** `e350` and `e351` found
the width buying 0.4125 of diagonal; `e359` found the coupling costing about 0.05; this finds the saturation costing
**0.0024**. Three manipulations of the same object, and the benchmark sorts them by an order of magnitude: what the
state has room for matters, what mixes it barely does, and whether it saturates does not show up at all.

**That is the same lesson the state read-out's channel gave, in the other direction.** There, `e343` and `e345` found
the loop rewriting 117% of the state and no decoder reading it; here the world's own dynamics rewrites the trajectory
and no head reads it. **A benchmark's method numbers are about what the read-out can see, and this line has now
measured that from both sides of the loop.**

## 4. What it cannot do

*One saturation and one strength*: `tanh` on the carry with no gain to tune, so "nonlinear" is one point on an axis
and not a family. *One coupling and one draw*: the same matrix `e359` drew, whose **shape** is still unexamined. *The
linear reference is a different artifact*, paired by the recorded fingerprints and the per-replicate seed stream.
*And trapped is a claim about what a policy could do*: nothing here trains a policy to exploit the fixed points, so
the saturation's consequence for the game is a possibility this unit **creates** and does not test.
