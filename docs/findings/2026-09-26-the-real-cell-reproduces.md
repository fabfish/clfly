# The `real` cell reproduces: four groups to the last bit and one to 1.7e-6

*2026-09-26 06:27, `experiments/e225_real_cell_census.py` — a census of the 26 artifacts that carry a `real` cell with
an analytic excess, grouped by the five fields that determine it (`circuit_size`, `support`, `seeds`, `seed0`, `q`).
Exit code 0. No runs.*

## 1. What it checks, and why the premise needed checking

The previous finding leaned on **"the rewiring does not touch the connectome"** — that is why two `e223` drawings
reproduced `real` to five decimals (0.01774 in both) while every rewired cell moved. That premise had never been
checked corpus-wide, and this census is the check: **a `real` cell's value must be identical in every artifact whose
tasks and circuit are the same**, even when the artifacts differ in `rewire_seed`, in the other topologies they carry,
or in when they were written.

The classification has to be **derived rather than listed**, because the corpus contains two analytic implementations
of a `real` cell and they are not the same quantity: the **pooling** family (`e3_basis_selection --ladder`, `e13`)
writes bases `bio:pool1 … bio:pool128` and an `_abs` block, and the **cell-class** family (`e2_topology_gap`, and
everything this week's work ran) writes `diagonal(EWC)`, `bio:cell_class`, `rand:cell_class`. A group's family is
read off the base names its `real` block carries.

## 2. The census: 26 artifacts, 20 groups, 6 with more than one member

| class | group | value(s) | spread |
|---|---|---|---|
| **EXACT** | cs 800 / support 80 / 3 seeds | 0.0183041398 in `e208_hole_sweep_cs800_3seeds` and `e2_analytic` | **0** |
| **EXACT** | cs 800 / support 80 / 12 seeds | 0.0174878399 in `e3_ladder` and `e3_ladder_v2` | **0** |
| **EXACT** | cs 800 / support 80 / 18 seeds | 0.0176167312 in `e3_seeds18` and `e58_bases_18seeds_perseed` | **0** |
| **EXACT** | cs 400 / support 80 / 3 seeds | 0.0177361014 in `e223`'s two drawings | **0** |
| **FLOATING** | cs 1500 / support 150 / 12 seeds | 0.0147410550 in `e9_ladder_d1874`, 0.0147410795 in `e79_ladder_d1874_perseed` | 2.45e-8 (**1.66e-6** relative) |
| **MATERIAL, cross-family (declared)** | cs 300 / support 30 / 3 seeds | 0.0272282530 in `e13_control3_d952`, 0.0297827645 in `e217_ladder_cs300` | 0.00255 (**8.96e-2** relative) |

**The premise holds where it can be tested.** Four groups reproduce **to the last bit** — and three of those four
pairs differ in `rewire_seed`, in the topologies list, or in both, so the identity is doing real work rather than
comparing a file with itself. The fifth agrees to **1.66e-6 relative** — the same runner at two epochs, i.e. a
floating-point difference in a matrix solve. **No group disagrees materially inside one family**, which is what the
exit code counts.

## 3. The dates make it a cross-epoch result, and the two families behave differently

The census now records each group's **write span** (rule 47: a file's timestamp dates the *end* of its run), and the
spans turn the agreements into epoch statements:

| group | members' write times | span | class |
|---|---|---|---|
| cs 800 / 80 / 3 seeds | `e2_analytic` **09-22 03:22** → `e208_hole_sweep_cs800_3seeds` **09-26 00:48** | **3.89 days** | **EXACT (0)** |
| cs 800 / 80 / 18 seeds | `e3_seeds18` 09-23 → `e58_bases_18seeds_perseed` 09-23 | 0.81 days | EXACT (0) |
| cs 800 / 80 / 12 seeds | `e3_ladder` → `e3_ladder_v2` | 0.15 days | EXACT (0) |
| cs 400 / 80 / 3 seeds | `e223`'s two drawings | 0.01 days | EXACT (0) |
| cs 1500 / 150 / 12 seeds | `e9_ladder_d1874` **09-22 19:54** → `e79_ladder_d1874_perseed` **09-23 05:13** | **0.39 days** | FLOATING (1.66e-6) |
| cs 300 / 30 / 3 seeds | `e13_control3_d952` 09-22 16:09 → `e217_ladder_cs300` 09-26 03:59 | 3.49 days | MATERIAL, cross-family |

**The cell-class `real` cell reproduces to the last bit across 3.89 days** — and those four days contain the
`434b512` commit (2026-09-25 08:57), which touched **both** `clfly/connectome/circuits.py` and
`clfly/connectome/tasks.py`. So that commit's own inertness claim — *"the fix is INERT in every artifact because it is
0 neurons either way"* — is **verified empirically by two artifacts written four days apart**, which is stronger than
the argument it was made with.

**And the two families behave differently**: the pooling family's pair differs by **1.66e-6 across 9 hours**, while the
cell-class family agrees exactly across four days. The pooling path's arithmetic is order- or path-dependent (an
eigendecomposition through a different code path), so **an exact reproduction claim in this record has to say which
family it is about** — the cell-class path is bit-stable across days and the pooling path is not bit-stable across
hours.

## 3. And the one material disagreement in the corpus is not a reproducibility failure

The cs-300 pair looks alarming — **8.96e-2 relative** — and it is the corpus's only material `real`-cell difference.
It is **two implementations, not two measurements**:

- `e13_control3_d952` is a **pooling-family** artifact: its `real` block carries `bio:pool1 … bio:pool128`, `rand:pool1
  … rand:pool128` and an `_abs` block;
- `e217_ladder_cs300` is a **cell-class** artifact: `diagonal(EWC)`, `bio:cell_class`, `rand:cell_class`.

Their configs also differ in `ladder`, `align_top` (16 against absent), `control_draws` (3 against absent) and
`extra_bases`, so the quantity named `real.diagonal(EWC).analytic.excess_mean` is computed by two different code paths
on two different base sets. **A reader who compared the two numbers without noticing the families would report a
reproducibility failure that is not one**, which is why the family is derived from the artifact's own base names
rather than from a name list.

## 4. The boundary, stated because it does no work here

The FLOATING/MATERIAL boundary is **1e-4 relative**, and the corpus leaves it **four orders of room**: the largest
within-family difference is **1.66e-6** and the only cross-family one is **8.96e-2** — so any boundary between 1e-5
and 1e-3 classifies this corpus identically. The choice is in the module with that sentence beside it, so a future
artifact landing between them is visible rather than absorbed.

## 5. What this cannot do

It sees only the 26 artifacts carrying a `real` cell with an analytic excess — the realized arm, the network line and
every aggregate summary are outside its scope; it compares **one number per artifact** rather than the whole cell; it
cannot say *which* code changed where a FLOATING difference appears, only that the value moved by less than a
hundredth of a percent; and a group of one is reported and classified as `single`, so the census is silent about the
14 groups that have no second measurement at all.
