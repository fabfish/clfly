# The repair destroyed the diagnostic's evidence

**Date:** 2026-09-23
**Scripts:** `experiments/e64_predictor_per_seed.py` (repaired), `experiments/e93_cs300_draw_sd_upgrade.py`
(its "before" column rebuilt from primary sources)
**Artifacts:** `runs/e64_predictor_per_seed_analysis.json`, `runs/e93_cs300_draw_sd_upgrade.json`
**Context:** `docs/findings/2026-09-23-the-predictors-denominators-were-borrowed-and-the-borrowing-was-optimistic.md`
(`e94`, which measured the correct denominators), `...-the-predictors-denominators-came-from-the-other-circuit.md`
(`e93`, which found the borrowing).

---

## 1. The fix the audit asked for, applied

`e93` named the repair: `DRAW_SD_SOURCES` was keyed by rung and not by circuit size, so four of `e6`'s five
conditions were being handed d = 1307 numbers while they ran at cs = 300. `e94` then measured all twenty of
those pairs at their own configuration and the count moved **21 → 20**.

Until this fire, the corrected number lived **only** in `e94`'s diagnostic while `e64_predictor_per_seed.py`
— the script that produced the published count — still produced the old one. **Two scripts in one repository
disagreed about the same quantity**, which is the same shape this week's audits kept finding in documents,
one level further in.

The repair keys the lookup on the condition as well, with an explicit `CONDITION_CIRCUIT` map so the fallback
can be *checked* rather than assumed to suit:

```python
if label == "baseline":                      # e86 measured this one, and only this one
    path = Path(f"runs/e86_drawsd_cs300_{rung}_min1.json")
...
table = DRAW_SD_SOURCES.get(rung)
if table is not None and CONDITION_CIRCUIT.get(label) == SHARED_TABLE_CIRCUIT:
    return Path(table[0]), table[1], SHARED_TABLE_CIRCUIT
return None, None, None                      # a *pending* denominator, not a substitute
```

`e64` now reports **20 of 25 clearing 2σ and 19 of 20 called correctly**, the miss being
`rewired-swap2`/`cell_class` — **identical to `e94`'s independent re-derivation.** The paper's corrected
figure is therefore reproducible from the code that produced the original one.

## 2. And the repair reproduced the bug it was removing — inside itself

The first version of `draw_source` looked for `e86`'s files by rung **without checking the label**:

```python
for path, src in ((Path(f"runs/e86_drawsd_cs300_{rung}_min1.json"), "e86, cs = 300"),
                  (Path(f"runs/e94_drawsd_{label}_{rung}_min1.json"), "e94, cs = 300")):
```

so `larger-circuit` — which ran at **cs = 800** — picked up a **cs = 300** measurement. That is exactly the
defect the function was written to remove, re-introduced by the function's own lookup in the same
configuration-blind form. **What caught it was an assertion added at the call site**, which is the only
reason it never reached a number:

```
AssertionError: larger-circuit/side: draw sd from circuit 300 but the condition ran at 800
```

So the guard is worth its line: the mistake's *first* instance took a week of audits to find by hand, and its
second instance was caught by the compiler of my own intent on the first run. **A repair is a fresh
opportunity to make the original mistake**, and a repair that carries a check for the property being repaired
catches it.

## 3. And the repair blinded the diagnostic that documented the defect

`e93`'s job is to report the defect: for each rung, the cs = 300 measurement against **the value `e64` used**.
It read that second column from `pairs[...]["draw_sd"]` in `runs/e64_predictor_per_seed_analysis.json` — the
live output of the producer it documents. After the repair, that artifact carries the **corrected** values, so
the run printed:

```
side                0.0003246 | 0.0003246   1.00
cell_class          0.001247  | 0.001247    1.00
...
```

**Every ratio 1.00. The diagnostic went blind the moment the defect was repaired**, and reported it as
agreement rather than as its own loss of function — which is the same failure this project keeps meeting in
another form: a tool that cannot see a thing reports that the thing is not there.

`runs/` was not a fallback either, because **the same re-run overwrote `e93`'s own pre-fix output** — the
artifact that held the borrowed table. So the only remaining copies of "what `e64` used to say" were the
findings prose and the five **primary source artifacts** that the borrowed table was itself read from
(`e67`, `e17`, `e17b`), which the repair did not touch.

**The durable form is to read the primary sources**, and `e93` now does: `BORROWED_SOURCES` names the same
five artifacts `e64` originally consulted, so the "before" column is reconstructed from the measurements the
defect consisted of *misreading* rather than from the output of the thing that was wrong. Its columns read
**21 of 25 (borrowed) against 21 of 25 (baseline repaired alone)**, with the full four-condition correction
delegated to `e94` — and one more contamination was caught while doing this: the "after" column had silently
become the *full* correction, because `e64` now writes corrected values into the field the column read for the
other three conditions. **A column labelled "baseline only" has to be made to be baseline-only.**

## 4. The rule

**A repair destroys the evidence of the defect, and the record of "what it used to say" must not live in any
artifact the repair overwrites.**

This is rule 22's family with the sign reversed. Everything in this project's audit discipline assumes the
artifact is the durable record and the *document* drifts. Here the document was right, the artifact was the
thing being corrected, and correcting it deleted the only machine-readable account of what had been wrong —
including, in this case, the diagnostic's own output. Three consequences worth carrying:

- **A diagnostic's "before" column must be reconstructible from immutables** — primary measurements, or
  prose — and never from the producer's live output. `e93` now reads `e67`/`e17`/`e17b`.
- **Fixing a producer is not finished until its consumers are re-read**, because a consumer that reads the
  producer for the *old* value will silently report the new one. The tell is a column that suddenly reads
  1.00 or an unchanged count.
- **And the fix belongs in the producer, not in a second script.** Between yesterday and today the repository
  held two contradictory values for one published quantity; a reader running the script that produced the
  paper's number would have got the optimistic one.
