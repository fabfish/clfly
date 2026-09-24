# With the unpenalised channel frozen in every arm, the paper's method ordering inverts — and the biology still shows nothing

**Date:** 2026-09-24
**Artifact:** `runs/e140_r32_methods_frozenbias_40reps.json` — the five-method table at forty replicates with
`--frozen-bias` in **every** arm, the last of the day's queue. Comparator:
`runs/e140_r32_methods_plastic_40reps.json` (the same table with the channel free).
**The registration** is the `e140` row of `docs/research_plan.md`, written before either arm ran: **C0a** the
plastic arm's rows must be per-replicate identical to `e133`'s; **C0b** the frozen arm's `naive` must be identical
to `e125`'s across four unread settings; **P1** the frozen arm's `ewc − naive` is negative at ≥ 3σ; **P2** replay's
margin over `naive` shrinks when the channel is removed, at ≥ 2σ; **P3** the penalties' mutual ordering is
identical in both arms.

---

## 1. Every control passes, and two of them are exact

| control | result |
|---|---|
| **C0a** plastic `naive` and `ewc` against `e133` | **identical, worst \|difference\| 0** |
| `e135`'s first five replicates in the frozen arm | **identical, worst \|difference\| 0** |
| **C0b** frozen `naive` against `e125`'s, over forty replicates | **identical, worst \|difference\| 0** |

**The C0b probe is the one worth naming**: the frozen arm's baseline is bit-identical to `e125`'s, whose
`fisher_batches`, `lam` and replay settings all differ, so **four settings the method cannot read are confirmed
inert on this arm at forty replicates** — a control that had to hold, and did (rule 39's benign twin).

## 2. The table, and the three registered verdicts

| method | **plastic** (channel free) | | | **frozen** (channel removed) | | |
|---|---|---|---|---|---|---|
| | forgetting | accuracy | | forgetting | accuracy | newest |
| `naive` | +0.0750 | 0.9125 | | +0.0227 | 0.9306 | 0.9401 |
| `ewc` (diagonal) | +0.0654 | 0.8856 | | **−0.0021** | 0.9102 | **0.8750** |
| `ewc-block` | +0.0573 | 0.9168 | | +0.0062 | 0.9345 | 0.9297 |
| `ewc-block-rand` | +0.0779 | 0.9054 | | +0.0091 | 0.9344 | 0.9318 |
| `replay` | **−0.0034** | 0.9609 | | +0.0018 | **0.9436** | **0.9406** |

| registered claim | measured | verdict |
|---|---|---|
| **P1**: frozen `ewc − naive` negative at ≥ 3σ | **−0.0247 ± 0.0042 = 5.85σ**, 32/40 negative (the plastic comparator: 1.21σ) | **HOLDS** |
| **P2**: replay's margin shrinks at ≥ 2σ | **−0.0784 → −0.0208, a 73% cut at 6.15σ** (`e135` saw 66% at five replicates, 2.23σ) | **HOLDS** |
| **P3**: the penalties' mutual ordering identical in both arms | plastic `replay < ewc-block < ewc < naive < ewc-block-rand`; frozen **`ewc < replay < ewc-block < ewc-block-rand < naive`** | **FAILS — the ordering inverts** |

## 3. What P3's failure means, and it is the paper's headline

**With the 800 offsets frozen in every arm, the diagonal penalty becomes the best method on the paper's metric and
`replay` becomes second**: `ewc − replay` is **−0.0039 ± 0.0038 = 1.04σ**, i.e. the two are *indistinguishable*
there, from **9.40σ** in the plastic arm where replay wins by 0.0687.

**So the paper's sentence *"replay is the stronger method in every setting"* is a statement about a baseline that
forgets through a channel the penalties cannot see** — which is what `e135` suggested at five replicates (a 66%
cut at 2.23σ) and what this arm settles at forty (73% at 6.15σ). **The sentence that survives is narrower and
still true**: replay reaches zero forgetting *without* any constraint, and it is the only arm here whose
newest-task accuracy is untouched (§5).

## 4. And the paper's central claim gains a third, independent support

`ewc-block − ewc-block-rand` — the one contrast in this paper that isolates the *biology* from its size-matched
random control — is **−0.0206 ± 0.0099 = 2.08σ in the plastic arm** (the biology better, the single-draw value
whose three-draw control later failed its registration) and **−0.0029 ± 0.0029 = 0.98σ in the frozen arm**.
**The manipulation that removes the confound from every arm removes the biology's advantage with it**, and it does
so in a design that has nothing to do with the control-draw question: no partition was redrawn, every arm was
re-run with a frozen bias.

**So the paper's central null now has three independent supports** — the base family's three-draw control
(**1.33σ**, falsifier fired), the shared-input family's three-draw control (**0.99σ**, falsifier fired), and this
one (**0.98σ**) — and the second and third agree with the first through *different* manipulations.

## 5. Two unregistered results worth recording

**First, the floor model predicted a number it had never seen.** The `e148` finding proposed that replay's margin is
simply *the baseline's forgetting*, because replay drives its own forgetting to ≈ 0 (ratios 1.045 and 0.921 on the
two families, and 1.17 in `e135`'s five-replicate frozen arm). **This arm is a configuration that model had never
been evaluated on, and it predicted a margin of −0.0227** (the frozen `naive`'s forgetting): measured **−0.0208,
ratio 0.918**. Four configurations now, and the model needed no parameter.

**Second, the two-axis reversal is complete in this arm.** The method that becomes *best* on the paper's metric is
the *worst* on the other axis: `ewc`'s newest-task accuracy is **−0.0651 ± 0.0073 = 8.95σ** below `naive`'s,
against `ewc-block` at 2.24σ, `ewc-block-rand` at 1.77σ, and **`replay` at 0.15σ**. So the frozen arm's ranking
by forgetting (`ewc` first at 5.85σ) and its ranking by plasticity (replay first by 6.5σ over `ewc`) do not
merely differ — **they are opposite at the top**, and the arm in which the penalty "wins" is the arm in which it
pays the most.

## 6. What this cannot settle

- **`--frozen-bias` changes the model class**, so the ordering under it is not the paper's headline measurement —
  it is a *diagnostic* on the pair (baseline, penalty), and what it shows is that the paper's headline is
  conditional on the baseline's channel. That is a statement about the benchmark, not a proposal to freeze
  anything.
- **Five replicates have been the paper's granularity for this table** and the plastic comparator in this row is
  the two-arm value from `e135`, not a fresh run of the same five-method table at five replicates; the
  forty-replicate plastic arm is the comparator that matters and it is this run's own sibling.
- **One λ**, one read-out (32), one circuit, three tasks, and the ordering claim is about *this* configuration's
  ranking — `e140`'s registration says exactly that, and the arm-to-arm reproducibility caveat of §9 applies to
  every row here (the frozen arm's own arms are first executions).
- And **the two newest-task rankings are point estimates on one task**: the frozen arm's `ewc-block` and
  `ewc-block-rand` are 2.24σ and 1.77σ from their baseline, so their order between themselves is not resolved.
