# E66 — the named annotation rungs pass the per-seed discipline, and one verdict reverses: `cell_type` is a **20.3σ disadvantage**, not a null

**Date:** 2026-09-23
**Script:** `experiments/e66_named_bases_seed_robustness.py`
**Artifact:** `runs/e58_bases_18seeds_perseed.json` (18 seeds, cs = 800), `runs/e66_named_bases_seed_robustness.json`
**Context:** `2026-09-22-c2-passes-the-per-seed-discipline.md` (e57), `2026-09-23-side-draw-sd-refutes-the-concentration-model.md` (e67), plan rule 8

---

## 1. The gap this closes

`e57` asked the three C1-discipline questions of C2 — unanimous signs, leave-one-out stability,
single-seed leverage — and could only ask them of the **pool ladder**, because that was the only C2
family whose artifact stored `excess_per_seed`. The claim itself is stated on the **named annotation
rungs**, and the artifact with the most seeds for that family (`e3_seeds18.json`, eighteen) was
precisely the one that could not be checked. `e58` re-ran the same configuration with per-seed storage;
this script is its analysis.

**Every basis in a run sees the same task geometries in the same order**, so a biological rung and its
size-matched control are matched observations and the contrast between them is *paired*. Applying that
is not a refinement — for one rung it changes the answer.

## 2. The five named rungs, per seed

| rung | delta | seed sem (paired) | **σ(task)** | signs | LOO min σ | flips | leverage | σ(rule) | binding axis |
|---|---|---|---|---|---|---|---|---|---|
| `side` | −0.00477 | 0.000151 | **31.7** | 18/18 − | 29.9 | no | 0.60 | **18.1** | draw |
| `cell_class` | −0.00319 | 0.000115 | **27.8** | 18/18 − | 26.2 | no | 0.44 | **12.1** | draw |
| `cell_type` | **+0.000261** | **0.0000129** | **20.3** | **18/18 +** | 19.1 | no | 0.61 | **3.8** | draw |
| `ito_lee_hemilineage` | −0.00296 | 0.000105 | **28.1** | 18/18 − | 26.5 | no | 0.47 | **26.1** | seed |
| `supertype` | −0.00145 | 0.000070 | **20.7** | 18/18 − | 19.5 | no | 0.59 | **13.3** | draw |

**Five of five rungs have completely unanimous per-seed signs (18/18), no leave-one-out removal
flips any of them, and the smallest leave-one-out σ is 19.1.** The largest single-seed leverage is
0.61 on a scale whose ceiling is 1. So the discipline that dismantled the side lines finds nothing
wrong with the family the core claim is stated on — and it is the *first* per-seed evidence for that
family, rather than evidence about a different one.

σ(rule) folds in each rung's **measured** control-draw sd (`e17`, `e17b`, `e67`) rather than an
interpolated one, and the binding axis is reported per rung: four of the five are draw-bound,
`ito_lee_hemilineage` is seed-bound, and no rung's rule-σ falls below 3.8σ.

## 3. And `cell_type` is not a null — the verdict was an unpaired-sem artifact

The published five-rung table reports `cell_type` at **0.74σ** and the paper describes it as "the rung
that is nearly the diagonal and shows **nothing at any configuration**". Per seed with pairing it is
**+0.000261 ± 0.0000129 = 20.3σ, 18/18 positive** — a real and precisely measured *disadvantage*, since
a positive delta means the biological partition sits further from the oracle than its size-matched
control.

The reason is visible in the arms themselves:

| rung | corr(bio, rand) | unpaired sem | paired sem | **pairing gain** |
|---|---|---|---|---|
| `cell_type` | **0.9987** | 0.000351 | 0.0000129 | **27.3×** |
| `supertype` | 0.9585 | 0.000340 | 0.0000701 | 4.8× |
| `side` | 0.2102 | 0.000166 | 0.000151 | 1.1× |

```
cell_type  bio   0.01831 0.01456 0.01661 0.01746 0.01972 0.01732 0.01738 0.01687 0.01851 ...
           rand  0.01801 0.01430 0.01641 0.01718 0.01943 0.01711 0.01713 0.01659 0.01839 ...
           delta 0.00030 0.00025 0.00019 0.00028 0.00029 0.00021 0.00025 0.00028 0.00013 ...
```

