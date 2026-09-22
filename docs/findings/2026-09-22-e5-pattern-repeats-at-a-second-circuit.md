# E45 — `e5`'s association at two circuit sizes: the pooled verdict flips, and the "one seed carries it" pattern repeats

**Date:** 2026-09-22
**Script:** `experiments/e45_e5_seed_pattern_across_circuits.py`
**Artifacts:** `runs/e45_e5_seed_pattern.json`, `runs/e37_kappa_real_cs800.json`, `runs/e5_anisotropy.json`
**Context:** `2026-09-22-e5-does-not-reproduce-its-own-artifact.md` (§4), `2026-09-22-e5-replication.md` (`e43`)

---

## 1. The escape route this closes

`e41` found that the project's most-quoted direction — *more anisotropy gives a larger gap* — is
carried by **one seed of three** at cs = 800. That leaves the obvious escape: maybe those three seeds
were an unlucky draw of the *tasks*, and the association is fine.

It is testable, because `e37` ran `e5`'s manipulation at **cs = 300 as well**, with the same three
seeds, the same seven `kappa` values, and an independent task draw. Two circuit sizes, two
independent sets of tasks, one manipulation. Both are the `real` topology, so `--topology real` is a
no-op and the comparison is exactly `e5` at each size.

## 2. The two draws disagree about the pooled statistic, and agree about everything else

Per-seed `Spearman(flattening, gap_EWC)`, each seed being a complete repeat of the sweep:

| draw | seed 0 | seed 1 | seed 2 | **pooled** | |
|---|---|---|---|---|---|
| **cs = 800** (d = 1307) | **−0.964** (p = 0.0005) | −0.321 (p = 0.48) | **+0.107** (p = 0.82) | **−0.282 (p = 0.216)** | **null** |
| **cs = 300** (d = 952) | −0.321 (p = 0.48) | **−0.893** (p = 0.0068) | **+0.500** (p = 0.67, n = 4 of 7) | **−0.507 (p = 0.032)** | **SIGNIFICANT** |

Two things, and they point in opposite directions for anyone hoping to rescue the claim:

- **The pooled verdict flips.** At cs = 800 the pooled association does not reach significance
  (p = 0.216); at cs = 300 it does (p = 0.032). So the *significance* of "more anisotropy, larger
  gap" is not a property of the manipulation — it is a property of which circuit you draw the tasks
  from. That is `e12`'s control-draw lesson reappearing on the task draw rather than the control
  draw, and it means neither the significant nor the null verdict can be quoted as the result.
- **The shape repeats exactly.** In each draw, precisely one seed shows a strong association
  (ρ < −0.8) and precisely one has the *opposite* sign — **+0.107 at cs = 800, +0.500 at cs = 300**,
  on different tasks and a different circuit. One strong, one weak-negative, one positive, twice.

So the honest model is that the association is a **per-seed event that occurs in a minority of
seeds**, not a uniform property of the manipulation with noise on top. Under that reading the two
draws are consistent with each other (2 strong-seed hits in 6 seeds) *and* with the pooled statistic
being unstable in sign of significance — which is what a mixture produces when you average it.

I would not push further than that: six seeds is enough to say the pattern repeats and not enough to
estimate the mixing weight.

## 3. The `e37` artifact also closes two open questions from last fire

`e37_kappa_real_cs800.json` has landed, and it is the same configuration as `e5`, so it settles two
things at the JSON level rather than the log level:

- **`e43`'s conclusion is confirmed on the artifact, not just the log.** Its 21 points are
  bit-identical to `e5_anisotropy.json`, so the artifact is the live output of the current code and
  the published table's discrepant cells are the stale thing.
- **The `excess_ewc` field added last fire is consistent with the derived column.** `e37`'s run
  stored `excess_ewc` directly, having been launched after that change, and it agrees exactly with
  `gap_ewc x oracle_final` recovered from `e5_anisotropy.json`: per-seed **−0.929, +0.214, +0.071**,
  pooled **+0.040 (p = 0.862)** from both routes. So the prescribed absolute metric can be trusted
  whether it was stored or derived — which matters because `e41`'s headline negative result rests on
  exactly that column.

Note what the absolute metric does here: it does **not** rescue the association at either size. At
cs = 800 the pooled absolute ρ is **+0.040 (p = 0.86)** — the sign even flips relative to the
relative-gap value of −0.282. cs = 300's absolute column needs its JSON, which is why §2 quotes the
relative gap there.

## 4. Where this leaves `e5`

| statement | status |
|---|---|
| "Spearman(flattening, gap) = −0.75" | not in the artifact (`e41`), and the artifact is the live one (`e43`, now confirmed in JSON by `e37`) |
| "the gap dips to a minimum at `kappa ≈ 0.5` … an easy middle regime" | **withdrawn** — one substituted cell (`e41` §3) |
| "more anisotropy gives a larger gap" | **supported in a minority of seeds and unstable in pooled significance across circuit size**; at cs = 800 pooled p = 0.216 and under the prescribed metric +0.040 (p = 0.86) |
| "`e5` corrects `e2`'s confounded trend" | **cannot carry that weight as it stands** |

The direction may well be right — in both draws one seed shows it at ρ ≈ −0.9 — but a correction
resting on one of three realised sweeps is itself a single-draw result, and this is the fifth place
in the project where that has been the failure mode. `e42` (12 seeds of `e5`'s configuration, in
flight) is the experiment that can put a number on the mixing weight instead of a pattern.

## 5. Limits

- **cs = 300's seed 2 is incomplete** — 4 of its 7 `kappa` points at the time of writing — so its
  per-seed ρ (+0.500) and the pooled −0.507 (p = 0.032) will move when it finishes. The *shape*
  (one strong negative, one positive) is already determined by seeds 0 and 1 and does not depend on
  that seed.
- **The two draws differ in two ways at once** — circuit size *and* task draw — so "the verdict flips
  with the draw" is the supported statement, not "it flips with circuit size". They are the same
  operation here (`circuits.extract(max_neurons=...)` changes the subsample and the tasks together),
  which is itself the confound `e2`'s line has been chasing all along.
- **n = 3 seeds per draw.** Six seeds total is enough to say the pattern repeats; it is not enough to
  estimate how often it occurs.
- The log route cannot compute the absolute excess, because `e5`'s progress line does not print
  `oracle_final`. That is why §2's cs = 300 row is the relative gap only, and it is a gap in the
  *script*, not in the data — the JSON will carry it.
