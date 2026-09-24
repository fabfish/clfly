# The two interventions add at forty seeds — and the axis where they are strictly opposed is the one that adds *exactly*

**Date:** 2026-09-24
**Script:** `experiments/e149_intervention_interaction.py` — **analysis only, no runs**.
**Artifacts:** the four arms of one 2x2 on the same forty seeds — `runs/e133_r32_naive_ewc_40reps.json`
(`naive`), `runs/e125_r32_frozenbias.json` (offsets frozen, no penalty), `runs/e141_r32_ewc_lam3e-4.json`
(`ewc` λ = 3e-4, offsets free) and `runs/e147_r32_frozenbias_ewc_lam3e-4.json` (both).
**Labelled exploratory in the script itself, and that label is the point.** Every other reader in this project
carried a prediction written before its runs existed; this one could not, because three of its four artifacts
had already been read for other questions. What it carries instead is the discipline the artifacts can still
support: the **pairing check** and the **ceiling**.

---

## 1. The 2x2, and why the four cells are paired

The four arms are on one seed stream — the pairing check compares **every one of the 14 fields that determines
the seeds** (`seed0`, `repeats`, `circuit_size`, `iters`, `lr`, `batch`, `train`, `test`, `noise`, `classes`,
`support`, `shared_head`, `input_overlap`, `readout_size`): **14 of 14 agree, 40 replicates each**. What differs
is exactly the two knobs:

| arm | `frozen_bias` | `lam` | `fisher_batches` | method |
|---|---|---|---|---|
| `naive` (`e133`) | False | 3e-3 | 32 | naive |
| freeze only (`e125`) | True | 1.0 | 8 | naive |
| penalty only (`e141`) | False | 3e-4 | 32 | ewc |
| both (`e147`) | True | 3e-4 | 32 | ewc |

The two settings that differ on the freeze arm beyond the freeze — `lam` 1.0 and 8 Fisher batches — are
**inert for a `naive` method**, and `e146` already produced a *bit-identical* artifact under a different `lam`
and batch count on that arm, so they are read-only knobs here rather than confounds. This is the first time the
project has held all four cells of a 2x2 on one seed stream.

| arm | forgetting | loss forgetting | accuracy | θ drift |
|---|---|---|---|---|
| `naive` | **+0.0750** | +0.1767 | 0.9125 | 0.0497 |
| freeze only | **+0.0227** | +0.0567 | 0.9306 | 0.0551 |
| penalty only (λ = 3e-4) | **+0.0396** | +0.1177 | 0.9174 | 0.0457 |
| both | **+0.0026** | +0.0189 | 0.9271 | 0.0510 |

Paired changes against the same `naive` row:

| contrast | forgetting | loss forgetting | accuracy | θ drift |
|---|---|---|---|---|
| freeze alone | −0.0523 (**5.90σ**) | −0.1200 (**8.69σ**) | +0.0181 (3.27σ) | **+0.0054** (**21.55σ**) |
| penalty alone | −0.0354 (**4.27σ**) | −0.0590 (**4.02σ**) | +0.0049 (0.91σ) | **−0.0040** (**16.86σ**) |
| both | −0.0724 (**8.61σ**) | −0.1578 (11.02σ) | +0.0146 (2.55σ) | +0.0013 (5.04σ) |

