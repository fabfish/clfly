# `e108`, pre-registered: the interference term, against the two quantities that already failed

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py`, four runs; artifacts `runs/e108_interference_r{0,128,32}.json` and
`runs/e108_interference_r32_frozen.json`.
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, 5 replicates, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, read-out 0 / 128 / 32.
**Context:** `docs/findings/2026-09-23-the-bodys-drift-is-monotone-and-forgetting-is-not.md`, which measured the
body's displacement and the plastic-minus-frozen accuracy gap and found **both monotone in the read-out and
neither ordering the forgetting**. It named the surviving candidate as interaction-shaped — the overlap between
what a task changes and what an earlier task uses — and named measuring it as the next step. This is that
measurement, registered before its result; the result is in `2026-09-23-the-interference-term.md`.

---

## 1. What is being measured

The one-line form of the interference account: the change in a task's loss caused by moving the body along a
displacement, **to first order**,

    damage(j) = < grad_j(theta_final),  theta_final - theta_after_j >

with `grad_j` the gradient of task *j*'s own training loss at the **final** body, and the displacement being
what task *j* actually experienced — the cumulative motion from the end of task *j* to the end of training. The
per-task displacements `theta_k - theta_{k-1}` are stored too, so the term can be decomposed into which later
task did the damage, and `first_order_damage` records the **two factors separately**: `grad_norm`, `disp_norm`
and the `cosine` beside the product.

**That decomposition is not decoration.** `e107` showed the two quantities already tried — how far the body
moved, and how much the task needed it — are each monotone in the read-out, so a first-order term that *does*
order the forgetting could be doing so through either factor; the factors are stored so that this can be told
apart rather than inferred. And a term that does **not** order it cannot be rescued by either factor, which is
why the failure is the informative outcome.

**The control is built into the manipulation**, which is rule 26: a **frozen body cannot move**, so every
displacement is zero and every term must be **exactly `0.0`** with a defined cosine rather than a `0/0`. That is
the same control that validated `theta_drift`, and it is checked before anything below is read.

## 2. The predictions, and the falsifier, written before the runs finish

| | prediction |
|---|---|
| **P1, within a configuration** | the cumulative term is **larger for task 0 than for task 1** at every read-out, matching the forgetting's own ordering (+0.0833 against +0.0125 at the whole state, a 6.7× ratio) |
| **P2, across read-outs** | the cumulative term orders the three read-outs the way the forgetting does: **smallest at 128**, then 0, then largest at 32 |
| **Falsifier** | the term's ordering disagrees with the forgetting's in **either** comparison |

**Why P1 is the stronger test.** `e107` measured the drift as **near-constant across tasks within a
configuration** (spreads of 0.0014, 0.0056 and 0.0033) while the forgetting varies **sevenfold** across those
same tasks. So any quantity that orders the forgetting *within* a configuration must be doing it through the
gradient or the direction, not through the magnitude of the motion — there is almost no magnitude variation
left for it to use. If P1 holds while the drift is flat, the interference account has located the ordering in
the one place the previous two candidates could not reach.

**Why the falsifier is live.** Three quantities will then have been tested against the same non-monotone
series, and the previous two both failed. If this one fails too, the reportable result is not a missing
mechanism but a **negative one with three members**: network forgetting on this substrate is not ordered by how
far the body moved, by how much the task needed it, or by the first-order interference of the two. That is a
stronger statement than any single failure and it is the outcome this fire is prepared to publish.

---

**Registered, and then run.** This document is the prediction as it stood before the four runs finished — it is
committed in that state — and the result, including the falsifier firing on both predictions, is in
`docs/findings/2026-09-23-the-interference-term.md`.
