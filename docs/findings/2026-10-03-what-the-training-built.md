# What the training built: at the wide step it puts 0.1118 more of the cue into the world, and again a probe reads exactly what the head reads

*2026-10-03. `experiments/e380_what_the_training_built.py` runs `e371`'s cell -- the action source at `cue@0`, the
corpus's head and step size, twenty replicates, two arms -- with `--save-theta`, and rolls the saved recurrent
weights before training and after each task with the corpus's own probe fitted on the world each time. 1042 s for
the run; the reader is `runs/e380_what_the_training_built.json`. Five claims, registered before the run's reading
was opened.*

## 1. The wide end, and its mirror

| arm | probe, initial body | probe, trained body | trained head | world's spread |
|---|---|---|---|---|
| naive | **0.6736** | **0.7854** | 0.7691 | 0.2780 to **0.3159** |
| replay | **0.6736** | 0.7611 | 0.7389 | 0.2780 to 0.3159 |

chance 0.2500; `e363`'s frozen grid records **0.6602** for this cell on an untrained body.

| claim | measured | verdict |
|---|---|---|
| ZA1 the reconstruction is faithful | **0.0000** apart from the artifact's own per-replicate `learned`, over 120 replicate-tasks | **MET** |
| ZA2 the initial body reproduces `e363`'s cell | **+0.0135** from **0.6602** | **MET** |
| ZA3 the trained body carries the cue | **0.7854**, **+0.5354** over chance | **MET** |
| ZA4 the training put more of the cue there | **+0.1118** on a sem of **0.0093** over 60 paired replicate-tasks | **MET** |
| ZA5 a probe on the trained body beats the trained head | **+0.0163** on a sem of **0.0064** | **FALSIFIER FIRED** |

**And the two ends of the window are now the same measurement with opposite signs.**

| step | probe, initial | probe, trained | trained head | what the training did |
|---|---|---|---|---|
| `cue@0` (widest) | 0.6736 | **0.7854** | 0.7691 | **built +0.1118** of the cue into the world |
| `cue@8` (tightest live) | 0.6597 | **0.2361** | 0.2437 | **removed 0.4236** of it |

## 2. What the fired claim says

**The corpus's trained head reaches everything a closed-form fit reaches on the body it was trained against, at both
ends of the window.** At `cue@0` the probe reads **0.7854** and the head **0.7691** -- **+0.0163**, unresolved. At
`cue@8` (`e379`) the probe reads **0.2361** and the head **0.2437** -- **-0.0076**, unresolved. So the head is
neither beating nor losing to the probe anywhere this line has measured it on the body that was trained.

**Which means the head is never the limit; the body is.** Every comparison this window has made of "a trained head
against a frozen probe" was across two different bodies, and the honest reading of all of them is a statement about
what the training did to the world: at the wide step it **adds** **0.1118** of the cue to what a linear fit can
recover, and at the tight step it **destroys** **0.4236** of it. `e371`'s **0.7691** against the untrained body's
**0.6602** was therefore not the head finding more in the same representation -- the representation itself was
better -- and `e374`'s chance reading was not the head failing to find what was there, because nothing was.

**And the head is saturated at both ends.** That is what `e375` to `e378` were circling: freezing the body recovers
**0.2156** at the tight step, the head's step size is worth **0.1965** on a frozen body and **0.0104** on a plastic
one, and the cue source's own step size is worth **0.2132**. Every one of those levers moves a *frozen* body's
number, and none of them moves a plastic one, because on a plastic body the head has already taken everything the
world has.

## 3. What it means for the game

**The playable end of the window is the wide one, and what makes it playable is the body's plasticity.** At `cue@0`
the trained world carries **0.7854** and the trained head reads **0.7691**; the untrained body carries 0.6736 and
`e363`'s probe read 0.6602. At `cue@8` the same training leaves the world at chance. So a closed-loop task on this
connectome is a task **about what training does to the recurrent weights**, and the read-out is transparent: a
least-squares fit on eight numbers recovers what the SGD head recovers, at both ends.

**And it closes the piece of `e372` that was left open.** That unit found the two drive sources 0.0708 apart at
`cue@0` and called it the price of acting; this unit's `cue@0` numbers are for the action source, and `e378`'s
`cue@8` numbers are for both -- so the shape over the window is now: the cue source keeps working to the boundary,
the action source works at the wide end and is emptied at the tight end, and in every cell a probe on the trained
body reads what the head reads.

**Reported and not claimed**: the world's spread **grows** at both ends, from 0.2780 to 0.3159 here and from 0.0479
to 0.1667 at `cue@8`, so the training makes the world louder wherever it is, and what differs is whether the label
is in it. And ZA2's **+0.0135** is worth comparing with `e379`'s Z2, which came out a null at **-0.1020**: the same
kind of roll against a frozen cell reproduces it here and not there, which is what a world with a spread of 0.2780
against one of 0.0479 would do to a 96/48 probe.

## 4. What it cannot do

*One cell per end*: `cue@0` and `cue@8` on this draw with the drive on the agent's own action, so the cue source's
wide end and every step between the two are not measured, and `e370` showed the boundary moves with the draw. *And a
probe is not a mechanism*: it says how much of the label a linear fit recovers from the world's eight numbers, so
"built 0.1118" is about recoverability and not about what the body changed, and a label a linear fit cannot reach is
not thereby absent. *And `--save-theta` keeps the body at each task's end*, so nothing here says when during the 500
iterations the world gained or lost the cue, which is the measurement that would say whether the tight step's loss
is a collapse at a particular update or a drift.
