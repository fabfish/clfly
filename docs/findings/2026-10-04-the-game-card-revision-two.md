# The game card, revision 2: the benchmark with the two numbers a user must now report

*2026-10-04. `experiments/e409_the_game_card_revision_two.py` writes the second revision of the closed-loop benchmark's
card and reads **every** number in it from the artifact that measured it. No training and no roll. Five claims,
registered before this unit read any of them.*

## 1. The card

**The closed-loop earned-label game, revision 2, read 2026-10-04.**

Its first revision's clauses are carried unchanged -- published here as the artifact holds them, and checked against
`e392`'s own card:

| clause | what it says |
|---|---|
| **substrate** | circuit `mb+cx+al@n952`, 300 neurons, read-out draw `59926518137c`, basis `cell_class`, support 80, `seed0 = 0`, 4 classes per task |
| **loop** | the cue pulse at step **0**; the world's drive reads the **action** population; the world is **8**-dimensional, **coupled** with leak **0.35**, **linear**; the head reads the **world** |
| **protocol** | three tasks in sequence; 96 train / 48 test; `lr = 3e-3`; the iteration budget is the schedule |
| **arms** | `naive`, `replay` |
| **metrics** | accuracy; the retention matrix's diagonal; its last row; their difference; backward transfer |
| **absent** | a reward; a policy; an episode boundary; a held-out task; a second world; a second draw |

And four clauses the redraw series established, each with the artifact it is read from:

| clause | reading | artifact |
|---|---|---|
| **world** | the six worlds span **0.0750** at 20 updates and **0.3104** at 500 | `e407` |
| **stream** | three clean streams span **0.0323** at the far point against the worlds' **0.3344**, **0.097** of it | `e403` against `e396` |
| **recovery** | **1** of **5** worlds measured at the far point ends above its own connectome reading by 0.05 | `e396` |
| **invariance** | the connectome's own reading is **0.6875** over **35** readings, spread **0.0000** | `e396` and `e407` |

| claim | measured | verdict |
|---|---|---|
| AM1 the first revision's clauses are unchanged | **6 of 6** equal | **MET** |
| AM2 the world clause is measured at both ends | **0.0750** and **0.3104** over six worlds | **MET** |
| AM3 the stream clause is measured against the world's | **0.0323** against **0.3344** | **MET** |
| AM4 the recovery clause is one world's | **1 of 5** | **MET** |
| AM5 the invariance clause is carried | **0.6875** over **35** readings, spread **0.0000** | **MET** |

## 2. What revision 2 says that revision 1 could not

**The absence is now a pair of numbers.** Revision 1 measured that its cell carried **one world** and **one seed
stream**, so every number the line published was conditional on both, and it could state that only as a sentence.
Revision 2 carries the two spreads beside the numbers they bound: at the far point the **world** axis spans 0.3344
across five draws and the **stream** axis spans 0.0323 across three, so a user of the benchmark can see that the draw
is the axis that matters and by how much.

**And the draw is not merely large, it is decisive.** One of five worlds recovers and four end below an untrained
body, so the clause is not "the draw moves the reading by a third" but "whether the body keeps the cue at all is the
draw's". A benchmark that reports one number without its draw is reporting one of five outcomes without saying which.

**And the one thing that does not move is named with its count.** Thirty-five readings of the connectome's own
weights, across two artifacts, five worlds and six budgets, take **one** value. A benchmark whose most stable
quantity is the untrained body's reading and whose least stable is the trained one's is a benchmark about what
training does to a circuit, which is the question the repository was built to ask.

## 3. What it cannot settle

- **A card is a definition and not a result**: it states what the benchmark is and points at the artifacts for every
  number in it.
- **And the numbers are six worlds' and one arm's**: the four engine redraws are not in the six-budget series, and
  the 3e-3 `naive` bodies are the only ones measured at those budgets.
- **And the clause it cannot state is the mechanism**: the line has screened the draw's distance to the action
  population, five geometric properties of it, the substrate's own biological groupings and the trained bodies'
  movement and alignment, and none of them separates the one world that recovers.
