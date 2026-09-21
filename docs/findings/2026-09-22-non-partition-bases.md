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

d = 952, 2 seeds, analytic effect size:

| basis | constrained_fraction | excess | pressure |
|---|---|---|---|
| `bio:side` | 0.5014 | +0.00466 | 0.0214 |
| **`eigbasis`** | **0.9979** | **+0.01435** | **0.0297** |
| `diagonal(EWC)` | 0.9979 | +0.02838 | 0.1196 |
| `rank4` | 0.9916 | +0.03359 | 0.0782 |
| `rank16` | 0.9664 | +0.03354 | 0.0779 |
| `rank64` | 0.8655 | +0.03307 | 0.0768 |

`eigbasis` and `diagonal(EWC)` have **identical `constrained_fraction`** — a rotated
diagonal keeps the same number of free entries — so this is not a granularity effect.
Anchoring in the wiring's own preferred directions **halves the excess error**
(+0.0144 against +0.0284) at the same capacity.

This is a new and independent positive result, and it is *structural rather than
biological*: the eigenbasis is derived from the weight matrix, not from any
annotation. It says the fly's wiring has preferred directions that are a better place
to anchor a Fisher matrix than the neuron coordinate basis is — which is the
project's founding question answered affirmatively, one level below the annotation
ladder.

The honest caveat is capacity accounting: a rotated diagonal needs `d(d-1)/2`
rotation numbers. Those are **shared across tasks** and computed once from the
connectome, so the per-task cost is `d` — but a reader should know the rotation is
not free, and `bases.py` tracks it in `n_shared_parameters`.

## 3. The predictor generalises to the eigenbasis — and fails on truncation

`projection_pressure` orders the non-partition bases correctly for `eigbasis`
(0.0297, predicting better than the diagonal's 0.1196 — and it *is* better) but
**wrongly for all three `rank` bases**: pressure 0.077–0.078, lower than the
diagonal's 0.120, yet their excess (+0.0331 … +0.0336) is *worse* than the
diagonal's (+0.0284).

Over the full 15-basis set this drags the rank correlation from +0.982 (partitions
only, at d=952) down to **+0.696** (all bases). The matched-pair sign test on
partitions is unaffected — 5/5.

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
