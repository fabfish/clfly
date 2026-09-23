# The findings corpus is clean on every structured surface — and the one known defect is invisible to all of them

**Date:** 2026-09-23
**Script:** `experiments/e97_findings_corpus_audit.py`
**Artifacts:** `runs/e97_findings_corpus_audit.json`
**Method:** a mechanical audit of all **107** documents under `docs/findings/`: whether every `runs/` file they
cite exists, whether each `**Setup:**` line agrees with its named artifact's `config` on circuit size and
seed count, and how many declare an artifact at all.
**Context:** `docs/findings/2026-09-23-the-fisher-batch-sweep-is-a-stitch-of-first-replicates.md` (the `e8c`
defect, found by hand yesterday); `docs/findings/2026-09-23-the-status-word-is-a-header-nobody-re-derives.md`
(the plan table's audit, one surface over).

---

## 0. The audit's first finding was about itself

Two things about this document are worth stating before its results. It was written **without an
`**Artifacts:**` line**, which the audit counts as machine-uncheckable — so the audit's first act on itself was
to add one. And it **cites `runs/e10_smoke.json` as an example of a missing file**, which makes it a second
existence flag: a document that names a path in order to discuss its absence is indistinguishable, to a
scanner, from one that cites it as evidence. **Both flags in the table below are therefore documented
absences, and the count of findings citing a live artifact that is missing is zero** — but that sentence
required reading both documents, which is the whole point of §2.

---

## 1. The result, which is a positive one

**The corpus is clean on everything a machine can check.**

| check | result |
|---|---|
| documents | **107** |
| declare an `**Artifacts:**` line | **86** |
| cite a `runs/` file that does not exist | **2 flags, and both are documented absences** |
| `**Setup:**` disagrees with the named artifact's `config` on circuit size or seeds | **0** |

The two existence flags are `2026-09-22-synapse-annotation-ladder.md`, whose own Artifacts line reads
`` `runs/e10_rung_*.json` (in flight), `runs/e10_smoke.json` (aborted) `` — **the absence is documented** — and
**this document**, which cites the same path as an example (§0). So the true count of findings citing a
missing live artifact is **zero**.

So after a week in which this project's audits found a hybrid range in the abstract, a concentration range
read off half a table, two denominators borrowed from the wrong circuit, a proxy table applied to four
configurations it did not match, a sweep stitched from first replicates, and a status word that contradicted
its own cell — **the corpus's own provenance is intact.** That is worth recording for its own sake: the
paper's reproducibility section can say that every artifact any finding names is on disk and agrees with the
finding's stated configuration, at 86 of 107 documents.

## 2. And the checker is blind to the defect it was built for

`e8c`'s defect was that its named artifact no longer held the sweep it reported. A check for that kind of
thing is the natural next row of the table above, so it was written — and then **validated against the known
case**, which is the step that matters:

```
Setup    : circuit `mb+cx+al@n1307`, 3 tasks, λ = 0.1, 500 iterations, chance 0.25
Artifacts: `runs/e8_fisher_batches.json`

regex cs claim    -> []          (the Setup says "@n1307", not "cs = 800")
regex seeds claim -> []          (the sweep claim is "single seed", which carries no digit)
```

**The check returns nothing on the very finding it was modelled on**, and it returns nothing because
`e8c`'s drift lives in a **body sentence** — *"single seed, λ = 0.1, sweeping the Fisher batch count"* —
while its metadata lines are self-consistent. A scan of metadata lines cannot reach it, and neither could a
sweep-detector restricted to the `Setup:` line: run that way it finds **0 findings in the corpus**, because
no document declares a sweep in its metadata.

**A checker validated only on a clean corpus reports "0 problems found", and that is indistinguishable from
blindness.** The known positive is what separates the two, and this project did not have one for the plan
table either until `e85` found eight rows by hand. Stating a check's sensitivity against a case it *should*
catch is therefore not optional polish; without it, its zero is uninterpretable.

## 3. What this says about where further automated audits can pay

The two failures found this week in *prose* —
`e8c`'s "sweeping the Fisher batch count" and C2b's "`side` has never been run" sitting above its own Update
paragraph — were both found by **reading a claim next to the claim it is about**, not by scanning. Every
surface that can be scanned has now been scanned: artifacts exist, configs agree, the plan table's status
column re-derives, the abstract's figures were checked against the body, and the white-space-insensitive
search is in the method list. **Existence and configuration checks on this corpus have low remaining
expected yield, and the residual risk is in sentences.**

Two concrete limitations to carry forward rather than rediscover:

- **21 of 107 findings (20%) declare no artifact at all**, so no mechanical check can even start on them.
  Their dates are 1 from 09-20, 12 from 09-22 and 8 from 09-23, i.e. it is not a habit that got fixed — and
  **this document was one of them until the audit was run on it** (§0), which is a fair illustration of how
  easy the omission is. A
  finding that states a number and names no artifact is unfalsifiable by construction, and this corpus has
  twenty-one of them.
- **The one class of drift that remains reachable by machine is "right file, wrong content"**, and it is
  reachable only where a finding states its configuration in a form that can be compared — which is why the
  `Setup:` line matters and why a finding that omits it has thrown away the only handle a later check has.

## 4. The generalisable rule

**An absence claim needs three things, and this week produced one instance of each failing.**

1. **The whole listing, not a prefix** — `hits[:20]` and `hits` render identically, and a truncated scan
   nearly filed a wrong correction for the 55% evaluation floor.
2. **A positive control** — a checker that returns zero on a case it should catch is not a passing checker.
   This fire's config check returns zero on `e8c`, and only the known case reveals it.
3. **The claim's own scope printed beside the verdict** — the grid report's verdict gate printed `FAIL` for
   an unscored clause, then `PASS` on a partial set, before it was made to print
   `PENDING (d = 952 20/20, d = 1307 20/20, d = 1874 8/20)`.

All three are the same underlying requirement: **a report of nothing must carry the evidence of having
looked.** The third is now enforced in code; the first two are habits, and this document is their record.
