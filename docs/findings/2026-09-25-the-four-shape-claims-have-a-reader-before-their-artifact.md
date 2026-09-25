# The four shape claims have a reader before their artifact — and its first version read S1's null off the wrong quantity

**Date:** 2026-09-25
**A tool unit, done while `e193`'s last level runs.** S1-S4 were registered in the plan's row for `e193` with their
bars; the verdict on them was going to be an ad-hoc python snippet inside a shell task. That is the same defect the
per-term progress fraction and rule 42's footer were added to two readers today to remove — a registered claim whose
read is a hand computation is a claim whose read is not versioned, not tested, and not reproducible by a reader of
the repo. `experiments/e194_s_claims_read.py` now holds the four claims and prints their verdicts.

---

## 1. The claims as data, and the reader as the thing that judges them

Each claim is one row: an id, the **achieved** overlap it is stated at, the quantity, its comparison, its bar, its
falsifier, its null if it named one, and the sentence's meaning.

| | quantity | bar | falsifier |
|---|---|---|---|
| **S1** | distant-pair progress minus adjacent-pair progress, points | **≥ 40** | < 15 |
| **S2** | adjacent-pair progress, % of its own 0 → 1 change | **< 50** | ≥ 50 |
| **S3** | network far progress minus `e7`'s far progress, points | **≥ 15** | ≤ 0 |
| **S4** | accuracy progress, % of its own 0 → 1 change | **< 176.6** | ≥ 176.6 |

All four are stated at **achieved 0.6000**, the last intermediate level, and the table asserts that rather than
leaving it to the eye. Nothing is stated at a target overlap: the x-axis is measured first, so a claim written at a
target would move if the circuit or the seed set changed.

**It is deliberately not in the gate list yet.** It exits 1 while any claim is refused, which is the correct
behaviour before the artifact and a red gate if it were run now — so it joins the gate list at the same moment the
artifact lands, and until then its contract is the pytest tests rather than the suite.

The verdict is the registrations' own three-valued one, in their own order — bar, then falsifier, then the null —
and a measurement that clears neither is reported as **between the bar and the falsifier** rather than forced into
one. Each row also prints the extrapolation its registration wrote down before the run (S2's 30.8% and 22.6%, S3's
52.16%), so that a verdict is read against what was predicted and not against a remembered figure.

## 2. What it refuses, and why the refusals are the point

Written before its artifact, the reader's important case is the one where there is nothing to judge. A claim whose
level has not landed prints `REFUSED -- no measured progress at achieved 0.6`; a claim whose quantity is absent —
the penalised arms are refused a `progress_fraction` by both dose readers, because their admitted baseline is itself
at overlap 1.0 — prints the reason, and the count of refusals is the exit code. Measured today on the three
registered levels, all four refuse:

```
S1: REFUSED -- no measured progress at achieved 0.6
S2: REFUSED -- no measured progress at achieved 0.6
S3: REFUSED -- no measured progress at achieved 0.6
S4: REFUSED -- no measured progress at achieved 0.6
```

## 3. The defect it caught in itself, which no live print would have shown

**S1's null is "*both* between 30% and 60%" — a statement about each term, not about their difference.** The first
version carried the band as a pair of numbers and applied it to whatever quantity the claim named, which for S1 is
`far − near`. So a level with the two terms at 10% and 45% (difference 35, inside the band, one term far outside it)
would have been reported as *the registered null*.

**No live print could have shown this**, because at the only level that currently has values S1 is decided by its bar
(62.13 ≥ 40 → MET) and the null branch is never reached. It was caught by constructing the case, which is what the
test does: the band is now checked against the keys the registration *names*.

This is the fifth instance today of one class — a quantity read in the wrong window, direction or subject prints a
plausible number — and the third that a test caught rather than a run:
`docs/findings/2026-09-25-p2s-bar-is-60-percent-and-the-read-applied-46.md` (the bar's sentence, and a denominator
that was a λ difference), and
`docs/findings/2026-09-25-the-accuracy-accounts-interior-overshoots-its-own-endpoint.md` (an inverted sign
convention, caught by a synthetic test with a known answer).

## 4. One check that a green reader is not a correct one

A key spelled wrongly in the table would make **every** verdict a refusal, and a refusal is a plausible-looking
output — four `REFUSED` lines look like an artifact that has not landed rather than like a typo. So a test asserts
that the keys the table names are the keys `measure()` produces, on the midpoint artifact, where they exist.

## 5. What this does not license

- **That the four claims will be decidable at 0.6000.** They are registered with bars that the two measured levels
  make plausible, and S1 and S3 are large at the midpoint (62.13 and 65.60 points against bars of 40 and 15), while
  S2 is 20.0% against a 50% bar and S4 is 176.6% against its own value — so S2 and S4 are the ones the last level
  can plausibly move. The reader prints which; it does not predict.
- **That a MET here would be a mechanism.** All four are shape statements about one configuration — `mb+cx+al@n1307`,
  three tasks of eighty neurons, seed 0, 40 replicates — and the achieved-overlap table is a property of that
  circuit.
- **That the refusal count means "not yet".** A refusal is also what a broken arm or a renamed constant produces,
  which is why §4's key check exists and why the reason is printed rather than just the verdict.
