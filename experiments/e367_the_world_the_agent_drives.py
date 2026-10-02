"""E367 -- the world the agent drives: the first trained closed loop whose world listens to the agent's own action.

`e363`'s frozen grid read six cells of one world and closed on a structure. At `cue_at = 11`, the step the world is
read, **both** drive sources read **0.2578** -- chance. At `cue_at = 10`, one step of margin, the two sources
separate: the world listening to the **cue population** reads **0.8555** and the world listening to the **action
population** reads **0.2578**, still chance. At `cue_at = 0` the action source reads **0.6602**, so the agent's own
action does carry the cue when it has eleven steps to write it there -- it is the one-step case that is empty.

`e364` trained the read-step cell and found training cannot beat the interface (**0.2326**), and `e365` trained the
cue-source cell at `cue@10` and found the knob is a working task (**0.5337**). **The trained action-source cell at
`cue@10` -- the cell where the world listens to the agent and the margin is not zero -- has never been run.** That
is the configuration a game needs: the agent's own action is the world's drive, and the world's state is the
read-out. This unit runs it, at `e362`'s flags with the drive left on the action population and the cue one step
earlier, and pairs it with `e365`'s cue-source run at the same step and the same seeds.

Five claims, registered before the new run's reading was opened.

- **T1 -- one configuration except where the world's drive is read.** Against `e362`'s action-source run at the read
  step: the circuit, the population fingerprints, the world's dimension, its leak, its coupling fingerprint, the
  drive map, the basis, the tasks and their widths, the read-out, the replicate count and the seed stream all agree,
  with the cue's step the only difference. Against `e365`'s cue-source run at the same step: the same, except the
  drive's source and the two draws that follow from its width -- the drive map and, because the wider map consumes
  more of the environment's draw, the coupling matrix. **That second difference is not new and is not excused**: it
  fired `e364`'s T1 and is registered here as expected rather than discovered. **Falsifier**: any *other* field
  differing between any of the three, or the action-source pair's coupling fingerprint not being `5326f4a0edb4`.
- **T2 -- and the frozen floor of this cell is chance, as `e363` recorded.** That unit's cell for the action source
  at `cue@10` is within **0.05** of chance. **Falsifier**: **0.10** or more above chance, which would say the frozen
  probe could already read the channel and the trained run is not measured against the floor. **REFUSED** when that
  artifact is absent.
- **T3 -- and the agent can build the channel.** The trained `naive` diagonal is at least **0.10** above chance.
  **Falsifier**: within **0.05** of chance, which would say a body free to shape its own action population cannot
  route a cue into the world even with a step of margin, and the closed loop is not a task. **Null**: between.
  *This is the claim the unit exists for.*
- **T4 -- and being handed the channel is worth more than building it.** `e365`'s cue-source `naive` diagonal
  exceeds this unit's action-source one by at least **0.05**, paired over the twenty replicates. **Falsifier**: the
  closed loop matching or beating the hard-wired channel, i.e. a paired delta of **0.02** or less, which would say
  the interface's value is the training and not the wiring. **Null**: between.
- **T5 -- and the answer is earned in the closed loop.** Both arms' paired channel readings are at least **0.10**
  and positive at **2 sigma**. **Falsifier**: an arm below 0.10, at or below zero, or unresolved.

**What it can do beyond that.** The frozen grid's `action@0` cell -- **0.6602**, the same source with eleven steps
instead of one -- is reported beside the trained number and not claimed against it, because a trained one-step body
and a frozen eleven-step one are different instruments and the comparison has no registered bar. It is the number
that says how much of the gap training closed.

**What it cannot do.** *One cell*: the action source at `cue@10`, so the trained grid is four of `e363`'s six cells
and the two untrained ones are `cue@0` and `action@0`. *One world and one coupling*: eight dimensions at
`leak = 0.35` with `e359`'s matrix, and the action source's own draw rather than the cue source's. *And the pairing
is across artifacts*: `e367`'s run and `e365`'s share the recorded seed stream and the read-out draw, which is what
makes T4's pairing legitimate, but they are two files and two coupling matrices and not one run of two arms.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the run this unit made: the closed loop, the world's drive on the **action** population, the cue at step 10
CLOSED = Path("runs/e367_earned_label_cue10_actionsource_20reps.json")
#: `e365`'s cue-source run at the same step and the same seeds, and `e362`'s action-source run at the read step
CUE = Path("runs/e365_earned_label_cue10_cuesource_20reps.json")
LATE = Path("runs/e362_earned_label_latecue_20reps.json")
#: `e363`'s frozen grid, which holds the floor for this cell and the eleven-step action cell
FROZEN = Path("runs/e363_where_the_cue_can_reach_the_world.json")
FROZEN_SOURCE, FROZEN_STEP = "action", 10
FROZEN_SAME_SOURCE, FROZEN_SAME_STEP = "action", 0
ARMS = ("naive", "replay")
NAIVE, REPLAY = ARMS
#: the action source's own coupling draw, which `e362` recorded and this unit's run must reproduce
COUPLING_SHA1 = "5326f4a0edb4"
REPLICATES = 20
CUE_STEP = 10
LATE_STEP = 11
SIGMA = 2.0
LEARNS = 0.10
FLAT = 0.05
CARRIES = 0.10
COSTS = 0.05
FREE = 0.02
SAME = 0.05
FIRES = 0.10
CLAIMS = (
    ("T1", "one configuration except where the world's drive is read",
     "Against the action-source run at the read step every recorded field agrees with the cue's step the only "
     "difference, and against the cue-source run at this step every field agrees except the drive's source and the "
     "two draws that follow from its width",
     "falsifier: any other field differing, or the action pair's coupling not being 5326f4a0edb4"),
    ("T2", f"and the frozen floor of this cell is chance, within {SAME:.2f}",
     "`e363`'s cell for the action source at the cue step 10 is within 0.05 of chance",
     f"falsifier: {FIRES:.2f} or more above chance; refused when that artifact is absent"),
    ("T3", f"and the agent can build the channel, by {LEARNS:.2f} over chance",
     "The trained `naive` diagonal is at least 0.10 above chance",
     f"falsifier: within {FLAT:.2f} of chance; null: between {FLAT:.2f} and {LEARNS:.2f}"),
    ("T4", f"and being handed the channel beats building it, by {COSTS:.2f}",
     "`e365`'s cue-source `naive` diagonal exceeds this unit's by at least 0.05, paired over the replicates",
     f"falsifier: a paired delta of {FREE:.2f} or less; null: between {FREE:.2f} and {COSTS:.2f}"),
    ("T5", f"and the answer is earned there, by {CARRIES:.2f} at {SIGMA:.0f} sigma",
     "Both arms' paired channel readings are at least 0.10 and positive at 2 sigma",
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


#: the fields a configuration comparison is made of. `drive_from_cue` is normalized because `e362` was written
#: before the draw carried it, so an absent field and `False` are the same fact and must compare equal.
SHARED = ("loop_world_leak", "readout_from_world", "loop_world_dims", "closed_loop", "loop_world_modes",
          "loop_world_nonlinear", "repeats", "circuit_size", "readout_size", "basis", "seed0", "task_names",
          "task_readout_widths", "cue_sha1", "feedback_sha1", "iters", "n_cue")
#: and the seven fields this unit registers as following from the drive's source rather than from the manipulation:
#: the source itself, the **action population** it is read from and its width, and the three world draws that come
#: after the drive map in the environment's own draw -- the drive map, the read map and the coupling matrix, whose
#: width and consumption both move with the population. All seven must match the action-source run's and all seven
#: must move against the cue-source one. `e364` fired its T1 on the last two, so they are registered here as
#: expected rather than discovered; the first three are the same fact and are registered with them.
FOLLOWS_FROM_THE_SOURCE = ("drive_from_cue", "loop_drive_from_cue", "action_sha1", "n_action", "world_drive_sha1",
                           "world_read_sha1", "world_coupling_sha1")


def _facts(run: dict | None) -> dict:
    s = (run or {}).get("config") or {}
    d = (run or {}).get("env_draw") or {}
    return {"loop_cue_at": s.get("loop_cue_at"), "drive_from_cue": bool(d.get("drive_from_cue")),
            "loop_drive_from_cue": bool(s.get("loop_drive_from_cue")), "loop_world_leak": s.get("loop_world_leak"),
            "world_coupling_sha1": d.get("world_coupling_sha1"), "readout_from_world": bool(s.get("readout_from_world")),
            "loop_world_dims": s.get("loop_world_dims"), "closed_loop": bool(s.get("closed_loop")),
            "loop_world_modes": s.get("loop_world_modes"), "loop_world_nonlinear": bool(s.get("loop_world_nonlinear")),
            "repeats": s.get("repeats"), "circuit_size": s.get("circuit_size"), "readout_size": s.get("readout_size"),
            "basis": s.get("basis"), "seed0": s.get("seed0"), "iters": s.get("iters"),
            "task_names": [t.get("name") for t in (run or {}).get("tasks") or []],
            "task_readout_widths": sorted({int(t.get("n_readout")) for t in (run or {}).get("tasks") or []}),
            "cue_sha1": d.get("cue_sha1"), "feedback_sha1": d.get("feedback_sha1"),
            "action_sha1": d.get("action_sha1"), "world_read_sha1": d.get("world_read_sha1"),
            "world_drive_sha1": d.get("world_drive_sha1"), "n_action": d.get("n_action"), "n_cue": d.get("n_cue")}


def frozen_cell(path: Path = FROZEN, source: str = FROZEN_SOURCE, step: int = FROZEN_STEP):
    doc = load(path)
    if not doc:
        return None
    for c in doc.get("cells") or []:
        if c.get("source") == source and c.get("cue_at") == step:
            return {"accuracy": float(c["accuracy"]), "chance": float(c["chance"]), "artifact": Path(path).name}
    return None


def reading(closed_path: Path = CLOSED, cue_path: Path = CUE, late_path: Path = LATE,
            frozen_path: Path = FROZEN) -> dict:
    closed, cue, late = load(closed_path), load(cue_path), load(late_path)
    out = {"rows": {**{f"closed_{a}": arm_reading(closed, a) for a in ARMS},
                    **{f"cue_{a}": arm_reading(cue, a) for a in ARMS},
                    **{f"late_{a}": arm_reading(late, a) for a in ARMS}},
           "facts": {"closed": _facts(closed), "cue": _facts(cue), "late": _facts(late)},
           "runs": {"closed": Path(closed_path).name, "cue": Path(cue_path).name, "late": Path(late_path).name},
           "expected_coupling_sha1": COUPLING_SHA1, "expected_replicates": REPLICATES, "expected_cue_step": CUE_STEP,
           "present": {"closed": closed is not None, "cue": cue is not None, "late": late is not None},
           "frozen": frozen_cell(frozen_path), "frozen_wider": frozen_cell(frozen_path, FROZEN_SAME_SOURCE,
                                                                          FROZEN_SAME_STEP),
           "built_gap": None, "handed_gap": None, "earned_closed": None}
    out["ok"] = {"closed": closed is not None and all(out["rows"][f"closed_{a}"].get("ok") for a in ARMS),
                 "cue": cue is not None and all(out["rows"][f"cue_{a}"].get("ok") for a in ARMS),
                 "late": late is not None and all(out["rows"][f"late_{a}"].get("ok") for a in ARMS)}
    if out["ok"]["closed"] and out["ok"]["cue"]:
        out["handed_gap"] = paired(out["rows"][f"cue_{NAIVE}"]["diagonal"],
                                   out["rows"][f"closed_{NAIVE}"]["diagonal"])
    if out["ok"]["closed"] and out["frozen"]:
        out["built_gap"] = out["rows"][f"closed_{NAIVE}"]["mean_diagonal"] - out["frozen"]["accuracy"]
    return out


def judge(r: dict) -> list[dict]:
    rows, ok = r.get("rows") or {}, r.get("ok") or {}
    if not ok.get("closed"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the closed-loop run is not on disk"}
                for c in CLAIMS]

    fa, fc, fl = r["facts"]["closed"], r["facts"]["cue"], r["facts"]["late"]
    pres = r.get("present") or {}
    if not (pres.get("cue") and pres.get("late")):
        j1 = {"id": "T1", "measured": f"the runs this unit compares against are "
                                      f"`{r['runs']['late']}` (present {bool(fl)}) and `{r['runs']['cue']}` "
                                      f"(present {bool(fc)})",
              "verdict": "REFUSED -- a run this unit pairs against is absent, so the configuration check cannot "
                         "be made"}
    else:
        vs_late = {k: [fa.get(k), fl.get(k)] for k in SHARED + FOLLOWS_FROM_THE_SOURCE if fa.get(k) != fl.get(k)}
        vs_cue = {k: [fa.get(k), fc.get(k)] for k in SHARED if fa.get(k) != fc.get(k)}
        source_draws = {k: [fa.get(k), fc.get(k)] for k in FOLLOWS_FROM_THE_SOURCE if fa.get(k) != fc.get(k)}
        good = (not vs_late and not vs_cue and len(source_draws) == len(FOLLOWS_FROM_THE_SOURCE)
                and fa.get("loop_cue_at") == CUE_STEP
                and fa.get("world_coupling_sha1") == COUPLING_SHA1 and fa.get("repeats") == REPLICATES
                and fl.get("loop_cue_at") == LATE_STEP and fc.get("loop_cue_at") == CUE_STEP
                and rows[f"closed_{NAIVE}"]["n"] == REPLICATES and rows[f"closed_{REPLAY}"]["n"] == REPLICATES)
        j1 = {"id": "T1", "measured": f"the closed-loop run `{r['runs']['closed']}` against the action-source "
                                      f"read-step run `{r['runs']['late']}` (cue steps {fl.get('loop_cue_at')} and "
                                      f"{fa.get('loop_cue_at')}, differing {vs_late}) and against the cue-source run "
                                      f"`{r['runs']['cue']}` at the same step (differing {vs_cue}, with the drive "
                                      f"following it in {sorted(source_draws)}): circuit {fa['circuit_size']}, tasks "
                                      f"{fa['task_names']} at read-out widths {fa['task_readout_widths']}, "
                                      f"{fa['repeats']} replicates at seed0 {fa['seed0']}, basis {fa['basis']}, "
                                      f"coupling {fa['world_coupling_sha1']} against {fl.get('world_coupling_sha1')} "
                                      f"and {fc.get('world_coupling_sha1')}",
              "verdict": "MET -- one configuration, with the drive's source the only difference from either run that "
                         "this unit did not register as following from it" if good else
              f"FALSIFIER FIRED -- fields differ beyond the drive's source: against the read-step run {vs_late}, "
              f"against the cue-source run {vs_cue}, coupling {fa.get('world_coupling_sha1')}"}

    fz = r.get("frozen")
    naive = rows[f"closed_{NAIVE}"]
    if not fz:
        j2 = {"id": "T2", "measured": "the frozen cell is not on disk",
              "verdict": "REFUSED -- the floor the trained run is measured against is absent"}
    else:
        above = fz["accuracy"] - fz["chance"]
        j2 = {"id": "T2", "measured": f"`{fz['artifact']}` records the action source at the cue step "
                                      f"{FROZEN_STEP} at {fz['accuracy']:.4f} against a chance of {fz['chance']:.2f}, "
                                      f"{above:+.4f} above it",
              "verdict": f"MET -- the frozen floor of this cell is chance, {above:+.4f}" if above < SAME else
              f"FALSIFIER FIRED -- the frozen probe already reads {above:+.4f} above chance, so this cell has a "
              f"signal and the trained run is not measured against the floor" if above >= FIRES else
              f"NULL -- {above:+.4f} above chance, between {SAME:.2f} and {FIRES:.2f}"}

    learned = naive["mean_diagonal"] - naive["chance"]
    j3 = {"id": "T3", "measured": f"the closed-loop `{NAIVE}` arm's diagonal mean is {naive['mean_diagonal']:.4f} "
                                  f"against a chance of {naive['chance']:.2f}, {learned:+.4f} above it, over "
                                  f"{naive['n']} replicates",
          "verdict": f"MET -- the agent built the channel, {learned:+.4f} above chance" if learned >= LEARNS else
          f"FALSIFIER FIRED -- only {learned:+.4f} above chance: a body free to shape its own action population "
          f"cannot route the cue into the world" if learned < FLAT else
          f"NULL -- {learned:+.4f} above chance, between {FLAT:.2f} and {LEARNS:.2f}"}

    gap = r.get("handed_gap") or {"delta": None}
    if gap.get("delta") is None:
        j4 = {"id": "T4", "measured": "the paired comparison was not computable",
              "verdict": "REFUSED -- the cue-source run is absent or its replicates do not pair"}
    else:
        j4 = {"id": "T4", "measured": f"`{r['runs']['cue']}`'s `{NAIVE}` diagonal is "
                                      f"{rows[f'cue_{NAIVE}']['mean_diagonal']:.4f} and the closed loop's is "
                                      f"{naive['mean_diagonal']:.4f}, so being handed the channel is worth "
                                      f"{gap['delta']:+.4f} on a sem of {gap['sem']:.4f} "
                                      f"({_sg(gap['sigma'])} sigma) over {gap['n']} paired replicates",
              "verdict": f"MET -- building the channel costs {gap['delta']:+.4f}" if gap["delta"] >= COSTS else
              f"FALSIFIER FIRED -- the closed loop is within {FREE:.2f} of the hard-wired channel, "
              f"{gap['delta']:+.4f}: the wiring is not what the interface is worth" if gap["delta"] <= FREE else
              f"NULL -- {gap['delta']:+.4f}, between {FREE:.2f} and {COSTS:.2f}"}

    detail = "; ".join(f"`{a}` {rows[f'closed_{a}']['paired']['delta']:+.4f} at "
                       f"{_sg(rows[f'closed_{a}']['paired']['sigma'])} sigma" for a in ARMS)
    weak = [a for a in ARMS if not (rows[f"closed_{a}"]["paired"]["delta"] is not None
                                    and rows[f"closed_{a}"]["paired"]["delta"] >= CARRIES
                                    and (rows[f"closed_{a}"]["paired"]["sigma"] or 0) >= SIGMA)]
    j5 = {"id": "T5", "measured": f"the closed loop's paired channel readings over {naive['n']} replicates: {detail}",
          "verdict": "MET -- the answer is earned in both arms, at 2 sigma or better" if not weak else
          f"FALSIFIER FIRED -- the answer is not earned in {weak}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    ok = r.get("ok") or {}
    if not ok.get("closed"):
        print("== the world the agent drives ==\n   REFUSED -- the closed-loop run is not on disk")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the world the agent drives ==")
    print(f"   the closed loop `{r['runs']['closed']}` against the cue-source run `{r['runs']['cue']}` at the same "
          f"step and `{r['runs']['late']}` at the read step")
    print(f"\n   {'run':>8} {'cue at':>7} {'arm':>7} {'final':>8} {'diagonal':>9} {'forget':>8} {'channel':>9} "
          f"{'sigma':>6}")
    for key, row in r["rows"].items():
        when = {"closed": r["facts"]["closed"].get("loop_cue_at"), "cue": r["facts"]["cue"].get("loop_cue_at"),
                "late": r["facts"]["late"].get("loop_cue_at")}[key.split("_", 1)[0]]
        print(f"   {key.split('_', 1)[0]:>8} {str(when):>7} {row['arm']:>7} {row['mean_final']:8.4f} "
              f"{row['mean_diagonal']:9.4f} {row['mean_forgetting']:8.4f} {row['paired']['delta']:+9.4f} "
              f"{_sg(row['paired']['sigma']):>6}")
    if r.get("frozen"):
        print(f"   the frozen cell for this configuration in `{r['frozen']['artifact']}` reads "
              f"{r['frozen']['accuracy']:.4f}, so training is {r.get('built_gap'):+.4f} against it")
    if r.get("frozen_wider"):
        print(f"   and the same source with the cue at step {FROZEN_SAME_STEP} reads "
              f"{r['frozen_wider']['accuracy']:.4f} frozen (reported, not claimed)")

    print("\n== the registered claims, T1-T5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e363` read the action-source world at chance with one step of margin and at 0.6602 with eleven;")
    print("    `e364` found training cannot beat the interface at zero margin and `e365` that the cue source is a")
    print("    working task at this one -- this is the cell where the agent's own action drives the world)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--closed", type=Path, default=CLOSED)
    ap.add_argument("--cue", type=Path, default=CUE)
    ap.add_argument("--late", type=Path, default=LATE)
    ap.add_argument("--frozen", type=Path, default=FROZEN)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(closed_path=args.closed, cue_path=args.cue, late_path=args.late, frozen_path=args.frozen)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
