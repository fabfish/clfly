# The reversal with five arms: the effect is carried by the arms that read a penalty

*2026-10-01 13:11. Runs: **two new** — `runs/e317_five_as_built.json` and `runs/e317_five_reverse.json`, written by
`e8_rate_network.py --circuit-size 300 --readout-size 32 --train 96 --test 48 --iters 500 --repeats 5 --methods
naive,ewc,ewc-block,ewc-block-rand,replay` with `--task-order as-built` and `--task-order reverse`. About six minutes
each.*

## 1. The question the last two runs left open

`e315` made the corpus's first permuted suite and found **all six** of its moved-position contrasts favouring the run
that trains the task first, in three arms. `e316` repeated the reversal on the assembly family and found the effect
carried by **`ewc` alone** — +0.0854 at 4.38 sigma and −0.0958 at 6.27 — with `naive` and `replay` at or below 0.71
sigma. Its own limitation named what that left open: **`ewc` is the arm that reads the largest penalty, so whether the
effect is about the penalty is a third configuration's question.**

**This is the third configuration.** The same reversal, the same assembly family and the same circuit, with **all
five** arms — `naive` and `replay` reading no penalty, `ewc`, `ewc-block` and `ewc-block-rand` each reading one.

**R1 MET** — same circuit `mb+cx+al@n952`, same read-out subset `59926518137c`, same seeds, one task list reversed.

## 2. The answer: the penalty arms carry it, and the control holds in exactly those three

`delta` is forwards minus backwards, paired over the five replicates; a positive delta at position 0 or a negative
one at position 2 is a contrast **with** the position effect.

| arm | reads a penalty | `odour_identity` 0 → 2 | `odour_input` 2 → 0 | control `heading` |
|---|---|---|---|---|
| `ewc` | yes | **+0.0917 (2.75σ)** | **−0.1083 (4.33σ)** | 0.55σ, smallest |
| `ewc-block` | yes | **+0.0167 (1.37σ)** | **−0.0500 (1.99σ)** | 0.24σ, smallest |
| `ewc-block-rand` | yes | **+0.0458 (2.56σ)** | **−0.0542 (2.15σ)** | 0.15σ, smallest |
| `naive` | no | −0.0083 (0.78σ) | −0.0042 (**1.00σ**) | **1.97σ, not smallest** |
| `replay` | no | +0.0125 (0.88σ) | −0.0083 (0.67σ) | **1.05σ, not smallest** |

- **R2 MET**: **9 of 10** moved contrasts favour the first-trained run; the one that does not is `naive`'s
  `odour_identity` at 0.78 sigma.
- **R3 FIRED**, on the narrowest possible margin: **7 of 10** contrasts clear one sigma and they belong to
  `ewc-block`, `ewc-block-rand`, `ewc` **and one `naive`** — `naive`'s `odour_input` at exactly **1.00 sigma**.
  `replay` never clears it at all.
- **R4 MET**: the unchanged-position task is the smallest of its three contrasts in **3 of 5** arms — **and the three
  are exactly the penalty arms**. In `naive` and `replay` the control is the *largest* contrast of the three.

## 3. What the three runs together say

| run | family | arms | replicates | what carries the effect |
|---|---|---|---|---|
| `e315` | overlap, three draws | 3 | 5 | all three, direction unanimous |
| `e316` | assembly, three modalities | 3 | 10 | **`ewc` alone**, 4.38 and 6.27 sigma |
| `e317` | assembly, same configuration | **5** | 5 | **the three penalty arms**, 1.37 to 4.33 sigma |

So `e316`'s contrast was not about `ewc`: it was about `ewc` being **the only penalty arm in that run**. With the
other two added, all three carry the effect and both arms that read no penalty sit at the threshold — `naive`'s
1.00 sigma is the single crossing, and the control separates the two groups perfectly, being the smallest contrast in
exactly the three penalty arms and the largest in the two others.

**That is a mechanism-shaped result**: where a task sits in the sequence costs the arms that are regularising toward
a basis, and costs the unregularised arms nothing. It is also a warning for the benchmark: a suite whose order is
permuted will move the numbers of the penalty arms and leave `naive` and `replay` where they were, so an order-axis
comparison has to say which arms it is about.

## 4. What it cannot do

**One configuration and five replicates per arm**, so a contrast near the threshold is a contrast this run does not
resolve, and R3's firing is exactly that: `naive`'s crossing is 1.00 sigma. **The arms are not independent
experiments** — same suite, same seeds, same initial body — so "carried by the penalty arms" is a statement about
which arms move and not about a mechanism, and the three penalty arms' contrasts share their tasks. **No arm is
compared with itself**: the design contrasts arms that read a penalty with arms that do not, and not one arm with its
penalty switched off, which would be the controlled version of the same question. **And a reversal is one
permutation**: the middle task holds its position by construction, so the control is a *position* that did not move
and not a run perturbed in one place only.

## 5. And it flipped a resolved *method* comparison

The same two runs fired **`e295`'s B2**, which had registered that *the block penalty is behind the diagonal on
`mean_forgetting` in every resolved comparison*. It is not any more, and the comparison that fired it is this unit's
own pair:

| artifact | block minus diagonal on `mean_forgetting` | sigma |
|---|---|---|
| `e317_five_as_built.json` | **−0.08333** | **2.64** |
| `e317_five_reverse.json` | **+0.07500** | **2.60** |

**The same configuration, one order forwards and the other reversed, resolves the block penalty against the diagonal
on one run and for it on the other, at 2.6 sigma each.** So the sign of the corpus's headline arm comparison on the
forgetting metric is the **order's** and not the method's — which is the strongest form this axis has taken: not that
the order moves a level, but that it moves the *conclusion* a methods table would print
(`docs/findings/2026-10-01-the-ordering-in-the-other-currency.md`).
