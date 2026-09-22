# E79 — the granularity ladder's per-seed check, at the second configuration: **8 of 8 rungs unanimous**, and the finest rung's disadvantage replicates

**Date:** 2026-09-23
**Script:** `experiments/e57_basis_ladder_seed_robustness.py --artifact runs/e79_ladder_d1874_perseed.json`
**Artifacts:** `runs/e79_ladder_d1874_perseed.json` (cs = 1500, d = 1874, 12 seeds), `runs/e83_ladder_d1874_robustness.json`
**Context:** `2026-09-22-c2-passes-the-per-seed-discipline.md` (e57), `2026-09-22-ladder-replicates-at-d1874.md` (e9), `2026-09-23-cell-type-is-not-a-null.md` (e66), plan rule 8

---

## 1. The gap, and why it was worth 5.6 hours

`runs/e9_ladder_d1874.json` is the granularity ladder at the **second configuration** — cs = 1500,
d = 1874, support 150, 12 seeds — and it stores **no `excess_per_seed` on any of its eighteen bases**. So
the family that carries claim C2 had its per-seed evidence at one circuit size only, and `e9`'s own
finding is the one a per-seed check should test: *the ladder replicates there in form and not in number*.

`e79` re-ran the byte-for-byte identical configuration with per-seed storage, and `e57`'s analysis now
takes an `--artifact` argument so that both ladders get the same treatment rather than two scripts that
drift apart.

## 2. The result, at the second configuration

| rung | groups | delta | seed sem | σ (paired) | signs | LOO min σ | flips | leverage |
|---|---|---|---|---|---|---|---|---|
| `pool1` | 812 | **+0.00035** | 0.00004 | **+9.85** | 12/12 **+** | 9.0 | no | 0.50 |
| `pool2` | 90 | −0.00586 | 0.00008 | −69.78 | 12/12 − | 63.7 | no | 0.50 |
| `pool4` | 29 | −0.00722 | 0.00018 | −39.95 | 12/12 − | 36.7 | no | 0.67 |
| `pool8` | 10 | −0.00776 | 0.00017 | −45.95 | 12/12 − | 42.0 | no | 0.57 |
| `pool16` | 8 | −0.00590 | 0.00010 | −58.03 | 12/12 − | 53.0 | no | 0.62 |
| `pool32` | 3 | −0.00501 | 0.00008 | −61.14 | 12/12 − | 55.8 | no | 0.51 |
| `pool64` | 3 | −0.00407 | 0.00018 | −22.45 | 12/12 − | 20.5 | no | 0.57 |
| `pool128` | 2 | −0.00480 | 0.00020 | −24.44 | 12/12 − | 22.3 | no | 0.50 |

**Eight of eight rungs have completely unanimous per-seed signs (12/12), no leave-one-out removal flips
any of them, the smallest leave-one-out σ is 9.0, and the largest single-seed leverage is 0.67** on a
scale whose ceiling is 1.

| | d = 1307 (`e57`) | **d = 1874 (`e79`)** |
|---|---|---|
| rungs with unanimous per-seed signs | 7 of 8 | **8 of 8** |
| smallest leave-one-out σ | 6.6 | **9.0** |
| largest single-seed leverage | 0.80 | **0.67** |

**So the second configuration is at least as robust as the first, and by both summary statistics it is
more so.** That is the answer to the question the per-seed check existed to ask, and it is the same answer
the pool ladder's *shape* got from `e9` — form replicates — with the numbers now checked rather than
assumed.

## 3. And the finest rung's disadvantage replicates

`e66` found at d = 1307 that the finest granularity is **not a null but a reliable disadvantage**: the
pooled `cell_type` partition's matched-control contrast is positive (biology worse) at 20.3σ paired,
because a near-diagonal partition's two arms co-move at ρ = 0.9987 and the unpaired sem is 27× too large.

At d = 1874 the same rung is **+0.00035 at 9.85σ paired, unanimous 12/12** — a different circuit size,
a different task suite, a different seed count, and the same verdict. That is the first *independent*
confirmation of `e66`'s reversal, and it is worth having because a single-configuration reversal is
exactly the shape of result this project has had to withdraw four times.

## 4. The crowding repeats, with the detail that started the draw-sd line

At d = 1307 the ladder's `pool32` and `pool64` are **the same partition** — only two cell types have
≥32 neurons — and their controls disagree at 4.7σ, which is where the entire draw-spread investigation
began. At d = 1874 the same thing happens one rung higher: **`bio:pool64` and `bio:pool128` are identical**
(same `constrained_fraction` 0.40041, same `n_parameters` 1053408, same excess 0.00121, same pressure
0.00607) — **while their controls are separate draws**, giving deltas of −0.00407 and −0.00480, a
**0.00073 disagreement**.

So the ladder has **eight rows and seven distinct biological partitions** at d = 1874, and the duplicate
pair's two controls differ by 0.00073 — about **one measured draw sd** for that partition family
(6.1e-4 to 7.3e-4 from `e14`), which is what two independent draws of the same control population should
differ by. The coincidence that originally exposed the single-draw problem is therefore not a quirk of one
circuit size; it is what this vocabulary does at every size, at whichever rung the group sizes thin out.

## 5. Limits, and one number that is not comparable

- **The draw sds in `e57`'s part 2 are all d = 1307 measurements.** Comparing them against the d = 1874
  ladder's seed sems is a comparison **across circuit sizes**; the script now says so, and computes the
  ratio rather than asserting it (5.1× at d = 1874 against "more than ten times" at d = 1307, which the
  first version of that line asserted flat). The substantive point — the draw component, not the seed,
  binds — stands, but the ratio at a second size is not measured.
- **σ (paired) is a statement about twelve task draws**, not about the partition population. The
  population-level reading needs a measured draw sd for the d = 1874 rungs, which does not exist; the
  ladder's rule-level σ therefore remains a d = 1307 quantity, and `e73`'s head-to-head is not
  recomputable at the second size.
- **One configuration each.** d = 1307 and d = 1874 differ in circuit size, support (80 against 150) and
  task geometry together, so "replicates across configurations" cannot be separated into which of those
  three it replicates across. That is a property of a connectome-derived substrate rather than of this
  design.
- **`e9`'s "form not number" claim is confirmed, not extended.** The deltas differ in magnitude between
  the two sizes (pool4 −0.00884 against −0.00722); what replicates is the ordering, the sign pattern and
  now the per-seed unanimity.
