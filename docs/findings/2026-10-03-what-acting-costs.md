# What acting costs: 0.0708 at 7.13 sigma, three and a half times what two files could show, and the buffer helps by the same amount either way

*2026-10-03. `experiments/e372_what_acting_costs.py` trains the same game at the same step with the world's drive
pointed at the **cue population** instead of the agent's own action -- `e371`'s exact flags plus
`--loop-drive-from-cue` -- twenty replicates, two arms, three tasks in sequence, paired over the same seeds.
Nineteen minutes for the run; the reader is `runs/e372_what_acting_costs.json`. Five claims, registered before the
run's reading was opened.*

## 1. The two sources side by side

| source | arm | final | diagonal | forgetting | paired channel |
|---|---|---|---|---|---|
| **cue** | naive | 0.5670 | **0.8399** | 0.4094 | +0.3115 (18.74 sigma) |
| **cue** | replay | 0.7160 | 0.8028 | 0.1302 | +0.4580 (34.77 sigma) |
| **action** | naive | 0.5191 | **0.7691** | 0.3750 | +0.2642 (18.08 sigma) |
| **action** | replay | 0.6785 | 0.7389 | 0.0906 | +0.4247 (31.65 sigma) |

chance 0.2500. The frozen cells at this step: **cue 0.7891** (spread 0.2156), **action 0.6602** (spread 0.2029).

| claim | measured | verdict |
|---|---|---|
| R1 one configuration except where the drive is read | shared fields all equal, the source's own seven moving, couplings `1b7d09f2b469` and `5326f4a0edb4` | **MET** |
| R2 the channel is live for the cue source too | `e363`'s `cue@0` is **+0.5391** over chance | **MET** |
| R3 the handed-over game is learnable too | cue-source `naive` diagonal **+0.5899** over chance | **MET** |
| R4 the answer is earned there | naive **+0.3115** at **18.74 sigma**, replay **+0.4580** at **34.77 sigma** | **MET** |
| R5 acting costs nothing measurable, within 0.05 | **+0.0708** on a sem of **0.0099**, **7.13 sigma** paired | **NULL** |

**R5 is the claim the unit exists for and it did not resolve either way, which is itself the reading.** The claim was
that the two sources are the same task to within 0.05, and the falsifier was 0.10; the measurement is **0.0708**, in
the registered null band between them. What that band means has to be said plainly: **0.05 was refuted** -- the cost
is not nothing, and at **7.13 sigma** paired over twenty replicates it is not noise -- while **0.10 was not reached**,
so "building the channel is a real cost" does not fire either. **The cost is small, positive and resolved**, and the
bars this unit registered bracketed it rather than deciding it.

**And it is three and a half times what `e371` could show.** That unit reported **0.0200** from comparing the
trained action-source body with the *frozen* cue-source probe, and said it was the artifact of comparing two files.
It was: the paired measurement puts the same difference at **0.0708**, and the direction is the same. A comparison
across artifacts understated the cost by a factor of **3.5**.

**Training closes most of the gap the channels start with.** Frozen, the two sources are **0.1289** apart (0.7891
against 0.6602); trained, they are **0.0708** apart, so the twenty replicates of training recover **0.0581** of that
**0.1289**, or **45%** of the price of acting. Reported and not claimed: it is arithmetic on two pairs of registered
readings and had no registered bar.

## 2. The number the corpus now has twice

**Both trained bodies beat their own source's frozen probe.** Cue: **0.8399** against **0.7891**, **+0.0509**.
Action: **0.7691** against **0.6602**, **+0.1089**. `e371` was the first cell in this line where that happened and it
was one number; this unit shows it is not a property of the action source -- the source the world listens to
**directly**, where a probe has the easiest possible job, is also beaten, by **0.0509**. Both are reported, neither
had a registered bar, and what they say together is that on this task a trained body is not a
worse instrument than a least-squares decoder on a frozen one, which is the opposite of what `e364` and `e365` found
at the late steps.

**And the buffer helps by nearly the same amount in both.** `replay` minus `naive` on forgetting: cue source
**-0.2792** (0.1302 against 0.4094), action source **-0.2844** (0.0906 against 0.3750). The two differ by **0.0052**,
which is inside what twenty replicates can separate, so **what the buffer is worth here does not depend on whether
the agent has to act**. Reported and not claimed, and it is the first time this line has had two substrates to say
anything about a method's transfer in.

## 3. What it means

**The game is playable from both sides and the side matters by a measurable, small amount.** A closed-loop task on
this world where the answer is carried by the cue population costs **0.0708** less than the same task where the agent
must build the channel with its own action -- 7.13 sigma, so the direction is settled, and **0.0708** in absolute
terms, so a claim that the two are "the same task" is wrong in a way that matters more to a paper than to a
benchmark. `e363`'s frozen grid said the two channels differ by 0.1289; training takes 45% of that
back.

**And this is the first unit in the line where a method's behaviour could be compared across the two sources at
all**, because it is the first time both sources have been trained at the same step on the same seeds. The buffer
result replicates to **0.0052**, and the paired channel readings order the same way in both (**replay** higher than
**naive** by 0.1465 in the cue source and 0.1605 in the action source), so the two substrates agree about the arm and
not only about the level.

## 4. What it cannot do

*One step, and the widest one*: this is `cue@0`, where `e369`'s window is widest for both sources; at the late steps
the two sources are not the same task at all, because the action source's world is at rest and the cue source's is
not, so nothing here says what acting costs where the window is narrow -- and the price is exactly the kind of thing
that could grow as the margin shrinks. *Two couplings, by construction*: the drive map's width follows the population
it reads, so the two runs carry different coupling matrices and R1 registers that rather than removing it. *And the
null band is this unit's choice*: 0.05 and 0.10 were registered before the reading and 0.0708 fell between them, so
what is established is that the cost is small and positive at 7.13 sigma, and a unit that wants to say whether a
seventh of an accuracy point is "nothing" has to register what nothing means in the units of the benchmark rather
than in the units of the diagonal.
