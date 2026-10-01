# The benchmark has no time in it

*2026-10-01. Runs: `experiments/e322_the_benchmark_has_no_time_in_it.py --json-out
runs/e322_the_benchmark_has_no_time_in_it.json` -- two circuit sizes, both suite builders, the frozen connectome
network. Minutes.*

## 1. The word that had never been measured

The plan's benchmark block calls this suite a continual-learning benchmark for a **recurrent** network, and its own
description of a task says the stimulus is *"injected into a task's input population as a sustained drive"*.
*Sustained* is the load-bearing word: if the drive is constant for the whole trial then the trial's time axis carries
no information, the recurrence is a settling transient from a zero state toward a fixed point, and the label is a
property of **where the state lands** rather than of anything happening over time.

That distinction decides what the benchmark can be asked. A game needs the environment's next input to depend on the
agent's previous output, which is exactly a stimulus that changes with time. So this unit measures the axis before
anything is built on it.

**T1 MET** -- 18 task instances over 6 suite builds (assembly and overlap at 0.0 and 1.0) and 2 circuit sizes
(`mb+cx+al@n952`, `mb+cx+al@n1307`): the worst `max_t |u[:, t] - u[:, 0]|` over both splits is **exactly 0**.
The stimulus is the same array at every one of the twelve steps.

**T2 MET** -- and there is only one place in the repository that could write it. An AST scan of every module under
`clfly/` and `experiments/` for subscript stores into a three-dimensional array finds **one** site,
`clfly/network/tasks.py:121`, and its time axis is a full slice (`u[:, :, inp] = stim[:, None, :]`, a broadcast). A
store whose middle index were a step variable would have been flagged; none exists. The scan also finds sites under
`tests/`, and they are fixtures -- including, on the second run, the three the tests for this very unit write into
temporary files, which is the count growing with the suite rather than the claim moving.

**T5 MET** -- and the corpus is inside these two builders: **182 artifacts** name 3 assembly-family task names and 15
overlap-family names, and **none is in neither family**. So the invariance is a property of every replicate this
project has recorded, not only of the two builders measured here.

## 2. The registered claim that fired, and what the trial actually does

**T3's falsifier FIRED.** The claim was that the state settles: that the step size at the last step is below 5% of the
first step. It is **197%** of it, worst case, across all 18 tasks. The registered denominator is the zero state's
first step (`alpha * tanh(u)`, no recurrent contribution), so that ratio is biased upward by construction, and the
unbiased version was reported beside it: **with the trial's own largest step as the denominator, the worst last step
is 1.000 of it.** The last step of the trial is the largest step of the trial.

The curves say it plainly. For `assembly/odour_identity` at `mb+cx+al@n952` the per-step change runs

```
3.00e-01  3.89e-01  4.78e-01  4.97e-01  5.28e-01  5.50e-01  5.64e-01  5.66e-01  5.75e-01  5.82e-01  5.88e-01
```

monotone in every task of both suites and both sizes, and the increments **level off near 0.59 rather than
decaying**. So the trial ends with the state far from equilibrium and the increments still rising: nothing in the
twelve steps is a settled read-out. That the level is a fixed point the trajectory is approaching in a straight line
and a limit cycle it has entered are not separated here -- both give a constant increment -- and the unit does not
claim which.

**T4 landed on its registered NULL.** The claim was that the label is already readable by the midpoint: for every task
whose final-rung probe is above chance by 0.05, the midpoint probe is within 0.05 of the final one. It is within
**0.0833**, between the window and the falsifier at 0.10. What the probe curves show is why: **the read-out peaks
early and declines.** On the frozen network the linear probe is at its ceiling after one or two recurrent steps --
1.00 for every whole-state read-out and 0.92 to 1.00 for `odour_identity`, whose Kenyon-to-MBON path takes exactly
one step -- and **falls** over the remaining trial (`odour_input` at `mb+cx+al@n1307`: 0.38, 1.00, 0.92, 1.00, 0.96,
0.83, 0.83, 0.75, 0.79, 0.67, 0.54, 0.50). In 13 of the 18 tasks the last step reads strictly worse than the best
one.

## 3. What that says

**The benchmark's recurrent dynamics, on the frozen connectome, make the label less readable over the trial rather
than more.** Propagation from the input population to the read-out completes in one or two steps; after that the
state keeps moving, and what it moves through is the decoder's problem. The twelve steps are therefore not a
computational resource -- they are a cost paid to an accelerating transient.

