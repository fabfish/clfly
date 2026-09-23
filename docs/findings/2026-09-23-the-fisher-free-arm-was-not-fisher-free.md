# The Fisher-free arm was not Fisher-free, and the flag went on the reproducible point

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py`, `e8_hardened_basis`'s configuration; artifacts
`runs/e101_rate_fb32.json`, `runs/e102_replayonly_fb8.json`, `runs/e102_replayonly_fb32.json`,
`runs/e102_rate_fb8_rerun.json`.
**Context:** `docs/findings/2026-09-23-the-batch-count-discriminator.md` §1, which identified the 32-batch point
of that sweep as coming from "a different environment" and therefore treated only the 8-vs-128 pair as
controlled; and rule 26, which rests on the same inference.

---

## 1. The claim, and the measurement that inverts it

The previous fire noticed that `replay` is `+0.0333` in its two new runs and `+0.0500` in the older
32-batch artifact, concluded that `replay` — which consults no Fisher matrix — **cannot** depend on the batch
count, and so dated the older artifact to a different environment. **Three measurements say the 32-batch point
was the reproducible one and the two new runs were not.**

**First, the older artifact reproduces exactly.** Re-running its command today, 13 hours and five commits
later:

| | value |
|---|---|
| numeric fields compared (`methods` subtree, `e8_hardened_basis` vs the re-run) | **280** |
| differing | **0** |

Every replicate of all five arms — `learned`, `retention`, `mean_forgetting`, `final_accuracy` — is identical
to the last printed decimal, `replay` included. **A point that reproduces on 280 of 280 fields is not an
artifact of an older environment.**

**Second, its config does date its code epoch, and that is a different thing** (rule 27). Its `config` has
`frozen_body`, added 09-22 **10:18**, and lacks `replay_batch`, added 09-22 **11:48** — so it predates the five
commits since, and it still reproduces exactly. **A code epoch is not an environment**: the epoch can be
stamped from inside the payload and may be numerically inert, while the environment is what moves values and
leaves no stamp.

**Third, `replay` is not invariant, and the batch count is not why.** The sweep's own premise is that a
Fisher-free arm cannot depend on `--fisher-batches`. Run the arm set that makes that premise *true by
construction* — `--methods naive,replay`, where no Fisher is estimated at all and therefore no Fisher batch is
drawn:

| run | `replay`, mean forgetting | its 15 stored numbers |
|---|---|---|
| `naive,replay` only, `--fisher-batches 8` | +0.0500 ± 0.0163 | vector **X** |
| `naive,replay` only, `--fisher-batches 32` | +0.0500 ± 0.0163 | vector **X** |
| full arm set, `--fisher-batches 32` | +0.0500 ± 0.0163 | vector **X** |
| full arm set, `--fisher-batches 8` (this fire) | +0.0500 ± 0.0163 | vector **X** |
| full arm set, `--fisher-batches 8` (previous fire) | +0.0333 ± 0.0121 | vector **Y** |
| full arm set, `--fisher-batches 128` (previous fire) | +0.0333 ± 0.0121 | vector **Y** |

**The first two rows are the control that the previous fire did not run.** With no Fisher in the process,
`replay` gives the *same* 15 numbers at 8 batches as at 32 — so the batch count cannot be the cause of the
difference, and "it consults no Fisher matrix, therefore it cannot depend on the batch count" is true of the
code and false of the numbers. **`naive`, by contrast, is bit-identical at the replicate level in all six
processes above**, which is why the level control survives and the environment detector does not: the two
roles were never the same property, and only the level one is a property of the arm.

## 2. Which arms reproduce at a fixed configuration

Two runs of one command, an hour apart, at `--fisher-batches 8`:

| arm | run 1 (`e101`) | run 2 (`e102`) | same numbers? |
|---|---|---|---|
| `naive` | +0.0729 ± 0.0151 | +0.0729 ± 0.0151 | **yes, all 15** |
| `ewc` (diagonal) | +0.0271 ± 0.0117 | +0.0271 ± 0.0117 | **yes, all 15** |
| `ewc-block` (biological) | +0.0167 ± 0.0170 | +0.0229 ± 0.0182 | **no** |
| `ewc-block-rand` (matched) | +0.0521 ± 0.0177 | +0.0396 ± 0.0209 | **no** |
| `replay` | +0.0333 ± 0.0121 | +0.0500 ± 0.0163 | **no** |
| **block − matched random** | **−0.0354 ± 0.0218 (1.63σ)** | **−0.0167 ± 0.0232 (0.72σ)** | **no** |

And at `--fisher-batches 32`, the same comparison across processes **13 hours and five commits apart**:
**all five arms reproduce**, block and matched-random included.

**So reproducibility here is not a property of the method, the runner, or the epoch. It is a property of the
arm *at a configuration*, and it is not inferable from the code's data flow.** The two arms that reproduce at
both batch counts are the ones with no estimated object between them and the training signal — `naive` has no
anchor, `ewc` has a 26,568-entry diagonal; the three that fail at 8 batches are the two that fill 5.3e7 block
entries and the one whose numbers the previous fire used as a detector. **The practical consequence is the
rule, not the observation: a network-line contrast needs its own reproduction run, and a reproducibility
result at one configuration licenses nothing at another.**

## 3. What this does to `e101`, and what it does not

**The level control survives, and it is the part the argument actually needed.** `naive` is
+0.0729 ± 0.0151 in all six processes, so the forgetting level is fixed under the manipulation and no
level-based explanation of the block's standing is available. That is measured, not inferred.

**The flag was on the wrong run.** `e101` wrote that only the 8-versus-128 pair is fully controlled. Measured,
the 32-batch point reproduces on 280 of 280 fields and the 8-batch point does not reproduce on any of the
three arms the sweep is about.

**And P1's refutation survives with a quantified caveat.** The clause was that the block-minus-matched-random
gap shrinks monotonically as batches rise, with the level fixed; the gap does not shrink monotonically, and it
**changes sign**, which no account that makes the block's standing a function of its Fisher's data can
accommodate. The caveat is the run-to-run variation just measured: **at 8 batches the gap moved 0.019 between
two runs of one command against a within-run paired sem of 0.022**, so the sem understates the run-to-run
uncertainty by about 1.4×, while the sign change across the batch counts is 0.033–0.052 — **larger than that
variation, so the sign instability is not noise, and the account is still refuted on the one axis that
isolates it.** What changes is the confidence attached to the *magnitude* of any single gap in the sweep, and
it is now stated with its own reproduction attached rather than asserted from one run.

**And the "positive transfer result" stays withdrawn.** The contrast that made it look like a transfer was
`block − naive`; the matched random control earns a similar advantage, so the two arms bracket the result
rather than separating biology. The reproducibility data adds a second reason: the block's own value at 8
batches moves by 0.006 between runs of one command.

**One correction the re-runs surfaced.** The previous fire's σ figures for this contrast were computed from
the **unpaired** sem (−0.0354 at 1.44σ), while the two arms are trained on a shared seed sequence and the
runner's own stored `matched_pair` uses the **paired** one (−0.0354 ± 0.0218 = **1.63σ**). The paired figure is
the right one and is what is used here; the paper's §4.7 quoted the unpaired sem in the same sentence and has
been corrected with it.

## 4. The rule

**A control is a control only in the process where you checked it.** The previous fire's inference had the
right *shape* — find an arm the manipulation cannot move, and use it to detect that something else moved — and
it skipped the step that makes the shape sound: **run the arm in a process where the manipulation is absent,
and see whether it moves anyway.** `--methods naive,replay` costs minutes and would have shown that `replay`
is process-dependent, which is what the evidence actually said. The general form:

- **Level control:** an arm that cannot depend on the manipulation *and* reproduces across processes. Here
  `naive` is both, and it is the only one.
- **Environment detector:** an arm whose invariance you have *demonstrated in the manipulation-free process*.
  `replay` failed that test, so it can date nothing.
- **Per-configuration reproduction:** which arms reproduce is a measured, configuration-specific fact. Report
  it with the contrast rather than assuming it from the code.

This is the same lesson as rule 24's and rule 25's, one level out again: the project keeps writing rules about
what a *quantity* can be trusted to say, and this one is about what an *invariance* can be trusted to mean.
