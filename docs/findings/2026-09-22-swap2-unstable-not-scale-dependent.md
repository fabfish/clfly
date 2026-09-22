# E26 — `swap2`'s excess alternates in sign across four circuit sizes while its controls hold to 6%: the C1 refutation is a statement about one graph

**Date:** 2026-09-22
**Script:** `experiments/e2_topology_gap.py --circuit-size {300,400,500,800} --seeds {3,6} --no-realized`
**Artifacts:** `runs/e21_e2_paired.json`, `runs/e26_size400.json`, `runs/e26_size500.json`, `runs/e2_analytic.json`

---

## 1. Four points

| topology | d = 952 | d = 1010 | d = 1086 | d = 1307 | spread |
|---|---|---|---|---|---|
| `real` | +0.01902 | +0.01822 | +0.01934 | +0.01830 | **6.2%** |
| `swap0.5` | +0.02257 | +0.02065 | +0.02438 | +0.02317 | 18.0% |
| **`swap2`** | **+0.05782** | **+0.01762** | **+0.03492** | **+0.01237** | **367%** |

And the contrast that carries C1's interference refutation:

| `swap0.5 → swap2` | d = 952 | d = 1010 | d = 1086 | d = 1307 |
|---|---|---|---|---|
| Δ excess | **+0.03525** | **−0.00304** | **+0.01054** | **−0.01079** |
| significance | 21.8σ paired | 4.8σ paired | 14.5σ paired | 32.7σ unpaired |

**The sign alternates: +, −, +, −** — and every one of the four is decisive, the weakest at 4.8σ.
`swap2`'s excess does not trend with circuit size; it oscillates by a factor of ~3 between
*adjacent* sizes, while `real` holds to 6.2% and `swap0.5` to 18%.

## 2. Against the pre-registered prediction

The prediction written before the sweep had three branches; the result is unambiguously the second:

> **"If `swap2` is an unstable object rather than a scale-dependent one: its excess jumps between
> neighbouring sizes by more than the monotone trend allows — e.g. 0.058, 0.013, 0.050 at consecutive
> `d` — which no smooth function of the circuit can produce."**

The observed sequence is 0.058, 0.018, 0.035, 0.012 — the same shape as the example written down in
advance. The third branch ("`swap2` moves monotonically while `real`/`swap0.5` do not") is excluded,
and so is the first.

## 3. What this means for C1

**The refutation is a statement about one graph.** It rests on `excess(swap2) − excess(swap0.5)`,
computed at d = 1307, where that quantity is −0.01079. At three other circuit sizes drawn from the
same connectome the same quantity is +0.03525, −0.00304 and +0.01054 — different signs, each
resolved.

That is stronger than the previous fire's "configuration-specific": a *systematic* dependence on
circuit size would have left the refutation meaningful within a range of sizes. An **alternating**
sign with decisive resolution at every step means the statistic is dominated by which realization of
the swap rule you drew, and the swap family at this perturbation strength does not define a stable
quantity to reason about.

Which also means the previous fire's conclusion — *"at d = 952 heavy rewiring makes the penalty
worse, which is what the interference hypothesis predicts"* — is itself one draw from that unstable
statistic and should not be read as support for interference either. **Neither direction survives.**

## 4. The confound I cannot yet remove, and the experiment that would

The sweep varies **two** things at once: the circuit subsample (different `--circuit-size`) and the
specific swap realization, because `apply_null(W0, topology, rng)` draws its swaps from a stream
seeded by `seed0` applied to a different `W0` at each size. So "alternates with size" and "alternates
with realization" are not distinguishable from these four points.

**That is separable, and cheaply.** Fix the size, fix the task seeds, and vary only the swap stream:
six realizations of `swap2` at d = 1307, five minutes each. If the excess spreads over 0.012–0.058
there, the conclusion is that `excess(swap2)` is not a reproducible statistic and the whole swap
family needs re-deriving; if it is tight there, the variation is genuinely about the circuit and the
picture changes again. The second is the informative outcome and the first is the more likely one.

`e2_topology_gap.py` needs a `--rewire-seed` argument for this, since `seed0` currently drives the
tasks and the rewiring together.

## 5. Limits

- **Different seed counts per point** (3 at d = 952, 6 at the two new sizes, 3 at d = 1307), so the
  sems are not comparable. The means are precise enough that this does not affect the conclusion:
  the adjacent-point differences are 4.8–14.5σ.
- The two new points use `--no-realized`, so only the analytic arm exists for them — which is the arm
  every conclusion in this line is drawn from.
- Four points is enough to exclude monotonicity and not enough to characterise the distribution of
  `excess(swap2)`. §4's realization sweep is what would.
- `swap0.5`'s 18% spread is larger than `real`'s 6.2% but still an order of magnitude below `swap2`'s,
  so the instability is specific to the strongest rewiring and not a general property of the family.
