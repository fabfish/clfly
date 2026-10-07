# What a fresh clone reports: 157 of the gate's 229 entries read `runs/`, 13 of them report an empty corpus instead of refusing, and the corpus is 947 MiB

*2026-10-07. `experiments/e452_what_a_fresh_clone_reports.py` measures the question the corpus's own thread list has
carried on every fire and no unit has put a number beside: **should `runs/` ship?** `runs/` is gitignored, so a clone has
no artifacts, and every plan row that closed with a refusal path has asserted in prose that the corpus is *usable*
without them rather than *wrong*. No training and no probe: the gate's own entry list is parsed, each entry is resolved
to the module it invokes, that module's source is read for whether it names a path under `runs/` and whether it carries a
refusal, and `runs/` itself is censused. Five claims, registered before this unit's pass over the gate and the corpus.*

## 1. The numbers

| the gate's entries | count | share |
|---|---|---|
| total `run` entries | **230** | |
| the test suite | 1 | |
| Python modules | **229** | |
| naming `runs/` in their source | **157** | **0.686** of the 229 |
| naming it **and** carrying a refusal | **144** | **0.917** of the 157 |
| naming it with **no** refusal | **13** | 0.083 of the 157 |
| naming no `runs/` (source-only) | **72** | 0.314 of the 229 |
| passing `--json-out` | **206** | 0.896 of the 230 |

| `runs/` | value |
|---|---|
| files | **4164** |
| bytes | **947.4 MiB** |
| the largest single file | `e427_most_of_the_aid_needs_a_plastic_bias.json` at **5.0 MiB** |
| files over 5 MiB | **0** |

| claim | measured | verdict |
|---|---|---|
| CY1 the ledger is carried | **230** entries, **229** Python modules, **0** absent | **MET** |
| CY2 and the gate is artifact-dependent | **0.686** of the Python entries | **MET** |
| CY3 and the dependence is not uniform | **72** source-only entries | **MET** |
| CY4 and the refusal convention covers most of them | **0.917** of the 157 | **MET** |
| CY5 and the corpus does not fit a repository | **947.4 MiB** over **4164** files | **MET** |

## 2. What the numbers say

**The corpus is two thirds artifact-dependent and one third sources-only, and the split is the design.** **157** of the
gate's **229** Python entries are modules whose source names a path under `runs/`; the other **72** read the corpus's own
text -- the plan, the findings, the paper, the gate itself. So a clone without `runs/` is not a clone without a
benchmark: it is a clone whose **31.4%** of entries run and whose **68.6%** decline. That is the number the thread has
been missing, and it is a better fact than either "the artifacts are needed" or "they are not": which third of the
corpus is reproducible from the repository alone is now a list.

**And the refusal convention covers 0.917 of the dependent entries -- the 13 that it does not are the censuses.** The
dependent modules that carry a refusal number **144**, and the **13** that do not are
`e97`, `e105`, `e127`, `e163`, `e182`, `e184`, `e185`, `e190`, `e192`, `e198`, `e201`, `e205` and `e230`: the units that
**count** the corpus -- findings, tables, citations, draws, durations, ranks. They carry no registered claim to refuse on,
so on a clone they would run to completion against an empty `runs/` and report **counts of nothing** -- a corpus of zero
artifacts, zero draws, zero citations -- in the same words a corpus of a thousand would produce. That is the one failure
mode a clone must not have, and it is a defect rather than a decision: it is fixable in thirteen modules without anything
being shipped.

**And what blocks shipping is the total and the file count, not any one file.** **947.4 MiB** over **4164** files, with
**no file over 5 MiB** -- so nothing crosses a hosting service's per-file limit and the obstacle is a clone's transfer
and a working tree's size. The corpus grows by roughly **1 MiB per closed-loop roll** (the six this line has driven since
`e438` are 1.1 to 1.7 MiB each) and by **five files apiece**, so the number in this finding is a bound with a slope
attached rather than a level.

**And 206 of the 230 entries write.** Nearly nine tenths of the gate passes `--json-out`, most of them into `runs/`, so a
clone that ran the gate would create files under a directory that is gitignored -- the corpus's own working form is
*artifacts are written locally and never committed*, and the thread's question is whether that form should change. This
unit does not answer it: **it supplies the number the answer needs and nothing else**, and the three readings above are
what the answer turns on.

## 3. What it cannot settle

- **A static reading**: whether a module names `runs/` is read from its source and not from running it, so a module that
  builds its artifact path from a constant the source does not spell would be misclassified, and a refusal spelled
  otherwise than `REFUSED` counts as absent -- which is exactly what the **13** are read as.
- **And no clone is simulated**: the gate is not re-run with `runs/` hidden, so the **0.686** is a share of entries and
  not a measurement of what each would do, and the refusal's *correctness* is not in it.
- **And the corpus grows**: entries, files and bytes all move with it, so every bar here is a bound and the shares are
  the statements; **947.4 MiB** is one day's reading of a corpus that has grown by **271** to **630**-odd arms in this
  line's own hands.
- **And it is not a decision**: whether `runs/` should ship, and what a clone should do instead, is the user's to make,
  and this unit's whole content is that the number is **947.4 MiB over 4164 files** with **13** modules that would
  answer nothing rather than refuse.
