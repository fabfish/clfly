# The census's draw-field list was itself a guess: `rewire_seed` was missing, and the exposure is 187 of 285 artifacts, not 215

**Date:** 2026-09-25
**Analysis only; the second correction to the family census in one evening.** The first correction
(`docs/findings/2026-09-25-the-census-was-reading-flag-names.md`) found that the census read the *network* line's
three draw flags and so missed the *linear* line entirely. This one is one layer down and one field over: the field
list itself was handwritten, and it omitted **`rewire_seed`**.

---

## 1. What was missing, and how it was found

Rather than guess again, the corpus was asked what seed-like keys it carries:

| key | artifacts | values seen |
|---|---|---|
| `seed0` | 318 | `0` — the base of every draw set, constant across the corpus |
| `seeds` | 168 | 2–12 — the **count** of task draws (handled as its own component) |
| `readout_seed` | 81 | 1, 2, 3, `None` |
| `partition_seed` | 37 | 1, 2, `None` |
| **`rewire_seed`** | **26** | **0–4, `None`** |
| `support_seed` | 8 | 1, 2, `None` |
| `seed_step`, `seed_b` | 3, 1 | 100 |
| `matching_seeds` | 2 | a **path string** (not a seed) |

**`rewire_seed` is the null-model draw** — the rewiring a topology control is built from — and the families
`e32`/`e33`/`e65` **vary it across 26 artifacts**. The census called them "replicates" (no manipulation varied), which
**hides the one family type that answers the question the census exists for**: a family that varies a *draw* is
measuring that draw.

**And it needed the same fix in two places.** Adding `rewire_seed` to the field list was not enough: `draw_keys`
builds the per-artifact draw tuple from components it names, and a field in the list but not in the tuple leaves
`len(draws) == 1`, so the rewire families still came out "replicates". Both layers are now covered.

## 2. The rule that replaces the list

> **A key whose name contains "seed" and whose values are all integers or `None` is a draw**, except `seed0` (the base
> of a draw set) and `seeds` (a *count* of task draws). A key whose values include a path string is not a draw.

`matching_seeds` is excluded by that last clause, `seed_b`/`seed_step` come in by the first, and the next line that
names its flag something else is still invisible — which is the honest limit of a rule over a vocabulary rather than
over designs.

## 3. The corrected census, twice corrected

| verdict | first run | flag-names fix | **this fix** |
|---|---|---|---|
| SINGLE-DRAW | 41 families / 215 artifacts | 38 / 205 | **35 / 187** |
| REPLICATED ACROSS DRAWS | 15 / 63 | 18 / 73 | 18 / 73 |
| DRAW ONLY | 1 / 3 | 1 / 3 | **4 / 21** |
| replicates | 2 / 4 | 2 / 4 | 2 / 4 |

**The exposure fell twice, from 215 artifacts to 187**, and both times for the same reason: the census was reading
names rather than designs, and every correction made the corpus look *better* than the previous reading. **That
direction is worth stating** — an audit whose first number is alarming should be suspected of over-reporting until its
field list has been tested against the corpus's vocabulary, and here that test was simply *asking which keys exist*.

**And the census now names the four families that deliberately measure a draw**: `e32`, `e33` and `e65` vary
`rewire_seed` (the null-model rewiring), and `e117` varies `readout_seed`. Those are the corpus's own draw
measurements, and a reader asking "has this draw ever been varied?" can now read the answer off the census instead of
believing a claim like the one `e199`'s registration got wrong.

## 4. What this does not change

- **The 187.** Those families still do not vary a draw between their artifacts, and 146 of the 285 artifacts still
  **average** a draw inside each cell — an averaged draw is not a varied one.
- **The network line's own measurements.** The support draw's 3.3–6.6σ effect and the read-out draw's size-specific
  smallness are measurements, not classifications, and no field list touches them.
- **The `timing_s` blind spot found while looking.** 12 artifacts — the linear line's — carry only `timing.total_s`
  where 298 carry a top-level `timing_s`, so the audits that key on `timing_s` (`e169`'s scope, `e190`, `e38`) have
  never seen them. It is the same class as this unit, it is small, and it is recorded rather than fixed here so that
  the fix can carry its own measurement of what it changes.
