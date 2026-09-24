# Four versions of the readership table, and what each one's failure revealed about the corpus

**Date:** 2026-09-24
**Script:** `experiments/e160_which_fields_are_read.py` — **left at the version whose λ check passes** (the one
committed last fire), with three attempted refinements documented here rather than kept.
**Why a finding about a *method* rather than a result:** the table's purpose is to answer, before an identity
claim is written, *does this arm read the field that differs?* — and `e153`'s `lam = 1.0` against `e144`'s `3e-3`
is the measured cost of not asking. **Trying to make the instrument sharper exposed three properties of the corpus
that bound any such table**, and they are the deliverable.

---

## 1. The four versions and what each did

| # | rule for a verdict | λ row | what it got right | what it got wrong |
|---|---|---|---|---|
| **1** | single-field differences only; verdict **assigned per pair in iteration order** | — | the restriction is the instrument's foundation | **an identical pair could overwrite a `read`**, so the answer depended on which pair came last — the defect class this project keeps finding in its own readers |
| **2** *(committed)* | single-field differences only; evidence **counted**, with a `CONFLICTING` verdict | **`naive` unread, three penalty arms read, `replay` unread** ✓ | conservative and order-independent; answers rule 44's question for the field that cost three artifacts | reports `CONFLICTING` for several fields, which is uninformative without knowing *why* |
| **3** | as 2, plus **the whole `environment` block as one field** | `replay`'s λ fell to `possibly read` | catches the `OMP_NUM_THREADS` pairs, which *are* two-field pairs | **the block contains a timing** (`calibration_matmul_s`), so almost any two newer runs "differ in the environment" and the clean evidence disappears |
| **4** | as 2, plus **each environment key as its own field** and a **two-pass** rule: pass one collects the unread set from every bit-identical pair, pass two convicts a field if some pair differing in it *plus only already-unread fields* moved | `frozen_bias` becomes `CONFLICTING` for **all five** arms | the licensing rule is right in principle — a field known unread can be varied freely, which is rule 39's benign twin used as a tool | **pass one's premise is false**: it assumes an identical pair is a pair of independent runs, and the corpus contains **re-writes** |

## 2. The three properties of the corpus that bound the instrument

**First, provenance is not recorded.** `e119_r300_test480` and `e123_r300_test480` are the same run re-read for the
loss metric, and their arms are bit-identical by construction — so *any* rule that infers "unread" from identity
**inherits every re-dump in the corpus as evidence about the runner**. Version 4 made this fatal (the unread set
inflates until every field is in it, and then every field is `CONFLICTING`); version 2 survives it only because it
requires the difference to be strictly single-field.

**Second, the environment block mixes a setting with a measurement.** `omp_num_threads` and the library versions
are settings; `calibration_matmul_s` is a *timing*, which `e77` and the two `e140` arms already showed varies
across runs that reproduce exactly. A single "environment differs" boolean therefore cannot exist downstream of
that block without someone deciding which keys matter — **and deciding that by hand is exactly what this table
exists to avoid**.

**Third, the corpus contains run-to-run movement that no field explains.** `replay`/`fisher_batches` is
`CONFLICTING` because `e101_rate_fb8` and `e101_rate_fb32` differ in that field alone and their `replay` arms
differ — and `replay` builds no Fisher. That is §9's own measurement (two runs at `--fisher-batches 8` disagree on
`replay`), so **the table cannot separate a readership signal from a reproducibility one**, and a `read` verdict is
therefore "this field moved an arm at least once" rather than "this field necessarily changes the arm".

## 3. What that means for how the table should be used

**Use it for what it is**: a **finder** that answers rule 44's question *conservatively* — **a field whose row is
one-sided is safe to differ in an identity claim; a `CONFLICTING` or `possibly read` row is a field about which the
corpus has nothing clean to say, and such a claim must be checked against the two artifacts directly instead** —
which is what rule 44 requires anyway. Its two load-bearing rows are the ones this evening needed:

- **`lam`: read by `ewc`, `ewc-block`, `ewc-block-rand`; unread by `naive` and `replay`.**
- **`replay_per_task`/`replay_batch`: unread by `naive`, read by `replay`** — the two controls `e140` rests on.

**And the refinements that would make it a verdict are named with their costs**: recording whether an artifact is
a re-write (an `e103`-style provenance field would do it, and `e98`'s migration is where such re-writes came
from), and separating the environment's settings from its timings (a list, which is a hand decision — so the
alternative is to *record* the functional keys as their own top-level fields in the runner, which is a code change
and not an analysis).

## 4. What this cannot settle

- **It does not measure readership exhaustively**: a field with no clean pair is reported as `untested` or
  `possibly read`, and the code — not the table — is then the only source. `anchor_bias`, `partition_seed` and
  `readout_seed` are the fields with the widest `untested` rows.
- **Four versions is not a search**: each was chosen by one property of the corpus, and the fourth's failure was
  visible in one run; a fifth (provenance-filtered) is the obvious next one and is not attempted here.
- And **the table's subject is this runner**: `lam`, `basis` and the replay settings mean what they mean here, and
  a second substrate with the same field names would need its own row.
