# `e138` pre-registered: put the bias **inside** the penalty — the arm no λ can reach

**Date:** 2026-09-24
**Status:** pre-registered **before** the runs. Committed as its own commit; the runs are launched after it.
**Script:** `experiments/e8_rate_network.py` with the new **`--anchor-bias SCALE`**.
**Planned artifacts:** `runs/e138_r32_ewc_anchorbias1.json` and `runs/e138_r32_ewc_anchorbias33.json`, each
`--methods ewc --repeats 40 --iters 500 --test 48 --readout-size 32 --fisher-batches 32 --lam 3e-3 --shared-head
--input-overlap 0.0 --seed0 0 --circuit-size 800` with `--anchor-bias 1.0` and `--anchor-bias 33.2`.
**Comparators:** `runs/e133_r32_naive_ewc_40reps.json` — its `naive` arm (per-replicate identical to
`runs/e116_r32_40reps.json`) and its **unanchored `ewc`** arm (**+0.0654 ± 0.0079**, 1.21σ from naive).
**Context:** the chain this session built. `e125`: the 800 per-neuron offsets carry **70%** of this
configuration's forgetting and holding them at their initialisation removes it *and* raises accuracy. `e137`: the
diagonal penalty **relocates** adaptation into them — its `theta` moves 28% less while its bias moves **25%
more**. `e133`: at forty replicates diagonal EWC is **1.21σ** from naive, where the paper quotes **2.47σ** from
five. **So the natural next question is not a λ and not a basis: it is whether a penalty that covers the channel
does what no λ can.**

## What the flag does, and why the scale is a number rather than a switch

`--anchor-bias` computes the bias's own diagonal Fisher **on the same batches as the weights'**, unit-mean
normalises it exactly as the weights' is normalised, and then adds
`0.5·λ·SCALE·Σ fisher_b·(bias − anchor_b)²` to the loss. The anchor and the Fisher are created **after** each
task, so **task 0 is trained with no bias penalty in every arm** — which is why the registration's first control
is that task 0's bias step is identical across arms, and why that control is an *internal* one rather than a
comparison of runs.

**The scale is a ratio of per-parameter anchoring strength, and the two arms bracket the ambiguity**:
`SCALE = 1.0` treats every parameter alike, so the bias carries **800/27,368 = 2.9%** of the penalty's mass;
`SCALE = 26,568/800 = 33.2` gives the two sets **equal total mass**. **The choice is not cosmetic**: with equal
mass the penalty's half is spent on 2.9% of the parameters, which is the version a practitioner adding the bias
to their Fisher would *not* write and the version that could plausibly fix something.

## The predictions

- **C0a.** The bias's step at **task 0** is identical across both arms and `e133`'s unanchored `ewc` arm — there
  is no Fisher and no anchor before the first task, so any difference would be a bug in the flag rather than a
  result.
- **C0b, the manipulation check.** The bias's cumulative movement falls **monotonically** in the scale:
  unanchored (`e133`) > `SCALE 1.0` > `SCALE 33.2`. A flag that does not move the thing it names is not a
  manipulation.
- **P1, and it is the fire.** **The forgetting falls monotonically in the scale**: unanchored **+0.0654** >
  `SCALE 1.0` > `SCALE 33.2`, with the frozen-bias value **+0.0227** as the limit a penalty should approach
  **from above and not reach** (a penalty is not a freeze). *The direction is registered rather than a magnitude,
  because a magnitude here would be a new claim: what licenses the direction is `e125`, which removed the channel
  entirely and took 70% of the forgetting with it.*
- **Falsifier.** The `SCALE 33.2` arm's forgetting is **within 2σ of the unanchored arm's** (+0.0654 ± 0.0079).
  Then **covering the channel does not fix the penalty**, the omission is not the explanation, and the reason
  diagonal EWC fails has to be looked for in *how* the penalty acts rather than *what* it covers — which would
  make `e125`'s 70% a fact about the naive baseline rather than about EWC.
- **P2, descriptive and registered so that it is reported**: the per-task forgetting. `e133` found the unanchored
  arm's mean is the cancellation of a **3.79σ** improvement on task 0 and a degradation on task 1, so the
  question for every arm here is whether anchoring the bias removes the trade or merely shifts it.

## Why this arm and not a λ sweep

**No λ can reach the channel**, because the penalty is a sum over `theta` and the channel is not in `theta`:
a λ sweep moves both channels' weights together and the bias's share of the penalty's mass stays exactly zero.
`e137`'s substitution result is what makes that more than a bookkeeping observation — the penalty's effect on
the weights was **matched by an opposite movement in a channel carrying 70% of the forgetting**, so a sweep of λ
would sweep how hard you squeeze a channel whose content escapes into one that is unpressed. **This is therefore
the only arm in which the penalty can act on the whole body**, and it is the arm §8's item 6 (a) registers.

## What this cannot settle, in advance

- **One read-out, one λ, one circuit, three tasks.** The bias's share is read-out dependent (`e134`: 70%, 89%,
  83% at read-outs 32, 128 and 1307), so a result here is a result at the read-out where the confound is largest.
- **The scale's two values bracket an ambiguity rather than resolving it**, and a non-monotone result would say
  the anchoring strength itself is a hyperparameter with an interior optimum — which is a finding, and is not
  what the registration predicts.
- **A penalty is not a freeze**, so the comparison's *limit* is `e125`'s +0.0227 and not a target. There is no
  registered expectation that penalising the bias reaches it.
- **And the fit may suffer.** Anchoring 2.9% of the parameters with half the penalty's mass is a real constraint
  on the model's capacity, so the diagonal accuracy is a cost to report and not only a benefit: `e125`'s
  *freezing* raised accuracy, and a penalty need not.
