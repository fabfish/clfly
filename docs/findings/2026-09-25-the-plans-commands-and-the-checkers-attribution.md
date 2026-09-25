# Nine flags the plan appeared to contradict, and all nine were the checker's — four attribution rules, then 24 checks and none

**Date:** 2026-09-25
**Read of:** `docs/research_plan.md` — all 138 table rows it held when this was run (140 once the two rows below
are registered), and the `config` of the artifacts those rows name under `runs/` (316 files), with the flag table
taken from `experiments/e172_parser_registry.py`'s syntax-derived registry.
**Instrument:** `experiments/e182_command_prose_audit.py` (and `--readout-census`, its second question), tested in
`tests/test_e182_command_prose_audit.py`.
**Retracts** an inline suspicion from the fire before this one: that some runner **rewrites** a `config` value before
writing it (`readout_size: 1307` where the plan said "read-out 0").

---

## The question, and the hand pass that raised it

`e163` derives a command **from** a `config`; `e172` decides which runner could have written one. This asks the
opposite: the plan states a command **in prose**, the artifact beside it carries the `config` the run actually used,
and the two can disagree. The failure that would catch is the one this project is most exposed to — a row whose
command text was edited after the run, or copied from another row, while its numbers stayed put.

The plan already contains one hand run of this check, in L1046: *"its command was VERIFIED against `e79`'s own
config rather than written from memory … the derived command differs from the launched one in exactly three fields,
`--circuit-size` (1500 -> 300), `--support` (150 -> 30) and `--json-out`."* So the check is wanted; it had simply
never been generalised or run over the other 137 rows.

**The first pass was done by hand, in a shell, and produced 24 checks and 9 mismatches.** All nine were the checker's
own error. That is this finding's first result, and the reason the script exists: **nine false positives in 24 checks
is not a table with nine defects, it is a checker whose attribution was wrong, and every one of the nine came from
comparing a flag with an artifact the row mentions for some other purpose.**

| # | line | the apparent contradiction | what it actually was |
|---|---|---|---|
| 1 | 989 | `--control-draws` "says K", config has `3` | `K` is a placeholder, not a value |
| 2 | 1007 | `--extra-bases` says `--seeds`, config has `True` | a `store_true` flag paired with the next flag as its value |
| 3 | 1074 | `--readout-size` says `0`, config has `1307` | the flag fragment belonged to a different artifact the row cites — **and `0` and `1307` are the same run** (see the census below) |
| 4 | 1078 | `--methods` says `naive,ewc`, config has `naive`; `--fisher-batches` says `32`, config has `8` | the command belongs to **`e133`**, the row's own label (`runs/e133_r32_naive_ewc_40reps.json` holds `methods: naive,ewc`, `fisher_batches: 32`); `e116_*` is cited in the same row for a different purpose |
| 5 | 1078 | `--lam` says `3e-3`, config has `0.003` | numerical equivalence: the same number written two ways |
| 6 | 1092 | `--input-overlap` says `1.0`, config has `0.0` | the artifact that holds the command is `e148_*` (a registration); `e140_*` is a *baseline* the row contrasts against |

Five rows, nine flags, no defect. The correction was not to weaken the check but to make **attribution** the subject.

## The conversion, with the numbers at each step

Every step below was a change made *because* the step above it produced a false positive against the real table.

| version | what changed | checks | mismatches |
|---|---|---|---|
| hand pass (inline, not saved) | flags from the whole row × every artifact the row mentions | 24 | 9 |
| v1 | tokenise the first cell; attribute to the artifact that cell names | **0** | 0 |
| v2 | fix v1's tokeniser | 25 | 5 |
| v3 | a label must identify exactly one file; a comparison clause names a baseline | 27 | 4 |
| v4 | the command ends where the cell first names its artifact; a list-valued config agrees with a member | **24** | **0** |

(The buckets move in both directions between versions — a rule that admits a row to the checkable set also removes
flags from it — so these are the script's own outputs at each step, not a decomposition of the decrease.)

**v1's row is the most instructive one in this table.** It reported zero mismatches and zero checks, and its skip
ledger read `136 rows state no flag` — *a clean table*. The cause: it matched a Markdown code span as one token
(`` `[^`]+` ``), and **this table writes every command inside a code span**, so the command was consumed whole and no
flag was ever seen. A checker that reports "no findings" because it has stopped looking is worse than no checker; it
is the same failure `e127`'s rule 22 records, reached from a different direction.

v3 → v4 is the only step where the count of checks went *down*, and the four mismatches it removed all came from
**one row**: L1046, the row that verifies its own command. That row states nine flags and then *quotes* the three
fields in which the derived command differs; v3 read the quotation as a second command and reported the row's
`--circuit-size` as both `300` and `1500`, its `--support` as both `30` and `150`, and `--topologies real` as a
mismatch against the list `["real"]`.

## The four attribution rules, each one derived from a false positive it produced

1. **A code span is not a token.** Backticks are dropped before tokenising. (v1's zero.)
2. **A runner's file name is not a label.** `e5_anisotropy_axis.py` begins with `e5`, and the first version resolved
   that to the artifact `e5_anisotropy.json` and reported the row's `--seeds 12` against that artifact's `3`.
3. **A label with zero files is not a reference, and a label with several files is an unresolvable one.** Zero-file
   labels are how this table names a *runner* (`e3`, `e8`); conflating them with ambiguity is what made `e182`'s own
   unit tests report a runner-naming cell as unattributable. A label with several files is genuine ambiguity:
   `e140` is **four** artifacts, and keeping one of them is what made the hand pass compare a five-method command
   with a one-method config.
4. **The command ends where the cell first names its artifact.** This is the table's own convention — a registering
   row reads "its artifact to be written as `e148_….json` under `runs/`". It is also the rule that has to be stated
   as a *scope* rather than a guarantee: the checker therefore does not read 250 tokens of prose, and exactly **1
   flag** in that prose (`e163 --command`, mentioned on L1035 as a mode rather than as a command) goes unchecked.

Plus three smaller ones, each bought with a misreport: a clause introduced by *against* / *vs* names a **baseline**
(L1097's `against e133's overlap-0.0 naive` is the contrast the row exists to make, not a claim about the command's
own config); `3e-3` **is** `0.003`; and a list-valued config (`--topologies real` runs `["real"]`) agrees with a
member of it — said out loud in the verdict, because a silent pass there would hide a cell naming one member of a
family the run actually swept.

