# `e142`: at the registration's resolution limit

**Date:** 2026-09-24
**Script:** `experiments/e8_rate_network.py`, unchanged.
**Artifact:** `runs/e142_r32_overlap1.json` — `--input-overlap 1.0 --readout-size 32 --shared-head --repeats 40`.
**Comparator:** `runs/e133_r32_naive_ewc_40reps.json`'s `naive` — the **same** `make_overlap_suite` at
`--input-overlap 0.0`, the same seeds, the same configuration in every other respect.
**Pre-registration:** `docs/findings/2026-09-24-the-overlap-family-at-a-narrow-read-out-registered.md`.
**The plastic arm has landed. P1 misses its registered bar by 0.01σ; the falsifier does not fire; the frozen-body
premise is still running.**

---

## 1. The measurement

| | overlap 0.0 (`e133`'s `naive`) | **overlap 1.0** |
|---|---|---|
| mean forgetting | +0.0750 ± 0.0088 | **+0.1068** (per-repeat sd 0.0584) |
| **paired difference** | — | **+0.03177 ± 0.01063 = 2.9876σ**, 29/40 positive |
| learned (diagonal), per task | 0.9682 / 0.9526 / 0.9667 | **0.9682 / 0.9547 / 0.9724** |
| final accuracy | 0.9125 | **0.8939** (−0.0186 ± 0.0069 = **2.69σ**) |
| θ drift, final | 0.0498 | 0.0465 |

Per task: **+0.0349 ± 0.0173 = 2.02σ** on task 0 and **+0.0286 ± 0.0130 = 2.20σ** on task 1 — so the increase is
spread across both and **neither resolves on its own**, which is the shape that makes the aggregate the right
statistic here and also the reason the aggregate's resolution is the whole question.

**So three identical input populations — the same 80 neurons driven with three different class templates — raise
the forgetting by 42%** (0.0750 → 0.1068) while costing 2.7σ of final accuracy.

## 2. And the registration's three parts

- **P1 — "resolved at ≥ 3σ" — IS NOT MET, by 0.012σ.** A 3.00σ bar needs an effect of **0.03190**; the effect is
  **0.03177**. The prediction misses by **0.00013 in the effect**, which is what "at the threshold" means
  numerically.
- **The falsifier does not fire.** It was registered at "within 2σ of `e133`'s `naive`", and 2.99σ is not within
  2σ — so the outcome that would have **emptied §8's second route** did not happen either.
- **C1, the premise, is still running.** The frozen-body arm at the same setting is in flight, and it is the
  control that says whether the body is load-bearing for *this* family — the whole reason the question was worth
  asking at a narrow read-out. **Nothing above is interpreted until it lands.**

## 3. What the registration feared, and did not happen

The registration listed a **knife-edge** as a possible outcome: if the shared-input family's `learned` accuracies
collapsed toward chance, the family would be **too hard rather than harder**, and the forgetting would be
uninterpretable. **They did not collapse**: the diagonal is 0.9682 / 0.9547 / 0.9724 against the overlap-0
family's 0.9682 / 0.9526 / 0.9667 — identical on task 0, within 0.5% on the others. **The family is exactly as
learnable and forgets 42% more**, which is what a harder benchmark is supposed to look like.

## 4. The methodological finding, which is the part worth keeping

**A bar at 3.0σ whose estimate is a sem computed from forty pairs is not a bright line.** That sem carries a
relative uncertainty of about **11%**, so the same data are consistent with roughly **2.7σ to 3.4σ**, and the
registered statement *"resolved at ≥ 3σ"* **cannot distinguish "met" from "missed"** at the resolution the
statistic has. The sign test on the same forty pairs — which the registration did not name — gives **29/40
positive, two-sided p = 0.0064**.

**So the honest report has three parts, and none of them is "the prediction failed" in the sense that matters:**

1. the **direction** was registered and is what was measured, at +42%;
2. the **registered form** of the threshold is **not met**, and it is not met by a margin an order of magnitude
   below the statistic's own uncertainty;
3. **the falsifier that would have killed the route did not fire**, so the reading the registration would have
   accepted as *no* is not the reading the data support either.

**And the lesson is a rule rather than a re-registration**: a threshold has to be either far enough from the
estimate to be **decidable** at the sample size, or the registration has to say **which of the available forms**
(paired σ, sign test, effect ratio) is the one that decides — **before** the number is known. Choosing after is
how a soft bar becomes a coin flip, and choosing the form that happens to clear it would be the same defect one
level up. This is rule 30's demand — *a cost computed from an sd needs the same evidential standard as the
effect* — arriving on the **threshold**. `docs/research_plan.md` rule **37** records it.

## 5. What this cannot settle

- **C1 is in flight and it is the premise.** If the frozen body matches the plastic arm at overlap 1.0, then
  sharing the input population has restored decoder-solvability, the body is not load-bearing for this family
  either, and **the 42% is a fact about a benchmark that the decoder can solve alone** — which would be the
  registration's C1 failing rather than P1 deciding anything.
- **One overlap value (1.0), one read-out (32), one seed set, the shared head.** The suite supports 0.25/0.5/0.75
  and a *shape* in overlap is the second fire; per-task heads would change what the body must do and are not
  varied.
- **The comparator is a different task family from the default suite**: `--input-overlap 0.0` picks its input
  populations **at random** while the default suite uses identified circuits (`KC → MBON`, `CX`, `ALPN → KC`), so
  this is a statement about *overlap* and not about the default tasks.
- **No method has been run on the harder family.** The fire can say the problem is harder and nothing about which
  method handles it — and `e140`/`e141`, which would, are on the training-free configuration.
- **And the extra forgetting's channel has only a negative first reading.** The two families' bodies move the same
  amount — the bias's cumulative path differs by **0.01σ** and θ's drift by 0.00σ / 1.43σ / **−4.45σ** — which on
  norms alone says nothing about which channel carries the 42%, and `e137`'s own lesson is why it says nothing:
  an intervention that removes 70% of an effect can coexist with a weak across-seed correlation. `e143`
  (`--frozen-bias` at overlap 1.0) is the run that decides it, registered with a convergence prediction and the
  opposite falsifier (`docs/findings/2026-09-24-the-harder-family-moves-the-body-the-same-amount.md`).
