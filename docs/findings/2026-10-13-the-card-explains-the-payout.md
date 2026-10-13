# The card explains the payout: the twentieth revision carries the earning and the two currencies

*2026-10-13. `experiments/e503_the_game_card_revision_twenty.py` writes revision 20: a **`payout` clause** added to
the card, carrying the earned-vs-meter ablation at the pass's two rungs and the payout read on the agent's own action,
every number read from `e500`'s, `e501`'s and `e502`'s artifacts and from their readings recomputed, with the card now
**revision 20** and every revision-19 field checked equal. **NA1, NA2 and NA3 all MET.** The clause the card gains is
the reading three revisions of this line left out: the pass has a payout an agent can play for.*

## 1. The revision

The clause's `two_trials` rung, read from `e500`'s artifact and its reading recomputed, the payout on the world's
**carried** state:

| the arm | the earned reward diagonal | the meter run's | the gain | sigma | the accuracy change | sigma | the map's distance from the identity |
|---|---|---|---|---|---|---|---|
| `naive` | **-4.5457** | -6.0542 | **+1.5086** | **+22.74** | -0.0017 | -0.25 | **5.8133** |
| `ewc-block` | **-4.5947** | -6.0070 | **+1.4123** | **+22.57** | +0.0014 | +0.17 | **5.2579** |
| `replay` | **-5.0295** | -6.1017 | **+1.0722** | **+15.54** | -0.0021 | -0.36 | **6.7272** |

the clause's `three_trials` rung, the same reader at the pass's second rung, read from `e501`'s artifact and its
reading recomputed:

| the arm | the earned reward diagonal | the meter run's | the gain | sigma | the accuracy change | sigma | the map's distance from the identity |
|---|---|---|---|---|---|---|---|
| `naive` | **-4.4878** | -5.9440 | **+1.4562** | **+22.92** | +0.0024 | +0.40 | **5.3064** |
| `ewc-block` | **-4.5730** | -5.9315 | **+1.3586** | **+36.39** | -0.0035 | -0.51 | **5.0752** |
| `replay` | **-4.9706** | -5.9837 | **+1.0131** | **+19.68** | -0.0038 | -0.75 | **6.6939** |

the clause's `action` rung, the payout read on the world's **one-step response to the action**, read from `e502`'s
artifact and its reading recomputed:

| the arm | the action run's reward diagonal | the meter run's | the gain | sigma | the accuracy change | sigma | the map's distance from the identity | the carried-state level (`e500`'s own) |
|---|---|---|---|---|---|---|---|---|
| `naive` | **-3.8024** | -7.8884 | **+4.0860** | **+21.68** | -0.0010 | -0.15 | **3.3914** | -4.5457 |
| `ewc-block` | **-3.8560** | -7.9915 | **+4.1356** | **+23.62** | +0.0031 | +0.55 | **3.5436** | -4.5947 |
| `replay` | **-4.8238** | -7.8619 | **+3.0381** | **+15.12** | -0.0101 | -1.61 | **4.1694** | -5.0295 |

| what the clause carries | the number |
|---|---|
| the readers the payout is read on | the world's **carried** state (two and three trials) and its **one-step response to the action** |
| the drive's width and the target's width in the action's currency | **`n_action` 8** and **`world_dims` 8**, the card's own configuration |
| the replicates, the bar and the chance | **20** replicates, the bar **0.10** above a four-class chance of **0.25**, at **2** sigma |

| claim | measured | verdict |
|---|---|---|
| NA1 the card carries the payout clause and the revision is 20 | the clause carries the rungs `two_trials`, `three_trials` and `action` under both readers, and the card is revision **20** | **MET** |
| NA2 the clause's numbers are the runs' own | **3** rungs, each arm's reward contrast with its sigma, its accuracy change with its sigma and the map's move, with **0** rungs disagreeing against `e500`'s, `e501`'s and `e502`'s artifacts and **0** against that line's readings recomputed | **MET** |
| NA3 the revision is backward-compatible with revision 19 | the revision-19 `label_first` clause's **12** fields all present and equal, the card's **32** other fields equal, and the `absent` list **`[]`** as it was | **MET** |

## 2. What it says

**And the revision is an addition with nothing taken away.** The `label_first` clause revision 19 carried keeps all
**12** of its fields -- the placement, the two windows, the two shares, the three arms' diagonals with their contrasts
and sigmas and the bar, and its own `three_trials` rung -- with the card now **revision 20**, the **32** fields outside
the clauses equal, and the `absent` list the empty list it has been since `e490`. **So the payout is written beside the
pass rather than on top of it**, and a reader can still check every earlier clause against the revision it was written
at.

**And the clause's numbers are the three units' own and not a sentence.** Every number in the clause is read twice:
from `e500`'s, `e501`'s and `e502`'s artifacts and from that line's readings recomputed at the card's own pass, read
and world. The two-trial gains **+1.5086**, **+1.4123** and **+1.0722** at **+22.74**, **+22.57** and **+15.54** sigma,
the three-trial gains **+1.4562**, **+1.3586** and **+1.0131** at **+22.92**, **+36.39** and **+19.68** sigma, and the
action's **+4.0860**, **+4.1356** and **+3.0381** at **+21.68**, **+23.62** and **+15.12** sigma all agree, with the
accuracy changes **-0.0021** to **+0.0014**, **-0.0038** to **+0.0024** and **-0.0101** to **+0.0031** and the map's
distance from the identity on every arm of every rung. **So a reader can check the clause against the three units
rather than against this clause's claim about them.**

**And the card now says what the pass is worth to an agent that acts.** Revision 17's `episode` clause says what the
pass is, revision 18's `label_first` clause says where its label has to be, revision 19 says the placement's clause
holds over the pass's own split, and this revision says the pass has a payout the world will pay. **So the working
episodic mode is written down with its earning as well as its shape**, and the card carries the ablation -- the map
trained by the payout against the map trained by the task loss -- in the same clause that names what the payout is read
on.

**And the two currencies are two readers of one world.** The carried reader pays **+1.5086**, **+1.4123** and
**+1.0722** more and the action reader **+4.0860**, **+4.1356** and **+3.0381** more, both against their own meter
runs, over the same pass, the same read, the same placement and the same target. **So the earning is a property of the
pair and of the reader, not of the pass's length**, which is what makes it a clause of the card rather than a reading
of one run.

## 3. What it cannot do

- **Two currencies and one world**: the carried and action readers are two ways of scoring the environment's own linear
  read of the cue, so a second world or a second payout shape is a different unit, and the clause's earnings are one
  configuration's.
- **And one budget and one seed stream**: every run behind the clause is the card's own setting at the run's own
  `--lr`, so how hard the map is paid is not swept and the **+1.01** to **+4.14** are not a curve over a learning rate.
- **And the action's currency turns on a coincidence of widths**: the world's one-step response has width `n_action`
  and the cue's target has width `world_dims`, and the clause's **8** and **8** are the card's own configuration rather
  than the currency's, so the same flag at another `--loop-world-dims` does not compare -- the coincidence `e502`'s own
  finding spells out.
- **And a clause is not a result**: NA3 shows revision 19 survives into revision 20 and not that revision 19 was right,
  and the clause's numbers are three units' readings rather than an independent draw.
- **And the pass's length is carried to three trials and no further**: the clause's rungs are the two- and three-trial
  splits, so the **four- and six-trial splits** and the passes with the label at an **interior trial** are not in it,
  and how far the earning's family extends is open.
