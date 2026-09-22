# E57 — C2 passes the discipline that overturned C1, and the per-seed evidence is for the wrong family

**Date:** 2026-09-22
**Script:** `experiments/e57_basis_ladder_seed_robustness.py`
**Artifacts:** `runs/e57_basis_seed_robustness.json`, `runs/e3_ladder_v2.json`, `runs/e3_seeds18.json`
**Context:** `2026-09-22-c1-contrast-is-seed-robust.md` (`e47`), `2026-09-22-network-variance-is-learner-variability.md` (`e38`), `2026-09-22-naive-arm-census.md` (`e54`)

---

## 1. The three questions, asked of the core claim for the first time

Six fires took the C1 topology line apart by asking the same three things of every contrast: are the
signs unanimous across seeds, does removing one seed change the answer, and **which axis carries the
noise**. The project's core claim is C2 — *a biological module basis beats a size-matched random
partition* — and none of those questions had been asked of it.

## 2. It passes, and by a wider margin than C1 did

`runs/e3_ladder_v2.json` is the only C2 family that stores `excess_per_seed` — twelve seeds of the
pool ladder at cs = 800. Lower excess is closer to the oracle, so a negative delta favours biology:

| rung | groups | Δ | seed sem | σ (seed only) | signs | LOO min σ | flip? | leverage |
|---|---|---|---|---|---|---|---|---|
| `pool1` | 812 | +0.00019 | 0.00003 | +7.35 | `++++++++-+++` | 6.6 | no | 0.80 |
| `pool2` | 90 | −0.00801 | 0.00034 | −23.3 | `------------` | 21.3 | no | 0.53 |
| `pool4` | 29 | −0.00884 | 0.00020 | **−44.4** | `------------` | 40.7 | no | 0.71 |
| `pool8` | 10 | −0.00685 | 0.00022 | −31.0 | `------------` | 28.4 | no | 0.51 |
| `pool16` | 8 | −0.00765 | 0.00020 | −38.8 | `------------` | 35.4 | no | 0.59 |
| `pool32` | 3 | −0.00699 | 0.00019 | −36.4 | `------------` | 33.3 | no | 0.60 |
| `pool64` | 3 | −0.00548 | 0.00027 | −20.4 | `------------` | 18.6 | no | 0.53 |
| `pool128` | 2 | −0.00409 | 0.00023 | −17.9 | `------------` | 16.3 | no | 0.55 |

**Seven of eight rungs are unanimous across all twelve seeds, no leave-one-seed-out removal flips any
sign, the smallest LOO σ is 6.6, and single-seed leverage is 0.51–0.80** — on a scale whose ceiling is
1, where 1 means one seed is worth a whole sem on its own. The exception is `pool1`, at eleven of
twelve and +7.35σ, which is *itself* the finest end where the plan already says biology does not help.

Compare C1, where the contrasts were unanimous over 3–6 seeds at 4–33σ. **C2 is unanimous over twelve
seeds and its weakest rung is still 16σ on the seed axis alone.** So the discipline that repeatedly
overturned the side line does not touch the core one — which is the check that makes the discipline
worth having, and the strongest positive result in the project.

## 3. But the seed σ is the inflated one, and the binding axis is the **draw**

The seed sem above is 2–3e-05. The *control* arm is **one draw** from a population of size-matched
random partitions, and `e12`–`e17` measured that population's spread:

| measured on | draws | sd across draws | sem over draws |
|---|---|---|---|
| `cell_type` min_size 2 / 3 / 4 / 6 | 5 | 0.000929 / **0.001010** / 0.000613 / 0.000728 | 0.000415 / 0.000452 / 0.000274 / 0.000325 |
| `cell_class` | 5 | 0.000237 | 0.000106 |
| `ito_lee_hemilineage` | 5 | 0.000042 | 0.000019 |
| `supertype` | 5 | 0.000084 | 0.000037 |

