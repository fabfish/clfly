# `e135` pre-registered: the §4.2 method table, re-run with the bias frozen in **every** arm

**Date:** 2026-09-24
**Status:** pre-registered **before** the runs. Committed as its own commit; the runs are launched after it.
**Script:** `experiments/e8_rate_network.py`, unchanged.
**Planned artifacts:** `runs/e135_r32_methods_plastic.json` and `runs/e135_r32_methods_frozenbias.json`, each
`--readout-size 32 --iters 500 --test 48 --repeats 5 --methods naive,ewc,ewc-block,ewc-block-rand,replay
--fisher-batches 32 --lam 3e-3 --replay-per-task 96 --replay-batch 8 --shared-head --input-overlap 0.0
--seed0 0 --circuit-size 800`, the second with `--frozen-bias`. **Fifty replicates in total.**
**Context:** `docs/findings/2026-09-24-the-unpenalised-channel-carries-seventy-percent.md`, which measured that
**70%** of this configuration's `naive` forgetting lives in the 800 per-neuron offsets that **no penalty in this
paper covers**, and which forces the question this run asks: if the thing all five methods are measured *against*
is mostly a confound, **does the comparison between them survive its removal?**

## Why the prediction is sharp rather than exploratory

`model.bias` appears in `experiments/e8_rate_network.py` in exactly three places — the optimiser's parameter
list, the drift record and the checkpoint save — and **`clfly/network/fisher.py` does not mention it at all**.
So the bias's contribution to each arm's forgetting is **method-independent by construction**: no Fisher, no
penalty and no replay term reads or updates it. Therefore:

- **freezing it subtracts approximately the same quantity from every arm's forgetting**, so **every paired
  contrast against `naive` should be unchanged**, and
- **every level should fall**.

That is a prediction with a mechanism behind it, and it is falsifiable in one direction only — a contrast that
*moves* is evidence that the bias **interacts** with that method, which cannot happen through the penalty and
therefore would have to come through the training dynamics.

## The predictions

- **C0a, and it is three controls in one arm.** The plastic arm must reproduce, **as values**, three artifacts
  from other epochs at the settings it shares with them: `runs/e8_hardened_basis.json`'s **`naive`** (+0.0729)
  and **`ewc`** (+0.0208) rows, and `runs/e61_replay96_step8.json`'s **`replay`** (−0.0125) — the last because
  `e8_hardened_basis` **predates `--replay-batch`** (rule 27) and its own replay row is the untuned +0.0500.
  This is the fourth, fifth and sixth instances of the same check.
- **C0b.** The frozen arm's `bias_norms` must be **exactly 0.0** at every task and replicate for all five
  methods, while `theta_drift` is non-zero — the flag is per-run, so this also checks that `--frozen-bias`
  composes with the block penalties and with replay rather than only with `naive`.
- **P1, and it is the fire.** **Every paired contrast against `naive` is unchanged within 2σ**: for each of
  `ewc`, `ewc-block`, `ewc-block-rand` and `replay`, the difference between the two arms' `(method − naive)`
  is below 2σ of its own paired sem.
- **P2.** **Every method's level falls** in the frozen arm, and the `naive` level falls by the most in absolute
  terms, because it has the least else to lose.
- **Falsifier.** **Any** contrast moves by **≥ 3σ**. Then the bias does not contribute a method-independent
  quantity, one of the paper's method comparisons is partly a comparison of how each method handles an
  unpenalised channel, and §4.2's table needs a second column rather than a footnote.

## What this cannot settle, in advance

- **Five replicates**, matching the paper's table, so a contrast's paired sem is of the order of the effects
  being compared — this run can detect a *large* interaction and cannot bound a small one. The registered
  claim is therefore "within 2σ at five replicates", which is a wide bound and is stated as one.
- **One configuration**: read-out 32, test 48, three tasks. The bias's share is read-out dependent (`e134`
  measures that) and the ordering here would not transfer to read-out 1307 without its own run.
- **The bias is frozen, not penalised.** A frozen parameter cannot report what it would have done at an
  optimum it was never allowed to find, so an unchanged contrast here says the channel's contribution is
  method-independent, not that penalising the channel would leave the table unchanged.
- **Replay's 96-sample pool is content memory**, so its arm has something the others do not; if any contrast
  moves it is the likeliest, and the registration does not predict which.
