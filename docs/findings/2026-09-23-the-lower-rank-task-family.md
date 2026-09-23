# E100 — the lower-rank task family: the account is confirmed twice, and the diagonal's advantage is configuration-specific

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py --classes 2` at cs = 800, `e8_hardened_basis`'s configuration
otherwise unchanged; artifact `runs/e100_rate_cs800_classes2.json`.
**Pre-registration:** `docs/findings/2026-09-23-the-lower-rank-task-family-preregistered.md`
**Context:** `docs/findings/2026-09-23-the-reversed-ordering-question-at-a-smaller-circuit.md` (`e99`, the
circuit-size route), and the plan's §8 item 2, which names both routes.

---

## 1. Three configurations, one design

Five replicates each, λ = 0.003, 32 Fisher batches, `cell_class`, `readout_size` 32, `shared_head`,
`support` 80; the middle column changes only `--circuit-size`, the right one only `--classes`:

| arm, mean forgetting ± sem | 4 classes, cs = 800 | 4 classes, cs = 300 (`e99`) | 2 classes, cs = 800 (`e100`) |
|---|---|---|---|
| `naive` | +0.0729 ± 0.0151 | +0.0875 ± 0.0194 | +0.0167 ± 0.0107 |
| `ewc` (diagonal) | +0.0208 ± 0.0147 | +0.0771 ± 0.0374 | +0.0229 ± 0.0083 |
| `ewc-block` (biological) | +0.0604 ± 0.0201 | +0.0938 ± 0.0216 | +0.0250 ± 0.0126 |
| `ewc-block-rand` (matched) | +0.0438 ± 0.0156 | +0.0833 ± 0.0291 | +0.0208 ± 0.0087 |
| `replay` | +0.0500 ± 0.0163 | +0.0458 ± 0.0234 | **+0.0125 ± 0.0083** |

| contrast | 4 classes, cs = 800 | 4 classes, cs = 300 | 2 classes, cs = 800 |
|---|---|---|---|
| block − matched random | +0.0167 (0.65σ) | +0.0104 (0.29σ) | **+0.0042 (0.27σ)** |
| **block − diagonal** | **+0.0396 (1.59σ)** | **+0.0167 (0.39σ)** | **+0.0021 (0.14σ)** |
| `naive` − diagonal | +0.0521 (**2.47σ**) | +0.0104 (0.25σ) | **−0.0063 (0.46σ)** |

## 2. The clauses

- **P1 holds.** The biological block is worse than its matched random control in all three configurations
  (+0.0167, +0.0104, +0.0042), same direction, resolved in none.
- **P2 holds, and by more than the circuit route bought.** The block-minus-diagonal gap falls from
  **+0.0396 to +0.0021 — a 95% reduction**, against the circuit route's 58%.
- **P3 holds.** 0.14σ. Nothing is resolved here either.
- **The falsifier did not fire.**
- **P4 — the discriminator — holds.** Its clause was: *if the account is right, both routes shrink the gap;
  if one shrinks and one grows, the account is incomplete.* **Both shrink it**, by 58% and by 95%, via two
  different mechanisms — fewer entries to estimate, and a lower-rank target — with the circuit, the
  partition, the entry count and the batch count held fixed in one of them. **So the estimation-noise account
  now has two independent confirmations in direction**, where a single route could only have given one.

**And the ordering is the one the account wants**: the gap is largest where the estimation problem is hardest
(4 classes, d = 1307), smaller where the estimate is cheaper (4 classes, d = 952), and nearly zero where the
target is simplest (2 classes, d = 1307). Three points, one ordering, no point where it moved the other way.

**But it is three points, and none of the three gaps is resolved.** The account predicts a *direction* and
has now been right about it three times; it predicts a *magnitude* at no point, because 0.0396 is 1.59σ and
0.0021 is 0.14σ. So the honest standing is what `e99`'s finding already said at two sizes, now at three
configurations: **resolved in direction, unresolved in size, and the account is the best explanation on
offer rather than a measurement of anything.**

## 3. And the diagonal's advantage over `naive` appears in exactly one of the three configurations

| `naive` − diagonal | |
|---|---|
| 4 classes, cs = 800 | **+0.0521 at 2.47σ** — the diagonal helps |
| 4 classes, cs = 300 | +0.0104 at 0.25σ — gone |
| 2 classes, cs = 800 | **−0.0063 at 0.46σ** — the sign has flipped, the diagonal is worse |

This is the paper's own §4.7 result — *"λ = 0.003 with the Fisher estimated from 8 batches gives +0.010 ±
0.010 forgetting against naive's +0.066 ± 0.019, a **2.6σ** advantage"* — and it is now measured in three
configurations of which **one** reproduces it. So the claim is true and **configuration-specific**, and the
paper states it as if it were the λ = 0.003 result rather than the result at that λ *in that configuration*.

**That is the third unanticipated finding in two fires**, and all three have the same shape: a network-line
claim that holds in the configuration it was measured in and stops holding when one thing changes —
the diagonal's benefit (circuit size, then task rank), the basis ordering (task rank, `e99`), and now this.
**The network line has four configurations and the paper reports each result from one of them.**

## 4. What this does not settle

- **`--classes 2` also makes the benchmark easier.** Every arm's forgetting falls (naive +0.0729 → +0.0167;
  the diagonal +0.0208 → +0.0229) and every arm's accuracy rises to ~0.97. The *contrasts* survive that
  change because all five arms see the same suite, but "an easier benchmark compresses all the gaps" cannot
  be excluded from one configuration — and it would predict exactly what was observed. **That is the
  strongest competing explanation for this run**, and it is not addressed by anything measured here.
- **Three configurations are still three points.** P4's "both routes shrink it" is two differences from one
  baseline, which is what the pre-registration asked for and all it asked for.
  **And the account's own two movements are inside their error bars**: block-minus-diagonal moves
  +0.0396 → +0.0167 (cs = 800 → 300) at **0.46σ**, and the level hypothesis's movement is **0.59σ**, so
  neither the account nor its competitor is excluded by a resolved difference. Separating them needs
  **~57 replicates per arm**, i.e. 6–44 hours for this one contrast (`docs/findings/2026-09-23-the-competing-explanation-is-not-excluded.md`).
- **None of the three gaps clears 2σ**, and the `naive` per-repeat sd of 0.048 means a 0.04 gap is within one
  replicate's spread however many are averaged.
