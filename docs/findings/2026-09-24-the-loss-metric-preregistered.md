# `e123` pre-registered: report the retention matrix in loss, and measure what it buys against the accuracy metric

**Date:** 2026-09-24
**Status:** pre-registered **before** the runs. Committed as its own commit; the run is launched after it.
**Script:** `experiments/e8_rate_network.py`, unchanged apart from `retention_loss`, which `e122` added.
**Planned artifacts:** `runs/e123_r128_test480.json` and `runs/e123_r300_test480.json`,
`--repeats 40 --iters 500 --test 480 --readout-size {128, 300}`, the rest at the house defaults
(`--circuit-size 800 --lr 3e-3 --batch 32 --lam 3e-3 --train 96 --noise 1.0 --classes 4 --shared-head
--input-overlap 0.0 --methods naive --seed0 0`).
**Reference artifact:** `runs/e119_r128_test480.json` — read-out 128, the same configuration, **bit-identical
training expected** (see C0).
**Context:** `docs/findings/2026-09-24-the-seeds-solutions-are-connected.md` §4 and
`docs/findings/2026-09-24-the-metric-is-thirty-times-noisier.md`. `e118` measured the reported metric's
relative precision at **74–134% of its own value** against the drift's 2.6–3.5% — a **thirty-fold** handicap —
and named the estimator: the forgetting is a difference of accuracies over a held-out set with **granularity
1/240**, while the drift is a norm over 26,568 numbers. `e119` then removed 94% of the *removable* evaluation
noise with a tenfold test set, leaving 40% of the variance in the training trajectory, so the handicap narrowed
to eighteenfold and **the rest is not noise to be removed but a floor under the estimator**.

## The quantity, defined by mirroring the accuracy form rather than inventing one

`retention_loss[k][j]` is the full-train-set loss (mean cross-entropy over the task's 96 training samples) on
task `j` at checkpoint `k`. The accuracy forgetting is

    F_acc(j) = max_{k in [j, T-1]} R[k][j]  -  R[T-1][j]

and the loss forgetting is **the same expression with the roles of the two directions swapped**, because loss
falls where accuracy rises:

    F_loss(j) = L[T-1][j]  -  min_{k in [j, T-1]} L[k][j]          (nats)

`min` includes `k = T-1`, so `F_loss >= 0` by construction exactly as `F_acc >= 0` is. The reported metric is
`mean_{j < T-1} F_loss(j)`, nats, over the three-task suite. A scale-free companion is registered beside it —
`mean_j log(L[T-1][j] / min_k L[k][j])` — **and it is the companion and not the metric**, because its
denominator is the just-fitted loss (~0.0018) where the fit is tightest and a relative error there is inflated.

**Nothing here is compared across runs.** Both metrics come out of the **same 40 replicates** of the same run,
so the comparison is paired and no draw, seed or environment term can enter it — which is the whole reason this
is worth running rather than argued.

## The predictions

- **C0, the extension control, and it is exact.** The per-repeat, per-task `mean_forgetting` of
  `runs/e123_r128_test480.json` must be **bit-identical** to `runs/e119_r128_test480.json`'s 40 replicates.
  Adding `retention_loss` changes what is *recorded* and not what is *trained*: the extra `full_split_loss`
  calls evaluate under `torch.no_grad()`, step no optimiser and **draw no random number**, so the training RNG
  streams are untouched. **If this fails, the instrumentation perturbed the run**, every number below is a
  cross-run comparison and the fire is void — which is why it is checked first and reported first.
- **P1, directed.** The per-repeat sd of `mean_forgetting_loss` is **smaller** than the per-repeat sd of
  `mean_forgetting`, at **both** read-outs: `sd_loss / sd_acc < 1`.
- **P2, the scale.** That ratio is **below 0.71** (a factor of √2 or better) at both read-outs. This is the
  claim worth registering, because `e118` attributes the accuracy metric's handicap to *granularity*, and a
  continuous quantity has none: if the diagnosis is right the loss should be several times better, not a few
  percent.
- **P3, the level, and it must be stated because it is the trap.** `mean_forgetting_loss` is **not** predicted
  to equal `mean_forgetting` in any units — nats and accuracy are different scales and no calibration between
  them is meaningful. The registered claim is about the **precision of each quantity against itself**, never
  about agreement between them. A fire that reads a disagreement as a failure has misread its own registration.
- **Falsifier.** `sd_loss / sd_acc >= 1` at **either** read-out. Then the loss-valued retention matrix is not
  an improvement, the accuracy metric's floor is not its estimator's granularity, and `e118`'s diagnosis is
  incomplete — which is a result and would be reported as one.

## Why the paired form, and what it cannot settle

**Why paired:** `e114` found that pairing is structurally blind when the confound is fixed within a run (its
paired σ was optimistic by exactly the draw's contribution). Here that blindness is the *point*: the draw, the
seed block and the circuit are identical by construction, and the only thing that differs between the two
numbers is the estimator. **The failure mode to guard against is the opposite one** — that both quantities are
computed from the same forward passes and therefore share their noise, so a shared component would make the
loss look better than it is. The falsifier is symmetric enough to catch that: shared noise cannot push the ratio
below 1 by itself unless the loss's *own* component is genuinely smaller.

**Cannot settle:** one circuit, three tasks, one draw per read-out, so the ratio is a property of this benchmark
rather than a law about loss and accuracy; the loss is measured on the **training** split, whose 96 samples are
the ones the model interpolates, so its own sampling floor is not something a bigger test set can remove and the
ratio is not a decomposition into components the way `e119`'s was; and it says nothing about whether a
loss-valued *retention* metric is what a continual-learning reader would want to see, only about its precision.
