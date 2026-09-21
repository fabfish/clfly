# Phase 2 — the connectome substrate, and two traps in it

**Date:** 2026-09-22
**Scope:** `clfly/connectome/**`, `tests/test_connectome.py`
**Data:** FlyWire v783, verified and cached

---

## 1. What landed

| Module | Role |
|---|---|
| `fetch.py` | clones the substrate from its distributors into gitignored `data/`, recording commit hashes for provenance |
| `graph.py` | the signed sparse wiring diagram, weight scaling, spectrum, induced subgraphs, modularity |
| `annotate.py` | the annotation table as a ladder of candidate anchoring bases |
| `circuits.py` | circuit extraction by annotation-seeded expansion along the wiring |

Data in place, both verified loadable:

| source | commit | file | size |
|---|---|---|---|
| `philshiu/Drosophila_brain_model` | `91bdd1e7dcf1` | `Connectivity_783.parquet` | 100.8 MB |
| | | `Completeness_783.csv` | 3.5 MB |
| `flyconnectome/flywire_annotations` | `8587524c1748` | `Supplemental_file1_neuron_annotations.tsv` | 31.9 MB |

Loaded: **138,639 neurons, 15,091,983 connections, 54,492,922 synapses**, 40.0%
inhibitory, mean out-degree 108.9, max out-degree 9,783. The top symmetrised
eigenvalues are `[317.3, 263.3, 261.5, 201.4, 195.9, 186.4, …]` — a heavy,
structured head, which is the opposite of the flattened spectrum a random graph
would give and is the first hint that the connectome is in the regime where
LGCL's "diagonalisation is free" result should fail.

## 2. Trap one: the sign is in a different column

The shipped edge table keeps **magnitude and sign apart**: `Connectivity` is the
*unsigned* synapse count and `Excitatory` is ±1. Taking `Connectivity` at face
value makes every inhibitory synapse look excitatory, and — this is the
dangerous part — nothing downstream complains. The counts are still plausible,
the degrees are still plausible, and every result is quietly wrong in a way no
sanity check would catch.

The loader now asserts `Connectivity ≥ 0` and `Excitatory ∈ {-1, +1}` and forms
the product, rather than inferring the convention from a column name.

## 3. Trap two: indices that are not the indices you think

`Completeness_783.csv` has columns `Unnamed: 0` (the FlyWire root id, ~7.2e17)
and `Completed` (a **boolean** flag). A name-based column guess picked
`Completed`, producing an all-`True` "id" vector that joined to **nothing** —
the first symptom was every basis reporting 0.0% coverage with 138,639 groups.

Two fixes, both structural rather than local:

- `load_root_ids` now selects by *value* (an integer column with magnitude
  > 1e12) and refuses to guess if none exists.
- `_verify_index_alignment` samples the edge table and asserts
  `root_ids[index] == ID`. If the file ever switches to its own enumeration,
  every partition label would be silently permuted — again a failure that
  produces plausible numbers and no error. Now it raises.

## 4. The basis ladder, and the trap in it

`annotate.basis_table` on the full brain (138,639 neurons):

| basis | named groups | coverage | largest | constrained fraction |
|---|---|---|---|---|
| `flow` | 17 | 1.000 | 118,480 | 0.251 |
| `side` | 18 | 1.000 | 69,504 | 0.502 |
| `super_class` | 24 | 1.000 | 77,530 | 0.615 |
| `cell_class` | 49 real (+31,737 singleton) | 0.771 | 22,311 | 0.936 |
| `cell_type` | 10,331 | 0.989 | 7,932 | 0.992 |
| `cell_sub_class` | 112,971 | 0.186 | 8,029 | 0.995 |
| `nerve` | 129,072 | 0.069 | 3,638 | 0.999 |
| `ito_lee_hemilineage` | 101,318 | 0.271 | 3,875 | 0.999 |
| `hartenstein_hemilineage` | 104,033 | 0.251 | 3,411 | 0.999 |
| `supertype` | 106,693 | 0.244 | 2,189 | 0.999 |

Two things to read off this, and both change the experimental design.

**Most of the ladder is unusable on the whole brain.** Only `flow`, `side`,
`super_class` and `cell_type` have coverage ≥ 99%. `cell_class` covers 77%,
and the hemilineage/supertype/nerve columns cover 7–27%: the `named_groups`
counts of 100,000+ are almost entirely *unannotated neurons each getting a
private singleton group*. A basis built on 25% of neurons is not a basis for the
brain; it is a basis for a quarter of it with the rest silently reduced to the
diagonal.

