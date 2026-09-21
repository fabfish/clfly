# Non-partition anchoring bases: the connectome's eigenbasis wins, and where the predictor breaks

**Date:** 2026-09-22
**Script:** `experiments/e3_basis_selection.py --extra-bases`
**Artifacts:** `runs/e3_seeds18.json` (d=1307, 18 seeds, in flight at time of writing);
the d=952 figures below are complete measurements.

---

## 1. Why non-partition bases

Every candidate so far has been a *partition* — a fixed grouping of neurons
(cell class, cell type, hemilineage, left/right). That answers "which partition?"
but not the more general question the project actually started from: **which
structure should the Fisher be projected onto?** Three non-partition candidates are
now included, all handled by the same `Basis` machinery and the same predictor:

- `rank4`, `rank16`, `rank64` — spectral truncation: keep the top-``r`` eigen-
  directions of the posterior and flatten the rest. **State-dependent**: the retained
  directions are re-chosen from the current posterior at every step.
- `eigbasis` — the diagonal in the **connectome's own eigenbasis**, i.e. the
  eigenvectors of the symmetrised, centred weight matrix. A fixed structural rotation
  that has nothing to do with the annotation vocabulary.

## 2. Result: the connectome's eigenbasis beats the neuron diagonal at equal capacity

**d = 1307, 18 seeds** (the standard configuration):

| basis | constrained_fraction | excess | sem | pressure |
|---|---|---|---|---|
| `bio:side` | 0.5011 | +0.00391 | 0.00008 | 0.1002 |
| `bio:cell_class` | 0.8280 | +0.01147 | 0.00016 | 0.1770 |
| **`eigbasis`** | **0.9985** | **+0.01270** | 0.00020 | **0.1257** |
| `bio:ito_lee_hemilineage` | 0.9668 | +0.01422 | 0.00020 | 0.3420 |
| `bio:supertype` | 0.9736 | +0.01577 | 0.00023 | 0.4651 |
| `diagonal(EWC)` | 0.9985 | +0.01762 | 0.00025 | 0.6604 |
| `rank64` | 0.9021 | +0.02220 | 0.00037 | 0.4204 |
| `rank16` | 0.9755 | +0.02231 | 0.00037 | 0.4258 |
| `rank4` | 0.9939 | +0.02233 | 0.00037 | 0.4270 |

At d = 952 (2 seeds) the same comparison gives `eigbasis` +0.01435 against the
diagonal's +0.02838, i.e. a 49% reduction.

`eigbasis` and `diagonal(EWC)` have **identical `constrained_fraction`** — a rotated
diagonal keeps the same number of free entries — so this is not a granularity effect.
Anchoring in the wiring's own preferred directions cuts the excess error by **28%**
(+0.01270 against +0.01762) at equal capacity, making it the third-best of the
fourteen candidates and the best non-annotation one.

This is a new and independent positive result, and it is *structural rather than
biological*: the eigenbasis is derived from the weight matrix, not from any
annotation. It says the fly's wiring has preferred directions that are a better place
to anchor a Fisher matrix than the neuron coordinate basis is — which is the
project's founding question answered affirmatively, one level below the annotation
ladder.

The honest caveat is capacity accounting: a rotated diagonal needs `d(d-1)/2`
rotation numbers. Those are **shared across tasks** and computed once from the
connectome, so the per-task cost is `d` — but a reader should know the rotation is
not free, and `bases.py` tracks it in `n_shared_parameters`. A related subtlety is that
the rotation is *estimated from the same connectome that generates the tasks*, so this
is a favourable case for it; a task whose structure came from outside the wiring would
not obviously benefit.

### 2.1 The three worst candidates are the adaptive ones

