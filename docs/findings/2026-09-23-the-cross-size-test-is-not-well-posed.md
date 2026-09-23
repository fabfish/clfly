# E86 — the spread statistic's cross-size test is not well-posed: the same nine labels are **different partitions** at every size

**Date:** 2026-09-23
**Script:** `experiments/e86_spread_at_other_sizes.py`
**Artifacts:** `runs/e86_drawsd_cs{300,1500}_*.json` (d = 952 complete, d = 1874 partial at 5 of 9), `runs/e86_spread_at_other_sizes.json`
**Context:** `2026-09-23-pressure-spread-predicts-the-draw-spread.md` (e80), `2026-09-23-the-mechanisms-two-halves.md` (the firing falsifier), `2026-09-23-the-pressure-mechanism-at-three-sizes.md` (e82)

---

## 1. What the pre-registration assumed, and what is false about it

`e80` found at d = 1307 that the **absolute** draw-to-draw spread of `projection_pressure` ranks the
measured draw spread of the control's excess at **+0.767 (p = 0.016)** while correlating only +0.317 with
concentration. `e86` was pre-registered to check that at two more sizes, predicting **≥ +0.70 and beating
concentration at each**. The plan's row states the assumption it rests on without noticing it: *the same
nine labels*.

**The labels are the same and the partitions are not.** A pooling that leaves 29 `cell_type` groups at
d = 1307 leaves a handful at d = 952, so the nine partitions each label names are — at every size —
different objects. Measured, for the nine targets actually run:

| size | concentration range of its nine partitions |
|---|---|
| d = 952 | **0.006 to 0.754** |
| d = 1307 | 0.020 to 0.536 |
| d = 1874 | 0.034 to 0.324 |

So the first step of the "replication" is a comparison between a set with four partitions beyond 0.69 and
a set whose coarsest is 0.536. **A rank correlation over "the same nine rows" is not comparing like with
like**, and the overlap of all three ranges (0.034–0.324) contains enough rows at only one size.

## 2. The result at d = 952, where the test is complete

| candidate | Spearman vs measured sd | p | Spearman vs concentration | partial, given concentration |
|---|---|---|---|---|
| **absolute pressure sd** | **+0.412** | 0.271 | +0.160 | **+0.509** (p = 0.197) |
| relative pressure sd | +0.882 | **0.002** | **+0.950** | +0.531 (p = 0.176) |
| concentration | **+0.832** | **0.005** | +1.000 | — |

The absolute pressure spread is **below the pre-registered +0.70 and well below concentration's +0.832** —
the falsifier fires. The form that does score well, the relative spread at +0.882, correlates **+0.950 with
concentration**, and the sentence that stood here called it a size restatement on the strength of that
number alone. **Partialling concentration out of both ranks does not support that inference as cleanly as
it was stated** — the relative form keeps **+0.531**, which is *above* the absolute form's +0.509 and is not
what a restatement should produce. But the partial is the wrong instrument for a variable this coupled to
the confound: at ρ = +0.950 the relative form's rank residual has almost no variance left, so the ratio is
taken on a small denominator — the fragile-denominator failure `e72` was diagnosed with — and at d = 1874
the same quantity reaches ρ = **+1.000** with concentration on five rows, where the residual is only what
rounding failed to remove. So what these nine points support is the weaker statement: **the relative form is
not distinguishable from concentration by rank correlation, raw or partial**, and neither form's partial
here is resolved (p = 0.20, 0.18). The instrument that settles it is the one `e92` supplies — cells whose
concentration is **set** rather than found — and it scores both forms.

## 3. And *why* it fires, which is the part worth keeping

Restricting to the fine end answers it. The d = 952 nine are **bimodal**: four rows sit at concentration
0.690–0.754 with measured sds of 2.96–3.54e-3, and five sit at 0.006–0.159 with 0.9e-4–1.2e-3.
`cell_type` min 4 and min 6 there are not merely the same partition — they are the **same run**, giving
byte-identical rows, because the same pooled labels and the same control seed produce the same
permutation.

