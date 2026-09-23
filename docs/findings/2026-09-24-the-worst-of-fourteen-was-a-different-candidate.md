# The worst of fourteen was a different candidate

**Date:** 2026-09-24
**Script:** none new; the numbers are fields of `runs/e58_bases_18seeds_perseed.json` (the 18-seed per-seed run,
`--extra-bases`) and `runs/e66_named_bases_seed_robustness.json` (`e66`'s per-seed contrasts over it).
**Paper:** `docs/paper/clfly-v1.md` §4.4, one parenthetical, corrected in this fire.
**Trigger:** the previous fire (`docs/findings/2026-09-24-the-sharp-check-counted-a-column-it-cannot-check.md`)
stopped counting §4.4's `delta vs the diagonal` column as a *failure* and left it **unchecked**, and the first
question that leaves is the one the table cannot answer by itself: **does the paragraph's reference value close
against the table's deltas?**

---

## 1. The answer, and it is no

§4.4's last paragraph says, of the adaptive spectral truncations:

> Spectral truncation to the top `r` directions of the current posterior — locally optimal at every step — is the
> *worst* of all fourteen (+0.0222 against the diagonal's +0.01762).

The same 18-seed run's artifact holds all fifteen keys — the diagonal plus the fourteen candidates — and sorted by
excess at **d = 1307** it reads:

| basis | excess (18 seeds) | in the table? |
|---|---|---|
| **`rank4`** | **0.0223347** | yes — `+0.00472` vs the diagonal |
| `rank16` | 0.0223113 | yes — `+0.00469` |
| `rank64` | **0.0222016** | yes — `+0.00458` |
| `diagonal(EWC)` | 0.0176167 | the reference |
| … the other eleven, 0.01755 down to 0.00391 | | |

**So the worst of the fourteen is `rank4` at +0.0223, and the paragraph's `+0.0222` is `rank64`'s value** — the
third-worst of the three truncations, quoted as the worst. The two differ by **0.00013**, and both are in the
artifact: this is not a measurement error but **the wrong member of a family**, which is exactly the shape a
reader cannot catch, because the quoted number is a real number from a real run.

## 2. And the identity that makes it checkable

The two artifacts are independent in the sense that matters: `e58` stores each basis's **absolute** excess,
`e66` stores each basis's **paired delta against the diagonal**. They must satisfy

```
excess(rank4) - excess(diagonal) = delta(rank4)
0.022334689567 - 0.017616731227 = 0.004717958340
```

and they do, **to floating-point precision** (they differ in the eighteenth decimal) — so the artifacts agree, the
table is right, and the prose is the only place the error can be. The same identity holds for the paragraph's
other two numbers, which are **correct**: the diagonal's +0.01762 is 0.0176167 and the eigenbasis's +0.01270 is
0.0127022, both to five decimals, and the "28%" reduction is 1 − 0.0127022/0.0176167 = **27.9%**. **One number in
three was the wrong member.**

## 3. The correction, and why it took this long

The paragraph is corrected in place and marked. **What kept it invisible is the subject of the previous fire**:
the column that holds the deltas was reported by the sharp check as *failing* for a reason that was false (no row
matched the comparator), so its real state — **not checkable, and therefore unchecked** — was masked. A checker
that is wrong about *why* a thing fails is as bad as one that is wrong about *whether* it fails, because the
first hides the second's absence.

**And the general form of this defect is rule 34's**: a sentence can be closed against a table by arithmetic, and
here the arithmetic is *subtraction between two artifacts*. `e132` mechanises that for a registered prediction
with given inputs; this is a second instance of the same shape, found by hand, and it is recorded as a candidate
for that audit rather than as a new tool.

## 4. What this does not change

- **Not a measurement.** No number in the table moves: all four deltas, four σ's, four sign patterns, four
  LOO minima and four leverages match `e66`'s stored fields at the printed precision, and the sentence's claim
  — *the three worst candidates are the adaptive ones* — holds exactly, with the top three places occupied by
  `rank4`, `rank16`, `rank64`.
- **Not a change in §4.4's conclusion.** The eigenbasis still beats the diagonal by 28% at d = 1307 and is still
  third-best of fourteen; the correction moves the worst candidate's absolute by 0.0001331, which is 0.6% of that
  candidate's own excess (0.0223347).
- **And the correction is not a coin-flip between two near-ties.** `rank4` really is the worst of the three
  truncations: paired across the same eighteen seeds, `rank4` − `rank64` is **+0.0001331 ± 0.0000078 = 16.96σ,
  18/18 positive**, and `rank4` − `rank16` is **+0.0000233 ± 0.0000028 = 8.38σ**. So the paper's number was not
  merely a rounding of a tie — **the number it should have printed is resolved from the number it did print at
  17σ**, on the same seeds, inside one artifact.
- **And it does not make the column checkable.** A `delta vs X` column still cannot be closed from inside its own
  table; what this fire shows is that the *prose beside it* can be, by an identity between two artifacts — which
  is a different check in a different place, and is why both are now recorded.
