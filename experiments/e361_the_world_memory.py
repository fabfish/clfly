"""E361 -- the world's memory: the earned label at the leak that holds nothing.

`e359` gave the world its own dynamics and found the earned label surviving a coupling; `e360` gave it a saturation
and found the benchmark unable to see it. Both manipulations act on how the world **mixes** what it carries. Neither
touches the other half of the world's rule -- how much it carries at all -- and that is the one the game the user
asked for depends on: **a world is worth having because it holds what the agent put there.**

**This unit takes the world's memory away.** `world_leak = 1.0` is the rule's endpoint, where the carried part of
`w_t = (1 - leak) * (w_{t-1} @ K.T) + leak * drive_t` is multiplied by zero, so the world's state **is** the drive:
a fixed linear function of the agent's action at that instant and of nothing earlier. The loop is still load-bearing
-- unwired, the world does not run and the read-out is a constant -- but the world remembers nothing, and a body that
wants the answer at the last step has to be saying it there.

One run at `e359`'s exact flags with `--loop-world-leak 1.0`, `--methods naive,replay`, `--repeats 20`, paired
against `e359`'s memoried world (`leak = 0.35`) at the same seeds and the same coupling draw. Five claims, registered
before the new run's reading was opened.

- **T1 -- one configuration except the world's memory.** The two runs agree on the populations, the world, the
  **coupling fingerprint**, the basis, the tasks and read-out widths, the sizes, the replicate count and the seed
  stream, differing only in `world_leak` itself. **Falsifier**: any of those differing, which would say the two runs
  are not one manipulation apart.
- **T2 -- and the instant world is learnable.** The no-memory `naive` arm's diagonal mean is at least **0.10** above
  chance. **Falsifier**: within **0.05** of chance, which would say the earned label **needs** a world that holds --
  and that the label is earned by writing rather than by saying. **Null**: between.
- **T3 -- and the answer is still earned there.** Both no-memory arms' paired channel readings are at least **0.10**
  and positive at **2 sigma**. **Falsifier**: an arm below 0.10, at or below zero, or unresolved.
- **T4 -- and the memory is worth something.** The memoried world's `naive` diagonal exceeds the instant one's by at
  least **0.05**, paired over the seeds. **Falsifier**: within **0.02**, which would say holding is worth nothing and
  the world is only a re-encoding of the current action -- the shape `e343` and `e345` found for the state read-out's
  channel, now asked of the environment's own memory. **Null**: between.
- **T5 -- and the buffer still helps there.** `replay`'s `mean_forgetting` is lower than `naive`'s by at least
  **0.05**, paired over the twenty replicates. **Falsifier**: `replay` forgets more by 0.05 or more. **Null**:
  between.

**What it cannot do.** *One endpoint*: `leak = 1.0` against 0.35, with the shape between them unrun -- and a leak
sweep is what would say whether the memory's value is a gradient or a cliff. *One coupling and one draw*: the
coupling is `e359`'s own matrix, whose shape is still unexamined and whose carry the leak multiplies away. *The
memoried reference is a different artifact*, paired by the recorded fingerprints and the per-replicate seed stream.
*And "remember" is scalar here*: the world holds eight numbers for at most a few steps, so nothing here is about a
world that keeps a long history, which is what a game with episodes would need.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the memoried coupled arms already on disk at the same seeds, and the no-memory run this unit made
MEMORY = Path("runs/e359_earned_label_coupled_20reps.json")
INSTANT = Path("runs/e361_earned_label_nomemory_20reps.json")
ARMS = ("naive", "replay")
NAIVE, REPLAY = ARMS
WORLD_READ_SHA1 = "3a7ba76b3619"
COUPLING_SHA1 = "5326f4a0edb4"
MEMORY_LEAK = 0.35
INSTANT_LEAK = 1.0
REPLICATES = 20
SIGMA = 2.0
LEARNS = 0.10
FLAT = 0.05
CARRIES = 0.10
WORTH = 0.05
NOTHING = 0.02
FORGETS = 0.05
CLAIMS = (
    ("T1", "one configuration except the world's memory",
     "The two runs agree on the populations, the world, the coupling fingerprint, the basis, the tasks and widths, "
     "the sizes, the replicate count and the seed stream, differing only in `world_leak`",
     "falsifier: any of those differing"),
    ("T2", f"and the instant world is learnable, by {LEARNS:.2f} over chance",
     "The no-memory `naive` arm's diagonal mean is at least 0.10 above chance",
     f"falsifier: within {FLAT:.2f} of chance"),
    ("T3", f"and the answer is still earned there, by {CARRIES:.2f} at 2 sigma",
     "Both no-memory arms' paired channel readings are at least 0.10 and positive at 2 sigma",
     "falsifier: an arm below 0.10, at or below zero, or unresolved"),
    ("T4", f"and the memory is worth something, by {WORTH:.2f}",
     "The memoried world's `naive` diagonal exceeds the instant one's by at least 0.05, paired over the seeds",
     f"falsifier: within {NOTHING:.2f}; null: between"),
    ("T5", f"and the buffer still helps there, by {FORGETS:.2f}",
     "`replay`'s `mean_forgetting` is lower than `naive`'s by at least 0.05, paired over the replicates",
     f"falsifier: `replay` forgets more by {FORGETS:.2f} or more"),
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
    return {"arm": arm, "ok": True, "n": len(reps), "chance": 1.0 / n_classes, "forgetting": forgetting,
            "diagonal": diagonal, "final": final, "mean_forgetting": statistics.fmean(forgetting),
            "mean_diagonal": statistics.fmean(diagonal), "mean_final": statistics.fmean(final),
            "paired": paired(channel, [0.0] * len(channel)),
            "retention": [[None if x is None else float(x) for x in row] for row in (reps[0].get("retention") or [])]}


def _facts(run: dict | None) -> dict:
    s = (run or {}).get("config") or {}
    d = (run or {}).get("env_draw") or {}
    return {"loop_world_leak": s.get("loop_world_leak"), "env_world_leak": d.get("world_leak"),
            "loop_world_coupled": bool(s.get("loop_world_coupled")), "world_coupled": d.get("world_coupled"),
            "world_coupling_sha1": d.get("world_coupling_sha1"), "world_nonlinear": d.get("world_nonlinear"),
            "readout_from_world": bool(s.get("readout_from_world")), "loop_world_dims": s.get("loop_world_dims"),
            "closed_loop": bool(s.get("closed_loop")), "repeats": s.get("repeats"),
            "circuit_size": s.get("circuit_size"), "readout_size": s.get("readout_size"), "basis": s.get("basis"),
            "seed0": s.get("seed0"), "task_names": [t.get("name") for t in (run or {}).get("tasks") or []],
            "task_readout_widths": sorted({int(t.get("n_readout")) for t in (run or {}).get("tasks") or []}),
            "world_read_sha1": d.get("world_read_sha1"), "world_drive_sha1": d.get("world_drive_sha1"),
            "cue_sha1": d.get("cue_sha1"), "action_sha1": d.get("action_sha1"),
            "feedback_sha1": d.get("feedback_sha1")}


def reading(memory_path: Path = MEMORY, instant_path: Path = INSTANT) -> dict:
    memory, instant = load(memory_path), load(instant_path)
    out = {"rows": {**{f"memory_{a}": arm_reading(memory, a) for a in ARMS},
                    **{f"instant_{a}": arm_reading(instant, a) for a in ARMS}},
           "facts": {"memory": _facts(memory), "instant": _facts(instant)},
           "runs": {"memory": Path(memory_path).name, "instant": Path(instant_path).name},
           "expected_world_read_sha1": WORLD_READ_SHA1, "expected_coupling_sha1": COUPLING_SHA1,
           "expected_replicates": REPLICATES, "expected_leaks": [MEMORY_LEAK, INSTANT_LEAK],
           "diagonal_gap": None, "instant_buffer": None}
    out["ok"] = {"memory": memory is not None and all(out["rows"][f"memory_{a}"].get("ok") for a in ARMS),
                 "instant": instant is not None and all(out["rows"][f"instant_{a}"].get("ok") for a in ARMS)}
    if out["ok"]["instant"]:
        out["instant_buffer"] = paired(out["rows"][f"instant_{REPLAY}"]["forgetting"],
                                       out["rows"][f"instant_{NAIVE}"]["forgetting"])
        if out["ok"]["memory"]:
            out["diagonal_gap"] = paired(out["rows"][f"memory_{NAIVE}"]["diagonal"],
                                         out["rows"][f"instant_{NAIVE}"]["diagonal"])
    return out


def judge(r: dict) -> list[dict]:
    rows, ok = r.get("rows") or {}, r.get("ok") or {}
    if not ok.get("instant"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the no-memory run is not on disk"}
                for c in CLAIMS]

    mem = r["facts"]["memory"]
    ins = r["facts"]["instant"]
    shared = ("readout_from_world", "loop_world_dims", "closed_loop", "repeats", "circuit_size", "readout_size",
              "basis", "seed0", "task_names", "task_readout_widths", "world_read_sha1", "world_drive_sha1",
              "cue_sha1", "action_sha1", "feedback_sha1", "world_coupling_sha1")
    differ = {k: [mem.get(k), ins.get(k)] for k in shared if (mem and mem.get(k) != ins.get(k))}
    leaks = sorted({x for x in (mem and mem.get("loop_world_leak"), ins.get("loop_world_leak")) if x is not None})
    expected = sorted(r["expected_leaks"])
    good = (not differ and ins.get("loop_world_leak") == INSTANT_LEAK
            and (mem is None or mem.get("loop_world_leak") == MEMORY_LEAK)
            and ins.get("env_world_leak") == INSTANT_LEAK
            and ins.get("world_coupling_sha1") == COUPLING_SHA1
            and ins.get("world_read_sha1") == WORLD_READ_SHA1 and ins.get("repeats") == REPLICATES
            and rows[f"instant_{NAIVE}"]["n"] == REPLICATES and rows[f"instant_{REPLAY}"]["n"] == REPLICATES)
    j1 = {"id": "T1", "measured": f"no-memory arms from `{r['runs']['instant']}` against the memoried run "
                                  f"`{r['runs']['memory']}`: circuits {ins['circuit_size']}, tasks "
                                  f"{ins['task_names']} at read-out widths {ins['task_readout_widths']}, "
                                  f"{ins['repeats']} replicates each at seed0 {ins['seed0']}, basis {ins['basis']}, "
                                  f"world read {ins['world_read_sha1']} (expected {r['expected_world_read_sha1']}), "
                                  f"coupling {ins['world_coupling_sha1']} against the memoried run's "
                                  f"{mem and mem.get('world_coupling_sha1')} (expected "
                                  f"{r['expected_coupling_sha1']}), leaks {leaks} against the expected {expected}, "
                                  f"other fields differing {differ}",
          "verdict": "MET -- one configuration except the world's memory" if good else
          f"FALSIFIER FIRED -- the runs differ beyond the leak: {differ}, leaks {leaks}, coupling "
          f"{ins.get('world_coupling_sha1')}/{mem and mem.get('world_coupling_sha1')}"}

    naive = rows[f"instant_{NAIVE}"]
    above = naive["mean_diagonal"] - naive["chance"]
    j2 = {"id": "T2", "measured": f"the no-memory `{NAIVE}` arm's diagonal mean is {naive['mean_diagonal']:.4f} "
                                  f"against a chance of {naive['chance']:.2f}, {above:+.4f} above it, over "
                                  f"{naive['n']} replicates",
          "verdict": f"MET -- the instant world is learnable, {above:+.4f} above chance" if above >= LEARNS else
          f"FALSIFIER FIRED -- only {above:+.4f} above chance: the earned label needs a world that holds" if
          above < FLAT else f"NULL -- {above:+.4f} above chance, between {FLAT:.2f} and {LEARNS:.2f}"}

    detail = "; ".join(f"`{a}` {rows[f'instant_{a}']['paired']['delta']:+.4f} at "
                       f"{_sg(rows[f'instant_{a}']['paired']['sigma'])} sigma" for a in ARMS)
    weak = [a for a in ARMS if not (rows[f"instant_{a}"]["paired"]["delta"] is not None
                                    and rows[f"instant_{a}"]["paired"]["delta"] >= CARRIES
                                    and (rows[f"instant_{a}"]["paired"]["sigma"] or 0) >= SIGMA)]
    j3 = {"id": "T3", "measured": f"the no-memory arms' paired channel readings over {naive['n']} replicates: "
                                  f"{detail}",
          "verdict": "MET -- the answer is still earned in both arms, at 2 sigma or better" if not weak else
          f"FALSIFIER FIRED -- the answer is not earned in {weak}"}

    est = r.get("diagonal_gap") or {"delta": None}
    if est.get("delta") is None:
        j4 = {"id": "T4", "measured": "the memoried-instant diagonal difference was not computable",
              "verdict": "REFUSED -- the difference was not computable"}
    else:
        j4 = {"id": "T4", "measured": f"the memoried `{NAIVE}` diagonal is "
                                      f"{rows[f'memory_{NAIVE}']['mean_diagonal']:.4f} and the instant one "
                                      f"{naive['mean_diagonal']:.4f}, {est['delta']:+.4f} apart on a sem of "
                                      f"{est['sem']:.4f} ({_sg(est['sigma'])} sigma)",
              "verdict": f"MET -- the memory is worth {est['delta']:+.4f}" if est["delta"] >= WORTH else
              f"FALSIFIER FIRED -- within {NOTHING:.2f} of it, {est['delta']:+.4f}" if est["delta"] < NOTHING else
              f"NULL -- {est['delta']:+.4f}, between {NOTHING:.2f} and {WORTH:.2f}"}

    buf = r.get("instant_buffer") or {"delta": None}
    if buf.get("delta") is None:
        j5 = {"id": "T5", "measured": "the no-memory buffer value was not computable",
              "verdict": "REFUSED -- the buffer value was not computable"}
    else:
        j5 = {"id": "T5", "measured": f"the no-memory `{REPLAY}` arm forgets "
                                      f"{rows[f'instant_{REPLAY}']['mean_forgetting']:.4f} against the no-memory "
                                      f"`{NAIVE}` arm's {naive['mean_forgetting']:.4f}, so the buffer changes it by "
                                      f"{buf['delta']:+.4f} on a sem of {buf['sem']:.4f} ({_sg(buf['sigma'])} sigma)",
              "verdict": f"MET -- the buffer still helps there by {abs(buf['delta']):.4f}" if buf["delta"] <= -FORGETS
              else f"FALSIFIER FIRED -- it makes forgetting worse by {buf['delta']:.4f}" if buf["delta"] >= FORGETS
              else f"NULL -- {buf['delta']:+.4f}, between {FORGETS:.2f} either way"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    ok = r.get("ok") or {}
    if not ok.get("instant"):
        print("== the world's memory ==\n   REFUSED -- the no-memory run is not on disk")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the world's memory ==")
    print(f"   no-memory arms from `{r['runs']['instant']}` against the memoried run `{r['runs']['memory']}`")
    print(f"\n   {'world':>8} {'arm':>7} {'final':>8} {'diagonal':>9} {'forget':>8} {'channel':>9} {'sigma':>6}")
    for key, row in r["rows"].items():
        world = key.split("_", 1)[0]
        print(f"   {world:>8} {row['arm']:>7} {row['mean_final']:8.4f} {row['mean_diagonal']:9.4f} "
              f"{row['mean_forgetting']:8.4f} {row['paired']['delta']:+9.4f} {_sg(row['paired']['sigma']):>6}")

    print("\n== the registered claims, T1-T5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e359` and `e360` changed how the world mixes what it carries; this asks whether carrying at all")
    print("    is what the earned label is worth, which is the half of the rule a game needs)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--memory", type=Path, default=MEMORY)
    ap.add_argument("--instant", type=Path, default=INSTANT)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(memory_path=args.memory, instant_path=args.instant)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
