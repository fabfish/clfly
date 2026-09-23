# `e133`: diagonal EWC does not survive its own configuration at eight times the replicates — it redistributes

**Date:** 2026-09-24
**Script:** `experiments/e8_rate_network.py`, unchanged; artifacts `runs/e133_r32_naive_ewc_40reps.json` (naive
and ewc, 40 replicates each, the paper's hardened configuration) and `runs/e125_r32_frozenbias.json`.
**C0's comparator:** `runs/e116_r32_40reps.json` (naive, 40 replicates) and `runs/e8_hardened_basis.json` (the
five-replicate table the paper quotes).
**Setup:** `mb+cx+al@n1307` (cs = 800), 3 tasks, chance 0.25, `--methods naive,ewc --shared-head
--input-overlap 0.0 --noise 1.0 --iters 500 --lr 3e-3 --batch 32 --test 48 --readout-size 32 --lam 3e-3
--fisher-batches 32 --circuit-size 800 --repeats 40 --seed0 0`.
**Pre-registration:** `docs/findings/2026-09-24-does-the-penalty-beat-the-free-constraint-preregistered.md`.
**Both registered predictions fail, and the falsifier fires in the opposite direction.**

---

## 1. The result

| arm | forgetting | per-repeat sd | accuracy |
|---|---|---|---|
| **naive** | **+0.0750 ± 0.0088** | 0.0556 | 0.9125 |
| **EWC**, diagonal, λ = 0.003, 32 Fisher batches | **+0.0654 ± 0.0079** | 0.0502 | **0.8856** |
| **frozen-bias**, no penalty at all | **+0.0227 ± 0.0033** | 0.0207 | 0.9306 |

Paired over the forty shared seeds:

| comparison | difference | resolution | registration |
|---|---|---|---|
| **EWC − naive** | **−0.0096 ± 0.0080** | **1.21σ** — does not resolve | **P1 (≥ 3σ) FAILS** |
| **frozen-bias − naive** | −0.0523 ± 0.0089 | **5.90σ**, 31/40 negative | — |
| **frozen-bias − EWC** | **−0.0427 ± 0.0086** | **4.98σ**, 32/40 negative | **P2 (< 2σ) FAILS** |

**The falsifier was *"EWC beats frozen-bias by ≥ 3σ"*; what fired is the reverse, at 4.98σ.** And the level
comparison is the sharpest form of it: **at five replicates diagonal EWC removed 71% of the naive forgetting;
at forty it removes 13%**, against a paper that quotes the first number at **2.47σ**.

## 2. It is not "EWC does nothing" — it is that a two-task mean hides a resolved, opposite-signed pair

| task | naive | EWC | EWC − naive |
|---|---|---|---|
| **0** | +0.0964 ± 0.0144 | **+0.0609** ± 0.0113 | **−0.0354 ± 0.0094 = 3.79σ**, 25/40 negative |
| **1** | +0.0536 ± 0.0092 | **+0.0698** ± 0.0096 | **+0.0161 ± 0.0118 = 1.37σ**, EWC *worse* |

**At forty replicates diagonal EWC reduces the first task's forgetting by a resolved 3.79σ and increases the
second task's by 1.37σ, and the mean over the two moves 1.21σ.** So the headline — the mean — is unresolved
**while both of its terms are moving**, one of them decisively. The mechanism is not a failure to anchor: it is
**redistribution between tasks**, and the paper's `mean_forgetting` column is exactly the statistic that hides it.

**And that is a measurement trap of the same family as the ones already on the list**, distinct from
*"'resolves from zero' is not 'differs from its neighbour'"*: here the average is unresolved because **two
resolved components cancel**, and no re-derivation of the mean can show it. With three tasks the mean is over
**two** numbers, so one improving at 3.8σ and one degrading at 1.4σ is the whole of what the table reports.

**The accuracy moves the same way**: EWC's final accuracy is **0.8856** against naive's **0.9125** at forty
replicates, where at five it was 0.9222 against 0.9139. **Both metrics reverse**, which is what a five-replicate
artefact looks like when the configuration is asked again.

## 3. How favourable were the five seeds the paper quotes?

Honest answer: **favourable, but not impossibly so.** EWC's first five replicates have a mean of **+0.0208**
against **+0.0717** for replicates 6–40, and their **ranks among the forty** are 10, 6, 9, 1, 16 — **not** the
five lowest, so this is not "the five best were taken". Enumerating all C(40,5) = 658,008 five-subsets of EWC's
own values, **11,952 (1.8%) have a mean at least as low as the first five's**. So the paper's five-replicate
figure is a **~1-in-55 draw** from the configuration's own distribution: unlikely, and exactly the kind of draw
that five replicates cannot rule out — which is the whole content of the project's own rule that a design
landing on its criterion cannot answer the question it is asked.

## 4. What this changes

- **§4.2's headline** — *"on the hardened configuration, diagonal EWC finally resolves"* at **2.47σ** — **does not
  survive its own configuration at eight times the replicates.** The row is a five-replicate effect, and the
  paper's table needs the forty-replicate figure beside it.
- **The abstract's** *"EWC helps only when the read-out is narrow enough to make the plastic weights
  load-bearing"* is now doubly qualified: **at forty replicates it does not resolve at that read-out either**,
  its accuracy is *lower* than naive's, and a free 800-parameter constraint beats it by **4.98σ**.
- **And the interesting version of the result is §2.** A reader told only that EWC's `mean_forgetting` is 1.21σ
  from naive's would conclude the penalty does nothing; the per-task table shows it moving two tasks in opposite
  directions, one of them at 3.79σ. **The negative is in the average, not in the method.**

## 5. What this cannot settle

- **One read-out, one task order, one circuit** — and the task order matters more than usual here, because the
  mechanism is a *trade* between task 0 and task 1. A different order, or four tasks, would give a different
  pair, and `mean_forgetting` over two numbers is the statistic §2 shows to be the wrong summary.
- **It does not say EWC is useless**, and it does not re-open the *theory*: LGCL makes EWC a 33%-lossy
  approximation of the exact filter, and that claim is about the linear substrate and untouched here.
- **It does not bound what a *different* λ would do.** The configuration is the paper's own hardened one; a
  λ sweep at forty replicates is the natural follow-up and is not this run.
- **And the block and replay rows are not re-measured here.** `e135` — the whole five-method table, with and
  without the bias frozen — is running and its plastic arm has already been validated per replicate against
  three other-epoch artifacts. Until it lands, this finding is about the **diagonal** row alone, which is the
  one the paper calls its resolved result.
