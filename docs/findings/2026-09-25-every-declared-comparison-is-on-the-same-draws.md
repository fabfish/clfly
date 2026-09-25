# Every comparison the corpus declares is measured on the same draws — and that is a different defect from the one the axis had

**Date:** 2026-09-25
**Analysis only, no runs.** Today's work left three things in place: the substrate makes at least two RNG draws per run
(the overlap suite's **supports** and the **read-out subset**); two support draws move the learning quantities by
3.3–6.6σ on identical configurations and identical seeds; and `e198 --reconstruct` identifies the draw of **264 of the
299** live (artifact, draw) pairs at zero cost. Together they make one question answerable for the corpus as it
stands: **for every comparison the corpus declares, do both sides draw the same thing?** `e200` asks it over the ten
declared two-point contrasts and the four dose families.

---

## 1. The audit needed two semantic corrections before its answer meant anything

**It compared fingerprints first, and flagged 19 of 19 pairs.** Every one of them was wrong, and the reason is the
finding: **a fingerprint bundles the draw with the manipulation.** `e116` is at target overlap 0.0 and an `e193` level
at 0.50, so their supports *necessarily* differ — the overlap **is** the support construction — while both used
support draw 0. The right test is the **draw key**, `(seed, n, size)`, which for the supports does not contain the
overlap; the fingerprints are then printed beside the verdict as evidence rather than used as it.

**A draw live on one side only is not a confound.** The read-out draw exists only for a subset — `0` is the runner's
"whole state" — so a pair with one subset-read-out side and one whole-state side has no second draw to compare, and
calling that a difference would be the same false alarm pointing the other way. It is reported as *live on one side
only*.

**And the draw-varying families were silently absent.** `e195`/`e197`/`e199`'s levels are **correctly refused** against
draw 0's baselines, because `support_seed` is not an inert field — so with only the draw-0 baselines offered as
candidates the audit produced no pairs for them at all, and **an absent pair reads like a clean one**. Offering each
family's own endpoints first brought them in: the audit went from 19 pairs to **27**.

## 2. The answer

| | pairs |
|---|---|
| **SAME DRAW** | **27** |
| CONFOUNDED (a draw differs) | **0** |
| partly unidentified (a draw live on one side only) | 0 |
| read-out draw confounded | 0 |
| support draw confounded | 0 |

**Every comparison the corpus declares or reads is measured on the same draws** — the ten two-point contrasts
(`e116`/`e125`/`e140` against `e142`/`e144`/`e148`/`e153`, and the frozen-bias and rand-draw pairs) and all four dose
families' level-against-baseline comparisons, including each varying family's own within-family pairs.

## 3. The distinction this makes, which is the point

**A confounded comparison and a single-draw family are different defects, and only one of them is in this corpus.**

- A **confounded comparison** measures the manipulation *and* a draw difference at once, so the contrast cannot be
  attributed. `e200` checks for it, and there is none.
- A **single-draw family** measures each configuration once, so the effect is attributable *within* the family but its
  *generalization* beyond that draw is untested. That is what the axis had: every one of its claims was measured at
  support draw 0 and read as a property of the overlap, and the replication's job was to vary what `e200` cannot see.

**`e200` cannot see the second defect at all** — a family with one artifact per configuration passes it trivially,
which is exactly what the axis did for eleven hours. So the two instruments are complements and neither replaces the
other: `e200` is a *cross-artifact* check that runs on the corpus as it stands, and rule 53's "measure each draw's own
effect" is a *design* instruction for a family whose claims will be generalized. A reader who ran only `e200` would
have concluded the axis was clean.

## 4. What this does not license

- **That the corpus is draw-clean.** It says the *declared comparisons* do not differ in a draw. A comparison nobody
  declared, or one whose draws are unidentified (35 pairs after reconstruction), is not covered.
- **That a same-draw comparison is a good comparison.** Draw agreement is one requirement among the corpus's others —
  inert-field admission, replicate counts, the matched-budget rule — and `e200` checks only this one.
- **That the read-out draw's agreement matters as much as the supports'.** It is checked and it agrees everywhere;
  it is also the draw measured to move nothing it has been tried on, so its agreement is cheap.
- **That a family measured at one draw is broken.** Its within-family effects are what they are; what is unavailable
  is quoting them as properties of the manipulation rather than of the draw.
