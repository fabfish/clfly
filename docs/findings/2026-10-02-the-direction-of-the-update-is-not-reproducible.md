# The direction of the update is not a reproducible quantity

*2026-10-02. Runs: `experiments/e8_rate_network.py --circuit-size 300 --iters 500 --readout-size 32 --repeats 5
--methods replay --closed-loop --loop-symbols 8 --loop-noise 1.0 --loop-scale 1.0 --loop-world-modes 2
--loop-world-leak {1.0, 0.35}` -- 146 s and 181 s, read by `experiments/e336_the_direction_of_the_update.py`.*

## 1. The fourth and last account a norm cannot speak to

`e333` measured `replay`'s retention moving in opposite directions under the thread's last two changes to the world's
channel. Three units then excluded the accounts a **norm** can speak to:

    e334   not the stored features fitting worse     0.32 sigma on the loss the arm minimises
    e335   not the buffer's contents differing       byte-identical, element by element
    e335   not the body drifting further             the carried body moved 2.93% LESS

and `e335` ended on the one it could not reach, in words its own "what it cannot do" had written in advance: *"drift
is a norm and not a direction"*. Its named instrument was a per-task **direction** of `theta_final - theta_before`.

**This unit records it.** `run_method` now keeps, per task, the update sampled at a **fixed index set** drawn from a
constant seed and normalised to a unit vector -- so two runs' vectors live in the same coordinates and a cosine
between them estimates the cosine between the full 20,079-dimensional updates. Two runs, `replay` alone, five
replicates, on `e333`'s two worlds, same seeds.

**T1 MET.** Same circuit `mb+cx+al@n952`, same read-out `59926518137c`, the same three task names, five replicates
each, the environment draw identical in every field the leak does not name, and **every recorded direction carrying
the same index fingerprint** `57355f38f584` in both runs -- so the comparison is on one subspace and not on two.

## 2. And within a world the direction is noise

| task | within, instantaneous | within, carried | across the two |
|---|---|---|---|
| 0 | 0.1467 | 0.0505 | 0.1384 |
| 1 | 0.0193 | −0.0143 | 0.0408 |
| 2 | 0.0550 | 0.0715 | 0.0494 |
| **pooled** | **0.0737** | **0.0359** | **0.0762** |

**T2's falsifier FIRED.** The registered claim was that the direction is **reproducible within a world** -- a mean
within-run cosine of at least 0.50 -- and it is **0.0548**. **T3's and T4's fired too**: the across-run cosine is
*higher* than the within-run one by 0.0214, and it is higher for two of the three tasks.

**And the number has a floor that explains it.** Two independent directions in a 256-dimensional subspace have an
expected cosine of **1/sqrt(256) = 0.0625**, and the measured within-run mean is **0.0548** -- the measurement sits
**on** the random-overlap floor. So two replicates of the **same** configuration do not point the same way at all:
the update's direction decorrelates between replicates while its **norm** is reproducible to a few per cent, which
is precisely why three units could compare norms and none could compare directions.

**The instrument is not too coarse; the quantity is not there at five replicates.** The subspace fixes the floor at
0.0625 and the effect would have to exceed it to be visible; a within-world reproducibility of 0.5 would have been
plain, and 0.05 is not a weak version of it. The honest reading of the two-group design is that **the across-run
comparison has no scale to be read against**, which is why T3 and T4 are reported as fired and not as nulls: their
falsifiers were written on a drop, and what arrived is the opposite sign.

## 3. What it says

**The fourth account is out, and this one is out for a stronger reason than the first three.** `e334` and `e335`
each excluded a quantity that *was* measurable -- the loss on the stored features, the buffer's contents, the drift's
size -- and this one excludes a quantity that is **not measurable at this replicate count at all**. The update's
direction is not a property of the configuration; it is a property of the seed's trajectory, and two seeds of one
configuration differ from each other by as much as two configurations do.

**So the thread's most robust fact stands with no account attached to it.** `replay`'s retention moves by 0.03 to
0.04 when the world's channel changes, at 2.45 to 2.89 sigma, and it is not the fit, not the buffer, not the
distance and not the direction. What is left after four exclusions is a shorter list than an open one: something
that averages over replicates rather than being visible in any single one -- the *distribution* of updates rather
than their direction, or the interaction between the replayed gradient and the current task's, which no unit here
has isolated.

**And one thing is now known about the instrument rather than about the world.** A direction comparison at this
subspace needs more than five replicates or a **paired** design -- two arms whose replicates share a seed's
trajectory -- and nothing in this corpus is paired that way for the closed loop. That is the shape the next unit
would have to take, and it is a design statement rather than a measurement.

## 4. What it cannot do

**Two runs and one arm**: `naive`, `ewc` and the block arms are not run, and `e332`'s other sign is not asked.
*A 256-dimensional subspace of a 20,079-dimensional update*: the cosine estimates the full one and is not it, and
the subspace sets the noise floor at 0.0625 -- a smaller true effect inside the subspace would be invisible, and a
difference living outside it entirely is invisible by construction. *Direction is one summary of a trajectory*: the
update is taken once per task, so a path that curved and came back is indistinguishable from a straight one.
*Five replicates*: with a within-world cosine at the random floor, nothing here can say how many replicates would
put a real reproducibility above it -- the run that would is the same design with more of them. *And this is about
`theta` alone*: the bias channel, which no penalty in this project covers, is not in the vector.
