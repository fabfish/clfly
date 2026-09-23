# `e109`, pre-registered: the second-order term, and the first candidate that is not a magnitude

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py`, four runs; artifacts `runs/e109_second_order_r{0,128,32}.json` and
`runs/e109_second_order_r32_frozen.json` (in flight).
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, 5 replicates, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, read-out 0 / 128 / 32.
**Context:** `docs/findings/2026-09-23-the-interference-term.md`, where the **first-order** term got the sign
right in 5 of 6 cases and the ordering wrong in both comparisons, and where the reason was structural: the
displacement, the load-bearing gap and the first-order term are **all monotone in the read-out**, so all three
are dominated by one axis while the forgetting is not. That finding named the next candidate as one that is
**not a function of the read-out**.

---

## 1. What is being measured, and why it is the natural next term

The second-order term of the same account: `½ Δθᵀ H_j Δθ`, with `H_j` task *j*'s Hessian at the final body and
`Δθ` the displacement task *j* actually experienced. Two things make it the natural successor rather than
another guess:

1. **A quadratic form is positive by construction** for a positive-semidefinite Hessian, so it **cannot get the
   sign wrong** — and the first-order term's sign failure (negative for the task that forgot *most*, at
   read-out 0) is exactly the failure a second-order term fixes for free.
2. **The first-order term's cosines are +0.003 to +0.048** — the displacement is nearly *orthogonal* to the
   task's gradient — while the task forgets 0.06–0.08 of accuracy. For a nearly-orthogonal displacement the
   first-order change is small **by construction**, and what is left is the second order. `e108` measured the
   small number and the substantial forgetting side by side.

**Two quantities are recorded, and they answer different questions.** `quad = ΔθᵀHΔθ` is linear in the
directional curvature and **quadratic in the displacement**, so it inherits the read-out monotonicity of every
magnitude in this line. The **Rayleigh quotient `quad / ‖Δθ‖²` divides the magnitude out** and is therefore a
property of the **direction** — the first candidate in this sequence that is not a magnitude, and the form
`e108` said the next candidate had to take.

## 2. The instrument, and a cross-check that already failed once

The first version of `directional_curvature` was a **central finite difference** of the gradient along Δθ, and on
a one-replicate smoke run at read-out 32 it was **not converged**: at identical weights it returned
`quad = 8.512e-01` at a step of `1e-3‖θ‖` and `1.709e-01` at `1e-2‖θ‖` — the two steps disagree with **each
other** by 5×. It is therefore replaced by an **exact double backward**
(`autograd.grad` of `gradient·Δθ` with respect to θ), which on the same weights gives `quad = 3.027`, so the
finite difference was **3.6× low at the finer step and 18× low at the coarser**. The likely cause is
nameable: a central difference differences two float32 gradient vectors of ~26,568 components each of order
1e-3, and the difference over a step this small is at the resolution limit.

**Both are still computed and stored**, because a value with a failed cross-check is worth recording as such
rather than replacing silently. **The smoke run is an instrument validation, not a peek at the hypothesis**: its
purpose was to check that the curvature can be measured at all, it found that the finite-difference form cannot,
and it says nothing about the ordering across read-outs that the predictions below are about.

## 3. The predictions, and the falsifier, written before the four runs finish

| | prediction |
|---|---|
| **P1, structural** | the exact `quad` is **positive for both tasks at every read-out** — a positive-semidefinite Hessian admits no other sign, so the first-order term's sign failure cannot recur. If it is negative anywhere, the Hessian is not PSD at that point and **that** is the finding |
| **P2, the new candidate** | the **Rayleigh quotient `curvature`** orders the three read-outs the way the forgetting does: **smallest at 128**, then 0, then largest at 32 |
| **P3, expected to fail** | `quad` **itself** is monotone in the read-out, because it is quadratic in a magnitude that `e107` measured as monotone — so it will order the read-outs as the first-order term did (0 < 128 < 32) and **fail** P2's ordering |
| **Falsifier for P2** | `curvature` is itself monotone in the read-out, or non-monotone in the wrong order |

**P3 is stated as an expectation rather than a hope, and that is the point of writing it down.** After three
monotone candidates it is the inference the evidence supports, and stating it in advance is what stops a fourth
monotone failure from being read as "another miss" rather than as the pattern it is: **the read-out axis makes
every magnitude monotone, so the only candidates left are direction quantities.** P2 is the first of those, and
it is the one this fire is actually about.

## 4. What this cannot settle

- **Three tasks and three read-outs.** Two forgetting values per configuration and one ordering across three
  read-outs, so a failure is conclusive and a success would be a correlation on a small grid.
- **Curvature at one point.** `H_j` is taken at the **final** body, which is where the task's loss is being
  evaluated but not where the displacement happened; a curvature that changes along the path is approximated by
  its endpoint value.
- **Second order only, and the truncation is not bounded** — a larger third-order contribution would make a
  second-order success coincidental.