**A near-diagonal partition's two arms are the same object to four decimal places**, so each arm's own
value swings by ±0.0015 with the task draw while their difference is stable to ±0.00005. The unpaired
sem therefore measures the task geometry, which cancels, rather than the contrast, which does not — and
it is **27× too large** for this rung. The finer the partition, the more completely the pairing cancels,
which is exactly why the *finest* rung is the one whose verdict the unpaired analysis got wrong.

So the corrected statement is the opposite of the published one, and it is a stronger result than a
null: **at the finest annotation granularity the biological partition is reliably worse than its
size-matched control — 20.3σ about these eighteen task draws, 3.8σ about the partition population once
the measured control-draw sd is included.** That is consistent with the ladder result (the fine end
collapses) and with the network line's λ=1.0 rungs, and it removes the one rung the paper used to
argue that the vocabulary's finest level is merely inert.

## 4. The non-partition candidates get their first per-seed check, and it is unanimous

`§4.4`'s headline — that the wiring's own eigenbasis beats the neuron diagonal at equal capacity — had
no per-seed evidence either. These four contrasts are against `diagonal(EWC)`, and they are
**deterministic functions of the circuit**, so no control draw exists and the task draw is the only
axis this artifact samples:

| basis | delta vs the diagonal | σ(task) | signs | LOO min σ | leverage |
|---|---|---|---|---|---|
| `rank4` | +0.00472 | **30.5** | 18/18 + | 28.7 | 0.54 |
| `rank16` | +0.00469 | **30.2** | 18/18 + | 28.5 | 0.54 |
| `rank64` | +0.00458 | **29.9** | 18/18 + | 28.2 | 0.55 |
| **`eigbasis`** | **−0.00491** | **26.0** | **18/18 −** | 24.5 | 0.48 |

**The eigenbasis's advantage is unanimous over eighteen seeds at 26.0σ**, and the three adaptive
spectral truncations are unanimously *worse* than the plain diagonal — the "fixed structures beat
adaptive ones here" claim, now with per-seed backing rather than a pooled mean. Both deltas match the
published figures (0.00492 against the stated 0.01270 vs 0.01762, and 0.0046–0.0047 against the stated
"+0.0222 against the diagonal's +0.01762").

## 5. What this changes, and what it does not

**Changes:**
- The five-rung table's σ are **paired** and larger wherever the two arms are correlated: 31.7 / 27.8 /
  **20.3** / 28.1 / 20.7, against published unpaired values of 28.78 / 12.14 / 0.74 / 9.32 / 4.26. The
  change is not uniform — `side` moves 1.1×, `cell_type` moves **27×** — so the ranking of the rungs
  changes too: `cell_type` is no longer the weakest rung, `side` is the strongest, and the spread
  between the best and worst rung narrows from 39× to 1.6×.
- **`cell_type` is not a null.** The paper's "shows nothing at any configuration" is withdrawn.
- The paper's §4.4 and the "adaptive candidates are worst" claim acquire per-seed evidence.

**Does not change:** the direction of the core claim at the rungs that carry it — `side`,
`cell_class`, hemilineage and `supertype` all still favour biology, unanimously, at 20–32σ paired and
13–26σ about the rule. Nor the ladder's verdict, nor the predictor's 13 of 13.

## 6. Limits

- **One configuration.** cs = 800, support 80, q = 0.02, three tasks, one circuit. The d = 1874 ladder
  is a different family and remains open.
- **`cell_type`'s pairing gain of 27× is a warning about every near-diagonal rung in the project, not
  just this one.** Any rung whose constrained fraction exceeds ~0.97 has two arms correlated near 1, so
  any unpaired σ reported for it is dominated by a term that cancels. The network line's λ = 1.0 rungs
  (`cell_type`, `supertype`) were reported with unpaired sems and are not covered here.
- **σ(task) is a statement about eighteen task draws**, not about the task distribution; σ(rule) is the
  one that speaks about the partition population, and for four of the five rungs it is the smaller of
  the two.
- **`cell_type`'s rule-σ of 3.8σ is the weakest of the four draw-bound rungs** and rests on `e67`'s
  eight-draw measurement of a partition with 812 groups, whose own sd is known to about ±25%.
