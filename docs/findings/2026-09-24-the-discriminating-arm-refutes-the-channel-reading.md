# The discriminating arm: read-out 700 refutes the channel reading and leaves the floor model untouched

**Date:** 2026-09-24
**Artifact:** `runs/e155_r700_naive_replay.json` — the read-out-700 arm, the one the registration named as the arm
that could separate the two readings. Comparator: `runs/e116_r700_40reps.json`.
**The registration** (`docs/findings/2026-09-24-the-floor-model-across-the-readout-axis-registered.md`) said, before
either arm ran: *"at 700 the share is unmeasured; if it is near 60% the channel reading predicts **−0.0133** against
the model's **−0.0221**, 0.0088 apart ≈ 2.2σ — so the 700 arm is the discriminating one"*.

---

## 1. The reading

| | forgetting | newest-task accuracy | mean accuracy |
|---|---|---|---|
| `naive` (`e155`, read-out 700) | **+0.0221** | 0.9396 | 0.9439 |
| **`replay`** | **+0.0008** | **0.9453** | **0.9622** |
| `naive` (`e116`, same read-out) | +0.0221 | 0.9396 | 0.9439 |

| control / claim | result |
|---|---|
| **C0 — this run's `naive` against `e116`'s** | **per-replicate identical, worst difference 0** — the **fourth** configuration this project has executed more than once, and the second in this run |
| **the margin: `replay − naive`** | **−0.0214 ± 0.0045 = 4.71σ** |
| **the floor model's −0.0221** | difference **+0.0008 = 0.12σ** — the model is untouched |
| the channel reading at a 60% share, −0.0133 | difference −0.0081 — **and the reading needs a different share to survive at all** |

## 2. Why this arm discriminates, and it is by *refuting* one reading rather than confirming the other

**The floor model's prediction is the baseline's forgetting, and the margin matches it to 0.0008.** But that
prediction is an identity — `margin = replay_own − baseline_own` — so the arm cannot "confirm" it; what it does is
**measure `replay_own` in a fifth configuration: +0.0008.**

**The channel reading is a substantive claim and the arm refutes it to the extent the share is known.** Solving the
measurement for the share it requires:

    share needed = margin / baseline = 0.0214 / 0.0221 = 97%

**So for *"the margin is proportional to the unpenalised channel's share"* to hold at read-out 700, the offsets
would have to carry 97% of that baseline's forgetting — against the shares measured at the neighbouring read-outs,
89% at read-out 128 and 83% at 1307** (`e134`). A 97% share between an 89% and an 83% neighbour is not what the
record's own read-out trend predicts, and the registration's own arithmetic is why this arm could see it: **at a
baseline forgetting of 0.0221, any share-based prediction is far from the whole number, while a whole-based one is
exact.**

## 3. And the pooled bound on `replay`'s own forgetting tightens to ±0.0062

| configuration | `replay`'s own forgetting |
|---|---|
| base family, read-out 32 | −0.0034 |
| shared-input family | +0.0083 |
| base family, channel frozen | +0.0018 |
| base family, read-out 128 | −0.0096 |
| **base family, read-out 700** | **+0.0008** |
| **pooled over the five distinct configurations** | **−0.0004 ± 0.0030** |

**0.14σ from zero, a 2σ bound of ±0.0059** (against ±0.0076 over the four), 95% interval
[−0.0062, +0.0054] — and the five values still span −0.0096 to +0.0083 with an across-configuration sd of **0.0066**,
so they remain consistent with one value. **And the identity holds in all five**: `1 − replay_own/baseline` reads
**1.045, 0.922, 0.921, 1.259, 0.964** against the measured ratios **1.045, 0.921, 0.916, 1.259, 0.968**.

## 4. What this cannot settle

- **Two read-outs, and the read-out axis is not a clean dose–response**: 128 and 700 differ from the base
  configuration in the read-out *and* therefore in the fit (support is the same, 80). The share's trend (89% → 83%)
  is from `e134`'s measurements at 128 and 1307, so the interpolation to 700 is the record's, not this arm's.
- **The floor model is an identity, so "it survived" is weaker evidence than it looks**: what is measured is
  `replay_own`, and its *bound* (±0.0062) is the claim. A configuration where replay's own forgetting were larger
  would break the arithmetic reading of the family differences, and none of the five has one.
- **The registration's own 2σ window for this arm was about ±0.008, and the observed gap between the two readings
  is 0.0088** — so the arm separates them by roughly one bar, and the refutation of the channel reading rests on the
  share's *plausible range* rather than on a direct measurement of it. A frozen-bias run at read-out 700 would
  measure the share and close that, and it does not exist.
- One circuit, three tasks, one seed stream, and the newest-task axis again shows nothing (replay +0.0057 at
  0.76σ).
