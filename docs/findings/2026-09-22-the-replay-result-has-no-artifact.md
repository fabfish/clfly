# E62 — the network line's headline positive result has **no artifact**, and the nearest one that exists gives it at 1.17σ

**Date:** 2026-09-22
**Artifacts examined:** every `runs/*.json` (77 files); `runs/e61_replay96_step{8,16,48}.json` launched
**Context:** `2026-09-22-network-line-settled.md`, `2026-09-22-replay-budget-inversion.md`, `2026-09-22-replay-budget-inversion.md`, plan rule 8

---

## 1. What the line claims, and where the number is

The network line's one surviving positive result is stated in two findings and the plan's programme
table as: **replay (pool 96, per-step 8) reduces forgetting to −0.010 ± 0.006 against naive's
+0.066 ± 0.019 — 4.2σ — its "best method found"**, at 0.968 ± 0.013 accuracy, for 6.0 MB against the
diagonal Fisher's 0.2 MB. The same finding reports a *budget inversion* over the per-step draw:
per-step 8 gives −0.010, 16 gives +0.017, 48 gives +0.007 — so more replay is worse.

Every one of those numbers is tied to a specific configuration: `--replay-per-task 96` and
`--replay-batch ∈ {8, 16, 48}`.

## 2. No such run is on disk

A census of all 77 artifacts:

```
"replay_per_task": 16   <- 18 occurrences, every one of them
"replay_batch":     16   <- 11 occurrences, every one of them
runs with replay in --methods: 5
```

**There is no artifact with `replay_per_task: 96`, and none with `replay_batch: 8` or `48`.** A
repository-wide search (including `/tmp`) finds nothing. So the configuration behind the network
line's headline result was never saved, or was saved and overwritten — and `runs/` is gitignored, so
there is no history to recover it from.

This is the **third** instance of the same failure in this project, and the most serious because the
claim is live:

| | what was missing | how it resolved |
|---|---|---|
| `e41` | the `e5` finding's table was not reproducible from the artifact it cites | `e43`: the artifact was live and the *table* was stale — the finding's numbers were the ones that had to go |
| `e54` | the network `naive` arm's per-seed values existed for one of six distinct computations | the pooling had to be restricted to the one that agrees |
| **here** | **the run behind the network line's best result is absent entirely** | **the claim cannot be checked either way** |

## 3. And the nearest artifact that does exist gives it at 1.17σ, not 4.2σ

The five artifacts that carry a `replay` arm all use pool 16 / per-step 16. Their replay-versus-naive
**forgetting** contrast, per seed:

| run | n | replay | naive | Δ | σ | signs | LOO σ range |
|---|---|---|---|---|---|---|---|
| `e8_hardened` (λ=0.003, batches 32, hardened) | 5 | +0.0500 | +0.0729 | **−0.0229** | **−1.17** | `+----` | **[0.67, 5.66]** |
| `e8_hardened_basis` (same) | 5 | identical to the above | | | | | |
| `e8_class_incremental` | 5 | +0.0646 | +0.0437 | **+0.0208** | **+0.70** | `-+++-` | [0.11, 1.28] |
| `e8_basis` (λ=0.1) | 3 | −0.0000 | +0.1007 | −0.1007 | −1.81 | `+--` | — |
| `e8_rate` (λ=1.0) | 3 | +0.0313 | +0.1354 | −0.1042 | −5.77 | `---` | — |

**The best available instance of the claim is −1.17σ, with one seed of five positive and a
leave-one-seed-out σ range of [0.67, 5.66]** — an eight-fold spread, i.e. a single seed moves the
conclusion from "nothing" to "5.7σ". And the two large σ are both at **n = 3** (5.77 and 1.81), which
is precisely the sample size plan rule 20 says to treat as provisional.

So the network line's status is the same as the C2b line's after `e46`: **every well-powered
measurement is a null.** `e46` gives the basis contrast at **+0.0039 ± 0.0161 (n = 16)**; here, replay
at the largest n available is 1.17σ, and its headline 4.2σ has no artifact.

## 4. The fix, which is cheap and launched

`e8_hardened` took **474 s (8 minutes)** for three methods across five replicates, so the missing run
is not expensive — it was simply never saved under a name that survived. **`e61` recreates the whole
budget sweep** at the hardened configuration:

```
--basis cell_class --lam 0.003 --fisher-batches 32 --shared-head --readout-size 32 \
  --input-overlap 0.0 --classes 4 --noise 1.0 --support 80 --seeds 5 --repeats 5 \
  --methods naive,replay --replay-per-task 96 --replay-batch {8, 16, 48}
```

So both halves of the finding — the 4.2σ and the budget inversion — become checkable, and their
per-seed structure becomes visible. This is the same move as `e58` for the C2 census gap and `e43` for
the `e5` provenance question: **when a claim has no artifact, the cheap answer is to produce one
rather than to argue about the number.**

**Two things went wrong in launching it, both worth recording because both are invisible from a
summary.** The first attempt passed `--seeds 5`, which `e8_rate_network` does not accept — it uses
`--repeats` — so all three runs exited instantly with argparse's `error: unrecognized arguments`, and
the shell loop still printed nothing alarming. That is the *second* time in this sequence that a flag
name has silently killed a run (the first was `--min_size`/`--min-size`); the lesson is the same and
still not automated: **check for an artifact, not for an exit path.**

The corrected single run then took longer than ten minutes under a loaded machine and was killed by
the default timeout — plan rule 16, in the same sequence — before writing its JSON. Its partial log
carries the check that matters, though: its `naive` arm gives **0.914 accuracy and +0.073 forgetting**,
matching `e8_hardened`'s 0.9139 / +0.0729 exactly, so **the reconstructed configuration is the right
one** and the comparison it enables will be like-for-like.

## 5. Limits

- **Absence of an artifact is not evidence the run did not happen.** The finding's numbers are
  specific and internally consistent (a three-point budget sweep, memory arithmetic at 96 × 12 × 1307
  floats = 6.0 MB, which checks out), so the most likely history is a real run whose JSON was
  overwritten by a later one sharing its `--json-out` path. What can be said is that **nothing on
  disk supports it**, which is the same standard `e41` applied.
- **`e61` is a recreation, not a reproduction.** It cannot confirm that the original run produced
  −0.010 ± 0.006; it can only produce a number for that configuration with its own seeds and its own
  per-seed structure. If they agree, that is strong; if not, the original is unrecoverable.
- **Per-step 8 / pool 96 may not be the optimum.** The finding says "best when tuned", and `e61`
  sweeps only the three per-step values the finding names; the pool size is held at 96 throughout.
- **The other method in the comparison is `naive`**, whose per-seed spread at this configuration is
  itself large (the e54 census puts `e8_hardened`'s naive in a cluster of its own, differing from the
  main one in `shared_head`/`readout_size`), so the contrast carries both arms' spread.
