# "On disk" is not a definition: 262 diagonal arms where the paper says 17, and its conclusion is falsified

*2026-09-29 01:10. Runs: **none new** — `experiments/e278_on_disk_is_not_a_definition.py` enumerates the population a
paper sentence names in prose and checks the sentence's own count, extremum and conclusion against it, writing
`runs/e278_on_disk_is_not_a_definition.json`. Seconds.*

## 1. The item: a population named in prose is part of the claim

`e277` found the paper's **counts** are scopes in disguise. An **extremum over a population** is the same defect one
step further out, because the population itself is part of the claim and the paper names it in prose:

> the hardened row's EWC cell (+0.010 ± 0.010) is **below every one of the 17 diagonal arms on disk**, whose minimum is
> +0.0208

**"On disk" is not a definition.** The sentence does not say how the population was enumerated, so as written it is
**unfalsifiable** — and under its plain reading, every artifact's diagonal arm under `runs/`, it is **false**. The
module enumerates it, counts it, reads its minimum, and checks the sentence's own comparison against it.

## 2. What the enumeration gives

| the sentence says | the enumeration gives |
|---|---|
| a population of **17** | **262** entries over 13 arm names — **15.4×** |
| a minimum of **+0.0208** | **0.00022** (`e228_rho05_cs300`, the `real` arm) — 95× below, with **71** entries under the quoted figure |
| its cell **+0.010** is below every one | **20 entries are below it**: 0.00598 (`e208_hole_sweep_cs800_3seeds`), 0.00022, 0.00033, and seventeen more |

**X1, X2 and X3 all MET.** The sentence was wrong three ways in one clause: about how large its population is, about
its minimum, and about its conclusion.

## 3. Either reading is a defect, and they are different defects

**If "on disk" means every diagonal arm under `runs/`**, the sentence is false as read: its cell is above twenty of
them. **If it means some narrower set, the sentence does not say which**, and a reader cannot check it at all. The
first is a defect of fact and the second of scope, and the fix for both is the same thing: **the enumerator** — which
artifacts, which field, which date — and not a corrected number.

## 4. The correction applied

The sentence now carries a clause naming the field the enumeration reads
(`topologies[*]["diagonal(EWC)"]["analytic"]["excess_mean"]`), the population it gives today (262), its minimum
(0.00022) and the twenty counterexamples, with the finding path. The clause is deliberately an **enumerator** rather
than a replacement count, because a replacement count would go stale the same way.

## 5. What it cannot do

**The module's enumeration is the one the words admit and not necessarily the one the author used**, so a narrower
population turns X1 to X3 into a *disagreement* rather than a falsehood — the report prints the population it
enumerated beside the sentence's own numbers so a reader can see which is which, and that is the honest limit of an
audit over prose. The field read is one path in `topologies`, so an artifact recording a diagonal arm elsewhere is
invisible. **X3 borrows the sentence's own cell value** rather than re-measuring it, since the claim being checked is
the comparison the sentence makes. And nothing here says the sentence was wrong **when it was written**: 17 entries and
a minimum of +0.0208 is a plausible reading of the corpus as it stood, which is exactly the point — the population
grew, and the sentence did not say what it was counting.
