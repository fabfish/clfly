# `replay`'s margin tracks the baseline's forgetting, not the channel's share

**Date:** 2026-09-24
**Artifact:** `runs/e148_r32_overlap1_replay.json` — `--input-overlap 1.0 --methods replay`, forty replicates —
against `runs/e144_r32_overlap1_methods_40reps.json` (the same family's `naive` and `ewc` rows),
`runs/e140_r32_methods_plastic_40reps.json` (`replay` on the base family) and
`runs/e133_r32_naive_ewc_40reps.json` (its `naive`).
**The registration** is §6 of `docs/findings/2026-09-24-on-the-wiring-family-the-biology-still-shows-nothing.md`,
written and committed before the run: **P1** `replay` beats `naive` on the wiring family at ≥ 3σ; **P2, the fire**
its margin is **smaller** than the base family's −0.0784 at ≥ 2σ, because `e135`'s arithmetic says replay's
advantage came from a baseline that forgets through a channel no penalty covers, and on the wiring family that
channel carries **44%** of the baseline's forgetting against **70%**; **falsifier** the margin is **larger** by
≥ 2σ, which would make `e135`'s arithmetic specific to the base family and the explanation of replay's margin
about replay rather than about the baseline.

---

## 1. The numbers

| arm | forgetting | mean accuracy | newest-task accuracy |
|---|---|---|---|
| `naive`, wiring family (`e144`) | +0.1068 | 0.8939 | 0.9724 |
| **`replay`, wiring family (`e148`)** | **+0.0083** | **0.9609** | **0.9771** |
| `ewc` (diagonal), wiring family | +0.0630 | 0.9427 | 0.9427 |
| `naive`, base family (`e133`) | +0.0750 | 0.9125 | 0.9667 |
| `replay`, base family (`e140`) | −0.0034 | 0.9609 | 0.9630 |

| contrast, paired on the forty shared seeds | change | resolution |
|---|---|---|
| **P1: wiring `replay` − `naive`** | **−0.0984 ± 0.0091** | **10.79σ, 38/40 negative** |
| base `replay` − `naive` (the comparator) | −0.0784 ± 0.0084 | 9.35σ |
| **P2: the difference of those two differences** | **−0.0201 ± 0.0124** | **1.62σ, in the falsifier's direction** |
| wiring `replay` − wiring `ewc` | −0.0547 ± 0.0075 | 7.30σ |
| wiring `replay` − `naive`, mean accuracy | +0.0670 ± 0.0053 | 12.73σ |
| wiring `replay` − `naive`, newest task | +0.0047 ± 0.0042 | 1.12σ |

## 2. The verdicts

**P1 holds, and by more than the base family's own margin** — 10.79σ against 9.35σ.

**P2 fails, and the falsifier does not fire.** The margin is **larger** on the wiring family by 0.0201, which is
the falsifier's *direction*, but at **1.62σ** it is below the registered 2σ bar. So the registered prediction is
**contradicted in sign and unresolved in size**, which is neither of the two outcomes the registration named — and
it is the **third** registered threshold today to land inside its own uncertainty (`e141`'s P2 at 1.60σ against a
2σ bar, `e142`'s P1 at 2.99σ against 3.00σ, this at 1.62σ against 2σ). Rule 37's theme, arriving again.

## 3. The reading the data do support, and it is simpler than the registry's

**Both `replay` arms drive the forgetting to ≈ 0 — +0.0083 and −0.0034 — so the margin over the baseline is
whatever the baseline had to forget.** That is a floor effect, and it makes a prediction the channel-share story
does not: **margin ÷ baseline forgetting ≈ 1 in every configuration**.

| configuration | baseline's forgetting | `replay`'s margin | ratio |
|---|---|---|---|
| base family | +0.0750 | −0.0784 | **1.045** |
| wiring family | +0.1068 | −0.0984 | **0.921** |
| base family, unpenalised channel frozen in every arm (`e135`, **five** replicates) | +0.0250 | −0.0292 | 1.17 |

**So the wiring family's larger margin is what the floor model predicts** — its baseline has 42% more forgetting to
remove — and it needs no channel-share mechanism. **`e135`'s 66% cut is explained the same way**: freezing
the offsets in every arm took `naive` from +0.0479 to +0.0250 on those replicates, and a method that is already at
zero loses the whole of that reduction. The third row is five replicates, where the ratio's own uncertainty is an order of magnitude larger than the two
forty-replicate rows', so its 1.17 is not evidence against the model; the two forty-replicate ratios are 1.045 and
0.921, i.e. within 8% of the model's prediction from either side.

**And that re-reads the registry's premise rather than refuting it.** `e135`'s arithmetic is a statement about the
*frozen* comparison — where the baseline's forgetting is reduced — and it is true there. What the wiring family
tests is a different move (a baseline with *more* forgetting), and the floor model says the margin should grow,
which is what happened. The registration's error was to treat "the unpenalised channel's share" as the quantity
the margin tracks when the simpler quantity — **the baseline's total forgetting** — fits both families and the
frozen arm without a free parameter.

## 4. The two registered descriptive checks, and both keep the paper's headline standing

- **The family chosen to contest the paper's headline does not contest it**: `replay` beats the wiring family's
  **diagonal** by **−0.0547 ± 0.0075 = 7.30σ**, against **9.35σ/1.21σ** on the base family. The registration said
  that if the diagonal's 4.73σ on this family were real the two methods might be close; they are not — the
  diagonal is beaten on the family where it is strongest.
- **`replay` again pays nothing on the newest task** (wiring **+0.0047 at 1.12σ**, base −0.0036 at 0.79σ), while
  the wiring diagonal pays **4.57σ** there. This is the third family/arm pair in which the method that reaches
  zero forgetting is also the one that does not buy it with last-task accuracy, consistent with `e151`'s
  twelve-arm census and `e152`'s frontier.

## 5. One caution the artifact itself supplies

**The two `replay` arms' mean accuracies agree to 1.5 × 10⁻⁹** (0.9609374995 against 0.9609375010, i.e. the same
total correct count over 5,760 evaluations) **while their per-replicate accuracies differ by up to 0.0486 and are
not identical**. So a reader comparing aggregates would call this a reproduction and be wrong: only per-replicate
identity is a reproduction in this project (`e140`'s C0a, `e146`'s tell), and two arms on **different task
families** agree here at the fifth decimal by coincidence of the aggregate. The agreement is real, is not an
identity, and licenses nothing.

## 6. What this cannot settle

- **One read-out (32), one overlap value (1.0), three tasks and one seed set.** The falsifier's 1.62σ is a bound on
  the *family difference* and this design cannot separate a floor effect from a channel effect that happens to be
  the same size; the two are distinguished by the ratio table above and not by a manipulation.
- **The floor model is fitted and not manipulated**: its two forty-replicate points both come from this project,
  but a configuration whose baseline forgets *less* than the frozen base family (+0.0227) would be the third test,
  and it does not exist yet.
- **`replay`'s own level is not exactly zero** (−0.0034 and +0.0083, each 1–2σ from it), so "the margin is the
  baseline's forgetting" is a model with a residual, not an identity.
- The wiring family's five-method table is still **four** methods plus this row: `ewc-block` and `ewc-block-rand`
  have never been run at `--input-overlap 1.0` with `replay` present, so the family's *ranking* under replay is
  assembled from two artifacts rather than measured in one table.
