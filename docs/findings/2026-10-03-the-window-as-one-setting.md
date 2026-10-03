# The window as one setting: forty closed-loop artifacts on one circuit, one draw and one seed stream, with the horizon their own artifacts imply

*2026-10-03. `experiments/e387_the_window_as_one_setting.py` reads every artifact under `runs/` whose configuration
wired the closed loop -- **forty** of them, from `e362` to `e386` -- and asks the two questions a benchmark has to
answer before it can be used: which fields **define** the setting, and which are the **manipulations**. It also
states the horizon the line registered instead of asserting it, by checking three artifacts against each other. No
run; three tenths of a second. Five claims, registered before this unit read the corpus as a set.*

## 1. The setting

Eight fields take **one value each** across all forty artifacts:

| field | distinct values |
|---|---|
| circuit | 1 |
| read-out draw | 1 |
| basis | 1 |
| task names | 1 |
| classes per task | 1 |
| seed stream | 1 |
| circuit size | 1 |
| support | 1 |

**H1 MET.** So the line from `e362` to `e386` is one configuration: the same connectome circuit, the same read-out
draw, the same basis, the same three tasks with the same four classes, on one seed stream. Whatever the twenty-five
units disagree about, they are not disagreeing about the setting.

**And fourteen fields vary, of which seven are the manipulations and seven follow from them.** `H2 MET`:

- **moved**: the cue's step, the drive's source, the learning rate, the iteration budget, the replicate count, the
  world's dimension, the frozen-body flag;
- **following by construction**: the three world draws (the drive map, the read map and the coupling matrix, whose
  widths and consumption move with the population the world listens to and with the world's dimension), the action
  population's fingerprint and width, the drive's source flag, and the tasks' read-out widths, which the runner sets
  to `arange(loop_world_dims)` when the read-out is the world.

That second list is the one three units have now tripped over -- `e381`'s head-row field, `e383`'s missing learning
rate and `e386`'s read-out widths -- and this unit is the first to **write it down in one place** rather than
rediscovering it one field at a time.

## 2. The horizon, checked against the artifacts that measured it

`e369` walked the circuit's mask and found the cue population at directed distance **0** from itself and **2** from
the action population; `e368`'s curve records the last clearing step as **10** for the cue source and **8** for the
action one. With `tau = 12`, `tau - 2 - d` predicts **10** and **8**. **H3 MET**: the formula the line registered is
the curve's own two cliffs, read from the two artifacts rather than restated.

## 3. The draw

`e370` drew sixteen configurations and took the distance **1** eleven times and **2** five times; every window run
carries `seed0 = 0`, which that sweep puts among the two-hop draws. **H4 MET.** So the whole window is on the
**minority** draw -- five of sixteen -- and every horizon in it is the two-hop horizon: the modal draw's boundary is
one step later, which `e370` measured and no unit in the window has run on.

**H5 MET**: forty artifacts against a bound of twenty, and the count is asserted as a bound because it grows with
the corpus.

## 4. What a user of this window needs to be told

Three traps are in the corpus's own artifacts and are worth being in one place:

1. **The splits.** The window's runs train each task on **96** examples and read it on **48**; `e366`'s ladder prices
   that at **0.0677** against 512 examples in two halves, and its suite structure at **-0.0278**. A diagonal here is
   not comparable with a 512-example probe without that price.
2. **The learning rate.** Thirty-one of the window's forty runs trained their head at the corpus's `3e-3` and
   nine at `0.03`, and `e376` and `e378` measured that step size as worth **0.1965** and **0.2132** on *frozen*
   bodies. **Every one of those thirty-one diagonals is a lower bound on what its cell reaches.**
3. **The comparisons across bodies.** Every "a trained head against a frozen probe" claim in the window is a
   comparison of two different bodies; `e379` and `e380` are the units that made it like-for-like, and on the trained
   body the probe and the head agree to **-0.0076** at the tight end and **+0.0163** at the wide one.

## 5. Two reader bugs this unit had

**Both were found by the fired claim rather than by review.** `H4` first read the distances at the top level of
`e370`'s rows, where they are not -- they live under each row's `sources` -- so it counted zero of everything and
fired a claim about that unit which that unit does not make; and its fix then compared the **counts** to the
**distances**, asking whether `{11, 5}` equals `{1, 2}`. The claim's statement was right both times and the reader
was wrong both times, which is the useful thing about registering a check that is specific enough to fail: a reader
that reads the wrong field cannot pass it silently.

## 6. What it cannot do

*A definition by a field*: the window is the artifacts whose `config.closed_loop` is true, so a run that wired the
loop by another name would be outside it and a run that set the flag without a world would be inside. *And it audits
consistency and not correctness*: forty artifacts agreeing on a circuit and a draw says the corpus is one setting
and says nothing about whether the setting is the right one. *And the horizon is stated, not measured here*: H3
checks three artifacts against each other and rolls nothing, so the two cliffs are `e368`'s and the two distances are
`e369`'s, exactly as those units left them. *And the three traps are quoted*: each is a number in another unit's
artifact, not a measurement this one makes.
