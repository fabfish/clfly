# The base family's λ response saturates at 3e-2, and the matched λ separates it from the wiring family

**Date:** 2026-09-24
**Script:** `experiments/e165_base_lambda_ladder.py` — analysis only, no runs. Artifact:
`runs/e165_base_lambda_ladder.json`.
**Artifacts read:** `runs/e161_r32_base_ewc_lam1.json` (λ = 1.0, forty seeds, the run `e161` registered),
`runs/e141_r32_ewc_lam3e-4.json`, `..._lam3e-2.json`, `..._lam3e-1.json`, `runs/e133_r32_naive_ewc_40reps.json`
(the control, and the λ = 3e-3 rung), `runs/e140_r32_methods_plastic_40reps.json` (the control's own control) and
`runs/e153_r32_overlap1_methods_40reps.json` (the wiring family at the same λ).

---

## 1. `e161`'s registration, read

| | registered | measured |
|---|---|---|
| **P1**, direction | the λ = 1.0 arm is **worse than `naive` on forgetting** | **+0.0091** — the wrong way, at **0.91σ** |
| **P1**, cost | a newest-task cost **larger than 0.0313** | **−0.0719**, at **13.91σ** |
| **falsifier** | it beats `naive` at **≥ 2σ** | **does not fire** |

**P1 holds**, in direction on both halves and in resolution on the cost half only. The two halves differ by a
factor of fifteen in resolution, and that gap is the finding rather than a caveat: **at the top of the λ range the
base family's penalty is a plasticity cost and nothing else** — the stability half is 0.91σ and the cost half is
13.91σ, which is the **most resolved quantity in the whole ladder**.

## 2. Five rungs, 3.5 decades, forty paired seeds at every one

`ewc` against its own `naive` (the same configuration; `e160` derives `lam` as a field `naive` cannot read):

| λ | `ewc` forgetting | vs `naive` | resolution | newest-task cost | resolution |
|---|---|---|---|---|---|
| 3e-4 | 0.0396 | **−0.0354** | **4.27σ** | −0.0297 | **6.47σ** |
| 3e-3 | 0.0654 | −0.0096 | 1.21σ | −0.0526 | 6.63σ |
| 3e-2 | 0.0810 | +0.0060 | 0.58σ | **−0.0755** | 9.45σ |
| 3e-1 | 0.0846 | +0.0096 | 0.85σ | −0.0729 | 9.00σ |
| **1.0** | 0.0841 | +0.0091 | 0.91σ | −0.0719 | **13.91σ** |

**`naive` at the same configuration: forgetting 0.0750, newest task 0.9667.**

**And the adjacent rungs, paired, are what turn that table into a shape:**

| step | forgetting | resolution | newest task | resolution |
|---|---|---|---|---|
| 3e-4 → 3e-3 | **+0.0258** | **3.74σ** | **−0.0229** | **2.97σ** |
| 3e-3 → 3e-2 | +0.0156 | 1.60σ | **−0.0229** | **2.84σ** |
| 3e-2 → 3e-1 | +0.0036 | **0.36σ** | +0.0026 | **0.27σ** |
| 3e-1 → 1.0 | **−0.0005** | **0.05σ** | +0.0010 | **0.11σ** |

**Every resolved movement is at or below 3e-2, and above it two tenfold increases move neither axis** — the
forgetting step is +0.0036 then −0.0005, the cost step +0.0026 then +0.0010, all under **0.4σ**. So the base
family's λ curve is not a curve at the top, it is a **step**, and the step is finished before the top of the
sweep: **the penalty's net effect on this family is decided in the decade between 3e-3 and 3e-2, and λ = 1.0 is
the same regime as λ = 3e-2 extrapolated, not a new one.**

**The ladder's two ends are opposite regimes, and both are resolved.** At 3e-4 the penalty **wins on both
metrics** (−0.0354 at 4.27σ on forgetting, and its cost is the *smallest* in the ladder at 0.0297) — which is
`e141`'s floor-is-the-optimum result — and at 3e-2 and above it **loses on both**. **The falsifier's shape is
therefore what the ladder's bottom rung looks like**, which is exactly why the registration's own question needed
a matched λ rather than a level.

## 3. The control, and the control's own control

`e161` was registered with no `naive` arm of its own, so the control is `e133`'s forty-replicate row — and the
artifact that makes that safe is `e140`'s plastic arm, which carries the **same two arms at λ = 3e-3** under a
config differing from `e133`'s in exactly one key (`anchor_bias`, absent from the older artifact). Measured:
**bit-identical across all forty replicates on both axes, `naive` and `ewc` alike** (`e165` asserts this).

That is worth its own sentence for two reasons. It is rule 45's floor met on **the arms the paper's headline
numbers use**, at forty replicates rather than five — the strongest instance of exact reproduction in the corpus.
And it is a pair of artifacts from **two schema epochs** that is bit-identical on the arms whose code did not
change, which is `e163`'s epoch result read from inside: the movement there was in `replay` and the block arms,
and these two arms are untouched across the same date boundary.

## 4. The matched λ: what differs between the families

Both families at **λ = 1.0**, each against its own `naive`, on the same forty seeds:

| family | its own `naive` | `ewc` gain over `naive` | resolution | newest-task cost | resolution |
|---|---|---|---|---|---|
| base (`input_overlap` 0.0) | 0.0750 | **−0.0091** (loses) | 0.91σ | −0.0719 | 13.91σ |
| wiring (`input_overlap` 1.0) | 0.1068 | **+0.0370** (gains) | **3.68σ** | −0.0276 | 4.65σ |

**And the interaction — the wiring family's gain minus the base family's, paired within seed, which is the
quantity the registration needs and the levels cannot give:**

- forgetting: **+0.0461 ± 0.0131 = 3.52σ**, 8 of 40 seeds negative;
- newest task: **+0.0443 ± 0.0077 = 5.79σ**.

**So at the same λ the two families are separated on both axes and in opposite directions**: the wiring family's
penalty buys stability at 3.68σ where the base family's buys a plasticity cost 2.6× larger and no resolved gain
at all. This is the number `e153`'s accident created the need for and `e161` was registered to supply, and it
closes the *measurement*: the two families are different objects at matched λ, not one object at two levels.

## 5. What this cannot settle

- **The turn is an interval, not a point, and on the forgetting axis it is not resolved** — 3e-3 → 3e-2 is
  **1.60σ** on forgetting against **2.84σ** on the cost, so "the curve turns between 3e-3 and 3e-2" is what the
  data support and "the turning point is 1e-2" is not.
- **The saturation is in the means, not in the resolution**: the top rung's cost σ *grows* (9.45σ at 3e-2,
  9.00σ at 3e-1, **13.91σ** at 1.0) while its mean is flat, so "the cost saturates" is a statement about
  `|Δ| < 0.004` over two tenfold steps and the resolution is the paired sem shrinking, not the effect moving.
- **Both accounts of §4 survive.** *The wiring family tolerates more* and *the wiring family has more to remove*
  predict the same interaction — the second because a larger `naive` forgetting mechanically offers more to
  recover and may spend a different share of the penalty's gradient on plasticity. Separating them needs the
  **naive level varied within a family** (noise, class count, task count) or a third family whose `naive` sits
  between 0.0750 and 0.1068, and the record has neither.
- **Two families and one read-out (32), three tasks, one seed stream.** The families' configs differ in
  `input_overlap` alone, which is the strongest form available here, but it is still two artifacts rather than a
  manipulated axis inside one.
- And the λ = 1.0 wiring point is `e153`, whose provenance is an accident of a paraphrase (rule 44) — sound
  numbers, accidental existence.
