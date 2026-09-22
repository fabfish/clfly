# E53 — the coordinate search, enumerated: the rank coordinate orders the excess but does not fix its magnitude

**Date:** 2026-09-22
**Script:** `experiments/e53_geometry_coordinate_sweep.py`
**Artifacts:** `runs/e53_coordinate_sweep.json`
**Context:** `e36`–`e40`, `2026-09-22-the-smoke-test-was-one-seed.md` (`e51`), plan rule 13

---

## 1. What this closes, and why a closure was needed

Four findings established that `excess(swap2)` swings 166% across six circuits while its controls hold
to 10.5% and 24.3%, and that the one coordinate proposed for it fails as a law. The plan's summary is
*"no coordinate tried so far accounts for it"* — a statement about what happened to be tried, not a
closed search.

Every run stores the same geometry block, so **all eight coordinates can be tested at once**, on three
axes: **across circuit sizes** (the axis the ρ = +1.000 was claimed on), **across realizations at
fixed circuit size** (the independent axis, needing no circuit change), and **pooled**, which mixes
them. With eight coordinates that is up to 24 tests, so an uncorrected p is not a result.

## 2. The result: a survivor, and it is narrow

| axis | n | best coordinate | ρ | raw p | Holm over coordinates | **Holm over distinct orderings** |
|---|---|---|---|---|---|---|
| across circuit sizes | 6 | `effective_rank` / `flattening` | +0.829 | 0.0583 | 0.4667 | **0.1167 — no** |
| **across realizations** | 6 | `effective_rank` / `flattening` | **+0.943** | **0.0167** | 0.0833 | **0.0333 — YES** |
| **pooled** | 12 | `top_eig_share` | **−0.895** | **0.0002** | 0.0014 | **0.0008 — YES** |
| pooled | 12 | `effective_rank` / `flattening` | +0.839 | 0.0010 | 0.0071 | **0.0040 — YES** |

**So the rank coordinate orders `excess(swap2)` significantly within one circuit's realizations
(corrected p = 0.033) and on all twelve points (0.0008) — and not across circuit sizes on its own
(corrected p = 0.117), where the raw p is 0.058 at n = 6.** That last case is a power statement, not a
refutation, and it should be reported as one.

**Which means the plan's phrasing is too strong.** The correct statement is that **the coordinate
accounts for the *ordering* of the excess and not for its *magnitude law*** — the law being refuted
separately (cross-family log slopes 6.06σ apart, the pre-registered ±0.0034 band missed by 1.84×) and
the across-circuit sign rule separately again (above its bracket at −10σ). "No coordinate accounts
for it" invited the reading that the ordinal relation was also dead, and it is not.

## 3. Two things the enumeration forced, both of which changed the answer

**The coordinates are not eight tests.** On the cross-size axis the eight collapse to **two** distinct
orderings — `effective_rank`, `flattening`, `mean_rank_fraction` and `chance_alignment` all give
+0.829, and `top_eig_share` and `mean_rank` give −0.829 — and on the pooled axis to five. Holm over
eight treats one line of evidence as five, and it is what put the realization axis on the wrong side
of 0.05: **0.0833 over coordinates against 0.0333 over the two distinct orderings.** The script now
reports both columns and says which is which.

**There is no independent negative control among the recorded coordinates.** I had intended
`chance_alignment` as one — it is a property of the task construction rather than of the rewiring —
but it equals `mean_rank / d`, so it is monotone in `mean_rank` and moves with the circuit exactly as
`mean_rank` does. It gave +0.829 on the cross-size axis, identical to `effective_rank`. **The intended
control is collinear with a real coordinate and cannot falsify anything**, which means this sweep has
no internal falsification test and the survival in §2 rests on the corrections alone.

## 4. Two bugs in my own first version, both caught by re-running

- **`exact_p` above n = 8 returned `nan`, and the report printed that as "degenerate".** The pooled
  axis has 12 points, so its entire result was hidden behind a *reporting* bug — the correlations were
  perfectly computable. Fixed with a Monte-Carlo permutation p (200,000 draws, seeded, and with the
  +1 in numerator and denominator so a finite sample never reports p = 0), and "no spread to
  correlate" is now distinct from "no p available".
- **The script claimed to apply a distinct-ordering correction it never implemented**, and the
  version that did implement one scaled each p by its own rank within the distinct set — which gives
  the largest |ρ| no correction at all and is not Holm. Fixed by running Holm over one representative
  per distinct |ρ| and mapping back.

## 5. What this does not close

- **Functional forms and interactions are not searched.** Logs, products, ratios and pairs of these
  quantities are an unbounded space; §2's survival is about the recorded quantities as recorded.
- **Quantities the runs do not record** are not searched, and the most likely candidate — something
  about the *propagator's* conditioning rather than the task's spectrum — is not in the geometry block.
- **The pooled axis mixes two axes** and is the reading a casual "look at all the data" would take. It
  is reported because it is legitimate (the two axes overlap in effective-rank range, 1.4–15.4 and
  1.4–8.2) and because it is the strongest single number here, but it should not be quoted alone.
- `e48` had not landed when this ran, so cs = 800's contribution on the cross-size axis comes from
  `e2_analytic`. Its geometry is the same; only its per-seed storage differs, which this sweep does not
  use.
