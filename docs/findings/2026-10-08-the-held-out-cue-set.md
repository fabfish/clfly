# The held-out cue set: the first task the sequence never trained, and training raises its decodability at ten sigma

*2026-10-08. `experiments/e469_the_held_out_cue_set.py` reads the corpus's first **held-out task**. Two rolls of the
card's own configuration with `--loop-holdout`: a fourth cue set is drawn in the same world, the sequence still trains on
three, and at the end the body is frozen and a ridge read-out is fitted on the held-out cue set's train split and scored
on its test split -- once for the trained body and once for a freshly drawn initial one. Four claims, all four **MET**.*

## 1. The probe

| the roll and arm | the initial body | the trained body | the paired change |
|---|---|---|---|
| `bio`, `naive` | 0.6875 | **0.7719** | **+0.0844** at **10.11** sigma |
| `bio`, `ewc-block` | 0.6875 | **0.7625** | **+0.0750** at **9.00** sigma |
| `bio`, `replay` | 0.6875 | **0.7677** | **+0.0802** at **6.84** sigma |
| `rand`, `naive` | 0.6875 | **0.7719** | **+0.0844** at **10.11** sigma |
| `rand`, `ewc-block-rand` | 0.6875 | **0.7667** | **+0.0792** |
| `rand`, `replay` | 0.6875 | **0.7677** | **+0.0802** |

| the held-out cue set, against the baseline's trained reading | paired difference | sigma |
|---|---|---|
| `ewc-block` | **-0.0094** | **-0.86** |
| `ewc-block-rand` | **-0.0052** | **-0.40** |
| `replay` | -0.0042 | -0.34 |

| claim | measured | verdict |
|---|---|---|
| VA1 the two rolls are one configuration with the arm list moved | **51** fields compared, **3** arms each at **20** replicates, the held-out name in neither task list | **MET** |
| VA2 and the probe is recorded for every arm and every replicate | **6** arm-rolls, `loop_holdout`, **96** train and **48** eval each | **MET** |
| VA3 and the trained body reads the unseen cue set better than the initial one | **+0.0844** at **10.11** sigma on both rolls | **MET** |
| VA4 and the anchoring does not move it | **-0.86** and **-0.40** sigma | **MET** |

## 2. What the probe says

**The card's absent list has named a held-out task since its first revision, and this is the first one run.** The card's
`absent` list carries *a reward, a policy, an episode boundary and a held-out task*; the suite has been three cue sets in
one world since `e392`, and the evaluation is per-task decoders -- so a task the sequence never trained on has no
decoder and no unit could read one. With `--loop-holdout` the fourth cue set is drawn, the sequence still trains on
three, and the probe is the fourth's own reading: **the benchmark now has a number for a task outside the sequence.**

**And the trained body reads it better than the initial one, by a lot.** The probe goes from **0.6875** to **0.7719** for
the baseline, a paired **+0.0844** at **10.11** sigma, and every arm and both rolls agree: the six readings run **0.7625**
to **0.7719** against **0.6875** before. **And the initial body's reading is well above chance** -- four classes, so
**0.25** -- which is worth saying plainly: the cue set is a pulse at step 0 read off the circuit's own thirty-two
columns, and a third of the trained reading is there before any training at all, so **what the sequence adds is the
last two thirds of the decodability and not the decodability**.

**And neither anchor moves it.** The cell-class partition's trained reading is **0.0094** below the baseline's at
**0.86** sigma and the matched-random one is **0.0052** below at **0.40**, so on a task neither arm ever saw the basis
is a null as it is on the diagonal of the tasks both arms did see -- which is the card's `basis` clauses asked a fourth
time, on a task outside the sequence, with the same answer. **And the buffer is between them**: `replay`'s trained
reading is **0.0042** below the baseline at **0.34** sigma and **0.0040** above the biological anchor's.

**And the flag's own two rolls are one configuration with the arm list moved, and their shared arms agree to four
decimals.** `bio`'s and `rand`'s `naive` arms both read **0.7719** and both `replay` arms **0.7677**, which is the
check that the flag draws one world for both and that the probe is deterministic given a body.

**And what the flag moves is the world, not the sequence.** `--loop-holdout` draws one more block of cue templates, so a
holdout run is a **different world** from the run beside it and is compared within itself; the three trained tasks'
names, their counts and every other field of the artifact are the ones the ladder's rolls carry, which is why the
sequence's own fields are not read against `e438` here. **So the held-out task is a fourth cue set inside the world the
sequence trained in** -- held out means *not in the sequence* and not *from another world*, which is the weaker of the
two things the phrase can mean and the one this corpus can draw.

## 3. What it cannot do

- **A probe and not a task**: the read-out is fitted on the held-out cue set's **own labels**, so this measures how
  **linearly readable** the task is from the body and not how well the sequence's method would learn it if it were
  trained. A method that is bad at the held-out task would look the same here.
- **And the probe is one ridge**: `1e-2` on a linear head, so a different regulariser or a non-linear one would move the
  level, and nothing here says which one the benchmark should fix.
- **And the held-out cue set is one draw**: a fourth block of cue templates whose seed is the suite's own length, so the
  reading is one draw's and a redraw of the fourth block is not measured.
- **And two rolls**: the card's world with the biological and the matched-random anchor at twenty replicates, so the two
  nulls against the baseline are **0.86** and **0.40** sigma and a redraw could put either above the bar.
- **And the flag costs one artifact field**: `holdout` is written on every replicate of a holdout run and is `null` on
  every run that does not pass the flag, which is what keeps the runs beside it one configuration with their own kind.
