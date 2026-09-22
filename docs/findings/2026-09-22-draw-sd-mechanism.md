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
- the `side → pool4` budget of K ≈ 1.4 **stands**, and the "coarse" column of the budget table did
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

## 6. Second and third measurements: the knee is between 0.02 and 0.325, and the plateau is flat

e14 has now measured two more partitions, and both land where they were predicted to:

| ``sum s^2/d^2`` | 0.006 | 0.020 | 0.325 | **0.395** | **0.459** | 0.678 | 0.754 |
|---|---|---|---|---|---|---|---|
| groups | 812 | 812 | 90 | **51** | **29** | 3 | 8 |
| draw sd | 9e-5 | 4e-5 | 9.3e-4 | **1.01e-3** | *(running)* | 1.06e-3 | 1.08e-3 |

**The plateau is flat.** Above ~0.33 the draw sd is 0.93, 1.01, 1.06, 1.08 ×1e-3 — a 15% spread over
a factor of two in concentration. So a single number, ~1.0e-3, is a good working value for any
concentration above a third, which is what the budget table assumed.

**The knee is bounded on one side only.** The measurements bracket it between 0.020 (4e-5) and 0.325
(9.3e-4) — a 25× rise across an interval with no point inside it. The two remaining runs (29 groups,
concentration 0.459; 12 groups, 0.536) are both on the flat side, so **e14 will not locate the knee**.
That would need points near 0.05–0.25, which no rung of the ladder supplies. Recording this because
the previous section said the knee-placement runs "will place it" and they will not.

**A side observation on the curve itself.** `min_size 3` is a granularity the ladder **skips** — it
goes 1, 2, 4, 8 — and it sits at constrained 0.6046, between `pool2` (0.674) and `pool4` (0.540),
with a delta of −0.00972. That is larger than either neighbour's (−0.00801 and −0.00884). It is from
3 seeds rather than 12, so it is not directly comparable and no claim is made from it; but it is one
more sign that the ladder's spacing is thinnest exactly where the effect is largest, which is the
reason the shape claims were withdrawn in the first place.

## 7. Correction: it *ranks* within a circuit, it does not *set the level*

§4 of this finding said the draw sd can be "predicted before any filter runs" from the
concentration. `e13` — the first full ladder with averaged controls, at d = 952 — contradicts the
strong form of that, and the docstring of `concentration` has been narrowed to match:

| concentration | draw sd at d = 1307 | draw sd at d = 952 |
|---|---|---|
| 0.006 / 0.020 | 3.9e-5 (n=2) | 9.8e-5 |
| 0.325 / 0.395 | 9.3e-4, 1.01e-3 | — |
| 0.678 / 0.690 | 1.06e-3 (n=2) | **4.94e-4** |
| 0.754 | 1.08e-3 | **8.40e-4** |
| 0.804 / 0.819 | — | 1.92e-3, 1.35e-3 |

Monotone **within** each circuit; a factor of two apart **between** them at a concentration near
0.7. So the defensible claim is:

> **concentration ranks the draw sd within a circuit; it does not set its absolute value.**

What that does and does not damage:

- **The `side` prediction is unaffected.** It interpolates on the d = 1307 curve, which is the
  circuit `side` lives in. The qualifier is about transferring the *number* to another circuit,
  which the prediction never did.
- **The budget table's "coarse" column is unaffected in practice, but for a weaker reason.** It used
  a single value (1.1e-3) for every coarse rung of *one* circuit, and the measurements on that
  circuit (9.3e-4, 1.01e-3, 1.06e-3) support it. The reason it works is that the rungs are all in
  one circuit, not that the value is universal.
- **The mechanism claim survives.** The rise with concentration is visible in both circuits; what
  fails is the calibration constant, not the axis.

