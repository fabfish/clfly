# E84 — both missing replay arms reproduce in direction, and **neither is a restoration**: the `naive` fingerprint fails because the environment is unrecorded

**Date:** 2026-09-23
**Script:** `experiments/e84_replay_other_settings.py`
**Artifacts:** `runs/e84_replay96_taskIL_5reps.json`, `runs/e84_replay96_classIL_5reps.json`, `runs/e84_replay_other_settings.json`
**Context:** `2026-09-23-the-replay-result-reproduces.md` (e61), `2026-09-22-the-replay-result-has-no-artifact.md` (e62), `2026-09-22-naive-arm-census.md` (e54), plan rule 21

---

## 1. The gap, and the test that was supposed to settle it

`e62`'s census found `replay_per_task: 96` in **exactly one** artifact carrying a `naive` arm — `e61`'s
own recreated run. Of the four replay numbers the paper's §4.7 carries, the hardened class-IL setting is
now recreated (6.73σ at sixteen replicates), and the **task-incremental and class-incremental settings at
pool 96 / per-step 8 had no artifact at all**. This run fills both.

The plan pre-registered the test: `naive` carries no basis and no penalty, so the configuration fixes it
exactly, and `e54` used that property to group artifacts by computation rather than by an assumed config
key. The settled finding reports task-IL naive **+0.101**, matching `e10_rung_*`'s stored **0.8241 /
+0.1007** — so a recreation whose naive reproduces that is the same computation. **Prediction: it does.
Falsifier: it does not.**

## 2. The falsifier fires on both arms, and the diagnosis is the one rule 21 wrote down

| setting | recreated naive | stored comparison | identical |
|---|---|---|---|
| task-IL | **0.8417 / +0.1000** | `e10_rung_*`: 0.8241 / +0.1007 | no |
| class-IL | **0.9194 / +0.0688** | `e8_class_incremental`: 0.9361 / +0.0437 | no |

Same configuration in every field that can affect `naive` — both runs were built to match field by field,
with only the inert ones (methods, replay settings, λ) differing. **And the per-seed values say what kind
of difference this is:**

```
e84 task-IL naive  0.8333  0.8264  0.8403  0.8542  0.8542      mean 0.8417
e54 cluster 0      0.8958  0.7917  0.7847  0.8333  0.8542      mean 0.8319
        difference -0.0625 +0.0347 +0.0556 +0.0208  0.0000
```

Large, **mixed-sign** per-seed differences with one seed coinciding exactly — the signature of a different
training *trajectory*, not a systematic offset or a wrong parameter.

**The cause is the environment.** `e77` established that the same command under a different
`OMP_NUM_THREADS` trains to a different result, and rule 21 codified the consequence. Both of these runs
went out with `OMP_NUM_THREADS=3`; the originals' settings are recorded **nowhere**. So:

> **A missing artifact cannot be restored across environments.** The `naive` fingerprint is a valid
> identity test *within* one environment — and `e54`'s census remains sound for the artifacts it grouped,
> as this run's own check shows: `e10_rung_*`'s three-replicate mean **0.8241** is exactly the mean of
> `e54` cluster 0's first three seeds — but it is not a restoration test.

This is rule 21's first *practical* casualty rather than a methodological note.

