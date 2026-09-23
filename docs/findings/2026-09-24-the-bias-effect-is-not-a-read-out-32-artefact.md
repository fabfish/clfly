# `e134`: the bias effect is not a read-out-32 artefact — it is present at all three read-outs, and both registered predictions were in the wrong unit

**Date:** 2026-09-24
**Script:** `experiments/e134_frozenbias_readouts.py` (new); artifact `runs/e134_readouts.json`.
**Arms:** `runs/e125_r32_frozenbias.json` and `runs/e134_r128_frozenbias.json`, 40 replicates each, against
`runs/e116_r32_40reps.json` and `runs/e116_r128_40reps.json`.
**Pre-registration:** `docs/findings/2026-09-24-is-the-bias-effect-a-load-bearing-effect-preregistered.md`.
**Context:** `docs/findings/2026-09-24-the-unpenalised-channel-carries-seventy-percent.md` §5, which names *"one
read-out, and it is the one chosen for the opposite reason"* as the first limitation — read-out 32 was picked
**because it maximises the chance of seeing the bias matter**, so a null there would have been weak evidence.

---

## 1. The result at three read-outs, and both registered predictions fail

| read-out | plastic | frozen-bias | **absolute** difference | σ | fraction removed | per-repeat sd plastic → frozen | relative sd plastic → frozen |
|---|---|---|---|---|---|---|---|
| **32** | 0.0750 | 0.0227 | **−0.0523** | 5.90 | **70%** | 0.0556 → 0.0207 | 74% → 91% |
| **128** | 0.0370 | 0.0039 | **−0.0331** | **6.40** | **89%** | 0.0325 → 0.0107 | 88% → **275%** |
| **1307** | 0.0357 | 0.0060 | **−0.0297** | **4.14** | **83%** | 0.0423 → 0.0097 | 119% → 162% |

**P1 was registered as an ordering of the *fraction* removed — 32 > 128 > 1307 — and it fails on all three
terms: the fractions are 89% (128), 83% (1307), 70% (32).** The **absolute** differences order exactly the other
way — **0.0523 > 0.0331 > 0.0297** — which is the ordering the load-bearing gap has (**+0.1000 at 32, +0.0167 at
128, −0.0111 at 1307**). **And P2 fails too**: it predicted that the effect would be *unresolved* at read-out 1307,
where the body is not load-bearing at all, and it is resolved at **4.14σ**, with **83%** of that read-out's (small)
forgetting in the same channel.

**So the registered question and the registered form disagreed, and the form was the one that was wrong.** The
comparators' levels differ by a factor of **2.0** (0.0750 against 0.0370) while the effects differ by **1.6×**, so
dividing by them reorders what it was meant to rank. **This is the third costume of the same error in one
session** — `e123`'s sd in nats divided by an sd in accuracy, rule 35's `ln 4` divided by a fraction of chance,
and now a fraction of a baseline whose size varies more than the effect. Rule 35 is extended below.

## 2. What the fire was actually asking, and it is answered in the direction that strengthens e125

`e125`'s concern was that its single read-out **maximised** the chance of seeing the effect, so the honest
possibility was that the effect was a read-out-32 artefact. **It is not.** At read-out 128 the same arm — `naive`
with 800 offsets held at their initialisation and **nothing else changed** — removes **89%** of the forgetting at
**6.40σ over forty paired seeds, 33 of 40 negative**, and **raises accuracy** (0.9313 → 0.9429). The residual is
**0.0039 ± 0.0017**, which is **2.3σ from zero**: at this read-out the forgetting is, to the resolution this design
has, **gone**.

**And the effect is large at both read-outs, in absolute terms, with 32 larger** — which is the ordering the
load-bearing gap would predict and the opposite of the *fraction's*. **So the effect tracks the gap in the unit
that is not normalised by a moving baseline**, and e125's limitation is discharged in the direction that makes
the finding stronger rather than weaker: this is not one configuration's accident.

