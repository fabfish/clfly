# The scope in the field's currency: the front page named the metric and not the half of the quantity it is

*2026-10-01 06:49. Runs: **none new** — `experiments/e307_the_scope_in_the_fields_currency.py` reads the README's
scope blockquote for the field it is measured in, a cue that says what that field is, and a citation of the unit that
measured it, writing `runs/e307_the_scope_in_the_fields_currency.json`. Seconds.*

## 1. Three facts, one clause, and the reader

`e299` scoped the front page's absence and named its field. `e304` then showed what that field is: **the lost half of
the shortfall**, exact and computable for every arm, and blind to the part of a task the arm never learned. `e305`
measured the blindness at the level of one arm and `e306` at the level of the ordering. **The clause said none of it.**

A reader who meets *"55 of its 271 arms have a forgetting indistinguishable from zero"* reads it as a statement about
retention. It is not: on those very arms the median unlearned share of the shortfall is **0.821**, and 17 of the 55
have more left to learn than the corpus's typical arm.

## 2. As found: one of three

| | as found | after the correction |
|---|---|---|
| **N1** the clause names the field | **MET** — it carries `mean_forgetting` | MET |
| **N2** and it says what that field is | **FALSIFIER FIRED** — no cue | MET, three cues |
| **N3** and it cites the unit that measured that | **FALSIFIER FIRED** — nothing cited | MET, three findings |

The clause was **872 characters** and grew to **1622**.

## 3. The correction

The clause gains a paragraph saying what the field is — that `mean_forgetting` is exactly `R[j][j] - R[T-1][j]`, the
part of a task the arm learned and gave back — and what it cannot see, with the 0.821 median and the 17 of 55, citing
the three findings that measured the decomposition, the arms and the ordering.

**The claims are registered as the invariant the front page now satisfies**, as `e298` stated the paper's
recommendations': an edit that drops the currency turns this unit red. The as-found count lives here and not in the
artifact, because a claim about a corrected document cannot be re-run.

## 4. What it cannot do

**The cues are lexical**, so a clause that says the same thing in other words reads as absent and the count is a
lower bound — `e298`'s caveat applies unchanged. **This is a claim about text**: N2 verifies that the clause carries a
phrase and not that the phrase's numbers are right, and those numbers are `e304` to `e306`'s business. **The clause is
read from the README and nothing else** — the blockquote runs to the first line that is not one, so a cue in the
prose below it does not count and neither does one in a finding. **And `e299`'s scope is untouched**: the front page
still states its two absences and still carries its `Scoped 2026-09-29` marker, which this unit checks rather than
replaces, because the sentence this one adds is about the **field** and not about the count.
