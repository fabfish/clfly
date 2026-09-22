# E80 — the fifth candidate is the first one that works, and it works for a reason the others could not: `projection_pressure`'s **absolute** spread ranks the draw spread at +0.767 and is not a size scalar

**Date:** 2026-09-23
**Script:** `experiments/e80_pressure_draw_spread.py`
**Artifact:** `runs/e80_pressure_draw_spread.json` (9 partitions × 6 draws × 3 task seeds, d = 1307)
**Context:** `2026-09-23-the-alignment-explains-six-percent.md` (e75), `2026-09-23-the-alignment-predictor-is-refuted.md` (e72), `2026-09-23-side-draw-sd-refutes-the-concentration-model.md` (e67)

---

## 1. Why this candidate is different from the four that failed

Four candidates for the control's draw spread have failed: group count (`e12`), concentration (`e67`),
the normalised alignment spread (`e72`) and the bare alignment's co-movement (`e75`). **Every one of them
is a subspace overlap of one kind or another**, and the two that came closest are the plainest
partition-size scalars.

`projection_pressure` is not a subspace overlap. It asks how much of the **exact filter's posterior
trajectory** a basis would discard — running that filter itself, whose prior trajectory is
basis-independent and therefore computable before any anchored filter exists — and it **weights the
discarded part by the task's measurement information `J_k`**, in the metric that makes it dimensionless.
The weighting is the whole point: without it the number would merely re-derive `constrained_fraction`.

The prediction, written before the run: the spread of `pressure` across control draws ranks the measured
draw spread of the control's *excess* at **Spearman ≥ +0.8**, with a correlation with **concentration
below +0.5**. Falsifier: a concentration correlation as high as +0.85, which is what `e72`'s normalised
alignment spread achieved while failing the target.

## 2. The result, and it splits

| candidate | Spearman vs measured draw sd | p | Spearman vs concentration | p |
|---|---|---|---|---|
| **absolute pressure sd** | **+0.767** | **0.016** | **+0.317** | 0.406 |
| relative pressure sd (`sd/mean`) | **+0.850** | **0.004** | +0.767 | 0.016 |
| pressure level (mean) | −0.650 | 0.058 | **−0.983** | **0.000** |
| concentration *(the failed scalar)* | +0.617 | 0.077 | +1.000 | 0.000 |

Neither form satisfies both pre-registered clauses, and **the way the relative form fails is the
interesting part**:

* the **absolute** spread passes the independence clause (+0.317, well under +0.5) and misses the target
  by 0.033 (+0.767 against +0.80), with p = 0.016;
* the **relative** spread hits the target exactly (+0.850, p = 0.004) and fails independence (+0.767).

**And the diagnostic says why: the pressure *level* is −0.983 with concentration — a near-perfect
monotone re-expression of it — so dividing the spread by the level manufactures the size correlation.**
The relative form's contamination is not evidence that pressure is a size scalar; it is evidence that its
*denominator* is one. That is the same structure `e72` found in the opposite direction: there the
*normalisation* (by a random subspace) collapsed the quantity onto span size, and here the
normalisation (by the level) collapses it onto concentration.

So the number to carry forward is the **absolute** one:

> The draw-to-draw spread of `projection_pressure` ranks the draw-to-draw spread of the control's excess
> at **+0.767 (p = 0.016)** over nine partitions spanning concentration 0.020–0.536, and is only
> **+0.317** with concentration and −0.433 with the pressure level.

**This is the first significant positive relationship this sub-line has produced in five attempts, and
the first candidate that is not a re-expression of partition size.**

## 3. What it says mechanistically, and why that is a real advance

The four failures together said: the draw spread is not the relabelled span's geometry against the task's
precision *subspace*. `e80` says what it *is*, at least at +0.767: it tracks **how much of the predicted
prior the projection discards, weighted by the task's measurement information**.

That is a different object in exactly the way the four failures were not: the alignment candidates all
used the task's **subspace** (which directions the drive occupies), whereas pressure uses the task's
**information** (`J_k`, how strongly each direction is measured). So the honest mechanism sentence for
the project's error bars is now:

> The matched-random control is one draw, its spread is a property of *(partition, tasks)*, and the part
> of it that is predictable at n = 9 is the projected-precision deficit — not the subspace geometry.

And it retro-explains the four failures: a subspace overlap cannot see `J_k`, and the draw spread is
about `J_k`.

## 4. Limits

- **Nine partitions and four candidate families tested on the same nine targets.** The p-values are
  nominal; with four candidates one at p = 0.016 is not a discovery on its own. What makes it more than
  that is that it is the *first* of five and that its independence from concentration was checked on
  the same data rather than assumed.
- **The absolute and relative versions are ±0.083 apart on the target**, i.e. indistinguishable at
  n = 9. The reason to prefer the absolute one is not its target score but its *diagnosed* independence,
  and that is an argument rather than a measurement.
- **The targets are measured, not exact.** Each of the nine draw sds comes from 3–8 draws
  (`e14`, `e17`, `e17b`, `e67`, `e74`), so the target itself carries 20–50% error and the ceiling on any
  predictor's observed ρ is below 1.
- **`projection_pressure` runs the exact filter**, which is the expensive part; six draws × three seeds
  × nine partitions is about eight minutes, so a wider partition set is affordable — which is the right
  next step before this is called a predictor rather than a lead.
- **The per-(draw, seed) pressures are kept** in the artifact (`per_draw_seed`), so the co-movement
  question `e75` asked of the alignment can be asked of the pressure without recomputing the expensive
  half — the mistake `e75`'s first version made and `e80` avoids.
