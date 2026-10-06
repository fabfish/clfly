"""E441 -- the anchor's price under another order: whether what `e438` measured on the card's world is the position's or the task's.

`e437` read the **buffer's** ledger on the card's world under three orders and found the position effect to be the
position's: the same task, moved from the first position to the last, loses about **0.33** of its gain, and the last
position's loss held at **-0.0604**, **-0.0208** and **-0.0552** across three different orders. `e438` then put the first
anchor on that world under the **as-built** order alone and found it is not a buffer: `ewc-block` over `naive` reads
**+0.0625**, **-0.0354** and **-0.1177** by position, behind the baseline on the mean diagonal by **-0.0302**, and `e440`
read the two parameters that carry that price. `e438`, `e439` and `e440` all closed on the same gap: **one order**, so no
anchor on this world has a second position for any task.

**This unit drives the anchor's second order.** The same configuration with `--task-order 1,0,2` alone differing from
`e438`'s, at the same twenty replicates with `naive`, `ewc-block` and `replay`, so that the two shared arms can be
checked against `e437`'s own rotated roll record for record and the anchor's ledger can be read at a second order. Under
`1,0,2` the suite is trained `loop_heading`, `loop_odour_identity`, `loop_odour_input`, so the **last position holds the
same task as the as-built roll** and the **middle position holds a different one** -- which is what separates the price's
position from the price's task. Five claims, registered before the new run's reading was opened.

- **BS1 -- and the run is one configuration.** The three arms at **20** replicates, every other recorded field agreeing
  with `e438`'s with `task_order` alone differing, the task sets equal, and the new run's `naive` and `replay` replicates
  **bit-identical** to `e437`'s rotated roll and to `e438`'s as-built one. **Falsifier**: any other field differing, an arm
  missing or short, or any shared replicate's record differing.
- **BS2 -- and the anchor pays the last position under this order too.** `ewc-block` minus `naive` on the last-taught task
  is at most **zero**. **Falsifier**: above **+0.05**; **null**: between.
- **BS3 -- and it pays about what it paid under the as-built order.** The last-taught task's cost under `1,0,2` is within
  **0.05** of the as-built one's. **Falsifier**: **0.10** or more apart; **null**: between. *The last position holds the
  same task in both orders, so this is the anchor's price read twice at one cell and its answer is the price's
  order-sensitivity.*
- **BS4 -- and the anchor is behind the baseline at the middle position too.** `ewc-block` minus `naive` on the middle
  task is at most **zero**. **Falsifier**: above **+0.05**; **null**: between. *This is the position whose task differs
  between the two orders, so agreeing with the as-built answer here and not only at the last is the reading that says the
  shape is the anchor's rather than the suite's.*
- **BS5 -- and its price is not the buffer's under this order either.** The buffer's last-taught cost exceeds the
  anchor's. **Falsifier**: at or below it.

**What it can do beyond that.** It puts `e438`'s falsified claim -- that the earlier-position advantage belongs to a
buffer and not to anchoring -- in the one place it can be wrong about the *suite*: a second order in which the middle
position holds a different task. If the anchor's three-position ledger reads the same way under both orders then the
shape `e438` measured is the anchor's on this world, and `e437`'s cliff is the buffer's and not the world's.

**What it cannot do.** *Two orders* of a three-task suite's six, so the other four are not in the reading. *And one
cell*: the card's world at twenty replicates, so the other five draws and the three streams are not either. *And one
anchor*: `ewc-block-rand` is absent, which `e439` makes cheap to argue about but does not measure here. *And an order is
not a mechanism*: that the ledger holds under a second order does not say which of the corpus's instruments keeps it.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the anchor under a second order, the roll it is compared with, and the buffer's own rotated roll as the control
RUNS = {
    "new": Path("runs/e441_earned_label_anchor_order102_20reps.json"),
    "asbuilt": Path("runs/e438_earned_label_three_arms_20reps.json"),
    "control": Path("runs/e437_earned_label_cue0_order102_20reps.json"),
}
ARMS = ("naive", "ewc-block", "replay")
SHARED_ARMS = ("naive", "replay")
ANCHOR = "ewc-block"
BASELINE = "naive"
BUFFER = "replay"
ORDER = "task_order"
SHARED = ("circuit", "readout", "tasks")
DRAW_FIELDS = ("cue_sha1", "action_sha1", "world_read_sha1", "world_drive_sha1", "world_coupling_sha1")
IGNORED = ("json_out", "save_theta", "methods", ORDER)
N_TASKS = 3
N_ARMS = 3
MIN_REPS = 20
LAST_BAR = 0.0
LAST_FIRES = 0.05
MOVES = 0.05
MOVES_FIRES = 0.10
MIDDLE_BAR = 0.0
MIDDLE_FIRES = 0.05
CLAIMS = (
    ("BS1", f"and the run is one configuration, at {MIN_REPS} replicates on all three arms",
     "The three arms at twenty replicates, every other recorded field agreeing with e438's with task_order alone "
     "differing, the task sets equal, and the new run's naive and replay bit-identical to e437's rotated roll and to "
     "e438's as-built one",
     "falsifier: any other field differing, an arm missing or short, or any shared replicate's record differing"),
    ("BS2", "and the anchor pays the last position under this order too",
     "ewc-block minus naive on the last-taught task is at most zero",
     f"falsifier: above {LAST_FIRES:+.2f}; null: between"),
    ("BS3", f"and it pays about what it paid under the as-built order, within {MOVES:.2f}",
     "The last-taught task's cost under 1,0,2 is within 0.05 of the as-built one's",
     f"falsifier: {MOVES_FIRES:.2f} or more apart; null: between"),
    ("BS4", "and the anchor is behind the baseline at the middle position too",
     "ewc-block minus naive on the middle task is at most zero",
     f"falsifier: above {MIDDLE_FIRES:+.2f}; null: between"),
    ("BS5", "and its price is not the buffer's under this order either",
     "The buffer's last-taught cost exceeds the anchor's",
     "falsifier: at or below it"),
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
    methods = doc.get("methods") or {}
    got = {}
    for arm in ARMS:
        if arm not in methods:
            continue
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        got[arm] = {"replicates": len(reps),
                    "final": [statistics.fmean([r["final_per_task"][k] for r in reps]) for k in range(len(tasks))],
                    "diagonal": [statistics.fmean(r["final_per_task"]) for r in reps],
                    "forgetting": statistics.fmean([r["mean_forgetting"] for r in reps]),
                    "records": [{"final_per_task": list(r["final_per_task"]),
                                 "mean_forgetting": r["mean_forgetting"]} for r in reps]}
    ed = doc.get("env_draw") or {}
    cfg = doc.get("config") or {}
    return {"artifact": path.name, "tasks": tasks, "arms": got, "task_order": cfg.get(ORDER),
            "shared": {k: doc.get(k) for k in SHARED}, "draws": {k: ed.get(k) for k in DRAW_FIELDS},
            "config": {k: cfg.get(k) for k in sorted(set(cfg) - set(IGNORED))}}


def _identical(a: list, b: list) -> dict:
    out = {"equal": True, "n": min(len(a), len(b)), "first_differing": None, "fields": []}
    if len(a) != len(b):
        out["equal"] = False
        return out
    for i, (x, y) in enumerate(zip(a, b)):
        if x == y:
            continue
        out["equal"] = False
        out["first_differing"] = i
        out["fields"] = sorted(k for k in set(x) | set(y) if x.get(k) != y.get(k))
        break
    return out


def reading(runs: dict = RUNS) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "identical": {}, "gains": {}, "by_task": {},
           "orders": {}, "spans": {}}
    for label, path in runs.items():
        got = _roll(path)
        if got is None:
            return {**out, "ok": False, "reason": f"roll {label}: {path} is absent or carries no arm"}
        out["runs"][label] = got
    new, asbuilt, control = out["runs"]["new"], out["runs"]["asbuilt"], out["runs"]["control"]
    missing = [a for a in ARMS if a not in new["arms"]]
    if missing:
        return {**out, "ok": False, "reason": f"the new roll carries no arm for {missing}"}
    #: every recorded field of the two three-arm rolls, with the order the one the run moves
    same = {}
    fields = sorted(set(new["config"]) | set(asbuilt["config"]))
    for k in fields:
        same[f"config.{k}"] = new["config"].get(k) == asbuilt["config"].get(k)
    for k in DRAW_FIELDS:
        same[f"env_draw.{k}"] = new["draws"].get(k) == asbuilt["draws"].get(k)
    same["circuit"] = new["shared"].get("circuit") == asbuilt["shared"].get("circuit")
    same["readout"] = new["shared"].get("readout") == asbuilt["shared"].get("readout")
    same["tasks"] = set(new["tasks"]) == set(asbuilt["tasks"])
    out["same"] = same
    for other in ("control", "asbuilt"):
        for arm in SHARED_ARMS:
            if arm not in out["runs"][other]["arms"]:
                continue
            out["identical"][f"new/{other}:{arm}"] = _identical(new["arms"][arm]["records"],
                                                                out["runs"][other]["arms"][arm]["records"])
    for label, roll in out["runs"].items():
        for pair in (("replay-naive", (BUFFER, BASELINE)), ("ewc-naive", (ANCHOR, BASELINE)),
                     ("ewc-replay", (ANCHOR, BUFFER))):
            name, (a, b) = pair
            if a in roll["arms"] and b in roll["arms"]:
                out["gains"][f"{label}.{name}"] = [roll["arms"][a]["final"][k] - roll["arms"][b]["final"][k]
                                                   for k in range(N_TASKS)]
    for label, roll in out["runs"].items():
        out["orders"][label] = roll["task_order"]
        out["by_task"][label] = {t: {"position": roll["tasks"].index(t),
                                     "gain": roll["arms"][ANCHOR]["final"][roll["tasks"].index(t)]
                                             - roll["arms"][BASELINE]["final"][roll["tasks"].index(t)]}
                                 for t in roll["tasks"] if ANCHOR in roll["arms"]}
    last_new = out["gains"]["new.ewc-naive"][-1]
    last_base = out["gains"]["asbuilt.ewc-naive"][-1]
    mid_new = out["gains"]["new.ewc-naive"][1]
    means = {label: statistics.fmean(roll["arms"][ANCHOR]["diagonal"]) - statistics.fmean(roll["arms"][BASELINE]["diagonal"])
             for label, roll in out["runs"].items() if ANCHOR in roll["arms"] and BASELINE in roll["arms"]}
    out["spans"] = {"replicates": sorted({v["replicates"] for roll in out["runs"].values()
                                         for v in roll["arms"].values()}),
                    "arms": {label: len(roll["arms"]) for label, roll in out["runs"].items()},
                    "same_fields": len(same),
                    "last": {"new": last_new, "asbuilt": last_base, "move": last_new - last_base},
                    "middle": {"new": mid_new},
                    "means": means, "orders": out["orders"],
                    "last_tasks": {"new": new["tasks"][-1], "asbuilt": asbuilt["tasks"][-1]},
                    "middle_tasks": {"new": new["tasks"][1], "asbuilt": asbuilt["tasks"][1]}}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no arm"} for c in CLAIMS]
    differ = sorted(k for k, v in r["same"].items() if not v)
    not_identical = sorted(k for k, v in r["identical"].items() if not v["equal"])
    thin = {f"{lbl}.{a}": v["replicates"] for lbl, roll in r["runs"].items() for a, v in roll["arms"].items()
            if v["replicates"] < MIN_REPS}
    short = {} if len(r["runs"]["new"]["arms"]) >= N_ARMS else {"new": sorted(r["runs"]["new"]["arms"])}
    j1 = {"id": "BS1",
          "measured": f"the new roll carries {len(r['runs']['new']['arms'])} arms at {r['spans']['replicates']} "
                      f"replicates over {r['spans']['same_fields']} compared fields, the orders {r['spans']['orders']}, "
                      f"the shared arms bit-identical {len(r['identical']) - len(not_identical)} of "
                      f"{len(r['identical'])}",
          "verdict": "MET -- three arms on one configuration with the order alone differing, the shared arms "
                     "reproducing both the as-built roll and the buffer's own rotated one" if
                     (not short and not differ and not not_identical and not thin) else
                     f"FALSIFIER FIRED -- differing {differ}, not bit-identical {not_identical}, thin {thin}, "
                     f"short {short}"}
    last = r["spans"]["last"]["new"]
    j2 = {"id": "BS2",
          "measured": f"on the last-taught task `{r['spans']['last_tasks']['new']}` ewc-block over naive is "
                      f"{last:+.4f}, against replay's {r['gains']['new.replay-naive'][-1]:+.4f}",
          "verdict": f"MET -- the anchor pays the last position under this order too, {last:+.4f}" if last <= LAST_BAR
                     else f"FALSIFIER FIRED -- {last:+.4f} is above the bar" if last > LAST_FIRES else
                     f"NULL -- {last:+.4f} between {LAST_BAR:+.2f} and {LAST_FIRES:+.2f}"}
    move = abs(r["spans"]["last"]["move"])
    j3 = {"id": "BS3",
          "measured": f"the anchor's last-position cost is {last:+.4f} under `1,0,2` and "
                      f"{r['spans']['last']['asbuilt']:+.4f} as-built, {move:.4f} apart",
          "verdict": f"MET -- the anchor pays the last position about what it paid, {move:.4f} apart" if move <= MOVES
                     else f"FALSIFIER FIRED -- the move is {move:.4f}" if move >= MOVES_FIRES else
                     f"NULL -- the move is {move:.4f}, between {MOVES:.2f} and {MOVES_FIRES:.2f}"}
    middle = r["spans"]["middle"]["new"]
    j4 = {"id": "BS4",
          "measured": f"on the middle task `{r['spans']['middle_tasks']['new']}`, which the as-built order puts a "
                      f"different task in, ewc-block over naive is {middle:+.4f}",
          "verdict": f"MET -- the anchor is behind the baseline at the middle position too, {middle:+.4f}" if
                     middle <= MIDDLE_BAR else
                     f"FALSIFIER FIRED -- {middle:+.4f} is above the bar" if middle > MIDDLE_FIRES else
                     f"NULL -- {middle:+.4f} between {MIDDLE_BAR:+.2f} and {MIDDLE_FIRES:+.2f}"}
    buffer_last = r["gains"]["new.replay-naive"][-1]
    j5 = {"id": "BS5",
          "measured": f"under `1,0,2` the buffer's last-taught cost is {buffer_last:+.4f} against the anchor's "
                      f"{last:+.4f}",
          "verdict": f"MET -- the buffer is less penalised at the last position than the anchor by "
                     f"{buffer_last - last:+.4f}" if buffer_last > last else
                     f"FALSIFIER FIRED -- the buffer is not above the anchor"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the anchor's price under another order ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source and the earned label, as-built and `1,0,2`, twenty replicates")
    print(f"\n   {'roll':>9} {'order':>9} {'tasks in the order trained':>62}")
    for label, roll in r["runs"].items():
        print(f"   {label:>9} {str(roll['task_order']):>9} {'>'.join(roll['tasks'])[:62]:>62}")
    print("\n   the gain over naive, by position:")
    for label in ("asbuilt", "new"):
        for name in ("ewc-naive", "replay-naive", "ewc-replay"):
            key = f"{label}.{name}"
            if key in r["gains"]:
                print(f"      {key:>18}: " + " ".join(f"{x:+.4f}" for x in r["gains"][key]))
    print("\n   the anchor's gain over naive, task by task against the position it sat in:")
    for label, spots in r["by_task"].items():
        for task, got in spots.items():
            print(f"      {label:>9} {task:>22} p{got['position']} {got['gain']:+.4f}")
    m = r["spans"]["means"]
    print(f"\n   the anchor over the baseline on the mean diagonal: " +
          ", ".join(f"{k} {v:+.4f}" for k, v in m.items()))
    print(f"   the shared arms against e437's rotated roll and e438's: " +
          ", ".join(f"{k} {v['equal']}" for k, v in r["identical"].items()))
    print("\n== the registered claims, BS1-BS5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e437` read the buffer's ledger as the position's; `e438` read the anchor's at one order. This puts")
    print("    the anchor on a second order, whose middle position holds a different task from the as-built one's)")
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
