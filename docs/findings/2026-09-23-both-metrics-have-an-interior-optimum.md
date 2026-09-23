# `e112`: both metrics have an interior optimum at read-out 300, and the five-point bowl was not one

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py`, five runs; artifacts `runs/e112_readout{300,700}_{plastic,frozen}.json`
and `runs/e112_readout300_plateau.json`.
**Artifacts:** the five above, plus the `e109`/`e110`/`e111`/`e104` artifacts at read-out 1307 / 900 / 512 / 128 / 32.
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, 5 replicates, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, **read-out 300 and 700**.
**Pre-registration:** `docs/findings/2026-09-23-bracketing-the-minimum-preregistered.md`, committed before the runs.
**Context:** `docs/findings/2026-09-23-the-read-out-axis-has-an-interior-minimum.md`, where five points gave
*"a two-sided interior minimum at 512 with both arms monotone"*.

---

## 1. Both predictions failed, and in the branch the pre-registration separated

**P1 failed**: forgetting at 700 is **+0.0354**, above 900's +0.0292 — so **the wide arm is not monotone**, and
the break is a local bump at 700 (+0.0062 against 900, +0.0146 against 512).
**P2 failed**: forgetting at 300 is **+0.0083**, *below* 512's +0.0208 — the minimum has **moved** to the narrow
side of the new bracket and is **2.5× deeper**.

That second failure is exactly the branch the pre-registration set aside in advance — *"a value below 512's means
a deeper, shifted bowl, which is a better result for the benchmark statement and a worse one for the location
claim, and those are different findings"* — and reporting it as one finding or the other is the whole reason to
separate them. **The location claim is refuted. The benchmark statement is strengthened.**

## 2. Seven points, two metrics, and they agree

| read-out | **forgetting** | **final accuracy** | task 0 forgetting | load-bearing gap | body drift |
|---|---|---|---|---|---|
| **1307** (whole) | +0.0479 | 0.9333 | +0.0833 | −0.0111 | 0.0195 |
| **900** | +0.0292 | 0.9347 | +0.0375 | −0.0014 | 0.0213 |
| **700** | **+0.0354** | 0.9431 | +0.0500 | −0.0014 | 0.0238 |
| **512** | +0.0208 | 0.9486 | +0.0333 | +0.0014 | 0.0258 |
| **300** | **+0.0083** | **0.9569** | +0.0208 | +0.0153 | 0.0313 |
| **128** | +0.0333 | 0.9333 | +0.0583 | +0.0167 | 0.0391 |
| **32** | +0.0729 | 0.9139 | +0.0833 | +0.1000 | 0.0493 |

**Read-out 300 has both the lowest forgetting and the highest accuracy of the seven** — and the
forgetting value is the **lowest plastic `naive` forgetting anywhere in this corpus** (0.0083 against 68 plastic
`naive` arms, the next lowest being the 2-class configuration's 0.0167). Task 1's forgetting there is
**negative** (−0.0042, i.e. better retained than at any point during its own training), and task 0's minimum is
**also** at 300 — so unlike the five-point reading, this shape is **per-task consistent**: task 0's series is
0.0833 / 0.0375 / 0.0500 / 0.0333 / **0.0208** / 0.0583 / 0.0833, the same minimum in the same place.

**The accuracy series is non-monotone too** — 0.9333, 0.9347, 0.9431, 0.9486, **0.9569**, 0.9333, 0.9139 — rising
to a peak at 300 and falling after. So **the two metrics a practitioner cares about agree on an interior
optimum**, which is the strongest form this statement can take, and it is not the form the paper's principle
implies.

## 3. The five-point bowl was not a bowl, and this is the fourth such revision

The previous fire's description — *both arms monotone, minimum at 512* — came from five points and was **wrong in
one arm** and **misplaced by 1.7× in the other**. Its numbers all stand; its shape does not. That is the fourth
time in this sequence that adding points has revised a shape claim, and the revisions have gone
**outlier → interior minimum → two-sided bowl → a non-monotone wide arm with the minimum at 300**, each time from
a pre-registered prediction about the *next* point rather than from re-reading. **A shape claim supported by
monotone arms on three and four points was not supported at all**: two more points broke one arm and moved the
minimum.

**The lesson is not "measure more points"** — it is that a monotone arm of length three is the weakest possible
evidence for monotonicity, and in this sequence it has now failed twice (the wide arm at 700 here; the
"whole state is an outlier" reading that a second wide point retired).

## 4. The design statement, and the two statements it separates

**Both metrics are optimized at read-out ≈ 300 of 1307 (~23% of the state), and neither is optimized at either
extreme.** Meanwhile **the load-bearing gap keeps rising monotonically as the read-out narrows** — −0.0111,
−0.0014, −0.0014, +0.0014, +0.0153, +0.0167, +0.1000, which is monotone non-decreasing at seven points and is
the series the paper's design principle is about. So:

> **"Narrow the read-out so the body is load-bearing" and "do not narrow it past an optimum" are two different
> statements, and the paper makes only the first.** The gap says the body matters more the narrower you go; the
> forgetting and the accuracy both say the *benchmark* is best at about a quarter of the state's width, and that
> going narrower than that costs on both metrics.

That is the first design statement this sequence has produced that a practitioner could act on, and it is the
opposite of what a monotone reading of the principle would suggest: read-out 32 has the **largest** gap (+0.1000,
the body is maximally load-bearing) and the **worst** forgetting (+0.0729) and accuracy (0.9139) of the seven.

**And it sharpens the sequence's central negative result rather than weakening it**: every mechanical quantity
measured (the drift, the gap, the first-order term, the second-order quadratic form) is monotone in the read-out
at the points where it has been measured, while both *reported* metrics are non-monotone and both peak in the
interior. A monotone quantity cannot order a non-monotone one, which is why four candidate mechanisms failed
here — and now there are **two** measured series with the same two-sided shape, not one.

## 5. What this cannot settle

- **Seven points is a curve on seven points**, and the minimum is now bracketed by **(128, 512)**. The bump at
  700 (+0.0062) is real at this configuration, since a fixed read-out has reproduced bit-identically at seven
  executions, but it is unexplained and it may be a second local feature rather than noise.
- **The accuracy peak carries the test-set floor**: 0.9569 is measured on 144 held-out decisions per replicate,
  so a difference of 0.008 between 512 and 300 is comparable to that floor even though the replicate spread here
  is zero — the two are different quantities and the paper's own §4.7 distinguishes them.
- **It does not say why**, and the sequence's mechanism search is where it was: every mechanical quantity is
  monotone, and the answer is not one of them.
