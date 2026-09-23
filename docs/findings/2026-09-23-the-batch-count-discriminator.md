# E101 — the batch-count discriminator refutes the account on its own axis, and finds a positive transfer result

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py` at `--fisher-batches 8` and `128`, `e8_hardened_basis`'s
configuration otherwise (λ = 0.003, cs = 800, 4 classes, 5 replicates); artifacts `runs/e101_rate_fb8.json`,
`runs/e101_rate_fb128.json`, against `runs/e8_hardened_basis.json` at 32.
**Pre-registration:** `docs/findings/2026-09-23-the-batch-count-discriminator-preregistered.md`
**Context:** the three fires that built the estimation-noise account (`e99` −58%, `e100` −95%,
`docs/findings/2026-09-23-the-competing-explanation-is-not-excluded.md`), and the paper's §4.7.

---

## 1. The design worked, and it caught something about its own inputs

| arm, mean forgetting ± sem | 8 batches | 32 batches | 128 batches |
|---|---|---|---|
| `naive` | **+0.072917 ± 0.0151** | **+0.072917 ± 0.0151** | **+0.072917 ± 0.0151** |
| `ewc` (diagonal) | +0.0271 ± 0.0117 | +0.0208 ± 0.0147 | +0.0250 ± 0.0142 |
| `ewc-block` (biological) | **+0.0167 ± 0.0170** | **+0.0604 ± 0.0201** | **+0.0104 ± 0.0132** |
| `ewc-block-rand` (matched) | +0.0521 ± 0.0177 | +0.0438 ± 0.0156 | +0.0271 ± 0.0091 |
| `replay` | +0.0333 ± 0.0121 | +0.0500 ± 0.0163 | +0.0333 ± 0.0121 |

*Added 2026-09-23: the 8-batch column is **one run, and it does not reproduce.** A second run of the same
command gives `naive` +0.0729 and `ewc` +0.0271 **unchanged** and `ewc-block` **+0.0229**, `ewc-block-rand`
**+0.0396**, `replay` **+0.0500** — the block-minus-random gap moves from −0.0354 to −0.0167. The 32-batch
column is the only one measured twice, and it reproduces on **280 of 280 numeric fields**
(`docs/findings/2026-09-23-the-fisher-free-arm-was-not-fisher-free.md`).*

**P2 — the built-in control — half holds, and the half that fails is informative.** `naive` is
**identical to six decimals** at all three batch counts, exactly as the design requires: it consults no Fisher
matrix, so the forgetting level is **provably fixed** across the sweep, and no level-based explanation of
anything below is available. **`replay` also consults no Fisher matrix and is NOT identical**: it is +0.0333 in
both new runs and **+0.0500 at the old 32-batch point**.

> **Correction (2026-09-23, `e102`), and it inverts the diagnosis below.** This section read that difference as
> evidence that the 32-batch run came from a different environment. **Measured, the 32-batch point is the
> reproducible one**: re-running its command reproduces `e8_hardened_basis` on **280 of 280 numeric fields**
> 13 hours and five commits later, `replay` included, while **two runs of the 8-batch command an hour apart
> agree on `naive` and `ewc` and disagree on `ewc-block`, `ewc-block-rand` and `replay`**. And the arm set with
> **no Fisher in it at all** (`--methods naive,replay`) gives `replay` the *same* 15 numbers at
> `--fisher-batches 8` as at `32` — so the batch count is not what moved it, and `replay` is
> **process-dependent rather than manipulation-dependent**. The level control is unaffected and remains the
> part the argument needs; the environment-detector role is withdrawn. **Everything below is read on the
> re-measured sweep**, and every clause that survives is quoted with its reproduction attached
> (`docs/findings/2026-09-23-the-fisher-free-arm-was-not-fisher-free.md`).

**The old reading of the sweep's controls, kept because it was the reasoning that produced the flag:** the
three-point sweep appeared to mix one old run with two new ones, with only the 8-versus-128 pair controlled.
**What is measured is the reverse** — 32 is the point with two exact reproductions and 8 is the point whose
arms move — and the honest statement is that **which arms reproduce is a configuration-specific fact that has
to be measured at each configuration rather than inferred from the code**
(`docs/findings/2026-09-23-the-fisher-free-arm-was-not-fisher-free.md`).

## 2. The clauses

| contrast | 8 batches | 32 batches (reproduces exactly) | 128 batches |
|---|---|---|---|
| **block − matched random** | **−0.0354 ± 0.0218 (1.63σ)** | +0.0167 ± 0.0252 (0.66σ) | **−0.0167 ± 0.0134 (1.24σ)** |
| block − diagonal | −0.0104 (0.51σ) | +0.0396 (1.59σ) | −0.0146 (0.75σ) |
| **block − `naive`** | **−0.0562 (2.48σ)** | −0.0125 (0.50σ) | **−0.0625 (3.12σ)** |
| `naive` − diagonal | +0.0458 (2.40σ) | +0.0521 (2.47σ) | +0.0479 (2.31σ) |

*The block-minus-random row now carries the **paired** sem, which is the right one because the two arms share
a seed sequence and is what the runner's own stored `matched_pair` holds. The σ figures this document
originally printed for that row (1.44σ, 1.04σ) came from the unpaired sem; the other rows are unchanged.*

**P1 is refuted.** The clause was that the block-minus-matched-random gap **shrinks monotonically** as batches
rise, with the level held fixed. It does not shrink: it is **negative at two of the three batch counts**
(−0.0354 and −0.0167, i.e. the biological block *beats* its matched random control at those two) and positive
at the middle one, so **the gap changes sign along the axis**, which is not a monotone function of estimation
quality. **And the sign change is larger than the run-to-run variation**: at 8 batches the same command gave
−0.0354 and −0.0167 an hour apart, a movement of **0.019 against a within-run paired sem of 0.022**, while the
sign change is **0.033–0.052** — so P1's direction does not appear anywhere, and the reason is not
measurement noise at this replicate count
(`docs/findings/2026-09-23-the-fisher-free-arm-was-not-fisher-free.md`).

**The falsifier fires, and in its strongest form.** It was *the gap does not shrink with the batch count while
`naive` stays identical*; what happened is stronger — **the gap changes sign**, which no account that makes the
block's standing a function of its Fisher's data can accommodate.

**P3 held and turned out to matter**: the diagonal's own forgetting is +0.0271, +0.0208, +0.0250 — **flat**,
not rising as it did at λ = 0.1 in `e96`. So at λ = 0.003 the diagonal is not over-constrained by more batches,
which is why block-minus-diagonal tracks block-minus-random here instead of being distorted.

## 3. What this does to the account, and to the three fires that built it

**The estimation-noise account is refuted on the one axis that isolates it.** Its content is that the block's
penalty is the noise in its off-diagonal blocks, `Σ s_g²` entries filled from the same 256 observations; the
prediction that follows is that giving it 16× more data (`e96` protocol) should move it toward the diagonal and
toward its own control. **With the level provably fixed, it moves the other way at both ends, and its sign
relative to the control is unstable.**

**Which re-reads `e99` and `e100`.** Both varied a configuration and reported a monotone-looking reduction —
58% and 95% — and `e100`'s P4 was read as *"both routes shrink the gap, so the account is supported twice"*.
**The one manipulation that changes estimation quality alone says no**, so those two reductions are
**coincidences of configuration**, not confirmations of a mechanism: two axes moved the gap and one did not,
and the one that did not is the one the account is *about*. That is a plain correction of the last three
fires' reading and it goes against the direction they were building.

## 4. And a positive transfer result the paper does not report — **withdrawn the same day**

> **Correction (2026-09-23, same day).** Everything in this section was measured correctly and the conclusion
> drawn from it was wrong, because it stopped one comparison short. **At 128 batches the size-matched *random*
> control also beats `naive`, by −2.60σ against the block's −3.12σ**, so the advantage over the baseline is a
> **granularity** effect — partitioning the synapses coarsely at all — and not a biological one. The only
> contrast that isolates biology is the block against that control, and it is negative at two batch counts and
> positive at the third, resolving nowhere. **And the reproducibility work compounds it**: at 8 batches the
> block's own value moves by 0.006 between two runs of one command, while `naive` and `ewc` are identical in
> both. §4.7 was right and this section was an artefact of not carrying the control into the sentence
> (`docs/findings/2026-09-23-the-positive-transfer-result-was-not-one.md`,
> `docs/findings/2026-09-23-the-fisher-free-arm-was-not-fisher-free.md`).

**The claim as this fire wrote it, kept for the record:** *the biological block resolves an advantage over
`naive` at both controlled points — 2.48σ at 8 batches and 3.12σ at 128 — and at 128 batches it is the best
arm in the table on both metrics** (forgetting +0.0104 against `naive`'s +0.0729 and the diagonal's +0.0250;
accuracy **0.950** against 0.914 and 0.911).*

**The comparison that was missing, and it was already printed in the same run's output four lines below**:

| contrast, mean forgetting | 8 batches | 128 batches |
|---|---|---|
| block (biological) − `naive` | −0.0562 (2.48σ) | −0.0625 (3.12σ) |
| **block-rand (matched control) − `naive`** | −0.0208 (0.89σ) | **−0.0458 (2.60σ)** |
| diagonal − `naive` | −0.0458 (2.40σ) | −0.0479 (2.31σ) |
| **block − its matched control** | −0.0354 (1.63σ) | −0.0167 (1.24σ) |

**At 128 batches the advantage over `naive` is shared almost entirely by a size-matched random partition of
the same synapses**, so what resolves at this λ is not biology. The block's accuracy of 0.950 is real and the
control reaches 0.9431.

## 5. What follows

- **The account as stated should be withdrawn**, not qualified: its own axis refutes it, and `e99`/`e100`'s
  support is now read as configuration coincidence.
- **P1's failure is the finding**, so it belongs in §7 as a *refuted mechanism* rather than as an open
  question — the network line's basis behaviour varies with configuration in a way no account this project has
  proposed predicts.
- **And the one thing that is stable is the diagonal**, which beats `naive` by 0.046–0.052 at 2.3–2.5σ in all
  three batch counts *and* is bit-identical in its `naive` comparator. That is the most robust number in the
  network line, and it is not the one the section argues about.