## What the check covers, and what it cannot (the denominator)

**The table held 138 rows when this was run** (140 after these two registrations), of which 28 name an artifact by a
`runs/` reference (all 28 present): **24 flag checks over 6 rows, 0 disagreements.** Every row is accounted for — 6
attributed, 132 not, by these reasons —

| why the row was not attributed | rows |
|---|---|
| states no flag at all | 82 |
| states flags but names no artifact it can resolve (usually names its *runner*; its artifact is in the status column) | 43 |
| names more than one artifact | 3 |
| the named artifact carries no `config` | 2 |
| names a label that identifies several files | 1 |
| names an artifact only as a comparison partner | 1 |

and, *inside* the six attributed rows, 2 flags were not compared because they are `store_true` flags with no value
after them. Those 2 are flags, not rows — the first version kept one counter for both and its denominator was a sum
of rows and flags, a number that looks like a scope and is not one.

**The licensed sentence is therefore narrow, and it is worth writing exactly:** *wherever this checker can attribute a
row's stated command to exactly one artifact, the stated flags and the artifact's `config` agree — 24 flags, 6 rows,
0 disagreements.* It is **not** "the plan's commands are verified". **50 of the 56 rows that state a command are not
attributed at all** (43 of them because the cell names no artifact it can resolve), and the checker says so instead
of guessing — guessing is what produced all nine of the first pass's findings.

## The second question: what `--readout-size` means, and the retraction it closes

`--readout-census` over the 144 artifacts whose `config` carries a `readout_size`:

| how the read-out is written | artifacts |
|---|---|
| a literal below the circuit's achieved neuron count — a real draw | 111 |
| `0` | 27 |
| the achieved count itself (`1307`) | 2 |
| a literal, with no achieved count recorded to compare it to | 4 |

- **`0`, `1307` and the flag's absence are three spellings of the same run: the whole state.** `--readout-size` is
  applied only when it is non-zero *and* strictly below the circuit's neuron count, so all three take the same
  branch. All 29 whole-state artifacts in the corpus are at `n = 1307`.
- **The artifact's own `readout` block agrees with that rule in every artifact that carries one — 0 contradictions
  of the 60 that do.** (Only 60 of the 144 carry the block; it was added to the runner late, and a claim of "0
  disagreements" over all 144 would be a claim about 84 artifacts that cannot disagree because they say nothing —
  the first version of this census made exactly that over-claim and the denominator is now printed beside the
  zero.) So the suspicion that a runner rewrites a `config` value before writing it is **retracted**: `config` is
  `vars(args)`, `readout_size: 1307` was passed on the command line literally, and `0` in the row's prose is simply
  the other spelling.
- **Where `1307` comes from, and the one fragility that is real.** `--circuit-size` is a **soft** budget: the
  extractor keeps every cell type, so `--circuit-size 800` *achieves* `mb+cx+al@n1307`. The achieved count is
  recorded in the `circuit` name and **nowhere else** — not in the `config`, which carries the budget. So the
  literal `--readout-size 1307` means "the whole state" at circuit 800 and would mean "a draw of 1307 neurons" at any
  circuit achieving more than 1307. `e9_ladder_d1874.json` (`--circuit-size 1500`) reaches d = 1874, so this is not
  hypothetical, and 4 of the 144 artifacts record no achieved count at all, which makes the meaning of their
  `readout_size` unrecoverable from the artifact.

**Falsifiers, stated before anyone looks for them.** The census claim dies if any artifact's own `readout` block
disagrees with the run-time rule (currently 0 of the 60 that carry a block, and the test suite writes such an artifact
to prove the check fires). The agreement claim dies if any row's stated flag differs from its attributed artifact's
`config` under the four rules (currently 0 of 24) — or if a fifth attribution convention exists that this script
reads as agreement or as unattributable, which is the far more likely failure, and is why the skip ledger is printed
beside the count rather than reported as a clean table.

## Reproduce

```
uv run python -m experiments.e182_command_prose_audit                    # the gate: 24 checks, 0 mismatches, exit 0
uv run python -m experiments.e182_command_prose_audit --readout-census    # plus the read-out census
uv run pytest tests/test_e182_command_prose_audit.py -q
```
