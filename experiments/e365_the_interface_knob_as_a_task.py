"""E365 -- the interface knob as a working task: the trained `cue@10` cell of the cue-source world.

`e363`'s frozen grid found the knob and read it: a world whose drive listens to the cue's own neurons reads a cue
**one step old** at **0.8555** against **0.2578** for a world listening to the action population, while both read
**0.2578** -- chance -- at the step the world is read. `e364` trained that last cell and found training cannot beat
the interface: **0.2326**, below chance, agreeing with the frozen probe to 0.0252.

**This unit trains the cell where the frozen probe says there is something to learn.** The same world, the same
interface knob, the cue one step earlier: if the knob is a working task and not only a frozen reading, a trained body
should learn it -- and the pair of units then says the whole thing in one line: **the knob is worth nothing at zero
margin and is a task at one step of margin.**

One run at `e364`'s exact flags with `--loop-cue-at 10`, `--methods naive,replay`, `--repeats 20`, paired against
`e364`'s cue-source run at the read step -- both cue-source, so the drive maps have the same width and the draws
align -- and against `e363`'s frozen cell for this configuration. Five claims, registered before the new run's
reading was opened.

- **T1 -- one configuration except the cue's step.** The two cue-source runs agree on the populations, the world, the
  **coupling fingerprint** and every other recorded field, differing in the cue's step. **Falsifier**: any of those
  differing.
- **T2 -- and the knob is a working task.** The trained `naive` diagonal is at least **0.10** above chance.
  **Falsifier**: within **0.05** of chance, which would say the knob is a frozen curiosity and a trained body cannot
  use it even with a step of margin. **Null**: between. This is the claim the unit exists for.
- **T3 -- and the answer is earned there.** Both arms' paired channel readings are at least **0.10** and positive at
  **2 sigma**. **Falsifier**: an arm below 0.10, at or below zero, or unresolved.
- **T4 -- and it is at least what the probe found.** The trained `naive` diagonal is within **0.10** of `e363`'s
  frozen cell for this configuration (`cue@10`, the cue source) in the sense of not being below it by more than
  that -- training should not *lose* what a linear probe on a frozen net could read. **Falsifier**: **0.15** below
  it. **REFUSED** when that artifact is absent.
- **T5 -- and the buffer helps there.** `replay`'s `mean_forgetting` is lower than `naive`'s by at least **0.05**,
  paired over the replicates. **Falsifier**: `replay` forgets more by 0.05 or more. **Null**: between.

**What it cannot do.** *One cell*: `cue@10` in the cue source, with the remaining cells of `e363`'s six unrun -- so
the knob's value across gaps is two points and not a curve. *One world and one coupling*: eight dimensions at
`leak = 0.35`, and both runs here share the coupling draw because both send the drive to the same population, which
is what makes this pairing cleaner than `e364`'s. *And "at least the probe" is a weak bar*: a linear probe on a
frozen net and a trained body are different instruments, and T4 asks only that training not throw the information
away.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the cue-source run at the read step, and the cue-source run one step earlier that this unit made
AT_READ = Path("runs/e364_earned_label_drivefromcue_20reps.json")
AT_TEN = Path("runs/e365_earned_label_cue10_cuesource_20reps.json")
#: the frozen cell `e363` recorded for this configuration
FROZEN = Path("runs/e363_where_the_cue_can_reach_the_world.json")
FROZEN_SOURCE, FROZEN_STEP = "cue", 10
ARMS = ("naive", "replay")
NAIVE, REPLAY = ARMS
COUPLING_SHA1 = "1b7d09f2b469"
REPLICATES = 20
CUE_STEP = 10
SIGMA = 2.0
LEARNS = 0.10
FLAT = 0.05
CARRIES = 0.10
LOSES = 0.15
FORGETS = 0.05
CLAIMS = (
    ("T1", "one configuration except the cue's step",
     "The two cue-source runs agree on the populations, the world, the coupling fingerprint and every other recorded "
     "field, differing in the cue's step",
     "falsifier: any of those differing"),
    ("T2", f"and the knob is a working task, by {LEARNS:.2f} over chance",
     "The trained `naive` diagonal is at least 0.10 above chance",
     f"falsifier: within {FLAT:.2f} of chance"),
    ("T3", f"and the answer is earned there, by {CARRIES:.2f} at 2 sigma",
     "Both arms' paired channel readings are at least 0.10 and positive at 2 sigma",
     "falsifier: an arm below 0.10, at or below zero, or unresolved"),
    ("T4", f"and it is at least what the probe found, within {FLAT:.2f} below",
     f"The trained `naive` diagonal is not below `e363`'s frozen cell `{FROZEN_SOURCE}@{FROZEN_STEP}` by more than "
     f"0.10",
     f"falsifier: {LOSES:.2f} below it; refused when that artifact is absent"),
    ("T5", f"and the buffer helps there, by {FORGETS:.2f}",
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
    return {"loop_cue_at": s.get("loop_cue_at"), "loop_drive_from_cue": bool(s.get("loop_drive_from_cue")),
            "drive_from_cue": d.get("drive_from_cue"), "loop_world_leak": s.get("loop_world_leak"),
            "world_coupling_sha1": d.get("world_coupling_sha1"), "readout_from_world": bool(s.get("readout_from_world")),
            "loop_world_dims": s.get("loop_world_dims"), "closed_loop": bool(s.get("closed_loop")),
            "repeats": s.get("repeats"), "circuit_size": s.get("circuit_size"), "readout_size": s.get("readout_size"),
            "basis": s.get("basis"), "seed0": s.get("seed0"),
            "task_names": [t.get("name") for t in (run or {}).get("tasks") or []],
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


def reading(read_path: Path = AT_READ, ten_path: Path = AT_TEN, frozen_path: Path = FROZEN) -> dict:
    read, ten = load(read_path), load(ten_path)
    out = {"rows": {**{f"read_{a}": arm_reading(read, a) for a in ARMS},
                    **{f"ten_{a}": arm_reading(ten, a) for a in ARMS}},
           "facts": {"read": _facts(read), "ten": _facts(ten)},
           "runs": {"read": Path(read_path).name, "ten": Path(ten_path).name},
           "expected_coupling_sha1": COUPLING_SHA1, "expected_replicates": REPLICATES, "expected_cue_step": CUE_STEP,
           "frozen": frozen_cell(frozen_path), "probe_gap": None, "ten_buffer": None}
    out["ok"] = {"read": read is not None and all(out["rows"][f"read_{a}"].get("ok") for a in ARMS),
                 "ten": ten is not None and all(out["rows"][f"ten_{a}"].get("ok") for a in ARMS)}
    if out["ok"]["ten"]:
        out["ten_buffer"] = paired(out["rows"][f"ten_{REPLAY}"]["forgetting"],
                                   out["rows"][f"ten_{NAIVE}"]["forgetting"])
        if out["frozen"]:
            out["probe_gap"] = (out["rows"][f"ten_{NAIVE}"]["mean_diagonal"] - out["frozen"]["accuracy"])
    return out


def judge(r: dict) -> list[dict]:
    rows, ok = r.get("rows") or {}, r.get("ok") or {}
    if not ok.get("ten"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the cue-at-ten run is not on disk"}
                for c in CLAIMS]

    rd = r["facts"]["read"]
    tn = r["facts"]["ten"]
    shared = ("loop_world_leak", "world_coupling_sha1", "readout_from_world", "loop_world_dims", "closed_loop",
              "repeats", "circuit_size", "readout_size", "basis", "seed0", "task_names", "task_readout_widths",
              "cue_sha1", "feedback_sha1", "action_sha1", "world_read_sha1", "drive_from_cue", "loop_drive_from_cue")
    differ = {k: [rd.get(k), tn.get(k)] for k in shared if (rd and rd.get(k) != tn.get(k))}
    good = (not differ and tn.get("loop_cue_at") == CUE_STEP
            and (rd is None or rd.get("loop_cue_at") == CUE_STEP + 1)
            and tn.get("world_coupling_sha1") == COUPLING_SHA1 and tn.get("repeats") == REPLICATES
            and rows[f"ten_{NAIVE}"]["n"] == REPLICATES and rows[f"ten_{REPLAY}"]["n"] == REPLICATES)
    j1 = {"id": "T1", "measured": f"cue-at-ten arms from `{r['runs']['ten']}` against the read-step run "
                                  f"`{r['runs']['read']}`: circuits {tn['circuit_size']}, tasks {tn['task_names']} at "
                                  f"read-out widths {tn['task_readout_widths']}, {tn['repeats']} replicates each at "
                                  f"seed0 {tn['seed0']}, basis {tn['basis']}, cue steps "
                                  f"{[rd and rd.get('loop_cue_at'), tn['loop_cue_at']]}, coupling "
                                  f"{tn['world_coupling_sha1']} against the read-step run's "
                                  f"{rd and rd.get('world_coupling_sha1')}, the drive's source "
                                  f"{tn['drive_from_cue']} against {rd and rd.get('drive_from_cue')}, other fields "
                                  f"differing {differ}",
          "verdict": "MET -- one configuration except the cue's step" if good else
          f"FALSIFIER FIRED -- the runs differ beyond the cue's step: {differ}, cue steps "
          f"{[rd and rd.get('loop_cue_at'), tn.get('loop_cue_at')]}, coupling "
          f"{tn.get('world_coupling_sha1')}/{rd and rd.get('world_coupling_sha1')}"}

    naive = rows[f"ten_{NAIVE}"]
    above = naive["mean_diagonal"] - naive["chance"]
    j2 = {"id": "T2", "measured": f"the cue-at-ten `{NAIVE}` arm's diagonal mean is {naive['mean_diagonal']:.4f} "
                                  f"against a chance of {naive['chance']:.2f}, {above:+.4f} above it, over "
                                  f"{naive['n']} replicates",
          "verdict": f"MET -- the knob is a working task, {above:+.4f} above chance" if above >= LEARNS else
          f"FALSIFIER FIRED -- only {above:+.4f} above chance: the knob is a frozen curiosity" if above < FLAT else
          f"NULL -- {above:+.4f} above chance, between {FLAT:.2f} and {LEARNS:.2f}"}

    detail = "; ".join(f"`{a}` {rows[f'ten_{a}']['paired']['delta']:+.4f} at "
                       f"{_sg(rows[f'ten_{a}']['paired']['sigma'])} sigma" for a in ARMS)
    weak = [a for a in ARMS if not (rows[f"ten_{a}"]["paired"]["delta"] is not None
                                    and rows[f"ten_{a}"]["paired"]["delta"] >= CARRIES
                                    and (rows[f"ten_{a}"]["paired"]["sigma"] or 0) >= SIGMA)]
    j3 = {"id": "T3", "measured": f"the cue-at-ten arms' paired channel readings over {naive['n']} replicates: "
                                  f"{detail}",
          "verdict": "MET -- the answer is earned in both arms, at 2 sigma or better" if not weak else
          f"FALSIFIER FIRED -- the answer is not earned in {weak}"}

    fz = r.get("frozen")
    if not fz:
        j4 = {"id": "T4", "measured": "the frozen cell is not on disk",
              "verdict": "REFUSED -- the number the trained run is compared against is absent"}
    else:
        gap = r.get("probe_gap")
        j4 = {"id": "T4", "measured": f"the trained `{NAIVE}` diagonal is {naive['mean_diagonal']:.4f} and the frozen "
                                      f"cell `{FROZEN_SOURCE}@{FROZEN_STEP}` of `{fz['artifact']}` is "
                                      f"{fz['accuracy']:.4f}, so training is {gap:+.4f} against it",
              "verdict": f"MET -- training is not below the probe by more than 0.10, {gap:+.4f}" if
              gap >= -0.10 else
              f"FALSIFIER FIRED -- training lost {abs(gap):.4f} of what the probe read" if gap <= -LOSES else
              f"NULL -- {gap:+.4f}, between {-LOSES:.2f} and {-FLAT:.2f}"}

    buf = r.get("ten_buffer") or {"delta": None}
    if buf.get("delta") is None:
        j5 = {"id": "T5", "measured": "the cue-at-ten buffer value was not computable",
              "verdict": "REFUSED -- the buffer value was not computable"}
    else:
        j5 = {"id": "T5", "measured": f"the cue-at-ten `{REPLAY}` arm forgets "
                                      f"{rows[f'ten_{REPLAY}']['mean_forgetting']:.4f} against its `{NAIVE}` arm's "
                                      f"{naive['mean_forgetting']:.4f}, so the buffer changes it by {buf['delta']:+.4f} "
                                      f"on a sem of {buf['sem']:.4f} ({_sg(buf['sigma'])} sigma)",
              "verdict": f"MET -- the buffer helps there by {abs(buf['delta']):.4f}" if buf["delta"] <= -FORGETS else
              f"FALSIFIER FIRED -- it makes forgetting worse by {buf['delta']:.4f}" if buf["delta"] >= FORGETS else
              f"NULL -- {buf['delta']:+.4f}, between {FORGETS:.2f} either way"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    ok = r.get("ok") or {}
    if not ok.get("ten"):
        print("== the interface knob as a working task ==\n   REFUSED -- the cue-at-ten run is not on disk")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the interface knob as a working task ==")
    print(f"   cue-at-ten arms from `{r['runs']['ten']}` against the read-step run `{r['runs']['read']}`")
    print(f"\n   {'cue at':>7} {'arm':>7} {'final':>8} {'diagonal':>9} {'forget':>8} {'channel':>9} {'sigma':>6}")
    for key, row in r["rows"].items():
        when = key.split("_", 1)[0]
        print(f"   {when:>7} {row['arm']:>7} {row['mean_final']:8.4f} {row['mean_diagonal']:9.4f} "
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
    print("\n   (`e363` read the cue-source world at 0.8555 one step from the read and 0.2578 at it; `e364` found")
    print("    training cannot beat the interface at zero margin, and this asks the cell where the probe saw signal)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--read", type=Path, default=AT_READ)
    ap.add_argument("--ten", type=Path, default=AT_TEN)
    ap.add_argument("--frozen", type=Path, default=FROZEN)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(read_path=args.read, ten_path=args.ten, frozen_path=args.frozen)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
