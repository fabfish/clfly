# E29 — the third synapse rung, and a reporting degeneracy that made a zero look like a null

**Date:** 2026-09-22
**Script:** `experiments/e8_rate_network.py --basis ito_lee_hemilineage --lam 1.0`, and a report fix
**Artifacts:** `runs/e10_rung_ito_lee_hemilineage.json`

---

## 1. The third rung

| method | final accuracy | sem | mean forgetting | sem |
|---|---|---|---|---|
| naive | 0.8241 | 0.0359 | +0.1007 | 0.0486 |
| `ewc-block` (biological) | 0.8333 | 0.0244 | +0.0694 | 0.0352 |
| `ewc-block-rand` (matched control) | 0.8333 | 0.0145 | +0.0868 | 0.0347 |

Biological minus matched random: **+0.0000 accuracy**, −0.0174 forgetting (0.43σ). So the third of
five rungs is another null at λ = 1.0, on both metrics, and — like `side` and `cell_class` — it does
not beat the naive baseline on accuracy (0.8333 against 0.8241 is 0.25σ).

Three of five rungs now measured, all at λ = 1.0:

| rung | constrained | biological | matched random | Δ accuracy | σ paired |
|---|---|---|---|---|---|
| `side` | 0.6947 | 0.8148 | 0.8264 | −0.0116 | 0.43 |
| `cell_class` | 0.9250 | 0.8426 | 0.8611 | −0.0185 | 0.35 |
| `ito_lee_hemilineage` | 0.9945 | 0.8333 | 0.8333 | **+0.0000** | **degenerate** |

**The control is not vacuous**, which had to be checked given an identical accuracy to four
decimals: `random_matched` preserves every group's size and changes every group's membership
(verified directly), and the per-replicate values differ substantially. The agreement is in the
*means*.

## 2. The per-replicate deltas are large and their mean is exactly zero

```
accuracy   bio  0.7847  0.8542  0.8611        rand 0.8403  0.8056  0.8542
per-replicate delta  −0.0556  +0.0486  +0.0069     mean = 0.000000
```

So the run measured a mean difference of **0.0000 with a paired sem of 0.0305**, from three
replicates that disagree by up to 0.056. That is the honest number, and it is a *tight bound around
zero* — not evidence that nothing is there. §3 is about why the report said something else.

## 3. `σ = 0.00` is degenerate for a near-zero delta, and the report now says so

The report printed `delta +0.0000 ... paired 0.00 sigma`. A reader takes `0.00σ` to mean "no
evidence", but a σ of zero follows *from* the delta being zero — it is `|δ|/sem` with `δ ≈ 0` — and
it says nothing about how well the zero is measured. With sem 0.0305 the interval is ±0.03, which is
neither tight nor meaningless.

The fix is to print the sem next to σ and to say explicitly when the mean has fallen inside its own
sem:

```
final_accuracy  delta +0.0000 +- 0.0305 unpaired (0.00 sigma)  0.0305 paired (0.00 sigma)
                the mean is inside its own sem, so sigma is degenerate;
                the measurement is +0.0000 +- 0.0305
```

This is the same failure mode as three others in this project — a **statistic that is only
interpretable away from the value it was reported at**:

- a sign test on differences below the noise floor is a random draw;
- ``K`` in a draw budget is infinite when the seed budget binds, and a large number otherwise;
- and now σ of a zero delta is zero however uncertain the zero is.

Each is a ratio or a threshold whose denominator or reference point vanishes exactly where a reader
most wants an answer. The general remedy is to print the **interval** and let σ be a secondary
readout.

## 4. Where the network line's rung evidence now stands

The rung question — *would a different granularity have shown the effect the neuron line found?* —
has three of five rungs at λ = 1.0, all nulls with intervals of roughly ±0.03 accuracy. Two facts
about that:

- **λ = 1.0 is the λ at which the `cell_class` contrast is *smallest*** (−0.0185, 0.35σ) against
  −0.0648 at λ = 0.1, so the rungs have so far been sampled where the effect is weakest. `e28` is
  measuring `side` at λ = 0.1, which puts the coarsest rung at the λ where the effect is largest.
- The **intervals** are the binding constraint: ±0.03 accuracy against a neuron-level effect of
  ~0.005 excess (about 10% of the oracle gap). A network effect of that relative size would be
  invisible here, and `2026-09-22-e10-side-rung-underpowered.md` already priced the repeats needed.

## 5. Limits

- Three replicates per rung; the per-replicate deltas span ±0.056, so each rung's interval is
  estimated from three numbers.
- The degenerate-σ guard triggers on `|δ| < sem`, which is the right condition for the *warning*
  but not a statement about the measurement's quality — a delta of 0.001 with sem 0.030 would also
  trigger it and would be a good measurement of ~zero.
- Nothing here is about the granularity *axis*: the three rungs are three λ = 1.0 points, and the
  comparison between them (at one λ) has not been made.
