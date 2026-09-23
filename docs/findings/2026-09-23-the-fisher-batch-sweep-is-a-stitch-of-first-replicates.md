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

## 6. `e96` is re-measuring it, and the equivalence test came back negative

`e96_fisher_batch_sweep.py` re-runs the three points at the finding's own setup, carrying the finding's
table inside the script as the comparison. **First, whether that comparison is even legitimate**, because a
re-run is not a recovery and rule 21 is why: the test is the **`naive` arm**, which uses no Fisher matrix and
therefore **cannot depend on the batch count**. If the two invocations were equivalent it would be
*identical*. It is not:

| execution (naive, seed 0, 32 batches, identical recorded flags) | `learned` after each task | final accuracy | mean forgetting |
|---|---|---|---|
| stored artifact, replicate #0 | 0.875, 0.896, 0.938 | 0.896 | **+0.010** |
| `e96`, `OMP_NUM_THREADS=1` | **0.958, 0.938, 0.917** | 0.799 | **+0.208** |
| `e96`, `OMP_NUM_THREADS=4` | **0.958, 0.938, 0.917** | 0.868 | **+0.104** |
| `e96`, `OMP_NUM_THREADS=3` (the sweep's own) | 1.000, 0.875, 0.896 | 0.833 | **+0.135** |

**Four executions of one nominal experiment, on an arm that cannot depend on the quantity being swept, span
0.799 to 0.896 in accuracy and +0.010 to +0.208 in forgetting.** Two of them (`OMP_NUM_THREADS` 1 and 4)
agree exactly on `learned` and still differ in the final readout by 0.104, so the spread has at least two
components and the honest statement is the one rule 21 already licenses: *the torch path is not reproducible
across environments, and a network-benchmark forgetting number carries an environment-shaped component that
this project has measured at 55% of the `naive` arm's total variance.*

**What that means for the finding's table, and for the paper:** the finding's `naive` column reads **+0.010 at
every batch count** — which a spot check would take as evidence that the naive arm is batch-independent, and
it is, *because it is one execution repeated in the table*. The column is a single realisation, and the
realisations above put the same quantity anywhere in +0.010 to +0.208. So the finding's rows **cannot be read
cell-by-cell against a re-run**, and `e96`'s value is what it is for a different reason: **its three points
are only comparable to each other**, one process, one thread count, which is exactly how the sweep needs to
be read. A level from `e96` means nothing next to a level in the paper; the *ordering of the three points*
within it means something.

This is the same lesson as rule 17's third shape (a statistic from a growing set is a moving target) one
level further out: here the set is not growing, it is **re-executed**, and the number moves anyway. The
guard is the same in form — report the environment and the comparison's scope, not a bare level — and it is
worth stating that the sweep's whole design had this problem from the start, since the paper's claim is
about a *difference between three levels* and the levels themselves are environment-dependent.

**First numbers, at 8 batches** (single seed): the three arms reported give (0.833, +0.135), (0.868, +0.052),
(0.785, +0.188) — none of which is the finding's 8-batch `ewc` value of (0.826, +0.063), for the reason
above rather than as a scientific disagreement. The run is still in flight and no verdict is drawn from a
partial sweep (rule 17's third shape).

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

## 7b. A near-miss on the way, which is worth more than the correction it nearly made

While tracing the adjacent "55% of the `naive` arm's per-replicate variance", a scan over every
floor/variance/share field under `runs/` for a value in [0.50, 0.60] printed **twenty of its thirty-four
hits** and showed no `naive` value of 0.55 — so the 55% was written off as unsourced and a correction to
0.6187 was drafted into the paper. **The scan had truncated itself.** `runs/e71_variance_share_audit.json`
carries `corrected.naive_floor_share = 0.5490` and `naive_learner_share = 0.4510`, exactly the paper's
figures, and it sorts late enough that `[:20]` cut it off. The correction was withdrawn before it was
committed, and the paper's sentence stands with its **source** added instead.

Two things follow, and the second is the general one:

- The 55% and the 62% are **both** right and are not rivals: they are the same statistic on two pools —
  **0.5490 on the `e54` pool at sixteen replicates** and **0.6187 on the `e38` pool at nine**, with
  **0.2599 at three** in the same artifact. The floor is a per-observation sd (0.0305) that does not shrink
  with `n` while the measured sd does, so the *estimate* of the share drifts upward as replicates are added.
  A share quoted without its pool and its `n` is not wrong, it is unfalsifiable, which is worse.
- **A truncated scan is indistinguishable from a complete one unless the truncation is printed.** The
  earlier audits in this project's record all ended by *finding* something; this one ended by *not* finding
  something, and it was the not-finding that was false. So the guard is: when a scan's result is going to be
  used to *assert an absence*, print the hit count next to the listing and make the listing the whole of it —
  `hits[:20]` and `hits` render identically otherwise.

Had this gone through, the paper would have carried a freshly-introduced wrong number filed as a
correction, which is the worst kind: the audit's authority would have protected it from the next audit.

## 8. Corrections applied

- The paper's §4.7, both places: the monotone triple is withdrawn to *no artifact*, and the `+0.063 → +0.250`
  pair is replaced by the artifact-backed 32-batch measurement with its replicate spread.
- The paper's §4.7 caveat and §8 item 2: both said "128 Fisher batches"; every one of the 25 rate-network
  artifacts used 8 or 32, so **the number was wrong as well as unsourced** and both now read 32.
- `docs/findings/2026-09-22-fisher-batches-negative.md`: a correction note at the top naming what the
  artifact now holds, that the 128 point has no artifact, and which of its rows are first replicates. The
  prose table is left standing, because it is the only surviving trace of those numbers.
- The plan's `e8c` row records the defect and the two-field check that finds it.
