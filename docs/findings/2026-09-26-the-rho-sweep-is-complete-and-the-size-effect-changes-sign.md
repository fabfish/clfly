# The sweep is complete: R3 is MET — the cs-800 headline is a `rho = 0.9` statement — and the size effect's SIGN flips between `rho` 0.9 and 0.99

*2026-09-26 09:05, the four `e228` cells (`runs/e228_rho{05,099}_cs{300,800}.json`, 521 / 503 / 934 / ~950 s) read by
`e229_read_rho_sweep.py` against the `rho = 0.9` references recomputed from `e217` (cs 300) and
`e208`+`e212`/`e213`+`e216` (cs 800). All three registered claims now have verdicts, and the reader's exit code is 0:
R1 MET, R2's falsifier fired, **R3 MET**. Registration:
`docs/findings/2026-09-26-registered-the-assembly-geometry-against-the-top-step.md`.*

## 1. The grid

Top step = Erdős–Rényi ÷ (the mean of `alloy1` and `inalloy1`), with the two families' own spellings beside it.

| size | `rho` 0.5 | `rho` 0.9 (reference) | `rho` 0.99 |
|---|---|---|---|
| **cs 300** | **1.018×** (0.83 / 1.31) | **1.280×** (1.28 / 1.28) | **11.774×** (14.77 / 9.79) |
| **cs 800** | **1.151×** (1.30 / 1.03) | **2.737×** (2.49 / 3.04) | **0.748×** (0.42 / **3.62**) |

**R3 MET.** The registered claim was that the cs-800 cells at `rho` ≠ 0.9 are outside 1.5× of the on-disk
2.76×/3.02×; they measure **1.151×** and **0.748×**, i.e. **0.27×–0.42×** of the reference. So *"Erdős–Rényi is a
separate regime"* and *"the top step is 7×"* are **`rho = 0.9` statements**, and the verdict does not depend on the
one cell of the four that is unresolvable (below): the `rho` 0.5 cell alone is 0.42× of the reference.

## 2. The result the completed grid adds: the size effect changes sign

| comparison | at `rho` 0.5 | at `rho` 0.9 | at `rho` 0.99 |
|---|---|---|---|
| cs 300 | 1.018× | 1.280× | **11.774×** |
| cs 800 | 1.151× | 2.737× | **0.748×** |
| cs 800 ÷ cs 300 | **1.13×** | **2.14×** | **0.06×** |

**The size effect is not one effect.** At `rho` 0.9 the larger circuit has the *larger* top step (2.14×); at `rho`
0.99 the ordering **reverses by a factor of 15.7×** (cs 300's 11.774× against cs 800's 0.748×); at `rho` 0.5 the two
sizes agree to 1.13×. The record's sentence *"the top step is size-dependent"* was measured at one `rho`, and the
completed grid says the dependence it describes is a **`rho`-dependent effect whose sign the untested scalar
controls** — which is a different statement, and a stronger one, than either "size does it" or "`rho` does it".

## 3. And at high `rho` the one-side level is not one quantity: the rank collapse is DIRECTIONAL

At cs 800, `rho` 0.99 the two one-side families are **8.7× apart** — `alloy1` 0.11395 against `inalloy1` 0.01312 —
so the cell's top step has two spellings of **0.42×** and **3.62×**, and *the mean spelling of 0.748× is the only
thing R3's design can state*. The geometry block says why:

| cs 800, `rho` 0.99 | excess | alignment × chance | `effective_rank` |
|---|---|---|---|
| `alloy1` (out-degrees destroyed) | 0.11395 | 3.377 | **21.01** |
| `inalloy1` (in-degrees destroyed) | 0.01312 | 4.356 | **1.29** |
| `erdos_renyi` (both) | 0.04751 | 6.921 | 4.20 |
| `real` | 0.00693 | 0.199 | 11.80 |

Destroying the **in**-side at high `rho` collapses the task geometry to **1.29 effective dimensions** and its penalty
with it (0.01312); destroying the **out**-side leaves **21.0** dimensions and a penalty 8.7× higher (0.11395). So at
high `rho` the two one-side nulls are not two drawings of one construction — they are two different regimes, and
"the one-side level" is a mean over quantities that have come apart. At cs 300, `rho` 0.99 they stay together
(0.00547 against 0.00825, 1.5×; ranks 1.05 and 1.10) — so the asymmetry is itself `rho`- and size-dependent.

## 4. The mechanism statement, at its measured strength

Across the **four** cells that vary `rho`, the **penalty** top step spans **15.74×** while the **alignment** top step
spans **1.56×**. The alignment contrast cannot carry the dependence; the task geometry's **shape** is the statistic
that orders with it — the one-side rank contrast runs 1.02× / 1.73× / 3.25× against the penalty's three cs-300
spellings — and it now has a *direction* attached (§3). It still does not carry the magnitude (3.25× against 11.5×),
so this remains a candidate with evidence: **the shape of the task geometry is where to look next and the alignment
is where not to.**

## 5. What this cannot do

- **One drawing per cell**, and one of the four cells cannot resolve its own quantity: at cs 800, `rho` 0.99 the two
  families' spellings are 0.42× and 3.62×. R3 survives that because the `rho` 0.5 cell alone carries it.
- **The middle level and the floor were not re-measured at cs 800** at the new `rho` values, so the size comparison's
  other levels are unread.
- **No interaction term**: two sizes × three `rho` values with one drawing each cannot separate a size effect from a
  `rho` effect that differs by size, and §2's sign flip is *consistent with* both descriptions.
- **`rho` moves depth and weight scale together** (`stable_weights` rescales the whole matrix), so nothing here
  attributes the rank collapse to propagation depth rather than to the scale the propagation is fed.
- **Nothing here speaks for the realized arm or the network substrate.**
