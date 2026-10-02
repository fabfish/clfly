"""E364 -- can a trained body beat the interface? The earned label at the read step, on a world that listens to the cue.

`e363` told apart the two causes `e362`'s finding had named together, in six frozen rolls: at the step the world
read-out reads, **both** drive sources carry nothing about the cue (**0.2578, exactly chance**), so the timing is the
hard limit; and one step earlier the sources separate sharply (**0.8555** for a world whose drive reads the cue's own
neurons against **0.2578** for one reading the action population), so the populations decide what the one step the
timing allows is worth. Its own "what it cannot do" says what is missing: *"a frozen body ... the trained versions of
five of the six cells are not run."*

**This unit trains the decisive cell.** A world whose drive reads the cue population, with the cue delivered at the
read step: if the information is absent from the world's state, **no training can supply it**, and the trained run
must come back at chance -- which is `e363`'s frozen reading, now asked of a body that is allowed to do whatever it
likes. `--loop-drive-from-cue` exposes the interface knob to the runner, off by default.

One run at `e362`'s exact flags plus `--loop-drive-from-cue`, `--methods naive,replay`, `--repeats 20`, paired
against `e362`'s action-source late-cue run at the same seeds and the same coupling draw. Five claims, registered
before the new run's reading was opened.

- **T1 -- one configuration except the drive's source.** The two runs agree on the populations' cue and feedback
  fingerprints, the world, the coupling fingerprint, the basis, the tasks and read-out widths, the sizes, the
  replicate count, the seed stream and the cue's step, differing in `drive_from_cue` and in the drive map that
  follows from it. **Falsifier**: any of the others differing.
- **T2 -- and training cannot beat the interface.** The cue-source world's `naive` diagonal is within **0.05** of
  chance. **Falsifier**: **0.10** or more above chance, which would say a trained body finds information the frozen
  probe did not -- and would refute `e363`'s structural reading. **Null**: between. This is the claim the unit
  exists for.
- **T3 -- and nothing is earned there.** Both arms' paired channel readings are within **0.05** of zero. **Falsifier**:
  **0.10** or more in either arm, which would say the answer depends on the loop after all. **Null**: between.
- **T4 -- and the trained run agrees with the frozen one.** The `naive` diagonal is within **0.05** of the frozen
  cell `e363` recorded for the same configuration (`cue@11`, the cue source). **Falsifier**: **0.10** apart.
  **REFUSED** when that artifact is absent, since the number it is compared against would then be off disk.
- **T5 -- and the buffer is inert there.** `replay`'s `mean_forgetting` is within **0.05** of `naive`'s.
  **Falsifier**: **0.10** apart, which would say there is something for a buffer to do in a task nobody can learn.

**What it cannot do.** *One cell of `e363`'s six*: the cue-source world at the read step, with the other five cells'
trained versions unrun -- and the interesting one is `cue@10`, where the frozen probe reads 0.8555 and a trained body
would be the test of the interface knob as a working task. *One world and one coupling*: eight dimensions at
`leak = 0.35` with `e359`'s matrix. *The action-source reference is a different artifact*, paired by the recorded
fingerprints -- except the drive map, whose width follows the population and therefore lands differently -- and by
the per-replicate seed stream. *And chance is a floor, not a proof*: a task at chance could in principle be one a
better optimiser would learn, which is why T4 puts the trained reading beside the frozen one rather than beside zero
alone.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the action-source late-cue arms already on disk at the same seeds, and the cue-source run this unit made
ACTION = Path("runs/e362_earned_label_latecue_20reps.json")
CUE = Path("runs/e364_earned_label_drivefromcue_20reps.json")
#: the frozen cell `e363` recorded for the same configuration
FROZEN = Path("runs/e363_where_the_cue_can_reach_the_world.json")
FROZEN_SOURCE, FROZEN_STEP = "cue", 11
ARMS = ("naive", "replay")
NAIVE, REPLAY = ARMS
COUPLING_SHA1 = "5326f4a0edb4"
REPLICATES = 20
CUE_STEP = 11
SIGMA = 2.0
FLAT = 0.05
CARRIES = 0.10
CLAIMS = (
    ("T1", "one configuration except the drive's source",
     "The two runs agree on the cue and feedback fingerprints, the world, the coupling fingerprint, the basis, the "
     "tasks and widths, the sizes, the replicate count, the seed stream and the cue's step, differing in "
     "`drive_from_cue` and in the drive map that follows from it",
     "falsifier: any of the others differing"),
    ("T2", f"and training cannot beat the interface, within {FLAT:.2f} of chance",
     "The cue-source world's `naive` diagonal is within 0.05 of chance",
     f"falsifier: {CARRIES:.2f} or more above chance, which would refute the structural reading"),
    ("T3", f"and nothing is earned there, within {FLAT:.2f} of zero",
     "Both arms' paired channel readings are within 0.05 of zero",
     f"falsifier: {CARRIES:.2f} or more in either arm"),
    ("T4", f"and the trained run agrees with the frozen one, within {FLAT:.2f}",
     f"The `naive` diagonal is within 0.05 of the frozen cell `{FROZEN_SOURCE}@{FROZEN_STEP}` `e363` recorded",
     f"falsifier: {CARRIES:.2f} apart; refused when that artifact is absent"),
    ("T5", f"and the buffer is inert there, within {FLAT:.2f}",
     "`replay`'s `mean_forgetting` is within 0.05 of `naive`'s",
     f"falsifier: {CARRIES:.2f} apart"),
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
    return {"loop_cue_at": s.get("loop_cue_at"), "loop_drive_from_cue": bool(s.get("loop_drive_from_cue")),
            "drive_from_cue": d.get("drive_from_cue"), "loop_world_leak": s.get("loop_world_leak"),
            "loop_world_coupled": bool(s.get("loop_world_coupled")), "world_coupling_sha1": d.get("world_coupling_sha1"),
            "readout_from_world": bool(s.get("readout_from_world")), "loop_world_dims": s.get("loop_world_dims"),
            "closed_loop": bool(s.get("closed_loop")), "repeats": s.get("repeats"),
            "circuit_size": s.get("circuit_size"), "readout_size": s.get("readout_size"), "basis": s.get("basis"),
            "seed0": s.get("seed0"), "task_names": [t.get("name") for t in (run or {}).get("tasks") or []],
            "task_readout_widths": sorted({int(t.get("n_readout")) for t in (run or {}).get("tasks") or []}),
            "cue_sha1": d.get("cue_sha1"), "feedback_sha1": d.get("feedback_sha1"),
            "action_sha1": d.get("action_sha1"), "world_read_sha1": d.get("world_read_sha1")}


def frozen_cell(path: Path = FROZEN, source: str = FROZEN_SOURCE, step: int = FROZEN_STEP):
    doc = load(path)
    if not doc:
        return None
    for c in doc.get("cells") or []:
        if c.get("source") == source and c.get("cue_at") == step:
            return {"accuracy": float(c["accuracy"]), "chance": float(c["chance"]), "artifact": Path(path).name}
    return None


def reading(action_path: Path = ACTION, cue_path: Path = CUE, frozen_path: Path = FROZEN) -> dict:
    action, cue = load(action_path), load(cue_path)
    out = {"rows": {**{f"action_{a}": arm_reading(action, a) for a in ARMS},
                    **{f"cue_{a}": arm_reading(cue, a) for a in ARMS}},
           "facts": {"action": _facts(action), "cue": _facts(cue)},
           "runs": {"action": Path(action_path).name, "cue": Path(cue_path).name},
           "expected_coupling_sha1": COUPLING_SHA1, "expected_replicates": REPLICATES, "expected_cue_step": CUE_STEP,
           "frozen": frozen_cell(frozen_path), "frozen_gap": None, "cue_buffer": None}
    out["ok"] = {"action": action is not None and all(out["rows"][f"action_{a}"].get("ok") for a in ARMS),
                 "cue": cue is not None and all(out["rows"][f"cue_{a}"].get("ok") for a in ARMS)}
    if out["ok"]["cue"]:
        out["cue_buffer"] = paired(out["rows"][f"cue_{REPLAY}"]["forgetting"],
                                   out["rows"][f"cue_{NAIVE}"]["forgetting"])
        if out["frozen"]:
            out["frozen_gap"] = paired(out["rows"][f"cue_{NAIVE}"]["diagonal"],
                                       [out["frozen"]["accuracy"]] * out["rows"][f"cue_{NAIVE}"]["n"])
    return out


def _within(value, target, bar) -> bool:
    return value is not None and abs(value - target) < bar


def judge(r: dict) -> list[dict]:
    rows, ok = r.get("rows") or {}, r.get("ok") or {}
    if not ok.get("cue"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the cue-source run is not on disk"}
                for c in CLAIMS]

    act = r["facts"]["action"]
    cue = r["facts"]["cue"]
    shared = ("loop_cue_at", "loop_world_leak", "loop_world_coupled", "world_coupling_sha1", "readout_from_world",
              "loop_world_dims", "closed_loop", "repeats", "circuit_size", "readout_size", "basis", "seed0",
              "task_names", "task_readout_widths", "cue_sha1", "feedback_sha1")
    differ = {k: [act.get(k), cue.get(k)] for k in shared if (act and act.get(k) != cue.get(k))}
    flips = (cue.get("drive_from_cue") is True and cue.get("loop_drive_from_cue") is True
             and (act is None or (act.get("drive_from_cue") in (False, None)
                                  and act.get("loop_drive_from_cue") in (False, None)))
             and cue.get("action_sha1") == cue.get("cue_sha1")
             and (act is None or act.get("action_sha1") != act.get("cue_sha1")))
    good = (not differ and flips and cue.get("loop_cue_at") == CUE_STEP
            and cue.get("world_coupling_sha1") == COUPLING_SHA1 and cue.get("repeats") == REPLICATES
            and rows[f"cue_{NAIVE}"]["n"] == REPLICATES and rows[f"cue_{REPLAY}"]["n"] == REPLICATES)
    j1 = {"id": "T1", "measured": f"cue-source arms from `{r['runs']['cue']}` against the action-source run "
                                  f"`{r['runs']['action']}`: circuits {cue['circuit_size']}, tasks "
                                  f"{cue['task_names']} at read-out widths {cue['task_readout_widths']}, "
                                  f"{cue['repeats']} replicates each at seed0 {cue['seed0']}, basis {cue['basis']}, "
                                  f"cue step {cue['loop_cue_at']}, coupling {cue['world_coupling_sha1']} against the "
                                  f"action run's {act and act.get('world_coupling_sha1')}, the drive's source "
                                  f"{cue['drive_from_cue']} against {act and act.get('drive_from_cue')} with the "
                                  f"action's fingerprint equal to the cue's here "
                                  f"{cue.get('action_sha1') == cue.get('cue_sha1')} and not there "
                                  f"{act and act.get('action_sha1') != act.get('cue_sha1')}, other fields differing "
                                  f"{differ}",
          "verdict": "MET -- one configuration except the drive's source" if good else
          f"FALSIFIER FIRED -- the runs differ beyond the drive's source: {differ}, source "
          f"{cue.get('drive_from_cue')}/{act and act.get('drive_from_cue')}, cue step {cue.get('loop_cue_at')}"}

    naive = rows[f"cue_{NAIVE}"]
    chance = naive["chance"]
    gap = naive["mean_diagonal"] - chance
    j2 = {"id": "T2", "measured": f"the cue-source `{NAIVE}` arm's diagonal mean is {naive['mean_diagonal']:.4f} "
                                  f"against a chance of {chance:.2f}, {gap:+.4f} above it, over {naive['n']} "
                                  f"replicates",
          "verdict": f"MET -- training cannot beat the interface, {gap:+.4f} above chance" if
          _within(gap, 0.0, FLAT) else
          f"FALSIFIER FIRED -- {gap:+.4f} above chance: a trained body found what the probe did not" if
          gap >= CARRIES else f"NULL -- {gap:+.4f}, between {FLAT:.2f} and {CARRIES:.2f}"}

    detail = "; ".join(f"`{a}` {rows[f'cue_{a}']['paired']['delta']:+.4f} at "
                       f"{_sg(rows[f'cue_{a}']['paired']['sigma'])} sigma" for a in ARMS)
    loud = [a for a in ARMS if not _within(rows[f"cue_{a}"]["paired"]["delta"] or 0.0, 0.0, FLAT)]
    j3 = {"id": "T3", "measured": f"the cue-source arms' paired channel readings over {naive['n']} replicates: "
                                  f"{detail}",
          "verdict": "MET -- nothing is earned there in either arm, within 0.05 of zero" if not loud else
          f"FALSIFIER FIRED -- the answer depends on the loop in {loud}"}

    fz = r.get("frozen")
    if not fz:
        j4 = {"id": "T4", "measured": "the frozen cell is not on disk",
              "verdict": "REFUSED -- the number the trained run is compared against is absent"}
    else:
        est = r.get("frozen_gap") or {"delta": None}
        j4 = {"id": "T4", "measured": f"the trained `{NAIVE}` diagonal is {naive['mean_diagonal']:.4f} and the frozen "
                                      f"cell `{FROZEN_SOURCE}@{FROZEN_STEP}` of `{fz['artifact']}` is "
                                      f"{fz['accuracy']:.4f}, {est['delta']:+.4f} apart",
              "verdict": f"MET -- the trained run agrees with the frozen one to {est['delta']:+.4f}" if
              _within(est["delta"], 0.0, FLAT) else
              f"FALSIFIER FIRED -- {est['delta']:+.4f} apart, so training moved a cell the probe read at chance" if
              abs(est["delta"]) >= CARRIES else
              f"NULL -- {est['delta']:+.4f}, between {FLAT:.2f} and {CARRIES:.2f}"}

    buf = r.get("cue_buffer") or {"delta": None}
    if buf.get("delta") is None:
        j5 = {"id": "T5", "measured": "the cue-source buffer value was not computable",
              "verdict": "REFUSED -- the buffer value was not computable"}
    else:
        j5 = {"id": "T5", "measured": f"the cue-source `{REPLAY}` arm forgets "
                                      f"{rows[f'cue_{REPLAY}']['mean_forgetting']:.4f} against its `{NAIVE}` arm's "
                                      f"{naive['mean_forgetting']:.4f}, so the buffer changes it by "
                                      f"{buf['delta']:+.4f}",
              "verdict": f"MET -- the buffer is inert there, {buf['delta']:+.4f} apart" if
              _within(buf["delta"], 0.0, FLAT) else
              f"FALSIFIER FIRED -- the buffer moves it by {buf['delta']:+.4f} in a task nobody can learn" if
              abs(buf["delta"]) >= CARRIES else
              f"NULL -- {buf['delta']:+.4f}, between {FLAT:.2f} and {CARRIES:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    ok = r.get("ok") or {}
    if not ok.get("cue"):
        print("== can a trained body beat the interface? ==\n   REFUSED -- the cue-source run is not on disk")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== can a trained body beat the interface? ==")
    print(f"   cue-source arms from `{r['runs']['cue']}` against the action-source run `{r['runs']['action']}`")
    print(f"\n   {'drive':>8} {'arm':>7} {'final':>8} {'diagonal':>9} {'forget':>8} {'channel':>9} {'sigma':>6}")
    for key, row in r["rows"].items():
        drive = key.split("_", 1)[0]
        print(f"   {drive:>8} {row['arm']:>7} {row['mean_final']:8.4f} {row['mean_diagonal']:9.4f} "
              f"{row['mean_forgetting']:8.4f} {row['paired']['delta']:+9.4f} {_sg(row['paired']['sigma']):>6}")
    if r.get("frozen"):
        print(f"   the frozen cell `{FROZEN_SOURCE}@{FROZEN_STEP}` of `{r['frozen']['artifact']}` reads "
              f"{r['frozen']['accuracy']:.4f}")

    print("\n== the registered claims, T1-T5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e363`'s frozen cell read the cue-source world at the read step at chance; this asks a body that is")
    print("    allowed to do whatever it likes, which is the strongest form the structural claim can take)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--action", type=Path, default=ACTION)
    ap.add_argument("--cue", type=Path, default=CUE)
    ap.add_argument("--frozen", type=Path, default=FROZEN)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(action_path=args.action, cue_path=args.cue, frozen_path=args.frozen)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
