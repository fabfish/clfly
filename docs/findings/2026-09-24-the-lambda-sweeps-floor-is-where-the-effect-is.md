# The λ sweep's floor is where the effect is

**Date:** 2026-09-24
**Script:** `experiments/e8_rate_network.py`, unchanged.
**Artifact:** `runs/e141_r32_ewc_lam3e-4.json` — `--lam 3e-4 --methods ewc --fisher-batches 32 --repeats 40`, the
paper's hardened configuration at read-out 32.
**Comparators, all forty paired seeds:** `runs/e133_r32_naive_ewc_40reps.json`'s `naive` (+0.0750 ± 0.0088) and
its `ewc` at **λ = 3e-3** (+0.0654 ± 0.0079); `runs/e138_r32_ewc_anchorbias33.json` (λ = 3e-3 **with the offsets
anchored**, +0.0292).
**Pre-registration:** `docs/findings/2026-09-24-the-lambda-sweep-at-forty-registered.md` — **the top of the sweep
(λ = 3e-2 and 3e-1) is still running; this reports the arm below the floor of every sweep this project has run.**

---

## 1. The measurement: a weaker penalty is better on every metric

| | `naive` | **λ = 3e-4** | λ = 3e-3 | λ = 3e-3, offsets anchored |
|---|---|---|---|---|
| mean forgetting | +0.0750 ± 0.0088 | **+0.0396** | +0.0654 | **+0.0292** |
| final accuracy | 0.9125 | **0.9174** | 0.8856 | 0.9073 |
| bias cumulative path | 3.5206 | 3.6835 | 4.2819 | 3.4452 |
| θ drift, tasks 0 / 1 / 2 | — | 0.0506 / **0.0436** / **0.0428** | 0.0506 / 0.0380 / 0.0357 | 0.0506 / 0.0403 / 0.0400 |

Paired over the same forty seeds:

- **λ = 3e-4 against `naive`: −0.0354 ± 0.0083 = 4.27σ**, with **27 of 40** replicates negative on each task;
- **both forgettable tasks improve** — task 0 by **−0.0422 ± 0.0119 = 3.54σ**, task 1 by
  **−0.0286 ± 0.0100 = 2.87σ** — where λ = 3e-3 at forty has its task 1 *worse* than `naive` (`e133`), so the
  penalty's characteristic per-task **trade is absent at the weaker setting**;
- **accuracy is not worse than `naive`'s** (+0.0049 ± 0.0053 = 0.91σ), where λ = 3e-3 costs **2.69σ** of it;
- and it is **3.74σ better than λ = 3e-3 on forgetting with 6.00σ better accuracy**.

**So on this configuration the diagonal penalty's useful direction is *down* from 3e-3, and the arm that gets
there beats `naive` at 4.27σ on forgetting *and* 0.91σ on accuracy — a win on both metrics, which no penalty arm
in this project has produced before.**

## 2. Why this is a refutation rather than a new hyper-parameter

**The 2026-09-22 sweep swept λ ∈ {0.003, 0.01, 0.03, 0.1, 0.3} and concluded *"λ matters enormously, and 0.003 is
the only useful setting"*** — and **3e-4 is below every point that sweep tried**. Its floor was the optimum it
found, so *"the only useful setting"* was a statement about the grid rather than about the configuration, and this
is the same defect the project has recorded before in another form (*a range that excludes the rung that matters*).

**And the claim it supports needs its forty-replicate correction too.** The paper's §4.7 says *"at λ = 0.003 all
three Fisher variants do beat `naive`"*, which is true on the five-replicate table and **is not true at forty**:
λ = 3e-3 is **1.21σ** from `naive` there (18/40 negative) while λ = 3e-4 is **4.27σ** (27/40). **So the sentence
was right about the setting and wrong about the resolution**, in the same way §4.2's diagonal row was.

## 2b. And the sweep is complete: a **bracketed** interior optimum, with the forgetting tracking how much movement the penalty displaces into the offsets

`λ = 3e-2` and `λ = 3e-1` landed (`runs/e141_r32_ewc_lam3e-2.json`, `runs/e141_r32_ewc_lam3e-1.json`), so the λ
axis has **five** points including the unpenalised one, and the registered sweep is finished:

| λ | mean forgetting | accuracy | bias cumulative path | θ drift, tasks 0–1 |
|---|---|---|---|---|
| **0** (`naive`) | +0.0750 ± 0.0088 | 0.9125 | 3.5206 | 0.0496 |
| **3e-4** | **+0.0396** | **0.9174** | 3.6835 | 0.0471 |
| **3e-3** | +0.0654 | 0.8856 | 4.2819 | 0.0443 |
| **3e-2** | +0.0810 | 0.8592 | 5.4367 | 0.0406 |
| **3e-1** | **+0.0846** | **0.8469** | **6.2313** | **0.0349** |

