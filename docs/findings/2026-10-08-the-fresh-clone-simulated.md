# The fresh clone, simulated: the corpus's absence reaches past the modules that name it

*2026-10-08. `experiments/e464_the_fresh_clone_simulated.py` builds a copy of this repository without its corpus and runs
**every Python entry of `tools/gates.sh`** inside **its own copy of that tree**, one subprocess each with a wall-clock
bound, then classifies what comes back. `e452` answered the same question by reading source and said so: *no clone is
simulated*. Four claims, registered before the sweep; the first two **MET** and the last two **FALSIFIER FIRED**.*

## 1. The sweep

| the copy | |
|---|---|
| files | **1355** |
| fingerprint | `d98f9a945a0f` |
| carries the corpus | no |
| gate modules absent from it | **0** of **242** |

| the sweep | |
|---|---|
| Python entries run, each in its own copy | **242** |
| refused by name (`REFUSED`) | **146** |
| exited non-zero | **195** |
| failed with a traceback | **28** |
| past the 300 s bound | **7** |
| answered (exit zero, no refusal) | **39** |

| claim | measured | verdict |
|---|---|---|
| CL1 the tree is this repository and carries no corpus | **1355** files, no corpus, **242 of 242** modules present | **MET** |
| CL2 and the corpus-dependent entries decline rather than answer | **151** of **170**, **89%** | **MET** |
| CL3 and nothing outside the ledger answers | **8** corpus-dependent entries answer although their source carries a refusal | **FALSIFIER FIRED** |
| CL4 and the entries that do not read the corpus are not disturbed | **52** of **72** of them decline, **72%** | **FALSIFIER FIRED** |

## 2. What the sweep says

**The convention reaches 89% of the entries that need the corpus, and that is the half `e452` was right about.** Of the
**170** entries whose module names a path under `runs/`, **151** decline when it is gone: **146** print `REFUSED` and the
rest exit non-zero or run past the bound. So *a clone is usable rather than wrong* is measured and not asserted, and the
number is high.

**And carrying a refusal in the source is not the same as refusing.** **8** entries name the corpus **and** carry the
word `REFUSED` in their source, and they answered anyway: `e200`, `e268`, `e302`, `e322`, `e369`, `e392`, `e416` and
`e452` itself. Their refusal is conditional -- it fires for the claims whose inputs are missing and not for the report
around them -- so a reader of a clone gets a printed table from them instead of a refusal. **`e452` is the unit that
measured this statically, and the ledger it produced is a ledger of the source and not of the behaviour**: it names 13
modules that carry no refusal, and **11** of those 13 do answer, while these 8 answer *with* one.

**And the absence reaches much further than the source text says.** **52** of the **72** entries whose module names no
path under `runs/` still decline on the empty tree -- **72%**, more than three times the fifth the fourth claim allowed.
**Three of
them fail on a path they never spell**: `e189`, `e191` and `e194` raise `FileNotFoundError: ... runs\e7_interference.json`
because the path comes out of the corpus helper rather than out of a literal, which is exactly the misclassification
`e452` registered as its own blind spot and could not size. So *the corpus-dependent share* is a **lower bound read off
the text** and the behaviour is what the clone meets.

**And 28 of the 242 entries fail with a traceback rather than declining by name, which is the number a person meets.**
They are the arithmetic of an empty corpus: `ZeroDivisionError` in `e252`, `e277`, `e290` and `e299`,
`statistics.StatisticsError: no median for empty data` in `e291` and `fmean requires at least one data point` in
`e310`, `TypeError: unsupported format string passed to NoneType` in `e292`, `e296`, `e304` and `e305`, `KeyError` on
missing blocks in `e285`, `e295`, `e297`, `e309`, `e311`, `e314`, `e315` to `e319` and `e321`, and `e262`'s subscript
of `None`. **A clone does not print a refusal for these; it prints a stack.** And **7** entries ran past the 300 s bound
-- `e349` to `e354`, the readers this line found slow in its own gate, plus this unit, whose copy of itself cannot
finish a sweep of a sweep -- so the bound is doing work rather than padding the count.

**And the classification the corpus's convention implies is not what it does.** The two channels are not the same:
`REFUSED` is what the convention asks for, an exit code is what the gate reads, and **146** entries take the first while
the corpus's exit codes carry the refusal count so a refused claim is usually a non-zero exit as well. What the sweep
separates is the entries that do neither, and CL3 and CL4 are the two ways that happens -- a refusal in the source that
the code path never reaches, and a dependence the source never spells.

## 3. What it cannot do

- **A copy and not a checkout**: the tree under test is the working tree minus the corpus, so it carries uncommitted
  files, its fingerprint moves with the working tree rather than with a commit, and the count is of the tree this unit
  was run in and not of a release.
- **And it has no version-control directory**: `.git` is excluded with the corpus and the environment, so **one** entry
  -- `e283`, whose `git log` raises `CalledProcessError` -- declines for a reason a clone of a repository would not
  have. It is the only gate module that shells out to `git`, and the number is stated rather than subtracted.
- **And the corpus is removed, not empty**: a module could behave differently when `runs/` exists and holds nothing,
  which is what a partial clone looks like, and none of that is measured here.
- **And one environment**: every entry runs with this interpreter on this machine, so an entry that fails for a reason
  unrelated to the corpus is counted as declining; CL4's own firing is what that control was for, and it says the
  control is not a clean one.
- **And a bound is not a diagnosis**: this unit names which entries answer and which crash, and not why.
- **And the sweep leaves its copies behind when it runs past the bound.** The **7** entries that hit the 300 s bound
  hold their working copies for the rest of the run: the kill reaches the interpreter this process started and not
  always the one behind it, and a locked directory on Windows refuses a delete until nothing holds it, so the six
  copies that are still there when the sweep ends are exactly the six entries that ran past the bound. They are
  **removable as soon as the sweep's process exits**, the reader reports them rather than hiding them, and no claim
  here rests on the copies being gone -- but a sweep that leaves seven temp copies is a wart, and the retry window and
  a startup cleanup are what a later unit owes it.
