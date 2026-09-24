# The aggregate hides the diagonal five times, and every constrained method pays on the task no forgetting term covers

**Date:** 2026-09-24
**Script:** `experiments/e151_pertask_contrast_audit.py` — **an audit, no runs.** It takes every contrast the
record quotes at forty paired replicates and decomposes it into the two terms that average to `mean_forgetting`,
plus the one quantity the aggregate *cannot* contain by construction: the final accuracy on the newest task.
**Artifacts:** the 22 contrasts in the registry, all on disk (`runs/e1{25,33,38,40,41,42,43,44,47}_*`).
**What it is for:** the plan has named this trap twice by hand — the diagonal improves task 0 while worsening
task 1, and the anchored arm's last-task cost is invisible to a mean over the first `T − 1` tasks. This is that
hand search done once, as a rule rather than as a memory.

---

## 1. The rule, so the catalogue cannot be read selectively

For A − B on forty paired seeds: the aggregate, each of the two terms, and the newest task's retention. The label
is a function of σ and signs, never of taste:

| label | condition | what the aggregate is |
|---|---|---|
| **fair** | resolves, both terms resolve with its sign | a summary of one effect |
| **one term** | resolves, exactly one term resolves | a summary of a lopsided effect |
| **weak pair** | resolves, neither term resolves, signs agree | the sum of two sub-threshold hints |
| **cancelling** | resolves, the terms' signs disagree | a *difference* between two effects |
| **hidden** | does **not** resolve while a term does | the printed number is not the effect |
| **null** | nothing resolves | — |

## 2. The catalogue

| contrast | aggregate | σ | task 0 | σ | task 1 | σ | newest | σ | class |
|---|---|---|---|---|---|---|---|---|---|
| e133: ewc − naive (λ = 3e-3) | −0.0096 | 1.21 | **−0.0354** | **3.79** | +0.0161 | 1.37 | **−0.0526** | **6.63** | **hidden** |
| e140: ewc − naive (same arm) | −0.0096 | 1.21 | −0.0354 | 3.79 | +0.0161 | 1.37 | −0.0526 | 6.63 | hidden |
| e140: block − naive | −0.0177 | 2.09 | −0.0182 | 1.36 | −0.0172 | 1.60 | −0.0083 | 1.55 | weak pair |
| e140: block-rand − naive | +0.0029 | 0.28 | +0.0016 | 0.10 | +0.0042 | 0.33 | −0.0104 | 2.08 | null |
| **e140: replay − naive** | **−0.0784** | **9.35** | −0.0906 | 6.63 | −0.0661 | 6.91 | −0.0036 | **0.79** | fair |
| e140: block − block-rand | −0.0206 | 2.08 | −0.0198 | 1.38 | −0.0214 | 2.27 | +0.0021 | 0.34 | one term |
| e141: λ 3e-4 − naive | −0.0354 | 4.27 | −0.0422 | 3.54 | −0.0286 | 2.87 | −0.0297 | 6.47 | fair |
| e141: λ 3e-2 − naive | +0.0060 | 0.58 | −0.0219 | 1.64 | **+0.0339** | **2.22** | −0.0755 | 9.45 | **hidden** |
| e141: λ 3e-1 − naive | +0.0096 | 0.85 | −0.0208 | 1.52 | **+0.0401** | **2.38** | −0.0729 | 9.00 | **hidden** |
| e141: λ 3e-4 − λ 3e-3 | −0.0258 | 3.74 | −0.0068 | 0.81 | −0.0448 | 4.70 | **+0.0229** | **2.97** | one term |
| e138: anchored 1.0 − naive | −0.0398 | 4.63 | −0.0583 | 4.06 | −0.0214 | 2.29 | −0.0688 | 9.70 | fair |
| e138: anchored 33.2 − naive | −0.0458 | 4.84 | −0.0708 | 5.80 | −0.0208 | 1.75 | −0.0620 | 8.88 | one term |
| e138: anchored 33.2 − unanchored | −0.0362 | 4.03 | −0.0354 | 3.58 | −0.0370 | 2.95 | −0.0094 | 1.02 | fair |
| e125: frozen offsets − naive | −0.0523 | 5.90 | −0.0672 | 4.75 | −0.0375 | 3.81 | −0.0266 | 4.42 | fair |
| e147: frozen+ewc − frozen | −0.0201 | 5.53 | −0.0297 | 5.52 | −0.0104 | 2.15 | **−0.0328** | **6.49** | fair |
| e147: frozen+ewc − naive | −0.0724 | 8.61 | −0.0969 | 7.06 | −0.0479 | 4.47 | −0.0594 | 9.16 | fair |
| e142: overlap 1.0 − base | +0.0318 | 2.99 | +0.0349 | 2.02 | +0.0286 | 2.20 | +0.0057 | 1.10 | fair |
| e143: wiring frozen − wiring naive | −0.0469 | 5.04 | −0.0443 | 2.99 | −0.0495 | 4.47 | −0.0245 | 4.07 | fair |
| e144: ewc − naive (wiring) | −0.0437 | 4.73 | −0.0693 | 5.20 | −0.0182 | 1.13 | −0.0297 | 4.57 | one term |
| e144: block-rand − naive (wiring) | −0.0216 | 2.48 | −0.0250 | 2.02 | −0.0182 | 1.74 | −0.0026 | 0.65 | one term |
| e144: block − block-rand (wiring) | −0.0018 | 0.17 | −0.0047 | 0.40 | +0.0010 | 0.07 | −0.0021 | 0.54 | null |

