# Which `config` fields does each method read? The record answers, and its conflicts have three names

**Date:** 2026-09-24
**Script:** `experiments/e160_which_fields_are_read.py` — **analysis, no runs**, over 304 artifacts. Artifact:
`runs/e160_field_readership.json`.
**Why it exists:** rules 39 and 44 both turn on the same question — *does this arm read the field that differs?* —
and neither a registration's prose nor the code as remembered answers it. **The evening's cost of not asking it is
on the record**: `e153` was registered to reproduce `e144` and ran at `lam = 1.0` against `3e-3`, and three
artifacts were written on the mistaken premise before one config comparison refuted it. **The corpus can answer the
question empirically**, because it contains hundreds of pairs of runs that differ in known fields and whose arms
either moved or did not.

---

## 1. The method, and its one sound rule

For every pair of artifacts that share an arm, a seed stream and a replicate count, compare that arm's
per-replicate values and record which config fields differ:

| evidence | verdict |
|---|---|
| a pair differing in **only** this field, and the arm **moved** | **read** — an identity claim across it is false |
| a pair differing in **only** this field, and the arm **stayed identical** | **unread** — the arm cannot see it |
| both of the above | **CONFLICTING** — no identity claim should rest on this field until the conflict is explained |
| the field was only ever varied alongside others | **possibly read** (the table is silent) |

**Only single-field differences are used**, and that restriction is the whole reason the table is sound: a pair
that differs in five fields and moves says nothing about which field the arm read. **And the verdict is counted
rather than assigned in iteration order** — the first version of the function let an identical pair overwrite a
`read`, so its answer depended on which pair came last, which is the defect class this project keeps finding in
its own readers.

## 2. The check this table was built for, and it passes

| method | `lam` |
|---|---|
| `naive` | **unread** |
| `ewc` | **read** |
| `ewc-block` | **read** |
| `ewc-block-rand` | **read** |
| `replay` | **unread** |

**`lam` is read by exactly the three penalty methods** — which is the correction that cost three artifacts,
now derived from the record instead of from a paraphrase. **So rule 44 can be executed rather than remembered**:
before writing an identity claim, look up whether the field that differs is `read` by the arm it is about.

**And the table is right about the fields the project relies on for its other controls**: `replay_per_task` and
`replay_batch` are **unread by `naive`** (so `e140`'s C0a across those settings is sound) and **read by `replay`**
(so the C0b probe's four settings are the ones the flag names); `basis` is **unread by `naive`** and **read by both
block arms** (the partition only matters where it is used); `readout_size` is read by `naive` and `replay`.

## 3. And the conflicts are the useful output, with three distinct causes

Every `CONFLICTING` cell is a field about which the corpus contains **both** an identical pair and a moved pair,
both differing in that field alone. Reading them:

- **the environment is not controlled for**: `naive`/`fisher_batches` is conflicting because two of the moved pairs
  are `e101_rate_fb128` against `e102_rate_fb8_omp1` and `..._omp4` — runs that set **`OMP_NUM_THREADS`**, which is
  in the `environment` block and not in `config`. **So a single-field `config` difference is not a single-field
  difference**, and `e77` already measured that the thread count moves this line's values. *The refinement the
  table needs is to treat the environment as a field.*
- **re-dumps masquerade as pairs**: `naive`/`frozen_bias` has identical pairs like `e119_r300_test480` against
  `e123_r300_test480`, which is the loss-metric *re-read* of the same run rather than a second execution — so a
  "stayed" verdict can rest on provenance and not on readership. *The refinement is to exclude artifacts that are
  re-writes of another artifact rather than independent runs.*
- **and some movements are reproducibility rather than readership**: `replay`/`fisher_batches` is conflicting
  because `e101_rate_fb8` and `e101_rate_fb32` differ in that field alone and their `replay` arms differ — and
  `replay` does not build a Fisher. That is §9's own story (two runs of one command at `--fisher-batches 8`
  disagree on `replay`), i.e. **the corpus contains run-to-run movement in this line that no field explains**, and
  the table cannot tell that apart from a readership signal.

**So the table is a finder and not a verdict**, on the same division of labour as `e158`'s corrections index: its
one-sided rows (λ, the replay settings, `basis`, the read-out) are load-bearing, and its conflicting rows are a
list of pairs to explain rather than evidence about the runner.
