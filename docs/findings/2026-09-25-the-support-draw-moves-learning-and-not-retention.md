# The support draw moves LEARNING at 3.3σ and retention and interference at ~1σ — the first measurement of the draw the axis rests on

**Date:** 2026-09-25
**A cheap unit on the first artifact of the replication, available before the rest of its family.** `e195`'s
overlap-0.0 run landed at 18:27, and it is comparable to `e116` — the same target, the same arm, the same circuit,
the same read-out draw, the same 40 seeds — with **one live difference: the support draw**. That makes the first
measurement in this corpus of what the support draw does on its own, which is the quantity every "one draw" caveat
here has been unable to size.

---

## 1. The contrast is clean, and the inert fields are checked rather than assumed

`differing_fields` between `e116`'s config and `e195_r32_ovl00_ss1_naive_40reps.json`'s gives **three** keys:

| field | `e116` | `e195` | status for `naive` |
|---|---|---|---|
| `support_seed` | absent (pre-flag) | 1 | **the manipulation** |
| `lam` | 0.003 | 1.0 | inert — verified **bit-identical** below |
| `fisher_batches` | 8 | 32 | inert — verified **bit-identical** below |

**The inertness is a measurement and not a declaration.** Both premises were checked by finding artifact pairs that
differ in exactly one of them and comparing the naive arm's four per-replicate series:

| pair | differs in | naive series |
|---|---|---|
| `e116` vs `e140` | `fisher_batches` 8 vs 32 | **bit-identical** |
| `e144` vs `e153` | `lam` 0.003 vs 1.0 (**333×**) | **bit-identical** |

`readout` is byte-identical too (`subset_sha1 33bcd7fa68a2`, draw seed 0), and so is `circuit`. So draw 1 minus draw 0
on this configuration is the support draw's own effect, at 40 paired seeds.

## 2. The measurement

| quantity | draw 0 → draw 1 | difference | σ |
|---|---|---|---|
| forgetting | 0.07500 → 0.06354 | −0.01146 ± 0.01113 | 1.03σ |
| accuracy | 0.91250 → 0.90243 | −0.01007 ± 0.00715 | 1.41σ |
| **`learned (older)`** | 0.96042 → 0.94557 | **−0.01484 ± 0.00444** | **3.34σ** |
| **newest task** | 0.96667 → 0.94323 | **−0.02344 ± 0.00660** | **3.55σ** |
| adjacent-pair interference | 0.13302 → 0.14738 | +0.01436 ± 0.01040 | 1.38σ |
| distant-pair interference | 0.11500 → 0.08607 | −0.02893 ± 0.01706 | 1.70σ |

**The draw moves the two LEARNING quantities and nothing else.** Both learning measures are resolved (3.3σ and 3.6σ)
at the same overlap, on the same 40 seeds, with no manipulation at all; the retention measure and both interference
terms stay inside 1.0–1.7σ. That is a structure rather than a noise figure, and it is the same structure today's axis
finding reports from the other direction: **the interior's cost is a fitting effect**
(`docs/findings/2026-09-25-the-axis-is-complete-and-the-two-terms-cross.md` §3), and the draw's own effect lands on
the fitting quantity.

**The partition draw, measured by `e168`, acts differently.** On the matched-random control it moved *forgetting* by
up to 0.0138 (1.33σ, unresolved) and the newest task by 0.0068 (1.48σ) — so on that draw the retention quantity was
the larger one, and neither resolved
(`docs/findings/2026-09-24-the-random-control-is-a-sample-and-31-of-38-artifacts-do-not-say-which.md` §2). The two
draws are not the same size on the same quantities, and the support draw is the **larger** of the two on the newest
task by a factor of 3.4 and the only one of the two that resolves.

## 3. What this does to the axis's claims, quantity by quantity

| the axis reports | its σ | the draw's own effect | ratio |
|---|---|---|---|
| `learned (older)` at achieved 0.3333 = −0.03255 | 8.10σ | −0.01484 | **2.2×** |
| the newest task at achieved 0.3333 = −0.01667 | 2.25σ | −0.02344 | **0.7×** |
| forgetting at overlap 1.0 = +0.03177 | 2.99σ | 0.01146 | 2.8× |
| distant-pair interference at achieved 0.3333 = +0.07239 | 3.31σ | 0.02893 | 2.5× |

**The newest-task numbers are inside the draw's own scatter** — the axis's −0.01667 is *smaller* than the 0.02344 the
draw moves the same quantity by on a configuration with no manipulation at all. That is the sharpest caveat this
session has produced about any of its own numbers, and it applies to the newest-task column in three findings today,
including the one that says the newest-task drop is *not* arm-independent
(`docs/findings/2026-09-25-the-fitting-deficit-is-the-same-in-all-three-arms.md` §3).

The other three survive: the interior deficit is 2.2× the draw effect, the endpoint's forgetting 2.8×, the midpoint's
far term 2.5×. **Being 2.2× a resolved 3.3σ nuisance is not the same as being safe**, which is what the replication is
for — but it does mean the deficit is not *made* of the draw.

## 4. Registered now, before the replication's midpoint lands

The interior deficit is a **difference of two overlaps within one draw**, so a draw effect that is *constant across
the axis* cancels out of it, and only a draw effect that *depends on the overlap* moves it:

```
draw-1 deficit = draw-0 deficit + δ(0.3333) − δ(0.0),   with δ(0.0) = −0.01484 measured
```

- **D1 — the draw's effect is not constant across the axis.** The measured δ(0.0) is −0.01484; D1 says δ shrinks
  toward zero as the overlap rises, so δ(0.3333) ≈ 0 and the draw-1 deficit is **−0.0177**, landing R1 **in its own
  null band** (−0.0200 < x < −0.0100) rather than MET.
- **The competing reading is the constant one**: δ(0.3333) = δ(0) leaves the deficit unchanged at **−0.0326** and
  **R1 is MET**. The two readings are 0.0148 apart against R1's own sem of ~0.004 — **decidable**, which is why the
  forecast is worth writing down.
- **Falsifier**: R1's falsifier fires (draw-1 deficit above −0.0100). By the identity above that needs
  δ(0.3333) > +0.0048, i.e. the draw's effect on `learned (older)` *reverses sign* between overlap 0.0 and achieved
  0.3333 — a shape worth knowing about and not one either reading predicts.
- **Read by**: `e194 --claims replication` with the draw-1 family's own endpoints, which is already armed.

## 5. What this does not license

- **A between-draw standard deviation.** Two draws give a difference, not a spread; "the draw effect is 3.3σ" means
  *these two draws differ by that much at 3.3σ*, and rule 10's answer — many draws averaged — is not what this design
  pays for.
- **Transferring the magnitude to another overlap.** §2 is measured at target 0.0 only; the whole content of D1 is
  that the magnitude may not transfer.
- **Reading the draw into the retention claims.** Forgetting moved 1.03σ here; that the endpoint's forgetting claim
  is 2.8× the draw effect is an argument from one configuration, not a measurement at the endpoint.
- **That the interference split is draw-robust because its two terms measured 1.4σ and 1.7σ.** Both are unresolved
  here, which bounds them from above at ~0.03 on the far term — the far term's own axis change is 0.072, so the ratio
  in §3 is a lower bound on the margin.
