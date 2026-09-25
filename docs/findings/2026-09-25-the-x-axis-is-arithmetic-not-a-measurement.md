# The overlap axis is arithmetic, not a measurement of the circuit — and the registration said a reader must recompute it

**Date:** 2026-09-25
**A cheap unit on existing code, no runs.** `ACHIEVED_OVERLAP` — the table that converts a target `--input-overlap`
into the Jaccard overlap the reads put on their x-axis — carried this comment in `e191` and in `e188`:

> What a TARGET `--input-overlap` achieves as a Jaccard overlap, on `mb+cx+al@n1307` with three tasks of 80 neurons
> at seed 0 ... The table is a property of the circuit, the support and the seed and NOT of the annotation: **a
> reader re-running this on a different circuit must recompute it.**

and the registration's own §5 named it as one of the things that "would make this registration wrong rather than
merely refuted":

> **The achieved overlaps could move** if the circuit's seed set changes between now and the runs: §2's table is a
> property of `mb+cx+al@n1307` at seed 0, and a different circuit changes every cell.

**Neither is true, and the check takes one line of arithmetic rather than a run.**

---

## 1. The construction is exact, so the table is a formula

`overlap_controlled_supports` builds `T` supports as a shared pool `P` plus disjoint private complements:
`A_k = P ∪ priv_k` with `|P| = round(overlap · size)`. So `|A_j ∩ A_k| = |P|` **exactly** for every pair, and

```
Jaccard = |A_j ∩ A_k| / |A_j ∪ A_k| = o·s / (s(2 - o)) = o / (2 - o)
```

— independent of `n`, `size`, `T` and `seed`. Measured anyway rather than asserted, on three circuit sizes and three
seeds, for all five targets:

| target | table | `o/(2−o)` | pairwise Jaccard observed (n = 300 / 800 / 5000 × seeds 0, 1, 7) |
|---|---|---|---|
| 0.00 | 0.0000 | 0.000000 | 0.000000 |
| 0.25 | 0.1429 | 0.142857 | **0.142857143**, identical across all nine combinations |
| 0.50 | 0.3333 | 0.333333 | **0.333333333**, identical across all nine |
| 0.75 | 0.6000 | 0.600000 | 0.600000000 |
| 1.00 | 1.0000 | 1.000000 | 1.000000000 |

Every pair's Jaccard is the same value to nine decimals, on every circuit size and every seed. The table's cells are
that formula **rounded to four places**, and the rounding is load-bearing because both reads key their per-level
lookups on it.

## 2. What this changes

1. **No recomputation is needed on another circuit.** The table is valid wherever the construction is feasible
   (`need = shared + T·private ≤ n`); it is not a fact about `mb+cx+al@n1307`. The 3.6-point emphasis the registration
   put on "the same four decimals `e7`'s controlled sweep reports" is also misdirected: that agreement is the **same
   construction evaluated twice**, not two measurements agreeing. The conclusion it was used for — the two lines'
   x-axes are commensurable and need no conversion — survives and is *stronger* by this reading, since arithmetic
   cannot agree approximately.
2. **The axis carries no measurement error.** Nothing in this afternoon's results can be attributed to axis drift, and
   no uncertainty belongs on the x-values.
3. **The real gap is the supports' identity, not their overlap.** Which neurons each task drives depends on the
   circuit, on `size` and on the generator's seed, and **is recorded in no artifact** — so two runs at the same target
   overlap share their *ratio* exactly and share *no neurons*. That is the second half of the registration's bullet,
   and it stands.
4. **The table is now bound to the construction by a test rather than by a comment.** A change to
   `overlap_controlled_supports` — a rejection step, a different call in `make_overlap_suite` — would move the
   x-axis of a multi-hour run silently; the test now fails on three circuit sizes and three seeds if the construction
   stops producing `o/(2−o)`, and asserts that `e191`'s and `e188`'s two copies of the table have not drifted apart.

## 3. Why it was worth stopping for

The claim was in two module comments *and* in the registration, in the "what would make this wrong" section — the
place a reader goes to find the limits. It is a **factual claim about code**, not a prediction, so correcting it does
not touch what was registered: the registrations' P1, P2, S1-S6 and the falsifiers all stand, and none of them depends
on the table being a circuit property. What changes is a reader's task list: instead of recomputing a table they
cannot recompute (the supports are not in the artifact), they can now read it off the formula.

It is also the second defect today whose subject was **not a number but a provenance claim** — the first being four
files naming `e193_r32_overlap{25,50,75}` where the launch wrote `025`/`050`/`075`
(`docs/findings/2026-09-25-the-midpoints-cost-is-a-learning-deficit-not-forgetting.md` §3). Both were found by
checking something the corpus asserted about itself rather than about the experiments.

## 4. What this does not license

- **That the supports are what the construction says.** They are not recorded. A run whose generator seed, support
  size or task count differed from what its `config` says would produce a different support set at the same *target*
  overlap, and this finding cannot see that — which is exactly why §2's third point is the one that matters.
- **That the axis is what the *tasks* feel.** The construction fixes the input populations' overlap; whether two
  tasks are "close" to the network is a statement about the propagated representation, and C4 already says the
  anatomical overlap is not the predictor on the real circuit.
- **Any change to the numbers already read.** The reads printed the achieved value beside each level and keyed their
  lookups on it; the values are unchanged, and this corrects their description and not their use.
