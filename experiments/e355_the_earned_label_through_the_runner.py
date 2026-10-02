"""E355 -- the earned label through the corpus's own runner: its methods, its metrics, its instrument.

`e349` to `e354` built and tested a task whose answer exists **only in the environment** -- the head reads the
world's own state, the world is driven by the agent's own actions, and unwired the world is at rest so the read-out is
a constant and the accuracy is chance -- and every one of those units named the same gap in its own "what it cannot
do": *the loop is written here rather than taken from the runner*, so `ewc`, the block penalties and the
matched-random control do not apply and none of the numbers is comparable with the corpus's artifacts.

**This unit closes it.** `CueActionEnv` gained a `WorldReadout` wrapper beside `ClosedLoop`, which writes the
world's own state into the read-out's columns at the last step -- and because every call site in the runner computes
the head's input as `traj[:, -1, :][:, task.readout_neurons]`, the training loop, the evaluation, the Fisher blocks
and the gradients all read the environment **without any of them being edited**. Two flags expose it,
`--loop-world-dims` and `--readout-from-world`, both off by default so every artifact written before them is
bit-identical, and the runner run they drove is `runs/e355_earned_label_r32_5reps.json`.

The run is `--circuit-size 300 --iters 500 --readout-size 32 --train 96 --test 48 --repeats 5 --methods
naive,ewc-block,ewc-block-rand,replay --closed-loop --loop-symbols 4 --loop-noise 1.0 --loop-world-dims 8
--loop-world-leak 0.35 --loop-scale 1.0 --readout-from-world`, so it is four of the corpus's own arms on three
sequential tasks, with the answer read from the world. Five claims, registered before its reading was opened.

- **T1 -- and it is the earned-label configuration.** The artifact records the world read-out (`--readout-from-world`
  and a positive `--loop-world-dims`), every task's read-out is the world's own width, and every arm the command
  names has its replicates. **Falsifier**: any of those absent or different, which would mean the run measured the
  model's state while labelling itself otherwise.
- **T2 -- and the suite is learned.** `naive`'s diagonal mean is at least **0.10** above chance. **Falsifier**:
  within **0.05** of chance, which would say the runner cannot learn through the world at all. **Null**: between.
- **T3 -- and it forgets.** `naive`'s `mean_forgetting` is at least **0.05**. **Falsifier**: below **0.02**, which
  would say the runner's own protocol holds the world by itself. **Null**: between.
- **T4 -- and the buffer reduces it.** `replay`'s `mean_forgetting` is lower than `naive`'s by at least **0.05**,
  paired over replicates. **Falsifier**: `replay` forgets more by 0.05 or more. **Null**: between. `e352` measured
  **0.2188** in the local loop; this asks the same question with the runner's trainer.
- **T5 -- and the answer is earned.** Every arm's **paired channel reading** -- the same trained body read once
  through the loop and once with it unwired, the corpus's own `e338` instrument -- is positive at **2 sigma**.
  **Falsifier**: an arm at or below zero at 2 sigma, or unresolved. This is the property the whole line exists for,
  and the runner measures it without being asked.

**What it cannot do.** *One configuration and five replicates*, so T2 to T5 are five paired numbers each, and the
matched-random contrast the run also computes is reported and not claimed. *The world read-out's arms are the
corpus's methods and not its controls*: `frozen`, `frozen-bias` and the oracle line are not run, and the basis
contrast on the earned label needs the matched-random pair on more replicates than five. *One world, one leak and
one width*: `leak = 0.35`, eight dimensions and four symbols per task, with `e351`'s finding that the width is 88% of
the carrier's value and its channel's shape a seventh. *And the paired channel reading's unwired side is exact rather
than evaluated*: with the environment unwired the world does not run, so the head sees one constant and that accuracy
is computed from the rest state, which is the definition of an earned label and not a measurement of one.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUN = Path("runs/e355_earned_label_r32_5reps.json")
ARMS = ("naive", "ewc-block", "ewc-block-rand", "replay")
NAIVE, REPLAY = "naive", "replay"
SIGMA = 2.0
LEARNS = 0.10
FLAT = 0.05
FORGETS = 0.05
NOTHING = 0.02
CLAIMS = (
    ("T1", "and it is the earned-label configuration",
     "The artifact records the world read-out, every task's read-out is the world's own width, and every arm the "
     "command names has its replicates",
     "falsifier: any of those absent or different"),
    ("T2", f"and the suite is learned, by {LEARNS:.2f} over chance",
     "`naive`'s diagonal mean is at least 0.10 above chance",
     f"falsifier: within {FLAT:.2f} of chance"),
    ("T3", f"and it forgets, by {FORGETS:.2f}",
     "`naive`'s `mean_forgetting` is at least 0.05",
     f"falsifier: below {NOTHING:.2f}"),
    ("T4", f"and the buffer reduces it, by {FORGETS:.2f}",
     "`replay`'s `mean_forgetting` is lower than `naive`'s by at least 0.05, paired over replicates",
     f"falsifier: `replay` forgets more by {FORGETS:.2f} or more"),
    ("T5", f"and the answer is earned, at {SIGMA:.0f} sigma",
     "Every arm's paired channel reading is positive at 2 sigma",
     "falsifier: an arm at or below zero at 2 sigma, or unresolved"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def paired(one: list[float], two: list[float]) -> dict:
    diffs = [a - b for a, b in zip(one, two)]
    if len(diffs) < 2:
        return {"n": len(diffs), "delta": None, "sem": None, "sigma": None}
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / math.sqrt(len(diffs))
    return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": abs(mean) / sem if sem else float("inf")}


def _sg(sigma) -> str:
    return "inf" if sigma is None else f"{sigma:.2f}"


def arm_reading(run: dict | None, arm: str) -> dict:
    """One arm: its aggregates, and the paired channel reading averaged over the tasks within a replicate."""
    if not run:
        return {"arm": arm, "ok": False}
    method = (run.get("methods") or {}).get(arm)
    if not isinstance(method, dict) or not method.get("replicates"):
        return {"arm": arm, "ok": False, "why": "no replicates"}
    reps = method["replicates"]
    channel = []
    for r in reps:
        entries = r.get("paired_channel")
        if not isinstance(entries, list) or not entries:
            return {"arm": arm, "ok": False, "why": "no paired record"}
        channel.append(statistics.fmean([e["with_loop"] - e["without_loop"] for e in entries]))
    n_classes = int((run.get("tasks") or [{}])[0].get("n_classes") or 2)
    return {
        "arm": arm, "ok": True, "n": len(reps), "n_tasks": len(reps[0].get("paired_channel", [])),
        "chance": 1.0 / n_classes,
        "final_accuracy": float(method.get("final_accuracy")),
        "mean_forgetting": float(method.get("mean_forgetting")),
        "diagonal": float(statistics.fmean(method.get("learned") or [0.0])),
        "final_per_task": [float(x) for x in (reps[0].get("final_per_task") or [])],
        "forgetting_per_task": [float(x) for x in (reps[0].get("forgetting_per_task") or [])],
        "retention": [[None if x is None else float(x) for x in row] for row in (reps[0].get("retention") or [])],
        "paired": paired(channel, [0.0] * len(channel)),
        "channel_by_replicate": channel,
    }


def reading(path: Path = RUN) -> dict:
    run = load(path)
    rows = {arm: arm_reading(run, arm) for arm in ARMS}
    settings = (run or {}).get("config") or {}
    draw = (run or {}).get("env_draw") or {}
    out = {
        "run": Path(path).name, "arms": list(ARMS),
        "rows": {arm: rows[arm] for arm in ARMS},
        "readout_from_world": bool(settings.get("readout_from_world")),
        "world_dims": settings.get("loop_world_dims"),
        "world_leak": settings.get("loop_world_leak"),
        "world_modes": settings.get("loop_world_modes"),
        "closed_loop": bool(settings.get("closed_loop")),
        "replicates": settings.get("repeats"),
        "circuit_size": settings.get("circuit_size"),
        "readout_size": settings.get("readout_size"),
        "task_readout_widths": sorted({int(t.get("n_readout")) for t in (run or {}).get("tasks") or []}),
        "task_names": [t.get("name") for t in (run or {}).get("tasks") or []],
        "env_world_dims": draw.get("world_dims"),
        "env_world_drive_sha1": draw.get("world_drive_sha1"),
        "env_world_read_sha1": draw.get("world_read_sha1"),
    }
    if rows[NAIVE]["ok"] and rows[REPLAY]["ok"]:
        out["buffer_value"] = paired(
            [r["mean_forgetting"] for r in (run["methods"][REPLAY]["replicates"])],
            [r["mean_forgetting"] for r in (run["methods"][NAIVE]["replicates"])])
    return out


def judge(r: dict) -> list[dict]:
    rows = r.get("rows") or {}
    if not all(rows.get(a, {}).get("ok") for a in ARMS):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the four arms are not in the artifact"}
                for c in CLAIMS]

    widths = r["task_readout_widths"]
    good = (r["readout_from_world"] and (r["world_dims"] or 0) > 0 and r["closed_loop"]
            and widths == [int(r["world_dims"])])
    j1 = {"id": "T1", "measured": f"run `{r['run']}`: circuit size {r['circuit_size']}, {len(r['task_names'])} "
                                  f"tasks {r['task_names']} with read-out widths {widths}, four arms "
                                  f"{r['arms']}, {r['replicates']} replicates, closed loop {r['closed_loop']}, "
                                  f"`--readout-from-world` {r['readout_from_world']}, world dimensions "
                                  f"{r['world_dims']} at leak {r['world_leak']} (the draw's own "
                                  f"{r['env_world_dims']}, drive {r['env_world_drive_sha1']}, read "
                                  f"{r['env_world_read_sha1']})",
          "verdict": "MET -- the run reads the environment and says so" if good else
          f"FALSIFIER FIRED -- the read-out is not the world's: flag {r['readout_from_world']}, dimensions "
          f"{r['world_dims']}, widths {widths}"}

    naive = rows[NAIVE]
    above = naive["diagonal"] - naive["chance"]
    j2 = {"id": "T2", "measured": f"`{NAIVE}`'s diagonal mean is {naive['diagonal']:.4f} against a chance of "
                                  f"{naive['chance']:.2f}, {above:+.4f} above it, and its final accuracy is "
                                  f"{naive['final_accuracy']:.4f}",
          "verdict": f"MET -- the runner learns through the world, {above:+.4f} above chance" if above >= LEARNS
          else f"FALSIFIER FIRED -- only {above:+.4f} above chance" if above < FLAT else
          f"NULL -- {above:+.4f} above chance, between {FLAT:.2f} and {LEARNS:.2f}"}

    forget = naive["mean_forgetting"]
    j3 = {"id": "T3", "measured": f"`{NAIVE}`'s `mean_forgetting` is {forget:.4f}, its per-task forgetting "
                                  f"{[round(x, 4) for x in naive['forgetting_per_task']]} and its retention "
                                  f"{[[None if x is None else round(x, 3) for x in row] for row in naive['retention']]}",
          "verdict": f"MET -- the suite forgets, {forget:.4f}" if forget >= FORGETS else
          f"FALSIFIER FIRED -- below {NOTHING:.2f}, {forget:.4f}" if forget < NOTHING else
          f"NULL -- {forget:.4f}, between {NOTHING:.2f} and {FORGETS:.2f}"}

    est = r.get("buffer_value") or {"delta": None, "sem": None, "sigma": None}
    if est["delta"] is None:
        j4 = {"id": "T4", "measured": "the paired buffer value was not computable",
              "verdict": "REFUSED -- the paired buffer value was not computable"}
    else:
        j4 = {"id": "T4", "measured": f"`{REPLAY}` forgets {rows[REPLAY]['mean_forgetting']:.4f} against "
                                      f"`{NAIVE}`'s {forget:.4f}, so the buffer changes it by {est['delta']:+.4f} "
                                      f"on a sem of {est['sem']:.4f} ({_sg(est['sigma'])} sigma)",
              "verdict": f"MET -- the buffer reduces it by {abs(est['delta']):.4f}" if est["delta"] <= -FORGETS else
              f"FALSIFIER FIRED -- it makes forgetting worse by {est['delta']:.4f}" if est["delta"] >= FORGETS else
              f"NULL -- {est['delta']:+.4f}, between {FORGETS:.2f} either way"}

    detail = "; ".join(f"`{a}` {rows[a]['paired']['delta']:+.4f} at {_sg(rows[a]['paired']['sigma'])} sigma"
                       for a in ARMS)
    weak = [a for a in ARMS if not (rows[a]["paired"]["delta"] is not None
                                    and rows[a]["paired"]["delta"] > 0
                                    and (rows[a]["paired"]["sigma"] or 0) >= SIGMA)]
    j5 = {"id": "T5", "measured": f"the paired channel reading per arm (the same trained body through the loop and "
                                  f"unwired): {detail}",
          "verdict": "MET -- every arm's answer is earned, at 2 sigma or better" if not weak else
          f"FALSIFIER FIRED -- the answer is not earned in {weak}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    rows = r.get("rows") or {}
    if not all(rows.get(a, {}).get("ok") for a in ARMS):
        print("== the earned label through the runner ==\n   REFUSED -- the four arms are not in the artifact")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the earned label through the runner ==")
    print(f"   run `{r['run']}`: {r['circuit_size']} circuit, {len(r['task_names'])} tasks through a "
          f"{r['world_dims']}-dimensional world at leak {r['world_leak']}, {r['replicates']} replicates per arm")
    print(f"\n   {'arm':>15} {'final acc':>10} {'diagonal':>9} {'forget':>8} {'channel':>9} {'sigma':>6}")
    for arm in ARMS:
        row = rows[arm]
        print(f"   {arm:>15} {row['final_accuracy']:10.4f} {row['diagonal']:9.4f} {row['mean_forgetting']:8.4f} "
              f"{row['paired']['delta']:+9.4f} {_sg(row['paired']['sigma']):>6}")
    print(f"   `{NAIVE}`'s retention: "
          f"{[[None if x is None else round(x, 3) for x in row] for row in rows[NAIVE]['retention']]}")

    print("\n== the registered claims, T1-T5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e349` to `e354` built the earned label in a local loop; the `WorldReadout` wrapper makes the")
    print("    runner's own methods, metrics and paired-channel instrument apply to it unchanged)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", type=Path, default=RUN)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(path=args.run)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
