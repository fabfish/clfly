# The baseline list had three words and two of them were real

**Date:** 2026-09-25
**Read of:** `docs/research_plan.md`'s benchmark block, every `runs/*.json`'s `methods`, every runner's parser
through `e172`'s registry, and the module tree.
**Instrument:** `experiments/e185_benchmark_spec_audit.py`, whose baseline arm is rebuilt here (tests in
`tests/test_e185_benchmark_spec_audit.py`).

---

## 1. The check was matching a word, and the word was a baseline that does not exist

`e185` verifies the benchmark block against the code. Its baseline arm admitted `naive`, `replay` and the rest of
the run methods on **evidence** — every artifact's own `config.methods` — and then exempted three names by fiat:
`CONTROL_WORDS = ("oracle", "frozen", "joint")`. Two of those are real:

- `frozen` — the flag `--frozen-body` exists in the parsers, and artifacts carry `frozen_body: true`;
- `oracle` — `clfly/bench/oracle.py` implements the Kalman/RTS reference line.

**`joint` is not.** `grep joint` over `clfly/` and `experiments/` returns one local variable in
`e36_geometry_carrier.py` (a product of p-values, printed as "Joint, both topologies independently") and the
checker's own word list. No module, no flag, and no artifact has ever run it: the corpus's methods are exactly
**`naive` (129 artifacts), `ewc` (49), `ewc-block-rand` (41), `ewc-block` (38) and `replay` (34)**. So the block
offered a **joint-training upper bound** for two days, and the check that exists to catch exactly that agreed with
it, because a three-word list is not evidence.

The three words are replaced by an evidence map: a control counts when a **flag** exists in some runner's parser
(read from `e172`'s syntax-derived registry) or a **module** carries its name. The live map is now
`frozen ← --frozen-body`, `replay ← --replay-batch`, `oracle ← clfly/bench/oracle.py`, and `joint` resolves to
nothing, so the block no longer offers it — it is named in the block's prose as proposed, beside `SI`, `MAS` and
`Online-EWC`.

## 2. And the baseline arm had been reading nothing for three fires

Rebuilding the arm exposed two defects in the list collector, one of which is worse than the phantom baseline
because it made the zero vacuous:

- **`marked()` broke out of the loop at the first prose line.** The function collects the items of the list a mark
  introduces and stops at the first line that is not an item — but it *stopped scanning the block*, so **every mark
  after a paragraph was invisible**. The implemented suite's list is followed by a paragraph, so the proposed and
  baseline marks were never reached: on the live block those two arms returned an empty list and reported a clean
  zero. A synthetic block with no prose between its lists cannot show it, which is why the bug survived its own
  tests; what found it was asking the baseline arm for its evidence and getting none.
- **A wrapped bullet ended the list.** An indented continuation line was treated as prose, so only the *first* item
  of the proposed list was ever read. With both fixed the three lists read as **3 / 12 / 6 items**.

One more fix came out of the same rebuild, and it is a small one with a principle in it: a **path inside a bullet**
(the block writes "`oracle` — the Kalman/RTS reference line, implemented in `clfly/bench/oracle.py`") is that
bullet's *evidence* rather than another baseline claim, so tokens containing `/` or ending in `.py`/`.json` are
skipped. It was the first flag the revived arm produced.

**The live gate now asserts the baseline list is non-empty before believing its verdict**, which is the guard
against this whole class: a check whose input list is empty reports success, and a denominator printed beside the
zero would have shown it three fires earlier.

## 3. Falsifiers and scope

- The claim that `joint` does not exist dies on any module, flag or artifact carrying the token in a joint-training
  sense — the check's evidence map is derived from the parser registry and the module tree, and the methods come
  from every artifact's own `config`. What the map *cannot* see is a joint upper bound implemented somewhere that
  is neither a runner flag nor a module name (an inline loop in a script, say): the honest statement is "nothing
  offers it, by the two forms of evidence this check reads".
- The collector is deliberately strict: **a list ends at the first unindented prose line**, so a mark whose bullets
  are separated from the mark by a paragraph reads as empty. That is a *contract* on the block, and the block now
  satisfies it — but it is also a way the check could go quiet again, which is why the non-empty assertion is in the
  test rather than in a comment.
- Scope: this is about the **block's** claims and the **corpus's** methods. It says nothing about whether a
  joint-training upper bound is a good idea — only that the block offered one that has never been built.

## Reproduce

```
uv run python -m experiments.e185_benchmark_spec_audit     # 0 flags, with the control evidence printed
uv run pytest tests/test_e185_benchmark_spec_audit.py -q  # 12 tests, 5 of them new here
```
