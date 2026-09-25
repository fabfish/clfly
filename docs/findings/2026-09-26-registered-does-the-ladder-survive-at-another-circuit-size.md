# Registered: does the ladder survive at another circuit size?

**Date:** 2026-09-26. **Registered before its runs.** Artifacts to be written: `runs/e217_ladder_cs300.json` and
`runs/e217_ladder_cs400.json`.

---

## 1. What is being replicated, and why this is the claim to test

The four-construction result of the last fire is this week's headline: **the diagonalisation penalty follows how many
of the graph's two degree sequences a null destroys** — 0 destroyed ≈0.02 (`swap*`, `signshuffle`), **1 destroyed
≈0.045 by two independent routes** (`alloy1` mean 0.051, `inalloy1` mean 0.047), **2 destroyed ≈0.145**
(`erdos_renyi`) — a three-level ladder with a 7× top step, while the tasks' alignment is *decoupled* from it.

Every construction in that ladder was measured at **cs 800 with `seed0` 0**. This project's own standard, written into
its method notes after C1's history, is that a claim has to hold at more than one circuit size before it is quoted as
a property of the substrate rather than of one graph — and the ladder is exactly the kind of claim whose "levels" could
be a coincidence of one circuit's degree distributions.

## 2. The design

Two commands, four cells each, at the two circuit sizes the record uses most for C1's contrasts:

```
experiments/e2_topology_gap.py --circuit-size {300,400} --support {30,40} --seeds 3 --seed0 0 --q 0.02 \
  --topologies real,alloy1,inalloy1,erdos_renyi --no-realized \
  --json-out runs/e217_ladder_cs{300,400}.json
```

The four cells are the ladder's three levels: `real` (0 destroyed), `alloy1` and `inalloy1` (1 each, one per side),
`erdos_renyi` (2). `--support` is `circuit_size / 10`, which is this line's own convention (the d = 1307 ladder drives
80 neurons and the d = 1874 one 150 — 10% of the circuit in both).

**Cost (rule 49), from artifacts rather than from taste**: at cs 400, `e26_size400` took **584 s per cell** at six
seeds *including* the realized arm; at cs 800 this week's cells took **240 s** analytic-only at three seeds. Three
seeds and no realized arm at cs 300–400 therefore sit between those, so **10–20 min per size and 20–40 min for
both**, one command per size on an idle machine.

## 3. The claims, stated for EACH size separately

**Z1 — the top step.** At each size, `erdos_renyi`'s analytic excess exceeds the **larger** of the two one-side nulls'
by at least **1.5×** (at cs 800 the factors are 0.1419/0.0514 = 2.76 and 0.1419/0.047 = 3.02). **Falsifier**: within
**1.25×** at either size, i.e. no top step at that size and the ladder is cs-800-specific. **Null**: 1.25–1.5×.

**Z2 — the middle level is ONE level.** At each size, the two one-side nulls' excesses differ by at most **2×** (at
cs 800 the five-drawing means are 0.05136 and 0.04704, a ratio of 1.09). **Falsifier**: more than **2×** apart at
either size, which would say the two sides are not interchangeable and the ladder's middle is two levels rather than
one — the outcome that would break the ladder's shape while keeping its ends. **Null**: 1.5–2×.

**Z3 — the floor.** At each size, `real`'s excess is **below both** one-side nulls. **Falsifier**: `real` at or above
either one-side null at either size, which would say destroying one side can *lower* the penalty below the intact
connectome's and the ladder is not ordered.

**Reported, not claimed**: each cell's alignment and × chance, `top_eig_share`, `effective_rank`, `flattening`, and
the paired contrasts between adjacent levels — so the two sizes' ladders can be read side by side with cs 800's.

## 4. What this cannot do

- **Give a circuit-size trend.** Two sizes plus the existing cs 800 give three points and no relation; the claim here
  is only that the *ladder* appears at each size separately.
- **Separate the ladder from the support size**, which is held at the 10% convention rather than varied.
- **Replicate the top step's tightness or the middle level's spread**: one realization per cell per size, and the
  alloy's own five-drawing spread at cs 800 was 3.34×, so a single drawing at a new size is a point and not a level.
- **Speak for the sign pattern** (excluded at cs 800 by `e215` and not re-tested here) or for the network substrate.
