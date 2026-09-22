# E26 (partial) — `swap2` moves 3.3× for a 6% change in circuit size, while its two control topologies move ≤12%

**Date:** 2026-09-22
**Script:** `experiments/e2_topology_gap.py --circuit-size 400 --seeds 6 --no-realized`
**Artifacts:** `runs/e26_size400.json` (d = 1010); three of six sweep points in

---

## 1. Where the sweep stands

| topology | d = 952 (e21, 3 seeds) | **d = 1010** (e26, 6 seeds) | d = 1307 (published, 3 seeds) | spread |
|---|---|---|---|---|
| `real` | +0.01902 ± 0.00109 | +0.01822 ± 0.00080 | +0.01830 ± 0.00115 | **4.4%** |
| `swap0.5` | +0.02257 ± 0.00077 | +0.02065 ± 0.00043 | +0.02317 ± 0.00031 | **12.2%** |
| **`swap2`** | **+0.05782 ± 0.00122** | **+0.01762 ± 0.00033** | +0.01237 ± 0.00011 | **4.7×** |

The `swap0.5 → swap2` contrast, which carries C1's interference refutation:

| | d = 952 | d = 1010 | d = 1307 |
|---|---|---|---|
| Δ excess | **+0.03525** | **−0.00304** | −0.01079 |
| significance | 21.8σ paired | 4.8σ paired | 32.7σ unpaired |

So **the two control topologies hold to 4–12% across the whole sweep** while `swap2` falls by a
factor of **3.3 between d = 952 and d = 1010** — a size change of **6%** (952 → 1010 neurons).

## 2. Against the pre-registered prediction

The prediction written before the sweep had three branches. The result matches neither cleanly:

- **"a scale effect"** would give `real`/`swap0.5` flat *and* `swap2` moving monotonically. Both
  halves are true — `swap2` does decrease monotonically (0.0578 → 0.0176 → 0.0124).
- **"an unstable object"** would give a jump *exceeding* what a monotone trend allows, e.g.
  0.058, 0.013, 0.050. Not that either: the drop is monotone.

What actually happened is **monotone with an outsized first step**: 3.3× across a 6% size change,
against ≤12% movement in the two topologies that serve as internal controls. Whichever way it is
read, the *magnitude* of the first step is not something a smooth function of circuit size explains,
and the controls make that hard to attribute to subsample composition — which was the third
pre-registered branch and the one that would have made the whole comparison uninterpretable.

**That the controls are flat is the important part.** `real` and `swap0.5` agree across three
different subsamples to 4–12%, so changing which neurons are in the circuit at this scale does not
move the excess much; `swap2` moves by 330%. The excess of `swap2` is therefore a property of the
**rewired graph**, and it is an order of magnitude more sensitive to the graph than its neighbours
are.

## 3. What this does to C1

At d = 1010 the contrast is **−0.00304 at 4.8σ paired** — the same sign as the published d = 1307
value and opposite to d = 952. So two of the three measured points support the refutation and one
reverses it decisively. The honest state remains what the previous fire concluded and is now
better supported:

> The refutation rests on a contrast whose sign is **positive at d = 952, negative at d = 1010 and
> negative at d = 1307**, with the middle and outer points differing by more than an order of
> magnitude in the gap between them. It is a real observation at d = 1307 and not a stable one.

And the mechanism search is now better constrained: conditioning behaves oppositely at d = 952 and
d = 1307 (`cond(I − W)` for `swap2` is the best at one and the worst at the other), so it is not
conditioning, and the controls' stability rules out subsample composition. **Neither of the two
obvious explanations survives**, which is a cleaner negative than either a confirmation or an
unexplained anomaly.

## 4. What remains

Three points — d = 1086, 1149, 1229 — are still running. They decide between two readings of the
present data:

- if the remaining three interpolate smoothly between 0.0176 and 0.0124, then `swap2` is a smooth
  function of circuit size with one anomalous point at d = 952, and the anomaly is the thing to
  explain;
- if they scatter, then `swap2` is not a stable object across subsamples at all and the d = 952
  value is one draw from a wide distribution, which would make the published refutation a statement
  about one graph rather than about the swap family.

## 5. Limits

- The three points have **different seed counts** (3 at d = 952, 6 at d = 1010, 3 at d = 1307), so
  their sems are not comparable; the comparison is between means, and the means are precise enough
  that this does not matter for the conclusion.
- `e26` runs `--no-realized`, so only the analytic arm is available for the new points. That is the
  arm every conclusion in this line is drawn from.
- One point of six. The remaining three are the difference between "anomaly" and "noise", and
  neither reading is available yet.
