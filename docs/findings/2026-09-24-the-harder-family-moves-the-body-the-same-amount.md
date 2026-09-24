# The harder family moves the body the same amount — and that does not exonerate the channel

**Date:** 2026-09-24
**Script:** none new; the numbers are fields of `runs/e142_r32_overlap1.json` against
`runs/e133_r32_naive_ewc_40reps.json`'s `naive` — the same construction at `--input-overlap 0.0`, the same seeds,
forty replicates each.
**Context:** `e142`'s plastic arm measured that **three identical input populations forget 42% more**
(+0.0750 → +0.1068, **2.9876σ**). `e125` measured that **70%** of the overlap-0 family's forgetting is carried by
the 800 per-neuron offsets, and `e137` that the diagonal penalty **relocates** adaptation into them. **So the
first question the harder family raises is whether it is harder in the same channel** — and this fire answers the
half of it that existing artifacts can answer, and registers the half that needs a run.

---

## 1. Both channels move the same amount

Paired over the forty shared seeds, overlap 1.0 minus overlap 0.0:

| | overlap 0.0 | overlap 1.0 | difference |
|---|---|---|---|
| **bias cumulative path** | 3.5206 | 3.5199 | **−0.0007 ± 0.0464 = 0.01σ** |
| bias distance from zero (final) | 2.0005 | 1.9816 | −0.0189 ± 0.0387 = 0.49σ |
| bias step, task 0 / 1 / 2 | 1.1183 / 1.1767 / 1.2256 | 1.1183 / 1.1747 / 1.2269 | 0.00σ / 0.08σ / 0.03σ |
| θ drift, task 0 / 1 / 2 | 0.0506 / 0.0486 / 0.0498 | 0.0506 / 0.0494 / 0.0465 | 0.00σ / 1.43σ / **−4.45σ** |
| **mean forgetting** | **+0.0750** | **+0.1068** | **+0.0318 = 2.99σ** |

**The body moves the same distance in the same places, and forgets 42% more.** The one resolved trajectory
difference goes the *other* way: at overlap 1.0 the weights drift **4.45σ less** on the last task. So on
norms alone, neither channel's motion explains the extra forgetting — which is a **negative result about the
mechanism** and is reported as one.

**And the retention matrix says where the extra forgetting lands**: final retention is **−0.0349 (2.02σ)** on
task 0, **−0.0266 (1.91σ)** on task 1 and **+0.0057 (1.10σ)** on task 2 — the earlier tasks are **retained worse**
while the newest is learned no worse (its diagonal is 0.9724 against 0.9667). The training loss moves in both
directions at once (**+3.92σ** on task 1 and **−8.51σ** on task 2), which is what tasks sharing their inputs
should do: fit one another's data better in some places and worse in others.

## 2. Why the norm reading does not exonerate the channel, in `e137`'s own words

**`e137` already faced this exact comparison and gave the answer.** It measured that freezing the offsets removes
**70%** of the overlap-0 forgetting (`e125`) while, *within* an arm, the channel's movement correlates with the
forgetting at only **r = +0.340** (n = 40, and −0.101 in the other arm) — and it stated the resolution: **"a
quantity can matter enormously and still be nearly constant between the runs being compared, since the whole
channel varies by 8% of its own magnitude across seeds."**

**A 0.01σ difference in cumulative path norms is exactly the comparison that lesson warns about.** The bias's path
is a *norm over 800 parameters accumulated over three tasks*; two families can have the same norm while the
**distribution** of that movement over offsets, or its **correlation with each task's loss**, differs completely.
A per-parameter anchor is what the penalty actually applies, and a norm is not what it anchors. **So the honest
statement is that the existing artifacts cannot answer the question**, not that they answer it negatively.

## 3. The run that does answer it, registered here rather than after the fact

**`e143`: `--frozen-bias` at `--input-overlap 1.0`, forty replicates, against `runs/e125_r32_frozenbias.json`,
whose frozen-bias arm at overlap 0.0 is `+0.0227 ± 0.0033` over the same forty seeds.**

- **P1, and it is a convergence prediction.** The frozen-bias arm at overlap 1.0 is **within 2σ of +0.0227** —
  i.e. **freezing the offsets removes the family difference as well as the forgetting**. That follows from
  `e125`'s 70% and would make the extra forgetting the *same channel's* doing at a *larger* level, which is what
  §8's item 4 needs to know: the harder benchmark would be harder **in the structured channel's competitor**, not
  in the wiring.
- **Falsifier.** The frozen arm at overlap 1.0 remains **≥ 3σ above +0.0227**. Then **the harder family's extra
  forgetting survives the freeze**, the 800 offsets are not its carrier, and the difference lives in the 26,568
  connectome-masked weights — which is the outcome this project's framing *wants*, because it would make the
  shared-input family the benchmark where the **structured** channel is the one under pressure, exactly what
  §8's item 4 asks a harder benchmark to be.
- **And the pair is complete either way**: `e142`'s C1 arm is the `--frozen-body` diagnostic on the same family
  running now, so the two controls §7 requires — *the body is two parameter sets, diagnose twice* — will both
  exist at overlap 1.0.

**The registration is worth its cost because the two outcomes are opposite readings of the same benchmark**:
P1 says the harder family stresses the channel that `e125` says carries this configuration's forgetting; the
falsifier says it stresses the wiring, which is the version a connectome-constrained continual-learning benchmark
has been looking for.

## 4. What this cannot settle

- **One read-out (32), one overlap value (1.0), one seed set, the shared head.** The suite supports 0.25/0.5/0.75,
  so a *shape* in overlap is a third fire, and nothing here says the 42% would grow with it.
- **Norms only.** The bias's movement is a path length over 800 coordinates; per-coordinate movement is not
  recorded, and it is what a per-parameter anchor acts on. So §1 is a bound on what *these* instruments can see
  rather than a statement about the movement.
- **The comparator is a different task family from the default suite** (`--input-overlap 0.0` draws random
  supports), and **no method has been run on either family in this comparison** — the fire compares `naive` to
  `naive`.
- **And the two families' forgetting differ at 2.99σ**, so even the effect whose mechanism is being asked about is
  at the registration's resolution limit (`docs/findings/2026-09-24-at-the-registration-s-resolution-limit.md`).
