# The matched-settings pair is in flight: a reader registered ahead of its data

*2026-09-28 19:05. Runs: **two, launched and in flight** — `e8_rate_network` at cs 300 with `--readout-size 32
--shared-head --basis side --lam 1.0 --fisher-batches 32 --support 80 --repeats 16 --methods
naive,ewc,ewc-block,ewc-block-rand`, run twice with `--seed0 0` and `--seed0 100` and nothing else changed. The reader
`experiments/e266_matched_settings_read.py` was written while they ran and names both artifacts.*

## 1. What `e265` left open

`e265` found that the ordering `e264` read over the corpus does not reproduce: the pair that differs only in its basis
leads in 21 of the 50 readable matrices, and the five `fb8` runs that share **every** configuration field give it ranks
1, 0, 1, 0 and 0. `e265` read that disagreement as an **unrecorded setting**, because only two of those five runs are
bit-identical and three of them name thread counts no artifact records.

**The alternative reading is that a correlation at sixteen replicates is simply too noisy to order three pairs**, and
the corpus cannot separate the two: the only configuration it ever ran twice at fixed settings is `e153`/`e159`, whose
runs are bit-identical, so it produces no disagreement and no power either. Every other repeat in the record varies
something — threads, overlap, λ, basis, circuit size or the replicate count.

## 2. What was bought

**Two runs of one configuration, differing in `seed0` alone.** Both are `side` at cs 300 with `readout_size` 32,
`shared_head`, `fisher_batches` 32 and `lam` 1.0 — the cell of the corpus's best-powered matrix, which has 144
replicates — with **sixteen** replicates, four arms, and the environment block filled in by the runner (torch version,
thread counts, platform, calibration constant). That gives a fixed-settings repeat for the first time.

**And four arms rather than three.** The second addition is the plain `ewc` arm: a penalty with **no basis**, so it
shares the penalty form with both block arms and the basis with neither. `e265` noted that the corpus cannot separate
those two by arm counts, because only 22 of its 35 artifacts carry `ewc` and only at five replicates in this
neighbourhood. Here it is at sixteen, in both runs.

## 3. The reader, and its four registered claims

`e266` reads the pair, plus the same cell's 144-replicate matrix as an across-budget check. All four claims are
**confirmatory**, registered in the module before the data landed:

| claim | what it says | falsifier |
|---|---|---|
| **M1** | one configuration gives one ordering: the two seeds put the basis pair at the same rank | different ranks between the runs |
| **M2** | and the runs agree inside the sampling noise of a correlation: every pair within the 95% Fisher band at n = 16 | a pair outside its band |
| **M3** | the plain-EWC arm separates the penalty form from the basis: the penalty-only pair is above both naive pairs, in both runs | it is at or below both naive pairs in either run |
| **M4** | and the ceiling device applies at this cell: every arm's test-floor below its own spread | an arm at or above its own spread |

**M1 is the one that matters for `e265`.** If the two seeds order the pairs differently, then `e265`'s disagreement
needs no unrecorded setting to explain it, and its W3 should be read as sampling noise; if they agree, the
fixed-settings repeat supports the unrecorded-setting reading and the `fb8` group's disagreement stands as a real
difference between experiments.

**The module reports its own absence rather than a number.** Its exit code is the count of claims refused because an
artifact is missing, so while the runs are in flight it exits 4 with all four refused — which is why the programme
table's row for it names no artifact under `runs/` and why it is **not yet in `tools/gates.sh`**: a gate entry for a
reader whose data has not landed would be a red gate for a reason that is not a defect. Both come with the data.

## 4. What it cannot do

**Two seeds are two draws.** M1 is a single comparison, and `e265`'s five-run group is the better replication of the
same question — the pair was bought to relieve that tension, not to settle it. The two runs share the machine, the
torch version and the thread count, so neither can see an environmental change: a *fixed* setting is not a *recorded*
one, and only the environment block makes it the second. Sixteen replicates leave a correlation a standard error near
0.25, which is why M2 is a band and not a difference. And M3 is a one-directional prediction about a cell that has
never carried the plain-`ewc` arm before, so a null there is a null on one cell.

**The runs are also the first this line has launched with a four-arm method list at this cell**, so their wall clock
is itself a measurement: the runner's own progress line reports the naive arm at 12 to 13 s per replicate and projects
about thirteen minutes for that arm's sixteen, which is what prices anything the pair's results go on to ask for.
