# The third arm names the source: what the pairing shares is the penalty's, not the task's

*2026-09-28 18:00. Runs: **none new** — `experiments/e264_the_third_arm.py` reads the corpus's three runs that carry
`naive` beside both EWC arms with an `evaluation_noise` block (`e60`, `e46`, `e178`), writing
`runs/e264_the_third_arm.json`. Seconds.*

## 1. The item: `e263` found the shared component and could not name it

`e263` measured that the two arms of the network line's central contrast share much more of their run-to-run variance
than the benchmark's own noise decomposition can explain, and that on the forgetting metric the shared *training*
component is the larger half of the pairing's benefit. But the two arms differ only in their basis — the task, the data
order, the initialisation and the test set are common to both — so the correlation alone cannot say whether what the
pairing exploits is **the task** or **the penalty's machinery**.

**Every run of this contrast trained a third arm, and it is the control that separates them.** The `naive` arm shares
the task, the data order, the initialisation and the test set with both EWC arms, and shares neither the Fisher nor the
penalty. So a task-level shared component would lift all three pairwise correlations together, while a penalty-level
one lifts the EWC pair and leaves the naive arm apart. `e263`'s item ceiling is reused as the reference: each pair's
**excess** is its correlation minus the most a perfectly shared test set could give it, so a positive excess is a
lower bound on that pair's shared-training correlation.

## 2. The matrices

| run | n | `ewc-block` against `ewc-block-rand` | `naive` against `ewc-block` | `naive` against `ewc-block-rand` |
|---|---|---|---|---|
| `e178` side, accuracy | 144 | **+0.317** (excess +0.085) | +0.118 (−0.125) | +0.140 (−0.100) |
| `e178` side, forgetting | 144 | **+0.282** (excess **+0.175**) | +0.122 (+0.007) | +0.124 (+0.013) |
| `e46` cell_class, accuracy | 16 | +0.321 (−0.024) | +0.303 (−0.078) | +0.298 (−0.199) |
| `e46` cell_class, forgetting | 16 | +0.354 (+0.177) | +0.189 (+0.029) | **+0.483** (+0.244) |
| `e60` side, accuracy | 16 | **+0.542** (+0.168) | −0.026 (−0.454) | +0.319 (−0.159) |
| `e60` side, forgetting | 16 | +0.504 (+0.328) | +0.274 (+0.100) | **+0.605** (+0.388) |

The artifact's own `matched_pair.corr` agrees with the matrix's EWC cell in all six, so the new instrument is reading
the same quantity the register already quotes.

## 3. The registered claims (T1-T3, all MET)

| claim | what it says | measured |
|---|---|---|
| **T1** | the naive arm separates the two candidates on accuracy | the EWC pair's excess is positive in **two of three** runs (+0.168, +0.085) and **neither** naive pair's is positive in any (they run −0.078 to −0.454) |
| **T2** | and the largest budget says it twice as loudly | at 144 replicates the EWC pair leads both naive pairs on both metrics: 0.317 against 0.118 and 0.140 (2.70×, 2.26×), 0.282 against 0.122 and 0.124 (2.31×, 2.28×) |
| **T3** | so the shared component is not the task | on forgetting the EWC excess is **+0.175 against +0.007 and +0.013** (25× and 13×), while the two naive pairs sit **0.002** apart on forgetting and 0.023 apart on accuracy |

**T3 is the answer, and the third arm is what makes it an answer rather than a guess.** All three arms share the task,
the order and the initialisation; the two EWC arms additionally share the Fisher and the penalty. At the corpus's
largest budget the naive arm is **as close to the random-basis arm as to the biological one** (0.122 against 0.124 on
forgetting, 0.118 against 0.140 on accuracy) while both sit far below the EWC pair. So the excess `e263` measured is
attached to what the two EWC arms share and the naive arm does not: **the penalty and the Fisher, not the seed
sequence.**

## 4. The negative result beside it: the sixteen-replicate ordering is a draw

The small runs do not support the relation, and their disagreement is part of the finding. On **forgetting**, both
sixteen-replicate matrices put `naive` against the *random* basis highest (0.605 and 0.483, above the EWC pair's 0.504
and 0.354), and the 144-replicate run does not: there the same pair is the *lowest* of the three on accuracy and
level with `naive` against `ewc-block` on forgetting. Two of the four small matrices therefore choose a different
winner from the one the best-powered matrix does, on the same three arms and the same metric — a caution about every
three-way comparison in this register made at sixteen replicates, and the reason T2 and T3 are stated at the largest
budget of each metric rather than pooled over the six.

## 5. What it cannot do

The excess is a **bound and not an estimate**: a positive item covariance would lower it, and nothing here measures
that covariance directly, so "the EWC pair's excess is +0.175" reads as "at least +0.175". The naive arm is not a
*penalty* control in the strict sense — it also has no Fisher — so "the penalty's machinery" is the reading of what
the two EWC arms share and not a decomposition of which part of it does the work. The small-run ordering is a draw
(§4), so nothing about T1's two-of-three is a stable property of the corpus. And only the three artifacts that carry
`naive` beside both EWC arms with an `evaluation_noise` block can be read this way; a run missing the third arm is
silent rather than neutral.
