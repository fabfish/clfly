# Can a trained body beat the interface? No: the cue-source world at the read step is at chance, and it agrees with the frozen probe to 0.0252

*2026-10-02. One runner invocation -- `e362`'s exact flags plus `--loop-drive-from-cue`, `--methods naive,replay`,
`--repeats 20` -- into `runs/e364_earned_label_drivefromcue_20reps.json`, paired against `e362`'s action-source
late-cue run and against `e363`'s frozen cell for the same configuration. Nineteen minutes. Read by
`experiments/e364_can_training_beat_the_interface.py`.*

## 1. The strongest form of a structural claim

`e363` told apart the two causes `e362` had named together, in six frozen rolls: at the step the world read-out reads,
**both** drive sources carry nothing about the cue (**0.2578, exactly chance**), so the timing is the hard limit;
one step earlier the sources separate sharply (**0.8555** for a world whose drive reads the cue's own neurons against
**0.2578** for one reading the action population). And it closed on what was missing: *"a frozen body ... the trained
versions of five of the six cells are not run."*

**A frozen probe reading chance is not a proof that the information is absent -- a trained body might find it.** So
this unit trains the decisive cell: a world whose drive reads the cue population, with the cue delivered at the read
step, and a body allowed to do whatever it likes.

## 2. The answer

| drive reads | arm | final accuracy | diagonal | `mean_forgetting` | paired channel | sigma |
|---|---|---|---|---|---|---|
| the action population | `naive` | 0.2514 | 0.2361 | -0.0229 | +0.0010 | 0.16 |
| the action population | `replay` | 0.2483 | 0.2375 | -0.0161 | -0.0028 | 0.31 |
| **the cue population** | `naive` | 0.2531 | **0.2326** | -0.0307 | **+0.0083** | 0.83 |
| **the cue population** | `replay` | 0.2517 | 0.2410 | -0.0161 | **+0.0059** | 0.49 |

chance 0.2500. **T2 MET**: the cue-source world's `naive` diagonal is **0.2326 -- 0.0174 *below* chance**. Training
cannot beat the interface. **T3 MET**: and nothing is earned there -- the paired channel readings are **+0.0083 at
0.83 sigma** and **+0.0059 at 0.49 sigma**, inside 0.05 of zero. **T4 MET**: the trained reading sits **0.0252** from
the frozen probe's cell (`0.2578`) for the same configuration, so the body and the probe agree that there is nothing
there. **T5 MET**: the buffer is inert, `replay` and `naive` differing by 0.0146 of forgetting.

**T1 FALSIFIER FIRED, and it names a third difference beyond the manipulation.** The two runs agree on the cue and
feedback fingerprints, the world, the basis, the tasks, widths, sizes, replicates, seeds and the cue's step -- and
they differ in `drive_from_cue` and in the **drive map**, whose width follows the population it reads. That last
difference has a consequence the claim did not anticipate: the wider map consumes more of the environment's draw, so
**the coupling matrix lands differently too** (`5326f4a0edb4` against `1b7d09f2b469`). Three differences where the
registration allowed one: the source, its map's width, and a coupling matrix that is a different draw of the same
kind -- both scaled so their largest singular value is one, so the chance result stands, but the pairing is not one
manipulation apart and is reported as fired rather than excused.

## 3. What it settles

**The structural reading survives its strongest test.** A body that is free to do anything at all, trained for five
hundred steps on twenty seed streams, does not learn a task whose cue arrives at the step the world is read -- in the
*same* world where that body learns the same task at 0.7691 when the cue arrives at step 0 (`e359`). **So the
interface is a hard constraint and not an optimisation problem**, which is what `e363`'s frozen grid argued and this
confirms on a body.

**And the two late-cue runs are the same failure.** The action-source and cue-source worlds at the read step read
0.2361 and 0.2326, both below chance, with channel readings of +0.0010 and +0.0083. The interface knob `e363` found
-- which is worth **0.8555 against 0.2578** one step earlier -- is worth nothing at zero margin, exactly as its
frozen grid said.

## 4. What it cannot do

*One cell of `e363`'s six*: the trained versions of the other five are unrun, and the one that matters is `cue@10`,
where the frozen probe reads **0.8555** and a trained body would be the test of the interface knob as a *working*
task -- a positive result this unit does not have. *One world and one coupling*: eight dimensions at `leak = 0.35`.
*And the pairing is not clean*: beyond the drive's source, the two runs differ in the drive map's width and in the
coupling draw, so T1 fired; what the contrast establishes is about the **read-out's reach** and not about a single
manipulated field. *Chance is a floor and not a proof*, which is exactly why T4 sits the trained reading beside the
frozen one: two instruments, one at chance with the other.
