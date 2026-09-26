# What the pairing shares: the benchmark's noise decomposition is arm-specific and the arms are not

*2026-09-26 22:45. Runs: **none new** — `experiments/e263_what_the_pairing_shares.py` reads the three artifacts that
carry both an `evaluation_noise` block and a `matched_pair` block (`e60`, `e46`, `e178`), writing
`runs/e263_what_the_pairing_shares.json`. A second.*

## 1. The item: two blocks in one artifact that do not know about each other

The network benchmark prices its central contrast in two places, computed in the same run:

- **`evaluation_noise`** splits **each arm's** run-to-run variance into a test-set part (the binomial noise of the
  `n_eval = 144` held-out decisions, printed as "removable") and a training part, and prints the fraction.
- **`matched_pair`** reports the same contrast **paired**, with the arm-to-arm correlation of the replicates that
  licenses it — the line's own note says the paired sem is the right one "because the two arms share a seed sequence".

Neither block mentions the other, and taken together they are inconsistent: **the decomposition gives each arm its own
test-set and training component, so it predicts a correlation of zero between the arms and a paired sem no tighter
than the unpaired one.** The artifacts report correlations of 0.28 to 0.54 and paired sems 1.18× to 1.47× tighter.

## 2. The gap is measurable, and the algebra validates itself

Write `v`, `b`, `t` for an arm's total, test-set and training variance. The observed paired variance is
`v1 + v2 − 2·cov`, so `cov` is recoverable from the artifact's own numbers — and **the recovered algebra reproduces
the reported `corr` to three decimals in all six readings** (0.317/0.317, 0.282/0.282, 0.321/0.321, 0.354/0.354,
0.542/0.542, 0.504/0.504). That is what makes everything below a measurement rather than a model.

| reading | var bio | var control | shared cov | corr observed | item ceiling | training bound | pairing now | without the shared items |
|---|---|---|---|---|---|---|---|---|
| `e60 side/final_accuracy` | 0.003215 | 0.002417 | 0.001510 | **0.542** | 0.373 | 0.270 | **1.468×** | 1.166× |
| `e60 side/mean_forgetting` | 0.007623 | 0.004589 | 0.002983 | **0.504** | 0.176 | **0.401** | **1.398×** | 1.274× |
| `e46 cell_class/final_accuracy` | 0.003782 | 0.002273 | 0.000941 | **0.321** | **0.345** | −0.037 | 1.205× | **0.983×** |
| `e46 cell_class/mean_forgetting` | 0.008447 | 0.003862 | 0.002021 | **0.354** | 0.177 | **0.220** | 1.220× | 1.115× |
| `e178 side 144 reps/final_accuracy` | 0.005480 | 0.005593 | 0.001757 | **0.317** | **0.233** | 0.110 | 1.210× | 1.060× |
| `e178 side 144 reps/mean_forgetting` | 0.011583 | 0.012468 | 0.003389 | **0.282** | 0.107 | **0.196** | 1.180× | 1.115× |

The **item ceiling** is the correlation a fully shared test set could produce (the two arms' test-set noises
perfectly correlated, which is the most any item term can contribute); the **training bound** is what is left over,
a lower bound on the shared-training correlation. **The arms hold in common 0.24 to 0.47 of the biological arm's
run-to-run variance and 0.27 to 0.65 of its random control's** — which is why the paired sem is tighter at all.

## 3. The registered claims (C1-C4, all MET)

| claim | what it says | measured |
|---|---|---|
| **C1** | the arms are correlated and the decomposition cannot say so | every reading at or above +0.28, where the two components imply 0 |
| **C2** | the test set cannot account for it | short by more than 0.05 in **five of six** (+0.085 to +0.328), so those require a shared *training* component |
| **C3** | a bigger test set would take most of the benefit with it | every advantage falls, five by more than 0.10; on `cell_class`/accuracy the surviving advantage is **0.98×** |
| **C4** | the source of the benefit splits by metric | forgetting's training bound exceeds the item ceiling in **3 of 3**; accuracy reverses in **3 of 3** |

**C4 is the sharpest of the four and it separates on the strict side.** Because the item figure is an upper bound and
the training figure a lower bound, "the training bound exceeds the item ceiling" *proves* shared training dominates —
and that holds for the forgetting metric in all three runs (0.401 against 0.176, 0.220 against 0.177, 0.196 against
0.107). So **on forgetting the pairing is not the test set at all; it is the two arms sharing a training trajectory**
— the same initialisation, the same data order, the same arms but for the basis. On accuracy the comparison reverses
in all three runs, which is evidence in that direction but not a proof, because there the two bounds point the same
way.

**And the practical reading of C3**: today's 1.18× to 1.47× advantage is mostly a finite test set. A large enough
`n_eval` would leave 1.06× to 1.27× on four readings and nothing at all on `cell_class`/accuracy, where the entire
pairing benefit is the shared 144 decisions. This extends the benchmark's own sentence — the test-set part of the
noise is "removable" — from the **absolute floor** to the **relative advantage of pairing**, which the same sentence
does not mention.

## 4. What it cannot do

The shared-item figure is an **upper bound** and the shared-training figure a **lower bound**, so C4's forgetting half
is a strict statement while its accuracy half is bound-versus-bound and proves nothing on its own. Every reading is at
the same `n_eval = 144`, so "a bigger test set" is arithmetic under the model rather than a run: nothing here varies
the test-set size. The decomposition inherits the model's own assumption that the held-out decisions are independent,
which `e8`'s own print says is a signal when a fraction exceeds 100%. And only the three artifacts carrying both
blocks can be read this way — an artifact with one of them is silent, not neutral.
