# E65 — the `swap0.5` realization sweep: the C1 contrast is **2.2σ about the rewiring rule**, and the bound `e59` reported was the optimistic end

**Date:** 2026-09-23
**Script:** `experiments/e65_realization_sd_by_rule.py`
**Artifacts:** `runs/e65_swap05_rewire{0..5}.json`, `runs/e32_rewire{0..5}.json`, `runs/e33_er_rewire{0..5}.json`, `runs/e65_realization_sd_by_rule.json`
**Context:** `2026-09-22-two-sigmas-per-family.md` (e59), `2026-09-22-cs800-column-reproduced-and-paired.md` (e48), `2026-09-23-side-draw-sd-refutes-the-concentration-model.md` (e67)

---

## 1. Why this run exists, and the reading it replaced

`e59` established that every σ in the C1 family is one of two: a σ about **the particular graphs
drawn** (the task-seed sem) and a σ about **the rewiring rule** (how much the excess moves across
independent draws of the rule). For `swap2` both were measured; for `swap0.5` there was **no
realization sweep**, so the contrast's rule-σ could only be reported as its most favourable value —
2.7σ, computed with `swap0.5`'s realization sd set to **zero** — with 1.9σ as the alternative if
`swap0.5` had a `swap2`-sized sd. Those two differ by 40%, which is the whole question, and the run
that settles it is this one.

`e65` is `swap0.5` at cs = 800 over **six independent rewire seeds**, the shape `e32` already provided
for `swap2`. Its realization 0 reproduces `e48`'s published `swap0.5` value (0.022868) exactly, which
fixes which draw the published column used.

## 2. The three rules' wiring spreads, and they are all of the same order

| rule | draws | excess mean | **sd across draws** | seed sem | ratio |
|---|---|---|---|---|---|
| `swap0.5` | 6 | 0.021683 | **0.002687** | 0.000406 | **6.6×** |
| `swap2` | 6 | 0.015299 | **0.003774** | 0.000203 | **18.6×** |
| `erdos_renyi` | 6 | 0.143913 | **0.003195** | 0.000755 | 4.2× |

```
swap0.5        0.022868  0.023626  0.022418  0.022029  0.016308  0.022852
swap2          0.012547  0.013496  0.015033  0.019402  0.020305  0.011009
erdos_renyi    0.141759  0.142226  0.148966  0.146883  0.141337  0.142307
```

**Every rule's realization sd is ≈ 0.003, and `swap0.5`'s is only 1.4× below `swap2`'s** — not the 7×
that the first four draws suggested. The wiring draw outweighs the task draw by 4–19× depending on the
rule, so this is the binding axis of the whole family and it is a roughly constant 0.003 on the excess
scale, independent of how much of the wiring was randomised.

## 3. The C1 contrast under each question you can ask of it

| question | figure |
|---|---|
| **(i)** about **these two graphs** (paired, at the published draw) | **28.8σ** |
| **(ii)** about the **rule**, one redraw of each | **2.2σ** |
| `e59`'s most favourable reading (`swap0.5` sd := 0) | 2.7σ |
| `e59`'s alternative (`swap0.5` sd := `swap2`'s) | 1.9σ |
| **(iii)** about the **rule**, comparing means of draws | **3.4σ** |
| **(iii)** dropping each arm's worst draw | **5.8σ** |

`(i)` is the number the C1 line publishes and it is a statement about two graphs. The rule-level
answers are **2.2σ** on the redraw question and **3.4–5.8σ** on the means question.

**So `e59`'s bound was not tight, and the branch it called the pessimistic alternative was the close
one.** The measured 2.2σ sits beside the 1.9σ "if `swap0.5` had a `swap2`-sized sd" — the assumption
that `swap0.5`'s spread is negligible was the wrong one, and the assumption that it is comparable to
`swap2`'s was nearly right.

## 4. The reading this replaces, which was stated before the sweep finished

While four of the six draws were in, the sd was **0.000535** and the conclusion drawn was that `swap0.5`
was 7× tighter than `swap2` so the 2.7σ bound was essentially exact. That reading was reported. **The
fifth draw is 0.016308** — 2.0 sd below the six-draw mean, against a five-draw band of 0.0220–0.0236 —
and it alone multiplied the sd by five. The sixth changed nothing. So:

* **a four-draw realization sd is not an estimate of anything**, which is plan rule 15 arriving on the
  *realization* axis rather than the seed axis. The same sd computed on draws 0–3 was 0.000535; on all
  six it is 0.002687, a factor of 5.0;
* **the honest form of the rule-σ is a range**, and the range is measurable rather than hypothetical:
  `(iii)` moves from 3.4σ to 5.8σ when each arm's worst draw is dropped, so that is the interval to
  quote;
* the one thing the partial reading got right is the direction of the *headline*: the rule-σ is smaller
  than 2.7σ, not larger. It got the factor wrong by 1.2× and the mechanism — "the two rules have
  different wiring spreads" — wrong by 5×.

## 5. What this leaves the C1 line asserting

* **About the two graphs drawn at cs = 800: −0.010322 ± 0.000358 = −28.8σ, paired over six task seeds.**
  Unchanged, and it is a legitimate statement about those graphs.
* **About the rewiring rule: 2.2σ** on the one-redraw reading; **3.4–5.8σ** on the rule-mean reading.
  So "randomising the wiring this much moves the diagonalisation penalty" is **supported at the rule
  level but only at 2–6σ, not 28.8σ** — and the two rules differ by 0.0064–0.0103 in excess, against a
  wiring spread of 0.003. The contrast is 2–3 realization sds.
* **The Erdős–Rényi separation is unaffected and remains the strong one**: `e59` has it at 364.9σ about
  the graphs and 26.1σ about the rule, and ER's realization sd measured here (0.003195) is the same
  order as the swaps' — the reason ER's rule-σ is 26σ rather than 2σ is that its contrast is 0.13, an
  order of magnitude larger. Same wiring noise, larger effect.

## 6. Limits

- **Six draws per rule.** An sd on six points is pinned to about ±30%, so `(ii)` is good to a factor of
  ~1.3 and `(iii)` worse. Both are quoted as ranges.
- **One circuit size.** cs = 800 only. The six-point size sweep in §4.2 is a different design and says
  nothing directly about these sds at other sizes.
- **The two ensembles share their base graph `W0`.** The *within*-ensemble sds used here are unaffected
  by that, but `(iii)` compares means of two ensembles built from the same base, so any property of
  `W0` common to both cancels in the difference rather than being sampled — which makes `(iii)` a
  statement about the rewiring operator, not about connectomes in general.
- **`(ii)` and `(iii)` answer different questions and both are reported.** Collapsing them into one
  number would hide that the published contrast is fragile to a redraw (2.2σ) while the rules' mean
  excesses genuinely differ (3.4σ). Neither licenses the 28.8σ.
