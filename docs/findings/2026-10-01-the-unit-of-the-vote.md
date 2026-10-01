# The unit of the vote: the corpus's best-forgetting arm is a property of the counting and not of the corpus

*2026-10-01 07:21. Runs: **none new** — `experiments/e308_the_unit_of_the_vote.py` reads the same corpus's same
forgetting field through `e297`'s method and `e306`'s, writing `runs/e308_the_unit_of_the_vote.json`. Seconds.*

## 1. An attribution `e306` made and this unit tests

`e306` orders the five arms by `replay > ewc > ewc-block > ewc-block-rand > naive` on the corpus's forgetting field.
`e297` orders the same arms on the same field as `ewc > replay > ewc-block-rand > ewc-block > naive`. `e306` named
the difference in its own limitations and **attributed it to its population** — the 301 arms with a readable
retention matrix rather than every arm `e297` reads. Two things differ between the units and only one of them is the
population:

```
e297   one pooled contrast per artifact,      then a majority over artifacts
e306   one vote per (artifact, replicate),    then a majority over votes
```

Holding each fixed in turn settles it.

## 2. V1 — the population moved nothing

Restricting **`e297`'s own method** to the **147 artifacts** that carry a readable retention matrix changes **no edge
and no ordering, on either metric** — all ten pairs, both chains. `e306`'s caveat is resolved in the negative: the
filter is not what moved the top of the ordering.

## 3. V2 and V3 — the counting moved exactly two pairs, and they are the top

| pair | artifact-level | votes | per-vote |
|---|---|---|---|
| `ewc` vs `replay` | **`ewc`** | 15 of 26 (58%) | **`replay`**, 147 of 271 (54%) |
| `ewc-block` vs `ewc-block-rand` | **`ewc-block-rand`** | 20 of 42 (48%) | **`ewc-block`**, 339 of 652 (52%) |
| the other eight | identical | — | identical |

**V2 MET**, and not loosely: the two pairs whose majority *edge* flips are **exactly** the two the two orderings place
differently — the edge set and the inversion set are the same two pairs. **V3 MET**: the artifact-level method puts
**`ewc` first and `replay` second**; the per-vote method puts **`replay` first and `ewc` second**.

So the corpus's answer to *"which arm forgets least"* is `ewc` if an artifact is the unit of the vote and `replay` if a
replicate is — and both pairs that decide it are decided inside four points of a half.

## 4. What this corrects, and what it leaves standing

**`e306`'s limitations section attributes the difference to the population and that attribution is wrong**; this
finding's V1 is the test that refutes it, and `e306`'s finding now says so. What survives from `e306` is everything
its own R4 checked within one population: the recomputed lost term and the stored field agree on all ten edges.

**What it does not settle.** *Both readings are on the same corpus and the same field*, but pooling replicates into
one mean before voting is a different quantity from a vote per replicate, and this unit reports **which pairs move
and not which method is right**. *Neither carries an interval*: a majority edge is a count, and both pairs that move
sit within four points of a half. *Neither is the only reading*: a weighted majority, a paired test per artifact or a
bootstrap over configurations would each be a third, and nothing here says which a benchmark should print. *And the
corpus's artifacts are not independent configurations*, which is why the weighting question is live at all — a
configuration run forty times can outvote one run five times.

## 5. RE-READ 2026-10-01 11:04 — V1 fired when `e315`'s two artifacts landed

`e308`'s V1 held when this was written: restricting `e297`'s method to the artifacts carrying a readable retention
matrix changed **no edge**. The two artifacts `e315` wrote carry the matrix in full and add `ewc` and `replay`
comparisons at a third circuit size, and **one of the ten pairs now moves with the population**: `ewc>replay`.

**V2 and V3 stand unchanged** — the weighting still moves exactly `ewc>replay` and `ewc-block>ewc-block-rand`, and
the two orderings still put different arms first. So the unit's finding is narrower than it was written: the filter is
not *invariantly* innocent, it was innocent of the corpus as it stood, and a run that adds matrix-carrying artifacts
at a new configuration can move one edge
(`docs/findings/2026-10-01-the-order-the-runner-never-took.md`).

## 6. RE-READ 2026-10-01 12:04 — all three fired, and the two countings now agree at the top

`e316`'s two artifacts carried the corpus past this unit's reading, and **V1, V2 and V3 have all fired**:

- **V1**: the population moves one edge (`ewc>replay`), as it did after `e315`.
- **V2**: the two methods now disagree about `ewc>replay` **and** the two orderings differ by one adjacent pair
  (`ewc-block` against `ewc-block-rand`), so the edge set and the inversion set are no longer the same two.
- **V3**: the artifact-level method now puts **`replay` first**, as the per-vote method does, so **the two countings
  agree at the top**.

So this unit's headline — *which arm forgets least is a property of the counting and not of the corpus* — held on the
corpus as it stood and **does not hold now**: the artifact-level chain moved to `replay > ewc > ewc-block-rand >
ewc-block > naive` against the per-vote `replay > ewc > ewc-block > ewc-block-rand > naive`, and the disagreement is
one adjacent pair in the middle rather than the top. What stands is the *method*: a census's answer depends on
whether an artifact or a replicate is the unit of the vote, and two more runs were enough to move one of the two
chains
(`docs/findings/2026-10-01-the-reversal-in-the-other-family.md`).

## 7. RE-READ 2026-10-01 13:24 — the population moves nothing again

`e317`'s two artifacts changed the corpus once more and **`moved_by_population` is empty again**: with the filter the
population moved **no** edge, where `e315` and `e316` had it moving one (`ewc>replay`). So V1's invariance is not a
fact about the filter's innocence or otherwise; it is a fact about the corpus at the moment it is read, and three
consecutive runs have made it alternate. V2's and V3's readings are unchanged from §6 — the two countings agree at
the top and differ by one adjacent pair in the middle
(`docs/findings/2026-10-01-the-reversal-with-five-arms.md`).
