# `e153` landed: the registered claims hold, and its own C0a control fails on exactly the three penalty arms

> **CORRECTED THE SAME EVENING, AND THE CORRECTION REMOVES THE FINDING.** Section 2 below treats the three penalty
> arms' difference as evidence about reproducibility. **It is not: `e153` ran at `lam = 1.0` and `e144` at
> `3e-3`** — one config field, omitted from the registration's paraphrase of the command, which the launch then
> used (the runner's default is `lam = 1.0`). That explains the whole pattern exactly: the three arms that differ
> are the three that **read** `lam`, `naive` and `replay` are bit-identical because they do not, and the magnitude
> is a 333× stronger penalty. **So there is no evidence of penalty-arm non-reproducibility, §9's
> `--fisher-batches 32` claim is not contradicted by anything, and C0a's failure is a defect in the claim, not in
> the arms.** Rule 44 now requires a C0 identity claim to be checked against the two artifacts' `config` fields
> rather than against a paraphrased command. The evidence and the two further instances of the same shape are in
> `docs/findings/2026-09-24-the-penalty-arms-were-never-non-reproducible.md`; sections 1, 3 and 4 below stand as
> written (the registered claims hold, the artifact's numbers stand, and the newest-task column is unaffected).

**Date:** 2026-09-24
**Artifact:** `runs/e153_r32_overlap1_methods_40reps.json` — the wiring family's five-method table in one artifact,
and that configuration's second execution.
**The registration** is `docs/findings/2026-09-24-the-wiring-familys-five-method-table-registered.md`: **C0a** the
four reused arms must be per-replicate identical to `e144`'s; **C0b** the `replay` row must be identical to
`e148`'s; **P1** this artifact's `ewc-block − ewc-block-rand` lies within 2σ of `e144`'s **three-draw** mean
(−0.0078, total sem 0.0079); **P2** the family's ranking keeps `replay` first and the plain diagonal second;
**falsifier for P1** more than 2σ from the three-draw mean.

---

## 1. The registered claims

| claim | result |
|---|---|
| **P1** — the biology's contrast against the three-draw mean | this artifact gives **−0.0107 ± 0.0100**, which is **0.23σ** from the three-draw mean → **P1 HOLDS**, falsifier silent |
| **P2** — `replay` first, the diagonal second | `replay − ewc` **−0.0615 ± 0.0098 = 6.27σ**, and `replay − naive` **−0.0984 ± 0.0091 = 10.79σ** → **P2 HOLDS** |
| **C0b** — the `replay` row against `e148`'s | **per-replicate identical, worst difference 0** |
| **C0a** — the four reused arms against `e144`'s | **`naive` identical (0) — the three penalty arms are NOT** |

**The one artifact's table**, which is what the unit was for: `naive` **+0.1068**, `ewc` **+0.0698**,
`ewc-block` **+0.0633**, `ewc-block-rand` **+0.0740**, `replay` **+0.0083** — and the newest-task column in the
same table, against `naive`: `ewc` **−0.0276 (4.65σ)**, `ewc-block` **−0.0313 (5.60σ)**, `ewc-block-rand`
**−0.0245 (4.60σ)**, **`replay` +0.0047 (1.12σ)**. **So the family's whole comparison now sits in one artifact,
and the two-axis pattern is in it**: the diagonal is second on forgetting and third on the newest task, the block
arms are third and fourth on forgetting and pay 4.6–5.6σ there, and replay leads on both.

## 2. And C0a's failure is the finding

| arm | vs `e144` | worst per-replicate difference |
|---|---|---|
| `naive` | **identical** | 0 |
| **`ewc`** | **differs** | **0.229** |
| **`ewc-block`** | **differs** | **0.177** |
| **`ewc-block-rand`** | **differs** | **0.198** |
| `replay` (vs `e148`) | **identical** | 0 |

**And it is not a pairing or labelling artefact**: the sorted per-replicate values differ too (`np.sort` equal is
False for each of the three), so the arms genuinely computed different numbers on the same seed stream — and 15
to 20 of the forty replicates move by more than 0.05 on each.

**The code epoch is not the explanation.** The last commit touching `experiments/e8_rate_network.py` is at
**13:20**, and `e144` was *written* at 14:18 — but `e144`'s config **lacks the `partition_seed` key** that commit
added at **10:21**, so `e144`'s process started before 10:21 and ran for hours: **the epoch that matters is when a
process starts, not when its artifact lands.** What that commit changed is the **matched-random partition only**
(`--partition-seed`, defaulting to `--seed0`, so the draw is unchanged), and it touches neither the Fisher nor the
penalty path — so it cannot explain `ewc`'s difference, which has no partition at all.

**What the record can say instead is the pattern, and it is arm-specific and configuration-specific**:

| configuration | `naive` | the penalty arms |
|---|---|---|
| base family, `e140` vs `e133` (3 h apart, different `lam`/`fisher_batches`/replay settings) | identical | **`ewc` identical** |
| base family, `--fisher-batches 32` at five replicates (`e101` vs `e102`) | identical | identical on all five arms |
| **wiring family, `e144` vs `e153` (7 h apart, same epoch for the penalty path)** | identical | **all three differ** |

**So §9's sentence *"at `--fisher-batches 32` the whole five-arm benchmark reproduces exactly: 280 of 280 numeric
fields"* is a statement about the base family at five replicates**, and the first execution of the *wiring* family
at forty replicates breaks it on the three penalty arms by up to 0.229 per replicate — while `naive` and `replay`
reproduce to the last digit for the third and fourth time today.

**And the project's own audit found it without being told**: the arm-overlap check added to `e103` this fire
reports this pair and no other same-configuration pair of `e153`'s, so the extension's first act on real data is
to catch a control failure a registration had predicted would be an identity.

## 3. What would settle it, and it is running

**A third execution of the same command decides between "one-off/epoch" and "run-to-run"**: if a third run matches
`e153` exactly, then `e144` was the outlier (an epoch effect after all, and the penalty path is deterministic); if
it differs from both, the penalty arms are run-to-run non-reproducible and **every penalty-arm number in this
paper carries a run-to-run term no previous measurement has sized**. `e159` is that run, launched on the slot the
queue freed, and its registered reading is in the plan's programme table.

## 4. What this cannot settle

- **One pair of executions is not a rate**: seven hours apart, different epochs for some of the code, and the
  family has only two executions — so "the wiring family's penalty arms are not reproducible" is the honest
  description of what happened, not yet a property of the family.
- **`e103`'s movement figure and mine are different quantities**: the audit reports the spread of the arms'
  *means* (0.0068, 0.0201, 0.0112 here) and the `exact` flag, while the per-replicate worst differences above
  (0.229, 0.177, 0.198) are the reason `exact` is false — both are true and the second is the one that matters for
  a paired contrast.
- **It does not touch this artifact's own numbers**, which are internally consistent and paired on their own
  seeds; it touches every *cross-artifact* comparison that assumed the penalty arms are deterministic — including
  the two-draw and three-draw controls built from `e144`, whose draws are separate executions of the same command
  and therefore now have a second source of spread besides the partition draw.
