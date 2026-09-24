# The channel-resolved form orders the forgetting across ten cells — and the θ-only form mostly does too, which is narrower than this project has been claiming

**Date:** 2026-09-24
**Script:** `experiments/e156_channel_resolved_ordering.py` — analysis only, no runs. Artifact:
`runs/e156_ordering.json`.
**Artifacts read:** `runs/e140_r32_methods_plastic_40reps.json` and
`runs/e140_r32_methods_frozenbias_40reps.json` — the same five-method table run twice, with the channel free and
with the unpenalised channel removed from every arm. **Ten cells** (five methods × two channels), each forty
paired seeds.
**Why now:** `e139` tested this instrument on **three** arms and `e149` on **four** cells of one 2×2. The second
run of the five-method table makes the record's strongest test of its own mechanism quantity available.

---

## 1. The ten cells

| arm | method | forgetting | sem | whole-body | θ-only | bias-only | bias share |
|---|---|---|---|---|---|---|---|
| plastic | `naive` | +0.0750 | 0.0088 | 0.3440 | 0.1905 | 0.1535 | 0.446 |
| plastic | `ewc` | +0.0654 | 0.0079 | 0.3366 | **0.0166** | 0.3199 | **0.951** |
| plastic | `ewc-block` | +0.0573 | 0.0070 | 0.3517 | 0.1257 | 0.2260 | 0.643 |
| plastic | `ewc-block-rand` | +0.0779 | 0.0099 | 0.3938 | 0.1405 | 0.2533 | 0.643 |
| plastic | `replay` | **−0.0034** | 0.0034 | **0.0013** | 0.0004 | 0.0009 | 0.685 |
| frozen | `naive` | +0.0227 | 0.0033 | 0.1614 | 0.1614 | **0.0000** | **0.000** |
| frozen | `ewc` | −0.0021 | 0.0029 | 0.0217 | 0.0217 | 0.0000 | 0.000 |
| frozen | `ewc-block` | +0.0062 | 0.0033 | 0.0675 | 0.0675 | 0.0000 | 0.000 |
| frozen | `ewc-block-rand` | +0.0091 | 0.0035 | 0.0954 | 0.0954 | 0.0000 | 0.000 |
| frozen | `replay` | +0.0018 | 0.0032 | 0.0005 | 0.0005 | 0.0000 | 0.000 |

**The bias share is exactly 0.000 in all five frozen cells** — a structural identity, since a frozen offset
cannot move — and it is the same instrument whose bias component `e149` verified as *exactly* `0.0` per replicate
on those arms. On the plastic side the column is the mechanism: the diagonal pushes **95.1%** of its first-order
term through the offsets, `naive` **44.6%**, the two block arms **64.3%** each, and `replay` **68.5%** of a term
that is itself **300× smaller** than anybody else's.

## 2. Which form orders the forgetting

| form | Spearman ρ (10 cells) | p | pairwise agreement (45 pairs) | within plastic | within frozen |
|---|---|---|---|---|---|
| **whole-body** (θ+bias) | **+0.927** | **1.1e−4** | **41/45 = 0.911** | +0.700 | +0.900 |
| θ-only | +0.721 | 0.019 | 36/45 = 0.800 | +0.800 | +0.900 |
| bias-only | +0.679 | 0.031 | 27/45 = 0.600 | — | — |
| whole-body, task 0 | +0.879 | 8.1e−4 | 39/45 | — | — |
| **whole-body, task 1** | **+0.952** | **2.3e−5** | **42/45** | — | — |

**This is the strongest support the ordering law has had**: ten cells, two channel manipulations, both tasks, and
the pairwise count agrees with the rank statistic rather than hiding a near-tie. `e139`'s three-arm ordering and
`e149`'s four-cell task-0 ordering are consistent with it at a scope four times larger.

## 3. And two corrections this makes to claims already in the record

**First, the θ-only form does order the forgetting here — more weakly, but resolved.** ρ = **+0.721 (p = 0.019)**,
36 of 45 pairs. **This project has been writing that the θ-only term "cannot order the forgetting"** (`e108`'s
three-negative-member result, `e139`'s 98% cut with the effect unmoved, `e149`'s channel-blindness), and the
narrower true statement is: **it orders arms worse than the channel-resolved form (0.721 against 0.927) and it
cannot see the bias's contribution at all** — which is *why* an intervention that cuts it 9.8-fold leaves the
effect standing. "Orders worse and is blind to a channel" and "cannot order" are different claims, and only the
first is what the measurements say at this scope. (`e108`'s failure was *within* a configuration — task 0 against
task 1 — which is a different statistic from a rank correlation across cells, and both can be true.)

**Second, `e149`'s "the whole-body ordering is a task-0 statement" is too strong.** At task 1 the ten-cell
agreement is **+0.952 against task 0's +0.879**, i.e. task 1 orders *better*, not worse. What `e149` actually
found was a violation **inside its own four-cell freeze×penalty design** (the penalty arm carrying more task-1
interference than `naive` while forgetting less). **The licensed form is therefore narrower: the ordering broke in
that four-cell set, and it does not break across the ten.** `e149`'s finding carries this correction.

## 4. What this cannot settle

- **Ten points, and they are not independent**: two runs × five methods on the same forty seeds and one base
  model, with the two runs sharing their `naive`-free structure but not their arms. A Spearman ρ over ten
  non-independent cells is a descriptive statistic and its p-value is optimistic — the pairwise count is quoted
  beside it for that reason, and it is not an independent replication either.
- **The cell means carry sems from 0.0029 to 0.0099**, so several adjacent pairs in the ten-cell order are *not*
  resolved (plastic `ewc` +0.0654 against plastic `ewc-block` +0.0573 is 0.0081 apart with sems 0.0079 and 0.0070),
  and a rank correlation counts those as correctly or incorrectly ordered with equal weight. The 4/45 pairs where
  the whole-body form disagrees are the places to look, and this script does not name them — a per-pair table is
  the obvious next step if a claim ever rests on one of them.
- **It compares forms of one instrument on one benchmark configuration** (read-out 32, `cs = 800`, three tasks);
  the ordering law's scope is exactly that, and the read-out axis is where `e139`'s instrument has already been
  shown to move faster than the forgetting.
- And the ten-cell set contains **one manipulation of the channel** (all-or-nothing freeze of the offsets), not a
  graded one, so "the channel-resolved form beats the θ-only form" is established for a channel that is either
  free or absent.
