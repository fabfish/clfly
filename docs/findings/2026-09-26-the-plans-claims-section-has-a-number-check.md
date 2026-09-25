# The plan's Claims section now has the number check the paper has -- and the first thing it caught was a count nothing computes

*2026-09-26 09:05, `runs/e226_plan_claims_numbers.json` — one audit, seconds, plus one annotation re-count (~1 min).
Read from the document and from the findings corpus; the two declared numbers re-run against
`clfly.connectome.annotate`. The section audited is `## Claims` up to `## Experimental programme`, 1198 lines.*

## 1. What was missing

`e97` checks that a finding's cited artifacts exist. `e105` checks the numbers inside findings' tables. `e192`
checks the one relation a reader of the **paper** relies on: a number it states beside a citation is a number that
source contains. The document in between -- `docs/research_plan.md`, which is what each fire reads to decide what to
run -- had no such check anywhere, and its `## Claims` section carries **898 number tokens**, **593 distinct**
(decimal point, or an integer of three digits or more).

`e226` asserts the same relation there: a number the plan states is a number the findings corpus carries. The exit
code is the count of number tokens that no finding carries and that the `DECLARED` table does not account for.

## 2. The result, on the live section

| | count |
|---|---|
| number tokens checked | 898 |
| distinct | 593 |
| carried by the findings corpus as a **token**, outside the declared class | 591 |
| declared as an annotation count (and carried -- see below) | 2 |
| **carried by nothing** | **0** |

Both declared numbers re-run against the annotation and both **MATCH**: `556` (`cell_class` startswith `LH`) and
`6114` (`cell_type` contains `T5`). A declaration here is a measurement with a column, a rule and a prefix attached,
not an exemption -- the run that produces the exit code re-counts them.

**And the declaration is a state rather than a hiding place.** Both entries are printed whether or not the corpus
carries them, and both are now carried -- by **this finding**, which is the document that measured them. Removing it
from a copy of the corpus (`--findings` on a directory without it) flips both back to "no witness in the corpus",
which is the interesting half: the class the audit exists to catch is a count **no document carries**, and writing a
finding that measures a count is exactly what moves one out of it.

## 3. Three rules differ from `e192`, and each difference is measured rather than stylistic

- **The match is a number token, not a substring.** `e192`'s first arm is `quoted in source`, and on this section --
  with this finding excluded, as it stood -- that arm carries **592 of 593** against the token arm's **591**, and the
  one member it adds is `556`, carried **vacuously**: the digit run occurs inside longer numbers (`0.5563`, `15564`)
  in 26 findings. A synthetic case pins the mechanism for good: a claim of `4321` is supported by a finding carrying
  `0.43213` under that arm and by nothing under the token arm. So **the arm is the whole difference between 0 and 1
  unwitnessed numbers on this section**, and the looser arm would have reported this audit clean for the wrong
  reason.
- **Integers start at three digits.** One- and two-digit integers here are section numbers, ladder indices
  (`alloy1`, `inalloy1`), rungs and multiplicities, not measurements.
- **A scientific notation's exponent counts in the quoted precision.** `e192` reads the decimals off the string's
  first `.`, which makes `7.6e-4` unsupportable by anything; folding the exponent in (`7.6e-4` is stated to the fifth
  decimal) makes it supported by `7.58e-4`, the coefficient `docs/findings/2026-09-22-penalty-cost-has-two-terms.md:48`
  fits. Measured on the live section, this rule is the difference between **two** unsupported numbers and **one**.

## 4. The number it caught, and the correction

The plan's benchmark block said:

> `{cell_type=T5}` (6005, under the prefix rule the runner uses — a **substring** count says 6183, and the difference
> is `T5` inside longer names)

**`6183` is in no finding, and it is not a count either rule produces.** Measured on the shipped annotation:

| rule | count |
|---|---|
| `cell_type` **startswith** `T5` — the rule `e185 --populations` prints and the runner resolves a probe through | **6005** |
| `cell_type` **contains** `T5` | **6114** |

The substring count is larger by **109**, and the names that make it larger are exactly the ones the sentence means:
`LPT50`–`LPT58`, `LT51`–`LT59` and `LHCENT5` — 21 distinct names carry `T5`, of which only 4 (`T5a`–`T5d`) are
prefix matches. So the sentence's *structure* was right and its number was not: **6183 is a count of nothing**, and
the plan now carries **6114** with the three name families named in it. This is the audit's first catch, and it is the
class the check exists for -- a count in a claim that no measurement in the repository produces.

## 5. What the check cannot do

- **Present is not the same as intended.** The token is matched corpus-wide, so a number is supported by *any* finding
  that happens to carry it. `7.6e-4` is a live example of the loophole in the other direction: its support is a
  rounding of the coefficient the cost finding fits, and the same section also contains `0.00076` as a table entry of
  a different experiment entirely -- the audit sees the value, not the sentence's intent. The corpus-wide search also
  cannot say **which** finding supports a claim, only that one does.
- **A witness is not a derivation.** The 591 token-carried numbers include counts quoted from findings that measured
  something else; the check localises a number to a document, not to a measurement, and it cannot tell a witness that
  computed the value from one that quoted it.
- **The three-digit floor is a choice with a cost.** A wrong one- or two-digit claim (a baseline count, a rung) passes
  unchecked, and the section is full of them.
- **The declared class is two entries deep and both are annotation counts.** If a count enters a claim whose rule is
  neither `startswith` nor `contains` on one column, the entry would have to grow a rule rather than a number.
- **It speaks for the Claims section and the benchmark block, not the programme table** -- the table's own numbers are
  `e127`/`e105`'s business, and `e192`'s run on the plan covers the rows whose prose carries a citation.
