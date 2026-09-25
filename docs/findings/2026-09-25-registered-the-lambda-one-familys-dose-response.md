# Registered: the λ = 1.0 family's dose-response, which the mis-specified launch accidentally produced

**Date:** 2026-09-25
**Registered while its remaining levels run.** `e193`'s three commands inherited the runner's default **λ = 1.0**
while the family they were registered against runs **λ = 3e-3**
(`docs/findings/2026-09-25-a-333x-penalty-step-dressed-as-an-overlap-effect.md` §1). Per-arm admission salvages them
into **two** dose-responses, and one of them — the block arms against `e153` (λ = 1.0, overlap 1.0) — is a design
nobody registered. This registers it, with one of its three points already measured.

---

## 1. Why this is worth registering rather than discarding

The block arms at λ = 1.0 with overlap 0.1429 already say something the λ = 3e-3 family does not: **lowering** the
input overlap from 1.0 to 0.1429 **raises** their forgetting by **+0.0453 ± 0.0110 = 4.1σ** (accuracy −0.0309 =
4.2σ) while their own first-order interference term moves **+0.0010 = 0.3σ**. The λ = 3e-3 family's `naive` arm
moves the *other* way on the same axis (+0.0141 for *raising* the overlap) — but those two families are at different
penalties and different ends of the axis, so nothing licenses comparing them directly. What the λ = 1.0 rows give is
a **three-point response within one family**, which is the shape question the registered design asked.

## 2. The registration

**Design**: the three `e193` artifacts (targets 0.25 / 0.50 / 0.75 → achieved Jaccard 0.1429 / 0.3333 / 0.6000),
`ewc-block` and `ewc-block-rand` arms, read against `runs/e153_r32_overlap1_methods_40reps.json` (λ = 1.0,
overlap 1.0, 40 replicates, same circuit and read-out). **Instrument**: `e191 --dose` and `e188 --dose`, whose
per-arm admission selects `e153` for these arms automatically and prints the pair each row measures.

- **P1 — monotone in the overlap, in the direction the 0.1429 point already shows.** The forgetting at achieved
  0.3333 and at 0.6000 lies **between** its value at 0.1429 (+0.0453) and its value at 1.0 (zero by construction),
  with the 0.3333 point **above** the 0.6000 point: *less overlap, more forgetting*, ordered.
- **P2 — the dissociation persists.** The block arms' adjacent-pair interference term stays within 1σ of zero at
  **every** level, i.e. the first-order account does not track the 4.1σ forgetting move at any of the three points.
- **Falsifier — the response is not ordered**: forgetting at achieved 0.3333 or 0.6000 **exceeds** the 0.1429 value
  at ≥2σ (a rise as the overlap *increases* toward 1.0), or the interference term rises at ≥2σ at some level, which
  would restore the account's tracking and kill P2.
- **Null worth keeping**: both new points unresolved (~1σ) on forgetting, which would say the 4.1σ at 0.1429 is a
  one-point anomaly rather than the start of a graded response.

## 3. What would make this registration wrong rather than refuted

- **The family is one draw.** `e153` and the three levels share `partition_seed` 0 for the block partition and
  `readout_seed` 0 for the read-out draw; rule 10's population question is untouched and no level varies either.
- **λ = 1.0 is not a neutral setting**: `e153`'s own finding records that at λ one the wiring family's arms are
  *also* the λ = 1.0 arms, so a level effect here is not separable from what the penalty does at that strength — which
  is exactly why the registration is stated as an ordering *within* the family and never as a magnitude against the
  λ = 3e-3 rows.
- **The x-axis is unchanged and measured**: the three levels' achieved overlaps are the ones `overlap_controlled_supports`
  produces at seed 0 on `mb+cx+al@n1307` (0.1429 / 0.3333 / 0.6000), the same four decimals `e7`'s controlled sweep
  reports.

## Reproduce

```
uv run python -m experiments.e191_interference_across_lines --dose runs/e193_r32_overlap025_methods_40reps.json
uv run python -m experiments.e188_overlap_contrast --dose runs/e193_r32_overlap025_methods_40reps.json
```
