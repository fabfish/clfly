# E50 — the ladder's fourth rung is another null at 3.4 h, and the fifth was stopped rather than run

**Date:** 2026-09-22
**Script:** `experiments/e38_variance_budget.py` (§5, ladder summary), `experiments/e49_kappa_leverage_by_topology.py` (JSON-complete re-read)
**Artifacts:** `runs/e10_rung_supertype.json`, `runs/e37_kappa_swap2_cs800.json`, `runs/e38_variance_budget.json`, `runs/e49_kappa_leverage.json`
**Context:** `2026-09-22-penalty-cost-has-two-terms.md` (`e44`), `2026-09-22-network-variance-is-learner-variability.md` (`e38`), plan rule 18

---

## 1. `supertype` landed, and it is a null at three and a half hours

Twelve thousand, three hundred and forty-two seconds — **3.43 h** for one rung, against
`ito_lee_hemilineage`'s 0.77 h, which is `e44`'s cost model (G = 9,938 dispatch-dominated) showing up
in the wall clock.

| arm | final accuracy | per-replicate sd | mean forgetting |
|---|---|---|---|
| `naive` | 0.8241 | 0.0622 | +0.1007 |
| `ewc-block` (biological) | 0.8148 | 0.0462 | +0.0972 |
| `ewc-block-rand` (matched control) | 0.8333 | 0.0347 | +0.0590 |

**Biological minus matched random: −0.0185** — unpaired 0.55σ, paired 0.58σ (the pair correlation is
+0.08, so pairing buys nothing), and a detection floor of **±0.063**. Resolving a 0.01 effect would
take **119 replicates**. So this rung adds a fourth null with the *same sign* as the other three: the
biological partition is slightly worse than its size-matched random control.

## 2. All four rungs, at λ = 1.0

| rung | constrained | biological | control | Δ | σ | detection floor | reps for 0.01 | hours |
|---|---|---|---|---|---|---|---|---|
| `side` | 0.6947 | 0.8148 | 0.8264 | −0.0116 | −0.43 | 0.0523 | 82 | 1.76 |
| `cell_class` | 0.9250 | 0.8426 | 0.8611 | −0.0185 | −0.35 | **0.1026** | 316 | 1.16 |
| `ito_lee_hemilineage` | 0.9945 | 0.8333 | 0.8333 | +0.0000 | 0.00 | 0.0593 | 106 | 0.77 |
| **`supertype`** | **0.9988** | **0.8148** | **0.8333** | **−0.0185** | **−0.58** | 0.0630 | 119 | **3.43** |

**Three of four put biology below its own control, and none resolves — the largest |σ| is 0.58.**
Every run's detection floor is 0.05 or wider, while the effect the neuron line found is ~10% of the
oracle gap. So the honest reading of all four is unchanged from the first one: *at `λ = 1.0`, at these
rungs, the network benchmark cannot see the effect it is being asked about.* `cell_class`'s floor is
the worst at 0.10 — its 3-seed pair correlation was −0.98, so pairing made its σ worse, which is
`e38`'s point about quoting a paired sem without measuring the correlation.

## 3. The fifth rung was stopped, on four independent grounds

`cell_type` (G = 19,618) had started. It is stopped, and the reasons are separate:

1. **Its answer is entailed.** Plan `e35`'s arithmetic bound is `constrained ≤ 1 − (d/m + 1)/(d + 1)`,
   so a column with 19,618 groups over 26,568 weights is the diagonal by construction. `supertype`'s
   measured `constrained` is already 0.9988; the diagonal is what the bound leaves.
2. **It is the most expensive rung.** `e44` measured the per-step cost at all five real group counts;
   the fine rungs are dispatch-dominated at ~28–33 µs per group per step, and `cell_type` has twice
   `supertype`'s groups. Extrapolating the 3.43 h gives **~6 h** on a queue that already has four
   jobs.
3. **It cannot resolve the question anyway.** `e38` §3: at 3 replicates the floor is ±0.05–0.10, so
   a 0.01–0.03 network effect is invisible; `cell_type` at 3 replicates would add a fifth
   unresolvable null.
4. **The rungs that can carry a claim are already measured.** `side`, `cell_class` and
   `ito_lee_hemilineage` are the three whose `constrained` leaves room for biology to do something
   (0.6947, 0.9250, 0.9945 against 0.9988).

This is a deliberate scope decision, not a blocked thread, so it is recorded as one: **the ladder is
four rungs and stops there**, and `e44`'s own recommendation — *"do not run `supertype` and
`cell_type` at all"* — was written before `supertype` finished and is now applied to the one that was
still running. The queue freed by stopping it goes to `e46`, the 16-replicate run at `λ = 0.1`, which
is the only C2b measurement with a detection floor small enough to matter.

## 4. And `e49`'s `swap2` result, now from the complete JSON

`e37_kappa_swap2_cs800.json` has landed with all 21 points and the stored absolute excess, so last
fire's log-based numbers can be checked. They hold:

| seed | knob travel / seed noise | ρ(gap, flattening) | ρ(absolute excess, flattening) | verdict |
|---|---|---|---|---|
| 0 | 8.8 | −0.143 (p = 0.76) | +0.607 | over noise |
| 1 | 19.3 | **−0.786 (p = 0.036)** | −0.714 | informative |
| 2 | 8.6 | −0.964 (p = 0.0005) | −0.964 | over noise |

against `real`'s travel/noise of **142–271**. The log read gave 9.4 / 20.2 / 5.3 with the third seed
partial; the complete run gives 8.8 / 19.3 / 8.6. Rule 17's distinction is exactly this: the log was
sound for the individual points and would have been misleading for anything pooled.

Two things worth noting in the completed numbers. The **absolute** signs are +0.607, −0.714, −0.964 —
they disagree with each other, over a carrier range of 0.004. And seed 2's ρ = −0.964 (p = 0.0005) is
the *strongest* of the three while being flagged inert: a large correlation over a range barely wider
than the noise is the failure mode `e49` was written to catch, and it is sitting in this very table.

## 5. Limits

- **Stopping `cell_type` is a judgement**, and the four grounds are independent but not equally firm:
  (1) and (3) are entailments from the project's own arithmetic and power analysis, (2) is an
  extrapolation from `supertype`'s measured cost, and (4) is a reading of `constrained`. If
  someone wants the fifth null for completeness it costs ~6 h, and `e8_rate_network --basis cell_type`
  is the command.
- The rung comparisons are all at **λ = 1.0**, the argparse default that plan rule 14 was written
  about. `e46` addresses λ = 0.1, not the ladder at λ = 1.0.
- `supertype`'s Δ = −0.0185 happens to equal `cell_class`'s to four decimals. That is a coincidence
  of two 3-seed means, not a shared value; their sems are 0.0322 and 0.0245.
- The ladder's four nulls do **not** jointly bound the effect at 4 × ±0.06 — they are four
  configurations, not four independent samples of one.
