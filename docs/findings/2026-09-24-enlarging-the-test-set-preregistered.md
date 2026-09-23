# `e119`, pre-registered: enlarging the test set, to see whether the metric's handicap is removable

**Date:** 2026-09-24
**Script:** `experiments/e8_rate_network.py`, two runs; artifacts `runs/e119_r128_test480.json`,
`runs/e119_r300_test480.json` (in flight).
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, `--seed0 0`, **`--repeats 40 --test 480`** at read-out 128 and
at read-out 300 (a tenfold test set, against the 48 of every run so far).
**Context:** `docs/findings/2026-09-24-the-metric-is-thirty-times-noisier.md`, which measured the forgetting to
**74–134% of its own value** across forty replicates while the drift is measured to **2.6–3.5%** — a thirtyfold
relative handicap — and named two routes out: **a metric with a better SNR**, or a statement that does not need
the metric ordered.

---

## 1. Why this is a causal test and not a fishing trip

The handicap is not a property of the physics, and the runner says so in its own payload. Each artifact carries
an `evaluation_noise` block that splits a method's per-replicate spread into the part attributable to the
**test set** and the residual:

| read-out | replicate sd (accuracy) | **binomial component** | residual | removable share of the variance |
|---|---|---|---|---|
| 1307 | 0.03199 | 0.01999 | 0.02498 | 39% |
| **128** | 0.02283 | **0.02109** | 0.00876 | **85%** |
| 32 | 0.03505 | 0.02355 | 0.02596 | 45% |

**At read-out 128, 85% of the accuracy spread is the test set's binomial noise** — and `evaluation_noise`'s own
docstring records that this is *"cheap to reduce and easy to forget"*, and removable *"by asking for a bigger
test set, which costs almost nothing next to training"*. Read-outs 1307 and 32 have much smaller removable
shares (39% and 45%), which is why **this fire runs 128 and 300** — the two points whose comparison is the axis's
one resolved step, and 128 is where the removable share is largest.

## 2. The design, and the arithmetic of the predicted effect

A tenfold test set divides the binomial component by √10 = 3.16 while leaving the residual — the training
trajectory's own variation — untouched. Carrying the 85% split over to the **forgetting** (which is a difference
of accuracies and so may have a *larger* evaluation share, not a smaller one):

    forgetting sd now      0.0325  = sqrt(0.85·0.0325² + 0.15·0.0325²)   -> 0.02996 evaluation, 0.01259 residual
    forgetting sd at 480   = sqrt((0.02996/3.16)² + 0.01259²)           -> 0.01575

**So the predicted fall is from 0.0325 to ≈0.0157 — a factor of 2.1**, and the bounds are 1.0× (if the forgetting's
variation is entirely training-trajectory) and 3.16× (if entirely evaluation).

## 3. The predictions, and the falsifier, written before the runs finish

| | prediction |
|---|---|
| **P1** | the per-repeat forgetting sd at read-out 128 **falls**, by a factor of **1.5× to 3.2×** (predicted ≈2.1×) |
| **P2** | the **mean** forgetting at read-out 128 is **unchanged** within one sem of the new, smaller sem — a bigger test set changes the noise, not the physics |
| **P3, the deliverable** | with the better metric the **plateau-to-128 step's σ roughly doubles** (from 2.1–2.4σ) — and if the plateau's *internal* differences were real but buried in evaluation noise, they should now appear |
| **Falsifier** | the sd **does not fall** (a factor below 1.5). The noise is then training-trajectory variation rather than evaluation noise, **no test-set enlargement can remove it**, and the metric's thirtyfold handicap is a *physical* limit — leaving more tasks or more replicates as the only routes, and the plateau as the final word on the axis |

**The falsifier is the interesting outcome**, which is why it is stated as a *bound* rather than as a hope. A
metric whose noise survives a tenfold test set is a metric whose noise is the *substrate's* — and that would be a
finding about the connectome-constrained benchmark rather than about the estimator, contradicting the
expectation that `evaluation_noise`'s docstring records and that this fire is the first to test at forty
replicates.

**Two read-outs, not one, because P3 needs a comparison**: a fall in 128's sd only shows the metric can improve;
whether the *step* sharpens needs the plateau's side measured at the same test size.

## 4. What this cannot settle

- **It does not make the metric as precise as the drift.** Even a 3.16× fall leaves a relative spread of ~30%,
  against the drift's 3% — the handicap narrows from thirtyfold to tenfold, and the sequence's central negative
  result (mechanical quantities cannot order this metric) would be *weakened* rather than removed.
- **A tenfold test set is one choice.** The cost is linear in `--test`, and if the fall lands inside the
  predicted band the natural next step is to price a further enlargement rather than to take it.
- **It says nothing about the training-trajectory residual**, which is the part the substrate owns; if the
  residual is 0.0126 as the split suggests, that is the floor a metric can be brought to at this replicate count,
  and it is 39% of the current spread.
