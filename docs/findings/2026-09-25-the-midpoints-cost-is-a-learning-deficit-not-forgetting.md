# The midpoint's accuracy cost is a LEARNING deficit (8.10σ), while the endpoint's is forgetting (2.99σ) — and finding it exposed four files naming artifacts that do not exist

**Date:** 2026-09-25
**A cheap unit done while `e193`'s last level runs**, on artifacts that already exist. The runner records, per
replicate, the accuracy on each task **right after learning it** (`learned[j]`) and **at the end**
(`final_per_task[j]`), with `mean_forgetting` the mean drop over the first T-1 tasks. So the accuracy cost *is* a
learning term plus a retention term, and the two can be read apart. They are not the same at the two ends of the
overlap axis, and that is the finding.

---

## 1. The decomposition, and the identity it rests on

`mean(final_per_task[:-1]) == mean(learned[:-1]) - mean_forgetting` **holds exactly**, per replicate, to 1e-12, at all
four artifacts — checked in the tests rather than asserted. So a change in the older tasks' final accuracy is the sum
of a change in how well they were learned and a change in how much they were forgotten, and each can be tested on
its own. `naive`, 40 seeds, against the disjoint baseline `e116` (overlap 0.0):

| achieved overlap | **learned (older tasks)** | **forgetting** | final (older) | newest task |
|---|---|---|---|---|
| 0.1429 | **+0.00651 ± 0.00320 = 2.03σ** | +0.01406 ± 0.01213 = 1.16σ | −0.00755 (0.62σ) | +0.00677 (1.23σ) |
| **0.3333** | **−0.03255 ± 0.00402 = 8.10σ** | +0.00833 ± 0.01060 = **0.79σ** | **−0.04089 (3.86σ)** | **−0.01667 (2.25σ)** |
| 1.0000 (`e144`) | +0.00104 ± 0.00318 = **0.33σ** | **+0.03177 ± 0.01063 = 2.99σ** | −0.03073 (2.93σ) | +0.00573 (1.10σ) |

**Two ends of the same axis, the same size of accuracy cost, opposite mechanisms.** At full overlap the older tasks'
final accuracy is 2.93σ down and **all of it is forgetting** (2.99σ) with learning unchanged (0.33σ). At achieved
0.3333 the older tasks' final accuracy is 3.86σ down and **almost all of it is learning** (8.10σ) with forgetting
unresolved (0.79σ). And at achieved 0.1429 the learning term moves the *other* way — 2.03σ **better**.

This is the mechanism behind the puzzle recorded in
`docs/findings/2026-09-25-the-accuracy-accounts-interior-overshoots-its-own-endpoint.md` §1: that the midpoint's
accuracy cost is 176.6% of its own 0 → 1 endpoint change while its forgetting is 0.79σ. The overshoot is not a
retention effect at all; it is an interior level at which the network learns the earlier tasks markedly worse.

**And the excursion is resolved against both neighbours**, so it is not a single point's noise:

| `learned (older)` | contrast | resolution |
|---|---|---|
| achieved 0.3333 − achieved 0.1429 | +0.03906 ± 0.00401 | **9.73σ** |
| achieved 0.3333 − overlap 1.0 (`e144`) | −0.03359 ± 0.00445 | **7.55σ** |

## 2. What the measurement does NOT distinguish, which matters here

`learned[j]` is the accuracy on task j measured immediately after training it. **A task set that is harder to fit and
a task set whose members interfere are the same measurement.** The manipulation changes which neurons the three tasks
share, so at achieved 0.3333 the tasks' supports overlap more than at 0.1429; a higher overlap can make each task
harder to fit behind a shared decoder without any "interference between tasks" being involved. This design cannot
separate those two readings, and the finding is therefore about **which component moves**, not yet about why.

Two further scope limits, both checkable:

- **The supports are not in the artifact.** They are reconstructed from the target `input_overlap`, the circuit and
  seed 0, which the registration already names as a limitation for the achieved overlap itself. What *is* checkable
  was checked: `readout` and `seed0` are byte-identical across all four artifacts, and `circuit` is
  `mb+cx+al@n1307` for all four. `partition_draw` is absent from `e116` and `e144`, but that field records the
  **matched-random control's** draw and not this arm's supports
  (`docs/findings/2026-09-24-the-random-control-is-a-sample-and-31-of-38-artifacts-do-not-say-which.md`).
