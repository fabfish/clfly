# E21 — the contrast that refutes the interference mechanism does not replicate, and reverses

**Date:** 2026-09-22
**Script:** `experiments/e2_topology_gap.py --circuit-size 300 --seeds 3 --topologies real,swap0.5,swap2`
**Artifacts:** `runs/e21_e2_paired.json` (d = 952), `runs/e2_analytic.json` (d = 1307, published)

---

## 1. What was run and why

The previous fire audited the project's significances and found that `e2`'s adjacent-topology
contrasts use the **unpaired** formula on a comparison whose seeds are shared, and argued from a
variance decomposition that this made them **conservative**. The `e2_analytic.json` artifact predates
per-seed storage, so the argument could not be checked. `e21` re-runs the three topologies that carry
the refutation, with per-seed storage, at a smaller circuit — and it answers the conservatism
question, and then raises a much larger one.

## 2. The first two topologies replicate; the third does not

| topology | d = 952 (e21) | d = 1307 (published) | ratio |
|---|---|---|---|
| `real` | +0.01902 ± 0.00109 | +0.01830 ± 0.00115 | 1.04× |
| `swap0.5` | +0.02257 ± 0.00077 | +0.02317 ± 0.00031 | 0.97× |
| **`swap2`** | **+0.05782 ± 0.00122** | **+0.01237 ± 0.00011** | **4.67×** |

`real` and `swap0.5` agree between the two configurations to within 4%. **`swap2` is 4.67× apart**,
and the disagreement is `0.04545 ± 0.00122` — **37σ**.

This is not a noise issue in either direction. The per-seed values are:

- d = 952: `swap2` = 0.06017, 0.05606, 0.05723 (sd 0.00212)
- d = 1307: `swap2` = 0.01237 ± 0.00011 (sd 0.00019)

Both are tight. They are measuring different things, or the same thing on objects that differ.

## 3. The obvious confounds are controlled

**Rewiring strength is matched.** The swap rule preserves degree and edge count, and the achieved
`swap_fraction` is nearly identical at the two sizes:

| topology | d = 952 | d = 1307 |
|---|---|---|
| `swap0.5` | 0.611 | 0.614 |
| `swap2` | **0.912** | **0.924** |

So `swap2` perturbed 91–92% of the same targets at both sizes. The 4.7× difference is not a
difference in how much was rewired.

**Conditioning does not explain it — it behaves oppositely.** `cond(I − W)`:

| topology | d = 952 | d = 1307 |
|---|---|---|
| `real` | 88,605 | 81,286 |
| `swap0.5` | 24,246 | 41,368 |
| `swap2` | **13,773** | **108,308** |

At d = 952 `swap2` is the *best*-conditioned of the three; at d = 1307 it is the *worst*. And the
excess goes the other way in both: the best-conditioned `swap2` has the highest excess, the
worst-conditioned one the lowest. Conditioning tracks neither, so this is a third instance of the
project's recurring "the obvious quantity does not drive the penalty" — but here it leaves the
disagreement unexplained rather than resolved.

## 4. What this does to C1's refutation

C1's refutation rests on one contrast: **the excess falls from `swap0.5` to `swap2` by 32.7σ while
overlap doubles**, which is the opposite of what interference would do. At d = 952 the same contrast
**rises**, and decisively:

| contrast | d = 952 | d = 1307 |
|---|---|---|
| `swap0.5 → swap2` | **+0.03525** (21.8σ paired, 24.4σ unpaired) | **−0.01079** (32.7σ unpaired) |
| relative to `real` | 0.01902 → 0.05782, the penalty **nearly triples** | 0.01830 → 0.01237, the penalty **falls** |

So **at d = 952 heavy rewiring makes the diagonalisation penalty much worse, which is what the
interference hypothesis predicts**; at d = 1307 it makes it better, which is what refuted it. The
refutation is therefore **configuration-specific**, and the plan's C1 status — "the obvious mechanism
is refuted, decisively" — is stronger than the evidence supports.

The geometry replicates, so this is not a task-construction artefact: overlap rises with rewiring at
both sizes (d = 952: 0.122 → 0.457 → 1.209 × chance; d = 1307: 0.135 → 0.414 → 1.069).

## 5. The conservatism argument was wrong, in the same run

The audit inferred that the unpaired figure must be conservative because the shared task-draw
component makes `E[corr] > 0` by construction. The measurement:

| contrast | unpaired | **paired** | r |
|---|---|---|---|
| `real → swap0.5` | 2.7σ | 2.4σ | −0.216 |
| `swap0.5 → swap2` | 24.4σ | **21.8σ** | **−0.274** |

The correlation is **negative** at both contrasts, so the paired sem is 1.10–1.12× *larger* and the
unpaired figure is mildly **optimistic** — the opposite of the inference. With n = 3 a correlation of
−0.27 is not well determined, so this does not establish a negative sign either; what it establishes
is that the shared task-draw component is **not** large enough to make the conservatism safe to
assume. The audit's §3 conclusion should be read as *unresolved* for `e2` rather than conservative.

## 6. What is and is not established

**Established:** at matched rewiring strength and with both measurements tight, the `swap2` endpoint's
analytic excess differs by 4.7× between d = 952 and d = 1307, and the `swap0.5 → swap2` contrast —
the sole carrier of C1's refutation — **reverses sign**. Two configurations, one run each.

**Not established:** which configuration is representative. Two points cannot distinguish a
scale-dependence from a subsample-dependence, and the two runs differ in *which* neurons the circuit
contains (a 300 vs 800 neuron cap, not a nested refinement) as well as in size. Nothing here says the
d = 1307 result is wrong; it says it is not the whole picture.

**Not established either:** the mechanism. Conditioning behaves oppositely at the two sizes and
tracks neither excess. The honest state is that the `swap2` object is unstable across these
configurations for reasons that are not yet identified.

## 7. What to do about it

The refutation needs a **sweep over circuit size**, not a second opinion at one size. `e2` already
takes `--circuit-size`; the run is `--topologies real,swap0.5,swap2 --seeds 12` at three or four
sizes, which is ~1–2 h each at d ≤ 1307 and answers whether the sign flip is monotone in scale. Until
that exists, the plan's C1 status is downgraded to "refuted at d = 1307, **reversed at d = 952**",
and the paper's abstract says so.

## 8. Limits

- Three seeds per configuration. The `swap2` means are tight (sds 0.0021 and 0.0002) but the
  task-geometry *population* is sampled three times, so the population means carry an uncertainty the
  sems do not capture. The 37σ is a statement about these draws.
- `e21` ran three topologies rather than five, so `swap0.1` and `erdos_renyi` are not re-measured here;
  the Erdős–Rényi separation (152σ) is untouched by this finding and belongs to a different regime.
- The paired correlations are from n = 3, so §5 refutes the *inference*, not the sign of the
  population correlation.
- The d = 1307 artifact stores no per-seed values, so its contrasts could not be re-analysed paired;
  the published figures are quoted as published.
