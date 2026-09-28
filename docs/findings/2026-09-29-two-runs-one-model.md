# Two runs, one model: the suite moved, the trained models did not, and the replicate spread is the sample's

*2026-09-29 00:18. Runs: **none new** — `experiments/e285_two_runs_one_model.py` reads the two artifacts `e275` left
behind, writing `runs/e285_two_runs_one_model.json`. Seconds.*

## 1. The question `e275`'s read left open

`e275`'s read established that the two runs trained the same models: its registered control named a held-out column,
and the column that is actually on the training set (`losses`) is identical at 5 of 5 arms. But the two artifacts'
configs differ in exactly **one** substantive flag — `test`, 48 to 200 — so if the training is identical, then **the
same forty models were evaluated on two different held-out samples**. Nobody read that off the pair. It makes them a
*sample-swap experiment*, at zero training cost, and this unit is its instrument.

## 2. The reading

**W1 MET — one configuration at two suites.** `['json_out', 'test']` are the only config keys that differ, so the
manipulation is the suite and nothing else.

**W2 MET — and the fields that moved are exactly the held-out ones.** Every per-replicate field the artifact carries
is declared here as computed on the held-out sample or not, and the declaration is checked cell by cell over the
**200** arm-by-replicate rows:

| computed on the held-out sample | cells that moved | not on the held-out sample | cells identical |
|---|---|---|---|
| `final_accuracy` | 200 of 200 | `theta_drift` | 200 of 200 |
| `final_per_task` | 200 of 200 | `bias_norms` | 200 of 200 |
| `forgetting_per_task` | 200 of 200 | `retention_loss` | 200 of 200 |
| `learned` | 200 of 200 | `interference` | 200 of 200 |
| `mean_forgetting` | 200 of 200 | `losses` | 200 of 200 |
| `retention` | 200 of 200 | `full_train_loss` | 200 of 200 |
| | | `method` | 200 of 200 |

**1,200 cells moved and 1,400 are identical, with no exception in either direction and no field left unclassified.**
The partition of the artifact's fields is the partition by *what data they are computed on*, exactly. And because
`theta_drift`, `bias_norms`, `retention_loss`, `interference`, `losses` and `full_train_loss` are all functions of the
trained parameters, the pair is the same forty models under two evaluations.

**W3 MET — the replicate spread falls, ten times out of ten.** With those same models:

| arm / metric | sd at 144 | sd at 600 | ratio | `1/sqrt(n)` predicts |
|---|---|---|---|---|
| `replay` / final_accuracy | 0.0168 | 0.0072 | **0.428** | 0.490 |
| `ewc-block-rand` / mean_forgetting | 0.0219 | 0.0104 | 0.476 | 0.490 |
| `ewc` / final_accuracy | 0.0226 | 0.0117 | 0.518 | 0.490 |
| `ewc-block-rand` / final_accuracy | 0.0196 | 0.0104 | 0.528 | 0.490 |
| `ewc-block` / final_accuracy | 0.0181 | 0.0097 | 0.533 | 0.490 |
| `replay` / mean_forgetting | 0.0200 | 0.0110 | 0.552 | 0.490 |
| `ewc` / mean_forgetting | 0.0181 | 0.0109 | 0.599 | 0.490 |
| `ewc-block` / mean_forgetting | 0.0209 | 0.0128 | 0.613 | 0.490 |
| `naive` / final_accuracy | 0.0147 | 0.0105 | 0.718 | 0.490 |
| `naive` / mean_forgetting | 0.0207 | 0.0165 | 0.800 | 0.490 |

Ten of ten, so **p = 2^-10 = 0.00098** under a sign null. In variance terms the 144-item measure is **1.56x to 5.46x**
the 600-item one. The candidate accounts are printed beside the observation and this unit does not choose between
them: a per-model sampling deviation whose spread goes as `1/sqrt(n_eval)` predicts `0.490` for every comparison and
the observed ratios straddle it (four of the five `final_accuracy` ratios sit in 0.43 to 0.53), while the account
built on the accuracies' move toward the ceiling predicts the *ratio of* `p(1-p)`, which for `mean_forgetting` is
**above 1** — that is, it predicts the spread should have *risen* where it fell — so that account fails on the one
metric where it makes a signed prediction.

## 3. What it does to everything else in the corpus

Every sigma this project prints is a difference divided by a spread, and `e267`'s "floor" is the same quantity read
from the other side — a *numerator* floor compared against a spread. This unit measures the spread's own dependence on
the evaluation sample, with the models held fixed, which neither `e267` nor `e275` could do:

- **The spread is not a property of the models alone.** An arm's error bar at 48 items per task is 1.25x to 2.34x the
  same arm's error bar at 200 items per task, on the same weights.
- **The direction is friendly to the corpus's older numbers.** A larger spread makes a σ smaller, so sigma values
  computed on the 48-item suites are *conservative* in this direction rather than optimistic — the correction would
  make old effects stronger, not weaker. This unit does not recompute any of them, and the paired-difference sem that
  most of the paper's sigmas use is a *different* variance over the same replicates and is not measured here.
- **And it is the same phenomenon as `e267`**, read from the other end: `e267` said the test set's floor can be larger
  than the spread; here the spread itself shrinks as the floor does, and a suite large enough to make the floor
  negligible also makes the spread it is compared against smaller.

## 4. What it cannot do

**The models' identity is inferred and not exhibited.** Neither artifact stores its parameters, so "the same forty
models" rests on every parameter-derived field they do carry being byte-identical — six of them, 1,200 cells — together
with the same seeds, support draw, readout draw and matched-random partition. That is strong evidence and it is not a
saved `theta`. **The two runs are four days apart**, so a runner change between them would appear as a training field
moving, which is W2's falsifier; nothing here says which code revision trained the older artifact, whose
`code_revision` is null. **Two samples and one configuration**: W3 is a sign result over ten comparisons, so it
establishes the direction and the size on these two samples and not the rate at which a spread falls with the suite.
**The mechanism is not separated** — the three candidate accounts are reported side by side, and one of them makes a
signed prediction this data contradicts. **The metrics are aggregates over the tasks**, so what falls is the spread of
a mean over three tasks and not of a single task's accuracy. And **nothing here re-measures any published σ**; the
consequence in section 3 is the direction of a correction, computed nowhere.
