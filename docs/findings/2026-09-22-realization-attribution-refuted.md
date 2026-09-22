# E36 — the 367% spread is not a realization effect, and the C1 contrast's *sign* is a function of `swap2`'s rank collapse

**Date:** 2026-09-22
**Script:** `experiments/e36_geometry_carrier.py` (read-only over `runs/`)
**Artifacts:** `runs/e36_geometry_carrier.json`, `runs/e26_size400.json`, `runs/e26_size500.json`, `runs/e26_size600.json`, `runs/e32_rewire{0,1,2}.json`, `runs/e33_er_rewire{0,1}.json`
**Context:** `2026-09-22-swap2-unstable-not-scale-dependent.md`, `2026-09-22-er-separation-realization-exposure.md`, `2026-09-22-swap2-geometry-anomaly.md`

---

## 1. The claim I am testing, in one line

Two fires ago I attributed the 367% spread of `excess(swap2)` across four circuit sizes to
**re-drawing the swap realization**, and the last fire used that sd (0.0205) to argue the 152σ
Erdős–Rényi separation would fall to 4.5σ. Both readings leaned on a number that was **inferred**
from a sweep in which circuit size and realization vary together. `--rewire-seed` separates them, so
this fire measures it.

## 2. First, the published numbers reproduce exactly

Eight of eight, to five decimals, at the seeds the originals used:

| point | published | re-run | |
|---|---|---|---|
| cs300 (d=952) `real` / `swap0.5` / `swap2` | 0.01902 / 0.02257 / 0.05782 | identical | MATCH |
| cs800 (d=1307) `real` / `swap0.5` / `swap2` | 0.01830 / 0.02317 / 0.01237 | identical | MATCH |
| cs400 (d=1010) `swap2`, 6 seeds | 0.01762 | 0.01762 | MATCH |
| cs500 (d=1086) `swap2`, 6 seeds | 0.03492 | 0.03492 | MATCH |

Also worth recording because it was an untested assumption: `e32` run with no `--rewire-seed` at
cs=800 reproduces the published `0.01237` as the mean of its first three seeds, so **the flag's
default is realisation 0**, and the size sweep's points are comparable to the realisation runs.

## 3. The realization displacement, measured

Fixed circuit size (800), fixed six task seeds, only `--rewire-seed` varies:

| topology | realizations | sample sd | attributed sd | ratio | P(sd this small │ 0.0205) |
|---|---|---|---|---|---|
| `swap2` | 0.01255, 0.01350, 0.01503 | **0.00125** | 0.0205 | **16.3× smaller** | **0.0037** |
| `erdos_renyi` | 0.14176, 0.14223 | (n=2) | 0.0205 | — | 0.0128 |

For `swap2` the three-realization sd is 0.00125 on 2 df — a three-point sd is itself uncertain by
roughly a factor of two, and `e32` has three more realizations running — but it is **16× below** the
number the earlier fires used, and the χ² test rejects the attributed sd at p = 0.0037.

For ER the relevant statistic is the two-draw difference, paired over the four task seeds:
**+0.00047 ± 0.00065** (t = +0.72, n = 4), i.e. **0.33% of ER's own value**. Under the attributed sd,
two independent draws would differ by ~0.029; observing a difference this close to zero has
probability 0.0128. Independently for the two topologies, the attributed sd predicts a
**1-in-3000 coincidence**.

Note precisely what this is and is not. It is *not* a claim that realizations do not matter: the
paired t on `swap2` is +2.65, so re-drawing the rewiring does move the number, by 0.00095. It is a
claim that the movement is **about 1/20th** of the spread it was invoked to explain. The 367% is
therefore not realization noise, and the four points are not four draws from one distribution.

## 4. Consequence: the `e34` bound is void, and the direction it worried about is closed

`e34` was explicitly a sensitivity bound — "if ER's realization sd were as large as `swap2`'s
inferred 0.0205, the 152σ becomes 4.5σ". That input is now refuted by measurement, and ER's own
displacement is 0.00047, i.e. **65× below the 0.0305 that would take the separation to 3σ**. So the
152σ is not fragile in the way the last fire warned, and the correct scope statement for the ER
separation reverts to what it was before `e34`: single-realization, but not demonstrably
realization-limited. `e33` will put an sd on it; at two realizations it does not have one.

## 5. The new fifth point breaks the "alternating sign" claim

`e26` finished cs=600 (d=1149), which adds the fifth point to the contrast that carried C1's
interference refutation:

| d | effrank(`swap2`) | effrank(`swap0.5`) | `swap0.5 → swap2` Δ | σ | sign |
|---|---|---|---|---|---|
| 952 | 15.407 | 12.607 | +0.03525 | +21.8 paired | + |
| 1010 | 2.213 | 23.339 | −0.00304 | −4.8 paired | − |
| 1086 | 5.040 | 19.448 | +0.01054 | +14.5 paired | + |
| **1149** | **2.476** | **23.425** | **−0.00223** | **−4.4 paired** | **−** |
| 1307 | 1.703 | 19.271 | −0.01079 | −32.7 unpaired | − |

