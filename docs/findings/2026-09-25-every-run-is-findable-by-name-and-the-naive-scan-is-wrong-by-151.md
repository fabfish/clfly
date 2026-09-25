# Every run in `runs/` can be found by name — and the scan that reports 156 of them as uncited is wrong by 151

**Date:** 2026-09-25
**Read of:** `runs/` (376 JSON payloads) against the whole document corpus (`docs/**/*.md` plus `README.md`, 263
files, 2.68 M characters), with a robustness pass over `experiments/*.py`.
**Instrument:** `experiments/e184_artifact_citation_census.py`, tested in
`tests/test_e184_artifact_citation_census.py`.

---

## 1. The direction nobody had checked

`e97` asks whether every artifact a **document** cites exists. `e105` asks whether a **table's** numbers are located
by the cells around them. `e127` asks whether a **row's** claim matches the disk — and its check C, added an hour
before this, asks whether a row under-claims what is on disk. **None of them asks the reverse of `e97`:** is every
file in `runs/` named by some document? The plan's own rule 8 is why it matters — *"check that the artifact will
contain the field the question needs"* — and its complement is that a number whose artifact cannot be found by name
cannot be re-checked at all, which is the state `e97` calls *unfalsifiable by construction*.

**The literal version of this check is wrong, and the size of its error is the first result.** Asking "is this file
name a substring of the corpus?" reports **156 of the 376 files as never named**. Two conventions account for **151**
of those, and both are measured classes rather than judgement calls:

| class | files | what it is |
|---|---|---|
| cited by full name | 220 | the ordinary form |
| **cited only through a brace shorthand** | **34** | findings write `runs/e74_drawsd_min{8,16,128}.json` and `runs/e147_r32_frozenbias_ewc_lam3e-{3,4}.json`; one citation, several files, and a substring test sees none of them |
| **no file cited, the experiment is** | **121** | (117 runs and 4 audit reports) the experiment is written up at *aggregate* granularity — see §3 |
| **no citation of any kind** | **1** | `runs/e43_e5_replication.json` |

So the naive count of 156 is wrong by 151, and the number this audit exists to produce is the last row: **one file,
and it is not a run** — *and this finding closed it*: `runs/e43_e5_replication.json` is cited by this document, so
the count the script prints today is **0**. That is the one self-reference the classes cannot avoid, and it is worth
one line because a reader who reruns the audit sees a zero where the table says one.

## 2. The one un-named file, and why the exit code asks about runs

`runs/e43_e5_replication.json` is an **audit report** — its payload is `{reference, candidates, log}`, not a
`config` — written by `e43_e5_replication.py`, whose plan row names the script and whose numbers the finding
`2026-09-22-e5-does-not-reproduce-its-own-artifact.md` quotes. No document writes its file name.

That is why `e184`'s **exit code counts un-named *runs*** and not un-named files: an un-named report is explained by
its plan row naming the script, while an un-named run would be a result nobody has written up. A single count mixing
them would fire on the audit's own output — `e184`'s report is itself one of the 60 files that carry no `config`.

**And the same distinction makes a claim of `e182`'s precise, which is the second result here.** The corpus is
**316 runs carrying a `config`** (the `vars(args)` shape that `e163`, `e172` and `e182` read) and **60 payloads that
carry none** — and those 60 are the audits' own report files (`e103_reproducibility_audit.json`,
`e127_programme_table_audit.json`, `e151_pertask_contrast_audit.json`, …), not runs. So the three config-based
audits are not blind to any run: "all 316 artifacts that carry a config" is the same set as "every run".

## 3. The weakest class, sharpened twice

The 121 "no file cited, the experiment is" files are one step weaker than a citation and one step stronger than
nothing, and they were worth two further measurements rather than being left as a lump.

**First: which of them are runs?** 117 of the 121 carry a `config`; the other 4 are reports. So this class is mostly
real payloads.

