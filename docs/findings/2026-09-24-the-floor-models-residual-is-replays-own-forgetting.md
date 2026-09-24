# The floor model's residual is `replay`'s own forgetting, and it is measurable in every configuration

**Date:** 2026-09-24
**Artifact:** `runs/e155_r128_naive_replay.json` — the **read-out-128** arm of `e155`, landed; the read-out-700 arm
is still running. Comparator: `runs/e116_r128_40reps.json` (that read-out's `naive` at forty replicates).
**The registration** is `docs/findings/2026-09-24-the-floor-model-across-the-readout-axis-registered.md`, committed
before the run: **C0** both new `naive` rows must be per-replicate identical to `e116`'s; **P1** the margin lies
within 2σ of its own baseline's forgetting (**−0.0370 ± 0.0051** at this read-out); **falsifier** more than 2σ
away, with the channel-share reading (**−0.89 × 0.0370 = −0.0329**) named as the sharper alternative. **And the
registration stated in advance that this arm cannot separate the two** — their predictions are 0.0041 apart,
inside each other's 2σ windows — so it is a *generalisation* test; the 700 arm is the discriminating one.

---

## 1. The reading

| | forgetting | newest-task accuracy | mean accuracy |
|---|---|---|---|
| `naive` (`e155`, read-out 128) | **+0.0370** | 0.9500 | 0.9313 |
| **`replay`** | **−0.0096** | **0.9594** | **0.9665** |
| `naive` (`e116`, same read-out) | +0.0370 | 0.9500 | 0.9313 |

| control / claim | result |
|---|---|
| **C0 — the `naive` row against `e116`'s** | **per-replicate identical, worst difference 0** (forgetting and accuracy): a second execution of that arm reproduces it exactly |
| **the margin: `replay − naive`** | **−0.0466 ± 0.0058 = 8.07σ** |
| **P1 — within 2σ of the floor model's −0.0370** | difference **−0.0096 ± 0.0077 = 1.25σ** → **P1 HOLDS** |
| the channel reading, −0.0329 | difference −0.0137 ± 0.0077 = **1.78σ** → not rejected either |
| **C1 — replay's own forgetting near zero?** | **−0.0096**, i.e. *negative*: replay ends up **better** on the old tasks than it was right after learning them |
| the newest task | replay − naive **+0.0094 at 1.96σ** |

**So the arm generalises (P1 holds) and refuses to discriminate, exactly as registered** — the floor model is
1.25σ away and the channel reading 1.78σ away, and neither is rejected at forty seeds. That is the outcome the
registration predicted for this arm, and it is not a null: the margin is 8.07σ and the question was which model
predicts it.

## 2. And the residual is not noise — it is `replay`'s own forgetting, in all five configurations

The registration's C1 turned out to be the finding. **`replay`'s own forgetting is not zero here, and its value
*is* the model's error, arithmetically**: the margin is `replay_own − baseline_own`, so

    |margin| / baseline = 1 − replay_own / baseline

and the ratios this project has measured are exactly that expression:

| configuration | baseline's forgetting | **`replay`'s own forgetting** | margin | ratio | `1 − replay_own/baseline` |
|---|---|---|---|---|---|
| base family, read-out 32 | +0.0750 | **−0.0034** | −0.0784 | 1.045 | 1.045 |
| shared-input family | +0.1068 | **+0.0083** | −0.0984 | 0.921 | 0.922 |
| base family, channel frozen (`e140`) | +0.0227 | **+0.0018** | −0.0208 | 0.918 | 0.921 |
| base family, channel frozen (`e135`, 5 reps) | +0.0250 | **−0.0042** | −0.0292 | 1.17 | 1.17 |
| **base family, read-out 128** | **+0.0370** | **−0.0096** | **−0.0466** | **1.261** | **1.259** |

**So the "floor model" is not a fitted regularity with a ratio near 1 — it is an identity in which the only free
quantity is replay's own forgetting, and that quantity is small and signed in every configuration: between
−0.0096 and +0.0083 across five of them.** The model's real content is therefore **a bound on `replay`'s own
forgetting**, which is the paper's own sentence (*replay drives the forgetting to zero or below*) stated
quantitatively; and the family difference that motivated the whole question — the shared-input family's *larger*
margin — is the baseline's forgetting being larger, with replay pinned near zero.

**That relocates the claim rather than confirming it.** The `e148` finding asked whether replay's advantage is
proportional to the *unpenalised channel's share*; the answer is no, and the reason is that it is not proportional
to anything about the baseline beyond its total: **the margin is the baseline's forgetting minus a replay term of
magnitude ≤ 0.01.** A model with a term that small cannot be distinguished from "the margin is the baseline's
forgetting" at forty seeds — which is why both readings survived this arm.

## 3. What this cannot settle

- **The discriminating arm is still running.** Read-out 700 has a baseline forgetting of **+0.0221** and an
  unmeasured channel share; the registration says that at a share near 60% the channel reading predicts −0.0133
  against the floor model's −0.0221, **0.0088 apart ≈ 2.2σ**, so that arm is where the question can be decided.
- **One read-out per point, one circuit, three tasks, one seed stream**; the identity in §2 is arithmetic, and
  what is measured is the size of `replay`'s own forgetting, which is a property of *this* suite.
- **The identity has no explanatory content by itself** — what it does is move the question from *"why is the
  margin what it is"* to *"why is replay's own forgetting ≤ 0.01"*, and that second question is the paper's
  central one about content memory, not something this table answers.
- And the C0 reproduction is **an arm at a configuration**, which is the unit §9 of the paper insists on: it does
  not license anything about the other 34 configurations, and it is now the **third** configuration this project
  has executed more than once.
