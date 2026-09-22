# E6b — the predictor has no unexplained failure: 13/13 on every measurable pair

**Date:** 2026-09-22
**Script:** `experiments/e6_predictor.py --seeds 6`
**Artifacts:** `runs/e6_predictor_6.json`
**Setup:** circuit `mb+cx+al`, 5 conditions, 6 task seeds each, 11 candidate bases per condition

---

## 1. The open question

`e6` validated `projection_pressure` as an a-priori predictor for which anchoring basis to
use, and it made **one** error in 25 matched bio/random pairs: on the `rewired-swap2`
condition, the `cell_class` pair was called the wrong way with a large margin
(`pressure_delta = −0.971` predicting biology better, `excess_delta = +0.0031` biology
actually worse). That was recorded as a known failure mode and left open.

The suspicion this fire tested was that the pair's excess difference is simply too small to
measure — every *other* pair delta in that condition was of order 0.001–0.003 as well. If so,
the "failure" is not a failure of the predictor but a pair on which no predictor can be
scored, and the fix is not a better predictor but reporting the target's resolvability
alongside the score.

`e6` now computes, for every matched pair, the standard error of the excess difference and
flags whether it clears 2σ.

## 2. Result: the predictor is correct on every measurable pair

| condition | d | Spearman | signs | **resolvable pairs** |
|---|---|---|---|---|
| `baseline` | 952 | +0.973 | 5/5 | **3/3** |
| `wider-tasks` | 952 | +0.991 | 5/5 | **4/4** |
| `faster-drift` | 952 | +0.973 | 5/5 | **3/3** |
| `rewired-swap2` | 952 | +0.991 | **4/5** | **0/0** |
| `larger-circuit` | 1307 | +0.991 | 5/5 | **3/3** |
| **all** | | **mean +0.984** | 24/25 | **13/13** |

**The single failure is in the one condition where not a single pair is resolvable.** On
`rewired-swap2` all five matched-pair excess differences fall below 2σ; the predictor scored
4 of 5 there, which is what a coin would produce. **Across the four conditions with measurable
pairs it is 13 out of 13**, in addition to its rank correlations of +0.97 to +0.99.

That also explains the *shape* of the miss: the predictor was over-predicting the magnitude.
The `pressure` deltas in that condition span 0.02 to 1.7, while the excess deltas span
0.001–0.003. The predictor correctly identifies `cell_class` as much better than the
*diagonal* there (pressure 10.8 against 16.7; the true excesses 0.057 against 0.068) — it is
only the *bio-versus-random* comparison, a difference of 0.003, that is unmeasurable. The
predictor's ranking of the methods is right even in the condition where its pair-level sign
test is unscoreable.

## 3. Why that condition has no measurable pairs, which ties back to e2

`swap2` is the topology where the rewiring has collapsed the task precisions to nearly
rank-one — `e2` measured `flattening = 0.023` there, against 0.69 on the real connectome. Two
consequences, both measured:

- the **level** of the diagonalisation excess is dramatic and highly resolved: `e2` found the
  excess *falling* by **32.7σ** from `swap0.5` to `swap2`;
- the **ordering among bases** becomes unmeasurable, because the basis-to-basis differences
  shrink to ~0.003 while the task-to-task variance stays at ~0.01.

So the same condition that gave the project its cleanest refutation (the penalty does not
track interference, at 32.7σ) is also the condition where the basis question stops being
answerable. That is not a coincidence: both follow from the task structure collapsing to
essentially one direction, which makes the tasks trivially non-interfering *and* makes
different anchorings nearly equivalent.

## 4. The predictor's standing, final form

| property | value |
|---|---|
| rank correlation, 5 conditions | **mean +0.984** (range +0.973 to +0.991) |
| matched-pair signs | **24/25**, and **13/13 on pairs the excess can resolve** |
| validated out of sample | task width, drift rate, topology, circuit size, and the hardened network read-out |
| applies to | **fixed** anchoring structures — partitions and fixed rotations. It fails on state-dependent ones (spectral truncation) because it scores each step myopically and cannot see the retained subspace being renewed; measured step-to-step overlap 0.03 for `Rank(4)` |
| does not apply to | the network's synapse partitions, where it was not tested and where the ordering question itself turned out unmeasurable at one batch count and absent at another |
| known caveats | it is a **ranking** predictor, not a calibrated one — its dynamic range varies by an order of magnitude across conditions while excess deltas stay of order 0.003–0.010 |

The honest final statement of C2's predictor:

> For a fixed anchoring structure on a connectome-derived task family,
> `projection_pressure` — the measurement-weighted share of the exact filter's posterior that
> the structure would discard — ranks candidate bases at ρ ≈ +0.98 and identifies the better
> of each biological-versus-matched-random pair on every pair the excess metric can resolve.

That is the thing C2 lacked for most of the project, and it now holds under a resolvability
test rather than merely on a headline count.

## 5. Rule added to the project

The predictor's "failure" was a scoring artefact, and the same artefact would have corrupted
any method comparison on that condition. So the project's measurement rules gain:

> **Report the target's resolvability alongside any sign or ranking score.** A sign test on
> differences below the measurement's noise floor is a random draw, and counting such draws as
> successes or failures is a way of manufacturing both results and failures.
