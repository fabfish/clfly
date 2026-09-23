# The Fisher-free arm was not Fisher-free, and the flag went on the reproducible point

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py`, `e8_hardened_basis`'s configuration; artifacts
`runs/e101_rate_fb32.json`, `runs/e102_replayonly_fb8.json`, `runs/e102_replayonly_fb32.json`,
`runs/e102_rate_fb8_rerun.json`.
**Artifacts:** `runs/e101_rate_fb8.json`, `runs/e101_rate_fb32.json`, `runs/e101_rate_fb128.json`,
`runs/e102_rate_fb8_rerun.json`, `runs/e102_rate_fb8_rerun2.json`, `runs/e102_rate_fb128_rerun.json`,
`runs/e102_rate_fb8_omp1.json`, `runs/e102_replayonly_fb8.json`, `runs/e102_replayonly_fb32.json`,
`runs/e8_hardened_basis.json`.
**Setup:** `experiments/e8_rate_network.py`, circuit `mb+cx+al@n1307`, cs = 800, 3 tasks, 5 replicates,
λ = 0.003, 4 classes, shared head, read-out 32 neurons, `--fisher-batches` 8/32/128, chance 0.25.
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

**The sweep was then run out to seven executions of the same five-arm command**, so the reproducibility claim
is per arm *and* per batch count rather than a single pair:

| run | `naive` | `ewc` | `ewc-block` | `ewc-block-rand` | `replay` | block − control | control − `naive` | block − `naive` |
|---|---|---|---|---|---|---|---|---|
| 8 batches, `e101` | +0.0729 | +0.0271 | +0.0167 | +0.0521 | +0.0333 | **−0.0354** | −0.0208 | −0.0562 |
| 8 batches, `e102` #1 | +0.0729 | +0.0271 | +0.0229 | +0.0396 | +0.0500 | **−0.0167** | −0.0333 | −0.0500 |
| 8 batches, `e102` #2 | +0.0729 | +0.0271 | +0.0229 | +0.0396 | +0.0500 | **−0.0167** | −0.0333 | −0.0500 |
| 32 batches, 09-22 | +0.0729 | +0.0208 | +0.0604 | +0.0438 | +0.0500 | **+0.0167** | −0.0292 | −0.0125 |
| 32 batches, `e102` | +0.0729 | +0.0208 | +0.0604 | +0.0438 | +0.0500 | **+0.0167** | −0.0292 | −0.0125 |
| 128 batches, `e101` | +0.0729 | +0.0250 | +0.0104 | +0.0271 | +0.0333 | **−0.0167** | −0.0458 | −0.0625 |
| 128 batches, `e102` | +0.0729 | +0.0250 | +0.0313 | +0.0375 | +0.0500 | **−0.0062** | −0.0354 | −0.0417 |

**Five of the seven runs reproduce exactly against their partner — every arm, every replicate.** And the two
that do not are **`e101`'s two runs and only those two**: `e102`'s 8-batch pair agrees on all five arms, the
32-batch pair agrees on all five arms 13 hours apart, and it is `e101`'s 8-batch and 128-batch runs that stand
apart. **So the two runs the previous fire declared "fully controlled" are the two that fail to reproduce, and
the point it flagged as contaminated is the one with two exact reproductions.** That is not a subtle
mis-ordering of evidence; it is the flag pointing at the control group.

**What is reproducible and what is not, measured:**

- **`naive`: all seven runs, bit-identical**, at every batch count. This is what makes it the level control.
- **`ewc` (the diagonal): identical at every batch count** (0.0271 / 0.0208 / 0.0250, two or three runs each).
  It is the configuration's *most* reproducible Fisher arm, which is consistent with its 26,568-entry
  estimate against the block arms' 5.3e7.
- **`ewc-block`, `ewc-block-rand`, `replay`: no.** Not at 8 batches, not at 128; yes at 32.
- **The one quantity the section argues about, the block-minus-control gap, reproduces in SIGN and not in
  magnitude**: −0.0354 and then −0.0167 twice at 8 batches; +0.0167 twice at 32; −0.0167 and −0.0062 at 128.
  **Six of six paired runs agree in sign with their twin**, so the sign function of the batch count is
  **−, +, −** — non-monotone, and reproducible as a *pattern*, with the magnitudes moving by up to **0.021**
  between runs of one command.

## 3. What this does to `e101`, and what it does not

**The level control survives, and it is the part the argument actually needed.** `naive` is
+0.0729 ± 0.0151 in all six processes, so the forgetting level is fixed under the manipulation and no
level-based explanation of the block's standing is available. That is measured, not inferred.

**The flag was on the wrong run.** `e101` wrote that only the 8-versus-128 pair is fully controlled. Measured,
the 32-batch point reproduces on 280 of 280 fields and the 8-batch point does not reproduce on any of the
three arms the sweep is about.

**And P1's refutation survives with a quantified caveat.** The clause was that the block-minus-matched-random
gap shrinks monotonically as batches rise, with the level fixed. Measured on the seven-run table above, the
gap's **sign is reproducible at every batch count and its magnitude is not**: negative twice at 8 batches
(−0.0354, −0.0167, −0.0167), positive twice at 32 (+0.0167, +0.0167), negative twice at 128 (−0.0167,
−0.0062). **So the sign function of the batch count is −, +, −**, which no account that makes the block's
standing a function of its Fisher's data can accommodate, and **the run-to-run movement of the magnitude
(up to 0.021) is smaller than the gap's own sign change (0.033)**. The account is therefore still refuted on
the one axis that isolates it, and the confidence attached to any *single* gap's magnitude is what changes:
each one in the paper is now quoted with its pair rather than alone.

**And the "positive transfer result" stays withdrawn, on two independent grounds.** The contrast that made it
look like a transfer was `block − naive`; **the matched random control beats `naive` at every batch count in
every run too** (−0.0208, −0.0333, −0.0292, −0.0458, −0.0354), and the biology-specific contrast is smaller
than the granularity one in every run. Second, the block's own value moves between runs of one command
(0.006 at 8 batches, 0.021 at 128), so the arm carrying the claim is one of the three that do not reproduce.

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

## 5. Naming the variable: the thread count is a carrier, and it settles what `naive` is for

Seven runs established **that** `ewc-block`, `ewc-block-rand` and `replay` move run to run at fixed config while
`naive` and `ewc` do not, and said nothing about **which** environment variable carries it. The candidate the
project had already measured is the thread count (`e96`: one nominal experiment spanning 0.799 to 0.896 in
accuracy on the `naive` arm across `OMP_NUM_THREADS` 1, 3 and 4). Both outcomes were written down before the
runs, and at per-step 8 with the flags of §1:

| arm | `e101` (Y) | `e102` run 2 (X) | **`OMP_NUM_THREADS=1`** |
|---|---|---|---|
| `naive` | +0.0729 ± 0.0151 | +0.0729 ± 0.0151 | **+0.0792 ± 0.0134** |
| `ewc` (diagonal) | +0.0271 ± 0.0117 | +0.0271 ± 0.0117 | **+0.0250 ± 0.0205** |
| `ewc-block` (biological) | +0.0167 ± 0.0170 | +0.0229 ± 0.0182 | **+0.0437 ± 0.0141** |
| `ewc-block-rand` (matched) | +0.0521 ± 0.0177 | +0.0396 ± 0.0209 | **+0.0792 ± 0.0126** |
| `replay` | +0.0333 ± 0.0121 | +0.0500 ± 0.0163 | **+0.0542 ± 0.0204** |
| **block − matched random** | −0.0354 | −0.0167 | **−0.0354 ± 0.0163 (2.17σ)** |

**All five arms move, on none of them does `OMP_NUM_THREADS=1` match either vector, and `naive` moves too**
(+0.0062, i.e. 0.4 of its own sem). So the thread count **is** an environment variable this benchmark is shaped
by — §9's measurement, reproduced on a different configuration — and it is **not** the variable behind the
X-versus-Y split, because if it were, one of the two runs would have landed on one of the two vectors. **The
registered test answered "neither" to both of its branches**, which is the outcome it did not enumerate, and it
still narrows the question: the carrier of the X/Y difference is something other than `OMP_NUM_THREADS ∈ {1, 4}`
at this configuration.

**And it corrects the repair, not just the diagnosis.** The previous fire's §4 wrote that `naive` should be
*"the level control, and never … an environment detector"*. Measured, the opposite is true on both halves:

- **`naive` is a valid environment detector, and this run is it firing.** It consults neither the Fisher nor
  replay, so it is invariant under every manipulation in this benchmark; and it moved by +0.0062 when nothing but
  the thread count changed. Its bit-identity across the seven runs of §2 is therefore *evidence that those seven
  shared an environment*, which is what a level control's silence is supposed to mean.
- **`replay` is not a valid one**, because it moved between `e101`'s runs and `e102`'s while `naive` did not:
  `replay` has a source of variation that is not the environment, and an arm with two sources can date nothing.

**So the roles are: `naive` is both the level control and the environment detector — invariant under the
manipulation and mobile under the environment, which is the definition rather than a defect — and `replay` is
neither, despite being Fisher-free.** That is the *third* revision of this claim in one session (the original
diagnosis, the previous fire's inversion of it, and this), and the reason to state it in this form is that each
revision came from a run rather than from re-reading: the first was one pair of values, the second was seven
runs, and this one was a single named variable.

**And the record will not have to be reconstructed like this again.** The default on this machine is
**20** torch threads, and while `OMP_NUM_THREADS` was set to 1 and 4 for these two runs, **`e101`'s and `e102`'s
seven earlier runs recorded nothing about how many threads they actually used** — so whether the X-versus-Y
split is a thread-count difference at some value other than 1 or 4 is not answerable from the corpus, which is
rule 21's standing complaint and the reason a 58-minute sweep was needed to rule out one value of one variable.
`experiments/e8_rate_network.py` now writes an **`environment`** block into every artifact
(`omp_num_threads`, `mkl_num_threads`, `torch_num_threads`, `torch_num_interop_threads`, `torch_version`,
`python`, `platform`), with `"unset"` recorded as a *value* rather than as a missing key, and two tests pin it
(`tests/test_network.py`). The next run of any configuration answers this question for free.

**And §3's clause is unaffected in sign and further bounded in magnitude.** At 8 batches the
block-minus-matched-random gap is now measured **four times in two environments** — −0.0354 (Y), −0.0167 (X),
−0.0167 (X), −0.0354 (thread-limited) — so it is negative in all four and takes two values, and the monotone
direction the account predicts is still absent at every batch count. The accuracy contrast on the same pair
moves as far as the forgetting one: −0.0125 (0.60σ) in the X runs against **+0.0222 (4.35σ paired)** under
`OMP_NUM_THREADS=1`, so *neither* metric is stable to the environment, and the paper's claims about this
partition are stated on forgetting with the accuracy contrast beside them
(`runs/e102_rate_fb8_omp1.json`).
