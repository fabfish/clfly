# `e153`, pre-registered: the wiring family's five-method table, in one artifact

**Date:** 2026-09-24
**Design:** `--circuit-size 800 --iters 500 --lr 3e-3 --batch 32 --train 96 --test 48 --noise 1.0 --classes 4
--support 80 --shared-head --input-overlap 1.0 --readout-size 32 --fisher-batches 32 --seed0 0 --repeats 40
--replay-per-task 96 --replay-batch 8 --methods naive,ewc,ewc-block,ewc-block-rand,replay`, writing
`runs/e153_r32_overlap1_methods_40reps.json`.
**Why now:** the launch slot that `e148` freed is the slot this unit was waiting for.

---

## 1. What is missing, and it is two things at once

**Coverage.** The wiring family's comparison is currently assembled from **two artifacts**: `e144` ran
`naive,ewc,ewc-block,ewc-block-rand` there, and `e148` ran `replay` alone, because the method the paper calls
strongest was missing from the family where the diagonal is at its best. **No single artifact of this family has
ever held all five methods**, so the family's *ranking* is a cross-artifact construction — and this project has
paid for that pattern before (`e140`'s C0a exists because a table's rows must be on one footing).

**Reproduction.** §9 of the paper states that **2 of 35 configurations have ever been executed more than once**,
and that a reproduction is a claim about an *arm at a configuration* rather than about a benchmark. The
`--input-overlap 1.0` four-method configuration has been executed once. **This run is its second execution**, and
it is the cheapest reproduction the queue can buy: the flags are identical to `e144`'s apart from adding a fifth
method that `e144` did not run.

## 2. The controls, which are the point of the unit

- **C0a — the four reused arms must be per-replicate identical to `e144`'s**, i.e. the whole `naive`-and-`ewc`-and-
  block-arms block, worst absolute difference 0.000. `e140`'s C0a passed on a run whose replay settings differed,
  so the expected outcome is exactness; **a failure here is a finding about the configuration's reproducibility
  and not about the methods**.
- **C0b — the `replay` row must be per-replicate identical to `e148`'s**, which was run in a *separate process*
  with the same flags. This is the same shape as `e140`'s C0b probe (four unread settings), and per rule 39 it is a
  **control that must hold**, not a test.
- **And the caution this unit exists to respect**: two arms' *aggregate* accuracies agreed to 1.5 × 10⁻⁹ across
  two different task families in `e148` while their per-replicate values differed by up to 0.0486, so **the
  criterion here is per-replicate identity and never an aggregate**.

## 3. The registered claims

- **P1 — the family's own central contrast is stable across runs.** In this artifact,
  `ewc-block` − `ewc-block-rand` must lie **within 2σ** of `e144`'s three-draw mean (**−0.0078**, total sem
  0.0079, the falsifier of that registration having fired). The single-draw value that contrast takes here is one
  sample of a control whose draw sd is **0.0086** on this family, so 2σ is the honest bar and a *point* difference
  is not evidence.
- **P2 — the wiring family's ranking, in one table, keeps the base family's order for the two methods that
  resolve there**: `replay` first and the plain diagonal second, i.e. `replay` − `ewc` negative and resolved at
  ≥ 2σ in this artifact, as it is in the two-artifact construction (**−0.0547 ± 0.0075 = 7.30σ**).
- **Falsifier for P1**: the contrast here is **more than 2σ** from `e144`'s three-draw mean. Then the wiring
  family's central contrast is **not stable across executions**, `e144`'s three-draw control is not a population
  estimate but one execution's, and every cross-family sentence in the paper that leans on it acquires a
  run-to-run term that no number in this project has measured.
- **Descriptive, registered with it**: the newest task's accuracy for all five methods in one table, which `e151`
  could only assemble — the wiring family has never had that column measured for `ewc-block` or `ewc-block-rand`.

## 4. What this cannot settle whatever it shows

- It is one configuration, one read-out, one overlap value, one seed set, and a fifth method added to four that
  were already run — so it moves the **family's** replication count from 1 to 2 and says nothing about the other
  thirty-three configurations in §9.
- **A per-replicate identity would be a statement about determinism at this configuration**, which §9 already
  qualifies (thread count moves analytic results at the fourth significant digit); a *failure* of C0a would be
  informative and its absence is not proof of anything beyond this environment.
- The biology's contrast here is still a **single draw** of the matched-random control; with three draws on this
  family already measured (`e144`), the honest way to read this artifact's block-rand row is against the draw
  population, which is why P1 is stated as a *stability* claim and not as a new measurement of the biology.
