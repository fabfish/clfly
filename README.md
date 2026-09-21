# clfly

**Continual learning on the *Drosophila* whole-brain connectome.**

One brain, many behaviours, no catastrophic forgetting. A fly learns to associate
odours with food, navigate by landmarks, and dodge looming threats — sequentially,
without its olfactory memories being erased by its navigation lessons. Artificial
networks are famously bad at exactly this.

This repository asks a narrow, answerable version of that question:

> **EWC anchors its Fisher matrix in the neuron coordinate basis. Should it?**

That is not a rhetorical question. The LGCL theory in `reference/` shows EWC is a
Kalman filter whose posterior covariance is projected onto the coordinate basis
at every step — so `Diagonal()` *is* EWC, and the choice of basis is the whole
approximation. In synthetic problems with random task rotations that projection
turns out to be nearly lossless (<1% excess error), which is why nobody has
looked. A real connectome is not a random rotation. It is sparse, modular,
heavy-tailed, and — crucially — **annotated**, with a biological hierarchy of
groupings (cell type, hemilineage, nerve, neuropil) that suggests where the
information actually lives.

So the substrate is the FlyWire adult brain (139,255 neurons, ~3.7M proofread
connections) with the wiring frozen and only synaptic weights learned, and the
question is which anchoring basis minimises forgetting — with matching controls
that make the answer mean something.

## Why this might be interesting

- **No one has done it.** Full-text search for `connectome AND continual learning`
  returns nothing. Connectome-constrained models are used for simulation and
  knockout screens, never for forgetting curves.
- **The basis question is unstudied.** There is one 2018 paper that rotates
  weights to help EWC. There is no matched-budget comparison of parameter /
  eigen / neuron / module / cell-type bases.
- **The theory makes a falsifiable prediction.** LGCL's unimodal misalignment
  gap was a negative result in the parameter basis and reappeared in the Gram
  basis, with the mechanism pinned down: the loss is `rotation x recursive
  projection`, a *geometric resonance* requiring the anchoring basis to align
  with the task's precision basis. A cell-type partition is a concrete,
  testable candidate for such an alignment.
- **It has a clean control.** Group-size-matched random partitions have exactly
  the same number of free parameters as the biological basis they replace. If
  cell types win, they win for structural reasons, not capacity.

## Status

Phase 0 (toolchain), Phase 1 (LGCL port) and Phase 2 (connectome substrate) are
done. The first real experiment — basis selection — is next.

| Phase | What | State |
|---|---|---|
| 0 | toolchain, repo skeleton | done |
| 1 | LGCL port + exact reproduction of published numbers | done |
| 2 | FlyWire v783 graph, annotation ladder, circuit extraction | done |
| 3 | task definitions + FlyCL-v0 | next |
| 4 | experiments: topology effect, basis selection, modularity | pending |
| 5 | write-up | pending |

See `docs/research_plan.md` for the claims and `docs/findings/` for dated
experiment logs — including negative results, which are the useful kind. Two are
already recorded:

- **`2026-09-20`** — the published unimodal misalignment peak does **not** appear
  in the coordinate basis. The penalty turns out to be governed by task
  *anisotropy*, not rotation angle (~500× larger for a steep spectrum), which is
  what a real connectome supplies and a random synthetic task does not.
- **`2026-09-22`** — most of the annotation ladder is unusable as a full-brain
  basis (coverage 7–27% for hemilineage/supertype/nerve), and a near-singleton
  partition *is* plain EWC. Requires `constrained_fraction` as the matching
  variable, and a circuit-level reduction because a whole-brain covariance would
  be 152 GB.

## Reproduce the LGCL numbers

```bash
python -m clfly.lgcl.repro            # all published anchors
python -m clfly.lgcl.repro --json     # machine-readable, for the metric loop
python -m clfly.lgcl.probes           # mechanism experiments
pytest -q                             # regression gate (connectome tests skip without data)
```

Fetch the connectome (420 MB, gitignored, never redistributed):

```bash
python -m clfly.connectome.fetch
python -m clfly.connectome.fetch --check   # status only
```

## Install

Requires Python >= 3.10. The connectome data is **not** in this repository; it is
downloaded on demand (see `LICENSE` for the data's own terms).

```bash
# core only — enough for the LGCL work
pip install -e .

# everything: plots, connectome readers, tests
pip install -e ".[dev,connectome]"

# PyTorch is only needed from Phase 2 onwards
pip install -e ".[torch]"
```

## Reproduce the LGCL numbers

```bash
python -m clfly.lgcl.repro            # all published anchors
python -m clfly.lgcl.repro --json     # machine-readable, for the metric loop
pytest -q                             # regression gate
```

## Layout

```
clfly/lgcl/         the minimal solvable model, its oracle, and the method zoo
clfly/connectome/   FlyWire fetch, graph, annotations, rewiring controls
clfly/tasks/        FlyCL task suite (olfaction, vision, navigation, ...)
clfly/bench/        protocols, metrics, runners
clfly/diagnostics/  principal angles, interference, observability spectra
experiments/        one script per research claim
reference/          the LGCL source materials this project builds on
```

## The idea in one object

```python
from clfly.lgcl.bases import Full, Diagonal, Partition, Rank

Full(20)                  # keep everything            -> Kalman oracle
Rank(20, r=4)             # keep the top 4 directions  -> spectral truncation
Partition(cell_types)     # keep within-cell-type      -> the fly-anchored candidate
Diagonal(20)              # keep the diagonal          -> textbook EWC
```

Every method in continual learning is a point in this family. The project is
about which point reality sits at.

## Licence

Code: Apache-2.0. Connectome data: not redistributed, downloaded from its
distributors under their own terms (CC BY-NC 4.0 for FlyWire) — see `LICENSE`.
