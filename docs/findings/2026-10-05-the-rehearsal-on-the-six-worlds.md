# The rehearsal on the six worlds: the aid is the same on every one, and it swamps the draw four to five times over

*2026-10-05. `experiments/e411_the_rehearsal_on_the_six_worlds.py` reads the second arm off the same six
five-hundred-update runs `e410` read -- the `replay` arm's final accuracy and mean forgetting over twenty replicates,
each beside the `naive` arm's -- and puts them against the six worlds' own span on the benchmark's metric. No
training, no probe. Five claims, registered before any of the second arm's matrices was read.*

## 1. The benchmark's own two-term comparison, on the six worlds

| world | naive acc | replay acc | gain | naive mf | replay mf | cut |
|---|---|---|---|---|---|---|
| **card** | 0.5191 | 0.6785 | **+0.1594** | 0.3750 | 0.0906 | **+0.2844** |
| **9** | 0.5323 | 0.6896 | +0.1573 | 0.4052 | 0.0979 | +0.3073 |
| **6** | 0.5215 | 0.6757 | +0.1542 | 0.4063 | 0.0917 | +0.3146 |
| **14** | 0.5434 | 0.6969 | +0.1535 | 0.3885 | 0.1130 | +0.2755 |
| **3** | 0.5500 | 0.6990 | +0.1490 | 0.3865 | 0.1187 | +0.2677 |
| **1** | 0.5479 | 0.6809 | +0.1330 | 0.3255 | 0.0917 | +0.2339 |

The worlds are ordered by their accuracy gain, best first. The same twenty replicates and the same three-by-three
retention matrices that `e410` read on the `naive` arm are carried on the `replay` arm on all six worlds.

| claim | measured | verdict |
|---|---|---|
| AP1 the second arm's matrices are carried | six worlds, **20** replicates and **20** matrices each | **MET** |
| AP2 the rehearsal helps on every world | gains **+0.1330** to **+0.1594**, all positive | **MET** |
| AP3 and by at least a tenth | least **+0.1330** on cue 1 | **MET** |
| AP4 and it cuts the forgetting on every world | cuts **+0.2339** to **+0.3146**, all above a fifth | **MET** |
| AP5 and the aid swamps the draw | **4.30** times the naive span of **0.0309** | **MET** |

## 2. What the two terms are worth

**The arm is worth thirteen to sixteen hundredths of accuracy and a fifth to a third of forgetting, on every world.**
Storing sixteen transitions per task and replaying them moves the mean final accuracy from **0.5191 to 0.6785** on the
card's world and from **0.5479 to 0.6809** on cue 1, and cuts the mean forgetting from **0.3255 to 0.0917** on cue 1
and from **0.4052 to 0.0979** on cue 9. Every cut is above **0.23** and every gain above **0.13**: the aid is not a
property of the draw, it is the term the corpus's own protocol changes.

**And the draw is worth three hundredths on the same metric, so the benchmark is measuring the arm and not the
world.** `e410` found the six worlds one population on the `naive` arm, spanning **0.0309** in final accuracy. The
smallest of the six gains here is **+0.1330**, which is **4.30 times** that span, and the six gains themselves span
only **0.0264** -- less than the draws they are measured across. A user of this benchmark choosing a world is
choosing a term worth three hundredths; choosing an arm is choosing one worth thirteen to sixteen.

**And the card's world is where the two terms are cleanest.** It has the highest world reading (0.7729), the lowest
final accuracy (0.5191) and the largest gain (**+0.1594**), so the world whose head fits worst is the one the
rehearsal helps most: what the `naive` arm loses there is the same forgetting every other world loses. `e371` read
this world's 0.2844 cut alone; it is the second largest of the six and the ranking across worlds carries no
structure.

## 3. What it cannot settle

- **One rehearsal setting**: `--replay-per-task 16 --replay-batch 16`, so what is measured is the corpus's own buffer
  and not the aid in general.
- **And the penalty arms are absent**: this cell was run with `naive` and `replay` only, so `e276`'s
  replay-over-**penalty** contrast is not available on these six worlds.
- **And the metric is the corpus's**: `mean_forgetting` is the retention matrix's diagonal minus its last row, which
  `e305` showed cannot see the part an arm never learned.
- *And a probe is not a mechanism.*
