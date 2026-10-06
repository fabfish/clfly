# Where the anchors' movement goes on the card's world: the anchors hold the weights harder than the corpus's penalty cells, and the retention is the buffer's and not the holding's

*2026-10-06. `experiments/e440_where_the_anchors_movement_goes.py` reads the two three-arm rolls of the card's world --
`e438`'s and `e439`'s -- through the corpus's own instruments. `e438` and `e439` found that on that world neither
anchoring is a buffer and both of them closed on the same sentence, *an arm is not a mechanism*, naming `e432`'s split of
interference into its weight and bias halves and `e433`'s two parameters as what had not been asked of that world. No
training and no probe. Five claims; the two parameters in section 1 were inspected while the module was written, so
**BR2 and BR3 are confirmatory** and stated as `e276` stated his, and the interference split in BR4 and BR5 was not
computed before it was registered.*

## 1. The two parameters, cell by cell

| roll | arm | drift ratio | bias ratio | held | pushed |
|---|---|---|---|---|---|
| penalty | `ewc-block` | **0.6234** | **1.4483** | yes | yes |
| penalty | `replay` | 0.9556 | **0.8531** | yes | no |
| rand | `ewc-block-rand` | **0.6188** | **1.4622** | yes | yes |
| rand | `replay` | 0.9556 | **0.8531** | yes | no |

| for comparison, `e433`'s pooled pattern over the corpus | drift ratio | bias ratio |
|---|---|---|
| `ewc` / `ewc-block` / `ewc-block-rand` | 0.718 / 0.751 / 0.752 | 1.508 / 1.473 / 1.456 |
| `replay` | 0.984 | 0.946 |

| the share of the whole-body interference term carried by the bias half | task it accounts for 1 | 2 |
|---|---|---|
| the baseline `naive` | 0.3776 | 0.4873 |
| `ewc-block` | **0.8956** | **0.9366** |
| `ewc-block-rand` | **0.4900** | **0.8705** |
| `replay` | **0.3159** | **0.4073** |

| claim | measured | verdict |
|---|---|---|
| BR1 the ledger is carried | **4** cells over **2** rolls at twenty replicates, all three fields present | **MET** |
| BR2 and the anchors hold the weights on this world too | drift ratios **0.6234** and **0.6188** | **MET** |
| BR3 and they push the bias | bias ratios **1.4483** and **1.4622** | **MET** |
| BR4 and their interference runs through the bias on every task it accounts for | **0.8956 / 0.9366** and **0.4900 / 0.8705**, against the baseline's **0.3776 / 0.4873** | **MET** |
| BR5 and the buffer's does not | **0.3159 / 0.4073** | **MET** |

## 2. What the two instruments say here

**The anchors' two parameters are the corpus's pattern, and harder on the weights.** `e433` pooled the corpus's penalty
cells at drift ratios **0.718**, **0.751** and **0.752** with bias ratios **1.508**, **1.473** and **1.456**; the card's
world reads **0.6234** and **0.6188** with **1.4483** and **1.4622**. So the world where the anchors are *not* buffers is
a world where they hold the recurrent weights **more** tightly than the corpus's typical penalty cell -- by **0.10** to
**0.13** of the baseline's drift -- while their push on the bias sits at the corpus's own level. The anchors are not
failing to anchor here; they are anchoring harder.

**And the buffer's cell is the corpus's buffer's, from the other side.** `replay` moves the weights to **0.9556** of the
baseline's drift and the bias to **0.8531** of its distance from zero, against the corpus's **0.984** and **0.946** -- so
on this world the buffer is the arm that disturbs the parameters least, and it is the only cell of the four that does not
hold-and-push. The two arms the corpus's pattern separates are separated here in the same direction and by a wider
margin on the weights.

**And that is why the split does not carry the anchors' price.** `e438` and `e439` measured that the anchors buy
**-0.0474** and **-0.0229** of forgetting and pay **-0.0302** and **-0.0365** of mean diagonal for it, while the buffer
buys **-0.2844** and pays nothing. Read beside this unit's parameters the two facts do not line up: **the arm that buys
six times the retention holds the weights to 0.956, and the arms that hold them to 0.62 buy almost none of it.** Across
the three arms of this world, holding the recurrent weights where they are is not what the retention is bought with --
which is `e433`'s sentence read from the other end, and it is offered as a reading of three arms and not as a law.

**And the interference split separates the anchors from the buffer cleanly, and the two anchors from each other less
so.** The whole-body term is carried by the bias half in **0.8956** and **0.9366** of `ewc-block`'s cases, **0.4900** and
**0.8705** of `ewc-block-rand`'s, and **0.3159** and **0.4073** of the buffer's, against the baseline's **0.3776** and
**0.4873** -- so `e432`'s finding that a penalty's interference runs through the bias travels to this world, and the
buffer's does not. The one place the two anchors differ is the **first** task, **0.8956** against **0.4900**: the basis
makes no difference to either parameter above and no difference to the accuracy `e438` and `e439` measured, and it does
change which half carries the interference on one of the two tasks the account covers. This unit has no sigma on that
cell and offers it as an observation rather than a claim.

## 3. What it cannot settle

- **Two cells**: one world and one order, so this is the corpus's pattern read at two anchor cells and not a
  distribution, and the section 2 reading rests on three arms rather than on a sample.
- **And one partition draw**: the matched-random partition is a draw of the same group sizes and not the family of them.
- **And a parameter is not a cause**: that the anchors hold the weights while their accuracy falls below the baseline
  does not say the holding causes the fall, and neither half of `e432`'s split is a counterfactual.
- **And the split is one implementation's**: the first-order whole-body term is the runner's own account of interference
  and not an independent measurement of it, so BR4 and BR5 carry whatever that account carries.
