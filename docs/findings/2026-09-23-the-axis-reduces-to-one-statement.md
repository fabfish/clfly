# `e114`: the read-out axis reduces to one statement, and pairing is the wrong tool for it

**Date:** 2026-09-23
**Method:** every read-out pair computed from the seven stored artifacts, against two uncertainty sources — the
per-repeat spread within a run and the draw span measured by `e113` — plus a replicate count for each step.
**Artifacts:** `runs/e109_second_order_r{0,128,32}.json`, `runs/e110_readout512_plastic.json`,
`runs/e111_readout900_plastic.json`, `runs/e112_readout300_plastic.json`,
`runs/e112_readout700_plastic.json`, `runs/e113_r300_draw{1,2,3}.json`, `runs/e113_r512_draw1.json`.
**Context:** `docs/findings/2026-09-23-the-draw-is-as-large-as-the-effect.md`, which withdrew the design statement
and named two things as the next step: **the paired treatment**, which all seven runs license because they share
the training seeds, and **a second draw at every read-out**.

---

## 1. The paired treatment is not uniformly tighter, and it cannot see the draw

| neighbour step | difference | paired sem | unpaired sem | paired σ | unpaired σ |
|---|---|---|---|---|---|
| 1307 → 900 | +0.0188 | 0.0397 | 0.0355 | 0.47 | 0.53 |
| 900 → 700 | −0.0063 | 0.0218 | 0.0198 | 0.29 | 0.32 |
| 700 → 512 | +0.0146 | 0.0185 | 0.0194 | 0.79 | 0.75 |
| **512 → 300** | +0.0125 | 0.0141 | 0.0129 | 0.88 | 0.97 |
| **300 → 128** | −0.0250 | 0.0199 | 0.0161 | 1.25 | 1.56 |
| **128 → 32** | +0.0396 | 0.0254 | 0.0196 | 1.56 | 2.02 |

**Pairing makes four of the six neighbouring steps *worse* and none of them decisive**, because the per-replicate
differences do not share a sign — at the whole state, replicate forgetting runs
`−0.0104 / +0.0833 / −0.0104 / +0.0104 / +0.1667`, so the paired difference against any other read-out is
dominated by the same replicate-to-replicate swing the mean already carried.

**And where pairing *does* look strong it is structurally the wrong tool.** Two pairs tighten dramatically —

| pair | difference | paired sem | paired σ | unpaired σ |
|---|---|---|---|---|
| 900 → 300 | −0.0208 | **0.0033** | **6.32** | 1.54 |
| 300 → 32 | +0.0646 | **0.0077** | **8.44** | 3.56 |

— and the reason is that a **systematic** difference between the two read-outs' draws is a **constant offset** in
the paired difference. **Pairing removes the shared training-seed variance and cannot touch the draw**, because
the draw is fixed within a run and differs between the two sides; so a paired σ is *optimistic by exactly the
amount the draw contributes*, and `e113` measured that amount: **a span of 0.0125 across four draws at one
size**. Against that, **900 → 300's 0.0208 is 1.7 draw-spans** — suggestive, not decisive — while the paired
σ of 6.32 would have been read as a resolution. **A contrast whose statistic is blind to its own confound is not
a tighter measurement; it is a differently wrong one**, which is this project's oldest lesson in a new place.

## 2. Only four of twenty-one read-out pairs resolve, and all four involve read-out 32

| pair | difference | unpaired σ |
|---|---|---|
| **900 → 32** | +0.0438 | **2.49** |
| **512 → 32** | +0.0521 | **3.04** |
| **300 → 32** | +0.0646 | **3.56** |
| **128 → 32** | +0.0396 | **2.02** |

**Every other pair of the twenty-one is below 2σ**, and the neighbour steps are all below **1.6σ** — including
the 512 → 300 step the withdrawn design statement rested on (0.97σ). **Read-out 32 does not resolve against the
whole state either** (0.67σ), because the whole state carries the largest per-repeat spread of the seven
(**0.0768**, against 0.018–0.039 for the others) — which is the paper's own resolution-limit sentence showing up
as a number at one point.

**So five fires of shape work reduce to one sentence: read-out 32 forgets more than 900, 512, 300 and 128.** The
interior minimum, its location, the local bump at 700, and the coarse decline from the whole state are **all
inside the noise of at least one of the two uncontrolled factors** — the per-repeat spread, or the draw.

## 3. What this costs, per step, and what that says to run

With the measured per-repeat sd at each end, the replicate count for a 2σ unpaired resolution is
`ceil((2·sqrt(sd_a² + sd_b²)/diff)²)` per read-out, at ≈ 22 s per replicate for `--methods naive`:

| neighbour step | difference | pooled sd | replicates per side | time |
|---|---|---|---|---|
| 1307 → 900 | 0.0188 | 0.0793 | **72** | ~53 min |
| **900 → 700** | **0.0063** | 0.0442 | **200** | **~147 min** |
| 700 → 512 | 0.0146 | 0.0433 | 36 | ~26 min |
| **512 → 300** | **0.0125** | 0.0289 | **22** | **~16 min** |
| 300 → 128 | 0.0250 | 0.0359 | 9 | ~7 min |
| 128 → 32 | 0.0396 | 0.0438 | 5 | ~4 min |

**Two conclusions, and they are opposite in kind.** The **700 bump is not worth chasing** — 200 replicates per
side, nearly two and a half hours, to resolve a 0.0063 difference that the draw alone moves by 0.0125. And **the
512 → 300 step is affordable at 22 replicates per side (≈ 16 minutes)**, which is the step the withdrawn
statement rested on and the one an interior minimum stands or falls with.

**So the registered next step is not the second draw at read-out 32** — that was this fire's other naming, and
this table says the draw is *not* the binding limit at 32: its per-repeat sd is 0.0338 against a draw span that
has not been measured there. **The binding limit at every step is the per-repeat spread**, which the paper
already names in §4.7, and the way to beat it is replicates rather than draws.

## 4. What this does *not* touch, and the boundary is the draw

- **Within-run contrasts are unaffected.** Every arm inside one run shares that run's read-out subset, so
  contrasts like §4.7's `ewc-block` against `ewc-block-rand`, or the diagonal against `naive`, are **immune to
  the draw** — the confound is a property of the axis, not of the runs on it. The paper's within-run σ's stand as
  they are; what this fire reduces is the **cross-read-out** series of §4.2.
- **The frozen-body series is cross-read-out and therefore shares the problem**, since each size has one draw
  and the plastic and frozen runs at a size *do* share it. Its coarse trend (a gap that rises from −0.0111 to
  +0.1000 as the read-out narrows) is far larger than any draw span, so it survives; its individual steps have
  not been tested against the draw.
- **And it does not re-open the mechanism search.** The negative result *"mechanical quantities are monotone in
  the read-out while both reported metrics are not"* was already reduced to its coarse form last fire; this fire
  shows that the fine structure it was about is not there to be explained.

## 5. What this cannot settle

- **The draw span is measured at one size** (0.0125 at read-out 300, four draws; confirmed at 512 with two). The
  cost table uses the per-repeat sd only, so its replicate counts are **upper bounds** if the draw were
  eliminated by averaging over draws — which is a different (and more expensive) design.
- **Four of twenty-one is a count on seven points**, and read-out 32's excess is the one thing that resolves;
  whether 32 is a *special* read-out or simply the far end of a monotone trend is exactly what does not resolve.
- **No new run is made here.** This fire is analysis, and its deliverable is a decision: run 22 replicates at 300
  and 512, and stop chasing the 700 bump.
