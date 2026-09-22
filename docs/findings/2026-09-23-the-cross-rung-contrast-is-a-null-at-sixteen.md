# E76 — the C2b cross-rung contrast at sixteen replicates is a **null**, and the line's last outstanding figure is now closed

**Date:** 2026-09-23
**Script:** `experiments/e76_c2b_cross_rung_powered.py`
**Artifacts:** `runs/e60_side_lam0.1_16reps.json` (`side`, new), `runs/e46_c2b_powered.json` (`cell_class`), `runs/e76_c2b_cross_rung_powered.json`
**Context:** `2026-09-22-the-c2b-rung-result-was-three-seeds.md` (e46), `2026-09-22-rung-question-resolved-at-lambda-0.1.md` (withdrawn), `2026-09-22-network-line-settled.md`

---

## 1. What `e46` left open, and what closes it

`e46` is the project's best-powered C2b measurement — `cell_class` at λ = 0.1 with sixteen replicates,
where the published three-replicate figure had been −0.0648 (2.65σ) and is **+0.0039 ± 0.0161
(0.24σ)**. It closed with the one thing it could not do:

> the paired `side − cell_class` contrast at 2.13σ **loses its main term**; `side` needs its own
> 16-replicate run before the contrast can be restated.

`e60` is that run, and it is the same configuration in every field that matters:

* **23 config fields compared, 0 differ**; the only differing field is `basis` — `side` against
  `cell_class` — which is the variable under study;
* the **`naive` arms are bit-identical across all sixteen replicates**, which is the check that the
  replicate seeds are aligned. `naive` carries no basis and no penalty, so it is the one arm the two
  runs *must* share exactly, and if they did not share it every paired figure below would be
  meaningless.

## 2. Each rung at sixteen replicates

| rung | metric | delta | sem | σ | signs | LOO min σ | flip | published (3 replicates) |
|---|---|---|---|---|---|---|---|---|
| `side` | accuracy | **−0.01519** | 0.01278 | **1.19** | `+-+-0+++---+--+-` | 0.72 | no | +0.0069 / 0.48σ |
| `cell_class` | accuracy | **+0.00391** | 0.01615 | **0.24** | `---+-+-+-0++++-+` | **0.08** | **yes** | −0.0648 / 2.65σ |
| `side` | forgetting | **+0.02409** | 0.01976 | **1.22** | `++---+--+++-++-+` | 0.79 | no | — |
| `cell_class` | forgetting | **−0.01107** | 0.02273 | **0.49** | `+++---+++0------` | 0.03 | no | — |

Two things worth separating. **Both are nulls**, so the published asymmetry (a 2.65σ disadvantage at the
fine rung against a 0.48σ null at the coarse one) is gone at power. And **the rung whose published claim
was the strongest is the one a single replicate can erase**: `cell_class`'s accuracy contrast has a
leave-one-out minimum of **0.08σ and a sign flip**, while `side`'s is 0.72σ with no flip. The three-seed
result rested on replicates that a sixteen-replicate run shows are not typical of it.

## 3. The contrast `e46` asked for, and it is a null

| metric | delta | sem | **σ** | signs | LOO min | flip |
|---|---|---|---|---|---|---|
| accuracy | **−0.01910** | 0.02161 | **0.88** | `+++-+++-----+-` | 0.47 | no |
| forgetting | **+0.03516** | 0.02907 | **1.21** | `-+-+++---+++++-+` | 0.77 | no |

**The published cross-rung figure was +0.0718 at 2.13σ. At sixteen replicates on both rungs it is
−0.01910 ± 0.02161 = 0.88σ on accuracy and +0.03516 ± 0.02907 = 1.21σ on forgetting** — a null on
both metrics, sign-inconsistent, and with no leave-one-out fragility to blame.

And the floors say the run could have seen it:

| quantity | detection floor at 16 replicates (2 sems) | the three-replicate claim | ratio |
|---|---|---|---|
| `side` | 0.0256 | 0.0069 | **0.27×** — never resolvable here |
| `cell_class` | 0.0323 | 0.0648 | **2.0×** — resolvable and absent |
| cross-rung | 0.0432 | 0.0718 | **1.7×** — resolvable and absent |

## 4. The line's status, which is now complete rather than pending

The C2b rung question — *does the biological synapse partition beat its size-matched control at any
λ, basis or granularity* — now has a well-powered measurement at **both** rungs and at the contrast
between them, all null:

| measurement | n | result |
|---|---|---|
| `cell_class` bio − rand | 16 | +0.0039 ± 0.0161 (0.24σ) |
| `side` bio − rand | 16 | −0.0152 ± 0.0128 (1.19σ) accuracy; +0.0241 ± 0.0198 (1.22σ) forgetting |
| `side − cell_class` | 16 | −0.0191 ± 0.0216 (0.88σ); +0.0352 ± 0.0291 (1.21σ) |
| the four λ = 1.0 rungs | 3 each | all nulls, largest 0.58σ, floors ≥ 0.05 |

So the line's honest summary is the one `e46` gave and this fire completes: **every well-powered
measurement in C2b is a null**, with a detection floor of about 0.03 accuracy, and the earlier positives
were three-replicate events. Nothing here says the *neuron*-level C2 result is affected — that is a
different substrate, a different metric (analytic excess) and a different family of controls, and its
per-seed discipline is the one the project has now applied to all five named rungs.

## 5. One substantive thing the nulls leave behind

The two rungs lean in **consistently opposite directions** on both metrics: `side` toward "biology is
worse" (−0.0152 accuracy, +0.0241 forgetting) and `cell_class` toward "biology is better" (+0.0039,
−0.0111). Neither resolves, and the cross-rung contrast inherits the disagreement rather than
cancelling it — which is why the cross-rung σ is *smaller* than either rung's own in accuracy terms
(0.88 against 1.19 and 0.24). That is the signature of two independent nulls, not of a shared effect
being diluted.

## 6. Limits

- **Sixteen replicates at one λ (0.1), one Fisher-batch count (8) and one circuit size (800).** The
  λ = 1.0 rungs were three replicates each and were already nulls.
- **The floor is ~0.03 accuracy**, so *"any advantage is below about 0.03 at 80% power"* is the
  statement, not *"there is no advantage"*. `e46`'s replicate arithmetic says 0.01 needs 105 replicates
  and 0.03 needs 19.
- **The two runs are different executions**, so the pairing rests on the seed alignment, which the
  bit-identical `naive` arms establish by value rather than by assumption. That is the strongest
  available evidence and it is still evidence, not proof: a code revision could have changed the
  trained arms and not the `naive` one.
- **`input_overlap` is `None` in both configs**, which is the setting where the task circuits are
  disjoint by construction. A different overlap would change the interference structure and nothing
  here transfers to it.
