# The Fisher is measured *after* each task's training, so no level knob is clean — and the room account has no isolating test

**Date:** 2026-09-25
**Corrects:** `e173`'s registration premise, one sentence in the paper's §4.7 (pushed an hour earlier), and §3 of
`docs/findings/2026-09-25-the-level-knob-moves-the-gain-and-the-high-end-is-a-null.md`. All three asserted that
`--iters` holds the penalty's Fisher fixed, and **the code says otherwise**.
**Read:** `e171 --knob iters` on `runs/e173_r32_iters250_lam3e-4.json`. Artifact:
`runs/e171_iters_level_knob.json`.

---

## 1. The premise was false, and 2.09σ from a *flat level* is what exposed it

`e173` was registered on this argument: `e167`'s noise knob moves the training data, hence the Fisher, hence the
penalty's *strength* as well as the room — so **`--iters`**, which the project believed left the Fisher untouched,
would move the level with the penalty term held fixed. The registration says so in as many words: *"the Fisher is
computed at θ_init and does not depend on how long the network trains."*

**The Fisher is not computed at θ_init.** In `experiments/e8_rate_network.py` the task loop is

```
for k, task in enumerate(suite):            # line 571
    ... losses.append(train_task(...))      # line 580   <- task k is trained
    ... got = diagonal_fisher(model, ...)   # line 621   <- the Fisher is measured HERE
    ... anchor = model.theta.detach().clone()
```

so the Fisher and the anchor the penalty uses for task *k* are measured at **the parameters after task *k−1*'s
training** — which are exactly what `--iters` moves. Task 0 has no penalty at all (`ewc` is `None` until a Fisher
exists), which is why the loop looks ordinary from outside.

**And the first arm of the run demonstrates it from the other side:**

| setting | `naive` forgetting | level step | resolution | the penalty's gain | gain step | resolution |
|---|---|---|---|---|---|---|
| iters 500 (reference) | 0.0750 | — | — | **+0.0354** | — | — |
| **iters 250** | 0.0794 | **+0.0044** | **0.55σ** | **+0.0141** | **−0.0214** | **2.09σ** |

**The level did not move and the gain fell anyway.** Under the room account — which predicts that the advantage
tracks how much there is to forget — a flat level should mean a flat gain. It halved. And under the *correct* code
reading, that is exactly what is expected: at 250 iterations the parameters the Fisher is measured at are closer to
where they started, so the penalty is a different object even though λ and the level are the same.

**P1 fails** at this end (the level is flat at 0.55σ), **P2 agrees nowhere**, the falsifier does not fire, and the
design's own null applies: **`iters` 250 is not a level knob for this metric.**

## 2. The consequence is general, and it is the unit's real result

**Every knob that moves the forgetting level also moves the parameters the Fisher and the anchor are measured at.**
`noise` changes the data, `iters` changes how far training went, `train` changes how much data there is, and
`classes` changes the task structure — and in all four cases the penalty's *inputs* are re-measured at the state
the knob has moved. So:

> **the corpus contains no single-field manipulation that can isolate the room from the penalty's own strength.**

**What that does to the account's status, stated exactly:**

- **`e166`'s census** found the direction in 5 of 5 resolved level-moving cases and 0 against. It is a
  *correlational* result and it says so.
- **`e167`'s noise knob** confirmed it at 3.55σ/3.57σ with the architecture, read-out, class structure and
  partition fixed — and its confound was named at registration.
- **`e173`'s iters knob** was built to remove that confound and cannot: **its premise was false.**
- So the honest claim is that the room account is **corroborated wherever a level knob has power, and its
  alternative — that the knob changed the penalty's inputs — is bounded and not excluded.** The paper now says
  this instead of the sentence it said an hour ago.

