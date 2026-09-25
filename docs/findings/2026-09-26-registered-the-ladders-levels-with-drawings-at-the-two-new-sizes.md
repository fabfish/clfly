# Registered: the ladder's levels with drawings at the two new circuit sizes

**Date:** 2026-09-26. **Registered before its runs.** Artifacts to be written: `runs/e219_draws_cs{300,400}_rs{0,1,2}.json`
(six runs, three cells each).

---

## 1. The asymmetry the last read named

`e217` ran the ladder at cs 300 and cs 400 and its verdict was that the **top step does not replicate** — 1.28× at
cs 300 (Z1's null band) and 1.08× at cs 400 (Z1's falsifier) against cs 800's 2.76×/3.02× — while the **middle level**
(the two one-side nulls agreeing to 0.1% and 5%) and the **floor** (the intact connectome lowest) do.

But the comparison carries an asymmetry that the finding itself recorded as the first thing a replication should fix:
**the cs 800 levels are five- and three-drawing means** (`alloy1` from `e213`'s five drawings, `inalloy1` from
`e216`'s three) **while cs 300 and cs 400 are ONE drawing per cell** — and the alloy's own five-drawing spread at
cs 800 was **3.34×**. A single drawing's top step of 1.08× could therefore be a drawing rather than a level, in either
direction.

## 2. The design

Two sizes × three realizations, three cells each (the levels the top step and the middle level need):

```
experiments/e2_topology_gap.py --circuit-size {300,400} --support {30,40} --seeds 3 --seed0 0 --q 0.02 \
  --topologies alloy1,inalloy1,erdos_renyi --rewire-seed {0,1,2} --no-realized \
  --json-out runs/e219_draws_cs{300,400}_rs{0,1,2}.json
```

`real` is not re-run: it is the connectome, the rewiring does not touch it, and `e217`'s single cell per size is the
floor for every drawing at that size.

**Cost (rule 49)**: `e217`'s cs 300 run took **372 s for four cells** (≈93 s per cell) and its cs 400 run was similar,
so three cells per drawing are ≈5 min, three drawings ≈15 min per size and **≈30 min for both** — quoted from this
week's own measurements of the same command at the same sizes rather than extrapolated.

## 3. The claims

**R1 — the cs-800 top step is absent at both sizes, drawing by drawing.** At each size, the **mean** top step over the
three drawings is **below 1.5×**, and **no single drawing reaches 2.0×** (cs 800's values are 2.76× and 3.02×).
**Falsifier**: a mean at or above **1.5×** or any drawing at or above **2.0×** — which would mean the top step *is*
present at these sizes and `e217`'s single drawings understated it, i.e. the last finding's verdict was a drawing
artifact. **Null**: a mean below 1.5× with one drawing between 1.5× and 2.0×, which would make the top step
drawing-dependent at these sizes.

**R2 — the middle level's agreement is per-drawing.** At each size, in **every** drawing the two one-side nulls agree
within **2×** (cs 800: the five- and three-drawing means agree to 9%, and `e217`'s single drawings to 0.1% and 5%).
**Falsifier**: any drawing more than **2×** apart, which would say the one-level middle is a mean artifact and the two
sides are not interchangeable at every drawing. **Null**: a mean within 2× with one drawing beyond it.

**R3 — reported, not claimed**: at each size, the three drawings' **range** for each level (the one-side nulls, ER) and
for the top step, beside cs 800's own spreads (`alloy1` 3.34× over five drawings, `inalloy1` 1.24× over three, ER
1.05× over nine). The spread is the quantity this design exists to measure, and predicting it would pre-empt what it
is for.

**And the reading that follows either way**: if R1 holds, `e217`'s verdict stands on three drawings per size and the
top step's absence at cs 300/400 is a level; if R1's falsifier lands, the demotion of the top step was premature and
the ladder is intact at all three sizes — which would be a *correction of the correction* and the more interesting
outcome.

## 4. What this cannot do

- **Separate the support fraction from the circuit size**: `--support` stays at the 10%-of-circuit convention, so the
  hypothesis that the one-side level rises because supports are a larger share of a smaller circuit is not tested.
- **Give a distribution** in the sense of a quoted sd: three drawings are a range, which is this project's convention
  for a handful of samples.
- **Re-measure cs 800's levels with their own drawings** — they already have five and three — or equalise the drawing
  counts across sizes, which would need two more cs-800 cells and is not what the question needs.
- **Speak for the sign pattern** (excluded at cs 800 only) or for the network substrate.