Also worth recording from the same run: at d = 952 the ladder reaches concentration **1.0**, which is
a single group — the `Full` basis, whose excess is exactly zero by construction. `pool64` and
`pool128` are not granularity rungs at all there. `concentration` is a cheap way to detect that,
and its docstring now says so.

## 8. The d = 1307 curve is not even monotone, so the axis is only coarse-versus-fine

`e14`'s third run is `min_size 4`, which is **the `pool4` rung itself** (29 groups, constrained
0.5407 against the ladder's 0.5403 — the same partition). Concentration 0.459, and:

| concentration | 0.020 | 0.325 | 0.395 | **0.459** | 0.678 | (d = 1307) |
|---|---|---|---|---|---|---|
| draw sd | 3.9e-5 | 9.29e-4 | 1.01e-3 | **6.1e-4** | 1.06e-3 |

**That is non-monotone**: 1.01e-3 at 0.395 and 6.1e-4 at 0.459, a 40% drop in the middle of the
rise, from two runs of the same experiment. With 5 draws each measurement carries ~35% relative
error, so a 40% swing is within ~1.9σ of that — suggestive of real scatter rather than decisive
either way, and either reading damages the same claim.

So the axis has to be stated even more weakly than §7 did:

> **Concentration separates fine partitions from coarse ones — roughly two orders of magnitude —
> but it does not rank coarse partitions among themselves.** Across 0.325–0.678 the draw sd is
> 6.1e-4 to 1.06e-3, a factor of 1.7, with no ordering.

**What that means for the budget table: nothing, because the table used a constant.** Every coarse
rung was assigned ~1.1e-3 regardless of its concentration. That crudeness is what makes the table
robust — it is at the top of the observed range, so it *overstates* the required ``K`` rather than
understating it. The measurements now bracket the true value between 6.1e-4 and 1.06e-3, and at
6.1e-4 the claims get *easier*:

| claim | with 1.1e-3 (the table) | with `pool4`'s measured 6.1e-4 |
|---|---|---|
| `pool4` delta resolves from zero | 7.9σ | **13.7σ** |
| `side → pool4` | K = 1.28, σ at K=1 = 2.66 | **K = 0.81, σ at K=1 = 3.32** |

The second row moves the claim across the line: at the measured draw sd for `pool4` and the
predicted one for `side`, **`side → pool4` clears 3σ with the single draw the ladder already took**,
which is why it belongs in the "worth buying" list only for the sake of a second confirmation.

**And the `side` prediction survives for a better reason than interpolation.** It was ~1.0e-3 *by
interpolation at concentration 0.498*. But every coarse partition measured on d = 1307 — 0.325,
0.395, 0.459, 0.678 — lands between 6.1e-4 and 1.06e-3, so ~1.0e-3 is the right *order* for any
coarse rung on that circuit without any interpolation at all. The prediction is now supported by
the flatness of the range rather than by a curve fit through it.

## 9. The complete d = 1307 curve, and the number to actually use

`e14` has finished. All six points on the instrument circuit, each with its group count:

| concentration | 0.020 | 0.325 | 0.395 | 0.459 | 0.536 | 0.678 |
|---|---|---|---|---|---|---|
| groups | 812 | 90 | 51 | 29 | 12 | 3 |
| min_size | 1 | 2 | 3 | 4 | 6 | 32 |
| draw sd | 3.9e-5 | 9.29e-4 | 1.01e-3 | 6.13e-4 | 7.28e-4 | 1.06e-3 |
| draws | n=2 | 5 | 5 | 5 | 5 | n=2 |

Two of the six (`min_size 3` and `min_size 6`) are rungs **the ladder skips** — it goes 1, 2, 4,
8 — so this is the first look at those granularities as well.

**The coarse range has a factor of 1.7 of scatter and no ordering.** 6.13e-4 to 1.06e-3 across
0.325–0.678, with the minimum in the middle. Mean ≈ 8.7e-4, and the three middle points
(9.29e-4, 1.01e-3, 6.13e-4, 7.28e-4) differ from each other by more than the smooth trend would
suggest. Four independent runs of the same experiment, so this is not a single bad draw.

