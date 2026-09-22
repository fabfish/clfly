# E46 — the C2b rung contrast's −0.0648 was three seeds; at sixteen it is +0.0039

**Date:** 2026-09-22
**Artifacts:** `runs/e46_c2b_powered.json`, `runs/e31_methodlist_check.json`
**Context:** `2026-09-22-rung-question-resolved-at-lambda-0.1.md`, `2026-09-22-network-variance-is-learner-variability.md` (`e38`), `2026-09-22-naive-arm-census.md` (`e54`), plan rule 19

---

## 1. The best-powered C2b measurement, and it is a null

`e46` is `e31`'s configuration — `cell_class`, λ = 0.1, `fisher_batches` 8, `iters` 500, cs = 800 —
with **sixteen** replicates instead of three, which is the count `e38` specified for a 0.03 effect.

| arm | final accuracy (n = 16) | per-replicate sd |
|---|---|---|
| `naive` | 0.841 ± 0.010 | 0.0411 |
| **`ewc-block` (biological)** | **0.825 ± 0.015** | 0.0615 |
| **`ewc-block-rand` (matched control)** | **0.821 ± 0.012** | 0.0477 |

**Biological minus matched random: Δ = +0.0039 ± 0.0161** (paired over the sixteen seeds) — a 0.24σ
null whose detection floor is **0.032**. Forgetting: Δ = −0.0111 ± 0.0227 (0.49σ).

And the reproduction check passes exactly: **e46's first three replicates equal `e31`'s six values
bit-for-bit, on both arms.** So the comparison is legitimate and the config is identical.

## 2. Which makes this a retraction, because the three-seed answer was −0.0648

Per-replicate paired deltas, in seed order:

```
-0.0278  -0.0556  -0.1111  +0.1181  -0.0208  +0.0833  -0.0347   0.0000
-0.0972   0.0000  +0.0347  +0.1042  +0.0069  +0.0278  -0.0069  +0.0417
```

| first k seeds | mean Δ | sem | σ | signs |
|---|---|---|---|---|
| **3** | **−0.0648** | 0.0245 | **−2.65** | `---` |
| 6 | −0.0023 | 0.0353 | −0.07 | `---+-+` |
| 9 | −0.0162 | 0.0252 | −0.64 | `---+-+-+-` |
| 12 | −0.0006 | 0.0214 | −0.03 | `---+-+-+--++` |
| **16** | **+0.0039** | 0.0161 | **+0.24** | `---+-+-+--++++-+` |

**The first three seeds are the three most negative of the sixteen** (−0.0278, −0.0556, −0.1111), and
they are the entire effect. Three more seeds take it from −2.65σ to −0.07σ: **the result did not decay
as n grew, it died at the sixth seed.** The sixteen-seed signs are **7 negative, 2 tied, 7 positive** —
a perfect split.

## 3. What this withdraws

The plan's `2026-09-22-rung-question-resolved-at-lambda-0.1.md` is the project's one *positive* C2b
result: at λ = 0.1 the rung contrast resolves, with `side` at +0.0069 (0.48σ) against `cell_class` at
**−0.0648 (2.65σ)**, and the paired cross-rung contrast `side − cell_class` at +0.0718 ± 0.0336 (2.13σ,
same sign in all three replicates). Its mechanism reading was that *the coarse rung wins because the
fine rung loses to its own control, not because the coarse one gains*.

**The main term of that is now +0.0039 ± 0.0161.** So:

| claim | status |
|---|---|
| "at λ = 0.1 the rung contrast resolves" | **withdrawn** — `cell_class` is +0.0039 ± 0.0161 at n = 16 |
| "the coarse rung wins because the fine one loses to its own control" | **withdrawn** — the fine one does not lose to its control |
| "`side` is +0.0069 (0.48σ)" | unchanged, and it was already a null |
| the paired `side − cell_class` contrast at 2.13σ | **loses its main term**; `side` needs its own 16-replicate run before the contrast can be restated |

So the C2b ladder is nulls at **every** rung and **every** λ now tested — and where the earlier
statement was "four λ = 1.0 rungs are nulls but the λ = 0.1 rung resolves", the honest position is
**"the best-powered measurement in the line is a null, with a floor of 0.032"**. That is a stronger
negative than the plan had, not a weaker one, because it is now the *well-powered* configuration that
is null.

## 4. The noise floor at n = 16, which `e38` predicted

| arm | per-replicate sd | evaluation share | training |
|---|---|---|---|
| `naive` | 0.0411 | 0.0305 (**55%**) | 0.0276 |
| `ewc-block` | 0.0615 | 0.0317 (**26%**) | 0.0527 |
| `ewc-block-rand` | 0.0477 | 0.0319 (**45%**) | 0.0354 |

At sixteen replicates the evaluation floor is 26–45% of the variance, and removing 90% of
`ewc-block`'s share would take its sd from 0.0615 to 0.0536 — **1.15×**, consistent with `e38`'s 1.28×
bound from a different run. The required replicates for a 0.01 effect are **167**; for 0.03, **19**.

## 5. The fourth time n = 3 has misled, and the general form

Plan rule 19 says a smoke test does not read a direction and its `n` must be quoted beside any figure
taken from it. This is that rule's more general form:

> **a pooled figure needs its `n`, and every `n` below about ten in this project has eventually
> reversed.** `e51`/`e52` (3 seeds: the mechanism's direction), `e45` (3 seeds: "a minority of seeds"),
> `e36` (4 points: "the sign alternates"), `e42` (3 seeds quoted as the result for three fires), and
> now `e46` (3 seeds: the C2b rung contrast). Each was a legitimate computation on the data available;
> in each case more seeds reversed or nulled it.

The cheap guard is the one `e47`/`e57` apply: **compute the per-seed values and look at them before
quoting the pooled number.** Here that would have shown the three negative seeds immediately — and
`e46`'s own cumulative table shows the effect dying at k = 6, which no summary statistic at k = 3 could
have revealed.

## 6. Limits

- **Sixteen seeds, one configuration.** This is `cell_class` at λ = 0.1. It says nothing directly about
  `side`, `ito_lee_hemilineage`, or λ = 1.0 — though the four λ = 1.0 rungs were already nulls at
  three replicates.
- **The null is bounded at 0.032**, not at zero. A 0.03 effect is still undetected by this run, and 19
  replicates would be needed; the honest statement is *"any advantage is below ~0.032 accuracy at 80%
  power"*, not *"there is no advantage"*.
- **`e46` adds the `naive` arm**, so its three-arm structure differs from `e31`'s two-arm one — but the
  first three replicates of both EWC arms reproduce `e31` bit-for-bit, so the arms are independent of
  the method list, which is the check `e31` itself was run to establish.
- **The run took 6,869 s (1.9 h)** at the λ where the contrast was supposed to be largest, so the
  remaining rungs at 16 replicates are affordable — `side` is the one that would complete the
  cross-rung contrast.
