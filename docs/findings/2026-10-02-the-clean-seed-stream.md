# The clean seed stream: the flip was the read-out and the populations

*2026-10-02. Runs: `experiments/e8_rate_network.py --circuit-size 300 --iters 500 --readout-size 32 --repeats 5
--methods replay --closed-loop --loop-symbols 8 --loop-noise 1.0 --loop-scale 1.0 --loop-world-modes 2
--loop-world-leak {1.0, 0.35} --seed0 4 --readout-seed 0 --loop-seed 0` -- read by
`experiments/e340_the_clean_seed_stream.py` against `e333`'s pair and `e337`'s.*

## 1. The fix `e339` named, and only one side of the pair needed running

`e337` ran `e333`'s two worlds on a **second seed stream** and the effect **reversed**: +0.0375 at 2.45 sigma one
way, -0.0771 at 3.36 the other. `e338` then asked one trained body both questions and found the manipulation moves
**nothing** (0.0000 on a sem of 0.0022). And `e339` measured what that redraw was: `--seed0` also draws the
**read-out subset** and the environment's **three populations**, so `e337`'s pair differed in three draws at once.

`e339` named the fix -- `--readout-seed 0` for the decoder and a new **`--loop-seed 0`** for the populations -- and
this unit is it. **Only one side of the pair needed running**: `e333`'s two runs were issued at `--seed0 0` with both
other draws at their defaults, and those defaults are seed 0, so `e333`'s pair *is* the clean stream-0
configuration. The two runs here are the same worlds at `--seed0 4` with `--readout-seed 0 --loop-seed 0`.

**T1 MET.** The stream-4 runs carry the read-out fingerprint `59926518137c` and the cue population
`3985fc4e3252` -- **the same as `e333`'s** -- with `seed0` 0 against 4 and every other setting equal. The new
`--loop-seed` is recorded in the config and both sides of the pair name it.

## 2. And the sign comes back, unresolved

| stream | instantaneous | carried | Δ forgetting | σ |
|---|---|---|---|---|
| clean, `seed0 = 0` (`e333`) | 0.0479 | 0.0854 | **+0.0375** | 2.45 |
| clean, `seed0 = 4` | 0.0500 | 0.0667 | **+0.0167** | **0.95** |
| confounded, `seed0 = 4` (`e337`) | 0.0958 | 0.0188 | **−0.0771** | 3.36 |

**T2 MET**: the sign holds once the other two draws are held, where `e337`'s confounded one had it the other way.
**T3 landed on its NULL** at 0.44x -- the size shrank but not by an order of magnitude. **T4 MET**: the clean pair
differs from `e337`'s by **0.0938**, so **holding the read-out and the populations moved the answer by nearly a
tenth of a point of forgetting**, from -0.0771 to +0.0167.

**So the flip `e337` reported was the read-out subset and the environment's populations, and not the training
seeds.** That is what `e339` predicted from the fingerprints and this unit confirms by re-running the experiment
with them held -- and it is the third and last of the draws `--seed0` was doing at once.

**And what is left after the fix is not significant**: +0.0167 at **0.95 sigma**. The clean stream agrees with
`e333`'s sign and its magnitude is under half of it, with five replicates. So the honest summary of the whole thread
is now: **the effect is in one direction on a clean stream and unresolved there**, while `e338` showed that on a
single trained body the manipulation moves **nothing at all**.

## 3. What it says

**The thread's headline effect was the instrument's, twice over, and the two failures were different failures.**
`e338` took the *model-to-model* variation out and the effect went to 0.0000; this unit took the *draw* variation
out and the effect went from 3.36 sigma the wrong way to 0.95 sigma the right way. Neither the channel nor the
training seeds carry it: what carried it was the decoder's draw and the environment's populations, which are now
named, separated and measured rather than bundled into the word "seed".

**And `--loop-seed` is the smallest change that made the difference.** One flag, defaulting to `--seed0` so every
earlier artifact is unaffected, and it is the flag whose absence made `e337`'s conclusion wrong in a way its own
"what it cannot do" had half-admitted -- it named the read-out **width**, and the **subset** was the sharper version.

**What survives untouched is everything measured within a run.** `e325`'s frozen divergence, `e331`'s ordering (4.4
to 7.6 sigma, arm against arm **within** a sample) and `e328`'s within-stream rate differences are not comparisons of
two separately trained models at two draws, and nothing here changes them.

## 4. What it cannot do

**One clean pair**, so the read-out and the populations are held but the training seeds are still a single redraw,
and two points give a span and not a standard deviation. *The stream-0 side is `e333`'s run and not a re-run*: it is
the same configuration by the defaults' arithmetic, and a reader who changed `fly_env.build`'s seeding would break
that identity without breaking any claim here. *Five replicates*, the count `e336` and `e337` both found to be at
the floor for a configuration contrast -- and the clean effect at 0.95 sigma is the third measurement of this
manipulation to land there. *One arm and one world pair*: `naive`, `ewc` and the block arms are not run. *And a
0.95 sigma in the same direction is not a confirmation*: it is consistent with a small real effect and with zero,
and separating those needs the replicates this design does not have.
