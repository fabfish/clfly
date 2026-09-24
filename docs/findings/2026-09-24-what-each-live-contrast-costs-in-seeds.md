# The price of resolving each live contrast, in seeds — and it is why so many registrations landed in their own middle

**Date:** 2026-09-24
**Script:** `experiments/e157_power_table.py` — analysis only, no runs. Artifact: `runs/e157_power_table.json`.
**What it does:** for each of the line's live contrasts, from the forty paired seeds already on disk, the paired
per-seed sd gives the seeds that contrast would need for 2σ and 3σ **at the effect it measured** — and, because an
effect estimated at forty seeds is biased away from zero, also at **half** and **a quarter** of it.

---

## 1. The table

| contrast | metric | Δ | σ now | n(2σ) | **n(3σ)** | at Δ/2 | at Δ/4 |
|---|---|---|---|---|---|---|---|
| plastic `replay − naive` | forgetting | −0.0784 | 9.35 | 2 | **4** | 16 | 66 |
| frozen `ewc − naive` | newest | −0.0651 | 8.95 | 2 | **4** | 18 | 72 |
| frozen+ewc 3e-4 − the freeze (shared-input) | forgetting | −0.0409 | 6.87 | 3 | **8** | 30 | 122 |
| frozen offsets − `naive` | forgetting | −0.0523 | 5.90 | 5 | **10** | 41 | 165 |
| frozen `replay − naive` | forgetting | −0.0208 | 5.89 | 5 | **10** | 42 | 166 |
| frozen `ewc − naive` | forgetting | −0.0247 | 5.85 | 5 | **11** | 42 | 168 |
| wiring `ewc − naive` | forgetting | −0.0437 | 4.73 | 7 | **16** | 64 | 258 |
| frozen+ewc λ step (shared-input) | forgetting | −0.0182 | 4.34 | 8 | **19** | 76 | 306 |
| **plastic `block − block-rand` (the BIOLOGY)** | forgetting | −0.0206 | 2.08 | 37 | **83** | 333 | 1,334 |
| frozen+ewc λ step (base) | forgetting | −0.0047 | 1.46 | 75 | **169** | 674 | 2,697 |
| plastic `ewc − naive` | forgetting | −0.0096 | 1.21 | 109 | **246** | 983 | 3,930 |
| **frozen `block − block-rand` (the BIOLOGY)** | forgetting | −0.0029 | 0.98 | 165 | **372** | 1,489 | 5,955 |
| plastic `replay − naive` | newest | −0.0036 | 0.79 | 254 | **571** | 2,284 | 9,136 |
| **wiring `block − block-rand` (the BIOLOGY)** | forgetting | −0.0018 | 0.17 | 5,585 | **12,567** | 50,269 | 201,076 |
| wiring `block − block-rand` (the BIOLOGY) | newest | −0.0021 | 0.54 | 550 | **1,237** | 4,948 | 19,791 |
| frozen `replay − naive` | newest | +0.0005 | 0.15 | 7,052 | **15,867** | 63,469 | 253,878 |

**8 of the 17 resolve at 3σ at forty seeds. The median n(3σ) at the observed effect is 83; at half the effect it
is 333.**

## 2. Three things it says

**First, the contrasts that resolve are almost free.** Every contrast at ≥ 4σ would have resolved at **4 to 19
seeds**: the line's forty is *insurance* against the seed draw, not the thing that made those results. That is the
right reading of `e140`'s C0a and of the reproduction claims — the extras buy robustness, not resolution.

**Second, the paper's central claim is unresolvable at any affordable n, and the table says so in arithmetic.**
The biology's own contrast (`block` − `block-rand`) measures, at forty seeds, an effect that would need **83**
seeds to resolve at 3σ in the plastic arm, **372** in the frozen arm, and **12,567** — at *half* that effect,
**50,269** — on the shared-input family. **So the honest form of the claim is the bound the paper already quotes**
(*the difference this design can see is smaller than the variation of its own control*), and the three-draw tests
are what turned three separate single draws into that bound. A later session that reads *"n = 83 would settle it"*
should read the Δ/2 column with it: 333.

**Third — and this is the finding — it explains the session's four registrations that landed in their own middle,
in one number.** Those four were contrasts whose measured resolutions were 1.60σ (`e141`'s P2), 2.99σ (`e142`'s
P1), 1.62σ (`e148`'s P2) and a mid-zone landing (`e150`'s P1). **Read against this table, an effect quoted at
1.5–3σ at forty seeds is an effect that needs between 83 and 1,237 seeds to resolve at 3σ** — i.e. between two and
thirty times the budget the project was spending. **Rule 41 said "place the bar between the competing predictions
rather than at a round number"; this table says what the alternative costs**, and it makes the rule arithmetic
rather than stylistic: *a registration whose predicted effect would need more seeds than the project is willing to
run is a registration that should be written as a bound, not as a bar.*

## 3. What this cannot settle

- **`n(3σ) = (3·sd/Δ)²` is circular by construction**, which is why Δ/2 and Δ/4 are printed. The four middle
  registrations are *also* the evidence that Δ at forty seeds is optimistic for small effects, and the table's
  Δ/4 column is the pessimistic end rather than a prediction.
- **It assumes the paired sd is known and stable.** For the arms with interleaved draws the sd has a draw
  component the pairing removes only within a draw; the three-draw controls showed the *draw* term at 0.0096 on
  the base family, which for the biology's contrast is *larger than the effect* — a fact this table's `sd` column
  does not separate.
- **Seeds are not the only currency**: the interaction between the two interventions (`e149`) needs **62–140 seeds**
  and is quoted as a bound for the same reason, while `e155`'s floor-model test buys a *new axis* rather than more
  seeds for the same contrast. n is what a bar costs; a different form is often cheaper, and this table prices only
  the first.
- One read-out, one circuit, three tasks, one seed stream: these n are properties of *this benchmark's* noise, and
  the read-out axis is already known to move it (the metric is thirty times noisier at some read-outs than at
  others).
