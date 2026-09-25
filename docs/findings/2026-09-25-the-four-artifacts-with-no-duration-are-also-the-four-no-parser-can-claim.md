# The four artifacts that record no duration are also the four no parser can claim

*2026-09-25, second half of the `e205` unit. Code: `e205_duration_field_census.py` (the declaration is now
checked against `e172`'s registry), the two writers fixed (`e122_path_geometry.py`,
`e124_barrier_distribution.py`), verified by two real runs. Artifacts: `runs/e122_timing_smoke.json` (6.487 s),
`runs/e124_timing_smoke.json` (5.645 s).*

## 1. The reader was named as the writer

`e205`'s first version declared the writer of each of the four no-duration artifacts by hand, and two of the
declarations were **wrong in a way this project keeps finding**: `e130_barrier_r32.json` and
`e131_barrier_r1307.json` were attributed to `e136_geometry_persistence.py`, which is the module that **reads**
those two grids (it is an analysis whose three flags are `--grid`, `--worst`, `--json-out`). The artifact's
reader is not its writer — the same shape as `e201`'s draw fields, `e160`'s environment identity and `e172`'s
epochs.

The repair is to stop declaring and start deriving. A `config` is `vars(args)`, so the writer is the parser that
accounts for the most of the artifact's keys, and `e172`'s AST registry says which module defines which flags.
Ranking by overlap gives a **unique** answer for all four, with a margin:

| artifact | derived writer | keys explained | runner-up | keys the writer does not define |
|---|---|---|---|---|
| `e122_path_geometry.json` | `e122_path_geometry.py` | 28 of 29 | `e124_barrier_distribution.py` 26 | `save_theta` |
| `e124_barrier_12seeds.json` | `e124_barrier_distribution.py` | 30 of 31 | `e122_path_geometry.py` 26 | `save_theta` |
| `e130_barrier_r32.json` | `e124_barrier_distribution.py` | 32 of 33 | `e122_path_geometry.py` 26 | `save_theta` |
| `e131_barrier_r1307.json` | `e124_barrier_distribution.py` | 32 of 33 | `e122_path_geometry.py` 26 | `save_theta` |

The declaration is now data that the check **compares against the derivation**, so a wrong name is a counted
violation rather than a comment — which is how this table would have caught its own first version, and a test
pins it (`test_a_declared_runner_that_does_not_derive_is_counted_as_a_violation`).

## 2. Why `e172`'s own candidate test found nobody — and the paragraph this first got wrong

`e172`'s `candidates()` requires a parser to define **every** key an artifact carries, and for these four it
returns the empty set. The reason is the last column above: all four carry one key that no parser defines —
`save_theta` — and it is the *same* key in all four.

**The first version of this finding said that key was a flag that had since been removed, and that is wrong.**
`save_theta` is assigned by the runners themselves, inside their training loop:

    experiments/e122_path_geometry.py:272   args.save_theta = args.theta_dir
    experiments/e124_barrier_distribution.py:57  args.save_theta = args.theta_dir

It exists because the shared `run_method` expects that attribute (`e8_rate_network.py:778` reads
`getattr(args, "save_theta", None)`), and because the artifact stores `vars(args)`, the runner's own plumbing is
serialized into the `config` beside the flags the caller passed. So the correct statement is stronger and more
general than the one it replaced: **a `config` is `vars(args)` plus whatever the runner adds to it**, which means
`e172`'s premise ("a runner is a candidate exactly when its parser defines every key the artifact carries") is
refuted by the runners' own code, and `e169`'s key-clock reads a keyset that is partly plumbing.

**And the corpus already said so.** `tests/test_e163_repeat_floor.py` documented this in its docstring — *"the
four that no runner fits are exactly the artifacts `e172` found carrying a key no parser defines (`save_theta`,
which two runners assign at runtime)"* — so the correction was one test away from where I was looking, and the
guess I published instead was checked against a *derivation* (my own max-overlap ranking) rather than against the
sentence a colleague had already written.

