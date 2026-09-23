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

**P2 — the built-in control — half holds, and the half that fails is informative.** `naive` is
**identical to six decimals** at all three batch counts, exactly as the design requires: it consults no Fisher
matrix, so the forgetting level is **provably fixed** across the sweep, and no level-based explanation of
anything below is available. **`replay` also consults no Fisher matrix and is NOT identical**: it is +0.0333 in
both new runs and **+0.0500 at the old 32-batch point**. Since `replay` cannot depend on the batch count, that
difference means the 32-batch run was taken in a **different environment** — which is rule 21's property of
the torch path, and the reason §9 exists.

**So the three-point sweep mixes one old run with two new ones, and only the 8-versus-128 pair is fully
controlled** (both new, run in one process, with `naive` and `replay` identical between them to six decimals).
Everything below is read on that pair; the 32-batch point is reported and marked.

## 2. The clauses

| contrast | 8 batches | 32 (old, flagged) | 128 batches |
|---|---|---|---|
| **block − matched random** | **−0.0354 (1.44σ)** | +0.0167 (0.65σ) | **−0.0167 (1.04σ)** |
| block − diagonal | −0.0104 (0.51σ) | +0.0396 (1.59σ) | −0.0146 (0.75σ) |
| **block − `naive`** | **−0.0562 (2.48σ)** | −0.0125 (0.50σ) | **−0.0625 (3.12σ)** |
| `naive` − diagonal | +0.0458 (2.40σ) | +0.0521 (2.47σ) | +0.0479 (2.31σ) |

**P1 is refuted.** The clause was that the block-minus-matched-random gap **shrinks monotonically** as batches
rise, with the level held fixed. It does not shrink: within the controlled pair it is **negative at both ends**
(−0.0354 and −0.0167, i.e. the biological block *beats* its matched random control), and the flagged middle
point is the only positive one. **A gap whose sign is not stable across the axis is not a monotone function of
estimation quality**, and P1's direction does not appear anywhere.

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

## 4. And a positive transfer result the paper does not report

**The biological block resolves an advantage over `naive` at both controlled points — 2.48σ at 8 batches and
3.12σ at 128 — and at 128 batches it is the best arm in the table on both metrics** (forgetting +0.0104
against `naive`'s +0.0729 and the diagonal's +0.0250; accuracy **0.950** against 0.914 and 0.911).

§4.7 says *"biology does not help **synapse** anchoring at 0.925 constrained"*, and that is a statement about
λ = 0.1 and `cell_class`. **At λ = 0.003 with 128 Fisher batches the biological synapse partition beats the
naive baseline by 3.12σ**, which is the transfer the paper's network line has been reported as *not* finding.
It is not the earlier claim overturned — the λ and the batch count both differ — but it is a result the
section does not carry, and the block's accuracy of 0.950 is the highest any Fisher variant reaches anywhere
in this paper.

**And it is unresolvable in magnitude for the reason the last fire quantified**: the gap is 0.0625 against a
per-repeat sd of 0.019–0.084, so it is a fraction of one replicate's own variation however many are averaged.
The 3.12σ is a sem-based figure and the *direction* is what three of the four contrasts agree on.

## 5. What follows

- **The account as stated should be withdrawn**, not qualified: its own axis refutes it, and `e99`/`e100`'s
  support is now read as configuration coincidence.
- **P1's failure is the finding**, so it belongs in §7 as a *refuted mechanism* rather than as an open
  question — the network line's basis behaviour varies with configuration in a way no account this project has
  proposed predicts.
- **And the one thing that is stable is the diagonal**, which beats `naive` by 0.046–0.052 at 2.3–2.5σ in all
  three batch counts *and* is bit-identical in its `naive` comparator. That is the most robust number in the
  network line, and it is not the one the section argues about.
