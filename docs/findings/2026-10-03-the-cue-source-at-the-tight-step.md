# The cue source at the tight step: the head was worth 0.2132 there and 0.0104 on the action source, so the playable end of the window moves and the other does not

*2026-10-03. `experiments/e378_the_cue_source_at_the_tight_step.py` runs the cue source at `cue@8` -- the last step
`e368`'s curve says both channels are alive on this draw -- with the head's step size at `e376`'s `0.03`, filling
the fourth cell of that row. 1049 s; the reader is `runs/e378_the_cue_source_at_the_tight_step.json`. Five claims,
registered before the run's reading was opened.*

## 1. The row, complete

The tight step `cue@8`, both drive sources, the corpus's head at two step sizes, against each source's own probe on
the **untrained** body:

| cue@8, source | lr 0.003 | lr 0.03 | probe on the untrained body |
|---|---|---|---|
| **cue** | 0.4368 | **0.6500** | **0.8906** |
| **action** | 0.2333 | 0.2437 | **0.7617** |

| cue at | source | lr | arm | diagonal | forgetting | paired channel |
|---|---|---|---|---|---|---|
| 8 | cue | 0.03 | naive | **0.6500** | 0.2594 | +0.2285 (16.47 sigma) |
| 8 | cue | 0.03 | replay | 0.6292 | **0.0396** | +0.3649 (26.46 sigma) |
| 8 | cue | 0.003 | naive | 0.4368 | 0.0563 | +0.1535 (8.81 sigma) |
| 0 | cue | 0.003 | naive | **0.8399** | 0.4094 | +0.3115 (18.74 sigma) |

| claim | measured | verdict |
|---|---|---|
| Y1 one configuration at both comparisons | vs `e374` differing `{'lr'}`, vs `e372` differing `{'lr'}` | **MET** |
| Y2 the channel is live at this step | **+0.6406** over chance, spread **0.0600** | **MET** |
| Y3 the step size helps this source too | **+0.2132** on a sem of **0.0202**, **10.55 sigma** | **MET** |
| Y4 the tight step still costs | **0.1899** below the wide step | **MET** |
| Y5 the answer is still earned | **+0.2285 at 16.47 sigma** and **+0.3649 at 26.46 sigma** | **MET** |

## 2. The same lever, two answers

**The step size is worth 0.2132 to the cue source at this cell and 0.0104 to the action source.** Same step, same
head, same twenty seeds, same suite: **+0.2132 at 10.55 sigma** against **+0.0104 at 1.78 sigma**. That is `e377`'s
interaction appearing across sources rather than across bodies, and it says the same thing from the other side: what
a better-fitted head buys depends on whether the representation underneath it is still there.

**So the playable end of the window moves and the other does not.** The cue source at the tight step goes from
**0.4368** to **0.6500** when the head is allowed to fit -- still **0.1899** below the wide step, and still above
chance by **0.4000** with the answer coming through the loop at **16.47 sigma** -- while the action source stays at
chance under the same change and under everything else this line has turned at that cell. A game built on this
world can be played at `cue@8` **on the cue source**, and only there.

**And the buffer still helps, on a fourth substrate.** At the tight step with the larger head, `replay` forgets
**0.0396** against `naive`'s **0.2594** -- a paired **-0.2198 at 8.35 sigma** over the twenty seeds -- and the
channel moves from **+0.2285** to **+0.3649**. That is the same direction `e276`, `e355`, `e371` and `e372` found,
now at the window's tight end.

## 3. The caveat this unit makes unavoidable

**Every diagonal in this row made at the corpus's step size is a lower bound.** The wide step's **0.8399** was read
at `lr = 3e-3`, and this unit shows the same source at the same head recovers **0.2132** of what it was short of at
the tight step when the step size rises. So the **0.1899** that Y4 reports as the margin's cost is **not** the
margin's cost: it is the tight step measured with a fitted head against the wide step measured with an unfitted one,
and if the wide step is also short of its own ceiling then the true cost of the margin is **larger** than 0.1899.
Nothing in this unit measures the wide step at the larger size, and until something does, **the price of the window
is a number with a direction and not a magnitude**.

This is the same kind of caveat `e366` put on this line's example counts and arrangements, and it reaches further:
`e363`'s frozen grid, `e364`, `e365`, `e367`, `e368`, `e369`, `e370`, `e371`, `e372`, `e373` and `e374` were all read
with the corpus's `lr = 3e-3` wherever a head was trained. Every trained diagonal in that list is a lower bound on
what its cell can reach, and the ones where the world's spread is small are the ones where the gap is largest.

**And `e374`'s own headline is the one that matters for the game.** At the tight step the action source is at chance
and the cue source is at **0.6500** with a fitted head; the difference between the two sources there is not the
head, which this unit just moved, and not the cue's step, which `e374` held, and not the body's plasticity being
removable, which `e375` tested. It is what the body does to its own representation while it is being trained, and
that is the unit this one points at: the trained body's weights are not in any artifact unless a run keeps them
(`--save-theta` exists for exactly that), so the measurement that would settle it is a probe on the **trained**
body's world and not on a frozen one's.

## 4. What it cannot do

*One lever at one value*, as in the two units before it: ten times the default is a direction and not a dose, so
where the step size stops mattering is not measured and a larger one is not ruled out at either source. *One cell
and one draw*: `cue@8` on this draw, whose boundary `e370` showed moves with the draw, so a different draw's tight
step is a different cell. *And it does not say what the body did to the representation*: this unit moves the head
and reads the diagonal, so the difference between a world that carries less and a world that carries the same thing
less readably is exactly the measurement it does not make.
