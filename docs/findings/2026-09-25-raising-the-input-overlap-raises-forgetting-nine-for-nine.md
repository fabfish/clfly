# Raising the input overlap raises forgetting — nine comparisons, nine in the same direction, on a two-point axis

**Date:** 2026-09-25
**Read of:** every pair of `runs/*.json` payloads that differ in `input_overlap` and, for the method being compared,
in nothing that method reads; paired by seed through `e151`'s `load_arm` and `paired`.
**Instrument:** `experiments/e188_overlap_contrast.py`, tested in `tests/test_e188_overlap_contrast.py`.
**The suite this is about is the one the corpus mostly ran**: `e187` counted the overlap family at 120 artifacts and
2439 replicates against the assembly suite's 25 and 107.

---

## 1. The question the builder was written to ask, and the answer

`make_overlap_suite`'s docstring states its purpose: *"does raising input overlap raise forgetting?"* — with
`overlap = 0` giving fully disjoint random supports and `overlap = 1` giving every task the same input population,
so the tasks differ only in their class templates. Reading every matched pair in the corpus:

| comparison | method | overlap 0 | overlap 1 | **change (1 − 0)** | σ |
|---|---|---|---|---|---|
| naive, disjoint vs identical inputs | `naive` | +0.0750 | +0.1068 | **+0.0318 ± 0.0106** | **2.99** |
| naive, second overlap-0 arm of the same configuration | `naive` | +0.0750 | +0.1068 | **+0.0318 ± 0.0106** | **2.99** |
| naive, third overlap-0 arm | `naive` | +0.0750 | +0.1068 | **+0.0318 ± 0.0106** | **2.99** |
| ewc-block-rand, draw 2 | `ewc-block-rand` | +0.0646 | +0.0872 | **+0.0227 ± 0.0086** | **2.63** |
| ewc-block-rand, draw 1 | `ewc-block-rand` | +0.0591 | +0.1010 | **+0.0419 ± 0.0092** | **4.55** |
| ewc-block (biological side partition) | `ewc-block` | +0.0573 | +0.0833 | **+0.0260 ± 0.0106** | **2.45** |
| ewc + frozen bias, λ = 3e-4 | `ewc` | +0.0026 | +0.0190 | **+0.0164 ± 0.0038** | **4.32** |
| ewc + frozen bias, λ = 3e-3 | `ewc` | −0.0021 | +0.0008 | +0.0029 ± 0.0036 | 0.79 |
| replay | `replay` | −0.0034 | +0.0083 | **+0.0117 ± 0.0046** | **2.53** |

**Nine comparisons, nine positive, eight resolved at ≥2σ, none in the other direction.** The direction is unanimous
across methods — the unpenalised body, a biological synapse partition, its matched-random control (both draws), the
frozen-bias arm and replay — which is what makes the answer more than one arm's accident.

**The one unresolved case is the arm with no forgetting to raise**: `ewc + frozen bias` at λ = 3e-3 has an overlap-0
level of **−0.0021**, i.e. already at or below zero, and its overlap effect is +0.0029 (0.79σ). The complement is
worth stating too, because it is the same fact seen from the other side: at λ = 3e-4 the *same* arm, whose level is
+0.0026, moves by +0.0164 at **6.3× its own level** — the largest relative effect in the table.

## 2. What the magnitudes do NOT do

The effect does **not** order with the overlap-0 level, and saying so is part of the result rather than a caveat on
it: the largest *absolute* effect (+0.0419) is not at the largest level (+0.0750 moves +0.0318), and the two arms
whose levels sit at or below zero move by +0.0117 and +0.0029. So the licensed sentences are **"the direction is
unanimous"** and **"the size is not a function of the level"** — not "the effect is proportional to the room".

## 3. Which pairs were admitted, and which were refused

A pair is evidence about `input_overlap` only if nothing else **that the compared arm reads** has changed, and which
fields those are differs by method — so the rules are declared per method and checked against each pair's actual
`config` diff:

- **`lam` is inert for `naive` and `replay` and is not inert for the penalised arms.** This is what refuses
  `e153_r32_overlap1_methods_40reps.json` against `e140_r32_methods_plastic_40reps.json`: the overlap-1 arm ran at
  λ = 1.0 and the overlap-0 arm at 3e-3, so the contrast would mix the overlap with a 300× penalty step. It is
  declared in the script as a refusal, so the admission rules have a known positive.
- **`pool_buckets` and `partition_seed` are inert for the diagonal arm and not for the block arms**, because they
  define the block partition and the matched-random draw.
- **`methods` is inert for every method**, on the strength of a measurement this project already has: each arm is
  trained from the same initial body on the same task draws, so a payload that also ran `replay` does not change its
  `naive` arm — which is what `e102`/`e104`'s C0 checks assert to the digit.
- **`frozen_bias: None` and `False` are the same state** and are compared as such.

## 4. The two limits, and the one experiment that would remove the larger of them

**And the analytic line already has the dose–response this finding asks for, pointing the other way.**
`runs/e7_interference.json`'s `controlled` block sweeps **six** overlap levels and finds interference **falling** as
overlap rises — perfectly monotone, `Spearman = −1.000`, which `e7`'s finding records as the refutation of C4's
direction. `e189` (the same fire) puts the two side by side and localises the disagreement to the **adjacent**
pairs: the analytic near component falls from +0.0258 to below zero while the network's adjacent-task cost rises
+0.0557 → +0.0833. So the sentence a reader must carry away from this finding is *raising the input overlap raises
the network line's forgetting*, not *overlap raises forgetting* — the two lines differ, and by a mechanism the
distance split makes visible.

**The axis has two points *on the network side*.** Overlap 0.0 and 1.0 have both been run; **no intermediate
overlap has ever been run in the rate network**, so the answer above is a *two-point* direction and not a
dose–response — while the analytic line's six points make the sharper question available: the network's near
component should be measured at 0.25/0.5/0.75 to see whether it rises *linearly*, as the analytic one falls. `make_overlap_suite` takes `overlap` as a
float and `--input-overlap` is already a flag on the runner, so an intermediate point is a command rather than a
code change — and it is the natural next registration, because a dose–response would separate "overlap raises
forgetting" from "any overlap at all is enough", which two points cannot.

**And everything here is one circuit, one read-out and one task count**: `mb+cx+al@n1307`, read-out 32,
three tasks, `support 80`. `e188`'s live table carries one circuit size and one read-out, and a read-out-128 or a
five-task replication is a different experiment rather than more data on this one.

## 5. Falsifiers

- **The direction** dies if any admitted comparison comes out negative at ≥2σ; the check asserts `n_negative == 0`
  over the live table, so a new artifact on the same axis either confirms it or fails the test rather than passing
  silently.
- **The admission rules** die if a declared pair is refused by the corpus, or a declared refusal is admitted — the
  exit code counts exactly those contradictions, and one entry is declared as a refusal so the rule has a case it
  must catch.
- **The two-point limit** is not a falsifier but a scope: a reader who wants a dose–response has to ask for the
  experiment, and the run that would provide it is named in §4.

## Reproduce

```
uv run python -m experiments.e188_overlap_contrast                    # 9 comparisons, 0 negative, 1 declared refusal
uv run python -m experiments.e188_overlap_contrast --json-out ONE.json
uv run pytest tests/test_e188_overlap_contrast.py -q
```
