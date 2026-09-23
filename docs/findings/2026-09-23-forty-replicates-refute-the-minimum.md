# `e115`: forty replicates refute the interior minimum, and the noise estimate was the reason

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py`, two runs; artifacts `runs/e115_r300_40reps.json`,
`runs/e115_r512_40reps.json` (40 replicates each at read-out 300 and 512).
**Artifacts:** the two above, plus the seven-point series of `e109`–`e113`.
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, `--seed0 0`, `--repeats 40`.
**Pre-registration:** `docs/findings/2026-09-23-forty-replicates-on-one-step-preregistered.md`, committed before
the runs.
**Context:** `docs/findings/2026-09-23-the-axis-reduces-to-one-statement.md`, whose cost table priced this step at
22 replicates per side, and whose only surviving claim was read-out 32's excess.

---

## 1. The control passes, so the runs can answer the question

The training seed is `seed0 + 100·r`, so the first five replicates of a forty-replicate run use exactly the seeds
of the stored five-replicate runs — and at **both** read-outs the first five replicates are **bit-identical** to
the stored ones. **So the runs are extensions rather than separate samples**, which is the check that
`e61`/`e68` failed after the fact and that this fire made in advance. Without it the thirty-five extra replicates
would add no power and the result below would be uninterpretable.

## 2. P1 fails, and the failure is in the five-replicate means

| read-out | **40 replicates** | 5 replicates |
|---|---|---|
| **512** | **+0.0250** ± 0.0048, per-repeat sd 0.0305 | +0.0208 ± 0.0081, sd 0.0180 |
| **300** | **+0.0232** ± 0.0040, per-repeat sd 0.0252 | +0.0083 ± 0.0101, sd 0.0226 |

**The 512 → 300 difference is +0.0018 at 0.29σ.** P1 fails, and the reason is visible in the means rather than
in the arithmetic: **read-out 300's mean moved from +0.0083 to +0.0232** — a change of **+0.0149**, *larger than
the entire step the withdrawn design statement rested on* (0.0125). With forty replicates the two lowest points
on the axis are **statistically indistinguishable**, and neither differs from read-out 900 (300 vs 900 is 0.61σ,
512 vs 900 is 0.41σ).

**So the interior minimum is not a minimum — it is a flat trough**, and even its edges are inside the noise.
**This is the third consecutive fire to retract a shape claim on this axis, and the first to do it by adding
replicates rather than points**: five points gave a bowl, two more broke it, the draw control showed the scale
was wrong, and more replicates now show the floor is flat.

**And it falsifies a second claim from the same measurement.** The previous fire recorded that read-out 300's
forgetting was **"the lowest plastic `naive` value in this whole corpus"** — true of the five-replicate value
(0.0083, against 68 such arms, next lowest the 2-class configuration's 0.0167) and **false of the forty-replicate
value**: the same configuration sits at **+0.0232**, above it. A corpus record built on five-replicate minima has
five-replicate resolution, and the record now says so.

## 3. P2 held by its letter and failed by its purpose, and that is the durable part

The forty-replicate sds are **1.69×** (512) and **1.12×** (300) the five-replicate estimates — inside the
factor-of-two tolerance, so P2 passes. **But a factor-of-two tolerance on an sd is a factor-of-*four* tolerance
on a replicate count**, since `n ∝ sd²`, and the observed ratios moved the cost table's counts by **2.9× and
1.2×**: the step priced at 22 replicates per side was really a ~63-replicate step.

**So the cost table's method was right and its inputs were too thin**, which is the sequence's own lesson applied
to the estimation of its own noise: an sd from five points is not an sd. The registered tolerance was written to
catch a bad estimate and it was too loose to catch this one, which is worth recording as a rule rather than as an
excuse — **when a cost is computed from an sd, the sd needs the same evidence standard as the effect.**

## 4. What the axis is, now that its two lowest points have forty replicates each

| read-out | forgetting | replicates |
|---|---|---|
| 1307 (whole) | +0.0479 | 5 |
| 900 | +0.0292 | 5 |
| 700 | +0.0354 | 5 |
| **512** | **+0.0250** | **40** |
| **300** | **+0.0232** | **40** |
| 128 | +0.0333 | 5 |
| **32** | **+0.0729** | 5 |

**Read-out 32's excess is untouched and remains the axis's only resolved claim** — against the 40-replicate 300
it is +0.0497 at **3.2σ**, and against 900, 512 and 128 it was already 2.0–3.6σ. Everything between 128 and 900
is a flat region whose internal structure does not resolve.

**And the axis is now measured with unequal precision, which changes what its neighbouring comparisons can
say.** The 300 and 512 points carry forty replicates and the other five carry five, so every comparison
involving one of them is now dominated by the *other* side's noise — 900's sem is 0.0090 against 300's 0.0040.
**Finishing the axis means forty replicates at the other five points**, which the same arithmetic prices at
**5 × ~15 min ≈ 75 minutes**, and that is the concrete next step rather than any further point.

## 5. What this cannot settle

- **The draw is still one draw per read-out**, so read-out 300's forty replicates are forty *samples of the
  training noise at one draw*; the draw span (0.0125 at that size) is not averaged over, and a difference that
  resolved here would still be a statement about this draw.
- **Forty replicates is not a variance.** The sds it gives (0.0305, 0.0252) are themselves estimated from forty
  points and would move again; the point is that they moved *up* from the five-replicate values by more than the
  registered tolerance allowed for a count, not that they are final.
- **It does not re-open the mechanism question**, which the previous fires narrowed to its coarse form: every
  mechanical quantity is monotone in the read-out while both reported metrics are not, and the fine structure
  that claim was about is now known not to be there.
