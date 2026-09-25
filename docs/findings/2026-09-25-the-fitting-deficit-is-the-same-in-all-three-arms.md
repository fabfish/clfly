# The fitting deficit at achieved 0.3333 is the same in all three arms — including the size-matched random control

**Date:** 2026-09-25
**A cheap unit on existing artifacts.** The previous unit decomposed `naive`'s accuracy cost and found the midpoint's
cost to be a **learning** deficit (8.10σ) while the endpoint's is **forgetting** (2.99σ), with the caveat that "a task
set that is harder to fit and one whose tasks interfere are the same measurement"
(`docs/findings/2026-09-25-the-midpoints-cost-is-a-learning-deficit-not-forgetting.md` §2). The obvious next question
is the one that caveat leaves open: **is the deficit a property of the tasks, or of the method?** The same
decomposition, taken per arm, answers it — and the answer is the tasks, because the project's own matched-random
control shows it too.

---

## 1. The deficit in all three arms

`learned (older)` — the mean accuracy on the first T-1 tasks measured right after learning each — against each arm's
**own** admitted baseline, from the same inert-fields admission the dose reads use (so `naive` takes `e116` at
overlap 0.0 and the penalised arms take `e153` at overlap 1.0), 40 seeds:

| arm | achieved 0.1429 | **achieved 0.3333** |
|---|---|---|
| `naive` (vs `e116`) | +0.00651 ± 0.00320 = 2.03σ | **−0.03255 ± 0.00402 = 8.10σ** |
| `ewc-block` (vs `e153`) | +0.00234 ± 0.00397 = 0.59σ | **−0.04010 ± 0.00404 = 9.92σ** |
| **`ewc-block-rand`** (vs `e153`) | +0.00469 ± 0.00435 = 1.08σ | **−0.03516 ± 0.00465 = 7.55σ** |

**And measured on the axis every arm shares**, the drop from achieved 0.1429 to achieved 0.3333 within each arm:

| arm | drop in `learned (older)` | resolution |
|---|---|---|
| `naive` | −0.03906 ± 0.00401 | **9.73σ** |
| `ewc-block` | −0.04245 ± 0.00431 | **9.85σ** |
| `ewc-block-rand` | −0.03984 ± 0.00450 | **8.84σ** |

The three drops span 0.0034, and **the arms are indistinguishable from each other on this quantity**, in contrasts
paired by replicate index (the arms share each run's repeats, so they are not independent samples and are not treated
as such):

| cross-arm contrast | measurement | σ |
|---|---|---|
| `naive` − `ewc-block` | +0.00339 ± 0.00547 | **0.62σ** |
| `naive` − `ewc-block-rand` | +0.00078 ± 0.00533 | **0.15σ** |
| `ewc-block` − `ewc-block-rand` | −0.00260 ± 0.00589 | **0.44σ** |

while each arm's own drop is 8.8–9.9σ from zero. In absolute terms, on `learned (older)` accuracy:

| arm | achieved 0.1429 | achieved 0.3333 | overlap 1.0 |
|---|---|---|---|
| `naive` | 0.9669 | **0.9279** | 0.9615 |
| `ewc-block` | 0.9438 | **0.9013** | 0.9414 |
| `ewc-block-rand` | 0.9427 | **0.9029** | 0.9380 |

**Every arm dips at the same level and returns to roughly its own 0.1429 value at full overlap.** The penalised arms
sit about 0.027 *below* `naive` at every overlap — their penalty's standing cost — but the dip's **size** does not
depend on the arm.

## 2. Why the control is the point

`ewc-block-rand` is the project's group-size-matched random control: it penalises the same **number** of connections
drawn **at random** rather than the connectome's own mask. So the deficit surviving in that arm says two things at
once:

- it is **not the method's** — a strong penalty does not remove it (if anything the penalised arm's dip is the
  largest of the three, though not resolved as larger);
- it is **not which neurons the tasks share** — the control's sharing is random, and the dip is the same size.

What is left is the manipulation itself: at achieved overlap 0.3333 the three tasks' supports share enough neurons
that fitting them is harder, uniformly across methods. **That is a bound on the previous finding rather than a
mechanism**: the earlier caveat said the design cannot separate "harder to fit" from "interference"; this says the
effect is not reachable by the penalty or by the mask, which is where an interference-between-learned-solutions story
would have to live.

## 3. What is NOT arm-independent, which is worth keeping

The **newest** task's drop from achieved 0.1429 to 0.3333:

| arm | newest-task drop | resolution |
|---|---|---|
| `naive` | −0.02344 ± 0.00651 | **3.60σ** |
| `ewc-block` | −0.01354 ± 0.00698 | 1.94σ |
| `ewc-block-rand` | +0.00104 ± 0.00860 | 0.12σ |

So the *older-task* deficit is arm-independent and the *newest-task* deficit is **not** — it is largest for the
unpenalised arm and absent for the control. The two are not one phenomenon, and a finding that reported only §1 would
have flattened that.

## 4. The penalised arm's split moves too

For `ewc-block` against `e153`, the two components of its cost:

| | `learned (older)` | `forgetting` |
|---|---|---|
| achieved 0.1429 | +0.00234 = 0.59σ | **+0.04531 = 4.10σ** |
| achieved 0.3333 | **−0.04010 = 9.92σ** | +0.01849 = 1.60σ |

**At achieved 0.1429 the penalised arm's cost is forgetting and at achieved 0.3333 it is fitting** — the same switch
the `naive` arm makes between the endpoint and the midpoint, one level earlier. The penalty does not change which
component carries the cost; it changes the baseline the cost is read against.

## 5. Scope

- **The two baselines are not the same end of the axis.** `naive` is measured against overlap 0.0 and the penalised
  arms against overlap 1.0, so §1's *levels* are not one axis and only the signs and resolutions are comparable
  there. §1's **drops** are the same axis (within-arm, 0.1429 → 0.3333) and are the comparison the finding rests on.
- **One interior level** of a five-level design, n = 40, three tasks, `mb+cx+al@n1307` at seed 0.
- **The supports are still reconstructed rather than recorded** (the previous finding's §2), so what the arms share
  at each target overlap is a property of the construction, not of any artifact.
- **The three arms are not independent draws of the tasks.** They share each run's partition and readout draws, so
  §1's cross-arm contrasts are **paired by replicate index** rather than treated as independent samples — which is
  how the three contrasts in §1 are computed, and why they carry a σ at all.

## 6. Registered now, before level 0.75 lands

**S6 — the control's deficit is still there at two thirds of the axis.** At achieved 0.6000
`ewc-block-rand`'s `learned (older)` against `e153` is **below −0.0100**, i.e. the arm that makes the 0.3333 excursion
a property of the task set rather than of the method still shows it, at roughly a quarter of its 0.3333 size or more.
**Falsifier**: at or above **−0.0020**, which is unresolved at that arm's sem of ~0.0047 and would say the excursion
is local to the 0.3333 level — a single interior peak rather than a graded defect of the axis. **Null worth keeping**:
between −0.0100 and −0.0020, a partial deficit that neither resolves nor vanishes.

It is read by `e194` at the same achieved overlap as S1-S5, from the same admission rule, and its verdict prints the
arm, the value, the σ and the sem.
