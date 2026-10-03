# The game card: the closed-loop benchmark written down, with its two absences measured

*2026-10-04. `experiments/e392_the_game_card.py` writes the closed-loop game down as a card -- substrate, loop,
protocol, arms, metrics and what it does not have -- and checks every clause against the corpus. No training is run;
the reader is `runs/e392_the_game_card.json`. Five claims, registered before this unit read the corpus for them.*

## 1. The card

**The closed-loop earned-label game, revision 1, read 2026-10-04.**

| clause | what it says |
|---|---|
| **substrate** | circuit `mb+cx+al@n952`, 300 neurons, read-out draw `59926518137c`, basis `cell_class`, support 80, `seed0 = 0`, 4 classes per task |
| **loop** | the cue pulse at step **0**; the world's drive reads the **action** population; the world is **8**-dimensional, **coupled** with leak **0.35**, **linear**; the head reads the **world** |
| **protocol** | `loop_odour_identity`, `loop_heading`, `loop_odour_input`, in that order; 96 train / 48 test; `lr = 3e-3`; the iteration budget is the schedule |
| **arms** | `naive`, `replay` |
| **metrics** | accuracy; the retention matrix's diagonal; its last row; their difference; backward transfer |
| **absent** | a reward; a policy; an episode boundary; a held-out task; a second world; a second draw |

## 2. What the checks found

| claim | measured | verdict |
|---|---|---|
| M1 the substrate clause is carried and constant | over **64** closed-loop artifacts each of the six fields takes **one** value, and each is the card's | **MET** |
| M2 the loop clause is carried by a cell | **36 of 64** artifacts realise it | **MET** |
| M3 the protocol clause is carried by that cell | **1** task order, **1** split, **1** class count over the cell's 36 | **MET** |
| M4 every named metric is computable in every artifact of the cell | all 36 ran `naive,replay` and carry a matrix for each | **MET** |
| M5 the absent list is measured | the cell's three world draws each take **1** value; across **768** artifacts carrying **86** distinct configuration keys, **0** name a reward, a policy, an episode, a goal or a return | **MET** |

**The card is unanimous where it claims constancy.** Eight fields that `e387` found fixed across the window are
still fixed four units later, now over sixty-four artifacts rather than forty, and each carries the card's own value
rather than merely agreeing with its neighbours. The cell -- the card's loop clause -- is **36** artifacts, from
`e359` to `e391`, spanning iteration budgets **1** through **500** and replicate counts **5** and **20**. So the
benchmark's clause is not a description of a handful of runs: the whole valley-and-climb line lives inside it.

**And the two absences are the load-bearing half.** The cell's world is **one** world: the drive, read and coupling
fingerprints each take exactly one value over all thirty-six artifacts, so every number the line has published is
conditional on a single draw. And no configuration key anywhere in the corpus names a reward, a policy, an episode,
a goal or a return -- checked by name over **86** distinct keys in **768** artifacts. Together those say what the
benchmark is: a **retention** benchmark on one world, and not a **behaviour** benchmark. A game in which the agent
can act differently and be scored differently does not exist here; what exists is a stateful world inside one trial
whose state is the label, which is what `e371` called the first playable cell.

**One further limit the card should carry and does not.** The plan's own C4 note fixes the task-count bound for a
permutation test at `1/(T! + 1)`, so with **three** tasks the smallest attainable p-value is **1/7**. The benchmark
cannot claim a p below 0.14 by permuting its own task labels until it has at least seven tasks, and it has three.

## 3. What the card is for

It is the thing the repository has been asked to grow toward, stated once and tied to artifacts: a reader can take
the card and re-derive every number in it from `runs/`. It also fixes the vocabulary -- the *cell* is the card's
loop clause, the *window* is every artifact that wired the loop, and the *absences* are measured rather than
asserted -- so the next revision can be diffed against this one instead of re-argued.

## 4. What it cannot settle

- **A card is a definition and not a result.** It says what the benchmark is; every performance number belongs to the
  units that measured it, and none of them is restated here.
- **The cell is a choice.** The loop clause is the wide step and the linear world. The tight step, the cue source,
  the nonlinear world and the frozen bodies are outside it, so M3 and M4 say nothing about their artifacts, and the
  window's other 28 artifacts are counted by M1 and not covered by the protocol and metric clauses.
- **The absences are the corpus's and not the theory's.** No key names a reward, which does not say a reward could
  not be added, only that nothing in the corpus has one, and the reader who wants a behaviour benchmark needs a
  builder and a runner that do not exist yet.
- **And a card ages.** The plan's FlyCL v0 was written on 2026-09-25 and described three sustained classification
  tasks a month later than the loop arrived; this one names its revision and the date it was read, which is the only
  defence against the same drift.
