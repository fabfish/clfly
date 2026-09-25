# The read-out draw, varied for the first time: a small nuisance, and the one surviving axis claim survives it too

**Date:** 2026-09-25
**`e199` completed at 20:38 and both claims are decided.** `--readout-seed` had existed since mid-project but no
artifact in the record was ever run at a second read-out draw, so every read-out-conditional result in the corpus
inherited a condition that had never been tested. It has been now, at two targets and 40 seeds, with the support draw
held at 0.

**A note on what the two artifacts do and do not share, because the labels are easy to swap**: both `e199` artifacts
carry the **same read-out draw** (`subset_sha1 9a4a5774e161`, seed 1) and **different support fingerprints**
(`4393a24aa245` at target 0.0 and `3e5caba2c52c` at 1.0). That is the design: within `e199` only the manipulation
varies, and the supports necessarily differ between the two ends of it because the overlap *is* their construction.
The read-out draw is varied by comparing `e199` against `e116`/`e144`, which are at read-out seed 0 with support seed 0.

---

## 1. F1 — MET, at 4.82σ

The endpoint's forgetting rise at read-out draw 1, measured within that draw:

| configuration | endpoint forgetting rise | σ |
|---|---|---|
| support draw 0 (`e116` → `e144`) | +0.03177 ± 0.01063 | 2.99σ |
| support draw 1 (`e195`) | +0.03516 ± 0.01064 | 3.30σ |
| support draw 2 (`e197`) | +0.02161 ± 0.00800 | 2.70σ |
| **read-out draw 1 (`e199`)** | **+0.04349 ± 0.00902** | **4.82σ** |

**Four of four configurations show it, resolved, and the read-out draw gives the largest value of the four.** So the
only claim on this axis that survived three support draws also survives the other draw dimension: **3 of 3 on
supports, 1 of 1 on read-outs, 4 of 4 overall.** It is the project's oldest claim — nine of nine matched comparisons,
registered long before today's axis work — and it is now the most-tested statement in this family.

## 2. F2 — MET, and the read-out draw is the *small* one

The read-out draw's own effect, comparing `e199`'s artifacts against the read-out-0 originals at the same target,
support draw 0 on both sides, at **both** ends of the axis:

| quantity | at overlap 0.0 | at overlap 1.0 |
|---|---|---|
| forgetting | −0.01120 ± 0.01071 (1.05σ) | +0.00052 ± 0.01327 (0.04σ) |
| accuracy | +0.01024 ± 0.00604 (1.70σ) | −0.00521 ± 0.00729 (0.71σ) |
| **`learned (older)`** | **+0.00260 ± 0.00343 (0.76σ)** | −0.00703 ± 0.00456 (1.54σ) |
| newest task | +0.00312 ± 0.00576 (0.54σ) | −0.00052 ± 0.00535 (0.10σ) |
| adjacent-pair interference | −0.01672 ± 0.01636 (1.02σ) | −0.03470 ± 0.02213 (1.57σ) |
| distant-pair interference | −0.02118 ± 0.02081 (1.02σ) | +0.01530 ± 0.02495 (0.61σ) |

**Nothing is resolved: twelve quantity-by-end combinations, the largest 1.70σ.** And on the quantity the axis's
learning claims are made of, `learned (older)` at overlap 0.0, the two draws are **not the same size**:

| draw | effect on `learned (older)` at overlap 0.0 | σ |
|---|---|---|
| **supports** (draw 1 − draw 0) | **−0.01484** | **3.34σ** |
| **read-out** (seed 1 − seed 0) | **+0.00260** | 0.76σ |

**The read-out draw's point estimate is 5.7× smaller and its 2σ bound (0.0095) is below the support draw's point
estimate.** So on the learning quantities the read-out draw is the smaller lever — which is the expected direction,
given 32 neurons against the supports' 240.

**But it is not uniformly smaller, and the honest bound matters.** On the adjacent-pair interference the read-out
draw's 2σ bounds are ±0.050 at overlap 0.0 and ±0.079 at 1.0, and the *support* draw moved that same term by 0.08036
at the midpoint — so on that term the read-out draw's bound is as large as the support draw's own measured effect, and
no claim of uniform smallness is available.

## 3. What this means for the corpus

**The read-out draw was the largest unidentified class after reconstruction** (80 artifacts before
`e198 --reconstruct` identified them, 0 after). The result is that varying it moves nothing it has been tried on —
which is *good news for the 121 artifacts whose read-out draw is now identified*, because the condition they inherit
is a measured-small one on the accuracy, forgetting and learning quantities, and a merely bounded one on the
interference terms.

**And the contrast between the two draws is the finding**: the substrate has at least two draws, and they are of
different sizes and act on different quantities — the supports move learning at 3.3–6.6σ, the read-out does not
resolve anything. **Which means rule 53's operative advice is not "vary every draw" but "measure each draw's own
effect, because you cannot tell which one matters from its description."**

## 4. What this does not license

- **That one read-out draw characterises the read-out's variability.** One alternative draw is a difference at
  n = 2, and today's own lesson is that such a difference can be an outlier's distance. F2 is a robustness statement
  and a bound, not a spread.
- **Transferring the smallness to other read-out sizes.** `--readout-size` is held at 32 and subsets of different
  sizes are drawn independently; a 300-neuron read-out is a different question.
- **Reading the interference bound as small.** §2's last paragraph: on the adjacent-pair term the bound is as large
  as the support draw's own measurable effect.
- **Any statement about intermediate overlaps.** Two targets only.
