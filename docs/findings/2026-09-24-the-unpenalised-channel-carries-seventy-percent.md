# `e125`: the 800 parameters no penalty covers carry **70%** of this benchmark's forgetting

**Date:** 2026-09-24
**Script:** `experiments/e8_rate_network.py` with the new `--frozen-bias`; artifacts
`runs/e125_r32_plastic.json`, `runs/e125_r32_frozenbias.json` (+ `runs/e125_r32_frozenbody.json`).
**C0's comparators:** `runs/e116_r32_40reps.json` (bit-identity) and `runs/e104_frozen_r32_plastic.json`
(values).
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, chance 0.25, `--methods naive --shared-head
--input-overlap 0.0 --noise 1.0 --iters 500 --lr 3e-3 --batch 32 --test 48 --readout-size 32 --circuit-size 800`,
**40 replicates**, `seed0 + 100r`.
**Pre-registration:** `docs/findings/2026-09-24-the-unpenalised-channel-preregistered.md`, committed before the
run. **The falsifier fired.**
**Context:** the flag came from reading `train_task` and `diagonal_fisher` together, not from a hypothesis about
biology — see that registration's §1.

---

## 1. The falsifier fired, at 5.90σ, on 40 paired seeds

| arm | forgetting | accuracy | per-task forgetting |
|---|---|---|---|
| **naive** (plastic) | **+0.0750 ± 0.0088** | 0.9125 | +0.0964, +0.0536 |
| **frozen-bias** (no penalty, no cost) | **+0.0227 ± 0.0033** | **0.9306** | +0.0292, +0.0161 |

Paired over the forty shared seeds: **+0.0523 ± 0.0089 = 5.90σ, 31 of 40 replicates positive.** And the two
arms' per-task numbers are the striking part — **both forgettable tasks lose exactly 70% of their forgetting**
(0.0964 → 0.0292 and 0.0536 → 0.0161), a uniform reduction rather than one carried by a task.

**So the registered consequence follows as written**: *"800 parameters, 2.9% of the body, carry the majority of
this benchmark's forgetting"*, and — the clause that matters more — **every EWC number in this project is
measured against a naive baseline whose forgetting partly lives where no penalty looks.** At read-out 32 that
"partly" is **70%**.

**And it is not free, but it pays.** The diagonal — how well each task was *learned* — falls slightly on all
three tasks (**0.9682 → 0.9464, 0.9526 → 0.9505, 0.9667 → 0.9401**), while the **final accuracy rises**
(0.9125 → 0.9306): the retention gained on tasks 0 and 1 outweighs the fit lost on task 2. The retention loss
says the same thing in the other metric — **0.20998 → 0.08018** (2.62×) and **0.15320 → 0.04392** (3.49×), with
the loss-valued forgetting falling **68%**, which is the two metrics agreeing on a direction rather than the loss
one being more precise (`e123` measured that it is not).

## 2. The mechanism, and it is legible

**The body drifts *more* with the bias frozen** — `theta_drift` 0.0506 → 0.0554, **+10%** — while forgetting 70%
less. So the adaptation does not become smaller; it **moves into a different set of parameters**.

That is exactly what the two channels are. The 800 offsets are **per-neuron** and **global**: every one of them
shifts its neuron's operating point for **every** task and every input, so training task `k` through them moves
the whole network's response at once and damages every earlier read-out simultaneously. The 26,568 weights are
**masked by the connectome** — sparse, sign-constrained, and structured — so they can carry adaptation along
paths that are more local, and a longer walk in the structured channel interferes less than a shorter walk in the
global one.

**Which reframes the omission rather than merely condemning it.** The registration listed as a possible
reconciliation that *"the bias has no wiring semantics… so a result that the omission is harmless would be a
cleaner outcome than the argument for the omission currently on record."* That outcome did **not** obtain: the
omission is not harmless, and it is not harmless *because* the bias has no wiring semantics — a channel with no
locality is precisely the one that interferes most.

## 3. And the comparison it forces on the project's own headline

At **the same five seeds** (all these arms use `seed0 + 100r`, so the first five of any forty-replicate run *are*
a five-replicate run):

| arm | forgetting | vs naive, paired | resolution |
|---|---|---|---|
| naive | +0.0729 | — | — |
| **EWC**, diagonal, λ = 0.003, 32 Fisher batches | +0.0208 | −0.0521 ± 0.0272 | 1.92σ |
| **frozen-bias**, no penalty at all | +0.0250 | −0.0479 ± 0.0202 | **2.37σ** |

and **frozen-bias − EWC = +0.0042 ± 0.0205 = 0.20σ.** **A free structural constraint is indistinguishable from
the project's tuned diagonal penalty, and its effect is the better resolved of the two.**

