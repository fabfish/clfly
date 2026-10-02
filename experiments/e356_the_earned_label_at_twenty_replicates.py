"""E356 -- the earned label at twenty replicates: the corpus's own method contrast, on a substrate it has not run.

`e355` closed the gap every unit from `e349` to `e354` had named -- the earned label now runs through the corpus's
own runner, with its optimiser, its metrics and its paired-channel instrument -- and it closed with what five
replicates could not do: *"one configuration and five replicates ... the basis contrast needs the matched-random pair
on many more replicates than five"*, and its own power note put detectability at 0.106.

**This unit buys the replicates for the two arms the corpus's headline contrast is between.** One run, the same
configuration as `e355`'s but with `--repeats 20` and `--methods naive,ewc-block,replay`: twenty paired replicates
of `replay` against the penalty, on a task whose answer exists only in the environment. That makes the earned label
**another substrate for the method contrast** -- `e276` found `replay` beating `ewc-block` by 3.30 to 11.84 sigma on
the state read-out, `e346` found the ordering travelling across twenty-six experiments, and `e347` found the family
that disagreed resolving at 3.11 sigma once it was powered. Whether it holds where the answer is read from the world
is a question the corpus has never asked, and twenty replicates is the power to ask it.

The run is `--circuit-size 300 --iters 500 --readout-size 32 --train 96 --test 48 --repeats 20 --methods
naive,ewc-block,replay --closed-loop --loop-symbols 4 --loop-noise 1.0 --loop-world-dims 8 --loop-world-leak 0.35
--loop-scale 1.0 --readout-from-world`, into `runs/e356_earned_label_r32_20reps.json`. Four claims, registered
before its reading was opened.

- **T1 -- and it is the earned-label configuration.** The artifact records the world read-out, every task's read-out
  is the world's own width, the world is the same draw `e355` and the local loop used, and all three arms carry
  **twenty** replicates. **Falsifier**: any of those absent or different.
- **T2 -- and the ordering resolves on the earned label.** `replay`'s `mean_forgetting` is lower than
  `ewc-block`'s by at least **0.05**, paired over the twenty replicates, at **2 sigma**. **Falsifier**: `replay`
  forgets **more** by 0.05 or more, i.e. the ordering inverting on this substrate. **Null**: unresolved. This is
  `e276`'s contrast asked where the answer lives in the environment.
- **T3 -- and it is not paid for on the newest task.** `replay`'s diagonal mean is within **0.05** of
  `ewc-block`'s. **Falsifier**: `replay` is lower by **0.10** or more, which would say the retention is bought out
  of acquisition. **Null**: between.
- **T4 -- and the answer is earned in every arm, at 2 sigma.** Every arm's paired channel reading -- the same
  trained body read once through the loop and once with it unwired -- is at least **0.10** and positive at **2
  sigma**. **Falsifier**: an arm below 0.10, at or below zero, or unresolved. `e355` measured this at five
  replicates and 6.06 to 16.64 sigma; this asks whether twenty replicates move it.

**What it cannot do.** *Three arms and no matched-random pair*: the basis contrast -- `ewc-block` against the
size-matched random partition, the corpus's own headline and the null eleven audits left standing -- is **not** in
this run, so nothing here is about the connectome's block structure; five replicates of it in `e355` were a 0.0125
near-tie and that is all the corpus now has on the earned label. *One world, one leak and one width*: `leak = 0.35`,
eight dimensions and four symbols per task, with `e351`'s finding that the width is 88% of the carrier's value. *And
the paired reading's unwired side is exact rather than evaluated*: an unwired world does not run, so the head sees
one constant and that accuracy is computed from the rest state.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUN = Path("runs/e356_earned_label_r32_20reps.json")
ARMS = ("naive", "ewc-block", "replay")
NAIVE, PENALTY, REPLAY = ARMS
#: the world `e355` and the local loop drew, so a reading of this run is comparable with theirs to the fingerprint
WORLD_READ_SHA1 = "3a7ba76b3619"
REPLICATES = 20
SIGMA = 2.0
CARRIES = 0.10
FORGETS = 0.05
SAME = 0.05
SAME_FIRES = 0.10
CLAIMS = (
    ("T1", "and it is the earned-label configuration",
     f"The artifact records the world read-out, every task's read-out is the world's own width, the world is the same "
     f"draw as `e355`'s, and all three arms carry {REPLICATES} replicates",
     "falsifier: any of those absent or different"),
    ("T2", f"and the ordering resolves on the earned label, by {FORGETS:.2f}",
     f"`{REPLAY}`'s `mean_forgetting` is lower than `{PENALTY}`'s by at least 0.05, paired over the replicates, at "
     f"2 sigma",
     f"falsifier: `{REPLAY}` forgets more by {FORGETS:.2f} or more; null: unresolved"),
    ("T3", f"and it is not paid for on the newest task, within {SAME:.2f}",
     f"`{REPLAY}`'s diagonal mean is within 0.05 of `{PENALTY}`'s",
     f"falsifier: `{REPLAY}` is lower by {SAME_FIRES:.2f} or more"),
    ("T4", f"and the answer is earned in every arm, by {CARRIES:.2f} at 2 sigma",
     "Every arm's paired channel reading is at least 0.10 and positive at 2 sigma",
     "falsifier: an arm below 0.10, at or below zero, or unresolved"),
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
        return {"n": len(diffs), "delta": None, "sem": None, "sigma": None, "vals": diffs}
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / math.sqrt(len(diffs))
    return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": abs(mean) / sem if sem else float("inf"),
            "vals": diffs}


def _sg(sigma) -> str:
    return "inf" if sigma is None else f"{sigma:.2f}"


def arm_reading(run: dict | None, arm: str) -> dict:
    """One arm: its per-replicate numbers and its paired channel reading, averaged over the tasks."""
    if not run:
        return {"arm": arm, "ok": False}
    method = (run.get("methods") or {}).get(arm)
    if not isinstance(method, dict) or not method.get("replicates"):
        return {"arm": arm, "ok": False, "why": "no replicates"}
    reps = method["replicates"]
    channel, forgetting, diagonal, final = [], [], [], []
    for r in reps:
        entries = r.get("paired_channel")
        if not isinstance(entries, list) or not entries:
            return {"arm": arm, "ok": False, "why": "no paired record"}
        channel.append(statistics.fmean([e["with_loop"] - e["without_loop"] for e in entries]))
        forgetting.append(float(r["mean_forgetting"]))
        diagonal.append(float(statistics.fmean(r["learned"])))
        final.append(float(r["final_accuracy"]))
    n_classes = int((run.get("tasks") or [{}])[0].get("n_classes") or 2)
    return {"arm": arm, "ok": True, "n": len(reps), "n_tasks": len(reps[0]["paired_channel"]),
            "chance": 1.0 / n_classes, "forgetting": forgetting, "diagonal": diagonal, "final": final,
            "mean_forgetting": statistics.fmean(forgetting), "mean_diagonal": statistics.fmean(diagonal),
            "mean_final": statistics.fmean(final),
            "paired": paired(channel, [0.0] * len(channel)),
            "retention": [[None if x is None else float(x) for x in row] for row in (reps[0].get("retention") or [])]}


def reading(path: Path = RUN) -> dict:
    run = load(path)
    rows = {arm: arm_reading(run, arm) for arm in ARMS}
    settings = (run or {}).get("config") or {}
    draw = (run or {}).get("env_draw") or {}
    out = {"run": Path(path).name, "arms": list(ARMS), "rows": rows,
           "readout_from_world": bool(settings.get("readout_from_world")),
           "world_dims": settings.get("loop_world_dims"), "world_leak": settings.get("loop_world_leak"),
           "world_modes": settings.get("loop_world_modes"), "closed_loop": bool(settings.get("closed_loop")),
           "replicates": settings.get("repeats"), "circuit_size": settings.get("circuit_size"),
           "readout_size": settings.get("readout_size"),
           "task_names": [t.get("name") for t in (run or {}).get("tasks") or []],
           "task_readout_widths": sorted({int(t.get("n_readout")) for t in (run or {}).get("tasks") or []}),
           "env_world_dims": draw.get("world_dims"), "env_world_read_sha1": draw.get("world_read_sha1"),
           "expected_world_read_sha1": WORLD_READ_SHA1}
    if rows[REPLAY]["ok"] and rows[PENALTY]["ok"]:
        out["forgetting_contrast"] = paired(rows[REPLAY]["forgetting"], rows[PENALTY]["forgetting"])
        out["diagonal_contrast"] = paired(rows[REPLAY]["diagonal"], rows[PENALTY]["diagonal"])
        out["final_contrast"] = paired(rows[REPLAY]["final"], rows[PENALTY]["final"])
    if rows[NAIVE]["ok"]:
        out["naive_forgetting"] = rows[NAIVE]["mean_forgetting"]
        out["naive_sem"] = (statistics.stdev(rows[NAIVE]["forgetting"]) / math.sqrt(rows[NAIVE]["n"]))
    return out


def judge(r: dict) -> list[dict]:
    rows = r.get("rows") or {}
    if not all(rows.get(a, {}).get("ok") for a in ARMS):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the three arms are not in the artifact"}
                for c in CLAIMS]

    widths = r["task_readout_widths"]
    good = (r["readout_from_world"] and (r["world_dims"] or 0) > 0 and r["closed_loop"]
            and widths == [int(r["world_dims"])] and r["env_world_read_sha1"] == WORLD_READ_SHA1
            and all(rows[a]["n"] == REPLICATES for a in ARMS))
    j1 = {"id": "T1", "measured": f"run `{r['run']}`: circuit size {r['circuit_size']}, tasks {r['task_names']} "
                                  f"with read-out widths {widths}, arms {r['arms']} at {r['replicates']} "
                                  f"replicates each, closed loop {r['closed_loop']}, `--readout-from-world` "
                                  f"{r['readout_from_world']}, world dimensions {r['world_dims']} at leak "
                                  f"{r['world_leak']}, and the draw's world read fingerprint "
                                  f"{r['env_world_read_sha1']} against `e355`'s {r['expected_world_read_sha1']}",
          "verdict": "MET -- twenty replicates of the earned-label configuration" if good else
          f"FALSIFIER FIRED -- flag {r['readout_from_world']}, dimensions {r['world_dims']}, widths {widths}, "
          f"fingerprint {r['env_world_read_sha1']}, replicates "
          f"{ {a: rows[a]['n'] for a in ARMS} }"}

    est = r.get("forgetting_contrast") or {"delta": None}
    if est.get("delta") is None:
        j2 = {"id": "T2", "measured": "the paired contrast was not computable",
              "verdict": "REFUSED -- the paired contrast was not computable"}
    else:
        resolved = (est["sigma"] or 0) >= SIGMA
        j2 = {"id": "T2", "measured": f"`{REPLAY}` forgets {rows[REPLAY]['mean_forgetting']:.4f} and "
                                      f"`{PENALTY}` {rows[PENALTY]['mean_forgetting']:.4f}, so the ordering is "
                                      f"{est['delta']:+.4f} on a sem of {est['sem']:.4f} "
                                      f"({_sg(est['sigma'])} sigma) over {est['n']} paired replicates",
              "verdict": f"MET -- the ordering resolves on the earned label, {est['delta']:+.4f} at "
                         f"{est['sigma']:.2f} sigma" if (est["delta"] <= -FORGETS and resolved) else
              f"FALSIFIER FIRED -- it inverts, `{REPLAY}` ahead by {est['delta']:.4f} at "
              f"{est['sigma']:.2f} sigma" if (est["delta"] >= FORGETS and resolved) else
              f"NULL -- {est['delta']:+.4f} at {_sg(est['sigma'])} sigma, unresolved"}

    d = (r.get("diagonal_contrast") or {}).get("delta")
    if d is None:
        j3 = {"id": "T3", "measured": "the diagonal contrast was not computable",
              "verdict": "REFUSED -- the diagonal contrast was not computable"}
    else:
        j3 = {"id": "T3", "measured": f"`{REPLAY}`'s diagonal mean is {rows[REPLAY]['mean_diagonal']:.4f} and "
                                      f"`{PENALTY}`'s {rows[PENALTY]['mean_diagonal']:.4f}, {d:+.4f} apart, and "
                                      f"their final accuracies differ by "
                                      f"{(r.get('final_contrast') or {}).get('delta', float('nan')):+.4f}",
              "verdict": f"MET -- the retention is not paid for on the newest task, {d:+.4f}" if d >= -SAME else
              f"FALSIFIER FIRED -- `{REPLAY}` is lower by {abs(d):.4f}" if d <= -SAME_FIRES else
              f"NULL -- {d:+.4f}, between {-SAME_FIRES:.2f} and {-SAME:.2f}"}

    detail = "; ".join(f"`{a}` {rows[a]['paired']['delta']:+.4f} at {_sg(rows[a]['paired']['sigma'])} sigma"
                       for a in ARMS)
    weak = [a for a in ARMS if not (rows[a]["paired"]["delta"] is not None
                                    and rows[a]["paired"]["delta"] >= CARRIES
                                    and (rows[a]["paired"]["sigma"] or 0) >= SIGMA)]
    j4 = {"id": "T4", "measured": f"the paired channel reading per arm over {rows[NAIVE]['n']} replicates: {detail}",
          "verdict": "MET -- every arm's answer is earned, at 2 sigma or better" if not weak else
          f"FALSIFIER FIRED -- the answer is not earned in {weak}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    rows = r.get("rows") or {}
    if not all(rows.get(a, {}).get("ok") for a in ARMS):
        print("== the earned label at twenty replicates ==\n   REFUSED -- the three arms are not in the artifact")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the earned label at twenty replicates ==")
    print(f"   run `{r['run']}`: {r['circuit_size']} circuit, {len(r['task_names'])} tasks through a "
          f"{r['world_dims']}-dimensional world at leak {r['world_leak']}, {r['replicates']} replicates per arm")
    print(f"\n   {'arm':>11} {'final':>8} {'diagonal':>9} {'forget':>8} {'forget sem':>11} {'channel':>9} {'sigma':>6}")
    for arm in ARMS:
        row = rows[arm]
        print(f"   {arm:>11} {row['mean_final']:8.4f} {row['mean_diagonal']:9.4f} {row['mean_forgetting']:8.4f} "
              f"{statistics.stdev(row['forgetting']) / math.sqrt(row['n']):11.4f} {row['paired']['delta']:+9.4f} "
              f"{_sg(row['paired']['sigma']):>6}")
    est = r.get("forgetting_contrast") or {}
    if est.get("delta") is not None:
        print(f"   `{REPLAY}` minus `{PENALTY}` on forgetting: {est['delta']:+.4f} on a sem of {est['sem']:.4f} "
              f"({_sg(est['sigma'])} sigma), per replicate {[round(x, 3) for x in est['vals']]}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e276` found `replay` over the penalty at 3.30 to 11.84 sigma and `e346` found the ordering")
    print("    travelling; this asks it on a substrate where the answer is read from the environment)")
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
