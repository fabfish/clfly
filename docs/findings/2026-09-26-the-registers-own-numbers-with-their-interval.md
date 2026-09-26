# The register's own numbers, with the interval they were measured inside: 2.76× is a 20th-percentile draw and the two spellings differ by less than the noise

*2026-09-26 14:05, `runs/e242_register_intervals.json` through `e242_register_intervals.py` — no new runs. The
convention cell every headline figure comes from (cs 800, support 80, `rho` 0.9) carries **6 drawings of
`erdos_renyi`, 5 of `alloy1` and 3 of `inalloy1`**, which is more than the record's own top-step figures were read
from. **R1 lands in its null band and R2 is MET.***

## 1. The top step at the convention cell, over its own drawings

The top step is Erdős–Rényi ÷ the one-side level, and the record quotes it as two spellings — 2.76× (over `alloy1`'s
five-drawing mean) and 3.02× (over `inalloy1`'s three). Every cross-drawing pair gives a value:

| spelling | pairs | min | q25 | median | q75 | max | the register's figure |
|---|---|---|---|---|---|---|---|
| ER ÷ `alloy1` | 30 | 1.40 | 3.02 | **3.45** | 3.90 | 4.95 | **2.76× → 20th percentile** (6 of 30 pairs at or below) |
| ER ÷ `inalloy1` | 18 | 2.71 | 2.82 | **3.10** | 3.37 | 3.54 | **3.02× → 33rd percentile** (6 of 18) |

Read against the *mean* spelling — one value per Erdős–Rényi drawing against the denominator's mean, which is how the
record states it — the register's 2.76× sits at the bottom of the six values (2.75–2.90) and its 3.02× **just below**
the other six (3.03–3.19).

## 2. R1's null band: the quoted number is a low draw of its own distribution

R1 registered that both figures would sit in the central half of their distributions. The ER ÷ `inalloy1` figure does
(33rd percentile, inside q25–q75), but the ER ÷ `alloy1` figure is at the **20th percentile — below q25**, though well
inside the range (min 1.40). So the record's headline spelling is a **low-ish draw** of the thirty its own drawings
support: the honest central value of that quantity at this cell is **3.45×, not 2.76×**, and the range is **1.40× to
4.95×** — a factor of 3.5 around a number quoted to two decimals.

## 3. R2 is MET: the two spellings are not a distinction the drawings support

The two spellings differ by **9%** (2.76 against 3.02). The interquartile ranges are **26%** of the median for the
`alloy1` spelling and **18%** for the `inalloy1` one — both larger than the gap. So quoting the level as *"2.76×/3.02×,
two spellings"* presents as a family distinction what the drawings cannot separate; a **single interval** is the form
the data supports:

> the top step at cs 800/support 80/`rho` 0.9 is **3.45× [3.02, 3.90]** over 30 drawing pairs (range 1.40–4.95) for
> the `alloy1` spelling, and **3.10× [2.82, 3.37]** over 18 pairs for the `inalloy1` spelling.

(This is the same shape as `e240`'s C2, which put the two-side *advantage* above 3× at this cell alone — the advantage
is real here and its size is 3.1–3.5×, not 2.76×.)

## 4. Why the convention cell is the only place this can be done, and what that says

The census also shows where an interval is **not** available: cs 800/support 20 and support 160 have 2 drawings per
family (4 pairs each), every `rho` value above 0.9 at cs 800/support 80 has **one** pair (a single drawing per side),
and `real` never has two different drawings at all. So **the register's numbers can be bracketed at exactly one
cell** — and by `e241`'s lesson the answer there would be sharper with a designed base, which is the next unit
rather than a claim here.

## 5. What this cannot do

- **The drawings are the corpus's accidental ones**: 6, 5 and 3 runs that some experiment happened to make, not a
  designed axis; the pairs are not independent (each drawing appears in many pairs), so the quartiles are a summary of
  those runs and not of a population.
- **One size, one support, one `rho`**, so no interaction is in view.
- **Nothing new is measured**: if a drawing carries a config error, this inherits it.
- **A claim's implementation is as fallible as the claim.** The first version of R2 compared the spellings' *ratio*
  (1.09) against the distributions' *relative* IQR (0.26) and fired the falsifier on that unit error; the fix is in the
  module and the incident is recorded here rather than quietly repaired.
