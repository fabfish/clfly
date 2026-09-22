# E19 — the coarsest synapse rung has now been run, and the negative holds; the benchmark cannot resolve the effect it was run for

**Date:** 2026-09-22
**Script:** `experiments/e8_rate_network.py --basis side --methods naive,ewc-block,ewc-block-rand --iters 500 --repeats 3`
**Artifacts:** `runs/e10_rung_side.json` (`side` = 10 groups, constrained 0.6947, 1.72 GB)

---

## 1. What this was for

`C2b` in the plan said the network line's basis negative — *the biological synapse partition never
beats a size-matched random control* — had only ever been measured at `cell_class` (constrained
0.9250), the second-coarsest of the five annotation rungs, and that **`side` (0.6947) was the rung
the neuron result implicated and the one that had never been run.** The neuron result's best rung
*is* `side`, so if the vocabulary were the problem, `side` is where a positive result would appear.

This is that run. It is the first synapse basis comparison at any rung other than `cell_class`.

## 2. Result: no advantage, and block EWC does not help at all

| method | final accuracy | sem | mean forgetting | sem |
|---|---|---|---|---|
| naive | 0.8241 | 0.0359 | +0.1007 | 0.0486 |
| `ewc-block` (biological) | 0.8148 | 0.0346 | +0.0972 | 0.0614 |
| `ewc-block-rand` (matched control) | 0.8264 | 0.0212 | +0.0938 | 0.0276 |

Biological minus matched random: **accuracy −0.0116** (the biological partition is slightly *worse*),
forgetting **+0.0035**. And the biological block-EWC is below the *naive* baseline on accuracy
(0.8148 against 0.8241), so at this rung anchoring in the connectome's own groupings does not merely
fail to beat a random partition — it fails to beat doing nothing.

**So the rung hypothesis is not supported.** Testing the rung that the neuron result implicated did
not turn the network negative around. Whatever separates the two substrates, it is not that the
network line had been measuring the wrong granularity.

## 3. But the run cannot resolve the effect it was run for

The differences above are 0.29σ and 0.05σ against unpaired sems of 0.041 and 0.067. That is not a
measurement of zero; it is a measurement with a very wide interval:

| comparison | delta | **95% interval** |
|---|---|---|
| accuracy | −0.0116 | **−0.091 to +0.068** |
| forgetting | +0.0035 | **−0.128 to +0.135** |

On an accuracy scale where chance is 0.25 and the naive baseline reaches 0.82, a 95% interval
spanning ±0.08 says almost nothing. **The per-repeat spread is the obstacle**: the three replicate
accuracies for `ewc-block` are 0.8264, 0.7500, 0.8681 — a range of 0.12 — giving a per-repeat sd of
0.060 (and 0.037 for the control arm, pooled **0.048**; forgetting's pooled sd is **0.077**). At 3
repeats that is the sem of 0.041.

How many repeats would be needed, at those spreads (2σ, and the run cost 105.5 min for 3 repeats, so
**≈35 min per repeat**)? The per-replicate sd of a **difference** is `hypot(0.0599, 0.0367)` = 0.0702
unpaired and 0.0463 paired (the two arms correlate at r = 0.636), so the requirement scales as its
square:

| effect to detect | repeats, unpaired | **repeats, paired** | wall-clock per rung (paired) |
|---|---|---|---|
| 0.05 accuracy | 8 | **4** | ≈2.3 h |
| 0.03 accuracy | 22 | **10** | ≈5.9 h |
| **0.01 accuracy** | **198** | **86** | **≈50 h** |
| 0.03 forgetting | — | 23 | ≈13 h |
| 0.01 forgetting | — | 202 | ≈118 h |

**Pairing is worth 2.3×** (198 → 86 at 0.01 accuracy). And five rungs are queued. **The e10 ladder as
configured cannot settle C2b.** It can bound the advantage — "no effect larger than about 0.09
accuracy at `side`", the edge of the interval above — and it does, but the interesting range for a
continual-learning claim is 0.01, which is two orders of magnitude of compute away.

> **Correction.** An earlier version of this table used 0.0483 — the *mean* of the two arms' sds —
> and reported 94 repeats. That is not a valid pooled sd for a difference of means, and the correct
> figures are 198 unpaired and 86 paired. The conclusion is unchanged; the recommendation is not, since
> pairing turns out to be the larger of the two available levers
> (`docs/findings/2026-09-22-evaluation-noise.md` §7).

## 4. Pairing helps, by 1.5×, and the benchmark does not use it

`ewc-block` and `ewc-block-rand` share the seed sequence, so their replicates are pairable and the
per-repeat difference is a matched observation:

| comparison | unpaired sem | **paired sem** | improvement |
|---|---|---|---|
| accuracy | 0.0406 | **0.0267** | 1.5× |
| forgetting | 0.0673 | **0.0409** | 1.6× |

Per-repeat accuracy deltas are +0.0278, −0.0625, −0.0000 — mixed in sign and large, which is exactly
what a dominantly run-to-run variance looks like. The paired figure is still 0.43σ.

This is the same lesson as the neuron ladder (`2026-09-22-shape-needs-paired-contrasts.md`), in a
second substrate and arrived at independently: **the bio-versus-control comparison is paired by
construction and is being reported unpaired.** The rate-network JSON stores `replicates`, so the
paired figure is computable after the fact; the printed summary does not show it. It should.

## 5. What C2b now says

The plan's framing — *"the rung the neuron result implicates is untested"* — is superseded:

> At `side`, the coarsest of the five synapse rungs, the biological partition shows no advantage
> over its size-matched random control (−0.0116 accuracy, 0.43σ paired) and does not beat the naive
> baseline. The negative therefore is not an artefact of having tested the wrong granularity. But
> this run bounds the advantage only at ≈0.09 accuracy: the benchmark's own run-to-run sd (0.048
> per repeat) puts effects in the range a CL claim would care about at 90–240 repeats, i.e. 55–140
> hours per rung. **Settling C2b is a benchmark-variance problem, not a rung problem.**

That is the same shape as the frozen-body lesson — a benchmark obstacle that is not about the
science question being asked — and it is worth stating in those terms because the next move is to
reduce the variance, not to run more rungs.

## 6. Limits

- **One rung of five**, 3 repeats, one circuit, one annotation column, `--iters 500`, λ = 1.0 with
  the Fisher normalised. The other four rungs are queued.
- The 95% intervals assume the replicates are exchangeable, which 3 points cannot check.
- The paired improvement is computed from 3 pairs, so the paired sem itself carries ~50% relative
  error — the *direction* of the improvement (pairing helps) is robust, the factor is not.
- "Block EWC does not beat naive" is a statement about this configuration. The earlier network work
  found the same thing at `cell_class`, and it also found the diagonal Fisher *hurts* as its
  estimate improves, so the two are consistent rather than independent.
- No claim is made here about whether a variance reduction (more classes per task, more tasks,
  longer training, averaging decoders) would recover the power; that is the next experiment, not
  this one.
