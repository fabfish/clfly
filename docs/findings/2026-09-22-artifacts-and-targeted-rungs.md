# Run artifacts were not valid JSON, and the two claims worth buying can be bought in a third of the compute

**Date:** 2026-09-22
**Scripts:** `clfly/bench/artifacts.py` (new), `experiments/e12_control_spread.py` (`--column`)
**Artifacts:** `runs/e15_artifact_check.json` (strict-parse verification)

---

## 1. Every rate-network artifact was rejected by strict JSON parsers

Python's :mod:`json` writes ``NaN`` and ``Infinity`` by default — extensions that are **not in the
JSON specification** — and reads them back by default, so the non-conformance is invisible from
inside this project and obvious to everyone else. ``JSON.parse``, ``serde_json``,
``encoding/json`` and ``pandas.read_json`` all reject such files.

This was not hypothetical. An audit of the existing artifacts:

| artifact | ``NaN``/``Infinity`` tokens | strict parser |
|---|---|---|
| `e2_*`, `e3_*`, `e5_*`, `e6_*`, `e7_*`, `e9_*` | 0 | accepts |
| `e8_rate`, `e8_basis`, `e8_class_incremental`, `e8_fisher_batches`, `e8_hardened`, `e8_hardened_basis`, `e8_tuned_lambda` | 27–81 each | **rejects** |

Seven files, all of the network line, because its retention matrix is initialised to ``NaN`` for
the task pairs not yet trained — a meaningful "not applicable" that belongs in the file as
``null``. The whole network line's evidence was unreadable to a strict consumer.

**Fix.** `clfly/bench/artifacts.write_json` recursively replaces non-finite floats with ``None``
(handling numpy scalars and arrays via ``tolist``) and serialises with ``default=str``. Applied to
all four artifact writers (`e2`, `e3`, `e8`, `e12`), with 8 tests in `tests/test_artifacts.py`.

**Verified on a real run**, not just in a unit test: `e8_rate_network --methods naive --iters 40`
now writes `retention = [[0.79, null, null], [0.71, 0.88, null], [0.63, 0.85, 0.67]]`, zero raw
``NaN`` tokens, and a strict parse of the file succeeds. Before the change those three entries were
``NaN``.

**A guard I removed.** The first version re-parsed its own output with ``parse_constant`` set to
raise, to catch anything that had slipped through. A test showed it **could not fire for any
input**: ``default=str`` has already turned any unserialisable value into a *quoted* string, so the
offending token is never bare. The check and its test were deleted rather than left in as
decoration — the test now pins the real behaviour instead.

## 2. The zero-seed division, and an invalid-JSON path of a different kind

Adding `--column` to `e12` made it possible to run with a single seed, and a single seed gives a
zero standard error. The old code then wrote ``Infinity`` into the artifact — invalid JSON by the
same route as §1, and reachable by an ordinary command line rather than by an unusual payload.
`safe()` now returns a non-finite value that `write_json` turns into ``null``, and the factor is
printed either way, because for a fine partition the ratio is *below* 1 and that is the correct
reading rather than a bug.

## 3. The targeted experiment: a third of the compute for the two claims that matter

§4 of `docs/findings/2026-09-22-draw-budget.md` identified exactly two curve claims worth buying:
`side → pool4` (a pooled partition beats the annotation vocabulary's own best rung) and
`pool2 → cell_class` (the biggest single drop in the curve). A full `--control-draws 4` ladder
re-run costs ≈41 bases × 12 seeds ≈ 5 h.

It does not need to. The claims involve **three rungs** — `side` (4 groups), `pool4` (29),
`pool2` (90) — so measuring those three with K draws each costs `3 × (1 + K)` bases: at K=4,
15 bases ≈ 1.9 h, and it reports both error components directly rather than through a delta of
deltas. `e12_control_spread.py` gains `--column` so it can build the partition from any annotation
column (`--column side --min-size 1`), which makes it the instrument for one rung at a time.

## 4. An observation that is deliberately *not* treated as evidence

A two-draw smoke run of `--column side` at d = 952 reported an across-draw sd of **9e-5** — far
below the 1.1e-3 assumed for coarse partitions. That is **not** evidence against the model: it is
two draws (the sd of two points has a standard error of order 50%), on a different circuit. It is
recorded because it flags a real gap: `side` is a *balanced* 4-group partition, whereas the pooled
partitions have one group holding 867–1062 of 1307 neurons — about two-thirds of ``sum_g s_g^2``.
So the draw sd may depend on the group-size **profile** and not only on the group *count*, in which
case the 1.1e-3 figure does not transfer to `side` and the `side → pool4` budget is wrong in either
direction. `e14` measures only cell-type pooling; `side` needs its own run.

## 5. Limits

- The artifact audit covers the files present on this machine. New artifacts written through
  `write_json` are conformant by construction; anything that bypasses it is not, and there is no
  test that would notice a script added later.
- The 15-base cost estimate for the targeted run is arithmetic from the measured 37 s per
  base-seed at d = 1307 with 12 seeds. Under CPU contention it has been running nearer 100 s.
- The group-size-profile hypothesis in §4 is untested. It is written down so that the `side`
  measurement can falsify it rather than be read after the fact.
