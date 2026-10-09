# Replay beats the penalty by up to 12σ while the line's own headline is a null

*2026-09-29 00:05. Runs: **none new** — `experiments/e276_replay_against_the_penalty.py` reads the four forty-replicate
artifacts of the `r32` line that carry both the `replay` and the `ewc-block` arms
(`e140_r32_methods_frozenbias_40reps`, `e140_r32_methods_plastic_40reps`, `e153_r32_overlap1_methods_40reps` and its
rerun `e159_r32_overlap1_methods_rerun`), writing `runs/e276_replay_against_the_penalty.json`. Seconds.*

## 1. The item: a contrast the register quotes nowhere

The network line's headline is the **basis** contrast — a biological anchoring partition against its size-matched
random control — and eleven fires of audit have left it a **null** at every budget the corpus has: 1.19σ at sixteen
replicates, 1.57σ for the ordering's leader at 144, 0.28σ on the one rung that has 144.

Beside it, every forty-replicate `r32` run trains a **replay** arm, and the contrast between the two *methods* has
never been quoted the way the basis contrast is: paired over the same seeds, with a sigma. It is a read of the
register, and it is the largest number on this line.

## 2. What the register says

| configuration | replay − `ewc-block`, accuracy | `ewc-block` − `naive`, accuracy | replay − `naive`, accuracy |
|---|---|---|---|
| frozen bias | **+0.0090 (3.30σ)** | +0.0040 (1.74σ) | +0.0130 (6.21σ) |
| plastic | **+0.0441 (9.09σ)** | +0.0043 (0.80σ) | +0.0484 (9.83σ) |
| overlap 1.0, λ 1.0 | **+0.0618 (11.84σ)** | +0.0052 (0.81σ) | +0.0670 (12.73σ) |

and on forgetting, replay minus `ewc-block`: **−0.0044 (1.26σ)**, **−0.0607 (8.42σ)**, **−0.0549 (7.12σ)** — negative
is better.

**V1 MET — replay beats the penalty on accuracy at every configuration, by 3.3 to 11.8σ.** **V2 MET — and it does not
pay for it in forgetting**: replay forgets less in all three, resolved at two. **V3 MET — while the penalty's own gain
over the naive baseline is unresolved on accuracy at all three** (1.74σ, 0.80σ, 0.81σ). **V4 MET — and the contrast is
not a draw**: `e153` and `e159` are the same configuration run twice and carry **bit-identical** replicate lists, so
that configuration's 11.84σ is exact rather than one sample.

## 3. What it means for the line

**The strongest method contrast in this record is replay against the penalty, and the register has been quoting the
basis contrast instead.** The two statements sit on the same runs: the biological anchoring contributes nothing
resolvable over a random basis (the audits' null), while a replay buffer — a textbook method with no connectome in it —
is worth 0.009 to 0.062 accuracy and 0.004 to 0.061 forgetting over the penalty, at up to 12σ. And the penalty's own
contribution over the naive baseline is unresolved on accuracy at every configuration, which is the same statement
from the other side: **what the benchmark measures strongly is that replay works, not that the connectome's basis
does.**

**The scope is the substrate, and the paper already says why.** Its analytic line records the ordering *inverting*
when the unpenalised channel is removed from every arm — `ewc` minus `replay` at 1.04σ there against 9.40σ with the
channel free — so "replay is the stronger method" is conditional on what the baseline is allowed. Nothing here says the
`r32` line's ordering travels to another substrate; what it says is that this line's strongest contrast is the one it
does not quote.

## 4. What it cannot do

**Three configurations are not the line**, and only the frozen-bias one carries all five arms. The `r32` readout is a
32-wide shared head — exactly the "channel" the paper's analytic caveat is about — so the scope is narrow by
construction. `frozen_bias` removes most of the training variance and so carries the smallest of the three contrasts
(3.30σ against 9.09 and 11.84). The comparison is paired over seeds, but the arms are trained inside one process, so an
arm-order effect is not excluded. And **no run is made**: this is a read of runs the register already has, and the
missing measurement is the one that would say whether the ordering survives a different substrate — which is a run, not
a re-reading.

## RE-READ 2026-10-09: the owed run is made, and the ordering is larger on the second substrate

Section 4 closes on *"no run is made: this is a read of runs the register already has, and the missing measurement is
the one that would say whether the ordering survives a different substrate -- which is a run, not a re-reading."*
`e476` made that run: `e140`'s own command at circuit 800, five hundred updates, the 32-neuron shared head,
`lam = 3e-3` and `seed0 = 0`, with the **assembly suite** in place of the overlap builder and forty replicates on
`naive`, `ewc-block` and `replay`. `replay` minus `ewc-block` there is **+0.1214** at **13.41** sigma on the diagonal
and **-0.1857** at **-14.06** on forgetting, against this unit's own **+0.0441** at **9.09** and **-0.0607** at
**-8.42**; `ewc-block` minus `naive` is a null on both (**+0.80** here, **-1.33** there). **So the ordering travels
and it widens, and the widening is the baseline's**: the buffer reads **0.9609** and **0.9540** on the two substrates,
**0.0069** apart, while `naive` falls **0.067** and `ewc-block` **0.084**.

**What this unit published stands** and its V1 to V4 are untouched; what changes is the scope its own section 4 named,
which is now measured rather than owed
(`docs/findings/2026-10-09-the-ordering-on-another-substrate.md`).