The `rank` bases are the **worst** of all fourteen (+0.0222 … +0.0223 against the
diagonal's +0.01762), and they are the only candidates that adapt their retained
subspace to the current posterior. Truncating to the top `r` directions is *locally
optimal at every step* and loses to a fixed commitment; at d = 952 the inversion is
larger still (+0.0331 against +0.0284).

That ordering is itself a result. The two winners are both **fixed** structures — the
coarsest biological grouping, then the wiring's own eigenbasis — and the losers are
the adaptive scheme. A myopic, locally-optimal projection loses to a fixed commitment
on a substrate where the failure mode is re-projection rather than interference.

## 3. The predictor generalises to the eigenbasis — and fails on truncation

`projection_pressure` orders the non-partition bases correctly for `eigbasis`
(0.1257, second-lowest of the fourteen — and it is third-best) but **wrongly for all
three `rank` bases**: pressure 0.42–0.43, mid-table and lower than the diagonal's
0.660, yet their excess (+0.0222 … +0.0223) is the *worst* of the fourteen against the
diagonal's +0.01762.

Over the full 15-basis set this drags the rank correlation to **+0.611**, against
**+0.991** over the 11 partition bases alone. The matched-pair sign test on partitions
is unaffected — **5/5**. (Within the non-partition set alone the predictor scores
+1.000, but that is a degenerate ordering: the three `rank` bases are separated by
0.0001 in excess, so little is being tested there.)

**Why truncation breaks it, with a measured mechanism.** For a partition or the
eigenbasis the projection map is **fixed**: it retains a fixed set of coordinates, and
the same coordinates at every step. `Rank(r)` retains the top-``r`` eigen-directions
of the *current* posterior, so the coordinate set it keeps is re-chosen every step.
Measured on the exact filter, the retained 16-dimensional subspace overlaps the
previous step's by **0.03 for `Rank(4)` and 0.02 for `Rank(64)`** — it is essentially
renewed every step.

`projection_pressure` scores each step's discarding **myopically**. For a fixed
structure that is adequate, because the retained coordinates never move. For a
state-dependent basis it is not: directions that mattered for earlier tasks are
discarded and never recovered, and the one-step metric cannot see the accumulation.
The predictor is therefore a **fixed-structure** predictor, with a testable
prediction — *any* basis whose projection depends on the current posterior will be
mispredicted.

(The same measurement gives 0.73 for `Diagonal(EWC)`, which is a proxy artefact
rather than a finding: `Diagonal` retains a fixed *set of entries* but the top-16
eigendirections of a diagonal matrix follow whichever diagonal entries happen to be
largest. The fixed/state-dependent distinction is about the projection *map*, not
about the top eigendirections of its output.)

## 4. A second thing the extras expose: `constrained_fraction` does not summarise `Rank`

`constrained_fraction` is computed as `1 − n_parameters / (d(d+1)/2)` with
`n_parameters = r(d+1)` for `Rank(r)`. That treats truncation as if it merely
"constrains" the covariance, which is not what it does: it keeps `r` directions
*exactly* and replaces the remaining `d − r` eigenvalues with their scalar mean. So
`rank4` reports 0.9916 while behaving like a much more aggressive intervention than
the 0.9979 diagonal — and it is worse.

This is a bookkeeping limitation rather than a scientific one, but it is the kind
that invites a wrong comparison, so it is recorded: **`constrained_fraction` is a
valid matching variable only within a family of bases that discard the same kind of
thing.** It is meaningful across partitions (all of which zero entries) and across
rotated diagonals, but not between a partition and a spectral truncation.

## 5. Status of the anchoring question

| candidate family | best member | excess vs the neuron diagonal |
|---|---|---|
| partition (annotation) | `side` (0.50 constrained) | **−80%** |
| fixed structural rotation | `eigbasis` | **−49%** at equal capacity |
| spectral truncation (state-dependent) | `rank*` | **+17%** (worse) |
| the neuron diagonal | `diagonal(EWC)` | — |

So the answer to "which structure?" is: **the coarsest biological grouping if one is
available, otherwise the wiring's own eigenbasis** — and *not* an adaptive
truncation, which is worse than doing nothing beyond the diagonal despite being
locally optimal at every step.

That ordering is itself a result: the two winners are both fixed structures, and the
loser is the adaptive one. A myopic, locally-optimal scheme loses to a fixed
commitment, on a substrate where the tasks are near-orthogonal and the failure mode is
re-projection rather than interference.
