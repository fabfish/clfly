# Scale robustness at d = 3150 — the small-circuit objection, partly answered

**Date:** 2026-09-22
**Script:** `experiments/e3_basis_selection.py --circuit-size 3000 --support 150 --seeds 2 --no-realized`
**Artifacts:** `runs/e3_large.json`

---

## 1. Why

Every headline result so far is at d = 1307, a circuit of the mushroom body, central
complex and antennal lobe. The obvious objection is that a 1300-neuron circuit is a
small object and the conclusions might be an artefact of its size. This re-runs the
core experiment (e3, the anchoring-basis comparison) at **d = 3150**, which is 2.4×
the neurons and ~14× the dense linear algebra per filter pass.

Task width was raised with it (support 80 → 150) to keep the rank fraction comparable:
150/3150 = 4.8% against 80/1307 = 6.1%.

## 2. Results

| rung | constrained (1307) | σ (1307) | constrained (3150) | **σ (3150)** |
|---|---|---|---|---|
| `side` | 0.501 | 12.93 | 0.502 | **11.87** |
| `ito_lee_hemilineage` | 0.967 | 2.61 | 0.955 | **3.28** |
| `cell_class` | 0.828 | 3.68 | 0.750 | **1.29** |
| `supertype` | 0.974 | 1.23 | 0.944 | 1.19 |
| `cell_type` | 0.979 | 0.22 | 0.952 | 0.28 |

> **Resolved (>2σ, biology better): 3/5 at d=1307, 2/5 at d=3150.**

Oracle analytic error at d=3150 is 0.04358, and the diagonal's excess is +0.01474 —
a 34% excess, matching the +33% at d=1307. **The primary magnitude result is
scale-stable.**

Three readings.

**`side` and `hemilineage` are robust.** The strongest rung stays overwhelming
(11.9σ vs 12.9σ) and the hemilineage rung is if anything stronger at the larger size
(3.28σ vs 2.61σ). Those two survive the scale change.

**`cell_class` does not.** It falls from 3.68σ to 1.29σ. Its `constrained_fraction`
also shifts (0.828 → 0.750), because proportional subsampling on a larger circuit
gives a different group-size distribution — so this is not purely a scale effect, it
is a slightly different basis. Either way, on the present evidence `cell_class` is
**not** a scale-robust rung and should not be relied on.

**The two null rungs stay null.** `supertype` and `cell_type` are the two most
constrained bases in both circuits (0.94–0.98) and neither resolves at either size,
exactly as the granularity account predicts.

## 3. The predictor is scale-robust

| scale | Spearman vs analytic excess | matched-pair signs |
|---|---|---|
| d = 1307 | +0.982 | 5/5 |
| **d = 3150** | **+0.991** | **5/5** |

The predictor's performance is essentially identical at 2.4× the neurons, which is
the strongest evidence yet that it is capturing a real structural property rather
than fitting the particular circuit it was built on. Together with the five
out-of-sample conditions in `e6` (task width, drift, topology, size), the predictor
has now been evaluated on six conditions it was not tuned on, with sign agreement
29/30.

## 4. What this changes

The paper's claim is narrowed and sharpened. Instead of "biological layouts beat
matched random ones at 3 of 5 rungs", the defensible statement is:

> **Two biological rungs — the coarsest structural split (`side`) and the
> developmental lineage (`ito_lee_hemilineage`) — beat size-matched random partitions
> at both circuit scales tested, up to 11.9σ. A third (`cell_class`) does so only at
> the smaller scale and is not scale-robust.**

That is a weaker claim than the previous fire's 3/5 and a better-supported one. The
predictor, by contrast, is unchanged and remains the strongest positive finding.

`docs/paper/clfly-v1.md` §4.3 has been updated to this form; §7's limitations now say
which rungs are scale-robust and which are not, rather than reporting a single size.

## 5. Cost and consequence

One d=3150 run with 11 bases and 2 seeds cost ~48 minutes. At d=1307 the same run is
~7 minutes. That ratio (≈7×) is the practical limit on how far this can be pushed:
the exact oracle is O(d³) per filter pass, so d ≈ 3000 is roughly the ceiling at this
budget, and the "why not the whole brain" question remains answered by conditioning
(§3.3 of the paper) rather than by choice.

The cheaper route to more statistical power is more seeds at d=1307, where a run is
7 minutes. Since the analytic estimator's sem is dominated by the task-geometry draw
(sd ≈ 0.0005–0.0021 at d=1307), and seeds are the only way to average that, the
obvious next step is a 15–20 seed run at d=1307 rather than a further push on d.
