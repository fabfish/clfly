# E63 — the predictor's "one failure" is an unresolved observation, and the rewired condition was never tested

**Date:** 2026-09-22
**Script:** `experiments/e63_predictor_resolvability.py`
**Artifacts:** `runs/e63_predictor_resolvability.json`, `runs/e6_predictor_6.json`, `runs/e6_predictor.json`
**Context:** `2026-09-22-c2-passes-the-per-seed-discipline.md` (`e57`), `e35`'s arithmetical bound, plan rules 8 and 20

---

## 1. The score, at the resolution it was actually measured at

The predictor is one of the project's two headline positive results. `e6_predictor_6` (six seeds) stores,
for each of 25 matched pairs across five out-of-sample conditions, the σ of the pair's excess
difference — and that is what says whether a call was *evidence* or a *coin flip*:

| condition | d | resolvable | correct | per-pair σ |
|---|---|---|---|---|
| baseline | 952 | 3/5 | **3/3** | 7.48, 6.62, 0.03, 4.98, 1.95 |
| wider-tasks | 952 | 4/5 | **4/4** | 18.25, 8.25, 0.04, 5.97, 2.18 |
| faster-drift | 952 | 3/5 | **3/3** | 7.25, 6.32, 0.03, 4.79, 1.89 |
| **rewired-swap2** | 952 | **0/5** | — | 0.09, **1.74**, 0.06, 0.75, 0.23 |
| larger-circuit | 1307 | 3/5 | **3/3** | 15.53, 4.49, 0.26, 3.27, 1.54 |
| **total** | | **13/25** | **13/13** | |

So the honest score is **13 of 13 correct on the resolvable pairs**, which is the plan's figure, and the
"24 of 25" form counts twelve sub-resolution calls as evidence. The artifact had the resolvability
recorded all along — this is a reporting question, not a measurement one, and the plan is already right.

## 2. The "one failure" is 1.74σ, in a condition where nothing resolves

The plan names the predictor's one failure: *"on heavily rewired wiring the biological-vs-random sign is
called wrongly **with a large margin**"*. The condition is `rewired-swap2`, and its five σ values are
**0.09, 1.74, 0.06, 0.75, 0.23** — all far below resolution:

| rung | excess Δ | σ | called correctly? |
|---|---|---|---|
| `side` | −0.000053 | 0.09 | yes |
| **`cell_class`** | **+0.003402** | **1.74** | **no** |
| `cell_type` | +0.000166 | 0.06 | yes |
| `ito_lee_hemilineage` | −0.001827 | 0.75 | yes |
| `supertype` | +0.000595 | 0.23 | yes |

**The disagreement is the largest σ of the five, and 1.74σ is not resolution.** What *is* large is the
prediction's confidence — the pressure delta is −0.911 against the observed +0.0034 — so the honest
description is **a confident prediction meeting an unresolved observation**, not a wrong call with a
large margin. Reaching 3σ on the seed component alone would need **≈18 seeds**; the σ scales as
1/√n, so this is affordable but not free.

## 3. And the rewired condition is untested, not failed

**Zero of its five pairs resolve at six seeds.** The predictor has therefore never been *tested* on a
rewired topology: the condition appears in the list as an out-of-sample condition and contributes a
disagreement, but no pair in it is measurable at this resolution. The plan's condition list should say
**untested** where it currently implies a success or a failure, which is rule 18's distinction applied
to a score sheet rather than to an intervention.

> **OVERTURNED by `e64` (`docs/findings/2026-09-23-the-predictors-record-per-seed.md`).** The σ in this
> section are the **unpaired** ones — `hypot(sem_bio, sem_rand)` — and for a pair whose two arms co-move
> across task draws that quantity is an order of magnitude too large. `e64` re-ran these five
> conditions with per-seed storage, and on the **paired** sem the failure is **10.63σ** with **six of
> six seeds agreeing in sign** (8.54σ with the control-draw component folded in). So the condition is
> neither untested nor a null: four of its five pairs resolve and the predictor gets three of them
> right, the one miss being a **confident wrong call on heavily rewired wiring**. The original `e6`
> reading — "one confident failure, called the wrong way with a large margin" — was right and this
> section's softening of it was an artefact of the error formula.
>
> The same applies to the two readings below: paired, **`supertype` resolves in every condition at
> 8.1–14.8σ** and **`cell_type` at 7.8–13.9σ**, so "the 13 resolvable calls are about the three coarser
> rungs" is withdrawn as well. What does survive is that `cell_type`'s *delta* is ~0.00006 — the reason
> its σ is small is not the predictor but the near-diagonal partition, exactly as the second bullet
> says. And the denominator itself moves: on the paired sem **24 of the 25 pairs resolve**, against the
> 13 reported here, with **20 of 21** called correctly once the measured draw sds are included.

Two further readings from the same table, both consistent with `e35`'s arithmetic bound
(`constrained ≤ 1 − 1/m`, so a very fine partition is the diagonal):

- **`cell_type` never resolves in any condition** (0.03, 0.04, 0.03, 0.06, 0.26σ) and **`supertype`**
  resolves in none either (1.54–2.18σ). So the predictor's 13 resolvable calls are effectively about
  **the three coarser rungs** — `side`, `cell_class`, `ito_lee_hemilineage` — which is the same
  crowding the project found on the granularity ladder, showing up in its own score sheet.
- `cell_type`'s σ being **0.03** is not a property of the predictor: it is that the underlying
  biological-versus-random difference is ~0 there, which is what a near-diagonal partition must give.

## 4. What does not change, and one gap that remains

**13 of 13 on the resolvable pairs is a real result** and the strongest positive evidence in the
project, with rank correlations of +0.97 to +0.99 over the full 25 pairs. §2 and §3 narrow *where* it is
evidenced, not whether. And the artifact is honest about this: it stored `resolvable` and
`sign_ok` separately, so the refinement above needed no new computation — only reading both columns.

**The remaining gap is rule 8's, for the third time in this sequence.** The pairs' deltas are stored as
means over six seeds, with a `sigma` but no per-seed values, so the per-seed structure of the
predictor's score — whether any single call is carried by one or two seeds — is unchecked. `e57` found
the same for C2's headline family (closed by `e58`), `e54` for the network `naive` arm, and `e47` for
the cs = 800 contrast. **The review that would settle it is `e6_predictor_6` re-run with per-seed
storage**, which the current `e6` code would have to be checked for — and the predictor's own
"13/13" is the last headline number in the project without one.

## 5. Limits

- **Resolvability is judged at six seeds.** A pair at 1.95σ (`supertype`, baseline) is below the
  stored threshold; at more seeds it might resolve, and the threshold itself is a policy choice the
  artifact made rather than a law.
- **The σ is the seed component only.** The predictor's conditions are all `real`-topology or one
  `swap2` condition at a single realization, so the realization component — which `e59` showed is
  98% of the variance elsewhere — is not in these σ's at all. That makes them optimistic for any
  claim about a *rewiring rule* and correct for a claim about these graphs.
- **One condition per topology.** `rewired-swap2` is a single rewired topology at one circuit size, so
  "untested on rewired wiring" is a statement about that one.
- This is a **re-reading of an existing artifact**, not a new measurement. The pairs' σ values were
  computed by `e6` and stored; nothing was recomputed.
