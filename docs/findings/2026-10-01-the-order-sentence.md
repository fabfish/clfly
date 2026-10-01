# The order sentence: the block promised a fixed order, and the runs that broke it say what fixing it costs

*2026-10-01 15:58. Runs: **none new** — `experiments/e320_the_order_sentence.py` reads the FlyCL v0 block's
reference-framework paragraph and the corpus's record of orders, writing `runs/e320_the_order_sentence.json`. Seconds.*

## 1. The sentence a benchmark's users act on

The block ends with:

> Reference framework: `clfly/bench/` with fixed task orders and seeds, so numbers are comparable across methods — a
> shared protocol that CL-for-SNN work currently lacks.

`e302`'s M4 read the corpus against it and found it **trivially** true: every artifact recorded its suite's own naming
order, so the order was a variable with one value. `e310` measured what varying it would cost, and `e315` to `e319`
varied it — five units and ten runs. **The sentence had not been re-read since.**

## 2. As found: two of three

| | as found | after the correction |
|---|---|---|
| **O1** the paragraph carries an order cue and a comparability cue | **MET** | MET |
| **O2** and it says what the order moves | **FALSIFIER FIRED** — no cue, no unit | MET, two cues and two units |
| **O3** and the corpus holds a permuted suite | **MET** — two suites in two orders | MET |

So the block promised **fixed orders so numbers are comparable** and told a reader **nothing about what fixing it
costs**, while the corpus had already stopped holding one order per suite.

## 3. The correction

The paragraph gains a **scoped 2026-10-01** clause: the order is fixed by convention and not because it cannot move;
reversing a suite's order moves **the arms that read a penalty** toward the position that trains each task first, by
up to **4.82 sigma**, and leaves the arms that read none alone — `naive`'s two contrasts identical to six decimals at
every penalty strength — while the penalty's own **strength stops mattering at the first notch**, so what an order
costs is a property of *whether* an arm regularises toward a basis and not of how hard (`e317`, `e319`).

The claims are stated as the **invariant the block now satisfies**, as `e298` stated the paper's and `e307` the
README's: an edit that drops the currency turns this unit red. The as-found counts live here rather than in the
artifact.

## 4. What it cannot do

**The cues are lexical**, so a clause saying the same thing in other words reads as absent and the count is a lower
bound — `e298`'s caveat applies unchanged. **This is a claim about text**: O2 verifies that a clause exists and not
that its numbers are right, which is `e315` to `e319`'s business. **O3 is a census of the corpus as it stands** and
not about a fresh clone, which has no artifacts at all. **The unit of reading is the paragraph and not the sentence**,
which is why a scope clause added after the promise is visible to the detector: a detector that read one sentence
would declare its own correction invisible, and `e298` recorded exactly that defect when its splitter merged a
paragraph into its predecessor.
