# The world's memory: taking it away changes nothing the benchmark sees, and the task starts becoming the state read-out

*2026-10-02. One runner invocation -- `e359`'s exact flags with `--loop-world-leak 1.0`, `--methods naive,replay`,
`--repeats 20` -- into `runs/e361_earned_label_nomemory_20reps.json`, paired against `e359`'s memoried world
(`leak = 0.35`) at the same seeds and the same coupling draw. Nineteen minutes. Read by
`experiments/e361_the_world_memory.py`.*

## 1. The half of the rule the game needs

`e359` gave the world a coupling and `e360` gave it a saturation; both act on how the world **mixes what it
carries**. Neither touches how much it carries at all, and that is the half a game world is *for*: **a world is worth
having because it holds what the agent put there.**

**This unit takes the memory away.** At `leak = 1.0` the carried part of
`w_t = (1 - leak) * (w_{t-1} @ K.T) + leak * drive_t` is multiplied by zero, so the world's state **is** the drive:
a fixed linear function of the agent's action at that instant and of nothing earlier. The loop is still load-bearing
-- unwired, the world does not run and the read-out is a constant -- but the world remembers nothing, and a body that
wants the answer at the last step has to be saying it there.

## 2. The answer

| world | arm | final accuracy | diagonal | `mean_forgetting` | paired channel | sigma |
|---|---|---|---|---|---|---|
| memoried (`leak = 0.35`) | `naive` | 0.5191 | **0.7691** | 0.3750 | +0.2642 | 18.08 |
| memoried | `replay` | 0.6785 | 0.7389 | 0.0906 | +0.4247 | 31.65 |
| **instant (`leak = 1.0`)** | `naive` | 0.5201 | **0.7927** | **0.4089** | +0.2622 | 16.98 |
| **instant** | `replay` | **0.7000** | 0.7757 | **0.1135** | +0.4382 | 31.98 |

chance 0.2500. **T1 MET**: one configuration except the leak -- coupling `5326f4a0edb4` on both sides, the world
read `3a7ba76b3619`, the populations unchanged, leaks `[0.35, 1.0]`, and no other field differing.

**T2 MET**: the instant world is learnable -- the `naive` diagonal is **+0.5427 above chance**. **T3 MET**: and the
answer is still **earned**, at **+0.2622 (16.98 sigma)** and **+0.4382 (31.98 sigma)**. **T5 MET**: the buffer is
worth **0.2953 at 11.84 sigma**.

**T4 FALSIFIER FIRED, and the sign is against memory: the world's memory is worth nothing.** The memoried world's
`naive` diagonal is **0.7691** and the instant one's **0.7927** -- the memory is **behind by 0.0236 at 1.85 sigma**,
inside the 0.02 that fired its falsifier and pointing the wrong way. The instant arms also forget slightly more
(0.4089 against 0.3750, and 0.1135 against 0.0906) and reach slightly higher final accuracies (0.5201 and 0.7000
against 0.5191 and 0.6785).

## 3. And the task starts becoming the state read-out

**That is the mechanism, and it is exact rather than suggestive.** With no memory the world's state *is* the drive,
so the head reads `drive_t @ P.T @ Q` -- a **fixed linear function of the current action**, and the action is a
function of the body's own state. So the read-out has stopped being the environment's history and become **another
linear read-out of the state**, which is the read-out every unit in this corpus before `e348` used. The diagonal goes
*up* by 0.0236 because a fixed linear re-encoding of the state is a **better** feature for a linear head than a
leaky, mixed, saturating one. The channel reading stays at 17 to 32 sigma because the loop still exists -- unwired,
the world does not run -- even though the world holds nothing.

**So the earned label's numbers sort by the read-out's width and not by the world's rule.** Four manipulations of the
same object, in the order the corpus measured them:

| manipulation | effect on the `naive` diagonal |
|---|---|
| the world's **width** (`e350`, `e351`) | **+0.4125** from one number to eight |
| the world's **coupling** (`e359`) | about **0.05** |
| the world's **memory** (this unit) | **-0.0236**, the wrong way |
| the world's **saturation** (`e360`) | **+0.0024** |

**What the read-out has room for is the benchmark; how the world computes is not.** That is the same lesson the
state read-out's channel gave from the other side -- `e343` and `e345` found the loop rewriting 117% of the state
with no decoder reading it -- and it is now measured on the environment's own dynamics as well.

## 4. What it cannot do

*One endpoint*: `leak = 1.0` against 0.35, with the shape between them unrun -- a leak sweep is what would say
whether the memory's value is a gradient or a cliff, and this unit's -0.0236 is a two-point difference. *One coupling
and one draw*: the coupling is `e359`'s own matrix, whose carry the leak multiplies away. *The memoried reference is a
different artifact*, paired by the recorded fingerprints and the per-replicate seed stream. *And "remember" is eight
numbers for a few steps*: nothing here is about a world that keeps a long history, which is what a game with episodes
would need, and nothing here trains a policy -- the task is still "hold the cue", not "act on the world".
