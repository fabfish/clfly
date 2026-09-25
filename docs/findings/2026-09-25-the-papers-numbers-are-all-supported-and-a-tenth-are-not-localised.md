# Every number the paper states with a citation is in the findings corpus — and 34 of them are in the *wrong* finding

**Date:** 2026-09-25
**Read of:** `docs/paper/clfly-v1.md` (256 k characters) against `docs/findings/*.md`.
**Instrument:** `experiments/e192_paper_numbers.py`, tested in `tests/test_e192_paper_numbers.py`.

---

## 1. The relation nobody had checked

`e97` asks whether every `runs/` file the **paper** cites exists, and whether the commands it names resolve to real
modules and flags. `e105` checks the numbers inside **findings'** tables. Nothing checked the relation a reader of
the paper actually relies on: **a number the paper states, in a sentence that cites a finding, is a number that
finding contains.**

Sentences carry no structure to lean on, so the audit's own rules had to be measured before its result meant
anything, and two of them are classes rather than conveniences:

- **Precision.** The paper quotes `-0.0854` where the finding has `-0.08542`. A substring test calls that
  unsupported, and under it the strictest class -- numbers absent from the *entire* findings corpus -- contained
  **one** entry. The rule used instead is that a quoted number is supported when a **number in the source rounds to
  it at the quoted precision**, and with that rule the class is **0**. A rule that turned a rounding into a finding
  would have been the audit's own defect, which is the third time in this project's audit thread that the first
  version's output was its own error.
- **Which citation a number belongs to.** A sentence cites a finding for its *claim* and may quote numbers another
  finding computed. Those are reported as their own class with the file each number was found in, and are **not**
  failures.

## 2. The result

| | |
|---|---|
| sentences carrying a number **and** a findings citation | **104** |
| numbers in them | **330** |
| present in the finding the sentence cites | **296** |
| absent there, present in **another** finding | **34** |
| **absent from the whole findings corpus** | **0** |

So the paper's arithmetic is fully supported by the corpus, and **34 of its quoted numbers are not localised by the
citation beside them** -- the class that a reader who followed the citation would not find. Samples, with the file
the number actually appears in:

| number | the sentence cites | the number is in |
|---|---|---|
| `-0.0854` | `2026-09-24-with-the-channel-frozen-in-every-arm...` | `2026-09-22-lambda-tuning-negative.md` |
| `0.0129` | `2026-09-24-with-the-channel-frozen-in-every-arm...` | `2026-09-22-draw-budget.md` |
| `0.9139` | `2026-09-23-the-frozen-body-control-is-in-no-penalty...` | `2026-09-22-the-replay-result-has-no-artifact.md` |
| `0.0147` | `2026-09-23-the-frozen-body-control-is-in-no-penalty...` | `2026-09-22-scale-robustness-d3150.md` |
| `-0.0521` | `2026-09-23-the-frozen-body-control-is-in-no-penalty...` | `2026-09-23-the-replay-result-reproduces.md` |

**One caveat, because the table would otherwise read as stronger than it is**: the "found in" column names the
**first** match in a fixed file order, and common numbers (4.7, 0.0147) are carried by several findings. So the
class is exactly "not localised by the citation beside it", and the column is one witness rather than the source.

## 3. What this does and does not license

- **It is not "the paper is right."** The check is textual: it asks whether the number *appears* in a finding, not
  whether the finding's number means the same thing or came from the same artifact. A number can appear in a
  finding's prose as a *refuted* value -- this project's findings quote superseded numbers in order to correct them
  -- so "present" is necessary and not sufficient.
- **The middle class is a documentation question, not a defect.** 34 of 330 is 10%, and the pattern is a sentence
  with several numbers: the citation anchors the claim and the numbers come from two or three findings. Making the
  citation per-number would be worse prose for a reader and better for a machine; the honest version is that the
  class is *counted and sampled*, which is what this finding does.
- **What would falsify §2**: any number in a cited sentence that no finding carries -- the live test asserts the
  class is empty, so a new paper number without a finding fails the gate rather than passing quietly.

## Reproduce

```
uv run python -m experiments.e192_paper_numbers                 # 104 sentences, 330 numbers, 0 unsupported
uv run pytest tests/test_e192_paper_numbers.py -q               # 6 tests, one per rule and one per class
```
