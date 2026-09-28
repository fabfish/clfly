# The fall is not the sample's size: three sample swaps, and the mechanism they refute

*2026-09-29 00:55. Runs: **none new** — `experiments/e286_the_fall_is_not_the_samples_size.py` reads the three pairs
of artifacts the corpus was already holding, writing `runs/e286_the_fall_is_not_the_samples_size.json`. Seconds.*

## 1. The question `e285` left

`e285` read one pair of artifacts as a sample swap — the same forty trained models evaluated on two held-out samples —
and found the across-replicate spread falling in ten of ten arm-by-metric comparisons when the suite went from 144 to
600 items. It named three candidate accounts and separated none of them. The decisive move was available and had not
been made: **the corpus was already holding two more sample swaps**, at a suite ratio of **ten** rather than 4.17, and
the accounts make *opposite* predictions about which of the two should fall further.

## 2. The census, and why the strict rule is the one that selects

A **sample swap** is defined here by the strong rule: two artifacts at different suite sizes whose training-derived
fields agree in every shared arm-replicate row. The census first runs a *weaker* rule — a declared list of shape
fields that must agree, and draw blocks that must not disagree, with a block only one side records counting as a
missing record rather than a disagreement — and the gap between the two rules is X1's reading:

```
the weak rule admits 28 pairs and the training fields keep 3
```

The three, all at forty replicates:

| pair | suite | size | arms | what only one side records |
|---|---|---|---|---|
| `e116_r128_40reps.json` → `e119_r128_test480.json` | 144 → 1440 | x10 | 1 | — |
| `e115_r300_40reps.json` → `e119_r300_test480.json` | 144 → 1440 | x10 | 1 | — |
| `e140_r32_methods_frozenbias_40reps.json` → `e275_frozenbias_suite600_40reps.json` | 144 → 600 | x4.17 | 5 | `support_draw`, `support_seed`, `fisher_from`, `save_fisher` |

**X1 MET — the weak rule is not sufficient and the training fields are what select.** Twenty-five of the
twenty-eight candidates are the corpus's four days of runner changes: artifacts that share a shape and a suite size
and did not train the same models. That is the same class of defect `e285` documented about records and `e284` about
flags, and here it is the reason a pairing rule cannot be built out of config keys alone.

## 3. The designed test: the fall goes the wrong way

**X2 MET — every comparison falls.** Fourteen of fourteen, sd ratios 0.428 to 0.875. The fact `e285` established is now
**three configurations wide**: the same models spread less on a larger held-out sample.

**X3 MET — and the amount is not the sample's size.**

| pair | suite ratio | sd ratio, median | what `1/sqrt(n_eval)` predicts |
|---|---|---|---|
| `e115`/`e116` → `e119` | **x10** | **0.802** | **0.316** |
| `e140` → `e275` | x4.17 | 0.543 | 0.490 |

The account that would let a suite be *priced* — a per-model sampling deviation whose spread goes as `1/sqrt(n_eval)`
— predicts the largest fall for the largest ratio, and the ten-times pairs are the ones that **barely moved**: a
ten-fold suite expansion bought a **20%** reduction in spread where a 4.17-fold expansion bought **46%**. Across the
fourteen comparisons the observed ratio is negatively correlated with the prediction, **corr = −0.697**.

**X4 MET — nor is it the accuracy level's.** The ceiling account rides on `p(1-p)`, and in the **eight** comparisons
where that ratio is above one it predicts the spread should *rise*. It fell in all eight (0.476 to 0.875). So the
account that was the most natural alternative is wrong in its *sign* every time it makes a signed prediction, and the
account that predicts a scaling law is *anti*-ordered.

## 4. What is left standing, and the axis the pairs suggest

**The fact survives; the pricing does not.** `e267` turned the benchmark's own noise block into "the suite each
configuration would need", and `e269` measured that held-out decisions are free — the pair of them is an argument that
a suite can be *sized by arithmetic*. `e275` then bought one. What this unit adds is that the arithmetic cannot
predict the *spread* it is supposed to be compared against: the spread does fall when the sample grows, but not as
the sample's size, and the natural account is refuted in the direction of its own prediction.

**And the pairs suggest the axis is not the suite at all.** The two configurations that barely moved read out through
**128 and 300** neurons; the one that moved by half reads out through **32**. That is the same variable the corpus has
already found load-bearing elsewhere — a wide read-out solves these tasks without the recurrent weights doing the
routing, which is why the `readout_size` ladder exists — and it is named here as the next thing to vary, not
measured.

## 5. What it cannot do

**Three configurations and three pairs**, so every statement is about those; the axis they suggest is named and **not
varied**, and nothing here separates read-out width from circuit size (300 and 800), arm count (one against five),
method mix or code epoch. **Two suite ratios** (4.17 and 10), so X3 is an ordering test between two points and not a
scaling law: what it refutes is `1/sqrt(n_eval)`, and it cannot say what the fall *is* a function of. **The spread is
measured on forty replicates**, so each ratio carries about a third of its own value as sampling error, and the
ten-times pairs rest on four comparisons where `e285`'s rests on ten — which is why X3 is stated as an ordering and a
correlation rather than as a value. **The training is inferred to be identical** from the parameter-derived fields and
not from stored weights, exactly as in `e285`. **The weak rule is permissive by construction**: a missing draw or a
missing flag does not separate, so X1 bounds how much the strong rule is needed and not how many sample swaps exist —
and the pairing rule's permissiveness is the price of a corpus that spans four days of runner changes. And **the pairs
are not the same experiment**: `e285`'s has five arms and both new ones a single `naive` arm, which is why X3 refutes
an account rather than measuring one.
