# The frozen-body control is in no artifact, and two of the paper's tables print cells from different runs

**Date:** 2026-09-23
**Method:** every number in `docs/paper/clfly-v1.md` §4.2's and §4.4's tables, and in the findings they come
from, searched against **every arm of all 204 artifacts** under `runs/` — in three shapes: does an arm contain
this value; do all cells of one row come from one run; is a column's comparator a single number.
**Context:** the per-arm reproducibility audit (`e103`,
`docs/findings/2026-09-23-the-config-keyset-dates-five-artifacts.md`), `e62` (which found the tuned replay
headline had no artifact), and `e8f` (which introduced `--frozen-body`).
**Artifacts:** all 204 artifacts under `runs/` were searched; the ones that carry a cell are
`runs/e8_hardened_basis.json`, `runs/e101_rate_fb32.json`, `runs/e101_rate_fb8.json`,
`runs/e61_replay96_step8.json`, `runs/e84_replay96_taskIL_5reps.json`, `runs/e84_replay96_classIL_5reps.json`
and `runs/e8_hardened.json`.
**Setup:** a corpus search, so the units are artifacts and cells rather than neurons; the underlying runs are
circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, 5 replicates, λ = 0.003, 4 classes, shared head, 32-neuron
read-out, chance 0.25.

---

## 1. The control that justifies the hardened configuration is in no artifact

The paper's §4.2 says *"The limiter was the benchmark, not the methods — and fixing it flipped a result"*, and
the evidence is a `--frozen-body` sweep: **the plastic-minus-frozen accuracy gap and the forgetting both grow as
the read-out narrows** (+0.007 → +0.009 → +0.102 accuracy, against +0.021 → +0.035 → +0.066 forgetting). The
same control is the paper's stated design principle in §7 — *"a benchmark whose frozen-body control matches its
trained accuracy contains no continual-learning problem"* — and it is the reason the hardened configuration
exists at all, which is the substrate of §4.4, §4.7 and §1's headline.

**Measured: not one artifact in this repository contains a frozen-body result.**

| | |
|---|---|
| artifacts whose `config` has `frozen_body: false` | **204 of 204** |
| artifacts whose `config` has `frozen_body: true` | **0** |
| artifacts with a `frozen` arm among their methods | **0** |
| artifacts with a frozen-body result anywhere in the payload | **0** |

The source finding (`docs/findings/2026-09-22-benchmark-measured-its-decoder.md`, `e8f`) declares
`runs/e8_hardened.json`, and that file's three methods are `naive`, `ewc` and `replay`. **Its central table has
six rows — three plastic and three frozen — and none of the frozen three is in the artifact it names.** And
`e8f` is the commit that *added* `--frozen-body` (09-22 10:18), so the runs were made in the fire that
introduced the flag: this is not a capability that was missing, it is a measurement that was printed and not
saved.

**So three of the paper's load-bearing series have no artifact behind them**: the frozen arm's forgetting at each
read-out size, the plastic-minus-frozen gap, and the monotone relationship between them that the design
principle is drawn from. The paper states the principle in the imperative ("*must* use a narrow read-out")
while the diagnostic it rests on has never been applied in this repository as far as the record shows.

## 2. §4.4's nine cells: three are backed, and all three are `replay`

