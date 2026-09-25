# The interior fitting deficit did NOT replicate: R1's falsifier fired, and the draw's own effect reverses sign across the axis

**Date:** 2026-09-25
**The replication's midpoint landed at 18:45 and the first two of its claims are decided.** `e195`'s overlap-0.0
baseline (18:27) and its midpoint (18:45) carry the whole of R1 and D1, read against **their own draw's** baseline.
Both come out against today's headline, and the second one comes out against both readings that were registered
against it. `R2` and `R3a`/`R3b` need the overlap-1.0 anchor, which is still running.

---

## 1. R1's falsifier fired: the deficit is not there on a second draw

**R1** was registered as: at achieved 0.3333 on draw 1, `naive`'s `learned (older)` against that draw's own
overlap-0.0 baseline is **at or below −0.0200**; falsifier **above −0.0100**, which "would make that 8.10σ a one-draw
result".

| | draw-0 deficit (the day's headline) | **draw-1 deficit** |
|---|---|---|
| `learned (older)`, achieved 0.3333 − 0.0 | **−0.03255 ± 0.00402 = 8.10σ** | **+0.00417 ± 0.00361 = 1.15σ** |

**The falsifier fired.** On a second support draw the older tasks are learned *slightly better* at the midpoint than
at overlap 0.0, at 1.15σ, and the 8.10σ interior deficit is **a property of draw 0's 80-neuron supports and not of
the overlap**. Three findings today rest on that deficit and each is now marked in place:
`docs/findings/2026-09-25-the-midpoints-cost-is-a-learning-deficit-not-forgetting.md`,
`docs/findings/2026-09-25-the-fitting-deficit-is-the-same-in-all-three-arms.md` (whose arm-independence result is
draw-0 throughout) and the axis summary's §3.

## 2. D1 failed, and the shape it was testing is bigger than the thing it was about

**D1** predicted that the draw's effect on `learned (older)` **shrinks toward zero** as the overlap rises, so that
δ(0.3333) ≈ 0 and the draw-1 deficit would land at −0.0177 — inside R1's own null. The competing reading was that δ is
**constant**, leaving the deficit unchanged at −0.0326. Measured:

| | δ = draw 1 − draw 0 on `learned (older)` |
|---|---|
| at overlap 0.0 | **−0.01484 ± 0.00444 = 3.34σ** |
| **at achieved 0.3333** | **+0.02187 ± 0.00497 = 4.40σ** |

**Both readings are wrong, and the truth is the clause the registration filed as its falsifier**: the draw's effect
**reverses sign** across the axis. The arithmetic closes exactly, which is what makes it a measurement rather than a
coincidence:

```
draw-0 deficit + δ(0.3333) − δ(0.0) = −0.03255 + 0.02187 + 0.01484 = +0.00416
measured draw-1 deficit                                             = +0.00417
```

So the draw effect on this quantity is **±0.015–0.022 depending on the overlap** — *larger*, at both ends, than the
±0.005 sem of the deficit it was supposed to explain.

## 3. The whole midpoint, both draws, against each draw's own baseline

`naive`, 40 seeds, every quantity measured within its own draw so that no quantity is compared across draws:

| quantity at achieved 0.3333 | draw 0 | draw 1 |
|---|---|---|
| forgetting | +0.00833 ± 0.01060 (0.79σ) | **+0.03255 ± 0.00922 (3.53σ)** |
| accuracy | **−0.03281 ± 0.00737 (4.45σ)** | −0.00417 ± 0.00653 (0.64σ) |
| **`learned (older)`** | **−0.03255 ± 0.00402 (8.10σ)** | **+0.00417 ± 0.00361 (1.15σ)** |
| newest task | −0.01667 ± 0.00739 (2.25σ) | **+0.04427 ± 0.00507 (8.73σ)** |
| adjacent-pair interference | +0.02463 ± 0.01555 (1.58σ) | **+0.09064 ± 0.01928 (4.70σ)** |
| distant-pair interference | **+0.07239 ± 0.02190 (3.31σ)** | **+0.12257 ± 0.02263 (5.42σ)** |

**And the draw's own effect at the midpoint**, paired across the two draws:

| Δ(0.3333) = draw 1 − draw 0 | value | σ |
|---|---|---|
| `learned (older)` | +0.02187 ± 0.00497 | **4.40σ** |
| newest task | +0.03750 ± 0.00569 | **6.59σ** |
| adjacent-pair interference | +0.08036 ± 0.01623 | **4.95σ** |
| accuracy | +0.01858 ± 0.00861 | 2.16σ |
| forgetting | +0.01276 ± 0.01154 | 1.11σ |
| distant-pair interference | +0.02124 ± 0.02714 | 0.78σ |

**The learning quantities and the adjacent-pair term move at 4.4–6.6σ between two draws, on identical configurations
and identical 40 seeds.** That is the same structure the overlap-0.0 point showed — the draw acts on learning — but at
the midpoint it also reaches the adjacent-pair interference term, which at overlap 0.0 it did not (1.38σ).

## 4. What survives, stated as the only things that do

**Signs mostly agree; magnitudes and resolutions do not.** Every quantity except one keeps its direction across the
two draws: the interference terms rise, forgetting rises, accuracy falls. What changes is *whether anything is
resolved* and *by how much*:

| survives both draws | draw 0 | draw 1 |
|---|---|---|
| **the distant-pair interference rises with the overlap** | +0.07239 (3.31σ) | +0.12257 (5.42σ) |
| the adjacent-pair term rises with it | +0.02463 (1.58σ) | +0.09064 (4.70σ) |
| forgetting rises with it | +0.00833 (0.79σ) | +0.03255 (3.53σ) |
| accuracy falls with it | −0.03281 (4.45σ) | −0.00417 (0.64σ) |

**Only the interference account's rise is resolved on both draws**, and only for the distant term. That is also the
one claim this project had *before* today from other artifacts — "raising the input overlap raises the network's own
interference terms, nine of nine comparisons" — so the replication agrees with the corpus's older, wider evidence and
disagrees with today's narrower headline.

**The two claims that were the day's headline are the two that fail**: the 8.10σ fitting deficit (sign reversal) and
the 4.45σ accuracy cost (4.45σ → 0.64σ). Both were measured on draw 0 and both were reported as properties of the
axis.

## 5. What this does not license

- **That the overlap axis has no effect.** It has one, on the interference account, resolved on both draws and
  agreeing with nine-of-nine evidence from other artifacts.
- **That the other draw is "the" draw.** Two draws give a difference, not a distribution; δ could itself be a
  two-sample accident, and the sign reversal is one pair. Rule 10's answer remains many draws averaged.
- **That draw 0 was wrong.** Draw 0's numbers are what they are; what is refuted is their reading as properties of the
  overlap rather than of the supports.
- **Reading §3's draw effects into R2 and R3.** The adjacent-pair draw effect is 4.95σ at the midpoint, so **R2's
  40-point separation claim is now the one most at risk** — it is stated at that same achieved overlap and its
  numerator contains exactly the term that moves. R2 and R3 are read when the anchor lands, and neither should be
  called before it does.
- **Any mechanism.** A sign-reversing draw effect on a learning quantity says which neurons were drawn matters
  differently at different overlaps, and nothing here says why.
