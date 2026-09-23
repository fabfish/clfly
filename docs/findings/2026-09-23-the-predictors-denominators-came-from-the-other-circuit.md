# The predictor's cs = 300 denominators were borrowed from d = 1307

**Date:** 2026-09-23
**Script:** `experiments/e93_cs300_draw_sd_upgrade.py`; artifact `runs/e93_cs300_draw_sd_upgrade.json`
**Artifacts read:** `runs/e64_predictor_per_seed_analysis.json`, and the five draw-sd sources it names
(`runs/e67_drawsd_side_min1.json`, `runs/e17_cell_class_drawsd.json`,
`runs/e17b_{ito_lee_hemilineage,supertype}_drawsd.json`, `runs/e67_drawsd_cell_type_min1.json`), plus all
nine `runs/e86_drawsd_cs300_*` measurements.
**Context:** the paper's §5 headline count, 21 of 25 pairs clearing 2σ.

---

## 1. The finding

The paper's §5 says the four cs = 300 conditions *"remain interpolated rather than measured"*. Reading the
artifact behind the count says something different and worse.

`experiments/e64_predictor_per_seed.py:33-40` holds a table called `DRAW_SD_SOURCES` with **five rows, keyed
by rung alone** — `side`, `cell_class`, `ito_lee_hemilineage`, `supertype`, `cell_type` — and no circuit-size
key. All five source artifacts are:

| source row | artifact | cs | d | support |
|---|---|---|---|---|
| `side` | `e67_drawsd_side_min1.json` | 800 | **1307** | 80 |
| `cell_class` | `e17_cell_class_drawsd.json` | 800 | **1307** | 80 |
| `ito_lee_hemilineage` | `e17b_ito_lee_hemilineage_drawsd.json` | 800 | **1307** | 80 |
| `supertype` | `e17b_supertype_drawsd.json` | 800 | **1307** | 80 |
| `cell_type` | `e67_drawsd_cell_type_min1.json` | 800 | **1307** | 80 |

`e64` scores five conditions, of which **four ran at cs = 300** (`baseline`, `wider-tasks`,
`faster-drift`, `rewired-swap2`) and one at cs = 800 (`larger-circuit`). Since the table has no size key,
the cs = 800 numbers are applied to the cs = 300 conditions:

> **20 of the 25 pairs in the headline count carry a d = 1307 denominator. Of those 20, the number measured
> at cs = 300 is zero.**

So those rows were not *interpolated* — nothing was fitted to them. They were **borrowed from the other
circuit size**, and the two errors need different fixes: a borrowing can be replaced by measurement wherever
the configuration matches, an interpolation cannot. Two of the four borrowed conditions are also mismatched
on support (`baseline` 30, `wider-tasks` 60, against the sources' 80), so the borrowing is a mismatch in two
coordinates at once for `wider-tasks`.

**And a lookup table keyed by one identifier when the quantity depends on two silently applies one cell's
value to another's.** That is the same question this line of work keeps asking — *what is actually being
compared?* — asked of a `dict` rather than of a partition.

## 2. What replaces it, and the answer is a negative result

`e86`'s cs = 300 half ran at **support 30, q = 0.02, real**, which is `baseline` exactly, for all nine
partitions at five draws each. So `baseline` — one of the four borrowed conditions, five of the twenty
borrowed pairs — can be re-derived from measurement:

| rung | cs = 300 measured (`e86`) | borrowed from d = 1307 | ratio |
|---|---|---|---|
| `side` | 3.246e-4 | 2.157e-4 | 1.51× |
| `cell_class` | **1.247e-3** | 2.371e-4 | **5.26×** |
| `cell_type` | 9.128e-5 | 6.802e-5 | 1.34× |
| `ito_lee_hemilineage` | **2.050e-4** | 4.158e-5 | **4.93×** |
| `supertype` | 1.865e-4 | 8.351e-5 | 2.23× |

Recomputing `baseline`'s five σ(rule) with `e64`'s own arithmetic, `|delta| / hypot(seed_sem, draw_sd)`:

| rung | σ, borrowed denominator | σ, measured denominator | verdict |
|---|---|---|---|
| `side` | 8.70 | 7.97 | unchanged |
| `cell_class` | **11.26** | **4.92** | unchanged |
| `cell_type` | 0.89 | 0.66 | unchanged |
| `ito_lee_hemilineage` | 11.15 | 10.65 | unchanged |
| `supertype` | 8.06 | 7.41 | unchanged |

**The count does not move: 21 of 25 before, 21 of 25 after, and no pair's verdict changes.** The largest
single correction in the whole exercise is `baseline`/`cell_class`, whose σ falls by a factor of **2.3** —
and it stays four times above the line.

## 3. What that negative result does *not* license

The robustness is a consequence of **where the affected pairs sit**, not of the denominator being
unimportant. Multiplying a cs = 300 draw sd by 5.26× moved one σ from 11.26 to 4.92, and both are far from
2; the one unresolved pair in that condition moved from 0.89 to 0.66, and both are far below. Nothing here
tests a pair near the boundary.

**And §5 records precisely such a pair elsewhere**: an earlier version of this count had its 2σ line fall
between `baseline/supertype` at **1.94** and `wider-tasks/supertype` at **2.17**, which is a configuration
where a factor of 2.3 in a denominator is decisive. So the honest reading is: *the headline count survives
the one replacement the existing data allows*, and the pairs that would be sensitive to a size mismatch are
in the three conditions that still cannot be replaced.

What remains borrowed is therefore **15 of the 25 pairs**: `wider-tasks` (support 60), `faster-drift`
(q 0.10) and `rewired-swap2` (`swap2`), none of which `e86` ran. Repairing them needs cs = 300 draw-sd runs
at those three settings — the same `e12_control_spread.py` protocol, nine partitions each, roughly the cost
`e86`'s cs = 300 half took.

## 4. Two caveats on the replacement itself

- **`e86` used 3 task seeds where `e64` used 6.** `e12`'s across-draw sd is measured on a fixed seed set, so
  the 3-seed value carries slightly more seed noise and is biased **high**, which makes every σ reduction
  above a conservative **upper bound**. Re-measuring `baseline`'s five sds at 6 seeds would tighten them.
- **The support mismatch is not repaired for `wider-tasks`,** and it is the one condition whose support
  differs from `e86`'s; even a cs = 300 run at support 30 says nothing directly about support 60.

## 5. Corrections applied

- The paper's §5, which said the four cs = 300 conditions "remain interpolated rather than measured": the
  mechanism is corrected to *borrowed from d = 1307*, with the 20-of-25 and 0-of-20 counts, and the
  robustness of the headline count is added where the claim is made.
- §4.3's companion sentence that the cs = 300 conditions "remain interpolated rather than measured" likewise
  points here.
- The plan's `e64` row records the defect so the next run of that table cannot repeat it, and the fix — a
  `(rung, circuit_size)` key — is named rather than left to be rediscovered.
