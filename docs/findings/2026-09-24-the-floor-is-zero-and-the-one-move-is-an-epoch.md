# The run-to-run floor is exactly zero, and the corpus's one move is an epoch

**Date:** 2026-09-24
**Script:** `experiments/e163_repeat_floor.py` — analysis only, no runs. Artifact:
`runs/e163_repeat_floor.json`. The grouping is `e103`'s (`group_repeats`), so this unit cannot disagree with the
audit about what "the same configuration" means: `config` with `json_out` dropped.
**Runs it is about:** the ten configurations the corpus has executed more than once — 40 artifacts, 18
arm-comparisons. Companion run: `e164`, the same command executed twice today.

---

## 1. The corpus has a floor, and it is zero

| case | groups | runs | worst movement (forgetting) | worst (accuracy) |
|---|---|---|---|---|
| same config, **one** recorded environment | **8** | **33** | **0.0000** | **0.0000** |
| same config, **two** recorded environments | **0** | 0 | — | — |
| same config, **no** recorded environment | 2 | 7 | 0.0396 | 0.0458 |

**33 runs of one configuration each, across 8 configurations, moved by nothing** — every arm bit-identical, not
"identical to four digits". That is the number the project's reproducibility claims have been resting on as prose
since the second execution existed, and it is now a count: **10 of 18 arm-comparisons are bit-identical and 8 of 10
groups do not move at all.**

**And the second row is empty** — a result in itself: **not one group in the corpus contains two recorded
environments**, so the environment split `e103` documents has never fired on real data. Its docstring's measured
claim for the 8-batch group ("within the three default-thread runs `naive` and `ewc` are bit-identical") is
**correct but read from filenames** (`..._omp1`, `..._omp4`), because those five artifacts record no environment at
all. The code path works — `tests/test_e163_repeat_floor.py` exercises it on a synthetic multi-environment group —
but the corpus contains no group that triggers it.

## 2. The 7 runs that moved are exactly the 7 that predate the environment field

| artifact | written | `environment` |
|---|---|---|
| `e101_rate_fb8.json` | 09-23 15:34 | absent |
| `e101_rate_fb128.json` | 09-23 16:00 | absent |
| `e102_rate_fb8_rerun.json` | 09-23 17:03 | absent |
| `e102_rate_fb128_rerun.json` | 09-23 17:32 | absent |
| `e102_rate_fb8_rerun2.json` | 09-23 17:48 | absent |
| `e102_rate_fb8_omp1.json` | 09-23 18:46 | absent |
| `e102_rate_fb8_omp4.json` | 09-23 19:11 | absent |

`77a2f3d` ("record the environment in the artifact") landed at **09-23 19:06**, and these seven are every repeated
run written before it. **The two sets coincide exactly, so the corpus cannot separate "these are the old runs" from
"these are the runs where something moved"** — the classification in §1 is total on this corpus and is nonetheless
an *identification*, not an experiment. Every reproducibility number this project has ever quoted from these seven
artifacts is a number without a recorded environment.

## 3. Inside the 8-batch group: the floor measured twice, and one move that persisted

All five arms of the group, per run (forgetting means, five replicates):

| run | `naive` | `ewc` | `ewc-block` | `ewc-block-rand` | `replay` |
|---|---|---|---|---|---|
| `e101_rate_fb8` (15:34) | 0.072917 | 0.027083 | 0.016667 | 0.052083 | 0.033333 |
| `e102_rate_fb8_rerun` (17:03) | 0.072917 | 0.027083 | 0.022917 | 0.039583 | **0.050000** |
| `e102_rate_fb8_rerun2` (17:48) | 0.072917 | 0.027083 | 0.022917 | 0.039583 | **0.050000** |
| `e102_rate_fb8_omp1` (18:46) | **0.079167** | 0.025000 | 0.043750 | 0.079167 | 0.054167 |
| `e102_rate_fb8_omp4` (19:11) | **0.079167** | **0.035417** | 0.054167 | 0.060417 | 0.035417 |

**Three findings sit in this table.**

**(a) Two executions 45 minutes apart agree on every value.** `rerun` and `rerun2` are identical on all five arms
*and* on all five seeds, and they are **not a re-dump**: `timing_s` differs — **968.766 s against 969.858 s** — so
these were two separate 16-minute processes. A 968-second job reproduced itself to the last digit. That is the
floor measured at the level of the whole arm rather than at the level of a count.

