# `e136`: the barrier's hard cases do not persist — not the pairs, and not the seeds

**Date:** 2026-09-24
**Script:** `experiments/e136_geometry_persistence.py` (new); artifact `runs/e136_geometry_persistence.json`.
**Grids:** the three stored geometry runs, which used the **same twelve seeds** (`0 + 100k`) and therefore the
**same 66 pairs** — `runs/e130_barrier_r32.json`, `runs/e124_barrier_12seeds.json` and
`runs/e131_barrier_r1307.json`, each read at checkpoint 2.
**Context:** `docs/findings/2026-09-24-the-barrier-orders-like-the-bodys-load.md`, which established that the
barrier's **level** is set by how much the body carries at the read-out, and whose §5 says *"three read-outs is
still a curve on three points"*. **This asks a question about the grids rather than about the curve.**

---

## 1. The three answers

**The per-pair barriers do not correlate across read-outs — and what correlation there is runs negative:**

| | Pearson | Spearman |
|---|---|---|
| read-out 32 vs 128 | **−0.224** | −0.313 |
| read-out 32 vs 1307 | −0.142 | −0.226 |
| read-out 128 vs 1307 | −0.046 | −0.012 |

**The worst-ten sets barely overlap, and this is the cleanest evidence because it needs no correlation model:**

| | shared |
|---|---|
| 32 vs 128 | **1 of 10** |
| 32 vs 1307 | **1 of 10** |
| 128 vs 1307 | **1 of 10** |
| **all three** | **0 of 10** |

| read-out | its five worst pairs |
|---|---|
| 32 | 0/300, 0/700, 300/700, 500/800, 500/700 |
| 128 | **400**/1000, **400**/600, **400**/700, 700/1000, 0/400 |
| 1307 | **100**/1100, **100**/800, **100**/700, **100**/500, **100**/900 |

**And it is not the seed either.** Each seed appears in eleven pairs, so a seed's own level is the mean barrier
over those eleven; the twelve seeds give a 12-vector per read-out, and those are **also negatively correlated**
across read-outs: **−0.337** (32 vs 128), −0.135 (32 vs 1307), −0.201 (128 vs 1307).

**So the barrier has no transferable ranking.** Which pair is hardest to connect is redetermined at every
read-out, and no seed carries a tendency to be hard from one to the next.

## 2. What does organise each read-out, and it is a different seed each time

The per-seed means are not flat, and their shape changes with the read-out:

| read-out | worst seed | its level | median seed | **ratio** |
|---|---|---|---|---|
| 32 | **0** | 0.2916 | 0.2245 | **1.30×** |
| 128 | **400** | 0.0814 | 0.0506 | **1.61×** |
| 1307 | **100** | 0.0807 | 0.0214 | **3.77×** |

**The concentration grows as the read-out widens** — 1.30× to 3.77× — and that is exactly what the two limits
should give. At read-out 32 the median barrier is **0.2245 of chance**, so *every* seed is hard to connect and
none stands out; at read-out 1307 the median is **0.0214** and the barrier is all but absent, so the few pairs
that do rise are those involving **one seed that landed somewhere unusual** — and seed 100 sits in **four of the
five** worst pairs. **"Which seeds are hard to connect" is therefore a question that has an answer only at a wide
read-out, and the answer is a different seed at each read-out.**

## 3. Why this matters, and it is stronger than the caveat it sharpens

`e124`, `e130`, `e131` and the paper's §4.2 paragraph all carry the same limitation — *"one read-out"* — and the
reading they invite is that the **level** is configuration-specific. This says something more: **the identity of
the hard cases does not survive either.** `e124`'s sentence *"the worst pair is 400 and 1000"* is a fact about
read-out 128 and about nothing else; at read-out 32 the worst pair is 0/300 and 400/1000 is not in the top ten,
and at read-out 1307 the worst is 100/1100 and neither appears. **A single-read-out geometry study cannot be read
as a statement about the seeds**, and the natural next question a reader would ask — *"are some seed pairs
intrinsically hard to connect?"* — has a measured answer: **no, not in this benchmark.**

**And it closes the same door the forgetting side has closed twice.** `e121` found the fit depth carries no
information about retention across forty seeds; `e124` found the barrier is not the pair's disagreement in
retention. This adds that the barrier is not the pair's identity either. **Three different pair-level
descriptions, three nulls** — which is what a connected, over-parameterised set with no pair-level structure
should look like.

## 4. What this cannot settle

- **The correlations are descriptions of these three grids and not estimates of a population.** 66 pairs come
  from 12 seeds, so the effective `n` for a pair-level correlation is 12 and for the seed-level one it is 12; two
  of the three are around −0.3, and twelve points cannot resolve that. **What needs no model is the overlap: 0 of
  10 across all three read-outs.**
- **They are all negative and that is not a mechanism.** Non-persistence would give ≈ 0; three negative
  correlations of −0.05 to −0.34 are three draws near zero, and reading them as *"a seed that is hard at one
  read-out tends to be easy at another"* would be reading a sign into unresolved numbers. The honest statement is
  **no evidence of persistence**, not evidence of anti-persistence.
- **Three read-outs, one draw each, one circuit, one task order.** A fourth read-out, or the same three with a
  second read-out draw, could find a pair that persists by chance — the worst-ten overlap is exactly the
  statistic that would show it, and 1 of 10 pairwise is already one more than the 0.9 expected if the two sets
  were independent draws from 66.
- **And the seeds' levels are means over eleven dependent pairs**, so a seed's "hardness" is partly the read-out's
  level and only partly its own; §2's ratios are ratios of means and not of a seed's intrinsic property.