**That is not yet a result and `e133` is registered to make it one**: the EWC arm has five replicates and this
one has forty, so "indistinguishable" is currently a statement about a five-replicate pen. `e133` runs **the same
hardened configuration** — `--methods naive,ewc --fisher-batches 32 --lam 3e-3`, 500 iterations — at **forty
replicates**, on the same seeds, and asks whether the tie survives the power. **P2 of that run is this paragraph;
its falsifier is EWC beating frozen-bias by 3σ.**

**What it would mean if the tie survives**: the paper's §4.2 table has a row missing, and not because the penalty
is wrong. It would mean the honest comparison against `naive` is a comparison against a naive run that is
**unnecessarily forgetful** — 70% of what the penalty is measured as fixing is forgetting that a zero-cost
constraint of the body removes, in a channel the penalty never looks at.

## 4. Controls

- **C0a, the extension control, is bit-identity.** The plastic arm's forty replicates reproduce
  `runs/e116_r32_40reps.json` with **max |difference| 0.000e+00**, and — new here — `e104_frozen_r32_plastic.json`'s
  five replicates are **identical as values** to the first five of both, despite carrying a *different key set*.
  **A third instance of rule 32's converse**, and the one that licenses the cross-epoch comparison in §3.
- **C0b passes exactly**, and it is the flag's own control: **every `bias_norms` entry is exactly 0.0 across all
  forty replicates** (both `step` and `from_zero`, all three tasks) **while `theta_drift` is non-zero at every
  task and replicate** (minimum **0.0507**). The first half alone would pass for a run that froze everything.
- **`e125_r32_frozenbody.json`** — the third arm — is the `e104` control at eight times the power, and it is a
  **structural zero**: forgetting is exactly **0.0000 at all forty replicates** (one distinct value, sd 0.0000),
  with every `bias_norms` entry 0.0 and every `theta_drift` 0.0, and the fit loss is two orders above the plastic
  arm's (0.2147 / 0.3311 / 0.1745 against 0.0046 / 0.0052 / 0.0055). **The load-bearing gap replicates**:
  plastic 0.9125 − frozen-body 0.8134 = **+0.0991** against `e104`'s **+0.1000** at five replicates.

## 4b. And it cuts the benchmark's own per-repeat spread — in one unit and not the other

The three arms at forty replicates give a result this fire did not register and that bears directly on §4.7's
sentence that the binding limit is the **per-repeat spread**:

| arm | forgetting | per-repeat sd | **relative sd** |
|---|---|---|---|
| naive | 0.0750 | **0.0556** | **74.1%** |
| frozen-bias | 0.0227 | **0.0207** | **91.2%** |
| frozen-body | 0.0000 | 0.0000 | — |

**The absolute spread falls 2.69×** — from 0.0556 to 0.0207, and the plastic arm's worst replicate forgets
**+0.2500** where the frozen-bias arm's worst is **+0.0729** — **while the relative spread rises 1.23×**, because
the mean falls **3.30×** and faster than the sd.

**Both statements are true and only one of them is what `e118` measured.** That section's handicap is a
*relative* precision (74–134% of its own value against the drift's 2.6–3.5%), so on that scale removing the
channel makes the forgetting **harder** to measure — the effect shrinks faster than its noise. On the absolute
scale it makes the benchmark quieter. **Registering only the second would have been the `e123` unit error in a
third costume**, which is why the table carries the column `e118` used.

And it puts a qualifier on §4.7's "binding limit": the limit is the per-repeat spread, **and the spread is
partly self-inflicted** — a channel carrying 70% of the forgetting also carries most of the variance, because a
global 800-parameter offset is exactly the kind of parameter that lands differently for different seeds.

## 5. What this cannot settle

- **One read-out, and it is the one chosen for the opposite reason.** Read-out 32 is where the body is most
  load-bearing, which *maximises* the chance of seeing the bias matter; the registration stated that direction
  in advance so that a null here would have been weak evidence. It fired, so the remaining question is
  generality: **at read-out 1307 the plastic weights are not needed at all** (the load-bearing gap is −0.0111),
  and a bias effect there would need its own explanation.
- **`frozen-bias` is a diagnostic, not a method.** It holds 800 parameters at their initialisation: no
  hyperparameter, no regulariser, comparable to EWC only because both are interventions on the same training
  loop. **A tie makes it the cheaper measurement of what the penalty is worth, not the better method.**
- **The bias is frozen at exactly zero, which is its own initialisation and not a tuned value.** A different
  frozen value, or a *penalty* on the bias, is a third arm this fire did not run — and `e125` therefore does not
  say that a bias penalty would help, only that removing the channel does.
- **The mechanism in §2 is an inference from drift-plus-retention**, not a measurement of locality. What is
  measured is that the body moves *more* and forgets *less*; "the adaptation moved into a more local channel" is
  the reading that fits and is not separately tested.
