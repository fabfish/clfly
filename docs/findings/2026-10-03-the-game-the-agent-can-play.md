# The game the agent can play: at the first step the closed loop learns to 0.7691, beats the frozen probe it was measured against, and the buffer cuts forgetting by 0.2844

*2026-10-03. `experiments/e371_the_game_the_agent_can_play.py` trains the closed loop at the **first** cue step --
the world's drive reads the agent's own action population, the cue arrives at step 0, and the world's final state is
the read-out -- at `e367`'s flags with `--loop-cue-at 0`, twenty replicates, two arms, three tasks in sequence.
Nineteen minutes for the run; the reader is `runs/e371_the_game_the_agent_can_play.json`. Five claims, registered
before the run's reading was opened.*

## 1. The result

| cell | cue at | arm | final | diagonal | forgetting | paired channel |
|---|---|---|---|---|---|---|
| **played** | **0** | naive | 0.5191 | **0.7691** | 0.3750 | **+0.2642** (18.08 sigma) |
| **played** | **0** | replay | **0.6785** | 0.7389 | **0.0906** | **+0.4247** (31.65 sigma) |
| empty | 10 | naive | 0.2514 | 0.2361 | -0.0229 | +0.0010 (0.16 sigma) |
| empty | 10 | replay | 0.2483 | 0.2375 | -0.0161 | -0.0028 (0.31 sigma) |

chance 0.2500. The frozen probe for this configuration reads **0.6602** on a world with spread **0.2029**.

| claim | measured | verdict |
|---|---|---|
| G1 one configuration except the cue's step | every recorded field equal to the read-step run's, cue steps 10 and 0 the only difference | **MET** |
| G2 the channel is live here | `e363`'s `action@0` is **+0.4102** over chance | **MET** |
| G3 the game is learnable | naive diagonal **+0.5191** over chance | **MET** |
| G4 the answer is earned through the agent's own action | naive **+0.2642** at **18.08 sigma**, replay **+0.4247** at **31.65 sigma** | **MET** |
| G5 the buffer helps in this substrate | replay forgets **0.2844** less, at **14.37 sigma** over 20 pairs | **MET** |

**And the game cell is 0.5330 above the empty one.** The same instrument, the same suite, the same twenty seeds and
the same drive population: at step 10 the trained body reads **0.2361** and at step 0 it reads **0.7691**. That is
reported and not claimed, because the two runs differ by construction and `e369` and `e370` already explain the
difference from the wiring -- the cue population is **2** hops from the action population in this draw, and the
world reads the state produced two steps before the trial ends.

## 2. The number the corpus has not seen before

**The trained body reads more than the frozen probe.** 0.7691 against 0.6602, a gap of **+0.1089**, and the three
earlier trained cells in this line all read *below* their frozen probes: `e365`'s cue-source cell at 0.5337 against
a probe's 0.8555, `e367`'s action-source cell at 0.2361 against a probe's 0.2578, `e364`'s at 0.2326 against the
same. So this is the first cell where the thing that was trained beats the thing that was handed to a least-squares
decoder for free.

**And it lands within 0.0200 of the other source's frozen ceiling.** At the same step, `e363` read the world whose
drive listens to the **cue population** at **0.7891** -- the channel a body would be given rather than have to
build. The trained body, which builds it through its own action population, reads **0.7691**. Both numbers are
reported rather than claimed: the first is arithmetic on two registered readings and the second is across two
artifacts and two drive sources, and neither had a registered bar. What they say is that at this step the price of
acting rather than being listened to is inside the noise of a twenty-replicate diagonal.

## 3. What it means

**This is the first playable cell of the game the repository was asked to grow toward.** An agent whose own action
drives the world, a world whose state is the answer, a cue delivered early enough for the wiring to carry it, three
tasks trained in sequence, and a buffer that halves the forgetting: every part of a closed-loop continual-learning
benchmark is now measured on the connectome rather than assumed. The two units before this one are what made it
possible: `e369` said the window is `tau - 2 - d` and `e370` said `d` is the draw's, so the cell to train is the
one at the **wide** end of the window and not the one at the narrow end, which is where the line had been looking.

**And the buffer's result is `e276`'s question on a substrate that did not exist when it was asked.** That unit
found replay beating the penalty at twelve sigma on the earned-label suite; here, on a task whose answer exists only
in the world and is carried by the agent's own action, replay cuts forgetting from **0.3750** to **0.0906**, a paired
**-0.2844** at **14.37 sigma** over twenty replicates, and it does so while reading *better* (final accuracy 0.6785
against 0.5191) rather than by trading accuracy for stability. `naive` at this cell forgets **0.3750**, against at most **0.0922**
in the four closed-loop cells trained before it, so the game is not an easy suite being solved: it is a suite with
real interference and a buffer that removes most of it.

**And `naive` and `replay` differ in the channel as much as in the metric.** The paired channel reads **+0.2642**
under `naive` and **+0.4247** under `replay`: the arm that keeps a buffer is also the arm whose answer depends more
on the loop, which is the same direction `e355` found through the runner and is now on a task with a live channel.

## 4. What it cannot do

*One cell at one drive source*: the cue-source game at the same step is `e363`'s frozen **0.7891** and has **no
trained run**, so this unit does not price what it costs the agent to act rather than to be listened to -- the
0.0200 above is a comparison across two artifacts and two drive sources and not a paired measurement, and the run
that would pair them is a unit of its own. *One world and one coupling*: eight dimensions at `leak = 0.35` with
`e359`'s matrix and the action source's own draw, and `e370` found that draw is a **two-hop** one, so the window here
is one step shorter than the modal draw's -- this cell sits at the wide end either way, and a cell one step later
would not survive the modal draw's being the short one. *And "learnable" is a diagonal above chance*: the corpus's
significance convention is a paired channel at 2 sigma and its floor is the test set's own noise, so a resolved G3
is a statement that the suite trains, not that it trains well -- and the per-replicate spread the runner reports
(`replay`'s 0.0437, of which 79% is evaluation) is what a smaller effect would have to clear.