**Second: is an un-named run a duplicate of a named one, or a configuration nothing named carries?** Two payloads
with the same `config` (minus `json_out`) are one run written twice, and a citation of either covers both. Of the
117, **2 have a named twin** — and **115 carry a configuration that no named file carries**. The class is therefore
not explainable as duplication.

**Third: then what is cited for those 115?** The answer is the citation's *form*, and it is an aggregate:

| experiment | un-named members | what the corpus does name |
|---|---|---|
| `e92` | 60 | `runs/e92_grid_report.json` |
| `e86` | 18 | `runs/e86_spread_at_other_sizes.json` |
| `e94` | 15 | `runs/e94_predictor_denominators.json` |
| `e65` | 6 | `runs/e65_realization_sd_by_rule.json` |
| `e104` | 4 | `e104_classil_naive_ewc.json`, `e104_frozen_r32_{frozen,plastic}.json` |
| `e14` | 3 | `e14_drawsd_min2.json` |

So this project cites at **two granularities** — the individual payload, and the aggregated report or a
representative member of a sweep. That is a legitimate convention and it is now written down, which is the point:
the licensed sentence is *"every run is findable"*, **not** *"every run was read"*. 115 distinct configurations are
represented in the documents by an aggregate and are not named one by one, and a later reader who needs one of them
must find it through its report.

## 4. Robustness, because the result is a zero and a zero invites a soft check

Two ways the zero could be an artefact of the scan, both run rather than argued:

- **Letting code cite too** (`--include-code`): 343 files scanned, 237 citations by full name, 28 shorthand-only,
  111 sibling-only, and **still 0 un-named files**. Including the runners' own docstrings *reduces* the uncited set
  by one and cannot change the class of any run.
- **Dropping the requirement that a brace citation end in `.json`.** The corpus writes 68 brace-bearing tokens and
  **28 of them have no `.json` suffix** (`e37_kappa_{real,swap2}`, `e112_readout{300,700}`,
  `e116_r{1307,900,700,128,32}`, `e104_frozen_{whole,r128,r32}`) — so the pattern's strictness is a live risk. Tested:
  exactly **1** of the 122 uncited files changes class, and it is `e43_e5_replication.json` again, matched through
  the *script* name `experiments/e43_e5_replication.py`. The classes are stable under the loosening, which is what
  makes the zero worth reporting.

## 5. Falsifiers and the scope of the claim

- **Scope, first, because "every run can be found by name" is a statement about names.** The check tests file names
  (with digit runs allowed to sit in a brace group) against `docs/**/*.md` and `README.md`. A document that reports a
  run's numbers **without** naming its file is invisible here — and that is exactly the class `e97` measures from the
  other side: **121 of its 261 findings declare no `Artifacts:` line at all (46%)**, which it calls *"unfalsifiable by
  construction"*. The two numbers look contradictory and are not, and the difference is worth stating because either
  one alone reads as the whole truth: `e97` measures the **declared metadata line**, while this audit measures **any
  mention anywhere in the corpus**, prose included. A finding can therefore be un-anchored by `e97`'s standard and
  still be the document that names a run — which is the normal case in this corpus, and the reason both checks are
  needed.
- **Falsifier.** The claim dies if any run carrying a `config` belongs to an experiment no document names in any
  form — the list is printed by the script (`NO file of the experiment cited anywhere`, with the runs among them
  printed separately) and is empty. It is also defeated by any citation form the two patterns do not generate, which
  is why the two loosening tests above are part of the instrument rather than of the prose.

## Reproduce

```
uv run python -m experiments.e184_artifact_citation_census                  # exit 0: zero un-named runs
uv run python -m experiments.e184_artifact_citation_census --include-code    # the robustness switch
uv run python -m experiments.e184_artifact_citation_census --list            # the two weaker classes, by file
uv run pytest tests/test_e184_artifact_citation_census.py -q
```
