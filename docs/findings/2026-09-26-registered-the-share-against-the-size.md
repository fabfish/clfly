# Registered: the share against the size, decided at one circuit size that holds the other fixed

**Date:** 2026-09-26. **Registered before its runs.** Artifacts to be written:
`runs/e223_cs400_support80_rs{0,1}.json` (two runs, four cells each).

---

## 1. The confound the last two fires left

`e221` moved the *support* at cs 800 and got a clean answer for one half of the ladder: the **one-side level** is
**1.42×** higher at a 1.53% share than at a 12.24% share (0.07642 against 0.05374), and **the top step is not
organised by the share at all** (1.96× and 2.10× at those supports against the convention's 2.76×, non-monotone).

But every measurement in that comparison is at **one circuit size**, where the support count and the support share
move together: at cs 800, support 20 is 1.53% and support 160 is 12.24%, and neither is at the convention. The
circuit-size dependence of the one-side level (0.047–0.051 at cs 800 → 0.122–0.139 at cs 300–400) is therefore still
explained by **two candidates that have never been separated**: the share of the *neurons* engaged, or the circuit
itself (its neuron count, its assembly geometry, its edge density).

**The design that separates them is cheap and was already named**: run **cs 400 at support 80**, a **7.9% share**
(80 / 1010), which sits *between* cs 800's 6.1% and cs 400's own convention of 4.0% — so a share-driven level should
land between the two levels measured at those shares, and a size-driven level should stay at cs 400's convention
value.

## 2. The design

```
experiments/e2_topology_gap.py --circuit-size 400 --support 80 --seeds 3 --seed0 0 --q 0.02 \
  --topologies real,alloy1,inalloy1,erdos_renyi --rewire-seed {0,1} --no-realized \
  --json-out runs/e223_cs400_support80_rs{0,1}.json
```

`real` is included because its level has never been measured at a non-convention support either, so the design gets
the floor's own answer at a 7.9% share as well as the two one-side levels.

**Cost (rule 49)**: cs 400 cells took **≈93 s** in `e217` and `e219` (372 s for four cells and 300–314 s for three), so
four cells are ≈6 min per drawing and **≈12 min for both** — one command per drawing on an idle machine.

## 3. The claims

**S1 — the share, with a second circuit size holding the size fixed.** At cs 400, the one-side level's mean at
**support 80** is below its mean at **support 40** (the convention, `e217`/`e219`: 0.12480–0.13859, mean ≈0.1315) by at
least **1.5×**, i.e. at or below ≈0.0877. **Falsifier**: at or above the support-40 level (0.1315), which would say
the share does not lower the one-side level at cs 400 at all and that the cs-800 support effect was a cs-800
peculiarity. **Null**: a drop smaller than 1.5×, i.e. between 0.0877 and 0.1315.

**S2 — which candidate wins.** The one-side level at cs 400/support 80 lies **below the midpoint** of the levels at
the two shares it sits between — cs 400's 4.0% (≈0.1315) and cs 800's 6.1% (≈0.049), midpoint **≈0.0902** — i.e. it
tracks the **share** more than the **size**. **Falsifier**: at or above 0.1315, which would say the level is set by
the circuit and not by the share. **Null**: 0.0902–0.1315, a level that has moved toward the larger share but not
past halfway.

**Reported, not claimed**: `real`'s level at the 7.9% share (never measured at a non-convention support), and each
drawing's own values, so the two drawings' spread is visible beside the means — the cs-800 one-side spreads were
1.29× and 1.67× at supports 20 and 160, and a 1.5× bar against that is the reason S1's falsifier is written as an
absolute level rather than a ratio alone.

## 4. What this cannot do

- **It does not measure a share axis** — one new support at one new size is a two-point test of two candidates, and
  the share responds to *both* the support and the neuron count by definition.
- **It does not explain the top step**: `e221` showed the share does not organise it, and this design's four cells
  can report the top step at a 7.9% share without making the shape any more explained.
- **Two drawings per cell**, so every mean is a mean of two and the drawing spreads (1.29–1.67× at cs 800) are the
  same order as the effect being tested — which is why the claims are written as levels with an absolute falsifier.
- **Only cs 400 and cs 800**: cs 300 and cs 500–700 have their own conventions and are not part of this test.
