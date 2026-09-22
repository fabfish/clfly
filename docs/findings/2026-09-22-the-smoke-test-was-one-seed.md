# E51 — the 3-seed intervention reverses the 2-point smoke test, and the mechanism's direction survives where the law does not

**Date:** 2026-09-22
**Script:** `experiments/e49_kappa_leverage_by_topology.py`
**Artifacts:** `runs/e37_kappa_{real,swap2}_cs{800,300}.json`, `runs/e49_kappa_leverage.json`
**Context:** `2026-09-22-the-knob-is-inert-where-the-mechanism-was-proposed.md`, `2026-09-22-realization-attribution-refuted.md` §6b, plan rule 18

---

## 1. The caveat I recorded two fires ago was one seed

Two fires ago I added a caveat to `e36`'s finding §6b and to the plan: the `kappa` intervention
"already went the *other* way in a 2-point smoke test at cs = 300 — more concentration gave a *larger*
gap, which is `e5`'s sign at `real`, not `swap2`'s", and I marked the mechanism as the weaker reading
on that basis.

That smoke test was `--circuit-size 300 --kappas 0,1 --topology swap2` with `--seeds` left at its
default of **1**. The finished 3-seed run reproduces it in one seed and reverses it in the others:

| seed | `gap_EWC` at κ=0 → κ=1 | direction |
|---|---|---|
| 0 | 1.1244 → 1.2572 | **RISES** — this is the smoke test, to four decimals |
| 1 | 1.0316 → 0.8206 | falls |
| 2 | 1.3679 → 1.1040 | falls |
| **3-seed mean** | **1.1746 → 1.0606** | **falls** |

**The smoke test reproduced seed 0 exactly and the other two seeds disagree with it.** So the caveat
was a one-seed, two-point reading of a direction — and having been written into both the plan and a
finding, it has been shaping the mechanism's status for two fires. Both are corrected in place.

This is the third time in this sequence that a reading off the smallest possible sample has misled:
here (2 points, 1 seed), `e45` (a pooled statistic from a partial seed, which moved p across 0.05),
and `e36` (an "alternating sign" claim from four points). All three read a *shape or sign* from the
minimum sample that could produce one.

## 2. The intervention, now powered, at the one place it can test the mechanism

`swap2`/cs = 300 is the testable configuration — `e49` had established that `swap2`/cs = 800 is inert
(the knob travels 0.004 against a seed spread of 0.00044) because its precision is *already*
collapsed. At cs = 300 it is not:

| config | knob travel / seed noise | `effective_rank` κ0 → κ4 | verdict |
|---|---|---|---|
| `real` cs=800 | 142–146 | 55 → 2.0–3.5 | has leverage |
| `real` cs=300 | 262–271 | 48 → 1.9–3.1 | has leverage |
| **`swap2` cs=300** | **30.2, 29.6, 29.2** | **16.58 → 2.35** | **has leverage** |
| `swap2` cs=800 | 8.8, 19.3, 8.6 | 1.72 → 1.46 | inert / marginal |

And the mechanism's prediction is directional: **`excess(swap2)` is high when the effective rank is
high.** On the metric the plan's rule 3 prescribes, per seed:

| seed | ρ(absolute excess, flattening) | p | ρ(relative gap, flattening) | p |
|---|---|---|---|---|
| 0 | **+0.143** | 0.76 | −0.393 | 0.38 |
| 1 | **+0.214** | 0.65 | +0.036 | 0.94 |
| 2 | **+0.357** | 0.43 | −0.464 | 0.29 |

**All three seeds are positive on the prescribed metric — the mechanism's direction — and none is
significant.** Three-of-three agreement has p = 0.125 against a fair coin, so this is weak support and
not a confirmation. The relative gap, which `e5` reports, is sign-inconsistent across the same three
seeds and equally unresolved.

The seed-averaged curve says why the correlation is weak: it is **non-monotone**.

| κ | flattening | effective rank | absolute excess |
|---|---|---|---|
| 0 | 0.2435 | 16.07 | 0.07664 |
| 0.25 | 0.2313 | 15.27 | 0.07417 |
| 0.5 | 0.2072 | 13.67 | 0.06793 |
| 1 | 0.1486 | 9.81 | 0.06255 |
| 1.75 | 0.0851 | 5.62 | 0.06290 |
| 2.5 | 0.0536 | 3.54 | **0.03814** |
| 4 | 0.0318 | 2.09 | **0.08211** |

