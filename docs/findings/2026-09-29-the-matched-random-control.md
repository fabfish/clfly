# The matched-random control: the corpus's three penalty arms form a cycle, and the basis question has no answer without naming the comparator and the metric

*2026-09-29 03:30. Runs: **none new** — `experiments/e296_the_matched_random_control.py` reads every artifact that ran
both `ewc-block` and its matched random control, writing `runs/e296_the_matched_random_control.json`. Seconds.*

## 1. The control, and the direction it took

`e295` read the project's own comparison — the block-anchored penalty against the diagonal — and found the block arm
ahead on accuracy in 21 of 26 comparisons and behind on forgetting in all three of the resolved ones. That comparison
is between *anchoring structures*. The corpus's design has a control for the **biological** part of it:
**`ewc-block-rand`**, the same penalty on a **matched random partition** with the same group sizes. Forty artifacts ran
both arms, and the direction is stated rather than assumed: delta is `ewc-block` minus `ewc-block-rand`, and "ahead"
means better on that metric — higher for accuracy, **lower** for forgetting.

**C1's falsifier fired.** On `final_accuracy` the biological partition is ahead in only **15 of the 40 comparisons
(38%)** — so **a random partition of matched size is the more accurate arm by count**. Of the five resolved accuracy
comparisons, one favours the biological partition, and it is the largest (4.35σ, `e102_rate_fb8_omp1`, which the
corpus's own plan row already reports as sign-unstable across batch counts).

**C2 MET — the control does not separate the arms on forgetting by count.** The biological partition is ahead in
**18 of 40 (45%)**.

**C3's falsifier fired, and it is the substantive result.** Of the **two** comparisons resolved at two sigma with
forty replicates, **both favour the biological partition**:

| artifact | metric | delta | σ | replicates |
|---|---|---|---|---|
| `e140_r32_methods_plastic_40reps.json` | mean_forgetting | −0.02057 | 2.08 | 40 |
| `e275_frozenbias_suite600_40reps.json` | mean_forgetting | −0.00400 | 2.19 | 40 |

Negative on forgetting means the biological partition **forgets less** than its matched random control. And every
resolved comparison that favours it on either metric rests on 5, 40 or 40 replicates, while the ones against it rest on
**3 or 16** — so where the power is, the biological grouping *does* buy forgetting.

## 2. What the two units say together: a cycle, not an order

| comparison | accuracy | forgetting |
|---|---|---|
| block **vs diagonal** (`e295`) | block ahead, 8 of 9 resolved | block **behind**, 0 of 3 resolved |
| block **vs matched random** (this unit) | block **behind** by count (15 of 40), ahead in the largest resolved | block **ahead** where the power is (2 of 2 at forty) |

**The three penalty arms form a cycle rather than an order.** The block penalty beats the diagonal on accuracy and
loses to it on forgetting; it beats its matched random control on forgetting and loses to it on accuracy by count. So
*"which anchoring basis minimises forgetting"* has **no answer without naming the comparator and the metric**, and the
two comparisons the paper leans on point in **opposite directions on both metrics**. This unit therefore does not
report that the project's recommendation is wrong; it reports that the recommendation is not yet a statement — the
same shape `e295` found inside one comparison, now across two.

## 3. What it cannot do

**The two arms differ in the partition and in nothing else only if the runner's control is what it says it is**, and
this unit reads the artifacts' own `basis` field rather than re-deriving the matched partition; `e266`'s two seeds and
`e144`'s draw pairs are the corpus's own controls for that. **The matched random partition is one draw per
artifact**, so the comparison carries the random partition's own draw error, which `e286` showed can move a spread by
1.6x to 5.5x — and the corpus records the random draw's seed without having measured its spread. **Forty comparisons
are not forty configurations.** **A σ below two is not equality**, and 35 of 40 accuracy comparisons and 33 of 40
forgetting comparisons are unresolved. **And the largest resolved accuracy comparison is the least stable one**: it is
an `e102` batch-count variant whose sign the plan row already reports as unstable, which is why C3 is stated at forty
replicates rather than at five.
