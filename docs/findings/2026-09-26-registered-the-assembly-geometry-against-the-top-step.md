# Registered: the assembly geometry against the top step — the ladder's size dependence meets a knob, not another size

*2026-09-26 08:30, registration. Runs: `e2_topology_gap` at cs {300,800} × `rho` {0.5, 0.99}, four runs, sixteen
cells, **~48 min**, written as `runs/e228_rho{05,99}_cs{300,800}.json`. The `rho = 0.9` references at both sizes are
already on disk (`e217` at cs 300; `e208` for `real`+`erdos_renyi`, `e212`/`e213` for `alloy1`, `e216` for `inalloy1`
at cs 800), so only the two new values per size are run.*

## 1. What is open, and what the candidates have in common

The ladder has three levels — **zero degree sequences destroyed** (`swap*`, `signshuffle`, 0.012–0.030), **one**
(`alloy1`, `inalloy1`, ≈0.045) and **two** (Erdős–Rényi, 0.14187) — and its **top step is size-dependent**: the same
four cells give **1.28× at cs 300** and **1.08× at cs 400** against **2.76×/3.02× at cs 800**, while the middle level
and the floor replicate at all three sizes. `e220`/`e223`/`e224` have tested **the support count**, **the support
share** and **the number of destroyed degree sequences** against it; none explains it, and what is left is named in
the record as *the assembly geometry, the propagation depth, the circuit's edge density*.

**Those three all vary with the circuit.** `rho` does not: it is the scalar the task builder already carries
(`stable_weights` rescales the connectome's weights to spectral radius `rho = 0.9`), so it can be moved at a **fixed
circuit size**, which is the one comparison the size dependence has never had.

## 2. Why the claims are shaped this way: a one-seed smoke test

The runner had no `--rho` flag until this fire; it does now (default `None` = the builder's 0.9, and a config that
omits it is normalised to 0.9 by `e225`/`e227` so that absence and an explicit default are one configuration). The
flag was smoke-tested at **cs 300, support 30, one seed, two topologies**, and the smoke test is *not* evidence for
any registered claim — it is the reason the claims are written the way they are:

| `rho` | `real` excess | Erdős–Rényi excess | ER ÷ `real` |
|---|---|---|---|
| 0.9 | 0.031800 | 0.154173 | **4.85×** |
| 0.5 | **0.000315** | 0.023982 | **76.2×** |

The floor collapses by a factor of **100** while the top rung falls by only **6.4**, so the *ratio* moves by **16×**
between two values of one scalar — at one circuit size, on one seed. A quantity that moves 16× from a knob cannot be
read as a size effect until the knob is held fixed and varied.

## 3. The claims

The **top step** is defined here as **(Erdős–Rényi excess) ÷ (the one-side level)**, where the one-side level is the
mean of the `alloy1` and `inalloy1` excesses — the "one degree sequence destroyed" rung, which is the level the
record's 1.28×/1.08×/2.76× figures divide by. The ER ÷ `real` ratio is **reported** as well and is a different
quantity; nothing here conflates them.

- **R1 (the primary question).** At cs 300 the top step spans **more than the size gap it is supposed to explain**:
  its range over `rho` ∈ {0.5, 0.9, 0.99} covers [1.28×, 2.76×]. **Falsifier**: the cs-300 top step stays within
  **1.5×** of itself at all three `rho` — then the assembly geometry does not compete with size for this quantity
  and the size dependence survives as a size effect. **Null**: the range is wider than 1.5× but does not reach
  cs 800's level, i.e. `rho` matters without displacing size as the explanation.
- **R2 (the direction), registered from the smoke test's arithmetic.** The top step **falls as `rho` rises**:
  `rho` 0.5 > 0.9 > 0.99, because the floor is the more `rho`-sensitive of the two levels (measured: ×100 against
  ×6.4 at one seed). **Falsifier**: the reverse ordering, monotone increasing in `rho`. **Null**: non-monotone, or a
  spread smaller than the drawing spreads below.
- **R3 (the cs-800 headline).** The four cells at cs 800 with `rho` ≠ 0.9 are **outside 1.5×** of the on-disk
  2.76×/3.02×, i.e. *"the ladder's top step is a 7× jump"* is a **`rho = 0.9` statement**. **Falsifier**: within
  1.2× of the on-disk value, which would say the headline survives moving the geometry's one scalar.

**Reported** for every cell: the `real`, `alloy1`, `inalloy1` and `erdos_renyi` analytic excesses, the one-side
level, the top step, and ER ÷ `real`; plus each run's `timing_s` and its config's recorded `rho`.

## 4. What it cannot do

- **One drawing per cell.** The one-side families' own drawing spreads are the larger of the two at cs 800
  (`alloy1` 3.34× across five drawings, `inalloy1` 1.24× across three), so a ratio whose numerator moves less
  (ER: 1.05× across three drawings) inherits the *denominator's* spread, and a 1.5× bar on a 3.34×-spread
  denominator is a coarse test. The verdict is written to be refused when a single drawing lands somewhere
  uninformative.
- **`rho` is not a pure depth knob.** `stable_weights` rescales the whole weight matrix to the target spectral
  radius, so `rho` also changes the absolute weight magnitude; a mechanism read off `rho` cannot be attributed to
  propagation *depth* rather than to scale (`--rho` does not touch `TASK_ASSEMBLIES`, the propagation mode, or the
  circuit).
- **Two sizes and three `rho` values, one drawing each**, so no interaction term is identifiable: R1 and R3 are
  existence statements about a range, not a fitted slope.
- **Nothing about the network substrate**, and nothing about the realized arm (`--no-realized`, as in every cell of
  this line).

## 5. Cost (rule 49)

Measured from this corpus, not estimated: **cs 300 = 120 s/cell** (`e217`, four cells in 481 s) and **cs 800 =
237 s/cell** (`e216`, one cell; `e208` gives 228 s/cell over eight cells). So the cs-300 pair is **2 × 4 × 120 s ≈
16 min** and the cs-800 pair **2 × 4 × 237 s ≈ 32 min**: **≈ 48 min, four runs, sixteen cells**, launched in one
background loop with the `rho = 0.9` references already on disk.
