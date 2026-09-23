# The Fisher-batch sweep is a stitch of first replicates, and its 128-batch point has no artifact

**Date:** 2026-09-23
**Script:** `experiments/e96_fisher_batch_sweep.py` (re-measurement, in flight); audit is of
`runs/e8_fisher_batches.json` and every other artifact under `runs/`.
**Context:** the paper's §4.7, and `docs/findings/2026-09-22-fisher-batches-negative.md` (`e8c`).

---

## 1. The trigger

The paper's §4.7 states, twice, that raising the Fisher batch count makes the diagonal worse:

> *the diagonal degrades as its Fisher estimate improves* (+0.010 → +0.028 → +0.035 as batches go
> 8 → 32 → 128, monotone; **+0.063 → +0.250** on the unhardened configuration)

> Raising the Fisher batch count from 8 to 128 drives the diagonal's forgetting from **+0.063 to +0.250**
> while its accuracy collapses from 0.826 to **0.701**

Both come from `e8c`, which reports a *"single seed, λ = 0.1, sweeping the Fisher batch count"* and names
`runs/e8_fisher_batches.json` as its artifact. Following the number to its source turned up three separate
problems.

## 2. No 128-batch run exists on disk

Every `fisher_batches` value anywhere under `runs/` — 30 occurrences across 25 artifacts — is **8 or 32**.
There is no 128. The artifact the finding names now holds a **three-repeat, 32-batch** run written later:
its `config` reads `fisher_batches: 32, repeats: 3` against the finding's "single seed, sweeping".

So the *path* was reused by a different run, and the sweep's record stopped existing. **This is a shape of
rule 22's failure the project had not named**: not a misquoted number, not a half-covered artifact, but an
artifact replaced at its own path. The tell is mechanical and cheap — **compare the finding's stated setup
against the named artifact's `config`** — and here it fails on two fields at once (`repeats: 3` against
"single seed"; one batch count against "sweeping the batch count").

## 3. The 32-batch row is a first replicate presented as a batch-count point

`runs/e8_fisher_batches.json` keeps its `replicates`, so the finding's rows can be matched exactly. All
**four** of its 32-batch cells are **replicate #0** of that artifact:

| method | finding's 32-batch row | artifact replicate #0 | artifact's mean over 3 |
|---|---|---|---|
| `naive` | +0.010 (0.896) | **+0.010 (0.896)** | +0.101 (0.824) |
| `ewc` | +0.125 (0.792) | **+0.125 (0.792)** | **+0.069 ± 0.028 (0.843)** |
| `ewc-block` (bio) | +0.104 (0.833) | **+0.104 (0.833)** | +0.104 ± 0.024 (0.838) |
| `ewc-block-rand` | +0.010 (0.868) | **+0.010 (0.868)** | +0.069 ± 0.049 (0.850) |

So the number the paper leans on for the diagonal at 32 batches, **+0.125**, is one replicate of three, and
it is the **worst** of the three (`+0.125, +0.031, +0.052`). The three-replicate mean is **+0.069 ± 0.028**.
The `naive` column being identical everywhere is expected rather than suspicious — that arm uses no Fisher
and cannot depend on the batch count — but it is also what made the stitch invisible to a spot check.

The finding's 8-batch row matches `e31_methodlist_check.json`'s replicate #0 for its two block arms, and
**its `ewc` cell (+0.063, 0.826) matches no replicate in any artifact**. Its 128-batch row matches nothing.

## 4. And the values the paper quotes for 32 and 128 appear in no artifact at all

The complete list of every `ewc` (diagonal) mean forgetting on disk is six numbers:

| artifact | `ewc` mean forgetting | λ | Fisher batches | replicates |
|---|---|---|---|---|
| `e8_hardened.json` | +0.0208 | 0.003 | 32 | 5 |
| `e8_hardened_basis.json` | +0.0208 | 0.003 | 32 | 5 |
| `e8_basis.json` | +0.0556 | 0.1 | — | 3 |
| `e8_fisher_batches.json` | +0.0694 | 0.1 | 32 | 3 |
| `e8_class_incremental.json` | +0.1208 | 0.003 | 32 | 5 |
| `e8_rate.json` | +0.1562 | 1.0 | — | 3 |

