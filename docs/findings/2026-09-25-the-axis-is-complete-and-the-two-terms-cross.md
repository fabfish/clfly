# The axis is complete: all six registered claims decided, the fitting deficit is a shape and not an excursion, and the two interference terms cross

**Date:** 2026-09-25
**The last level landed at 18:04:46 and the three-level registration is fully read.** `e193_r32_overlap075` achieved
Jaccard **0.6000**; `e194` judged all six claims the moment it appeared, exit 0. The launching command has finished
(exit 0), so the family is closed. Every number below is off artifacts that exist; the readers are deterministic and
the whole set is reproducible with three commands.

---

## 1. The six claims

| | claim | bar | measured at achieved 0.6000 | verdict |
|---|---|---|---|---|
| **S1** | far progress − near progress, points | ≥ 40 | **28.02** | **between the bar and the falsifier** (falsifier < 15) |
| **S2** | near progress, % of its own 0 → 1 change | < 50 | **47.88** | **MET** — by 2.1 points |
| **S3** | network far − analytic far, points | ≥ 15 | **23.74** | **MET** |
| **S4** | accuracy progress, % of its own 0 → 1 change | < 176.6 | **157.94** | **MET** |
| **S5** | `learned (older)` vs `e116` | > −0.0100 | **−0.0263 ± 0.0035 = 7.48σ** | **FALSIFIER FIRED** (falsifier ≤ −0.0200) |
| **S6** | `ewc-block-rand`'s `learned (older)` vs `e153` | < −0.0100 | **−0.0143 ± 0.0042 = 3.43σ** | **MET** |

**S5's falsifier firing is the result, not a failure of the design.** It was registered to distinguish "the midpoint's
deficit is an excursion" from "it is the axis" — and the axis is what it is: the deficit is **−0.0263 at achieved 0.6
against −0.0326 at achieved 0.3333**, so it decays slowly rather than ending. **S6 MET says the same thing on the arm
that makes it a task-set property**: the size-matched random control still shows it, at 3.43σ.

## 2. The complete shape of the two interference terms — and they cross

`naive`, each term as a fraction of its own 0 → 1 change:

| achieved overlap | adjacent pairs | distant pairs |
|---|---|---|
| 0.1429 | 12.3% (1.23σ) | 7.5% (0.30σ) |
| 0.3333 | 20.0% (1.58σ) | **82.1% (3.31σ)** |
| **0.6000** | **47.9% (3.78σ)** | **75.9% (3.40σ)** |
| 1.0000 | 100% (7.81σ) | 100% (3.12σ) |

**The far term is non-monotone**: it reaches 82.1% of its range by one third of the axis and then comes *down* to
75.9%, so its peak is at the midpoint. **The near term is strongly back-loaded**: 12.3% → 20.0% → 47.9% → 100%, i.e.
**more than half its rise happens in the last 40% of the axis.** That is why **S1 landed between its bar and its
falsifier** — the 62-point gap at the midpoint narrows to **28 points** as the near term accelerates and the far term
retreats, and S1's registration named neither of those two outcomes.

**The registered extrapolations for S2 were both wrong in the same direction.** The registration wrote down 30.8%
(constant slope) and 22.6% (constant ratio to the analytic line); measured **47.88%** — the near term accelerated
past both, and the bar was met by 2.1 points rather than comfortably. A registration that had placed the bar at
either extrapolation would have called a MET a failure.

## 3. The accuracy account, complete

| achieved overlap | `learned (older)` | `forgetting` | accuracy as % of its 0 → 1 change |
|---|---|---|---|
| 0.1429 | +0.0065 (2.03σ) | +0.0141 (1.16σ) | 15.0% |
| 0.3333 | **−0.0326 (8.10σ)** | +0.0083 (0.79σ) | **176.6%** |
| **0.6000** | **−0.0263 (7.48σ)** | +0.0156 (1.56σ) | **157.9%** |
| 1.0000 | +0.0010 (0.33σ) | **+0.0318 (2.99σ)** | 100% |

**S4 MET** — the accuracy cost does come back down from the midpoint's peak (176.6% → 157.9%), so the midpoint is a
local maximum as registered and the endpoint's 100% is a genuine turn. And the reading of the whole column is now
unambiguous: **the interior of the axis costs the network the ability to fit its tasks (7.5–8.1σ at two points),
while the endpoint costs it retention (2.99σ), and the two never fire together** — learning is flat at both ends
(0.33σ at 1.0, 2.03σ *better* at 0.1429) exactly where forgetting is 1.2–3.0σ, and vice versa.

