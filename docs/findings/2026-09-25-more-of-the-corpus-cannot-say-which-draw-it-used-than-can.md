# More of the corpus cannot say which draw it used than can: 238 (artifact, draw) pairs, and the largest class is the one today measured to matter

**Date:** 2026-09-25
**Analysis only, no runs.** `e168` asked one question of one draw and published the answer -- **31 of 38 artifacts
which ran a `*-rand` arm could not say which matched-random partition they drew**
(`docs/findings/2026-09-24-the-random-control-is-a-sample-and-31-of-38-artifacts-do-not-say-which.md`). Two more draws
exist, and today's events made the census of all three worth having: **two support draws on identical configurations
and identical 40 seeds differ by 3.3–6.6σ on the learning quantities**, and six of the axis's claims failed to
replicate across them.

`experiments/e198_artifact_draw_census.py` reads the artifacts' own metadata and never a measurement. A draw is
**live** in an artifact when the configuration makes it so (a read-out subset smaller than the circuit, an
`ewc-block-rand` arm, an `--input-overlap` suite) and **recorded** when the artifact carries the field with a non-null
fingerprint.

---

## 1. The census, on the 323 artifacts under `runs/`

| draw | recorded as | live in | recorded | **unidentified** | named by |
|---|---|---|---|---|---|
| the read-out subset | `readout.subset_sha1` | 144 | 64 | **80** | `--readout-seed` |
| the matched-random partition | `partition_draw.fingerprint_sha1` | 45 | 14 | **31** | `--partition-seed` |
| **the overlap suite's supports** | `support_draw.fingerprint_sha1` | 130 | **3** | **127** | `--support-seed` |

**238 (artifact, draw) pairs cannot say which draw they used, against 81 that can** — the corpus is more
draw-unidentified than draw-identified, and **the largest single class is the draw today measured to matter most**:
of the 130 artifacts whose supports are a live draw, **3 identify it (2.3%)**.

Two properties of the census worth stating because they are what make it a census rather than a script:

- **It reproduces `e168`'s published figure exactly** -- 31 for the partition draw -- on a corpus that has grown since
  that count was taken. The number is asserted in the tests, so a change to the corpus that moves it will be seen.
- **It does not report everything.** An artifact read out from *every* neuron has no subset to identify (7 such
  artifacts were being counted before the liveness test compared `readout_size` against `circuit_size`), and an
  artifact without an overlap suite has no support draw at all. The false-alarm class is the one `e126`'s preamble is
  about: *a checker that reports everything gets ignored.*
- **A null block is unidentified, not identified.** `support_draw: None` and the field's absence are the same fact --
  the artifact cannot say -- and the tests pin that they are not confused with a fingerprint.

## 2. Why the missing field is not bookkeeping

The three draws are not small, and today measured one of them directly:

| the support draw's own effect (draw 1 − draw 0, same configuration, same seeds) | σ |
|---|---|
| `learned (older)` at overlap 0.0 | −0.01484 ± 0.00444 (**3.34σ**) |
| `learned (older)` at achieved 0.3333 | +0.02187 ± 0.00497 (**4.40σ**) — **opposite sign** |
| the newest task at achieved 0.3333 | +0.03750 ± 0.00569 (**6.59σ**) |
| the adjacent-pair interference at achieved 0.3333 | +0.08036 ± 0.01623 (**4.95σ**) |

**And the six claims that failed to replicate across those two draws** include the day's 8.10σ headline (sign reversal)
and the registered P1 of the original pre-registration (NOT met on draw 0, MET at 4.70σ on draw 1). An artifact that
does not record its support draw therefore cannot have its overlap-sensitive claims attributed to the overlap — which
is the 127 artifacts of §1, i.e. essentially every overlap result this project has.

**The read-out draw is the second-largest class (80 of 144)** and the one whose effects this project has reasoned
about least: every "bit-identical over seven executions" result in the record is conditional on a read-out draw that
was held fixed, and the field that would let a reader check it exists in fewer than half the artifacts that need it.

## 3. What the census does and does not say

- **It says** which artifacts can identify each draw they use, and it counts the exposure.
- **It does not say** that the unidentified artifacts' results are wrong. Their measurements are what they are; what
  is unavailable is the attribution of a manipulation effect when the draw itself moves the quantity.
- **It does not rank the draws by their effects.** One draw's effect is measured (§2, the supports); the read-out's is
  not, and `e168`'s partition figure (up to 0.0138 on forgetting, unresolved) is on a different quantity.
- **It is a census of the corpus as it stands**, and it will change as new artifacts carry the fields. It is not a
  gate -- but `e198` exits 0 on the current corpus, so it can be one.

**Rule 53 is added for the general statement**: every RNG draw a run makes is a sample of that run's configuration,
the corpus must record *which*, and a family's claims should be read across draws rather than within one.
