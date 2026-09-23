# The location audit was reading half of each artifact

**Date:** 2026-09-24
**Script:** `experiments/e105_table_audit.py` — `ARRAY_FIELDS`, `corpus_index`, `audit_table`, section 2's report.
**Tests:** `tests/test_table_audit.py`, three new cases (29 pass in the file).
**Trigger:** chasing the two most-resolved tables in the audit's own listing — 97% and 92% — to see whether their
single unmatched cells were defects. **They were not: the numbers were in the artifacts, in a field the check did
not read.**

---

## 1. What the unmatched cells were

The paper prints, for the body's motion at three read-outs, a column headed **mean θ drift**: **0.0195**, 0.0391,
**0.0493**. The audit reported 0.0195 and 0.0493 as unmatched and 0.0391 as located. The artifacts say:

```
runs/e107_drift_r0.json    agg[theta_drift] = [0.0197, 0.0187, 0.0201]   mean 0.0195
runs/e107_drift_r32.json   agg[theta_drift] = [0.0510, 0.0477, 0.0493]   mean 0.0493
```

**The paper's column is the mean over the three tasks, and two of its three values do not equal any stored
entry — while the third does, exactly, by coincidence.** That is the signature: `ARRAY_FIELDS` named three of the
arrays the runner writes (`learned`, `forgetting_per_task`, `final_per_task`) and **not** `theta_drift`,
`bias_step`, `bias_from_zero` or `full_train_loss`. A table of element-means therefore reads as unexplained, and
a table whose element *happens* to equal the mean reads as explained.

## 2. The change, and it is in two parts

- **The index now reads every array the runner writes.** The four missing fields are in `ARRAY_FIELDS`.
- **A second index holds one derived entry per array: its mean.** It is consulted **only** for tokens the field
  index misses, so nothing that located before locates differently, and the report keeps the answers apart:
  `matched`, **`aggregate`**, `unmatched`, printed as three numbers with the aggregate cells listed under
  *"only as a mean:"*.

**Measured on the paper's 27 tables, before and after**: unmatched cells **211 → 199**, with **12 cells in 8
tables** now resolving as an array's mean; verdicts move from `{mixed 19, nothing located 5, all located 3}` to
`{mixed 20, nothing located 3, all located 3, all located or aggregated 1}`; and one table — the
`run | forgetting | sd (per repeat) | accuracy | accuracy sd | drift` table at lines 1355-1358 — becomes **fully
resolved** (7 located, 3 as means, 0 unmatched).

## 3. Why this is the direction to be suspicious of, and what is done about it

**The change makes the corpus look better**, which is the direction that deserves the most suspicion and the
reason the aggregate bucket is a third bucket rather than a merge: "an artifact **field holds** this number" and
"an artifact **averages to** this number" are different claims, and only the first is what the location listing
was ever a statement about. Three safeguards, each with a test:

- **a field match is never displaced** by the looser index (`matched` is consulted first, and a test asserts it
  when both would answer);
- **the aggregate index is opt-in**, so calling the auditor without it reproduces the old answer exactly (a test
  asserts the same cell is `unmatched` that way);
- **the residual count is printed beside the new one** — 199 unmatched tokens remain, and this fire explains 12
  of the previous 211, not the class.

## 4. What the remaining unmatched cells are, and what they are not

In the same tables the unmatched residues are things like **−0.0111**, **−0.0014** and the σ's in §4.2's method
table. **These are differences and standard errors, i.e. the class the check's own docstring already excludes** —
*"a sigma, a ratio and a cost are all derived"* — and this fire adds a **second named derived class: an aggregate
of a stored array**. **And an aggregate is not evidence of backing in the sense that matters**: the mean of the
wrong field is still the wrong number, and the audit's job in this section is to say which cells resolve rather
than to certify them. So nothing here changes what the audit *convicts*; it changes only how many cells it
declines to explain, and it explains 12 more.

## 5. The general shape, which is the third instance today

Twice already this session a check's *coverage* was the defect rather than its arithmetic — `check (a)`
false-flagging a column it could not check, and the corpus mode skipping every finding without rows. **This is the
third: a listing whose subject is "every number an artifact records" read four scalars and three of seven
arrays.** In each case the count was right about what it looked at and wrong about its subject, and in each case
the repair was to widen the subject and to print the widened part separately rather than folding it in.
