# The ordering of the arms: two chains, five arms, and the diagonal at opposite ends of them

*2026-09-29 03:49. Runs: **none new** — `experiments/e297_the_ordering_of_the_arms.py` builds each of the ten arm
pairs' majority edge from every artifact that ran both, writing `runs/e297_the_ordering_of_the_arms.json`. Seconds.*

## 1. The table the last two units could not draw

`e295` read one edge of the corpus's arm graph (the block penalty against the diagonal) and `e296` another (the block
penalty against its matched random control); together they found a *cycle* across two comparisons. That prompts the
question those units could not ask: **what is the ordering of all five arms, on each metric, from the corpus's own
comparisons?** Five arms — `naive`, `ewc`, `ewc-block`, `ewc-block-rand`, `replay` — ten pairs, two metrics, every
artifact that ran both arms of a pair supplying one paired comparison. The direction is a named constant: for
`final_accuracy` a larger delta is better, for `mean_forgetting` a smaller one is.

| pair (A over B) | metric | comparisons | A ahead | resolved | winner |
|---|---|---|---|---|---|
| `naive` over `replay` | final_accuracy | 34 | 3% | 16 | `replay` |
| `ewc` over `replay` | final_accuracy | 24 | 0% | 11 | `replay` |
| `ewc-block` over `replay` | final_accuracy | 22 | 36% | 8 | `replay` |
| `ewc` over `ewc-block` | final_accuracy | 26 | 19% | 9 | `ewc-block` |
| `ewc-block` over `ewc-block-rand` | final_accuracy | 40 | 38% | 5 | `ewc-block-rand` |
| `naive` over `ewc` | mean_forgetting | 38 | 18% | 18 | `ewc` |
| `ewc` over `ewc-block` | mean_forgetting | 26 | 58% | 3 | `ewc` |
| `ewc` over `ewc-block-rand` | mean_forgetting | 25 | **84%** | 5 | `ewc` |
| `ewc` over `replay` | mean_forgetting | 24 | 54% | 7 | `ewc` |
| `ewc-block` over `ewc-block-rand` | mean_forgetting | 40 | 45% | 7 | `ewc-block-rand` |

## 2. A1 MET — each metric is one chain, with no cycle inside it

```
final_accuracy   worst to best:  ewc < naive < ewc-block < ewc-block-rand < replay
mean_forgetting  worst to best:  naive < ewc-block < ewc-block-rand < replay < ewc
```

Both are acyclic. So the "cycle" `e295` and `e296` found is a **cross-comparison** phenomenon — it appears when the
block penalty's two comparisons are put side by side — and not a cycle within either metric.

## 3. A2 MET — and the diagonal sits at opposite ends of the two chains

The best arm on accuracy is **`replay`**; the best on forgetting is **`ewc`**. The **rank correlation between the two
orders is +0.000** — and the specific case is sharper than that: `ewc` is **1st of five on accuracy (worst)** and
**5th of five on forgetting (best)**. So the arm the project's question selects is the arm the accuracy metric
rejects, and `replay` — the strongest arm on accuracy, which `e276` found beating the penalty by up to 12 sigma — is
fourth of five on forgetting.

## 4. A3's falsifier fired, and it is my registration that was wrong

The claim I registered was that the diagonal forgets *more* than no penalty at all. The data: **the diagonal is better
on forgetting in 31 of 38 comparisons (82%), 18 of them resolved**, so the *falsifier* fired and the direction is the
one a penalty is supposed to produce. `ewc` against `naive` is therefore the corpus's cleanest positive control on
this metric — a penalty that reduces forgetting against no penalty, at 18 resolved comparisons — and the unit's title
claim about it was backwards when registered.

**That is the second registration error in two fires** (`e296`'s C1 and C3 were the first), and both were caught by
the falsifier rather than by a reader: a claim whose direction is written from an impression and checked against the
data before it is published. Worth stating as a rate, because the instrument is what makes it visible.

## 5. What it cannot do

**The comparisons are not independent**: the same configuration recurs across pairs, so one well-run configuration
weights every edge it touches. **The majority edge throws the power away**: the pair counts run 21 to 40 and the
resolved counts 0 to 18, so `ewc-block` against `ewc-block-rand` on forgetting is a 22-to-18 coin flip among forty
noisy comparisons while `ewc` against `naive` on forgetting is 31 to 7 with 18 resolved. **A σ below two is not
equality.** **The arms are paired within an artifact and not across them**, so the edges are majorities of paired
differences at many configurations rather than an estimate at one. **And `replay`'s position inherits `e276`'s caveat**
— it is the arm whose measured spread moves most between samples — while it is also the arm with the fewest artifacts
in several edges (21 to 24 comparisons against 34 to 40 for the pairs involving `naive`).
