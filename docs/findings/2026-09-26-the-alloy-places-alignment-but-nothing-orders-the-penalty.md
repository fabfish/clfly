# The alloy places alignment but neither the fraction nor the alignment orders the penalty

*2026-09-26 03:06, `runs/e213_alloy_draws_rs0.json` … `rs4.json` — ten cells, five drawings at each of two fractions,
read by `e214_alloy_draws_read.py`, exit 0. The registration is
`docs/findings/2026-09-26-registered-five-drawings-at-two-alloy-fractions.md`.*

## 1. The three verdicts

| | claim | verdict |
|---|---|---|
| **W1** | at least three of ten cells inside `[0.09101, 0.27135]` | **MET** — **9 of 10** |
| **W2** | the two fractions' means differ by ≥1.5× the larger within-fraction range | **FALSIFIER FIRED** — the difference is **0.21×** the range |
| **W3** | Spearman(measured alignment, penalty) ≥ +0.5 | **null band** — **+0.297** |

## 2. The ten cells

| drawing | cell | alignment | × chance | excess | `top_eig_share` | eff. rank |
|---|---|---|---|---|---|---|
| rs0 | `alloy0.9` | 0.08609 | 1.55× | +0.03171 | 0.640 | 2.46 |
| rs2 | `alloy0.9` | 0.10556 | 1.90× | +0.03812 | 0.625 | 2.59 |
| rs1 | `alloy0.9` | 0.11504 | 2.07× | +0.01752 | 0.819 | 1.50 |
| rs1 | `alloy1` | 0.12815 | 2.31× | +0.04130 | 0.636 | 2.48 |
| rs4 | `alloy0.9` | 0.13999 | 2.52× | +0.03727 | 0.685 | 2.14 |
| rs0 | `alloy1` | 0.14179 | 2.55× | **+0.10067** | 0.167 | 24.28 |
| rs3 | `alloy0.9` | 0.14682 | 2.64× | +0.05861 | 0.532 | 3.57 |
| rs3 | `alloy1` | 0.16704 | 3.01× | +0.03770 | 0.708 | 2.00 |
| rs4 | `alloy1` | 0.17411 | 3.13× | +0.03011 | 0.762 | 1.72 |
| rs2 | `alloy1` | **0.23238** | **4.18×** | +0.04704 | 0.666 | 2.24 |

## 3. W2's falsifier is the finding: the drawing swamps the fraction

| fraction | five penalties | mean | within-fraction range |
|---|---|---|---|
| `alloy0.9` | 0.03171, 0.03812, 0.01752, 0.03727, 0.05861 | 0.03665 | 0.04108 (**3.34×**) |
| `alloy1` | 0.04130, 0.10067, 0.03770, 0.03011, 0.04704 | 0.05136 | 0.07056 (**3.34×**) |

The two means differ by **0.01472** — **0.21×** the wider within-fraction range, against a bar of 1.5×. So the
registration's falsifier is exactly what landed: *"the requested fraction tells you nothing once the drawing is
accounted for."* **Each fraction's five drawings span 3.34× in penalty** — the same ratio in both, which is a
coincidence worth noting and not a claim — and the two fractions' **alignment ranges overlap** (0.086–0.147 against
0.128–0.232), so the fraction is only loosely an alignment control in the first place.

## 4. W3's null: alignment is a weak index, not the driver

**Spearman(alignment, excess) = +0.297 over ten cells** — positive, below the +0.5 bar, far above the falsifier's
zero. The two extremes show why: the **highest penalty in the ten (0.10067)** sits at alignment 0.14179, and the
**highest alignment in the ten (0.23238, 4.18× chance)** carries a **low** penalty (0.04704). Alignment orders the
penalty weakly at best across drawings.

## 5. What this establishes, and what it leaves

**Established**: the alloy is a good instrument for *placing* alignment — 9 of 10 cells land inside the hole, where
the 22 swap cells reached only its floor — and a **poor** instrument for reading the penalty's dependence on anything,
because a single drawing moves the penalty by 3.34× within one fraction. Together with the previous fire's coverage
census (the widest alignment gap hides a *fall*, the second-widest a *tripling*), the conclusion is now measured from
two directions: **at the transitional scale the penalty is drawing-dominated, and neither the construction parameter
nor the measured alignment predicts it.**

**The contrast that frames it**: the Erdős–Rényi family spans **1.05× across nine drawings**. So the *high* regime is
the most reproducible thing in this record and both transitional constructions are the least — 3.34× within a fraction
against 1.05× within ER.

**Left for the next design**: a within-band estimate needs many drawings per *narrow* alignment band (five per fraction
is what a 3.34× spread makes useless), and the interval that matters is `[0.23632, 0.27135]` — the only place where two
measured cells bracket a change of the size being studied. The registration's own limit stands: nothing here separates
alignment from `top_eig_share` and `effective_rank`, and those move across these ten cells too (0.167–0.819 and 1.50–24.28).
