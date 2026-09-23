# E73 — the ladder and the named rungs, on the same footing: 26.1σ against 13.7σ, not an order of magnitude

**Date:** 2026-09-23
**Script:** `experiments/e73_ladder_named_head_to_head.py`
**Artifacts:** `runs/e3_ladder_v2.json` (12 seeds), `runs/e58_bases_18seeds_perseed.json` (18 seeds), `runs/e73_ladder_named_head_to_head.json`
**Context:** `2026-09-23-cell-type-is-not-a-null.md` (e66), `2026-09-22-control-drawn-once.md`, `2026-09-22-c2-passes-the-per-seed-discipline.md` (e57)

---

## 1. A comparison the paper makes that its own two halves do not support

§4.3 says the five-rung table's best rung is *more* decisive than every corrected ladder rung. Both
sides of that were computed by different procedures:

* the ladder's corrected σ (the famous "**4–9σ** instead of 20–42σ") used **unpaired** seed sems of
  0.0002–0.0005 and an **assumed** 1.0e-3 draw sd;
* the named rungs' σ are now **paired** (every basis in a run sees the same task geometries in the same
  order) and use **measured** draw sds.

Neither correction is optional and neither belongs to one family alone, so the comparison as printed is
apples-to-oranges. This script applies both steps to both families.

## 2. Both families, paired, with measured draw sds

| family | rung | delta | sem unpaired | sem **paired** | pairing gain | σ(task) | draw sd | **σ(rule)** |
|---|---|---|---|---|---|---|---|---|
| ladder | `pool1` | +0.00019 | 0.00051 | 0.00003 | **19.6×** | 7.3 | 6.80e-5 ▣ | 2.6 |
| | `pool2` | −0.00801 | 0.00032 | 0.00034 | **0.9×** | 23.3 | 9.29e-4 ▣ | 8.1 |
| | `pool4` | −0.00884 | 0.00021 | 0.00020 | 1.1× | 44.4 | 6.13e-4 ▣ | **13.7** |
| | `pool8` | −0.00685 | 0.00023 | 0.00022 | 1.0× | 31.0 | 7.07e-4 ▣ | **9.3** |
| | `pool16` | −0.00765 | 0.00020 | 0.00020 | 1.0× | 38.8 | 6.68e-4 ▣ | **11.0** |
| | `pool32` | −0.00699 | 0.00018 | 0.00019 | 1.0× | 36.4 | **7.41e-4** ▣ | **9.1** |
| | `pool64` | −0.00548 | 0.00026 | 0.00027 | 1.0× | 20.4 | **7.41e-4** ▣ | **7.0** |
| | `pool128` | −0.00409 | 0.00023 | 0.00023 | 1.0× | 17.9 | 9.65e-4 ▣ | **4.1** |
| named | `side` | −0.00477 | 0.00017 | 0.00015 | 1.1× | 31.7 | 2.16e-4 ▣ | **18.1** |
| | `cell_class` | −0.00319 | 0.00026 | 0.00011 | 2.3× | 27.8 | 2.37e-4 ▣ | 12.1 |
| | `cell_type` | +0.00026 | 0.00035 | 0.00001 | **27.3×** | 20.3 | 6.80e-5 ▣ | 3.8 |
| | `ito_lee_hemilineage` | −0.00296 | 0.00032 | 0.00011 | 3.0× | 28.1 | 4.16e-5 ▣ | **26.1** |
| | `supertype` | −0.00145 | 0.00034 | 0.00007 | 4.8× | 20.7 | 8.35e-5 ▣ | 13.3 |

▣ = a measurement of that partition; ▢ = no measurement, the published 1.0e-3 carried as an **upper
estimate** (which *lowers* σ(rule), so those three are floor values).

## 3. The head-to-head, which is not the one printed

**The best named rung is 26.1σ and the best ladder rung is 13.7σ** — a factor of **1.9**, against the
"order of magnitude" the uncorrected tables implied (the ladder was printed at 20–42σ against the named
table's 4–9σ, i.e. the ladder looked *stronger*; corrected the same way, the named family is stronger by
a factor of two rather than weaker by ten).

**And the ladder's column is now fully measured rather than a floor.** `e74` supplied the three rungs
that had none — `pool8` **7.07e-4**, `pool16` **6.68e-4**, `pool128` **9.65e-4**, each at `e14`'s own
protocol (3 task seeds, 5 draws) so the points sit beside the old ones. All three came in *below* the
1.0e-3 the tables had assumed, which is why their σ rose rather than fell: `pool8` 6.7 → **9.3**,
`pool16` 7.5 → **11.0**, `pool128` 4.0 → **4.1**. So the earlier "floor" caveat is discharged, in the
direction that *widens* the ladder's spread and leaves the 1.9× factor unchanged.

## 4. The reason the two published tables were not comparable: the pairing gain is family-dependent

| | pairing gain |
|---|---|
| the pool ladder, all eight rungs | **0.9× – 1.0×** (except `pool1` at 19.6×) |
| the named rungs | **1.1× – 27.3×** |

The gain is governed by the correlation between a partition's biological and control arms across task
draws, which for a near-diagonal partition is essentially 1 (ρ = 0.9987 for `cell_type`). The ladder's
rungs are *pooled cell-type* partitions — coarser, less correlated arms — so for them the unpaired sem
was nearly right, while for the named family's finest rung it was 27× too large.

**So the two published tables carried the same two errors in different amounts, and the direction of
the difference flipped with the pairing gain.** One rung of the ladder pays for pairing (`pool2`, gain
0.9× — the paired sem is *larger* than the unpaired, the negative-correlation case the project's
`paired_delta` already documents), and one named rung gains 27× from it.

## 5. Limits

- **Every ladder rung now has a measured draw sd of its own.** `e74` supplied the last three (`pool8`
  7.07e-4, `pool16` 6.68e-4, `pool128` 9.65e-4, at `e14`'s protocol) and `e90` supplied the pair that had
  been *borrowed* from a neighbouring partition: `pool32` and `pool64` are **the same partition** at
  d = 1307 (both pool to 3 groups), and their own spread is **7.41e-4**, where the row previously used
  `e14` min 2's **9.29e-4** — 25% too high, so their σ moved from 7.4 to **9.1** and from 5.7 to **7.0**.
  Nothing in the head-to-head rests on a borrowed number any more, and the factor stays **1.9×**.
- **Different seed counts (12 against 18) and one circuit size.** The head-to-head compares two families
  measured by different runs; the footing is now the same, the artifacts are not.
- **σ(rule) is the honest axis for this comparison** and it is not the one the paper's tables report;
  both families' printed σ are σ(task)-like.
