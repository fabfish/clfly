# The benchmark's own metric: the six worlds are nearly indistinguishable on retention, and the reading this line measures does not track it

*2026-10-04. `experiments/e410_the_benchmarks_own_metric.py` reads the retention that the six worlds' five-hundred-update
runs already carry -- the retention matrix, the per-task final accuracies and the per-task forgetting of the `naive`
arm over twenty replicates -- beside the far-point task-0 **world reading** `e396` gave each world. No training, no
probe. Five claims, registered before any retention matrix was read.*

## 1. What the benchmark scores, and what this line has been measuring

| world | task-0 world reading | learned (3 tasks) | final (3 tasks) | forgetting (3 tasks) | mean forgetting | final accuracy |
|---|---|---|---|---|---|---|
| **3** | 0.5240 | 0.798, 0.801, 0.824 | 0.354, 0.472, 0.824 | 0.444, 0.329, 0.000 | 0.3865 | **0.5500** |
| **1** | 0.5062 | 0.677, 0.764, 0.854 | 0.325, 0.465, 0.854 | 0.352, 0.299, 0.000 | 0.3255 | 0.5479 |
| **14** | 0.5396 | 0.742, 0.839, 0.827 | 0.340, 0.464, 0.827 | 0.402, 0.375, 0.000 | 0.3885 | 0.5434 |
| **9** | 0.4625 | 0.747, 0.849, 0.811 | 0.350, 0.435, 0.811 | 0.397, 0.414, 0.000 | 0.4052 | 0.5323 |
| **6** | 0.4792 | 0.706, 0.798, 0.873 | 0.275, 0.417, 0.873 | 0.431, 0.381, 0.000 | 0.4063 | 0.5215 |
| **the card's** | **0.7729** | 0.743, 0.760, 0.804 | 0.324, 0.429, 0.804 | 0.419, 0.331, 0.000 | 0.3750 | **0.5191** |

The worlds are ordered by their final accuracy, best first. **The card's world has the highest task-0 world reading of
the six and the lowest final accuracy of the six.**

| claim | measured | verdict |
|---|---|---|
| AO1 the matrices are carried | six worlds, **20** replicates and **20** matrices each | **MET** |
| AO2 the last task is kept by every world | forgetting at task 3 is **0.0000** on all six | **MET** |
| AO3 the first task is lost by every world | **0.3521** to **0.4438** | **MET** |
| AO4 the card's world is not the benchmark's best | it is **last** of six | **MET** |
| AO5 the world's reading does not track the retention | rank correlation **−0.086** | **MET** |

## 2. What the two quantities are

**The benchmark's two ends are constant across the draws and its middle is nearly so.** Every world keeps the last
task exactly (forgetting **0.0000**) and loses the first by **0.35 to 0.44**, and the final accuracy -- the mean over
the three tasks -- spans only **0.0309** across the six, from 0.5191 to 0.5500. So on the corpus's own
continual-learning metric six different worlds are one population.

**And the quantity thirteen units have measured spans ten times as much and tracks none of it.** The world's task-0
reading spans **0.3104** across the same six draws where the final accuracy spans **0.0309**, and the rank correlation
between them is **−0.086**: the world whose probe reads the task best at the far point is the world whose final
accuracy over the three tasks is worst. What a linear probe recovers from the world's eight numbers is therefore a
**diagnostic** of the draw, and not the benchmark's score -- which is the sentence the whole redraw series has been
missing.

**And the card's world is the clearest instance of it.** Its world holds task 0 at 0.7729 where the five others hold
0.4625 to 0.5396, and its head finishes the three-task sequence at 0.5191, below every one of them. The world keeps
the cue and the agent does not: the two quantities are measuring different things, and the line's own instrument is
the one that moves.

## 3. What it cannot settle

- **One arm and one rate**: the 3e-3 `naive` bodies only. The `replay` arm's own retention is in the same artifacts
  and is not read here, and the `replay`-over-penalty contrast is what `e276` measured elsewhere.
- **And the metric is the corpus's**: `mean_forgetting` is the retention matrix's diagonal minus its last row, which
  `e305` showed cannot see the part an arm never learned -- so "retention" here is the corpus's decomposition and not
  a mechanism, and the card's world's low final accuracy could be a head that did not fit rather than a world that
  let go.
- **Six worlds are six**: the four engine redraws are not in the set.
- *And a probe is not a mechanism.*
