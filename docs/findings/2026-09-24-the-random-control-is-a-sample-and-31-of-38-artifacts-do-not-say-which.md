# The matched-random control is a sample: 31 of 38 artifacts do not record which, and the draw is reconstructible

**Date:** 2026-09-24
**Script:** `experiments/e168_draw_fingerprint_census.py` — analysis only, no runs;
`--reconstruct` rebuilds the draws and loads the connectome. Artifact:
`runs/e168_draw_fingerprint_census.json`.
**Answers:** `e162`'s block-rand λ column, whose two sides are `e144` (records no draw) and `e153` (records one).
**Outcome: the column stands, and it stands on a *reconstruction* rather than on the artifacts.**

---

## 1. The exposure

`ewc-block-rand` is the project's group-size-matched random control, and rule 10 says the control is a
**population** while one draw is one **sample** of it. The sample's identity is
`partition_draw.fingerprint_sha1` — a **top-level** field, so `e103`'s signature (which reads `config`) cannot see
it: **two artifacts whose draws differ are "the same configuration" by every check this corpus applies.**

| | |
|---|---|
| artifacts running a `*-rand` arm (so a reader could compare them) | **38** |
| of those, recording which partition they drew | **7** |
| **unidentifiable from the artifact** | **31** |
| distinct partitions ever drawn | **3** — `000b42be6ba2` (seed 0, the default), `3058aa874ae6` (1), `f6a658eabf9c` (2) |
| pairs sharing a `-rand` arm (703) | **5** same draw, **16** different, **217 one side only, 465 neither** |

## 2. The quantity at stake, measured

`--partition-seed` exists, so the corpus holds **two pairs of 40-seed runs that differ in nothing but the draw** —
the only clean measurement of the sample's own size, on both families:

| configuration | n | forgetting (draw 2 − draw 1) | resolution | newest task | resolution |
|---|---|---|---|---|---|
| base (`input_overlap` 0.0), `e140` | 40 | +0.0055 | 0.75σ | −0.0031 | 0.80σ |
| wiring (`input_overlap` 1.0), `e144` | 40 | **−0.0138** | 1.33σ | −0.0068 | 1.48σ |

**Two samples of one control differ by up to 0.0138 on forgetting and 0.0068 on the newest task, and neither
difference resolves** — the sample is small, which is rule 10's point rather than a defect. The *same* control is
**2.5× noisier on the wiring family than on the base family**, so a spread quoted for one family cannot be lent to
the other.

## 3. The unrecorded draw is reconstructible, and it reproduces