Two things are worth noting before the interaction. The two main effects on the **drift** have **opposite
signs** and are the largest resolvable effects anywhere in this table — larger in σ (21.55 and 16.86) than
either intervention's effect on the forgetting (5.90 and 4.27). And the additive prediction for the forgetting
is **−0.0128**, a level the metric can express (`e140`'s `replay` arm measures −0.0034 on the same design) but
one that neither arm reaches: the two together deliver +0.0026.

## 2. The interaction, and the three ways of saying the same number

On a metric where less is better, `I = d_both − d_freeze − d_pen` is the part of the two effects that is
**shared**: `I > 0` means the two together remove less than the sum of what they remove apart. The identity is
exact in the artifact to 10⁻¹⁷.

| metric | I | resolution | seeds positive | sign p | ceiling | I / ceiling |
|---|---|---|---|---|---|---|
| forgetting | **+0.0154** | **1.61σ** | 24/40 | 0.268 | 0.0354 | **0.43** |
| loss forgetting | +0.0212 | 1.46σ | 25/40 | 0.154 | 0.0590 | 0.36 |
| accuracy | −0.0083 | 1.47σ | 16/38 (2 tied) | 0.418 | 0.0049 | — |
| θ drift | **+0.000007** | **0.03σ** | 18/40 | 0.636 | 0.0040 | **0.0017** |

**On both forgetting metrics the interaction does not resolve**, and the sign test agrees with the σ test rather
than rescuing it (p = 0.27 and 0.15). So the licensed sentence is **not** "the effects are independent" — it is
**"whatever the two interventions share is below this design's resolution"**, with the point estimates saying
they share 43% and 36% of the smaller effect.

Those percentages and the e147 finding's retention fractions are **one measurement**, which is worth recording
because the finding quoted the fractions as if they were separate facts:

- the penalty retains **0.57** of its effect given the freeze: 1 − 0.57 = 0.43 = I / abs(d_pen) = 0.0154 / 0.0354;
- the freeze retains **0.71** of its effect given the penalty: 1 − 0.71 = 0.30 = I / abs(d_freeze) = 0.0154 / 0.0523.

With the signs kept, `retention = 1 + I/d` on both, and `pen_given_freeze = d_pen + I` is the identity that makes
them one number rather than two.

So "the penalty keeps 57% of its effect" and "43% of the ceiling is shared" are the same number read from two
ends, and **both inherit the 1.61σ of the interaction**: the fractions are point estimates whose departure from
1 is not resolved. The contrast that *is* resolved is the conditional effect itself (penalty given freeze
−0.0201 at **5.53σ**), not its ratio to the unconditional one.

## 3. The axis where the interventions are opposed is the axis where they add exactly

The drift is the one metric where the two interventions push in **opposite directions** — the freeze cost
+0.0054 (21.55σ) of drift, the penalty bought −0.0040 (16.86σ) — and it is the one metric where the combination
is the additive prediction **to six decimal places**: I = +7 × 10⁻⁶ against a ceiling of 0.0040, i.e. **0.17% of
the smaller effect** and 0.03σ, with the per-seed spread of I (0.0017) itself only 0.42× the ceiling.

So: on the axis that measures *how far the body moved*, the two interventions compose with no shared part at
all; on the axis that measures *what is retained*, the whole table's smallest main effect is 4.27σ and the
interaction that would explain how they combine is 1.61σ. **This is `e108` / `e137` / `e139`'s shape seen from
the other side: the quantity on which the two interventions are exactly additive is a quantity this project has
already shown does not order the effect.** If the 1.61σ interaction is real, it is not in the motion.

## 4. The same four cells on `e139`'s whole-body interference — the ordering holds on task 0 and not on task 1

The decomposition runs a second time on the quantity `e139` built its ordering claim on, and the four cells are
available for it because the two arms whose artifacts predate the instrument are carried by later artifacts that
hold **the same arms**: `e140`'s plastic `naive` row is per-replicate identical to `e133`'s (C0a) and `e146`'s
frozen `naive` row to `e125`'s (`e146`'s own identity). Same forty seeds, and the instrument check passes in the
form the freeze forces: the bias's share of the task-0 whole-body term is **0.4524** on `naive` — reproducing
`e139`'s 45% — **0.6888** on the penalty arm, and **exactly 0.0000** on both frozen cells, which is what a
frozen offset must give.

| whole-body first-order term | `naive` | freeze | penalty | both | additive | I | resolution |
|---|---|---|---|---|---|---|---|
| task 0 | 0.4266 | 0.2142 | 0.2472 | 0.0520 | 0.0347 | +0.0173 | **0.25σ** |
| task 1 | 0.2614 | 0.1087 | **0.4505** | 0.0464 | 0.2978 | −0.2514 | 1.14σ |
| mean | 0.3440 | 0.1614 | 0.3488 | 0.0492 | 0.1663 | −0.1171 | 0.96σ |

**The interaction is additive here too**, at 0.25σ on task 0 and 1.14σ on task 1, with per-seed spreads of 2.46×
and 9.17× their ceilings — the interference is a *noisier* quantity than the forgetting on this design, not a
sharper one. (The mean's ceiling, 0.0048, is not interpretable: the penalty's main effect on the mean is
+0.0048, an unresolved level, and the reader now refuses to quote a share when either main effect is below 2σ.)

