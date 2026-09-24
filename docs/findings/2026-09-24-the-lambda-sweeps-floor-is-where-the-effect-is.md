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

## 4. What this cannot settle

- **It is one λ below the swept range, not a curve.** The registration's P1 (the bias's movement falls
  monotonically in λ), P2 (the forgetting does not fall as λ rises) and P2b (θ drift falls while the forgetting
  does not) are **all still pending** on the λ = 3e-2 and 3e-1 arms, as is the falsifier — *the forgetting falls
  monotonically in λ and the top arm beats 3e-3 by ≥3σ* — which the arm above the floor does not touch.
- **And what this arm does to the falsifier is worth stating in advance**: λ = 3e-4 is **better** than 3e-3 by
  3.74σ, so the forgetting is **not monotone** in λ over the two arms measured, and the falsifier as registered
  (which needs the *top* arm to be the best) cannot be reached from below — it can only fire on the 3e-2/3e-1
  arms' being better still, which would be a different sentence from the one registered.
- **One read-out (32), one circuit, three tasks, one Fisher batch count (32).** `e101`'s sweep found the batch
  count moves the penalty's effective strength, so **λ and the batch count are confounded here as everywhere**:
  3e-4 with 32 batches is a *weaker* penalty, and whether the optimum is in λ or in the product is not separated
  by this arm.
- **And 4.27σ is not small but it is not the 4.84σ the anchored arm reaches** — the two are **1.21σ apart**, i.e.
  indistinguishable at this n, so *"weaken the penalty"* and *"cover the channel"* are two routes to a level this
  artifact cannot separate, and a third arm (weaker **and** anchored) is what would.
