# E72 — the pre-registered alignment predictor is REFUTED, and it fails because the excess normalisation throws the task away

**Date:** 2026-09-23
**Script:** `experiments/e72_alignment_draw_spread.py`
**Artifact:** `runs/e72_alignment_draw_spread.json` (9 partitions, d = 1307, cs = 800, 6 task seeds)
**Context:** `2026-09-23-side-draw-sd-refutes-the-concentration-model.md` (e67), plan row `e72`, `2026-09-22-draw-sd-mechanism.md`

---

## 1. The prediction, and the result

`e67` refuted the project's one-scalar model of the control's draw spread, and the refutation came with
a mechanical explanation the scalar cannot express: **a relabelling preserves group sizes exactly**, so
`concentration = sum_g s_g^2 / d^2` is *identical* for every draw, and the only thing a draw changes is
*which* neurons share a group. That made the draw-to-draw spread of a partition's **task alignment** the
natural candidate, and it is computable with no filter. The prediction was written down before the run:

> over the nine partitions that have both a measured excess draw sd and a computable alignment spread,
> the alignment spread ranks the excess spread at **Spearman ≥ +0.8**, where concentration is
> non-monotone (0.325 → 9.3e-4, **0.498 → 2.2e-4**, 0.678 → 1.06e-3).
> **Falsifier:** `side`'s alignment spread exceeding pooled-min-2's while its excess spread is 4.3×
> smaller.

| | result |
|---|---|
| **Spearman(alignment spread, measured excess sd)** | **+0.283 (p = 0.46)** — predicted ≥ +0.80 |
| Spearman(raw alignment spread, measured sd) | **−0.500** (p = 0.17) |
| Spearman(mean alignment excess, measured sd) | +0.283 |
| **Spearman(concentration, measured sd)** | **+0.617 (p = 0.077)** — *the refuted scalar, on the same nine points* |
| critical \|ρ\| at n = 9, two-sided 0.05 | ≈ 0.683 |

**The prediction is refuted, and so is the named falsifier's alternative**: `side`'s alignment spread is
**0.371 against pooled-min-2's 0.071** (5.2× larger) while its excess spread is 4.3× *smaller*. The
falsifier fires.

## 2. Why it fails, which is diagnosable rather than mysterious

The candidate is not an independent quantity. It is very nearly a monotone re-expression of the
partition's **size**:

| pair | Spearman | p |
|---|---|---|
| alignment spread vs **concentration** | **+0.850** | 0.0037 |
| alignment spread vs **indicator-span dimension** | **−0.904** | 0.0008 |

So the alignment spread is, to a good approximation, "one over the span size", and it *inherits*
concentration's failure because it carries almost no information concentration did not.

**And the mechanism is visible in what the quantity is.** `alignment_of` reports `excess =
raw / chance`, where `chance` is the mean alignment the *same* partition achieves against random
subspaces of the same dimension. That normalisation was introduced for a good reason — a finer
partition has a larger indicator span, overlaps every subspace more, and scores higher for free, which
is why the first version of that function came out *anti*-correlated with the anchoring benefit. But a
random subspace of dimension `p` is a generic object, and "how much more than generic is this
partition's overlap" is dominated by how *concentrated* the span is, i.e. by the partition's size
structure. **The normalisation removes the free size advantage and, in this measurement, the task
information with it** — leaving exactly the quantity `e67` had already refuted.

The wide-span partition shows it most plainly: `side` has **four** groups, so the largest possible
movement per relabelling, hence the largest alignment spread of the nine (0.371) — and one of the
smallest excess spreads (2.16e-4).

## 3. The nine points, which are the first wide-range calibration the project has

