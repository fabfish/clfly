# `e140` pre-registered: the five-method table at forty replicates, in both arms

**Date:** 2026-09-24
**Status:** pre-registered **before** the runs. Committed as its own commit; the runs are launched after it.
**Script:** `experiments/e8_rate_network.py`, unchanged.
**Planned artifacts:** `runs/e140_r32_methods_plastic_40reps.json` and
`runs/e140_r32_methods_frozenbias_40reps.json`, each

```
--methods naive,ewc,ewc-block,ewc-block-rand,replay --repeats 40 --replay-per-task 96 --replay-batch 8
--circuit-size 800 --iters 500 --lr 3e-3 --batch 32 --lam 3e-3 --train 96 --test 48 --noise 1.0
--classes 4 --support 80 --shared-head --input-overlap 0.0 --readout-size 32 --fisher-batches 32 --seed0 0
```

with the second arm adding `--frozen-bias`.
**Comparators:** `runs/e135_r32_methods_{plastic,frozenbias}.json` (the same table at **five** replicates, the
finding that raised this question), `runs/e133_r32_naive_ewc_40reps.json` (the plastic `naive` and `ewc` rows at
forty) and `runs/e125_r32_frozenbias.json` (frozen-bias `naive` at forty).

## Why forty replicates, and why both arms, and the arithmetic that makes the prediction sharp

`e135` found that removing the unpenalised channel from **every** arm changes exactly one of the four contrasts
against `naive`: **replay's advantage is cut by 66%, from −0.0854 to −0.0292**, a move of **2.23σ** — a suggestion,
because five replicates is what it had. It also found that under that arm the ranking is **ewc (−0.0104) <
replay (−0.0042) < ewc-block-rand (+0.0104) < ewc-block (+0.0167) < naive (+0.0250)**, i.e. **diagonal EWC becomes
the best method**, where the plastic table has replay first by a wide margin.

**The registration's fire is a resolvability claim, and it is arithmetic rather than hope.** At forty paired seeds
on this configuration the paired sem of a contrast against `naive` is **≈ 0.008** (`e133`: ewc − naive is
−0.0096 ± 0.0080). The frozen arm's ewc − naive contrast that `e135` saw at five replicates is **−0.0354**, which
is **4.4×** that sem — so a forty-replicate frozen arm **can resolve it if it is real**. The plastic arm's same
contrast is **−0.0096**, i.e. **1.2×** the sem, which is why forty replicates cannot resolve it and why `e133`
reported 1.21σ. **So the two arms at the same forty seeds ask opposite halves of one question**: *does removing
the channel that carries 70% of the forgetting make the penalty's advantage visible at the sample where the
penalty's own headline is invisible?*

## The controls, and one of them is a probe rather than a check

- **C0a, must hold.** The plastic arm's **`naive` and `ewc` rows are per-replicate identical to `e133`'s forty
  values**, and the frozen arm's `ewc` **first five** replicates are per-replicate identical to `e135`'s five.
  Each is the same command at the same seeds, so a mismatch is a bug in the epoch rather than a result.
- **C0b, and this one is a probe.** The frozen arm's **`naive` forty values are per-replicate identical to
  `e125`'s**, whose `fisher_batches` (**8**, against this fire's 32), `lam` (**1.0**, against 3e-3) and replay
  settings (**16/16**, against 96/8) all differ. `naive` constructs no Fisher and receives no replay buffer
  (`e8_rate_network.py`: `replay=(replay if method == "replay" else None)`, and the `ewc` tuple is built only for
  `method == "ewc"`), so **it must hold**. If it does not, then a setting the code does not read is reaching the
  arm — and every "identical command, identical numbers" claim in this project's record acquires a caveat that
  is worth more than this fire. This is rule 29 with a measurement attached rather than a code reading.
  **`config` records what was asked for; this is where that stops being a slogan.**
  **And the invariance already has measured precedents, which is worth saying so that a pass says less than it
  looks like it does.** Each of C0b's four differences has been crossed at these seeds before:
  `runs/e116_r32_40reps.json` is `naive` at **`fisher_batches` 8** and `e133`'s `naive` at **32** is
  per-replicate identical to it **across all forty replicates**; `runs/e61_replay96_step8.json` is `naive` at
  replay **96/8** and its five values are identical to `runs/e8_hardened_basis.json`'s `naive` at **16/16**; and
  `e133`'s `naive` (written in a process that also built a Fisher and trained `ewc`) is identical to `e116`'s
  `naive`-only arm, which is C0a's invariance. So C0b is a **confirmation under a conjunction of four settings
  at once, not a first test**, and what would make it informative is a failure: that would say the invariance is
  setting-specific rather than general.

## The predictions

- **P1, the fire.** In the **frozen** arm, `ewc` − `naive` resolves at **≥ 3σ** and is **negative** (the penalty
  helps). *The direction is registered and so is the threshold, because the size is not new: what is new is
  whether forty replicates can see it.*
- **P2.** In the frozen arm, replay's margin over `naive` is **smaller** than in the plastic arm, on the same
  seeds: the difference of differences resolves at **≥ 2σ**. `e135`'s five-replicate version of this is
  **+0.0563 ± 0.0252 = 2.23σ**.
- **P3, descriptive and registered so that it is reported.** The five-method ranking in each arm, and whether the
  **penalties' mutual ordering** (ewc best, block worse, matched-random between) is the same in both arms. That
  ordering is the paper's central network result — the *basis* question — and `e135` found it confound-robust at
  five replicates; whether it survives at forty is a separate question from P1 and is reported either way.
  **The three Fisher penalties' contrasts against `naive` are also expected to be near-identical between arms**
  (0.42σ, 0.21σ, 0.48σ at five replicates), for the same reason as C0b: no penalty touches the bias.
- **Falsifier.** The frozen arm's `ewc` − `naive` contrast is **within 2σ of zero**. Then removing the channel
  does not let the penalty beat `naive`, and the reading §4.2 currently invites — *the penalty acts on the half
  the damage does not live in* — is **not** why diagonal EWC fails. The reason would have to be found in **how**
  the penalty acts rather than in **what it covers**, which would make `e125`'s 70% a fact about the naive
  baseline and not about EWC at all.

## What this cannot settle, in advance

- **One read-out (32), one λ (3e-3), one replay budget (96/8), three tasks, one circuit.** Read-out 32 is where
  the channel's share is **largest** (70%, against 89% and 83% at read-outs 128 and 1307 — `e134`), which is the
  right place to ask whether the channel is the explanation and the wrong place to generalise from.
- **`--frozen-bias` is a diagnostic, not a method.** A ranking produced under it is a **ranking of these five
  methods on a model class whose 800 offsets never move**, and it is not a recommendation that a practitioner
  freeze them: the offsets are trainable parameters of the published model and freezing them changes the model.
  The reason the arm is legitimate is different and narrower — it is the only arm in which **the confound is
  absent from every method at once**, which is what makes the contrasts comparable.
- **The frozen arm's ewc row is a forty-replicate measurement of a number `e125` first reported as a by-product**,
  so the *level* of the ranking is new even though the ordering is not.
- **And it is a run of the same script**, so everything about the substrate — the connectome, the task suite, the
  rate model's own limits — is as `e133` left it. This fire can move a method comparison and nothing else.
