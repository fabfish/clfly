# The world gets a rule, and the arm that stores feels it both ways

*2026-10-01. Runs: `experiments/e8_rate_network.py --circuit-size 300 --iters 500 --readout-size 32 --repeats 5
--methods naive,replay --closed-loop --loop-symbols 8 --loop-noise 1.0 --loop-scale 1.0 --loop-world-modes 2
--loop-world-leak {1.0, 0.35}` -- 256 s and 295 s, read by `experiments/e333_the_world_gets_a_rule.py` against
`e332`'s state-world artifact.*

## 1. The state without the rule

`e332` gave the world a **state** and no rule: its channel carries two patterns the agent's action selects between,
so what comes back is a consequence the agent picked -- but the consequence of the **last** action and of nothing
earlier. Its own finding names what that leaves: *"the world has a state and no transition rule: the action picks a
consequence, and nothing else about the world evolves, so it is a world with a state and not yet a world with
dynamics."*

This gives it the rule. `CueActionEnv` gained `world_leak`, and the world's state is now

    w_t = (1 - leak) * w_{t-1} + leak * action_{t-1}

so the channel at step ``t`` is a **decaying sum of the whole action history** and not of one step, and `leak = 1` is
the instantaneous world `e332` measured -- the recursion is the identity.

**T1 MET.** Same circuit `mb+cx+al@n952`, same read-out `59926518137c`, the same three task names, both arms at five
replicates, cue symbols, cue noise, world state count, the action and feedback populations and the population
fingerprints all identical, and **no unexpected config or environment difference** once the leak itself is excluded.

**T4 MET, and it is the control that makes the rest readable.** The `leak = 1.0` run reproduces `e332`'s state-world
artifact **exactly, replicate for replicate, on both quantities and both arms** -- so the rule at one *is* the
instantaneous world rather than merely close to it. The one key the older artifact has not got is the flag itself,
which did not exist when it was written; the default it ran under is this unit's endpoint, and the key set is
reported beside the diff rather than absorbed by it.

## 2. And the rule moves the arm with nothing to retain, in the direction of helping

| arm | accuracy, instant | accuracy, carried | Δ | σ | forgetting, instant | forgetting, carried | Δ | σ |
|---|---|---|---|---|---|---|---|---|
| `naive` | 0.5167 | **0.5486** | **+0.0319** | 1.70 | 0.2271 | **0.1937** | **−0.0333** | 1.10 |
| `replay` | 0.6264 | 0.6042 | −0.0222 | 0.94 | 0.0479 | **0.0854** | **+0.0375** | **2.45** |

**T2 MET** and **T3 MET**: `naive` reads **0.0319 higher** and forgets **0.0333 less** under the carried world, both
clearing the registered 0.03 bar -- at 1.70 and 1.10 sigma, so both are above the bar the registration set and below
the two-sigma line the corpus usually holds.

**And the arm that noticed `e332`'s change notices this one too, the other way.** `e332` measured `replay`'s
forgetting **falling 0.0292 at 2.89 sigma** when the world's response became a state; here the same arm's forgetting
**rises 0.0375 at 2.45 sigma** when the world acquires a rule. So the largest number in this neighbourhood -- the
0.14 to 0.18 gap `replay` holds over `naive` -- is not fixed: it is the arm with stored features whose retention
moves with every change to the world's channel, by about 0.03 each time in whichever direction the change runs, and
it is the only arm that moves at all.

**That is one consistent story and this design does not prove it.** `replay` carries replayed activations, so its
stored features are features of a world; change the world's response and the features are stale in a new way, which
can cost retention (the rule, +0.0375) or -- less obviously -- help it (the state, −0.0292). Both signs are
measurements, neither is a mechanism, and separating them needs the stored features read out, which nothing here
does.

## 3. What it says

**The world now has dynamics, and the agent's own history is in its input.** The channel at step ``t`` is a decaying
sum of every action the agent has taken, so a task the network solves at the last step is solved against a world
that remembers how it got there -- which is the first thing in this thread that is a world rather than a response,
a mirror or a consequence.

**And the price of that is paid by the arm that stores, while the arm that does not is helped.** `naive` does better
in both currencies under the carried world (0.0319 up, 0.0333 less forgetting); `replay` loses 0.0375 of retention
and 0.0222 of accuracy. So the world's rule is not a difficulty knob: it is a change in the **currency**, moving
retention between the arms in opposite directions at the same time.

## 4. What it cannot do

**One leak**: 0.35 against 1.0, with the shape between them unmeasured, and `leak = 0` -- a world that never changes
-- not run either, so the rule's two endpoints are one measured and one named. *Two arms*: `ewc` and the two block
arms are not run, so the arm whose retention moves is the only one asked. *Five replicates*, whose paired standard
error at this spread is near 0.02 on accuracy and 0.03 on forgetting, so T2 and T3 clear their bars at 1.70 and 1.10
sigma and resolve 0.03 and not much less. *The rule is one leaky integrator of one scalar action*: no state-to-state
coupling, nothing the agent can push the world into, and no way for the world to keep a state the agent is not
currently writing. *And the label is still delivered*: the cue arrives at step 0, so the reward is still not earned.
