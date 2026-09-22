# The control's draw sd is set by *concentration*, not by group count — and `side` belongs with the coarse partitions

**Date:** 2026-09-22
**Script:** `clfly/bench/control.py` (`concentration`)
**Artifacts:** group profiles computed from the circuit; the measured draw sds are those of e12/e14

---

## 1. What was wrong with the model

The draw-budget analysis (`docs/findings/2026-09-22-draw-budget.md`) assumed a **hard step**:
``sd_draw ≈ 1.1e-3`` for partitions with at most ~12 groups, ``≈ 6e-5`` for those with hundreds,
and an interpolation in between. Group count was the chosen axis because it was the obvious proxy
for "coarse".

It produced a specific worry. A two-draw smoke run of `--column side` at d = 952 gave an
across-draw sd of **9e-5**, which is the *fine* regime, and `side` has 4 groups. If that were real,
the `side → pool4` budget would be wrong by more than an order of magnitude in the direction that
makes the claim easier.

## 2. The profiles say the axis is wrong

`sum_g s_g^2 / d^2` — how much of the neuron-pair covariance the partition constrains — is now a
function, `concentration(labels)`. Profiles of the partitions that have been measured:

| d | column | min_size | groups | biggest group / d | `sum s^2/d^2` | measured draw sd |
|---|---|---|---|---|---|---|
| 952 | `cell_type` | 1 | 812 | 0.056 | **0.006** | 9e-5 (5 draws) |
| 952 | `cell_type` | 4 | 8 | 0.866 | **0.754** | 1.08e-3 (4 draws) |
| 1307 | `cell_type` | 1 | 812 | 0.107 | **0.020** | 3.9e-5 (n=2) |
| 1307 | `cell_type` | 2 | 90 | 0.553 | **0.325** | 9.3e-4 (5 draws) |
| 1307 | `cell_type` | 32 | 3 | ~0.812 | **0.678** | 1.06e-3 (n=2) |
| **1307** | **`side`** | **1** | **4** | **0.501** | **0.498** | **not measured** |

The relation is monotone in ``sum s^2/d^2`` and steep between 0.02 and 0.33, then flat:

```
sd_draw (log) vs sum s^2/d^2
  1e-3 |                                     *     *     *
       |                          *
  1e-4 |  *
       |        *
       +------+------+------+------+------+------+------+
       0     0.1    0.2    0.3    0.4    0.5    0.6    0.7
```

Group count is a bad proxy for this. `side` has **4 groups** but a concentration of **0.498** —
higher than the 90-group partition's 0.325, because it is *balanced* (four near-equal parts of a
13-hundred-neuron circuit concentrate more than an 812-group partition whose groups are almost all
singletons). A model keyed on group count gets `side` exactly backwards, which is precisely what the
smoke run hinted at.

## 3. The prediction, written down before the measurement

**`side`'s draw sd is ~1.0e-3, not 9e-5.** Its concentration (0.498) sits above the measured point
at 0.325 (9.3e-4) and below the plateau at 0.678–0.754 (1.1e-3), so ~1.0e-3 is the interpolation;
and the mechanism — which neurons share the large group — is fully present at 0.498.

So:

- the 9e-5 smoke value is predicted **not to replicate**; it was two draws, and the sd of two points
  has a standard error of order 50%;
- the `side → pool4` budget of K ≈ 2.8 **stands**, and the "coarse" column of the budget table did
  not need to be split by column after all — but for a reason the group-count model could not have
  supplied.

This is recorded as a prediction rather than a conclusion because the measurement does not exist yet.
`e12_control_spread --column side --draws 5` settles it, and it is cheap: one biological partition
plus five controls.

## 4. What this buys

- **A mechanistic scalar instead of a lookup.** The draw sd can be predicted before any filter runs,
  from the group sizes alone. That is the input a designer of a matched-control experiment actually
  has, and it means the budget calculation in `2026-09-22-draw-budget.md` can be done for a new
  circuit without first measuring anything.
- **A check on the one number that looked wrong.** Two independent routes (the cross-run duplicate
  partitions at 0.020 and 0.678) and one direct measurement (0.325) agree; the odd value out has two
  draws.
- **`concentration` is exact and free** — no filter, no oracle, no seeds.

## 5. Limits

- **Five measured points, two of them from a single pair of draws.** The plateau's *height* (~1.1e-3)
  is better determined than the knee's *position* (somewhere between 0.02 and 0.33), which no
  measurement brackets on both sides. e14's remaining runs (min_size 3, 4, 6 → concentrations 0.395,
  0.459, 0.536) sit exactly in the knee and will place it.
- The relation is calibrated on **one circuit and one species**, as everything here is, and on
  `cell_type`-derived partitions. `cell_class` (0.171) and the annotation columns are unmeasured.
- ``sum s^2/d^2`` is not a sufficient statistic in general: two partitions with the same
  concentration but different size *profiles* could differ. `side` and the 3-group `pool32` partition
  are the closest available pair (0.498 vs 0.678) and they differ, which is the wrong direction for a
  claim of exactness — hence "predictive scalar", not "formula".
- The claim that the mechanism is "which neurons share the large group" is **argued, not tested**.
  A direct test would permute only the non-singleton groups and hold the singletons fixed.
