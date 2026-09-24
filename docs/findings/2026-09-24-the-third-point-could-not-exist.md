# `e146` cannot answer the question it was registered for, and the artifact says so by being bit-identical

**Date:** 2026-09-24
**Artifact:** `runs/e146_r32_lam3e-4_frozenbias.json` — `--methods naive --frozen-bias --lam 3e-4 --repeats 40`,
against `runs/e125_r32_frozenbias.json` (`--frozen-bias --lam 1.0 --fisher-batches 8`) and
`runs/e133_r32_naive_ewc_40reps.json`'s `naive`.
**Registered:** *"P1: its uncovered share is below the base family's 70%; falsifier: at or above 70%"*
(`docs/findings/2026-09-24-the-diagonals-advantage-tracks-its-uncovered-share.md` §3).

---

## 1. The result, and it is a design error rather than a measurement

**`e146`'s forty replicates are bit-identical to `e125`'s** — forgetting, accuracy and `theta_drift` all exactly
equal across all forty, in two artifacts whose `config` differs in **`lam` (3e-4 against 1.0)** and
**`fisher_batches` (32 against 8)**. So the run is a **third exact instance** of this session's unused-setting
control, after `e116`/`e133` (`fisher_batches`, forty replicates) and `e61`/`e8_hardened_basis` (the replay
settings, five) — **and here the unread setting is the one the fire varied.** `naive` builds no Fisher, so it
cannot read `--lam`.

**And that is the whole answer: the quantity I registered cannot depend on λ.** The "uncovered share" is defined
as *the share of the **naive** arm's forgetting that freezing the offsets removes* — and the naive arm is
λ-independent, so **the registered P1 asked whether a constant depends on λ, and its falsifier was guaranteed to
fire**. The measured value is the same in both arms by construction:

| arm | `naive` | offsets frozen | removed |
|---|---|---|---|
| λ = 3e-3 (`e125`) | +0.0750 | +0.0227 | **69.8%** (paired +0.0523 ± 0.0089 = 5.90σ) |
| λ = 3e-4 (`e146`) | +0.0750 | +0.0227 | **69.8%** — identical to the last digit |

## 2. What the error was, in the form the project records errors

**I conflated two different things that both live in the same table**: the *baseline's* channel decomposition (a
property of the naive arm, which no penalty can move) and the *penalty's* dependence on the uncovered channel
(a property of the penalty arm, which is what the relation in §1 of the registered finding was about). **The
artifact caught it by being identical to its comparator**, which is what that control is for — and it is the
second time this session that a control has caught a mistake in my own reasoning rather than in the code (the
first being `e139`'s whole-body instrument reading the wrong half).

## 3. The arm that *can* answer the intended question, launched

The intended question was: **does the λ floor's advantage come from less displacement into the uncovered
channel?** That is a property of the *penalty* arm, so the control belongs there: **freeze the offsets and vary
λ** — `--frozen-bias --methods ewc --lam {3e-4, 3e-3}`, forty replicates each, writing
`runs/e147_r32_frozenbias_ewc_lam{3e-4,3e-3}.json`.

- **P1.** With the uncovered channel held still, **λ still matters**: the two arms differ by **≥2σ** on
  forgetting. Then λ's effect is *not* only the displacement into the offsets — it acts on the covered channel
  too — and the two-family ordering in the registered finding has a second mechanism to explain.
- **Falsifier.** The two arms are **within 2σ of each other**. Then **λ's entire effect on this configuration
  runs through the uncovered channel** (the weaker penalty helps because it displaces less, and with the channel
  frozen there is nothing left for λ to do) — which would make the λ floor and the anchoring result (`e138`) two
  readings of one mechanism, and would predict that `--frozen-bias` at λ = 3e-4 and at λ = 3e-3 agree with each
  other *and* with `e125`'s frozen arm.
- **And there is a third possible answer worth registering**: both arms land **at or near `e125`'s frozen value
  (+0.0227)**, i.e. **the penalty adds nothing once the channel is held still** — which would say the diagonal
  penalty's entire benefit on this configuration is the management of the unpenalised channel.

## 4. What this cannot settle

- **It does not repair the registered relation.** §1 of the registered finding still has two measured points and
  no third, and the competing readings it names (*the trailing families differ in the size of their forgetting as
  well as in its channel*) remain unseparated. **The third point it asked for does not exist**, and this fire's
  contribution is to say so rather than to report a number that was fixed in advance.
- **And the launched arm answers a *neighbouring* question**: it asks where λ's effect lives, not whether the
  diagonal's cross-family advantage tracks the uncovered share. The relation remains two points.
