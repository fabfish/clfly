# λ's two effects have different owners: the channel owns its stability effect, the penalty owns its plasticity cost

**Date:** 2026-09-24
**Script:** `experiments/e149_intervention_interaction.py`, **second block** — analysis only. The four cells are
already on disk: `runs/e141_r32_ewc_lam3e-4.json` and `e133`'s `ewc` (λ = 3e-3) with the channel **free**,
`runs/e147_r32_frozenbias_ewc_lam3e-{4,3}.json` with it **frozen**.
**What it is:** the project's **second** 2x2. The first (`e149`'s own block) asked whether the freeze and the
penalty *share* an effect and answered **1.61σ, unresolved**. This one asks a different question of the same kind
of design: **does the channel change what the knob does?** — and it resolves.

---

## 1. The table

| metric | step λ: 3e-4 → 3e-3, channel **free** | step, channel **frozen** | **interaction** (frozen step − free step) |
|---|---|---|---|
| **forgetting** | +0.0258 (**3.74σ** worse) | −0.0047 (1.46σ better) | **−0.0305 ± 0.0074 = 4.10σ** |
| **loss-valued forgetting** | +0.0606 (**4.85σ** worse) | −0.0095 (**14.68σ** better) | **−0.0701 ± 0.0125 = 5.61σ** |
| mean accuracy | −0.0318 (**6.00σ** worse) | −0.0168 (**6.08σ** worse) | **+0.0149 ± 0.0051 = 2.92σ** |
| **newest-task accuracy** | −0.0229 (**2.97σ**) | −0.0323 (**5.74σ**) | −0.0094 ± 0.0076 = **1.23σ** |

Levels, forgetting: **free** +0.0396 → +0.0654; **frozen** +0.0026 → −0.0021. Newest-task accuracy:
0.9370 → 0.9141 free, 0.9073 → 0.8750 frozen.

**The interaction is computed per seed**, not as the two steps' sems in quadrature: the steps sit on different
arms but the **same forty seeds**, so their per-seed differences are correlated and quadrature *overstates* the
uncertainty. The quadrature bound is printed beside each interaction for exactly that reason (0.0076 against
0.0074 on forgetting, 0.0095 against 0.0076 on the newest task — the correlation is real and small).

## 2. What it says, and it is a separation

**The knob's stability effect belongs to the channel.** Raising λ from 3e-4 to 3e-3 costs **+0.0258 (3.74σ)** of
forgetting with the channel free and, with it frozen, **helps by 0.0047** — a step that does not resolve alone
(1.46σ) but whose **interaction resolves at 4.10σ, and 5.61σ on the loss-valued metric**. So the effect of λ on
forgetting *is* the management of the unpenalised channel, stated as an interaction rather than as a comparison of
one arm's levels: **the channel does not merely mask the penalty's effect (that was `e147`), it determines the
sign of the knob's effect.**

**And the knob's plasticity cost belongs to the penalty.** The same step costs newest-task accuracy in **both**
channels (−0.0229 at 2.97σ and −0.0323 at 5.74σ) and the interaction there is **1.23σ** — unresolved, i.e. the
cost is channel-independent at this resolution while each individual cost resolves. **So the two things λ does in
this benchmark have different owners**: what it does to the forgetting is a property of the channel it displaces
adaptation into (`e137`'s mechanism), and what it does to the newest task is a property of the penalty itself.

**The mean accuracy sits in between and for a reason worth recording.** Its interaction is **2.92σ** — resolved,
and *larger* than the newest task's 1.23σ. The mean carries the two old tasks' retention as well, and the freeze
changes those, so **the mean's interaction is not the newest-task interaction**: a reader who took "accuracy" for
"how well the last task was learned" would read 2.92σ where the column that measures that reads 1.23σ.

## 3. And it sharpens the contrast with the first 2x2

The two 2x2s are the same design on four arms of one seed stream, and they answer oppositely:

| 2x2 | factor 1 | factor 2 | interaction on forgetting |
|---|---|---|---|
| `e149`'s first block | the penalty's **presence** | the freeze | **+0.0154 ± 0.0096 = 1.61σ** — unresolved, additive at this resolution |
| this block | the penalty's **strength** | the channel | **−0.0305 ± 0.0074 = 4.10σ** — resolved, and it flips the step's sign |

**So "the penalty and the freeze are additive" and "the penalty's strength and the freeze are not" are both true,
on the same seeds, and they are different statements about different factors.** `e147`'s finding said the
penalty's effect is *masked by the free channel*; this says **what is masked is the knob's stability effect
(4.10σ) and what is not is the knob's plasticity cost (1.23σ)** — and that the masking is a sign reversal rather
than an attenuation.

## 4. What this cannot settle

- **Two λ, five-fold apart**, and one channel manipulation (the offsets frozen, not the body). Whether λ's
  stability effect is monotone *within* the frozen channel — the 7× between 3e-4 and 3e-3 is the whole measured
  interval — is untested; `e150`, running now, asks it on the harder family.
- One read-out (32), one circuit, three tasks, one seed stream. `--frozen-bias` is a **diagnostic and not a
  method**, so "the channel owns the stability effect" is a statement about the penalty and the benchmark, not
  advice about which arm to deploy.
- **An interaction of two steps is not a mechanism**: this measures that the knob's effect changes with the
  channel, and `e137`/`e139` are what say *why* (adaptation displaced into the 800 offsets). The interference
  column is not in this block because `e133`'s artifact predates the whole-body instrument — the same gap `e149`'s
  first block names.
- The interaction's own resolution is quoted **per seed**; the quadrature bound beside it is what a reader would
  compute from the two printed steps, and on the newest task those differ by 25% (0.0076 against 0.0095), so the
  convention is stated rather than assumed.
