# The base family's 2.08σ does not survive a second control draw

**Date:** 2026-09-24
**Artifacts:** `runs/e140_r32_methods_plastic_40reps.json` (the five-method table; its `ewc-block-rand` row is
**draw 0**) and `runs/e140_r32_rand_draw1.json` (**draw 1**, `--partition-seed 1`, fingerprint `3058aa874ae6`).
Draw 2 is still running; this is the two-draw reading of a three-draw registration.
**Context:** earlier this session the base family's central contrast was reported as *"the strongest it has ever
been measured — 2.08σ in favour of the biology"* after five replicates gave **+0.0167 in the opposite direction**.
**It is the control's own draw variation.**

---

## 1. The measurement

| | forgetting | accuracy |
|---|---|---|
| `ewc-block` (biological) | +0.0573 | 0.9168 |
| `ewc-block-rand`, **draw 0** | +0.0779 | 0.9054 |
| `ewc-block-rand`, **draw 1** | **+0.0591** | 0.9189 |
| `naive` | +0.0750 | 0.9125 |

**The two draws of the same control arm, on the same forty seeds, differ by −0.01875 ± 0.00804 = 2.33σ.** That is
the draw term alone, and it is **larger on the base family than on the wiring family**, where the same two draws
differed by 0.0138 (1.33σ).

**And the contrast the paper is about, against each draw:**

| control used | `ewc-block` − `ewc-block-rand` |
|---|---|
| **draw 0** (the single-draw number reported before) | **−0.02057 ± 0.00990 = 2.08σ**, 28/40 negative |
| **draw 1** | **−0.00182 ± 0.00690 = 0.26σ**, 21/40 negative |
| **mean of the two** | **−0.01120 ± 0.00752 = 1.49σ** |

**So the biological partition's advantage is 2.08σ against one sample of its own control and 0.26σ against
another.** The registered reading (P1: the three-draw contrast stays negative and at least as large as 2.08σ;
falsifier: within 2σ of zero) **fails its P1 already at two draws and fires its falsifier already at two draws**,
and draw 2 will make it formal.

## 2. And it converges with two independent lines that said the same thing

**Three measurements, taken in three different ways, all say the base family's advantage is inside the control's
own variation:**

1. **The wiring family's three-draw contrast is 0.99σ** and its registered falsifier fired
   (`docs/findings/2026-09-24-on-the-wiring-family-the-biology-still-shows-nothing.md`) — a family chosen to
   stress the *opposite* channel, where the forgetting is in the weights the partition acts on.
2. **No recorded mechanism quantity distinguishes the two partitions at all** — θ-only first order **0.06σ**,
   cosine 0.16σ, whole-body 0.52σ, bias half 0.57σ, second-order quadratic 1.10σ with a per-seed sd fifty times
   its own mean (`docs/findings/2026-09-24-the-central-contrast-has-no-mechanism-signature.md`).
3. **And now the base family's single-draw 2.08σ is 0.26σ against the second draw**, with a **2.33σ** difference
   between the two draws themselves.

**So the number that argued against the paper's null is the one the control's own variation explains**, and the
paper's central claim — *the biology shows no advantage over its size-matched random control* — is **strengthened**
by the measurement that was expected to break it.

## 3. What this changes

- **The paper's §4.7 sentence that this session wrote must be corrected in place.** It says the biology's own
  contrast *"both resolves further and reverses"* at forty replicates, reaching 2.08σ in favour of the biology.
  **It is 0.26σ against the other draw and 1.49σ against the mean of two**, and the honest form is *"the single
  draw that made it 2.08σ is one sample from a control whose measured spread is 2.33σ between two draws on this
  family"*.
- **And the five-replicate value's sign flip is explained rather than replaced**: five replicates gave **+0.0167**
  (biology worse) and one draw at forty gave **−0.0206** (biology better). **Both are draws of a control whose
  spread is this large**, so neither number is evidence about the biology — which is what rule 10 said before any
  of this was measured.
- **It also re-reads the mechanism finding**: the reason no recorded quantity distinguished the partitions is now
  the simplest one — **there is no resolved difference for a quantity to track.**

## 4. What it cannot settle

- **Draw 2 is running**, so the registered three-draw form is not yet computable; the two-draw reading is decisive
  enough to report because P1 and the falsifier are both already crossed, but the three-draw number is the
  registered one and will be reported when it exists.
- **One degree of freedom estimates the draw sd here**, so 0.00804 is a bound rather than a measurement, and the
  same is true of the wiring family's 0.0086.
- **And it does not say the partitions are equivalent** — it says the difference this design can see is smaller
  than the variation of its own control, which is a statement about the design's resolution: **with a draw term of
  this size, a contrast needs roughly 3σ × 0.008 ≈ 0.024 to resolve, and the largest single-draw value ever
  measured here is 0.0206.**
