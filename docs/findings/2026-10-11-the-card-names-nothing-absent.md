# The card names nothing absent: the episode enters, and the list the card has kept since its first revision is empty

*2026-10-11. `experiments/e490_the_game_card_revision_seventeen.py` writes revision 17: one clause added, the
**episode**, read from `e489`'s two runs and its own measurement recomputed, and one entry removed from the card's
`absent` list -- the last one it held. **UA1, UA2, UA3 and UA4 all MET**, and the list is `[]`.*

## 1. The revision

The clause's numbers, recomputed from the two runs of `e489` at the card's own neutral roll:

| the arm | the boundary run's accuracy diagonal | the plain run's | the change | sigma | the boundary run's last row | the plain run's |
|---|---|---|---|---|---|---|
| `naive` | **0.2476** | 0.2476 | -0.0000 | **-0.00** | 0.2365 | 0.2420 |
| `ewc-block` | **0.2497** | 0.2451 | +0.0045 | 0.61 | 0.2455 | 0.2559 |
| `replay` | **0.2524** | 0.2413 | +0.0111 | 1.02 | 0.2441 | 0.2441 |

and the episode the clause carries, measured again by this unit rather than copied:

| what the clause carries | the number |
|---|---|
| the episode | **3** trials of **4** steps, the pass's twelve split evenly |
| the world's state at the read step | the earlier trials move it by **0.7601** at **12.62** sigma over **64** episodes |
| the same manipulation at one trial per pass | **exactly 0** |
| the state's own scale | **0.7727** |
| the boundary | **8** neurons at gain **1.0**, marks `+1, 0, 0, 0, -1, 0, 0, 0, -1, 0, 0, 0`, **0** overlapping the three populations, inside the input, none at the endpoint |

| claim | measured | verdict |
|---|---|---|
| UA1 the sixteenth revision is carried, and the absent list is empty | **29** fields of `e486`'s card equal, the revision **17**, and `absent` going from `['an episode boundary']` to **`[]`** | **MET** |
| UA2 the clause's numbers come out of the runs and the measurement | **3** arms' boundary and plain diagonals with their contrasts and sigmas at **20** replicates with **0** disagreeing past the tolerance, the carry and the channel equal to the measurement's | **MET** |
| UA3 the clause's bearing is that the episode is carried and its opening marked | **0.7601** at **12.62** sigma beside **0.0e+00** at one trial, the marks the declaration, disjoint and inside the input | **MET** |
| UA4 the clause carries what the episode costs | every arm within **0.05** of the four-class chance of **0.25**, and the boundary's contrast unresolved on every arm | **MET** |

## 2. What the empty list means

**The clause is the runs and the measurement, and nothing in it is quoted.** `e486`'s card survives field for field --
**29** fields equal -- with only the revision, the new clause and `absent` moved, so this revision is an addition and a
subtraction and not a rewrite. Every number the clause carries is recomputed here twice over: from the two runs by
`e489`'s own reader, and from the connectome by `e489`'s own two measurements, and both agree with what `e489` wrote
to disk to a thousandth of a point. **So the clause says what the environment does and not what a unit said it did.**

**And the list the card has kept since its first revision is empty.** It read *a reward, a policy, an episode
boundary, a held-out task* when `e392` wrote the card down; `e470` removed the held-out task, `e482` the policy,
`e486` the reward, and this unit the episode boundary. **Four removals, each one a unit after the environment had
gained the capability and the benchmark had carried it**, which is the route those four units followed on purpose.
Read with `e486` it is the third revision in a row whose only content is a capability the corpus already had.

**And the clause carries the cost and not only the capability.** Every arm's accuracy on both runs sits within
**0.05** of the four-class chance and no boundaried contrast resolves, and that is `e489`'s fourth claim's firing
recorded in the card rather than left in the finding beside it: the read step is the pass's last one, the earlier
trials move the world's state by its own scale, and the label is a small part of what the head reads. **So this is
what the card now says the game is**: a substrate, a loop, a protocol, arms, metrics, a stream, a world, a held-out
task, a policy, a reward and an episode -- **and a benchmark whose episodic task cannot be done by any arm it
carries**.

**And an empty list is not completeness.** The card's `absent` list is its own account of what its game does not
have, measured against the corpus, and *naming nothing absent* is a statement about the card and not about the
benchmark's adequacy: `e392`'s own M5 measured the absences over `runs/` once and every one of them has since been
closed by a unit, and a card ages -- the episode it now names is one whose read step makes it a chance-level task,
which is a gap no `absent` entry ever named.

## 3. What it cannot do

- **One revision of one world**: the clause is read from one pair of runs at one budget, one episode length and one
  seed stream, so the episode's numbers are one setting's.
- **And a clause is not a result**: UA1 shows revision 16 survives into revision 17 and not that revision 16 was
  right, and the route from environment to benchmark to card is a convention rather than evidence.
- **And the clause carries a cost it cannot explain**: that the episode's task sits at chance is `e489`'s measurement
  of the read step, and a card is a record.
- **And an empty `absent` list is bookkeeping**: it says the card names nothing absent, which is a statement about the
  card's own account of the game and not about the game being usable or the benchmark being fair.
