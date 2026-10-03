# The position effect: the order the corpus never varied would have moved the numbers by four points

*2026-10-01 08:31. Runs: **none new** — `experiments/e310_the_position_effect.py` reads the diagonal of every
three-task arm's retention matrix by position, writing `runs/e310_the_position_effect.json`. Seconds.*

## 1. What `e302`'s M4 could not say

`e302` read the block's promise of **"fixed task orders and seeds, so numbers are comparable across methods"** and
registered M4: every artifact that records a named task list records its suite's own naming order, and **no
permutation of any suite has ever been run** — so the promise holds *trivially*, because the order is a variable with
one value. What it could not say is whether the order **would** move the numbers.

It can be said without a new run. For every three-task arm the diagonal of `R` is the level each task reached when it
was learned, so the task's **position in the sequence** can be read against that level.

## 2. The reading

| position | mean level reached |
|---|---|
| **learned first** | **0.9605** |
| learned second | 0.9168 |
| learned third | 0.9345 |

over **5581 arm-replicates**. The ordering is **first > last > middle**, and the first-to-middle gap is **0.0437** —
four points of accuracy.

**W1 MET** — the position predicts the level, ordered first > last > middle, with a gap far above the 0.02 the claim
asked for. **W2 MET** — paired *within* the arm, the first position beats the middle in **69%** of the replicates, the
last beats the middle in **54%**, and the first beats the last in **60%**, so the effect is not a pooled artefact.
**W3 MET** — of the **99 artifacts** carrying ten or more three-task arms, **89 (90%)** show the first above the
middle, so it is a property of the configurations rather than of the corpus's mixture.

## 3. And it is not one suite's task identities

| family | arms | first | last | middle | first above middle |
|---|---|---|---|---|---|
| **assembly** (`odour_identity`, `heading`, `odour_input`) | 866 | 0.9537 | 0.9142 | 0.8507 | **78%** |
| **overlap** (`ov*_t0..t2`, drawn per artifact) | 4715 | 0.9617 | 0.9382 | 0.9289 | **67%** |

**W4 MET.** The two families differ in the thing that would explain the effect away: the assembly suite's three tasks
are **fixed modalities in one order for every run**, while the overlap suites' three tasks are **drawn per artifact**.
The same ordering appears in both, and more sharply in the family whose task identities never change — so what
predicts the level is where the task sits and not which task it is.

The battery's answer, then, is that the order promise is **not** vacuous: the position moves the level by more than
four points on average, and 90% of the configurations show it. `e302`'s M4 stands — the corpus has never varied the
order — and this measures what varying it would cost, which is the number a benchmark needs before it decides the
order is fixed **on purpose**.

## 4. What it cannot do

**The diagonal is measured right after the task was learned**, so a task that was hard at the time and recovered later
is scored by its position and not by its end state — the `ended` row and the decomposition are `e304`'s subject.
**The two families are not a controlled comparison**: their configurations differ in circuit size, read-out width,
methods and epoch, so W4 is an argument that the ordering survives a change of suite and not that the families have
the same effect size. **The assembly family cannot separate "first" from "`odour_identity`" on its own**, which is
exactly why W4 needs both families and not either. **And the arms are not independent** — the same configuration
recurs across runs, so 69%, 90% and 5581 are counts of entries and carry no interval.

## RE-READ 2026-10-02: two of the four claims fire when eighty `loop_*` arms arrive

`e341` ran the closed loop's two worlds at **forty replicates** each, which put **80 new arms** into the corpus --
and two of this unit's four claims moved under them.

**W3 FIRED**: the share of artifacts that are powered and show the first above the middle is now **104 of 131,
0.794**, six thousandths under the unit's own bar of 0.80. That is a share on a corpus whose arm count grows, and
the bar is the unit's, so the verdict is reported as FIRED rather than re-based.

**W4 FIRED, and this one is not a rounding artefact**: the claim is that the effect holds **per family**, and the
**assembly** family's means are now **[0.8750, 0.8215, 0.8759]** -- its last rung has overtaken its middle, while its
first still beats the middle by 0.054. So the two ordering statements this unit makes are not equally robust: the
pooled first-above-middle margin survives (W1 and W2 are MET), and the **three-rung order within a family** does not.

What the tests assert now is the structure rather than the two verdicts: the pooled reading is still aligned and its
first-beats-middle margin is above 0.02; each family's first still beats its middle by more than 0.02; W3's verdict is
checked **against the unit's own bar**, so a corpus that pushes the share back over it has to be noticed; and W4's is
reported as it stands. The one thing this RE-READ cannot do is say whether the assembly family's reversal is the
loop family's arithmetic or a real change in the position effect on that family -- the arms arrived and the family's
order moved in the same step, and nothing here separates them.

**RE-READ 2026-10-03: W2'S OWN BAR IS CROSSED AND TWO MARGINS ARE NOW DIRECTIONS.** The live test asserted that
the first position beats the middle in at least sixty per cent of the arm-replicates, which is `e310`'s own
registration for W2; on **7346 arms** the share is **0.5996**, six thousandths under it, so **W2 reads FALSIFIER
FIRED** and the assertion is replaced by the direction the unit's argument needs -- the first rung above the middle
in more than half the arms -- with W2's verdict and its measured percentage read off the artifact as `e267` and
`e309` do for their fired claims. The per-family assertion lost its magnitude for the same reason: the assembly
family's first rung is **0.0196** above its middle against the **0.02** this line used to demand, while the pooled
reading still holds 0.02, so what a family is asked for here is the direction and not the margin. W1, W3 and W4 are
unchanged. This is the sixth unit this session to shed a value-pinned threshold, and the sentence is the same each
time: a number that tracks the corpus belongs in the reading and not in the gate.