**So the number to use in a budget is a constant, and it is now chosen against four measurements
rather than one.** The budget table used 1.1e-3 for every coarse rung. That is above all four
measured coarse values (max 1.06e-3), so it **overstates** the required ``K`` — the safe direction.
Recording it as a deliberate over-estimate rather than as a fitted value matters, because the
temptation once a curve exists is to interpolate on it, and the curve does not order.

**`side`'s prediction is now supported three ways**: by interpolation (≈1.0e-3 at concentration
0.498), by the flatness of the coarse range (every coarse partition on this circuit lands in
6e-4–1.1e-3), and by the mechanism (an unbalanced partition with a 501-neuron largest group has the
same reshuffling exposure as the measured ones). None of the three is exact, and they agree.

## 10. What is still unmeasured

- **The knee.** Between 0.020 (3.9e-5) and 0.325 (9.29e-4) no point exists, so the rise's shape is
  unknown — it could be a step, a power law, or two regimes. It does not affect any budget, which
  needs only the coarse plateau, but it is the obvious next measurement and needs partitions the
  `cell_type` pooling cannot produce (concentrations of 0.05–0.25).
- **The d = 952 coarse range**, with more than 3 draws. Three draws is what made that curve's top
  end unreadable (§5), and it is the only cross-circuit comparison available.
- **`cell_class`** (concentration 0.171) and the annotation columns generally. Their draw sds are
  still interpolated across the knee, which is the one place the interpolation is load-bearing: it
  decides whether `wider-tasks/supertype` sits above or below the 2σ line in the predictor's
  matched-pair count (`2026-09-22-predictor-survives-draw-correction.md` §4).

## 10. `supertype`: the interpolation was wrong by 2×, and nothing changed

`e17b` measured the first fine-column draw sd directly — `supertype` at d = 1307,
concentration 0.0257, 3 seeds, 5 draws:

| quantity | value |
|---|---|
| **draw sd** | **8.4e-5** |
| interpolated prediction | 4.14e-5 |
| ratio | **2.0×** |
| per-draw control means | 0.01628, 0.01613, 0.01622, 0.01629, 0.01635 |

This is the **worst interpolation error so far** — against 1.26× for `cell_class`, 1.15× for
`pool4` and 1.18× for `pool2` — and it is in the direction that matters, since the predictor's
matched-pair count turns on `supertype` and `ito_lee_hemilineage`. So the obvious question is
whether the count moves. It does not:

| | resolvable pairs | correct sign | closest pair to the 2σ line |
|---|---|---|---|
| as published (interpolated) | 13 | **13/13** | baseline/`supertype` at 1.94 |
| with the `e17`/`e17b` measurements | 13 | **13/13** | baseline/`supertype` at 1.94 |

The reason is that `supertype`'s seed sem (0.0007–0.0016) is an order of magnitude larger than either
draw sd, so the draw term is negligible for that column and doubling it changes nothing to two
decimals. **The predictor's headline is indifferent to an error of this size in exactly the columns
it depends on.**

Two consequences:

- **The reliability claim needed correcting, not the science.** Plan rule 10 said the three measured
  columns "all landed within 45% of their predicted values". True of the three measured *then*, and
  false as a general statement the moment a fourth column was measured: the spread is now
  1.15×–2.0×. The rule has been updated.
- **A 2× error in `sd_draw` is not a 2× error in a conclusion.** Where the draw term dominates
  (coarse partitions) the interpolation has been accurate to 15–26%; where it has been off by 2×,
  the column is fine and the draw term does not matter. The two failure modes are disjoint, which is
  why the budget table's constant and the predictor's count are both safe.

`ito_lee_hemilineage` (concentration 0.032) is the second fine column and is still running; it is the
last one needed to close the knee for every column the predictor uses.
