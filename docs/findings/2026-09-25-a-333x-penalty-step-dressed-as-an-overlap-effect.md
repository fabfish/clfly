# A 333× penalty step dressed as an overlap effect — caught before it was read, and the level-0.25 numbers

**Date:** 2026-09-25
**Read of:** `runs/e193_r32_overlap025_methods_40reps.json` (target overlap 0.25 → **achieved Jaccard 0.1429**,
40 replicates, three arms) against the baselines each arm admits, five minutes after it landed.
**Instruments:** `e191 --dose` (the interference account, name-matched) and `e188 --dose` (the accuracy drop), both
of which had to be fixed **before** this read meant anything.

---

## 1. The launch inherited `--lam 1.0`, and the audit's own admission rule is what caught it

The three `e193` commands were launched with `--methods naive,ewc-block,ewc-block-rand` and one `--input-overlap`
each, "everything else copied from `e140`". Everything else was **not** copied: the commands do not pass `--lam`, so
they inherited the runner's default **λ = 1.0**, while the family they were registered against — `e140` (overlap 0.0),
`e144`/`e153` (overlap 1.0) — runs **λ = 3e-3**. Measured config diff, launched level against `e140`:

| field | `e140` (ov0, the registered family) | launched level |
|---|---|---|
| `lam` | 3e-3 | **1.0** (the default) |
| `methods` | naive,ewc,ewc-block,ewc-block-rand,replay | naive,ewc-block,ewc-block-rand |
| `replay_batch` / `replay_per_task` | 8 / 96 | 16 / 16 |

**`lam` is inert for `naive` and is the penalty strength for the block arms** — so the first read of this artifact
was going to report a **333× penalty step as an overlap effect**, on the two arms where the effect looked largest:
`ewc-block`'s forgetting moved **+0.0513 = 4.9σ** against `e140` and **+0.0453 = 4.1σ** against `e153`, and its
interference moved **−0.0930 = 11.6σ** against `e140` and **+0.0010 = 0.3σ** against `e153`. Same artifact, same
field, two baselines, opposite stories.

**The fix is admission at the arm level**, which the two-point audit has had since `e188` and the dose reads were
written without: each arm takes the first candidate baseline whose config diff from the level is **inert for that
arm** (`e140` first, then `e153`), and refuses with the reason otherwise. Both dose reads now do that, and print the
baseline each row used. **So the artifact is not wasted and nothing was re-run**: the same three files are a
**λ = 1.0 dose-response** read against `e153` (λ = 1.0, overlap 1.0) for the block arms, and a **λ = 3e-3,
overlap-0 dose-response** read against `e140` for `naive` — the arm the registration's P1 and P2 are stated on.

## 2. The level-0.25 read, on the arms its own admission rules allow

| arm | baseline (and why) | forgetting Δ | accuracy Δ | interference Δ (adjacent) |
|---|---|---|---|---|
| `naive` | `e140` (λ inert for naive) | **+0.0141 ± 0.0121 = 1.2σ** | −0.0028 = 0.3σ | **+0.0152 ± 0.0123 = 1.2σ** |
| `ewc-block` | `e153` (λ = 1.0 family) | **+0.0453 ± 0.0110 = 4.1σ** | −0.0309 = 4.2σ | +0.0010 = **0.3σ** |
| `ewc-block-rand` | `e153` | +0.0159 = 1.5σ | −0.0111 = 1.6σ | +0.0035 = 0.3σ |

Three things follow, and the third is the interesting one:

- **`naive` moves in the registered direction and is unresolved at n = 40**: +0.0141 is **44%** of its full 0 → 1
  rise (+0.0318) at **40%** of the x-axis (achieved 0.1429 of 1.0), and its interference rise is **12%** of the full
  0 → 1 rise (+0.0152 of +0.1234). So on the regime's own scale the response is **slow at first and steep later**,
  or the sub-population at 0.1429 is not yet doing much — the level-0.5 artifact (achieved 0.3333) is what decides it.
- **The registered P1's bar does not apply here, and the first version of the read said it did.** P1 as registered is
  a statement about **achieved 0.3333** — the midpoint — and the print tagged "P1's bar NOT met" on this level, which
  is a claim the registration does not make. Fixed: the bar is checked only where it is registered, and elsewhere the
  row says so.
- **The block arms' forgetting moves 4.1σ while their own interference term moves 0.3σ** — a dissociation measured on
  one artifact, and the sharpest thing in this read: the first-order account does not track that arm's forgetting at
  this level. It is the `e139` shape again (the θ-only form cut by 98% while forgetting moved), now inside the same
  comparison rather than across two.

## 3. What is pending, and what would make this read wrong

**Levels 0.50 and 0.75 are running** (`e193` continues; the 0.50 command was at 9/120 arm-replicates when this was
written). They carry the registered P1 and P2 checks, on `naive` against `e140`, and their own block-arm rows
against `e153`.

**What would make §2 wrong**: a further field that differs and is inert for the arm it is compared on — the reads now
print the admitted differences beside every row, so a reader can see them rather than trust the header, and the one
field that mattered (`lam`) is named. And the λ = 1.0 block rows are a **different family** from the registered one:
they are evidence about the overlap axis at λ = 1.0, not about the dose-response the registration describes, which
is why they are reported as such and not pooled with the `naive` rows.

## 4. Carried into the run's own row

The plan row for `e193` now records the mis-specified launch, the two-family salvage and the per-arm rates
(`naive` 20–27 s, `ewc-block` 66–75 s per arm-replicate), and the read commands with their `--baseline` defaults.
No artifact was discarded and no command was re-run: the mistake cost an instrument fix and a paragraph, which is the
cheapest form it could have taken.

## Reproduce

```
uv run python -m experiments.e191_interference_across_lines --dose runs/e193_r32_overlap025_methods_40reps.json
uv run python -m experiments.e188_overlap_contrast       --dose runs/e193_r32_overlap025_methods_40reps.json
```
