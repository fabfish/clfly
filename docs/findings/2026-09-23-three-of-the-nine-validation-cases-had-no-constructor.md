# Three of the nine validation cases had no constructor

**Date:** 2026-09-23
**Script:** `clfly/lgcl/model.py` (`sample_partial` gained `drifted`); `tests/test_analytic.py` (three new
cases and a constructor guard).
**Context:** `docs/findings/2026-09-22-analytic-expected-error.md` §2 — the nine-row table behind the paper's
§6 claim that the exact estimator was "validated against Monte Carlo on nine configurations"; and
`docs/findings/2026-09-23-the-last-two-unaudited-sections-were-clean.md`, which listed that claim as the last
honest-but-unverified item.

---

## 1. The claim, and the gap under it

The paper's §6 and its source finding both state the validation as **nine configurations**. The finding's
table has exactly nine rows, in three families:

| family | bases | constructible before this fire |
|---|---|---|
| full-rank, drifting (`sample_full`) | kalman, EWC-diag, rank4 | **yes** — the `drifting` fixture |
| **rank-8, drifting** | kalman, EWC-diag, rank4 | **no constructor existed** |
| rank-8, non-drifting (`sample_partial`) | kalman, EWC-diag, rank4 | yes — the `partial` fixture |

`sample_partial` has hardcoded `drifted=False` since the repository's first commit (`d8fb966`), and
`git log -S` shows its signature never carried a drift option. So **the middle family could not be built by
any code in the repository**, and the *repeatable* check — the Monte Carlo tests in `tests/test_analytic.py` —
covered **five of the nine**: two fixtures × three and two bases.

**And the parameters were not recoverable from the record either.** The finding's §2 states d = 20, T = 5 and
4000 draws, but neither `q` nor the seed for the rank-deficient families — and the two families use
*different* `q` (0.02 for non-drifting, **0.05** for drifting, both at seed 1). Six combinations had to be
tried to find that, which is a search rather than a citation.

## 2. The restoration, and that it is exact

`sample_partial` gained `drifted: bool = False`, built by appending the walk to its own loop rather than
routing through `simulate` — which cannot be used here, because it takes a Cholesky of `J⁻¹` and `J` is
rank-deficient by construction. With the default the function is **bit-identical to what it produced before
the argument existed**: one `theta`, the same values in the same order, and no extra random numbers consumed.

With `drifted=True` at `q = 0.05`, seed 1, `obs_dim = 8`, the three previously-unbuildable rows reproduce the
finding's table **exactly**, to five decimal places:

| basis | finding's "rank-8, drifting" | reconstructed |
|---|---|---|
| kalman | 0.48689 | **0.48689** |
| EWC-diag | 0.92463 | **0.92463** |
| rank4 | 0.77275 | **0.77275** |

And the non-drifting family reproduces at the default: 0.12334 / 0.44014 / 0.29184, again exactly. So the
table is right, its parameters are now named, and **all nine cases are runnable**.

`tests/test_analytic.py` gains the `partial_drifting` fixture and the three Monte Carlo cases, so the
repeatable check goes from five of nine to **nine of nine** — and a guard test that builds each of the nine
`(family, basis)` pairs, which fails if a sampler stops offering one of them.

## 3. The generalisation, which is this week's lesson again

**A validation table is reproducible only if each row's *inputs* can still be built.** Everything the project
has audited this week — artifact existence, config agreement, status words, correction propagation — checks
whether a *number* can be traced. None of them asks whether the *construction* behind a number still exists.
Here the numbers were right, the sources were right, the finding was right, and the table could not be
re-produced because a sampler had been written without the option that generated three of its rows.

**The guard has to be on the constructors, not on the record**, which is what the new test does: it does not
compare numbers, it asserts that nine `(family, basis)` pairs can be *made*. That is a different check from
any the project has, and it is cheap because a constructor either exists or does not.

**And a smaller item from the same section, now measured rather than quoted.** §6 says response matrices were
"separately verified against finite differences to **1e-9**". Measured now over six `(fixture, basis)` pairs:
the drifting fixture agrees to **1.4e-9** and the rank-deficient one to **9.3e-9 – 1.2e-8**, so the figure is
right for the family it was measured on and an order optimistic for the other. The test asserting it uses
`atol=1e-5`, which is a tolerance and not the achieved agreement — the two were conflated in the prose.
