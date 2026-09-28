# The last row without an artifact: its flag has existed since the commit that created its runner, and its number belongs to another partition

*2026-09-28 23:40. Runs: **one, 3m43s** — the row's own command re-run with the flag it omits,
`python -m experiments.e12_control_spread --min-size 1 --seeds 2 --draws 5 --json-out runs/e12_control_spread.json`.
The read is `experiments/e284_the_last_row_without_an_artifact.py`, writing
`runs/e284_the_last_row_without_an_artifact.json`. Seconds.*

## 1. The table, read as a contract

The paper's §"what is reproducible" table is the page's promise: a claim, the command that produces it, and the
artifact it lands in. Four properties of that promise are mechanical and none of them had been read off it: **the
artifact cells** (every `runs/*.json` path named should be a file), **the commands** (every `python -m` target should
resolve), **the empty cell** (a row naming no artifact should name a runner that cannot write one, and if it can, the
gap is the transcription's), and **the re-run** (for such a row, running its command with the flag it omitted is a
measurement, and the number can be read against the number the row attributes to it).

## 2. The reading

**V1 MET — 39 distinct paths over 54 mentions, 0 not on disk.** Every artifact the paper names exists. **V2 MET — 14
distinct `python -m` targets, 0 failing to import.** Every command the page gives resolves. Both are existence checks
over a population the page itself defines, which is why they are worth stating briefly: the table's cells are backed.

**V3 FALSIFIER FIRED — and the row it fired on is one where an empty artifact cell is the right answer.** Fourteen
rows give a command; twelve name an artifact; two do not, and they are of two different kinds:

| row | its command as transcribed | cell | its runner has `--json-out` |
|---|---|---|---|
| §4.3 draw sds, named rungs | `e12_control_spread --column <rung> --min-size 1 --seeds 3 --draws 5 --json-out …` | `runs/e86_drawsd_*`, `runs/e67_drawsd_*`, `runs/e17*_*drawsd.json` | yes |
| §4.3 control-draw spread, first measurement | `e12_control_spread --min-size 1 --seeds 2 --draws 5` | *(none)* → the artifact below | yes |
| §6 | `clfly.lgcl.repro`, `pytest -q` | — | **no** |

The first row's command declares the flag and leaves its path a placeholder (the class `e182` documents), and its
artifact cell names a *family* as a glob rather than a file — so it reads as artifact-free to a path search and is
not one. The third is the test suite, where an empty cell is the correct answer and no artifact should exist. The
falsifier fired on the third, so **the claim as registered was too broad**: "every artifact-free row invokes a runner
that carries the flag" is false for the test-suite row and *ought* to be false. The row it would have been useful for
is the second, and the second is the one it was written for.

## 3. The row, filled — and the number that came back

The second row's command passed no `--json-out` and said so ("**no `--json-out`, so this command leaves no artifact**").
`git log -S'"--json-out"'` on the runner puts the flag in the **commit that created it** (`48ac23e`, 2026-09-22 15:04),
so the flag was never missing from the runner — only from the row's transcription. Re-running the row's own command
with it, **3m43s**:

```
biological partition (cell_type, min_size 1): 812 groups, constrained 0.9793
across-draw sd    0.00005   <- the component a single-draw sem omits
delta (biological minus matched-random): +0.00022
```

**V4 MET — and it fires in the direction that repairs the row rather than the claim.** The artifact's draw-to-draw sd
is **4.69e-5**, which is inside the band §4.3 states for this partition in its own words — "**~4e-5 to 9e-5 for
near-diagonal ones**", measured by this same runner on "812-group and 8-group partitions" — and **23× below the
1.1e-3** the row attributes to the command. §4.3 gives 1.1e-3 to *coarse* partitions (2 to 10 groups); this command
defaults to `--circuit-size 800` and produces **812 groups**. So the row's number and the row's command were about two
different partitions, and no flag in the transcribed command reaches the one the number belongs to.

The paper's row now carries a **Corrected 2026-09-28** clause with the flag, the runtime, the group count, the
measured sd and the two comparisons, and its artifact cell names `runs/e12_control_spread.json`. **The table's rows
that give a command and name no artifact are down to the two whose empty cells are correct.** This is the fifth stale
statement the series has found, and the first whose repair is a command rather than a sentence.

## 4. What it cannot do

**An artifact that exists is not an artifact of the right configuration** — V1 checks that the evidence is present and
not that it is what the row's claim needs, which is `e182`'s comparison and is made against another table. **V2
imports the module and does not execute the row's command**, so a target that resolves can still fail on its flags.
**The flag search is a source scan** for `add_argument("--json-out")` in the module's own text, so a runner that builds
its parser elsewhere reads as having no flag. **A row whose artifact cell holds prose rather than a path counts as
naming no artifact**, which is what puts the glob row in the table above. **V4 reads one draw sd from five draws**,
whose own sampling error is tens of per cent: it separates a band from a factor of twenty and cannot order the band's
members, so it does not re-measure §4.3's 4e-5 to 9e-5 range, it lands inside it. **"Near-diagonal" is §4.3's word**
and this unit takes the artifact's own group count as what puts a partition there rather than defining the term. And
**a re-run is not a reproduction of the original**: the original measurement that the row says produced 1.1e-3 is not
recoverable, so what this unit shows is that the row's *command* does not produce the row's *number*, not which of the
two the original run was.