| cell | value | artifact |
|---|---|---|
| task-IL `naive` | +0.101 ± 0.049 | **8 artifacts** (the unhardened benchmark's `naive`) |
| task-IL EWC | +0.128 ± 0.061 | **none** |
| task-IL `replay` | −0.004 ± 0.009 | `e84_replay96_taskIL_5reps.json` |
| class-IL `naive` | +0.059 ± 0.028 | **none** |
| class-IL EWC | +0.063 ± 0.010 | **none** |
| class-IL `replay` | +0.006 ± 0.015 | `e84_replay96_classIL_5reps.json` |
| hardened `naive` | +0.066 ± 0.019 | **none** |
| hardened EWC | +0.010 ± 0.010 | **none** |
| hardened `replay` | −0.010 ± 0.006 | **none** |

**Every cell in the EWC column matches nothing, and the three cells that resolve are the three `replay`
cells.** That has a history rather than a cause: `e62` and `e84` re-measured the *replay* arm in all three
settings, so `replay` acquired artifacts while the `naive` and EWC columns beside it were never re-measured,
because no one was asking about them.

**The two cells the paper's own summary rests on are among the unbacked ones.** *"**Replay beats EWC wherever
both work** — 4.2σ against 2.6σ on the hardened configuration"*: the EWC cell (+0.010 ± 0.010) is **below every
one of the 17 diagonal arms on disk**, whose minimum is +0.0208; the `naive` cell (+0.066 ± 0.019) is matched by
no artifact, where **seven** artifacts of that configuration agree on +0.0729 ± 0.0151. **And the same contrast
is printed twice in this paper with two values** — §1 gives −0.0854 ± 0.0129 = **6.6σ**, computed against
`e61_replay96_step8.json`'s own `naive`; §4.4's table gives −0.076 = **4.2σ**, computed against the phantom one.
The 4.2σ is `e62`'s pre-recreation figure, and the run `e62` launched to replace it was entered in §1 and not in
§4.4's table.

## 3. §4.2's table has two different `naive` baselines inside one column

The hardened-configuration table in §4.2 prints `naive` = +0.066 ± 0.019 and then four contrasts in a column
headed "vs naive". Subtracting each cell from each candidate baseline:

| row | cell | vs printed `naive` (+0.066) | vs the artifact's `naive` (+0.0729) | printed |
|---|---|---|---|---|
| EWC, diagonal | +0.010 | **−0.0560** ✓ | −0.0629 | −0.056 |
| EWC, block — biological | +0.0604 | −0.0056 | **−0.0125** ✓ | −0.013 |
| EWC, block — matched random | +0.0438 | −0.0222 | **−0.0291** ✓ | −0.029 |
| `replay` | −0.010 | **−0.0760** ✓ | −0.0829 | −0.076 |

**Two cells of the column subtract +0.0729 and two subtract +0.066**, so the column is not a column. The two
that use +0.0729 are the two whose cells come from `e8_hardened_basis.json` — the artifact that reproduces on
280 of 280 fields — and the two that use +0.066 are the two whose cells come from runs that do not exist. **The
table's block rows are therefore correct while the table's own `naive` row and its other two rows are not**,
which is why the *internal* inconsistency is the tell: a reader checking a single cell against a single finding
finds nothing wrong.

And the same table's `replay` row prints −0.010 ± 0.006 at 0.968 ± 0.013 accuracy, which matches no artifact;
`e61_replay96_step8.json` gives **−0.0125 ± 0.0039 at 0.9681 ± 0.0078** — same accuracy to three decimals,
different mean, different sem, so the row is a *near* miss rather than a typo, which is what a foreign run of the
same configuration looks like.

## 4. The failure shape is new, and `e103` cannot see it

The project's audits run in two shapes, and both are blind here:

- **number → artifact** (the sentence-level search that found `e8c`'s phantom sweep and this session's phantom
  `+45–63%` range): it finds a *single* unbacked number, and it passes a table as soon as *any* cell resolves.
  §4.4 would have been reported clean, because three of its nine cells resolve.
- **arm → second execution** (`e103`): it compares an arm against the same arm of a re-run of one configuration.
  Here the table compares **an arm against a different arm of a different run**, and no grouping by config can
  see it.

**The shape this failure needs is a cell-level table audit**: for every table in the paper, check (a) each cell
against the corpus, (b) that all cells of one row come from one run, and (c) that a column's comparator is a
single number. All three checks are mechanical, and (b) and (c) are the two that caught these tables. It is
registered as the next infrastructure step rather than done here, because transcribing the tables faithfully is
itself a step that should be done once, in code, and reviewed.

## 5. What is not established

- **The cells are not wrong measurements, they are unlocatable ones.** `2026-09-22-network-line-settled.md`
  declares **no `Artifacts:` line at all**, so whether a run existed and was overwritten, or was never run at
  that configuration, cannot be recovered. `e8c`'s artifact was reused at its own path; that is one mechanism
  and not the only one that produces this signature.
- **No replacement is proposed for the seven unbacked cells.** The honest table says "no artifact", and filling
  them is a new experiment rather than a correction: `--methods naive,ewc` at the two upper settings and
  `--frozen-body` at the three read-out sizes, all of them minutes each, which is the cheapest repair available
  in this project and the reason it should be run rather than argued about.
- **The frozen-body series is not refuted, only unbacked.** The flag exists, the effect sizes printed are
  plausible and monotone, and the paper's principle may well be right — but the record contains no run that
  tests it, and the paper's *imperative* form ("must use a narrow read-out") is stronger than what the record
  supports.
