# The audit re-armed on its means: eleven families instead of five, and cs 800 `alloy1` comes back

*2026-09-26 20:45. Runs: **none new** — `experiments/e257_audit_on_means.py` re-reads `e230`'s forty-two families on
the column `e230` already computes and never judges on, written as `runs/e257_audit_on_means.json`. JSON-only,
seconds.*

## 1. Why re-arm it

`e230` reads each family's between-`rho` rank contrast from the **single-drawing** rho cells the record quotes, and
skips any family without one. Drawing the `rho` grid at both sizes (`e255`, `e256`) therefore took its subject away:
**five of its forty-two families are still auditable**, and its declarations fell from five to two in one session —
the last un-declaration (cs 800 `alloy1`, 19:20) happening because the family *left the score* rather than because the
question was answered.

`e230` already computes what the re-arming needs: each rho group's **mean**, as its `between_mean` column. This module
judges on it.

## 2. The verdicts, all four MET

| claim | result |
|---|---|
| **G1** the re-arming covers more families | **11** carry a means verdict against the as-read column's **5** |
| **G2** it answers for families that left the scope | **6** families get a verdict the as-read column cannot give |
| **G3** it re-finds what leaving the scope had hidden | cs 800 `alloy1`: means **7.84** against its own scatter **16.44**, a ratio of **0.48** — NOT RESOLVABLE |
| **G4** the two surviving declarations survive too | cs 300 `swap0.5` 8.10 against 8.77, `swap2` 5.65 against 7.77 — both below 1 |

The 11 families with a means contrast (`within` is the family's own scatter at `rho` 0.9; `means` is the largest over
the smallest rho-group mean):

| cell | family | within | means | on means | as read |
|---|---|---|---|---|---|
| 300 | `alloy1` | 2.73 | 12.11 | RESOLVABLE | *(out of scope)* |
| 300 | `erdos_renyi` | 1.06 | 6.07 | RESOLVABLE | *(out of scope)* |
| 300 | `inalloy1` | 2.08 | 18.63 | RESOLVABLE | *(out of scope)* |
| 300 | `real` | 1.98 | 4.55 | RESOLVABLE | RESOLVABLE (3.76) |
| 300 | `signshuffle` | 1.19 | 3.67 | RESOLVABLE | RESOLVABLE (1.21) |
| 300 | `swap0.5` | 8.77 | 8.10 | NOT | NOT (4.05) **[DECLARED]** |
| 300 | `swap2` | 7.77 | 5.65 | NOT | NOT (1.18) **[DECLARED]** |
| **800** | **`alloy1`** | **16.44** | **7.84** | **NOT** | *(out of scope)* |
| 800 | `erdos_renyi` | 3.21 | 15.54 | RESOLVABLE | *(out of scope)* |
| 800 | `inalloy1` | 8.02 | 50.54 | RESOLVABLE | *(out of scope)* |
| 800 | `real` | 1.01 | 5.64 | RESOLVABLE | RESOLVABLE (5.64) |

## 3. What that changes

**The five ladder families' rho contrasts are real, and one of them is not.** `inalloy1` at either size, `erdos_renyi`
at either size and `alloy1` at cs 300 all clear their own scatters on the means — by 4.4× to 8.9×, which is the
question `e230` was built to ask and could no longer ask. **And cs 800 `alloy1` is the exception**: its rho contrast is
**7.84 against a 16.44 drawing scatter**, so it fails on the means exactly as it failed on the as-read column this
morning. Its un-declaration was **bookkeeping and not a resolution** — drawing the corpus did not answer the question,
it removed the instrument that could report the answer, and the re-armed instrument reports the same "not resolvable"
it reported before the corpus swallowed it.

**So the ledger has a third category, and this fire is where it appears.** A family is either
*resolvable* (the contrast beats the scatter), *declared unresolvable* (it does not, and the record says so), or —
until now — *out of scope* (no single-drawing cell is left, so nothing is said). The third category silently absorbed
an unresolvable family for one session. With the means column judged, it folds back into the first two: **ten families
resolvable, one not (cs 800 `alloy1`)**, and the two cs-300 swap declarations still stand.

## 4. What it cannot do

**31 of the 42 families carry a single rho group**, so neither reading applies to them at all — the means column widens
the audit's reach from 5 to 11 and not to 42, and the rest are un-auditable by this design. They are the size-ladder
cells (cs 400, 500, 600, 700 at one `rho` each) and the `swap` rungs, so the coverage limit is the corpus's shape
rather than the column's. The means column compares a contrast built from **one mean per rho value** against a scatter
measured **at `rho` 0.9 only**, so a family that scatters more elsewhere can still read resolvable — the two sides of
the comparison are not measured over the same cells. And the "means" are means over drawings that may straddle a code
epoch (see `e227`), which no column here can detect.
