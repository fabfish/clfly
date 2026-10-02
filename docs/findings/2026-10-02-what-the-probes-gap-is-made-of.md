# What the probe's gap is made of: training is 0.2858 of it, the splits 0.0677, and the suite gives 0.0278 back

*2026-10-02. Nothing trains: `experiments/e366_what_the_probes_gap_is_made_of.py` rolls the frozen network in three
cells of the same world -- one task at 512 examples, one task at 96, and the runner's three tasks at 96 each -- and a
least-squares probe reads the world's final state in each. Three seconds. Writes
`runs/e366_what_the_probes_gap_is_made_of.json`.*

## 1. The confound `e365` named against itself

`e363` read the cue-source world, cue one step from the read-out, at **0.8555** -- one four-symbol task, 512
examples, a frozen network, a probe. `e365` trained the same configuration and its three-task sequential diagonal
came back at **0.5337**, **0.3218 below**, and it wrote the confound into its own finding: *"`e363`'s cell is one
four-symbol task with 512 examples rolled on a frozen network ... `e365`'s diagonal is the mean of three tasks
trained sequentially with 96 examples each, on a body that is being changed. So the gap carries the multi-task
protocol, the smaller training splits and the training itself."*

**This unit prices the first two with nothing trained.**

## 2. The ladder

| cell | tasks | train/test | accuracy |
|---|---|---|---|
| `one512` | 1 | 256 / 256 | **0.8594** |
| `one96` | 1 | 48 / 48 | **0.7917** |
| `three96` | 3 | 48 / 48 | **0.8194** (per task 0.8125, 0.8125, 0.8333) |

chance 0.2500. **T1 MET**: one circuit, one read-out draw, one world of eight dimensions at `leak = 0.35` with the
cue source and the cue at step 10, the cells differing in the example count and the number of tasks.

**T2 MET, and it is the ladder's licence: this instrument reproduces `e363`'s cell.** `one512` reads **0.8594**
against that artifact's recorded **0.8555**, a gap of **+0.0039** -- so the two modules are the same measurement and
the ladder is comparable with both trained units.

**T3 MET**: the runner's **splits cost +0.0677** -- 0.8594 at 256+256 against 0.7917 at 48+48. **T4 MET, and the
sign is the other way: the suite structure gives 0.0278 back.** Three tasks at 48/48 read **0.8194** against one
task's 0.7917, because each task's probe is fitted separately and their readings happen to be at the top of that
cell's range. **So the arrangement is not what e365 lost.**

**And the residue is the training: 0.2858.** The ladder prices two thirds of `e365`'s gap -- **+0.0677** of splits
and **-0.0278** of suite -- and leaves **0.2858** (0.8194 frozen against 0.5337 trained) to the body. **That is 88%
of the 0.3257 gap against `one512`**, reported here and **not claimed**, since attributing it needs the trained
artifact and a claim that reaches across the two units.

## 3. What it means

**`e365`'s headline survives its own confound.** The unit found that a trained body reads less of the cell than a
frozen probe, and named three candidate causes; two of them are now priced at **0.0677** and **-0.0278**, so the
reading "training loses a third of the signal" becomes **"training loses 0.2858 of a 0.3257 gap, and the protocol
accounts for less than a quarter of it"**. The frozen probe's ceiling is a statement about the **training**, not
about the splits or the arrangement.

**And the ladder is a reusable instrument.** Any future unit that compares a frozen reading with a trained one --
which this line does on three cells now -- has to say what its example count and its task arrangement are worth, and
this is the price list for the configuration all of them share.

## 4. What it cannot do

*A frozen probe*: the two prices are the substrate's carrier at two split sizes and two arrangements, so nothing here
says what a trained body would read at 512 examples or on one task. *One world, one coupling and one cue step*: the
cue-source world with the cue at step 10, eight dimensions at `leak = 0.35`, which is exactly `e363`'s and `e365`'s
configuration and no other. *And the ladder is a sequence and not an attribution*: `one512` against `one96` moves the
count, `one96` against `three96` moves the arrangement, and neither moves the other -- so the two prices are read in
order and not as independent effects. *And the residue is quoted, not established*: 0.2858 is a difference between
two artifacts' numbers and not a measured training cost, which is the unit this one points at.
