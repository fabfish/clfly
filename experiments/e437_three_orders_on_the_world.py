"""E437 -- three orders on the benchmark's world: a third permutation, and the position ledger across all three.

`e436` drove the missing roll the card's order clause named -- the benchmark's own world with the as-built order and
with `reverse` -- and found the position effect there (**+0.3500** and **+0.3594**) but the reversal *gaining*
(**+0.0243**) rather than costing the buffer. It registered one permutation as what it could not settle.

**This unit drives a third order and reads the three together.** The same configuration again, with `--task-order 1,0,2`
alone differing, at the same twenty replicates, so that every task of the suite occupies at least two positions across
the three rolls (`loop_odour_identity` 0, 2 and 1; `loop_heading` 1, 1 and 0; `loop_odour_input` 2, 0 and 2). Five
claims, registered before the new run's reading was opened.

- **BM1 -- and the three rolls are carried.** The same configuration three ways, `task_order` alone differing, each at
  **20** replicates with both arms, the task sets equal and each roll's order a permutation of the as-built suite.
  **Falsifier**: any other field differing, a missing arm, or an order that is not a permutation.
- **BM2 -- and the position effect holds in all three.** In every roll the first-taught task's gain exceeds the
  last-taught task's. **Falsifier**: any roll where it does not.
- **BM3 -- and the last-taught task is cost in all three.** Every roll's last-taught task's gain is at most **zero**.
  **Falsifier**: any above **+0.05**; **null**: between.
- **BM4 -- and the last position's value is the position's and not the task's.** The three rolls' last-taught gains
  span at most **0.05**. **Falsifier**: above **0.10**; **null**: between. *`e436`'s two orders already put two
  different tasks on the last position -- `loop_odour_input` (**-0.0604**) and `loop_odour_identity` (**-0.0208**) --
  and the loss held there; the third order repeats `loop_odour_input` on it, so a small span says the loss is the
  position's rather than the task's.*
- **BM5 -- and the first position's value is the position's too.** The three rolls' first-taught gains span at most
  **0.08**. **Falsifier**: above **0.15**; **null**: between. *This is where the third order pays: the three rolls put
  three different tasks first (`loop_odour_identity` **+0.2896**, `loop_odour_input` **+0.3385**, `loop_heading` new),
  so a small span is the position's value carrying across the task's identity.*

**What it can do beyond that.** It turns `e436`'s two rolls into a ledger over positions: with three orders every task
of the suite occupies at least two positions, so the gain of a position can be read against the gain of a task. If the
spans are small the trade is the sequence's quantitatively; if they are wide, the task's identity carries part of it and
the card's order clause should say which.

**What it cannot do.** *Three of six permutations*: a three-task suite has six, so half of them are not in this reading.
*And one cell*: the card's world at twenty replicates, so the other five draws and the three streams are not either.
*And one arm pair*: `naive` and `replay`, so the penalty arms are absent. *And a permutation is not a mechanism*: that
the order moves the numbers does not say which of the corpus's instruments the movement runs through.
"""

from __future__ import annotations

import argparse
import itertools
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the same configuration under three orders: `e380`'s as-built run, `e436`'s reversed one and this unit's
ROLLS = {
    "as-built": Path("runs/e380_earned_label_cue0_actionsource_20reps.json"),
    "reverse": Path("runs/e436_earned_label_cue0_reverse_20reps.json"),
    "rotate": Path("runs/e437_earned_label_cue0_order102_20reps.json"),
}
ORDER = "task_order"
SHARED = ("circuit", "readout", "tasks")
DRAW_FIELDS = ("cue_sha1", "action_sha1", "world_read_sha1", "world_drive_sha1", "world_coupling_sha1")
CONFIG_FIELDS = ("circuit_size", "iters", "lr", "lam", "replay_per_task", "replay_batch", "train", "test", "classes",
                 "support", "basis", "closed_loop", "loop_cue_at", "readout_from_world", "loop_symbols",
                 "loop_world_leak", "loop_world_dims", "loop_world_coupled", "repeats", "methods")
