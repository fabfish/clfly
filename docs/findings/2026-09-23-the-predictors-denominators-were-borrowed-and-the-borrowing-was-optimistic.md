# The predictor's denominators were borrowed, and the borrowing was optimistic

**Date:** 2026-09-23
**Script:** `experiments/e94_predictor_denominators.py`; artifact `runs/e94_predictor_denominators.json`
plus the fifteen `runs/e94_drawsd_*` measurements it wrote.
**Context:** `docs/findings/2026-09-23-the-predictors-denominators-came-from-the-other-circuit.md` (`e93`),
which found the borrowing and replaced one of its four conditions.

---

## 1. The result

`e93` found that `e64`'s headline count gave **20 of its 25 pairs a d = 1307 draw sd while those pairs ran
at cs = 300**, because `DRAW_SD_SOURCES` is keyed by rung and not by circuit size. `e86`'s cs = 300 half
matched one condition (`baseline`) and replaced five of those twenty; the remaining fifteen had no artifact
in their configuration, so `e94` measured them — the predictor's own five rungs at cs = 300 for each of
`wider-tasks` (support 60), `faster-drift` (q 0.10) and `rewired-swap2` (`swap2`), which last one required
giving `e12_control_spread.py` an opt-in `--topology` that defaults to `real`.

**With every one of the twenty borrowed denominators replaced by a measurement at its own configuration:**

| | borrowed (d = 1307) | measured at cs = 300 |
|---|---|---|
| pairs clearing 2σ | **21 of 25** | **20 of 25** |
| of those, called correctly | **20** | **19** |
| the one confidence failure | `rewired-swap2`/`cell_class` | unchanged |

Exactly one pair changes verdict, and it is the same pair in the *other* condition that was already
interesting:

| pair | σ with the borrowed denominator | σ measured | draw sd | call |
|---|---|---|---|---|
| `rewired-swap2`/`cell_type` | **2.32** | **0.87** | 6.802e-5 → 1.897e-4 (**2.79×**) | **right** |

So it leaves the resolved set as a *correct* call, and the "called correctly" count falls from 20 to 19 with
it — the correction moves both numbers in the direction of less support, which is the direction a correction
should move a claim that rested on a borrowing.

## 2. The part that makes it a finding rather than a correction: it was systematic

The twenty ratios between the measured and the borrowed draw sd, across all four cs = 300 conditions:

| condition | `side` | `cell_class` | `cell_type` | `ito_lee_hemilineage` | `supertype` |
|---|---|---|---|---|---|
| `baseline` | 1.51 | 5.26 | 1.34 | 4.93 | 2.23 |
| `wider-tasks` | 1.09 | 3.21 | 1.21 | 5.26 | 1.71 |
| `faster-drift` | 2.08 | 6.73 | 1.70 | 6.24 | 2.83 |
| `rewired-swap2` | 1.09 | 2.74 | 2.79 | 2.05 | 2.43 |

**All twenty exceed 1. The range is 1.09 to 6.73 and the median is 2.33.** This is not noise around a
correct value — it is a **systematic bias**: the control's draw-to-draw spread at cs = 300 (d = 952) is
larger than at cs = 1307 for the same rung, in every case, by a factor of two on average. A relabelling of a
partition perturbs a larger share of a smaller circuit, which is a plausible mechanism and not one this
project has needed to state before, because nothing had previously measured the same rung at two sizes.

**Three consequences that generalise past this count:**

- **A borrowed denominator is not a conservative placeholder.** It was wrong by 2.3× on average and always
  in the same direction, so it made every cs = 300 σ **optimistic** — the opposite of the usual worry about
  substituting a nearby measurement.
- **The largest σ corrections are not the ones that matter.** `faster-drift`/`cell_class` falls **11.79 →
  5.05** and `wider-tasks`/`cell_class` falls **13.47 → 6.46**, both by more than a factor of two, and
  neither changes a verdict because both stay far above the line. The count moves because of a pair that
  was *near* it — which is the same observation `e94`'s own pilot made about the Fisher-batch count, and the
  reason a count is a poor summary of a distribution of σ.
- **The direction of the error is knowable in advance.** Since the draw spread is denominated in the
  circuit, and the borrowing went from the larger circuit to the smaller, the sign of the bias could have
  been predicted from the mechanism rather than discovered from the measurement — which is what `e92`'s
  clause P5 is doing for `projection_pressure`'s level.

## 3. What remains, stated plainly

- **The count is now `20 of 25`, but it still rests on three task seeds per pair.** The paired seed sem and
  the measured draw component are combined as `hypot(seed_sem, draw_sd)`, with the draw sd **not** divided
  by `sqrt(draws)` — the conservative form `e64` chose — so these σ are floors, not estimates.
- **`e86` and `e94` used three task seeds where `e64` used six**, so each measured across-draw sd carries
  slightly more seed noise and is biased high, which makes every σ reduction here a **conservative upper
  bound**.
- **`rewired-swap2`'s denominators were measured at a rewiring drawn with `seed0 = 0`**, matching
  `e6_predictor.py`'s own `default_rng(args.seed0)`. A different rewiring is a different task geometry and
  would need its own measurement; the pair's σ is not a property of "swap2" but of this realization of it.

## 4. Corrections applied

- The paper's §5 headline, both places, and its §1 contribution bullet and §7 limitation: **21 of 25 →
  20 of 25** and **20 of 21 → 19 of 20**, with the systematic direction of the bias stated where the count
  is first given.
- The plan's C2b status line and its `e64` row: the same two numbers, plus the `(rung, circuit_size)` key
  that the fix requires.
