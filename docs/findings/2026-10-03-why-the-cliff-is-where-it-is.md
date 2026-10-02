# Why the cliff is where it is: the cue population is two hops from the action population, and the cliff is `tau - 2 - d`

*2026-10-03. `experiments/e369_why_the_cliff_is_where_it_is.py` walks the circuit's own mask from the cue
population to the population the world's drive listens to, and rolls `e368`'s curve at two circuit sizes to check
the formula the walk implies. Five and a half seconds. Writes
`runs/e369_why_the_cliff_is_where_it_is.json`. Four claims, registered before any distance or any curve was read.*

## 1. The formula

The model's step is `x_{t+1} = (1 - a) x_t + a tanh(W x_t + b + u_t + fb_t)`, and a perturbation of `x` moves one
hop per step: `x_{s+1}` is nonzero on the neurons the cue is written on, `x_{s+1+d}` on the neurons at distance `d`.
The world's drive at step `t` reads `x_t`, and the trial's last world update is at `t = tau - 1`, so the last state
the world can see is the one produced by step `tau - 2`. **A population at directed distance `d` from the cue
population can hold the trial's trace at cue steps up to `tau - 2 - d`** and at no later one.

With `tau = 12`: **10** for the population the cue is written on, and **`10 - d`** for any other.

## 2. The distance

`mb+cx+al@n952`, 952 neurons, **20 079** edges: the cue population's directed distance to the action population is
**2**. With 12 cue neurons and 8 action neurons there are **96** possible direct edges and the mask holds none of
them, so the action population cannot see the cue before the second hop and the world cannot see the action
population's response before `x_{s+2}`.

**P1 MET**, and the falsifier's two directions are both informative: a distance of 1 would say a direct edge exists
and `e368`'s step-9 cliff needs another cause, and 3 or more would put the cliff earlier than either unit measured.

## 3. The check

| size | neurons | edges | distance (cue / action) | predicts | curve clears to |
|---|---|---|---|---|---|
| 300 | 952 | 20 079 | 0 / **2** | 10 / **8** | 10 / **8** |
| 600 | 1 149 | 23 551 | 0 / **2** | 10 / **8** | 10 / **8** |

**P2 MET**: `tau - 2 - d` predicts **10** and **8**, the curve measures **10** and **8**, and `e368`'s artifact
records **10** and **8**. The two cliffs that unit found one step apart are the same number 10 minus a distance.

**The `cue` distance is 0 by construction and not by the connectome**: with `drive_from_cue` the environment sets the
drive population to the cue population itself, which is why that source's cliff is the formula's maximum. The
environment's design is a fact about the design and is reported as one.

**P3 NULL, and the null is the honest reading.** The claim was that a second circuit size -- which redraws all three
populations from a different pool -- would move the distance and the cliff together. It moved neither: at 1 149
neurons the distance is again **2**, so the formula predicts the same number a second time and the check is on its
arithmetic rather than on its mechanism. What the second size does buy is a **replication of the shape** on an
independent draw: a different circuit, different populations and a different mask, and the same two cliffs at the
same two steps, with the curve above them of the same kind -- the cue source climbing from **0.6992** to **0.8672**
by step 8, the action source from **0.6836** to **0.8438**, and both constant from step 9 on. The **null is
registered as a null**, and the unit that would discriminate is named below.

**P4 MET**: every entry of `world_drive` -- 8 by 8 for the action source and 8 by 12 for the cue source -- and of
`world_read` (8 by 12) is nonzero at both sizes, so the world sees the whole drive population and answers through
the whole feedback population. The cliff is the circuit's wiring and not a hole in a drawn map.

**And the instrument reproduces `e368` exactly**: the first size's twelve steps of both sources are that artifact's
twelve steps to the digit, which is what makes the comparison with it a comparison rather than a coincidence.

## 4. What it means

**The cliff is computable before anything is rolled.** For this family of worlds the window a read-out has is
`tau - 2 - d`, where `d` is a directed shortest path in the connectome's own mask between two drawn populations --
no training, no probe and no roll. `e368` spent a curve to find where the window ends; this says where it ends from
the wiring, and it says the same number for a second circuit.

**And it gives the game its horizon.** A closed-loop task whose read-out listens to the agent's own action has
about **steps 0 to 8** of the trial to work in, because the world's last readable state is two steps short of the
read-out and the action population is another two hops short of the cue. A task that needs the agent's action to
carry the symbol has to deliver the cue at the start of the trial and read at the end; a task that needs it later
needs a different drive population -- one hop away, or the cue population itself.

**`e367`'s bit-identity is now fully accounted for.** That unit trained the action source at `cue@10` and `cue@11`
and got the same twenty replicates twice; `e368` showed the world is at rest at both steps and that a body with a
bias cannot see the trial either; and this unit says why the boundary sits between steps 8 and 9, which is one step
below the cell that was trained.

## 5. What it cannot do

*One distance, one pair of populations, two sizes*: both sizes gave **2**, so the formula is checked at the
configuration it was proposed for and its arithmetic is checked at a second, and a configuration whose distance is
**not 2** is what would test it -- a population draw with a direct cue-to-action edge, or a smaller circuit, is the
unit this one points at. *And the formula is about the trace existing, not about a probe clearing chance*: it says
which steps can hold the cue at all, and whether a least-squares probe at 512 examples recovers it at that step is a
second question, which is why P2 and P3 compare the formula against measured clearing steps rather than deriving
them. *And `d = 0` for the cue source is the environment's design*: the world listening to the cue is listening to
the neurons the cue is written on because `drive_from_cue` sets those populations equal, so the maximum of the
formula is a modelling choice and not a measurement of the connectome.
