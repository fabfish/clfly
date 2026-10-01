# The world answers with a state, and one arm notices

*2026-10-01. Runs: `experiments/e8_rate_network.py --circuit-size 300 --iters 500 --readout-size 32 --repeats 5
--methods naive,replay --closed-loop --loop-symbols 8 --loop-noise 1.0 --loop-scale 1.0 --loop-world-modes {0, 2}` --
197 s and 279 s, read by `experiments/e332_the_world_answers_with_a_state.py`.*

## 1. A mirror, and what a mirror cannot do

`e331` asked the line's headline ordering under the loop and found it surviving, on a world whose response to the
agent is a **scalar report**: the action is a ``tanh`` of the mean activity over eight neurons, scattered onto
twelve others, so what comes back says *what the agent did* and nothing else. That is a mirror, and a mirror is why
the two units before it ended on the same sentence -- `e325`'s *"a reward and a policy"* and `e326`'s *"the label
delivered at step 0 rather than earned"*. A world with no state of its own can correct the agent; it cannot present a
consequence.

**This unit gives the world a state, and only that.** `CueActionEnv` gained `world_modes`: at zero the channel is
the scalar report exactly as before, and at two the agent's action **selects** one of two patterns by a smooth
interpolation, so what comes back is a consequence the agent picked. The blend is taken about the two patterns'
midpoint, so a neutral action shows **nothing** -- a world that answers when it is asked and not otherwise.

**T1 MET.** Same circuit `mb+cx+al@n952`, same read-out `59926518137c`, the same three task names, both arms at
five replicates in both runs, the cue symbols, the cue noise, the feedback strength, the action and feedback
populations and the population fingerprints all identical, and **no unexpected config or environment difference**
once the world's state count and its pattern fingerprint are excluded.

## 2. And the agent barely notices

| arm | accuracy, report | accuracy, state | Δ | σ | forgetting, report | forgetting, state | Δ | σ |
|---|---|---|---|---|---|---|---|---|
| `naive` | 0.5111 | 0.5167 | +0.0056 | **0.22** | 0.2146 | 0.2271 | +0.0125 | 0.36 |
| `replay` | 0.6139 | 0.6264 | +0.0125 | 0.43 | 0.0771 | **0.0479** | **−0.0292** | **2.89** |

**T2's falsifier FIRED.** The registered claim was that the world's response moves `naive`'s level by at least 0.03;
it moves it by **0.0056**, at 0.22 sigma. **T3 landed on its NULL**: `naive`'s forgetting moves by 0.0125, inside
the band.

**So for the arm with no memory machinery, a world that answers with a consequence is the same world as one that
answers with a number.** That is a real negative and it is not a power problem for the size the registration
expected: five replicates put the standard error near 0.026 on accuracy, so a 0.03 effect would have been about
1.2 sigma -- thinner than the claim deserved, and the honest version is that this unit can rule out an effect of
`e331`'s contrast size and cannot rule out a small one.

## 3. And the one arm that notices is the one that stores

**T4 MET.** In the state world `replay` forgets **0.1792 less** than `naive` -- 0.0479 against 0.2271 -- and that is
the same order of magnitude `e331` measured on the mirror world (a gap of 0.1375 there). So the largest number in
this neighbourhood is the most robust thing in it: it survives a noisy cue, a headroom task, a closed loop and now a
world with a state, at 0.14 to 0.18 every time.

**And the arm that notices the change is `replay` alone**: its forgetting moves **−0.0292 at 2.89 sigma** when the
world starts answering with a state, while `naive`'s moves +0.0125 at 0.36. This is not one of the four claims -- it
is a description taken after the registration -- but it is the only resolved move in the table, and it points the
same way the whole thread does: what a change to the world's response costs is visible in **retention**, in the arm
that keeps something to retain, and not in the arm that does not.

**Two candidates and this design does not separate them**: a state channel is a *richer* self-input, so storing arms
get a better handle on their own history; or it is *noisier*, and `replay`'s stored features are what absorb it. Both
predict that `naive` is unmoved, which is what happened.

## 4. What it cannot do

**Two arms**: `ewc` and the two block arms are not run, so T4 is one pair and not the ordering, and the 2.89 sigma
move is `replay`'s alone. *Two world sizes*: zero states and two, with three or more not run and the interpolation
between more than two states a design this unit does not have. *Five replicates*, so T2's falsifier fired on a bar
the design could only have resolved at about 1.2 sigma -- the negative is "not of that size" and not "not there".
*The world has a state and no transition rule*: the action picks a consequence, and nothing else about the world
evolves, so it is a world with a state and not yet a world with dynamics. *And the label is still delivered*: the
cue arrives at step 0, so the reward is still not earned -- this is the first world that answers with a consequence,
and not yet a game.
