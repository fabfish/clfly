# The game card at revision 3: the arm's term written into the card beside the draw's

*2026-10-05. `experiments/e414_the_game_card_revision_three.py` writes the closed-loop benchmark's card at **revision
3** and reads every number in it from the artifact that measured it. No training and no roll: the card is a
dictionary, and each clause of it is checked against a reader that already exists. Five claims, registered before this
unit read any of them.*

## 1. The card, and what revision 2 did not carry

| clause | carried | read from |
|---|---|---|
| substrate | `mb+cx+al@n952`, circuit size 300, read-out `59926518137c`, basis `cell_class`, support 80, seed 0, 4 classes per task | `e392` |
| loop | cue at step 0, action drive, 8 world dimensions, coupled, leak 0.35, linear, read-out from the world | `e392` |
| protocol | `loop_odour_identity`, `loop_heading`, `loop_odour_input`, 96 train, 48 test, lr 3e-3 | `e392` |
| arms | `naive`, `replay` | `e392` |
| world | span **0.0750** at twenty updates, **0.3104** at five hundred, six worlds | `e407` |
| stream | span **0.0323** at the far point, against the worlds' **0.3344** | `e403`, `e396` |
| recovery | one of five worlds recovers, by a bar of 0.05 | `e396` |
| invariance | the connectome's own reading **0.6875**, spread **0.0000** | `e396`, `e407` |
| **arm** | gains **-0.0174** to **+0.0365** at budgets 1 and 20, **+0.1330** to **+0.1594** at 500, rises **+0.1142** to **+0.1639**, over six worlds | **`e413`** |
| **draw terms** | the draw's span on the benchmark's metric **0.0309** beside the arm's least five-hundred gain **0.1330** | **`e410`, `e411`** |

The first eight lines are revision 2's, carried unchanged; the last two are what this revision adds.

| claim | measured | verdict |
|---|---|---|
| AN1 the second revision's clauses are unchanged | all **ten** fields equal, with the revision now **3** | **MET** |
| AN2 and the arm clause is measured at three budgets | the three bands read off `e413`'s artifact | **MET** |
| AN3 and the arm clause's comparison is the artifact's | **2.79** times the twenty-update span, above twice | **MET** |
| AN4 and the draw's term is carried beside the arm's | **0.0309** against **+0.1330**, **4.30** times | **MET** |
| AN5 and the cut term is carried, above 0.20 | **+0.0635** at twenty, **+0.2339** at five hundred | **MET** |

## 2. What the third revision says

**The card now carries both of the benchmark's terms, and they are not the same size.** Revision 2 published the
*draw's* side: which world, which stream, how far a world's own reading spreads. This revision publishes the *arm's*
side: what storing sixteen transitions per task and replaying them is worth, at three update budgets, measured on the
same six worlds and the same runs. At five hundred updates that is **+0.1330 to +0.1594** of mean final accuracy
against the six draws' own span of **0.0309** -- **4.30** times it -- and **+0.2339 to +0.3146** of forgotten
accuracy cut.

**And it is measured where the aid exists.** At budgets 1 and 20 the six worlds' gains are all inside
**-0.0174 to +0.0365**, so a user reading the card at a small budget sees an arm worth nothing; at 500 every world
gains at least **+0.1330**, so the same clause at the top of the ladder is worth a sixth. The rise from twenty to five
hundred is at least **+0.1142** on every world, **2.79** times the six worlds' spread at twenty -- the arm's term
beats the draw's at the small budget as well as at the far one.

**And the clause the card still cannot state is the mechanism.** The line has screened the draw's geometry (`e397`,
`e398`, `e400`), its biology (`e404`), the trained bodies' movement (`e402`) and the six worlds' own score (`e410`),
and none of them separates the one world that recovers. Revision 3 adds a term, not a reason.

## 3. What it cannot settle

- **A card is a definition and not a result**: it states what the benchmark is and points at the artifacts for every
  number, so it is only as good as the readers it cites.
- **And the numbers are six worlds' and one arm pair's**: the four engine redraws are not in the series and the
  penalty arms are absent at every budget, so `e276`'s replay-over-penalty contrast is not a clause here.
- **And the clauses are only checked against each other**: AN1 checks that revision 2 survives into revision 3, not
  that revision 2 was right.
- *And a clause is not an experiment.*