ARMS = ("naive", "replay")
N_TASKS = 3
MIN_ROLLS = 3
MIN_REPS = 20
POSITION = 0.0
LAST_BAR = 0.0
LAST_FIRES = 0.05
LAST_SPAN = 0.05
LAST_SPAN_FIRES = 0.10
FIRST_SPAN = 0.08
FIRST_SPAN_FIRES = 0.15
CLAIMS = (
    ("BM1", f"and the three rolls are carried, at {MIN_REPS} replicates and both arms",
     "The same configuration three ways, task_order alone differing, each at twenty replicates with both arms, the task "
     "sets equal and each roll's order a permutation of the as-built suite",
     "falsifier: any other field differing, a missing arm, or an order that is not a permutation"),
    ("BM2", "and the position effect holds in all three",
     "In every roll the first-taught task's gain exceeds the last-taught task's",
     "falsifier: any roll where it does not"),
    ("BM3", "and the last-taught task is cost in all three",
     "Every roll's last-taught task's gain is at most zero",
     f"falsifier: any above {LAST_FIRES:+.2f}; null: between"),
    ("BM4", f"and the last position's value is the position's, within {LAST_SPAN:.2f}",
     "The three rolls' last-taught gains span at most 0.05",
     f"falsifier: above {LAST_SPAN_FIRES:.2f}; null: between"),
    ("BM5", f"and the first position's value is the position's too, within {FIRST_SPAN:.2f}",
     "The three rolls' first-taught gains span at most 0.08",
     f"falsifier: above {FIRST_SPAN_FIRES:.2f}; null: between"),
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


def reading(rolls: dict = ROLLS) -> dict:
    out = {"ok": True, "reason": None, "rolls": {}, "same": {}, "positions": {}, "by_task": {}, "permutations": {}}
    for label, path in rolls.items():
        got = _roll(path)
        if got is None:
            return {**out, "ok": False, "reason": f"roll {label}: {path} is absent or carries no arm"}
        out["rolls"][label] = got
    base = out["rolls"]["as-built"]
    base_tasks = set(base["tasks"])
    reference = {k: base["shared"].get(k) for k in SHARED if k != "tasks"}
    reference.update({f"env_draw.{k}": base["draws"].get(k) for k in DRAW_FIELDS})
    reference.update({f"config.{k}": base["config"].get(k) for k in CONFIG_FIELDS})
    same = {}
    for label, roll in out["rolls"].items():
        shared = {k: roll["shared"].get(k) for k in SHARED if k != "tasks"}
        shared.update({f"env_draw.{k}": roll["draws"].get(k) for k in DRAW_FIELDS})
        shared.update({f"config.{k}": roll["config"].get(k) for k in CONFIG_FIELDS})
        row = {k: (v == reference[k]) for k, v in shared.items()}
        #: the suite is carried as a set, so that an order is a permutation rather than a re-listing
        row["tasks"] = set(roll["tasks"]) == base_tasks
        same[label] = row
    out["same"] = same
    #: each roll's trained order, and whether it is a permutation of the as-built suite
    for label, roll in out["rolls"].items():
        order = roll["task_order"]
        indices = None
        if order == "as-built":
            indices = list(range(N_TASKS))
        elif order == "reverse":
            indices = list(reversed(range(N_TASKS)))
        elif isinstance(order, str):
            try:
                indices = [int(x) for x in order.split(",")]
            except ValueError:
                indices = None
        out["permutations"][label] = {"task_order": order, "indices": indices,
                                      "permutation": (sorted(indices) == list(range(N_TASKS)))
                                      if indices is not None else False}
    out["by_task"] = {t: {label: {"position": roll["tasks"].index(t), "gain": roll["per_task"][t]}
                          for label, roll in out["rolls"].items()} for t in base["tasks"]}
    out["positions"] = {str(p): {label: roll["gain"][p] for label, roll in out["rolls"].items()}
                        for p in range(N_TASKS)}
    firsts = [roll["gain"][0] for roll in out["rolls"].values()]
    lasts = [roll["gain"][-1] for roll in out["rolls"].values()]
    means = [roll["mean_gain"] for roll in out["rolls"].values()]
    out["spans"] = {"rolls": len(out["rolls"]), "replicates": sorted({r["replicates"] for r in out["rolls"].values()}),
                    "first_span": max(firsts) - min(firsts), "last_span": max(lasts) - min(lasts),
                    "mean_span": max(means) - min(means),
                    "first_over_last": {label: roll["gain"][0] - roll["gain"][-1]
                                        for label, roll in out["rolls"].items()},
                    "lasts": {label: roll["gain"][-1] for label, roll in out["rolls"].items()},
                    "last_tasks": {label: roll["tasks"][-1] for label, roll in out["rolls"].items()}}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no arm"}
                for c in CLAIMS]
    differ = {lbl: sorted(k for k, v in same.items() if not v) for lbl, same in r["same"].items()}
    differ = {k: v for k, v in differ.items() if v}
    not_perm = {lbl: p for lbl, p in r["permutations"].items() if not p["permutation"]}
    thin = {lbl: roll["replicates"] for lbl, roll in r["rolls"].items() if roll["replicates"] < MIN_REPS}
    j1 = {"id": "BM1",
          "measured": f"{len(r['rolls'])} rolls at {r['spans']['replicates']} replicates, the orders "
                      f"{ {lbl: p['task_order'] for lbl, p in r['permutations'].items()} }, each a permutation "
                      f"{ {lbl: p['permutation'] for lbl, p in r['permutations'].items()} }",
          "verdict": f"MET -- the three rolls are carried over {len(next(iter(r['same'].values())))} shared fields with "
                     f"`task_order` alone differing" if
                     (len(r["rolls"]) >= MIN_ROLLS and not differ and not not_perm and not thin) else
                     f"FALSIFIER FIRED -- differing {differ}, non-permutation {not_perm}, thin {thin}"}
    margins = {lbl: round(v, 4) for lbl, v in r["spans"]["first_over_last"].items()}
    behind = {k: v for k, v in margins.items() if v <= POSITION}
    j2 = {"id": "BM2",
          "measured": f"the first-taught task over the last-taught one is {margins} across the three orders",
          "verdict": f"MET -- the position effect holds in all three rolls, the smallest margin "
                     f"{min(margins.values()):+.4f}" if not behind else f"FALSIFIER FIRED -- {behind}"}
    lasts = {lbl: round(v, 4) for lbl, v in r["spans"]["lasts"].items()}
    over = {k: v for k, v in lasts.items() if v > LAST_BAR}
    j3 = {"id": "BM3",
          "measured": f"the last-taught gains are {lasts} on the tasks "
                      f"{r['spans']['last_tasks']}",
          "verdict": f"MET -- the last position is cost in all three rolls, the worst {max(lasts.values()):+.4f}" if
                     not over else
                     f"FALSIFIER FIRED -- {over} is above the bar" if any(v > LAST_FIRES for v in over.values()) else
                     f"NULL -- {over} between {LAST_BAR:+.2f} and {LAST_FIRES:+.2f}"}
    span4 = r["spans"]["last_span"]
    j4 = {"id": "BM4",
          "measured": f"the three rolls' last-taught gains are {lasts}, spanning {span4:.4f}",
          "verdict": f"MET -- the last position's value spans {span4:.4f} across the three orders" if
                     span4 <= LAST_SPAN else
                     f"FALSIFIER FIRED -- the span is {span4:.4f}" if span4 > LAST_SPAN_FIRES else
                     f"NULL -- the span is {span4:.4f}, between {LAST_SPAN:.2f} and {LAST_SPAN_FIRES:.2f}"}
    span5 = r["spans"]["first_span"]
    firsts = {lbl: round(roll["gain"][0], 4) for lbl, roll in r["rolls"].items()}
    j5 = {"id": "BM5",
          "measured": f"the first-taught gains are {firsts} on the tasks "
                      f"{ {lbl: roll['tasks'][0] for lbl, roll in r['rolls'].items()} }, spanning {span5:.4f}",
          "verdict": f"MET -- the first position's value spans {span5:.4f} across the three orders" if
                     span5 <= FIRST_SPAN else
                     f"FALSIFIER FIRED -- the span is {span5:.4f}" if span5 > FIRST_SPAN_FIRES else
                     f"NULL -- the span is {span5:.4f}, between {FIRST_SPAN:.2f} and {FIRST_SPAN_FIRES:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== three orders on the benchmark's world ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source, under three of the suite's six orders")
    print(f"\n   {'roll':>9} {'order':>9} {'tasks in the order trained':>62} {'gain 0/1/2':>26} {'mean':>8}")
    for lbl, roll in r["rolls"].items():
        print(f"   {lbl:>9} {str(roll['task_order']):>9} {'>'.join(roll['tasks'])[:62]:>62} "
              + " ".join(f"{x:+.4f}" for x in roll["gain"]) + f" {roll['mean_gain']:+8.4f}")
    print("\n   each task's gain by the position it sat in:")
    for task, positions in r["by_task"].items():
        print(f"      {task:>22}: " + ", ".join(f"{lbl} p{p['position']} {p['gain']:+.4f}"
                                                for lbl, p in positions.items()))
    s = r["spans"]
    print(f"\n   the first position spans {s['first_span']:.4f}, the last {s['last_span']:.4f}, the means "
          f"{s['mean_span']:.4f}")
    print("\n== the registered claims, BM1-BM5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e436` drove the reversed order and found the position effect there while the reversal gained; this")
    print("    drives a third order, so every task sits in at least two positions)")
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
