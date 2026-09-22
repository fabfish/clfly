# E45 — `e5`'s association is absent from the pooled statistic at **both** circuit sizes and under **both** metrics; the whole signal is one seed of three

**Date:** 2026-09-22
**Script:** `experiments/e45_e5_seed_pattern_across_circuits.py`
**Artifacts:** `runs/e45_e5_seed_pattern.json`, `runs/e37_kappa_real_cs{800,300}.json`, `runs/e5_anisotropy.json`
**Context:** `2026-09-22-e5-does-not-reproduce-its-own-artifact.md` (`e41`), `2026-09-22-e5-replication.md` (`e43`)

---

> ## ⚠ CORRECTION to this finding's first version, same fire
>
> The first version of this file, committed ~10 minutes before this one, reported that **the pooled
> verdict flips with the circuit size** — null at cs = 800, *significant* at cs = 300. **That is
> wrong**, and it was wrong for a reason worth recording: cs = 300 was read from `e37`'s **in-flight
> progress log**, at a moment when its third seed had **4 of its 7 `kappa` points**. A partial seed
> both contributes a badly-estimated per-seed ρ *and* is over-weighted in the pool (it enters with
> its 4 points alongside two complete seeds' 7). Completing that seed moved cs = 300's pooled
> p from **0.032 to 0.077** — across the significance line.
>
> The same partial data also made cs = 300's third seed look like **+0.500**, from which the first
> version concluded that "one strong seed and one *opposite-signed* seed repeats in each draw". With
> all 21 points that seed is **−0.179**, so **that claim is withdrawn too**.
>
> Everything below is computed from the finished JSONs, all 21 points per section.

## 1. The escape route this closes

`e41` found that the project's most-quoted direction — *more anisotropy gives a larger gap* — is
carried by **one seed of three** at cs = 800. That leaves the obvious escape: maybe those three seeds
were an unlucky draw of the *tasks*.

It is testable, because `e37` ran `e5`'s manipulation at **cs = 300 as well**, with the same three
seeds, the same seven `kappa` values, and an independent task draw. Both on the `real` topology, so
`--topology real` is a no-op and the comparison is exactly `e5` at two circuit sizes.

## 2. Four pooled statistics, all null

Per-seed Spearman, each seed a complete repeat of the sweep, and the pooled statistic over the 21
points:

**Relative gap `gap_EWC`** — the metric `e5` reports:

| draw | seed 0 | seed 1 | seed 2 | pooled |
|---|---|---|---|---|
| cs = 800 (d = 1307) | **−0.964** (p = 0.0005) | −0.321 (p = 0.48) | +0.107 (p = 0.82) | **−0.282, p = 0.216 — null** |
| cs = 300 (d = 952) | −0.321 (p = 0.48) | **−0.893** (p = 0.0068) | −0.179 (p = 0.70) | **−0.395, p = 0.077 — null** |

**Absolute excess** — the metric measurement rule 3 prescribes:

| draw | seed 0 | seed 1 | seed 2 | pooled |
|---|---|---|---|---|
| cs = 800 | **−0.929** (p = 0.0025) | +0.214 (p = 0.64) | +0.071 (p = 0.88) | **+0.040, p = 0.862 — null** |
| cs = 300 | +0.036 (p = 0.94) | **−0.893** (p = 0.0068) | +0.214 (p = 0.64) | **−0.103, p = 0.658 — null** |

**Not one of the four reaches significance**, and two of them (+0.040, −0.103) have the *opposite*
sign to the claimed direction. The claim is therefore not merely "unstable across a draw"; under the
metric the project itself prescribes, **it is absent from the pooled statistic at both circuit sizes
tested**.

## 3. What does repeat is the *shape of the failure*

One thing is identical in both draws: **exactly one seed of three shows a strong association, and the
two strong seeds agree closely** — ρ = **−0.964** and **−0.893** on the relative gap, **−0.929** and
**−0.893** on the absolute. The other two seeds in each draw are weak negatives or positive.

So the honest model is that the association is a **per-seed event occurring in a minority of seeds**,
not a uniform property with noise on top. That reading is consistent with both draws (2 strong hits in
6 seeds) *and* with every pooled statistic being null — which is what a mixture produces when it is
averaged.

Note what this does **not** say. It does not say the direction is wrong: in each draw one seed shows
it at ρ ≈ −0.9, and `e41`'s concern was never that the effect is absent but that it had been
estimated from a single realisation. Six seeds can say the pattern repeats; they cannot estimate the
mixing weight, which is what `e42`'s 12 seeds of the same configuration are for.

## 4. Two by-products from the same artifacts

**`e43` is confirmed at the JSON level, not just the log level.** `e37_kappa_real_cs800.json` has
landed and its 21 points are bit-identical to `e5_anisotropy.json`, so the artifact is the live output
of the current code and the published table's discrepant cells are the stale thing.

**The stored absolute-excess column is consistent with the derived one.** `e37`'s runs stored
`excess_ewc` directly, having been launched after that field was added, and they agree exactly with
`gap_ewc x oracle_final` recovered from the older artifact: both give per-seed −0.929 / +0.214 /
+0.071 and pooled +0.040 (p = 0.862). That matters because `e41`'s headline negative result rests on
exactly that column, and it now has a second, independently-stored source.

## 5. Where this leaves `e5`

| statement | status |
|---|---|
| "Spearman(flattening, gap) = −0.75" | not in the artifact (`e41`), and the artifact is the live one (`e43`, now confirmed in JSON) |
| "the gap dips to a minimum at `kappa ≈ 0.5` … an easy middle regime" | **withdrawn** — one substituted cell (`e41` §3) |
| "more anisotropy gives a larger gap" | **absent from the pooled statistic at both circuit sizes and under both metrics** (p = 0.216, 0.077, 0.862, 0.658); present in **one seed of three** in each draw, at ρ ≈ −0.9 |
| "the pooled verdict flips with the draw" | **withdrawn in this same fire** — an artifact of pooling an incomplete seed from an in-flight log |
| "`e5` corrects `e2`'s confounded trend" | **cannot carry that weight as it stands** |

## 6. Limits

- **n = 3 seeds per draw.** Six seeds total is enough to say the shape repeats; it is not enough to
  estimate how often the strong-seed case occurs, which is why §3 stops at "a minority".
- **The two draws differ in two ways at once** — circuit size *and* task draw — because
  `circuits.extract(max_neurons=...)` changes the subsample and the tasks together. So "a property of
  the draw" is the supported statement, not "a property of circuit size".
- **A partial seed biases a pooled statistic**, as §CORRECTION shows by moving p across 0.05. The
  script now excludes sections whose last seed is incomplete and prints a warning; it should have
  refused to compute a pooled statistic from an in-flight log at all.
- The log route cannot compute the absolute excess, because `e5`'s progress line does not print
  `oracle_final`. That is a gap in the *script*, not in the data — the JSONs carry it — and it is now
  a reason to prefer the JSON rather than a limitation of the finding.
