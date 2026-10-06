# The metrics against definitions: `e302`'s code arm was reading docstrings, and the one it blessed is a comment about a module nobody wrote

*2026-10-01 04:37. Runs: **none new** — `experiments/e303_the_metrics_against_definitions.py` re-reads the FlyCL v0
block's five metrics with every module's string and comment tokens removed, writing
`runs/e303_the_metrics_against_definitions.json`. Seconds.*

## 1. What `e302` counted, and why it was wrong

`e302` found four of the block's five metrics implemented, on an arm that counted a declared spelling **anywhere in a
module's text**. A docstring is text. Re-reading the same six spellings with Python's own tokenizer dropping every
`STRING` and `COMMENT` token moves two of them:

| metric | spelled form | in the text | in the code |
|---|---|---|---|
| average accuracy | `final_accuracy` | 109 | 2 |
| decomposed forgetting | `decompose_forgetting` | **1** | **0** |
| decomposed forgetting | `mean_forgetting` | 111 | 2 |
| backward transfer | `backward_transfer` | 0 | 0 |
| per-task observability spectrum | `observability` | **3** | **0** |
| pairwise task principal angles | `principal_angle` / `principal_angles` | 1 / 1 | 1 / 1 |

**R1 MET** — two of the six occur in the repository's documentation and in none of its code. **R2 MET** — the repaired
arm leaves **two of the five metrics implemented nowhere**, `backward transfer` and the per-task observability
spectrum, and the third that looks implemented is implemented **only through the conventional form the block
rejects**: `decomposed forgetting`'s only code spelling is `mean_forgetting`.

## 2. The exhibit, which is better than the count

`decompose_forgetting` occurs **once** in the whole repository, in `clfly/lgcl/model.py`'s `summarize`:

> NOTE: this metric rewards shrinkage bias — an estimator that pulls toward zero can score well on it while being
> wrong (LGCL v8 audit note). Use `clfly.lgcl.metrics.decompose_forgetting` when that matters.

**`clfly/lgcl/metrics.py` does not exist.** R3 MET, and this is the arm that sees the difference between a module
that implements a metric and a module that *defers* to one: the only reference to the metric the benchmark block was
written around is a comment pointing at a file nobody wrote, in the same breath as the sentence saying the metric the
corpus *does* store is the one that can be gamed.

The rule that finds it is worth stating because the obvious one does not: resolving the **longest prefix of the
dotted path that is a file** answers `clfly/lgcl/__init__.py` and blesses the reference. The module a dotted path
names is the path **minus its last component**, which is the attribute, so the test is whether `clfly/lgcl/metrics.py`
exists — and it does not.

## 3. What this costs `e302`

`e302`'s M1 stays MET: `backward transfer` really is implemented nowhere. Its *other* three verdicts are unaffected
in kind and one of them in degree — the per-task observability spectrum moves from implemented to implemented nowhere,
so the repaired reading is **two of five implemented, not four of five**. `e302`'s §5 recorded that its first arm read
its own spelling table as evidence; this is the same defect one level down, where the evidence was a *different*
module's documentation rather than its own, and it is the second time in two units that a lexical arm has been caught
blessing a word.

## 4. What it cannot do

**Counting tokens is not reading code.** A metric implemented through a computed name, a registry or a `getattr` reads
as absent here, and a comment on the line that defines something is evidence neither way. **`tokenize` can refuse a
file**, and a file that does not tokenise is returned to raw text and **reported** rather than counted — the fallback
is exactly the defect this unit exists to correct, so it is named in the artifact rather than left silent. **A
docstring is not nothing**: a module documented as computing a metric and not computing it is a different failure from
a module that never mentions it, and R3 is the arm that sees the difference, over one exhibit. **And this unit
re-reads `e302`'s five metrics and not the block itself**: the phrases and the spelling table are `e302`'s, so a
change to the block moves both, and a metric whose repository spelling is in neither table is outside both.

## 5. RE-READ 2026-10-01 05:12 — the module was written, and R3's falsifier fired on purpose

`e304` wrote `clfly/lgcl/metrics.py`, so the reference this unit's R3 rests on now resolves and the reading moves —
which is the outcome R3 was registered to detect, arriving as a **falsifier that fires because the defect was
repaired** rather than because the claim was wrong:

- `decompose_forgetting` is no longer prose only: **3 occurrences in code** across 5 in the text.
- **R1 stays MET** on the one spelling that is still documentation — `observability`, 3 occurrences in the text and
  0 in code — so the per-task observability spectrum is still implemented nowhere.
- **R2 stays MET**, unchanged: `backward transfer` and the per-task observability spectrum are the two metrics with
  no spelling in code, and `decomposed forgetting` is now implemented under **both** its spellings, the prescribed
  one and the conventional one.
- **R3 FIRES**: 0 dotted paths are written beside a prose-only spelling, so every module the prose names is on disk.

The unit's R3 was *"one of the prose-only mentions names a module that is not on disk"*, with *"the module it names
exists"* as its falsifier. It fired within the hour, by the repair it asked for
(`docs/findings/2026-10-01-the-decomposition-the-block-asked-for.md`).

## RE-READ 2026-10-03: the same carrier defect, one arm over

`e392`'s card names the block's metrics, and this unit counts each spelling twice -- once in a module's whole text
and once in the source with every string and comment stripped. The card's mention therefore landed in the **prose**
arm and in none of the code arm, and the prose-only list grew a second entry: `backward transfer`, in the card. That
is a module describing a metric, not the repository computing one. The carriers are now excluded from the evidence
with the auditors this unit delegates to, and **the prose-only list is the observability spectrum alone again**.

## RE-READ 2026-10-06: the closed-loop suite joins the suites that record two orders

`e436` rolled the card's world -- the closed-loop suite -- both ways, so the corpus now holds a **third** suite whose
artifacts record two orders, beside the overlap suite (`e315`) and the assembly suite (`e316`, `e317`). This unit's
live check had carried the count as the exact two those suites gave, which is a count that grows with the corpus rather
than a claim, so the test now asserts **at least two** and checks **every** such pair's two orders as permutations of
one task set -- the shape M4 fired into, made robust to the next suite anyone permutes. The claim itself is unchanged:
M4 is still the falsifier `e315` ended.