**`constrained_fraction` is the trap detector.** A near-singleton partition
keeps only the diagonal — which means **the finest "biological basis" quietly
*is* plain EWC**. `supertype` at 0.9994 constrained is not a rich biological
grouping; it is the diagonal wearing an annotation. Conversely `flow` at 0.251
constrains nothing and behaves like the full matrix. Only the middle of the
ladder has room for a basis to matter.

This is why every comparison downstream is matched on `constrained_fraction`
(equivalently on `n_parameters`), not on group count.

## 5. Full-brain exact LGCL is infeasible, so a subcircuit is mandatory

The largest weakly connected component is 138,113 neurons. One dense `d × d`
float64 covariance would be **152.6 GB**, and each Kalman step costs `O(d³) ≈
2.6e15` flops. The exact machinery — the thing that makes this project worth
doing, because it gives an exact oracle instead of a baseline — cannot run at
that size.

`circuits.py` reduces the dimension by taking a *circuit*: real neurons, real
wiring, real annotations, fewer of them. Seeds come from the annotation
vocabulary rather than hand-picked ids, so the selection is auditable:

- **mushroom body** — `cell_class ∈ {Kenyon_Cell, MBON, MBIN, DAN}` → 5,608 neurons
- **central complex** — `cell_class ∈ {CX, FB, EB, PB, NO, LAL}` → 2,875
- **antennal lobe** — `{ALPN, ALLN, ALIN, ALON, olfactory, LHLN, LHCENT}` → 3,987

At hop 0 the union is 12,470 neurons and the annotation is *excellent* —
`cell_class` 100% coverage / 12 groups, `cell_type` 99.9% / 812 groups,
hemilineage 81.7%. Expanding one hop balloons to 31,913 and pulls in thousands
of well-connected but unannotated optic-lobe neurons, which is what destroyed the
partition in the first attempt (see §6).

### The extracted circuit

`mb+cx+al@n3150` — 3,150 neurons, 86,443 edges, dense covariance 0.079 GB:

| basis | groups | largest | constrained fraction |
|---|---|---|---|
| `flow` | 2 | 2,600 | 0.288 |
| `super_class` | 2 | 2,600 | 0.288 |
| `side` | 4 | 1,611 | 0.502 |
| `cell_class` | 12 | 1,248 | 0.750 |
| `cell_type` | 812 | 527 | 0.952 |
| `supertype` | 918 | 527 | 0.944 |
| `ito_lee_hemilineage` | 611 | 329 | 0.955 |

The ladder now spans 0.29 → 0.96 — a real granularity sweep — and the matched
random control for `cell_type` reproduces `n_parameters` to the unit (237,793 vs
237,793). `flow` and `super_class` degenerate to 2 groups inside a central-brain
circuit, which is itself worth reporting: those rungs are whole-brain scales.

## 6. A methodology note worth keeping

The first version of `extract` capped the circuit by keeping the globally
highest-degree neurons. The result looked fine — 6,000 neurons, a rich-looking
basis table — and was worthless: the kept neurons were mostly unannotated optic
lobe, so `cell_class` came out as 4,737 groups on 6,000 neurons. **The partition
had dissolved into singletons while still reporting a large group count.**

The fix is `subsample_fraction`: sample every group proportionally, with a floor
of one member so no cell type disappears. That preserves the partition's size
distribution — which is what matched-budget comparisons depend on — instead of
selecting for connectivity.

The general lesson, which applies to the rest of this project: a basis's *group
count* says nothing about whether it constrains anything. `constrained_fraction`
and coverage are the numbers that do.

## 7. Status and next

Phase 2 substrate is done and tested (34 tests, all green; the connectome tests
skip cleanly without the data).

Next, in order:

1. **Task definitions.** LGCL needs a `J_k` per task. The connectome-native
   construction: a task reads out from a *functional assembly* — a set of cell
   types — so `J_k` is the precision of that readout subspace. Tasks get their
   structure from biology, not from a random rotation, which is the whole point.
2. **`experiments/e3_basis_selection.py`** — the core comparison: for each rung
   of the ladder, the EWC↔Kalman gap at matched `constrained_fraction`, against
   group-size-matched random partitions. Prediction: the biological rungs beat
   their matched random controls, and the ranking tracks the principal angles
   between each partition's indicator span and the task precision bases.
3. **Rewiring controls** (`rewiring.py`) for C1: degree-preserving, Erdős–Rényi,
   and matched-spectrum nulls.
4. **Modularity interpolation** for C3.

The open question the substrate work did *not* settle: with only 12 `cell_class`
groups inside the circuit, and `cell_type` at 0.95 constrained, the interesting
regime may be a *partial* cell-type partition — pooling the smallest types — which
is a granularity the annotation table does not directly provide. If the biological
rungs all sit at the extremes, the honest result is that the connectome's own
vocabulary does not put a basis where the theory says one is needed, and that is
worth knowing too.
