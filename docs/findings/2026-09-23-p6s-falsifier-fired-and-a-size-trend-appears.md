# P6's falsifier fired: the second shape stops decorrelating at d = 1307, and a size trend appears

**Date:** 2026-09-23
**Script:** `experiments/e92_grid_report.py`; artifact `runs/e92_grid_report.json`
**Data:** cs = 300 and cs = 800 are **both complete at 20 of 20 cells**; cs = 1500 has 8, all `flat`.
**Context:** `docs/findings/2026-09-23-the-concentration-matched-grid-preregistered.md` (clause P6),
`docs/findings/2026-09-23-the-grid-at-one-size-is-whole.md`

---

## 1. P6 failed on both of its thresholds, and its falsifier fired

P6 was written when d = 1307 had nine cells, all `flat`, with a concentration–target coupling of **+0.983**
and a partial of +0.654 whose profile bootstrap put **25% of resamples at or below zero**. It said the ten
`harmonic` cells would take the coupling **below +0.80** and the partial **above +0.654**, and it named its
falsifier: *the coupling stays above +0.90 with all twenty cells*.

| P6 | predicted | measured (20 cells) | |
|---|---|---|---|
| coupling | below **+0.80** | **+0.923** | **FAILS** |
| partial | above **+0.654** | **+0.618** | **FAILS** |
| falsifier: coupling above +0.90 | — | **+0.923** | **FIRES** |

**And the check P6 existed to protect came back yes anyway.** The d = 1307 partial is now **resolved**
where it was unreadable before:

| d = 1307, absolute form | 9 `flat` cells | 20 cells |
|---|---|---|
| partial | +0.654, p = 0.079 | **+0.618, p = 0.0048** |
| bootstrap at or below zero | **25.15%** | **0.20%** |
| leave-one-cell-out | +0.148 to +0.785 | **+0.552 to +0.669**, no sign flip |
| per-seed partials positive | 2 of 3 | **3 of 3** |

So the falsifier's first stated consequence — *the second shape does not decorrelate at that size* — holds,
and its second — *the partial there stays unreadable* — **does not**. The partial became resolved because
the grid doubled from nine cells to twenty, not because the confound was removed. **A clause can fire for
the right reason and be wrong about what follows**, and this is the first time in this project that a
pre-registered falsifier has done so: the mechanism it named was absent and the outcome it predicted in the
negative was absent too.

## 2. Why it failed: the decorrelation is size-dependent by a factor of four

The two complete sizes, absolute form, `flat` cells alone against both shapes:

| size | subset | n | ρ(concentration, target) | raw pressure | partial |
|---|---|---|---|---|---|
| d = 952 | `flat` only | 10 | +0.891 | +0.782 | +0.590 |
| d = 952 | **both** | 20 | **+0.677** | **+0.908** | **+0.919** |
| d = 1307 | `flat` only | 10 | +0.976 | +0.770 | +0.435 |
| d = 1307 | **both** | 20 | **+0.923** | +0.582 | **+0.618** |

**The second shape lowers the coupling by +0.214 at d = 952 and by only +0.052 at d = 1307 — four times
less** — and it moves the partial by +0.329 against +0.183. So the *design* half of the previous finding,
"The second shape is not decoration: it is what makes the statistic readable", **is a d = 952 result and
does not transfer.** At d = 1307 the second shape's real contribution is the ten extra cells.

**And at d = 1307 the second shape makes the raw correlation worse** — +0.770 → +0.582 — because the
`harmonic` profiles have *higher* measured draw sd at *higher* concentration, which flattens the monotone
relation the raw statistic reads. That is the same trade the grid was built to expose and the first time it
has been visible in the raw column: **adding a shape family that fills in the middle of the concentration
range costs raw rank correlation and buys partial rank correlation**, and which of the two it buys more of
depends on the circuit size.

## 3. And a size trend is emerging, in the same direction as `e82`'s

| size | cells | partial, absolute form | relative form |
|---|---|---|---|
| d = 952 | 20 of 20 | **+0.919** (p = 2.7e-08) | +0.955 |
| d = 1307 | 20 of 20 | **+0.618** (p = 0.0048) | +0.713 |
| d = 1874 | **8 of 20, `flat` only** | +0.120 | **−0.387** |

**This is not yet a result and must not be read as one** — the third row is 8 of 20 cells of one shape, so
it is a partial set, and rule 17's third shape is exactly about not quoting those. What it is worth
recording is that **if** it holds at 60 of 60, the partial spread statistic declines with circuit size
**0.919 → 0.618 → 0.120**, which is the **same direction and a similar shape** as `e82`'s co-movement
(mean *r* 0.923 → 0.906 → 0.810) and as the raw nine-partition correlations (+0.412 at d = 952 on the
bimodal set, +0.767, +0.800).

That would turn the cross-size question from *"the test is not well-posed"* into *"the statistic works and
works less well as the circuit grows"* — a weaker claim than the paper would like and a much better one than
either a pass or a fail, because two independent measurements of the same mechanism would agree on the
size dependence. **It is also the outcome that would make clause P1 — partial > 0 at every size —
technically pass while the paper's §4.3 sentence needs a third revision**, since "supported at two of three"
would become "positive at all three, declining significantly with size".

## 4. A third gate error, in my own report, of the kind this week has been about

With cs = 1500 crossing five cells, the report printed **P1 → PASS** (`d = 952 +0.919, d = 1307 +0.618,
d = 1874 +0.120`). It was gating on each size having **at least five cells**, so a size with **8 of its 20**
on disk counted as scored — a truncated set treated as the set, which is precisely the mistake this week's
audits kept finding in other tables (the `e86` range read off 5 of 9 rows; the `[:20]`-truncated scan).

The gate is now the grid's own expected size, and every clause line prints the per-size counts:

```
P1 partial > 0 at every size: ... -> PENDING (d = 952 20/20, d = 1307 20/20, d = 1874 8/20)
```

That is the **third** version of this one block — first it printed `FAIL` for a clause that was merely
unscored, then `PASS` on a partial set, and now `PENDING` with the counts that justify it. The lesson is
that a verdict gate needs the *target's* completeness test and not a proxy for it, and that a proxy chosen
for convenience (five cells) will be wrong in exactly the situation where the verdict matters.
