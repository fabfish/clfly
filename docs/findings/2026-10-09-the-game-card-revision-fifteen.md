# The game card's fifteenth revision: the policy enters, and the absent list loses one entry

*2026-10-09. `experiments/e482_the_game_card_revision_fifteen.py` writes the card's fifteenth revision: one clause
added, the **policy**, carrying `e481`'s readings recomputed from the two runs rather than quoted, and the `absent`
list losing exactly one entry. **All four claims MET**.*

## 1. The revision

| the field | revision 14 | revision 15 |
|---|---|---|
| the revision | 14 | **15** |
| `absent` | `a reward`, `a policy`, `an episode boundary` | **`a reward`, `an episode boundary`** |
| its fields, carried where not rewritten | -- | **27 of 27 equal** |

The new clause, read from `runs/e481_earned_label_policy_20reps.json`, `runs/e438_earned_label_three_arms_20reps.json`
and `e481`'s reading of them:

| the arm | the diagonal | against | contrast | sigma | the last row | against | contrast | sigma |
|---|---|---|---|---|---|---|---|---|
| `naive` | 0.8187 | 0.8042 | +0.0146 | 0.63 | 0.5045 | 0.5191 | -0.0146 | -0.86 |
| `ewc-block` | 0.7573 | 0.6865 | **+0.0708** | **+2.40** | 0.5340 | 0.4889 | +0.0451 | 1.71 |
| `replay` | 0.7313 | 0.7438 | -0.0125 | -0.80 | 0.6608 | 0.6785 | -0.0177 | -1.26 |

| claim | measured | verdict |
|---|---|---|
| VA1 the fourteenth revision is carried unchanged where it is not rewritten | **27** fields, all equal, the revision now **15**, and `absent` losing exactly `a policy` | **MET** |
| VA2 the clause's numbers come out of the runs | **6** contrasts over **20** replicates, **0** disagreeing past the tolerance, the movement counts **60 of 60** on both sides | **MET** |
| VA3 the freedom is used and the game is still learned | the movement runs **6.7094** to **9.2597** (mean **7.7980**) over **60** replicates, **0** at or below zero, and the `naive` diagonal is **+0.5687** above chance | **MET** |
| VA4 the clause carries what resolved rather than only what did not | the clause resolves **`ewc-block/diagonal`**, the reading the same | **MET** |

## 2. What the revision says

**The card's own account of its game and the corpus agree about what is absent, for the second time.** `e470` took `a
held-out task` off the list when the corpus first had one; this unit takes **`a policy`** off it, and the list goes
from three entries to two -- **`a reward`** and **`an episode boundary`**, which are the halves of `e325`'s sentence
this line has not built. **And revision 14 survives into revision 15 untouched**: **27 of 27** fields equal, so the
revision is an addition and a subtraction and not a rewrite, which is the check `e470`'s WA1 made one revision ago
and the reason a revision's diff is readable at all.

**And the clause's numbers are the runs'.** Every one of the six contrasts over the two runs and all three arms is
recomputed from the artifacts and then checked against `e481`'s own reading of them, to a thousandth of a point, and
the movement counts agree on both sides (**60 of 60**). **So the card carries no number that this unit did not
re-derive**, which is what makes a clause a reading rather than a quotation -- and `e481`'s reader is the instrument,
run again rather than trusted.

**And the clause's bearing is that the agent's freedom is used and the game is still learned.** The policy ends
**6.7094** to **9.2597** away from the identity it started at on **every** replicate (the mean is **7.7980**), and the
`naive` arm's diagonal is **0.8187** -- **+0.5687** above chance. **So the entry the list loses is not a capability
the corpus merely offers**: it is one that the benchmark's own run uses everywhere it can.

**And the clause carries the contrast that fired beside the five that did not.** One of the six resolves --
`ewc-block`'s diagonal at **+2.40** sigma -- and the clause records `resolved: ['ewc-block/diagonal']` rather than
the five nulls alone. **So a reader of the card sees the firing as well as the stability**, and `e481`'s finding
beside it carries the caveat a clause cannot hold: one test of six at 2.40 sigma has a family-wise chance of about
**9%** under the null, so it is a hint and not a result.

## 3. What it cannot do

- **One revision of one world**: the clause is read from one run at one budget and one seed stream, so it is one
  configuration's, and another world or another budget is a different clause.
- **And a clause is not a result**: VA1 shows revision 14 survives into revision 15 and not that revision 14 was
  right, and VA2 shows the clause agrees with the runs and not that the runs should be believed.
- **And the card still cannot say what a policy is for**: the reward half of `e325`'s sentence is untouched, so the
  `absent` list still names **a reward** and **an episode boundary**.
- **And the firing is carried and not explained**: the clause says which contrast resolved and nothing in the card
  can hold the multiplicity caveat, which lives in the finding beside it.
- **And the policy is the runner's, not the game's**: the clause says the benchmark can carry one and not that its
  runs do by default, so a reader who wants the numbers this card was read from has to know the flag.
