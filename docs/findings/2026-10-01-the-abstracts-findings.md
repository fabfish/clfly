# The abstracts findings: four numbered headlines, all four scoped, where the advice was not

*2026-10-01 02:51. Runs: **none new** — `experiments/e300_the_abstracts_findings.py` reads the paper's abstract and
writes `runs/e300_the_abstracts_findings.json`. Seconds.*

## 1. The contrast this unit exists to draw

`e298` read the paper's **basis recommendations** — the sentences a reader acts on — and found them as-found
**unscoped**: 0 of 3 named a metric, 1 of 3 named a comparator
(`docs/findings/2026-09-29-the-recommendation-needed-a-scope.md`). The abstract is the other end of the paper: the
sentences a reader **meets first**. Both are prose, both are about the same economics, and the question is whether the
paper's own front matter has the property the advice lacked.

It does. **Four numbered findings; each names the quantity it is about and the thing it beats.** A1 and A2 are both
MET.

| # | headline | metrics named | comparators named |
|---|---|---|---|
| 1 | *A large diagonalisation penalty appears.* | `excess` | `oracle`, `lgcl`, `random`, `diagonal`, `matched`, `synthetic` |
| 2 | *The connectome separates the tasks — and the claim that this does \*not\* drive the penalty does not survive.* | `excess`, `σ` | `random`, `matched` |
| 3 | *Biological anchoring bases beat capacity-matched random ones, and there is a working a-priori predictor.* | `σ` | `random`, `matched`, `control`, `rewired`, `erdős` |
| 4 | *The wiring's own eigenbasis beats the neuron diagonal at equal capacity* | `excess`, `forgetting`, `accuracy`, `σ` | `random`, `diagonal`, `naive`, `matched`, `control` |

**Scope is a property of a sentence's role, not of its content.** The abstract and the advice discuss the same
comparisons with the same vocabulary; what separates them is that a finding is written to be **checked** and a
recommendation is written to be **followed**, and only the first forces the author to name the axis and the alternative.
That is the reading this unit supports and the one `e298` corrected.

## 2. Two reading defects, both found by reading the instrument's output

- The `FINDING` pattern initially consumed the document's numbered lists **wherever they appeared**, not only at the
  top, so sections below the abstract were being read as headlines. The pattern now requires the list to open the
  paragraph and the paragraph to sit in the abstract.
- The `2.` heading contains `*not*`, so a single-line pattern stopped at the newline inside it. That heading is read
  with `re.S`.

Neither was caught by a test; both were caught by looking at what the instrument printed, which is why the module
prints its findings before its claims.

## 3. What it cannot do

**The metric and comparator lists are lexical**, so an abstract sentence that makes a claim without naming an axis or
an alternative is invisible, and the count is a lower bound. **A1 is a formatting claim**: it verifies that the
findings are a numbered list and not that the list is complete or true. **A2 verifies presence, not correctness** — that
a headline names `excess` does not mean the number attached to it is right, which is the business of the units `e295`
to `e299` and their predecessors. **Four sentences is the whole population**, so there is no power to report and no
test to run; the unit is a census. **The paper is a moving document**: this reads the version on disk at generation
time, and an edit that adds an unscoped headline turns A2 red.
