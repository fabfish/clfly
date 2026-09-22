# E82 — the pressure mechanism replicates at a second circuit size, to within ±0.02 of the same correlation

**Date:** 2026-09-23
**Script:** `experiments/e81_pressure_comovement.py --circuit-size 300 --support 30` (`e82`, first half)
**Artifacts:** `runs/e82_pressure_comovement_d300.json` (d = 952), against `runs/e81_pressure_comovement.json` (d = 1307)
**Context:** `2026-09-23-the-pressure-mechanism.md` (e81), `2026-09-23-pressure-spread-predicts-the-draw-spread.md` (e80)

---

## 1. Why this replication is the cheapest honest one the project has

`e81` found the mechanism: the control's excess moves across relabellings with
`projection_pressure` — the precision-weighted projected deficit — at *r* = 0.906, *r*² = 0.828, against
0.170 / 0.066 for the bare alignment on the identical design. The project's standing requirement for a new
result is a second configuration, and this one is unusually cheap to check because **the co-movement needs
no measured draw sd at all**: it is a within-partition correlation between two quantities computed on the
same relabelling. So unlike `e80`, whose target is nine numbers measured at one size, there is nothing to
re-measure at a new size.

Second configuration: **cs = 300 (d = 952)**, which is `e6`'s `baseline` condition. The d = 1874 half
(cs = 1500) is still running.

## 2. The result: identical to ±0.02, and the weakest partition *improved*

| partition | *r*, d = 1307 | **r, d = 952** | diff | *r*², d = 1307 | ***r*², d = 952** |
|---|---|---|---|---|---|
| `cell_type` min 1 | +0.851 | **+0.943** | +0.091 | 0.725 | 0.889 |
| `cell_type` min 2 | +0.911 | +0.892 | −0.019 | 0.830 | 0.795 |
| `cell_type` min 3 | +0.949 | +0.942 | −0.007 | 0.900 | 0.888 |
| `cell_type` min 4 | +0.968 | **+0.979** | +0.011 | 0.936 | 0.958 |
| `cell_type` min 6 | +0.958 | **+0.979** | +0.021 | 0.918 | 0.958 |
| **`side`** | **+0.681** | **+0.800** | **+0.119** | 0.464 | 0.640 |
| `cell_class` | +0.931 | +0.869 | −0.062 | 0.867 | 0.754 |
| `ito_lee_hemilineage` | +0.980 | +0.938 | −0.043 | 0.961 | 0.879 |
| `supertype` | +0.925 | +0.963 | +0.038 | 0.855 | 0.927 |

| | d = 1307 | d = 952 |
|---|---|---|
| mean *r* | +0.906 | **+0.923** |
| mean *r*² | 0.828 | **0.854** |
| partitions with a non-positive co-movement | 0 of 9 | **0 of 9** |
| seeds positive | 27 of 27 | **27 of 27** |

**The paired difference between the two sizes is +0.017 ± 0.020 with a sign test at p = 1.000** — i.e. no
detectable difference at all, in either direction, on the same nine partitions. Nine of nine partitions
have a positive co-movement at both sizes and every one of the 54 seed-level correlations across the two
runs is positive.

**And the key weakness reverses.** At d = 1307 the one partition where the mechanism was visibly weaker was
`side` (*r*² 0.464, the 4-group highest-concentration partition, and the one where the *alignment's*
co-movement was negative). At d = 952 `side` is among the stronger ones (+0.800, *r*² 0.640). So "83% on
average, 46% for the partition the paper leans on" is a statement about d = 1307 and not about `side` as a
partition — which is the right form of the caveat and it now has a measurement behind it.

## 3. One thing the replication exposes, and it is the project's own crowding again

At cs = 300 **`cell_type` min 4 and min 6 are the same partition** — identical pressure levels (0.00431),
identical *r*, identical *r*². So the "nine partitions" at d = 952 are **eight distinct**, and the row
count overstates the evidence there by one. This is the same crowding `e3` found at d = 1307, where
`pool32` and `pool64` are the same partition because only two cell types have ≥32 neurons; at 952 neurons
the crowding reaches one rung lower. It does not change the replication — dropping the duplicate gives
mean *r* **+0.916** and mean *r*² **0.841**, against +0.923 and 0.854 with it — but a reader counting rows
would be over-counting, so it is stated.

## 4. What this establishes, and what it does not

**Establishes:** the pressure mechanism is not a property of the d = 1307 task suite. Two circuit sizes
differing by 1.37× in neuron count, with different partitions at the fine end, give the same correlation
to within ±0.02 and the same unanimous sign record — **all 54 seed-level correlations across the two runs
are positive, the smallest +0.636**.

**Does not establish:** anything about the *spread* statistic. `e80`'s +0.767 needs the nine measured draw
sds, which are d = 1307 numbers; the script now **refuses to report that statistic** away from d = 1307
rather than printing a foreign target, which is why the d = 952 output has no spread line. Replicating
`e80` would require measuring nine draw sds at the new size — 9 partitions × 5 draws × 3 seeds of the
expensive path — and that has not been done.

**Nor** anything about a third size yet: the d = 1874 half (cs = 1500, 1.43× larger than d = 1307 in the
other direction) is running, and its `cell_type` poolings will be coarser at the fine end.

## 5. Limits

- **Three task seeds, six relabellings, two circuit sizes.** The same dof caution as `e81`: eighteen
  seed-centred points of which the six draws are shared across seeds, so effective dof nearer four or five.
  The *replication* is much better protected than either run alone, because the two runs are independent
  samples of the same quantities.
- **The task suite changes with the circuit size** (support 30 against 80, and a different neuron
  population), so "replicates across circuit size" also means "replicates across task geometry", and the
  two cannot be separated here. That is a property of the substrate rather than of this design.
- **`cell_type` min 1 at d = 952 has 508 groups** against 812 at d = 1307, so even the "same" rung is a
  different partition at the two sizes; the agreement is between two different partition families, which
  strengthens the claim rather than weakening it but is worth saying plainly.
