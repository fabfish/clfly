# The plan's cited numbers are three times less localised than the paper's, and its two exceptions are its own arithmetic

**Date:** 2026-09-25
**Read of:** `docs/research_plan.md` with the audit `e192` built for the paper — the same question, on the project's
working document: is a number the document states, beside a findings citation, in that finding?
**Instrument:** `experiments/e192_paper_numbers.py` (unchanged logic; it takes `--paper`, and now names the document
and warns about the class this run introduced).

---

## 1. The two documents side by side

| | the paper (`clfly-v1.md`) | **the plan (`research_plan.md`)** |
|---|---|---|
| sentences carrying a number **and** a findings citation | 104 | **185** |
| numbers in them | 330 | **804** |
| present in the finding the sentence cites | 296 (90%) | **526 (65%)** |
| absent there, present in **another** finding | 34 (**10%**) | **276 (34%)** |
| absent from the whole findings corpus | **0** | **2** |

**So the plan's numbers are three times less localised by their own citations than the paper's** — 34% against 10% —
and the reason is structural rather than a defect: a plan row summarises a whole experiment, so it quotes several
findings at once and its citation anchors the *row* while the numbers come from wherever they were measured. The
paper's sentences are written against one finding each. Both rates are now measured; the plan's is the expected
one for a document whose job is to aggregate.

## 2. The two members that no finding carries, read by hand

The class is the audit's sharpest — a number stated with a citation that the entire corpus lacks — so both members
were read rather than reported:

- **`1.5e-9`**, cited `2026-09-24-replays-margin-tracks-the-baselines-forgetting.md`: the row says *the two `replay`
  arms' mean accuracies agree to **1.5e-9***. That is **arithmetic performed in the row** on two artifacts' numbers —
  an agreement between arms, not a claim quoted from the finding.
- **`40.5`**, cited by the row that quotes this audit's own finding: it is the **heartbeat's projection**
  ("projected 40.5 min") from `e193`'s launch, i.e. a number that describes the run rather than a measured result.

**So the class is not empty by accident and not populated by defects either: on a working document it contains the
document's own arithmetic**, and the measured consequence is that this audit's exit code should not be a gate on the
plan. The script now says so in print — it names the document it read, and when the class is non-empty it points out
that a run's projection and an in-place agreement live there — and the paper's gate remains the one that means
"nothing the document claims is unsupported".

## 3. What this licenses, and the class it adds

- **licensed**: *the plan's citations localise their rows, not their numbers, at a measured rate of 34%; the paper's
  localise their numbers at 90%*; and *no number in either document is unsupported except two in the plan that are
  that document's own arithmetic*.
- **the class this run adds to the audit's own record**: "derived in place" is indistinguishable, by this method,
  from "unsupported". That is the fourth time in this audit thread that an instrument's first output on a new
  document was its own limitation rather than the document's defect (the paper's rounding, the paper's
  multi-finding sentences, and `e185`'s three collector defects were the others), which is why every run of this
  family now carries its false-positive classes in print.
- **scope**: the check is textual — *appears*, not *means the same thing* — and a findings document quotes superseded
  numbers in order to correct them, so presence is necessary and not sufficient. Nothing here says the plan's 276
  "elsewhere" numbers are wrong; it says their citations do not point at them.

## Reproduce

```
uv run python -m experiments.e192_paper_numbers                        # the paper: 330 numbers, 0 unsupported, exit 0
uv run python -m experiments.e192_paper_numbers --paper docs/research_plan.md   # the plan: 804, 2, informational
uv run pytest tests/test_e192_paper_numbers.py -q
```
