# E30 — the `swap2` anomaly is on the *geometry* axis too, and its association with anisotropy runs opposite to `e5`

**Date:** 2026-09-22
**Script:** analysis over `runs/e21_e2_paired.json`, `runs/e26_size400.json`, `runs/e2_analytic.json`
**Context:** `2026-09-22-swap2-scale-sweep-partial.md`, `2026-09-22-e5-anisotropy-axis.md`

---

## 1. The diagnostic

The sweep found `swap2`'s excess moving 4.7× across three circuit sizes while its two control
topologies held to 4–12%. The natural next question is **which side of the pipeline** the anomaly
lives on: the task geometry (the propagated observation covariance) or the filtering. Both are
recorded per topology, so it costs nothing to look.

| topology | d = 952 | d = 1010 | d = 1307 | **flattening spread** |
|---|---|---|---|---|
| `real` | 0.6643 | 0.6772 | 0.6920 | **4.2%** |
| `swap0.5` | 0.1910 | 0.3473 | 0.2654 | 81.8% |
| **`swap2`** | **0.2334** | **0.0329** | **0.0235** | **895%** |

`flattening = effective_rank / rank`, so **lower means more concentrated, i.e. more anisotropic**.
And `chance_alignment` — a property of the task construction, not of the rewiring — spans 24.8% for
every topology, as it should.

**`swap2` is an outlier on the geometry axis exactly as it is on the excess axis**: a 10× drop in
flattening between d = 952 and d = 1010, where the excess drops 3.3×. `real`'s geometry is flat to
4.2%. So the anomaly is not the filter behaving erratically on a fixed problem — **the rewiring
produced a different task geometry at d = 952**, and the excess followed.

That also narrows the mechanism search from the previous fire: conditioning was ruled out by
behaving oppositely at the two extremes, subsample composition by the flat controls, and now the
*pipeline* side is localised to the propagated task spectrum rather than the filter.

## 2. But the sign of the association contradicts `e5`

`e5` established the project's *replacement* mechanism: varying the task spectrum at **fixed
topology**, more anisotropy gives a **larger** gap (negative association with flattening, Spearman
−0.75). Applied to the three topologies here, where flattening is a *consequence* of rewiring:

| topology | flattening | excess | association |
|---|---|---|---|
| `real` | 0.664 → 0.677 → 0.692 | 0.0190 → 0.0182 → 0.0183 | flattening ↑, excess ↓ — **`e5`-consistent** |
| `swap0.5` | 0.191 → 0.347 → 0.265 | 0.0226 → 0.0207 → 0.0232 | flattening ↑, excess ↓ then reversed — **`e5`-consistent** |
| **`swap2`** | **0.233 → 0.033 → 0.024** | **0.0578 → 0.0176 → 0.0124** | both fall together — **opposite to `e5`** |

Within `swap2`, the *most* anisotropic point (d = 1307, flattening 0.0235) has the *smallest* excess,
and the least anisotropic (d = 952, 0.2334) has the largest. That is the reverse of "more anisotropy,
larger gap".

**Two of three topologies follow `e5` and one inverts it.** With three points each and no
intervention — flattening here is caused by the rewiring rather than varied independently — this is
not evidence against `e5`. But it is the first place in the project where the anisotropy story's
*sign* has come out backwards, and `e5`'s own finding notes the relation is U-shaped rather than
monotone, with the dip's mechanism unaccounted for. The honest reading is that **`e5`'s negative
association is a statement at fixed topology**, and applying it to configurations where the topology
is what varies is not licensed.

## 3. What would settle it

The same intervention `e5` used, applied at a rewired topology: vary the task's spectral
concentration at fixed wiring *and* fixed support, at `swap2` and at `real`. If the sign is the same
at both, the association is a property of the tasks and `e5` generalises; if it flips, then `e5`'s
relation is conditional on the wiring, which would be a more interesting result than either.

`e5_anisotropy_axis.py` already takes the topology-dependent circuit; the run is a few minutes and
has not been done.

## 4. Limits

- **Three points per topology**, and flattening within each is compared across *different
  subsamples*, so the association is between two graph-dependent quantities measured three times.
  A sample correlation of ±1 with n = 3 is the default, not a finding.
- `flattening` is computed from the task precisions *after* propagation, so it is downstream of the
  thing under study — it is a diagnostic co-ordinate, not an independent variable.
- The `chance_alignment` spread (24.8%, identical across topologies) shows the three sizes do not
  have identical task geometry to begin with, which is a floor on how cleanly any cross-size
  comparison can be made.
- §2's tension is with a *different* experiment's regime, and neither experiment was designed to
  test the other's.