## 3. The spread result replicates, and its direction is unit-dependent too — more starkly

At **both** read-outs the intervention cuts the **per-repeat sd**: **0.0556 → 0.0207 (2.69×)** at 32 and
**0.0325 → 0.0107 (3.04×)** at 128. And at both read-outs the **relative** sd moves the *other* way — **74% →
91%** at 32, and **88% → 275%** at read-out 128, where the mean has collapsed to 0.0039 and so what remains is
almost all noise.

**The 275% is the clearest instance of the problem in the paper.** A reader given only the relative sd would
conclude that freezing the bias makes the forgetting *three times less measurable*; a reader given only the
absolute sd would conclude it makes the benchmark *three times quieter*. Both are true, and they are different
statements: at read-out 128 the intervention has removed the signal and left the floor, which is a fact about the
benchmark's construction and not a measurement failure. **`e118`'s 74–134% handicap is quoted on the relative
scale, so the two must never be mixed**, and the script prints both columns for that reason.

## 4. The controls

**C0a passes at both read-outs** — every `bias_norms` entry exactly **0.0** across all forty replicates, with
`theta_drift` non-zero everywhere (minimum **0.0392** at read-out 128) — so the flag freezes the offsets and the
weights still move, at a second read-out and against a second comparator. **The comparators are other epochs'
artifacts**, admissible by the three per-replicate-identity precedents recorded in the registration rather than
by configuration identity, and this is the fifth and sixth instance of that check.

## 5. Rule 35 extended: an effect's size is a unit-dependent statement

**"A factor below chance" and "an effect removed 89% of a baseline" are the same kind of claim**, and both
require the number beside the thing it was divided from:

- **when the quantity is a ratio against a fixed reference** (`ln 4`, a chance level), quote the **fraction** and
  the factor together, because the factor alone can be divided twice;
- **when it is an effect against a varying baseline**, quote the **absolute** difference and the fraction
  together, because a baseline that moves by 2× between configurations will reorder the effects;
- **and when it is a spread**, quote the **absolute** sd and the relative one together, because an intervention
  that removes a signal collapses the mean faster than the sd and inverts the relative direction.

**The common form: a registered ordering must name its unit, and a results sentence should carry both numbers
wherever the normaliser varies across the configurations being compared.** In this benchmark the normalisers
vary by 2× across read-outs (the forgetting levels) and by ∞ within one (the residual at read-out 128), which is
why all three cases occurred here rather than elsewhere.

## 6. What this does not cover

- **The pre-registration's own question is answered in one unit and refused in the other.** Its *question* — does
  the effect track how much the body carries — is answered **yes** by the absolute differences (**32 > 128 >
  1307**, the gap's ordering) and **no** by the fractions (**128 > 1307 > 32**). **P1 and P2 both fail, and the
  registered form was the wrong one**, which is the third instance of that error this session and the reason rule
  35 was extended.
- **And the surprise is that the channel matters at *every* read-out**, including the whole state where the plastic
  weights are not load-bearing at all: 83% of read-out 1307's forgetting is in the offsets, at 4.14σ. So the
  prediction that a channel with nothing to carry would carry nothing is **wrong** — it carries most of what there
  is, and what there is is small.
- **Two read-outs and one comparator each**, both at test 48, both five-replicate-scale comparators for the
  paper's table but 40-replicate here — the pairing is on seeds and the epoch licence rests on §4's precedents.
- **The mechanism stays an inference.** Both read-outs show the body drifting *more* with the bias frozen
  (`e125` measured +10% at read-out 32) while forgetting less, which is the locality reading's signature; the
  locality itself is not measured.
- **And the effect's disappearance at read-out 128 does not make the benchmark harmless**: 0.0039 ± 0.0017 is
  2.3σ from zero, so *"the forgetting is gone"* is nearly resolved and is not resolved.