The control is built by one expression — `random_matched(from_labels(labels, pre, post, …),
default_rng(seed))` — and **`random_matched`'s body is byte-identical to the version that introduced it**
(`4b5d182`, 09-22 07:30; the file's two later commits do not touch its RNG), so the draw an artifact used is a
function of its `config`. That makes an unrecorded draw *identifiable* rather than merely missing, in two steps:

1. **The seeding is in the code history, and so is the epoch — from the run's *start*, not its artifact's
   timestamp.** `e144` predates `--partition-seed` (`5a0f06e`, 09-24 10:21), and the pre-flag line is
   `SynapsePartition.random_matched(bio, np.random.default_rng(args.seed0))` — **the same value the flag now
   defaults to.** The evidence is arithmetic and it needed the `timing_s` field to be read as a duration: **`e144`
   took 15474 s (4.30 h) and its file was written at 14:18, so its process began around 09:57 — twenty-four
   minutes *before* the commit that added the flag**, which is why an artifact newer than the commit has no
   `partition_seed` in its `config`. Its other fields are recorded and match the reconstruction's inputs
   (`seed0 = 0`, `basis = cell_class`, `pool_below = 0`, `pool_buckets = 1`, the last being both the shipped
   default and the recorded value).
2. **And the reconstruction reproduces the recorded values.** Rebuilding the circuit, the biological partition and
   the draw from those fields gives, for seeds 0, 1 and 2:

| seed | reconstructed | recorded among the 7 |
|---|---|---|
| 0 | `000b42be6ba2` | **MATCH** |
| 1 | `3058aa874ae6` | **MATCH** |
| 2 | `f6a658eabf9c` | **MATCH** |

**So `e144`'s draw was seed 0 — the same sample as `e153`'s — and `e162`'s premise holds.** The check is a command
(`e168 --reconstruct`), not a paragraph: the three fingerprints are computed from `config` fields alone and
compared against what the seven recording artifacts wrote.

**And a trap falls out of step 1 that is worth more than this pair: an artifact's timestamp dates the *end* of a
run, so for a long run it can be hours later than the code that produced it.** `e163` bracketed the 09-23 epoch
with the fb8 artifacts' write times, where a 16-minute run makes the error small; at `e144`'s 4.3 hours the write
time is on the wrong side of a commit that the run never contained.

## 4. What the pair *could* have moved, now that it is identified

The identification is what rules the following out, so the numbers are worth keeping as the bound it removes.
`e162`'s block-rand λ contrast, against the largest between-draw difference measured on that same family:

| contrast | step | resolution | draw size | |
|---|---|---|---|---|
| `ewc-block-rand` forgetting, λ = 3e-3 → 1.0 | −0.0112 | 1.09σ | 0.0138 | **under the draw** |
| `ewc-block-rand` newest task, same step | −0.0219 | 4.19σ | 0.0068 | 3.2× the draw |
| its margin over `naive`, forgetting | +0.0112 | 1.09σ | 0.0138 | under the draw |
| its margin over `naive`, newest task | +0.0219 | 4.19σ | 0.0068 | 3.2× the draw |

**Two readings of that table, and the right one is the second.** *If* the draws had differed, the forgetting
column would have been uninterpretable at 1.09σ and the newest column would have survived at 3.2×; the
reconstruction says the draws did not differ, so **both columns stand**. The margin rows equal the step rows
because `naive` is bit-identical across the pair (the design's own control, step 0.0000).

**And the biological block arm needs none of this**: `ewc-block`'s partition comes from `circ.labels[basis]`
through `from_labels`, with no seed anywhere in it — the draw enters only the `rand` branch of the code. So of the
two block arms, only the random control's column ever depended on the draw, and it is the one this unit checks.

## 5. Rule 46

*A contrast that uses a `-rand` arm across two artifacts must identify the draw on **both** sides — by printing
`partition_draw.fingerprint_sha1` or by reconstructing it from the config fields that determine it — and must
report the between-draw spread measured **on that same family** as the size of the term being ruled out.*

The rule is cheap because the reconstruction is one command, and it is necessary because the artifacts are silent:
**31 of the 38 artifacts that use the control cannot say which sample they used**, 682 of the 703 pairs that share
a `-rand` arm cannot be checked by reading, and `e103`'s identity check cannot see the field at all. The five pairs
that *are* licensed by two matching fingerprints, and the 16 that are **known to be different samples**, are the
only ones a reader can classify without re-running the reconstruction.

**And it is the fourth instance of tonight's one structure**: `environment` is absent from exactly the two
repeated configurations that moved (`e163`), `code_revision` is on one side of `e164`'s pair, the calibration is
on one side of the pair that shows a 1.78× wall-clock gap (`e164`), and the draw fingerprint is on one side of the
pair whose contrast it could move. The difference here is that this one was **recovered** — because the code that
produced the draw is under version control and unchanged, which is precisely what `code_revision` would have said
in one field.

## 6. What this cannot settle

- **The reconstruction's validity rests on three links, each named**: that `random_matched`'s body is unchanged
  (checked — byte-identical to `4b5d182`, and the file's two later commits do not touch its RNG), that the fields
  `e144` did not record took their then-defaults (checked field by field against the shipped defaults, and the
  pre-flag call site is in the history), and that the fingerprint expression is the same in both epochs (checked
  in the sense that matters: all three recorded fingerprints reproduce, so a divergence would have shown as a
  MISMATCH). **What is *not* checked is `e144`'s start time**, which is inferred from its `timing_s` and its
  file's write time rather than recorded — the inference needs the run to have been the only thing in flight, and
  a 4.30 h duration is a strong but indirect statement about when the process began.
- **The population's spread is estimated from two draws**, so 0.0138 is *one draw-pair difference*; if the two
  samples are independent its sd is about **0.0098**, and the honest reading is a bound rather than an sd.
- **It says nothing about draws outside the two families measured**, and the wiring family's spread is the larger.
- **682 of the 703 pairs remain unidentifiable by reading**; this method identifies a draw only when the config
  fields that determine it are recorded and the code is unchanged, so it will fail for any artifact written
  before a change to `fisher.py` — a limitation `code_revision` also cannot fix retroactively.
- **Nothing here licenses a `-rand` comparison across *different* circuit sizes or bases**, where the biological
  partition itself differs and the fingerprints are therefore not comparable objects at all.
