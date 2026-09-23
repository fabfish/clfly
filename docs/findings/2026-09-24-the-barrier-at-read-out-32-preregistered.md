# `e130` pre-registered: the barrier at read-out 32, where this axis's per-repeat spread is largest

**Date:** 2026-09-24
**Status:** pre-registered **before** the run. Committed as its own commit; the run is launched after it.
**Script:** `experiments/e124_barrier_distribution.py` — unchanged except for a new **`--matching-seeds`**
extension control, which is what makes this a replication rather than a second experiment.
**Planned artifact:** `runs/e130_barrier_r32.json`, twelve seeds, 66 pairs, 21-point chords, at **read-out 32**
with `--iters 500 --test 48 --shared-head --input-overlap 0.0 --seed0 0 --circuit-size 800 --methods naive`.
**C0's comparator:** `runs/e116_r32_40reps.json` — the identical configuration at forty replicates, of which
these twelve seeds are the **first twelve** (`seed0 + 100r` in both).
**Context:** `docs/findings/2026-09-24-the-barrier-over-all-pairs.md`, whose §6 names this as the first of its
limitations: *"**One read-out, one task order, one circuit.** Read-out 32 has the largest per-repeat spread on
this axis (`e116`: sd 0.0556 against 0.0325 here) and the barrier there is untested. The drift, the
load-bearing gap and the fit depth are all monotone in the read-out, so a barrier that is a property of the
geometry **and** a monotone function of the read-out would be two claims where this fire supports one."*

## Why this is a replication and not a fresh question

`e124` established, at read-out 128, that **every one of the 132 pair-checkpoints has a fit-task barrier below
25% of the chance level** — median **0.0361**, worst **0.1252**, i.e. 11.1× below the loss of a solution that
has learned nothing. The registered thresholds are reused here **verbatim**, so a failure at read-out 32 is a
failure of a claim already in the record and not of a new one fitted to this run.

## The predictions

- **C0a, the extension control, and it is exact.** The twelve seeds' `mean_forgetting`, in seed order, must be
  **bit-identical** to the first twelve of `runs/e116_r32_40reps.json`. Every run of this benchmark uses
  `seed0 + 100r`, so a twelve-seed run *is* the first twelve of a forty-replicate one at the same configuration
  — and at read-out 128 those twelve came out bit-identical in the previous fire, so this is a check with a
  known-answer precedent rather than a hope. **Newly built into the script** (`--matching-seeds`), because a
  control that is run by hand afterwards is a control that gets skipped.
- **C0b.** The three saved checkpoints pass `e122`'s endpoint control, **6 of 6**, reconstructing the runner's
  own recorded `retention_loss` at every task.
- **P1, and it is the replication.** **Every one of the 66 pairs** has a fit-task barrier **below 25%** of the
  chance level. This is `e124`'s registered P1 at a second read-out; the same threshold, nothing loosened.
- **P2, directed, and it is what read-out 32 is *for*.** The **median** fit-task barrier as a fraction of chance
  is **higher at read-out 32 than at read-out 128** (0.0361). The reason is specific rather than generic: read-out
  32 is where the seeds differ most — per-repeat sd **0.0556** against 0.0325, a factor of 1.7 — so if the
  barrier between two solutions tracks how far apart the seeds land, this is where it should show. **Stated as a
  direction rather than a magnitude**, because the magnitude would be a new claim and the direction is the one
  this fire is entitled to test.
- **Falsifier.** **Any** pair above **50%** of the chance level. Then the connected-set claim is false at this
  read-out, `e124`'s result is a property of read-out 128 rather than of the benchmark, and multi-basin
  explanations are back on the table **for the read-out where the seeds differ most** — which would be the
  strongest form the refutation could take.

## What this cannot settle, in advance

- **Two read-outs is a line, not a curve.** If P2 holds, the barrier grows as the read-out narrows; that is
  consistent with the drift, the load-bearing gap and the fit depth all being monotone in the read-out (`e118`,
  `e121`), and it does not distinguish "the barrier is a property of the geometry" from "the barrier is a
  monotone function of the read-out" — the distinction `e124`'s own §6 says needs a third read-out. Read-out 0
  (the whole state) is the natural third and is not this fire.
- **The chords are still through checkpoints, not minimisers**, so the fit task is readable and the retained
  tasks are not.
- **21 points can miss a ridge**, so every barrier is a lower bound; that is the safe direction for P1 and the
  unsafe one for P2, since a longer tail at read-out 32 could raise its median for a reason the maximum would
  also show.
- **Twelve seeds, 66 pairs, and the pairs are heavily dependent** — each seed appears in 11 of them — so the
  median is a median over 66 dependent values and the effective `n` for anything about seeds is 12.
