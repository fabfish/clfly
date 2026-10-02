# The body writes the cue into its action: the world reads 0.52 against a chance of 0.25, the state reads 0.9958

*2026-10-02. `experiments/e349_the_body_writes_the_cue.py` trains two arms per seed on one world: the head reads the
environment's **final world state** (one scalar) or the model's state at the channel's own neurons (twelve). Five
seeds, 500 Adam steps each, batch 32, `lr = 3e-3`. A minute. Writes
`runs/e349_the_body_writes_the_cue.json`.*

## 1. The unit `e348` licensed

`e348` answered the question that has to be answered before a read-out that is the **environment** is built: the
world's final state -- **one scalar per trial** -- predicts the held-out cue at **0.4336 against a chance of 0.25**
on the frozen substrate, while the model's own state at the channel's neurons reads **0.8125**. And it named what it
could not do in one clause: *"nothing is trained, so this licenses the unit that would train a body to **write** the
cue into its action and does not do it."*

**This is that unit.** The environment is wired, the head reads the **environment's** final state and nothing else,
and the body -- the connectome's recurrent weights and its bias -- has to make that one scalar separable by symbol.
The control arm is the identical training with the head reading the model's state at the channel's neurons instead,
which is the read-out every other unit in this chain has used.

## 2. The answer

| read | mean over 5 seeds | sem | per-seed |
|---|---|---|---|
| world, wired | **0.5208** | 0.0228 | 0.5625, 0.5833, 0.5000, 0.5000, 0.4583 |
| world, unwired | **0.2500** | 0.0000 | 0.2500 at every seed |
| state, wired | **0.9958** | 0.0042 | 1.0000, 0.9792, 1.0000, 1.0000, 1.0000 |

chance 0.2500. **T1 MET**: within a seed the arms share the circuit, the world draw, the examples, the body
initialisation and the batch order, and differ only in what the head reads -- one number against twelve.

**T2 MET**: **a body does write the cue into its action.** The world's one scalar is separable by symbol at
**0.5208, +0.2708 above chance**, on all five seeds. **T3 MET**: unwired, the same trained head reads **0.2500 on
every seed and predicts one class for every held-out example** -- the world at rest is a constant, so the answer
exists only while the environment is wired. **T4 MET**: the state arm reads **0.9958**, **0.4750 more** than the
world arm.

**So the label can be earned, and the price is a number.** Reading the answer out of the environment is possible and
costs **0.4750** of held-out accuracy against reading it out of the model's own state -- which is the read-out that
made every previous unit in this chain a nil, and the only reason to pay it is that the world's carrier is not there
when the loop is not.

## 3. What the pair of units says together

`e348`'s frozen readings and this unit's trained ones are not the same task -- different label draws, split sizes and
batches -- so the comparison is of order and not of tenths: the frozen world read **0.4336** and the trained world
reads **0.5208**, and the frozen state read **0.8125** against the trained state's **0.9958**. **Training moves both
carriers up, and it moves the state's further.** A body that is asked to hold the cue in its own state finds that
easy; a body that is asked to put it into a one-dimensional integrator of its own actions finds it possible and hard.

## 4. What it cannot do

*A bespoke training loop*: the optimiser, learning rate, step count and batch size are the corpus runner's, but the
loop is written here rather than taken from it, so every claim is a **within-unit contrast** -- the two arms of the
same seed -- and none of these numbers is comparable with the corpus's benchmark artifacts. *One leak, one scale and
one world*: `leak = 0.35`, `scale = 1.0`, two world modes and four symbols, with nothing said about a longer trial,
a stronger channel, or a state with more than one dimension -- which is `e333`'s named gap. *Five seeds*: enough to
resolve a 0.10 margin at this spread and not to bound a small one, and the world arm's own spread is wide
(0.4583 to 0.5833). *And the head is linear*: a non-linear read-out of the same scalar could see more, which is
`e345`'s question asked of the state and is not asked here.
