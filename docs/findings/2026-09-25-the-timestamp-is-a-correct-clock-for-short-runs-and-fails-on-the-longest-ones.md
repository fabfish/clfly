# The timestamp is a correct clock for short runs and fails on the longest ones: rule 47 measured

**Date:** 2026-09-25
**Script:** `experiments/e169_start_time_dating.py` — analysis only, no runs. Artifact:
`runs/e169_start_time_dating.json`.
**Validates:** rule 47, written last night from `e144`'s 4.30 h against a 24-minute window. This unit turns that
single inference into a check with a number.

---

## 1. A second dating method that never consults a timestamp

`e103`'s premise is that **a parser only ever gains flags**, which makes a config **keyset** a monotone marker of
time: wherever one artifact's keyset is a strict *subset* of another's, the smaller one must have been produced
earlier. That invariant tests any candidate clock, and it is independent of the clocks — it reads `config` and
nothing else.

**Scope, declared, because two exclusions decide the answer:**

- a **run artifact** must carry `timing_s`, a `methods` dict and a config of **at least 25 keys**. The smaller
  configs in `runs/` are hand-built summaries, and asking a summary for a parser's keyset is asking the wrong
  object — the defect `e103`'s docstring records twice. 129 of the 136 artifacts carrying a duration qualify;
- pairs whose two clocks are within **60 s** are counted as **neither**, because ordering them is a coin flip and
  reporting one as a violation would manufacture the defect the check exists to find. There are **none** in the
  scoped set.

Result: **5,263 strictly-nested keyset pairs**, each of which must be ordered with the smaller keyset first.

## 2. The answer: three violations by write time, none by start time

| clock | ordered correctly | **violated** |
|---|---|---|
| **write time** (the file's mtime) | 5,260 | **3** |
| **start time** (`mtime − timing_s`) | **5,263** | **0** |

**And all three violations are the same shape — the corpus's longest runs placed after shorter ones:**

| misplaced (smaller keyset) | keys | duration | placed after | keys | duration | by |
|---|---|---|---|---|---|---|
| `e144_r32_overlap1_methods_40reps` | 29 | **4.30 h** | `e144_r32_overlap1_rand_draw1` | 30 | 1.47 h | **2.48 h** |
| `e140_r32_methods_plastic_40reps` | 29 | **5.34 h** | `e144_r32_overlap1_rand_draw1` | 30 | 1.47 h | **1.47 h** |
| `e144_r32_overlap1_methods_40reps` | 29 | **4.30 h** | `e144_r32_overlap1_rand_draw2` | 30 | 1.49 h | **0.99 h** |

**The two artifacts write time misplaces are the two longest runs in the corpus** (5.34 h and 4.30 h, against a
median run of **16 minutes**), and the key at issue is `partition_seed` — the one `5a0f06e` added at **09-24
10:21**, which is exactly the boundary last night's reconstruction had to argue about. **Subtracting the duration
removes every violation.**

## 3. What this retroactively validates

`e144`'s code epoch was fixed last night by one inference — that a 4.30 h run written at 14:18 must have begun
around 09:57, before a 10:21 commit. **Two independent directions now agree, and the timestamp is the only one
that disagrees:**

- its config has **29 keys** and lacks `partition_seed`, which a parser can only produce before the flag existed;
- its **start time** (10:00) is 21 minutes before `5a0f06e`;
- its **write time** (14:18) is 4 hours after it, and would date it as post-flag.

So the reconstruction in `e168` — which identified the matched-random draw of a run that could not record it, and
thus saved `e162`'s block-rand column — rests on a dating that is now checked by an invariant that never consults
a timestamp at all.

## 4. Rule 47, with its check and its numbers

> **An artifact's timestamp dates the *end* of its run, so a long run's code epoch is set by its start — and the
> timestamp can therefore sit on the wrong side of a commit the run never contained.**

**Measured: 3 of 5,263 nested-keyset pairs are ordered wrongly by write time and 0 by start time, and every one of
the three involves a run of four hours or more.** The check is `experiments/e169_start_time_dating.py`, it reads
`mtime − timing_s` against the smaller-keyset invariant, and it is the tool a future unit should run before dating
anything by a file's timestamp.

## 5. What this cannot settle

- **The invariant is one-directional.** Nested keysets *do* imply an order; non-nested ones say nothing, so of the
  corpus's pairs only these 5,263 are checkable this way. A mis-dating between two artifacts at the same keyset
  size is invisible here — and that is the common case, because most keysets are identical.
- **It assumes a parser only gains flags.** A *removed* flag would look exactly like a mis-dated artifact, and
  `e103`'s docstring states the premise rather than deriving it.
- **Start time is itself derived from `timing_s`**, which the runner starts after imports and connectome loading:
  the true start is therefore *earlier* than `mtime − timing_s`, by an unmeasured constant. That bias points the
  same way as the correction (artifacts are older than this clock says), so it cannot create the violations that
  the start-time ordering avoids — but it means "start time" here is an upper bound on the start.
- **The 60-second tie rule and the 25-key floor are choices**, and both were made after seeing that the unscoped
  version reported 168 violations dominated by artifacts from *other runners* (whose parsers are unrelated even
  where their keysets nest) and by same-minute writes. The scoped number is the one this unit defends; the
  unscoped one is in the commit's history and in this paragraph.
