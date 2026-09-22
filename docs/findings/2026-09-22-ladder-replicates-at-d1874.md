# E9 — the granularity ladder replicates at a second configuration, with the peak in a different place and half the relative effect

**Date:** 2026-09-22
**Script:** `experiments/e3_basis_selection.py --ladder --circuit-size 1500 --support 150 --seeds 12`
**Artifacts:** `runs/e9_ladder_d1874.json` (d = 1874, support 150, oracle 0.06235, 12 seeds)

---

## 1. What was asked

The ladder was measured once, at d = 1307 with support 80, and everything downstream of it — the
plateau, the "pool the rarest cell types" recommendation, the predictor's rank correlation — rested
on that single configuration. `e9` re-runs it at **d = 1874 with support 150**: a 43% larger circuit
*and* wider tasks, 12 seeds, the same pooling device.

## 2. The rung-level result replicates

| rung | constrained (d = 1874) | delta | σ |
|---|---|---|---|
| `pool1` | 0.9657 | **+0.00035** | 1.6 |
| `pool2` | 0.8374 | −0.00586 | 28.4 |
| `pool4` | 0.7614 | −0.00722 | 39.2 |
| `pool8` | 0.6381 | **−0.00776** | 41.0 |
| `pool16` | 0.5307 | −0.00590 | 52.2 |
| `pool32` | 0.5102 | −0.00501 | 62.3 |
| `pool64` | 0.4004 | −0.00407 | 22.4 |
| `pool128` | 0.4004 | −0.00480 | 25.2 |

**Seven of eight rungs resolve** — the same seven-of-eight as the original, with the same exception:
`pool1`, which is the un-pooled `cell_type` partition, gives **+0.00035 at 1.6σ**. That is now the
**fourth independent confirmation** that the finest annotation rung buys nothing (0.4σ at d = 1307
with 12 seeds, 0.7σ with 18, 0.12σ at d = 952, and 1.6σ here). Every other rung beats its
group-size-matched random control, at 22–62σ.

The adjacent-rung contrasts tell the same story as before — **a curve with a broad interior maximum,
not a monotone trend**:

| contrast | Δ | σ |
|---|---|---|
| `pool1 → pool2` | −0.00621 | **20.7** |
| `pool2 → pool4` | −0.00136 | 4.9 |
| `pool4 → pool8` | −0.00054 | 2.1 |
| `pool8 → pool16` | +0.00186 | **8.5** |
| `pool16 → pool32` | +0.00088 | 6.4 |
| `pool32 → pool64` | +0.00095 | 4.8 |
| `pool64 → pool128` | −0.00073 | 2.8 |

Six of seven clear 2σ on the **unpaired** formula (this run predates per-seed storage, so the paired
figures are unavailable; for matched rungs the paired sem is smaller when the correlation is
positive, so these are conservative-or-optimistic depending on a sign that `e24` measured as
r ≈ −0.17…+0.23 for the *rung-level* contrast, i.e. near zero — so the unpaired formula is
approximately right here).

## 3. What does *not* replicate: the peak's position, and the effect's relative size

**The maximum moves.** |delta| peaks at constrained **0.540** at d = 1307 (`pool4`) and at **0.638**
at d = 1874 (`pool8`). Both are interior maxima on a broad plateau, and the plateau's width is
similar — but its location is configuration-dependent. That is exactly what the paper's limitations
section says ("the *shape* of the curve may be specific even if its lesson is not") and it is now
measured rather than asserted.

**And the effect is half as large in relative terms.** Comparing at matched granularity:

| | constrained | delta | oracle | delta / oracle |
|---|---|---|---|---|
| d = 1307, `pool4` | 0.540 | −0.00884 | 0.05195 | **17.0%** |
| d = 1874, `pool16` | 0.531 | −0.00590 | 0.06235 | **9.5%** |

So at the same granularity the biological advantage is **9.5%** of the oracle gap in the larger
configuration against **17.0%** in the smaller. The sign, the significance and the plateau all
replicate; **the magnitude does not** — it differs by a factor of 1.8 between two configurations that
differ in circuit size and task width together.

That is a real scope constraint on the recommendation: "pool the rarest cell types" survives, and the
*size* of what it buys is configuration-dependent by a factor of two.

## 4. The coarse-end degeneracy is systematic, not an accident

At d = 1307, `pool32 ≡ pool64` (both 3 groups) because only two cell types had ≥32 neurons. At
d = 1874, **`pool64 ≡ pool128` (both 3 groups)** — verified by comparing the label arrays directly:

```
d=1874: pool64 groups 3  sizes [1413, 263, 198]
        pool128 groups 3  sizes [1413, 263, 198]   ->  identical partitions
```

So each configuration has **six distinct partitions across eight rungs**, and in both cases the
duplicate is at the coarse end. That is a property of the *device* — a count threshold against a
cell-type size distribution whose median is 1 — and not of one circuit. Any future use of the ladder
should construct rungs by **rank** (merge the *k* smallest groups) rather than by threshold, which
would give eight distinct partitions by construction.

## 5. What this changes and what it does not

**Does not change:** the rung-level claim (biology beats a matched random partition over the coarse
range, replicated at two configurations and ~22–62σ), the `cell_type` null (four confirmations), the
plateau form (both configurations show a broad interior maximum rather than a monotone trend), or
the predictor's role.

**Changes:** the ladder is not a configuration-free object. Its peak position moves and its
*relative* effect size halves between two configurations. The paper now reports the curve as a
per-configuration measurement with a replicated *form*, rather than as a number.

**Raises:** the eight-rung ladder is six partitions at both scales, and two of the six are 2–3 group
blunt instruments. A rank-based ladder is the fix and is also what the synapse line needs
(`pool_buckets` was a partial answer there).

## 6. Limits

- **One alternative configuration** (d = 1874, support 150). Two points cannot separate circuit size
  from task width, and both differ here.
- **No per-seed storage** in this run, so the adjacent contrasts are unpaired. Given that `e24`
  measured the rung-level correlation as near zero, this is a small effect — but it is an assumption
  here rather than a measurement.
- The deltas are compared as fractions of the oracle gap, which differs between configurations
  (0.05195 against 0.06235); that normalisation is the project's convention but it is a choice.
- As throughout: one connectome, one species, and the ladder's rungs are annotated cell types rather
  than an ontology-free grouping.