The paired contrasts at 952/1010/1086 reproduce the published +0.03525 / −0.00304 / +0.01054 to the
last digit, which is the check that the new point is on the same footing. Its sign is **negative**,
so the sequence is **+, −, +, −, −**: two consecutive negatives, and the "the sign alternates and
every step is decisive" headline from two fires ago was a property of having exactly four points.

## 6. What the sign is actually a function of

Ordered by `swap2`'s **effective rank** — the participation ratio of the task precision spectrum,
recorded by every run — the same five points are:

```
effrank(swap2)   1.703   2.213   2.476   5.040  15.407
Δ excess        -0.01079 -0.00304 -0.00223 +0.01054 +0.03525
sign               -       -       -       +       +
```

**Spearman ρ = +1.000, exact permutation p = 0.0083 one-sided.** Every positive contrast has
effrank ≥ 5.040, every negative one ≤ 2.476 — so a separating threshold exists anywhere in
**[2.476, 5.040]** and the sign of the refutation is *predictable without running the learning
experiment at all*. And because neither effrank nor the excess is monotone in d (15.4, 2.2, 5.0,
2.5, 1.7), this cannot be a restatement of "circuit size".

> **CORRECTION, same day, `2026-09-22-geometry-mechanism-refuted-on-the-realization-axis.md`.** The
> mechanism paragraph that followed this table has been **withdrawn**. Re-drawing the rewiring at
> fixed circuit size — a second way of moving the effective rank — gives log slopes **13.6σ apart**
> between `swap2` and ER (0.0047 ± 0.0009 against 0.0340 ± 0.0020) with the circuit sweep's own
> 0.0202 matching neither, and the five-point curve misses a new realization whose effective rank
> lies *inside* the fitted range by **0.01902**, 6.4× its in-sample maximum residual. So the table
> above is a true statement about five points and a useful **descriptive** coordinate; it is not
> evidence that the effective rank *causes* the excess, and the paragraph below should be read as a
> hypothesis that has since failed rather than as the finding.

