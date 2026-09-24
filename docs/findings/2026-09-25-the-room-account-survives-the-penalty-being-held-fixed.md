# The room account survives the penalty being held fixed, and the Fisher's share is 1.13σ from zero

**Date:** 2026-09-25
**Script:** `experiments/e176_shared_penalty_read.py` — written before `e175`'s artifacts existed, run on both now.
Artifacts: `runs/e176_shared_penalty_read.json`, `runs/e175_r32_ref_noise1.0.json`,
`runs/e175_r32_noise0.5_shared.json`, and `runs/e175_inputs/` (80 per-replicate input files).
**Registered as:** `e175` (the two commands) and `e176` (the three predictions), both in the programme table before
either artifact existed.

---

## 1. The three predictions, read

**P0 — a control on the new flags, and it passes exactly**: the reference run's `naive` is **bit-identical** to
`e133`'s and its `ewc` is **bit-identical** to `e141`'s. So *writing* the penalty's inputs does not move a number,
and that is identity rather than equality within a tolerance.

**P1 — the control the design needs, and it passes exactly**: the shared-penalty run's `naive` is
**bit-identical** to `e167`'s noise-0.5 `naive`. That is one bit-identity doing two jobs: the stored Fisher cannot
reach an arm with no penalty, **and the level in the two low-noise runs is the same level** — so every difference
below is the penalty's inputs and nothing else.

**P2 — the account's test, with the penalty held fixed:**

| | level step | the gain's step | resolution |
|---|---|---|---|
| noise 0.5, penalty **held fixed** (one term for both runs) | **−0.0312** | **−0.0266** | **2.73σ** |
| noise 0.5, each run with its **own** Fisher (`e167`) | −0.0312 | −0.0370 | 3.57σ |

**The falsifier does not fire.** With the penalty's Fisher, anchor and λ **identical** across the two levels, a
lower forgetting level still costs the penalty **2.73σ** of its advantage. A design registered to *overturn* the
room account did not.

## 2. The Fisher's share, measured: 28% by point estimate and **1.13σ from zero**

The two low-noise runs differ **only** in where their Fisher came from, and they share a level and a seed stream, so
their difference is the Fisher's contribution on the nose:

**+0.0104 ± 0.0093 = 1.13σ** — i.e. **28%** of the own-Fisher step by point estimate, and **not resolvable at forty
seeds**.

**So the honest reading is a decomposition with one resolved term and one bound**: **the room accounts for the whole
part of the effect this sample can resolve (2.73σ), and the Fisher's share is smaller than the sample can see.**
**Rule 42's arithmetic on that number**: the effect is 0.0104 with a per-seed sd of 0.0588, so resolving *its* 3σ
needs about **290 seeds** — seven times this line's forty, and past the queue.

## 3. Why this is the strongest form the account's evidence has taken

Three kinds of evidence now agree, and they are of different kinds on purpose:

1. **`e166`'s census** — correlational, over every single-field manipulation the corpus had, found the direction 5
   of 5 with the field that cannot move the level moving it anyway;
2. **`e167`'s noise knob** — a level knob at fixed architecture, but each run with its own Fisher, so the confound
   was *named* and bounded rather than removed;
3. **`e175`, this** — the confound **removed by construction**: the penalty term is one object, stored by one run
   and replayed by the other, and the level across the two low-noise runs is bit-identical.

**And the design's own registration is what makes it evidence rather than a demonstration**: the falsifier was "with
the penalty shared the gain's step collapses toward zero, which would say the whole `e167` effect was the Fisher
being re-measured", and it is written in the plan before the artifacts existed.

## 4. What this cannot settle

- **The Fisher's share is unresolved, not zero.** 28% at 1.13σ is what forty seeds can say, and §2's arithmetic
  says what more seeds would buy. "The room accounts for the resolved part" is not "the Fisher contributes nothing".
- **One configuration**: one family (the base family's plastic arm), one read-out (32), three tasks, one seed
  stream, and λ = 3e-4 only. The wiring family's λ-insensitivity (`e162`) is a different regime and not re-tested.
- **The shared term is the *reference's* term.** Replaying it means the noise-0.5 run is penalised by the Fisher and
  anchor a noise-1.0 run had — which is exactly "the penalty held fixed", and also means the shared run's term is not
  the term such a run would *have*. That is the design and not a flaw, but it bounds the claim: it is about *this*
  penalty applied at two levels, not about the penalty each level would choose for itself.
- **`e173`'s dose confound does not apply here** (the iteration count is fixed) — and neither does its null, since
  `noise` is a level knob and `iters` is not.
- **The instrument's own limits** are in the parent finding: the flags cover the diagonal `ewc` only (the block
  methods are refused rather than silently given the wrong object), and the store is per replicate because the
  Fisher is seeded per replicate.
