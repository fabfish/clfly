# The assembly geometry moves the top step 11.6× — more than the circuit size does — and R2 is refuted in the direction opposite to its registration

*2026-09-26 08:40, `runs/e228_rho{05,099}_cs300.json` (two runs, 521 s and 797 s) read by `e229_read_rho_sweep.py`
against the `rho = 0.9` reference recomputed from `e217_ladder_cs300.json`. The registered claims are R1 (the range
covers cs 800's level), R2 (the top step falls as `rho` rises) and R3 (the cs-800 headline is a `rho = 0.9`
statement). **The cs-300 half of the design is complete, so R1 and R2 are judged; R3's two cs-800 cells are the other
half of the same sweep and the reader refuses R3 alone.** Registration:
`docs/findings/2026-09-26-registered-the-assembly-geometry-against-the-top-step.md`.*

## 1. The three cs-300 cells, at one circuit size

cs 300, support 30, seeds 3, one drawing each. The `rho = 0.9` row is the reference artifact; the other two are new.

| `rho` | `real` | `alloy1` | `inalloy1` | Erdős–Rényi | one-side mean | **top step** | ER ÷ `real` |
|---|---|---|---|---|---|---|---|
| 0.5 | 0.00022 | 0.02940 | 0.01876 | 0.02452 | 0.02408 | **1.018×** | 109.41× |
| 0.9 (ref) | 0.02978 | 0.12247 | 0.12233 | 0.15668 | 0.12240 | **1.280×** | 5.26× |
| 0.99 | 0.01590 | 0.00547 | 0.00825 | 0.08078 | 0.00686 | **11.774×** | 5.08× |

## 2. R1 is MET, and it overturns the reading the sweep was registered to test

**R1** registered: *at cs 300 the top step's range over `rho` covers [1.28×, 2.76×]*. It reads **1.018×, 1.280×,
11.774×** — a span of **11.56×**, which covers cs 800's level and goes four times past it.

The consequence is not that `rho` "also matters". It is that **the ladder's size dependence cannot be attributed to
size at all until `rho` is held fixed**: the top step moves **11.6×** over `rho` at one circuit size, against the
**2.2×** between cs 300 (1.280×) and cs 800 (2.737×). The record's sentence — *the mechanism is open on a variable
nobody has varied* — is now false in its first clause: the variable was listed in that very sentence (`rho` is the
assembly geometry's scalar) and moving it moves the top step further than the size comparison ever did. What the
size comparison shows is a **2.2× difference measured inside a 11.6×-wide `rho` dependence**, which is what a
size effect looks like when a hidden parameter is stronger than the variable of interest.

## 3. R2's falsifier fired — the registered direction was backwards, and its justification was measured on another ratio

**R2** registered: *the top step falls as `rho` rises (0.5 > 0.9 > 0.99)*. Measured, `rho` ascending: **1.018× <
1.280× < 11.774×** — **monotone increasing**, so the registered falsifier fires. Both halves of that registration
are wrong, and the second is the instructive one:

- the direction is the opposite of the registration's, so the claim is refuted rather than merely unmet;
- the registration justified the direction from the smoke test's **Erdős–Rényi ÷ `real`** ratio, whose denominator
  is the `real` cell. The claim's denominator is the **one-side level**, and the two denominators move by *different
  factors*: between `rho` 0.9 and 0.99 the one-side level falls **÷17.8** (0.12240 → 0.00686) while `real` falls
  only ÷1.9 (0.02978 → 0.01590) and Erdős–Rényi ÷1.9. That is why `ER ÷ real` *falls* (5.26× → 5.08×) while the top
  step *rises* (1.280× → 11.774×): the two ratios point in opposite directions on the same two cells.

This is the second time in this thread that a unit's *quantity* was the defect rather than its arithmetic (the first
was the excess being a difference of two larger numbers, `e227`). A claim inherited from a smoke test inherits the
smoke test's quantity, and the fix is to write the unit out — which the registration now does in prose and the
reader does in code, but the claims were already registered by then.

## 4. What the denominator is doing, stated as a result of its own

At `rho` 0.99 the **one-side nulls become nearly free**: their level is 0.00686 against Erdős–Rényi's 0.08078, so
destroying *one* degree sequence costs **11.5× less** than destroying both — where at `rho` 0.9 the two are nearly
equal (0.12240 against 0.15668, 1.28× apart). And at `rho` 0.5 the ladder's order **inverts**: Erdős–Rényi
(0.02452) sits *below* `alloy1` (0.02940), ER ÷ `alloy1` = **0.83×**.

So the ladder's ordering — *more destroyed degree structure costs more* — holds at `rho` 0.9 with a margin of 1.28×,
inverts at 0.5, and opens to 11.5× at 0.99. Whatever the mechanism is, it is a statement about the **propagation
regime** at least as much as about the destructive operation.

## 5. What this cannot do

- **One drawing per cell**, and the cell's own two families disagree: at `rho` 0.99 the top step's two spellings are
  **14.77×** (`alloy1`) and **9.79×** (`inalloy1`) — a 1.5× band around the mean spelling of 11.77× — while at
  `rho` 0.5 they are 0.83× and 1.31×. So the cs-300 cells' own family spread is the same order as the 2.2× size gap
  this line has been quoting, and **only the rho-0.99 cell's 11.6× range is comfortably outside it**.
- **`rho` is not a depth knob**: `stable_weights` rescales the whole weight matrix to the target spectral radius, so
  a mechanism read off `rho` mixes depth with scale.
- **R3 is not judged here.** The two cs-800 cells are being written as this is; until they are read, *"the cs-800
  headline is a `rho = 0.9` statement"* is not established either way — and given R1, the prior should be that it is.
- **The middle level and the floor were not re-measured at cs 800**, so the sentence *"the middle level and the floor
  replicate at all three sizes"* still carries its unstated condition, `rho = 0.9`.