The largest is **0.001010**, more than ten times the seed sem of any pool rung. So the −44σ above is
the naive figure, inflated 3–5×, and **the plan's own 3–8σ rung-level numbers are the right ones** —
it had already folded the draw term in. Nothing here changes those; what is new is the per-seed
structure, which the plan had never checked.

So C2's honest statement is unchanged and now *doubly* supported: **the rung-level claim holds at 3–8σ
with one control draw, the seed axis is nearly noiseless, and the draw is what limits it.** And the
draw cannot be averaged away for free — `draw-budget.md` already showed `pool1`/`cell_type` needs
infeasibly many draws for 3σ while every coarse rung needs ≤ 1.

## 4. The per-seed evidence is for a different family than the claim

The headline C2 claim is stated on the **named annotation bases** — `side`, `cell_class`, `cell_type`,
`ito_lee_hemilineage`, `supertype` — while the per-seed values exist for the **pool ladder**. A census:

| artifact | seeds | rungs | per-seed stored | verdict |
|---|---|---|---|---|
| pool ladder, d = 1307 (`e3_ladder_v2`) | 12 | 8 | **8/8** | checkable |
| pool ladder, d = 1307 (`e3_ladder`, v1) | 12 | 8 | 0/8 | rule-8 gap |
| pool ladder, d = 1874 (`e9_ladder_d1874`) | 12 | 8 | 0/8 | **rule-8 gap — the second configuration** |
| **named bases, 18 seeds (`e3_seeds18`)** | **18** | 5 | **0/5** | **rule-8 gap — the family the claim is on** |
| named bases, 5 seeds (`e3_real`, `e3_analytic`) | 5 | 5 | 0/5 | rule-8 gap |

**The artifact with the most seeds in the project — eighteen, on the family the headline is stated on —
cannot be re-analysed paired at all.** This is the same omission `e47` found for the cs = 800 contrast,
and `e54` found for the network `naive` arm, in a third place.

`e58` is launched to close the most important one: the same configuration as `e3_seeds18`
(`--extra-bases --seeds 18`, cs = 800), which took **1.31 h** the first time. The current code stores
`excess_per_seed` on that path — `e3_seeds18` simply predates the change — so the re-run is the whole
fix. The d = 1874 ladder is 5.64 h and is left for now, recorded as an open gap.

## 5. And the three lines have three *different* binding axes

Worth stating once, because each was found by a retraction:

| line | binding axis | how it was found |
|---|---|---|
| **C1** topology, neuron substrate | the **circuit / realization** | `e36`–`e40`: the coordinate that was to explain it failed on the realization axis, the pre-registered band, and above its own bracket |
| **C2** basis, neuron substrate | the **control draw** | `e12`/`e14`/`e17`: seed sem 2e-05 against a draw sd up to 1.0e-03 |
| **C2b** basis, rate network | the **learner's seeds** | `e38`/`e54`: 62% of the per-replicate variance is the learner, not the test set |

**So "the bracket is a bracket", "the control is one draw" and "the floor is 62% learner" are three
different corrections to three different lines, and none of them transfers.** That is the methodological
result of this whole sequence, and it is why each line needed its own check rather than a shared rule.

## 6. Limits

- **The pool ladder is one family at one configuration.** §4 shows the named bases are unchecked, and
  the d = 1874 replication likewise. Until `e58` lands, the per-seed claim in §2 is about the pool
  ladder only.
- **The seed-only σ of −44σ is not quotable** and is reported only to be retired (§3). The plan's 3–8σ
  figures, which fold in the draw, are the numbers to use.
- **`pool1`'s +7.35σ is seed-only too.** Its draw sd is the largest measured, so with the draw folded
  in it is the plan's 0.4σ — i.e. a null, which is what the plan says and what `draw-budget.md`
  established.
- **"Unanimous signs" is necessary, not sufficient**, for a rung-level claim: the draw term can be
  larger than the effect while the seeds agree perfectly, because the draw is shared by all seeds of a
  run. That is precisely what happens at `pool1`.
