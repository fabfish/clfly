# `e134` pre-registered: is the bias effect a **load-bearing** effect? The same arm at read-out 128 and 1307

**Date:** 2026-09-24
**Status:** pre-registered **before** the runs. Committed as its own commit; the runs are launched after it.
**Script:** `experiments/e8_rate_network.py` with `--frozen-bias`, unchanged.
**Planned artifacts:** `runs/e134_r128_frozenbias.json` and `runs/e134_r1307_frozenbias.json`, each
`--repeats 40 --iters 500 --test 48 --shared-head --input-overlap 0.0 --seed0 0 --circuit-size 800 --methods
naive --frozen-bias` at `--readout-size 128` and `--readout-size 1307`.
**Existing comparators, and no new plastic runs are needed:** `runs/e116_r128_40reps.json` (**+0.0370**, sd
0.0325) and `runs/e116_r1307_40reps.json` (**+0.0357**, sd 0.0423), both forty replicates at test 48 on the same
seed sequence.
**Context:** `docs/findings/2026-09-24-the-unpenalised-channel-carries-seventy-percent.md`, whose §5 names this
as its first limitation: *"**One read-out, and it is the one chosen for the opposite reason.** Read-out 32 is
where the body is most load-bearing, which maximises the chance of seeing the bias matter… It fired, so the
remaining question is generality."*

## The licence to compare against artifacts rather than re-running the plastic arm

Cross-epoch comparison is what rule 32 warns about, and here it rests on **three measurements rather than an
argument**: this session's `e8` additions are **record-only**, shown by per-replicate identity at
**read-out 32** (`e125`'s plastic arm against `e116_r32_40reps.json`, max |difference| 0.000e+00), at
**read-out 300** (`e123_r300_test480.json` against `e119_r300_test480.json`, max |difference| 0.000e+00, and the
two artifacts share **none** of the four new payload keys), and at **read-out 1307** (`e131`'s twelve seeds
against `e116_r1307_40reps.json`'s first twelve). **So a 40-replicate plastic comparator from an earlier epoch
is admissible at read-out 128 and 1307, and C0b below is not a formality but the fourth instance of the same
check.**

## The predictions

- **C0a, the flag's own control, at two more read-outs.** Each arm's `bias_norms` must be **exactly 0.0 at every
  task and every replicate** (both `step` and `from_zero`) **while `theta_drift` is non-zero at every task and
  replicate**. At read-out 32 the minimum drift with the bias frozen was **0.0507**; both of these arms should
  show the same qualitative structure, and the first half of the check alone would pass for a run that froze
  everything.
- **C0b.** A `naive` arm is *not* part of these runs, so the control is the one above plus the three precedents:
  if either artifact's `bias_norms` contain a single non-zero entry, the flag is not doing what its name says
  and the arm is void.
- **P1, and it is the fire.** The **fraction of the naive forgetting removed by freezing the bias** is
  **ordered 32 > 128 > 1307**. Read-out 32 removed **70%** at 5.90σ. The ordering is the one `e131` established
  for the barrier itself (**32 > 128 > 1307**) and the one the **load-bearing gap** has (+0.1000, +0.0167,
  −0.0111) — and it is **not** the per-repeat spread's (0.0556, 0.0325, 0.0423), whose middle term is
  read-out 1307. **So this is the same separation, applied to the intervention rather than to the geometry.**
- **P2.** At **read-out 1307** the effect is **not resolved**: the paired difference is below **2σ**. The body is
  not load-bearing there (the gap is **−0.0111** — freezing the whole body *helps*), and there is correspondingly
  little forgetting for a channel to carry.
- **Falsifier.** The ordering **inverts**: read-out 1307 loses **more** of its forgetting than read-out 128. Then
  the bias effect is not a load-bearing effect, and `e125`'s mechanism reading — *"a channel with no locality is
  the one that interferes most"* — needs a different account, because at the whole state the plastic weights are
  barely used and a global channel would have little to interfere with.

## Why the ordering and not a magnitude

`e125` measured one read-out and the registration that preceded it stated the direction in advance **so that a
null there would be weak evidence**. The mirror-image statement is what makes this fire's prediction sharp:
read-out 32 was chosen because it *maximises* the chance of seeing the effect, so a magnitude at 128 or 1307
would be a new claim fitted to new data, while **an ordering across three read-outs is a claim the axis already
licenses** — and one whose middle term (1307) is exactly where the confound of per-repeat spread would put it
second rather than last.

## What this cannot settle, in advance

- **Three read-outs is a line, not a curve**, and the three are at test 48 — the estimator's behaviour at test
  480 is a different question (`e123`).
- **The plastic comparators are 40-replicate artifacts from another epoch**, admissible by the three precedents
  in the licence paragraph and not by configuration identity. Any of the three could be wrong in a way that
  makes the fourth comparison wrong too, and it is the same check that licenses each.
- **`frozen-bias` freezes at exactly zero**, its own initialisation and not a tuned value, so an ordering of the
  *effect of removing a channel* is not an ordering of *how much the channel mattered*: a channel that is
  frozen at a value it never wanted cannot report what it would have done at its optimum.
- **And the mechanism stays an inference.** Even if the ordering holds, this measures that removing 800 offsets
  helps most where the body carries most; the locality reading of *why* is supported by the drift being higher
  with the bias frozen at read-out 32 and is not tested here.