Three consequences a task built for this benchmark has to live with:

- **A stimulus that varies with time is not merely absent, it is unauthorable through the current path.** One site
  writes `u`, and it writes a constant. A temporal task needs either a second writer with a time index or an
  environment in the training loop; either is a change to the runner, not to a spec table.
- **`tau = 12` is not a tuned window.** Nothing in the corpus chose it against a measurement of this axis; with the
  transient unfinished at the last step, the read-out is being taken at an arbitrary point of a diverging series.
- **A closed loop is the thing that is missing, not more tasks.** A fourth classification task on a constant drive
  adds a fourth fixed point to the same picture; a game needs the drive to depend on the state.

## 4. What it cannot do

**The frozen network is the connectome initialisation and not a trained one**, so the time constant measured here is
the substrate's; training multiplies `theta` and would move it. **The probe is linear** and fitted per step on the
read-out population, so a task that is not linearly decodable is reported as such rather than as a bad time axis, and
a non-linear decoder would place the ceiling differently (not later). **Three tasks and two circuit sizes at one
connectome, one weight scale and one leak**: whether the acceleration is the circuit's or `alpha`'s is not separated,
and one unit could: sweep `alpha` at a fixed circuit. **A settled trajectory would not have been a useless one**, so
T3's firing does not by itself say the benchmark is degenerate -- it says the last step is a snapshot and not a fixed
point, which is a statement about where the read-out is taken. **And the corpus check is a naming check**: `T5` reads
task names, so a hypothetical third builder that reused the two families' names would pass it.

## 5. RE-READ 2026-10-01, after `e323` added the second writer

**T2's falsifier FIRED, and the unit's own section 4 predicted the change that did it.** `e323` gives the suite its
first time-varying stimulus -- `make_sequence_task` in `clfly/network/tasks.py`, whose writer carries an explicit step
index -- and that is the *second* of the two options section 4 named (*"a temporal task needs either a second writer
with a time index or an environment in the training loop"*).

The reading is now **two authored sites, one writing along the time axis**, and the effect on this unit's claims is
exactly one of them: **T2 FIRED** and is reported as FIRED in `runs/e322_the_benchmark_has_no_time_in_it.json`. T1 is
untouched (18 task instances, worst deviation exactly 0 -- the measurement was never about the count), **T5 is
untouched** (182 artifacts, none outside the two families), **T3's falsifier is still FIRED** on the registered
denominator and **T4 still lands on its registered null**.

The assertion in `tests/test_e322_the_benchmark_has_no_time_in_it.py` that pinned `len(authored) == 1` is now the
structural one that replaces the count: one full-slice writer and one step-indexed writer, both in
`clfly/network/tasks.py`, the sustained builder older than the sequence builder. A third writer must therefore arrive
as a deliberate change rather than as a drift in a number, which is what the count was there to notice.

## 6. RE-READ 2026-10-01, after `e324` ran the sequence suite: T5 fired too

`e322`'s section 5 above was written when the second writer existed but no artifact used it. `e324` trained the five
arms on the sequence suite, so `runs/` now holds an artifact whose tasks are named `seq_odour_identity`,
`seq_heading` and `seq_odour_input` -- names in **neither** of the two families this unit's census knows.

**T5's falsifier FIRED**, and it is the same kind of event as T2's: the claim was a statement about the corpus as it
stood, the corpus grew a **builder**, and the census reports it rather than absorbing it. That is the instrument
working. The verdict now reads `FALSIFIER FIRED -- ['seq_heading', 'seq_odour_identity', 'seq_odour_input'] belong to
neither family`, over 183 artifacts, and the two builders' own counts are unchanged inside it.

What did **not** move: T1 (18 task instances over 6 suite builds and 2 circuit sizes, worst deviation exactly 0 --
the invariance measurement is about the sustained builders and they are untouched), T3's falsifier on the registered
denominator, and T4's null.

**The assertion in `tests/test_e322_*.py` is now the structural one**, and it is deliberately two-sided: the names
the census cannot classify must be exactly the `seq_` family, and the verdict must agree with whether there are any.
So the next builder to arrive fires it again, and a *reclassification* of the sequence family -- which would be an
instrument change made after reading -- cannot be slipped in as a green test.
