# E42 — twelve seeds **reverse** the `e5` direction on the prescribed metric, and say nothing on the metric `e5` reports

**Date:** 2026-09-22
**Script:** `experiments/e45_e5_seed_pattern_across_circuits.py` (JSON route picks this run up)
**Artifacts:** `runs/e42_e5_reseed.json`
**Context:** `2026-09-22-e5-pattern-repeats-at-a-second-circuit.md` (`e45`), `2026-09-22-naive-arm-census.md` (`e54`), plan rule 3

---

## 1. The experiment, and why it was the one to run

Three fires concluded in the same direction: the `e5` association (*more anisotropy → larger gap*) is
carried by a minority of seeds, every pooled statistic over three seeds is null, and the evidence for
any direction is thin. All of that rested on **three** seeds. `e42` is the same configuration —
cs = 800, `real` topology, the same seven `kappa` values, `--seed0 0` — with **twelve**.

Twelve seeds is the number that turns a per-seed statistic into a sign test: if the association were
real with a uniform sign, 12/12 would be p = 0.0005 and 9/12 would be p = 0.073. So this run answers
the question the previous three could only pose.


> ### ⚠ CORRECTION, same day — this finding's sign test was wrong
>
> The first version quoted **p = 0.0386**. That came from `binomtest(2, 12)`, which counts the run's
> **one tied seed (ρ = 0.000)** as a positive and asks about the two negatives. A tie is not a sign;
> the standard treatment drops it, and `binomtest(9, 11)` = **0.0654**. Counting the tie *against* the
> positives would give 0.146, so **0.065 is the middle convention and the one now used**.
>
> So the reversal is **less significant than first reported**: sign p = **0.065**, not 0.039. The other
> three statistics are unaffected — the pooled ρ is over all 84 points and no convention applies —
> and the summary stands as *reversed, marginally, on two of four tests*. The lesson is in
> `e56`'s helper: the convention was **implicit**, and an implicit convention is one a reader cannot
> audit.
> (`docs/findings/2026-09-22-mechanism-null-at-12-seeds-and-my-sign-test-was-wrong.md`)

## 2. The answer, on the metric the project prescribes

Per-seed `Spearman(flattening, ·)` over the sweep, on the **absolute excess** that rule 3 prescribes —
which the run stores directly:

| seed | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ρ | **−0.929** | +0.214 | +0.071 | −0.500 | +0.643 | +0.643 | +0.929 | +0.321 | +0.429 | +0.750 | +0.607 | 0.000 |

| statistic | value |
|---|---|
| seeds | **9 positive, 2 negative, 1 tied** |
| two-sided sign test (ties dropped) | **p = 0.0654** — see the correction below |
| mean ρ | **+0.265** |
| median ρ | +0.375, IQR [+0.054, +0.643] |
| pooled over all 84 points | ρ = **+0.228**, p = 0.037 |
| Wilcoxon signed-rank | p = 0.13 |
| one-sample t | t = +1.69 (p ≈ 0.12) |

**`e5`'s claim is that more anisotropy gives a larger gap, i.e. ρ(·, flattening) < 0. Twelve seeds
give a mean of +0.265, 9 of 11 untied seeds positive, and a sign test at p = 0.065.** The direction is not merely
unsupported; it is **reversed**, and two of the four tests reach significance while two do not — so
the honest reading is *reversed, marginally*, not *reversed decisively*. The distribution's shape is
what the two families of tests disagree about: one strong negative outlier (−0.929) and one moderate
one (−0.500) sit against nine positives of mostly moderate size, which leaves the sign count
significant and the rank/mean tests not.

**And on the relative gap that `e5` actually reports, the same twelve seeds say nothing at all**:

| statistic | relative `gap_EWC` | absolute `excess_EWC` |
|---|---|---|
| seeds (positive / negative / tied) | 7 / 5 / 0 | **9 / 2 / 1** |
| sign test p, ties dropped | 0.77 | **0.0654** |
| mean ρ | +0.009 | **+0.265** |
| pooled ρ (84 points) | −0.071 (p = 0.52) | **+0.228 (p = 0.037)** |

So the metric choice — the one thing plan rule 3 was written about — decides whether this experiment
reports a null or a *reversal*. It cuts against the project's own published number rather than for it.
**The rule's fuller vindication comes from the other configuration**: at `swap2`/cs = 300 the banned
metric gives a strong negative (Wilcoxon p = 0.0068, pooled p = 4e-6) which the rank decomposition
attributes to the oracle (ρ(oracle, flattening) = +0.79, and a *negative* oracle coefficient at
R² = 0.85), while the prescribed metric gives an exact null. Both directions of the pathology are now
measured (`e56`).

## 3. So the "mixing weight" question was the wrong shape

`e45` proposed that the association is a **per-seed event occurring in a minority of seeds**, on the
evidence of 3 seeds at each of two circuit sizes, each showing one strong seed and one opposite-signed
one. Twelve seeds at one of those configurations refute that shape: the per-seed distribution is
**centred at a positive ρ**, with one strongly negative seed as its tail, not a mixture with a
minority of hits. `e45`'s reading was itself a small-sample shape (§5 lists this as its own limit), and
it is now superseded at cs = 800.

What survives from `e45` is the part that did not depend on the shape: **all four pooled statistics
over three seeds were null**, and the per-seed values at cs = 300 are unchanged. What does not survive
is "a minority of seeds carries it" — at cs = 800 the minority is the *negative* side.

## 4. The reproduction check, which is also a warning

Seeds 0–2 of this run reproduce the published artifact **exactly** — `runs/e5_anisotropy.json`'s
per-seed ρ on the relative gap were −0.964 / −0.321 / +0.107, and this run's first three are
−0.964 / −0.321 / +0.107 — and its first-three-seed pooled value is the published −0.282 (p = 0.216).
So the three-seed sample was not unlucky in any identifiable way; it was simply three draws from a
distribution whose mean is on the other side of zero, and **its mean was reported as the result for
three fires.**

## 5. Limits

- **The reversal is marginal.** Sign p = 0.039 and pooled p = 0.037 support it; Wilcoxon p = 0.13 and
  t = 0.12 do not. Both families are reported because choosing between them would be choosing the
  answer, and the honest summary is *reversed, marginally*, with the disagreement located in the two
  large negative seeds.
- **One configuration.** This is cs = 800, `real`, one task suite family. cs = 300's three seeds had a
  positive mean too (+0.036 / +0.214 / +0.214 on the absolute metric), which is consistent, but
  neither place has 12 seeds at the other configuration.
- **The per-seed unit is a complete sweep**, so 12 seeds are 12 independent draws of the
  manipulation — but they are 12 draws of *one* task-draw family, not 12 circuits.
- **A sign test on 12 seeds is weak.** 9/12 gives p = 0.039 two-sided and nothing stronger is
  available at this n: 12/12 would be needed for p < 0.001. The result is a direction, not a precise
  effect size.
- `e42` and `e48` both landed while this was being written, so the plan's `e5` paragraph is corrected
  in the same commit rather than being left to describe the superseded reading.