**Counts over 22 contrasts: fair 9, one term 5, hidden 5, null 2, weak pair 1, cancelling 0.**

## 3. Three things the catalogue says

**First, the aggregate is a *fair* summary of every large effect.** Replay's 9.35σ is −6.63σ and −6.91σ on the two
terms; the frozen-and-penalised arm's 8.61σ is −7.06σ and −4.47σ; the λ = 3e-4 arm's 4.27σ is −3.54σ and
−2.87σ; the anchored arms are the same shape. **There is no contrast in this record whose headline number is
manufactured by an average of two disagreeing terms** — the one `cancelling` slot is empty. That is worth stating
plainly because the opposite was expected: the trap this audit was built to catch does not fire on the effects
the paper prints.

**Second, all five `hidden` slots are the same arm family — the diagonal at λ ≥ 3e-3 — and in each the hidden
half is a *pair*.** At λ = 3e-3 the aggregate is 1.21σ while task 0 resolves at **3.79σ in the diagonal's
favour** and task 1 at 1.37σ against it; at λ = 3e-2 and 3e-1 the aggregate is 0.58σ and 0.85σ while task 1
resolves at **2.22σ and 2.38σ *against*** the method. **So "the diagonal's effect is not resolved" is a statement
about a mean, and at the top of the λ sweep the same forty pairs say the method *is* resolved — as a trade, in
the wrong direction on one task.** The three distinct arms appear five times because two rows are C0a-identical
(`e133`'s `ewc` and `e140`'s, and `e141`'s λ = 3e-3 is that same arm).

**Third — and this is the systematic result — the newest task's retention is where the constraint is paid, and
the one method in the record that is not a constraint pays nothing.** Take the twelve contrasts of a constrained
arm against its own baseline: **ten of them resolve as a cost on the newest task's final accuracy, running from
2.08σ to 9.70σ** — λ = 3e-3 at 6.63σ, λ = 3e-4 at 6.47σ, λ = 3e-2 at 9.45σ, λ = 3e-1 at 9.00σ, anchored 1.0 at
9.70σ, anchored 33.2 at 8.88σ, the freeze at 4.42σ, frozen-plus-penalty at 6.49σ against the freeze and 9.16σ
against `naive`, `block-rand` at 2.08σ, the wiring family's diagonal at 4.57σ — and **the two that do not are
both `block` partitions** (`block` − `naive` at 1.55σ, the wiring family's `block-rand` at 0.65σ), which are also
the two constrained arms whose own forgetting contrasts are the smallest (2.09σ, the catalogue's only `weak pair`,
and 2.48σ). The count is over **twelve distinct constrained arms**; the table lists fourteen rows for them because
two are C0a-identical repeats of arms listed elsewhere. **And replay — the one arm here that is not a
constraint — pays −0.0036 at 0.79σ**, so its 9.35σ forgetting advantage, the largest ever measured on this
benchmark, is bought with no measurable last-task cost at all. **`mean_forgetting` is a mean over the first
`T − 1` tasks, so this column is invisible to every number the paper prints about retention**, which is exactly
the eighth trap, now measured over 22 contrasts instead of argued about.

## 4. And it corrects a finding of mine from earlier today

`e147`'s finding says the frozen-plus-penalty arm's accuracy is *"1.49σ below the freeze's (0.9306, i.e. the
same)"*. **That is true of the mean over three tasks and false of the newest one.** Per task, against the freeze
alone: task 0 **+0.0297 (5.52σ, better)**, task 1 **−0.0073 (1.54σ)**, and the newest task **−0.0328 (6.49σ,
worse)**. Against `naive` the same three are **+0.0750 (5.80σ)**, **+0.0281 (2.35σ)** and **−0.0594 (9.16σ)**.

**So the session's best result is partly bought on the task that `mean_forgetting` cannot see.** The sentence
"the pair closes the forgetting problem" stands — +0.0026 is +0.0026 — but it is not free, and the price is
visible in one place only: the final accuracy on the newest task, where the pair is **9.16σ below `naive`** and
**6.49σ below the freeze it was combined with**. The mean-accuracy line hid it because the two old tasks
*improved* (+5.80σ and +2.35σ). `e147`'s finding is quoted above and corrected here.

## 5. What this cannot settle

- **It is an audit of stored artifacts**, so it inherits their limits: one read-out (32), one circuit, three
  tasks, one seed set, and `T = 3` means "the middle task" and "the last forgettable task" are the same column,
  so no contrast here can separate a task-1 effect from a "second-of-two" effect.
- **The newest-task column is `final_per_task[-1]`**, which mixes how well the task was learned with how much
  interference it took, and the two are separated elsewhere (`learned`) rather than here.
- **The labels depend on a 2σ threshold**, and rule 37 already says a threshold needs its own uncertainty: four
  entries sit between 2.02σ and 2.38σ on some column (e142's task 0 at 2.02σ, e144's block-rand task 0 at 2.02σ,
  λ = 3e-2's task 1 at 2.22σ), so the class of a marginal entry is not a stable fact. The registry is a fixed
  list of 22 contrasts, not every contrast the artifacts could support.
- **And it does not say the constraints are bad.** Paying on the newest task is what a constraint does; the
  finding is that **no number in the paper's method tables could have shown it**, which is a statement about the
  metric and not about the methods.
