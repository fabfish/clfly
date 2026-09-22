# E40 — `cs700` rejects the pre-registered geometry reading by 1.8× its own band, and does *not* test the sign rule

**Date:** 2026-09-22
**Script:** `experiments/e36_geometry_carrier.py` (re-run; no code change beyond picking up the artifact)
**Artifacts:** `runs/e26_size700.json`, `runs/e36_geometry_carrier.json`
**Context:** `2026-09-22-realization-attribution-refuted.md` §9, `2026-09-22-geometry-mechanism-refuted-on-the-realization-axis.md` §6

---

## 1. The sixth point

`cs700` (d = 1229) finished, six seeds, the same three topologies and the same task seeds as the rest
of the sweep:

| topology | excess | sem | effective rank | top-eig share |
|---|---|---|---|---|
| `real` | 0.01982 | 0.00039 | 46.300 | 0.1352 |
| `swap0.5` | 0.02135 | 0.00031 | 21.605 | 0.3013 |
| **`swap2`** | **0.01733** | 0.00016 | **2.806** | 0.6740 |

## 2. The pre-registered prediction, and the numbers it is judged against

The prediction was registered **before** the run, in two readings of the same point:

- **realization reading:** a fresh draw from a distribution with sd 0.0205, 95% interval
  **[−0.01083, +0.06953]** — wider than the physical range, i.e. the reading is that the point
  carries no information about where on a curve it should sit;
- **geometry reading:** it lands on **0.00280 + 0.02016 · ln(effrank)**, in a band of **±0.0034**
  (the wider of the five-point fit's in-sample maximum residual, 0.00296, and the one genuine
  out-of-sample residual then in hand), which was called **"6× tighter"** and was the test that
  mattered.

`cs700`'s effective rank is **2.806**, so the geometry reading predicts **0.02360**. The observation
is **0.01733**:

| | value |
|---|---|
| predicted `excess(swap2)` | 0.02360 |
| observed | 0.01733 |
| residual | **−0.00627** |
| residual / pre-registered band | **1.84×** |
| residual / in-sample max residual | **2.1×** |
| realization reading's interval | **contains it, vacuously** |

**So the sharp reading is rejected and the vacuous one is not supported** — that is the correct
summary, and the asymmetry should not be spun the other way. The realization interval spans almost
the entire physical range of the quantity, so "the point fell inside it" is a statement about the
band's width, not about the realization model.

**And this is the second consecutive out-of-sample failure.** The three `swap2` realizations gave
residuals of +0.00341, −0.00773 and −0.01902 against the same curve; adding them already took the
8-point rank correlation to +0.810. `cs700` is the first failure at a *new circuit*, i.e. on the axis
the curve was fitted to.

## 3. The sign rule survives — but `cs700` does not test it, as pre-declared

`cs700`'s contrast against its own `swap0.5` arm, paired over the six task seeds, is
**−0.00402 at −18.7σ** (unpaired −11.5σ). Negative, which is what the rule of the previous fire
requires below its separator.

But **the rule's separator was bracketed in [2.476, 5.040]**, and `cs700`'s effective rank of 2.806
sits *inside* that bracket. The previous fire said this in advance, and it is worth holding to: a
point inside the bracket cannot test it. The most `cs700` can do is narrow the bracket — it moves the
lower edge from 2.476 to **2.806**, so the separator is now in **[2.806, 5.040]** — and it leaves the
rule's coverage gap between 2.8 and 5.0 exactly where it was.

**And the gap is what the cs=800 realizations already falsified from above**: `rw3` at effrank 5.853
gives −0.00377 at −10.0σ, above the bracket where the rule demands positive. So the sign rule has
failed on the only side of the gap that has been probed, and `cs700` neither rescues it nor tests it.

## 4. What the sixth point changes about the sweep itself

The cross-size picture, now six points:

| topology | cs300 | cs400 | cs500 | cs600 | cs700 | cs800 | spread |
|---|---|---|---|---|---|---|---|
| `real` | 0.01902 | 0.01822 | 0.01934 | 0.02023 | 0.01982 | 0.01830 | **10.5%** |
| `swap0.5` | 0.02257 | 0.02065 | 0.02438 | 0.02627 | 0.02135 | 0.02317 | 24.3% |
| **`swap2`** | 0.05782 | 0.01762 | 0.03492 | 0.02404 | 0.01733 | 0.01237 | **166%** |

The structural point that has survived every retraction in this line is unchanged and is now measured
on six circuits: the two control topologies hold to 10.5% and 24.3% while `swap2` spans 166%, a factor
of 4.7 between its extremes. `swap2` is the unstable object; that has never been in question.

What the sixth point does change is the *coordinate*:

| quantity | at 5 points | at 6 points |
|---|---|---|
| Spearman(effrank, excess), `swap2` | **+1.000** | **+0.829** |
| exact permutation p, one-sided | 0.0083 | **0.0292** |
| five-point fit's in-sample max residual | 0.00296 | **0.00512** |
| Spearman(effrank, excess) with the realizations | +0.810 | **+0.767** |

The correlation is still marginally significant at six points, and it should be reported as such — but
it is no longer the clean 1.000 that motivated calling it a coordinate, and the fit's own residual
has nearly doubled, driven by this one point.

## 5. Where the C1 line stands

Three independent axes have now refuted the geometry reading, each pre-registered:

1. **cross-family slope** — 13.6σ apart (0.0047 ± 0.0009 for `swap2`'s realizations against
   0.0340 ± 0.0020 for ER's), with the circuit sweep's own 0.0206 matching neither, and no single
   monotone form fitting all three;
2. **out-of-sample prediction at fixed circuit** — the curve misses realizations inside its own
   fitted range, worst by 0.01902;
3. **the pre-registered sixth circuit point** — missed by 1.84× the band the previous fire
   committed to, at a residual 2.1× the fit's own goodness of fit;
4. and, alongside them, the **sign rule fails above its bracket** at −10.0σ.

`excess(swap2)` is not a stable quantity across circuits, no coordinate tried so far accounts for it,
and the honest scope for every number in this family remains what it was three fires ago: the
contrasts are statements about the particular graphs drawn. **The one thing that carries weight is
the structural contrast** — the Erdős–Rényi separation, a regime offset by a factor of eleven — for
which the realization check has now been done and passed.

## 6. Limits

- The `cs700` `swap0.5` and `real` arms are the same-seed, same-task-set controls, so the contrast is
  properly paired (18.7σ paired against 11.5σ unpaired).
- `cs700`'s `swap2` excess has the tightest sem in the sweep (0.00016), so its rejection of the
  band is not an underpowered one.
- The band's width (±0.0034) was itself partly chosen from a small sample, so "1.84× the band" should
  be read as "outside a band that was generous relative to the fit's own residual", not as a p-value.
  A proper interval on the 2-parameter fit at a new effective rank would be wider than ±0.0034, and
  the miss would then be less than 1.84× — which is why §4's rank correlations, not this ratio, are
  the numbers to carry.
- One circuit size remains unrun at `swap2` between the bracket's edges, so the sign rule's coverage
  gap is still exactly that: a gap, not a refuted interval.
