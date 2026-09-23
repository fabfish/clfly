# The interference term does not order the forgetting, and it inherits the failure of the two before it

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py`, four runs; artifacts `runs/e108_interference_r{0,128,32}.json`
and `runs/e108_interference_r32_frozen.json`.
**Artifacts:** the four above.
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, 5 replicates, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, read-out 0 / 128 / 32.
**Pre-registration:** `docs/findings/2026-09-23-the-interference-term-preregistered.md`, committed before
the runs finished.
**Context:** `docs/findings/2026-09-23-the-bodys-drift-is-monotone-and-forgetting-is-not.md`, which
measured the body's displacement and the load-bearing gap as **both monotone in the read-out and neither
ordering the forgetting**, and named the first-order interference of the two as the surviving candidate.

---

## 1. The measurement

The one-line form of the interference account — the change in a task's loss caused by moving the body
along a displacement, to first order — is `damage(j) = <grad_j(theta_final), theta_final - theta_after_j>`,
with `grad_j` the gradient of task *j*'s own training loss at the **final** body. The two factors are
stored beside the product (`grad_norm`, `disp_norm`, `cosine`), because a term that ordered the forgetting
could have been doing so through either of them, and the pre-registration said the factors would have to be
told apart rather than inferred.

## 2. The result: the falsifier fires on both predictions, and the reason is structural


Written after the four runs finished. **The control passes exactly first**: the frozen body gives
`first_order = 0.0` for both tasks with a defined cosine, so nothing below is read off a broken instrument.

| read-out | forgetting per task | **first-order term per task** | cumulative cosine | grad norm | disp norm |
|---|---|---|---|---|---|
| **0** | +0.0833 / +0.0125 | **−1.727e-02 / +3.058e-03** | +0.003 / +0.013 | 0.313 / 0.082 | 7.43 / 5.39 |
| **128** | +0.0583 / +0.0083 | **+3.246e-02 / +4.137e-02** | +0.015 / +0.035 | 0.166 / 0.119 | 14.39 / 9.91 |
| **32** | +0.0833 / +0.0625 | **+1.636e-01 / +1.503e-01** | +0.036 / +0.048 | 0.277 / 0.271 | 18.41 / 13.27 |

**P1 fails at two of three read-outs.** At read-out **0** the term for task 0 is **negative** while task 0's
forgetting is the **largest** of the two, and at **128** task 1's term is the larger while task 0 forgets *more*
(+0.0583 against +0.0083). Only at read-out 32 does the ordering match.

**P2 fails under every aggregation.** The forgetting orders the read-outs **128 < 0 < 32**; the term orders them
**0 < 128 < 32**, whether it is averaged over tasks (−7.1e-03 / +3.7e-02 / +1.6e-01), taken at its maximum
(+3.1e-03 / +4.1e-02 / +1.6e-01), or made dimensionless by dividing by the task's own final loss
(+0.023 / +0.689 / +0.948). **No aggregation was found that matches, and the reason is not the choice of
aggregation.**

**The reason is structural, and it is the same reason the previous two candidates failed.** The first-order term
is **itself monotone in the read-out** — it rises with every step of narrowing, exactly as the body's
displacement does and exactly as the load-bearing gap does. **All three mechanistic quantities this project has
now measured are monotone in the read-out, and the forgetting is the only series that is not.** So the failure
is not a property of which quantity was chosen; the read-out axis makes every *mechanistic* quantity monotone,
and the ordering anomaly must come from something that is not a function of the read-out at all.

**And the term's own decomposition says where it gets its size.** The cumulative cosines are **+0.003 to +0.048**
— the displacement is nearly **orthogonal** to the earlier task's gradient at every read-out. So the account
predicts little interference *by direction*, while the term's size comes almost entirely from its two magnitude
factors (`grad_norm × disp_norm`), and both are read-out-axis quantities. **A quantity dominated by its magnitude
factors cannot order a per-task pattern**, which is what P1 needed it to do — and this is visible in the stored
factors rather than inferred, which is why the pre-registration stored them separately.

**One thing the account does get right, stated because it is not nothing:** the sign. Expected damage is
positive in **5 of the 6** task-level cases where the observed forgetting is positive, the exception being task 0
at read-out 0. So **the first-order account gets the sign right and the ordering wrong** — a more precise
statement than "it fails", and what a truncation error looks like when the displacement is not infinitesimal and
the loss is not quadratic.

**The pre-registered outcome is therefore the three-member negative, published as such**: network forgetting on
this substrate is not ordered by *how far the body moved*, by *how much the task needed it*, or by the
*first-order interference of the two* — and the third failure is explained by the third quantity inheriting the
read-out monotonicity of the first two. The next candidate must be a quantity that is **not** a function of the
read-out, which points at the **task-pair** structure — the per-task displacements `theta_k - theta_{k-1}` and
their alignment with each other, both of which are stored and neither of which has been looked at yet — rather
than at any further aggregate over the read-out axis.

## 3. What this cannot settle

- **Three tasks and three read-outs.** Two forgetting values per configuration and one ordering across three
  read-outs: a failure is conclusive and a success would have been a correlation on a small grid.
- **First order only.** A large term that does not match the forgetting falsifies the *account as tested*
  rather than refuting it: the loss is not quadratic and the displacement is not infinitesimal, so the
  truncation is a live alternative explanation for a mismatch.
- **It says nothing about the frozen arm beyond the control**, which is what a control is for.