The mechanism reads directly *(withdrawn — see the correction above)*: `swap2` is the only topology
in the family whose task precision **rank-collapses** (effrank 1.7–15.4 against `real`'s 43.8–50.2).
When the precision is dominated by one direction, protecting that direction is cheap and EWC lands
near the oracle, so its excess falls *below* its milder control's and the contrast turns negative.
When the collapse does not happen (effrank 15.4 at d = 952) the penalty is the largest in the family
and the contrast is positive.

On the level rather than the contrast, the same coordinate gives
`excess(swap2) ≈ 0.00280 + 0.02016 · ln(effrank)`, max residual 0.00296 over a range of 0.04545.

## 6b. And immediately, the first evidence against that mechanism

The mechanism in §6 is a reading of a *confounded* sweep: circuit size moves, the wiring moves with
it, and the effective rank moves as a consequence. The clean test is `e5`'s intervention — vary the
drive concentration `kappa` *within* a fixed wiring, which moves the effective rank without touching
the graph — and `e5` did not have a topology flag, so it had never been run at `swap2`. It does now
(`--topology` / `--rewire-seed` added, `experiments/e37`), and the 2-point smoke test used to
validate the new flag already goes the wrong way:

| `swap2`, cs = 300, `kappa` | effrank | flattening | gap vs oracle |
|---|---|---|---|
| 0 (uniform drive) | 16.6 | 0.2512 | **+1.1244** |
| 1 | 11.0 | 0.1661 | **+1.2572** |

More concentration (effrank falls) gives a **larger** gap — which is `e5`'s direction at `real`, and
the **opposite** of §6's cross-size relation, where a higher effrank goes with a higher excess. Two
points and one circuit size is not evidence, and cs = 300 is exactly where `swap2` is *least*
collapsed (effrank 16.6 against 1.7–2.5 at the negative-contrast points), so the regime may be the
whole story. But it means §6's mechanism is, as of this fire, **the weaker of the two readings**: a
cross-size rank correlation of ρ = 1 over 5 points, contradicted the moment concentration is moved
directly. The full run — 7 `kappa` values × 3 seeds, at `real` and at `swap2`, at both cs = 800 and
cs = 300 (`runs/e37_kappa_*.json`) — is what decides it, and if the direct intervention keeps
`e5`'s sign at both topologies then §6's mechanism paragraph should be withdrawn and the
cross-size correlation read as a coincidence of five points.

> **Outcome:** both §6 and the §7 coordinate below have since been **withdrawn**. The `cs700`
> point that §9 pre-registered as the decisive test landed and **missed the stated ±0.0034 band by
> 1.84×** (residual −0.00627), taking the six-point ρ from 1.000 to **+0.829** (exact p = 0.0292) and
> the fit's in-sample maximum residual from 0.00296 to 0.00512. Three `swap2` realizations had
> already failed the curve out of sample, and the cs=800 realization at effrank 5.853 fails the
> **sign rule** at −10.0σ because it sits above the bracket the rule named as the start of the
> positive region.
> (`2026-09-22-geometry-mechanism-refuted-on-the-realization-axis.md`,
> `2026-09-22-cs700-rejects-the-geometry-reading.md`)

## 7. Where the geometry reading stops, stated before it is oversold

*(withdrawn — see the outcome note in §6b; retained because it was written before the results and
records what was expected)*

- **It is ordinal, not calibrated.** The fit has 5 points and 2 parameters. Two genuine
  out-of-sample points are already in hand — `swap2` at the same circuit size, different rewiring —
  and they sit **+0.00341** and **−0.00773** off the curve. The second is 2.6× the in-sample maximum
  residual and 17% of the range. So the coordinate identifies **which end** of the instability you
  are at; it does not predict the value.
- **It is specific to the topology that collapses.** Across the same five circuit sizes the
  correlation is ρ = +0.400 (p = 0.26) for `swap0.5` and ρ = −0.100 (p = 0.61) for `real`. A
  constant ratio between a topology's excess and the `swap2` curve looks tidy for ER (2.03 ± 0.3%)
  but carries no slope information: ER's ln(effrank) leverage across its runs is **0.029**. Only
  `swap2` (leverage 2.373) can test the slope at all.
- **`effrank` is downstream.** It is computed from the same task build that produces the excess, so
  this is a diagnostic coordinate, not an intervention. The intervention that would license a causal
  reading is `e5`'s, applied at `swap2` — now launched (see §5b), because the smoke test
  **contradicted** the mechanism paragraph above.
- **Five points.** ρ = 1.000 at n = 5 has exact p = 0.0083, and leave-one-out stays 1.0 in all five
  deletions, which is more than the n = 3 version two fires ago had — but the threshold is a
  *bracket* [2.476, 5.040], not an estimate, and `cs700` is the sixth point.

## 8. Withdrawals and replacements, in one place

| earlier statement | status |
|---|---|
| "`excess(swap2)` moves with an sd of 0.0205 across realizations" | **withdrawn** — measured 0.00125 (16× smaller) |
| "substituting that sd turns the 152σ ER separation into 4.5σ" | **void** — input withdrawn; ER's measured displacement is 0.00047 |
| "the sign alternates, and every step is decisive" | **withdrawn at 5 points** — +, −, +, −, − |
| "`swap2`'s association with anisotropy runs opposite to `e5`, n = 3, default not a finding" | **upgraded** — n = 5, ρ = +1.000, exact p = 0.0083, leave-one-out all 1.0; the inversion is not noise |
| "the C1 refutation does not survive" | **survives as a description** — its sign across the five circuits is a monotone function of `swap2`'s effective rank |
| §6's **mechanism** (rank collapse *causes* the excess, and hence the sign) | **withdrawn same day** — log slopes 13.6σ apart across families, and a realization inside the fitted range missed by 0.01902 (`2026-09-22-geometry-mechanism-refuted-on-the-realization-axis.md`) |

Nothing in this fire restores the interference *hypothesis* either: the point is that the statistic
which refuted it is a deterministic function of a geometry that varies with the circuit, so a single
circuit's sign carries no general claim in either direction — and, after the correction above, the
geometry is a *description* of those five circuits rather than an explanation of them.

## 9. Pre-registered, for the next fire

`cs700` (d = 1229) is running. The two readings make numerically different predictions:

- **realization reading:** a fresh draw from a distribution with sd 0.0205 — 95% interval
  **[−0.01083, +0.06953]** (the interval is wider than the physical range; the reading is that the
  point carries no information about where on the curve it should sit);
- **geometry reading:** it lands on **0.00280 + 0.02016 · ln(effrank at cs700)**, a band of
  **±0.0034** (the wider of the in-sample max residual and the one out-of-sample residual already in
  hand) — **6× tighter**, and if it lands below 3 the contrast sign must be negative.

Also pre-registered: `e32`'s remaining three realizations will turn the 3-point sd of 0.00125 into a
6-point one; if it moves above ~0.004 the 16× ratio shrinks to 5×, and the withdrawal stands either
way but the margin changes.

## 10. Outcomes of §9, recorded here so the prediction and its result sit together

| pre-registered | outcome |
|---|---|
| realization sd stays below 0.004, so the ratio stays above 5× | **held** — 0.00303 at four realizations, ratio **6.8×**, χ² p = 0.0044. ER's is 0.00353, **5.8×**, p = 0.0069 |
| `cs700` lands inside the ±0.0034 geometry band around `0.00280 + 0.02016·ln(effrank)` | **the curve had already failed before `cs700` landed** — three other realizations gave residuals **+0.00341, −0.00773, −0.01902**, the last of which is 6.4× the in-sample maximum and lies at an effective rank *inside* the fitted range. `cs700` is now a further confirmation rather than a test |
| if `cs700`'s effrank < 3 the contrast sign must be negative | still open, and no longer load-bearing: the sign rule is a description of the five circuits, not a mechanism |

The third row is the honest state: the sign rule was never the part at risk, and the mechanism that
was supposed to explain it is the part that failed — see
`2026-09-22-geometry-mechanism-refuted-on-the-realization-axis.md`.