The excess falls from 0.0766 to 0.0381 across κ 0→2.5 and then **rises back above its starting value
at κ = 4**. So the relation is a U-shape, of the same kind `e5` found on the relative gap at `real`,
and a rank correlation is a poor summary of it.

> ### ⚠ SUPERSEDED, same day — the 3-seed "unanimous positive" was a subset of a null
>
> This finding read the `swap2`/cs = 300 intervention at **three** seeds as "+0.143, +0.214, +0.357 —
> the mechanism's direction, unanimously, none significant" and re-scoped the mechanism to
> *underpowered rather than refuted*. **`e52` has now run that configuration with twelve seeds, and
> three of them are the three this finding used:**
>
> | seeds | per-seed ρ on the prescribed metric |
> |---|---|
> | 0–2 | +0.143, +0.214, +0.357 ← what this finding reported |
> | 3–11 | +0.429, +0.821, 0.000, −0.286, +0.393, −0.643, −0.750, −0.786, 0.000 |
>
> At twelve seeds the counts are **6 positive, 4 negative, 2 tied**, sign p = **0.754**, mean
> **−0.009**, Wilcoxon p = **1.00**, pooled ρ = +0.076 (p = 0.49). **The direction is absent, not
> underpowered.** So this finding's §3 table row *"the ordinal direction at `swap2` — not refuted and
> not established"* becomes **"null at 12 seeds"**, and the honest model is no longer "a per-seed
> event in a minority of seeds" but "no effect on the metric the project prescribes".
>
> §1's withdrawal of the smoke test stands and is unaffected. This is the fourth instance in the
> sequence of a shape read off the smallest sample that could produce one, and the second time the
> culprit was **n = 3**.
> (`docs/findings/2026-09-22-mechanism-null-at-12-seeds-and-my-sign-test-was-wrong.md`)

## 3. Re-scoping the mechanism: the law is refuted, the direction is not

This separates two things the last four findings have run together.

| claim | status |
|---|---|
| **the quantitative law** — `excess ≈ a + b·ln(effrank)` with a shared `b`, and ±0.0034 bands | **refuted**: cross-family log slopes 13.6σ then 6.06σ apart, the two realization families agreeing on a *linear* slope (0.00116 each) that the circuit sweep overshoots 2.6×, `cs700` landing 1.84× outside the pre-registered band, and realizations inside the fitted range missed by 0.01902 |
| **the sign rule** across the five circuits | **refuted** above its bracket: a realization at effrank 5.853 gives −0.00377 at −10.0σ where the rule requires positive |
| **the ordinal direction at `swap2`** — the mechanism's own content | **not refuted and not established**: 3/3 seeds positive on the prescribed metric (+0.143, +0.214, +0.357) but p ≥ 0.43, over a non-monotone curve |
| `e36` §6b's smoke-test caveat | **withdrawn** — one seed of three (§1) |
| the `kappa` intervention at `swap2`/cs = 800 as a test | **cannot be run** — the knob is inert there (rule 18) |

So the honest position is narrower than "the mechanism is withdrawn on three axes" and wider than
"the mechanism is dead". **What died was the attempt to make it quantitative and predictive across
circuits. What survives, weakly, is the direction at the configuration it was proposed for — and it
is underpowered there (3 seeds, p ≥ 0.43), not confirmed.** The thing that would settle it is more
seeds of the `swap2`/cs = 300 sweep, not another coordinate.

## 4. Limits

- **Three seeds is not enough to support a direction** (p = 0.125 for 3/3), and it is being reported
  as weak support rather than as a result. The `κ = 4` point is doing most of the work in all three
  seeds and it is the single most extreme concentration in the grid.
- **The two configurations differ in `d`** (952 against 1307) as well as in whether the carrier is
  collapsed, so "testable only at cs = 300" is supported by the leverage measurement itself rather
  than by the size comparison.
- **The smoke test's numbers were correct**; what was wrong was reading a *direction* out of two
  points from one seed. The flag it was validating works, which is what a smoke test is for.
- `e42` — 12 seeds of the `real`/cs = 800 sweep — is still running and addresses `e5`'s mixing weight,
  not this. No run in flight addresses the `swap2`/cs = 300 direction.
