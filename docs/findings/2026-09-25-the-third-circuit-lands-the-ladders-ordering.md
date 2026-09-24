# The third circuit lands the ladder's ordering: `pool2`, `pool4`, `pool8` as the circuit grows

**Date:** 2026-09-25
**Run:** `runs/e181_ladder_d300_12seeds.json` — the eight-rung `pool_below` ladder at **cs = 300** (d = 952), twelve
seeds, **analytic** (`e3_basis_selection --ladder`, no training). Registered before its run with a P1, a P2, a
falsifier and a null; its command was derived from `e79`'s config and verified field for field.
**Reads:** this circuit against `e73`'s `ladder_rows` (d = 1307) and `e83`'s `pool_ladder` (d = 1874) — the same
`delta` quantity at all three, which is what `e179`'s correction established.

---

## 1. The three-point ladder

`delta` = the biological partition's excess over the oracle **minus** its matched random control's, so **negative
means the biological grouping wins** and smaller is better. All three columns are the same quantity at the same
twelve seeds:

| rung | d = **952** (cs = 300) | σ | d = 1307 | d = 1874 |
|---|---|---|---|---|
| `pool1` | +0.000070 | **0.04** | +0.000191 | +0.000353 |
| **`pool2`** | **−0.007966** | **−15.29** | −0.008007 | −0.005859 |
| **`pool4`** | −0.001690 | −11.64 | **−0.008844** ← min | −0.007218 |
| **`pool8`** | −0.002737 | −10.11 | −0.006852 | **−0.007763** ← min |
| `pool16` | −0.003283 | −10.50 | −0.007651 | −0.005898 |
| `pool32` | −0.000930 | −5.19 | −0.006986 | −0.005014 |
| `pool64` | **degenerate** | — | −0.005485 | −0.004068 |
| `pool128` | **degenerate** | — | −0.004094 | −0.004801 |

**The minimum is at `pool2` on d = 952, `pool4` on d = 1307 and `pool8` on d = 1874** — three points, monotone in
the circuit's size, and each one's plateau is a **single rung** within 2 sem.

**So P1 holds** (the optimum is finer than `pool4`: it is `pool2`), **P2 holds** (monotone in size, against the
alternative that the optimum is set by the annotation vocabulary — which is fixed across the three circuits and
would predict a constant rung), **the falsifier does not fire** (the minimum is not at `pool8` or coarser), and the
registered null does not apply (no circuit's ladder is flat across more than two rungs).

## 2. What the three points do and do not say

**They say the direction is real and three for three.** The mechanism — `pool_below` is an **absolute neuron
count**, so a fixed threshold merges *fewer* labels as the circuit grows — predicts exactly this ordering, and the
vocabulary alternative predicts no ordering at all.

**They do not say the exponent.** `pool_below`'s grid is **powers of two**, so the three optima can only land on
1, 2, 4, 8, …: **the observed 2× steps are the grid's resolution and not the mechanism's**. A size ratio of 1.37×
and one of 1.43× both produced a doubling, which is what a grid this coarse will show for any true shift between
one and two doublings. **The ordering is a measurement; the ratio is a resolution limit** — rule 43's discipline
applied to a rung index rather than to a statistic.

**And the coarse end on the smallest circuit is degenerate, which is new.** At cs = 300 the `pool64` and `pool128`
rungs have so few groups (300 neurons pooled below 64 leaves about two) that the biological partition and its
capacity-matched **random** control are the *same object*, so `delta` is 0 by construction and the two rungs carry
no contrast. At cs = 800 those rungs still carry one (−0.005485, −0.004094). **So the ladder's usable range shrinks
with the circuit**: the coarse rungs stop being rungs.

## 3. The actual cost, beside the estimate (rule 49's first use)

`e181`'s `timing.total_s` is **2653 s = 44 minutes**, against a registration that said *"minutes"* by scaling
`e79`'s 8305 s at cs = 1500 down by the circuit. **The cost fell by 3.1× when the circuit fell by 5×** — so the
analytic line's cost does not scale with the circuit as the estimate assumed, and `e79`'s `timing` block holds a
single total with nothing to decompose, so the scaling had no support. The row now carries both numbers.

## 4. What this cannot settle

- **Three circuits, one family, one estimator.** All three columns are the *matched-control* `delta` at twelve
  seeds with `--q 0.02` and `support` at 10% of the circuit; §4.3's oracle-distance quantity is a different one and
  `e179`'s correction is the standing example of what happens when the two are compared.
- **The rung index is the resolution** (§2), so "the optimum tracks the size" is established as an *order* over
  three points and not as a relation between two continuous quantities.
- **`pool1` is unresolved at 0.04σ on the smallest circuit** — the unpooled end is the *same object* as its control
  there for the same reason the coarse end is at the other extreme, so the ladder's contrast lives in its middle.
- **The three optima are also the three *numbers of groups* the annotation vocabulary yields** at those circuits,
  so "size" and "vocabulary" are not separated by this design: what is ruled out is the vocabulary predicting a
  *constant* rung, which it does not.
