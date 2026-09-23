# `e117`, pre-registered: the draw may have been the wrong culprit, and here is the test at the right power

**Date:** 2026-09-24
**Script:** `experiments/e8_rate_network.py`, three runs; artifacts `runs/e117_r128_draw{1,2,3}_20reps.json`
(in flight).
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, `--seed0 0`, **read-out 128 with `--readout-seed 1, 2, 3` and
`--repeats 20` each**, against the existing `--readout-seed 0` run at forty replicates.
**Context:** `docs/findings/2026-09-23-the-draw-is-as-large-as-the-effect.md`, which **withdrew a design
statement** on the grounds that the draw-to-draw span at one size (0.0125) **equalled** the across-size
difference the statement rested on, and `docs/findings/2026-09-24-the-axis-is-a-plateau.md`, which then replaced
that statement with the evenly measured plateau shape.

---

## 1. The arithmetic that sent this fire, and it is a problem with the **earlier** conclusion

`e113` measured four draws at read-out 300, **five replicates each**, and reported their span as 0.0125. But each
of those four means carries its own sem, and the scatter of four such means has a **known expectation if the draw
does nothing at all**:

| draw | mean | its own sem |
|---|---|---|
| seed 0 | +0.0083 | 0.0101 |
| seed 1 | +0.0146 | 0.0078 |
| seed 2 | +0.0208 | 0.0099 |
| seed 3 | +0.0208 | 0.0109 |

**Observed scatter: sd 0.0060. Expected from replicate noise alone: sd 0.0097.** So the four draws scatter
**0.61×** as much as replicate noise by itself produces — **the data are consistent with the draw contributing
*nothing*, and the "span of 0.0125" was four noisy means rather than four draws.**

**That does not make the e116 plateau wrong** — it was measured at forty replicates per read-out — but it does
mean **the draw was named as a confound on the strength of an estimate that cannot detect one.** Four draws at
five replicates give each mean an sem of ~0.010, which is *larger* than the 0.006 draw effect being looked for;
a design cannot measure a variance smaller than its own noise.

## 2. The design, and the power it actually has

**Twenty replicates per draw, three new draws, at read-out 128** — the read-out whose elevation above the plateau
is the axis's one resolved step (0.0138 at 2.12σ). The within-draw sd at 128 is 0.0325, so twenty replicates give
a **per-draw sem of 0.0073**, which is the same order as the candidate draw sd (0.006 measured, unsatisfactorily,
at read-out 300). With four draws (three new plus the stored seed-0 run) the test is a one-way comparison of
between-draw scatter against within-draw scatter, and it is powered for a draw sd **at or above** 0.0073 — the
smallest the earlier data suggested.

**Why 128 and not 300.** 128 is where the axis's surviving claim lives, so a draw effect there is the one that
matters; and 128's within-draw sd (0.0325) is close to 300's (0.0252), so the power is comparable.

## 3. The predictions, and the falsifier, written before the runs finish

| | prediction |
|---|---|
| **P1** | the four draw means' scatter at read-out 128 is **within the replicate-noise expectation** — the ratio of observed to expected sd is **≤ 1.0** |
| **P2, the correction it implies** | if P1 holds, **`e113`'s "draw span 0.0125" is replicate noise**, the draw is **not a demonstrated confound on this axis**, and the plateau shape of `e116` stands as a statement about the read-out **size** rather than about which neurons were drawn |
| **Falsifier** | the ratio **exceeds 1.0 beyond the sampling error of a four-draw estimate** — for three degrees of freedom that is roughly **> 1.6** — in which case the draw is a real variance component, `e113`'s withdrawal was right for the reason it gave, and the axis's steps need it treated as a systematic offset (which pairing cannot see, as `e114` showed) |

**A null result is the outcome that changes something**, which is the reverse of the usual arrangement: it would
**restore** a claim that was withdrawn one fire ago — in its weaker, correctly measured `e116` form — and it would
do so by showing that the reason for the withdrawal was a misread of four underpowered means. **The withdrawal
itself was still right at the time**, because the *five-replicate* means it was based on were shown by `e115` and
`e116` to be unreliable in both directions; what this fire tests is whether the *draw* was ever the culprit.

## 4. What this cannot settle

- **One read-out.** It tests the draw at 128; a draw effect could exist at 300 or at 32 and not here, and the
  earlier evidence for one is at 300 — where these twenty-replicate draws are **not** run, deliberately, because
  the axis's claim is at 128. If P1 holds here and someone wants the draw excluded at every point, that is four
  more fires of the same size.
- **Four draws is four draws.** The test has three degrees of freedom on the between-draw side and cannot resolve
  a draw sd below 0.0073; a real effect of 0.003 would pass it unnoticed, and the honest statement of a null is
  *"no draw effect at or above the size the earlier data suggested"* rather than *"no draw effect"*.
- **It does not re-open the mechanism question**, which stands where five fires left it.
