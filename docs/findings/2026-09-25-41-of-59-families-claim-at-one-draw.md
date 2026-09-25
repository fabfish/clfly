# 41 of 59 families make manipulation claims at one draw — and the census found a read-out variation I had wrongly said did not exist

**Date:** 2026-09-25
**Analysis only, no runs.** `e200` checks that the two sides of a *declared* comparison drew the same thing, and today
established the complement it cannot see: **a family that varies a manipulation while holding every draw fixed** —
within-family effects attributable, generalization untested. `e198 --reconstruct` identifies the draw of 264 of the
299 live pairs, so the corpus can be asked this question directly. `e201` groups artifacts by the project's own
experiment id (`eNNN`), and for each family with ≥2 artifacts reports what varies and how many draws it used.

---

## 1. The census

| verdict | families | artifacts |
|---|---|---|
| **SINGLE-DRAW** — varies a manipulation, uses exactly one (read-out, support) draw pair | **41** | **215** |
| REPLICATED ACROSS DRAWS — varies a manipulation *and* a draw | 15 | 63 |
| **DRAW ONLY** — varies only a draw, i.e. a deliberate draw replication | 1 (`e117`, read-out seed) | 3 |
| replicates — varies nothing | 2 (`e164`, `e2`) | 4 |
| **total (families with ≥2 artifacts)** | 59 | 285 |

**215 of 285 artifacts (75%) live in families that make manipulation claims at a single draw.** The largest are the
ladder and geometry grids (`e92` with 60 artifacts varying `circuit_size`/`k`/`shape`/`support`, `e86` with 18, `e94`
with 16), then the basis rungs (`e10` 4, `e26` 4, `e3` 6), the rewire families (`e32`/`e33`/`e65`, 6 each) and the
two-point overlap families (`e140` 4, `e153` 2, `e164` 2, and the `rand_draw` pairs).

**And the two families that already answer the question deliberately are named**: `e117` varies only the
read-out seed (`e117_r128_draw1_20reps.json` and its siblings) and `e113` varies it alongside the size —
the corpus had done this before today, at sizes 128 and 300 rather than at the axis's 32.

**This is a map of exposure and not a verdict.** A single-draw family's *within-family* contrasts are attributable —
that is what `e200` confirms — and how much the draw matters is per-manipulation and measured only where it has been
measured: on this substrate the **support** draw moves the learning quantities by 3.3–6.6σ when the overlap moves, and
cancels in comparisons between arms at fixed supports, while the read-out draw is unresolved at size 32 (§3). So the
census's flag is a prompt to ask the magnitude question per family, not a defect list.

## 2. The census found a claim of mine that was WRONG

`e199`'s registration and its finding both say that `--readout-seed` "had existed since mid-project but no artifact in
the record was ever run at a second read-out draw". **That is false, and the census says so by listing `e113` among the
15 REPLICATED ACROSS DRAWS families.** `e113` holds **four artifacts at read-out size 300** — `readout_seed` 1, 2 and
3, each with `naive` × 5 replicates, plus a re-run of draw 1 — and one at size 512. The read-out draw had been varied
before today, at a size the axis does not use, and my claim of novelty was an artifact of not having looked.

**The correction does not change what `e199` measured** — it is the first read-out draw variation at **size 32**, the
size every claim on the overlap axis is stated at, with 40 replicates rather than 5. What it changes is the sentence
about novelty, and it hands over a *second* read-out size for free.

## 3. And the existing family qualifies `e199`'s conclusion

`e113`'s three read-out draws at size 300, `naive`, 5 replicates each:

| quantity | seed 1 | seed 2 | seed 3 | span | pairwise σ (2−1 / 3−1 / 3−2) |
|---|---|---|---|---|---|
| forgetting | 0.01458 | 0.02083 | 0.02083 | 0.00625 | 0.42 / 0.42 / 0.00 |
| accuracy | 0.94167 | 0.94722 | 0.94861 | 0.00694 | 0.69 / 0.73 / 0.12 |
| `learned (older)` | 0.95417 | 0.97083 | 0.96458 | 0.01667 | 1.37 / 0.71 / 0.80 |
| newest task | 0.94583 | 0.94167 | 0.95833 | 0.01667 | 0.21 / **2.45** / 0.75 |
| adjacent-pair interference | 0.02470 | 0.01949 | 0.02573 | 0.00624 | 0.40 / 0.06 / 0.61 |
| **distant-pair interference** | 0.03919 | 0.00098 | 0.00945 | **0.03820** | **2.76 / 2.08 / 2.63** |

**The distant-pair interference moves at 2.08–2.76σ between read-out draws at size 300**, on 5 replicates, with a span
of 0.0382 — as large as the *support* draw's effect on that term at the midpoint (0.08036 at 40 replicates, so
comparable in order). Every other quantity is unresolved.

So **`e199`'s "the read-out draw is the small one" is size-specific**: at read-out size 32 it is unresolved on all
twelve quantity-by-end combinations; at size 300 it is resolved on one term. That is what one would expect — a
300-neuron read-out is a far coarser measurement of the same state than a 32-neuron one — and it is worth stating
because `e199`'s finding generalized from the size the axis uses without saying so.

## 4. What this does not license

- **Treating the 215 single-draw artifacts as broken.** §1: their within-family contrasts are what they are, and the
  draw's magnitude is per-manipulation. What is unavailable is generalizing them beyond their draw.
- **Reading `e113`'s far term as a measured draw effect size.** Five replicates, three draws, one size, and 2 df; the
  pairwise σs are distances between specific samples, and today's own lesson is that a difference at n = 2 or 3 can be
  an outlier's distance.
- **Grouping by experiment id as if it were a design.** An `eNNN` group can mix designs — `e104`'s eight artifacts vary
  `frozen_body`, `input_overlap`, `methods`, `readout_size` and `shared_head` at once — so the census's "varies" column
  is a reading of the configs and not a designed axis.
- **That the census is complete.** Families with one artifact are skipped, and 35 of the 299 live (artifact, draw)
  pairs remain unidentified (`e198`).
