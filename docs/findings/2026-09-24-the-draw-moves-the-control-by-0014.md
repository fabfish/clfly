# The draw moves the control by 0.014 — the network line's first measurement of its own control's spread

**Date:** 2026-09-24
**Artifacts:** `runs/e144_r32_overlap1_rand_draw1.json` and `..._rand_draw2.json` — the same command,
`--methods ewc-block-rand`, the same forty seeds, differing **only** in `--partition-seed`, with
`partition_draw.fingerprint_sha1` = `3058aa874ae6` and `f6a658eabf9c`.
**Why it is new:** rule 10 requires the matched-random control to be **averaged over draws**, and until
2026-09-24 `e8_rate_network.py` built **one** partition outside the replicate loop — so this line had **no
mechanism to vary its control at all**, and every `ewc-block-rand` number in the project's record is one draw.
`--partition-seed` is that mechanism, and these are its first two draws.

---

## 1. The measurement

| | fingerprint | mean forgetting | accuracy |
|---|---|---|---|
| draw seed 1 | `3058aa874ae6` | **+0.1010** | 0.8983 |
| draw seed 2 | `f6a658eabf9c` | **+0.0872** | 0.9012 |
| **draw 2 − draw 1** | — | **−0.01380 ± 0.01041 = 1.33σ** | +0.00295 ± 0.00671 = 0.44σ |

**The forty seeds are identical in both arms**, so that difference is **the draw term alone** — no seed variance
is in it. Its per-seed sd is **0.0658** on forgetting and 0.0424 on accuracy.

## 2. And on this line the draw term is *not* the small correction the linear line's budget suggests

**Rule 10 budgets ≈1e-3 for a coarse partition's draw sd — and that is a measurement of the linear substrate's
*excess* on d = 1307, not of this network's forgetting.** Here one draw moves the arm mean by **0.0138**, an order
of magnitude larger, and two more comparisons put it in proportion:

- **the per-seed sd of the draw difference (0.0658) is as large as the arm's own across-seed sd** (the same
  configuration's `naive` is 0.0556 and its `ewc-block-rand` 0.058–0.065) — so with seeds held fixed, the *draw*
  moves the arm about as much as *resampling the seeds* does;
- **and it is of the same order as the contrast it exists to bound**: `e135`'s five-replicate
  biological-minus-matched-random contrast on the base family is **−0.0125**, and one draw here moves the control
  by 0.0138.

**So on this configuration, a single-draw block contrast is a comparison whose control can wander by about as much
as the effect being tested** — which is not a criticism of the comparison having been made, it is what rule 10 was
written for, and it is the first time the number exists on this line.

## 3. What it implies for the run in flight, before that verdict exists

`e144` pits `ewc-block` against the **mean of three draws**. With the draw sd around **0.014**, the component that
term contributes to the control's standard error is roughly **0.014/√3 ≈ 0.008** (and it carries **2** degrees of
freedom), so **a ≥3σ contrast needs an effect of roughly 0.024 or more** — against a base-family contrast of
0.0125, i.e. **the base family's effect would not resolve here at all.** That is the level that decides whether
`e144`'s P1 is available, and it is written down **before** the block arm's numbers exist so that the verdict
cannot be read as if the control had been quiet.

## 4. What this does not settle

- **Two draws are one degree of freedom**, so 0.0138 is a *bound* on the draw sd and not an estimate of it; the
  third draw is in the main artifact and will make it two.
- **One configuration**: read-out 32, `cell_class` at cs = 800, three tasks. Rule 10's own text is that the draw
  sd is ordered by the partition's **concentration** and differs between circuits — 4.9e-4 at d = 952 against
  1.06e-3 at d = 1307 — so this number belongs to *this* partition on *this* circuit and transfers nowhere on its
  own.
- **And it says nothing about the biological partition.** Two `ewc-block-rand` draws vary the *control*; whether
  `ewc-block` sits outside that variation is exactly what the three-draw comparison asks, and it is not answered
  here.
