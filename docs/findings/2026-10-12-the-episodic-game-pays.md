# The episodic game pays: the target follows the label, and a draw-order defect it found

*2026-10-12. `experiments/e498_the_episodic_game_pays.py` makes the payout's target follow **the cue the label names**
-- the last trial where the label is the episode's last cue and the first where `e495` puts it there -- so the runner
no longer refuses the label-first placement with `--loop-reward`, and the episodic pass can be **paid**. **OB1, OB2 and
OB3 MET and OB4's falsifier FIRED.** And the unit found a defect in the draw order the corpus's other fields had
hidden: **a field drawn last is a field the next one shifts**.*

## 1. The run, the target and the training

`e495`'s own command with `--loop-reward` added, read against the same pass without it.

| the arm | the rewarded run's accuracy diagonal | the unpaid run's | learned vectors | final_per_task vectors |
|---|---|---|---|---|
| `naive` | **0.8299** | 0.8299 | **identical** | **identical** |
| `ewc-block` | **0.8139** | 0.8139 | **identical** | **identical** |
| `replay` | **0.8267** | 0.8267 | **identical** | **identical** |

| the arm | the reward diagonal | the reward last row | the contrast | sigma |
|---|---|---|---|---|
| `naive` | -6.0542 | -6.0646 | +0.0104 | **+0.27** |
| `ewc-block` | -6.0070 | -5.9947 | -0.0123 | **-0.31** |
| `replay` | -6.1017 | -6.1564 | +0.0547 | **+1.78** |

and the target's step, from the environment's own arithmetic, with the target's own response to the episode's other
symbols beside it:

| the placement | the label's step | the target's step | the target's move when the other symbols are redrawn | the world's final state's move |
|---|---|---|---|---|
| **label first** | 0 | **1** | **0.0000e+00** | 0.0046 |
| label last | 6 | **7** | **9.1609** | 0.7194 |

| claim | measured | verdict |
|---|---|---|
| OB1 the payout is the one flag moved | **0** config fields differing past the inert rule with `loop_reward` the one moved, the draw with `['reward_map_sha1']` added and **0** differing, **20** replicates | **MET** |
| OB2 the target is the cue the label names | the target's step is **1** with the label at **0** and **7** with it at **6**; redrawing the episode's other symbols moves the label-first target by **0.0000e+00** and its final state by **0.0046**, and the label-last target by **9.1609** | **MET** |
| OB3 the payout does not touch the training | the two runs agree on all three arms' `learned` and `final_per_task` vectors, **record for record** | **MET** |
| OB4 the world pays in the pass | the contrasts are **+0.0104**, **-0.0123** and **+0.0547** at **+0.27**, **-0.31** and **+1.78** sigma | **FALSIFIER FIRED** |

## 2. What it says

**And the target is the cue the label names, under either placement.** The step it is read at is the label's cue's
step plus one -- **1** with the label at the pass's first trial and **7** with it at the last -- and driven by hand
with the payout on, redrawing the episode's other symbols leaves the label-first target **exactly** unchanged
(**0.0000e+00**) while the world's final state moves (**0.0046**), where the label-last target moves by **9.1609**
because those symbols are in its past. **So the environment pays against the label** and the runner's refusal of the
pair is gone: the target rule is the label's, and a single-trial environment is the one it always was.

**And the payout does not touch the training, in the episode as at one trial.** The two runs agree on every
replicate's `learned` and `final_per_task` vector, **record for record**, on all three arms -- which is `e487`'s third
claim replicated at the episodic pass, and what makes OB4's currency the same pass's. **So the rewarded run's body is
the unpaid run's body** and the payout is a meter on it, as it has been since `e483`.

**And the currency inside the pass is flat.** No arm's reward diagonal resolves against its last row -- **+0.0104**,
**-0.0123** and **+0.0547** at **+0.27**, **-0.31** and **+1.78** sigma -- where the corpus's own one-trial world-0
run resolved the diagonal **below** its last row at **-4.91** to **-3.46** sigma (`e485`) and where the world-1 run
resolved nothing either (`e487`). **So the pass joins the second world in not carrying `e485`'s shape**, and what a
paid episodic pass would have to be measured against is a currency whose own level and shape are the world's.

**And the unit found a defect the corpus's fields had hidden: a field drawn last is a field the next one shifts.**
The environment drew the payout's map last and the boundary channel's neurons after it, so turning `--loop-reward`
**on** moved the boundary channel's draw -- OB1's falsifier fired on exactly that before the fix, and OB3's did with
it, since a different boundary channel is a different input. **The fix is the order**: the boundary's population is
drawn before the payout's map, so the payout's flag moves no field but its own. **And the corpus is unmoved by it**:
`e483` and `e484`'s numbers are the ones their artifacts and rows already carry (`e484`'s five margins re-read
**2.9086**, **1.9474**, **1.0812**, **-0.3169** and **-1.8376**, unchanged), because a run without the boundary draws
the payout from the same state it always did. *The rule the corpus follows is that a new field is drawn last so older
artifacts are bit-identical; what this unit adds is that a field drawn last is still shifted by the **next** field, so
"last" has to be the last **of the fields any claim compares across a flag**.*

## 3. What it cannot do

- **One placement pair and one episode length**: two trials of six steps with the label first and last, with the
  three- and four-trial passes and the interior placements not in it.
- **And one payout**: the environment's own target rule, with the payout a linear read of the cue; a reward on the
  action or sparse in time is a different unit.
- **And the payout is a meter here**: `e481` and `e488` train a policy on it and no unit in this line trains anything
  but the body and the head, so what the pass pays is what the world pays and not what the agent plays for.
- **And the target's step rule is new for the label-first placement**: every earlier artifact is unaffected because
  the flag is off there, and the corpus's own rule was the last cue's -- so an artifact that asks for the payout
  **and** the label-first placement is this unit's and not the corpus's.
- **And one budget, one world and one seed stream**: the card's own setting, so the flat currency is one draw's.
