# Three draws, four claims: exactly ONE is 3 of 3 — the endpoint's forgetting — and it is the claim the corpus already had

**Date:** 2026-09-25
**`e197` completed at 19:59 and the replication is read at three support draws.** This is the final tally for the
overlap axis: three draws at three targets each, `naive`, 40 seeds, every measurement taken within its own draw
against that draw's own baseline, and the read-out draw shared by all of them (`subset_sha1 33bcd7fa68a2`).

---

## 1. The tally

| claim | draw 0 | draw 1 | draw 2 | **of 3** |
|---|---|---|---|---|
| **R1** — the interior fitting deficit, `learned (older)` at achieved 0.3333 | **MET** −0.03255 (8.10σ) | FALSIFIER +0.00417 (1.15σ) | **MET** −0.02474 (8.12σ) | **2** |
| **R2** — the two terms' separation there, points | **MET** 62.13 | FALSIFIER 10.52 | FALSIFIER **−11.32** | **1** |
| **R3a** — the endpoint's forgetting | **MET** +0.03177 (2.99σ) | **MET** +0.03516 (3.30σ) | **MET** +0.02161 (2.70σ) | **3** |
| **R3b** — the endpoint's `learned (older)` within ±0.0100 | **MET** +0.00104 | between +0.01328 | **MET** +0.00439 | **2** |

**One claim out of four holds on all three draws, and it is the one the project already had**: raising the input
overlap to 1.0 raises forgetting, which the corpus registered as *nine of nine matched comparisons* before any of
today's axis work existed. Its three values are 0.0216, 0.0318 and 0.0352 — a span of **0.01354**, inside E3's
0.0200 bar and a third of the effect's own size.

**R2 is the weakest**: it fails on two of three draws, and on draw 2 the gap is **negative** (−11.32 points), i.e. the
distant-pair term sits *below* the adjacent-pair one at the midpoint. The "two terms with opposite shapes" picture
that the completed axis reported at 18:04 is a property of one draw out of three, and its sister claim (E2, the far
term's midpoint rise) is 2 of 3 rather than the 3 of 3 the design hoped for.

## 2. The one structural lesson worth keeping

**The draw cancels in comparisons between ARMS and does not cancel in comparisons between OVERLAPS.**

Every claim in §1 compares two *overlaps* of the same arm, so the supports differ between the two sides and the draw
enters the difference. A claim that compares two **arms at the same supports** is immune by construction, because both
sides share the draw. Today's other large result is of that kind: the λ = 1.0 family's interference saturation —
`ewc-block`'s adjacent-pair interference at overlap 1.0 is **+0.14700** at λ = 3e-3 (`e144`) against **+0.00162** at
λ = 1.0 (`e153`), **+0.14538 ± 0.01183 = 12.3σ**
(`docs/findings/2026-09-25-p2s-bar-is-60-percent-and-the-read-applied-46.md`) — and `e144` and `e153` are both draw 0
artifacts, so the draw is the *same* on both sides and cancels exactly.

**So the axis's fragility is not a fragility of the substrate or of the instruments; it is a property of what the
axis asks.** A design that moves the overlap must vary the supports, and the supports are a draw with a 3.3–6.6σ
effect on the quantities in question. A design that compares methods at a fixed support level avoids the problem
entirely — which is what most of this project's other work does, and which is why the replication did not touch it.

## 3. What the evening cost and what it bought

- **Cost**: three draws × three targets × 40 replicates ≈ **2.7 hours** of machine time, plus the stopped `e196`.
- **Bought**: the knowledge that of four registered axis claims, one is 3 of 3 (and it was already known), two are
  2 of 3 and one is 1 of 3 — and that **the axis's headline numbers from this afternoon are single-draw quantities**.
  Six findings were written on draw 0 and four of them now carry dated corrections; two were twice corrected.
- **The meta-lesson, stated because the sequence is the evidence**: three draws moved this project's reading of one
  quantity twice, in opposite directions, within two hours — a conclusion at n = 1, then at n = 2, then at n = 3. Each
  was the correct reading of the draws available at the time. Rule 10 has said "one draw is one sample" since this
  project's first week; rule 53 extends it to the substrate's draws; and the remedy for what happened today is the
  design — five levels × three-or-more draws before a shape claim is quotable — and not the prose.

## 4. What this does not license

- **That the axis's effects are absent.** R3a is 3 of 3 at 2.70–3.30σ, and R1 is 2 of 3 at ~8σ. What is unavailable is
  a single number for any of them.
- **That three draws are enough.** Span is a 2-df statistic and §1's "2 of 3" is a count, not a rate; rule 10's answer
  is many draws averaged.
- **That the draw is the only nuisance.** It is the one measured here; the read-out draw is unidentified in 80 of the
  144 artifacts that need it (`docs/findings/2026-09-25-more-of-the-corpus-cannot-say-which-draw-it-used-than-can.md`).
- **Transferring §2's immunity to every cross-arm claim.** It holds when both arms run at the *same* supports, which
  is true of the λ family at overlap 1.0 and not automatically of two arms at different overlaps.
