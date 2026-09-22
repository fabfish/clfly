# E55 — the "differences below ~0.05 are not resolvable" figure is stale, and it is not the figure that matters

**Date:** 2026-09-22
**Script:** `experiments/e55_seed_resolution_of_excess.py`
**Artifacts:** `runs/e55_seed_resolution.json`, `runs/e42_e5_reseed.json`, `runs/e48_cs800_perseed.json`
**Context:** plan rule 3, `2026-09-22-cs800-column-reproduced-and-paired.md` (`e48`), `e42`

---

## 1. What rule 3 says, and the two halves of it

Plan rule 3 prescribes the **absolute** excess over the oracle instead of the relative gap, because
the relative gap "has a standard deviation comparable to its own mean", and closes with *"at current
settings, excess differences below ~0.05 are not resolvable."* Both halves were written from a few
seeds. `e42` supplies **twelve** of one configuration (cs = 800, `real`, seven `kappa`), so both can be
measured.

## 2. The absolute metric does **not** fix the spread — only the ratio

| κ | absolute excess: mean / sd / **CV** | relative gap: mean / sd / **CV** |
|---|---|---|
| 0 | 0.02164 / 0.02185 / **1.01** | 0.403 / 0.401 / **1.00** |
| 0.5 | 0.01676 / 0.01171 / **0.70** | 0.324 / 0.236 / **0.73** |
| 1.75 | 0.02037 / 0.02569 / **1.26** | 0.465 / 0.535 / **1.15** |
| 4 | 0.00793 / 0.00901 / **1.14** | 0.515 / 0.581 / **1.13** |

Across κ the absolute metric's CV runs **0.70–1.26** and the relative gap's **0.73–1.15**. **They are
the same.** So rule 3's stated reason — that the relative gap's sd is comparable to its own mean —
is true but not *diagnostic*: the absolute excess behaves the same way at twelve seeds.

What the absolute metric actually fixes is the **ratio-of-two-small-close-numbers pathology**: the
inflation of the relative gap's error by the EWC estimator (the ±0.04 under a 1-ULP change in the
spectral radius, and the 1.38 maximum CV). It does not reduce the across-seed spread, and rule 3
should say which of the two problems it is solving. A reader who takes "prefer the absolute excess" as
"the absolute excess is more stable across seeds" is wrong by a factor of one.

## 3. The 0.05 is stale by 3×, and it is the wrong *kind* of number

The across-seed sd of the absolute excess in `e42`'s sweep has a median over κ of **0.01971** (range
0.00901–0.02569). The unpaired minimum detectable difference — 2.8 × sem, i.e. 80% power at a
two-sided 5% test — is then:

| n seeds | sem | min detectable |
|---|---|---|
| 3 | 0.01138 | **0.0319** |
| 6 | 0.00805 | 0.0225 |
| **12** | 0.00569 | **0.0159** |
| 24 | 0.00402 | 0.0113 |
| 48 | 0.00284 | 0.0080 |

So at n = 12 the figure is **0.0159** — 3.1× smaller than the plan's ~0.05 — and even at n = 3 it is
0.0319, 1.6× smaller. The plan's number was conservative at every n it could have been quoted at.

**But that is not the number the project's claims rest on.** Everything above is the *unpaired*
resolution: two arms whose seeds are independent. The project's contrasts are **within-seed
differences**. Measuring both on `e48` at cs = 800:

| quantity | value |
|---|---|
| per-seed sd of `swap0.5` and `swap2` | 0.00083 and 0.00062 |
| per-seed sd of their **difference** | **0.00088** |
| arm correlation recovered from those three | **r = +0.29** |
| min detectable, arms treated independently | 0.00118 |
| min detectable, as a within-seed difference | **0.00100** |

So for this contrast the two differ by only **1.2×** — and **pairing is not the reason the contrast
resolves**, since the arms correlate at r = +0.29 and cancelling is minimal. The reason is that the
difference is a stable quantity *relative to the signal*: 0.01032 against a 0.00036 sem is 29σ, while
either arm alone is comparable to its own mean.

**Which is why a single figure cannot do this job.** The basis deltas the neuron ladder resolves are
0.0015–0.0040; against the unpaired figure of 0.0159 they would look unmeasurable, and against the
within-seed figure of 0.0010 they are comfortably resolved. Rule 3 needs a pair, with the comparison
named.

## 4. And a third number, which argues against quoting any single figure at all

**The same topology's across-seed spread depends on the drive construction by an order of magnitude.**
`excess(real)` at cs = 800 has an across-seed sd of **0.01971** in `e42`'s sweep (uniform drive at
κ = 0) and **0.00175** in `e48`'s run, which uses `e2`'s default drive. Both are `real` at cs = 800,
same topology, same circuit, six-or-more seeds; what differs is the task construction. So a resolution
figure is only meaningful with its configuration attached, and rule 3's *"at current settings"* is
doing more work than it looks — it covers a 11× range.

## 5. What rule 3 should say

1. prefer the absolute excess, **because the relative gap is a ratio of two small close numbers** and
   inherits the EWC estimator's full relative error — not because the absolute metric is more stable
   across seeds, since its CV is also ~1.0 (0.70–1.26 at n = 12);
2. report **across-seed sems**, and expect a CV near 1, so that a single-draw excess is not a
   measurement;
3. give the resolution as a **pair**: unpaired ≈ 0.016 at n = 12 (0.032 at n = 3) for the sweep
   configuration, and within-seed differences an order of magnitude finer, which is what the
   project's contrasts use;
4. attach the configuration, because the same topology's spread moves 11× with the drive.

## 6. Limits

- **One configuration has n = 12.** The unpaired resolution is measured on `real`/cs = 800/`e42`; the
  within-seed example is `swap0.5 → swap2` at the same circuit. §4 shows these are not transferable,
  which is the point, but it also means the quoted numbers are not general.
- **2.8 × sem is a convention**, not a law: it is 80% power at a two-sided α = 0.05. A different
  convention moves every figure in §3 proportionally.
- **The CV estimate itself has n = 12 per κ.** A CV of 1.01 at n = 12 has a wide interval; the claim
  in §2 is that the two metrics' CVs are *indistinguishable*, not that either is exactly 1.
- **e42's κ = 0 is a uniform drive**, which is not `e2`'s default; the 11× spread difference in §4
  confounds the drive with whatever else `e5` and `e2` construct differently. It is evidence that
  configuration matters, not a decomposition of why.
