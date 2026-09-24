# `e153` is also the wiring family at λ = 1.0, and there the penalty arms beat `naive` at 3.4–4.2σ

**Date:** 2026-09-24
**Artifact:** `runs/e153_r32_overlap1_methods_40reps.json` — launched as a *reproducibility* check and corrected
this evening for having run at the runner's **default** `lam = 1.0` rather than `3e-3`. **That correction is what
makes it a measurement**: λ = 1.0 is a setting this project abandoned as unusable (the rung work ran there by
accident and every rung was a null), and nobody had read the artifact as a λ = 1.0 table.
**Comparators:** `runs/e141_r32_ewc_lam3e-{2,1}.json` (the base family's top of sweep, forty replicates) and
`runs/e133_r32_naive_ewc_40reps.json` (its baseline).

---

## 1. The wiring family at λ = 1.0, paired on forty seeds

| arm | forgetting vs `naive` | resolution | newest-task accuracy | resolution |
|---|---|---|---|---|
| `ewc` (diagonal) | **−0.0370 ± 0.0101** | **3.68σ** | −0.0276 | **4.65σ** |
| `ewc-block` (biological) | **−0.0435 ± 0.0103** | **4.21σ** | −0.0313 | **5.60σ** |
| `ewc-block-rand` (its control) | **−0.0328 ± 0.0095** | **3.44σ** | −0.0245 | **4.60σ** |
| `replay` | −0.0984 ± 0.0091 | 10.79σ | +0.0047 | 1.12σ |

**And the base family at the top of its swept range** (`e141`, the same statistic, forty paired seeds):

| arm | forgetting vs `naive` | resolution | newest-task accuracy | resolution |
|---|---|---|---|---|
| `ewc`, λ = 3e-2 | **+0.0060 ± 0.0104** | 0.58σ (*worse*, unresolved) | −0.0755 | **9.45σ** |
| `ewc`, λ = 3e-1 | **+0.0096 ± 0.0113** | 0.85σ (*worse*, unresolved) | −0.0729 | **9.00σ** |

**So at λ = 1.0 — 33× the base family's top swept λ — the wiring family's three penalty arms all beat `naive` on
forgetting at 3.4–4.2σ**, while the base family's own top swept λ is already *worse* than `naive`, unresolvedly, at
a plasticity cost three times larger (7.3–7.6 points against 2.5–3.1).

**That extends `e144`'s family result from a level to a range.** `e144` measured the diagonal beating `naive` by
**4.73σ** on this family at λ = 3e-3 against **1.21σ** on the base family. This says the difference is not that the
optimum sits elsewhere on this family — it is that **the family tolerates a penalty an order of magnitude past
where the base family's stops helping**, and that it pays less for it on the other axis too.

## 2. What the comparison cannot separate, and it is the obvious alternative

**The two families' baselines forget by different amounts** — the wiring family's `naive` sits at **+0.1068**
against the base family's **+0.0750**, i.e. 42% more room for a penalty to work in. **So "the family tolerates a
stronger penalty" and "the family had more forgetting to remove" predict the same sign here**, and no artifact
distinguishes them at matched λ.

**The deciding run does not exist and is now registered**: **`e161` executes the base family's `ewc` at
`lam = 1.0`, forty replicates**, against `e133`'s `naive` on the same seeds — the matched-λ comparison, one arm,
about an hour. **P1**: the base family's λ = 1.0 arm is *worse* than `naive` on forgetting (its sweep's 3e-2 and
3e-1 points are +0.006 and +0.010, so a monotone extension predicts worse still) **and** pays a newest-task cost
larger than the wiring family's 0.0276–0.0313; **falsifier**: it beats `naive` at ≥2σ, which would say the base
family does *not* fall off with λ and that `e141`'s interior optimum is about something else.

## 3. And the λ = 1.0 datum has one more use

**It is a level the project had only ever measured by accident.** The rung work's λ = 1.0 arms are three to five
replicates and were never read as a penalty-strength measurement; this artifact is forty replicates on a family
where the penalty works, so **λ = 1.0 now has one properly-powered point** — and it is the *top* of the λ range
the record covers on any family (the sweep's grid ends at 3e-1). **An interior optimum at 3e-4 therefore has a
measured point three and a half decades above it**, which is a stronger bracket than anything the sweep alone
provided.

## 4. What this cannot settle

- **One λ, one family, one read-out (32), three tasks, one seed stream** — and the wiring family has only *one*
  40-replicate λ = 1.0 table, whose launch was for another purpose.
- **The newest-task comparison across λ and family at once** is confounded as §1 says: the base family's points
  are at 3e-2/3e-1 and the wiring family's at 1.0, so "less plastic cost" is a statement about those two levels
  and not about the families' cost curves.
- **And the artifact's provenance is now a caveat**: `e153` was launched from a paraphrase of a command that
  omitted `--lam` (rule 44), which is what put it at 1.0 — the measurement is sound, and its existence is an
  accident worth remembering when a later session reads its row.
