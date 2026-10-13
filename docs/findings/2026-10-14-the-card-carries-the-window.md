# The card carries the window: the twenty-first revision names the drive steps its placement stands for

*2026-10-14. `experiments/e508_the_card_carries_the_window.py` writes revision 21: the `label_first` clause gains a
**`windows`** field, the eight placements the corpus holds with their pass lengths, trial indices, windows, each
arm's accuracy diagonal and the label's own share of the read, beside the two comparisons that decide the variable.
Every number is read from `e495`'s, `e497`'s, `e505`'s and `e506`'s artifacts and from their readings recomputed,
the card is **revision 21**, and every revision-20 field is checked equal. **NA1, NA2, NA3 and NA4 all MET.** The
clause `e496` wrote around the label's **placement** now carries what that placement is a name for.*

## 1. The window table

The field's eight placements, each read from the first of the four units that carries it, the others being
cross-checks:

| the placement | the pass | the label's trial | the window in drive steps | `naive` | `ewc-block` | `replay` | the label's share |
|---|---|---|---|---|---|---|---|
| two trials, the label first | 2 | 0 | **11** | 0.8299 | 0.8139 | 0.8267 | **1.0551** |
| two trials, the label last | 2 | 1 | 5 | 0.3104 | 0.2944 | 0.3031 | **0.0386** |
| three trials, the label first | 3 | 0 | **11** | 0.8538 | 0.8392 | 0.8580 | **1.0571** |
| three trials, the label at trial 1 | 3 | 1 | 7 | 0.3257 | 0.3069 | 0.3274 | **0.0489** |
| three trials, the label at trial 2 | 3 | 2 | 3 | 0.2566 | 0.2576 | 0.2542 | **0.0314** |
| four trials, the label first | 4 | 0 | **11** | 0.8316 | 0.8285 | 0.8281 | **1.0151** |
| four trials, the label at trial 1 | 4 | 1 | 8 | 0.3667 | 0.3580 | 0.3653 | **0.0878** |
| four trials, the label at trial 2 | 4 | 2 | 5 | 0.3031 | 0.2986 | 0.2903 | **0.0362** |

| what the field carries | the number |
|---|---|
| the flag and the formula | `--loop-episode N` with `--loop-label-at i`, the window being `11 - i * 12/N` |
| the arms, the chance and the bar | the three arms, a four-class chance of **0.25** and the bar **0.10** |
| the replicates, and the pass's own length | **20** replicates each, a pass of **12** steps |
| the four units the numbers come from | `e495`, `e497`, `e505` and `e506`, their artifacts and their readings recomputed, **15** source readings over the eight placements |

The two comparisons the field records beside the table, both against the registered spread, which is window **11**'s
own family spread across its three pass lengths:

| the comparison | the placements | the numbers | inside the registered spread |
|---|---|---|---|
| the **window**, held at **5** over two pass lengths | two trials at trial 1 against four trials at trial 2 | the spread **0.0073**, **0.0042** and **0.0128** | **yes**, 0.0128 under **0.0312** |
| the **window**, held at **11** over three pass lengths | two, three and four trials at trial 0 | the spread **0.0240**, **0.0253** and **0.0312** | **yes**, this family **is** the bound |
| the **position**, held at the pass's second trial over two pass lengths | four trials at trial 1 (window **8**) against three trials at trial 1 (window **7**) | the difference **+0.0410**, **+0.0511** and **+0.0379** | **no**, 0.0379 above **0.0312** |

