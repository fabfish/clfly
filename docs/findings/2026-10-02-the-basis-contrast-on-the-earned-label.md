# The basis contrast on the earned label is a null at 1.47 sigma, as the state read-out left it

*2026-10-02. One runner invocation -- `--methods ewc-block-rand --repeats 20` at `e356`'s exact flags -- into
`runs/e357_earned_label_rand_20reps.json`, paired against `e356`'s own `ewc-block` arm, which is already on disk at
twenty replicates. Fourteen minutes for the new arm. Read by
`experiments/e357_the_basis_contrast_on_the_earned_label.py`.*

## 1. The pair, and why half of it is not a new run

`e355` and `e356` moved the corpus's method contrast onto the earned label and `e356` resolved it at **11.65 sigma**
over twenty replicates. Both closed with the same missing piece: *"the basis contrast -- `ewc-block` against the
size-matched random partition, the corpus's own headline and the null eleven audits left standing -- is not in this
run."*

**`e356`'s artifact already carries the biological arm** on exactly this configuration, so only the matched-random
arm is missing, and one run at the same flags produces it. That the two files are one configuration is **measured,
not assumed**: both record the world's read fingerprint **3a7ba76b3619** and the matched-random partition
**0467b1a5f7a0 of 98 groups**, the same basis, the same three tasks at read-out width 8, the same `seed0 = 0` and
twenty replicates each -- and the fields that differ between the two runs are **none**, because each file's own
`methods` list is not one of them.

## 2. The answer

| arm | final accuracy | diagonal | `mean_forgetting` | sem | paired channel | sigma |
|---|---|---|---|---|---|---|
| `ewc-block` | 0.5219 | 0.7719 | 0.3750 | 0.0190 | +0.2660 | 16.52 |
| `ewc-block-rand` | 0.5479 | 0.7740 | 0.3391 | 0.0203 | +0.2899 | 19.48 |

chance 0.2500. **T1 MET**: one configuration in two artifacts, twenty paired replicates, and every shared field --
world, partition, basis, tasks, widths, seeds, sizes -- agreeing.

**T2 MET, and it is the corpus's own headline asked in a new place: the basis contrast does not resolve.**
`ewc-block` minus `ewc-block-rand` on `mean_forgetting` is **+0.0359 on a sem of 0.0244, 1.47 sigma** -- inside the
0.05 the claim allowed and far from the 0.10 that would have made the connectome's block structure matter. **T3
MET**: on the diagonal it is **-0.0021 at 0.22 sigma**. **T4 MET**: both arms are learned (**+0.5219** and **+0.5240**
above chance) and both are earned (**+0.2660 at 16.52 sigma** and **+0.2899 at 19.48 sigma**), so the contrast is not
being read between an arm that works and one that does not.

**And the sign is worth recording: it points against the biological partition.** The matched-random control forgets
**0.3391** where the cell-class partition forgets **0.3750**, and its final accuracy is 0.5479 against 0.5219. That
is the same asymmetry the C2b line's audits found on the state read-out -- the biological anchoring contributes
nothing resolvable over a size-matched random basis -- now on a task whose answer is read from the environment, with
twenty replicates and a resolution bound of about 0.05.

## 3. What the three units together now say

| contrast, on the earned label, twenty replicates | value | sigma |
|---|---|---|
| `replay` minus `ewc-block`, forgetting | **-0.2521** | **11.65** |
| `ewc-block` minus `ewc-block-rand`, forgetting | +0.0359 | 1.47 |
| `ewc-block` minus `ewc-block-rand`, diagonal | -0.0021 | 0.22 |
| the paired channel reading, per arm | +0.2660 to +0.4434 | 16.52 to 34.84 |

**The earned label reproduces the corpus's method line and not its basis line.** A replay buffer is worth a quarter
of a point of forgetting at eleven sigma; the block partition a given basis is drawn from is worth nothing
resolvable; and the answer is earned in every arm at sixteen sigma or better. That is the shape the state read-out's
own record has, on a substrate where unwired the read-out is a constant.

## 4. What it cannot do

*The pair is assembled from two artifacts rather than produced in one run*: what makes it legitimate is the recorded
partition fingerprint and the per-replicate seed stream agreeing, both checked in T1, and not the sharing of a
process -- and the runner's own matched-pair block would compute the same contrast in one pass, which is the cheaper
form for a future unit. *Two arms and one basis*: `cell_class` only, with `--anchor-bias`, the frozen controls and
the oracle line unrun, and nothing here is about `ewc` or the lambda. *One world, one leak and one width*:
`leak = 0.35`, eight dimensions and four symbols per task. *And a null is a bound*: twenty replicates bound the
contrast at about 0.05, so a basis effect smaller than that is not excluded, only unsupported.
