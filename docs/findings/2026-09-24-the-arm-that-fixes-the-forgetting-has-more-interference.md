# `e138`: the penalty works once it covers the channel — and the arm that works has **more** interference

**Date:** 2026-09-24
**Script:** `experiments/e8_rate_network.py` with the new **`--anchor-bias SCALE`**; the analysis is
`experiments/e138_anchored_bias.py`.
**Artifacts:** `runs/e138_r32_ewc_anchorbias1.json` and `runs/e138_r32_ewc_anchorbias33.json`, forty replicates
each, everything else the paper's hardened configuration.
**Comparators, at the same forty seeds:** `runs/e133_r32_naive_ewc_40reps.json`'s `naive` (+0.0750 ± 0.0088) and
its unanchored `ewc` (+0.0654 ± 0.0079); `runs/e125_r32_frozenbias.json`'s free freeze (+0.0227 ± 0.0033).
**Pre-registration:** `docs/findings/2026-09-24-putting-the-bias-inside-the-penalty-preregistered.md`.
**Every prediction holds, the falsifier does not fire, and the interesting part is what the account's own
quantity does.**

---

## 1. The registration, resolved

| arm | forgetting | per-repeat sd | accuracy |
|---|---|---|---|
| `naive` | **+0.0750 ± 0.0088** | 0.0556 | 0.9125 |
| diagonal EWC, unanchored | +0.0654 ± 0.0079 | 0.0502 | 0.8856 |
| + `--anchor-bias 1.0` (2.9% of the penalty's mass) | **+0.0352** | 0.0286 | 0.9000 |
| **+ `--anchor-bias 33.2` (equal total mass)** | **+0.0292** | 0.0365 | **0.9073** |
| frozen bias, no penalty at all (`e125`) | +0.0227 ± 0.0033 | 0.0207 | 0.9306 |

| registration | verdict |
|---|---|
| **C0a** — task 0's bias step identical in every arm | **HOLDS exactly**: 1.1183309719 in all three, spread 0 |
| **C0b** — the bias's cumulative movement falls in the scale | **HOLDS**: 4.2819 → 4.2190 → **3.4452**, the top contrast at **−0.8367 ± 0.0654 = 12.78σ** |
| **P1** — the forgetting falls in the scale | **HOLDS**: +0.0654 → +0.0352 → **+0.0292**, monotone in all three |
| **falsifier** — `SCALE 33.2` within 2σ of unanchored | **does not fire** (4.03σ) |

Paired over the forty shared seeds, the strong arm is **−0.0458 ± 0.0095 = 4.84σ** from `naive` and
**−0.0362 ± 0.0090 = 4.03σ** from the unanchored penalty — **the first penalty in this project to beat `naive` by
more than 3σ at forty replicates**, where the same λ on the same seeds was 1.21σ. It recovers **84.8%** of the
gap between the unanchored penalty and the free freeze (0.0654 → 0.0292 against a floor of 0.0227) and its
accuracy is **0.9073**, close to `naive`'s 0.9125 while forgetting **40% less**. **The two scales are not
resolved from each other** (−0.0060 ± 0.0068 = 0.88σ), so the monotonicity is an ordering rather than a
separation, and that is what the registration asked for.

## 2. And the interference term **rises** in the arms where the forgetting falls

The same artifacts record the account the theory is built on, so all four arms can be compared on identical
seeds. Task 0, cumulative, θ only:

| | `naive` | unanchored | `SCALE 1.0` | `SCALE 33.2` |
|---|---|---|---|---|
| **first-order interference** | 0.2336 | **0.0052** | 0.0167 | **0.0238** |
| **cut against `naive`** | — | **44.6×** | 14.0× | **9.8×** |
| cosine | 0.0476 | 0.0019 | 0.0069 | 0.0106 |
| displacement ‖θ_final − θ_0‖ | 18.817 | 14.142 | 14.433 | 15.380 |
| gradient norm | 0.2736 | 0.2238 | 0.1745 | 0.1370 |
| **mean forgetting** | **+0.0750** | **+0.0654** | **+0.0352** | **+0.0292** |

**The term's ordering across the three penalty arms is the exact reverse of the forgetting's.** The arm that cuts
it **44.6-fold** buys **1.21σ**; the arm that cuts it **9.8-fold** buys **4.84σ**. And the anti-monotonicity is
**resolved**, not nominated: `SCALE 33.2`'s term is **+0.0186 ± 0.0069 = 2.69σ** above the unanchored arm's and
its cosine is **+0.0122 ± 0.0027 = 4.46σ** above it — **on the same seeds, in the arm with the significantly
lower forgetting.** The comparison needs no normalisation between arms to make that point, because both penalties
are measured against the same `naive` row.

**So the quantity the interference account rests on is higher, by a resolved margin, in the arm where the
penalty works.** That is the third instance in the same session and the first one in the opposite direction:

- `e108` — the term could not **order** the forgetting across configurations;
- `e139` — under a penalty that cuts the term 45-fold the forgetting moves **1.21σ**, so the term is not
  sufficient;
- **`e138` — here the effect is present and the term is *larger*, so the term is not necessary either.**

A quantity that does not fall where the thing works, and does not rise where the thing fails, is **not the
carrier**; three instances now, one of them an intervention pointing the other way.

## 3. The mechanism: a reallocation across the body's two channels

- **The bias moves less and θ moves *more*, by resolved margins.** As the scale rises the bias's cumulative path
  falls 4.2819 → 4.2190 → 3.4452 (**12.78σ** at the top contrast) while **θ's drift per task rises** on the
  later tasks: unanchored `[0.0506, 0.0380, 0.0357]` against `SCALE 33.2`'s `[0.0506, 0.0403, 0.0400]`, i.e.
  **+0.0023 (5.42σ)** and **+0.0043 (5.34σ)**. **Constrain one channel and the other takes up the slack** —
  which is `e137`'s substitution with the sign of the intervention reversed, and it is resolved here at 5σ where
  `SCALE 1.0` showed it at 2.25σ.
- **And it is a change in distribution, not in size.** The displacement *rises* with the scale (14.142 → 15.380)
  while the gradient norm falls (0.2238 → 0.1370). The body does not stop moving; **how much of its motion
  damages old tasks changes.**
- **The registered manipulation check passes by ordering but only resolves at the strong scale** — 1.19σ at
  `SCALE 1.0`, 12.78σ at `33.2` — so an arm that moved the forgetting 4.20σ while moving the quantity it names
  1.19σ was a *weak* manipulation rather than a broken one, and the pair of scales is what separates the two
  readings.
- **It is not a learning change, and the last-task cost shrinks with the scale.** The retention matrix's diagonal
  is **identical on task 0** in all four arms (0.9682), 0.18σ / 0.37σ on task 1 and 2.11σ / 1.02σ on task 2 —
  and the training loss is identical within 1σ. Final retention improves on the old tasks at every scale
  (`SCALE 33.2`: **+0.0354 (3.58σ)** and **+0.0391 (3.35σ)**) while the **last-task cost falls** from
  **−0.0161 (2.11σ)** at `SCALE 1.0` to **−0.0094 (1.02σ, unresolvable)** at `33.2`. **So the trade the first
  scale paid is substantially bought back by pressing harder** — which is the eighth measurement trap's shape
  arriving on the benefit side, since `mean_forgetting` is over the first T−1 tasks and cannot show it either way.
- **And the θ-only form sees 13% of the instrument.** The `SCALE 33.2` artifact is the only one of the four that
  carries the `whole_body` block (the arm started after that instrument landed), and on task 0 it reads
  `whole_body` **0.1831** against `theta_only` **0.0238** and `bias_only` **0.1593** — so **the bias carries 87%
  of the whole-body first-order interference in this arm**, and the θ-only field the paper's theory is written in
  terms of holds **13%** of it. The arithmetic of the split closes exactly (`0.0238 + 0.1593 = 0.1831`), and task
  1's cancels (`0.0221 − 0.0205 = 0.0016`).

## 4. What this changes

- **§4.2's diagonal row is a statement about 97.1% of the parameters.** The same λ, the same seeds, the same
  selection rule: at 1.21σ from `naive` when the remaining 2.9% are left free, and at **4.84σ** when they are
  anchored. **The difference between "EWC does not resolve here" and "EWC resolves at 4.84σ" is a channel no
  penalty in this project covered** — and the coverage is not a hyper-parameter, since `e137` shows that a λ
  sweep presses the same 97.1% harder while the adaptation escapes into the 2.9%.
- **`e125` becomes a floor with a measured approach.** The free freeze is worth +0.0227 and the penalty reaches
  84.8% of the way, at four times the replicate count — so "a penalty is not a freeze" is now a quantitative
  statement rather than an expectation.
- **And it sharpens the paper's theory's status rather than its arithmetic.** The interference account is not
  shown to be *wrong* about θ; it is shown to be **about 13% of the body** in the arm that works, and to order
  the forgetting backwards across the three arms where the penalty's coverage changes.

## 5. What this cannot settle

- **One read-out (32), one λ (3e-3), one circuit, three tasks** — and read-out 32 is where the channel's share of
  the forgetting is **largest** (70%; `e134` measures 89% and 83% at 128 and 1307). The right place to ask
  whether covering the channel matters, the wrong place to generalise from.
- **The two scales bracket an ambiguity rather than resolving it** (equal per-parameter strength against equal
  total mass), and the **anchoring strength is now a hyper-parameter with a measured direction and an unmeasured
  optimum**: 1.0 → 33.2 buys −0.0060 ± 0.0068 (0.88σ), so a third scale is where "does it keep helping" would be
  asked.
- **A penalty is not a freeze**, and the 15.2% of the gap that remains is the part the penalty's own trade
  against the current task costs.
- **The whole-body comparison is one-armed until `e139` lands**: that run carries the same instrument on the
  `naive` and unanchored arms at the same seeds, so the three-way whole-body contrast is a reading of an artifact
  that is already running rather than a new experiment.
- **And nothing here covers `replay` or the block partitions**, which is `e140`'s arm: the same anchoring has not
  been applied to them, and `e135` says replay is the method whose margin is most confounded by this channel.
