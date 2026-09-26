# Registered: the drawing lottery — does the in/out asymmetry survive a second null drawing?

*2026-09-26 10:00. Runs: `e231_rank_versus_rho.py --rewire-seed {1,2}` over the nine-point `rho` grid at cs 300 and
over four points (`rho` 0.8/0.9/0.95/0.99) at cs 800, four topologies each, **~35 min**, to be written as
`e231_cs300_rw1.json`, `e231_cs300_rw2.json`, `e231_cs800_rw1.json`, `e231_cs800_rw2.json` in the runs directory.
The `--rewire-seed 0` curves already exist (`e231_cs300_rank_curve.json`, `e231_rank_versus_rho.json`).*

## 1. What is open, and why one drawing is not enough

`e231`'s completed grid gave three verdicts — the rank falls monotonically (P1, with one family's falsifier firing by
a 3% saturation at cs 800), the cs-300 family order is not stable (P2's falsifier, a crossing between `rho` 0.7 and
0.8), and the cs-800 `alloy1`/`inalloy1` separation is systematic in `rho` (P3 MET, 10.1× to 16.7× above the 4.14×
bar at six of nine points). But the registration flagged the limit that decides how much of it is about the
*substrate*: **every curve is one drawing of the null** (`--rewire-seed` defaults to `seed0`), and `e230` measured
`alloy1`'s scatter across drawings at cs 800 at **16.44×** — the same size as the separation P3 established.

**A smoke test of the new flag says the lottery is real and lands on the sign.** At cs 300, `rho` 0.9:

| drawing | `alloy1` | `inalloy1` | ratio |
|---|---|---|---|
| `--rewire-seed 0` | 7.20 | 11.62 | **0.62×** |
| `--rewire-seed 1` | **11.19** | **6.29** | **1.78×** |

The direction is **reversed** between two drawings of the same configuration, and the ratio moves from 0.62 to 1.78 —
a factor of 2.9. (Both new values also reproduce *stored* artifacts: `e230`'s census lists cs-300 `alloy1` at
`rho` 0.9 as 4.10–11.19 and `inalloy1` as 6.29–13.07, so this flag measures the corpus's own drawing axis rather than
a new one.)

## 2. The registered claims

- **D1 — the cs-800 separation survives the lottery (magnitude).** At cs 800, `rho` 0.9, the `alloy1`/`inalloy1`
  ratio exceeds **4.14×** for **all three** drawings (rewire seeds 0, 1, 2). **Falsifier**: any drawing at or below
  4.14×, which would say P3's 10.1× was that drawing's; **null**: one drawing above and one below (a magnitude that
  is drawing-dependent while the direction is not).
- **D2 — the cs-300 asymmetry is NOT drawing-stable (direction).** At cs 300, `rho` 0.9, the **mean** ratio over the
  drawings is within a factor of two of 1 (i.e. between 0.5 and 2). **Falsifier**: a mean at or outside those bounds,
  which would say the cs-300 direction is stable after all and the smoke test's reversal was one pair;
  **null**: a mean inside the bounds but with every *individual* drawing on one side of 1.
- **D3 — the cs-800 direction IS drawing-stable.** At cs 800, `rho` 0.99, **every** drawing gives a ratio **above 1**,
  i.e. the family whose out-structure is destroyed keeps less rank in every drawing. **Falsifier**: any drawing with a
  ratio at or below 1.

**Reported**: every drawing's four topology ranks at every measured `rho`, the ratio per (size, `rho`, drawing), the
spread of the ratio across drawings, and the instrument's verification lines against the corpus's `geometry` blocks
where they exist.

## 3. What it cannot do

- **Three drawings** (seeds 0–2), not a distribution: a ratio that is stable across three is not thereby stable
  across the population of nulls.
- **Two `rho` values at cs 800** carry the claims (0.9 and 0.99); the other two points are context.
- **The tasks' own stream is fixed** (`seed0` = 0, `--seeds 3`), so this varies the *null's* drawing and not the task
  seeds' — the two are separable here and only one is varied.
- **Nothing about the penalty**: this is the task geometry's rank, not the excess, and `rho` still mixes propagation
  depth with weight scale.
