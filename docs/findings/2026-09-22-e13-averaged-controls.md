# E13 — the first ladder with averaged controls: the wiring works, three seeds are not enough for the paired column, and the coarse end collapses to the trivial basis

**Date:** 2026-09-22
**Script:** `experiments/e3_basis_selection.py --ladder --control-draws 3`
**Artifacts:** `runs/e13_control3_d952.json` (d = 952, support 30, 3 seeds, 3 control draws, oracle 0.02995)

---

## 1. What ran

The first full ladder in which the group-size-matched control is **averaged over 3 independent
draws** rather than drawn once — the change `clfly/bench/control.py` was written for, and the first
end-to-end exercise of the `--control-draws` path at ladder scale. Eight rungs, each with its own
averaged control, at d = 952 / support 30 / 3 seeds.

**The wiring works.** Every `rand:` rung reports `draws=3` and a finite `sd_across_draws`, the
`excess_per_seed` bookkeeping carries through to `paired_delta`, and the report renders both the
paired and unpaired columns. That was the purpose of the run.

## 2. The rung-level result replicates at a second configuration

| rung | delta | σ (3-seed protocol) |
|---|---|---|
| `pool1` | +0.00025 | 0.12 |
| `pool4` | −0.00131 | 6.04 |
| `pool8` | −0.00207 | 6.73 |
| `pool16` | −0.00231 | 9.06 |
| `pool32` | −0.00245 | 7.22 |
| `pool2` | −0.00346 | 18.29 |

Five of eight rungs resolve, at 6–18σ. This is a **second circuit** (d = 952 against the headline
1307) and a **second task-support size** (30 against 80), and the sign and rough ordering match:
biology beats its matched random control over the coarse range, and buys nothing at the finest rung
(`pool1` = `cell_type`, +0.00025 at 0.12σ — a third independent confirmation of that null). The
rung-level claim is the one that survived the control-draw correction, and it now has a replication
rather than only a re-analysis.

The effect sizes are smaller here (−0.0013 to −0.0035 against −0.005 to −0.009 at d = 1307), which
is expected: the circuit and the tasks differ, and the magnitudes were never claimed to transfer.

## 3. Three seeds are not enough for the paired column, and the report now says so where it matters

The `corr` column comes out at **exactly ±1.00** for `pool1`, `pool4` and `pool32`, and `sigma_p`
disagrees with `sigma` by up to **3×** (`pool4` 16.49 against 6.04; `pool32` 22.50 against 7.22).
Neither is a property of the substrate — both are properties of **n = 3**. Three points lie almost
on a line, so a sample correlation of ±1.00 is unremarkable; and the paired sem is estimated from
three differences, carrying a relative error of order ``1/sqrt(2(n-1))`` = 50%.

So **e13 supports no shape claim**, and the adjacent-rung contrasts in its report (1.8σ unpaired
against 21.0σ paired for `pool1 − pool2`) should not be quoted. This is the limit already written
into the draw-budget finding — the paired column needs the 12-seed runs — now demonstrated on real
data rather than asserted. The 12-seed `runs/e3_ladder_v2.json` is the run for that.

## 4. A degeneracy worse than the one already documented

At d = 952 the ladder's coarse end does not merely become blunt, it **collapses to the trivial
basis**:

| rung | groups | concentration | constrained | excess |
|---|---|---|---|---|
| `pool8` | 4 | 0.804 | 0.196 | +0.00124 |
| `pool16` | 3 | 0.819 | 0.181 | +0.00120 |
| `pool32` | 3 | 0.819 | 0.181 | +0.00120 |
| **`pool64`** | **1** | **1.000** | **0.000** | **+0.00000** |
| **`pool128`** | **1** | **1.000** | **0.000** | **+0.00000** |

A one-group "partition" is the ``Full`` basis, so EWC in it **is** the exact filter and the excess is
exactly zero. `pool64` and `pool128` are therefore not granularity rungs at all, and neither is
their control (permuting a single group returns the same single group). The ladder has six distinct
partitions at d = 952, not eight, and two of the six are trivial. At d = 1307 the same collapse stops
one step earlier (`pool128` is 2 groups, not 1).

That produced a small reporting bug worth recording because of what it claimed: with delta and sem
both exactly zero, the σ column printed ``inf`` — two rungs announced as **infinitely resolved**.
`_sigma` in `clfly/bench/analytic.py` now returns ``nan`` for 0/0, ``inf`` only for a nonzero effect
with a zero sem, and there is a regression test.

## 5. The concentration relation is monotone within a circuit but its *level* is circuit-dependent

Measured draw sds (K = 3 here, K = 4–5 for the d = 1307 points):

| concentration | d = 1307 | d = 952 |
|---|---|---|
| 0.006 / 0.020 | 3.9e-5 (n=2) | 9.8e-5 |
| 0.325 / 0.395 | 9.3e-4, 1.01e-3 | — |
| 0.678 / 0.690 | 1.06e-3 (n=2) | **4.94e-4** |
| 0.754 | 1.08e-3 | **8.40e-4** |
| 0.804 | — | 1.92e-3 |
| 0.819 | — | 1.35e-3 |

Inside each circuit the sd rises with concentration. **Between circuits it does not agree**: at a
concentration near 0.7 the d = 952 value is 4.9e-4 where d = 1307 gives 1.06e-3, a factor of two;
and at d = 952 the top of the range is non-monotone (0.804 → 1.92e-3 against 0.819 → 1.35e-3, a 42%
swing that three draws cannot resolve).

So the honest form of the mechanism claim is narrower than the previous finding stated:
**concentration ranks the draw sd within a circuit; it does not set its absolute value.** The
`side` prediction is unaffected — it interpolates on the d = 1307 curve, which is the circuit `side`
lives in — but the claim that the scalar "predicts the draw sd" needs its qualifier, and the
mechanism finding has been corrected.

## 6. Limits

- One alternative configuration (d = 952, support 30), one seed count (3), one control-draw count
  (3), one annotation column.
- The draw sds in §5 come from **three** draws, so each carries a ~40–50% relative error; the
  non-monotonicity at the coarse end is within that and is not called a finding.
- §3's conclusion is about *this* seed count. It says nothing against the paired machinery, which
  is exercised correctly here; it says that three seeds cannot estimate it.
- The degenerate rungs are excluded from the "5 of 8" count in the sense that they cannot resolve,
  but they remain in the denominator, so the fraction understates the resolving power of the
  informative rungs: it is **5 of 6 distinct partitions**.
