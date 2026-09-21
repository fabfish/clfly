# E2 — the wiring *does* separate the tasks, but that is not what drives the gap

**Date:** 2026-09-22
**Script:** `experiments/e2_topology_gap.py`
**Artifacts:** `runs/e2_topology.json`
**Setup:** circuit `mb+cx+al@n1307` (d=1307), 3 seeds, 5 tasks, matched budgets

---

## 1. The test

E3 found that EWC's diagonal gap on wiring-derived tasks is ~45% of the oracle's
error (against <1% in LGCL's synthetic random-rotation family), and that the tasks
there come out near-orthogonal with disjoint supports. The natural reading was:
**the fly's modular wiring keeps the tasks apart, and that is why the coordinate
basis survives.** That reading makes a prediction — destroy the wiring, tasks
interfere, gap grows — and this experiment tests it.

Everything is held fixed except the targeting: same circuit, same neurons, same
assemblies, same support sizes, same seeds, same matched budgets. The null is one
operation at increasing strength — the classic double-edge swap, which preserves
in-degree, out-degree **and edge count exactly** — so the contrast is monotone in
a single interpretable quantity.

| topology | overlap | /chance | eff. rank | flattening | **gap:EWC** | **bio−rand** |
|---|---|---|---|---|---|---|
| `real` | 0.0075 | 0.135 | 50.2 | 0.692 | +0.634 | **−0.175** |
| `swap0.1` | 0.0105 | 0.189 | 44.3 | 0.610 | +0.509 | −0.079 |
| `swap0.5` | 0.0223 | 0.402 | 20.2 | 0.279 | +0.357 | +0.016 |
| `swap2` | 0.0626 | 1.127 | 1.9 | 0.026 | +0.226 | +0.017 |
| `erdos_renyi` | 0.2860 | 5.148 | 27.9 | 0.384 | **+3.116** | +0.078 |

`overlap` is the mean `cos²` between consecutive task precision subspaces;
`/chance` divides by the value expected for random subspaces of the same
dimensions (`rank/d = 0.0555`). `flattening` is the participation ratio of each
task's precision spectrum divided by its rank — 1 means flat, →0 means collapsed
onto a few directions.

## 2. Supported — the connectome separates the tasks, and rewiring destroys that

Monotone in both raw overlap and overlap relative to chance:

    overlap/chance:  0.135 → 0.189 → 0.402 → 1.127 → 5.148

The real connectome keeps the task subspaces **7× more orthogonal than random
subspaces would be**. A fully random graph makes them **5× more aligned than
chance**. This is a clean, quantitative statement of why a real brain resists
interference, and it is exactly the modularity story: different behaviours recruit
different cell types and the wiring does not scramble them together.

## 3. Refuted — the gap does not track interference

    EWC gap:   +0.634 → +0.509 → +0.357 → +0.226 → (+3.116)

Across the entire degree-preserving family the gap moves the **opposite way** to
overlap. Task interference rises 8× (0.0075 → 0.0626) while the gap *falls* by
almost two-thirds. The hypothesis in E3's "next steps" — rewiring scrambles the
assemblies, so the gap grows — is **wrong**, and it is wrong on the axis it was
most cleanly testable.

The gap is not explained by how much the tasks overlap.

## 4. What it does track instead

The variable that moves with the gap is **how spectrally rich each task's
precision is**. `flattening` (effective rank ÷ rank) falls monotonically
0.692 → 0.610 → 0.279 → 0.026 alongside the gap's fall, a perfect rank
correlation over these four points:

| | `real` | `swap0.1` | `swap0.5` | `swap2` |
|---|---|---|---|---|
| flattening | 0.692 | 0.610 | 0.279 | 0.026 |
| gap | +0.634 | +0.509 | +0.357 | +0.226 |

The connectome's propagator gives each task a precision spread over ~50 effective
directions out of ~72; as the wiring is randomised that spread collapses, and at
`swap2` each task is essentially **rank-1** (effective rank 1.9). A rank-1 task
constrains one direction and the diagonal projection loses almost nothing on it.

So the direction of the Phase-1 finding is reproduced but the *quantity* is not
the same one. Phase 1 varied the anisotropy of a **fully observed** task's
covariance and found more anisotropy → bigger penalty. Here every task is
**rank-deficient**, and the measure is concentration *within* the observed
subspace: a rich spectrum there means the diagonal throws away more. Both are
"anisotropy matters", but they are different axes and one does not imply the
other. Stating it as a single law would be overreach; stating that overlap is not
the driver is well supported.

## 5. A stronger result than expected — the biological advantage is a property of the wiring

The paired contrast (biological `cell_class` minus its group-size-matched random
control) is monotone in the null order and **flips sign**:

    bio − rand:  −0.175 → −0.079 → +0.016 → +0.017 → +0.078

On the real connectome the cell-class grouping beats an arbitrary partition of
identical capacity by 0.175 of gap. On a randomised graph it does not beat it at
all. This closes the most obvious objection to claim C2 — that "cell class" is
just *a* natural partition and any meaningful grouping would do equally well. It
does not: **the advantage exists only on biological wiring and decays to zero, and
slightly past zero, as the wiring is randomised.**

That is a better version of C2 than E3 alone supported. The grouping is not
intrinsically good for anchoring; it is good because it matches the connectome.

## 6. Caveat — Erdős–Rényi is a different regime, not the end of this axis

ER departs from both trends: overlap saturates high (as expected) but flattening
jumps *back up* to 0.384 and the gap explodes to +3.12, five times the real
connectome's. ER is not "more rewiring" — it also destroys the degree sequence,
and a dense signed random matrix at spectral radius 0.9 has a near-singular
`(I − W)`, so the propagator amplifies enormously and the task precisions become
wildly ill-conditioned.

Reporting ER as the endpoint of the swap axis would therefore be a mistake; it
changes the conditioning of the dynamics, not just the targeting. It is reported
here as a separate regime, and the monotonicity claims are restricted to the
degree-preserving family.

## 7. A methodology failure worth recording

The first version of the null permuted the post-synaptic target column globally.
One line of code, out-degree exactly preserved, and wrong: with 26,568 edges over
1,307 neurons the permutation collides heavily, and rebuilding the graph sums the
duplicates. **The null lost 70% of the edges** — so the "rewired" condition was
also the "much sparser" condition, and no gap difference could have been
attributed to topology.

Replaced with the double-edge swap, which is duplicate-guarded and preserves the
edge count exactly. The experiment now prints edges-before and edges-after for
every null; any future drift will be visible rather than silent.

## 8. Status

- **C1 (substrate effect):** the *geometry* half is supported strongly. The
  *mechanism* half is refuted as stated and replaced by a spectral-richness
  account, which is consistent with the data but tested on only four points.
- **C2 (biological basis):** strengthened. The advantage is monotone in wiring
  randomisation and absent off the real connectome.
- **Phase-1 ↔ Phase-2 link:** both say anisotropy governs the diagonalisation
  penalty, on different axes. Unifying them is now the main theoretical question.

Next:

1. Put more points on the flattening axis — it is confounded with the swap
   strength right now. A cleaner design varies the task's spectral spread
   *directly* (e.g. by filtering the assembly drive) at fixed topology.
2. Separate the two anisotropy axes explicitly: fully-observed anisotropic tasks
   versus rank-deficient tasks with controlled spectra, in one experiment.
3. Seed count: the `swap0.1` / `swap0.5` differences are single-digit-percent gap
   changes at 3 seeds; the monotone *bio − rand* trend is the robust one.
