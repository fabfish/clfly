"""E337 -- does it replicate on another seed stream? The thread's headline effect, asked of a second one.

`e333` measured `replay`'s mean forgetting **rising 0.0375 at 2.45 sigma** when the world's channel acquired a
transition rule, on five replicates at `--seed0 0`. `e334`, `e335` and `e336` then excluded four accounts of it --
the stored features fitting worse (0.32 sigma), the buffer's contents differing (byte-identical), the body drifting
further (2.93% less) and the update's **direction** differing (which turned out not to be a reproducible quantity
at five replicates at all, sitting on the 0.0625 random-overlap floor of its own 256-dimensional subspace).

**And `e336` left a question that sits under all four.** Its within-run cosines are at the random floor, which means
that at five replicates **a single seed stream carries very little information about a configuration** -- and every
number in this chain, including the 2.45 sigma that started it, comes from **one** stream. So the unit this chain
needs before any fifth mechanism is not another account: it is the same measurement on a **second** seed stream.

**This runs it.** `e333`'s two worlds again, at `--seed0 4` instead of 0, five replicates each and the same
everything else -- so the replicate seeds are `4, 104, 204, 304, 404` against `0, 100, 200, 300, 400`, a wholly
different sample of trajectories.

Four claims, registered before these runs' readings. The statistic is `replay`'s `mean_forgetting` difference,
carried minus instantaneous, paired by replicate index within a stream.

- **T1 -- and the two streams are independent samples.** Each stream's two runs agree on the circuit, read-out,
  task names, replicate count, cue symbols, cue noise and world state count; within a stream the configs differ only
  in the leak; and the streams' `seed0` differ. **Falsifier**: a differing field inside a stream, or two streams
  whose seed schedules are the same.
- **T2 -- and the sign replicates.** The difference is **positive** on the second stream as it was on the first.
  **Falsifier**: a negative difference, which would make the original sign the first stream's and not the world's.
- **T3 -- and the size replicates.** The second stream's difference is at least **half** the first's. **Falsifier**:
  below **a fifth** of it, which would say the effect shrinks by an order of magnitude on a redraw. **Null**:
  between a fifth and a half.
- **T4 -- and the first stream's own interval is honest about what five replicates buy.** The first stream's
  difference is resolved at **2 sigma** in the direction `e333` reported, restated here on the pair this unit reads
  rather than taken from `e333`'s prose. **Falsifier**: a first-stream difference below 2 sigma on this reader. This
  is the check that the unit is reading the same object `e333` did.

**What it cannot do.** *Two streams*: another redraw would change the answer again, and two points give a span and
not a standard deviation -- the honest statistic across two seeds is the pair, not an interval. *Five replicates per
run*: `e336` established that this many replicates put a direction measurement on its noise floor, and nothing here
says that five is enough for a retention difference either -- T3 is stated as a ratio of two point estimates for
that reason. *One arm*: `naive`, `ewc` and the block arms are not run. *One circuit, one read-out width and one
pair of worlds*: `e332`'s other sign, retention *improving* when the response became a state, is not asked. *And a
failed replication would not say the effect is absent*: it would say this design cannot see it at five replicates,
which is a statement about the instrument.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import duration_seconds, write_json

RUNS = Path("runs")
#: the two streams, each as (instantaneous, carried)
STREAMS = {
    "seed0=0": (RUNS / "e333_world_instant.json", RUNS / "e333_world_carry.json"),
    "seed0=4": (RUNS / "e337_stream4_instant.json", RUNS / "e337_stream4_carry.json"),
}
ORDER = ("seed0=0", "seed0=4")
ARMS = ("naive", "replay")
ARM = "replay"
SIGMA = 2.0
HALF = 0.5
FIFTH = 0.2
CLAIMS = (
    ("T1", "and the two streams are independent samples",
     "Each stream's two runs agree on circuit, read-out, task names, replicate count, cue symbols, cue noise and "
     "world state count; within a stream the configs differ only in the leak; and the streams' seed schedules differ",
     "falsifier: a differing field inside a stream, or two streams whose seed schedules are the same"),
    ("T2", "and the sign replicates",
     f"`{ARM}`'s carried-minus-instantaneous forgetting difference is positive on the second stream as on the first",
     "falsifier: a negative difference, which would make the original sign the first stream's"),
    ("T3", f"and the size replicates, at least {HALF:.0%} of the first stream's",
     f"The second stream's difference is at least {HALF:.0%} of the first's",
     f"falsifier: below {FIFTH:.0%} of it, an order of magnitude smaller on a redraw"),
    ("T4", f"and the first stream's difference is resolved at {SIGMA:.0f} sigma on this reader",
     f"The first stream's paired difference is at least {SIGMA:.0f} sigma in the direction `e333` reported",
     "falsifier: below it, which would say this reader is not reading what `e333` read"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def replicates(run: dict | None, arm: str = ARM) -> list[dict]:
    if not run:
        return []
    method = run.get("methods", {}).get(arm)
    return list(method.get("replicates", [])) if isinstance(method, dict) else []


def paired(one: list[float], two: list[float]) -> dict:
    diffs = [a - b for a, b in zip(one, two)]
    if len(diffs) < 2:
        return {"n": len(diffs), "delta": None, "sem": None, "sigma": None}
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / math.sqrt(len(diffs))
    return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": abs(mean) / sem if sem else float("inf")}


def stream_reading(instant: dict | None, carry: dict | None) -> dict:
    if not instant or not carry:
        return {"ok": False}
    ci, cc = instant.get("config", {}), carry.get("config", {})
    ei, ec = instant.get("env_draw") or {}, carry.get("env_draw") or {}
    return {
        "ok": True,
        "circuits": [instant.get("circuit"), carry.get("circuit")],
        "readout": [instant.get("readout", {}).get("subset_sha1"), carry.get("readout", {}).get("subset_sha1")],
        "task_names": [[t.get("name") for t in instant.get("tasks", [])],
                       [t.get("name") for t in carry.get("tasks", [])]],
        "counts": [len(replicates(instant)), len(replicates(carry))],
        "seed0": [ci.get("seed0"), cc.get("seed0")],
        "leaks": [ei.get("world_leak"), ec.get("world_leak")],
        "env_diff": {k: [ei.get(k), ec.get(k)] for k in sorted(set(ei) | set(ec))
                     if k != "world_leak" and ei.get(k) != ec.get(k)},
        "config_diff": {k: [ci.get(k), cc.get(k)] for k in sorted(set(ci) | set(cc))
                        if k not in ("json_out", "loop_world_leak") and ci.get(k) != cc.get(k)},
        "forgetting": paired([r["mean_forgetting"] for r in replicates(carry)],
                             [r["mean_forgetting"] for r in replicates(instant)]),
        "accuracy": paired([r["final_accuracy"] for r in replicates(carry)],
                           [r["final_accuracy"] for r in replicates(instant)]),
        "means": {"instant": instant["methods"][ARM].get("mean_forgetting"),
                  "carry": carry["methods"][ARM].get("mean_forgetting")},
        "timing_s": [duration_seconds(instant), duration_seconds(carry)],
    }


def reading(streams=None) -> dict:
    streams = streams or STREAMS
    out = {"streams": {}, "arms": list(ARMS)}
    for tag in ORDER:
        if tag not in streams:
            continue
        a, b = streams[tag]
        out["streams"][tag] = stream_reading(load(a), load(b))
    out["runs"] = sum(1 for s in out["streams"].values() if s.get("ok")) * 2
    if out["runs"] < 4:
        out["missing"] = [tag for tag in ORDER if not out["streams"].get(tag, {}).get("ok")]
    return out


def judge(r: dict) -> list[dict]:
    s = r.get("streams") or {}
    first, second = s.get("seed0=0", {}), s.get("seed0=4", {})
    if not first.get("ok") or not second.get("ok"):
        return [{"id": c[0], "measured": f"streams present: {sorted(k for k, v in s.items() if v.get('ok'))}",
                 "verdict": "REFUSED -- both streams are not on disk"} for c in CLAIMS]

    same_each = all(st["circuits"][0] == st["circuits"][1] and st["readout"][0] == st["readout"][1]
                    and st["task_names"][0] == st["task_names"][1] and st["counts"][0] == st["counts"][1]
                    and st["seed0"][0] == st["seed0"][1] and st["leaks"][0] == 1.0 and st["leaks"][1] < 1.0
                    and not st["config_diff"] and not st["env_diff"] for st in (first, second))
    distinct = first["seed0"][0] != second["seed0"][0]
    j1 = {"id": "T1", "measured": f"stream `seed0={first['seed0'][0]}`: circuits {first['circuits']}, read-out "
                                  f"{first['readout']}, tasks {first['task_names'][0]}, counts {first['counts']}, "
                                  f"leaks {first['leaks']}, config differing {first['config_diff']}, environment "
                                  f"differing {first['env_diff']}; stream `seed0={second['seed0'][0]}`: circuits "
                                  f"{second['circuits']}, counts {second['counts']}, leaks {second['leaks']}, config "
                                  f"differing {second['config_diff']}, environment differing {second['env_diff']}; "
                                  f"the streams' seeds differ {distinct}",
          "verdict": "MET -- two independent streams of one configuration in two worlds" if same_each and distinct
          else f"FALSIFIER FIRED -- inside a stream {[first['config_diff'], second['config_diff']]}, "
               f"distinct seeds {distinct}"}

    d1, d2 = first["forgetting"], second["forgetting"]
    j2 = {"id": "T2", "measured": f"`{ARM}`'s carried-minus-instantaneous forgetting: {d1['delta']:+.4f} on the "
                                  f"first stream ({d1['sigma']:.2f} sigma) and {d2['delta']:+.4f} on the second "
                                  f"({d2['sigma']:.2f} sigma)",
          "verdict": "MET -- the sign replicates" if d1["delta"] > 0 and d2["delta"] > 0 else
                     f"FALSIFIER FIRED -- the first stream {d1['delta']:+.4f}, the second {d2['delta']:+.4f}"}

    ratio = (abs(d2["delta"]) / abs(d1["delta"])) if d1["delta"] else None
    j3 = {"id": "T3", "measured": f"the second stream's difference is {'n/a' if ratio is None else f'{ratio:.2f}x'} "
                                  f"the first's ({d2['delta']:+.4f} against {d1['delta']:+.4f})",
          "verdict": ("REFUSED -- the first stream's difference is zero" if ratio is None else
                      f"MET -- the size replicates at {ratio:.2f}x" if ratio >= HALF else
                      f"FALSIFIER FIRED -- it is {ratio:.2f}x the first's" if ratio < FIFTH else
                      f"NULL -- {ratio:.2f}x, between {FIFTH:.0%} and {HALF:.0%}")}

    j4 = {"id": "T4", "measured": f"the first stream's paired difference is {d1['delta']:+.4f} on a sem of "
                                  f"{d1['sem']:.4f}, i.e. {d1['sigma']:.2f} sigma over {d1['n']} replicates",
          "verdict": f"MET -- this reader reads what `e333` read, at {d1['sigma']:.2f} sigma" if
          d1["delta"] > 0 and d1["sigma"] >= SIGMA else
          f"FALSIFIER FIRED -- {d1['sigma']:.2f} sigma, in the direction {d1['delta']:+.4f}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== does it replicate on another seed stream ==")
    for tag in ORDER:
        st = (r.get("streams") or {}).get(tag)
        if not st or not st.get("ok"):
            print(f"   {tag}: REFUSED -- one of its two runs is missing")
            continue
        print(f"   {tag}: {st['circuits'][0]}, {st['counts'][0]} replicates each, leaks {st['leaks']}, "
              f"forgetting {st['means']['instant']:.4f} instantaneous against {st['means']['carry']:.4f} carried, "
              f"delta {st['forgetting']['delta']:+.4f} ({st['forgetting']['sigma']:.2f} sigma)")
        print(f"          config differing {st['config_diff'] or 'none'}, environment differing "
              f"{st['env_diff'] or 'none'}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e333` measured this on one seed stream and four units then excluded four accounts of it; `e336`")
    print("    showed five replicates put a direction on its noise floor, so the effect itself is asked of a redraw)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading()
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
