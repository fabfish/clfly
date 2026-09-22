# E3b — the granularity ladder: the annotation vocabulary was hiding most of biology's contribution

**Date:** 2026-09-22
**Script:** `experiments/e3_basis_selection.py --ladder`
**Artifacts:** `runs/e3_ladder.json`
**Setup:** circuit `mb+cx+al@n1307`, 3 tasks, 12 seeds, analytic effect size, oracle error 0.05195

---

## 1. Why a ladder instead of rungs

The annotation vocabulary supplies five discrete rungs, and they are badly distributed:

| rung | constrained_fraction |
|---|---|
| `side` | 0.501 |
| `cell_class` | 0.828 |
| `ito_lee_hemilineage` | 0.967 |
| `supertype` | 0.974 |
| `cell_type` | 0.979 |

Four of the five sit in the top 15% of the granularity range, and there is a wide empty
interval between 0.50 and 0.83. Any statement of the form "the biological advantage is X"
was therefore a statement about where the vocabulary happens to put its rungs, not about what
the annotation structure can support.

`--ladder` replaces the five rungs with a **granularity curve**: the cell-type partition with
groups smaller than ``N`` merged into one shared group, for ``N`` ∈ {1, 2, 4, 8, 16, 32, 64,
128}, each with its own group-size-matched random control. That traces the interval
continuously — the same device the rate-network work uses to reach mid-granularity partitions
the vocabulary does not provide.

## 2. Result: 7 of 8 rungs resolve, up to 42σ, and the ladder's own best rung is beaten

| pooling | constrained | biological excess | matched-random excess | **delta** | **σ** |
|---|---|---|---|---|---|
| `pool1` (= plain `cell_type`) | 0.979 | +0.01743 | +0.01723 | +0.00019 | 0.4 |
| `pool2` | 0.674 | +0.00496 | +0.01296 | −0.00801 | **24.8** |
| `pool4` | 0.540 | **+0.00156** | +0.01041 | **−0.00884** | **42.2** |
| `pool8` | 0.450 | +0.00137 | +0.00822 | −0.00685 | 30.1 |
| `pool16` | 0.432 | +0.00133 | +0.00898 | −0.00765 | 39.1 |
| `pool32` | 0.322 | +0.00115 | +0.00814 | −0.00699 | 37.9 |
| `pool64` | 0.322 | +0.00115 | +0.00664 | −0.00548 | 20.9 |
| `pool128` | 0.191 | +0.00079 | +0.00488 | −0.00409 | 17.8 |
| *(reference)* `diagonal(EWC)` | 0.999 | +0.01749 | — | — | — |

**Seven of the eight rungs resolve**, at 17.8σ to **42.2σ** — an order of magnitude more
decisive than anything the five-rung ladder produced (its best was `side` at 28.8σ, delta
0.0048).

Four things follow, and the third changes the project's own headline.

**Merging only the singleton cell types recovers most of the available gain.** `pool2` — the
partition obtained by merging every cell type that has ≤1 neuron in this circuit into one
group — cuts the excess from +0.01743 to +0.00496, a **72% reduction**, and already beats its
matched random control at 24.8σ. The finest rung of the annotation ladder, which showed
nothing (0.4σ) and which earlier fires reported as "`cell_type` buys nothing", is the *worst*
rung in the ladder.

