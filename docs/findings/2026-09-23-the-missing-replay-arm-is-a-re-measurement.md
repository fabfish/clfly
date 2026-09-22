# E84 (task-IL) — the missing replay arm is a **re-measurement, not a restoration**, and the fingerprint failed for the reason rule 21 predicted

**Date:** 2026-09-23
**Script:** `experiments/e84_replay_other_settings.py`
**Artifacts:** `runs/e84_replay96_taskIL_5reps.json`, `runs/e84_replay_other_settings.json`
**Context:** `2026-09-23-the-replay-result-reproduces.md` (e61), `2026-09-23-the-c2b-rung-result-was-three-seeds.md` (e46), `2026-09-22-the-replay-result-has-no-artifact.md` (e62), plan rule 21

---

## 1. The gap, and the test that was supposed to settle it

`e62`'s census found `replay_per_task: 96` in **exactly one** artifact carrying a `naive` arm — `e61`'s
own recreated run. Of the four replay numbers the paper's §4.7 carries, the hardened class-IL setting is
now recreated (6.73σ at sixteen replicates); **the task-incremental and class-incremental settings at pool
96 / per-step 8 have no artifact at all**.

The plan's pre-registration for this run said the task-IL arm was *validatable*, because `naive` carries no
basis and no penalty and is therefore fixed by the configuration alone — `e54` used exactly that property
to group artifacts by computation rather than by an assumed config key. The settled finding reports
task-IL naive **+0.101**, matching `e10_rung_*`'s stored **0.8241 / +0.1007**. **The prediction: a
recreation whose naive reproduces that is the same computation. The falsifier: a naive that does not.**

## 2. The falsifier fires, and the diagnosis is the one rule 21 wrote down

| | recreated (5 reps) | stored (`e10_rung_*`, 3 reps) |
|---|---|---|
| naive accuracy | **0.8417 ± 0.0056** | **0.8241** |
| naive forgetting | **+0.1000 ± 0.0212** | **+0.1007** |

Same configuration in every field that can affect `naive` — the run was built to match `e10_rung_*` field
by field, with only the inert ones (methods, replay settings, λ) differing. **And the per-seed values say
what kind of difference this is:**

```
e84 task-IL naive  0.8333  0.8264  0.8403  0.8542  0.8542      mean 0.8417
e54 cluster 0      0.8958  0.7917  0.7847  0.8333  0.8542      mean 0.8319
        difference -0.0625 +0.0347 +0.0556 +0.0208  0.0000
```

Large, **mixed-sign** per-seed differences with one seed coinciding exactly — the signature of a different
training *trajectory*, not of a systematic offset or a wrong parameter.

**The cause is the environment.** `e77` established that the same command under a different
`OMP_NUM_THREADS` trains to a different result, and rule 21 codified the consequence. This run went out
with `OMP_NUM_THREADS=3`; `e10_rung_*`'s setting is recorded **nowhere**. So:

> **A missing artifact cannot be restored across environments.** The `naive` fingerprint is a valid
> identity test *within* one environment — and `e54`'s census, which is built on it, remains sound for the
> artifacts it grouped — but it is not a restoration test, because nothing in the record says what the
> environment was.

This is rule 21's first *practical* casualty rather than a methodological note. It also, usefully,
reaffirms the census: `e10_rung_*`'s three-replicate mean **0.8241** is exactly the mean of `e54` cluster
0's first three seeds, so those artifacts really do share a computation — inside their environment.

## 3. What the re-measurement gives, at five replicates

| | recreated, n = 5 | claimed, n = 3 |
|---|---|---|
| naive forgetting | +0.1000 ± 0.0212 | +0.101 ± 0.049 |
| replay forgetting | **−0.0042 ± 0.0091** | **−0.056 ± 0.009** |
| replay accuracy | 0.9319 ± 0.0034 | 0.921 |
| **replay − naive, forgetting** | **−0.10417 ± 0.01647 = 6.32σ**, `-----`, LOO min 4.84 | −0.157 at 3.1σ |
| **replay − naive, accuracy** | **+0.09028 ± 0.00761 = 11.87σ**, `+++++`, LOO min 9.62 | — |

**The arm reproduces in direction and with stronger evidence than the claim, but not in level.**

* the forgetting contrast is **−0.104 at 6.32σ with five of five replicates negative** and a
  leave-one-out floor of 4.84σ, against the claimed −0.157 at 3.1σ — the same effect with twice the
  evidence and a magnitude 34% smaller;
* the **accuracy** contrast is the strongest single number in the network line: **+0.090 at 11.87σ**,
  5/5 positive, LOO 9.62;
* and **replay's own forgetting does not reproduce: −0.0042 ± 0.0091 is 0.46σ from zero**, where the claim
  needs −0.056 ± 0.009 — a **6.3σ disagreement**. So *"replay eliminates forgetting in task-IL"* is
  supported, and *"replay drives forgetting 0.056 below zero"* is not.

## 4. What this does to the paper's §4.7 table

The task-IL row is one of the three whose artifact `e62` found missing, and this run is the only evidence
that exists for it. It should be reported as a **re-measurement under the described configuration, in a
different environment from the original**, with:

* the contrast (forgetting −0.104 at 6.32σ, accuracy +0.090 at 11.87σ) — the part that reproduces and with
  better evidence than the claim;
* replay's absolute forgetting as **≈ 0 (−0.0042 ± 0.0091)** rather than −0.056;
* and the explicit note that the fingerprint **failed**, so this is not the published computation. The
  table already carries a "no artifact" flag for two other pool-96 rows; this row now carries
  "re-measured, environment differs" instead, which is a more informative and less comfortable label.

## 5. Limits

- **Five replicates, one environment.** The contrast's σ is 6.32 and its leave-one-out floor 4.84, so no
  single replicate carries it; but the *level* of replay's forgetting rests on a comparison against a
  claim made in a different environment, and that comparison is the part that failed.
- **The environment is not recoverable.** `OMP_NUM_THREADS` was not recorded for any artifact before
  rule 21, so there is no way to re-run `e10_rung_*`'s environment deliberately and ask whether the
  fingerprint then passes. The honest statement is that the mismatch is *consistent with* the thread
  effect and cannot be attributed to it with certainty — a wrong-but-unrecorded parameter would look
  similar, and the field-by-field config diff is what rules that out as far as it can.
- **The class-IL arm of this run is still going.** Its fingerprint was never validatable — the claim's
  naive (+0.059 ± 0.028) matches no stored artifact, and the closest stored class-IL naive is
  `e8_class_incremental`'s 0.9361 — so it will be a re-measurement by construction, and the analysis script
  says so before printing any of its numbers.