**The optimum is now bracketed rather than merely at the edge.** λ = 0 is worse than 3e-4 by **4.27σ** and
λ = 3e-3 is worse than 3e-4 by **3.74σ**, so the forgetting falls from 0 to 3e-4 and rises from 3e-4 onwards:
**λ\\* ∈ (0, 3e-3), and 3e-4 is the best point measured.** What the five points do not do is *locate* it — the
bracket is two decades wide — so the licensed sentence is the one rule 38 asks for: *the best point measured is
3e-4, inside a bracket whose lower end is the unpenalised arm.*

**And the top of the sweep is dominated on both metrics**: at λ = 3e-1 the forgetting is **no better than
`naive`** (+0.0096 ± 0.0113 = 0.85σ, nominally worse) and the accuracy is **8.86σ below** it, so the two ends of
the sweep are worse than the baseline for opposite reasons — the unpenalised end by not helping, this end by
over-constraining.

**Along this axis the forgetting tracks the movement the penalty displaces into the offsets, and with four
penalty arms the co-movement is now a four-point relation rather than a three-point lead.** The bias's cumulative
path rises monotonically with λ — **3.6835 → 4.2819 → 5.4367 → 6.2313** — and the forgetting does too
(**+0.0396 → +0.0654 → +0.0810 → +0.0846**), while **θ's drift falls monotonically the other way**
(0.0471 → 0.0443 → 0.0406 → 0.0349) and the top contrasts are enormous: the bias path at λ = 3e-1 is
**+1.9494 ± 0.1173 = 16.63σ** above 3e-3's with **0 of 40** replicates against it, and θ's drift is
**−0.0095 ± 0.0004 = 22.35σ** below with **40 of 40**. **So the two registered predictions that concern the
mechanism hold in the strongest form the statistics allow**: raising λ moves adaptation out of `theta` and into
the 800 offsets, and **the more it moves, the worse the forgetting** — with the *unpenalised* arm the one point
that does not fit (its bias path is the lowest of all five and it is the second-worst).

