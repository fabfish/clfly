# The hole has a penalty, and on its first realization the response is graded

*2026-09-26 02:17, `runs/e212_alloy_analytic_rs0.json` — stage 2's **first realization** (`--rewire-seed 0`), read from
the runner's own report. Stage 2 was registered at two realizations, so **this is a measurement and not P2's verdict**;
the second realization is in flight. The registration is
`docs/findings/2026-09-26-registered-an-alloy-between-the-two-null-families.md`.*

## 1. The two cells

| cell | alignment | × chance | analytic excess | sem | bio − rand |
|---|---|---|---|---|---|
| `alloy0.75` | 0.0461 | 0.83× | **+0.02973** | 0.00023 | +0.00202 (6.0σ) |
| `alloy1` | 0.1417 | **2.55×** | **+0.10067** | 0.00057 | +0.00623 (9.4σ) |

The jump from `alloy0.75` to `alloy1` is **+0.07094** — **89.5σ** paired on the shared task seeds (116.1σ unpaired),
so it is not a marginal measurement in any sense.

## 2. What that number means for C3

Place the record's cs-800 penalty values in alignment order:

| regime | alignment | × chance | penalty |
|---|---|---|---|
| the in-axis cells (`real` … `swap2`) | 0.0044 – 0.0848 | 0.07 – 1.53× | 0.01237 – 0.02317 |
| `alloy0.75` | 0.0461 | 0.83× | 0.02973 |
| **`alloy1`** | **0.1417** | **2.55×** | **0.10067** |
| Erdős–Rényi | 0.2714 – 0.2904 | 4.89 – 5.23× | 0.14134 – 0.14897 |

**`alloy1`'s penalty is 71% of the distance from the in-axis regime to the Erdős–Rényi regime**, and 68% of the ER
value itself, at an alignment that is **half** the ER family's. So on this realization:

- **P2's bar is met**: the cell nearest the ER end has excess **0.10067 ≥ 0.06**, which the registration called *"the
  jump is already substantially made inside the hole, i.e. a steep gradient in alignment"*. The falsifier (at or below
  0.035) is nowhere near.
- **and the transition looks graded rather than thresholded** over the range the record can now see: 0.0135 (in-axis)
  → 0.0297 (0.83× chance) → 0.1007 (2.55×) → 0.1419 (5.2×), i.e. the penalty rises with alignment at **every** step,
  including through the interior of the hole that was empty an hour ago.
- The matched contrast moves with it: the biological partition's edge over its size-matched random control is
  **+0.00202 (6.0σ)** at `alloy0.75` and **+0.00623 (9.4σ)** at `alloy1`, against the record's earlier ~0.002 at the
  axis — so the *biological advantage* is also growing inside the hole, not just the penalty.

## 3. What is not yet established

**One realization.** The swap family's own spread was **1.60–2.05×** across five drawings at every strength, so a
single `alloy1` value cannot be attributed to `alloy1` until the second drawing says how much of 0.10067 is the
construction and how much is the draw. That is exactly what `--rewire-seed 1` is running for, and it is the reason
stage 2 was registered at two realizations rather than one.

Also unestablished: whether the response is graded over the **upper** half of the hole (`alloy1` is the ceiling of this
family by construction, so `[0.20, 0.271]` still needs a third construction — an alloy that randomises a fraction of
the **sources** as well, or a direct mix with the Erdős–Rényi edge set); and whether the same shape appears at other
circuit sizes, which have their own anchor sets.

## 4. The one-line state of C3

An hour ago C3's transition was *unmeasured* with a hole in it. It now has: a **monotone** interpolation between the
two null families, **one cell inside the hole with a penalty 71% of the way across**, a **89.5σ** step between the two
cells of the alloy axis, and a replication of that cell's value in flight.
