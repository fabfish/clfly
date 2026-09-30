# Which metric selects the basis: the block penalty is ahead on accuracy in 21 of 26 comparisons and on forgetting in none of the three resolved

*2026-09-29 03:13. Runs: **none new** — `experiments/e295_which_metric_selects_the_basis.py` reads every artifact that
ran both penalty arms, writing `runs/e295_which_metric_selects_the_basis.json`. Seconds.*

## 1. The project's own comparison, read as a population

The question is *"which anchoring basis minimises forgetting"*, and the comparison that carries it is between the two
penalty arms: `ewc` anchors its Fisher in the neuron coordinate basis, `ewc-block` in the within-group blocks of an
annotated partition — the cell-class basis the paper's recommendation is about. **Both arms ran in 26 artifacts**, with
the same seeds inside each, so every comparison is paired over replicates and the corpus can be read as a whole.

The two metrics pull in opposite directions, so the convention is stated rather than assumed: **delta is `ewc` minus
`ewc-block`**, and "ahead" means *better on that metric* — higher is better for `final_accuracy`, **lower** for
`mean_forgetting`.

## 2. B1 MET — on accuracy the block penalty is ahead nearly everywhere

| metric | comparisons | block ahead | resolved at 2σ | of those, block ahead | largest for it | largest against it |
|---|---|---|---|---|---|---|
| `final_accuracy` | 26 | **21 (81%)** | 9 | **8** | 10.45σ | 2.11σ |
| `mean_forgetting` | 26 | **11 (42%)** | 3 | **0** | 1.04σ | 3.67σ |

On accuracy the largest win is `e275`'s re-run at **10.45σ** (`-0.02308`), then `e140` at 6.61σ and the plastic twin
at 5.40σ. The single resolved comparison that goes the other way is `e8_basis.json` (+0.08333 at 2.11σ, **three
replicates**).

## 3. B2 MET — and on forgetting it is ahead in none of the resolved ones

**Three** forgetting comparisons resolve at two sigma and **every one of them is a case of the diagonal arm
forgetting less**:

| artifact | delta (`ewc` − `ewc-block`) | σ | replicates |
|---|---|---|---|
| `e275_frozenbias_suite600_40reps.json` | **−0.00825** | 3.67 | 40 |
| `e140_r32_methods_frozenbias_40reps.json` | **−0.00833** | 2.20 | 40 |
| `e135_r32_methods_frozenbias.json` | **−0.02708** | 2.15 | 5 |

And the largest comparison **for** the block arm on forgetting is **1.04σ** — so on the metric the project's question
is phrased in, the block anchoring has no resolved win anywhere in the corpus and three resolved losses, two of them
at **forty replicates**.

## 4. B3 MET — so the metrics do not select the same arm

Over the 26 artifacts carrying both metrics, the two **disagree about which arm is ahead in 10 of them (38%)** —
including `e140_r32_methods_frozenbias_40reps.json` and `e275_frozenbias_suite600_40reps.json` themselves, the corpus's
best-powered pair.

## 5. What the three add up to

**The recommendation the paper draws is supported by the metric the paper does not phrase its question in.** The basis
study's objective is forgetting; the block penalty loses every resolved comparison on it. A reader who takes
`final_accuracy` as the objective and a reader who takes `mean_forgetting` as the objective will **select different
anchoring bases from the same artifacts**, in 38% of the cases the corpus has. That is the same shape as `e276`'s
finding one arm over — where `replay` beat the penalty on both metrics — and it is the first time the corpus's own two
metrics have been put side by side across the whole arm set.

## 6. What it cannot do

**The 26 artifacts are not 26 configurations**: the same configuration recurs, so the counts weight whatever the corpus
happens to have run more than once, and `e276`'s `replay` arm is not in this comparison at all. **The arms are paired
within an artifact and not across them**, so each delta is one configuration's `ewc − ewc-block` and the population of
deltas is not a sample of anything. **A σ below two is not evidence of equality**: 11 of 26 accuracy comparisons and 23
of 26 forgetting comparisons are unresolved, and B3 counts disagreements of *sign* whether or not either side is
resolved. **`mean_forgetting` over a short sequence is a small number** — the three resolved deltas are 0.008 to 0.027
— so the metric that decides the question is the one with the smaller dynamic range, and nothing here rescales it.
**And the artifacts span four days of runner changes**, so an earlier epoch contributes a comparison of the same
quantity computed by slightly different means.

## RE-READ 2026-10-01 03:04 — the counts shifted and the three claims held

`e301` found seventeen files in the corpus that are a second execution of an experiment already here — including the
1440-item suite of the frozen-bias configuration, written twice — so this census now drops the second copies and reads
**24** comparisons per metric where the file count gave 28.

**B1 MET**: the block arm is ahead on `final_accuracy` in **19 of 24 (79%)** and in 7 of the 8 resolved at two sigma.
**B2 MET**: it is ahead on `mean_forgetting` in **8 of 24 (33%)** and in **0 of the 4** resolved — `e135` at 2.15,
`e140` at 2.20, `e275` at 3.67 and `e287` at **7.79**, the last being the 1440-item suite whose arrival also moved
`e286`. **B3 MET**: the two metrics pick different arms on **11 of 24 (46%)**. The finding's shape is unchanged — the
block penalty wins the accuracy metric and loses every resolved forgetting comparison — and only the denominators a
reader would quote moved.
