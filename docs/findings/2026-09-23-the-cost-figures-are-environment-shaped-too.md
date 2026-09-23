# The cost figures are environment-shaped too, by 2.2×

**Date:** 2026-09-23
**Method:** the analytic estimator timed at d = 1307 with its two components separated, uncontended, at two
thread counts.
**Context:** the paper's §6 ("~6 s per basis") and §9, which documents the *values'* dependence on
`OMP_NUM_THREADS` and says nothing about the *costs'*.

---

## 1. The measurement

| component, d = 1307, T = 5 | `OMP_NUM_THREADS=4` | `=1` | ratio |
|---|---|---|---|
| `expected_error_matrix` (one basis) | **6.08 s** | **13.13 s** | 2.16× |
| `expected_oracle` | 6.10 s | 13.15 s | 2.16× |
| `analytic_excess` (both) | 12.18 s | 26.28 s | 2.16× |
| circuit + task setup | 3.2 s | 4.4 s | 1.38× |

So §6's "**~6 s per basis**" is **exactly right at four threads** and **2.2× optimistic at one**, and the two
components cost the same as each other — they are the same computation one basis apart, which is why
`analytic_excess` is 12.2 s and not 6 s. My own earlier reading of 14.76 s per call was this quantity under
three-way contention, so the figure is reproducible in both directions once the environment is named.

## 2. Why this belongs to §9 rather than to §6

§9 already says the paper's numbers are environment-shaped and quantifies it for the *analytic values* —
fourth significant digit, 40× below the tightest sem. **It does not extend that to the timings**, and the
timings are the one class of figure in this paper whose dependence is not in the fourth digit but in the
**first**: 6.1 against 13.1 is a factor a reader would notice, and there are five cost figures in the paper
(§3.3's "152 GB and 2.6e15 flops" is arithmetic and safe; §3.1's mean out-degree is a property of the data;
but §6's per-basis cost, §7's "7× per run" and §4.5's "24.3 → 6.0 minutes of penalty calls" are measurements
of a machine). *This passage also attributed "0.2–6 hours depending on the rung" to §4.7, which was wrong:
**the paper contains no timing in hours at all**, and that figure lives in the plan's C2b and in the
network-variance finding — where it has since been corrected to **0.9–12 hours**, because the four completed
rung runs cost 5.12–22.86 minutes per arm-replicate and the excluded one was the expensive rung
(`docs/findings/2026-09-23-the-cost-range-excluded-the-expensive-rung.md`).*

**So the rule is the one §9 already applies to values, applied to costs: quote a cost beside the environment
it was measured in.** §6 now carries both endpoints instead of one bare figure, and §9 gains the sentence
alongside its values paragraph.

## 3. What this is an instance of

It is the **third** figure this week whose problem was not that it was wrong but that **it was unqualified**:
the `+45–63%` range was two statistics, the `7×` was right for a reason that cannot produce it (O(d³) predicts
2.95×), and `~6 s` is right on one machine and 2.2× off on another. In each case the number had been measured,
the measurement was recorded, and the *conditions* were dropped between the measurement and the sentence.

**And in each case the fix is the same shape**: name the thing the number depends on — the estimator, the
derivation, the thread count — rather than adjusting the number. A corrected figure would have gone stale
again on the next machine; a qualified one does not.


---

## 4. Which of those five cost figures are *derivations* and which are bare measurements

Following the rule above by checking each one's inputs turns a list into a checked list, and the five split cleanly:

| figure | kind | its inputs | verified |
|---|---|---|---|
| §3.3's 152 GB, 2.6e15 flops | arithmetic | `d` | **yes** — 138,113² × 8 bytes and 138,113³ flops |
| §3.1's mean out-degree 108.9 | a property of the data | the connectome | **yes**, to the digit |
| §6's ~6 s per basis | a measurement | the machine | **yes at four threads, 2.2x off at one** |
| §7's 7× per run | a measurement | the machine | **yes, 8.3x measured** — but its stated *reason* (O(d³)) predicts 2.95× and so cannot produce it |
| §4.5's 24.3 → 6.0 minutes | **a derivation** | **4,500 calls × two measured per-step costs** | **yes, exactly**: 4,500 × 0.3247 s = 24.36 min and × 0.0805 s = 6.04 min, with the speedup 4.0× matching 0.3247/0.0805 = 4.03 |

**So only one of the five is a derivation, and it is the only one whose inputs were already stated** — the 4,500-call run is in the finding's table header. What the *paper* dropped was the unit: §4.7 said "takes the coarsest rung from 24.3 to 6.0 minutes of penalty calls" and nothing about the call count, leaving a reader unable to distinguish a per-step cost from a per-run total. It now carries both, and the one cross-check available — `runs/e44_penalty_cost_scaling.json` measures **53.5 ms** per step for `side` against the finding's 80.5 ms — differs by **1.5×**, which is inside this paper's own 2.2× environment band rather than outside it.

**And the general form of the rule is now visible in all five**: the figures that are *derivations* need their inputs named, the figures that are *measurements* need their environment named, and the figures that are *arithmetic* need neither. Only the third kind was safe by construction.
