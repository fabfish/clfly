# `e178` registered and launched: the `side` rung's negative, priced before it is bought

**Date:** 2026-09-25
**Registered before its run:** `runs/e178_rung_side_cs300_144reps.json`, one command, 144 replicates, three arms.
**Probe:** `runs/e177_probe_cs300_side_1rep.json` — one replicate, run to *measure* what the design costs rather
than to estimate it.
**Reads:** `runs/e10_rung_side.json` (the three-replicate triple the paper calls decisive in direction and not in
size).

---

## 1. The arithmetic, done *paired*, from the artifact rather than from the section's prose

§8's first item says the `side` rung "has now been run — where the negative holds and the test is too weak to be
decisive (−0.0116 accuracy against a benchmark whose per-repeat sd is 0.048)". **That figure is an *unpaired* sd
— an arm's own accuracy spread — and the quantity the claim rests on is a *paired* per-replicate difference**, so
the first thing this unit did was compute the right one. `e10_rung_side.json` has **three** replicates, and its
per-replicate `ewc-block` minus `ewc-block-rand` accuracies are:

```
+0.0278   -0.0625   -0.0000      mean -0.0116   sd 0.0462   sem 0.0267
```

**So the section's number survives the correction**: the paired sd is **0.0462** against the quoted 0.048, and the
requirement is **144 replicates** for a 3σ reading where the unpaired figure implies **154**. The claim that the
test is too weak is right; the arithmetic behind it is now the right arithmetic.

**And the triple shows why**: one of its three replicates is *positive* and large (+0.0278), so the published
negative is the mean of a wildly scattered three — at n = 3 the design sits **0.43σ** from zero.

## 2. What decisiveness costs, measured at both circuits

A one-replicate **probe** at the second circuit (`e177`) times the command at **162 s**, against **703 s** per
replicate at the first (from `e10`'s own 6327 s over nine arm-replicates):

| circuit | per replicate | 144 replicates | note |
|---|---|---|---|
| **800** (d = 1307), the published one | 703 s | **≈ 28 h** | the coarse `side` partition's block penalty dominates |
| **300**, the probe | **162 s** | **≈ 6.5 h** | 4.3× cheaper, and the item's own title asks for "elsewhere" |

**So the item is not a queue entry at the circuit it was measured on and is one at the circuit it asks to be
replicated at** — which is the honest form of "too weak to be decisive": not an inability, a price.

## 3. The registration

**`e178`** — the same three arms at the **same basis** at **cs = 300**, `--iters 500`, `--fisher-batches 32`,
**144** replicates, which is the measured requirement and not a round number.

- **P1**: the block-minus-rand gap at cs = 300 is **negative and resolved at ≥ 2σ**. With the first circuit's
  per-replicate sd (0.0462) and 144 replicates the sem is **0.0038**, so an effect as large as +0.0116 would read
  at **3.0σ**.
- **P2 (the item's own account)**: the gap is **larger** at cs = 300 than at cs = 800. The estimation-quality
  account says the block Fisher's disadvantage comes from its estimation problem, which is *harder* — more block
  entries to fill — at the larger circuit, and `e99` already found the gap **falling 58%** from cs = 800 to 300.
  **So this design is a replication of a sign and a test of a *different* prediction from the same account**, and
  the two could disagree without either being an error of measurement.
- **Falsifier**: the gap resolves **positive** at ≥ 2σ — the coarse rung's negative is a property of the circuit it
  was measured on.
- **Null worth keeping**: unresolved even at 144 replicates, which would say the effect is smaller than the first
  circuit's triple — and *that* would be evidence for the account, since both circuits' gaps would then shrink as
  the estimation problem does.

## 4. What launching it costs, and what it does not settle

- **It is the longest job this project has run** (≈ 6.5 h at the measured rate), and it holds the CPU for several
  fires. The alternative — writing §8's item as a *bound* — costs nothing and settles nothing, so the trade is
  between a bound and a measurement and the measurement is available.
- **It does not make the published circuit's negative decisive.** cs = 800 would still sit at 0.43σ, and a
  resolved cs = 300 result would be a statement about the smaller circuit.
- **It is one rung.** The item asks for the ladder to be walked, and this is the rung the neuron result most
  implicates; the other four, and the synapse-side plateau, remain the item's work.
- **And the probe is one replicate**: 162 s could be a warm-cache or load artifact, though it was measured on a
  quiet machine (no other job was running) and the *block partition's size* is what dominates, which is a property
  of the circuit and not of the timing.
- **It gave the corpus something on the way**: the probe is the **first `-rand` artifact outside `cell_class` at
  cs = 800 whose draw is recorded** — `partition_draw.fingerprint_sha1 = fc064656e855`, the `side` partition at
  cs = 300. Two of `e168`'s tests had pinned the corpus's fingerprint *set* to the three cell_class@800 seeds and
  went red, which is the suite doing its job: the meaningful claim is **per artifact** (that each artifact's
  reconstruction reproduces its own recorded value, which `e168`'s `identified_draws` checks and which passes with
  **zero** mismatches), not that the corpus records only three draws.
