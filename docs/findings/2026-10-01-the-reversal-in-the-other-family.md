# The reversal in the other family: it reproduces in `ewc` at six sigma and does not reproduce in the other two methods

*2026-10-01 11:44. Runs: **two new** — `runs/e316_assembly_as_built.json` and `runs/e316_assembly_reverse.json`,
written by `e8_rate_network.py --circuit-size 300 --readout-size 32 --train 96 --test 48 --iters 500 --repeats 10
--methods naive,ewc,replay` with `--task-order as-built` and `--task-order reverse`. About six minutes each.*

## 1. What `e315` could not say

`e315` made the corpus's first permuted suite and found that **all six** of its moved-position contrasts favoured the
run that trains the task first. Its own limitations named two things it could not say: it was **one configuration and
five replicates**, and its control claim had fired on a **mis-specified registration**. This unit repeats the
reversal on the **assembly** suite — `odour_identity`, `heading`, `odour_input`, three different modalities rather
than three draws from one construction and the family `e310` found the effect in at 78% rather than 67% — at **ten
replicates per arm**, with the control taken **inside each method**.

**Q1 MET** — same circuit (`mb+cx+al@n952`), same read-out subset (`59926518137c`), same seeds, and one task list is
the other reversed.

## 2. The result: `ewc` reproduces, `naive` and `replay` do not

`delta` is forwards minus backwards, paired over the ten replicates. A negative delta at the first position or a
positive one at the last is a contrast **against** the position effect:

| method | task | positions | delta | sigma | |
|---|---|---|---|---|---|
| `ewc` | `odour_identity` | 0 → 2 | **+0.0854** | **4.38** | with |
| `ewc` | `odour_input` | 2 → 0 | **−0.0958** | **6.27** | with |
| `naive` | `odour_identity` | 0 → 2 | −0.0042 | 0.69 | **against** |
| `naive` | `odour_input` | 2 → 0 | +0.0021 | 0.21 | **against** |
| `replay` | `odour_identity` | 0 → 2 | +0.0062 | 0.71 | with |
| `replay` | `odour_input` | 2 → 0 | +0.0042 | 0.41 | **against** |

**Q2 FIRED** — **3 of 6** moved-position contrasts favour the first-trained run, not 6 of 6, and the three that do
not are all under 0.9 sigma. **Q4 MET** — the largest contrast is **6.27 sigma** over ten replicates, so the effect
this family carries is not a small-sample artefact. **Q3 FIRED** — the unchanged-position task is the smallest of its
three contrasts in **1 of 3** methods (`ewc`), and in `naive` and `replay` a moved contrast is smaller than the
control.

## 3. What that says

**The position effect is method-dependent in this family and was not in the other.** In `e315`'s overlap suite the
effect ran through `ewc` (1.90, 2.63), `replay` (3.16) and `naive` (0.80, 1.58) — the direction unanimous, the
magnitude varying. Here it is `ewc` alone at four to six sigma, with `naive` and `replay` at or below 0.7.

So the honest state of the axis is: **reversing the order moves the level, by a lot in one method and by nothing
resolvable in two others, on one family of three modalities — and by a little in all three methods on the family of
three random draws.** `e310`'s corpus-wide reading (a four-point first-to-middle gap, in 90% of configurations) is
about the *average* over arms and is not contradicted; what these two runs add is that a single configuration's
reversal can be carried by one method, and that a benchmark permuting its suite cannot assume the effect lands on
every arm.

## 4. What it cannot do

**Two configurations and two orders**, so the direction is now one unanimous instance and one method-specific one,
and neither unit samples orders. **The magnitudes are each configuration's**: five replicates on the overlap family
and ten here, so the sigmas are comparable in sign and not in size. **The task names differ**, so nothing pairs
`odour_identity` with `ov1_t0`. **The control is weaker than the contrast**: the unchanged-position task still has
the other two tasks around it changed, so its "no move" is about the position being held and not about a run
perturbed in one place only. **And `ewc` is the method whose arm reads the largest penalty in this design**, so
whether the effect is *about* the penalty is a third configuration's question.
