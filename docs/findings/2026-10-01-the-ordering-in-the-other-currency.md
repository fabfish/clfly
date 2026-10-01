# The ordering in the other currency: the arm the corpus ranks second-best on forgetting is the arm with the most left to learn

*2026-10-01 06:14. Runs: **none new** — `experiments/e306_the_ordering_in_the_other_currency.py` orders the five arms
by three quantities computed from their own retention matrices, writing
`runs/e306_the_ordering_in_the_other_currency.json`. Seconds.*

## 1. The question `e305` could only ask one arm at a time

`e297` ordered the corpus's five arms on two metrics: accuracy ranks `ewc` last and `replay` first, forgetting ranks
`ewc` first and `replay` fourth. `e304` then showed the forgetting field is **the lost half of the shortfall** and is
blind to the half a task never learned contributes. `e305` measured that blindness per arm. **This unit asks it of the
ordering**: if the field is half of a quantity, what does the other half rank?

Three quantities are computable from every arm's `retention` matrix, and each gives one paired comparison per
`(artifact, replicate)` in which both arms of a pair ran — **3129 such pairs**:

| quantity | best to worst | edges | cycles |
|---|---|---|---|
| **lost** (what the corpus stores) | `replay` > `ewc` > `ewc-block` > `ewc-block-rand` > `naive` | 10 | 0 |
| **unlearned** (never attained) | `naive` > `replay` > `ewc-block-rand` > `ewc-block` > `ewc` | 10 | 0 |
| **shortfall** (everything left to learn) | `replay` > `naive` > `ewc-block` > `ewc-block-rand` > `ewc` | 10 | 0 |

**R1 MET** — all three chain the five arms with no majority cycle, and so does the stored field. **R4 MET** — the
stored `mean_forgetting` and the recomputed lost term give **the same edge on 10 of 10 pairs**, so R2 and R3 are
about a different quantity and not about the field being read wrong.

## 2. The ends swap

**R2 MET.** `ewc` is **second-best on the corpus's metric** and **last of five on the shortfall**; `naive` is **last
on the metric** and **second of five on the shortfall**. **R3 MET** — the rank correlation between the lost ordering
and the unlearned ordering is **−0.400** over the five arms: ranking the arms by forgetting is close to
reverse-ranking them by how much they learned.

So the metric the corpus's ordering claims are written in separates the arms mostly by a quantity it cannot see.

## 3. The exhibit: where the separation actually lives

The margins say it arm by arm. `replay` against `ewc`:

| quantity | margin | rate |
|---|---|---|
| lost (the corpus's field) | **147 of 271** | **54%** |
| shortfall | **259 of 278** | **93%** |

On the corpus's own metric the best arm beats the worst-but-one by a **coin flip**. On the shortfall the same pair is
decided 259 to 19. And on the other side, `replay` beats `naive` on the metric at **360 of 403 (89%)** while `naive`
beats `replay` on the unlearned term at only **184 of 357 (52%)** — another coin flip, in the opposite direction.

A benchmark that reports `mean_forgetting` is reporting, for the corpus's two most-discussed arms, a difference that
its own retention matrices resolve thirteen times more sharply on a quantity the metric does not store.

## 4. What it cannot do

**The population is the arms with a readable retention matrix**, 301 of `e304`'s arms and not every arm `e297` reads:
`e297` takes an edge from any artifact that ran both arms, so its counts are larger and its forgetting order differs
at the top (`e297` puts `ewc` first, this unit `replay`) for that reason and not because the two units read different
metrics — which is what R4 checks within this population. **The arms are not independent**: the same configuration
recurs across the pairs, so a majority edge is a weighted count of correlated comparisons and not a vote of
independent ones, and a 52% margin is a coin flip among them. **A majority edge throws away the power** — the ten
margins run from 51% to 95% — so a chain built of five of them is a description of the corpus's comparisons and
carries no interval, and no verdict here would move if the ordering were read at one sigma instead of a majority.
**And the shortfall is not a loss**: an arm with much left to learn is not necessarily a bad arm, and a large
unlearned term says the arm never solved the task, which is a statement about the arm and not about its forgetting.

## 5. RE-READ 2026-10-01 07:21 — the caveat above is wrong and `e308` is the test that says so

§4 attributes this unit's difference from `e297` — `replay` first here, `ewc` first there, on the same field — to its
**population**, the 301 arms with a readable retention matrix. `e308` holds each of the two differences fixed in turn
and **the population moves nothing**: restricting `e297`'s own method to the 147 artifacts that carry a readable
matrix changes no edge and no ordering, on either metric.

What moves the top is the **unit of the vote**. `e297` pools each artifact's replicates into one contrast and takes a
majority over artifacts; this unit takes one vote per `(artifact, replicate)`. Exactly **two of the ten pairs** flip,
and they are the two this unit's ordering and `e297`'s place differently: `ewc` against `replay`, and `ewc-block`
against `ewc-block-rand` — 15 of 26 artifacts against 147 of 271 votes, and 20 of 42 against 339 of 652. Both pairs
sit within four points of a half under both counts.

Everything else in §4 stands, and R4 is untouched: the recomputed lost term and the stored field agree on all ten
edges within this population, which is the check that makes this unit's reading the corpus's own field
(`docs/findings/2026-10-01-the-unit-of-the-vote.md`).

## 6. RE-READ 2026-10-01 09:41 — R2 is withdrawn, and the third quantity is the accuracy

`e312` tests what this unit's first of three quantities is, and the answer is that it is not a third one:

    shortfall_mean = mean_j (1 - R[T-1][j]) = 1 - final_accuracy

The identity holds in **5581 of 5581** arm-replicates, and on all ten pairs the shortfall's majority edge **is** the
accuracy's, read each in its own direction. So **R2 is withdrawn as a finding**: *"the arm the corpus ranks
second-best on forgetting is the arm with the most left to learn"* is the same sentence as `e297`'s A2, *"the
diagonal is last on accuracy and first on forgetting"*, and `e297` established it three fires earlier.

**R1 stands and is now known to be about two of the corpus's own fields and their difference.** **R4 stands** and is
what made the correction checkable. **R3 stands and is the unit's real contribution**: the lost ordering against the
unlearned ordering is the forgetting against the level a task reached *when it was learned*, which is neither the
accuracy nor the forgetting and which `e310` then measured as a position effect. The currency the corpus lacks is
`unlearned`, and not a shortfall that turns out to be the accuracy with its sign flipped
(`docs/findings/2026-10-01-the-shortfall-is-the-accuracy.md`).