**Nothing is +0.028, nothing is +0.035, nothing is +0.250, and nothing is +0.063.** Scanned with a ±0.006
window, the first two have **zero** hits anywhere in `runs/`. So the paper's monotone triple
`+0.010 → +0.028 → +0.035` is a sentence with no artifact behind any of its three points, and the pair
`+0.063 → +0.250` has no artifact behind its second. Both sentences state an *argument* — that a
better-estimated Fisher is a stronger penalty at fixed λ — and an argument is a legitimate thing to write;
what is not legitimate is writing it with four decimal figures that read like measurements.

## 5. What is artifact-backed, stated plainly

- **At 32 batches, λ = 0.1, three replicates: the diagonal forgets +0.069 ± 0.028 at 0.843 accuracy**
  (`runs/e8_fisher_batches.json`). Its own first replicate is +0.125 (0.792).
- **The 8-batch and 128-batch points of the sweep have no artifact.** 8's diagonal cell matches no
  replicate; 128 exists nowhere, so *"the diagonal's accuracy collapses to 0.701"* cannot be checked.
- **The direction of the claim is therefore not established by the record** — not refuted either, simply
  unsupported. The paper's own §7 lists "more tasks" and "the reversed-ordering question" as open; this adds
  a third for the network line, and it is cheaper than either: three runs.

## 6. `e96` is re-measuring it, and that is a new measurement

`e96_fisher_batch_sweep.py` re-runs the three points at the finding's own setup, carrying the finding's
table inside the script as the comparison. **A re-run is not a recovery**: rule 21 measured the torch path as
`OMP_NUM_THREADS`-sensitive at the third decimal, so agreement is expected and exact reproduction is not,
and disagreement will be reported rather than averaged away. It is single-seed, matching the finding's
design, so it cannot fix the replicate problem — what it can do is establish whether the three points differ
at all, which nothing on disk currently does. A three-replicate version is the natural follow-up if the
single-seed sweep shows a direction worth resolving.

**First numbers, at 8 batches** (single seed): the three arms reported so far give (0.833, +0.135),
(0.868, +0.052), (0.785, +0.188) — none of which is the finding's 8-batch `ewc` value of (0.826, +0.063).
The run is still in flight and no verdict is drawn from a partial sweep (rule 17's third shape).

## 7. The section contradicted itself, and that is the fourth time this week

The paper's §4.7 table reports the three-replicate means for the very configuration the sweep used —
`naive 0.824 ± 0.036 / +0.101 ± 0.049`, `EWC diagonal 0.843 ± 0.025 / **+0.069 ± 0.028**`,
`bio 0.838 / +0.104`, `rand 0.850 / +0.069` — and those are **exactly** the values
`runs/e8_fisher_batches.json` holds. Fifteen lines below that table, the prose quoted the artifact's
**first replicate** as the diagonal's 32-batch result (**+0.125**) plus a 128-batch value that exists
nowhere. So one document carried the right number and the wrong number for one measurement, and the fix is to
delete the second rather than to reconcile them.

This is the fourth instance of *two halves of one document disagreeing* in this project's recent record
(after the plan's C2b carrying both "`side` has never been run" and its own Update paragraph reporting it),
and unlike the earlier three it is not a staleness of the record at all: both numbers were written from
artifacts, and one of them was written from the wrong *slice* of one. **The check that catches it is to ask
which rows of a table a paragraph is restating**, which is the same question as rule 22's "where should this
number come from" asked of a sentence rather than of a cell.

## 8. Corrections applied

- The paper's §4.7, both places: the monotone triple is withdrawn to *no artifact*, and the `+0.063 → +0.250`
  pair is replaced by the artifact-backed 32-batch measurement with its replicate spread.
- The paper's §4.7 caveat and §8 item 2: both said "128 Fisher batches"; every one of the 25 rate-network
  artifacts used 8 or 32, so **the number was wrong as well as unsourced** and both now read 32.
- `docs/findings/2026-09-22-fisher-batches-negative.md`: a correction note at the top naming what the
  artifact now holds, that the 128 point has no artifact, and which of its rows are first replicates. The
  prose table is left standing, because it is the only surviving trace of those numbers.
- The plan's `e8c` row records the defect and the two-field check that finds it.
