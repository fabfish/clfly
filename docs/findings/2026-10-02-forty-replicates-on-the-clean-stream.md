# Forty replicates on the clean stream: there is no effect

*2026-10-02. Runs: `experiments/e8_rate_network.py --circuit-size 300 --iters 500 --readout-size 32 --repeats 40
--methods replay --closed-loop --loop-symbols 8 --loop-noise 1.0 --loop-scale 1.0 --loop-world-modes 2
--loop-world-leak {1.0, 0.35} --seed0 4 --readout-seed 0 --loop-seed 0` -- read by
`experiments/e341_forty_replicates_on_the_clean_stream.py` and compared with `e340`'s five-replicate pair.*

## 1. The number three units left at the floor

`e333` measured `replay`'s forgetting rising **0.0375 at 2.45 sigma** when the world's channel acquired a transition
rule. `e337` found the sign reversing on a second `--seed0` (**−0.0771 at 3.36**). `e338` asked one trained body both
questions and the manipulation moved **0.0000** (sem 0.0022). `e339` measured that `--seed0` draws the read-out
subset and the environment's populations as well as the training seeds, `e340` held those two and re-ran, and the
sign came back at **+0.0167 and 0.95 sigma** -- with its own finding naming the unit that would separate a small
real effect from zero.

**This is that unit.** The clean pair -- same two worlds, `--seed0 4 --readout-seed 0 --loop-seed 0`, every other
field equal -- at **forty replicates**, the count `e328` found it took to resolve a forget-rate difference on this
family.

**T1 MET.** Same circuit `mb+cx+al@n952`, same read-out fingerprint `59926518137c`, the same three task names, forty
replicates each, the seeds, the cue symbols, the cue noise, the world state count and every environment field equal,
and the two runs differing only in `world_leak` -- `1.0` against `0.35`.

## 2. And the effect is not there

| stream | replicates | instantaneous | carried | Δ forgetting | sem | σ |
|---|---|---|---|---|---|---|
| confounded `seed0 = 0` (`e333`) | 5 | 0.0479 | 0.0854 | **+0.0375** | 0.0153 | 2.45 |
| clean `seed0 = 4` (`e340`) | 5 | 0.0500 | 0.0667 | **+0.0167** | 0.0176 | 0.95 |
| clean `seed0 = 4` | **40** | 0.0643 | 0.0630 | **−0.0013** | **0.0094** | **0.14** |

**T2's falsifier FIRED.** The paired difference over forty replicates is **−0.0013 at 0.14 sigma** -- the wrong side
of zero and four hundredths of the way to any resolution. **T3's fired too**: a magnitude of 0.0013 where the
registered floor was 0.005. **T4 MET**, and it is the unit's one caution rather than its result: the five-replicate
estimate was within 0.018 of the forty-replicate one, which clears the bar and is thirteen times larger than the
value it was estimating.

**And the design had the power to see `e333`'s effect.** The per-replicate spread is 0.0509 instantaneous and 0.0409
carried, so the forty-replicate standard error is **0.0094** and an effect of 0.0375 would have appeared at **4.0
sigma**. It appeared at 0.14, on the other side.

**So there is no effect of the world's channel on `replay`'s retention at this task, this channel strength and this
read-out** -- and the chain that ends here is worth reading as a chain: `e333`'s 2.45 sigma was a confounded stream's,
`e337`'s 3.36 was that confound reversing, `e338` showed the manipulation moves a trained body by nothing at all,
and `e340` showed the flip was the decoder's draw and the environment's populations. Four units, four different
explanations excluded, and the fifth measurement -- the one with the power -- says zero.

## 3. What it says

**The thread's five units after `e333` were spent on an effect that is not there, and they were right to spend it.**
`e334` to `e337` excluded four mechanisms; `e338` built the pairing that removes the model-to-model variation and
found 0.0000; `e339` found that the "seed stream" was three draws; `e340` built the clean pair; and this unit gave
it the replicates. Each of those is a statement that stands on its own -- and the last of them is the one that
closes the question, because it is the first measurement of this manipulation with the power to speak.

**And what it leaves standing is narrower than what it removes.** `e338`'s 0.0000 is the *strongest* form of the
result: on a fixed trained body, removing the channel changes at most one held-out decision in 144. This unit's
−0.0013 is the *between-model* form: run the two worlds as two configurations and the difference is a redraw's
noise, now measured at 0.0094 per replicate over forty. The two agree and neither is positive.

**What is untouched is everything measured within a run.** `e325`'s frozen divergence (52% of the peak state),
`e331`'s ordering (4.4 to 7.6 sigma, arm against arm inside one sample) and `e328`'s within-stream rate differences
are not comparisons of two separately trained models at two draws, and nothing in this chain changes them. A
benchmark may still say `replay` beats the penalty arms; it may not say closing the loop costs `replay` retention.

## 4. What it cannot do

**One stream, one arm and one world pair**: the clean stream at `--seed0 4` is a single redraw of the training seeds
and the stream-0 side stays at `e333`'s five replicates, so this resolves the effect **on this stream** and cannot
say a third would agree -- `e337` is the standing evidence that a second one changed the answer. *`naive`, `ewc` and
the block arms are not run.* *The paired standard error is the across-replicate one*: three tasks share a body and a
head, so a replicate's fifteen numbers are not independent and the task variation inside a replicate is averaged and
not modelled. *And a nil here is a nil at `scale = 1.0`, `leak = 0.35`, this task and this read-out*: nothing in
this unit says a different channel, a harder task or a wider read-out would also move nothing.
