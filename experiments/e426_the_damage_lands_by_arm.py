"""E426 -- the damage lands by arm: the buffer pays at the end and the penalty pays in the middle.

`e425` read the corpus's order axis for the `naive`/`replay` pair on three configurations rolled both ways and found
the trade following the position and not the task. The same rolls carry the **penalty** arms -- `ewc` on all three,
`ewc-block` and `ewc-block-rand` on the assembly suite at five arms -- so the same question can be asked of every arm
the corpus ran there, and one more: where in the order each arm's damage falls.

**This unit reads all of it.** Sixteen arm-rolls: the buffer in six rolls and the three penalties in ten, each
against its roll's own `naive`, over the three positions. No training, no probe. Five claims, registered before this
unit's pass over the runs.

- **BB1 -- and the ledger is carried.** Three configurations rolled under both orders, each roll carrying `naive`
  beside at least one penalty arm and `replay`, at five or ten replicates. **Falsifier**: a missing arm, a missing
  roll, or a field other than `task_order` differing.
- **BB2 -- and the position effect is every arm's.** In every one of the sixteen arm-rolls the gain at position 0
  exceeds the gain at the last position. **Falsifier**: any arm-roll where it does not. *This is the unit's own
  prediction: `e425` found the effect for the buffer, and if it is the sequence's it should hold for every arm the
  sequence was run with.*
- **BB3 -- and the first position gains, for every arm but one.** The gain at position 0 is positive in at least
  **15** of the sixteen. **Falsifier**: below **13**. **Null**: between.
- **BB4 -- and only the buffer's trade pays.** `replay`'s mean gain over the three positions is positive in **all
  six** rolls while every penalty arm-roll's mean is negative. **Falsifier**: any buffer roll at or below zero, or any
  penalty arm-roll at or above zero.
- **BB5 -- and the damage lands elsewhere.** The buffer's **worst** position is the last in all six rolls, while the
  penalty arms' worst position is the **middle** in at least **8** of their ten. **Falsifier**: any buffer roll whose
  worst is not the last, or fewer than **6** penalty arm-rolls whose worst is the middle.

**What it can do beyond that.** It separates the two arms' trades by where they are paid. On the same circuits and
draws the buffer's worst position is the task taught last (six of six), while `ewc` and its block variants are worst
in the middle (nine of ten) -- so the penalty's regularisation costs it the task it is halfway through learning, which
is why its trade does not pay. And the position effect `e425` found for the buffer holds for all sixteen arm-rolls,
with the oldest position ahead of the newest in every one.

**What it cannot do.** *Three configurations and five replicates for the penalties*: `ewc` appears six times at five
or ten replicates, `ewc-block` and `ewc-block-rand` twice each at five, so the penalty side of the ledger is thin and
its means carry the draws' spread. *And the arms are the corpus's*: one buffer setting and two penalty strengths. *And
the ordering is one protocol's*: three tasks with the middle left in place, so a full permutation is not here. *And the
metric is the corpus's*: the last task is never forgotten after it is taught, so its gain is a `learned` difference.
*And a ledger is not a mechanism.*
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: three configurations rolled under both orders, `task_order` the only field that differs
PAIRS = {
    "overlap": (Path("runs/e315_order_as_built.json"), Path("runs/e315_order_reverse.json")),
    "assembly": (Path("runs/e316_assembly_as_built.json"), Path("runs/e316_assembly_reverse.json")),
    "assembly-five": (Path("runs/e317_five_as_built.json"), Path("runs/e317_five_reverse.json")),
}
AS_BUILT, REVERSE = "as_built", "reverse"
BASELINE = "naive"
BUFFER = "replay"
RUN_FIELDS = ("json_out", "save_theta")
MIN_CONFIGS = 3
MIN_REPS = 5
MIN_ARMS = 3
MIN_FIRST_POSITIVE = 15
FIRST_POSITIVE_FIRES = 13
MIN_MIDDLE_WORST = 8
MIDDLE_FIRST = 6
CLAIMS = (
    ("BB1", f"and the ledger is carried, over at least {MIN_CONFIGS} configurations and {MIN_ARMS} arms",
     "Three configurations rolled under both orders, each roll carrying naive beside at least one penalty arm and "
     "replay, at five or ten replicates",
     "falsifier: a missing arm, a missing roll, or a field other than task_order differing"),
    ("BB2", "and the position effect is every arm's",
     "In every one of the sixteen arm-rolls the gain at position 0 exceeds the gain at the last position",
     "falsifier: any arm-roll where it does not"),
    ("BB3", f"and the first position gains, for every arm but one, {MIN_FIRST_POSITIVE} of sixteen",
     "The gain at position 0 is positive in at least 15 of the sixteen",
     f"falsifier: below {FIRST_POSITIVE_FIRES}; null: between"),
    ("BB4", "and only the buffer's trade pays",
     "replay's mean gain over the three positions is positive in all six rolls while every penalty arm-roll's mean is "
     "negative",
     "falsifier: any buffer roll at or below zero, or any penalty arm-roll at or above zero"),
    ("BB5", f"and the damage lands elsewhere, {MIN_MIDDLE_WORST} of ten",
     "The buffer's worst position is the last in all six rolls, while the penalty arms' worst position is the middle "
     "in at least eight of their ten",
     f"falsifier: any buffer roll whose worst is not the last, or fewer than {MIDDLE_FIRST} penalty arm-rolls whose "
     f"worst is the middle"),
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
    if BASELINE not in methods:
        return None
    reps = (methods.get(BASELINE) or {}).get("replicates") or []
    if not reps:
        return None
    base = [statistics.fmean([r["final_per_task"][k] for r in reps]) for k in range(len(tasks))]
    arms = {}
    for arm in sorted(methods):
        if arm == BASELINE:
            continue
        got = (methods.get(arm) or {}).get("replicates") or []
        if not got:
            continue
        final = [statistics.fmean([r["final_per_task"][k] for r in got]) for k in range(len(tasks))]
        arms[arm] = {"replicates": len(got), "gain": [final[k] - base[k] for k in range(len(tasks))]}
        arms[arm]["mean"] = statistics.fmean(arms[arm]["gain"])
        arms[arm]["worst"] = max(range(len(tasks)), key=lambda k: -arms[arm]["gain"][k])
    return {"artifact": path.name, "tasks": tasks, "arms": arms, "doc": doc}


def reading(pairs: dict = PAIRS) -> dict:
    out = {"ok": True, "reason": None, "rolls": [], "configs": {}}
    for name, (a_path, b_path) in pairs.items():
        a, b = _roll(a_path), _roll(b_path)
        if a is None:
            return {**out, "ok": False, "reason": f"configuration {name}: {a_path} is absent or carries no naive arm"}
        if b is None:
            return {**out, "ok": False, "reason": f"configuration {name}: {b_path} is absent or carries no naive arm"}
        ca, cb = (a["doc"].get("config") or {}), (b["doc"].get("config") or {})
        differing = sorted(k for k in set(ca) | set(cb) if k not in RUN_FIELDS and ca.get(k) != cb.get(k))
        for order, roll in ((AS_BUILT, a), (REVERSE, b)):
            for arm, got in roll["arms"].items():
                out["rolls"].append({"config": name, "order": order, "arm": arm, "artifact": roll["artifact"],
                                     "replicates": got["replicates"], "gain": got["gain"], "mean": got["mean"],
                                     "worst": got["worst"], "positions": len(roll["tasks"])})
        out["configs"][name] = {"differing_config": differing,
                                "same_tasks": set(a["tasks"]) == set(b["tasks"]) and a["tasks"] == list(reversed(b["tasks"])),
                                "arms": sorted(set(a["arms"]) | set(b["arms"]))}
    buffer = [r for r in out["rolls"] if r["arm"] == BUFFER]
    penalty = [r for r in out["rolls"] if r["arm"] != BUFFER]
    out["spans"] = {"rolls": len(out["rolls"]), "buffer_rolls": len(buffer), "penalty_rolls": len(penalty),
                    "arms": sorted({r["arm"] for r in out["rolls"]}),
                    "replicates": sorted({r["replicates"] for r in out["rolls"]}),
                    "first_ahead": sum(1 for r in out["rolls"] if r["gain"][0] > r["gain"][-1]),
                    "first_positive": sum(1 for r in out["rolls"] if r["gain"][0] > 0),
                    "first_positive_min": min((r["gain"][0] for r in out["rolls"] if r["gain"][0] > 0),
                                              default=None),
                    "buffer_positive_means": sum(1 for r in buffer if r["mean"] > 0),
                    "penalty_negative_means": sum(1 for r in penalty if r["mean"] < 0),
                    "buffer_worst_last": sum(1 for r in buffer if r["worst"] == r["positions"] - 1),
                    "penalty_worst_middle": sum(1 for r in penalty if r["worst"] == 1),
                    "worst_first_over_last": min(r["gain"][0] - r["gain"][-1] for r in out["rolls"])}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no naive arm"}
                for c in CLAIMS]
    cfg, s = r["configs"], r["spans"]
    broken = {n: {"differing": c["differing_config"], "same_tasks": c["same_tasks"]}
              for n, c in cfg.items() if c["differing_config"] != ["task_order"] or not c["same_tasks"]}
    thin = [f"{x['config']}/{x['order']}/{x['arm']}" for x in r["rolls"] if x["replicates"] < MIN_REPS]
    no_buffer = sum(1 for c in cfg.values() if BUFFER not in c["arms"])
    j1 = {"id": "BB1",
          "measured": f"{len(cfg)} configurations rolled under both orders, {s['rolls']} arm-rolls over "
                      f"{len(s['arms'])} arms at {s['replicates']} replicates",
          "verdict": f"MET -- the ledger is carried, {s['rolls']} arm-rolls over {len(s['arms'])} arms" if
                     (len(cfg) >= MIN_CONFIGS and len(s["arms"]) >= MIN_ARMS and not broken and not thin
                      and not no_buffer) else
                     f"FALSIFIER FIRED -- {broken or thin[:3] or no_buffer}"}
    behind = {f"{x['config']}/{x['order']}/{x['arm']}": [round(v, 4) for v in x["gain"]]
              for x in r["rolls"] if x["gain"][0] <= x["gain"][-1]}
    j2 = {"id": "BB2",
          "measured": f"the first position is ahead of the last in {s['first_ahead']} of {s['rolls']} arm-rolls, the "
                      f"smallest margin {s['worst_first_over_last']:+.4f}",
          "verdict": f"MET -- the position effect holds for all {s['rolls']} arm-rolls" if not behind else
                     f"FALSIFIER FIRED -- {behind}"}
    j3 = {"id": "BB3",
          "measured": f"the first position's gain is positive in {s['first_positive']} of {s['rolls']} arm-rolls, the "
                      f"smallest of those {s['first_positive_min']:.2e}",
          "verdict": f"MET -- the first position gains in {s['first_positive']} of {s['rolls']}" if
                     s["first_positive"] >= MIN_FIRST_POSITIVE else
                     f"FALSIFIER FIRED -- {s['first_positive']} is under the bar" if
                     s["first_positive"] < FIRST_POSITIVE_FIRES else
                     f"NULL -- {s['first_positive']}, between {FIRST_POSITIVE_FIRES} and {MIN_FIRST_POSITIVE}"}
    ba = {f"{x['config']}/{x['order']}": round(x["mean"], 4) for x in r["rolls"] if x["arm"] == BUFFER}
    pa = {f"{x['config']}/{x['order']}/{x['arm']}": round(x["mean"], 4) for x in r["rolls"] if x["arm"] != BUFFER}
    j4 = {"id": "BB4",
          "measured": f"the buffer's mean gains are {ba} and the penalties' {pa}",
          "verdict": f"MET -- only the buffer's trade pays: {s['buffer_positive_means']} of {s['buffer_rolls']} buffer "
                     f"rolls positive against {s['penalty_negative_means']} of {s['penalty_rolls']} penalty rolls "
                     f"negative" if (s["buffer_positive_means"] == s["buffer_rolls"]
                                     and s["penalty_negative_means"] == s["penalty_rolls"]) else
                     f"FALSIFIER FIRED -- { {k: v for k, v in ba.items() if v <= 0} } or "
                     f"{ {k: v for k, v in pa.items() if v >= 0} }"}
    j5 = {"id": "BB5",
          "measured": f"the buffer's worst position is the last in {s['buffer_worst_last']} of {s['buffer_rolls']} "
                      f"rolls, the penalties' worst is the middle in {s['penalty_worst_middle']} of "
                      f"{s['penalty_rolls']}",
          "verdict": f"MET -- the damage lands by arm: the buffer is worst last and the penalties worst in the "
                     f"middle, {s['penalty_worst_middle']} of {s['penalty_rolls']}" if
                     (s["buffer_worst_last"] == s["buffer_rolls"] and s["penalty_worst_middle"] >= MIN_MIDDLE_WORST)
                     else
                     f"FALSIFIER FIRED -- {s['buffer_worst_last']} of {s['buffer_rolls']} buffer rolls worst last "
                     f"and {s['penalty_worst_middle']} of {s['penalty_rolls']} penalty rolls worst in the middle"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the damage lands by arm ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   three configurations rolled under both orders, every arm the roll carries against its own naive")
    print(f"\n   {'configuration':>15} {'order':>10} {'arm':>16} {'gain by position':>30} {'mean':>9} {'worst':>6}")
    for x in sorted(r["rolls"], key=lambda x: (x["config"], x["order"], x["arm"])):
        print(f"   {x['config']:>15} {x['order']:>10} {x['arm']:>16} "
              + " ".join(f"{v:+.4f}" for v in x["gain"]) + f" {x['mean']:+9.4f} {x['worst']:6d}")
    s = r["spans"]
    print(f"\n   {s['rolls']} arm-rolls over {s['arms']}: the first position ahead in {s['first_ahead']}, positive in "
          f"{s['first_positive']}; the buffer's mean positive in {s['buffer_positive_means']} of {s['buffer_rolls']} "
          f"against the penalties' negative in {s['penalty_negative_means']} of {s['penalty_rolls']}; the buffer's "
          f"worst last in {s['buffer_worst_last']} of {s['buffer_rolls']} and the penalties' worst in the middle in "
          f"{s['penalty_worst_middle']} of {s['penalty_rolls']}")
    print("\n== the registered claims, BB1-BB5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e425` read the order axis for the buffer alone; the same rolls carry the penalties, and each arm's")
    print("    damage falls in a different place)")
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
