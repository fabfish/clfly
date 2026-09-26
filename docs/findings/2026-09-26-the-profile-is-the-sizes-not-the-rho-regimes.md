# The profile is the size's, not the `rho` regime's: at cs 800 the rank levels move by 20× between drawings

*2026-09-26 20:20. Runs: `e2_topology_gap` at `--circuit-size 800 --support 80 --seeds 3 --seed0 0 -q 0.02
--topologies alloy1,inalloy1,erdos_renyi --no-realized --rewire-seed 1`, one per `rho` (0.5, 0.7, 0.8, 0.95, 0.98,
0.99) — **six runs, ~11 min apiece, all exit 0** — `runs/e256_cs800_rho{05,07,08,095,098,099}_rs1.json`, read by
`experiments/e256_cs800_rank_curve.py` (`runs/e256_cs800_rank_curve.json`).*

## 1. Verdicts

**F1 FALSIFIER FIRED — the low-`rho` stability is cs 300's, not the regime's.** At cs 800 the new `alloy1` rank sits
within 1.00× of the corpus's at `rho` 0.5 but **1.25×** at 0.7 and **2.63×** at 0.8 (32.78 → **12.46**), against cs
300's 1.00×, 1.02× and 1.10×.

**F2 MET — the high-`rho` end moves there too, and far harder.** `rho` 0.95: 22.09 → **1.28** (17.2×); 0.98: 21.24 →
**1.04** (20.4×); 0.99: 21.01 → **1.01** (20.8×).

**F3 MET — the fall survives the new drawings**: 63.41 > 12.46 > 1.01.

**F4: the census's cs-800 exposure is closed — 0 of 15 registered figures name a single-drawing input.**

## 2. The two sizes' profiles side by side, which is the finding

| `rho` | cs 800 rank factor | cs 300 rank factor |
|---|---|---|
| 0.5 | **1.00×** | 1.00× |
| 0.7 | **1.25×** | 1.02× |
| 0.8 | **2.63×** | 1.10× |
| 0.9 | **9.80×** | 1.56× |
| 0.95 | **17.23×** | 2.34× |
| 0.98 | **20.41×** | 2.62× |
| 0.99 | **20.80×** | 1.03× |

**Every `rho` above 0.7 is drawing-dominated at cs 800 and none is at cs 300.** The profile of the drawing noise I
measured at cs 300 over the last three fires — "stable at the low end, explosive at the high end" — is therefore **a
property of the size and not of the `rho` regime**: at cs 800 the whole upper half of the curve is a drawing, and the
high end is not 2.6× unstable as at cs 300 but **20×** unstable. `e255`'s conclusion, that the census's flag on the
cs-300 cells was "a count of drawings rather than a measure of risk", does not generalise.

## 3. Why the reading is trustworthy, and what it is not

**Only `alloy1` moves.** At the same cells the new drawings give `inalloy1` 1.28 against the corpus's 1.29 and
`erdos_renyi` 5.47 against 4.20 — agreement to within 30% while `alloy1` is 20× away. That matters twice: it matches
`e230`'s "volatility belongs to the family, not the statistic" (`alloy1` is the volatile one on both rank and penalty),
and it **rules out the confound this record has been bitten by before** — a code epoch or a config difference between
the old and new artifacts would move every family, and the two artifacts' configs agree field for field
(`circuit_size` 800, `support` 80, `seeds` 3, `seed0` 0, `q` 0.02) with only `rewire_seed` differing (0 against 1).

**A mechanism candidate, stated as one.** The collapse is **shallower** at the larger circuit: at `rho` 0.99 the
corpus's cs-800 `alloy1` rank is 21.0, about **26% of the 80-neuron support**, against cs 300's 1.05, about **3.5% of
30**. A geometry that keeps a quarter of its rank near criticality has more room to be moved by which drawing it is,
while one collapsed to 3.5% has almost none — which is the same "ceiling" argument `e255` used at the low end, now at
the high end of the other size.

**And the cost of the reading is a knife-edge bar.** `e252`'s D3 was re-registered this fire from the count "6 of 38" to
a **share of a quarter** precisely because growth had fired the count twice; with the six new cells the exclusion now
removes **18 of 71 groups = 25.35%**, so the share bar fires too, by 0.35 of a point. A bar drawn on the corpus's
current size has the same problem as a count when the corpus is the thing that grows.

## 4. What the readers say with the new groups (71 of them now)

    e244 K1   null band (kind 1's median 1.218x with its range out to 78.48x)     K3 18 of 23 cell-pairs
    e246 N1   MET with the one-side span at 76.29x against the others' 6.11x      N3 -0.200, 33 of 63 pairs (52%)
    e247 R1   still a falsifier, and now count-matching changes NOTHING (76.29x -> 76.29x)
    e247 R2   null band: the pair-median separation falls to 1.262x while the two-lowest-seed one is 1.023x
    e252 D2   still a falsifier: only K1 and R2 return inside the domain

`e247`'s R1 is the one worth a sentence: the count-matching correction that halved `alloy1`'s span in its own fire now
does **nothing** (76.29× → 76.29×), because at cs 800 the family's cross-cell span is a **level** difference rather than
a sample-size one. So `e247`'s finding — "the spread is half sample size" — is itself size-dependent, holding where the
cells' drawing counts differed and not where the levels do.

## 5. And the drawing work has emptied `e230`'s audit, which is its instrument meeting its corpus

The same six drawings took the last single-drawing `rho` groups away at cs 800, so `e230` — whose verdict is computed
from the **as-read** contrast and skipped whenever a family has no one-drawing `rho` group — can no longer see the
cs-800 ladder families at all:

    cs 800 alloy1   sixteen-plus drawings at rho 0.9, and 21.01 against 1.29 in the contrast the record quotes
                    -> NOT RESOLVABLE, declared 18:20
                    -> at 20:20: between_single is None, so OUT OF SCOPE and un-declared

**Five of its forty-two families are still auditable** (cs 300 `real`, `signshuffle`, `swap0.5`, `swap2` and cs 800
`real`), and its declarations have gone from five to two in one session. That is worth stating rather than patching
quietly: an instrument built to read single-drawing cells **loses its subject as the corpus improves**, so the
questions it answered can only be re-asked by a different instrument — one that compares the *means* over drawings,
which `e230` already computes as its second column and does not judge on. The honest next form for it is a verdict on
the means, with the as-read column kept as a diagnostic.

## 6. What it cannot do

Two drawings per cell is **one difference and not a distribution**, and the two artifacts being compared are
`rewire_seed` 0 and 1 within one cell each, so "20× unstable" is a statement about that pair — though `e230`'s 16.44×
span for `alloy1` at cs 800/`rho` 0.9 over twelve drawings says the family's volatility there is not one pair's
accident. The two halves of the profile still come from two different sizes, so **size and `rho` remain confounded**:
cs 800/support 80 and cs 300/support 30 share the 10%-of-circuit support *fraction* but differ in neurons, edges,
assembly sizes and the ceiling each places on the rank. One `rho` per cell, no kind-0 families drawn there (so no
(1,0) margin), and no test of whether the cs-800 *excess* side behaves the same way at those `rho` values.
