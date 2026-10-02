# The frozen body on the earned label: all of the forgetting is the body's, and the connectome is worth 0.2080

*2026-10-02. One runner invocation -- `e356`'s exact flags plus `--frozen-body`, `--methods naive,replay`,
`--repeats 20` -- into `runs/e358_earned_label_frozen_20reps.json`, paired against `e356`'s plastic arms, which are
already on disk at the same seeds. Eighteen minutes. Read by
`experiments/e358_the_frozen_body_on_the_earned_label.py`.*

## 1. The control both earlier units named

`e356` resolved the method contrast on the earned label at 11.65 sigma and `e357` found the basis contrast a null on
it at 1.47 sigma. Both closed with the same untested control: *"`frozen`, `frozen-bias` and the oracle line are not
run."*

**`--frozen-body` trains the head and nothing else** -- the recurrent weights stay at the connectome's
initialisation -- and on this substrate it asks something the state read-out cannot. Here the answer is read from a
world the agent's own actions drive, so with the body frozen the head alone has to make the frozen dynamics write a
separable state into the world. Whether it can is a question about the connectome's role in the benchmark.

## 2. The answer

| body | arm | final accuracy | diagonal | `mean_forgetting` | paired channel | sigma |
|---|---|---|---|---|---|---|
| plastic | `naive` | 0.5493 | **0.8226** | **0.4099** | +0.2951 | 19.73 |
| plastic | `replay` | 0.6983 | 0.7802 | 0.1229 | +0.4434 | 34.84 |
| frozen | `naive` | 0.6146 | **0.6146** | **0.0000** | +0.3785 | 148.77 |
| frozen | `replay` | 0.6149 | 0.6149 | **0.0000** | +0.3788 | 197.63 |

chance 0.2500. **T2 MET**: the frozen body **does** learn the suite -- its diagonal mean is **+0.3646 above
chance** -- so the world read-out does not need a plastic body to be learnable at all. **T3 MET, and it is the
sharper half**: the plastic body is worth **+0.2080 of diagonal at 27.99 sigma**, paired over the seeds.

**T4 FALSIFIER FIRED, and it fires on the most informative number in the table: the frozen suite's forgetting is
exactly 0.0000.** On replicate 0 the frozen retention is `[[0.688], [0.688, 0.646], [0.688, 0.646, 0.583]]` -- task
0 reads **0.688** after task 0, after task 1 and after task 2, unchanged. **So all of the earned label's forgetting
is the body's**, and none of it is the head overwriting itself: with the connectome frozen, each task's cues drive
the world the same way for ever and a per-task head has nothing to interfere with. **T5 NULL**: with nothing to
forget, a sixteen-example buffer changes nothing either -- 0.0000 against 0.0000.

**And the frozen arms' channel reading is 149 and 198 sigma**, which is worth reading carefully: the plastic arms'
reading is 19.73 and 34.84, and the frozen arms' is far sharper because every replicate trains the **same** frozen
body, so the only variation across replicates is the head's initialisation. The quantity itself -- the answer
depending on the loop -- is the same in all four arms, which is the earned label's own signature and not a property
of the control.

## 3. What it means for the benchmark

**The earned label measures the connectome and not only a decoder.** The frozen control bounds what a linear map
over a fixed environment can do -- **0.6146** of diagonal -- and the plastic body adds **0.2080** on top at 28
sigma. And the *forgetting* is entirely the body's, which is the corpus's own quantity read in its cleanest form:
on the state read-out the head and the body both move and the decomposition is a model; here the control separates
them exactly, because freezing the connectome makes the suite's interference vanish to the last digit.

## 4. What it cannot do

**T1 FALSIFIER FIRED**, and it is a record and not a configuration: the frozen run's `partition_draw` is absent
because that run trained no block arm and the runner draws the matched-random partition only when one is asked for,
so the only fields differing beyond `frozen_body` are the partition's fingerprint and group count. Every field that
matters for the pairing -- the world's fingerprint, the basis, the tasks, the widths, the sizes, the replicate count
and the seed stream -- agrees. Beyond that: *one control and two arms*, with `frozen-bias`, `--anchor-bias` and the
oracle line unrun; *one world, one leak and one width*, `leak = 0.35` and eight dimensions; and *a frozen body is not
a lesioned one*, so this bounds plasticity's contribution and does not measure the substrate's.
