# The game card at revision 14: the held-out task, and the clause that reads it

*2026-10-08. `experiments/e470_the_game_card_revision_fourteen.py` adds one clause to the card, the **holdout**, and
removes one entry from its `absent` list. The clause carries `e469`'s readings recomputed from the two rolls rather than
quoted, and every other field is checked equal to `e461`'s card. Four claims, all four **MET**.*

## 1. The clause

| the held-out cue set | |
|---|---|
| its name | `loop_holdout` |
| in the sequence | no |
| the probe | a ridge read-out on the read-out neurons, the body frozen, fitted on the cue set's own train split |
| the ridge | 1e-2 |
| train / eval | 96 / 48 |

| the roll and arm | the initial body | the trained body | the change | sigma | against the baseline | sigma |
|---|---|---|---|---|---|---|
| `bio`, `naive` | 0.6875 | **0.7719** | **+0.0844** | **10.11** | -- | -- |
| `bio`, `ewc-block` | 0.6875 | **0.7625** | **+0.0750** | **9.00** | -0.0094 | -0.86 |
| `bio`, `replay` | 0.6875 | **0.7677** | **+0.0802** | **6.84** | -0.0042 | -0.29 |
| `rand`, `naive` | 0.6875 | **0.7719** | **+0.0844** | **10.11** | -- | -- |
| `rand`, `ewc-block-rand` | 0.6875 | **0.7667** | **+0.0792** | **8.54** | -0.0052 | -0.40 |
| `rand`, `replay` | 0.6875 | **0.7677** | **+0.0802** | **6.84** | -0.0042 | -0.29 |

| the absent list | revision 13 | revision 14 |
|---|---|---|
| | `a reward`, `a policy`, `an episode boundary`, **`a held-out task`** | `a reward`, `a policy`, `an episode boundary` |

| claim | measured | verdict |
|---|---|---|
| WA1 the thirteenth revision is carried and the absent list loses one entry | **26** fields equal, the revision now **14**, the absent list losing exactly the held-out task | **MET** |
| WA2 and the clause's numbers come out of the two rolls | **10** recomputed contrasts, **0** disagreeing past the tolerance, counts equal to `e469`'s | **MET** |
| WA3 and the clause's bearing is what the sequence adds | **+0.0844** at **10.11** sigma on both rolls, with the initial readings beside it | **MET** |
| WA4 and the two anchors are nulls in the clause | **-0.86** and **-0.40** sigma, with the buffer at **-0.29** | **MET** |

## 2. What revision 14 says

**The card's `absent` list stops naming a held-out task, because the corpus now has one.** The list has carried *a
reward, a policy, an episode boundary and a held-out task* since the card's first revision, and `e469` drove the fourth
of those: a cue set drawn in the same world, outside the sequence, read by a probe on the frozen body. Revision 14
removes that one entry and adds the clause that carries the reading, so the card's own account of its game and the
corpus now agree about what is absent.

**And the clause's content is the pair of readings and not the trained one alone.** The **holdout** clause carries each
arm's initial reading beside its trained one, because the initial body already reads the unseen cue set at **0.6875**
against a chance of **0.25** -- so a clause that carried only **0.7719** would invite a reader to credit the sequence
with all of it. What the clause says is that the sequence adds **0.0844** at **10.11** sigma, on both rolls, with the
level it started from written down next to it.

**And the two anchors are nulls in it, which is the fourth time this card has recorded that the basis does not move the
diagonal.** `ewc-block`'s trained reading is **0.0094** below the baseline's at **0.86** sigma and `ewc-block-rand`'s
**0.0052** below at **0.40**, with the buffer **0.0042** below at **0.29** -- so the clause about a task outside the
sequence says what the `basis` and `pair` clauses say about the tasks inside it.

**And the revision before this one survives it unchanged where it is not rewritten.** All **26** fields of revision 13
are carried, the revision is **14**, and the only other change is the single absent entry -- so the chain's
twenty-seven clauses are now twenty-eight, and the two corrections revisions 11 and 12 had to make are still in it.

**And what the card cannot do with its own clause is say how a probe should be built.** The ridge is **1e-2** because
that is what `e469` ran, and it is recorded and not prescribed: a clause that fixed the probe would be defining the
benchmark's held-out reading, and this one reports one.

## 3. What it cannot settle

- **One world of one revision**: the card's own world with the flag's own draw, so the clause is a reading of **one**
  held-out draw in it and not of the family of held-out draws.
- **And two rolls**: the nulls against the baseline are **0.86** and **0.40** sigma, which a redraw could put above the
  bar.
- **And a clause is not a result**: WA1 shows revision 13 survives into revision 14 and not that revision 13 was right,
  and WA2 shows the clause agrees with the two rolls and not that the two rolls should be believed.
- **And the absent list is not a programme**: the three entries left in it -- a reward, a policy, an episode boundary --
  are still absent, and a clause about them is a different unit's job.

## RE-READ 2026-10-09: the clause carries one draw's change

The clause's bearing is the sequence's contribution -- the baseline's trained minus initial reading, **+0.0844** at
**10.11** sigma -- and `e474` has since drawn the held-out cue set four times: the same quantity runs **+0.0719**,
**+0.0688**, **+0.1031** and **+0.0073**, a spread of **0.0958** with four of the six pairs of draws resolving. **So the
number this clause carries is one draw's**, and the card's sentence that *what the sequence adds is the last two thirds
of the decodability* is one draw's sentence: on the fourth cue set the sequence's contribution is **+0.0073** at
**0.53** sigma, which is nothing this corpus can see. The clause's **form** is untouched and was the right one -- it
carries the initial reading beside the trained one, which is what makes a reader able to see that the level is a draw's
-- and what it now needs is a reader who knows the change is a draw's too
(`docs/findings/2026-10-09-the-held-out-level-across-four-draws.md`).

## RE-READ 2026-10-09: the clause carries one world's change as well

The scope above is the **draw** of the held-out cue set. `e475` moved the other quantity the clause is silent about --
the **environment** -- and redrew the world under the same four draws with `--loop-seed 1` against the default **0**.
The change moves with the world too: at the held-out seed **11** the two worlds' changes are **+0.1031** and
**+0.0333**, a difference of **+0.0698** at **5.15** sigma, while at the other three seeds they agree (**0.64**,
**-1.60** and **0.47** sigma). **So the number this clause carries -- the sequence's contribution on a task outside
it -- is one draw's change in one world's environment**, and a clause revision that reports it needs both beside it.
The clause's **form** still stands, and this does not touch the card: it is a second scope on the same quantity
(`docs/findings/2026-10-09-the-held-out-reading-in-a-second-world.md`).