| claim | measured | verdict |
|---|---|---|
| NA1 the card carries the window and the revision is 21 | the clause carries `windows` naming **8** of the **8** placements with their pass lengths, trial indices, windows, arms and shares, and the card is revision **21** | **MET** |
| NA2 the window table is the runs' own | **8** placements over **15** source readings, each arm's accuracy and the label's share, with **0** disagreeing against `e495`'s, `e497`'s, `e505`'s and `e506`'s artifacts and **0** against those four readings recomputed | **MET** |
| NA3 the revision is backward-compatible with revision 20 | the revision-20 `label_first` clause's **12** fields all present and equal, the card's **32** other fields equal, and the `absent` list **`[]`** as it was | **MET** |
| NA4 the clause says which variable orders the pass | the comparisons are carried: the same-window families **0.0128** (window 5) and **0.0312** (window 11's own, the bound), and the same-position pair **+0.0379** to **+0.0511** against the bound, agreeing with the comparisons recomputed from the four units | **MET** |

## 2. What it says

**And the revision is an addition with nothing taken away.** The `label_first` clause revision 20 carried keeps all
**12** of its fields -- the placement, the two windows, the two shares, the three arms' diagonals with their
contrasts and sigmas and the bar, and its own `three_trials` rung -- with the card now **revision 21**, the **32**
fields outside the clauses equal, and the `absent` list the empty list it has been since `e490`. **So the window is
written beside the placement rather than on top of it**, and the two fields now say the same thing at two levels:
`window` names the two ends the clause was measured at, and `windows` names the quantity they are ends of.

**And the clause's clause is now the drive steps and not the trial index.** The field's `formula` is `11 - i * 12/N`
for the label at trial `i` of an `N`-trial pass, and the eight placements it names carry the windows **11**, **8**,
**7**, **5** and **3**. **So a reader no longer has to take the placement on faith**: the number the clause names
the label by is the distance between its cue and the read, and the two comparisons beside the table say which of the
two readings of that number the eight points support.

**And the two comparisons decide it the same way `e506` found.** The placements that share a **window** read alike
across the pass lengths that carry them -- window **5** on two trials at trial 1 and on four trials at trial 2,
differing by at most **0.0128**, and window **11** on two, three and four trials by **0.0312**, which is the bound
itself -- while the placements that share a **position** do not: the pass's second trial reads **0.3667**, **0.3580**
and **0.3653** at four trials against **0.3257**, **0.3069** and **0.3274** at three, a rise of **+0.0379** to
**+0.0511**, the smallest of the three above the **0.0312** bound. **So the clause carries the variable and not only
its name**, and the spread the window families are read inside is the runs' own -- window 11's family, the one
carried by the most pass lengths.

**And the table's numbers are the four units' own and not a sentence.** Every accuracy and every share is read
twice: from the four artifacts and from the four readings recomputed at their own runs, and the placements the
corpus holds more than once are read from every unit that holds them -- `two_at0` from `e495`, `e497` and `e506`
together, `two_at1` from `e495` and `e506`, `three_at0` from `e497`, `e505` and `e506`, and `three_at1` and
`three_at2` from `e505` and `e506`, **15** source readings in all over the eight placements -- with **0**
disagreeing. **So a reader can check the table against the four units rather than against this clause's claim
about them.** *And the one last digit worth naming*: a family's spread is taken from the unrounded means so it is
the runs' own, and the pair's difference is read off the two endpoints as the table records them, which is the
**+0.0379** to **+0.0511** above; from the unrounded means the same pair reads **+0.0378** to **+0.0510**, and the
clause carries both.

## 3. What it cannot do

- **A clause is not a result**: NA3 shows revision 20 survives into revision 21 and not that revision 20 was right,
  and the table's numbers are four units' readings rather than an independent draw.
- **And the table is eight placements over three pass lengths**: two, three and four trials, with window **11**
  carried by three of them and window **5** by two, so window **8**, window **7** and window **3** are each a single
  pass length -- a placement and not a test -- and the six-trial split and the placements beyond each pass's own
  trials are not in it.
- **And the pass's length and the trial's length move together**: the pass is twelve steps, so the label at trial
  `i` of `N` trials leaves `11 - i * 12/N` drive steps and one more trial is one more **cue** and a shorter **trial**
  at once. The window is that formula and nothing here separates a step's worth of window from a trial's; what would
  is a twelve-step pass with a fixed trial length, and that is not measured here.
- **And the payout is not on the placement runs**: the eight runs behind the table carry no `--loop-reward`, so
  nothing in the window the clause names is read against the world's currency. `e507` put the payout on one
  placement -- the three-trial label-at-1, window **7** -- and what the other seven windows are worth to an agent
  that acts is a different unit.
- **And one world, budget and seed stream**: every run behind the table is the card's own setting with `--seed0 0`
  and the run's own budget, so a second world and a second stream are not in it, and the table is a record of one
  configuration rather than a curve over any of its settings.
