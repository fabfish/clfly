# The game card's sixteenth revision: the reward enters, and the absent list is down to one entry

*2026-10-09. `experiments/e486_the_game_card_revision_sixteen.py` writes the card's sixteenth revision: one clause
added, the **reward**, carrying `e485`'s readings recomputed from the two runs rather than quoted, and the `absent`
list losing exactly one entry. **All four claims MET**.*

## 1. The revision

| the field | revision 15 | revision 16 |
|---|---|---|
| the revision | 15 | **16** |
| `absent` | `a reward`, `an episode boundary` | **`an episode boundary`** |
| its fields, carried where not rewritten | -- | **28 of 28 equal** |

The new clause, read from `runs/e485_earned_label_reward_20reps.json`, `runs/e438_earned_label_three_arms_20reps.json`
and `e485`'s reading of them:

| the arm | the reward diagonal | the reward last row | the contrast | sigma | the accuracy diagonal | the accuracy last row |
|---|---|---|---|---|---|---|
| `naive` | -6.8857 | -6.5639 | **-0.3218** | **-4.91** | 0.7691 | 0.5191 |
| `ewc-block` | -6.8495 | -6.4992 | **-0.3503** | **-4.98** | 0.7073 | 0.4889 |
| `replay` | -6.8743 | -6.6866 | **-0.1877** | **-3.46** | 0.7389 | 0.6785 |

and its `orderings`: the accuracy's **`naive`, `replay`, `ewc-block`** against the reward's **`ewc-block`, `replay`,
`naive`**.

| claim | measured | verdict |
|---|---|---|
| TA1 the fifteenth revision is carried unchanged where it is not rewritten | **28** fields, all equal, the revision now **16**, and `absent` losing exactly `a reward` | **MET** |
| TA2 the clause's numbers come out of the runs | **3** arms' reward cells and accuracy diagonals at **20** replicates, **0** disagreeing past the tolerance, the counts and the first-task flag equal to the reading's | **MET** |
| TA3 the clause's bearing is that the two currencies disagree | the reward's diagonal is below its last row on every arm at **-4.91** to **-3.46** sigma while the accuracy's is above it by **0.2500**, **0.2184** and **0.0604** | **MET** |
| TA4 the clause carries the reversal rather than hiding it | both orderings are in the clause and they disagree | **MET** |

## 2. What the revision says

**The card's own account of its game and the corpus agree about what is absent, for the third time.** `e470` took `a
held-out task` off the list when the corpus first had one, `e482` took **`a policy`** off it when the runner first
carried one, and this unit takes **`a reward`** off it. **The list is down to one entry -- `an episode boundary`** --
and **28 of 28** fields of revision 15 survive untouched, so this revision is an addition and a subtraction and not a
rewrite, which is the check both `e470` and `e482` made one revision each.

**And the clause's numbers are the runs'.** All three arms' reward diagonals, last rows, contrasts and sigmas, their
accuracy diagonals and the card roll's accuracy last rows are recomputed from the artifacts and then checked against
`e485`'s own reading of them, to a thousandth of a point, with the counts and the first-task flag agreeing. **So the
card carries no number this unit did not re-derive.**

**And the clause's bearing is a disagreement, which is what makes it worth carrying.** The reward's diagonal is
**below** its last row on every arm at **-4.91** to **-3.46** sigma while the accuracy's is **above** its own by
**0.2500**, **0.2184** and **0.0604**; and the two currencies order the three arms **exactly in reverse**. **A clause
that carried only a level would say the card has a reward; this one says the reward and the accuracy disagree about
which arm is best and about whether the sequence forgets**, which is the measurement `e485` made and the reason the
card can now afford to stop calling the reward absent.

**And the clause carries the reversal rather than hiding it.** Both orderings are in it, and its own `agree` flag is
**false**. **So a reader of the card sees the disagreement**, where a clause carrying one ordering alone would have
made the card's account of its arms a claim the reward's own currency contradicts.

## 3. What it cannot do

- **One revision of one world**: the clause is read from one run at one budget and one seed stream.
- **And a clause is not a result**: TA1 shows revision 15 survives into revision 16 and not that revision 15 was
  right, and TA2 shows the clause agrees with the runs and not that the runs should be believed.
- **And the clause carries a disagreement it cannot explain**: the reward's currency is the body's and the accuracy's
  is the head's, which is the finding beside this unit and not something the card's shape holds.
- **And the reward is the corpus's noisiest currency**: `e484` found the cue's share of the payout under the payout's
  own scatter, so the clause's **-3.46** to **-4.98** sigma are large numbers about differences of **0.19** to
  **0.35** in a currency whose cells run about **-6.9**.
- **And the card still cannot say what an episode is**: the `absent` list's one remaining entry is **an episode
  boundary**, and nothing in the corpus has one.

## RE-READ 2026-10-11

**The corpus has an episode now, and this unit's clause is what is owed.** Revision 16 removed a reward from the `absent` list and left **an episode boundary** in it, and its own *cannot settle* closed on *nothing in the corpus has an episode boundary*. `e489` gave `CueActionEnv` the episode -- `episode_len` trials to a pass, one cue each and the world's state the episode's rather than the last trial's -- and the runner `--loop-episode` and `--loop-boundary`, and measured it: the earlier trials move the world's state at the read step by **0.7601** at **12.62** sigma over **64** episodes against a state scale of **0.7727**, while at one trial the same manipulation moves it by **exactly zero**, and a boundary channel of eight neurons carries `+1` at the episode's opening, `-1` at every continuing trial and zero elsewhere. **And at three trials the benchmark's own read-out puts every arm at chance** (**0.2476**, **0.2451**, **0.2413** against **0.25**), which is what the read step being the pass's last one costs. So the list's one entry is owed by a card revision and not by the environment, and this row's numbers stand.