**What caught it was the pinned count.** `tests/test_e172_parser_registry.py` asserted
`len(res["unclaimed"]) == 4`, and the two smoke runs of §3 made it **6** — the assertion was a count of a class
that grows by one per run of either runner, exactly the mistake the neighbouring parser-floor comment warns about
one line above it. Both pinned counts are now floors with the class asserted precisely (every unclaimed
artifact's config, minus `save_theta`, is contained in one of the two injectors' flag sets — which also covers
`e130`/`e131`, artifacts whose *filenames* name no runner at all).

Taken together these four are the record's most provenance-poor artifacts: **no duration, no `environment`, no
`code_revision`, and no parser that can be shown to have produced them** (only a ranking can). They are not
unimportant — `e131`'s read-out 1307 grid is the point `e136` compares the other two against, and `e124`'s
twelve-seed barrier distribution is the C2b line's barrier evidence.

## 3. The fix, verified by execution rather than by reading

Both runners now take `t0` after argument parsing and write `timing_s` into their artifact — the same
expression every other runner uses, so `duration_seconds` and `e169`'s start-time clock can read it. Two real
runs at a small configuration confirm it end to end:

    e122_path_geometry --circuit-size 100 --iters 5 --train 8 --test 4 --readout-size 32 --support 20
        -> runs/e122_timing_smoke.json   timing_s = 6.487 s   (29 config keys)
    e124_barrier_distribution --circuit-size 100 --iters 2 --train 8 --test 4 --readout-size 32 --support 20
        --seeds 2 --points 3 --checkpoints all
        -> runs/e124_timing_smoke.json   timing_s = 5.645 s   (33 config keys)

Two details of the design are worth keeping:

- **`t0` is taken after `parse_args`**, so the number is the run and not the interpreter's import time; `e169`
  already declares that `timing_s` starts after imports and its start times are therefore upper bounds, and the
  new writers inherit that same bias in the same direction rather than adding a new one.
- **`e124`'s `--reanalyse` branch is left alone**: it rewrites the *stored* payload in place, so a reanalysis
  cannot pass its own few seconds off as the run's cost. Adding the field only to the training path is what
  makes that true; adding it to both would have been a silent way to overwrite four hours with six seconds.

## 4. The check I tried next and did not ship

With durations now readable, the obvious next level is the **citation**: rule 49's prices appear as prose, so
does the plan quote a duration that no artifact records? I built it, measured its error rate, and threw it away.

- *Bind a duration to any artifact id in the same table row.* 82 attributed tokens, **46 "unsourced"** — and
  almost all of them are other numbers: a row naming four artifacts quotes a duration from a fifth, "13 h and
  five commits later" is elapsed project time, "22.86 min per arm" is arithmetic, "12.2 h at the dearest" is an
  extrapolation the row itself labels as one. **A row is not a sentence.**
- *Bind a duration to a `runs/` path within 160 characters.* 8 candidate pairs, **6 false** — and the reason is
  structural rather than a tuning problem: this project's cost sentences are **comparisons** ("2653 s against
  1758.9 s", "1.5×"), so two artifacts' durations sit twenty characters apart and any proximity rule binds a
  number to its neighbour. **A number's neighbourhood is not its subject**, which is rule 52's lesson in a new
  place.

So the negative result is: **a duration-citation audit is not constructible from prose proximity in this
corpus**, and the reason is that the sentences which quote two costs are exactly the sentences that matter. A
version that worked would have to parse the structure of the claim rather than the neighbourhood of the number:
the registration format the plan already uses for bars (rule 51) is the only place a machine-readable statement
of a price exists, and that is where such a check should be built if it is built at all. Recorded here so the
next session does not pay for the same two designs.

## 5. What this changes in the record

- `e205`'s declaration now carries the derived writer and counts a disagreement as a violation; its exit code
  is still **0**.
- The previous finding of this unit said the fix was *"recorded rather than applied"* and named three runners;
  both are corrected: **two** runners had no clock, and both now write one.
- The count of run-like artifacts moves 161 → 163 as the two smoke runs land, which is the census behaving as a
  live reading rather than a stored number.
