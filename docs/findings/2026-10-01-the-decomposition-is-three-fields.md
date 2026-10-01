# The decomposition is three stored fields, and the retention matrix is their redundancy

*2026-10-01 10:14. Runs: **none new** — `experiments/e313_the_decomposition_is_three_fields.py` checks the retention
matrix's cells against the per-task fields the corpus writes beside it, writing
`runs/e313_the_decomposition_is_three_fields.json`. Seconds.*

## 1. Where the three cells come from

`e304` reads the shortfall `1 - R[T-1][j]` off the retention matrix and splits it at the level `R[j][j]`. `e312` then
showed the shortfall is `1 - final_accuracy`. This unit asks where each cell comes from, and the answer is that the
corpus writes all three down **per task**:

| matrix cell | stored field |
|---|---|
| `R[j][j]` — the level the task reached when it was learned | **`learned[j]`** |
| `R[T-1][j]` — the level it ended at | **`final_per_task[j]`** |
| their difference — the lost term | **`forgetting_per_task[j]`** |

**Y1, Y2 and Y3 all MET**, each in **6096 of 6096** arm-replicates carrying a matrix and its fields, per task. No arm
was refused for a mismatched length (`wrong_index` is 0 for the whole corpus).

## 2. And so the split's terms are the fields

**Y4 MET** — over **5581 of 5581** arm-replicates carrying both levels, `e304`'s three terms are the stored fields or
their complements: `unlearned_mean` is `1 - mean(learned)`, `shortfall_mean` is `1 - mean(final_per_task)`, and
`lost_mean` is `mean(learned) - mean(final_per_task)`.

## 3. What this corrects

**`e312`'s finding closes by saying the currency the corpus lacks is `unlearned`, and that is wrong**: the corpus has
it, as **`learned`**, in the same payload as the matrix. With `e312`'s result too, **no term of `e304`'s split is a
quantity this repository does not store** — the split is a re-derivation, and the matrix is the redundancy.

What `e304` still adds is not the arithmetic but **the verification**: the three fields agree with the matrix per task
in every arm of the corpus, which is what makes a number taken from either one trustworthy, and which is how the
redundancy was found. `e304`'s D1 and D2 were the first two of those three checks.

## 4. The contract this leaves open

`e309`'s conformance contract requires `mean_forgetting` and **a retention matrix**, and does not name `learned`,
`final_per_task` or `forgetting_per_task`. Since those three are what a reader can actually use — the matrix is 6096
copies of arithmetic over them — the contract's next revision should ask for them, and this unit's own `carried`
counts are what that revision needs. That is reported here and not claimed, because changing the contract would move
`e309`'s K1 to K4 and this unit does not do that.

## 5. What it cannot do

**These are identities between recorded numbers**, so Y1 to Y4 check a writer and not a result: a runner that wrote
`learned` wrongly and the matrix wrongly would pass. **Only arm-replicates carrying all three fields are read**, and
the count of those is reported rather than assumed — 6096 of the corpus's arm-replicates carry them, and an artifact
that carries the matrix alone would leave the question open rather than answered. **The claim is about this corpus's
runner**, so another runner's spelling reads as absent, which is `e309`'s question and not this one. **And nothing
here says the matrix should go**: it is larger than the three fields and carries nothing they do not, but it is what
an independent implementation can be checked against.
