# `e164`, half read: today's execution is the 09-23 post-change side of the epoch, and the numbers do not move with the machine

**Date:** 2026-09-24
**Read of:** `runs/e164_fb8_today_a.json` — the **first of two** executions registered as `e164`; the second is
running. The comparison uses `e103`'s signature rule and `e151`'s loader; no new script, because the registered
read is a four-artifact comparison.
**Registration:** the programme table's `e164` row — *the `e101_rate_fb8` configuration, its flags derived by
`e163 --command` from that artifact's own `config`, executed twice today.*

---

## 1. The command was reproduced field for field

`e164_fb8_today_a`'s config and `e101_rate_fb8`'s share **48 keys, and the only shared key whose value differs is
`json_out`** — the output path. The newer runner adds five keys the older artifact predates (`anchor_bias`,
`frozen_bias`, `partition_seed`, `readout_seed`, `save_theta`), all unset.

So this is rule 44 in its executable form: the flags were **derived** from the artifact's own `config` by
`e163 --command` rather than copied from a paraphrase, and the result is that artifact's configuration — including
`--lam 0.003`, which is the field `e153`'s accident lost and which the runner's default would have set to 1.0.

## 2. P2 holds: today's run is the post-change side of the epoch

`mean_forgetting`, all five arms, five seeds each:

| arm | `e101` (09-23 15:34) | `e102` rerun (17:03) | `e102` rerun2 (17:48) | **`e164_a` (09-24 23:49)** |
|---|---|---|---|---|
| `naive` | 0.072917 | 0.072917 | 0.072917 | **0.072917** |
| `ewc` | 0.027083 | 0.027083 | 0.027083 | **0.027083** |
| `ewc-block` | 0.016667 | 0.022917 | 0.022917 | **0.022917** |
| `ewc-block-rand` | 0.052083 | 0.039583 | 0.039583 | **0.039583** |
| `replay` | 0.033333 | 0.050000 | 0.050000 | **0.050000** |

**`e164_fb8_today_a` is bit-identical to both post-change runs on all five arms and all five seeds**, and differs
from the pre-change one on exactly the three arms `e163` localised the epoch to. So the epoch's later side **is the
current code**, 30.5 hours later, across two sessions, five commits and a code change (`77a2f3d` added
`environment`, and a `code_revision` field was added tonight) — none of which touched the numeric path of these
five arms.

## 3. And the numbers are invariant to a 1.8× slower execution

`e164_a`'s `timing_s` is **1725.8 s against 968.8 s** for the 09-23 runs — **1.78×** — because it ran under
three-way contention (`e159` and `e161` were both running). **Every value is bit-identical anyway.** Two things
follow, and the second is new:

- **Load and scheduling join the thread count in being excluded** as the cause of the movement `e163` localised.
  A 1.8× slower wall-clock is not a different arithmetic order: the runner is deterministic across it.
- **The recorded calibration does not see the load, and this is the first pair of artifacts that demonstrates the
  gap.** `e164_fb8_today_a`'s `calibration_matmul_s` is **0.0003 s** against **0.0004 s** for
  `e161_r32_base_ewc_lam1` — the *contended* run's calibration is **1.33× faster**, because the calibration is a
  **minimum over 50 repetitions** of one fixed matmul and therefore measures peak speed rather than queueing. Its
  own docstring says as much ("not a load count: the runner cannot see what else is running"); this is the
  measurement that shows what the field can and cannot be asked, and it is the reason a per-replicate cost cannot
  be compared across artifacts without a load term that no artifact carries.

## 4. The half-read: P1 still open, and the asymmetry the second execution would show

**P1 is the pair's own identity**: the two executions are bit-identical on all five arms and all five seeds and
differ only in `timing_s`. The second artifact is running.

