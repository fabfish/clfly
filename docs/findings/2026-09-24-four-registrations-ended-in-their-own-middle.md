# Four registrations ended in their own middle, and that is a defect in the bars

**Date:** 2026-09-24
**Scripts:** none — this is a count over today's registrations and what each one's bars were. It produced **rule
41** in the plan, and one upgrade to §7 of the paper.
**Artifacts:** the four runs and findings named below, all of which had their predictions committed *before* the
run.

---

## 1. The four

| registration | the bar | what was measured | distance from the bar |
|---|---|---|---|
| `e141`'s P2 — *the forgetting does not fall as λ rises* | λ = 3e-2 worse than 3e-3 at **≥ 2σ** | **+0.0156 ± 0.0098 = 1.60σ** | 0.40σ short |
| `e142`'s P1 — *a shared-input family raises the forgetting* | **≥ 3σ**, a 3.00σ bar needing an effect of **+0.03190** | **+0.03177** | **0.012σ** short |
| `e148`'s P2 — *replay's margin shrinks on the hard family* | smaller at **≥ 2σ** | **−0.0201 ± 0.0124 = 1.62σ** — **larger**, i.e. the *falsifier's* direction, but 0.38σ below its bar | neither yes nor no |
| `e150`'s P1 — *the pair is a unit* | at or below **+0.0149**; falsifier at or above **+0.0318** | **+0.0190** | inside the interval between the two bars |

**In every case the bar was a round number** — 2σ, 3σ, 2σ — **and in no case was it placed by asking what the
competing readings predicted.** `e148` is the sharpest: the registration *had* a mechanism, *had* a falsifier, and
its measurement landed between them, so a falsifier that had already been written down did not fire.

## 2. What this does and does not mean

**It does not mean the four findings are wrong.** Each of the four left something the design *could* decide, and
in three of them that something was the more useful half: `e141`'s question was answered *yes* at **4.24σ** by the
loss-valued metric in the same file (which became rule 37); `e142`'s C1 premise passed at **9.16σ** while its P1
missed by 0.012σ; `e148`'s falsifier direction is informative even unresolved, and its P1 held at 10.79σ; and
`e150`'s registration **named the middle in advance as informative rather than as a failure**, which is why its
outcome needed no repair at all. **So the defect is not the outcome — it is that four of today's bars were
placed at the measurement scale rather than between hypotheses.**

**And the bar's scale is knowable in advance from today's own numbers**: a sem estimated from forty pairs carries
about **11%** relative uncertainty (`e142`'s own §), so a bar within ~10% of the predicted effect is not decidable
at n = 40. `e142`'s bar was inside 0.04% of its effect.

## 3. The repair, in the form `e150` already used

`e150`'s registration is the worked example, and it is worth copying verbatim rather than paraphrasing: it wrote
down **what each competing reading predicts** — *the pair is the unit → +0.0069; the family scales it → +0.0314;
the penalty is saturated → +0.0398* — then placed its bars at the **edges of the interval those predictions span**
(+0.0149 and +0.0318), and named the middle an outcome. It also stated the resolution arithmetic that makes those
bars meaningful (a paired sem of 0.0036 is 6.0% of the residual per σ). Both halves are now rule 41.

**And the second half has a harder form worth naming**: when two competing readings' predictions fall inside each
other's 2σ windows, **no bar can separate them** and the registration should say so before the run rather than
discover it after. Neither of today's four did.

## 4. What this cannot settle

- **Four cases is a small sample and they are all from one session**, one configuration family (cs 800, read-out
  32, three tasks, forty seeds) and one project's habits; the count is a count of *this session's* registrations,
  not a rate.
- **The remedy costs seeds or changes the question**, and both are real prices: a bar far enough from the noise to
  be decidable needs either ~140 seeds for a 1.6σ-scale effect or a form (a ratio, a sign test, a second metric)
  whose noise is not the metric's own.
- And the four middles are **not evidence that the hypotheses are false** — in each case the *registered form*
  failed to decide while the question it asked was answered by another quantity in the same artifact. That
  sentence is rule 37's, and this finding is the count that made it worth writing down twice.
