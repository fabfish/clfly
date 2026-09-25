# The vocabulary was three spellings, and the third was one level down where my own check could not see it

*2026-09-25, third pass over the same unit. Code: `e205` (vocabulary 2 → 3, the scan now descends into
declared blocks, and a plumbing census added), `duration_seconds` in `clfly/bench/artifacts.py`. Artifacts read:
the 331 under `runs/` carrying a `config`, at 23:04.*

## 1. The near-miss was a spelling

The first version of `e205` found exactly three artifacts carrying a duration-shaped key outside its declared
vocabulary, decided they were a *"near-miss to inspect rather than to count"*, and printed them without
counting: `e6_predictor` (1073.4 s), `e6_predictor_6` (3216.0 s), `e64_predictor_6_perseed` (4964.5 s). That
phrase is borrowed from `e194`, where it is right — a claim whose level has not landed is not a defect — and it
is exactly wrong here: **a near-miss declared by the check that exists to find unknown spellings is a
spelling.** They are `summary = {"time_s": ...}`, written by the predictor analyses, and they hold **2.6 h** of
compute.

And the module's own vocabulary check could not have caught them, because it scanned the **top level** of each
file while the key sits one level down inside a block. So the check that exists to prevent a hand-written
vocabulary from missing a spelling (the `e201` failure, whose name is in its own docstring) shipped with a
hand-written vocabulary that missed one, and the scan's scope was the reason. This is the third time in one
evening that the defect was one level below the last audit — `e201`'s field list, `e160`'s environment, and
now this module's own scan — and the first time the audit was itself the thing audited.

**The repairs, both of them mechanical:**

- the vocabulary is a list of **dotted paths**: `timing_s`, `timing.total_s`, `summary.time_s`;
- the scan descends into the blocks a corpus can hide a duration in (`timing`, `summary`, `environment`) and
  prints its vocabulary on every run, so the next spelling is visible rather than inferred.

## 2. The census, now three-way

| spelling | artifacts | hours | share | who writes it |
|---|---|---|---|---|
| `timing_s` | 300 | 129.8 | 85.3% | the trained runners (all carry `methods`) |
| `timing.total_s` | 13 | 19.9 | 13.1% | the analytic line (none carries `methods`) |
| `summary.time_s` | 3 | 2.6 | 1.7% | the predictor analyses (`e6`, `e64`), one level down |

**316 of 331 artifacts carry a duration** (was reported as 311 of 329 before the third spelling was read; the
rest of the movement is the two smoke artifacts of the previous pass) and **none carries two spellings**, so the
spelling remains a property of the instrument. The blindness is three-way and asymmetric:

- a reader keying on `timing_s` cannot see **16** artifacts, **22.4 h = 14.7%** of the record's compute;
- one keying on `timing.total_s` cannot see **303** artifacts, **86.9%**;
- one keying on `summary.time_s` cannot see **313**, **98.3%**.

The third spelling's three artifacts are the smallest population and the largest per-artifact cost among them
(0.3–1.4 h each, against a median artifact of 11.7 min), which is the same asymmetry as before: the spelling
nothing reads is the one the expensive things use.

## 3. `save_theta` generalised, and the question closed

The previous pass found that the four no-duration artifacts each carry a key their own parser does not define
(`save_theta`, which two runners assign into their own namespace at runtime). The obvious next question is how
many such keys the corpus has and where they are, so `e205` now asks it of **every** artifact rather than only
of the gaps:

> **artifacts carrying a key their own best parser does not define: 6 of 331, over 1 key (`save_theta`), from 2
> runners** (`e122_path_geometry.py` and `e124_barrier_distribution.py`).

So the pattern is real, small and **closed**: one key, two runners, six artifacts, all accounted for. That
closes the question the previous pass opened — the plumbing is not a widespread property of this corpus's
`config`s, and `e172`'s containment test fails on exactly those six. It is reported rather than counted as a
violation, because a runner injecting an attribute its shared training function expects is a legitimate pattern
and a check that fires on it would be red for a design decision rather than for a defect.

## 4. What this changes, and what it does not

- `duration_seconds` reads the third spelling, so `e169`'s start-time clock and `e38`'s cost table can now date
  and price the three predictor artifacts. **No published number moves**: none of the three is in `e169`'s
  scope (a 3-key config, no `methods`), and `e38`'s table names its eight runs explicitly. As with the previous
  pass, the repair's value is in what it makes readable rather than in what it corrects.
- The check's exit code is still **0**, now over a three-spelling vocabulary, and its false-negative class is
  declared and tested: `cpu_time_s` starts with `cpu`, so the name rule does not see it — and it names a
  different quantity (CPU time against wall clock) anyway.

## 5. The lesson worth carrying

Three passes over one quantity: the first found two spellings and two readers that did not know about each
other; the second corrected a wrong writer attribution and a wrong explanation of an injected key; the third
found that the vocabulary was one spelling larger than declared, and that the reason was the *scan's scope*
rather than the corpus. **Each pass was prompted by taking the previous pass's own output literally** — the
declaration that disagreed with the derivation, the near-miss that had been printed instead of counted. The
operative habit, if this has one: a check's own printed exceptions are evidence about the check.
