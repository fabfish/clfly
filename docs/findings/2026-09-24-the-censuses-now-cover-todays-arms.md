# The censuses now cover today's arms — and the cheapest constraint is a different method on each family

**Date:** 2026-09-24
**Scripts:** `experiments/e151_pertask_contrast_audit.py` and `experiments/e152_stability_plasticity_trade.py`,
both **extended** rather than re-derived, because both of their registries were fixed before the arms that landed
this evening existed: `e148`'s `replay` row on the shared-input family and `e147`'s second λ.
**Artifacts written by this fire:** `runs/e151_pertask_audit.json`, `runs/e152_trade.json`.

---

## 1. Why extending a registry is a unit of work and not housekeeping

Both readers were published with a **fixed registry**, and both findings said so — `e151`'s says *"the registry is
a fixed list of 22 contrasts rather than everything the artifacts could support"* and `e152`'s plane held nine
arms. Two consequences followed, and the second is the one that forced this fire:

1. the paper's quoted ranges had to be annotated (*"and 12.06σ for the arm … added afterwards"*) instead of being
   wrong, which is what the previous fire did; and
2. **a census that does not grow stops being a census.** The point of `e151` is that a *count over the record*
   either covers the record or says which part it leaves out; a frozen list is only honest while the arms inside
   it are all the arms there are.

So the registries were extended, the readers re-run, and the numbers they publish moved — the moved numbers are
below, and the paper's two sentences were updated to the new counts.

## 2. `e151`: 22 → 27 contrasts, and the third count the extension made necessary

| class | before | now |
|---|---|---|
| `fair` | 9 | **13** |
| `one term` | 5 | 5 |
| `hidden` | 5 | 5 |
| `null` | 2 | **3** |
| `weak pair` | 1 | 1 |
| `cancelling` | 0 | 0 |

**The five new contrasts split three ways**, and one of them is the census's largest effect:

- `e148`'s `replay` − `naive` on the shared-input family: **`fair`**, newest task **+0.0047 at 1.12σ** — the
  method that reaches zero forgetting pays nothing there, on the second family as on the first.
- `e148`'s `replay` − `ewc`: **`fair`**, newest **+0.0344 at 5.20σ** — replay beats that family's diagonal on
  *both* axes, not only on forgetting.
- `e147`'s frozen+penalised arm at λ = 3e-3 against the freeze and against `naive`: both **`fair`**, newest
  **−0.0651 (8.95σ)** and **−0.0917 (12.06σ)** — the second is the widest plasticity cost in the record.
- `e147`'s λ-against-λ: **`null`** on the forgetting (aggregate 1.46σ) — **and this row is why a third count was
  added.** Its label is a rule over the aggregate and the two forgetting terms, so it is silent about the newest
  task, where the same forty pairs resolve at **5.74σ**. A reader taking `null` for "no effect" would be wrong.

**The extended census counts that dimension separately: 2 of 27 contrasts resolve nowhere on the forgetting while
the newest-task column resolves** — that λ-against-λ row (1.46σ against 5.74σ) and the base family's
`block-rand` − `naive` row (0.28σ against 2.08σ).

**And the newest-task cost census moves from "ten of twelve" to "eleven of thirteen"**, range **2.08σ to
12.06σ**, with **the same two exceptions** — both `block` partitions — and `replay` at **0.79σ** on the base
family and **1.12σ** on the shared-input family.

## 3. `e152`: a second plane, and the two families do not agree about which constraint is cheap

The base plane gains the pair at λ = 3e-3 (**index 0.84**, newest **−0.0917 at 12.06σ**, the worst plasticity cost
recorded) and **keeps `replay` as its only undominated arm** — with the pair at λ = 3e-3 dominated by `replay`
alone, **resolved on one axis** (newest 12.47σ, forgetting **0.30σ**): the arm that matches the best method's
forgetting is exactly the one whose forgetting the dominance cannot separate.

**The shared-input plane is new, and its five arms give a different ordering of the exchange rates:**

| arm (shared-input family) | Δ forgetting | σ | Δ newest accuracy | σ | index |
|---|---|---|---|---|---|
| **`replay`** | **−0.0984** | 10.79 | **+0.0047** | **1.12** | **21.00** |
| frozen offsets | −0.0469 | 5.04 | −0.0245 | 4.07 | 1.91 |
| `ewc` (diagonal) | −0.0437 | 4.73 | −0.0297 | 4.57 | 1.47 |
| `block` | −0.0234 | 2.26 | −0.0047 | 1.10 | **5.00** |
| `block-rand` | −0.0216 | 2.48 | −0.0026 | 0.65 | **8.30** |

- **`replay` is the only undominated arm on this family too**, and by the widest margin in the record: it
  dominates `block` **resolved on both axes** (8.79σ / 2.07σ), `block-rand` resolved on one (8.40σ / 1.80σ) and
  the freeze resolved on both (6.84σ / 5.43σ) — while its own newest-task cost is **smaller than zero** at 1.12σ.
- **The diagonal is dominated by the freeze on point estimates only** (0.40σ / 0.70σ): by rule 40's grade that is
  a frontier position in name and not in evidence, and the honest sentence is that **on this family the diagonal
  and a frozen offset are not separated on either axis** — which is the same conclusion `e144` reached from the
  forgetting side alone, now with the plasticity column attached.
- **And the cross-family statement is the point**: on the base family the cheapest non-replay constraint is the
  **freeze** (index 1.97) with the diagonal at 1.19, while on the shared-input family the cheapest are the two
  **`block`** arms (5.00 and 8.30) and the diagonal falls to **1.47**. **The diagonal is the *worst* exchange rate
  among the shared-input family's constraints and the *second-best* on the base family**, so "which constraint is
  worth its cost" is a property of the task family and not of the method — and the family whose difficulty lives
  in the wiring is the one where the *coarse* partition is the cheap one.

## 4. What this cannot settle

- **Extended registries are still curated lists.** 27 contrasts and two planes are what these two readers cover;
  a third reader's worth of arms (the block arms under the freeze, any combination with `replay`) is outside them,
  and the counts above are counts *of the registry* and not of the record.
- The new arms' entries inherit every limitation the two findings already state: one read-out (32), three tasks
  (so the middle and last forgettable task are one column), point-estimate dominance with its grades, and
  `--frozen-bias` being a diagnostic rather than a method.
- **Two of the five new `e151` rows are duplicate arms under different labels** (`e147`'s λ = 3e-4 row already
  existed; the λ = 3e-3 row is new), so the class counts moved by less than five — the counts are over *rows*,
  which is why they are quoted as such.
- And the exchange-rate index remains **unitless**: a retention difference over an accuracy. It orders arms on
  this benchmark's scale and nothing more, and the cross-family comparison in §3 uses it only to say which side
  of a trade each arm is on.
