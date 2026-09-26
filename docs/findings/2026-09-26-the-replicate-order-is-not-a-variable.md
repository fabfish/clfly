# The replicate order is not a variable: the one clustered sequence is what a scan of six gives for free

*2026-09-26 22:20. Runs: **none new** — `experiments/e262_replicate_order_is_not_a_variable.py` reads the two
artifacts the six paired readings come from (`runs/e60_side_lam0.1_16reps.json`,
`runs/e46_c2b_powered.json`), plus the corpus's one rerun pair (`e153`/`e159`), writing
`runs/e262_replicate_order_is_not_a_variable.json`. Half a second.*

## 1. The item: a lead that a fire leaves behind

`e261`'s exploration noticed that of the six paired readings this line reports, one — `cell_class` on forgetting —
has a sign sequence a runs test calls clustered: **four runs in sixteen replicates**, p = 0.019 uncorrected, with a
Spearman correlation against replicate index of **−0.508**. The tempting reading is that that rung's sixteen
replicates are not exchangeable, so its near-zero delta is the **average of two regimes** (a positive first half, a
negative second) rather than an absence of effect — a null that hides a sign change is a different object from a null.

The lead was found by looking at six sequences and taking the most extreme, so the null it needs is **the best of six
exchangeable sequences**, not one sequence's own p. That is what this module builds: hold each reading's own counts
of positive, negative and tied replicates fixed, permute them, and ask what the smallest p over the six looks like.

## 2. The six sequences, and the null

| reading | signs | runs (expected) | runs p | rho(index) | half-split z |
|---|---|---|---|---|---|
| `cell_class/mean_forgetting` | `+++---+++0------` | 4 (8.2) | **0.019** | −0.508 | −1.35σ |
| `side/final_accuracy` | `+-+-0+++---+--+-` | 10 (8.5) | 0.409 | −0.302 | −1.73σ |
| `cell_class/final_accuracy` | `---+-+-+-0++++-+` | 10 (8.5) | 0.409 | +0.421 | +0.62σ |
| `cross/final_accuracy` | `+++-+-+++-----+-` | 8 (9.0) | 0.605 | −0.438 | −1.49σ |
| `cross/mean_forgetting` | `-+-+++---+++++-+` | 8 (8.5) | 0.782 | +0.403 | **+1.88σ** |
| `side/mean_forgetting` | `++---+--+++-++-+` | 9 (8.9) | 0.948 | +0.038 | +1.22σ |

| percentile of the best-of-six null | 1st | 5th | 25th | 50th | 75th | 95th |
|---|---|---|---|---|---|---|
| p-value | 0.0029 | **0.0103** | 0.0522 | 0.1205 | 0.1725 | 0.4054 |

**The observed best of six is 0.0187, and 12.7% of exchangeable corpora produce a reading at least that clustered.**
And the nominal scan is priced exactly: **under exchangeability the best of six lands below 0.05 in 22.5% of draws**,
so "one of these six sequences is significant at 0.05" is not evidence of anything. The lead is what a scan of six
gives for free.

## 3. And the two order statistics disagree about which reading is most ordered

The most clustered sequence's own half-split is only **−1.35σ**, while the largest half-split in the corpus is
**+1.88σ** on `cross/mean_forgetting` — a sequence whose runs-test p is **0.782**, i.e. as unordered as a sequence of
its counts can look. Neither order statistic reaches 2σ, and they do not point at the same reading, which is what two
noise statistics should look like rather than what two views of one structure look like.

## 4. There is no order to recover, and the values are a function of the seeds

Two facts from the corpus close the question rather than leaving it merely quiet:

**No replicate record names a seed.** Across **309** artifacts carrying replicate lists — **5366** replicate records
and thirteen distinct per-replicate keys — **not one** carries a seed or a draw field. So for every paired reading the
index is the only order that exists, and "execution order" cannot be separated from "seed order" because the record
does not say which is which.

**And the one rerun the corpus contains reproduces its numbers bit for bit.**
`e153_r32_overlap1_methods_40reps.json` and `e159_r32_overlap1_methods_rerun.json` are the same configuration run
twice (they differ only in `json_out`, plus a 1.5× difference in the machine-calibration constant): **identical
replicate lists, identical matched pair, 40 replicates by three arms**, while the wall clock runs **14616 s against
11553 s** — 21% faster — and the numbers do not move by a digit. So the replicate values are a deterministic function
of the seeds and the timing is not, which is what makes the whole question answerable: the only randomness a paired
sem scales over is the seed sequence, and **a within-process drift would enter both arms of a pair and cancel in
their difference**, so an index trend in the difference can only be noise.

## 5. The registered claims (N1-N5, all MET)

| claim | what it says | measured |
|---|---|---|
| **N1** | the clustered sequence is inside its own null | 0.0187 against a 5th percentile of 0.0103; 12.7% of corpora reach it |
| **N2** | a nominal 0.05 scan of six costs about a fifth | 0.225 of draws |
| **N3** | the two order statistics disagree | −1.35σ against +1.88σ, no half-split at or above 2σ |
| **N4** | no per-replicate order is recorded | 309 artifacts, 5366 records, 13 keys, no seed |
| **N5** | the values are a function of the seeds | bit-identical replicate lists at 0.79× the clock |

## 6. What it cannot do

The runs test is a normal approximation on fifteen or sixteen values, so a four-run sequence sits where that
approximation is honest but not exact; the null permutes signs within each reading and so holds that reading's own
counts fixed, which is the right null for "is this sequence ordered" and not a null over the effects themselves; the
six readings are **not independent** (both rungs share the naive arm, and the cross-rung is built from the two rungs),
so treating them as six free sequences makes the best-of-six null conservative in the direction that weakens the
claim; and nothing here re-opens whether the effects are real, which is `e76`'s and `e259`'s subject. The honest
summary of this unit is that it **closes a lead as noise** — a negative result, and the useful kind, because it says
the register need not carry replicate order for these readings at all.

**And `e205` caught the same defect in this module that it caught in `e261` one fire earlier** — three source lines
reading a duration through `["timing_s"]` instead of `duration_seconds`, which is the spelling a small module reaches
for and not the quantity. Twice in two fires, in two modules written by the same reader: the gate earns its place.
