# E59 — every σ in this family is one of two, and the C1 contrast is **2.7σ** about the rewiring rule

**Date:** 2026-09-22
**Script:** `experiments/e59_separation_with_both_components.py`
**Artifacts:** `runs/e59_separation_components.json`, `runs/e48_cs800_perseed.json`, `runs/e32_rewire*.json`, `runs/e33_er_rewire*.json`
**Context:** `2026-09-22-cs800-column-reproduced-and-paired.md` (`e48`), `2026-09-22-twelve-seeds-reverse-the-e5-direction.md` (`e42`), `2026-09-22-er-separation-realization-exposure.md` (`e34`)

---

## 1. The distinction, finally made arithmetically

`e34` introduced it and `e36`–`e40` spent four experiments sharpening it, and it has never been put on
the two headline numbers in one place: **a σ about a graph is not a σ about a rule.** Both endpoints of
every contrast here come from the same six task seeds of **one** wiring, so there are two legitimate
error bars and they answer different questions:

- **about these two graphs** — the paired sem of the within-seed difference. It cancels the task draw
  (which is large) but not the wiring (which is larger).
- **about the rewiring rule** — the same, composed with each endpoint's realization sd, measured by
  sweeping six wirings at fixed circuit size.

A single realization's variance is the sum of these two components, so composing them is just the
variance-components decomposition:

| topology | mean | seed sem | realization sd | total sd | seed share |
|---|---|---|---|---|---|
| `swap2` | 0.01255 | 0.00025 | **0.00377** | 0.00378 | **0%** |
| `erdos_renyi` | 0.14214 | 0.00047 | **0.00320** | 0.00323 | 2% |
| `swap0.5` | 0.02287 | 0.00034 | *unmeasured* | 0.00034 | 100% |

**Ninety-eight percent or more of a single point's variance is the wiring draw, not the seeds.** That is
the quantitative statement of everything `e36`–`e40` found by other means.

## 2. The two headline figures

| | about these graphs | about the rewiring rule |
|---|---|---|
| **the ER separation** (`ER − swap2`), gap 0.12959 | **364.9σ** (paired, n = 6) | **26.1σ** |
| **the C1 contrast** (`swap0.5 − swap2`), gap 0.01032 | **28.8σ** (paired, n = 6) | **2.7σ** |

The paper's **152σ** was the seed-only, *unpaired* figure for two single realizations. The honest pair
of statements is **a few hundred σ about these graphs and 26σ about the rule** for the ER separation —
which leaves it by far the most robust quantity in the project, and the only one whose *both* endpoints
carry a measured realization sd.

**And the C1 contrast is 2.7σ as a statement about the rewiring rule.** That is a correction to the
previous fire's headline: `e48`'s paired −28.85σ is a correct and much better-founded statement *about
the cs = 800 graphs*, and it is exactly what `e47` asked for. But the quantity the project actually
claims — that heavy rewiring changes the penalty, as a property of the rewiring family — carries the
wiring draw, and on that reading it is **2.7σ**. Which is what `e36`–`e40` found by three other routes:
the sign flips across circuit sizes, the coordinate does not predict, and the sign rule fails above its
bracket.

**2.7σ is also a lower bound**, because `swap0.5` has no realization sweep and enters with a realization
sd of zero. A six-realization sweep of `swap0.5` is the single run that would settle the contrast's
magnitude, and it is the one gap this exercise exposes.

> **Closed, and the answer is 2.2σ (`e65`, `docs/findings/2026-09-23-the-c1-contrast-about-the-rewiring-rule.md`).**
> The six-realization sweep was run. `swap0.5`'s realization sd is **0.00269** against `swap2`'s 0.00377,
> so it is not negligible — the two rules have the *same order* of wiring spread, and the 1.9σ branch
> above was the close one while the 2.7σ "lower bound" was the optimistic extreme. Three readings are
> now reported rather than one: **28.8σ about the two graphs**, **2.2σ** on one redraw of each rule, and
> **3.4σ** comparing the rules' mean excesses (**5.8σ** with each arm's worst draw dropped). Every rule
> measured has a realization sd near 0.003 on the excess scale, so the separation between the ER
> result's 26σ and this contrast's 2.2σ is the *size* of the effect, not the noise. One further lesson
> from the sweep: at four draws `swap0.5`'s sd read 0.00054 and the bound looked exact; the fifth draw
> alone multiplied it by five.

## 3. What this does and does not change

**Changes:** the paper's 152σ should become *"364.9σ about these graphs, 26.1σ about the rewiring rule"*,
and the C1 refutation should be stated as *"28.8σ about the cs = 800 graphs, 2.7σ about the rewiring
rule"*. The previous fire's "the refutation is established" was right about the graphs and incomplete
about the rule.

**Does not change:** the ER separation remains the project's strongest result at 26σ about the rule; the
structure it describes — a separate regime, offset by a factor of eleven — is untouched; and the
realization attribution's *withdrawal* stands, since 98% of the variance being the wiring draw is a
statement about which component matters, not about whether the spread is a draw at all. The earlier
error was attributing the **spread across circuit sizes** (0.0205) to the realization component; the
realization component is real, small, and now measured.

## 4. Limits

- **`swap0.5`'s realization sd is unmeasured**, so the C1 row's across-graph figure is a lower bound in
  the σ and an *over*statement of the resolution. If its realization sd were as large as `swap2`'s, the
  contrast would fall to 1.9σ; if it were twice as large, to 1.3σ.
- **The realization sds are measured at one circuit size** (cs = 800, six wirings), which is where both
  headline figures live. Nothing here transfers to another circuit, and `e36` showed the circuit is
  precisely what moves these quantities.
- **The ER row's paired 364.9σ** arises because both endpoints are extremely stable seed-to-seed at
  cs = 800; it is a statement about these two graphs and should never be quoted as a result about
  Erdős–Rényi in general — that is the 26σ row.
- **This is a re-analysis, not a new measurement.** Every component comes from an artifact that already
  existed, which is the point: the numbers were always there to be composed and nobody had composed
  them.
