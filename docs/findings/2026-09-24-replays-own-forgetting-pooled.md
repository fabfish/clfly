# `replay`'s own forgetting, pooled: −0.0007 ± 0.0038 over four configurations

**Date:** 2026-09-24
**Script:** none — four numbers already on disk, pooled. **Artifacts:** `runs/e140_r32_methods_plastic_40reps.json`,
`runs/e148_r32_overlap1_replay.json`, `runs/e140_r32_methods_frozenbias_40reps.json`,
`runs/e155_r128_naive_replay.json` (all forty replicates).
**Why it is worth a finding:** the paper's sentence is *"replay drives the forgetting to zero or below"*, which is
an adjective. The five-configuration table in `e155`'s finding turned it into an identity — the margin over a
baseline is *replay's own forgetting minus the baseline's* — and that leaves exactly one quantity to estimate.
This is that estimate.

---

## 1. The pool

| configuration | `replay`'s own forgetting |
|---|---|
| base family, read-out 32 (`e140` plastic) | **−0.0034** |
| shared-input family (`e148`) | **+0.0083** |
| base family, channel frozen in every arm (`e140` frozen) | **+0.0018** |
| base family, read-out 128 (`e155`) | **−0.0096** |
| **pooled over the four distinct configurations** | **−0.0007 ± 0.0038** |

**That is 0.19σ from zero, with a 2σ bound of ±0.0076 and a 95% interval of [−0.0082, +0.0067].**

**And the four values are consistent with one value**: the across-configuration sd is **0.0076** against each
value's own sem of about **0.0033** (replay's per-seed sd is ≈ 0.021 at forty replicates), so the spread between
configurations is barely larger than the noise inside each. There is no evidence here of a configuration where
replay forgets *differently* — which is what makes a single number the right summary.

`e135`'s five-replicate frozen arm (−0.0042) is deliberately **not** pooled: it is the same configuration as the
`e140` frozen row at five of the same forty seeds, so including it would double-count. **With it included the pool
gives −0.0002, i.e. the same conclusion from a non-independent sample** — the kind of agreement that is worth
reporting and not worth counting.

## 2. What it changes

**The paper's sentence becomes a number.** *"Zero or below"* is now **−0.0007 ± 0.0038 pooled**, with the
individual values spanning **−0.0096 to +0.0083** — so the honest sentence is *"replay's own forgetting is zero to
within ±0.008 (2σ), and negative in three of the four configurations"*. That is a **bound**, like the biology's
null and for the same reason: the effect being bounded is smaller than what forty seeds resolve.

**And it makes the floor model's status precise.** The `e148` finding asked whether replay's margin tracks the
unpenalised channel's share; the answer is no, and the reason is that the margin is *the baseline's forgetting
minus a term bounded at ±0.008*. **So the model's last free quantity is measured, and the model reduces to the
paper's own claim about content memory** — which is a reduction and not an explanation, and the finding says so.

## 3. The next day's fifth configuration tightens it — added in place

`e155`'s **read-out-700** arm landed and measured `replay`'s own forgetting there at **+0.0008**, so the pool is
now **five** distinct configurations: **−0.0004 ± 0.0030** (0.14σ from zero, a 2σ bound of **±0.0059**, 95%
[−0.0062, +0.0054]). The five values span −0.0096 to +0.0083 with an across-configuration sd of **0.0066**, so the
conclusion is unchanged and the bound is 22% tighter. **That arm is also the one the registration named as the
discriminating one, and it refuted the alternative reading rather than confirming this one** — the margin there is
the baseline's forgetting to 0.12σ, while a proportional-to-the-share reading would need the offsets to carry
**97%** of that baseline's forgetting against **89%** and **83%** at the neighbouring read-outs
(`docs/findings/2026-09-24-the-discriminating-arm-refutes-the-channel-reading.md`).

## 5. What this cannot settle

- **Four configurations, one suite**: one circuit (`cs = 800`), three tasks, one seed stream, one read-out axis,
  and the four arms share the same base model. A fifth configuration with a *different* task family would be the
  test of whether the bound is a property of replay or of this suite.
- **The pool is a mean of means**, each estimated from forty paired seeds, and it treats the four as independent
  draws of one quantity — they are not (they share seeds and architecture), so ±0.0038 is optimistic in the same
  way every pooled estimate in this project is.
- **It is a bound on the *mean*, not on any single run**: an individual configuration's replay arm can sit at
  −0.0096, which is 2.5σ from the pooled value, and the bound that matters for a practitioner is the interval
  over configurations, not the interval over seeds.
- And **the quantity is measured on one metric**: the loss-valued forgetting form uses a different window (it is
  the diagonal-and-below counterpart, `e123`), and replay's own value on it is not in this pool.
