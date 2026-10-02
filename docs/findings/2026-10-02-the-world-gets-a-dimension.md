# The world gets a dimension: the earned label's price was the carrier's width

*2026-10-02. `experiments/e350_the_world_gets_a_dimension.py` trains three arms per seed on one world -- the head
reading the environment's scalar state (one number), its vector state (eight), or the model's own state (twelve).
Five seeds, 500 Adam steps each, batch 32, `lr = 3e-3`. Eighty seconds. Writes
`runs/e350_the_world_gets_a_dimension.json`.*

## 1. The two readings of `e349`'s price

`e349` made the label earned -- the head reading the **environment's** final state and nothing else -- and measured
what it costs: the world arm reads **0.5208** against a chance of 0.25 while the same training with the head on the
model's own state reads **0.9958**, a gap of **0.4750**. Two readings of that gap were left open, and they are
different units: either a body cannot *write* a rich answer into an integrator of its own actions, or the integrator
is **scalar** and there is nowhere to write it. `e333` named the second as its own gap: *"The world's rule is linear
and scalar: one leaky integrator of one action, with no state-to-state coupling and nothing the agent's actions can
push it into."*

**This unit gives the world a dimension.** `CueActionEnv` gained `world_dims`: above zero the state is a vector of
that many numbers, driven by the whole action **population** through a fixed map and answering through a second one,
both drawn from the environment's seed and fingerprinted in its draw. The change is additive -- `world_dims = 0` is
the scalar path untouched -- and the reproduction below is the evidence.

## 2. The answer

| read | mean over 5 seeds | sem | per-seed |
|---|---|---|---|
| `w1`, the scalar world (1 number) | **0.5208** | 0.0228 | 0.5625, 0.5833, 0.5000, 0.5000, 0.4583 |
| `w8`, the vector world (8 numbers) | **0.9875** | 0.0051 | 0.9792, 1.0000, 0.9792, 1.0000, 0.9792 |
| `state`, the model's own (12 numbers) | **0.9958** | 0.0042 | 1.0000, 0.9792, 1.0000, 1.0000, 1.0000 |
| `w8`, unwired | **0.2500** | 0.0000 | 0.2500 at every seed |

chance 0.2500. **T1 MET**: the three arms share the circuit, the cue, action and feedback populations, the examples,
the body initialisation and the batch order, with one distinct fingerprint each across the arms and one leak.

**T2 MET**: the vector world is learnable -- **0.9875, +0.7375 above chance**. **T3 MET**: the dimension buys
**+0.4667** (0.9875 against 0.5208), where the falsifier needed at least 0.02 of it to be nothing. **T4 MET, and it
is the answer**: the state arm's lead falls from **+0.4750** over the scalar world to **+0.0083** over the vector one
-- **four tenths of one held-out decision in 48**. And **`w8` unwired reads 0.2500 on every seed**, so the answer
still exists only while the environment is wired, which is what makes the label earned rather than merely delayed.

**So the price `e349` measured was almost entirely the carrier's width.** A body asked to write the cue into an
integrator with nowhere to put it gets 0.52; given eight numbers it gets 0.9875 and is level with the state read-out.

## 3. And the scalar arm reproduces `e349` to the digit

`w1` reads **0.5208** over the same five seeds with the same per-seed values the `e349` world arm recorded --
`0.5625, 0.5833, 0.5000, 0.5000, 0.4583` -- so the new environment field, the three-arm loop and the second module
all reproduce the earlier unit exactly on the arm they share. That is the control for the change being additive, and
it is stronger than an assertion about it.

## 4. What it cannot do

*The two world arms are different objects and not two widths of one*: `w8` replaces the scalar recursion and the
two-template blend with a linear map in and a linear map out, so the difference is the dimension **and** the shape of
the channel together, and only a dimension sweep would separate them -- `dims = 1` is the arm that would do it.
*Eight is the action population's size*, not a rung on a ladder: nothing here says what four or sixteen would do.
*One leak, one scale and four symbols*: `leak = 0.35`, `scale = 1.0`, 96 train and 48 test examples, and nothing
here says what a longer trial would carry. *Five seeds*, enough to resolve a 0.10 margin and not to bound a small
one, though the vector arm's spread is now tiny (0.9792 to 1.0000). *And the training loop is written here rather
than taken from the runner*, so every claim is a within-unit contrast between arms of the same seed and none of
these numbers is comparable with the corpus's benchmark artifacts.
