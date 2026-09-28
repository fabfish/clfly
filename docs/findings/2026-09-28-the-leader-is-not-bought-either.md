# The leader of the three pairs is not bought either: 232 to 297 replicates, not ten

*2026-09-28 23:00. Runs: **none new** — `experiments/e274_the_leader_is_not_bought_either.py` prices the *leader*
rather than the span, from the two `e266` matrices and `e178`'s 144-replicate matrix at the same cell, writing
`runs/e274_the_leader_is_not_bought_either.json`. Seconds.*

## 1. The item: `e272` used the wrong gap

`e272` priced the ordering claim and concluded that the register should state **one bit** — which pair leads — because
the three-way form needs 6,446 replicates while "the highest-against-lowest gap is 0.877, which needs **10**
replicates and is already resolved within the 144 the corpus has". **That is the span, not the leader's gap.** Which
pair leads is decided by the gap between the **top two**, and the span is large only because the *lowest* pair is far
below — a fact about the bottom of the ordering, which says nothing about its top.

The counter-example is already in the corpus: at sixteen replicates the two `e266` runs have **different leaders**. So
the bit is not resolved at that budget, and this unit prices what it would take.

## 2. What the matrices say

| matrix | n | leader | gap over the second | σ | replicates needed at 2σ |
|---|---|---|---|---|---|
| `e266` `seed0 0`, accuracy | 16 | `naive` against `ewc-block-rand` | 0.123 | 0.44 | 272 |
| `e266` `seed0 0`, forgetting | 16 | `naive` against `ewc-block-rand` | 0.168 | 0.56 | 172 |
| `e266` `seed0 100`, accuracy | 16 | `ewc-block` against `ewc-block-rand` | 0.499 | 1.44 | 28 |
| `e266` `seed0 100`, forgetting | 16 | `ewc-block` against `ewc-block-rand` | 0.547 | 1.53 | 25 |
| `e178`, accuracy | 144 | `ewc-block` against `ewc-block-rand` | 0.177 | **1.57** | **232** |
| `e178`, forgetting | 144 | `ewc-block` against `ewc-block-rand` | 0.158 | **1.39** | **297** |

**Y1 MET — one configuration, two seeds, two leaders.** At `seed0` 0 the top pair is `naive` against
`ewc-block-rand` on both metrics; at `seed0` 100 it is the basis pair. The one bit is not resolved at sixteen
replicates.

**Y2 MET — and the corpus's best-powered matrix does not resolve it either.** At 144 replicates the basis pair leads
by 0.177 on accuracy and 0.158 on forgetting, which is **1.57σ** and **1.39σ** against the gap's own standard error —
**under the 2σ bar the rest of the register uses**. So the corpus's best evidence leans one way and does not settle it.

**Y3 MET — so the leader costs 232 to 297 replicates, or 11.9 to 15.2 hours** at the cell's measured 185 s per
replicate. That is **more than the corpus's largest single run** (7.4 h) and 1.6 to 2 times the 144 replicates it has.

**Y4 MET — and the gap `e272` used is a different question.** The top-to-bottom span needs as few as **13** replicates
where the leader's gap needs **232** — a factor of **18**. The span is cheap because the lowest pair is far below; the
leader is expensive because the top two are close.

## 3. What follows

**`e272`'s one-bit reassurance is corrected, and the corrected form is still useful**: the register cannot buy the
leader cheaply, and it *can* buy the statement that the basis pair is not the lowest — which is what the two runs
actually agree about (both put `naive` against `ewc-block` last). So the affordable claim at this cell is **not "which
pair leads" but "which pair trails"**, and the two forms have different prices because the ordering's gaps are uneven.

**And the budget is payable, unlike the three-way form's**: 12 to 15 hours is 1.6 to 2 times the corpus's largest run,
where 367 hours is forty times it. So if the register wants the leader at this cell, it is a run and not an
impossibility — which was `e272`'s conclusion about the span, misapplied to the leader.

## 4. What it cannot do

The two metrics give **different** requirements — 232 and 297 replicates — and nothing here says which is binding for
the register's practice. The top-two gap is measured in three matrices at one cell, so the required budget is that
cell's and not the corpus's. **A leader established at 2σ is a leader at 95% and not a settled fact**, and the bar is
borrowed from the rest of the register rather than derived. The rate is a wall-clock average of a three-arm and two
four-arm runs on one machine. And no run is made: the requirement is arithmetic, and the 12 to 15 hours is a budget
and not a schedule.
