# Where the cue can reach the world: the timing is the hard limit and the populations are what make one step too few

*2026-10-02. Nothing trains: `experiments/e363_where_the_cue_can_reach_the_world.py` rolls the **frozen** connectome
network on one world in six cells -- two drive sources by three cue steps -- and decodes the world's final state with
the corpus's own least-squares probe. Seconds. Writes `runs/e363_where_the_cue_can_reach_the_world.json`.*

## 1. Two causes, named together, told apart

`e362` found the cue unreadable at the read step and its finding gives the cause as two things at once: the cue is
delivered onto `cue_neurons` and the world reads its drive off `action_neurons`, **two disjoint populations**, and
the drive is computed from the state **carried into** the step, so anything delivered at that step's input arrives
one step later.

**`CueActionEnv.build` gained `drive_from_cue`**, which points the world's drive at the cue's own neurons instead of
the action population. The draw is unchanged -- the same three populations are picked -- so the recorded fingerprints
show the manipulation exactly: the action's fingerprint becomes the cue's in those cells and stays its own in the
others. **Six frozen rolls** then say which cause is which.

## 2. The answer

| drive reads | cue at step 0 | cue at step 10 | cue at step 11 |
|---|---|---|---|
| the action population (disjoint from the cue) | 0.6602 | **0.2578** | **0.2578** |
| the cue population itself | 0.7891 | **0.8555** | **0.2578** |

chance 0.2500, 256 train and 256 test examples, one world of eight dimensions at `leak = 0.35`.

**T2 MET, and it is the first half of the answer: at the read step the world carries nothing, in both sources** --
0.2578, exactly chance, whether the drive listens to the cue's own neurons or to a disjoint population. **So the
timing is the hard limit and the populations are not the cause of it.** A world whose drive is *on* the cue's
neurons still cannot see a cue delivered at the step it is read, because the drive at that step was computed from the
state carried into it.

**T3 MET**: at step 0 both sources carry it (0.6602 and 0.7891). **T4 MET**: the drop from step 0 to the read step is
**0.4023** and **0.5312**.

**T5 FALSIFIER FIRED, and it is the second half: the populations are what make one step too few.** The registered
prediction was that one step of margin suffices in both sources. It does in the cue source -- **0.8555**, far above
its own step-0 reading -- and it does **not** in the action source, which is at chance (**0.2578**). So the two
causes have different jobs: the **timing** is necessary, and the **populations** decide whether the one step the
timing allows is enough.

**And the arithmetic says why, exactly.** The cue at step 10 is written into `u_10` on the cue neurons. The state at
step 10 is `(1 - alpha) x_9 + alpha * tanh(W x_9 + bias + u_10)`, so on the **cue** neurons it carries the cue and on
the **action** neurons it carries only `W x_9`, which has never seen it. The world's drive at step 11 reads the state
carried into step 11 -- that is, `x_10` -- so it sees the cue if and only if it reads the cue's own neurons. One
step of margin is enough for a world that listens there and not for one that makes the cue cross the connectome.

## 3. What it settles

`e362`'s finding named the populations first and the timing second, and the ordering was wrong: **the timing is the
limit; the populations decide what the limit costs.** That is a correction to a claim published one unit ago, made by
a unit that trains nothing, and it is why this one exists.

**It also gives the benchmark its first interface knob.** The corpus now has a world whose drive can be pointed at
the neurons the cue arrives on, which is the setting in which a cue one step old *is* readable at 0.8555 -- so the
interface, and not only the world's rule, is a variable a game-shaped task can be built on.

## 4. What it cannot do

*The two sources differ in more than the source*: the drive map's width follows the population it reads (8 for the
action population, 12 for the cue's), so the two cells consume different amounts of the environment's draw and their
**read maps land differently** -- the world-read fingerprint is not shared across sources, and T1 names that rather
than requiring it. *A frozen body*: this is the substrate's carrier, so it says where the information *can* be, and
`e362` is the trained version of the `cue_at = 11` cell (it agrees, 0.2361) while the trained versions of the other
five cells are not run. *One world draw and one coupling*: eight dimensions at `leak = 0.35` with `e359`'s matrix.
*And the probe is linear*, so "carries nothing" means a linear decoder on the world's own state does not recover it, which
is the bar `e345` and `e348` used.
