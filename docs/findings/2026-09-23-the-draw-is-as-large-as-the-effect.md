# `e113`: the draw is as large as the effect, so the design statement is withdrawn

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py` (now with `--readout-seed`), five runs; artifacts
`runs/e113_r300_draw{1,2,3}.json`, `runs/e113_r512_draw1.json`, `runs/e113_r300_draw1_plateau.json`.
**Artifacts:** the five above, plus the seven read-out artifacts of `e109`/`e110`/`e111`/`e112`.
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, 5 replicates, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, read-out 300 with **four independent draws** and 512 with
**two**, training seeds fixed at `--seed0 0`.
**Pre-registration:** `docs/findings/2026-09-23-is-the-read-out-shape-about-the-size-preregistered.md`,
committed before the runs.
**Context:** `docs/findings/2026-09-23-both-metrics-have-an-interior-optimum.md` — the seven-point design
statement — and a property of the runner that five fires of shape work had not noticed.

---

## 1. The confound was real: the axis's points differ in two ways at once

The read-out subset is drawn **independently for every size**, so `choice(size=300)` is not a superset of
`choice(size=32)`. Measured in a test: two draws at size 300 overlap in **63–73 of 300** neurons against a
chance rate of 69, and a size-32 draw is **not contained in** a size-300 draw at all. **So the seven-point
"read-out axis" was a sequence of unrelated neuron samples**, and every point on it differed from every other in
*how many* neurons were read out **and** *which* neurons they were — with only the first treated as the variable.

## 2. The control fires, and it fires at exactly the threshold

| run | forgetting | accuracy |
|---|---|---|
| read-out 300, **seed0 draw** | +0.0083 | 0.9569 |
| read-out 300, draw 1 | +0.0146 | 0.9417 |
| read-out 300, draw 2 | +0.0208 | 0.9472 |
| read-out 300, draw 3 | +0.0208 | 0.9486 |
| **four draws at one size** | **span 0.0125**, sd 0.0060 | |
| read-out 512, seed0 draw | +0.0208 | 0.9486 |
| read-out 512, draw 1 | +0.0333 | 0.9431 |
| **two draws at one size** | **span 0.0125** | |

**P1 fails and P2 fails**, both at exactly the number the pre-registration named: the draw-to-draw **span at a
single size is 0.0125**, and **0.0125 is also the across-size difference the design statement rests on** (512's
+0.0208 against 300's +0.0083). The metric's granularity explains the exact coincidence — with 5 replicates and
two forgetting tasks the mean forgetting lands on multiples of 1/480 = 0.002083, so a threshold can be hit
exactly — and it does not soften it: **the variation a practitioner cannot control (which neurons) is the same
size as the variation they can (how many).**

**The design statement is therefore withdrawn**, as the pre-registration said it would be: *"read-out ≈ 300 is
the optimum on both metrics"* is **not distinguishable from a property of which 300 neurons were drawn**, and
the same applies to the "anomaly" language of the two fires before it, which compared the same axis.

## 3. What survives, and the yardstick it is measured against

The draw sd at read-out 300 is **0.0060** over four draws. Taking each neighbouring step along the axis as a
multiple of it:

| step | difference | / draw sd | resolved? |
|---|---|---|---|
| 1307 → 900 | 0.0188 | 3.13 | **yes** |
| 900 → 700 | 0.0063 | 1.04 | no |
| 700 → 512 | 0.0146 | 2.44 | no |
| **512 → 300** | **0.0125** | **2.09** | **no** — and this is the step the design statement rested on |
| 300 → 128 | 0.0250 | 4.18 | **yes** |
| 128 → 32 | 0.0396 | 6.61 | **yes** |

**So three of the six steps survive the draw and three do not**, and the ones that do not are the fine structure:
**the bump at 700 is 1 draw-sd** — the previous fire's third open question, answered as *unresolved* rather than
as a second local feature — and the exact location of the minimum is inside the draw's own range.

**What survives is coarser and still worth having**: the whole state forgets more than 900, read-out 300 forgets
less than 128, and read-out 32 forgets far more than 128. The interior-minimum *existence* survives; its
**location and depth do not**.

**And the draw is not the only yardstick, which makes the picture worse rather than better.** The reported
`forgetting_sem` at read-out 300 is **0.0101** — the within-run variation over five training replicates at a
*fixed* draw — and the draw contributes a further **0.0060** on top of it. Neither covers the other, and a
difference between two read-outs is the difference of **two** such quantities, so the step the design statement
rested on is **well inside a combined uncertainty of roughly 0.017**. **The paper's sem was not wrong; it
measures something else**, which is this project's oldest lesson arriving on a new axis.

## 4. The rule this fire is an instance of, and the one it adds

**Rule 26 says to build the control into the manipulation.** Five fires of shape work along this axis satisfied
rule 26 *at each level* — every read-out was re-run and reproduced bit-identically, every frozen control was
exact (0 of 6 failures) — and violated it **at the level of the axis's own construction**: the points were
supposed to differ in one variable and differed in two, and the one that was not treated as a variable was never
varied. **The added rule: a factor that is not the manipulated variable is not thereby held constant — the
`config` records what was asked for, and "identical config except the variable" is a claim about the *code*'s
other inputs, one of which was an RNG draw.**

**And the reproducibility discipline this project has been applying was conditional on that draw.** Every
"bit-identical over seven executions" result in this sequence compares runs at the **same** draw; the repeat of
draw 1 here is bit-identical again, which is what makes the draw difference attributable to the draw. So the
measurements are reproducible *given a draw* and **not** reproducible across draws, and no artifact before this
fire recorded which draw it used — the `config` has `readout_size` and not the subset.

**A durable fix is now possible and is the next step**: have the runner record an **explicit `readout_seed` in
the config instead of `None`** so that `config` alone identifies the draw, and re-run the seven read-outs at a
second draw each — which is the full version of this control and was deliberately not run here, because whether
it was worth running is what this fire decided.

## 5. What this cannot settle

- **Four draws at one size and two at another.** The draw sd is estimated at read-out 300 (n = 4) and its span
  confirmed at 512 (n = 2); whether the draw variance is the same at other sizes is not measured, and read-out
  32 — one of the three surviving steps — has no second draw at all.
- **It does not re-open the mechanism search, and it narrows it differently than expected**: the negative result
  *"every mechanical quantity is monotone in the read-out while both metrics are not"* now rests on a series
  whose fine structure is inside the draw, so **the monotone quantities and the non-monotone ones are being
  compared at a resolution the axis does not have**. The honest version of that claim is the coarse one.
- **A paired treatment is not done here.** All seven runs share the training seeds (`seed0 = 0` → 0, 100, …, 400)
  while differing in the read-out draw, so a paired contrast between two sizes is legitimate and would be
  tighter than the unpaired arithmetic above; this fire reports the unpaired statement because it is the
  conservative one and because the pairing is across a variable whose variance is what is being estimated.