- **One interior level of a five-level design**, n = 40, three tasks, one circuit. A resolved interior excursion at
  one level is a fact about this axis at these seeds.

## 3. The defect this verification exposed: four files named artifacts that do not exist

The registration's prose writes the three levels `e193_r32_overlap{25,50,75}_methods_40reps.json`. The launch ran
`n=$(echo $ov | tr -d '.')`, which turns `0.25` into **`025`**, `0.50` into **`050`** and `0.75` into **`075`** — so
the files on disk are the *padded* names, and every reader pointed at the unpadded ones.

| file | carried |
|---|---|
| `experiments/e194_s_claims_read.py` | the default three-level list, unpadded |
| `tests/test_e194_s_claims_read.py` | the two interior levels, unpadded |
| `tests/test_e191_interference_across_lines.py` | the three levels, unpadded |
| `tests/test_e188_overlap_contrast.py` | the three levels, unpadded |

**Two of those tests asserted the falsehood, and passed.** `e191`'s
`test_the_dose_read_on_the_live_registration_says_which_levels_are_missing` and `e188`'s
`test_the_live_registration_names_three_levels_and_none_exists_yet` both asserted that all three levels were
"not written yet" — true when written, and still true in their output now, for the wrong reason: **two of the three
exist and were being looked for under names that do not resolve.**

**And a refusal cannot tell the two causes apart.** `e194`'s output was *identical* whether a claim was refused
because the artifact had not landed or because the path did not name it, and the first version of this unit's
verification read that output as "the reader refuses correctly". It does — but the check was vacuous. The reader now
prints the levels it found, before any verdict, so an empty list is a statement about the paths:

```
levels found: achieved 0.1429, achieved 0.3333
    S1: REFUSED -- no measured progress at achieved 0.6
```

This is the same class as the five instrument defects recorded today — a quantity read in the wrong window, direction
or subject prints a plausible number — with the subject being a **path** this time, and it is the second instance
where the plausible-looking output was a *refusal* rather than a number.

## 4. Registered now, before level 0.75 lands

**S5 — the midpoint's mechanism does not persist to two thirds of the axis.** At achieved 0.6000 `naive`'s
`learned (older)` change against `e116` is **above −0.0100**, i.e. the −0.03255 of §1 is an excursion rather than the
start of a monotone decline. **Falsifier**: at or below **−0.0200**, which would say the learning deficit persists at
two thirds of its size and that the endpoint's forgetting-dominated cost is the *interior* rather than the rule.
**Null worth keeping**: between −0.0200 and −0.0100 — a partial deficit, which would leave the shape graded rather
than either an excursion or a trend. The value, its σ and its sem are printed by `e194`, and S5's bar is read at the
same achieved overlap as S1-S4.

## 5. What this does not license

- **That the overlap *causes* worse learning at 0.3333 by interference.** §2: a harder task set and an interfering
  one are the same measurement here.
- **That the cost's mechanism changes *because* the overlap changes.** Two endpoints and one interior level are three
  points; the reading is that the components differ across them, and a mechanism would need a design that holds the
  task set's difficulty still while moving its overlap.
- **Anything across accounts.** These are `naive` accuracy quantities; the interference account's near/far split
  (82.1% against 20.0% at the same achieved overlap) is a different decomposition and nothing here measures whether
  the two coincide.
- **A σ on the newest task's 2.25σ.** It is one number at one level, and the newest task is a single task.

---

**CORRECTION, later the same day: the deficit this finding is about did not replicate at a second support
draw.** On `e195`'s draw-1 family the interior deficit is **+0.00417 ± 0.00361 = 1.15σ** against draw 0's
−0.03255 = 8.10σ, so the registered R1's **falsifier fired**: the 8.10σ is a property of **draw 0's supports** and
not of the overlap, and the draw's own effect on `learned (older)` is **−0.01484 (3.34σ) at overlap 0.0 and
+0.02187 (4.40σ) at achieved 0.3333** — it reverses sign across the axis. The decomposition and the identity in §1
stand (they are exact arithmetic); what is withdrawn is the reading of the deficit as the axis's mechanism. `docs/findings/2026-09-25-the-interior-fitting-deficit-did-not-replicate.md`