The forgetting column also shows the interior is not a simple ramp: **44.3% → 26.2% → 49.3%** of its own 0 → 1 change,
non-monotone in the means with every interior point unresolved (1.16σ, 0.79σ, 1.56σ).

## 4. The λ = 1.0 family, which this launch accidentally produced

Its registration put P1 and P2 on the block arms against `e153`. Complete:

| `ewc-block` vs `e153` | 0.1429 | 0.3333 | **0.6000** |
|---|---|---|---|
| forgetting | +0.0453 (4.10σ) | +0.0185 (1.60σ) | **+0.0250 (2.20σ)** |
| accuracy | −0.0309 (4.2σ) | −0.0458 (5.53σ) | **−0.0417 (5.20σ)** |
| adjacent-pair interference | +0.0010 (0.3σ) | −0.0059 (1.20σ) | **−0.0002 (0.1σ)** |

- **P1's ordering clause is unresolved, not refuted.** The registration said forgetting at 0.3333 lies above 0.6000;
  they are 0.0185 and 0.0250, and the paired contrast is **−0.00651 ± 0.01292 = −0.50σ** — a 0.5σ lean the other way.
  The clause "both between the 0.1429 value and zero" **does** hold (+0.0185 and +0.0250 against +0.0453), and the
  0.1429-against-0.6000 contrast is +0.02031 ± 0.01397 = 1.45σ, also unresolved.
- **P2 holds at this level**: the interference term is −0.0002 (0.1σ), inside its 1σ clause — it was the 0.3333 level
  that broke it marginally at 1.20σ.
- **The accuracy column tells the family's real story**: the penalised arm's cost is 4.2–5.5σ at **every** interior
  level and never resolves, while its forgetting is 1.6–4.1σ, i.e. the penalty moves the cost from retention to
  accuracy and keeps it there.

## 5. What the completed axis settles, and what it opens

- **C4's box asked for the network line's shape and now has it**: the adjacent-pair term rises monotonically and
  late; the distant-pair term rises early and non-monotonically. The two terms of one instrument have different
  shapes, which is not a property of the analytic line, whose far term rises monotonically and slowly
  (52.2% at achieved 0.6000).
- **The registered P1/P2 were both about the adjacent-pair term and both failed at the midpoint** — and the term that
  carries the resolved response there is the distant one. That is the sentence the registration did not ask.
- **The fitting deficit is the axis's interior.** Two interior levels, 7.5σ and 8.1σ, control-confirmed at both; the
  learning term is flat at both ends. So the shape is "flat, deep in the middle, flat", and the next question is
  whether the depth is a property of the *number of shared neurons* or of the particular supports, which needs a
  different design — one that holds the sharing fixed and moves something else.
- **Opened**: the far term's non-monotonicity has no registered explanation, and the near term's acceleration between
  0.6 and 1.0 is where half its rise lives.

## 6. What this does not license

- **That the far term's 82.1% → 75.9% drop is a fact about the mechanism.** Both points are ~3.3σ from zero and their
  difference is smaller than either; the non-monotonicity is in the *fractions*, not tested as a contrast.
- **That S1's middle outcome is a null.** It is one measurement between a bar and a falsifier placed by a
  registration whose two extrapolations both missed; nothing here says the separation is absent, only that it is
  between the two.
- **Any cross-family magnitude.** The λ = 1.0 rows are one draw per family at a penalty that is not neutral.
- **That the axis is about the connectome.** §2's supports are random draws at each target overlap, so what varies is
  how many neurons the tasks share and not which ones.

---

**CORRECTION, later the same day: §3's `learned (older)` profile is draw 0's, and its interior value did
not replicate.** On support draw 1 the midpoint's value is **+0.00417 ± 0.00361 = 1.15σ** against draw 0's
−0.0326 = 8.10σ, and the draw's own effect on that quantity is −0.0148 (overlap 0.0) and +0.0219 (achieved 0.3333)
— a sign reversal across the axis. §2's two-term profile and §1's six verdicts stand as draw-0 measurements, and
of the claims in §5 only the interference account's rise is resolved on **both** draws. `docs/findings/2026-09-25-the-interior-fitting-deficit-did-not-replicate.md`
