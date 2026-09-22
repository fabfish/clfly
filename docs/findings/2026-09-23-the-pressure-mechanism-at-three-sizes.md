# E82 (complete) — the pressure mechanism holds at **three** circuit sizes, and decays measurably at the largest

**Date:** 2026-09-23
**Script:** `experiments/e82_three_sizes.py`
**Artifacts:** `runs/e82_pressure_comovement_d300.json` (d = 952), `runs/e81_pressure_comovement.json` (d = 1307), `runs/e82_pressure_comovement_d1500.json` (d = 1874)
**Context:** `2026-09-23-the-pressure-mechanism.md` (e81), `2026-09-23-the-pressure-mechanism-replicates.md` (e82's first half), `2026-09-23-pressure-spread-predicts-the-draw-spread.md` (e80)

---

## 1. The measurement, at all three sizes

`e81` found the mechanism at d = 1307: the control's excess moves across relabellings with
`projection_pressure` — the precision-weighted projected deficit — at *r* = 0.906, *r*² = 0.828, against
0.170 / 0.066 for the bare alignment on the identical design. This run adds d = 952 (cs = 300, support 30,
`e6`'s `baseline` condition) and d = 1874 (cs = 1500, support 150, `e9`/`e79`'s ladder size).

| size | *n* | mean *r* | mean *r*² | median *r* | seeds positive | distinct partitions |
|---|---|---|---|---|---|---|
| **d = 952** | 9 | **+0.923** | 0.854 | 0.942 | **27/27** | 8 |
| **d = 1307** | 9 | **+0.906** | 0.828 | 0.931 | **27/27** | 9 |
| **d = 1874** | 9 | **+0.810** | **0.676** | 0.853 | **27/27** | 9 |

**All 81 seed-level correlations across the three sizes are positive** (smallest +0.368), and the bare
alignment's +0.170 is beaten at every size by a margin of 4.8× in *r*².

| paired comparison, shared labels | difference | σ | signs | p |
|---|---|---|---|---|
| d = 1307 − d = 952 | −0.0166 ± 0.0198 | 0.84 | `-++---++-` | 1.0000 |
| **d = 1874 − d = 1307** | **−0.0962 ± 0.0293** | **3.29** | **`+--------`** | **0.0391** |

## 2. So the mechanism replicates — and it is not size-invariant

**The first comparison is a null and the second is not.** Moving from d = 952 to d = 1307 changes nothing
detectable (0.84σ, sign test at exactly p = 1); moving from d = 1307 to d = 1874 costs **0.096 in *r*, at
3.29σ, with eight of nine partitions declining** and only `cell_type` min 1 improving. Mean *r*² falls
from 0.828 to 0.676.

Per partition, and the two shapes are different:

| partition | d = 952 | d = 1307 | d = 1874 |
|---|---|---|---|
| `cell_type` min 1 | +0.943 | +0.851 | **+0.880** |
| `cell_type` min 2 | +0.892 | +0.911 | +0.835 |
| `cell_type` min 3 | +0.942 | +0.949 | +0.853 |
| `cell_type` min 4 | +0.979 | +0.968 | +0.897 |
| `cell_type` min 6 | +0.979 | +0.958 | +0.904 |
| **`side`** | +0.800 | +0.681 | **+0.418** |
| `cell_class` | +0.869 | +0.931 | +0.853 |
| **`ito_lee_hemilineage`** | +0.938 | +0.980 | **+0.771** |
| `supertype` | +0.963 | +0.925 | +0.877 |

The four `cell_type` poolings and `supertype` and `cell_class` all stay in 0.83–0.90 at the largest size —
the mechanism is essentially intact for them. **What decays is `side` (0.681 → 0.418, *r*² 0.46 → 0.17) and
`ito_lee_hemilineage` (0.980 → 0.771)**, and those two are the rungs whose partitions are most extreme in
opposite ways: `side` is the 4-group, highest-concentration partition, `ito_lee_hemilineage` the
212-group near-diagonal one.

**`side` is now the one partition that behaves differently at every size**: +0.800 at d = 952, +0.681 at
d = 1307, +0.418 at d = 1874 — a monotone decline at three points, and the **only partition whose *r*²
falls below 0.5 at any size** (0.464 and 0.175 at the two larger ones, against 0.594–0.958 for every other
partition at every size). It is also the rung the paper's C1 claims lean on most, and the one whose draw
sd was the subject of `e67`'s refutation. Whatever the functional is measuring, it is least complete for
that partition.

## 3. What this does and does not change

**Does not change:** the mechanism's existence, its direction, or its independence from concentration. It
holds at three circuit sizes spanning 1.97× in neuron count, 81 of 81 seed-level correlations are
positive, and *r*² stays between 0.68 and 0.85 — against the bare alignment's 0.066. The claim in
`docs/paper/clfly-v1.md` §4.3 that the draw spread is about the **precision-weighted projected deficit**
rather than subspace geometry is unaffected, and its "83%" should now be quoted as **68–85% depending on
circuit size**.

**Does change:** the mechanism is **not size-invariant**, and the decay is measured rather than inferred
(3.29σ, 8 of 9 partitions). Two candidate explanations, neither tested:

* the functional is a **Frobenius aggregate over three tasks**, and at larger `d` the relabelling perturbs
  a higher-dimensional span, so the same 6-draw × 3-seed budget samples a smaller fraction of the
  perturbation space — which would make the decay a property of the *design*, not of the quantity;
* or the control's excess picks up contributions at large `d` that the pressure functional does not
  represent, which would make the decay a property of the *quantity*.

They are separable: the first predicts that more draws or seeds at d = 1874 restores *r*, the second
predicts it does not. That is the natural next run, and it is cheap by this line's standards (the
co-movement needs no measured draw sd).

## 4. Limits

- **Three task seeds, six relabellings, per size.** As in `e81`, the eighteen seed-centred points share
  their six draws across seeds, so effective dof is nearer four or five and every interval is wider than
  nominal. The *paired* comparisons are better protected than either run alone, and the 3.29σ decay has
  8-of-9 sign agreement behind it.
- **The task suite changes with the size** (support 30 → 80 → 150, and a different neuron population), so
  "decays with circuit size" also means "decays with task geometry" and the two cannot be separated here.
- **The distinct-partition counts differ** (8 at d = 952 because `cell_type` min 4 and min 6 coincide, 9
  at the other two), so the nine rows are not nine partitions everywhere; the paired comparisons above use
  the shared labels and are unaffected, but a reader counting rows would over-count at d = 952.
- **The d = 1874 `cell_type` poolings are coarser than at d = 1307** — more neurons clear each threshold —
  so the same label is a different partition at each size. That strengthens the replication and makes the
  decay harder to attribute.
- **The spread statistic is not replicated.** `e80`'s +0.767 needs the nine measured draw sds, which are
  d = 1307 numbers; the d = 952 and d = 1874 outputs refuse to print it, because a foreign target is
  worse than no target.
