# E35 — the coarse end of a granularity curve is low-resolution by arithmetic, not by choice of device

**Date:** 2026-09-22
**Script:** arithmetic + the rank-based rung construction, over the d = 1307 and d = 1874 circuits
**Context:** `2026-09-22-ladder-replicates-at-d1874.md` §4, which recommended a rank-based ladder

---

## 1. The correction

The previous fire found that the ladder has **six distinct partitions across eight rungs** — at both
configurations, with the duplication at the coarse end (`pool32 ≡ pool64` at d = 1307,
`pool64 ≡ pool128` at d = 1874) — and recommended a **rank-based** device: merge the *k* smallest
groups rather than everything below a size, which gives eight distinct partitions by construction.

It does, and the construction is implemented and checked below. **But the recommendation was too
strong, and the reason is arithmetic.**

## 2. The bound

`constrained_fraction = 1 − Σ s(s+1)/2 / (d(d+1)/2)` for a partition of ``d`` neurons into ``m``
groups. Since ``Σ s² ≥ d²/m`` by Cauchy–Schwarz,

```
Σ s(s+1)/2 = (Σ s² + d)/2  ≥  (d²/m + d)/2

  ⇒  constrained  ≤  1 − (d/m + 1)/(d+1)
```

| groups ``m`` | 2 | 3 | 4 | 6 | 10 | 20 | 50 | 100 | 812 |
|---|---|---|---|---|---|---|---|---|---|
| **max attainable constrained** | **0.4996** | 0.6662 | 0.7494 | 0.8327 | 0.8993 | 0.9493 | 0.9793 | 0.9892 | 0.9980 |

The bound is essentially `1 − 1/m` and is **scale-free**: at d = 1874 it is identical to four
decimal places.

So **a rung at constrained 0.5 requires at most four groups, and anything below 0.67 requires at most
three.** The coarse end of the curve is reachable only by having few groups, and few groups means
blunt instruments. That is what the old device's 3- and 2-group rungs were, and it is not something a
better pooling rule can change.

## 3. What the rank device does and does not fix

Merging the *k* smallest groups, at d = 1307:

| ``k`` | groups | constrained |
|---|---|---|
| 0 | 812 | 0.9793 |
| 128 | 685 | 0.9698 |
| 256 | 557 | 0.9412 |
| 384 | 429 | 0.8933 |
| **512** | **301** | **0.8263** |
| **640** | **173** | **0.7401** |
| **760** | **53** | **0.6083** |
| **800** | **13** | **0.4688** |

**Fixes:** eight distinct partitions, no duplicates, spanning 0.469–0.979 — and it fills the
fine-to-mid range where the threshold device jumped from 0.979 straight to 0.674.

**Does not fix:** the coarse end. `k = 800` already merges 800 of the 812 cell types and leaves 13
groups at 0.4688; going coarser means absorbing the remaining large types, i.e. ``m`` dropping to 7,
4, 2 — and the bound above says what that buys. **There is no way to sample constrained < 0.47 with
more than about ten groups.**

## 4. The structural point this exposes

Put the bound beside the problem the ladder was built to solve. The annotation vocabulary's five
rungs sit at 0.50, 0.83, 0.967, 0.974, 0.979 — crowded at the diagonal, with an empty interval
between 0.50 and 0.83 — and the ladder exists to fill that interval. The bound says **why the
vocabulary is crowded there**: constrained ≈ 1 − 1/m, so *most* of the range is reachable with many
groups and only a narrow band near the diagonal is the crowded part... except the vocabulary's
crowding is at 0.97+, which needs m ≳ 30, and its sparseness is at 0.5–0.83, which needs m ≈ 4–10.

So the real statement is sharper than "the vocabulary places its rungs badly": **the annotation
hierarchy's coarse levels supply few partitions, and the fine levels supply many, which is exactly
the shape of the bound.** A partition into few groups is a coarse partition *because* it has few
groups; there is no ontology-free way to make many distinct coarse partitions out of 1307 neurons
and 812 cell types.

Which means: the earlier headline "the annotation vocabulary under-reports biology's contribution by
placing four of its five rungs near the diagonal" is right about the vocabulary and **wrong to imply
a device could do better**. The rank ladder does better in 0.47–0.98 and cannot do better below that.
The honest recommendation becomes: **anchor at the coarsest granularity the arithmetic allows you to
distinguish — around 0.5–0.7, i.e. 4–10 groups — and accept that the fine structure of the coarse end
is not measurable.**

## 5. What is still open

- The bound is on `constrained_fraction`, which is a *storage* proxy for granularity. Two partitions
  with the same ``m`` can differ in what they group, which is why the matched random control remains
  necessary — and it is why the coarse-end rungs (3 and 2 groups) are still compared against controls
  of the same size structure rather than dismissed.
- Whether the *optimum* of the delta sits where the bound makes rungs plentiful or where it makes
  them scarce is an empirical question the ladder has answered twice with the peak at 0.54 and 0.64 —
  both in the interior, so the answer is not at either extreme.
- Nothing here changes the rung-level result: the coarse rungs, blunt as they are, are where the
  effect is largest (0.0078 at constrained 0.64 against 0.0004 at 0.97).

## 6. Implementation note

The rank construction is a five-line function (`merge the k smallest groups`, with the merged group
appended) and is checked above on both circuits. It is **not** yet wired into
`candidate_bases` — the recommendation is now to use it for the *fine-to-mid* rungs, which is where
it adds six distinct partitions the threshold device does not have, and to keep the threshold device's
coarse behaviour implicitly by simply not claiming resolution there.
