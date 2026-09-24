# `e159` reproduces the wiring family's five-arm table exactly, and it is the corpus's largest floor measurement

**Date:** 2026-09-25
**Read of:** `runs/e159_r32_overlap1_methods_rerun.json` — the third execution of one command, registered with a
C0, a P1 and a falsifier in the programme table. No new script: the read is a two-artifact comparison.
**Result: C0 and P1 both hold, the falsifier does not fire, and nothing differed.**

---

## 1. Rule 44 first: the configuration check

`e153` and `e159` have **identical `config` fields** — the same key set, and no shared key with a different value
once `json_out` is dropped. This is the check whose omission produced the `e153` accident (a paraphrase that lost
`--lam`), and here it is the reason the reproduction claim can be made at all: **the two runs were asked for the
same thing.**

## 2. The read

| arm | `e153` (09-24 21:36) | `e159` (09-25 00:44) | bit-identical | worst per-replicate difference |
|---|---|---|---|---|
| `naive` | 0.106771 | 0.106771 | **yes** | **0** |
| `ewc` | 0.069792 | 0.069792 | **yes** | **0** |
| `ewc-block` | 0.063281 | 0.063281 | **yes** | **0** |
| `ewc-block-rand` | 0.073958 | 0.073958 | **yes** | **0** |
| `replay` | 0.008333 | 0.008333 | **yes** | **0** |

**C0 holds** (`naive` and `replay` — the two arms that cannot read `lam` — are identical).
**P1 holds** (so are the three penalty arms, which is the stronger claim and the one that needed two runs of one
configuration).
**The falsifier does not fire**: there is no run-to-run term to add to §4.2's method table.

**Five arms × forty seeds = 200 values, all bit-identical, across a three-hour re-execution.** That is the
corpus's **largest exact reproduction** — the previous best was `e164`'s pair at five arms × five seeds, and
`e133`/`e140`'s twin at two arms × forty.

## 3. The environment differed, and only in its timing — which is the fix from earlier tonight

`e159`'s `environment` block is **not** equal to `e153`'s, and the difference is **one field**:
`calibration_matmul_s`, **0.000201 against 0.000309**. The timing-excluded identity is equal, so this pair is
**one recorded environment**, not two — which is precisely the case `e103`'s grouping was changed for two hours
earlier on `e164`'s pair. **This is that fix's second instance and its largest**: without it, the corpus's
strongest reproduction would have been filed as a *two-environment* group and excluded from the floor.

**And the calibration tracked the clock again**: `e159` ran in **11553 s** against `e153`'s **14616 s**
(1.27× faster) with a calibration 1.54× faster — the same direction, as in `e164`'s pair and unlike the `e161`
comparison. Three instances now, two agreeing and one not, on a field that measures peak speed rather than load.

**And `code_revision` is absent from `e159`** — it was launched at 21:37, four hours before the field existed
(23:35) — so this is the fourth pair tonight whose provenance is one-sided, and the same conclusion holds: the
one field that would have recorded the code is missing from the side that would have needed it.

## 4. What it does to the floor

`e163`'s census now reads **12 repeated configurations / 44 runs / 28 arm-comparisons**, of which

| | |
|---|---|
| the floor (one recorded environment) | **10 groups / 37 runs / 0.0000 on both axes** |
| two recorded environments | **0** |
| no recorded environment | 2 groups / 7 runs, worst movement 0.0396 forgetting / 0.0458 accuracy |
| bit-identical arm-comparisons | **20 of 28** |
| groups that do not move | **10 of 12** |

**The floor has grown three times tonight — 8 groups / 33 runs, then 9 / 35, now 10 / 37** — and every addition
is a pair whose arms are identical. The seven unrecorded-epoch runs remain the only ones that move, which is the
finding's original point surviving every change around it.

## 5. What this cannot settle

- **One configuration, and it is the wiring family's.** It says the runner is deterministic for this command at
  this circuit, read-out and seed stream — five arms and the block machinery included — not that it is
  deterministic in general. `e164`'s pair is the 8-batch configuration's evidence and it is five replicates deep.
- **A same-configuration agreement cannot date either run's code.** `e159` predates `code_revision` and `e153`
  predates `partition_draw`; both artifacts reproduce today's arithmetic, which is evidence about the *paths* they
  exercise and not about the trees they ran in.
- **The environment difference is real and only the timing is excluded from it**, so the two runs remain *not*
  like-for-like for any cost comparison: 11553 s against 14616 s is a 1.27× machine difference that a
  per-replicate cost would carry.
- **And the floor's own growth is not a finding about the runner** — it is a finding about the *corpus*, which now
  contains enough repeats to see that twenty-eight arm-comparisons across twelve configurations are what it takes
  to say so.
