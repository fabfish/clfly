# The top step's rho dependence is not the alignment contrast: the penalty spans 11.6× while the alignment spans 1.13×, and the task geometry's rank collapses to 1

*2026-09-26 08:55, `runs/e229_read_rho_sweep.json` through `e229_read_rho_sweep.py --geometry`, reading the three
`e228` cells that were on disk (cs 300 at `rho` 0.5 and 0.99, cs 800 at `rho` 0.5) against the `rho = 0.9` reference
recomputed from `e217`. Every number below is from the artifacts' own `geometry` blocks, which the runner writes for
every topology; the fourth cell (cs 800, `rho` 0.99) is the other half of the same sweep.*

## 1. The two candidates, side by side

The top step is a ratio of **penalties**. If its `rho` dependence came from how differently Erdős–Rényi and the
one-side nulls *line up* with the tasks, then the alignment ratio would move with the penalty ratio. It does not:

| cell | **penalty top step** | **alignment top step** | one-side align. (× chance) | ER align. (× chance) |
|---|---|---|---|---|
| cs 300, `rho` 0.5 | **1.018×** | 1.149× | 0.617 | 0.710 |
| cs 300, `rho` 0.9 (ref) | **1.280×** | 1.269× | 5.45 | 6.626 |
| cs 300, `rho` 0.99 | **11.774×** | 1.293× | 7.971 | 10.303 |
| cs 800, `rho` 0.5 | **1.151×** | 1.303× | 0.578 | 0.753 |

**Across the three cells measured, the penalty top step spans 11.56× and the alignment top step spans 1.13×.** The
alignment contrast between the two-side and one-side constructions is *flat* (1.15–1.30×) in every cell that varies
`rho` — the nulls move up and down in alignment together — so **the rho dependence cannot be the alignment
contrast**, whatever else it is. That is the same question `e213` asked of the alloy family at `rho` 0.9, here asked
across a parameter that moves the penalty by a factor of eleven.

## 2. What the same blocks say instead

The `geometry` block also carries the task geometry's **shape**, which does not depend on the basis at all, and it
moves:

| cell | one-side `effective_rank` | ER `effective_rank` | ER ÷ one-side rank | penalty top step | one-side `flattening` |
|---|---|---|---|---|---|
| cs 300, `rho` 0.5 | 26.17 | 26.75 | **1.02×** | 1.018× | 0.884 |
| cs 300, `rho` 0.9 (ref) | 9.41 | 16.31 | **1.73×** | 1.280× | 0.318 |
| cs 300, `rho` 0.99 | **1.07** | 3.48 | **3.25×** | 11.774× | 0.036 |
| cs 800, `rho` 0.5 | 60.35 | 64.39 | 1.07× | 1.151× | 0.831 |

Two things follow, and they are stated at their own strength rather than as the mechanism:

- **`rho` does not merely rescale the tasks; it reshapes them.** At cs 300 the one-side nulls' task geometry has
  **26.2 effective dimensions** at `rho` 0.5, **9.4** at 0.9 and **1.07** at 0.99 — at `rho` 0.99 a null's task
  geometry is essentially one-dimensional, with `flattening` down at 0.036 from 0.884.
- **The rank contrast is the statistic that orders like the penalty**: 1.02×, 1.73×, 3.25× against the penalty's
  1.02×, 1.28×, 11.77× — monotone in the same direction where the alignment contrast is flat. **It does not carry the
  magnitude** (3.25× against 11.5×), so this is a candidate with evidence and not a mechanism: the right reading is
  that the *shape* of the task geometry is where to look next and the *alignment* is where not to.

## 3. Why this matters for the ladder's headline

The record's ladder claims — "destroying more of the degree structure costs more", "Erdős–Rényi is a separate
regime", "the top step is size-dependent" — were all measured at `rho = 0.9`. The three cells here show that at a
**fixed** circuit size the same comparison reads 1.018× (`rho` 0.5) and 11.774× (`rho` 0.99), and that the one-side
nulls at `rho` 0.99 carry a *rank-1* task geometry. **The two-side distinction is therefore a statement about the
propagation regime as much as about the destructive operation** — and the size dependence (2.2×) is the smaller of
the two effects.

## 3b. Correction: the rank contrast's cs-800 half is inside its own drawing scatter

`e230` asked whether the rank contrasts read here beat the families' own scatter across drawings, and the answer splits the claim: **at cs 300 all four families resolve it** (`alloy1` 25.25x against a 2.73x scatter, `inalloy1` 23.53x against 2.08x, `erdos_renyi` 7.68x against 1.06x, `real` 3.76x against 1.98x), and **at cs 800 the collapsing family resolves it** (`inalloy1` 44.79x against 4.14x) while the family it was compared against does not (`alloy1`: twelve drawings spanning **16.44x** against a single-drawing contrast of **3.01x**). So the rank reading stands at cs 300 and for the collapsing side at cs 800, and the "the two families come apart" half is a statement about which drawing was taken (`docs/findings/2026-09-26-the-rank-contrast-meets-its-own-drawing-scatter.md`). The alignment half of this finding is untouched.

## 4. What this cannot do

- **Three cells, one drawing each**, so the penalty's 11.56× span rests on four artifacts, and the rank contrast is
  read off the same three points that the penalty is: the two statistics are *co-measured*, not independently varied,
  and nothing here separates "the rank contrast drives the penalty" from "a third thing drives both".
- **`rho` is one scalar and it moves depth and scale together** (`stable_weights` rescales the whole weight matrix to
  the target spectral radius), so the rank collapse cannot be attributed to the propagation's depth rather than to
  the weight scale the propagation is fed.
- **The alignment statistic is a single summary** (`all_pairs_alignment` over consecutive task pairs, against a
  random-basis chance level). A different alignment statistic could still move where this one is flat; what is
  excluded is *this* statistic.
- **The fourth cell is not read here**, and with three of four cells the cs-800 half of the sweep has one `rho` value
  only, so no size × `rho` interaction is measured.
