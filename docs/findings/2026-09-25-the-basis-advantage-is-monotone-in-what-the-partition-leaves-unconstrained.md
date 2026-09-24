# Withdrawn: a read that re-derived §4.3's uncorrected column and its conclusion was already reversed in the paper

**Date:** 2026-09-25
**What happened:** this unit computed, from `runs/e3_seeds18.json`, the biological-versus-matched-random contrast
for the five annotation bases at eighteen seeds, and concluded that the advantage is monotone in the partition's
`constrained_fraction` and that `cell_type` is unresolved. **§4.3 of the paper already carries that table, and
already carries its correction — the correct contrast is *paired*, and `cell_type` resolves at 20.3σ.** The finding
is withdrawn, and the useful output is the check that would have prevented it.

---

## 1. What the read found, and what the paper says

The numbers I computed are §4.3's own 18-seed column, to the digit: `side` 28.78σ, `cell_class` 12.14σ,
`ito_lee_hemilineage` 9.32σ, `supertype` 4.26σ, `cell_type` 0.74σ, with the capacity matching exact (identical
`n_parameters` **and** identical `constrained_fraction` on all five pairs). §4.3 then does the thing I did not:
**it says those σ are the unpaired ones and that the correct contrast is paired**, because every basis in a run
sees the same task geometries in the same order — "a biological rung and its size-matched control are matched
observations". Its paired column is

| rung | σ, unpaired (my read) | **σ, paired (the paper)** | corr(bio, rand) |
|---|---|---|---|
| `side` | 28.78 | **31.7** | 0.210 |
| `cell_class` | 12.14 | **27.8** | 0.832 |
| `ito_lee_hemilineage` | 9.32 | **28.1** | 0.910 |
| `supertype` | 4.26 | **20.7** | 0.959 |
| **`cell_type`** | **0.74** | **20.3** | **0.9987** |

**So both halves of my conclusion are wrong.** `cell_type` is not unresolved: it is the rung whose pairing gain is
the *largest* (27.3×) because it and its control are "the same object to four decimal places" (ρ = 0.9987), and the
unpaired reading understates it by a factor of 27. And the "perfectly monotone in `constrained_fraction`" ordering
was an artefact of the unpaired sems: the paired σ run 31.7, 27.8, 28.1, 20.7, 20.3, which is **not** monotone in
that fraction (28.1 > 27.8).

## 2. The check that would have prevented it, and it is one grep

**I read §8's items and the corpus, and did not read §4.3 — the section the comparison belongs to.** The paper owns
this table, states the estimator question in the paragraph immediately under it, and gives the correction. One
`grep` for the artifact's name in the paper would have shown that `e3_seeds18` is already *the* cited source and
that both of its columns are there.

**So the rule this unit contributes is a reading order, not a result**: *before computing a comparison from the
corpus, read the section of the paper that owns it* — not because the paper is authoritative, but because the
paper may already contain the comparison **and its correction**, and re-deriving the uncorrected version produces a
confident claim that is not merely redundant but backwards. This is the fifth self-correction of the night and the
first that a document check, rather than an artifact check, would have caught.

## 3. What survives

- **The capacity matching is verified independently**: `bio:X` and `rand:X` share `n_parameters` and
  `constrained_fraction` exactly on all five pairs, so §4.3's comparison is matched-budget by construction and not
  by assertion. That is worth having as a *check* rather than as a finding.
- **§4.3 needs no edit.** Nothing in the paper was changed for this unit.
- **And the `constrained_fraction` column is not a law**: the paired ordering refutes the monotonicity the unpaired
  one suggested, so the hypothesis is dropped rather than queued.
