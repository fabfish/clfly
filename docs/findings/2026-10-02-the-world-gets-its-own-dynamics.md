# The world gets its own dynamics: the earned label survives a state that mixes itself

*2026-10-02. One runner invocation -- `e356`'s exact flags plus `--loop-world-coupled`, `--methods naive,replay`,
`--repeats 20` -- into `runs/e359_earned_label_coupled_20reps.json`, paired against `e356`'s uncoupled arms at the
same seeds. Eighteen minutes. Read by `experiments/e359_the_world_gets_its_own_dynamics.py`.*

## 1. The gap `e333` named

`e350` gave the world a **dimension** -- a state vector driven by the whole action population -- and `e351` found the
width bought 88% of that unit's gain. But every dimension of that state is still an **independent leaky integrator**
of the drive, which `e333` named as its own gap in one sentence: *"The world's rule is linear and scalar: one leaky
integrator of one action, with no state-to-state coupling and nothing the agent's actions can push it into."*

**This gives the world its own dynamics.** `CueActionEnv` gained `world_coupled`: a fixed
`(world_dims, world_dims)` matrix replaces the independent integrators with
`w_t = (1 - leak) * (w_{t-1} @ K.T) + leak * drive_t`, so the world **mixes its own dimensions as it carries them**,
and `K = I` is the uncoupled rule exactly -- the endpoint the control rests on and the reason the field is additive.
The matrix is drawn from the environment's seed, scaled so its largest singular value is one, and fingerprinted:
this run's coupling is `5326f4a0edb4` and its world is `3a7ba76b3619`, the same draw `e355` and `e356` used, with the
cue, action and feedback populations unchanged.

## 2. The answer

| world | arm | final accuracy | diagonal | `mean_forgetting` | paired channel | sigma |
|---|---|---|---|---|---|---|
| plain | `naive` | 0.5493 | **0.8226** | **0.4099** | +0.2951 | 19.73 |
| plain | `replay` | 0.6983 | 0.7802 | 0.1229 | +0.4434 | 34.84 |
| **coupled** | `naive` | 0.5191 | **0.7691** | **0.3750** | +0.2642 | 18.08 |
| **coupled** | `replay` | 0.6785 | 0.7389 | **0.0906** | +0.4247 | 31.65 |

chance 0.2500. **T1 MET**: one configuration except the world's rule -- the coupled run records its coupling and
nothing else differs, with the uncoupled reference's absent record meaning the uncoupled rule because that artifact
predates the field.

**T2 MET**: a body **can** drive a world that moves on its own -- the coupled `naive` arm's diagonal mean is
**+0.5191 above chance**. **T3 MET**: and the answer is still **earned**, at **+0.2642 (18.08 sigma)** and
**+0.4247 (31.65 sigma)** -- the signature `e355`, `e356` and `e358` measured on the uncoupled world, intact on one
that mixes itself. **T4 MET**: the coupled suite forgets by **0.3750**. **T5 MET**: and the buffer is worth
**0.2844 at 14.37 sigma** -- **more** than the 0.2521 it was worth on the uncoupled world.

**So the world's own dynamics costs a little and breaks nothing.** The coupled arms sit about **0.05** of diagonal
below the uncoupled ones (0.7691 against 0.8226 under `naive`) and forget slightly less on `naive` (0.3750 against
0.4099) while the buffer's value rises. Nothing here is resolved as a contrast -- these are two configurations'
levels -- but the shape of the benchmark is unchanged: learned, earned, forgotten, and repaired by a buffer.

## 3. What it means for the game the user asked for

A game-like continual-learning benchmark needs a world whose state is a **consequence with its own life**, and this
is the first version of it: the agent's actions drive the state, the state mixes itself as it carries them, and the
answer is read from the world and exists nowhere else. **What the corpus now holds on the earned label** is four
twenty-replicate runs on one substrate -- uncoupled, coupled, frozen and matched-random -- with the method contrast
resolved at **11.65 sigma**, the basis contrast a null at 1.47, the frozen control showing that all of the
forgetting is the body's, and the coupling costing about 0.05 while leaving every property in place.

## 4. What it cannot do

*One coupling and one draw*: a single matrix from one seed, with its largest singular value scaled to one but its
**shape** unexamined -- a rotation, a contraction, a near-singular map and a differently drawn `K` are four different
worlds and only the first is run. *The uncoupled reference is a different artifact*, and what makes the pairing
legitimate is the recorded fingerprints and the per-replicate seed stream agreeing, plus the allowance that an
absent coupling record on the older side means the uncoupled rule. *One leak and one width*: `leak = 0.35` and eight
dimensions. *And a coupled world is not a nonlinear one*: the rule stays linear, so the world still cannot be pushed
into a state and trapped there, which is the next thing `e333`'s sentence asks for.
