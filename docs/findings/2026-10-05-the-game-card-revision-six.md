# The game card at revision 6: the order clause and the controls clause

*2026-10-05. `experiments/e428_the_game_card_revision_six.py` writes the closed-loop benchmark's card at **revision
6**. Two clauses are added -- the **order** the benchmark's tasks are taught in, and the corpus's own **controls** --
each read from the artifacts that measured them, and every other field is checked equal to `e424`'s revision 5 rather
than restated. No training and no roll. Five claims, registered before this unit read any of them.*

## 1. What revision 6 adds

| clause | carried | read from |
|---|---|---|
| **order** | **3** configurations rolled under both orders; the same task taught first against taught last at least **+0.0583** in all six contrasts; the reversal costing the buffer **-0.0694**, **-0.0618** and **-0.0028**; over **16** arm-rolls the first position ahead in **16** and positive in **15**; the buffer's mean positive in **6 of 6** against the penalties' **10 of 10** negative; the buffer's worst position last in **6 of 6** and the penalties' worst the middle in **9 of 10** | **`e425`, `e426`** |
| **controls** | **3** frozen-**body** cells with a largest gain of **0.0017** and forgetting cuts of **exactly zero**; a frozen **bias** leaving the buffer **0.27** of its gain and **0.27** of its cut, with the `naive` arm's own forgetting falling **0.0523** | **`e417`, `e427`** |

The other eighteen fields -- the substrate, loop, protocol, metrics, arms, absence list, the world, stream, recovery
and invariance clauses, the buffer clause and draw terms, the penalty clause, and the trade, terms and arm-terms
clauses -- are carried equal.

| claim | measured | verdict |
|---|---|---|
| BD1 the fifth revision is carried unchanged where it is not rewritten | **18** fields equal, revision now **6** | **MET** |
| BD2 and the order clause is `e425`'s and `e426`'s | 3 configurations, 16 arm-rolls, contrast **+0.0583**, costs **-0.0028** to **-0.0694** | **MET** |
| BD3 and the clause carries where each arm's damage falls | buffer worst last **6 of 6**, penalties worst middle **9 of 10** | **MET** |
| BD4 and the controls clause's first half is `e417`'s | **3** cells, worst gain **0.0017**, cuts **0.0000** | **MET** |
| BD5 and its second half is `e427`'s | gain and cut at **0.27** of the plastic pair's, drop **0.0523** | **MET** |

## 2. What the sixth revision says

**The card now says that the benchmark's own order is a variable, not a convention.** Revisions 2 to 5 published what
each arm is worth and what the buffer does task by task; revision 6 states that both follow the **position** in the
sequence: on the same configuration the same pathway is worth **+0.2333** taught first and **-0.0104** taught last, and
reversing the order costs the buffer **-0.0028**, **-0.0618** and **-0.0694** of its mean gain. A reader comparing two
suites is comparing orders as much as tasks, and the card says so with the artifacts behind it.

**And it says where in the sequence an arm pays.** The buffer's worst position is the task taught last in six of six
rolls; a penalty's is the **middle** in nine of ten -- the task it was halfway through when the last one arrived. So
the card's penalty clause and its trade clause now have a position attached to them.

**And it says how much of an arm's worth the corpus's own controls can remove.** On a frozen recurrent body the buffer
is worth **nothing** (a largest gain of **0.0017** and cuts of exactly zero); with only the head's bias frozen it keeps
**0.27** of its gain and cut, and the arm that does nothing has its own forgetting fall by **0.0523**. A headline
number can now be read against what survives the freeze.

## 3. What it cannot settle

- **A card is a definition and not a result**: it states what the benchmark is and points at the artifacts for every
  number.
- **And the clauses are one protocol's**: three tasks with the middle left in place, so a full permutation is not
  measured, and the order clause is measured on the overlap and assembly suites rather than the earned-label world.
- **And the controls are the corpus's two flags**: a frozen body and a frozen bias, not a frozen head, a frozen input
  or a frozen read-out.
- **And the clauses are only checked against each other**: BD1 shows revision 5 survives into revision 6 and not that
  revision 5 was right.
- *And a clause is not an experiment.*
