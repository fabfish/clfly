# The pairing in the corpus: 68 matched pairs, a median correlation of +0.30, and eight contrasts the unpaired convention would not have resolved

*2026-09-29 02:56. Runs: **none new** — `experiments/e294_the_pairing_in_the_corpus.py` reads every `matched_pair`
block the corpus carries, writing `runs/e294_the_pairing_in_the_corpus.json`. Seconds.*

## 1. The blocks nobody had read as a population

Every rate-network artifact that ran both arms of a contrast stores a `matched_pair` block: the delta, the sem over
the replicates computed **paired** and **unpaired**, the correlation between the two arms' per-replicate values, and
the two sigmas. `e276` used one of those blocks to correct a sigma the paper had quoted from the unpaired sem, which
is what a *case* of the problem looks like. This unit reads all of them.

## 2. P1 MET — the two arms move together

**68 blocks over 34 artifacts, spanning 3 to 144 replicates. 59 of the 68 correlations are positive, median +0.302**,
and the paired sem is the smaller in **59 of 68**, median ratio **0.837** — against `sqrt(1 - rho)` predicting
**0.835**, so the stored sems obey the identity where the two arms' sds are comparable. By replicate count:

| replicates | blocks | positive | median correlation |
|---|---|---|---|
| 3 | 12 | 10 | +0.382 |
| 5 | 28 | 23 | +0.302 |
| 16 | 8 | 8 | +0.488 |
| 40 | 18 | 16 | +0.214 |
| 144 | 2 | 2 | +0.300 |

## 3. P2 MET — and not always

**9 of the 68 correlations are negative**, from **−0.500** (`e10_rung_supertype`), and **all nine have the paired sem
*larger* than the unpaired one** — for those contrasts pairing costs interval width rather than saving it. The
mechanism is exactly the correlation's sign: the two arms disagree from replicate to replicate, so their difference
is noisier than either value.

## 4. P3 MET — and the convention decides what resolves

Over the same 68 contrasts: **resolved at two sigma, 10 under the paired sem against 2 under the unpaired one.** That
is the number that matters, and it is what `e276` found in a single instance: a sigma quoted from the unpaired sem
asks the reader to buy noise the design already cancelled. In this corpus that convention would have thrown away
eight of the ten contrasts it resolves.

## 5. What it cannot do

**The correlation is an across-replicate correlation between two arms' aggregate metrics**, not an item-level one, so
nothing here says how much of it is the shared test sample and how much the shared training — `e285`'s sample swap is
the instrument for that, and it has one configuration. **The blocks span 3 to 144 replicates**, so a correlation on
three replicates carries an error of about 0.5 and the list's extremes are its small-n entries; the claims are stated
over the whole population for that reason and the report breaks it down by replicate count. **`sem_paired /
sem_unpaired` equals `sqrt(1 - rho)` only when the two arms' sds are equal**, which is why the identity holds on the
median and fails badly where they are not (`e28_side_lam0.1` measures 0.389 where the identity predicts 0.029), and
nothing here corrects for that. **The two counts at two sigma are counts of stored sigmas**, so they inherit the
runner's formula, and a contrast at 2.1 sigma is one replicate from crossing. **And nothing here re-reads the
paper**: which of its printed sigmas came from the unpaired convention is a question for a reader with both numbers in
front of them.
