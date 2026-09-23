# `e139`: the interference instrument is channel-blind — EWC cuts the term it targets by 98% while the forgetting moves 1.21σ

**Date:** 2026-09-24
**Script:** `experiments/e139_whole_body_interference.py` (new) — an analysis of `e133`'s forty replicates, plus
the `whole_body` block added to `e8_rate_network.py` for the run that tests the explanation.
**Data:** `runs/e133_r32_naive_ewc_40reps.json` — `naive` and `ewc`, forty paired seeds, no penalty covering the
bias in either arm — **and `runs/e139_r32_wholebody.json`, the same two arms re-run with the `whole_body` block,
which is what §4 reports; §4's third arm is `runs/e138_r32_ewc_anchorbias33.json` at the same seeds.**
**Context:** `e125` (the 800 offsets carry 70% of the forgetting), `e137` (the penalty relocates adaptation into
them: `theta` moves 28% less, the bias 25% more), `e133` (the penalty's forgetting moves **1.21σ** where the
paper quotes 2.47σ from five). **Those three leave a question: the penalty was designed to reduce interference,
so does it?**

---

## 1. It does — by a factor of forty-five — and nothing happens

The `theta`-only first-order term `⟨grad_j(θ_final), θ_final − θ_j⟩`, the interference account's one-line
prediction, over forty paired seeds:

| cumulative term, task 0 | naive | EWC | change | ratio |
|---|---|---|---|---|
| **first order** | **+0.2336** | **+0.0052** | **−0.2284 ± 0.0221 = 10.34σ** | **0.022** |
| cosine | +0.0476 | +0.0019 | −0.0457 ± 0.0032 = **14.41σ** | 0.040 |
| displacement norm | +18.817 | +14.142 | −4.675 ± 0.166 = **28.25σ** | 0.752 |
| gradient norm | +0.2736 | +0.2238 | −0.0498 ± 0.0237 = 2.10σ | 0.818 |

and on task 1 the same terms fall at **9.04σ** (first order) and **10.41σ** (cosine) — **with one detail that supports the redistribution reading**: task 1's *gradient* norm **rises** under the penalty (0.2452 → 0.3608, ratio **1.471**, **3.73σ**), which is what a body that has moved *away* from task 1's optimum looks like and is the same statement as `e133`'s per-task finding that EWC's task-1 forgetting is *worse* than naive's.

**So diagonal EWC does exactly what its theory says: the first-order interference a later task inflicts on task 0
falls by 98%, the component along the gradient by 96%, and the displacement by 25%.** The second-order term does
not differ (1.29σ and 1.37σ on the quadratic form and the Rayleigh quotient).

**And the forgetting moves 1.21σ.** `e133` measured that on the same artifact, so this is not a comparison across
runs: **one instrument is reduced by a factor of forty-five and the effect it exists to predict is unchanged.**

## 2. The explanation is that the instrument reads one channel and the effect lives in the other

`interference` is built from `_grad_j(θ)` and `θ_final − θ_j` — **`theta` alone**. `e125` measured that **70%** of
this configuration's forgetting is carried by the **800 per-neuron offsets**, and `e137` that the penalty's
effect on `theta` is matched by an **opposite movement** in that channel. So the one-line account is evaluated
over the half of the body the penalty squeezed and not over the half the damage moved to, and **a term that falls
45-fold in a channel holding 30% of the effect can leave the effect untouched.**

**This is the dissociation, and it is stronger than `e108`'s result rather than a repetition of it.** `e108` found
the first-order term could not **order** the forgetting *across configurations* — a correlation statement, where
the confound is that everything is monotone in the read-out. This is a **manipulation**: the term is *reduced by
a factor of forty-five* by an intervention, and the effect does not move. **A quantity that can be moved 45-fold
without the effect moving is not the effect's carrier**, and no correlation can show that as cleanly as an
intervention can.

**Which also re-reads `e108`'s null**: the term failed to order the forgetting, and the reason is now visible —
it was measuring the wrong half. That is a better account of a five-fire-old null than "the geometry is flat".

## 3. And the follow-up that the same reasoning forces

**The instrument should be evaluated over the body the perturbation actually moved**, so `whole_body_grad`
returns the gradient with respect to both halves and the `interference` block now stores
`whole_body.per_task`, `whole_body.cumulative` and its two components `theta_only_cumulative` and
`bias_only_cumulative`. **`e139`'s run — `naive` and `ewc`, forty paired seeds, the same configuration — is what
turns the explanation into a measurement**, and its prediction is registered here rather than after the fact:

- **P1.** The **whole-body** first-order term is **not** reduced as the `theta`-only form is: the ratio
  `whole_body(EWC)/whole_body(naive)` is **above 0.5**, against the `theta`-only ratio of **0.022**. The
  prediction is directional and follows from `e137`'s measured substitution: the bias's displacement **grows**
  25% under the penalty, so a term that includes it cannot fall the way the `theta`-only term does.
- **P2.** The **bias's own** contribution is a **substantial share** of the whole-body term in the naive arm —
  not a correction to it.
- **Falsifier.** The whole-body ratio is **below 0.1**, i.e. the body-wide term falls about as hard as the
  `theta`-only one. Then the channel-blindness is *not* the explanation, the penalty reduces the body's
  interference as thoroughly as it reduces the weights', and the forgetting's failure to move has to be explained
  by something other than where the instrument was pointed.

## 4. And it is measured: P1 holds, and the extended instrument orders the effect where the old one does not