**(b) The thread knob moves `naive` too, and that is what makes the remaining move identifiable.** Both
`_omp`-named runs give `naive` = **0.079167** against **0.072917** for the three default-named runs — a movement of
**0.00625**, 0.3 of a test unit (1/48). `naive` trains the same way in every arm and reads no penalty, no Fisher
and no replay buffer, so a movement in it can only come from the environment — which is `e77`'s result, visible
here in an arm that cannot be blamed on any method. **And `ewc` moves with the thread count and *between* the two
thread settings** (0.025 at 1 thread, 0.035417 at 4): the diagonal Fisher's value is thread-dependent through its
summation order, which is why λ is not comparable across environments.

**(c) The one move that no field explains is confined to three arms and is *persistent*.** `e101_rate_fb8` (15:34)
differs from both later runs on `ewc-block` (0.016667 → 0.022917), `ewc-block-rand` (0.052083 → 0.039583) and
`replay` (0.033333 → 0.050000), and on **nothing else** — `naive` and `ewc` are untouched. Three eliminations, all
measured rather than argued:

- **Not the thread count**: a thread difference moves `naive`, and this difference does not (row (b) is the control
  for exactly this, in this very group).
- **Not a committed code change**: between 15:34 and 17:48 the nearest commits touching `experiments/` or `clfly/`
  are `cc3137e` at **13:06** and `77a2f3d` at **19:06** — the repository's code did not change in the window, and
  the three commits inside it (`e295c27`, `45fb09e`, `edb84de`, 16:02–16:06) touch only `docs/`.
- **Not a re-dump**: same `timing_s` argument as (a).

**And the same three arms move in the same window in the *other* configuration**: `e101_rate_fb128` (16:00) against
`e102_rate_fb128_rerun` (17:32) — `ewc-block` 0.010417 → 0.03125, `ewc-block-rand` 0.027083 → 0.0375, `replay`
0.033333 → 0.050000, with `naive` and `ewc` again untouched. The decisive detail is `replay`'s: **its two values
are the same in both configurations** — 0.033333 before, 0.050000 after — and `replay` builds no Fisher at all
(`e160` derives `fisher_batches` as unread by it), so a change that moves it by exactly the same amount in a
configuration with 8 Fisher batches and one with 128 is a change **in the replay code path**, not in the Fisher's.
That is the signature of an epoch, and it is not noise: noise does not persist across two executions 45 minutes
apart, and it does not take the same value in two different configurations.

**So the corpus's only unattributable movement is an epoch whose change is in the working tree rather than in the
history** — uncommitted code, or a launch parameter that is not in `config`. This is rule 44 read from the other
side: there, a *paraphrase* omitted a field that `config` would have carried; here, `config` and `environment`
together are silent, and the artifact's provenance is short by one dimension.

## 4. What this means for `e159`

`e159` is a third execution of a wiring-family command whose first two executions are bit-identical on every arm,
and its registered falsifier is "any arm differs". The corpus's prior for what such a difference would mean is now
measured rather than assumed:

- **Where an environment is recorded, the floor is 0.0000 over 33 runs** — so a difference is not the runner
  jittering.
- **Every difference this corpus contains is confined to `replay` and the two block arms**, by an amount
  (0.006–0.017) that is *larger* than several effects the record has registered for, and it is a **persistent**
  difference — two later executions agree with each other and disagree with the earlier one.
- If `e159` differs from `e153`, the corpus's reading is therefore "something changed that the artifact cannot
  see", and it will be undiagnosable for exactly the reason §3 names. `e164` (the same command twice today)
  measures the floor in the current epoch directly, so that reading will have a control.

## 5. What this cannot settle

- **The identification in §2 is confounded by construction**: the 7 unrecorded runs and the 7 runs in a moved
  group are the same 7, so this unit cannot say whether a run that records its environment can also move. It can
  only say that the 33 that do were identical.
- **The epoch in §3 is not identified, only localised** to `replay` + the block arms, to a window
  (15:34–17:03 overlapping 16:00–17:32) and to "not committed". Nothing in the record says which code differed,
  and the working tree of 09-23 afternoon is gone.
- **`replay`'s invariance to `fisher_batches` is read from `e160`'s join, not from a controlled pair here**: the
  two configurations differ in that field alone between the pairs compared, which is the strongest form available
  in this corpus, but it is a join over artifacts rather than a run.
- **`e103`'s epoch test reads `config` keysets only**, so it cannot see any of this: the artifacts at issue are
  schema-identical to the ones that reproduce.
- **`command_from_config` closes the launch half of the gap and nothing else.** A command derived from an
  artifact's own config cannot omit a field that the config carries — but it cannot recover a field that was never
  recorded, and no artifact in this corpus records its code revision. **Named improvement, not implemented here:**
  a top-level `code_revision` field written beside `environment`, which is a `git rev-parse HEAD` plus a
  dirty-tree flag at launch. Its cost is *not* the epoch audit: `e103` compares `config` keysets, and `environment`
  is top-level, so a sibling field adds no rows to that report.
