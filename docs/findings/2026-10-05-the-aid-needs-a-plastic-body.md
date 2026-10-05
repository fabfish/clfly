# The aid needs a plastic body: the corpus's frozen-body cells are worth nothing, at any head

*2026-10-05. `experiments/e417_the_aid_needs_a_plastic_body.py` reads every corpus artifact that carries `naive` and
`replay` at five replicates or more -- **158** cells, with the corpus's own rule collapsing 24 second executions --
and splits them by the `config.frozen_body` field every artifact records. No training, no probe. Five claims,
registered before this unit's pass over the corpus.*

## 1. The ledger, split by the body

| body | cells | naive accuracy | buffer's gain | buffer's forgetting cut |
|---|---|---|---|---|
| **frozen** | **3** | 0.4490, **0.6146**, **0.6455** | **-0.0017**, **+0.0003**, **+0.0007** | **0.0000**, **0.0000**, **0.0000** |
| plastic | 155 | 0.25 to 0.94 | -0.05 to **+0.1799** | -0.02 to **+0.2953** |

The frozen cells are `e375`, `e358` and `e376`, all of the earned-label world at twenty replicates.

| claim | measured | verdict |
|---|---|---|
| AN1 the ledger is carried | **158** cells, **3** of them frozen, at five replicates or more | **MET** |
| AN2 and on a frozen body the buffer is worth nothing | gains **-0.0017** to **+0.0007** | **MET** |
| AN3 and its forgetting cut is exactly zero | **0.0000** on all three, to a thousandth | **MET** |
| AN4 and the plastic cells are worth a tenth | **29** cells below 0.58 of accuracy gain at least **+0.10** | **MET** |
| AN5 and the head's own fitting does not move it | levels **0.1965** apart, gains **0.0024** apart | **MET** |

## 2. What the control says

**The aid's worth is not the head's accuracy.** `e412` and `e413` both registered the confound under the budget
ladder: the naive arm's own accuracy rises along the same axis as the aid's gain, so "the aid goes with what was
learned" was a reading over a joint ramp. The corpus carries the control for it. On a **frozen** recurrent body the
buffer is worth **-0.0017**, **+0.0003** and **+0.0007** of final accuracy and its forgetting cut is **exactly 0.0000**
on all three cells, while **29** plastic cells sitting below 0.58 of naive accuracy gain a tenth or more, up to
**+0.1799**. Two of the three frozen cells read **0.6146** and **0.6455** -- more accurate than every one of the six
earned-label worlds, whose best is 0.5500.

**And the head's own fitting does not move it.** `e375` and `e376` are one configuration whose only differing
`config` field is `lr`, with the draws identical, so the head's step size is the intervention: it is worth **0.1965**
of naive accuracy (0.4490 to 0.6455) and the aid is worth **0.0024** more on the better-fitted cell, with the
forgetting cut exactly 0.0000 on both. `e376` raised the level by 0.1965 and left the buffer with nothing to add, so
what the aid needs is not a well-fitted head but a body that can still move.

**And the joint ramp in the budget ladder is therefore read correctly.** Along the card's world's ladder the naive
accuracy rises 0.2438 to 0.5191 and the aid rises to +0.1594; the frozen cell at 0.6455 of accuracy -- a *higher*
level -- has no aid at all. What the ladder's rise tracks is the body's training, which the ladder also varies, and
not the head's level, which the frozen pair varies alone.

## 3. What it cannot settle

- **One control and three cells**: the corpus's frozen-body setting is three runs of the earned-label world, so the
  split is that world's and not the benchmark's.
- **And the ledger is not a design**: the cells are one configuration each at five to forty replicates, and the plastic
  cells differ from the frozen ones in many fields besides the body.
- **And the arms are the corpus's**: `replay` is the corpus's buffer (`--replay-per-task 16 --replay-batch 16`), and
  the penalty arms are not in this reading.
- **And the metric is the corpus's**: `mean_forgetting` is the retention matrix's diagonal minus its last row, which
  `e305` showed cannot see the part an arm never learned -- which is also why a frozen body's cut reads exactly zero
  rather than being undefined.
- *And a ledger is not a mechanism.*
