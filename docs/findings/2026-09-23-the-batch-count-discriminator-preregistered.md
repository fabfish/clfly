# E101 — the batch-count discriminator, pre-registered: a manipulation that fixes the level exactly

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py`, `e8_hardened_basis`'s configuration at `--fisher-batches 8` and
`128` (32 is already on disk); artifacts `runs/e101_rate_fb8.json`, `runs/e101_rate_fb128.json` (in flight).
**Context:** `docs/findings/2026-09-23-the-competing-explanation-is-not-excluded.md`, which found that
separating the estimation-noise account from the "easier benchmark compresses the gaps" hypothesis needs
**~57 replicates per arm and 6–44 hours** for one contrast, and asked for a control that lowers difficulty
without lowering task rank.

---

## 1. There is a cheaper discriminator, and it was already in the data

The expensive control varies *difficulty* and hopes the level and the mechanism move apart. **The
`--fisher-batches` knob separates them by construction**, because the benchmark has arms that do not consult a
Fisher matrix at all:

| arm | uses the Fisher? |
|---|---|
| `naive` | **no** |
| `replay` | **no** |
| `ewc`, `ewc-block`, `ewc-block-rand` | yes |

So changing the batch count moves the three Fisher arms and leaves the other two **bit-identical**, and the
level — which is the `naive` arm's forgetting — is **provably fixed**. Verified from the `e96` sweep already
on disk, which ran all three batch counts in one process at λ = 0.1:

| batches | `naive` | `ewc` | `ewc-block` | `ewc-block-rand` |
|---|---|---|---|---|
| 8 | **+0.1354** | +0.0521 | +0.1875 | +0.0625 |
| 32 | **+0.1354** | +0.0833 | +0.2396 | +0.1771 |
| 128 | **+0.1354** | +0.1458 | +0.2708 | +0.1875 |

**`naive` is identical to four decimals across the sweep while every Fisher arm moves.** So any change in the
block's standing under this manipulation is not a level effect — the level did not move.

**And the one version of this test that exists is single-seed and therefore undecided**: from those same
three artifacts, block-minus-matched-random is **+0.1250, +0.0625, +0.0833** as batches go 8 → 32 → 128 —
down then up — and block-minus-diagonal is **+0.1354, +0.1563, +0.1250**, which is flat. The per-repeat
forgetting sd at this configuration is **0.019–0.084**, so a 0.06 movement in a gap is about one replicate's
own variation at one seed. **The test needs replicates, and two runs supply them.**

## 2. The design, and why the primary clause is on the control contrast

`--fisher-batches 8` and `128`, `e8_hardened_basis` otherwise field for field (λ = 0.003, cs = 800, 4
classes, 5 replicates, `cell_class`, `readout_size` 32, `shared_head`), against the **32**-batch run already
on disk. Three points, five replicates each.

**P1 — the control, and the primary clause.** The block-minus-**matched-random** gap shrinks as the batch count
rises: **block − rand(8) > block − rand(32) > block − rand(128)**, with the two ends resolvable. This is the
symmetric contrast under a batch sweep, because the matched random control is the *same partition shape* and
sees the *same* batch count, so a change in penalty strength moves both arms and cancels.

**P2 — the built-in control, which voids the run if it fails.** `naive`'s and `replay`'s mean forgetting are
**identical to four decimals** across the three runs. They do not use a Fisher matrix, so any difference at all
means something other than the batch count changed and the comparison is void. **This clause is checked first,
and if it fails the run is reported as void rather than as a result.**

**P3 — a prediction in the *other* direction, on the contrast that is confounded.** Block-minus-**diagonal**
should **not** shrink monotonically, and the reason is measured rather than assumed: raising the batch count
makes the diagonal's penalty *stronger at fixed λ* — `e96` measured the diagonal's forgetting rising
**+0.052 → +0.083 → +0.146** across 8 → 32 → 128 at λ = 0.1 — so both arms of this contrast get worse
together and the difference between them is not attributable to estimation quality. **The clause is that this
contrast is reported as secondary and *not* used to decide H1**, which is the design choice the earlier
findings could not make because they had only this contrast.

**Falsifier.** The block-minus-matched-random gap does **not** shrink with the batch count, while `naive`
stays identical. That is a *positive* disconfirmation of the estimation-noise account on the axis built to
test it — with the level fixed, so no level explanation is available — and it would leave the account
supported by the two configuration changes of `e99`/`e100` and contradicted by the one manipulation that
isolates its mechanism.

## 3. What this does not settle

- **Three points on one axis.** Even a clean monotone result would be one axis, and `e99`/`e100` are two other
  axes; the account's case would be three axes agreeing rather than a mechanism measured.
- **The batch count also changes how strong every Fisher penalty is**, which is why P1 is gated on the
  symmetric contrast. A cleaner design would vary the *estimation quality* without varying the penalty
  strength — a different prior, or a shrinkage estimator — and that is not a knob this benchmark has.
- **Five replicates give a sem near 0.02 against a per-repeat sd of 0.019–0.084**, so the resolvable
  difference between two gaps is about 0.06. A P1 that holds by 0.03 will be a direction and not a result.