**A pre-stated detail about that pair**: `e164_a` was launched at **23:00, thirty-five minutes before the
`code_revision` field existed** (`b1fb11a`, 23:35), so it carries `environment` and **not** `code_revision` —
while the second execution, a fresh process importing the module as it now stands, will carry both. The two
artifacts will therefore differ in a **top-level key** while claiming to be the same command. That is legal here
and only here: `e103` compares the declared `ARM_FIELDS`, so a provenance key is not an arm, and the pair becomes
the corpus's first whose *recorded provenance* differs while its *command* does not. If any arm differs between
them, the difference is the floor in the current epoch and the field that would have named the code is present on
one side only — which is rule 45's problem stated by the artifacts themselves rather than by a paragraph.

## 5. P1, read once the second execution landed: **it holds**, and the asymmetry is the point

Both executions are on disk. **They are bit-identical on all five arms and all five seeds** — `naive` 0.072917,
`ewc` 0.027083, `ewc-block` 0.022917, `ewc-block-rand` 0.039583, `replay` 0.050000 — their `config` fields are
identical once `json_out` is dropped, and their durations differ (1725.8 s against 1601.4 s), so they are two
processes and not a copy. **P1 holds.**

**And they differ in exactly one top-level key, which is the detail §4 pre-stated.** `code_revision` is present in
the second execution and absent from the first:

```
e164_fb8_today_b.json  "code_revision": {"commit": "62690d118b2d45ed1abc868b596d8a6c55719462", "dirty": false}
e164_fb8_today_a.json  (absent — launched 23:00, 35 minutes before the field existed)
```

So the corpus now contains **a pair that is identical on every arm and differs in its provenance** — the case
`e103`'s *declared* `ARM_FIELDS` was built to survive, and it does: a provenance key is not an arm, so the
identity check reads the pair as identical, which is right, because the arithmetic is identical. **Rule 45's ideal
artifact pair is therefore in the corpus, and it arrived by the accident of a 35-minute window rather than by
design.**

**And the field's semantics are demonstrated by the same artifact.** The second execution was launched at 23:49
**in a clean tree** and recorded `dirty: false` — while the half-hour that followed contained this unit's own
uncommitted finding and plan row, which are *not* in the record. That is the truthful snapshot: the runner calls
`code_revision()` while it builds the payload, before the replicate loop, so what it captures is the tree the
process imported. A run launched mid-edit would instead carry `dirty: true` and the paths.

**Three consequences.** (i) **The current epoch's floor is measured twice** — two executions of one command, 25
seed-arm values bit-identical — and together with `e164_a`'s agreement with both 09-23 post-change runs, the
current epoch now rests on three independent executions. (ii) **The pair is the first in the corpus whose recorded
provenance differs while its command does not**, which is what makes it the clean demonstration that adding a
provenance field does not disturb an identity claim. (iii) **The calibration tracked the wall-clock here**, in the
*opposite* way to §3's comparison: these two runs differ by 7% in duration (1725.8 / 1601.4) and by 18% in
`calibration_matmul_s` (0.00033 / 0.00028) — the same direction. So within one command the calibration does see
the machine's speed; §3's `e161` comparison is the case where it does not, because the difference there was queue
and not speed. The field is a speedometer, not a load meter, and the two artifacts together say so.

## 6. What this cannot settle

- **P1 was the pair's identity and it is now read** (§5); what remains is a floor measured twice rather than
  many times.
- **One configuration, five replicates, three tasks.** This is the 8-batch config; the 40-replicate headline
  config is `e159`, which is still running and is now ~2.5 h into a job that takes ~1.5 h alone.
- **The epoch is bounded and still not identified.** `e163` localised it to the 15:34 → 17:03 window and excluded
  threads, committed code and re-dumps; this read excludes machine speed and places the epoch's far side at the
  current commit. **What changed is still nothing in the record** — the working tree of 09-23 afternoon is the
  only remaining candidate, and it is exactly what `code_revision` would have captured.
- **It says nothing about the current code beyond these five arms.** Five arms reproducing is evidence about the
  code paths they exercise (both block arms, `replay`, the diagonal, and `naive`), not about the runner.