**And the ordering result is the more interesting half.** Sorted by the task-0 whole-body term the four arms run
**`both` < freeze < penalty < `naive`** — *identically* the ordering by forgetting, which is `e139`'s claim
extended to two cells the instrument had never covered (a frozen arm and a freeze-plus-penalty arm). Sorted by
the task-1 term it runs **`both` < freeze < `naive` < penalty**: the penalty arm has **1.72× `naive`'s**
interference on task 1 while its task-1 forgetting is **0.0250 against `naive`'s 0.0536, less than half**.

So **`e139`'s whole-body ordering is a task-0 statement**, and the task where it breaks is the one where the
diagonal penalty does the relocation `e137` measured: on task 1 the penalty *raises* the first-order interference
while lowering the forgetting. That is `e138`'s "the arm that fixes the forgetting has more interference"
appearing here as a per-task sign, and it is why the mean is a cancelling pair rather than a summary.

## 5. Why forty seeds cannot answer this question, in one number

The seed-level spread of I is **0.0604** on the accuracy-valued forgetting and **0.0918** on the loss-valued one,
against per-seed spreads of the metric itself of **0.0556** and **0.0916**. The ratios are **1.09** and **1.00**.

**The 2x2 subtracts the level but not the noise**: pairing the four arms removes the seed effect from the means
and leaves the interaction's spread at the metric's own per-seed spread, so its resolution is exactly the metric's
— and the interaction is a fraction of a main effect while the noise is not. The price follows arithmetically:

| metric | seeds for 2σ | seeds for 3σ |
|---|---|---|
| forgetting | **62** | 139 |
| loss forgetting | 75 | 168 |
| accuracy | 74 | 167 |
| θ drift | 244,666 | 550,499 |

So *"do the freeze and the weak penalty remove the same forgetting"* is **not answerable at forty seeds**, and a
registered test of it would have to carry ~70–140 seeds — or change the question, and §4 shows that the
interference is not the change: it is additive at the same forty seeds and noisier.

## 6. What this cannot settle

- **CORRECTED 2026-09-24, the same day, by `e156`**: §4's closing sentence — *"the whole-body ordering is a
  task-0 statement"* — is **too strong**. With the five-method table now run twice (the channel free, and the
  unpenalised channel removed from every arm), the same instrument orders **ten** cells at ρ = **+0.927**, and its
  **task-1** form is *better* than its task-0 form (**+0.952** against +0.879; 42/45 pairs against 39/45). What
  this finding actually found is a violation **inside its own four-cell freeze×penalty design**, not a task
  asymmetry of the instrument, so the licensed statement is *"the ordering broke in that four-cell set"* and the
  ten-cell test does not reproduce it
  (`docs/findings/2026-09-24-the-channel-resolved-form-orders-ten-cells-and-the-theta-only-form-mostly-does.md`).

- **It is exploratory and it is not a registration.** The prediction in the script's docstring was written after
  three of the four artifacts had been read, so this is the one reader in `experiments/` whose numbers are not a
  pre-registered result, and nothing here should be cited as one.
- **The interaction is a bound, not a zero.** Forty seeds put any shared part below 0.0154 in absolute terms;
  "additive at this resolution" and "the effects are independent" are different sentences and only the first is
  licensed.
- **The accuracy axis cannot carry an additive reading at all**: one of its two main effects is unresolved
  (penalty alone +0.0049 at 0.91σ), so the ceiling — the smaller main effect — is not a measured effect, and its
  interaction's sign is not interpretable. That is why the shared fraction is left out of the table above.
- One read-out (32), one circuit, three tasks, **one λ** (3e-4) and **one freeze variant** (the offsets, not the
  body); the whole 2x2 sits at the read-out where the offsets' share of the forgetting is largest, so the
  interaction is measured where the unpenalised channel is strongest by construction.
- Both λ-sweep arms say this configuration's optimum is at the edge of the measured grid, so "the penalty" here
  is *the weakest penalty this project has measured*, not the penalty.

## 7. What would decide it

Either the seeds — a registered test at 62–140 replicates, which is a queue cost the project has been avoiding
all session — or a *third* quantity that carries the effect with less noise than the metric does. §4 asked the
interference to be that quantity and it is not: it is additive at the same forty seeds and its per-seed spread is
2.5× to 9× its own ceiling. What §4 does hand the next fire is narrower and real: **the ordering claim is a
task-0 claim**, and the task-1 exception is where the penalty's relocation shows, so the instrument that could
separate the two interventions' shared part may have to be per task rather than per arm.
