# The replication's verdict: R2's falsifier fired too, R3a MET, and only TWO of the axis's claims survive a second draw

**Date:** 2026-09-25
**The draw-1 family completed at 19:03:43 and all four replication claims are read** (`e194 --claims replication`,
exit 0), against **its own draw's** baseline and anchor as the admission rule requires — `support_seed` is not an
inert field, so a draw-1 level cannot be paired with a draw-0 endpoint at all. R1 and D1 were read at 18:45 and
reported in `docs/findings/2026-09-25-the-interior-fitting-deficit-did-not-replicate.md`; this is the whole set.

---

## 1. The four verdicts

| | claim | draw 0 | **draw 1** | verdict |
|---|---|---|---|---|
| **R1** | the interior fitting deficit, `learned (older)` at achieved 0.3333 | −0.03255 (8.10σ) | **+0.00417 (1.15σ)** | **FALSIFIER FIRED** |
| **R2** | the two terms' separation there, points | 62.13 | **10.52** | **FALSIFIER FIRED** |
| **R3a** | the endpoint's forgetting | +0.03177 (2.99σ) | **+0.03516 (3.30σ)** | **MET** |
| **R3b** | the endpoint's `learned (older)` within ±0.0100 | +0.00104 (0.33σ) | **+0.01328 (4.49σ)** | **between the bar and the falsifier** |

**R2's falsifier firing is the sharper of the two.** The claim was that the separated shapes the midpoint showed —
20.0% against 82.1% of their own 0 → 1 changes — survive a second draw. On draw 1 they read **56.4% and 66.9%**: the
gap is 10.5 points, below the 15-point falsifier, so **the "two terms with opposite shapes" result was draw 0's
arrangement of the supports and not the overlap axis's**. The registered **P1** of the original pre-`e193`
registration goes the other way on the same artifact — its bar is +0.0617 and draw 1 measures **+0.09064 (4.70σ)**, so
**P1 is MET on draw 1 and NOT met on draw 0**. The corpus's oldest axis claim is draw-dependent in the same way as
its newest ones.

## 2. The complete two-draw axis

Every quantity within its own draw, each against that draw's own overlap-0.0 baseline:

| at achieved 0.3333 | draw 0 | draw 1 |
|---|---|---|
| forgetting | +0.00833 (0.79σ) | **+0.03255 (3.53σ)** |
| accuracy | **−0.03281 (4.45σ)** | −0.00417 (0.64σ) |
| `learned (older)` | **−0.03255 (8.10σ)** | +0.00417 (1.15σ) |
| newest task | −0.01667 (2.25σ) | **+0.04427 (8.73σ)** |
| adjacent-pair interference | +0.02463 (1.58σ) | **+0.09064 (4.70σ)** |
| distant-pair interference | **+0.07239 (3.31σ)** | **+0.12257 (5.42σ)** |
| **that draw's own 0 → 1 rises** | near +0.12337, far +0.08818 | near **+0.16084**, far **+0.18329** |

| at overlap 1.0 | draw 0 | draw 1 |
|---|---|---|
| **forgetting** | **+0.03177 (2.99σ)** | **+0.03516 (3.30σ)** |
| accuracy | −0.01858 (2.69σ) | −0.00503 (0.64σ) |
| `learned (older)` | +0.00104 (0.33σ) | **+0.01328 (4.49σ)** |
| newest task | +0.00573 (1.10σ) | **+0.02865 (5.29σ)** |
| adjacent-pair interference | +0.12337 (7.82σ) | +0.16084 (7.79σ) |
| distant-pair interference | +0.08818 (3.12σ) | +0.18329 (6.91σ) |

**The 0 → 1 rises themselves move by 30% (near) and 108% (far) between draws.** So the *normalisation* is
draw-dependent too: a progress fraction can move because its numerator moved, or because its denominator did, and
draw 1's near term moved for both reasons at once (numerator 3.7×, denominator 1.30×).

## 3. What survives a second draw, stated exhaustively

**Two things, and both were in the corpus before today:**

1. **The endpoint's forgetting rises with the input overlap: +0.03177 (2.99σ) and +0.03516 (3.30σ).** This is the
   claim the project registered as "nine of nine matched comparisons", and it is the only *cost* claim that survives
   — R3a's MET.
2. **The distant-pair interference rises at the midpoint: +0.07239 (3.31σ) and +0.12257 (5.42σ)**, and it is the one
   term resolved on both draws at both ends. Its partner, the adjacent-pair term, rises on both too but resolves on
   only one (+0.02463 = 1.58σ, +0.09064 = 4.70σ).

**Everything else on the axis is draw-conditional:**
the interior fitting deficit (sign), the midpoint's accuracy cost (4.45σ → 0.64σ), the endpoint's accuracy cost
(2.69σ → 0.64σ), the midpoint's forgetting (0.79σ → 3.53σ), the newest task at both ends (−0.01667 → +0.04427, and
+0.00573 → +0.02865), the two terms' separation (62.1 → 10.5 points), the registered P1, and the 0 → 1 rises that
every fraction is normalised by.

## 4. What this says about the design, and what was done about it

**The two draws differ by more than the effects on almost every quantity measured.** Six of today's findings were
written on draw 0 alone and read as properties of the overlap axis; four of them now carry dated correction blocks and
the plan's `e193` row carries one on its headline clause. The two that stand are the ones with pre-existing
nine-of-nine evidence behind them, which is the pattern one would expect and is the reason the project's rule 10
(the control is a population, one draw is one sample) exists in the first place.

**Registered and launched on the strength of it: a THIRD draw.** `e196`, which was running, refined *draw 0's* shape
with two more interior levels — a design whose value collapsed the moment R2's falsifier fired, since what it would
locate is an arrangement of draw 0's supports. It was stopped after 1 of 40 replicates of its first level, before any
artifact was written, and replaced by **`e197`: support draw 2 at the same three targets (0.0 / 0.5 / 1.0),
`--methods naive --repeats 40`**, the same 3 × 13–18 min. Three draws cannot give a between-draw sd worth quoting
(2 df), but they give the *span* of every claim that has replicated so far, which is what the next decision needs:

- **E1** — the endpoint's forgetting is resolved (≥2σ) on draw 2 as well, making it 3 of 3.
- **E2** — the distant-pair term's midpoint rise is resolved on draw 2 as well.
- **E3** — the span of the endpoint's forgetting across the three draws is **below 0.0200** (draw 0 +0.03177, draw 1
  +0.03516 span 0.0034 so far). Falsifier: above 0.0300, which would say even the surviving claim needs
  averaging rather than quoting.

## 5. What this does not license

- **That the axis has no overlap effect.** Two quantities survive, and one of them is the project's oldest and
  widest-supported claim.
- **That draw 0 was anomalous and draw 1 correct.** Two draws give a difference; which is "typical" needs the third.
- **A between-draw standard deviation from two draws.** δ's sign reversal is itself one pair of draws.
- **Reading either draw's numbers as the axis's.** Both are single samples of the supports, and the honest form of
  every draw-0 or draw-1 number on this axis is *"on this draw"*.
- **Rehabilitating the stopped design.** The two extra interior levels remain registered
  (`docs/findings/2026-09-25-registered-two-more-interior-levels.md`) with their claims unread, and they should be run
  only if a draw-averaged version of the axis is wanted — the shape of one draw is not worth locating.
