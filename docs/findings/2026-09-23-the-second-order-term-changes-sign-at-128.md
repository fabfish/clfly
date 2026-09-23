# The second-order term changes sign at the read-out that forgets least, and its ordering depends on how tasks are pooled

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py`, four runs; artifacts `runs/e109_second_order_r{0,128,32}.json` and
`runs/e109_second_order_r32_frozen.json`.
**Artifacts:** the four above.
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, 5 replicates, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, read-out 0 / 128 / 32.
**Pre-registration:** `docs/findings/2026-09-23-the-second-order-term-preregistered.md`, committed before the
runs finished.
**Context:** `docs/findings/2026-09-23-the-interference-term.md`, where the first-order term got the sign right
in 5 of 6 cases and the ordering wrong in both comparisons, and where all three previously measured quantities
were **monotone in the read-out** while the forgetting is not.

---

## 1. The instrument first, because its first form failed and its negatives needed adjudicating

**Controls.** The frozen body gives `quad = 0.0` and `curvature = 0.0` for both tasks, so the instrument's zero
is a zero. And the **finite-difference form is recorded as having failed its cross-check**: at identical weights
it returned `8.512e-01` at a step of `1e-3‖θ‖` and `1.709e-01` at `1e-2‖θ‖`, disagreeing with *itself* by 5×,
against an exact double backward of `3.027`. It is kept in the artifacts and not reported as a measurement.

**The negatives needed an independent implementation, and now have one.** `dᵀHd` computed by my double backward
is compared in `tests/test_network.py` against `torch.autograd.functional.hvp` on the same graph, and the two
agree to 1e-4 relative. **So the negative quadratic forms below are a property of the loss surface, not of the
code** — which matters because a negative curvature is exactly what a broken implementation would also produce,
and the finite-difference check could not adjudicate (it disagreed with itself by 5× and then by *sign*).

## 2. The result

| read-out | forgetting per task | **`quad` per task** | **curvature (Rayleigh quotient) per task** |
|---|---|---|---|
| **0** | +0.0833 / +0.0125 | **+2.985e-01 / −2.991e-03** | **+5.541e-03 / −7.396e-05** |
| **128** | +0.0583 / +0.0083 | **−5.427e-01 / −4.159e-02** | **−2.649e-03 / −3.871e-04** |
| **32** | +0.0833 / +0.0625 | **+1.015e+00 / +7.041e-01** | **+2.915e-03 / +4.025e-03** |

**P1 is refuted, and the refutation is the informative kind.** The prediction was structural — *a quadratic form
is positive by construction for a positive-semidefinite Hessian, so the first-order term's sign failure cannot
recur* — and it fails in **3 of the 6** task-level cases (read-out 0 task 1, and both tasks at read-out 128).
**That premise was an assumption about convexity, and this loss is not convex**: `H_j` is a cross-entropy
Hessian of a tanh recurrent net, and the measured negatives say the body moved into directions along which the
earlier task's loss **decreases** to second order. The sign argument that motivated the second-order term —
"a quadratic form cannot get the sign wrong" — is therefore **not available**, which is worth stating because it
was the stated reason for measuring this term at all.

**P2 is not confirmed, and it is aggregation-dependent.** With the curvature **averaged over tasks** the
read-outs order as **128 < 0 < 32** (+2.73e-3 at 0, −1.52e-3 at 128, +3.47e-3 at 32) — which **matches the
forgetting's ordering exactly**, the first agreement in this sequence. But taken at its **maximum over tasks**
the ordering is **128 < 32 < 0** (+5.54e-3, −3.87e-4, +4.03e-3), which **fails**. **One aggregation agreeing and
another failing is not a confirmation**, and the honest verdict is that this candidate is *unresolved* rather
than supported — the same standard applied to `e99`/`e100` earlier in this project, where a monotone-looking
reduction was read as a confirmation from point estimates inside their own error bars.

**P3 is refuted against my own expectation.** I predicted that `quad` would be **monotone in the read-out**, as
the displacement, the gap and the first-order term all are, and would therefore fail. Measured, it is **not
monotone**: it is **negative at read-out 128** (−2.92e-1 by the task-mean, against +1.48e-1 at 0 and
+8.59e-1 at 32). **So the second-order term is the first quantity in this sequence whose structure is
non-monotone in the read-out** — which is exactly what `e108` said the next candidate had to be, and I did not
expect this one to be it.

## 3. What survives every aggregation, and it is a hypothesis rather than a result

**Read-out 128 is the only read-out where the curvature is negative for *both* tasks**, and read-out 128 is the
read-out with the **least** forgetting (+0.0333 against +0.0479 and +0.0729). Every other read-out has at least
one positive curvature, and the sign pattern is otherwise mixed (read-out 0 has one of each).

That is a **qualitative** difference at the anomalous read-out, and it is the first qualitative difference anyone
has found there: the three previous candidates differed from each other only in magnitude along the same axis.
**But it is one read-out on the negative side of a sign**, so it is a hypothesis, and the test it implies is
cheap and specific: **a fourth read-out between 128 and 1307**, where the forgetting is not yet known, should
have negative curvature for both tasks if the pattern is real. That is the next step, and unlike the last four it
is a prediction that can fail cleanly.

## 4. What this cannot settle

- **`H_j` is taken at one point**, the final body — where the loss is being evaluated but not where the
  displacement happened. A curvature that changes along the path is approximated by its endpoint value.
- **Second order only.** With a truncation this size (cosines of +0.003 to +0.048 against forgetting of
  0.06–0.08) the third-order term is not bounded, so even a clean ordering at second order would not be a
  mechanism.
- **The aggregation question is not a technicality.** This fire's headline could be written two ways — "the
  second-order term orders the forgetting" (mean) or "the second-order term does not order the forgetting"
  (max) — and neither is the honest one. The honest one is that the choice of pooling was made after seeing
  both, which is a degree of freedom this project has a rule against, and the reason §3 states a *qualitative*
  claim instead of a quantitative one.