| subset at d = 952 | absolute pressure sd | concentration | relative sd |
|---|---|---|---|
| all nine | +0.412 | **+0.832** | +0.882 |
| nine minus the exact duplicate | +0.476 | +0.881 | +0.905 |
| **fine end only (conc < 0.6, n = 5)** | **+0.900** (p = 0.037) | **+0.900** (p = 0.037) | +0.900 |

**Within the fine end all three candidates tie at +0.900.** So the reversal is not the pressure spread
failing to track the excess; it is a **bimodal design in which four near-duplicate coarse rows occupy four
of the nine ranks at the top of both orderings** — which concentration captures by construction, since the
clusters *are* its levels, and which contributes almost no discriminating information while dominating a
nine-point rank correlation.

That makes the d = 952 failure **not a clean refutation of `e80`** and not a confirmation either: it is a
test whose partition set does not match the one the claim was made on.

## 4. What this leaves, and the d = 1874 half

`e86`'s d = 1874 targets are **5 of 9 complete** (the four named rungs are still running) and the partial
row is therefore not read as a verdict:

| size | n | absolute pressure sd | vs concentration | beats concentration |
|---|---|---|---|---|
| d = 952 | 9 | +0.412 | +0.832 | no |
| d = 1307 | 9 | **+0.767** | +0.617 | yes |
| d = 1874 | **5** | +0.500 | +0.300 | yes, but n = 5 and neither reaches +0.70 |

**The standing position on the spread statistic is therefore: one complete size in its favour (d = 1307,
where it was found), one complete size against (d = 952), and one partial — and none of the three is over
the same partitions as any other.** Combined with `e87`'s finding that the *co-movement* is the robust half
(5.15σ under the shared-draw correction), the honest summary is:

> The **explanatory** claim about `projection_pressure` — the draw spread is about the precision-weighted
> projected deficit rather than subspace geometry — is supported, by the co-movement, at three circuit
> sizes. The **predictor-shaped** claim — the size of pressure's variation ranks the size of the excess's,
> better than a size scalar does — is supported at exactly one circuit size, and the design that would
> test it across sizes has never been run.

## 5. The design that would test it, pre-registered

The flaw is mechanical and the fix is the same in each case: **choose partitions by concentration, not by
label, and use the same concentration grid at every size.** Concretely, for each size, build a set of
partitions whose `constrained_fraction` (or `sum_g s_g^2/d^2`) falls in a fixed set of bins, so that
"partition *i*" means the same region of partition space everywhere. That also removes the bimodality,
since binning forces the coarse end to be sampled at several levels rather than in one cluster.

**Prediction:** on a concentration-matched grid the absolute pressure spread beats concentration at every
size, and its ρ is stable to ±0.15 across sizes. **Falsifier:** a size where it again loses to
concentration, which — with the design flaw removed — would be a genuine refutation of the predictor-shaped
claim rather than an artefact of which partitions were labelled the same.

## 6. Limits

- **d = 1874 is 5 of 9**, and its `rho_conc` of +0.900 is computed on those five. The row is reported for
  completeness and explicitly not read as a verdict.
- **The fine-end subsets are n = 5.** Every correlation in §3 is on 5–9 points, where the two-sided 0.05
  critical value is 0.683 at n = 5 and 0.9 at n = 5 one-sided; the "all three tie at +0.900" is therefore
  a statement that *no* candidate resolves there, not that they agree closely.
- **The concentration ranges are of the *biological* rungs, not of their controls.** A matched-random
  control has the same group sizes and so the same concentration by construction, so the range statement
  transfers, but the numbers quoted are the biological rungs'.
- **This is the third time in this line that the same latent assumption has bitten**: `e66` found that two
  arms of a near-diagonal partition co-move (making an unpaired sem 27× too large), `e73` found that the
  ladder's own `pool32` and `pool64` are one partition, and now `e86` finds that the same nine labels are
  different partitions at different circuit sizes. All three are the same question — *what is actually
  being compared?* — asked of a design that had not asked it.