**A design that would isolate it, named and then built**: hold the penalty's inputs fixed *by construction* while
moving the level, so that two levels of forgetting are penalised by the **same** term. That needed a runner change
and it now exists — **`--save-fisher` writes the inputs (the diagonal Fisher and its anchor, one entry per task, as
they stood when that task was trained) and `--fisher-from` uses them instead of computing them** — and what makes
it trustworthy is that a replayed run is **bit-identical** to the run that computed them: verified by an actual
pair of runs, identical `forgetting_per_task` on every task, worst difference **0.0**, configs differing only in the
two flags and the output path. `--fisher-from` is **refused** for the block methods, whose inputs are a partition
and a trace-normalised matrix, because a stored diagonal would silently be a different object.

**And the flags' own `--help` found a defect that had been hiding the runner's flag list**: `argparse`
`%`-formats help strings, so a bare `70%` in `--anchor-bias`'s help raised `TypeError` and **`uv run python
experiments/e8_rate_network.py --help` could not print at all** — two such percents (`70%`, `2.9%`) are now escaped
and a test refuses any future bare one, since that failure mode makes the documentation unprintable rather than
wrong.

## 3. What this cannot settle

- **The iters-1000 arm is still running**, and it may move the level where 250 did not (more training, more
  forgetting). Its read will be the same `e171 --knob iters`, and **it will have the same confound**: this unit's
  result is that no arm of this design can avoid it.
- **The demonstration is 2.09σ.** A marginal resolution, on a design whose premise turned out false — so it is
  evidence that the room account is *not sufficient*, not proof that it is wrong. The 3.55σ/3.57σ co-movement at
  the noise knob is not cancelled by it.
- **The code reading is of one runner at one commit.** `diagonal_fisher` and `block_fisher` are both called inside
  the loop, and the block penalty is built once per task (`part.make_penalty(blocks, anchor_b, model.theta, ...)`),
  so the same applies to `ewc-block*`; a future runner that snapshots a Fisher at initialisation would make this
  unit's claim obsolete and the registration right.
- **And it does not say the room account is false** — only that this corpus cannot run the experiment that would
  isolate it, which is a statement about the corpus and not about the mechanism.

## 4. Both `iters` arms, read: the knob is flat at both ends, and it has a second confound

The 1000-iteration arm landed, so `e171 --knob iters` now reads both ends of the design that was supposed to remove
the confound:

| setting | `naive` forgetting | level step | resolution | the penalty's gain | gain step | resolution |
|---|---|---|---|---|---|---|
| iters 500 (reference) | 0.0750 | — | — | **+0.0354** | — | — |
| iters 250 | 0.0794 | +0.0044 | **0.55σ** | +0.0141 | −0.0214 | **2.09σ** |
| iters 1000 | 0.0786 | +0.0036 | **0.38σ** | +0.0320 | −0.0034 | 0.28σ |

**P1 fails at both ends, P2 agrees nowhere, the falsifier does not fire, and the null applies.** And the null is
the finding rather than a failure to find one: **quadrupling the training length (250 → 1000) moves `naive`'s
forgetting by 0.0008** — the level is flat at both ends of a fourfold range, while `noise` moved it by 0.0312 at
3.55σ. **So on this configuration the forgetting level is set by the tasks' difficulty and not by how long the
network trains**, which is a property of the benchmark and not of the penalty: the tasks are learned to
convergence well inside 250 iterations, and more iterations add nothing to forget.

**And it identifies a second, independent reason this knob cannot isolate the room**: **the penalty acts *during*
training**, so `--iters` changes how many steps it is applied for — at 250 iterations the term has half as many
steps to act in. The gain's fall at 250 (−0.0214 at 2.09σ) is therefore over-determined: a shorter dose *and* a
different Fisher, both in the same direction. Task 0 has no penalty at all and the last task has no future, so the
dose is exactly proportional to the iteration count in between.

**None of this touches the noise result**, which is what the paper's §4.7 carries: there the level moved at 3.55σ
and the gain with it at 3.57σ, on a knob whose impurity is the Fisher alone. What this unit adds to that section is
that **the alternative explanations are bounded rather than excluded, and that the design which would exclude them
is now built** — `e175` is running, and `e176` reads it.
