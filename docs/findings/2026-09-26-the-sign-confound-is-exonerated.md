# The sign confound is exonerated: shuffling only the signs leaves the penalty at the axis's level

*2026-09-26 03:29, `runs/e215_signshuffle_rs0.json` … `rs2.json` — three cells, 12 min. Read from the artifacts' own
geometry and analytic blocks. The registration is
`docs/findings/2026-09-26-registered-the-sign-shuffle-has-this-line-been-reading-a-sign-effect.md`.*

## 1. The three cells

| drawing | alignment | × chance | excess | sem | `top_eig_share` | eff. rank |
|---|---|---|---|---|---|---|
| rs0 | 0.02211 | 0.40× | +0.02975 | 0.00148 | 0.150 | 33.97 |
| rs1 | 0.02151 | 0.39× | +0.02800 | 0.00064 | 0.141 | 37.20 |
| rs2 | 0.01874 | 0.34× | +0.02776 | 0.00076 | 0.135 | 38.94 |

## 2. Both corroborating claims are falsified, and that is the answer

- **X1's falsifier landed**: the sign-shuffled alignment is **0.01874–0.02211 (0.34–0.40× chance)** — far below the
  0.20 bar, below even the band's floor, and *inside the biological axis's own range* (0.07–1.53× chance across the
  34 in-axis cells). So **shuffling the signs does not move the task geometry upward at all**; it leaves it where the
  ordinary rewiring family lives.
- **X2's falsifier landed**: the excess is **+0.02776 to +0.02975** — at or below the 0.06 falsifier bound, against a
  MET bar of 0.10 and the Erdős–Rényi band of 0.14134–0.14897. So **the sign half of the Erdős–Rényi construction
  produces an axis-level penalty, not the jump.**

**So the confound is real but it is not the driver.** `erdos_renyi` does change the wiring *and* the signs, and the
sign half alone leaves the penalty at ≈0.028 — a factor of **5.0× below** the Erdős–Rényi level (0.14187) and only
marginally above the in-axis regime's 0.01237–0.02317. **C1's topology story survives its first confound test**, and
the paper's sentence about Erdős–Rényi does not have to be qualified: whatever carries the jump is in the edge set or
the degree structure, not in which synapses are excitatory.

## 3. The bonus measurement: a third construction's tightness

| construction | drawings | penalty | spread |
|---|---|---|---|
| Erdős–Rényi | 9 | 0.14134 – 0.14897 | 1.05× |
| **sign shuffle** | 3 | 0.02776 – 0.02975 | **1.07×** |
| `alloy1` | 5 | 0.03011 – 0.10067 | **3.34×** |
| `alloy0.9` | 5 | 0.01752 – 0.05861 | **3.34×** |

**The two constructions that homogenise the relation between wiring and weights are the tight ones** — the sign
shuffle keeps the graph and moves the weights, Erdős–Rényi moves both anywhere, and each reproduces its own penalty to
7% over three and nine drawings — **while the alloy, which keeps every weight attached to its source and moves only the
targets, spans 3.34× across five drawings.** That is a *measured* contrast and not a mechanism: what it suggests is
that the alloy's drawings leave a residual, source-specific relation between a neuron's outgoing weights and its
targets, and that this residual is what varies from drawing to drawing. Nothing here tests that.

## 4. What this changes, and what it does not

- **It removes a standing worry** about every Erdős–Rényi contrast in the record — C1's orthogonality sentence, the
  eight ER cells in `e207`'s join, and the interval `[0.23632, 0.27135]` where the penalty changes. The sign pattern
  is now a *tested-and-excluded* confound rather than an unexamined one.
- **It does not say what carries the jump.** The remaining candidates are the edge set, the degree sequence (ER
  preserves neither in- nor out-degree; the alloy preserves out-degree exactly) and the *joint* effect of moving both
  endpoints. Separating them needs a null that preserves one degree sequence and destroys the other — which is the
  next construction, not this one.
- **It does not make the sign pattern uninteresting**: the sign shuffle lowered the alignment to 0.34–0.40× chance,
  i.e. to the *low* end of the axis, so the sign pattern does affect the task geometry even though it does not drive
  the penalty.
- **Three drawings**, so the 1.07× tightness is a range and not an sd, and the same caveat the whole week has carried
  applies: one circuit size, `seed0` 0 throughout.
