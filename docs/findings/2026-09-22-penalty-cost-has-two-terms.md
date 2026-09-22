# E44 — the synapse ladder's cost has **two** terms with opposite granularity dependence, and the plan reasons about only one

**Date:** 2026-09-22
**Script:** `experiments/e44_penalty_cost_scaling.py`
**Artifacts:** `runs/e44_penalty_cost_scaling.json`
**Context:** plan §C2b (*"what bounds the coarse end is time, not memory"*), `2026-09-22-penalty-bound-once.md`, `2026-09-22-e35*`

---

## 1. Why this was worth measuring

The `e10` ladder has spent the last six hours on one rung. `supertype` had consumed **3.5 CPU-hours**
when its log was last inspected, having finished two of its three arms — against
`ito_lee_hemilineage`'s 46 minutes for all three. I checked it was not stuck (12,571 CPU-seconds over
165 wall-minutes, so ~2.1 cores continuously), then looked at what it is actually doing.

`SynapsePartition.make_penalty` builds the penalty by **looping in Python over every group**, doing
one small torch matvec per group:

```python
def penalty(theta_now):
    total = torch.zeros(...)
    for blk, idx, a_g in zip(blocks_t, idxs, anchors):
        d = theta_now[idx] - a_g
        total = total + d @ (blk @ d)
    return 0.5 * lam * total
```

So there are two cost terms: a **per-group dispatch** (Python + torch overhead, independent of block
size) and a **per-group matvec** (the dense `s x s` product, i.e. the footprint `sum_g s_g^2`). The
plan's C2b section reasons about the footprint alone — *"block-Fisher accumulation cost also scales
with `sum_g s_g^2`, so a coarse rung takes minutes per run rather than seconds"* — which is right
where it was aimed (the coarse end) and silent about the term that governs the fine end.

## 2. Measured, with the two terms fitted

Synthetic partitions over the real theta dimension (26,568 weights), one thread, 40 timed calls after
a warm-up, at the ladder's five real group counts:

| rung | G | footprint `sum_g s_g^2` | loop µs/step | µs per group | regime |
|---|---|---|---|---|---|
| `side` | 10 | 70,585,864 | 53,649 | 5,365 | **footprint** |
| `cell_class` | 100 | 7,058,608 | 9,274 | 93 | **footprint** |
| `ito_lee_hemilineage` | 2,148 | 329,112 | 66,494 | 31 | dispatch |
| `supertype` | 9,938 | 73,212 | 323,971 | **33** | dispatch |
| `cell_type` | 19,618 | 40,468 | 533,582 | 27 | dispatch |

**Two-term fit: `cost(µs) = 28.3 x G + 7.58e-4 x sum_g s_g^2`, max relative residual 13%.** A pure
`G^a` fit gives `a = 0.337`, which is not a law at all — its log-residual is 1.52, i.e. it mispredicts
by a factor of ~4.6. The reason is visible in the per-group column: the *coarse* rungs cost **more per
group** than the fine ones, because their blocks are enormous (`side`'s ten groups average 2,657
weights each, so one block is 7 million entries).

A repeat of the same benchmark, on the same machine under the same load, moved the coefficients to
**32.9 µs/group** and a crossover at `sum_g s_g^2 / 43,845` (max residual 20%). The coefficients are
load-dependent to about a factor of 1.5; the **regime assignment below was identical in both runs**,
and that is the load-bearing part.

The terms cross at **G ≈ `sum_g s_g^2` / 37,347**, which puts `side` and `cell_class` on the footprint
side and the three fine rungs on the dispatch side. So:

> **the two orderings are opposite**, and the plan's conclusion that "the affordable rungs are
> precisely the uninformative ones" is true only for storage and accumulation. For *evaluation* — the
> part run 500 times per task — the fine rungs are the most expensive, and `supertype`'s 9,938 groups
> are 9,938 Python-level dispatches per step.

