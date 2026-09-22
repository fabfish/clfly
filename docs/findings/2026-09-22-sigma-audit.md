# E22 — a σ audit: every headline significance in the project, its design, and which way the omissions err

**Date:** 2026-09-22
**Script:** `experiments/e2_topology_gap.py` (contrast now paired when per-seed data exists), `runs/e21_e2_paired.json` (in flight)
**Context:** the control-draw work (`…control-drawn-once.md`, `…draw-budget.md`), the pairing work (`…shape-needs-paired-contrasts.md`, `…evaluation-noise.md`)

---

## 1. Why an audit

One methodological omission has now been found in four separate places: **a comparison was reported
with the formula that does not match its design.**

- the ladder's matched-pair *shape* contrasts used the unpaired formula on matched rungs;
- the ladder's deltas used a **single control draw** where the population was meant;
- the rate network reported a paired bio-versus-control comparison **unpaired**;
- and one power table used the **mean of two arms' sds** as if it were the sd of a difference.

Each was found by accident, while chasing something else. So the obvious move is to enumerate every
significance the project publishes and check its design, rather than wait to trip over the fifth.

## 2. The audit

| claim | reported | design | matches? | direction of the error |
|---|---|---|---|---|
| interference refutation, `swap0.5 → swap2` | **32.7σ** unpaired | paired — the task seeds are shared across topologies | **no** | conservative (see §3) |
| eigenbasis −28%, −0.00491 | 15.4σ unpaired | paired — same seeds | **no** | conservative |
| diagonal penalty +33–63% | a ratio, no σ | EWC vs the exact oracle | n/a | — |
| ladder rung deltas (e.g. `pool4` 42.2σ) | seed-only | one control draw | **no** | **optimistic** — corrected to 13.7σ |
| sign flip, 5 topologies | seed-only | one control draw | **no** | **optimistic** — corrected, and the draw sd now measured |
| predictor's matched pairs, 13/13 | seed-only | one control draw | **no** | **optimistic** — checked, count is 13 or 12 |
| rate-network matched pair | unpaired | paired | **no** | conservative — corrected, and it is 1.5–2.4× |
| C4 interference prior, ρ = +0.939 | LOO correlation | none | n/a | — |

## 3. The result: the same omission errs in *opposite* directions

This is the part worth keeping. The unpaired formula is used in two structurally different
situations, and it fails oppositely in each:

- **When the dominant noise is the control draw** (a single random partition), the unpaired formula
  ignores a component entirely, so the reported σ is **optimistic**. That is the ladder's problem,
  and it is why 42.2σ became 13.7σ.
- **When the two arms share seeds and no control is involved**, the unpaired formula *overstates*
  the sem whenever the arms correlate positively across seeds, so the reported σ is
  **conservative**. That is the `e2` problem, and it means the 32.7σ refutation and the eigenbasis'
  15.4σ are **lower bounds**, not overclaims.

So "we used the unpaired formula" is not a diagnosis on its own: it is a bug in one regime and a
safe approximation in the other. Which one you are in is decided by whether the comparison's two
arms differ by the *task draw* or by the *control draw*.

The conservatism claim rests on the correlation being positive, and it is worth being precise about
what can and cannot be shown. **Every cross-arm correlation measured in this project is n = 3**
(the rate network's replicates) or n = 3 with a *random* control (the d = 952 ladder, where the
measured values are +1.00 ×3, −0.63, −0.11, −0.09 — and I have already argued those are
uninformative, since three points lie almost on a line). So no *estimate* of `e2`'s correlation is
available.

What is available is a **variance-decomposition argument**, which does not depend on a sample: the
same task sequences are used at every topology, so each topology's excess contains a shared
task-draw component. A harder task set raises the excess at *both* topologies, so that component
contributes positively to the covariance; the rewiring-specific components are independent across
topologies. Hence **E[corr] > 0 by construction**, and the unpaired sem is conservative in
expectation. How far conservative in a given 3-seed sample is not established, and `e21` measures it
for this contrast rather than assuming it.

## 4. What has been fixed, and what is now measured

`e2_topology_gap.py`'s adjacent-contrast table now uses `paired_contrast` whenever both topologies
carry per-seed values, and says so when they do not — the same symmetry `e3` already had. The
published `runs/e2_analytic.json` predates per-seed storage, so the audit's conclusion for the 32.7σ
is an *inference*; `e21` re-runs the three topologies that carry it (`real`, `swap0.5`, `swap2`,
3 seeds) with per-seed storage, which turns the inference into a number.

## 5. What the audit does not claim

- It does not claim any *conclusion* changes. Where the error was optimistic, the corrected figures
  are 3–9σ and the claims survive; where it was conservative, the claims strengthen. **No headline in
  this project has been found to be wrong in sign or substance by any of the four omissions**, which
  is itself worth stating plainly given how many were found.
- It does not check the *realized*-metric results, which are superseded by the analytic estimator
  everywhere the paper quotes a number.
- The `e2` entries in §2 remain inferences until `e21` reports; they are marked as such rather than
  folded into the table as measured.

## 6. A statement in the earlier findings was imprecise, and is corrected

`2026-09-22-control-drawn-once.md` §7 says: *"Results that use **no** random control are untouched:
the `e2` topology family, the eigenbasis comparison, and the network line's method comparison."*
The `e2` topology family is not one thing — its **excess** contrasts use no control and are
untouched, but the same script also computes a `bio − rand` contrast, which is where the sign-flip
analysis lives and which the draw correction *did* change. The eigenbasis comparison is genuinely
untouched (it is a fixed basis against the diagonal, no random control anywhere), and so is the
network line's *method* comparison. The distinction is per-contrast, not per-experiment, which is the
same lesson as §3 in a smaller form.

---

## Correction (next fire): the conservatism was an inference, and the measurement refutes it for `e2`

§3 argues that `e2`'s unpaired contrasts must be conservative because the shared task-draw component
makes ``E[corr] > 0`` by construction. `e21` measures it, at d = 952 with per-seed storage:

| contrast | unpaired | **paired** | r |
|---|---|---|---|
| `real → swap0.5` | 2.7σ | 2.4σ | −0.216 |
| `swap0.5 → swap2` | 24.4σ | **21.8σ** | **−0.274** |

The correlation is **negative**, so the paired sem is 1.10–1.12× *larger* and the unpaired figure is
mildly **optimistic** — the opposite of the inference. With n = 3 the sign of a correlation of −0.27
is itself not determined, so this does not establish a negative population correlation either. What
it establishes is the narrower and more useful thing: **the shared task-draw component is not large
enough to make the conservatism safe to assume.** The `e2` rows of §2 should be read as *unresolved*
rather than conservative.

The empirical lesson is the one this project keeps re-learning: a variance-decomposition argument
that sounds structural ("the tasks are shared, therefore the covariance is positive") can be
outweighed by whatever else varies between the arms, and only a measurement settles which dominates.
