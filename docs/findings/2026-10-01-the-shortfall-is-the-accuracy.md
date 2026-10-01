# The shortfall is the accuracy: the third quantity `e306` ordered is the corpus's own first one

*2026-10-01 09:41. Runs: **none new** — `experiments/e312_the_shortfall_is_the_accuracy.py` joins `e304`'s
decomposition rows to the stored `final_accuracy` and tests what the shortfall term is, writing
`runs/e312_the_shortfall_is_the_accuracy.json`. Seconds.*

## 1. What `e306`'s third quantity is

`e304` splits the shortfall `1 - R[T-1][j]` into a **lost** term and an **unlearned** term, and `e306` ordered the
five arms by all three. The first of those three is not a new quantity:

```
shortfall_mean = mean_j (1 - R[T-1][j]) = 1 - mean_j R[T-1][j] = 1 - final_accuracy
```

because `R[T-1]` **is** the per-task final accuracy and the corpus's `final_accuracy` is its mean over tasks.

**X1 MET** — the identity holds in **5581 of 5581** arm-replicates that carry both, and `lost + unlearned` equals the
shortfall in **5581 of 5581** as well, since `e304` defined it as their sum. **X2 MET** — read with each quantity's
own direction, the shortfall's majority edge is the accuracy's **on all ten pairs**, and the two orderings are the
same: `replay > naive > ewc-block > ewc-block-rand > ewc`.

## 2. So `e306`'s R2 is `e297`'s A2

**X3 MET**, checked across the two units rather than against a constant. This unit ranks **`ewc` worst on the
shortfall** and **`ewc` second on the forgetting term**; `e297` on its own population ranks **`ewc` last on
accuracy** and **`ewc` first on forgetting**. The same arm sits at all four positions.

So `e306`'s finding — *"the arm the corpus ranks second-best on forgetting is the arm with the most left to learn"* —
is the same sentence as `e297`'s A2, *"the diagonal is last on accuracy and first on forgetting"*, which was written
three fires earlier. **R2 is withdrawn as a finding** on `e306`'s row; what remains of the unit is R1 (three chains,
arithmetically true and now known to be about two of the corpus's own fields and their difference), R4 (which is what
made this checkable: the recomputed lost term is the stored `mean_forgetting` on all ten edges), and **R3, which is a
genuine third quantity** — the lost ordering against the unlearned ordering is the forgetting against the level a
task reached *when it was learned*, which is neither the accuracy nor the forgetting, and which `e310` then measured
as a position effect.

## 3. What this says about the line

`e304`'s decomposition is exact and its lost term is the corpus's field (D2, `e306`'s R4). **Two of the three
quantities it names are the fields the corpus already stores**, and the third is their difference. That does not
weaken `e304` — the split is what makes the *level at learning time* legible, and `e310` and `e311` then read the
position and the denominator off it — but it does mean the currency the corpus **lacks** is `unlearned`, and not a
"shortfall" that turns out to be the accuracy with its sign flipped.

## 4. What it cannot do

**The identity is arithmetic**, so X1 checks a definition and not a result. **`e297` reads the same field on a
different population**, so "the same arm at the end" is a claim about the ordering and not about the numbers — which
is `e308`'s subject, and its V1 established that the population this unit uses changes no edge of that reading. **The
three terms are linearly dependent by construction**, so nothing here says which two of them a benchmark should
report; it says that two of them are the fields the corpus already has, and that the bookkeeping question is which
one a methods table should print alongside the accuracy.