This is the same shape as the frozen-body and unset-λ traps: a cost model that was correct for the
thing it was derived on, applied one step outside its range.

## 3. The fix, measured, and its regime of validity

The obvious fix is to bind every block **once** into a single block-diagonal sparse matrix and replace
the per-step loop with one sparse matvec — the per-group index work moves into the one-off bind, which
`make_penalty` already pays for its torch conversion of every block.

| rung | G | bind ms | sparse µs/step | speedup | relative disagreement |
|---|---|---|---|---|---|
| `side` | 10 | 4,006 | 166,845 | **0.3x — HURTS** | 2.4e-15 |
| `cell_class` | 100 | 587 | 14,894 | **0.6x — HURTS** | 1.6e-16 |
| `ito_lee_hemilineage` | 2,148 | 66 | 1,313 | **50.7x** | 1.5e-15 |
| `supertype` | 9,938 | 198 | 908 | **356.6x** | 2.4e-15 |
| `cell_type` | 19,618 | 246 | 599 | **891.1x** | 2.8e-15 |

Two things worth stating plainly, both of which the first version of this measurement got wrong:

- **It hurts the coarse end**, by 1.7–3×, because a block-diagonal sparse matvec has to touch the
  whole footprint while ten dense small matvecs do not. A single route is not the answer; the correct
  form is a hybrid keyed on the crossover in §2.
- **The numerical disagreement is real but tiny** — max 2.8e-15 relative — and it is *not* zero. My
  first run reported exactly 0.00e+00 because it used `theta = anchor = 0`, which makes both routes
  return zero and the check vacuous. The non-zero version is what is reported above, and the
  difference is pure floating-point reordering.

**It is not adopted.** `make_penalty`'s docstring promises bit-agreement with `penalty_tensor`
("the same `d @ (blk @ d)` per group, in the same order, at the same dtype, so a run that used
`penalty_tensor` per step and one that uses this agree to the bit"), and 2.8e-15 is not the bit. The
measurement is the deliverable here; swapping the route is a decision for whoever owns that contract,
and it should be made by adding an explicitly-named opt-in rather than by changing the default.

## 4. What this does not change, and the cheapest correct action

The fine rungs are still the uninformative ones — `e35`'s arithmetic bound
(`constrained <= 1 - 1/m`) says a column with 9,938 groups is near the diagonal by construction, and
`supertype`'s measured `constrained` is 0.9988. So the two facts point the same way:

> **do not run `supertype` and `cell_type` at all.** They are the most expensive rungs *and* the ones
> whose answer is fixed in advance. The five-rung ladder was a reasonable design before either fact
> was known; with both known, `side` (0.6947), `cell_class` (0.9250) and `ito_lee_hemilineage`
> (0.9945) are the rungs that can carry a claim, and the queue should stop there.

That is what the `e10` job should have been, and it is why six hours went into a rung whose result
cannot differ from the diagonal.

## 5. Limits

- **Absolute numbers are load-dependent.** This ran while five jobs shared a 20-core machine, and a
  repeat moved the coarse rungs by ~30% (`side` 79.0 → 53.6 ms/step). The ordering, the crossover and
  the two-term structure were stable across repeats; the coefficients are good to about a factor 1.5,
  and the quoted 28.3 µs/group could easily be 20 or 45.
- **Synthetic equal-size groups.** The real partitions have skewed group sizes (median 1 at the fine
  end), so the real dispatch cost per group is lower than the benchmark's — which makes §2's
  conclusion conservative, not optimistic.
- **One thread.** The real runs use torch's default threading, and for very small ops extra threads
  add overhead rather than removing it, so the real per-step cost may be higher than measured.
- **The `bind ms` column is a one-off cost**, and it is large for the coarse rungs (4.0 s at `side`)
  because assembling the index arrays for a 70-million-entry sparse matrix is itself expensive. Over
  1,500 steps that is irrelevant; over a few steps it is not.
