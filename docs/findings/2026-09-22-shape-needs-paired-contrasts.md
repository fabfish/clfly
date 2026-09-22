# E11 — a curve's shape needs *paired* contrasts, and "pairing is never worse" is false

**Date:** 2026-09-22
**Script:** `clfly/bench/analytic.py` (`paired_delta`, `contrast_of_contrasts`), `experiments/e3_basis_selection.py --report-from`
**Artifacts:** `runs/e3_ladder.json` (re-analysed), `runs/e3_ladder_v2.json` (in flight)

---

## 1. Why this exists

E3b's granularity ladder originally claimed a **shape**: an optimum at ~0.54 constrained.
Commit `f2d7486` corrected that to a **plateau** over ~0.32–0.67, on the grounds that
"the delta resolves from zero at 42.2σ" is a different claim from "the delta at rung X differs
from the delta at rung Y". The contrasts that decided this were computed by hand, with the
**unpaired** formula ``hypot(sem_bio, sem_rand)``.

That is the wrong formula in the likely case. Every basis in a run sees the same task
geometries in the same seed order, so `bio:pool4` and `rand:pool4` are *matched* samples: the
per-seed excesses are paired, and the sem of their difference is the sem of the *per-seed
differences*. The project already stored only the pooled moments, so the paired figure could
not be computed at all. Two things were needed: store the per-seed values, and provide the
contrast as a function rather than an ad-hoc expression.

## 2. The false claim a test caught

The first version of `paired_delta` documented the unpaired figure as "conservative" and the
paired one as always smaller. A test asserting that bound failed:

```
assert 0.10280011283623151 <= (0.09962430162240206 * (1 + 1e-09))
```

The algebra is that a difference of matched series has variance
``sd_a^2 + sd_b^2 - 2 rho sd_a sd_b``, so pairing helps **iff ``rho > 0``**, and with a negative
sample correlation the *paired* figure is the **larger** one — and the correct one. A finite
sample can produce a negative correlation by chance even when the true one is zero.

So "the unpaired figure is conservative" is not a fact about the method; it is a **guess about
the sign of a correlation that nobody had measured**. The fix is to measure it: `paired_delta`
now returns `corr` and `conservatism` (the ratio of the two sems) alongside both sems, and the
docstring states the regime dependence instead of asserting a bound. This is the same failure
mode the project keeps finding — a methodological shortcut that is safe *in the regime we
expect* and silently wrong outside it.

## 3. What is now in the code

- `analytic_excess` stores **`excess_per_seed`**, so any two bases from one run can be
  contrasted paired, after the fact.
- **`paired_delta(bio, rand)`** returns `delta`, `sem_unpaired`/`sigma_unpaired`,
  `sem_paired`/`sigma_paired`, `corr`, `conservatism`, and `per_seed_delta`; it degrades
  cleanly (unpaired fields only) when per-seed values are absent.
- **`contrast_of_contrasts(a, b)`** does the same for the difference of two deltas, which is
  the quantity that decides whether a curve has a shape.
- The e3 report now prints `sigma_p` and `corr` per rung, and an **adjacent-rung contrast
  table** with both figures.
- **`--report-from <json>`** re-prints a finished run's report without recomputing it. A
  full ladder is hours of compute; analysis of its shape must not require re-running it.
- 18 tests in `tests/test_analytic.py` (6 new) cover the paired helpers, including the
  regime dependence above.

## 4. A presentation bug that was load-bearing for the shape claim

The rung list was built with `sorted(agg)`, i.e. **alphabetically** — `pool1, pool128, pool16,
pool2, pool32, pool4, pool64, pool8`. Every printed rung table has been in that order. Harmless
for a per-rung number, and fatal for an adjacent-rung contrast: the "adjacent" pairs would have
been alphabetically adjacent, and the entire plateau argument reads off those pairs. The rungs
are now sorted by `constrained_fraction`, finest first.

## 5. Verification

`python -m experiments.e3_basis_selection --report-from runs/e3_ladder.json` reproduces the
published plateau contrasts exactly, now from committed code rather than a hand-typed snippet:

| contrast | Δ of deltas | σ unpaired |
|---|---|---|
| `pool1 − pool2` | +0.00820 | 13.6 |
| `pool2 − pool4` | +0.00084 | 2.2 |
| `pool4 − pool8` | −0.00199 | 6.4 |
| `pool8 − pool16` | +0.00080 | 2.7 |
| `pool16 − pool32` | −0.00067 | 2.5 |
| `pool32 − pool64` | −0.00150 | 4.7 |
| `pool64 − pool128` | −0.00139 | 4.0 |

And it reports `7/8` rungs resolved and the predictor at Spearman **+0.995**, matching the
published values.

## 6. Still open

The run the paired column needs is the **d = 1307 ladder at 12 seeds with per-seed storage**
(`runs/e3_ladder_v2.json`, in flight; it doubles as the reproducibility check on the headline
numbers). Until it lands, `sigma_p` is `nan` and the plateau is stated with the conservative
unpaired figures. If the seed correlation turns out to be strongly positive — as it should be,
both arms being dominated by the task-geometry draw — the plateau may be *sharper* than 2.2σ
between `pool2` and `pool4`, and the shape claim would need revisiting in the other direction.

## 7. Limits

- The paired test is only available when both bases come from the same run with the same seeds;
  cross-configuration contrasts (`runs/e9_ladder_d1874.json` vs `runs/e3_ladder.json`) cannot be
  paired and must use the unpaired figure.
- `sigma_p` from 12 seeds is itself estimated from 12 differences, so it carries its own
  uncertainty of roughly ``1/sqrt(2(n-1))`` ≈ 21% on the sem. It is the better figure, not an
  exact one.
