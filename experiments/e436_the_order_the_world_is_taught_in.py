"""E436 -- the order the benchmark's world is taught in: reversed, on the earned-label cell itself.

`e425` and `e426` read the corpus's order axis on the overlap and assembly suites and found the trade following the
**position** in the sequence: the same task is worth more taught first and cost taught last, and reversing the order
costs the buffer. Both registered the same limit -- the order clause the card carries at revision 7 is measured on those
two suites and **not on the benchmark's own world**. `e302`'s M4 found that no permutation of any suite had ever been
run, and the runner has carried `--task-order` since then.

**This unit drives the missing roll.** The card's world at `cue@0` with the action source, the same circuit, read-out
draw, environment draw, task set, iteration budget and arm pair as `e380`'s twenty-replicate run, with **`--task-order
reverse`** alone differing, at the same twenty replicates. Five claims, registered before the new run's reading was
opened.

- **BL1 -- and the pair is carried.** The two rolls agree on the circuit, the read-out draw, the environment draw and
  the task **set**, with `task_order` alone differing and the reversed suite the as-built one reversed; both arms at
  **20** replicates. **Falsifier**: any other field differing, a different task set, or an arm missing.
- **BL2 -- and the position effect holds on the benchmark's own world.** In **both** rolls the first-taught task's gain
  exceeds the last-taught task's. **Falsifier**: either roll where it does not.
- **BL3 -- and the last-taught task is cost under the reversed order.** The reversed roll's last-taught task's gain is
  at most **zero**. **Falsifier**: above **+0.05**; **null**: between.
- **BL4 -- and the reversal costs the buffer on this world.** The reversed roll's mean gain over the three tasks is
  **below** the as-built roll's. **Falsifier**: not below.
- **BL5 -- and the same task moves with its position here too.** For each of the two tasks that is first in one roll
  and last in the other, its gain when taught first exceeds its gain when taught last by at least **0.05**.
  **Falsifier**: either contrast below **0.02**; **null**: between. *This is the unit's own prediction: if the trade is
  the sequence's rather than the suite's, the benchmark's own world should show it under a permutation.*

**What it can do beyond that.** It closes the gap the card's own order clause names. `e425` measured the position
effect on three configurations of the overlap and assembly suites and `e426` on every arm of them; if the effect
appears on the earned-label cell with the same twenty replicates that carry the card's trade clause, then the clause's
statement is about the sequence rather than about those suites, and the card can say so.

**What it cannot do.** *One permutation*: `reverse` alone, so the other four permutations of a three-task suite are not
in this reading. *And one cell*: the card's world at twenty replicates, so the other five draws and the three streams
are not either. *And one arm pair*: `naive` and `replay`, so the penalty arms are absent. *And a permutation is not a
mechanism*: that the order moves the numbers does not say which of the corpus's instruments the movement runs through.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the same configuration rolled both ways: `e380`'s as-built run and this unit's reversed one
AS_BUILT = Path("runs/e380_earned_label_cue0_actionsource_20reps.json")
REVERSE = Path("runs/e436_earned_label_cue0_reverse_20reps.json")
ORDER = "task_order"
SHARED = ("circuit", "readout", "tasks")
DRAW_FIELDS = ("cue_sha1", "action_sha1", "world_read_sha1", "world_drive_sha1", "world_coupling_sha1")
CONFIG_FIELDS = ("circuit_size", "iters", "lr", "lam", "replay_per_task", "replay_batch", "train", "test", "classes",
                 "support", "basis", "closed_loop", "loop_cue_at", "readout_from_world", "loop_symbols",
                 "loop_world_leak", "loop_world_dims", "loop_world_coupled", "repeats", "methods")
ARMS = ("naive", "replay")
N_TASKS = 3
MIN_REPS = 20
POSITION = 0.0
LAST_BAR = 0.0
LAST_FIRES = 0.05
CONTRAST = 0.05
CONTRAST_FIRES = 0.02
CLAIMS = (
    ("BL1", f"and the pair is carried, at {MIN_REPS} replicates and both arms",
     "The two rolls agree on the circuit, the read-out draw, the environment draw and the task set, with task_order "
     "alone differing and the reversed suite the as-built one reversed",
     "falsifier: any other field differing, a different task set, or an arm missing"),
    ("BL2", "and the position effect holds on the benchmark's own world",
     "In both rolls the first-taught task's gain exceeds the last-taught task's",
     "falsifier: either roll where it does not"),
    ("BL3", "and the last-taught task is cost under the reversed order",
     "The reversed roll's last-taught task's gain is at most zero",
     f"falsifier: above {LAST_FIRES:+.2f}; null: between"),
    ("BL4", "and the reversal costs the buffer on this world",
     "The reversed roll's mean gain over the three tasks is below the as-built roll's",
     "falsifier: not below"),
    ("BL5", f"and the same task moves with its position here too, {CONTRAST:.2f}",
     "For each of the two tasks that is first in one roll and last in the other, its gain when taught first exceeds "
     "its gain when taught last by at least 0.05",
     f"falsifier: either contrast below {CONTRAST_FIRES:.2f}; null: between"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _roll(path: Path) -> dict | None:
    doc = load(path)
    if not doc:
        return None
    tasks = [t.get("name") if isinstance(t, dict) else t for t in (doc.get("tasks") or [])]
    got = {}
    for arm in ARMS:
        reps = ((doc.get("methods") or {}).get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        got[arm] = {"replicates": len(reps),
                    "final": [statistics.fmean([r["final_per_task"][k] for r in reps]) for k in range(len(tasks))]}
    gains = [got["replay"]["final"][k] - got["naive"]["final"][k] for k in range(len(tasks))]
    ed = doc.get("env_draw") or {}
    cfg = doc.get("config") or {}
    return {"artifact": path.name, "tasks": tasks, "gain": gains, "per_task": dict(zip(tasks, gains)),
            "replicates": min(got["naive"]["replicates"], got["replay"]["replicates"]),
            "mean_gain": statistics.fmean(gains), "task_order": cfg.get(ORDER),
            "shared": {k: doc.get(k) for k in SHARED},
            "draws": {k: ed.get(k) for k in DRAW_FIELDS},
            "config": {k: cfg.get(k) for k in CONFIG_FIELDS}}


def reading(as_built: Path = AS_BUILT, reverse: Path = REVERSE) -> dict:
    out = {"ok": True, "reason": None, "rolls": {}, "same": {}, "contrasts": {}}
    a, b = _roll(as_built), _roll(reverse)
    if a is None:
        return {**out, "ok": False, "reason": f"{as_built} is absent or carries no arm"}
    if b is None:
        return {**out, "ok": False, "reason": f"{reverse} is absent or carries no arm"}
    out["rolls"] = {"as_built": a, "reverse": b}
    same = {k: (a["shared"].get(k) == b["shared"].get(k)) for k in SHARED if k != "tasks"}
    #: the task list differs by construction -- that is the reversal -- so the pair agrees on the task **set**
    same["tasks"] = set(a["tasks"]) == set(b["tasks"])
    same.update({f"env_draw.{k}": (a["draws"].get(k) == b["draws"].get(k)) for k in DRAW_FIELDS})
    same.update({f"config.{k}": (a["config"].get(k) == b["config"].get(k)) for k in CONFIG_FIELDS})
    out["same"] = same
    out["same_tasks"] = (set(a["tasks"]) == set(b["tasks"])) and (b["tasks"] == list(reversed(a["tasks"])))
    out["orders"] = {"as_built": a["task_order"], "reverse": b["task_order"]}
    #: the two tasks that are first in one roll and last in the other, both directions
    for label, first, last in (("as_built_first", a, b), ("reverse_first", b, a)):
        task = first["tasks"][0]
        out["contrasts"][label] = {"task": task, "at_first": first["per_task"].get(task),
                                   "at_last": last["per_task"].get(task)}
        out["contrasts"][label]["difference"] = (out["contrasts"][label]["at_first"]
                                                 - out["contrasts"][label]["at_last"])
    out["spans"] = {"replicates": sorted({r["replicates"] for r in (a, b)}),
                    "as_built_mean": a["mean_gain"], "reverse_mean": b["mean_gain"],
                    "rise": b["mean_gain"] - a["mean_gain"],
                    "as_built_first_over_last": a["gain"][0] - a["gain"][-1],
                    "reverse_first_over_last": b["gain"][0] - b["gain"][-1],
                    "reverse_last": b["gain"][-1],
                    "smallest_contrast": min(c["difference"] for c in out["contrasts"].values())}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no arm"}
                for c in CLAIMS]
    differ = {k: v for k, v in r["same"].items() if not v}
    thin = {lbl: roll["replicates"] for lbl, roll in r["rolls"].items() if roll["replicates"] < MIN_REPS}
    j1 = {"id": "BL1",
          "measured": f"`{r['rolls']['as_built']['artifact']}` and `{r['rolls']['reverse']['artifact']}`, the config "
                      f"differing in `task_order` alone ({r['orders']}) with the reversed suite the as-built one "
                      f"reversed ({r['same_tasks']}), at {r['spans']['replicates']} replicates",
          "verdict": f"MET -- the pair is carried over {len(r['same'])} shared fields with `task_order` alone differing"
                     if (not differ and r["same_tasks"] and not thin) else
                     f"FALSIFIER FIRED -- differing {differ}, same tasks {r['same_tasks']}, thin {thin}"}
    margins = {lbl: round(roll["gain"][0] - roll["gain"][-1], 4) for lbl, roll in r["rolls"].items()}
    behind = {k: v for k, v in margins.items() if v <= POSITION}
    j2 = {"id": "BL2",
          "measured": f"the first-taught task over the last-taught one is {margins} on the benchmark's own world",
          "verdict": f"MET -- the position effect holds in both rolls, the smallest margin "
                     f"{min(margins.values()):+.4f}" if not behind else f"FALSIFIER FIRED -- {behind}"}
    last = r["spans"]["reverse_last"]
    j3 = {"id": "BL3",
          "measured": f"under the reversed order the last-taught task's gain is {last:+.4f} and the roll's per-task "
                      f"gains are {[round(x, 4) for x in r['rolls']['reverse']['gain']]}",
          "verdict": f"MET -- the last-taught task is cost under the reversed order, {last:+.4f}" if last <= LAST_BAR
                     else f"FALSIFIER FIRED -- {last:+.4f} is above the bar" if last > LAST_FIRES else
                     f"NULL -- {last:+.4f}, between {LAST_BAR:+.2f} and {LAST_FIRES:+.2f}"}
    rise = r["spans"]["rise"]
    j4 = {"id": "BL4",
          "measured": f"the reversed roll's mean gain is {r['spans']['reverse_mean']:+.4f} against the as-built "
                      f"roll's {r['spans']['as_built_mean']:+.4f}, a change of {rise:+.4f}",
          "verdict": f"MET -- the reversal costs the buffer on this world, {rise:+.4f}" if rise < 0 else
          f"FALSIFIER FIRED -- the reversal gains {rise:+.4f}"}
    contrasts = {k: round(c["difference"], 4) for k, c in r["contrasts"].items()}
    weak = {k: v for k, v in contrasts.items() if v < CONTRAST}
    j5 = {"id": "BL5",
          "measured": f"the same task taught first against taught last is "
                      f"{ {k: (r['contrasts'][k]['task'], v) for k, v in contrasts.items()} }",
          "verdict": f"MET -- the same task gains at least {r['spans']['smallest_contrast']:+.4f} more when it is "
                     f"taught first, in both directions" if not weak else
                     f"FALSIFIER FIRED -- {weak}" if any(v < CONTRAST_FIRES for v in weak.values()) else
                     f"NULL -- {weak} between the bars"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the order the benchmark's world is taught in ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source, rolled both ways at the same twenty replicates")
    print(f"\n   {'roll':>10} {'order':>9} {'tasks':>52} {'gain 0/1/2':>26} {'mean':>8}")
    for lbl, roll in r["rolls"].items():
        print(f"   {lbl:>10} {str(roll['task_order']):>9} {'>'.join(roll['tasks'])[:52]:>52} "
              + " ".join(f"{x:+.4f}" for x in roll["gain"]) + f" {roll['mean_gain']:+8.4f}")
    print("\n   the same task, taught first against taught last:")
    for k, c in r["contrasts"].items():
        print(f"      {k:>14}: {c['task']} at first {c['at_first']:+.4f} against at last {c['at_last']:+.4f}, a "
              f"margin of {c['difference']:+.4f}")
    s = r["spans"]
    print(f"\n   the first-over-last margin is {s['as_built_first_over_last']:+.4f} as-built and "
          f"{s['reverse_first_over_last']:+.4f} reversed; the mean gain moves {s['rise']:+.4f}")
    print("\n== the registered claims, BL1-BL5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e425` and `e426` measured the position effect on the overlap and assembly suites and both registered")
    print("    that the benchmark's own world was not in the reading; this drives that roll)")
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
