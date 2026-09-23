# `e117`: the draw is not detectable, and the plateau's one step survives four independent draws

**Date:** 2026-09-24
**Script:** `experiments/e8_rate_network.py`, three runs; artifacts `runs/e117_r128_draw{1,2,3}_20reps.json`
(20 replicates each), against `runs/e116_r128_40reps.json`.
**Artifacts:** the four above, plus the seven-point series of `e115`/`e116`.
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, `--seed0 0`, read-out 128 with `--readout-seed 1,2,3` × 20
replicates and `--readout-seed 0` × 40.
**Pre-registration:** `docs/findings/2026-09-24-the-draw-may-have-been-the-wrong-culprit-preregistered.md`,
committed before the runs.
**Context:** `docs/findings/2026-09-23-the-draw-is-as-large-as-the-effect.md`, which withdrew a design statement
because a four-draw span of 0.0125 equalled the across-size difference — and whose four draws were each
**five** replicates, so each mean carried an sem (≈0.010) *larger* than the 0.006 effect being looked for.

---

## 1. The result: the draw contributes nothing detectable, at two read-outs

| read-out 128, four independent draws | mean | its own sem | replicates |
|---|---|---|---|
| draw seed 0 | +0.0370 | 0.0051 | 40 |
| draw seed 1 | +0.0469 | 0.0096 | 20 |
| draw seed 2 | +0.0411 | 0.0082 | 20 |
| draw seed 3 | +0.0349 | 0.0080 | 20 |

**Observed scatter: sd 0.0053. Expected from replicate noise alone: sd 0.0079. Ratio 0.67.** P1 holds and the
falsifier does not fire: **the four draws scatter *less* than replicate noise by itself produces**, so the draw
variance component estimates to zero at read-out 128.

**And the same measurement at read-out 300 gives 0.61** — the four five-replicate draws of `e113`, whose observed
scatter (0.0060) is below their own replicate-noise expectation (0.0097). **Two read-outs, two independent
estimates, both below 1**: the draw is not detectable at either place it has been looked for.

**So `e113`'s "draw span of 0.0125" was four underpowered means rather than four draws.** Its withdrawal of the
design statement was still **right at the time and for a reason it did not give** — the five-replicate *means* it
rested on were shown by `e115` and `e116` to be unreliable in both directions — while the **draw itself was never
shown to matter**, and this fire shows it does not at the size the earlier data suggested (≥ 0.0079).

## 2. And the plateau's one resolved step survives the control

The axis's shape, from `e116`, is a flat plateau from 900 to 300 with the narrow end above it. **Every one of the
four independent draws of read-out 128 lands above the plateau**, each compared against the 300 point measured
at 40 replicates:

| draw | mean | against the plateau's 300 (+0.0232) | σ |
|---|---|---|---|
| seed 0 | +0.0370 | +0.0138 | **2.1** |
| seed 1 | +0.0469 | +0.0237 | **2.3** |
| seed 2 | +0.0411 | +0.0179 | **2.0** |
| seed 3 | +0.0349 | +0.0117 | 1.3 |

**Three of the four draws resolve above the plateau on their own, the fourth is in the same direction, and the
scatter among the four is smaller than replicate noise.** That is a stronger statement than the single-draw
version in `e116`, because it is the same step measured four times with the draw varied — **so the elevation of
read-out 128 is a property of the read-out *size* rather than of which 128 neurons were drawn.**

**Which restores the axis as a size axis, and the restoration is narrower than what was withdrawn.** What
`e113` withdrew was *"read-out ≈ 300 is the optimum on both metrics"*; `e115` and `e116` then showed that claim
was a five-replicate artifact and replaced it with a plateau whose narrow end rises. **What this fire restores is
the *interpretation*, not the claim**: the plateau's elevations are not draw artifacts, so the axis can be read
as a statement about the read-out size — *narrowing below 300 raises three-task naive forgetting, mildly at 128
and sharply at 32, with 900 to 300 forming one plateau.* **That is the third revision of one sentence in four
fires** (optimum at 300 → flat trough → plateau), and it is the first one whose *confound* has been measured
rather than assumed.

## 3. What this does not settle

- **A draw sd below 0.0079 is not excluded.** The test's power is set by the four draws' own sems, so the honest
  null is *"no draw effect at or above the size the earlier data suggested"*; an effect of 0.003 would pass
  unnoticed. Drawing that line precisely would need more draws, not more replicates.
- **It is measured at two read-outs**, 128 and 300, and not at 32 — the axis's largest step (0.0380 at 3.73σ) is
  the one *least* likely to be a draw effect of either measured size, but that is an argument rather than a
  measurement.
- **Forty replicates at one read-out and twenty at three** means the draw means have unequal sems, so the ratio
  test is an approximation rather than a one-way analysis; the direction of the result (0.67 against a boundary
  of 1.0, with the falsifier at 1.6) does not depend on the weighting.
- **It does not touch the mechanism question**, which stands where five fires left it: every mechanical quantity
  measured is monotone in the read-out while both reported metrics are not.
