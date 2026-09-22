# E8e — class-incremental on a shared head: it gets *easier*, not harder, and no method beats naive

**Date:** 2026-09-22
**Script:** `experiments/e8_rate_network.py --shared-head`
**Artifacts:** `runs/e8_class_incremental.json`
**Setup:** circuit `mb+cx+al@n1307`, 3 tasks, 5 replicates each, λ = 0.003, Fisher batches = 32, chance 0.25

---

## 1. Why the harder setting

Every network result so far used **per-task decoders** — the head belonging to a finished
task is never touched again, so only the shared recurrent body can be forgotten. That is
the task-incremental setting, and the standard objection to it is that it is too easy: a
per-task head can absorb any amount of task-specific structure, so the body is never
asked to hold several tasks at once.

`--shared-head` removes that. One decoder serves every task, read out from the **whole
circuit state**, and the tasks' label sets are made disjoint (task `k` owns classes
`4k … 4k+3` of a 12-way head), trained with cross-entropy over the task's own slice only —
the standard class-incremental protocol, where the learner never sees a future task's
classes.

## 2. Result: it got easier, and nothing beats naive

| method | final accuracy | mean forgetting |
|---|---|---|
| **naive** | **0.936 ± 0.011** | **+0.044 ± 0.018** |
| EWC, diagonal Fisher | 0.883 ± 0.039 | +0.121 ± 0.056 |
| EWC, block Fisher — biological cell-class pairs | 0.922 ± 0.023 | +0.058 ± 0.031 |
| replay (16 stimuli/task) | 0.917 ± 0.016 | +0.065 ± 0.024 |

**Naive sequential training is the best method on both metrics.** Nothing improves on it:
the diagonal is worse by +0.077 forgetting (1.3σ) and −0.053 accuracy, the block Fisher by
+0.014 (0.4σ), and replay by +0.021 (0.9σ).

**And replay no longer helps.** In the task-incremental configuration it drove forgetting
to −0.000 ± 0.021 against naive's +0.101 ± 0.049, the one network result that resolved
anything. Under a shared head it is *slightly worse* than naive and the difference is not
resolved. So replay's benefit is setting-dependent, and the strongest claim the network
line supports is narrower than it appeared.

**The shared head made the problem easier, not harder**, which is the opposite of the
expectation that motivated the experiment:

| configuration | naive accuracy | naive forgetting |
|---|---|---|
| task-incremental (per-task heads) | 0.840 ± 0.013 | +0.101 ± 0.020 |
| **class-incremental (shared head)** | **0.936 ± 0.011** | **+0.044 ± 0.018** |

## 3. Why, and why it is interesting rather than embarrassing

The usual reason a shared head makes class-incremental harder is that the tasks **share
an input space** — natural images, say — so they must be solved with the same features and
the head's directions for old classes get overwritten. Here they do not share an input
space: each task's stimulus is injected into a *different circuit*, and the read-out is the
whole state. So the three tasks' representations live in largely distinct parts of state
space, and a linear head with 15.7k parameters has no difficulty allocating near-orthogonal
directions to each task's classes. There is no competition to create forgetting.

That is the connectome doing something a conventional benchmark cannot: **the tasks are
separated at the input, by the wiring, rather than at the head.** The class-incremental
penalty that CL papers fight over largely evaporates when the tasks arrive through
different circuits — which is, of course, exactly how a fly avoids the problem.

## 4. The limitation this exposes, which matters more than the result

Both network settings now agree that **forgetting is mild and no method reliably improves
on naive**. The reason is visible in the numbers: all three tasks are learned to ~0.92–1.00
accuracy against 0.25 chance, and naive forgetting is +0.04 to +0.10. There is very little
headroom for a CL method to demonstrate anything.

**The benchmark is too easy to discriminate between methods**, and the fix is task
difficulty rather than more methods or more replicates:

- raise the stimulus noise so accuracy is ~0.6–0.7 rather than ~0.95, leaving room to
  forget;
- use more classes per task, and overlapping *within-task* structure so the head must
  reuse features;
- drive tasks into **overlapping** input populations (the controlled-overlap machinery from
  `e7` is already in the repo) so they compete for the same circuits — which is the
  configuration in which the class-incremental penalty should appear at all.

That third one is the interesting experiment: it would test whether the connectome's
input-level task separation is *why* forgetting is mild, by removing the separation and
seeing whether forgetting appears.

## 5. Where the network line stands

| claim | status |
|---|---|
| the benchmark runs, learns, forgets | **yes** — 3 tasks, ~0.92–0.94 vs 0.25 chance, in both settings |
| replay reduces forgetting | **only in the task-incremental setting**, ~2σ; not under a shared head |
| EWC helps, in any basis, at any λ or Fisher batch count | **no** — five λ values, three batch counts, two bases, two settings |
| the linear basis finding transfers to synapses | **no**, and its two candidate explanations (estimation noise, a bad λ) are both ruled out |
| the benchmark discriminates CL methods | **not yet** — too easy; task difficulty is the binding constraint |

The honest summary of the whole network effort: it produced a working, reproducible,
connectome-constrained CL benchmark, and the benchmark's own mildness is the reason no
method separation has been found on it. That is a limiter to fix, not a wall — and the
fix is identified.
