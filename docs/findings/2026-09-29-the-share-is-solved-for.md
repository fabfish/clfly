# The share is solved for: the paper's own decomposition of these pairs, reproduced, and the two comparisons that leave its range

*2026-09-29 01:28. Runs: **none new** — `experiments/e289_the_share_is_solved_for.py` reads the three sample swaps
`e285`, `e286` and `e287` found, writing `runs/e289_the_share_is_solved_for.json`. Seconds.*

## 1. The account this line refuted was not the account the paper holds

`e286` refuted a **one-component** account of the across-replicate spread — that it falls as `1/sqrt(n_eval)` — and
`e287` said the same account's failure was anti-ordered. The paper's §4.7 does not hold that account. It holds a
**two-component** one, and about **these same pairs**:

> A tenfold test set (`--test 480` against the 48 of every run above) at forty replicates … so the spread falls
> **1.47x** and **1.34x** — and the ceiling, solved for from the fact that the binomial part must fall by exactly
> sqrt(10) while the training part does not move, is **1.57x** and **1.41x**. **The tenfold test set therefore captured
> 94% and 95% of what is removable**

So `v = t^2 + b^2`, with `t^2` fixed and `b^2` falling by the suite ratio `k`. This unit reproduces that
decomposition from the artifacts, and then asks what the section does not.

## 2. Z1 MET — the section's own numbers come out of the artifacts

| pair | quantity | the section | this unit | difference |
|---|---|---|---|---|
| read-out 128 | fall | 1.47 | **1.468** | 0.002 |
| read-out 128 | ceiling | 1.57 | **1.572** | 0.002 |
| read-out 128 | captured | 0.94 | **0.934** | 0.006 |
| read-out 300 | fall | 1.34 | **1.343** | 0.003 |
| read-out 300 | ceiling | 1.41 | **1.407** | 0.003 |
| read-out 300 | captured | 0.95 | **0.954** | 0.004 |

Six numbers, **worst difference 0.0064**, from two artifacts each. That is an instrument agreeing with the paper it is
reading, and it is worth stating because three earlier units of this line read the same pairs and did not check
against it.

## 3. And the capture is not a measurement

The capture sounds like a third quantity and it is not one. With `ratio = sqrt(1 - (1 - 1/k)q)` and
`ceiling = 1/sqrt(1 - q)`,

```
captured = sqrt(1 - q) / sqrt(1 - (1 - 1/k) q)
```

— a function of the **solved share and the suite ratio alone**. So "captured 94% and 95% of what is removable" does
not measure how much of the removable part was captured; it **restates the solved share in another coordinate**.
The decomposition has **one free parameter per pair and one datum per pair**, so it fits every pair by construction
and its 94% cannot fail. What it can do is be asked for a *prediction*, and that needs a third suite size.

## 4. Z2 MET — and the model's range is left twice

A share of a variance cannot exceed the variance, so `q` must lie in `[0, 1]`; a comparison that fell further than the
whole of its removable part allows gives `q > 1`, and there the model has no ceiling to report. Over the corpus's
fourteen arm-by-metric comparisons, `q` runs **0.260 to 1.075**, and **two leave the range**:

| config | arm / metric | k | fall | solved share |
|---|---|---|---|---|
| read-out 32 | `replay` / final_accuracy | 4.17 | 2.336 | **1.075** |
| read-out 32 | `ewc-block-rand` / mean_forgetting | 4.17 | 2.101 | **1.018** |

Both are in the read-out-32 configuration and both are the arms `e285` measured. For those two the numbers cannot
close with the training component *fixed*: the spread fell further than removing the entire binomial part permits, so
the training component itself must shrink with the suite. That is `e286`'s and `e287`'s result stated in the section's
own terms, and it is the first statement in this line that the section's model cannot absorb.

## 5. Z3 MET — and the runner's noise block is not the model's parameter

The runner reports a removable share directly, `(binomial_sem / sd)^2`. Read as the model's `q` it must be at most
one; **in 8 of the 14 comparisons it exceeds one**, running **0.421 to 2.086** — the largest being `naive`'s
final_accuracy at read-out 32, where the nominal floor is twice the measured spread it is supposed to be a part of.
So the artifact's own noise block cannot be the decomposition's parameter, and the section says as much in the
neighbouring sentences (it solves for an *effective* 49 independent decisions where the nominal count is 144) — but
the two numbers had not been put side by side across the swap census.

## 6. What it cannot do

**The section is quoted and not audited**: this unit reproduces six numbers, and reproducing a fit made by
construction does not make it wrong. **`q` is solved from the same two sd's the fall is**, so Z1 is arithmetic rather
than measurement, and the only out-of-sample test available to it is a third suite size — which is what the run
training beside this unit is for, at the read-out width the section does not cover. **The nominal and the solved
shares are compared as quantities and not as definitions**: `binomial_sem` is the runner's binomial formula on an
accuracy at `n_eval` while the solved `q` carries whatever correlation the held-out items have. **Fourteen
comparisons over three configurations**, with the read-out widths confounded with the suite ratios exactly as `e286`
said, so nothing here separates them. **And no number of the section's is re-measured**: what is new is the
solved-versus-nominal comparison, the algebraic identity in section 3, and the two comparisons that leave the model's
range.
