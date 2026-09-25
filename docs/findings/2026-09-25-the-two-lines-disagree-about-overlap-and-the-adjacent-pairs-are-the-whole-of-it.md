# The two lines disagree about overlap, and the disagreement is exactly the adjacent pairs

**Date:** 2026-09-25
**Read of:** `runs/e7_interference.json`'s `controlled` block (the analytic line's six overlap levels) and the same
nine matched pairs `e188` admitted, split by task distance from their own retention matrices.
**Instrument:** `experiments/e189_overlap_sign_across_lines.py`, tested in
`tests/test_e189_overlap_sign_across_lines.py`.
**§3's far-component correction is itself corrected by `e191`**: this file read the network line's
**accuracy drop**, whose standard errors are large, and refused to call the far component resolved. The
network line also records an **interference decomposition per pair**
(`methods.<m>.replicates[r].interference[j]["per_task"][k]`), and on that quantity -- the one that shares a
name with the analytic line's -- the far component rises at 2σ in **nine of nine** admitted comparisons
(2.1σ to 7.4σ). So the composition this file's *first* version printed and its second version refused is the
right one, and the refusal was a property of the proxy rather than of the data. See
`docs/findings/2026-09-25-the-composition-survives-the-quantity-the-proxy-could-not-see.md`. The admitted pairs and their inert-field rules are **imported from
`e188`**, so the two audits cannot drift apart about which payloads are evidence.

---

## 1. Two results about the same axis, pointing opposite ways, both already in the repository

- **`e188` (a network read, an hour before this)**: raising the input overlap from 0 to 1 **raises** forgetting,
  nine matched comparisons, nine positive, eight resolved at 2σ.
- **`e7` (the analytic line, 2026-09-22)**: raising the input overlap **lowers** interference, over six levels,
  perfectly monotone — `Spearman(overlap, mean interference) = −1.000`, which its finding records as the refutation
  of C4's direction.

Nothing had put the two side by side, and each finding's own language ("raises", "reduces") is true of its own
line. The question this fire asks is whether the disagreement is a sign flip of one quantity or something with
structure inside it. **It has structure, and the structure is the finding.**

## 2. The split, which both lines can make

Both quantities decompose by **task distance**: the analytic block reports `mean_interference_near` (adjacent
pairs) and `mean_interference_far` (distant pairs) per level, and a network retention matrix gives the same split
because a three-task sequence realises exactly three ordered pairs — (1→0) and (2→1) adjacent, (2→0) distant — each
costing `R[k-1, j] − R[k, j]`, paired over replicates.

**The analytic line (`e7`'s controlled sweep, 5 tasks, 3 seeds, support 80):**

| overlap level | achieved | mean | **near (d = 1)** | **far (d > 1)** |
|---|---|---|---|---|
| 0.00 | 0.000 | +0.015347 | **+0.025751** | +0.008411 |
| 0.10 | 0.053 | +0.013057 | +0.022033 | +0.007073 |
| 0.25 | 0.143 | +0.010680 | +0.014882 | +0.007879 |
| 0.50 | 0.333 | +0.007330 | +0.005050 | +0.008850 |
| 0.75 | 0.600 | +0.006812 | +0.002334 | +0.009798 |
| 1.00 | 1.000 | +0.006111 | **−0.001327** | **+0.011069** |

Near **falls monotonically and crosses below zero**; far **rises by a third**. The aggregate falls because the near
component dominates it.

**The network line (the same nine comparisons, split the same way):**

| comparison | near 0 | near 1 | far 0 | far 1 |
|---|---|---|---|---|
| naive, disjoint vs identical inputs | +0.0557 | **+0.0833** | +0.0385 | +0.0469 |
| naive, second overlap-0 arm | +0.0557 | **+0.0833** | +0.0385 | +0.0469 |
| naive, third overlap-0 arm | +0.0557 | **+0.0833** | +0.0385 | +0.0469 |
| ewc-block (biological side partition) | +0.0401 | **+0.0646** | +0.0344 | +0.0375 |
| replay | −0.0052 | **+0.0052** | +0.0036 | +0.0062 |
| ewc-block-rand, draw 1 | +0.0404 | **+0.0792** | +0.0375 | +0.0437 |
| ewc-block-rand, draw 2 | +0.0458 | **+0.0768** | +0.0375 | +0.0208 |
| ewc + frozen bias, λ = 3e-3 | −0.0013 | −0.0013 | −0.0016 | +0.0042 |
| ewc + frozen bias, λ = 3e-4 | +0.0016 | **+0.0081** | +0.0021 | +0.0219 |

Tallied at 2σ (a component is called only when the paired change clears twice the sum-in-quadrature sem):
**near 7 of 9 rise, none fall, 2 unresolved**; **far 1 of 9 rises, 8 unresolved**.

## 3. The localisation, and the correction the sems forced

**The adjacent-pair component is where the two lines disagree, and both are resolved there**: the analytic line says
sharing a population makes adjacent tasks interfere *less* — a monotone fall from +0.0258 to below zero over six
levels — and the network line says it makes adjacent tasks forget *more*, +0.0557 → +0.0833 on the unpenalised arm
and the same sign in seven of nine comparisons.

**The distant-pair component does not support a shared-trend claim, and the first version of this script made one.**
It printed that the far trend is shared between the lines ("both lines say they get worse, so the aggregate's
opposite sign is a composition"). The analytic block reports three-seed means with **no interval**, and on the
network side the far changes clear 2σ in **one of nine** — the rest are changes of the same order as their own
error. So the licensed sentence is weaker: *the far component points the same way in both lines and is unresolved in
both; what the aggregate sign difference is made of is the adjacent pairs.*

**The mechanism the split suggests, stated as a hypothesis rather than a result**: in the analytic line two tasks
that share an input population share a **measurement operator**, and a posterior update from one is then not
harmful to the other; in the network line a shared input population puts two tasks' class templates on the **same
neurons behind one decoder**, so the directions compete. "Sharing inputs helps a shared measurement and hurts a
shared decoder" is testable — the cleanest form being the same overlap sweep with per-task heads, where the decoder
is not shared, which the corpus can express today: 17 of its runs already use per-task heads (`e186`).

## 4. Falsifiers and scope

- **The declaration is in the script**: the analytic near/fall and far/rise and the network tallies are written down,
  so a new artifact on this axis either reproduces them or fails the check rather than passing silently.
- **The analytic block's intervals are missing**, which is why §3 refuses to call its far rise resolved. Re-running
  `e7`'s controlled sweep with per-pair intervals would decide it; the block stores `n_pairs_zero_support_overlap:
  10`, so the pairs are known but their scatter is not.
- **The two lines' quantities are different by construction** — a covariance-based interference against an accuracy
  drop — so this finding's claim is about the *responses to one manipulation*, not about one quantity predicting the
  other. The comparison is licensed because the inputs are built by the same construction (`make_overlap_suite`'s
  own docstring: "the same pool-plus-private-complement construction as `e7`"), the same support (80) and the same
  task count is *not* shared: the analytic sweep has five tasks and the network three.
- **What would refute the localisation**: a network near component that falls with overlap, or an analytic near
  component that rises — either would move the disagreement out of the adjacent pairs.

## Reproduce

```
uv run python -m experiments.e189_overlap_sign_across_lines       # the two tables, the tallies, 0 contradictions
uv run pytest tests/test_e189_overlap_sign_across_lines.py -q
```
