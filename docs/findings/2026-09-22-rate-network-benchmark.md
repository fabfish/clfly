# E8 — the rate-network substrate: replay wins, diagonal EWC does nothing

**Date:** 2026-09-22
**Module:** `clfly/network/` (`model.py`, `tasks.py`)
**Script:** `experiments/e8_rate_network.py`
**Artifacts:** `runs/e8_rate.json`
**Setup:** circuit `mb+cx+al@n1307`, 3 tasks, 3 independent runs per method, 96 train /
48 test stimuli, 500 iterations, chance = 0.25

---

## 1. Why this fire exists

Every result in the project so far sits on the linear-Gaussian reduction. That was a
deliberate choice — it buys an exact Kalman oracle, which is why the basis question
could be answered at all — but the paper's own limitations section says a
rate-network benchmark with behavioural tasks is the natural next instrument, and
until now it had not been built.

This fire builds it and gets the first end-to-end CL numbers out of it. The question
is deliberately the minimal one: **does it work at all, does it forget, and does the
project's own theory predict what helps?**

## 2. The substrate

A connectome-constrained rate network:

    x_{t+1} = (1 - alpha) x_t + alpha * tanh( W x_t + b ),    W = M * theta

with `M` the connectome's **sign pattern as a fixed mask** and `theta` the trainable
synapse strengths (initialised at the connectome's `log1p` strengths). `tanh` is
smooth, so this trains by ordinary backprop-through-time — no surrogate gradients.
At the standard circuit that is 27k trainable recurrent weights over 1307 neurons, and
a full 3-task × 3-repeat × 500-iteration experiment runs in **4 minutes on CPU**.

Three behavioural tasks on **distinct circuits**: odour identity (stimulus into Kenyon
cells, read out from MBONs), heading (into central-complex ring neurons, read out from
CX), and odour input (into antennal-lobe projection neurons, read out from Kenyon
cells). Class identity is carried by a per-class input template plus noise, injected
as a **sustained** drive over 12 timesteps so the recurrence has time to propagate the
stimulus from the input population to the readout — which is the point of using the
wiring rather than a feedforward readout.

Decoders are **per task**, which makes this task-incremental: the shared recurrent body
is retrained on every task and is where forgetting happens. That is the standard first
setting and it isolates the body's forgetting from the head's.

## 3. Results

| method | learned (diagonal) | forgetting per task | **mean forgetting** | final accuracy |
|---|---|---|---|---|
| naive | [0.924, 0.924, 0.903] | [+0.236, +0.035, —] | **+0.135 ± 0.021** | 0.826 ± 0.004 |
| EWC, λ=1 | [0.924, 0.931, 0.917] | [+0.139, +0.174, —] | **+0.156 ± 0.078** | 0.819 ± 0.066 |
| replay (16/task) | [0.951, 0.917, 0.896] | [+0.014, +0.049, —] | **+0.031 ± 0.010** | 0.900 ± 0.013 |

**The benchmark works.** All three tasks reach ~0.92 accuracy against 0.25 chance, in
three independent runs each, so there is both a learnable signal and a real CL problem
to solve. Naive sequential training forgets the first task substantially (+0.236) and
the second mildly (+0.035).

**Replay gives a resolved ~4× reduction.** +0.031 ± 0.010 against naive's
+0.135 ± 0.021 — a difference of 0.104 ± 0.023, i.e. **4.5σ**. Sixteen stored stimuli
per task, which is a trivial memory budget.

**Diagonal-Fisher EWC gives no measurable benefit — at any λ.** The λ sweep
(0.01, 0.1, 1, 10, 100; single seed, so read as a scan rather than a measurement)
produced mean forgetting of +0.146, +0.135, +0.094, +0.198, +0.083 against naive's
+0.083 in the same single-seed comparison. **No λ beat naive**, and the best merely
tied it. At λ=1 with error bars the difference from naive is +0.021 ± 0.081 — not
resolved, and in the wrong direction.

The λ=100 single-seed case also shows *why* a mean is the wrong thing to stare at:
task 0's forgetting went **negative** (−0.042, it improved) while task 1's rose to
+0.208. EWC was trading one task's retention against another's rather than reducing
forgetting overall.

## 4. The theory predicted this

This is the first result in the project where the connectome-scale theory makes a
falsifiable call about a *learned* network, and it calls it correctly.

LGCL says EWC *is* a Kalman filter with the posterior covariance projected onto the
neuron coordinate basis, and §4.1 measured that projection to cost **+33% excess
error** on this very connectome. A method whose entire mechanism is that projection
should therefore not be expected to help on this substrate — and it does not help, at
any λ, on a benchmark where a strictly weaker method (storing sixteen stimuli) reduces
forgetting fourfold.

It also reproduces LGCL v7's regime finding from the other direction. These tasks are
**partially observed** — each drives a small input population, so each constrains a
low-rank subspace — and LGCL measured that in that regime content memory becomes
12.7× more valuable than in the fully-observed one. Replay is content memory. It wins.

## 5. Honest limits

- **Task-incremental, three tasks.** Per-task decoders mean the head does not have to
  solve task identification; class-incremental with a shared head is harder and is not
  tested here. Three tasks also makes "mean forgetting" an average of two numbers.
- **The λ sweep is single-seed.** Only λ=1 has error bars. The scan is enough to say
  "no λ produced a resolved improvement"; it is not enough to rank the λ values.
- **Input populations are small** (28–220 neurons of 1307), so each task is genuinely
  partial-observability, which is realistic but also means the shared body has plenty
  of unconstrained capacity — a possible reason forgetting is as mild as it is.
- **No basis comparison yet.** This is the network substrate running with the *neuron*
  coordinate basis for the Fisher. The project's actual finding — that coarser
  biological groupings and the wiring eigenbasis are better anchoring structures — has
  not been carried over to the network, and that is the obvious next experiment: group
  the 27k synapse parameters by (pre cell class, post cell class) and anchor the Fisher
  block-diagonally instead of diagonally.

## 6. Status

The rate-network substrate exists, trains, learns, forgets, and discriminates between
methods. It is the first instrument in the project on which a *learner* can be
compared rather than a filter. The natural next step is to repeat the basis comparison
inside it.
