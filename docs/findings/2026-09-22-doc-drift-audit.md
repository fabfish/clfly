# Doc drift — after five corrections, what went stale was the *aggregate* statements

**Date:** 2026-09-22
**Scope:** `README.md`, `docs/paper/clfly-v1.md`, `docs/research_plan.md`
**Artifacts:** the fixing commit; no experiment was run for this

---

## 1. Why this was done

Five corrections landed in one session: the metric-instability trap, the ladder's headline
(42.2σ peak → plateau), "granularity beats biology" → "granularity locates you", the withdrawal
of *that* replacement, and finally the control-draw finding. Each correction rewrote the sections
it belonged to. The parts that no one rewrote were the **summaries of those sections** — counts,
one-line claims, headline phrases — and they had drifted.

## 2. What had drifted, exactly

| where | said | should say |
|---|---|---|
| paper §0 | "Six of our own earlier conclusions … artefacts of these **three** traps" | seven conclusions; **five** traps |
| paper §7 | "**Two** measurement traps" | five, with the unpaired-shape-test and single-draw-control traps added |
| paper §7 | retraction list ended at "replay is setting-dependent" | plus the withdrawal of "granularity locates you, biology sets the height" |
| README | a hardcoded findings count (28, then 29) | **removed the count** — it drifts by construction, and it went stale a second time within this very fire |
| plan, programme table | "up to **42.2σ**" | 2.8–7.9σ once the control-draw component is included |
| paper §7 limits | coarse end described as "`pool64`/`pool128` **share a constrained_fraction**" | `pool32` and `pool64` are **bit-identical partitions**; `pool128` is a 2-group partition; six distinct partitions across eight rungs |

## 3. The pattern

**Counts and headline phrases are what go stale; the prose around them does not.** The detailed
sections were fine, because each correction rewrote them wholesale. An aggregate statement — "N of
our own conclusions", "two traps", "up to Xσ" — is a *derived* quantity that lives outside the
section being corrected, so nothing forces it to move when the section does. The ladder's headline
phrase was the worst case: it appeared in four files, and the second correction had to chase it
through all four.

The practical rule that falls out: after a correction, **grep for the aggregate forms** rather than
re-reading the documents. The forms that have actually gone stale here are counts
(`\b(five|six|seven) of our own\b`, `\b[0-9]+ of them\b`), extrema (`up to [0-9.]+σ`), and the
headline phrases themselves. Re-reading would not have found the `42.2σ` row in a programme table.

## 4. One drift was load-bearing, not cosmetic

The limits section claimed **"`side` is robustly strong at both scales"**, which had survived every
earlier correction. `side` is a **4-group** partition, i.e. exactly the coarse regime where `e12`
measured a draw sd of ~1.1e-3 against a seed sem of ~2e-4. Its σ at d = 1307 (28.78) and d = 3150
(11.87) are single-draw figures and are inflated several-fold. A claim that looked like the most
*robust* survivor in the paper is one of the ones most affected by the newest finding — because
robustness was being read off a number that the correction had not reached. The bullet now says so.

That is the same failure mode as the rest of this project's traps, one level up: a conclusion that
is safe *in the regime we were paying attention to* and silently wrong outside it. Here the regime
was "sections we rewrote".

## 5. Limits

- This is a self-audit with grep. It can show the greppable aggregate forms are now consistent; it
  cannot show the absence of drift in prose. A reader who finds a contradiction should treat it as
  a bug in this file's claim.
- The counts it fixed are themselves date-stamped: "seven retractions" and "29 findings" will be
  wrong the next time either rises. That is the argument for `docs/findings/` being the record and
  the README being a summary that is allowed to lag by one fire.
