# The game card at revision 4: the absence list rewritten, and the third arm carried

*2026-10-05. `experiments/e418_the_game_card_revision_four.py` writes the closed-loop benchmark's card at
**revision 4**. Two clauses change and both are checked against the artifact that closed the gap: the absence list
loses the two items the card's own clauses already cover, and the arms clause gains the penalty `e415` measured on the
card's own world. Every other clause is carried unchanged. No training and no roll. Five claims, registered before
this unit read any of them.*

## 1. What changed

| clause | revision 3 | revision 4 |
|---|---|---|
| `arms` | `naive`, `replay` | `naive`, `replay`, **`ewc-block`** |
| `absent` | a reward, a policy, an episode boundary, a held-out task, **a second world**, **a second draw** | a reward, a policy, an episode boundary, a held-out task |
| `penalty` | -- | **+0.1764** of accuracy at **11.50 sigma** and **0.2521** of forgetting cut at **11.65 sigma**, the penalty over the naive arm at **-0.0274** and **-1.95 sigma**, on the uncoupled rule that predates `e359` |

The other twelve fields -- the substrate, loop, protocol, metrics, the revision-3 buffer clause and draw terms, and the
world, stream, recovery and invariance clauses -- are carried equal.

| claim | measured | verdict |
|---|---|---|
| AP1 the third revision is carried unchanged where it is not rewritten | **12** fields equal, revision now **4** | **MET** |
| AP2 and the absence list loses exactly the two items a clause covers | 6 items to 4, losing *a second world* and *a second draw* | **MET** |
| AP3 and the arms clause gains the penalty | the third name is the arm `e415`'s cell carries | **MET** |
| AP4 and the penalty clause is the artifact's | every number equal to `e415`'s | **MET** |
| AP5 and the clause carries the rule it was measured on | the coupling is in the card's world's run and not in the measured cell | **MET** |

## 2. What the fourth revision says

**Two absences were struck because the card's own clauses had already closed them.** Revision 1 wrote *a second world*
and *a second draw* into the absence list, and revisions 2 and 3 carried the list unchanged while measuring **six**
worlds and **three** clean streams in the clauses beside it. A reader holding revision 3 was told the benchmark had
one world and one draw at the same time as the card's world clause quoted a spread over six of them. Revision 4
strikes exactly those two, and each strike is checked against `e409`'s artifact: the world clause reads six worlds,
the stream clause three streams. The four items that stand -- no reward, no policy, no episode boundary, no held-out
task -- are the benchmark's own statement of what it is not.

**And the benchmark now names the arms it runs.** `e415` read a run of the card's own world at the same cell, with
`naive`, `replay` and `ewc-block` in one run at twenty replicates, and found the buffer ahead on both axes at eleven
sigma while the penalty is not resolved against the naive arm. The card's `arms` clause had read `naive` and `replay`
since revision 1, so a reader had no way to know the penalty was run at all. Revision 4 carries the third arm and its
ordering, and it carries the rule the ordering was measured on: `e415`'s cell predates `e359`'s coupling, so the
clause says so rather than letting a reader assume the card's current world.

**And the card is now internally consistent.** Every clause is a number read from an artifact, the list of absences
names only what no clause covers, and the arms named are the arms the corpus runs on this world.

## 3. What it cannot settle

- **A card is a definition and not a result**: it states what the benchmark is and points at the artifacts for every
  number.
- **And the struck items are struck by the card's own clauses**: this revision does not re-derive the six worlds or
  the three streams, it reads the clauses that measured them, so a defect in those clauses would survive here.
- **And the penalty clause is one world's and one strength's**: the card's world at `lam = 1.0` with `ewc-block`, on
  the uncoupled rule. `e416`'s ledger is corpus-wide and not a clause.
- **And the four remaining absences stand**: no reward, no policy, no episode boundary and no held-out task has been
  added.
- *And a clause is not an experiment.*
