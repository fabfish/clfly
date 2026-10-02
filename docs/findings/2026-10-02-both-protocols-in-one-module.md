# Both protocols in one module: the shared head's cost is unresolvable at +0.0208, and pairing bought nothing

*2026-10-02. `experiments/e354_both_protocols_in_one_module.py` runs both protocols and both arms in one process over
five seeds. Eight minutes. Writes `runs/e354_both_protocols_in_one_module.json`.*

## 1. The paired version `e353` asked for

`e353` ran the earned-label suite class-incrementally and closed on the weakness of its own comparison: *"the
protocol comparison is against one number on disk, `e352`'s 0.3333 over five seeds, so T3 is a difference of two
estimates with their own spreads and not a paired contrast; the paired version would need both protocols in one
module."*

**This is that module**: four arms per seed -- both protocols crossed with both arms -- built from the same seed's
own world and the same body initialisation, so the protocol cost is a difference of two arms of the same seed.

## 2. And the four cells reproduce the two earlier units to four decimals

| cell | here | in its own unit |
|---|---|---|
| task-incremental, `naive` | **0.3333** | 0.3333 (`e352`) |
| task-incremental, `replay` | **0.1146** | 0.1146 (`e352`) |
| class-incremental, `naive` | **0.3542** | 0.3542 (`e353`) |
| class-incremental, `replay` | **0.0875** | 0.0875 (`e353`) |

with the diagonals 0.8153, 0.7875, 0.8028 and 0.7806 as those units recorded them. Two modules written days apart,
one of them after the world gained a dimension and a channel, give the same four numbers exactly -- and this module
holds all four in one process without any of them moving.

## 3. The answer, and the correction

**T1 MET**: one world across all four arms, one distinct fingerprint each. **T3 MET**: the paired cost is
**+0.0208**, under the 0.05 the claim asked for -- and it is the same number `e353` reported unpaired. **T4 MET**:
the buffer is worth **-0.2188** in the task-incremental protocol and **-0.2667** in the class-incremental one,
**0.0479 apart**, so a replay buffer's value is a property of the buffer and not of the protocol.

**T2 NULL, and the reason is the unit's finding. The paired cost is +0.0208 on a sem of 0.0765 -- 0.27 sigma.** The
five per-seed costs are `[-0.1667, +0.0313, -0.0937, +0.2813, +0.0521]`: they swing across a range of 0.45 while
their mean is 0.02. **And pairing made the estimate worse, not better**: the unpaired sem of the same difference is
**0.0700, smaller than the paired 0.0765**, because the two protocols' per-seed forgetting is **not positively
correlated** across seeds -- the correlation is **-0.208**. So `e353`'s weakness was not the one its own note named:
what the pair of units actually established is that **the protocol cost is a point estimate with no resolution at
five seeds**, and at this spread it would need of order **270 seeds** to resolve 0.02 at two sigma.

**That is a benchmark property and not a defect of either unit.** The suite's forgetting is seed-dominated -- the
buffer's value is 11.38 sigma in `e353` on the same five seeds, while the protocol's is 0.27 -- so on the earned
label the hard question that can be answered at this power is *whether a method helps*, and the question of what the
read-out's protocol costs is one this benchmark cannot answer at five seeds and should not be quoted as if it had.

## 4. What it cannot do

*Two arms and two protocols, three tasks and five seeds*: the paired cost has four degrees of freedom and T2 could
not resolve 0.02, so a cost of that size is bounded and not measured. *A bespoke loop*, with `ewc`, the block
penalties, the matched-random control and the frozen controls unrun, so this is a benchmark's shape and not a method
comparison. *One world, one leak and one width*: `leak = 0.35`, eight dimensions and four symbols per task. *And the
two protocols differ only in the head*, which is what makes the cost attributable at all -- a shared head over a
wider or non-linear read-out is `e350`'s axis and not this unit's.
