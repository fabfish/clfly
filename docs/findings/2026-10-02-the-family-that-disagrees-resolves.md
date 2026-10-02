# The family that disagreed resolves: at 300, with twenty replicates, `replay` is ahead at 3.11 sigma

*2026-10-02. One run: the `fisher-batches 8` configuration of `e101_rate_fb8`, its flags derived from that
artifact's own config through `e163 --command`, at `circuit_size = 300` and twenty replicates into
`runs/e347_fb8_at_cs300.json`. Nineteen minutes. Read by `experiments/e347_the_family_that_disagrees.py`, writing
`runs/e347_the_family_that_disagrees.json`.*

## 1. The residue `e346` named

`e346` read every experiment in the corpus carrying both the `replay` and the `ewc-block` arm and found the ordering
travels: fourteen resolve it in `replay`'s favour and none resolve it against. The six point estimates that go the
other way were not six substrates but one family, and `e346` said what it could not do about them: *"it cannot
separate 'the ordering travels' from 'the ordering was the same experiment'"*, because no run was made.

**The family is `fisher_batches` 8 or 128, where the rest of the corpus uses 32, and every one of its disagreeing
members is at `circuit_size = 800` with five replicates.** Of its thirteen members, five are negative -- `e101_rate_fb8` at **-0.0208 (1.43σ)**, `e101_rate_fb128` at **-0.0222 (1.54σ)**, `e102_rate_fb8_omp1` at **-0.0014
(0.10σ)**, `e102_rate_fb8_rerun` and `e164_fb8_today_a` at **-0.0083 (0.69σ)** each -- and **all five are at the 800
budget on the overlap suite**. Its six 300-budget members are all positive, at 2.57 to 7.56 sigma, and **all of them
are the assembly or sequence suite instead**; the corpus's only 300-budget overlap-suite artifact, `e99`, carries
`fisher_batches = 32` and is outside the family. So in this family **budget and suite have never been separated.**

**This run separates them.** It holds the family's own overlap suite, basis, classes, learning rate, lambda, buffer
sizes and seed, moves the budget from 800 to 300, and raises the replicates from five to twenty.

## 2. The answer

| read | value | sem | sigma |
|---|---|---|---|
| `replay` − `ewc-block`, accuracy | **+0.0177** | 0.0057 | **3.11** |
| `replay` − `ewc-block`, forgetting | **-0.0240** | 0.0101 | **2.36** |

**T2 MET**: the ordering resolves on this substrate **for `replay`**, at 3.11 sigma, where all five of the family's
800-budget members sit inside 1.54 sigma and four of them are on the wrong side of zero. **T4 MET**: `replay` forgets
less by **-0.0240 at 2.36σ**, so the accuracy is not bought with forgetting. **T3 MET**: the new contrast is
**0.0296** from the family's own artifact-level mean of **+0.0473** over its thirteen experiments, inside the 0.03
band the registration asked for and not the 0.05 that would have said the budget moves this contrast.

**So the family's disagreement does not survive power and does not survive the budget.** `e346`'s count of
experiments resolving against `replay` stays at zero, and the family is now the first place where a five-replicate
estimate on the wrong side of zero has been re-measured at four times the replicates: the sign goes with the
corpus's twenty positive estimates and the resolution is 3.11 sigma.

## 3. One claim fired, and it is the arm list

**T1 FALSIFIER FIRED.** The derived configuration differs from `e101_rate_fb8`'s in three fields, and the claim
allowed two: `circuit_size` (800 to 300) and `repeats` (5 to 20) are the intended moves, and **`methods`** is the
third -- the source records the five-arm list `naive,ewc,ewc-block,ewc-block-rand,replay` and this run trained
`replay,ewc-block`, narrowed to exactly the two arms the contrast is about. Every other field the derivation set
agrees, and both arms compared here are in the source's list, so the contrast is the same contrast on a narrower
run; but `methods` is a config field and the registered falsifier said any other field differing, so it fired and is
reported as fired rather than excused.

## 4. What it cannot do

*One run, one budget and one seed stream*: this uses the corpus's `seed0 = 0` and the family's own suite and seed, so
it is the same experiment at a smaller circuit and not an independent stream -- the independent-stream question is
`e337`'s and `e340`'s axis and not this unit's. *Twenty replicates give the power to see a family-sized effect and
not to bound a small one*: an unresolved T2 would have been a bound and not a nil, and this one resolved. *The family
is a config field and not a mechanism*: nothing here says why `fisher_batches` would move a method contrast, and the
run does not vary it. *The suite still moves with the budget for the rest of the family*: this run is the first
family member at 300 **and** the overlap suite, which is what makes it a separation, but it is one cell of a two-by-
two and the other three cells are still the corpus's. *And `ewc-block` is one penalty*: nothing here is about `ewc`,
`ewc-block-rand`, the lambda, or the basis contrast the audits left a null.