**And the third prediction fails.** P2 read *"the forgetting does not fall as λ rises — registered as the ordered
contrast λ = 3e-2 worse than λ = 3e-3 (larger forgetting) resolving at ≥ 2σ"*, and the measurement is
**+0.0156 ± 0.0098 = 1.60σ**: the **direction** is exactly as registered and the magnitude is **0.4σ below the
bar**. **The falsifier does not fire either** — the top arm is 1.74σ *worse* than 3e-3, not ≥3σ better — so the
registration's three outcomes are: **P1 holds at 16.63σ, P2b holds at 22.35σ, P2 fails at 1.60σ, and the
falsifier is silent.** That is the second time today a registered threshold has landed inside its own
uncertainty (`e142`'s 3.00σ bar missed by 0.012σ), and the two together are why rule 37 exists.

**And along this axis the forgetting tracks the movement the penalty displaces into the offsets, and with four
penalty arms the co-movement is a four-point relation rather than the three-point lead that died in §3.** The
bias's cumulative path rises monotonically with λ — **3.6835 → 4.2819 → 5.4367 → 6.2313** — and the forgetting
does too (**+0.0396 → +0.0654 → +0.0810 → +0.0846**), while **θ's drift falls monotonically the other way**
(0.0471 → 0.0443 → 0.0406 → 0.0349), and the top contrasts are enormous: the bias path at λ = 3e-1 is
**+1.9494 ± 0.1173 = 16.63σ** above 3e-3's with **0 of 40** replicates against it, and θ's drift is
**−0.0095 ± 0.0004 = 22.35σ** below with **40 of 40**. **So the registered P1 and P2b hold in the strongest form
the statistics allow**: raising λ moves adaptation out of `theta` and into the 800 offsets, and **the more it
moves, the worse the forgetting** — a dose–response for `e137`'s substitution, with the *unpenalised* arm as the
one point that does not fit (its bias path is the lowest of all five and it is the second-worst).

## 3. And the relocation is present even at the weak end

**The bias's cumulative path is 3.6835 against `naive`'s 3.5206 — +0.1629 ± 0.0387 = 4.21σ** — so a penalty five
times weaker than the one `e137` examined **still pushes adaptation into the 800 offsets**, and the path rises
monotonically across the three penalty arms (3.4452 anchored, 3.6835 at 3e-4, 4.2819 at 3e-3).

**Which produces a lead worth writing down and not banking — and the lead died within the hour, which is why it
is reported with its own correction.** Ordered by the bias's cumulative path the three penalty arms read
**3.4452 → 0.0292**, **3.6835 → 0.0396**, **4.2819 → 0.0654**: the quantity that `e125` credits with **70%** of
the *level* of this configuration's forgetting and that `e137` found uninformative *across seeds* (r = +0.340)
**ordered them perfectly** — a different axis from the one `e137` tested, *interventions* rather than *seeds*.

**(*And a fourth arm breaks it.*)** `e138` gives two more penalty arms at the same seeds, and with them in the
table the ordering is not monotone:

| penalty arm | forgetting | bias cumulative path | accuracy |
|---|---|---|---|
| λ = 3e-3, offsets anchored at **33.2** | **+0.0292** | **3.4452** | 0.9073 |
| λ = 3e-3, offsets anchored at **1.0** | +0.0352 | **4.2190** | 0.9000 |
| **λ = 3e-4**, unanchored | +0.0396 | **3.6835** | **0.9174** |
| λ = 3e-3, unanchored | +0.0654 | **4.2819** | 0.8856 |

Sorted by forgetting, the paths run **3.4452, 4.2190, 3.6835, 4.2819** — **up, down, up**. **So the bias path
orders the arms along each *knob* separately and not across the two of them**: within the anchoring axis
(4.2819 → 0.0654 against 3.4452 → 0.0292) and within the λ axis (4.2819 → 0.0654 against 3.6835 → 0.0396) the
relation is monotone, and the two families are **offset** from one another. **Which is the honest reading of a
three-point ordering: it was an ordering along one axis, and introducing a second axis is what tests whether a
quantity is a *carrier* or a *co-mover of one knob*.** No other recorded quantity orders the four either —
accuracy (0.9073, 0.9000, 0.9174, 0.8856), mean θ drift (0.0455, 0.0448, 0.0471, 0.0443) and the bias's final
distance from zero (1.9437, 2.4691, 2.0743, 2.5027) are all non-monotone in the same order — **so the four
penalty arms are not a one-parameter family and nothing in the artifacts ranks them.** The λ = 3e-2 and 3e-1
arms, when they land, will add two more points **on the λ axis** — which is the axis along which the ordering
above does hold — so they test the co-movement within one knob and say nothing about the cross-knob question.

**(*And with the complete λ axis that reading was itself too strong — both the lead and its obituary were
three-point statements.*)** λ = 3e-2 and 3e-1 have now landed, so the cross-knob table has **six** penalty arms,
and sorted by the bias's cumulative path they read:

| arm | bias cumulative path | forgetting |
|---|---|---|
| λ = 3e-3, offsets anchored **33.2** | 3.4452 | **+0.0292** |
| **λ = 3e-4**, unanchored | 3.6835 | +0.0396 |
| λ = 3e-3, offsets anchored **1.0** | 4.2190 | +0.0352 |
| λ = 3e-3, unanchored | 4.2819 | +0.0654 |
| λ = 3e-2 | 5.4367 | +0.0810 |
| λ = 3e-1 | 6.2313 | +0.0846 |

**Spearman +0.943 with exactly ONE inversion, and that inversion is 0.69σ** — the anchored-1.0 arm's 0.0352
against λ = 3e-4's 0.0396, a paired difference of **−0.0044 ± 0.0064**. So the honest statement is the opposite
of the obituary above: **within each knob the path orders the forgetting perfectly (+1.000 over the four λ arms
and +1.000 over the three anchoring arms), and across the six penalty arms it orders them at +0.943 with its
single inversion unresolved** — i.e. **consistent with monotone across both knobs at the resolution forty seeds
give**. **The unpenalised arm remains the exception and it is a different kind of point**: including it drops the
correlation to **+0.750**, because λ = 0 is not a weaker penalty but the absence of one, and a quantity that
orders a family of *interventions* need not order the baseline they are interventions on.

**And the practical reading is that three routes land in the same place.** The strong anchor (+0.0292), the weak
anchor (+0.0352) and λ = 3e-4 (+0.0396) are pairwise **0.69σ, 0.88σ and 1.21σ** apart — so **this data cannot
separate "weaken the penalty" from "cover the channel", weakly or strongly**, and the honest recommendation is
the cheapest route rather than the best one.

## 4. What this cannot settle

- **It is four λ on one axis, and the sweep is complete.** The registration's **P1 and P2b HOLD in the strongest
  form the statistics allow** (the bias path rises at **16.63σ** and θ's drift falls at **22.35σ** on the top
  contrast, with 0 of 40 and 40 of 40 replicates), **P2 FAILS at 1.60σ** against its registered 2σ, and **the
  falsifier does not fire** — the top arm is 1.74σ *worse* than 3e-3 rather than ≥3σ better.
- **And the optimum is bracketed but not located.** The bracket is **two decades wide** — λ\\* ∈ (0, 3e-3) with
  3e-4 the best point measured — so the licensed sentence is *"the best point measured"* and the locating sweep
  would be λ ∈ (1e-5, 3e-4), not another decade upwards.
- **One read-out (32), one circuit, three tasks, one Fisher batch count (32).** `e101`'s sweep found the batch
  count moves the penalty's effective strength, so **λ and the batch count are confounded here as everywhere**:
  3e-4 with 32 batches is a *weaker* penalty, and whether the optimum is in λ or in the product is not separated
  by this sweep — **the interior optimum is an optimum in this one knob.**
- **And 4.27σ is not small but it is not the 4.84σ the anchored arm reaches** — the two are **1.21σ apart**, i.e.
  indistinguishable at this n, so *"weaken the penalty"* and *"cover the channel"* are two routes to a level this
  artifact cannot separate, and a third arm (weaker **and** anchored) is what would. **The interior optimum makes
  that cheaper to ask now**: if the minimum is at 3e-4 unanchored, the anchored arm at 3e-4 is the natural next
  point, and the cross-knob table in §3 is already the reason to expect no single quantity to rank it.
