# Can the world be the read-out? Its one scalar carries the cue at 0.43 and the state carries it at 0.81

*2026-10-02. Nothing trains: `experiments/e348_can_the_world_be_the_readout.py` rolls the frozen connectome
network on one world's examples at two leaks and hands the environment's **final world state** -- one scalar per
trial -- to the corpus's own least-squares decoder. Three seconds. Writes
`runs/e348_can_the_world_be_the_readout.json`.*

## 1. The sentence that names the way out, and the knob it needed

Everything in this chain reads the **model's own state**: `e341` and `e344` read trained accuracy, `e342` and `e343`
read frozen decoders on it, `e345` read four widths of them, and all of them find the loop changing the state and
never the answer. `e333` -- whose subject was the world's transition rule -- closed with the sentence that says what
is missing: *"And the label is still delivered: the cue arrives at step 0, so the reward is still not earned."*

**A reward that is earned has to be read from somewhere the model's state is not**, and the environment's world is
exactly such a place: it is a leaky integral of the agent's own actions, reset with the trial, and until this unit
nothing could see its final value at all. `CueActionEnv.feedback()` now exposes it -- `last_world`, and the action as
`last_action` -- set on every call, so a read-out that is the **environment** rather than the model is buildable. The
change is purely additive (assignments only, no expression touched), so every artifact in the corpus is bit-identical
through it.

**This unit asks the question that has to be answered before such a read-out is built: does the world's final state
carry the cue at all, on the frozen substrate, with no training?**

## 2. The answer

| leak | world accuracy (chance 0.25) | state accuracy on the channel's own neurons | world sd | distinct values | channel divergence |
|---|---|---|---|---|---|
| **0.35** | **0.4336** | **0.8125** | 0.2607 | 512 | 56.84% |
| 1.00 | 0.4062 | 0.8125 | 0.2891 | 512 | 66.29% |

**T1 MET**: one configuration across the two leaks -- same circuit `mb+cx+al@n952`, same read-out draw, same 512
train and 256 test examples, four symbols, one scale, gain, noise and world -- and the world's final state takes
**512 distinct values** at the least, so it is a carrier and not a constant. Its per-symbol means at the carried
leak are `[-0.045, 0.271, -0.236, 0.007]`: **a code nobody designed**, with two symbols landing near zero and the
separation living in how far the integrator was pushed.

**T2 MET**: the world's **one scalar** predicts the held-out symbol at **0.4336 against a chance of 0.25**, i.e.
**+0.1836**, before anything is trained. **T3 MET**: carrying the trial is not worse than the instantaneous world --
**0.4336 against 0.4062, +0.0273**, inside the 0.05 the falsifier needed. **T4 MET and it is the finding**: the same
decoder on the model's state at the **channel's own neurons** reads **0.8125**, which is **0.3789 more** than the
world's scalar.

**So a world read-out is buildable and it has something to read -- and it is a worse carrier than the state the
model already has.** The loop's necessity can be bought by reading the answer from the environment; the price is
now a number, and it is that the world's one scalar carries about half of what the state's own channel neurons
carry. What that buys is the one thing the chain has never had: a read-out that is **identically uninformative
without the loop**, since the world's state is driven by the loop and by nothing else.

## 3. What it cannot do, and what it licenses

*A frozen body and a linear decoder*: this is the substrate's carrier capacity and not a trained model's, and a
non-linear decoder could see more from the same scalar. *The decoder is one scalar*: the world's state is one number
by construction, so +0.1836 is a statement about a one-dimensional carrier and not about the channel -- a world with
more state, or a state-to-state coupling, is `e333`'s named gap and not this unit's. *One cue step, one scale and
one leak pair*: the cue is a pulse at step 0 with `scale = 1.0` and `gain = 1.0`, and nothing here says what a
longer trial or a stronger channel would carry. *And nothing is trained*: this says a world read-out has something
to read, **not** that a body can learn to write the cue into its action -- which is the unit this licenses and not
the unit it is.