**A wrinkle on the class-IL arm worth recording**: its recreation is **closer to the claim** (naive
0.9194 / +0.0688 against the claim's 0.928 / +0.059) than to the stored artifact it is compared with
(`e8_class_incremental`'s 0.9361 / +0.0437). So the settled finding's class-IL configuration was neither
this run's nor that artifact's, and the fingerprint has no valid reference for it at all — which is why
the plan said in advance that this arm could be re-measured but not confirmed.

## 3. What the two re-measurements give, at five replicates

| | | recreated, n = 5 | claimed, n = 3 |
|---|---|---|---|
| **task-IL** | naive forgetting | +0.1000 ± 0.0212 | +0.101 ± 0.049 |
| | replay forgetting | **−0.0042 ± 0.0091** | −0.056 ± 0.009 |
| | replay accuracy | 0.9319 ± 0.0034 | 0.921 |
| | **contrast, forgetting** | **−0.10417 ± 0.01647 = 6.32σ**, `-----`, LOO 4.84 | −0.157 at 3.1σ |
| | **contrast, accuracy** | **+0.09028 ± 0.00761 = 11.87σ**, `+++++`, LOO 9.62 | — |
| **class-IL** | naive forgetting | +0.0688 ± 0.0296 | +0.059 ± 0.028 |
| | replay forgetting | **+0.0063 ± 0.0150** | −0.010 |
| | replay accuracy | 0.9611 ± 0.0084 | 0.975 |
| | **contrast, forgetting** | **−0.06250 ± 0.01647 = 3.79σ**, `-----`, LOO 2.84 | −0.069 at 2.2σ |
| | **contrast, accuracy** | **+0.04167 ± 0.00905 = 4.60σ**, `+++++`, LOO 3.48 | — |

**Both arms reproduce in direction, and both carry more evidence than the claims did:**

* **task-IL** — the contrast is 6.32σ against the claimed 3.1σ, five of five replicates negative, with a
  leave-one-out floor of 4.84σ; but its magnitude is 34% smaller (−0.104 against −0.157) and **replay's own
  forgetting is −0.0042 ± 0.0091, i.e. 0.46σ from zero** where the claim needs −0.056 ± 0.009 — a **6.3σ
  disagreement**.
* **class-IL** — the contrast is 3.79σ against the claimed 2.2σ, and **every one of the claim's four
  numbers is inside my interval**: naive forgetting +0.0688 against +0.059 ± 0.028, replay forgetting
  +0.0063 against −0.010, replay accuracy 0.9611 against 0.975, contrast −0.0625 against −0.069. This is
  the closest reproduction of a network-line claim in the project, and it is also the arm whose
  configuration could not be pinned — so the agreement says the *effect* is robust to the details of how
  that setting is instantiated, not that the original computation was recovered.
* **and the accuracy contrasts are the cleanest numbers either arm has**: +0.090 at 11.87σ and +0.042 at
  4.60σ, five of five positive each, leave-one-out floors 9.62 and 3.48.

**One claim the abstract must lose.** It says replay drives forgetting "to zero or below". In neither of
these settings does replay's own forgetting sit **below** zero with any confidence: −0.0042 ± 0.0091
(task-IL, 0.46σ) and +0.0063 ± 0.0150 (class-IL, 0.42σ above zero). What reproduces is *driven to zero*,
which is the part LGCL's prediction actually needs; the "or below" was a three-replicate reading.

## 4. What this does to the paper's §4.7 table

Two of the three rows `e62` flagged are now measured, and both carry the label the plan anticipated:
**re-measured, environment differs** — not "restored". The class-IL row's agreement with its claim is
striking and should be stated plainly, with the caveat that the configuration is inferred rather than
confirmed. The task-IL row's `-0.056` should become **≈ 0**, with the contrast kept.

## 5. Limits

- **Five replicates, one environment, two settings.** Every contrast has a leave-one-out floor between
  2.84 and 9.62 and no sign flip, so no single replicate carries any of them; but the *levels* compared
  against the claims were measured in a different environment, and that is the comparison that failed for
  task-IL.
- **The environment is not recoverable.** `OMP_NUM_THREADS` was not recorded for any artifact before rule
  21, so there is no way to re-run either original's environment deliberately and ask whether the
  fingerprints then pass. The honest statement is that the mismatches are *consistent with* the thread
  effect and cannot be attributed to it with certainty — a wrong-but-unrecorded parameter would look
  similar, and the field-by-field config diff is what rules that out as far as it can.
- **The class-IL configuration is inferred.** The settled finding describes it as "shared head, whole
  state"; this run used `--shared-head` with the default read-out and no `--input-overlap`, and the result
  is closer to the claim than any stored artifact is. That is evidence about the effect's robustness and
  not about the original.
- **Replay's pool is held at 96 and per-step at 8** throughout, as the claims name.
