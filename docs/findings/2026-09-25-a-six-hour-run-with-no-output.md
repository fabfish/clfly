# A six-hour run with no output, and the one line per replicate that fixes it

**Date:** 2026-09-25
**Measured on:** `e178` (the `side` rung at cs = 300, three arms, 144 replicates), running while this was written.
**Changed:** `experiments/e8_rate_network.py`, the replicate loop — a heartbeat print, no numerical change.

---

## 1. What the run looked like from outside, measured

The command pipes through `tail -6`, so nothing is emitted until it exits, and `--json-out` is written **once at the
end**. Between those two facts a six-hour run is completely opaque:

| quantity | value | where it comes from |
|---|---|---|
| start | **2026-09-25 04:54:40** | the process's own `StartTime` |
| CPU time so far | **270254 s ≈ 75 h of thread-time** | the process's `CPU`, across the ~20 torch threads ≈ 3.75 h wall |
| working set | **3.66 GB** | the process's `WS` |
| output lines | **0** | the task's log file is empty |
| the estimate | **≈ 6.5 h** | `e177`'s one-replicate probe at 162 s per replicate × 144 |

So the run is healthy and is **past its own estimate** (5.4 h at the time of measuring, estimate 6.5 h → due about
11:20), and the only way to know that is to interrogate the operating system for a process's CPU time. The
registration's price was an extrapolation from one replicate, and until the artifact lands there is no way to check
the extrapolation against the thing it extrapolates — which is the *cheap* half of the problem. The expensive half is
that a run which hangs is indistinguishable from a run which is working, for six hours.

## 2. Why the artifact is still written only at the end, and what was actually missing

Writing the JSON incrementally would be worse than the silence: `rule 47` records that an artifact's timestamp is
the run's **end**, and `e97`'s census already contains a document citing an aborted run's file. A partial artifact
is a claim that the run finished, and the project's whole provenance discipline rests on that claim being true.

**So the fix is a print, not a file**: one line per replicate, with the replicate's own duration, the elapsed total
and the projection from what has actually been done —

```
[17/432] ewc-block replicate 17/144 in 168 s; elapsed 48.1 min, projected 40.6 h
```

Shape of the line matters less than that it exists: the same command now reports its own progress, so a hang is
visible within one replicate (~3 min here) rather than at hour seven, and the projection is printed beside the
extrapolated estimate while both are still estimates. `flush=True` because the harness pipes stdout and a buffered
heartbeat is not a heartbeat.

## 3. Verification

The test suite runs `e8_rate_network.py` in-process twice with tiny settings, and both runs now print their line:

```
[1/1] ewc replicate 1/1 in 2 s; elapsed 0.0 min, projected 0.0 min
[1/1] ewc replicate 1/1 in 0 s; elapsed 0.0 min, projected 0.0 min
```

The replicate loop changed from a list comprehension to an explicit loop over the same seeds in the same order, so
nothing numerical moves — which the full suite confirms, including `test_fisher_replay.py`'s bit-identity check,
the project's strictest numerical test.

## 4. Limits, stated so the heartbeat is not oversold

- **It does not make a run recoverable.** A crashed run still loses everything since the last completed replicate;
  the heartbeat only tells you where it died.
- **It does not check the estimate.** It prints a projection *from the replicates so far*, which is a different
  number from the probe's extrapolation for at least the first few replicates — and a projection from an early
  sample is exactly the kind of estimate this project has already learned to distrust (`rule 49`).
- **It is one run's worth of motivation.** The claim it rests on is not "output is nice": it is that **the loop's
  cost is per-replicate and the artifact is written at the end**, which holds for every runner here that has a
  replicate loop.

## Reproduce

```
uv run pytest tests/test_fisher_replay.py -q -s        # two tiny runs, both printing their heartbeat
uv run python experiments/e8_rate_network.py --help     # the flag set is unchanged
```
