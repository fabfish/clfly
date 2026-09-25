# Registered: the source alloy — which side of the edge carries the penalty's jump?

**Date:** 2026-09-26. **Registered before its runs.** Artifacts to be written: `runs/e216_inalloy_rs0.json` … `rs2.json`.

---

## 1. The question the last two fires narrowed to

Three nulls now differ in a controlled way, and `e215` removed one of the three differences:

| null | out-degree | in-degree | weights | sign pattern | alignment (× chance) | penalty |
|---|---|---|---|---|---|---|
| `swap*` (the walk) | preserved | preserved | preserved | preserved | 0.65–1.72× | 0.012–0.023 |
| `alloy1` (targets redrawn) | **preserved** | free | attached to their source | preserved | 2.3–4.2× | 0.030–0.101 (3.34× spread) |
| `signshuffle` | preserved | preserved | permuted | **destroyed** | 0.34–0.40× | 0.0278–0.0298 (1.07× spread) |
| `erdos_renyi` | free | free | random | **destroyed** | 4.9–5.2× | 0.141–0.149 (1.05× spread) |

So the sign pattern is **tested and excluded** (`e215`: the sign half alone gives 0.028, 5.0× below the ER level), and
the remaining difference between the low-penalty and high-penalty constructions is **which side of the edge keeps its
degree structure**: the alloy preserves the **out**-degree and gives ≈0.05; Erdős–Rényi preserves neither and gives
≈0.145. The missing cell of the 2×2 is the null that preserves the **in**-degree and frees the out-side.

## 2. The construction

`random_sources` — reachable as the topology name **`inalloy<fraction>`** — is the exact mirror of the alloy: it
redraws the **source** of a fraction of the edges with the same duplicate guard, so it keeps every neuron's
**in-degree exactly**, the edge count exactly and the weights attached to their targets, and it frees the
out-structure. Verified on a toy graph at three fractions: in-degree sequences identical, out-degree sequences
changed, edge count identical, no self-loops, and the realised fraction matches the requested one.

## 3. The design

One command, three realizations (one drawing is not a measurement — the alloy's own spread was 3.34×):

```
experiments/e2_topology_gap.py --circuit-size 800 --support 80 --seeds 3 --seed0 0 --q 0.02 \
  --topologies inalloy1 --rewire-seed {0,1,2} --no-realized \
  --json-out runs/e216_inalloy_rs{0,1,2}.json
```

**Cost (rule 49)**: 225–240 s per cell from `e213`'s ten cells, so **≈12 min** for three. One command on an idle
machine.

## 4. The claims

**Y1 — which side carries the jump (the discriminator).** The three cells' analytic excess is **at or above 0.10**,
i.e. the same order as Erdős–Rényi's 0.14134–0.14897. Since `inalloy1` destroys the **out**-structure and preserves the
in-structure, this outcome says **the penalty's jump follows the out-side** — what each neuron sends. **Falsifier**:
at or below **0.06**, i.e. the same order as the alloy and the axis, which says the **in**-structure is what has to be
preserved for the penalty to stay low and therefore that the out-side is not the driver — and, with Erdős–Rényi high
while destroying both, would leave the driver in the *joint* destruction of the two rather than in either side alone.
**Null worth keeping**: 0.06–0.10, an intermediate level that would need the fraction axis swept rather than a third
construction.

**Y2 — the alignment follows the same side, or not.** The three cells' `all_pairs_alignment` is **at or above 0.20**
(the hole's upper half, where only Erdős–Rényi and one alloy drawing have reached). **Falsifier**: at or below
**0.0912**, the band's floor — the sign shuffle's shape, whose alignment fell *below* the axis while its penalty stayed
there; **null**: in the band but below 0.20.

**Y3 — reported, not claimed**: the same three cells' `top_eig_share`, `effective_rank` and `flattening`, and the
within-construction penalty spread (the alloy's 3.34× against Erdős–Rényi's 1.05× and the sign shuffle's 1.07× make
this a construction-level property worth having a fourth measurement of).

## 5. What this cannot do

- **Separate "which side" from "how many edges are free"**: `inalloy1` touches every edge's source, and the alloy
  every edge's target, so the two nulls differ in the side *and* in nothing else — the design is deliberately
  symmetric and the fraction axis is not swept here.
- **Speak for the weights' arrangement** beyond noting that both nulls keep each weight attached to its remaining
  endpoint.
- **Give a distribution** from three drawings, or speak for other circuit sizes and task draws.
- **Test the joint-destruction reading directly**: if Y1's falsifier lands, the claim "neither side alone is enough"
  would still need a null that preserves out-degree and destroys in-degree *and* the reverse, which is what the alloy
  and this null respectively are — so it is testable, but only with both rows of the 2×2 in hand, which is what this
  fire completes.
