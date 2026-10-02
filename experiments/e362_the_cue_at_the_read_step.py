"""E362 -- the cue at the read step, on a read-out that has no one-step limit.

`e344` mapped the **state** read-out's one-step limit exactly: a cue delivered at the step the decoder reads is
**invisible**, because the environment writes the cue onto `cue_neurons` and the connectome's weights carry it to the
decoder's own neurons only one recurrent step later -- that run came back at chance (0.5069) and the unit needed a
`cue_at = 10` control to say anything. **The world read-out has no such limit**, and for an exact reason: the head
reads the environment's state, the world's drive *is* a function of the state at the step it is read, and the cue at
that step is in that state. So a cue at the read step should be **readable**, and a task whose cue arrives there
needs nothing held at all.

**This unit puts the two lines side by side.** One run at `e359`'s exact flags with `--loop-cue-at 11`,
`--methods naive,replay`, `--repeats 20`, paired against `e359`'s cue-at-zero memoried world at the same seeds and
the same coupling draw. Five claims, registered before the new run's reading was opened.

- **T1 -- one configuration except the cue's step.** The two runs agree on the populations, the world, the coupling
  fingerprint, the basis, the tasks and widths, the sizes, the replicate count and the seed stream, differing only in
  `loop_cue_at`. **Falsifier**: any of those differing.
- **T2 -- and the cue at the read step is readable.** The late-cue `naive` arm's diagonal mean is at least **0.10**
  above chance. **Falsifier**: within **0.05** of chance, which would reproduce `e344`'s state read-out limit on this
  read-out and say the world's drive is not seen either. **Null**: between. This is the claim the unit exists for.
- **T3 -- and the answer is still earned there.** Both late-cue arms' paired channel readings are at least **0.10**
  and positive at **2 sigma**. **Falsifier**: an arm below 0.10, at or below zero, or unresolved.
- **T4 -- and the late cue is easier, by 0.05.** The late-cue `naive` diagonal exceeds the cue-at-zero one's by at
  least **0.05**, paired over the seeds -- the task that holds nothing should be the easier one. **Falsifier**:
  within **0.02**, which would say the gap costs the body nothing. **Null**: between.
- **T5 -- and the buffer still helps there.** `replay`'s `mean_forgetting` is lower than `naive`'s by at least
  **0.05**, paired over the twenty replicates. **Falsifier**: `replay` forgets more by 0.05 or more. **Null**:
  between.

**What it cannot do.** *One late step and one early step*: `cue_at` 11 against 0, with 1 to 10 unrun -- and the
interesting middle is where the body has *some* time to write into the world, which is the region `e344` walked on
the state read-out and this unit does not walk here. *The reference is a different artifact*, paired by the recorded
fingerprints and the per-replicate seed stream. *One world and one coupling*: `e359`'s own matrix, at `leak = 0.35`.
*And easier is not better*: a task that holds nothing is a **weaker** test of a world, so a resolved T4 would say the
earned label can be made easy by moving the cue, not that the benchmark got better.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the cue-at-zero memoried arms already on disk at the same seeds, and the late-cue run this unit made
EARLY = Path("runs/e359_earned_label_coupled_20reps.json")
LATE = Path("runs/e362_earned_label_latecue_20reps.json")
ARMS = ("naive", "replay")
NAIVE, REPLAY = ARMS
WORLD_READ_SHA1 = "3a7ba76b3619"
COUPLING_SHA1 = "5326f4a0edb4"
EARLY_CUE, LATE_CUE = 0, 11
REPLICATES = 20
SIGMA = 2.0
LEARNS = 0.10
FLAT = 0.05
CARRIES = 0.10
EASIER = 0.05
NOTHING = 0.02
FORGETS = 0.05
CLAIMS = (
    ("T1", "one configuration except the cue's step",
     "The two runs agree on the populations, the world, the coupling fingerprint, the basis, the tasks and widths, "
     "the sizes, the replicate count and the seed stream, differing only in `loop_cue_at`",
     "falsifier: any of those differing"),
    ("T2", f"and the cue at the read step is readable, by {LEARNS:.2f} over chance",
     "The late-cue `naive` arm's diagonal mean is at least 0.10 above chance",
     f"falsifier: within {FLAT:.2f} of chance, which would reproduce `e344`'s state read-out limit here"),
    ("T3", f"and the answer is still earned there, by {CARRIES:.2f} at 2 sigma",
     "Both late-cue arms' paired channel readings are at least 0.10 and positive at 2 sigma",
     "falsifier: an arm below 0.10, at or below zero, or unresolved"),
    ("T4", f"and the late cue is easier, by {EASIER:.2f}",
     "The late-cue `naive` diagonal exceeds the cue-at-zero one's by at least 0.05, paired over the seeds",
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
    return {"loop_cue_at": s.get("loop_cue_at"), "env_cue_at": d.get("cue_at"),
            "loop_world_leak": s.get("loop_world_leak"), "loop_world_coupled": bool(s.get("loop_world_coupled")),
            "world_coupling_sha1": d.get("world_coupling_sha1"), "readout_from_world": bool(s.get("readout_from_world")),
            "loop_world_dims": s.get("loop_world_dims"), "closed_loop": bool(s.get("closed_loop")),
            "repeats": s.get("repeats"), "circuit_size": s.get("circuit_size"), "readout_size": s.get("readout_size"),
            "basis": s.get("basis"), "seed0": s.get("seed0"),
            "task_names": [t.get("name") for t in (run or {}).get("tasks") or []],
            "task_readout_widths": sorted({int(t.get("n_readout")) for t in (run or {}).get("tasks") or []}),
            "world_read_sha1": d.get("world_read_sha1"), "world_drive_sha1": d.get("world_drive_sha1"),
            "cue_sha1": d.get("cue_sha1"), "action_sha1": d.get("action_sha1"),
            "feedback_sha1": d.get("feedback_sha1")}


def reading(early_path: Path = EARLY, late_path: Path = LATE) -> dict:
    early, late = load(early_path), load(late_path)
    out = {"rows": {**{f"early_{a}": arm_reading(early, a) for a in ARMS},
                    **{f"late_{a}": arm_reading(late, a) for a in ARMS}},
           "facts": {"early": _facts(early), "late": _facts(late)},
           "runs": {"early": Path(early_path).name, "late": Path(late_path).name},
           "expected_world_read_sha1": WORLD_READ_SHA1, "expected_coupling_sha1": COUPLING_SHA1,
           "expected_replicates": REPLICATES, "expected_cue_ats": [EARLY_CUE, LATE_CUE],
           "easier": None, "late_buffer": None}
    out["ok"] = {"early": early is not None and all(out["rows"][f"early_{a}"].get("ok") for a in ARMS),
                 "late": late is not None and all(out["rows"][f"late_{a}"].get("ok") for a in ARMS)}
    if out["ok"]["late"]:
        out["late_buffer"] = paired(out["rows"][f"late_{REPLAY}"]["forgetting"],
                                    out["rows"][f"late_{NAIVE}"]["forgetting"])
        if out["ok"]["early"]:
            out["easier"] = paired(out["rows"][f"late_{NAIVE}"]["diagonal"],
                                   out["rows"][f"early_{NAIVE}"]["diagonal"])
    return out


def judge(r: dict) -> list[dict]:
    rows, ok = r.get("rows") or {}, r.get("ok") or {}
    if not ok.get("late"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the late-cue run is not on disk"}
                for c in CLAIMS]

    ear = r["facts"]["early"]
    lat = r["facts"]["late"]
    shared = ("readout_from_world", "loop_world_dims", "loop_world_leak", "loop_world_coupled", "closed_loop",
              "repeats", "circuit_size", "readout_size", "basis", "seed0", "task_names", "task_readout_widths",
              "world_read_sha1", "world_drive_sha1", "cue_sha1", "action_sha1", "feedback_sha1",
              "world_coupling_sha1")
    differ = {k: [ear.get(k), lat.get(k)] for k in shared if (ear and ear.get(k) != lat.get(k))}
    cues = sorted({x for x in (ear and ear.get("loop_cue_at"), lat.get("loop_cue_at")) if x is not None})
    good = (not differ and lat.get("loop_cue_at") == LATE_CUE
            and (lat.get("env_cue_at") == LATE_CUE)
            and (ear is None or ear.get("loop_cue_at") == EARLY_CUE)
            and lat.get("world_coupling_sha1") == COUPLING_SHA1
            and lat.get("world_read_sha1") == WORLD_READ_SHA1 and lat.get("repeats") == REPLICATES
            and rows[f"late_{NAIVE}"]["n"] == REPLICATES and rows[f"late_{REPLAY}"]["n"] == REPLICATES)
    j1 = {"id": "T1", "measured": f"late-cue arms from `{r['runs']['late']}` against the cue-at-zero run "
                                  f"`{r['runs']['early']}`: circuits {lat['circuit_size']}, tasks "
                                  f"{lat['task_names']} at read-out widths {lat['task_readout_widths']}, "
                                  f"{lat['repeats']} replicates each at seed0 {lat['seed0']}, basis {lat['basis']}, "
                                  f"world read {lat['world_read_sha1']} (expected {r['expected_world_read_sha1']}), "
                                  f"coupling {lat['world_coupling_sha1']} against the early run's "
                                  f"{ear and ear.get('world_coupling_sha1')} (expected "
                                  f"{r['expected_coupling_sha1']}), cue steps {cues} against the expected "
                                  f"{sorted(r['expected_cue_ats'])}, other fields differing {differ}",
          "verdict": "MET -- one configuration except the cue's step" if good else
          f"FALSIFIER FIRED -- the runs differ beyond the cue's step: {differ}, cues {cues}, coupling "
          f"{lat.get('world_coupling_sha1')}/{ear and ear.get('world_coupling_sha1')}"}

    naive = rows[f"late_{NAIVE}"]
    above = naive["mean_diagonal"] - naive["chance"]
    j2 = {"id": "T2", "measured": f"the late-cue `{NAIVE}` arm's diagonal mean is {naive['mean_diagonal']:.4f} "
                                  f"against a chance of {naive['chance']:.2f}, {above:+.4f} above it, over "
                                  f"{naive['n']} replicates",
          "verdict": f"MET -- the cue at the read step is readable, {above:+.4f} above chance" if above >= LEARNS
          else f"FALSIFIER FIRED -- only {above:+.4f} above chance: the world read-out has the one-step limit too"
          if above < FLAT else f"NULL -- {above:+.4f} above chance, between {FLAT:.2f} and {LEARNS:.2f}"}

    detail = "; ".join(f"`{a}` {rows[f'late_{a}']['paired']['delta']:+.4f} at "
                       f"{_sg(rows[f'late_{a}']['paired']['sigma'])} sigma" for a in ARMS)
    weak = [a for a in ARMS if not (rows[f"late_{a}"]["paired"]["delta"] is not None
                                    and rows[f"late_{a}"]["paired"]["delta"] >= CARRIES
                                    and (rows[f"late_{a}"]["paired"]["sigma"] or 0) >= SIGMA)]
    j3 = {"id": "T3", "measured": f"the late-cue arms' paired channel readings over {naive['n']} replicates: "
                                  f"{detail}",
          "verdict": "MET -- the answer is still earned in both arms, at 2 sigma or better" if not weak else
          f"FALSIFIER FIRED -- the answer is not earned in {weak}"}

    est = r.get("easier") or {"delta": None}
    if est.get("delta") is None:
        j4 = {"id": "T4", "measured": "the late-early diagonal difference was not computable",
              "verdict": "REFUSED -- the difference was not computable"}
    else:
        j4 = {"id": "T4", "measured": f"the late-cue `{NAIVE}` diagonal is {naive['mean_diagonal']:.4f} and the "
                                      f"cue-at-zero one {rows[f'early_{NAIVE}']['mean_diagonal']:.4f}, "
                                      f"{est['delta']:+.4f} apart on a sem of {est['sem']:.4f} "
                                      f"({_sg(est['sigma'])} sigma)",
              "verdict": f"MET -- the late cue is easier by {est['delta']:+.4f}" if est["delta"] >= EASIER else
              f"FALSIFIER FIRED -- within {NOTHING:.2f} of it, {est['delta']:+.4f}: the gap costs the body nothing"
              if est["delta"] < NOTHING else
              f"NULL -- {est['delta']:+.4f}, between {NOTHING:.2f} and {EASIER:.2f}"}

    buf = r.get("late_buffer") or {"delta": None}
    if buf.get("delta") is None:
        j5 = {"id": "T5", "measured": "the late-cue buffer value was not computable",
              "verdict": "REFUSED -- the buffer value was not computable"}
    else:
        j5 = {"id": "T5", "measured": f"the late-cue `{REPLAY}` arm forgets "
                                      f"{rows[f'late_{REPLAY}']['mean_forgetting']:.4f} against the late-cue "
                                      f"`{NAIVE}` arm's {naive['mean_forgetting']:.4f}, so the buffer changes it by "
                                      f"{buf['delta']:+.4f} on a sem of {buf['sem']:.4f} ({_sg(buf['sigma'])} sigma)",
              "verdict": f"MET -- the buffer still helps there by {abs(buf['delta']):.4f}" if buf["delta"] <= -FORGETS
              else f"FALSIFIER FIRED -- it makes forgetting worse by {buf['delta']:.4f}" if buf["delta"] >= FORGETS
              else f"NULL -- {buf['delta']:+.4f}, between {FORGETS:.2f} either way"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    ok = r.get("ok") or {}
    if not ok.get("late"):
        print("== the cue at the read step ==\n   REFUSED -- the late-cue run is not on disk")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the cue at the read step ==")
    print(f"   late-cue arms from `{r['runs']['late']}` against the cue-at-zero run `{r['runs']['early']}`")
    print(f"\n   {'cue at':>7} {'arm':>7} {'final':>8} {'diagonal':>9} {'forget':>8} {'channel':>9} {'sigma':>6}")
    for key, row in r["rows"].items():
        when = key.split("_", 1)[0]
        print(f"   {when:>7} {row['arm']:>7} {row['mean_final']:8.4f} {row['mean_diagonal']:9.4f} "
              f"{row['mean_forgetting']:8.4f} {row['paired']['delta']:+9.4f} {_sg(row['paired']['sigma']):>6}")

    print("\n== the registered claims, T1-T5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e344` found the state read-out cannot see a cue delivered at the step it reads, because the")
    print("    weights carry it to the read-out's own neurons one step later; the world's drive is current)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--early", type=Path, default=EARLY)
    ap.add_argument("--late", type=Path, default=LATE)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(early_path=args.early, late_path=args.late)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
