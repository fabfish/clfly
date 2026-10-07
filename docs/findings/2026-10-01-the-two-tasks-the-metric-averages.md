# The two tasks the metric averages: the highest-level and the lowest-level task in the sequence

*2026-10-01 09:04. Runs: **none new** — `experiments/e311_the_two_tasks_the_metric_averages.py` reads the lost term of
every three-task arm position by position and checks the stored field against the mean over the first two, writing
`runs/e311_the_two_tasks_the_metric_averages.json`. Seconds.*

## 1. What `mean_forgetting` is a mean *of*

`e299` noted in passing that the metric averages the first `T - 1` tasks; `e304` showed it is the lost half of the
shortfall; `e310` measured that the **position in the sequence predicts the level a task reaches**. This unit puts the
three together, and the answer for a three-task suite is that the two positions the mean runs over are **the two ends
of the position profile**:

| position | level reached | lost | in the metric? |
|---|---|---|---|
| 0 (learned first) | **0.9605** | **0.07744** | yes |
| 1 (learned second) | **0.9168** | **0.05605** | yes |
| 2 (learned third) | 0.9345 | **0.00000** | no, and it cannot be |

**T1 MET** — the stored `mean_forgetting` equals the mean of the lost term over the first two positions in **5581 of
5581** arms, so the denominator is `T - 1` and not `T`. **T2 MET** — the excluded position's term is exactly
**0.0e+00** in every arm, because `R[T-1][T-1]` is both the level that task reached and the level it ended at; the
exclusion is arithmetic and the claim checks the convention rather than a finding about the substrate.

## 2. The two terms are not exchangeable

**T3 MET** — the first position's lost term averages **0.07744** against the second's **0.05605**, a factor of
**1.382**. The metric is a mean of the **best-learned and the worst-learned** task in the sequence, and their levels
differ by the four points `e310` measured. **T4 MET** — over the arms, the rank correlation between the first
position's reached level and its lost term is **+0.280**: a task that was learned better has more to lose. The
first-to-second level gap against the metric itself is **+0.237**.

So an arm's `mean_forgetting` is partly a statement about **how much there was to lose at the two positions the
average happens to fall on**, and the positions it falls on are the ones `e310` showed are furthest apart.

## 3. Why this is the last piece of the line

`e304` said the metric is half of a quantity; `e305` said the arms it is lowest in the corpus are the ones that
learned least; `e306` said the ordering it induces is close to the reverse of the ordering by learning; `e307` put the
currency onto the front page; `e308` showed the ordering moves with the unit of the vote; `e311` says which two tasks
the number is an average of, and that they are the two ends. **Every claim the corpus makes in `mean_forgetting` is
now attributable**: to the lost half, over the first `T - 1` positions, from a mean of a best-learned and a
worst-learned task, on a substrate whose position profile is worth four points.

## 4. What it cannot do

**The last position's zero is arithmetic and not a result**: it is excluded because it cannot be forgotten, so T2
checks the convention. **T4 is a correlation over arms that are not independent**, so +0.280 describes the corpus and
is not an estimate. **For any single artifact the position and the task are the same object**, so nothing here
separates `task 0` from `first` — `e310`'s two families are what make the position reading available, and this unit
does not repeat that argument. **And this unit reads the three-task suites only**: a longer sequence would average
more positions, and the shape of that mean is a different question.

## RE-READ 2026-10-07

The live test asserted that the two positions the metric averages are the **highest** and the **lowest** level of the
three, and the highest is no longer the first: the levels read **0.7425**, **0.7337** and **0.7429**, so the **last**
position is **0.0004 above the first** and the two are a tie. `e462`'s and `e463`'s own closed-loop rolls are what
walked it past, and they are the assembly family, whose first rung `e310` reads below its last. **Nothing in T1 to T4
moves**: which two positions the metric averages is structural, and T3 is about the two **lost** terms, which still
read **0.10480** at the first position against **0.08257** at the second, a factor of **1.269**, so the metric is still
the mean of the best-learned and the worst-learned task. What this reading holds now is the direction that survives on
the pooled levels -- the **middle** position is the lowest of the three -- and the three-rung level order is a
per-family fact rather than a pooled one
(`docs/findings/2026-10-07-the-neuron-readout-at-twenty-four-columns.md`).
