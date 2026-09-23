# `e120`: four times the training does not reduce the spread, and the walk has already saturated

**Date:** 2026-09-24
**Script:** `experiments/e8_rate_network.py`, one run; artifact `runs/e120_r128_test480_2000iters.json`
(40 replicates, `--iters 2000 --test 480`, read-out 128).
**Artifacts:** the above plus `runs/e119_r128_test480.json` (the same configuration at 500 iterations).
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, `--seed0 0`, `--repeats 40`.
**Pre-registration:** `docs/findings/2026-09-24-four-times-the-training-preregistered.md`, committed before the
run.
**Context:** `docs/findings/2026-09-24-the-metric-noise-is-mostly-the-substrates.md`, which found that a tenfold
test set captures 94% of the removable noise and left the forgetting's per-repeat sd at 0.0221 **with 40% of its
variance in the training trajectory** — and asked whether that residual is under-convergence.

---

## 1. The result: P1 holds, the falsifier does not fire, and the residual is intrinsic

| run | forgetting | sem | **sd (per repeat)** | accuracy | **accuracy sd** | drift |
|---|---|---|---|---|---|---|
| **500 iters** | +0.0402 | 0.0035 | **0.0221** | 0.9215 | **0.0196** | 0.0395 |
| **2000 iters** | +0.0461 | 0.0048 | **0.0305** | 0.9276 | **0.0222** | 0.0460 |

**P1 holds: the accuracy's seed-to-seed sd does not fall — it rises slightly** (0.0196 → 0.0222, a factor of
0.88 against a predicted bound of 1.3). **So the substrate's run-to-run residual is not under-convergence**:
four times the compute does not make two seeds agree, and it does not make them nearly agree. **The seeds land
in genuinely different places**, and a longer walk in a different direction is still a different direction —
which is what the pre-registration predicted from the drift's 2.9% relative reproducibility.

**And P2's propagation held, including its direction**: the forgetting's sd rose with the accuracy's
(0.0221 → 0.0305), so the two move together through `√(2(1−ρ))` as the diagnostic said. Solving for the
correlation gives **ρ ≈ 0.14 at 500 iterations and ≈ 0.06 at 2000** — so longer training makes the two
accuracies *less* correlated across seeds, which is the same statement as the spread rising: more training gives
each seed more room to become itself.

## 2. And the walk has already saturated, which is independent evidence against "under-trained"

**C1 asked the drift to grow, and it grew by only 1.16× for four times the iterations** (0.0395 → 0.0460) —
against a prediction of *"roughly doubling or more"*, which was wrong. **The body is essentially done moving at
five hundred iterations**: four times the steps move it a sixth further, so the remaining training is not
travel. That refutes the premise of the convergence hypothesis by a second route, and it has a consequence for
an earlier result: **the drift series measured across read-out sizes (`e116`: 0.0191 → 0.0497) is a series of
*converged* distances**, so it is a clean property of the configuration rather than a snapshot of an interrupted
optimisation. The drift's relative reproducibility is also unchanged by the budget (2.92% → 2.66%).

**What four times the training buys**: **+0.0060 accuracy** (0.9215 → 0.9276) and **+0.0059 forgetting**
(+0.0402 → +0.0461), for four times the compute, and **no reduction in spread at all.** So *"train the benchmark
longer"* is not a route to precision either — the accuracy gain is smaller than one per-repeat sd of either
quantity, and the spread is unaffected.

## 3. What this settles, and it strengthens the paper's existing sentence rather than adding a new one

`§4.7` says *"the binding limit on this line is the benchmark's own per-repeat spread, not the replicate count"*.
That sentence now has a mechanism and has survived two attempts to remove its cause:

| route tried | what it removed | what remained |
|---|---|---|
| more replicates (40 per read-out) | the sem, by 40× | the per-repeat sd, unchanged |
| a tenfold test set | **94% of the removable evaluation noise** | 40% of the variance, in the training trajectory |
| **four times the training** | nothing | **the sd rises slightly** |

**So the limit is intrinsic to the connectome-constrained optimisation**: forty seeds of one configuration,
trained four times as long, still disagree about the forgetting by 0.0305 — **74% of the value they are
disagreeing about.** That is a statement about the *substrate*, measured three ways, and it is the sharpest form
this project's oldest network-line caveat has taken.

**Which closes the "improve the measurement" family of routes.** Both members have now been tried — the metric
(`e119`) and the training budget (this fire) — and the residue is not measurement. What is left is what the
pre-registration of `e119` named second: **a statement that does not need the metric to be ordered, which is
what the plateau already is.**

## 4. What this cannot settle

- **One read-out and one seed block.** Read-out 128 at test 480; whether the spread is equally irreducible at 32
  — where it is largest (0.0556 at forty replicates) — is not tested, and 32 is where a route would matter most.
- **Two iteration counts is a line, not a curve.** The drift's 1.16× for 4× says the budget is not the variable
  *at this scale*, which is the scale the benchmark uses; an 8000-iteration run would test whether anything
  changes far outside it, at four times this fire's cost.
- **It does not distinguish "multi-basin landscape" from "same basin, different direction".** Both produce a
  seed-dependent endpoint that more steps do not collapse, and separating them would need the loss along the
  interpolated path between two seeds' solutions — a different instrument, and the first one this sequence has
  proposed that is about the *geometry* rather than the noise.
