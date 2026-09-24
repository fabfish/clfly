# The penalty works once the channel is held still — and it goes *below* the freeze

**Date:** 2026-09-24
**Artifacts:** `runs/e147_r32_frozenbias_ewc_lam3e-4.json` — `--frozen-bias --methods ewc --lam 3e-4`,
forty replicates — against `runs/e125_r32_frozenbias.json` (offsets frozen, **no** penalty),
`runs/e141_r32_ewc_lam3e-4.json` (the same λ **unanchored**) and `runs/e133_r32_naive_ewc_40reps.json`.
**The `λ = 3e-3` arm of the same design is still running**, so the registered λ-against-λ contrast is pending;
**the registered *third* outcome is not**, and it is refuted in the opposite direction.

---

## 1. The table

| arm | forgetting | accuracy | θ drift |
|---|---|---|---|
| `naive` | +0.0750 | 0.9125 | 0.0498 |
| `ewc` λ = 3e-3, unanchored | +0.0654 | 0.8856 | 0.0357 |
| `ewc` λ = 3e-4, unanchored | +0.0396 | 0.9174 | 0.0428 |
| **offsets frozen, no penalty** (`e125`) | +0.0227 | 0.9306 | 0.0547 |
| **offsets frozen + `ewc` λ = 3e-4** (`e147`) | **+0.0026** | 0.9271 | 0.0478 |

Paired over the forty shared seeds:

| contrast | change | resolution |
|---|---|---|
| **`e147` − `naive`** | **−0.0724 ± 0.0084** | **8.61σ**, 38/40 negative |
| **`e147` − the freeze alone** | **−0.0201 ± 0.0036** | **5.53σ**, 29/40 negative |
| **`e147` − the same λ unanchored** | **−0.0370 ± 0.0077** | **4.82σ**, 27/40 negative |
| `e147` − `ewc` λ = 3e-3 unanchored | −0.0628 ± 0.0082 | 7.70σ, 33/40 negative |

**Forgetting is 3.5% of `naive`'s and 11.5% of the freeze's** — a configuration that has essentially stopped
forgetting, at an accuracy **1.49σ below** the freeze's (0.9271 against 0.9306, i.e. the same) and **2.55σ
above** `naive`'s.

## 2. Three things this says

**First, the penalty and the constraint are complementary, and the penalty's effect is *masked* by the free
channel.** The identical penalty — λ = 3e-4, diagonal — gives **+0.0396** with the offsets free and **+0.0026**
with them held still: **the channel's freedom costs it 0.0370 (4.82σ)**. That is `e137`'s substitution with the
sign of the *intervention* reversed: the penalty's effect is real and about nine tenths of it is destroyed by the
channel it does not press.

**Second, the freeze is not a floor.** §4.2's note says the diagonal *"recovers 84.8% of the gap to the free
freeze"* and **approaches the freeze's +0.0227 from above without reaching it** — a penalty is not a freeze. **Here
the penalty plus the constraint goes 5.53σ *below* the freeze**, which the framing did not expect: the freeze alone
leaves +0.0227 of forgetting and the freeze plus a weak penalty leaves +0.0026. **So freezing the offsets is not
the best a constraint on them can do** — it removes their adaptation but leaves the *weights* unpenalised, and it is
the pair that closes the problem.

**Third, and it re-reads the λ sweep.** `e141` found the diagonal's optimum at λ = 3e-4 (0.0396) and the whole
curve above it worse; **with the offsets held still the same λ does three times better than the *best* unanchored
setting**, so λ's interior optimum is the optimum *given a channel that absorbs the penalty*, not the optimum of
the penalty.

## 3. What is pending and what is refuted

- **The registered λ-against-λ contrast is pending** (the λ = 3e-3 arm of this design is running): P1 said λ
  still matters with the channel held still (≥2σ), the falsifier that the two λs agree within 2σ.
- **And the registered *third* outcome is refuted**: I registered that both arms might land at `e125`'s frozen
  value, *"the penalty adds nothing once the channel is held still"*. **It adds −0.0201 ± 0.0036 = 5.53σ**, i.e.
  it adds more than the freeze did — and the refutation is in the *constructive* direction, which is the outcome
  the registration listed third and expected least.
- **And the falsifier's own consequence clause is refuted by the same contrast, which the registration did not
  organise.** The falsifier was *"the two arms are within 2σ of each other"*, and what it was registered to imply
  was stated in one breath: λ's whole effect runs through the uncovered channel, so `--frozen-bias` at both λ
  **would agree with each other and with `e125`'s frozen arm (+0.0227)**. The first clause is still pending — the
  second arm is running — but the second clause is already measured: this arm is **5.53σ below `e125`**, so
  *"λ's entire effect runs through the uncovered channel"* is refuted whatever the 3e-3 arm does. Two of the
  registration's three outcomes are therefore decided, in the same direction, by one arm; only the λ-against-λ
  clause remains.

## 4. What this cannot settle

- **One read-out (32), one circuit, three tasks, and one λ for this arm**; the λ = 3e-3 arm will say whether the
  near-zero is a property of the *combination* or of this particular λ.
- **CORRECTED 2026-09-24 by `e151`, which decomposed this contrast per task: the accuracy sentence in §1 holds of
  the mean and not of the newest task.** "*1.49σ below* the freeze's, i.e. the same" is the mean over three tasks;
  per task against the freeze alone, task 0 is **+0.0297 (5.52σ, better)**, task 1 **−0.0073 (1.54σ)** and the
  newest task **−0.0328 (6.49σ, worse)** — and against `naive` the same three are **+0.0750 (5.80σ)**,
  **+0.0281 (2.35σ)** and **−0.0594 (9.16σ)**. **So the pair's near-zero forgetting is partly bought on the one
  task `mean_forgetting` cannot see**, the price is invisible in the mean accuracy because the two old tasks
  improve, and the unaffected sentence is the forgetting one (+0.0026 is +0.0026). The audit that found this, and
  the twelve-arm version of the pattern, is in
  `docs/findings/2026-09-24-the-aggregate-hides-the-diagonal-and-the-last-task-pays.md`.
- **`--frozen-bias` remains a diagnostic and not a method**: it changes the model class, and a ranking produced
  under it is a ranking on a body whose offsets never move. **What this fire establishes is not that practitioners
  should freeze the offsets — it is that the diagonal penalty's measured effect is conditional on a channel the
  penalty does not press**, which is a statement about the penalty and about the benchmark.
- **And it does not touch replay**, which reaches −0.0034 unanchored on this family's neighbour — i.e. replay
  achieves near-zero forgetting *without* any freeze, so the honest comparison of "what the combination buys" is
  against the best single method and not only against the freeze.
