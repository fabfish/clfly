# The earned label through the corpus's own runner: the paired channel reads +0.28 to +0.43 at 6 to 17 sigma

*2026-10-02. One runner invocation: `--circuit-size 300 --iters 500 --readout-size 32 --train 96 --test 48
--repeats 5 --methods naive,ewc-block,ewc-block-rand,replay --closed-loop --loop-symbols 4 --loop-noise 1.0
--loop-world-dims 8 --loop-world-leak 0.35 --loop-scale 1.0 --readout-from-world`, into
`runs/e355_earned_label_r32_5reps.json`. Ten minutes. Read by
`experiments/e355_the_earned_label_through_the_runner.py`.*

## 1. The gap every unit from `e349` to `e354` named

`e349` to `e354` built a task whose answer exists **only in the environment** and named the same limit in each of
their "what it cannot do" sections: *the loop is written here rather than taken from the runner*, so `ewc`, the block
penalties and the matched-random control do not apply and none of the numbers is comparable with the corpus's
artifacts.

**Two changes close it, and neither touches a call site.** `CueActionEnv` gained a `WorldReadout` wrapper beside
`ClosedLoop`: it writes the world's own state into the read-out's columns at the last step, and because every call
site in the runner computes the head's input as `traj[:, -1, :][:, task.readout_neurons]`, the training loop, the
evaluation, the Fisher blocks and the gradients all read the environment without any of them being edited. Two flags
expose it -- `--loop-world-dims` and `--readout-from-world`, both off by default -- and **the world the runner drew
is the local loop's world to the fingerprint**: `world_read_sha1 3a7ba76b3619`, the same value `e352` and `e353`
recorded.

## 2. The answer

| arm | final accuracy | diagonal | `mean_forgetting` | paired channel | sigma |
|---|---|---|---|---|---|
| `naive` | 0.5667 | 0.8264 | **0.3896** | **+0.3056** | 8.93 |
| `ewc-block` | 0.5403 | 0.7583 | 0.3271 | **+0.2847** | 6.06 |
| `ewc-block-rand` | 0.5403 | 0.7667 | 0.3396 | **+0.2764** | 9.22 |
| `replay` | **0.6889** | 0.7736 | **0.1271** | **+0.4333** | 16.64 |

chance 0.2500. **T1 MET**: the artifact records the world read-out, every task's read-out is the world's own width,
and all four arms carry their five replicates. **T2 MET**: the runner learns through the world -- `naive`'s diagonal
mean is **+0.5764 above chance**. **T3 MET**: and it forgets, by **0.3896** (per task 0.4792, 0.2292, 0.0000;
`naive`'s retention is `[[0.771], [0.458, 0.812], [0.292, 0.583, 0.812]]`). **T4 MET**: `replay` cuts the forgetting
by **0.2625 at 5.42 sigma**, paired over replicates -- the same size and direction the local loop found (0.2188),
now on the corpus's own trainer.

**T5 MET, and it is the number this line has been looking for.** The **paired channel reading** -- the corpus's own
`e338` instrument, a trained body read once through the loop and once with it unwired -- is
**+0.2847 to +0.4333 in all four arms, at 6.06 to 16.64 sigma**. Every earlier unit in this chain measured that
quantity and found **0.0000**: `e338` on the state read-out, `e341` over forty replicates, `e344` at every cue
position. Here the same instrument, unmodified and unasked, reports that **the answer genuinely depends on the loop**
-- because the read-out is the environment, and unwired the environment is at rest.

## 3. What it means

**The earned label is now a corpus benchmark.** Four of the corpus's own arms, its own metrics (`learned`, the
retention matrix, `mean_forgetting`, `final_accuracy`), its own optimiser and its own paired-channel instrument run
on it unchanged, and the result is a benchmark-shaped table: a third of `naive`'s accuracy is forgotten, a
sixteen-example buffer takes two thirds of that away at 5.42 sigma, and every arm's answer is earned at 6 sigma or
better.

**And the matched-random pair is a near-tie on it**: `ewc-block` forgets 0.3271 and `ewc-block-rand` 0.3396, a
difference of 0.0125 on five replicates. That is the corpus's own basis contrast -- the one eleven audits left a null
on the state read-out -- and this run neither rescues it nor contradicts it: it is reported here and not claimed,
because five replicates put it far inside the noise.

## 4. What it cannot do

*One configuration and five replicates*: T2 to T5 are five paired numbers per arm, and the run's own power note says
it detects effects above 0.106, with 0.03 needing sixty-three replicates. *The arms are the corpus's methods and not
its controls*: `frozen`, `frozen-bias` and the oracle line are not run, and the basis contrast needs the
matched-random pair on many more replicates than five. *One world, one leak and one width*: `leak = 0.35`, eight
dimensions and four symbols per task, with `e351`'s finding that the width is 88% of the carrier's value and its
channel's shape a seventh. *And the paired reading's unwired side is exact rather than evaluated*: with the
environment unwired the world does not run, so the head sees one constant and that accuracy is computed from the rest
state -- which is the definition of an earned label and not a measurement of one.
