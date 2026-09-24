# Rule 43 applied to the paper's rank correlations: one is compliant, one is not, and the record can supply half of what is missing

**Date:** 2026-09-24
**Script:** none — a read of the paper's rank statistics against the artifacts behind them, prompted by rule 43,
which was written this session and says a rank correlation must be printed with the count of its inputs resolved
from zero and with a leave-one-out range.
**Artifacts:** `runs/e7_interference.json` (cs 800, support 80, **3 seeds**), `runs/e23_e7_permcheck.json`
(cs 300, support 30, **3 seeds**), `runs/e6_predictor.json`, `runs/e64_predictor_6_perseed.json`.

---

## 1. What the paper's rank correlations carry

| the paper's rank claim | does it print its inputs' resolution? |
|---|---|
| §5's **predictor table** — five out-of-sample conditions, ρ from +0.973 to +0.991 | **yes**: the table has a **"resolvable pairs"** column (5/5, 5/5, 5/5, 4/4, 5/5) — rule 43's spirit, implemented before the rule existed |
| §5's in-sample **+0.991 over 11 candidate bases** | the bases' sems come from the 18-seed artifacts behind §4.3, which carry draw sds; not re-derived here |
| §4.6's **ρ = +0.939** (the propagated representation predicts interference) | **no**: it carries a **leave-one-out range** ([+0.917, +0.983]) — the *"does one pair carry it"* half — and **nothing about the ten pairs' own resolutions** |
| §4.6's `Spearman(overlap, interference) = −1.000` over three groups | n = 3, quoted as "perfectly monotone" rather than as a coefficient |
| §4.3/§4.3-ladder, §4.2's ρ = 0.9987 identities | instrument checks (the same object to four decimals), not orderings |
| the ten-cell ordering test (`e156`) | **yes**, since this session: ρ printed with the two second-order forms it was built to discredit, and rule 43 now requires it |

## 2. The one that is not compliant, and what the record can and cannot supply

**`e7` computed the ten pairs' alignment, propagation and interference values at three seeds and recorded only
the means** — no per-pair sem, and no other artifact in `runs/` carries per-seed pair interference for the
analytic line. **So §4.6's ρ cannot be certified by rule 43 from the record**, and that is a gap in the record
rather than in the claim: the fix is three more seeds per pair or a per-pair sem, neither of which exists.

**What the record *can* supply, and never has, is a second configuration.** The same ten-pair table was computed
at cs 300 with support 30:

| configuration | pairs | ρ (propagation vs interference) | leave-one-out range |
|---|---|---|---|
| cs 800, support 80 (`e7`) | 10 | **+0.9394** ← the paper's number | 0.067 |
| cs 300, support 30 (`e23`) | 10 | **+0.9758** | 0.017 |

**And the per-pair orderings behind them agree at ρ = +0.867** — for the propagation values and, independently,
for the interference values (both +0.867 over the same ten pairs), i.e. the two configurations rank the pairs the
same way for two different quantities. **So the coefficient is configuration-robust across the two realizations
the record holds, and its inputs' *seed* resolution is the half that is missing.**

## 3. What this says about rule 43 rather than about the claim

**The audit's outcome is that the rule bites exactly where a rank correlation is a headline and not where it is
an instrument check.** §5's predictor results — the paper's most load-bearing rank statistics — were already
carrying their resolvable-pair counts, which is why the rule's *content* was available before its *statement*; the
§4.6 mechanism ρ carries the robustness check that its own finding needed (a leave-one-out range) and not the one
a rule written later asks for. **That is the ordinary asymmetry of retrospective rules, and the honest response is
to say which claim is uncertified and what would certify it, not to re-derive every ρ in the paper.**

**One claim is therefore now marked**: §4.6's ρ = +0.939 is a three-seed ten-pair statistic whose inputs'
resolutions are not in the record, and it is configuration-robust across the two realizations that exist. Both
sentences now stand in §4.6.

## 4. What this cannot settle

- **It does not check every ρ in the paper**, and it says so by table: the ones it did not re-derive are the ones
  whose inputs are themselves summary statistics of sampled quantities (the §5 in-sample ρ, the §4.3 ladder's
  ranks), where the resolution question has to be posed at the level of the sampled quantity and not the rank.
- **"Configuration-robust across two realizations" is not "resolved across seeds"**: the two configurations differ
  in circuit size *and* support, so their agreement is evidence about the ordering's stability to the substrate and
  not about a three-seed mean's own error bar.
- And the permutation test `e23` reports (p = 0.0165 over task labelings) answers a third question — could the
  ordering arise from the task structure — which is neither of the two rule 43 asks for.
