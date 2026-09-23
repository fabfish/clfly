# `e137`: the penalty does not remove the adaptation — it relocates it into the channel it cannot see

**Date:** 2026-09-24
**Script:** `experiments/e137_bias_substitution.py` (new); artifact `runs/e137_bias_substitution.json`.
**Data:** `runs/e133_r32_naive_ewc_40reps.json` — `naive` and `ewc` at forty replicates each, same seeds, the
paper's hardened configuration. **No new runs.**
**Context:** `docs/findings/2026-09-24-the-unpenalised-channel-carries-seventy-percent.md` (holding the bias
removes 70% of the forgetting) and `docs/findings/2026-09-24-diagonal-ewc-does-not-survive-its-own-configuration.md`
(diagonal EWC is 1.21σ from naive at forty, against 2.47σ at five). **Those are two facts about the same channel;
this puts them together.**

---

## 1. Where does the adaptation go?

The penalty's target moves **less** and the channel it does not cover moves **more**, both resolved:

| | theta_drift | bias movement (`from_zero`, last checkpoint) | forgetting | accuracy |
|---|---|---|---|---|
| **naive** | **0.0498** | **2.0005** | +0.0750 | 0.9125 |
| **EWC**, diagonal | **0.0357** | **2.5027** | +0.0654 | **0.8856** |
| naive − EWC | **+0.0141 ± 0.0006 = 25.24σ** (ratio 1.395) | **−0.5022 ± 0.0530 = 9.48σ** (ratio 0.799) | +0.0096 ± 0.0080 = 1.21σ | — |

**EWC's recurrent weights move 28% less than naive's, and its 800 per-neuron offsets move 25% more.** So the
code claim — `model.bias` appears in `e8_rate_network.py` only in the optimiser's parameter list, the drift record
and the checkpoint save, and `clfly/network/fisher.py` does not mention it — has a **measured consequence that is
stronger than "unpenalised"**: the channel is not merely ignored, it **absorbs what the penalty removes** from the
weights it does touch.

**And that is the mechanism behind `e133`'s null, which is more informative than "the five-replicate effect did
not replicate".** Constraining `theta` by 28% buys nothing on the forgetting (1.21σ) **because the adaptation
moved to the channel carrying 70% of it** — the penalty squeezes one end and the unpenalised end grows. Both
statements are true and this one explains why the other is.

**Which makes the follow-up a different method rather than a better λ.** A penalty that *also* covered the bias
would act on 100% of the body instead of 97.1% of it, and §8's item 6 already registers that arm; what this
finding adds is that it is not a refinement of the λ sweep but the only version of the experiment in which the
penalty can act on the whole thing.

## 2. And the first trajectory quantity whose sign lines up with the channel that carries the forgetting

Across the forty seeds of one arm, four quantities against the forgetting:

| quantity | naive arm, r (Spearman) | EWC arm, r (Spearman) |
|---|---|---|
| **bias movement, cumulative** | **+0.340 (+0.327)** | **−0.101 (−0.159)** |
| bias movement, last step | +0.263 (+0.198) | −0.169 (−0.280) |
| `theta_drift` | −0.102 (−0.107) | −0.250 (−0.369) |
| fit depth at task 0 | +0.048 (+0.048) | +0.168 (+0.107) |

**`bias_from_zero` is the largest of the four in the naive arm — r = +0.340 at n = 40, a ~3% two-sided draw — and
it is the first quantity in this project whose sign points at the channel `e125` identified.** `e108`, `e109` and
`e121` found the drift, the interference terms and the fit depth unable to order the forgetting; the channel that
carries 70% of it produces the strongest correlation of anything tried, which is a coherence check on `e125` that
`e125` could not have run.

**And it is a lead, not a result, for three reasons that are all printed beside it**: the same quantity is
**−0.101** in the EWC arm; the **per-task** steps are all ≈ 0 (r from −0.042 to +0.101 across four task-arm
combinations), so the correlation is with the **cumulative** movement and not with the task-specific one; and
fifteen quantities have now been correlated with the forgetting in this project, so one at ~3% is close to what
the multiplicity alone would produce.

## 3. Level and variation, which is why this is not in tension with `e125`

`e125` removed the channel and 70% of the forgetting went with it. Here the channel's own **seed-to-seed
variation** explains **0.340² = 12%** of the forgetting's variation. **Both can be true and the distinction is the
one this project keeps meeting**: a channel whose *level* carries most of an effect need not be a good *predictor*
across seeds, because a quantity can matter enormously and still be nearly constant between the runs being
compared — the whole channel varies by 8% of its own magnitude across seeds while carrying 70% of the effect.
**A large intervention effect and a weak correlation are evidence about two different things**, and reading the
second as a check on the first would be the error.

## 4. What this cannot settle

- **One read-out, one λ, one task order, one circuit.** The substitution is measured at the paper's own hardened
  configuration; whether a larger λ relocates *more* (the natural prediction, and therefore the natural test) is
  not measured — and a λ sweep at forty replicates now has a mechanism to look for rather than a null to report.
- **The substitution is a between-arm comparison of forty paired seeds**, so it is resolved; it says nothing about
  *how* the optimiser chooses, only that the two channels move in opposite directions by resolved amounts.
- **The lead in §2 is one arm, four quantities and forty seeds**, with the sign absent in the other arm. It is
  reported as a lead and would need its own pre-registration to become anything else.
- **And nothing here says the bias's movement is *harmful*.** `e125` shows that *freezing* it helps; that is a
  statement about the level, and a seed whose bias moves more may still be a seed that forgets less — the
  correlation's sign says it does not, at r = +0.340, which is weak.
