# The readership table classifies its own conflicts, and the corpus's most-cited one becomes a clean verdict

**Date:** 2026-09-25
**Script:** `experiments/e160_which_fields_are_read.py` — three changes to the join, no runs. Artifact:
`runs/e160_field_readership.json`.
**Supersedes:** the two named refinements in
`docs/findings/2026-09-24-which-fields-does-each-method-read.md`, both of which failed there; one of them now
works.

---

## 1. Three changes to the same join

**(a) An absent key and a default-valued key are the same statement.** A `vars(args)` dump's *absence* means the
parser had no such flag yet, and its stored `None`/`False` means the flag existed and was not given — which is the
same thing for a question about whether the run differed. Comparing them as values makes a **schema epoch look
like an intervention**, and it did: `e104_frozen_r32_plastic` (which predates `frozen_bias`) against
`e164_fb8_today_a` was read as a *single-field* difference in `frozen_bias` while both arms were bit-identical,
which is what made `frozen_bias × naive` **CONFLICTING**. New `effective()` drops `json_out` and every value that
**`is None` or `is False`** — `is`, not `in (None, False)`, because `0` equals `False` in Python and
`pool_below = 0` / `readout_size = 0` are real settings. After the fix: **`read`**.

**(b) The environment is a field, minus its timing.** A pair whose arms moved because the *machine* differed
cannot be evidence about a `config` field, and the environment is not in `config`, so the join could not see it.
The identity is `e103.environment_key` — the block **without `calibration_matmul_s`** — and that exclusion is
what makes the change work: the first attempt at this refinement keyed on the whole block and lost `lam`'s clean
verdict, because two runs of one command never share a calibration. Verified here: **`lam` is
`unread / read / read / read / unread` for `naive / ewc / ewc-block / ewc-block-rand / replay`, unchanged**.

**(c) An unrecorded environment is not evidence, and it is not "equal" either.** If either side of a pair lacks
the block, the pair carries a marker field (`environment:unrecorded`) and so drops out of single-field evidence.
Reading it as *equal* is the defect (b) exists to prevent, one level down; reading it as *different* would throw
away every pair in the pre-19:06 corpus. What the marker does instead is give those pairs **their own row**, and
that row is a statement about the corpus rather than about a method.

## 2. The table's conflicts, classified

| | |
|---|---|
| CONFLICTING cells, after (a)–(c) | **5 — every one of them the `environment:unrecorded` marker**, one per arm |
| CONFLICTING cells on the **97 artifacts that record an environment** | **0** |
| the two `fisher_batches` conflicts `e160`'s own finding explained | **gone** |

**And those two had different causes that look identical from `config` alone.** For `naive` the moved pairs are
`e101_rate_fb128` against `e102_rate_fb8_omp1` and `..._omp4` — the **thread** difference in two artifacts that
never recorded it. For `replay` they are `e101_rate_fb8` against `e101_rate_fb32` and against
`e102_replayonly_fb32` — **the `e101`→`e102` code epoch**, and *both* sides of those pairs are unrecorded, so
neither the environment nor the code revision could be read off them. A conflict table that cannot tell a thread
difference from a code change is exactly what (c) refuses to guess about.

## 3. What it costs, and what it buys

The sharper rule — an unrecorded environment treated as *equal*, which is what the table did before (c) — decides
**23 cells** that this one reports as `possibly read`. Every one of them is evidence from a pair with a
pre-2026-09-23-19:06 artifact in it, so the sharper column is not *wrong* about them: it is right, **given the
assumption that an unrecorded environment was the default one**, which is true for most of those artifacts and
false for `_omp1`/`_omp4`. That assumption is now printed beside the cells it decides rather than baked into
them.

**And exactly one cell goes the other way, which is the rule earning its keep rather than costing anything:
`fisher_batches × naive`.** It was **CONFLICTING**; refusing the unrecorded pairs leaves **two 40-replicate
recorded-environment pairs** — `e116_r32_40reps` against `e133_r32_naive_ewc_40reps` and against
`e139_r32_wholebody` — that both agree, so it is **`unread`, on better evidence than the conflict ever had**. The
corpus's most-cited readership conflict was the thread count in two artifacts that never said what they were.

**Rule 48: an artifact that does not say what it was measured in is not evidence about a field — and refusing
such pairs is sound, while its cost is decidable: it is exactly the set of verdicts whose only support was an
unattributable pair.** The two columns are reported together, sharp and sound, because the difference between them
*is* the measurement.

## 4. What this cannot settle

- **Whether an unrecorded environment was the default.** The sharper column's assumption is unverifiable per
  artifact: `_omp1`/`_omp4` prove it false for at least two of the seven, and the other five are only *probably*
  default because `e164`'s pair and `e161` show what the default is *today*.
- **The marker's own row is not a method claim.** It says the unrecorded runs sometimes moved together and
  sometimes did not; it cannot say why, and its CONFLICTING verdict is the correct shape for a thing nobody wrote
  down.
- **The join still reads `config` and `environment` and nothing else**, so a **code** difference is invisible to
  it — which is why `replay`'s conflict could be *classified* here only by hand, using `e163`'s epoch. A
  readership table over `code_revision` would need the field on both sides of a pair, and tonight's corpus has it
  on one.
- **23 decided verdicts become `possibly read`**, and two of them (`replay_per_task` for `naive` and for
  `replay`) are settings `e140`'s C0 controls were justified by. The controls themselves are unaffected — they
  compare two artifacts at one environment — but the *table's* support for them is now weaker, and it would be
  recovered by one pair of runs at a recorded environment.