| partition | concentration | span dim | alignment spread | **measured excess sd** |
|---|---|---|---|---|
| `cell_type` min 1 | 0.020 | 812 | 0.02368 | 6.80e-5 |
| `supertype` | 0.026 | 508 | 0.01032 | 8.35e-5 |
| `ito_lee_hemilineage` | 0.032 | 212 | 0.06902 | 4.16e-5 |
| `cell_class` | 0.171 | 12 | 0.07859 | 2.37e-4 |
| `cell_type` min 2 | 0.325 | 90 | 0.07102 | 9.29e-4 |
| `cell_type` min 3 | 0.395 | 51 | 0.04944 | 1.01e-3 |
| `cell_type` min 4 | 0.459 | 29 | 0.08057 | 6.13e-4 |
| **`side`** | **0.498** | **4** | **0.37128** | **2.16e-4** |
| `cell_type` min 6 | 0.536 | 12 | 0.15230 | 7.28e-4 |

## 4. What this says about concentration, which is not as dead as `e67` implied

`e67` refuted the one-scalar model on three points that sit close together in concentration
(0.325 / 0.498 / 0.678) and showed it mispredicts `side` by **4.8×**. On nine points spanning 0.020 to
0.536 it scores **+0.617**, and +0.617 at n = 9 is *below* the two-sided 0.05 critical value.

So the honest refinement is:

> concentration is a **weak global ordering** of the draw spread rather than noise — but it is not
> significant at the sample size available, it mispredicts the one partition whose behaviour the
> project's C1 claims lean on most (`side`) by a factor of five, and it is **non-monotone exactly in the
> 0.3–0.7 region where those claims live**.

That is a weaker statement than "the scalar is refuted" and it is the one the data support. What survives
of `e67` unchanged is the *local* refutation — the one that matters, because a budget or a σ is read off
a *pair of nearby rungs*, and that is the regime where the scalar fails.

## 5. Three candidates have now failed, and they fail the same way

| candidate | axis it really measures | Spearman with the draw spread |
|---|---|---|
| group count | partition size | none (the model that started the line, refuted by `e12`) |
| concentration | partition size (weighted) | +0.617, p = 0.077 |
| alignment spread | **inverse span size** | +0.283, p = 0.46 |

**All three are functions of the partition alone.** The draw spread is a property of the *(partition,
task family)* pair — it is how much the *excess* moves when the partition is relabelled, and the excess
is a filter quantity computed against the tasks. A partition-only scalar can only succeed if the task
dependence cancels, and in three attempts it has not.

**Which pre-registers the next candidate and its falsifier** (plan row `e75`): a quantity that is *not*
ratio-normalised against generic subspaces, namely the spread across draws of the **absolute** overlap
between the partition's indicator span and the task's own top-`r` spectral subspace — `||Q^T U_trunc||`
without the chance denominator — evaluated per draw and paired with the task draw rather than averaged
over it. **Prediction:** Spearman ≥ +0.8 with the measured draw spread, *and* Spearman with
concentration below +0.5, since it must carry task information the size scalars cannot. **Falsifier:** a
correlation with concentration as high as the alignment spread's +0.85.

## 6. Limits

- **Nine partitions, one circuit, one task family at one size** (d = 1307, cs = 800, support 80,
  q = 0.02, seed set 0–5). Spearman at n = 9 is a blunt instrument: the 0.05 critical value is 0.683, so
  only the two *diagnostic* correlations (0.850 and −0.904) and the refutation are firmly established;
  the difference between +0.283 and +0.617 is **not** resolved at this n.
- **The targets were measured with three task seeds for five of the nine points** (`e14`'s protocol) and
  eight draws for two (`e67`), while this run averaged over six seeds throughout. That makes the
  predictor *cleaner* than the target, so the observed correlations are if anything understated — it
  cannot rescue a +0.283 against a pre-registered +0.80.
- **`alignment_of` is imported from `e3`, not re-implemented**, deliberately and against the project's
  usual duplication convention: here the whole point is to use e3's definition of the excess, and a
  divergent copy would have silently tested a different quantity.
- **The null is 4 random subspaces per call**, not 8 as in `e3`. That makes the chance estimate noisier
  and so the excess noisier, which again works against the candidate rather than for it.
- **`e67`'s local refutation is untouched.** Nothing here says a budget may be computed from
  concentration; §4 says the scalar is a weak global ordering and §5 says why it cannot be trusted
  locally.
