# Under the freeze, λ stops mattering for forgetting — and starts mattering for plasticity at 5.7σ

**Date:** 2026-09-24
**Artifacts:** `runs/e147_r32_frozenbias_ewc_lam3e-3.json` (the second arm of `e147`, landed) against
`runs/e147_r32_frozenbias_ewc_lam3e-4.json`, `runs/e125_r32_frozenbias.json`,
`runs/e133_r32_naive_ewc_40reps.json`, `runs/e141_r32_ewc_lam3e-4.json` and
`runs/e140_r32_methods_plastic_40reps.json`.
**The registration** is `docs/findings/2026-09-24-the-third-point-could-not-exist.md` §3, written before either arm
ran: **P1** the two λ differ by ≥ 2σ with the channel frozen; **falsifier** they agree within 2σ, *"then λ's
entire effect on this configuration runs through the uncovered channel (the weaker penalty helps because it
displaces less, and with the channel frozen there is nothing left for λ to do)"*; and a **third outcome** — both
arms landing at `e125`'s +0.0227, *"the penalty adds nothing once the channel is held still"*.

---

## 1. The registered reading

| arm | forgetting | resolution of that forgetting, against `naive` (σ) | mean accuracy | newest-task accuracy |
|---|---|---|---|---|
| `naive` | +0.0750 | — | 0.9125 | 0.9667 |
| freeze only (`e125`) | +0.0227 | 5.90 | 0.9306 | 0.9401 |
| **frozen + ewc, λ = 3e-4** | **+0.0026** | 8.61 | 0.9271 | 0.9073 |
| **frozen + ewc, λ = 3e-3** | **−0.0021** | **8.45** | 0.9102 | **0.8750** |

The third column is a **resolution and not a difference**, so it does not close against the `naive` row it names —
the differences themselves are in the second table, where every row is a contrast and its comparator is named in
the row's own label.

| contrast, paired on the forty shared seeds | forgetting | mean accuracy | newest-task accuracy |
|---|---|---|---|
| **λ = 3e-4 − λ = 3e-3, both frozen** | **+0.0047 ± 0.0032 = 1.46σ** | **+0.0168 ± 0.0028 = 6.08σ** | **+0.0323 ± 0.0056 = 5.74σ** |
| λ = 3e-3 arm − freeze alone | −0.0247 ± 0.0042 = 5.85σ | −0.0203 ± 0.0034 = 5.94σ | −0.0651 ± 0.0073 = 8.95σ |
| λ = 3e-3 arm − `naive` | −0.0771 ± 0.0091 = 8.45σ | −0.0023 ± 0.0058 = 0.39σ | −0.0917 ± 0.0076 = **12.06σ** |

**P1 fails and the falsifier fires**: five-fold apart in λ, the two arms are **1.46σ** apart on forgetting. The
instrument check passes on the new arm in the form the freeze forces: the whole-body term's bias component is
**exactly 0.0** in all forty replicates.

**But the falsifier's *explanation* is refuted, and that is the finding.** The registration said that if the two λ
agree *"there is nothing left for λ to do"* — and there is: both arms sit **5.5σ and 5.9σ below the freeze they
were built on**, removing **88.5%** and **91%** of its residual forgetting. **So the penalty's presence matters
enormously and its strength does not.** The falsifier's first clause is an outcome and its second clause is a
mechanism, and the data separate them; the same shape as `e147`'s first arm, where the registered third outcome
was refuted at 5.53σ while remaining the outcome the registration expected least.

## 2. What λ does instead, and it is the other axis

Under the freeze the two λ differ by **1.46σ** on forgetting and by **5.74σ** on the newest task's accuracy
(0.9073 against 0.8750) and **6.08σ** on the mean (0.9271 against 0.9102). **So with the channel held still, λ's
entire resolvable effect is on plasticity, not on stability** — which is the reverse of what it does with the
channel free, where it is the stability axis that moves (4.27σ for 3e-4 against 1.21σ for 3e-3).

**That re-reads the λ sweep once more, and it is a different re-reading from the one `e152` gives.** `e141` found
the forgetting's interior optimum at 3e-4 with the channel free; `e152` showed one step above it worsens *both*
axes; and here, with the channel frozen, the stability axis is **flat** (1.46σ) while the plasticity axis is
**monotone in λ at 5.74σ**. So the sweep's optimum is not about how much forgetting the penalty can remove from
the weights — with the channel removed both λ remove nearly all of it — but about **how much adaptation λ
displaces into the offsets, which is exactly the channel the offsets' own forgetting is carried by.** λ = 3e-4
is the better setting under the freeze too, on the only axis where the difference resolves.

## 3. And the best forgetting in the record now has a name

`replay` measures −0.0034 on this family; **the frozen-plus-penalised arm at λ = 3e-3 measures −0.0021, which is
0.30σ from `replay` — indistinguishable from it on the stability axis — and 12.47σ below it on the newest task**
(0.9630 against 0.8750). At λ = 3e-4 the same comparison is forgetting 1.28σ and newest 8.33σ.

**So the session's two-axis picture has a concrete pair of arms at its centre**: a constraint that *matches*
replay's forgetting and pays **12.47σ** for it, and a method that pays **0.79σ**. It is also the widest
newest-task cost measured anywhere in this project — **outside the 2.08σ–9.70σ range `e151` and `e152` quote**,
because those two audits' registries were fixed before this arm existed and neither has been extended to it.
`e152`'s plane, read on this pair, gives the graded form rule 40 asks for: **`replay` dominates the λ = 3e-3 arm
on point estimates, resolved on one axis (12.47σ on the newest task) and 0.30σ — i.e. not resolved — on the
other.**

## 4. What this cannot settle

- **One read-out (32), one circuit, three tasks, one seed stream, and one freeze variant** (the offsets, not the
  body). `--frozen-bias` is a **diagnostic and not a method**: the ranking under it is not advice for a
  practitioner, and what this finding measures is a property of the penalty and of the benchmark.
- **λ has two measured values under the freeze**, five-fold apart, and the falsifier's verdict is a statement
  about that interval: whether λ matters on a *stability* axis below 3e-4 or above 3e-3 is untested, and `e141`'s
  sweep says the free-channel arm does move at those values.
- **The newest-task column is one task**, and `final_per_task[-1]` mixes how well it was fitted with how much
  interference it took (the `learned` diagonal separates them and is not quoted here).
- **The two audits that quote a cost range do not cover this arm**: `e151`'s registry of 22 contrasts and
  `e152`'s nine-arm plane were both fixed before it landed, so the 12.06σ and 12.47σ figures here are outside
  what those two readers print and must be re-derived from this finding's artifacts until either registry is
  extended.
