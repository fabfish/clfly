# Registered: the overlap axis at three intermediate levels, priced, with the x-axis measured first

**Date:** 2026-09-25
**Registered before its runs.** Three commands, no artifact yet. **Reads:** `e188`'s and `e191`'s two-point contrast
(overlap 0.0 against 1.0) and `e7`'s six-level controlled sweep on the analytic line.

---

## 1. Why this is the next experiment and not another read

`e188` measured that raising the input overlap from 0 to 1 raises the network line's forgetting in nine of nine
comparisons, and `e191` measured the same rise on the line's **own interference terms** — the adjacent-pair
component **+0.1234 ± 0.0158 = 7.8σ** on the unpenalised arm, rising in eight of nine comparisons — while the
analytic line's adjacent-pair interference **falls** monotonically over six levels and crosses below zero.

**Two points give a direction and not a shape, and the shape is what separates two readings the direction cannot**:
"overlap raises forgetting" (a graded response) from "**any** overlap is enough" (a step). The analytic line already
has the six levels; the network line has two. So this is the axis's own missing measurement, and it is cheap.

## 2. The x-axis, measured before the runs exist

The levels are set by `overlap_controlled_supports` (the same construction `make_overlap_suite`'s docstring says
`e7` used), and the achieved overlap is deterministic given the seed. Computed **now**, on the circuit these runs
will use (`mb+cx+al@n1307`, `--circuit-size 800`, 3 tasks of 80 neurons, seed 0):

| target `--input-overlap` | achieved Jaccard, and the three pairs agree | in `e7`'s controlled sweep |
|---|---|---|
| 0.00 | **0.0000** | 0.0000 |
| 0.25 | **0.1429** | 0.1429 |
| 0.50 | **0.3333** | 0.3333 |
| 0.75 | **0.6000** | 0.6000 |
| 1.00 | **1.0000** | 1.0000 |

**So the two lines' axes are commensurable without conversion** — the analytic block's `achieved_overlap` column is
reproducible on the network's circuit to four decimals, which is what makes the shape comparison in §4 legitimate.

## 3. The design and its price

Three commands at the **same** configuration as the two-point contrast, differing only in `--input-overlap`:

```
--input-overlap 0.25 / 0.50 / 0.75, cs = 800, read-out 32, --methods naive,ewc-block,ewc-block-rand, --repeats 40
```

**Cost, from the artifacts' own `timing_s` rather than from an extrapolation** (rule 49):

| artifact | methods | replicates | its own cost | per arm-replicate |
|---|---|---|---|---|
| `e133_r32_naive_ewc_40reps.json` | 2 | 40 | 4560 s | **57.0 s** |
| `e140_r32_methods_plastic_40reps.json` | 5 | 40 | 19220 s | 96.1 s |
| `e159_r32_overlap1_methods_rerun.json` | 5 | 40 | 11553 s | **57.8 s** |

3 levels × 3 methods × 40 replicates = **360 arm-replicates**, i.e. **5.8 h at 58 s each and 9.6 h at 96 s** — the
same order as `e178`, and affordable as one command per level if the queue prefers that.

## 4. The registration

**P1 — monotone, and more than half done by the midpoint.** The adjacent-pair interference at achieved overlap
0.3333 lies strictly between its values at 0.0 and at 1.0, **and is closer to the 1.0 end than to the 0.0 end**.
(For `naive` that is between +0.1330 and +0.2564, and above +0.1947.)

**P2 — the shape matches the analytic line's timing.** The analytic near component completes **80%** of its fall by
achieved overlap 0.3333 (+0.0258 → +0.0051 of a total fall to −0.0013). If the two lines' adjacent-pair responses
share a mechanism with opposite sign, the network's near rise should be **≥ 60% complete by achieved 0.3333**.

**Falsifier — the axis is a step, not a slope.** The near component at achieved 0.1429 equals its 1.0 value within
2σ: then *any* overlap suffices and the 0→1 rise is not a graded response.

**Null worth keeping — the intermediates are individually unresolved.** Three ~1σ rises whose means sit between the
ends would leave the *direction* standing on the two-point contrast while the shape stays unmeasured, and that is a
statement about the effect's size rather than about its existence.

**Read instrument:** `e191` (the name-matched interference split) and `e188` (the accuracy-drop contrast), which
take artifact paths rather than a design, so the read is one command per level.

## 5. What would make this registration wrong rather than merely refuted

- **The achieved overlaps could move** if the circuit's seed set changes between now and the runs: §2's table is a
  property of `mb+cx+al@n1307` at seed 0, and a different circuit changes every cell. The artifacts record the
  target `input_overlap` and **not** the achieved Jaccard, so a reader must recompute §2's table for the circuit
  the run used — which is why the table is here rather than in the read.

  > **CORRECTION, 2026-09-25: this bullet is wrong in its first half and right in its second, and the wrong half
  > mattered.** The table is **not** a property of the circuit: `overlap_controlled_supports` builds a shared pool
  > plus disjoint private complements, so ``|A_j n A_k| / size`` is *exactly* the target and the Jaccard is exactly
  > ``o / (2 - o)`` for **any** `n`, `size`, `T` or `seed` — checked on three circuit sizes and three seeds, and the
  > five cells reproduce the formula to four decimals (0.25 → 0.1429, 0.5 → 0.3333, 0.75 → 0.6). So no recomputation
  > is needed, the axis carries **no measurement error**, and `e7`'s agreement is not independent confirmation but the
  > same construction evaluated twice — which is *stronger* than a sampling agreement, since the two lines' x-axes
  > need no conversion at all. **The second half stands and is the real gap**: which neurons each task drives depends
  > on the circuit and the seed and is recorded in no artifact, so what is unrecorded is the supports' *identity*, not
  > their overlap. The table is now bound to the construction by a test rather than by a comment, so a change to
  > `overlap_controlled_supports` fails there instead of silently moving the x-axis of a multi-hour run
  > (`docs/findings/2026-09-25-the-x-axis-is-arithmetic-not-a-measurement.md`).
- **The cost is per arm-replicate and the machine's load has varied by 67%** across the five artifacts in §3, so
  5.8–9.6 h is a range and the artifact's own `timing_s` is the only figure to quote afterwards.

## Reproduce

```
uv run python -m experiments.e191_interference_across_lines     # the two-point basis this design extends
uv run python -m experiments.e188_overlap_contrast              # the accuracy-drop version of the same basis
```
