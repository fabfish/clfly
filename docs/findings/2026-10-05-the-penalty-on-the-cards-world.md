# The penalty on the card's world: the buffer beats the basis-matched penalty on both axes at eleven sigma

*2026-10-05. `experiments/e415_the_penalty_on_the_cards_world.py` reads the one cell of the earned-label world that
carries a penalty arm. `e356` rolled the card's world at five hundred iterations with **`naive`, `ewc-block` and
`replay`** in a single run and twenty replicates, and `e355` rolled the same cell at five replicates with the matched
random control `ewc-block-rand` beside them. No training, no probe. Five claims, registered before this unit's pass
over either artifact.*

## 1. The three arms on one cell, paired over the same twenty seeds

| arm | final accuracy | mean forgetting |
|---|---|---|
| `naive` | 0.5493 | 0.4099 |
| `ewc-block` | 0.5219 | 0.3750 |
| **`replay`** | **0.6983** | **0.1229** |

| contrast (paired, n = 20) | final accuracy | mean forgetting |
|---|---|---|
| `replay` minus `ewc-block` | **+0.1764** (11.50 sigma) | **-0.2521** (11.65 sigma) |
| `ewc-block` minus `naive` | -0.0274 (-1.95 sigma) | -0.0349 (-1.51 sigma) |
| `replay` minus `naive` | +0.1490 (9.43 sigma) | -0.2870 (13.10 sigma) |

| claim | measured | verdict |
|---|---|---|
| AP1 the cell is carried and it is the card's world | three arms at **20** replicates over **21 of 21** shared fields | **MET** |
| AP2 and the buffer beats the penalty on accuracy | **+0.1764** at **11.50 sigma** | **MET** |
| AP3 and on forgetting too | **+0.2521** at **11.65 sigma** | **MET** |
| AP4 and the penalty is not worth the naive arm here | **-0.0274** | **MET** |
| AP5 and the block basis is not distinguished from its matched control | **+0.0000** and **-0.0125** over 5 replicates | **MET** |

## 2. What the cell says

**The buffer wins on both axes, and by a wide margin.** On the closed-loop earned-label world at five hundred
iterations the arm that stores sixteen transitions per task and replays them finishes the three-task sequence at
**0.6983** where the biological-basis penalty finishes at **0.5219**, eleven and a half sigma apart over the twenty
shared seeds, and it forgets **0.2521** less. `e276` measured replay over penalty at twelve sigma on the overlap
suite; this is the same ordering on a **different substrate** -- the closed-loop world with the cue at step 0 and the
action driving the world -- at the same strength.

**And the penalty's own worth is not resolved against doing nothing.** `ewc-block` minus `naive` is **-0.0274** on
accuracy at **-1.95 sigma** and **-0.0349** on forgetting at **-1.51 sigma**: on this substrate the penalty neither
buys accuracy nor reliably keeps any, while the buffer buys both. That is the opposite of the overlap suite's picture
for accuracy, where the constrained arms beat `naive`, and it is what `e411`'s and `e413`'s gap hid.

**And the basis carries nothing its matched control does not.** On the five-replicate cell `ewc-block` and
`ewc-block-rand` are identical on final accuracy to five parts in a billion and differ by **-0.0125** on forgetting,
both inside the 0.05 bar. So on the card's world the block partition is not doing work that a random partition of the
same size does not do, and AP5 is a bound at five replicates rather than a resolution.

## 3. What it cannot settle

- **One world and one penalty strength**: the card's world at `lam = 1.0` with `ewc-block`, so the `lam` ladder and
  the diagonal penalty (`ewc`) are not in this cell.
- **And the world's rule is not the card's**: the artifact agrees with `e380` on all twenty-one shared fields, but
  `e380` records the world as coupled and this artifact carries no such field, so what is measured is the buffer
  against the penalty on the earned-label world's **uncoupled** rule, which predates `e359`.
- **And the control has five replicates**: AP5 is a bound.
- **And the metric is the corpus's**: `mean_forgetting` is the retention matrix's diagonal minus its last row, which
  `e305` showed cannot see the part an arm never learned.
- *And a probe is not a mechanism.*
