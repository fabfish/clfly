# One number, two channels: the width is 88% of `e350`'s gain and the shape is a seventh

*2026-10-02. `experiments/e351_one_number_two_channels.py` trains three arms per seed -- one number through the
template channel, one number through the map channel, eight numbers through the map channel -- on one world. Five
seeds, 500 Adam steps each, batch 32, `lr = 3e-3`. Eighty seconds. Writes
`runs/e351_one_number_two_channels.json`.*

## 1. The arm `e350` named and could not run

`e350` gave the world a state vector, measured the earned label's price falling from **+0.4750** to **+0.0083**, and
closed on the ambiguity it could not remove: *"the two world arms are different objects and not two widths of one:
`w8` replaces the scalar recursion and the two-template blend with a linear map in and a linear map out, so the
difference is the dimension **and** the shape of the channel together, and only a dimension sweep would separate
them -- `dims = 1` is the arm that would do it."*

**This unit runs that arm.** `world_dims = 1` holds the world at **one number** and replaces the channel: the drive
is the whole action population through a fixed `(1, n_action)` map instead of the mean through `tanh`, and the answer
is a fixed `(1, n_feedback)` map instead of the two-template blend.

## 2. The answer

| read | mean over 5 seeds | sem | per-seed |
|---|---|---|---|
| `scalar`, one number, template channel | **0.5208** | 0.0228 | 0.5625, 0.5833, 0.5000, 0.5000, 0.4583 |
| `dim1`, one number, map channel | **0.5750** | 0.0376 | 0.5417, 0.7083, 0.5208, 0.6042, 0.5000 |
| `dim8`, eight numbers, map channel | **0.9875** | 0.0051 | 0.9792, 1.0000, 0.9792, 1.0000, 0.9792 |

chance 0.2500. **T1 MET**: the arms share the circuit, the cue, action and feedback populations, the examples, the
body initialisation and the batch order, with one distinct fingerprint each and one leak.

**T2 NULL, and it is the honest answer to `e350`'s question.** The channel's shape at one number buys
**+0.0542** -- over the **0.05** the claim asked for and well under the **0.10** that would have made the width
incidental. Paired within a seed the five deltas are `[-0.0208, +0.1250, +0.0208, +0.1042, +0.0417]`, a mean of
**+0.0542 on a sem of 0.0268**, i.e. **2.0 sigma with four of five seeds positive**. So the shape is **not nothing**
and it is **not the story**: a seventh of the total.

**T3 MET**: the width buys **+0.4125** -- `dim8` at 0.9875 against the better of the two one-number arms at 0.5750
-- which is **88% of the +0.4667** `e350` measured. **T4 MET**: all three arms are far above chance (+0.2708,
+0.3250, +0.7375) and every one of them reads **a single class** on every held-out example when the environment is
unwired, so each answer exists only while the loop is closed.

**So `e350`'s headline stands with a correction.** "The price was the carrier's width" is right in the sense that
matters -- five sixths to seven eighths of the gain is the width -- and wrong if read as "the channel does not
matter", because at one number the map channel is worth **+0.0542** against the template one, at 2.0 sigma paired.
The honest sentence is that the width buys most of it and the shape buys a seventh.

## 3. And the scalar arm reproduces itself a third time

`scalar` reads **0.5208** over these five seeds with the same per-seed values `e349`'s world arm and `e350`'s `w1`
arm recorded -- `0.5625, 0.5833, 0.5000, 0.5000, 0.4583` -- and `dim8` reproduces `e350`'s `w8` to the digit as
well. Three modules, two of them written after the environment changed twice, give the same two arms exactly; that
is the strongest reproducibility statement this line has, and it is a by-product of asking the question.

## 4. What it cannot do

*Three points and not a sweep*: this separates one number from eight and says nothing about how the accuracy moves
between them or past eight -- `dims` 2, 4 and 16 are unrun, so the shape's +0.0542 is not known to be a constant in
the width. *The two one-number channels differ in more than one way*: the template arm has `tanh` and a blend and the
map arm has neither, so +0.0542 is the whole channel and not one of its parts. *One leak, one scale and four
symbols*: `leak = 0.35`, `scale = 1.0`, 96 train and 48 test examples. *Five seeds*: enough to resolve a 0.10 margin
and, on the paired contrast, to put the shape's contribution at 2.0 sigma and not more. *And the training loop is
written here rather than taken from the runner*, so every claim is a within-unit contrast between arms of the same
seed and none of these numbers is comparable with the corpus's benchmark artifacts.