**The advantage is flat-topped, not sharply peaked, and the coarse claim stands while the
fine one does not.** Every rung's delta is resolved from zero, most of them at 18σ–42σ — but
"resolved from zero at 42.2σ" is not the same statement as "the peak is distinguishable from
its neighbours", and the ladder's shape claim needs the second. Contrasting *deltas* between
adjacent rungs (each delta's sem combined in quadrature):

| contrast | Δ of deltas | σ |
|---|---|---|
| `pool1 − pool2` | +0.00820 | **13.6** |
| `pool2 − pool4` | +0.00084 | 2.2 |
| `pool4 − pool8` | −0.00199 | **6.4** |
| `pool8 − pool16` | +0.00080 | 2.7 |
| `pool16 − pool32` | −0.00067 | 2.5 |
| `pool32 − pool64` | −0.00150 | **4.7** |
| `pool64 − pool128` | −0.00139 | **4.0** |

So what resolves is that the **fine end collapses** (`pool1 − pool2` is 13.6σ — `cell_type`
really is the worst rung) and that the **coarse end declines** from `pool32` on. What does
*not* resolve is a peak at a particular rung: `pool2`, `pool4`, `pool8`, `pool16` and
`pool32` all sit between 0.0069 and 0.0088, and the largest adjacent contrast inside that
plateau is `pool4 − pool8` at 6.4σ, with `pool2 − pool4` at only 2.2σ. **The defensible shape
is a plateau spanning roughly 0.32–0.67 constrained, falling off at both ends** — not an
optimum at 0.540.

Two things bound that reading, in opposite directions. The deltas are *paired* — every basis
in the run sees the same task geometries in the same seed order — so the sem of a delta
computed unpaired, as here, is **conservative** whenever the two excesses are positively
correlated across seeds, which they are (both are dominated by the task-geometry draw). The
plateau may therefore be sharper than 2.2σ suggests. But this run did not store per-seed
values, so the paired test could not be computed from it; `clfly/bench/analytic.py` now
records `excess_per_seed` so that it can be, and a re-run is in flight. Until that lands, the
plateau is what the artifact supports.

**And the ladder's best rung is beaten at its own granularity.** `side` sits at constrained
0.501 with excess +0.00391; `pool4` sits at 0.540 with excess **+0.00156** — a **2.5×** smaller
penalty at essentially the same granularity, and the matched random control at that
granularity is +0.01041, i.e. *worse* than `side`. So at matched capacity a pooled cell-type
partition beats both the annotation ladder's best rung and a random partition of the same
size.

**This corrects the project's headline from "granularity beats biology".** That reading came
from the five-rung ladder, where the biological deltas were 0.0015–0.0048 and the granularity
trend was the more visible effect. On the ladder the biological deltas are **0.0041–0.0088** —
larger than any annotation rung's — and they *increase* with the granularity sweep up to 42σ.
The honest form is: **granularity sets where you are on the curve, and biology's contribution
is what the curve's height shows — which the annotation vocabulary under-reported by placing
four of its five rungs in the region where biology contributes almost nothing.**

## 3. The predictor handles the ladder

`projection_pressure` ranks the 17 partition bases at Spearman **+0.995**, and it tracks the
biological/random distinction across the whole sweep — `bio:pool8` pressure 0.0004 against
`rand:pool8` 0.125, and the ordering within the pooled family matches the measured excesses.

That matters because the ladder is a harder test than the five rungs: it contains eight
partitions of similar granularity distinguished only by *which* groups were merged. A
predictor that merely recovered `constrained_fraction` would give them all nearly the same
pressure, since matching was enforced on group sizes. It separates them.

## 4. Consequences

| statement | before | after |
|---|---|---|
| biological advantage, best rung | `side`, 0.0048, 28.8σ | `pool4`, 0.0088, **42.2σ** |
| best biological basis found | `side`, excess 0.00391 | `pool4`, excess **0.00156** (2.5× smaller) |
| number of resolved rungs | 4 of 5 | **7 of 8** |
| shape | "advantage decreases with granularity" | **flat-topped plateau over ~0.32–0.67, falling off at both ends** (the peak rung is only 2.2σ above its neighbour) |
| headline | granularity beats biology | **granularity locates you; biology sets the height** |

The practical recommendation also changes. It was "anchor in the coarsest available grouping";
it is now **"pool the rarest cell types and anchor there"** — which is a device any annotation
vocabulary supports, needs no new ontology, and delivers a 2.5× smaller penalty than the best
rung the fly's own annotation happens to provide.

## 5. Limits

- One circuit, one connectome, as throughout. The *shape* of the curve may be specific even if
  the lesson (pool the rarest groups) is not.
- The two coarse endpoints (`pool64`, `pool128`) have identical `constrained_fraction` (0.322)
  because beyond `pool32` no additional cell type meets the size threshold on this circuit, so
  the ladder has fewer than eight distinct granularities. The curve's fine end is finer than
  its coarse end.
- `pool1` is the only unresolvable rung, and it is unresolvable because it is nearly the
  diagonal (§ its `constrained_fraction` 0.979 against the diagonal's 0.999) — the two bases
  differ by a rounding error, which is itself the point.
