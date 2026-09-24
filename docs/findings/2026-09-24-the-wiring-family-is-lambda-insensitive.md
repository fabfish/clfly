# The wiring family is λ-insensitive over two and a half decades, and its block arms gain stability there

**Date:** 2026-09-24
**Script:** `experiments/e162_wiring_lambda_step.py` — analysis only, no runs. Artifact:
`runs/e162_wiring_lambda_step.json`.
**Artifacts read:** `runs/e144_r32_overlap1_methods_40reps.json` (λ = 3e-3) and
`runs/e153_r32_overlap1_methods_40reps.json` (λ = 1.0) — **the same four arms, the same family, the same forty
seeds**, so every step below is paired and the only manipulated field is `lam` (which `e160` derives that `ewc` and
both block arms read and `naive` does not — hence the control).

---

## 1. The step, and its control

| arm | forgetting, 3e-3 → 1.0 | resolution | newest-task accuracy, 3e-3 → 1.0 | resolution |
|---|---|---|---|---|
| **`naive`** — *the control* | **0.0000** | **exactly zero** | **0.0000** | **exactly zero** |
| `ewc` (diagonal) | +0.0068 | **0.62σ** | +0.0021 | **0.33σ** |
| `ewc-block` (biological) | **−0.0201** | **2.03σ** | **−0.0266** | **4.29σ** |
| `ewc-block-rand` (its control) | −0.0112 | 1.09σ | **−0.0219** | **4.19σ** |

**The control is exact**, which is this design's own manipulation check: `naive` cannot read `lam`, and it does not
move at the last digit — so the differences above are the field's effect and nothing else.

**And each arm against its own `naive`, at both λ:**

| λ | arm | forgetting | resolution | newest-task | resolution |
|---|---|---|---|---|---|
| 3e-3 | `ewc` | −0.0437 | **4.73σ** | −0.0297 | 4.57σ |
| 3e-3 | `ewc-block` | −0.0234 | 2.26σ | −0.0047 | **1.10σ** |
| 3e-3 | `ewc-block-rand` | −0.0216 | 2.48σ | −0.0026 | **0.65σ** |
| **1.0** | `ewc` | −0.0370 | **3.68σ** | −0.0276 | 4.65σ |
| **1.0** | `ewc-block` | **−0.0435** | **4.21σ** | −0.0313 | 5.60σ |
| **1.0** | `ewc-block-rand` | **−0.0328** | **3.44σ** | −0.0245 | 4.60σ |

## 2. Two results, and the second is the inverse of the base family's

**First, the diagonal does not care.** A **333-fold** increase in λ — from 3e-3, near the base family's own
optimum, to the runner's default — leaves the diagonal's forgetting and its newest-task accuracy **unmoved on both
axes** (0.62σ and 0.33σ). **On the base family one step of the ladder (3e-4 → 3e-3) already worsens both axes with
both resolved** (+0.0258 at 3.74σ and −0.0229 at 2.97σ), and λ = 3e-2/3e-1 are each dominated by seven of the
other eight arms in the plane. **So the same knob that is the whole story on one family is a dead knob on the
other, over a range 2.5 decades wide.**

**Second, the block arms are the ones that respond, and they respond by *gaining* stability.** Between the two λ,
the biological block arm's margin over `naive` grows from **2.26σ to 4.21σ** and its matched-random control's from
**2.48σ to 3.44σ** — while *both* acquire their **first resolved plasticity cost** (−0.0266 at 4.29σ and −0.0219 at
4.19σ), where at λ = 3e-3 they paid nothing (1.10σ and 0.65σ). **So on this family the strongest penalty the
record holds is better on both counts than the weaker one for the coarse partitions**, and the diagonal is simply
flat — which is the opposite of the base family, where the top of the swept range is dominated *because* of the
plasticity axis.

**And that gives `e144`'s family result its mechanism-shaped form**: the diagonal's advantage over `naive` is
**4.73σ** on this family at λ = 3e-3 against **1.21σ** on the base family, and here it **persists at 3.68σ when λ
is 333× larger** — so what differs between the families is not where the optimum sits but **how much of λ's range
is usable**, which is what the λ = 1.0 point measures.

## 3. What this cannot settle

- **Two λ per family**, five-fold and 333-fold apart, and the families' ranges do not overlap (the base family's
  top swept λ is 3e-1): **the comparison is "the wiring family at 1.0" against "the base family's top swept λ"**,
  and `e161` — the base family's own λ = 1.0, registered and running — is the matched-λ arm that closes it.
- **The wiring family has exactly one 40-replicate λ = 1.0 table**, and it exists because a paraphrase omitted
  `--lam` (rule 44); its numbers are sound and its provenance is an accident.
- **One read-out (32), three tasks, one seed stream**, and the newest-task axis is one task — where the block arms'
 *first* resolved cost appears at the top of the range, so the shape of that cost's growth with λ is one point.
- And **the block arms' λ step is 2.03σ and 1.09σ on forgetting** — resolved for the biological one and not for its
  control, so "the block arms gain stability with λ" is one-and-a-half of two arms on that axis.

---

## 4. Checked the same day, and the column stands: the unrecorded draw was reconstructible

`e168` found that the two artifacts this section's block-rand column is computed from **do not both say which
matched-random partition they drew**: `e144` (λ = 3e-3) carries no `partition_draw` at all, while `e153` (λ = 1.0)
records `000b42be6ba2`. The control is a **population** and one draw is one **sample** (rule 10), so the pair's two
sides were not *known* to be one sample — and the corpus can measure how much that could matter, because `e144`'s
own draw 1 and draw 2 are on disk as two 40-seed runs differing in nothing else: **two samples of this family's
control differ by 0.0138 on forgetting (1.33σ) and 0.0068 on the newest task (1.48σ)**.

**The identification was then recovered rather than assumed, and the draw is the same on both sides:**

- `e144`'s process began **around 09:57** (`timing_s` = 15474 s = 4.30 h, file written at 14:18), i.e. **24
  minutes before `5a0f06e` added `--partition-seed` at 10:21** — which is why an artifact newer than that commit
  has no `partition_seed` in its `config`;
- the pre-flag call site is `random_matched(bio, np.random.default_rng(args.seed0))`, and the flag defaults to the
  same value, so `e144` drew seed 0;
- `random_matched`'s body is byte-identical to the version that introduced it, and **rebuilding the draw from the
  recorded fields reproduces all three recorded fingerprints exactly** — seed 0 gives `000b42be6ba2`, which is
  `e153`'s own value.

**So the two sides are one sample and the block-rand column needs no correction.** What the measurement above
therefore does is *bound the risk that was taken*: had the draws differed, the forgetting column (step 0.0112,
1.09σ, against a 0.0138 draw difference) would have been uninterpretable, while the newest-task column (**−0.0219
at 4.19σ, 3.2× the draw**) would have survived. **The margin rows equal the step rows because `naive` is
bit-identical across this pair** (the design's own control, step 0.0000).

**And the biological block arm never depended on the draw at all**: `ewc-block`'s partition comes from
`circ.labels[basis]` through `from_labels`, with no seed anywhere in it — the draw enters only the `rand` branch.
So of the two block arms this section reports, only its matched-random control's column was ever exposed, and that
is the one `e168` checked
(`docs/findings/2026-09-24-the-random-control-is-a-sample-and-31-of-38-artifacts-do-not-say-which.md`).
