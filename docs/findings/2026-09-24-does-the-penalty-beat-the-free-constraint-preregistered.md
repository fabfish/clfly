# `e133` pre-registered: does a tuned 26,568-parameter penalty beat a free 800-parameter constraint?

**Date:** 2026-09-24
**Status:** pre-registered **before** the run. Committed as its own commit; the run is launched after it.
**Script:** `experiments/e8_rate_network.py`, unchanged.
**Planned artifact:** `runs/e133_r32_naive_ewc_40reps.json` — `--readout-size 32 --iters 500 --test 48
--repeats 40 --methods naive,ewc --shared-head --input-overlap 0.0 --seed0 0 --circuit-size 800
--fisher-batches 32 --lam 3e-3`, i.e. **the paper's hardened EWC configuration at forty replicates**.
**Existing comparators:** `runs/e125_r32_frozenbias.json` (40 replicates, `--frozen-bias`, no penalty, same
configuration otherwise) and `runs/e116_r32_40reps.json` (40 replicates, `naive`).
**Context:** `docs/findings/2026-09-24-the-unpenalised-channel-preregistered.md` and the run that fired its
falsifier — freezing the 800 recurrent-bias parameters removes **70%** of the naive forgetting at read-out 32
(**+0.0750 → +0.0227, +0.0523 ± 0.0089 = 5.90σ over 40 paired seeds**) *and* raises accuracy (0.9125 → 0.9306).

## What is already known, and why it needs this run

At **the same five seeds**, paired:

| arm | mean forgetting | difference from naive | resolution |
|---|---|---|---|
| naive | +0.0729 | — | — |
| **EWC**, diagonal, λ = 0.003, 32 Fisher batches | +0.0208 | −0.0521 ± 0.0272 | **1.92σ** |
| **frozen-bias**, no penalty at all | +0.0250 | −0.0479 ± 0.0202 | **2.37σ** |

and **frozen-bias minus EWC = +0.0042 ± 0.0205 = 0.20σ** — indistinguishable. So the project's tuned diagonal
penalty and a **free structural constraint** have the same effect at five seeds, and the constraint's effect is
the *better resolved of the two* because its paired difference has the smaller sem.

**That comparison is not yet a result**, for one reason: the EWC arm has **five** replicates and the frozen-bias
arm has **forty**, so "indistinguishable at five" is a statement about a five-replicate pen. **The paper's EWC
headline is quoted from those five.** This run puts both arms on forty.

## The predictions

- **C0a, and it is the control that licenses the cross-artifact comparison.** The `naive` arm in this run must
  reproduce, **as values**, `runs/e116_r32_40reps.json`'s forty replicates — the same statement three earlier
  comparisons have now delivered (at read-out 32, 128 and 300), and specifically: the first five must equal
  **+0.0417, +0.0521, +0.1042, +0.1146, +0.0521**, which is also what `runs/e104_frozen_r32_plastic.json`
  carries under a *different keyset*. **Note that `fisher_batches` cannot affect the `naive` arm** — the hardened
  artifact uses 32 and `e116` uses 8, and the two naive arms are identical in value — so running `naive` at
  `--fisher-batches 32` is a genuine control on the Fisher's independence from the plastic arm.
- **P1.** EWC at forty replicates resolves against its own run's naive arm: the paired difference is at least
  **3σ**. *(At five replicates it is 1.92σ, and a forty-replicate pen should roughly double the resolution; if it
  does not, the effect is smaller than the five-replicate figure suggested and that is itself a finding.)*
- **P2, and it is the fire's question.** **Freezing the bias and tuning the diagonal penalty are
  indistinguishable at forty replicates**: the paired `frozen-bias − EWC` difference is **below 2σ**.
- **Falsifier.** EWC beats frozen-bias by **≥ 3σ**. Then the penalty is doing something the free constraint
  cannot — a real, nameable advantage for the project's central method — and the reading that "70% of the
  forgetting lives where no penalty looks, and removing the channel removes it" is joined by "and the penalty
  handles what remains better than removing the channel does".

## Why this is the right comparison and not a rhetorical one

The two arms differ in **one** respect: EWC adds `0.5·λ·Σ fisher·(θ−anchor)²` over 26,568 weights; frozen-bias
removes 800 offsets from the optimiser. They are not variants of one method, and that is the point: **the project
has spent five fires sweeping λ and the basis for its own penalty, and has never asked what a zero-cost
constraint of the body does.** If they tie, the paper's §4.2 table has a row missing — not because the penalty is
wrong, but because **the baseline it is measured against forgets mostly through a channel it does not touch**,
and the honest comparison against naive is a comparison against a naive run that is *unnecessarily* forgetful.

## What this cannot settle, in advance

- **One read-out.** Read-out 32 is where the body is most load-bearing — the gap is +0.1000 there against
  −0.0111 at the whole state — so it is both the configuration where the bias has the most to do and the
  configuration the paper's EWC table uses. **The generality question is a second axis** and is not this run: at
  read-out 1307 the plastic weights are not needed at all, so a bias effect there would need its own explanation.
- **`frozen-bias` is a diagnostic, not a method.** It holds 800 parameters at their initialisation; it is not a
  regulariser, it has no hyperparameter, and it is comparable to EWC only because both are interventions on the
  same training loop. **A tie does not make it the better method** — it makes it the cheaper measurement of what
  the penalty is actually worth.
- **The two arms are in different artifact epochs** (this run carries `retention_loss`, `bias_norms` and the
  per-task checkpoint; the frozen-bias artifact carries them too but the hardened one does not), so the
  comparison leans on C0a rather than on configuration identity — which is what C0a is for.
- **And a tie at 40 replicates is a bound, not a zero**: the two could differ by up to twice the 40-replicate
  sem of their paired difference, which is what the run measures and not what this registration asserts.
