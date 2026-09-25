# The third draw refutes the two-draw conclusion: one draw was an outlier, and what the draw moves is not stable either

**Date:** 2026-09-25
**A cheap unit on the first artifact of `e197`, available before its family finishes.** `e197`'s overlap-0.0 run
landed at 19:22 and gives the same configuration at a **third** support draw. Three draws is 2 df and no good for a
standard deviation, but it is enough to test the conclusion published an hour ago on two — and that conclusion does
not hold.

---

## 1. The measurement

Overlap 0.0, `naive`, 40 seeds, the same circuit and the **same read-out draw** in all three (`subset_sha1
33bcd7fa68a2`), so the only thing varying is the support draw:

| quantity | draw 0 | draw 1 | draw 2 | span | σ(draw1−draw0) | σ(draw2−draw0) | σ(draw2−draw1) |
|---|---|---|---|---|---|---|---|
| forgetting | 0.07500 | 0.06354 | 0.08229 | 0.01875 | 1.03 | 0.65 | 1.92 |
| accuracy | 0.91250 | 0.90243 | 0.90677 | 0.01007 | 1.41 | 0.80 | 0.61 |
| `learned (older)` | 0.96042 | **0.94557** | 0.96406 | 0.01849 | **3.34** | **0.92** | **4.92** |
| newest task | 0.96667 | 0.94323 | 0.95677 | 0.02344 | **3.55** | 1.86 | **2.33** |
| adjacent-pair interference | 0.13302 | 0.14738 | **0.18711** | **0.05409** | 1.38 | **3.90** | 2.54 |
| distant-pair interference | 0.11500 | 0.08607 | 0.11214 | 0.02893 | 1.70 | 0.13 | 1.25 |

## 2. Both halves of the earlier reading are wrong

The earlier finding
(`docs/findings/2026-09-25-the-support-draw-moves-learning-and-not-retention.md`) said: *"the draw moves the two
LEARNING quantities and nothing else — both learning measures are resolved at 3.3σ and 3.6σ, and the retention
measure and both interference terms stay inside 1.0–1.7σ"*, on the pair draw 0 against draw 1. The third draw:

1. **`learned (older)`'s effect was one outlier draw, not a magnitude.** Draw 2 sits **0.92σ** from draw 0 on that
   quantity while draw 1 sits **3.34σ** away and 4.92σ from draw 2. The "3.3σ effect" is the distance to *one
   particular other draw*, and two of the three pairs are 0.92σ and 4.92σ. Nothing about that is a magnitude to
   quote — the honest description of three draws is the **span, 0.01849**, and even that rests on 2 df.
2. **"Nothing else moves" is false.** Draw 2 moves the **adjacent-pair interference by 3.90σ** — 0.13302 →
   0.18711, the **largest span of any quantity measured here (0.05409)** — where the draw 0/1 pair put it at 1.38σ.
   So the term I called draw-robust at this overlap is the one draw 2 moves most, and the quantity I called
   draw-dominated is the one draw 2 leaves alone.

**With two draws one cannot tell a draw effect from an outlier draw, and that is now a measured statement rather
than a caveat.** The earlier finding's own §5 said "δ's sign reversal is itself one pair of draws"; the third draw
says the same about the whole structure, including the sign reversal's denominator.

## 3. What this does for the endpoint read that is running

`e197`'s midpoint and endpoint land later, and **E1–E3 remain the right things to read** — a third draw at the
endpoint is what can tell whether the endpoint's forgetting rise (2.99σ on draw 0, 3.30σ on draw 1) is stable or
whether draw 1 was an outlier there too. One suggestive analogue is already visible: at overlap 0.0 the forgetting
span across the three draws is **0.01875**, just inside E3's 0.0200 bar, so if the endpoint behaves like this the
span test will be close.

**And the correction sharpens rule 53's operative clause.** The rule says a claim measured on one draw is
conditional on it; this unit adds the sharper form — **a claim measured across *two* draws is conditional on both,
and can be an outlier's distance rather than a spread.** Two draws can falsify (as R1 and R2 did) and cannot
characterise; three can bound a span; only averaging many, which rule 10 asks for, gives a magnitude.

## 4. What this does not license

- **That the support draw is harmless at overlap 0.0.** Its largest measured span is 0.05409 on the adjacent-pair
  interference, whose axis-wide effect at the midpoint is 0.09064 on draw 1 — the nuisance and the signal are the
  same size there.
- **That draw 1 is "wrong".** Three draws give two degrees of freedom; which draw is atypical is not a question they
  can settle, and draw 1's numbers remain its own.
- **A standard deviation.** No three-draw statistic here is a spread estimate; the spans in §1 are descriptive, and
  the pairwise σs are what they always were — distances between two specific samples.
- **That the axis claims are uniformly fragile.** Two of them survived the draw-0/1 comparison
  (`docs/findings/2026-09-25-only-two-of-the-axis-claims-survive-a-second-draw.md` §3), and the third draw has not
  yet reached the overlaps where they are stated.
