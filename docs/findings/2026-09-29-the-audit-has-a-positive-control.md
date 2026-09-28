# The audit has a positive control: a paper claim that enumerates its own population, confirmed to the last digit

*2026-09-29 02:10. Runs: **none new** — `experiments/e280_the_positive_control.py` reads
`runs/e124_barrier_12seeds.json` and checks the paper's 132-checkpoint claim against it and the artifact's own summary
against a recomputation from its own rows, writing `runs/e280_the_positive_control.json`. Seconds.*

## 1. The item: a check that only ever fires is uninterpretable

Five fires have found the paper stating things the corpus no longer supports:

| fire | what it found |
|---|---|
| `e268` | three quoted numbers a later finding had **superseded**, still in the paper with no note |
| `e270` | an **existence premise** ("no artifact on disk carries a 128-batch Fisher at all") contradicted by three artifacts |
| `e277` | **counts** over denominators that grew **2.45× and 6.44×**, one universal now covering **16%** |
| `e278` | an **extremum** over a population named only as "on disk": 262 diagonal arms against 17, its conclusion falsified by 20 counterexamples |
| `e279` | a **universal about a configuration** that is true of an **epoch** of the line: 167 artifacts now, an eighth outside the clause |

Every one of those claims was about a population its sentence **did not define** — a bare count, an "on disk", an
epoch — so a genuine staleness and a broken checker would look the same. `e97`'s own docstring makes the point for its
own audit and carries a known positive for exactly this reason. **This is that positive**, and the paper has one:

> Twelve seeds and **all 66 pairs**, 21-point chords at the **first and last checkpoints**, pre-registered before the
> run: **every one of the 132 pair-checkpoints** has a fit-task barrier below **25% of chance**, with min **0.0108**,
> median **0.0361** and max **0.1252**

**The sentence gives its enumerator**: twelve seeds, 66 pairs, the first and the last checkpoints — 132 rows.

## 2. What the check says

| the sentence | the artifact (`e124_barrier_12seeds`) |
|---|---|
| 132 pair-checkpoints | **132** rows |
| all 66 pairs | **66** distinct seed pairs |
| the first and last checkpoints | checkpoints **0 and 2** |
| min 0.0108, median 0.0361, max 0.1252 | **0.0108, 0.0361, 0.1252** — recomputed from the rows |
| every one below 25% of chance | **132 of 132**, the largest 0.1252 |

**C1, C2 and C3 all MET**, and the artifact agrees with itself: its own `distributions.fit` summary equals a
recomputation from its own `fit_tasks` rows.

## 3. What the control establishes

**The series' five failures are staleness and not a broken checker**, because the same instrument, aimed at a claim
whose sentence names its enumerator, confirms it to the last quoted digit. That is the whole reason `e97` carries its
known case, and it is worth stating what the contrast is: **a claim is checkable exactly to the extent that it names
its enumerator.** The five stale statements were not vague — each was crisp, quotable and wrong about the population it
quantified over; the control was vague about nothing and right.

## 4. What it cannot do

**It checks the claim against the artifact and the artifact against itself, not against a re-run**, so a defect shared
by the run and its own summary is invisible — the control is a consistency check and not a replication.
**`barrier_over_chance` is the field read** and the sentence's "of chance" is taken to be it rather than re-derived
from `ln 4`. The sentence's **"pre-registered before the run"** is a claim about a document rather than about the
corpus, and nothing here checks it. And **one claim establishes that the checker can pass**, not what fraction of the
paper it passes — which is the next thing the series would need and is not a claim about this artifact.
