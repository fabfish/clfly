# The third draw reverses my own last two findings: R1 is MET on 2 of 3 draws, and draw 1 is the outlier — on some quantities

**Date:** 2026-09-25
**`e197`'s midpoint landed at 19:40 and it decides R1, and E2, again — the other way.** Two findings today were
written on this quantity; the third draw contradicts the second. The sequence is the finding as much as the number is.

---

## 1. R1 at three draws

`learned (older)`, the two axis points, each draw measured within itself:

| draw | overlap 0.0 | midpoint (achieved 0.3333) | deficit | **R1's verdict** |
|---|---|---|---|---|
| **draw 0** | 0.96042 | 0.92786 | **−0.03255 ± 0.00402 = 8.10σ** | **MET** |
| **draw 1** | 0.94557 | 0.94974 | **+0.00417 ± 0.00361 = 1.15σ** | **FALSIFIER FIRED** |
| **draw 2** | 0.96406 | 0.93932 | **−0.02474 ± 0.00305 = 8.12σ** | **MET** |

**So the interior fitting deficit is present on two draws out of three, at 8.10σ and 8.12σ — nearly the same
magnitude — and absent on the third.** My finding at 18:45 said it "did NOT replicate … it is a property of draw 0's
80-neuron supports and not of the overlap", on the strength of draw 1 alone. That is now wrong in its conclusion and
right in its evidence: draw 0's deficit is not what draw 1 shows, and draw 2 shows it again.

**The mechanism of the cancellation is visible in the two points.** Draw 1's overlap-0.0 value is the **lowest** of
the three (0.94557 against 0.96042 and 0.96406) *and* its midpoint value is the **highest** (0.94974 against 0.92786
and 0.93932). A deficit is a difference of two points, so it vanishes when they move oppositely — which is what the
draw does here, and it is why the draw's effect on the *deficit* (+0.02187 at the interior, −0.01484 at overlap 0.0,
from `docs/findings/2026-09-25-the-interior-fitting-deficit-did-not-replicate.md` §2) has opposite signs at the two
ends of the difference.

## 2. And draw 1 is the outlier on the *other* quantities, not on this one

The three draws, midpoint against each draw's own baseline:

| quantity at achieved 0.3333 | draw 0 | draw 1 | draw 2 | resolved in |
|---|---|---|---|---|
| forgetting | +0.00833 (0.79σ) | +0.03255 (3.53σ) | +0.01172 (1.03σ) | **1 of 3** |
| accuracy | −0.03281 (4.45σ) | −0.00417 (0.64σ) | −0.02639 (3.28σ) | 2 of 3 |
| **`learned (older)`** | **−0.03255 (8.10σ)** | +0.00417 (1.15σ) | **−0.02474 (8.12σ)** | **2 of 3** |
| newest task | −0.01667 (2.25σ) | +0.04427 (8.73σ) | −0.00625 (1.07σ) | 1 of 3 |
| adjacent-pair interference | +0.02463 (1.58σ) | +0.09064 (4.70σ) | +0.02437 (1.12σ) | **1 of 3** |
| distant-pair interference | +0.07239 (3.31σ) | +0.12257 (5.42σ) | +0.02530 (1.12σ) | 2 of 3 |

**The signs agree everywhere; what moves between draws is which quantities resolve.** And draw 1 is the one that
resolves the retention and interference quantities — forgetting, the newest task, the adjacent pair — while being the
one that *fails* to resolve the learning and accuracy costs. Draw 0 and draw 2 are the mirror image. So "draw 1 is an
outlier" is true of the learning quantities and false of the interference ones, and the manipulation's **signature** —
which quantities it moves — is itself draw-dependent.

**E2 is falsified**: it asked for the distant-pair term's midpoint rise to be resolved on draw 2, and draw 2 measures
+0.02530 ± 0.02263 = **1.12σ**. The claim survives as 2 of 3 (draw 0 at 3.31σ and draw 1 at 5.42σ), which is weaker
than the registration's "3 of 3" framing.

## 3. What the sequence is evidence for

**Three draws moved this project's reading of one quantity twice, in opposite directions, within two hours.** At 18:45
the deficit was draw-0's; at 19:34 draw 1 was the outlier and the draw's effect had no stable magnitude; at 19:51 the
deficit is back at 8.12σ on a third draw and draw 1 is an outlier on the learning quantities. **Each of those
statements was the correct reading of the draws available at the time**, and the sequence is exactly what rule 10's
"one draw is one sample, average many" is for — a rule this project has had since its first week and which today's
axis work was written against repeatedly.

**What is now supportable, and at what strength:**

- the interior fitting deficit is real and large, **2 of 3 draws, 8.10σ and 8.12σ**, and one draw cancels it;
- the midpoint's accuracy cost is **2 of 3**, 4.45σ and 3.28σ;
- the distant-pair term's midpoint rise is **2 of 3**, 3.31σ and 5.42σ;
- the endpoint's forgetting (2.99σ and 3.30σ on draws 0 and 1) is pending draw 2's endpoint, as is R2, R3a and R3b;
- **nothing here is 3 of 3 yet.**

## 4. What this does not license

- **That the deficit is "confirmed".** Two of three is a majority, not a replication across the sample: one draw
  removes it entirely, and the three draws' values (−0.03255, +0.00417, −0.02474) span 0.0367.
- **That draw 1 is broken.** It is a legitimate draw of the supports; its numbers are what they are, and which draw is
  atypical is not a question three draws settle.
- **Quoting 8.10σ as the effect's size.** Three draws give a centre near −0.0200 with a spread of the same order; the
  honest form is the three values.
- **That the two *earlier* corrections were avoidable.** They were correct readings of one and two draws; what was
  avoidable was writing a conclusion at n = 1 and again at n = 2. **The remedy is the design, not the prose**: this
  family needs its five levels at three or more draws before any of its shape claims is quotable.

---

**AMENDMENT, 19:59, when draw 2's endpoint landed: R3a is 3 of 3 and R2 is 1 of 3.** §2's tally was missing the endpoint. Read now: the endpoint's forgetting rises on all three draws (+0.03177 = 2.99σ, +0.03516 = 3.30σ, +0.02161 = 2.70σ), which makes it the **only** claim on the axis that survives three draws — and the one the corpus already had as nine of nine — while R2's separation is **1 of 3**, failing on draw 2 with a **negative** gap of −11.32 points. `docs/findings/2026-09-25-three-draws-four-claims-exactly-one-is-3-of-3.md`
