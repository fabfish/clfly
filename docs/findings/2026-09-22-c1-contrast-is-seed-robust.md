# E47 — the C1 contrast is seed-robust: a positive control for the per-seed discipline, and a rule-8 hole on the 32.7σ figure

**Date:** 2026-09-22
**Script:** `experiments/e47_contrast_per_seed_signs.py`
**Artifacts:** `runs/e47_contrast_per_seed_signs.json`, `runs/e21_e2_paired.json`, `runs/e26_size{400,500,600,700}.json`, `runs/e2_analytic.json`
**Context:** `2026-09-22-e5-pattern-repeats-at-a-second-circuit.md` (`e45`), plan rules 8 and 13

---

## 1. Why this is worth doing even though nothing was expected to be wrong

Three fires of per-seed dissection (`e41`, `e45`) have turned on the same finding: in this project a
*pooled* statistic can be carried by one seed of three, and the `e5` anisotropy association was
exactly that. The C1 topology contrasts are pooled over task seeds as well, and the most-quoted of
them — the `swap0.5 -> swap2` contrast at cs = 800, **32.7σ** — carries the whole interference
refutation. So the same question is asked of them, which costs nothing because the per-seed excesses
were stored. It is the positive control the earlier findings lacked: if the discipline overturns
everything, it is not discriminating.

## 2. It does not overturn this: 27 of 27 seeds agree, and no removal flips a sign

| size | n | mean Δ | paired σ | per-seed signs | max seed leverage | drop-one σ | any flip? |
|---|---|---|---|---|---|---|---|
| cs300 | 3 | +0.03525 | +21.83 | `+++` | — (needs ≥3 left) | n/a | no |
| cs400 | 6 | −0.00304 | −4.80 | `------` | 0.58 | [3.9, 5.4] | no |
| cs500 | 6 | +0.01054 | +14.46 | `++++++` | 0.77 | [11.8, 19.4] | no |
| cs600 | 6 | −0.00223 | −4.36 | `------` | 0.68 | [3.6, 5.6] | no |
| cs700 | 6 | −0.00402 | −18.71 | `------` | 0.70 | [15.3, 22.2] | no |
| **cs800** | — | **+0.01079 published** | — | **no per-seed values** | — | — | — |

**Every seed agrees with its contrast's sign, at every size where the test is possible: 27 of 27.**
For the four six-seed sizes the chance of unanimity under a fair coin is 2^(1−6) = 0.031 each, and
cs300's 3/3 is 0.25 — individually weak, jointly not, though they are not independent draws.

**And no single seed does the work.** "Max seed leverage" is the largest change in the mean from
dropping one seed, in units of the all-seeds sem. These sit at **0.58–0.77**, and the scale has a
ceiling worth stating: for a single-outlier contrast leverage is *exactly* 1, because the mean shift
and the sem are both (outlier − bulk)/n. That identity is pinned in the tests — it holds at n = 5 and
n = 6 — so leverage is a **0-to-1 scale on which 1 means "one seed is worth a whole sem on its own"**,
not an unbounded detector. On that scale these five contrasts are comfortably short of it.

For contrast, the same statistics on `e5`'s association (`e45`): signs **not** unanimous — one seed
at ρ = −0.96 and another *opposite* in sign at +0.11 — and the pooled statistic null at both circuit
sizes and under both metrics.

**So the C1 line's two halves have different epistemic status, and the plan should say so.** The
*existence* of the instability — that `excess(swap2)` spans 166% across six circuits while its
controls hold to 10.5% and 24.3%, and that the contrast is unanimous in sign across 27 seeds — is
solid. The *interpretation* (the effective-rank coordinate of `e36`–`e40`) is what failed, on three
independent axes. That distinction has been implicit in the last four findings; `e47` makes it
measured.

## 3. And a real hole, on the headline number

`runs/e2_analytic.json` — the cs = 800 artifact — **stores no `excess_per_seed` for any of its five
topologies.** Every contrast in the sweep has per-seed values except this one, and this one is the
32.7σ figure. So it is the *only* published σ in the family that cannot be re-examined per seed, and
that is also why its paired form was unavailable and its σ was reported unpaired.

Plan rule 8 exists precisely to prevent this — *"store per-seed values: a pooled mean and sem cannot
be re-analysed paired, and re-deriving a two-hour run to recover them is avoidable"* — and the rule
was written after this artifact. The omission is the reason the sweep's most-quoted number is its
least checkable one.

**`e48` is launched to close it**: `e2_topology_gap --circuit-size 800 --seeds 6 --topologies
real,swap0.5,swap2,erdos_renyi --no-realized`, whose `e26`-style output stores per-seed excesses for
every arm. It is cheap (the cs400–700 runs took 40–55 minutes each), it doubles as a reproduction
check the way `e26` did at cs400 and cs500, and it will let the 32.7σ be quoted paired and checked
per seed for the first time.

## 4. `e32` completed: the realization study settles at 5.4×

The sixth and last `swap2` realization landed while this was being written:

| realizations of `excess(swap2)` at cs = 800 | |
|---|---|
| per realization | 0.01255, 0.01350, 0.01503, 0.01940, 0.02030, **0.01101** |
| sample sd (5 df) | **0.00377** |
| ratio to the withdrawn 0.0205 | **5.4×** |
| χ², P(sd this small │ 0.0205) | 0.0189, **p = 0.00059** |
| range | 0.00930 |

The margin has moved 16.3× → 6.8× → 5.9× → **5.4×** as realizations were added, so the withdrawal of
the 0.0205 attribution is settling rather than drifting. The pre-registered criterion was *"if it
moves above ~0.004 the 16× ratio shrinks to 5×"* — it reached 0.00377, just under, giving 5.4×.
**The prediction held, and the conclusion is unchanged at a fivefold margin.** And the effective rank
still fails to order the six realizations (`ρ = +0.943`, not 1.000), so §2's point is untouched.

## 5. Limits

- **Leverage saturates at 1**, so "0.58–0.77 is well short of 1" is a weaker statement than it looks;
  the load-bearing evidence in §2 is the 27/27 sign unanimity and the absence of any drop-one flip.
- **The five usable sizes are not independent**: cs400/cs500/cs600/cs700 share the `e26` run
  structure and the same six seeds, so the four "P = 0.031" figures cannot be multiplied. They are
  four separate task draws of the same manipulation at four circuit sizes, which is what makes them
  worth reporting together and not what makes them independent.
- **cs = 800 is excluded from the whole of §2** for the storage reason in §3, so the most-quoted
  contrast is missing from the positive control until `e48` lands.
- `e37` is part-way through its `swap2` arms; the topology-side intervention is still open and §2 says
  nothing about it.
