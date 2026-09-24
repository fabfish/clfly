# The central contrast has no mechanism signature, and its one measured confound is the same size

**Date:** 2026-09-24
**Artifact:** `runs/e140_r32_methods_plastic_40reps.json` — the five-method table at forty replicates, every
mechanism field the runner records already in it.
**Subject:** the paper's central network contrast, `ewc-block` − `ewc-block-rand` = **−0.0206 ± 0.0099 = 2.08σ**
(28/40). **Every recorded quantity that the paper's account is written in fails to distinguish the two
partitions.**

---

## 1. Five quantities, none of which can tell the biology from its matched random control

Task 0, cumulative, forty paired seeds:

| quantity | `ewc-block` | `ewc-block-rand` | **bio − rand** |
|---|---|---|---|
| θ-only first order | +0.1594 | +0.1605 | **−0.0011 ± 0.0200 = 0.06σ** |
| θ-only cosine | 0.0311 | 0.0306 | +0.0005 ± 0.0030 = **0.16σ** |
| θ-only displacement | 19.591 | 19.993 | −0.402 ± 0.268 = 1.50σ |
| **whole-body** first order | +0.4581 | +0.4122 | **+0.0458 ± 0.0889 = 0.52σ** |
| — its bias half | +0.2987 | +0.2517 | +0.0469 ± 0.0820 = **0.57σ** |
| second-order quadratic (exact) | +0.4047 | **+4.2044** | −3.800 ± 3.469 = 1.10σ |

**The instrument that this paper's theory is written in says the two partitions are the same partition.** The
largest of the six readings is 1.50σ, the θ-only and whole-body first-order terms are **0.06σ and 0.52σ**, and
**the forgetting the two arms produce differs by 2.08σ**.

**And each block arm is indistinguishable from `naive` on the whole-body term too** — `ewc-block` − `naive`
**+0.0314 ± 0.0843 = 0.37σ** and `ewc-block-rand` − `naive` **−0.0144 ± 0.0736 = 0.20σ** — while their θ-only
terms are **3.47σ and 3.46σ** *below* `naive`'s. **So the whole-body form is silent about the block arms
entirely**, which is the opposite of the anchoring axis, where it ordered the arms at 4.21σ.

**And the second-order term is the one quantity with a large difference — and it is unmeasurable.** `quad[0]` is
**4.2044 for the matched random control against 0.4047 for the biological partition**, a factor of ten, and
`ewc`'s is **−0.2117**; but the per-seed sd of the difference is **≈22**, so the contrast is **1.10σ**. A coarser
Fisher is expected to make a larger quadratic form — that is what a block partition *is* — and **its spread across
seeds is fifty times its own mean**, so at forty replicates the quantity cannot resolve anything.

## 2. So what would have to be true for the 2.08σ to be the biology

**The contrast would have to be carried by something none of these six quantities reads.** The candidates the
project has not measured on this arm are: the **loss landscape** at the endpoint (which the second-order term
tries to capture and fails to resolve), and the partition's effect on **which** parameters move rather than how
far — which no recorded norm sees.

**And the one confound that *has* been measured is the same size as the contrast.** This session measured the
matched-random control's own draw term at **0.0138** (two draws of the same arm on the same forty seeds, per-seed
sd 0.0658) — against the contrast of **0.0206**. **So a single draw of the control can move this contrast by about
two thirds of its own value**, and the 2.08σ is a single-draw measurement.

## 3. What this does and does not say

- **It does not say the biology is not better.** It says the biology's advantage, if it is one, is **invisible in
  every quantity the project records**, which is a statement about the instruments as much as about the effect.
- **It is the third instance of the same lesson in this session, at a new level.** `e139` found the θ-only
  instrument blind to the channel carrying 70% of the forgetting; `e138` found the arm that works carrying
  *more* of the term; **this finds the instrument blind to a difference between two partitions that the effect
  metric resolves at 2.08σ** — i.e. the account's quantities are not merely mis-scaled, they are **silent on the
  paper's own central comparison**.
- **And it makes the three-draw measurement decisive rather than confirmatory.** Two more draws of this control
  are running (`runs/e140_r32_rand_draw{1,2}.json`), with the reading registered in advance: **P1** the three-draw
  contrast stays negative and at least as large as 2.08σ; **falsifier** it is within 2σ of zero. **The record
  above — no mechanism signature anywhere and a measured confound of the same size — is the reason the falsifier
  is a live possibility rather than a formality**, and it is written down before the draws land.
- **What it cannot settle**: the whole-body reading is one task and one pair of arms; the second-order term's
  spread is so large that "no signature" there means "unmeasurable" rather than "absent"; and a partition can act
  on the *optimisation* without leaving a difference in the endpoint's displacement, which no endpoint quantity
  in this project reads.
