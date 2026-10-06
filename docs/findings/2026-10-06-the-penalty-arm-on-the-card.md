# The penalty arm on the card's world: `ewc-block` is not a buffer there -- it buys a small forgetting reduction and pays it back in accuracy

*2026-10-06. `experiments/e438_the_penalty_arm_on_the_card.py` reads the **first three-arm roll** of the card's world.
`e380` rolled it with `naive` and `replay` at twenty replicates, `e436` and `e437` rolled it twice more to read the
order, and **no unit of the corpus had ever put a penalty arm on it** -- so the position ledger `e437` reads was a
ledger of one buffer, and the corpus's own headline method contrast, `replay` against `ewc-block`, had never been asked
on a task whose answer is read from the environment. This unit drove the third arm: the same configuration with
`--methods naive,ewc-block,replay` alone differing from `e380`'s, at the same twenty replicates on the same as-built
order. Five claims, registered before the new run's reading was opened.*

## 1. The three arms

| arm | first | middle | last | mean | mean forgetting |
|---|---|---|---|---|---|
| `naive` | +0.3240 | +0.4292 | +0.8042 | +0.5191 | 0.3750 |
| `ewc-block` | +0.3865 | +0.3937 | +0.6865 | **+0.4889** | 0.3276 |
| `replay` | **+0.6135** | **+0.6781** | +0.7438 | **+0.6785** | **0.0906** |

| gain over `naive`, by position | first | middle | last |
|---|---|---|---|
| `replay` | **+0.2896** | **+0.2490** | **-0.0604** |
| `ewc-block` | +0.0625 | **-0.0354** | **-0.1177** |
| `ewc-block` over `replay` | -0.2271 | -0.2844 | -0.0573 |

| contrast, paired over the twenty replicates | mean diagonal | mean forgetting |
|---|---|---|
| `replay` minus `naive` | **+0.1594** at **11.97** sigma | **-0.2844** at **14.37** sigma |
| `ewc-block` minus `naive` | **-0.0302** at **1.77** sigma | -0.0474 at **2.77** sigma |
| `replay` minus `ewc-block` | **+0.1896** at **10.89** sigma | **-0.2370** at **10.69** sigma |

| claim | measured | verdict |
|---|---|---|
| BN1 and the run is one configuration | **3** arms at twenty replicates, **56** compared fields agreeing with `e380`, and `naive` and `replay` **bit-identical** to it replicate for replicate | **MET** |
| BN2 and the penalty arm pays the last position too | `ewc-block` over `naive` on the last-taught task is **-0.1177** | **MET** |
| BN3 and the two buffers pay it alike | the two costs are **-0.1177** and **-0.0604**, **0.0573** apart | **NULL** |
| BN4 and the buffers' advantage is the earlier positions' | `ewc-block` over `naive` at the first two positions is **+0.0625** and **-0.0354** | **FALSIFIER FIRED** |
| BN5 and the corpus's method contrast holds on this substrate | `replay` over `ewc-block` on the mean diagonal is **+0.1896** at **10.89** sigma | **MET** |

## 2. What the three arms say

**The ledger `e437` measured is `replay`'s, and the penalty arm is not a buffer on this world at all.** `e437` read
the buffer's gain over `naive` at the first position (**+0.2896**), the middle (**+0.2490**) and the last
(**-0.0604**) and found a cliff at the last position. Asked the same question of the arm that anchors toward a basis,
the card's world answers **+0.0625**, **-0.0354** and **-0.1177**: the penalty is ahead of the baseline only at the
first position, and at the middle and the last it is *behind* it. Its mean diagonal is **+0.4889** against `naive`'s
**+0.5191**, a difference of **-0.0302** that twenty replicates do not resolve (**1.77** sigma). So BN4's falsifier
fired on a claim that expected the two buffers to look alike, and what it fired on is this: **the earlier-position
advantage is a property of the buffer and not of anchoring**, and a card that says *the buffer's gain* should say
which arm it means.

**And what the penalty buys on this world is a little stability, paid for in full.** Its forgetting is lower than
`naive`'s by **-0.0474**, resolved at **2.77** sigma, and its accuracy is lower by **-0.0302**, unresolved. The
per-position pairing says where the two sides of that trade sit: the penalty is better than the baseline on the
**oldest** task by **+0.0625** (**3.52** sigma) and worse on the **newest** by **-0.1177** (**3.71** sigma), which is
the stability-plasticity trade in its textbook shape and, on this substrate, at a net loss. `replay` is the other
thing entirely -- **+0.1594** at **11.97** sigma on accuracy with **-0.2844** at **14.37** sigma on forgetting -- so
the contrast the corpus quotes as its headline reads **+0.1896** at **10.89** sigma here, and `e276`'s twelve-sigma
result survives the earned-label substrate and the closed loop.

**And the two buffers do pay the last position about alike, which the unit's own bar could not separate.** BN3 asked
whether the two last-position costs differ by at most **0.05** and they differ by **0.0573** -- inside the null band
between **0.05** and **0.10**, so the reading is that the cliff at the last position belongs to *both* buffers, at
**-0.0604** and **-0.1177**, and this unit's twenty replicates do not say how far apart they are. That is the honest
state of the one claim that landed on its null rather than outside it.

**And the run's own control came back exact, which licenses the design.** `naive`'s and `replay`'s twenty replicate
records are **bit-identical** to `e380`'s, field for field, and **56** other recorded fields agree, so adding a third
arm to an existing configuration moved nothing for the arms already in it. Every unit in this line that has wanted a
second arm has paid for a second run; this says a third arm can be added to a run at the cost of the arm.

## 3. What it cannot settle

- **One order**: the as-built one, so `ewc-block` has no second position for any task and its own position effect is
  read at three positions in one order rather than across orders as `e437` read the buffer's.
- **And three arms**: `ewc-block-rand`, the size-matched random partition that is the corpus's actual headline control,
  is absent, so this says the *penalty* is not a buffer here and not that the *basis* is what makes it one or not.
- **And one cell**: the card's world at twenty replicates, so the other five draws and the three streams are not in the
  reading, and BN3's **0.0573** against a **0.05** bar is exactly the margin a redraw could move.
- **And an arm is not a mechanism**: that the penalty pays the newest task and is paid by the oldest does not say which
  of the corpus's instruments the payment runs through, and `e432`'s split of interference into its weight and bias
  halves has not been asked of this world.