`runs/e139_r32_wholebody.json` landed, and on the same forty paired seeds, task 0 — **and it is the same
trajectories rather than merely the same command**: `e139`'s `naive` and `ewc` arms are **per-replicate
bit-identical** to `e133`'s in forgetting, final accuracy and `theta_drift`, all forty replicates and both
methods, so adding the `whole_body` instrumentation did not perturb training and the two forms are two readings
of one set of runs.

| cumulative, task 0 | naive | EWC | change | ratio |
|---|---|---|---|---|
| **whole body** | +0.4266 | +0.3257 | −0.1010 ± 0.0725 = **1.39σ** | **0.763** |
| of which `theta`-only | +0.2336 | +0.0052 | −0.2284 ± 0.0221 = **10.34σ** | **0.022** |
| of which **bias-only** | +0.1930 | **+0.3204** | **+0.1274 ± 0.0701 = 1.82σ** | **1.660** |

**P1 holds** (the registered ratio was "above 0.5"; it is 0.763), **the falsifier does not fire**, and **P2
holds**: the bias's contribution is **45%** of the whole-body term in the naive arm (0.1930 against 0.2336),
so it is a component and not a correction. **And the bias's contribution *grows* 66% under the penalty** — the
penalty relocates interference into the channel it does not cover, which is `e137`'s substitution measured in the
instrument's own units rather than in displacements.

**Which makes the channel-blindness quantitative rather than qualitative: the `theta`-only form was reading 55%
of the account, and the half it could not see grew while the half it could see collapsed.** The θ-only
instrument's share of the whole-body term is **98% ⇒ 2%** between the naive and EWC arms — the penalty does not
merely leave the instrument pointed at one channel, it **empties** that channel of the term and fills the other.

### The three-arm extension, which is the strongest form of the result

`e138`'s `SCALE 33.2` arm carries the same instrument at the same seeds, so the account can be read across three
arms whose effect differs by 4.84σ:

| cumulative, task 0 | naive | unanchored EWC | **anchored EWC (`e138`, 33.2)** |
|---|---|---|---|
| **whole-body first order** | 0.4266 | 0.3257, ratio 0.763 at **1.39σ** | **0.1831**, ratio **0.429** at **4.21σ** |
| `theta`-only | 0.2336 | **0.0052**, ratio 0.022 at **10.34σ** | 0.0238, ratio 0.102 at **9.72σ** |
| bias-only | 0.1930 | 0.3204, ratio 1.660 at **1.82σ** | 0.1593, ratio 0.825 at **0.66σ** |
| **shares (θ / bias)** | **55% / 45%** | **2% / 98%** | 13% / 87% |
| **mean forgetting** | **+0.0750** | **+0.0654** | **+0.0292** |

**The whole-body term's ordering across the three arms is the forgetting's ordering, and the `theta`-only form's
is not.** Whole body: 0.4266 → 0.3257 → **0.1831** against forgetting 0.0750 → 0.0654 → **0.0292**, with the
strong arm's cut at **4.21σ** where the arm that does not move the forgetting cuts it at **1.39σ**. The θ-only
form goes 0.2336 → **0.0052** → 0.0238, i.e. **lowest in the arm whose forgetting is highest of the three
penalties**. **So the extended instrument tracks the effect and the old one does not** — which is the whole of
§1–2's explanation, now an ordering rather than a single contrast, and the strongest evidence in this document
that the old instrument's failure was about *where it was pointed* rather than about the theory it was pointed
from.

**It also closes the loop with `e138`'s own result**: the arm that reaches 4.84σ on the forgetting is the arm that
cuts the whole-body term **4.21σ**, so the account is not discarded — it is *repaired*, by measuring the body the
penalty actually acts on rather than the half of it that the original formulation named.

## 5. The lead that sits beside it, and it is the same size as the last one

Within the naive arm, the `theta`-only first-order term **correlates with the forgetting at r = +0.329** across
the forty seeds — and **−0.221 in the EWC arm**. So it is the **second** quantity in this session whose
within-arm correlation with the forgetting is about +0.33 and whose sign does not survive a change of arm, the
first being the bias's movement (`e137`, +0.340 / −0.101). **Two quantities at ~+0.33, both with the wrong sign
in the other arm, is what a null looks like when it is measured at n = 40** — and the fact that they are
*r = +0.33 of the same magnitude* is a reason to be more suspicious of both, not less: fifteen quantities have
now been correlated with this forgetting, and two at 3% in the same arm are what multiplicity produces.

## 6. What this cannot settle

- **The whole-body term is measured for one task and one pair of arms plus `e138`'s strong scale.** §4's verdict
  is `naive` against EWC on task 0, with the third arm from another artifact at the same seeds — so the ordering
  is three points, and **task 1's whole-body term is not reported here at all**.
- **The first-order term is a linearisation**, and the second-order one *does not differ between the arms*
  (1.29σ). So what is established is that the **linear** account of the interference the penalty targets falls
  45-fold in one channel and 24% over the body; whether a nonlinear account would move is not measured.
- **One read-out, one λ, three tasks, one circuit.** The channel's share is read-out dependent (70%, 89%, 83% at
  read-outs 32, 128 and 1307 per `e134`), so this is the configuration with the largest share.
- **And nothing here says the penalty is mis-specified.** It says the penalty acts on one channel and the
  forgetting lives in the other — which is what `e125` measured before any of this, and what makes `e138`'s
  bias-anchored arm the only version in which the penalty can act on the whole body.
