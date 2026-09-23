# E89 — the abstract carried six stale or hybrid figures, two of them contradicting the results section

**Date:** 2026-09-23
**Artifact:** `docs/paper/clfly-v1.md`, §Abstract
**Context:** `2026-09-23-the-programme-table-had-drifted.md` (e85, which audited the plan and *then* the paper by grepping for overturned figures), plan rules 21 and 22

---

## 1. Why the abstract, and why the previous audit missed these

`e85`'s audit of the paper worked by **grepping for the figures recent fires had overturned** — "32.7σ",
"13 of 13", "1.1e-3", "bit-for-bit" — and found five sentences that had not been updated. That method is
cheap and it found real errors, but it has two blind spots, and the abstract's audit exposes both:

* **a variant spelling escapes the grep.** Rule 21 withdrew "bit-for-bit" and "bit-identical"; §4.2 was
  written as "**bit-reproducible**", which neither pattern matches. It survived five audits of that phrase.
* **a hybrid range looks locally plausible.** `e85` never looked at "+33–63%", because neither endpoint had
  been overturned — see §3.

The abstract is also the most-read part of the paper and it was edited piecemeal across a dozen fires, with
different fires touching different items. So it is the place a contradiction is most likely to sit
unnoticed. Six were found.

## 2. Two direct contradictions with the results section

**"Seven of our own earlier conclusions were retracted or overturned."** §8's retraction list says
**Thirteen**, and it has said thirteen since the C2b and replay-provenance entries were added. The abstract
and the body disagreed about a count the body enumerates. Fixed to Thirteen, with the section reference.

**Item 3 said "three of the eight rungs still have no measurement of that spread, so the column is a
floor."** That was true when it was written; `e74` measured the last three (`pool8` 7.07e-4, `pool16`
6.68e-4, `pool128` 9.65e-4), and `e73` then put the ladder and the named rungs on one footing. So the
sentence understated the project's own evidence in one clause and overstated it in another (the range was
4.0–13.7σ, now 4.1–13.7σ). Both are corrected, and the abstract now carries the comparison that replaced
the floor: **the ladder's best rung is 13.7σ against the named rungs' 26.1σ**, a factor of 1.9.

## 3. The hybrid range, which is the interesting one

The abstract's first finding read: *"EWC's excess error over the exact Kalman oracle is **+33–63%** on the
connectome against <1% in LGCL's synthetic random-rotation family."*

Neither endpoint is wrong on its own, and that is exactly the problem:

| endpoint | where it comes from | where the paper states it |
|---|---|---|
| **33%** | the analytic measurement at d = 1307 (§4.1: excess 0.0174 against an oracle error of 0.0520) | **§4.1** |
| **63%** | the upper end of an *earlier realization-based* estimate of the same contrast (+45–63%), which appears in `e5`'s finding and in the plan | **nowhere in the paper** |

So the abstract spanned two different measurements of the same physical quantity and presented the width
of that span as the quantity's range. The paper's own body supports **+33–34%** (33% at d = 1307, 34% at
d = 3150, which the body calls scale-stable). The abstract now says +33–34%, §4.1 records where the
earlier +45–63% came from and that the two were once carried side by side, and no result in the paper uses
the mixture.

**This is the failure mode of a summary written by combining numbers rather than by re-deriving them** —
the same mechanism as the plan's drift (`e85`) and as `e84`'s failed fingerprint: a document that inherits
its numbers instead of recomputing them, and inherits them from wherever they were last convenient.

## 4. And two things the abstract had fallen behind on

**The cross-rung contrast.** The network paragraph said the coarse rung `side` "is being re-measured at the
same power". `e60` finished and `e76` restated it: **−0.0191 ± 0.0216 on accuracy and +0.0352 ± 0.0291 on
forgetting**, against a published 3-replicate +0.0718 at 2.13σ — a null on both metrics, with detection
floors of 0.026 / 0.032 / 0.043. The abstract now says so, which strengthens its own negative.

**The two re-measured settings.** `e84` found that neither the task-incremental nor the class-incremental
pool-96 replay arm had an artifact, and that their re-measurements carry the network line's cleanest
numbers: **+0.090 ± 0.008 = 11.87σ** and **+0.042 ± 0.009 = 4.60σ** on accuracy, five of five replicates
positive each. The abstract now carries them — with the caveat that matters, that neither is a *restoration*
because the `naive` fingerprint fails across environments. A reader of the abstract previously saw a claim
about "every setting" supported only by the one setting whose artifact had been recreated.

## 5. Limits

- **The body has not been audited exhaustively.** This pass checked the abstract's figures against the
  body and the body's against artifact-derived findings where they intersected. The body is ~1300 lines of
  prose with numbers in most paragraphs, and the grep-based method's two blind spots apply to it as well.
- **"+33–34%" is now the abstract's range, and the *realization*-based +45–63% is not "wrong"** — it is a
  different estimator's answer on the same contrast. The distinction the paper now makes is which one its
  results use, not which one is true.

  > **Correction (2026-09-23), on that bullet specifically.** The preceding claim was itself too generous:
  > the realization-based estimate is not "a different estimator's answer" but a quantity whose per-seed sd
  > is as large as its own mean, and the `+45–63%` range matched no run at all — its upper end was the mean
  > of per-seed ratios rather than `gap_of_means`, its lower end nothing. The same configuration gives
  > +35.8 ± 13.5% at five seeds and +60.1 ± 43.9% at three. So there is no "45%" answer to be true or
  > false: the realized estimator does not produce values at this seed budget
  > (`docs/findings/2026-09-23-the-realization-range-has-no-artifact.md`). The six stale figures this
  > document corrected are unaffected, and the bullet above is left standing as the record of what was
  > believed when it was written.
- **The correction is to the paper, not to any finding**, so no σ or claim about the substrate moves. The
  two changes that do add evidence (the cross-rung null and the two re-measured settings) were already in
  findings.
