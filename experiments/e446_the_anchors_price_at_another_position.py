"""E446 -- the anchor's price at another position: whether the one resolved effect the card carries is the position's or the task's.

Revision 8 of the card carries the anchor's **newest-task price** as the one thing about that arm that resolves on every
roll this line has driven: `-0.1177`, `-0.0906`, `-0.0552` and `-0.0615` at **3.71**, **3.56**, **2.57** and **2.62**
sigma, while its whole-diagonal standing resolves on none of the four. **In every one of those rolls the last position
held `loop_odour_input`** -- the as-built order and the two redraws end with it, and `e441`'s rotated order
(`loop_heading`, `loop_odour_identity`, `loop_odour_input`) ends with it too -- so the price the card carries has only
ever been measured on one task, and `e445` named exactly that as what its own clause could not settle.

**This unit drives the order in which the last position holds another task.** `e438`'s configuration with
`--task-order reverse` alone differing, at the same three arms and twenty replicates, so the suite is trained
`loop_odour_input`, `loop_heading`, `loop_odour_identity` and the anchor's price is asked at a position whose task is
`loop_odour_identity`. `e436` drove this order with `naive` and `replay` alone, so the two arms this run shares can be
checked against it record for record. Five claims, registered before the new run's reading was opened.

- **BX1 -- and the run is one configuration with the order reversed.** The three arms at **20** replicates, every
  recorded field agreeing with `e438`'s except `task_order`, the output path and the saved weights, the new suite the
  as-built suite **reversed**, and the new run's `naive` and `replay` replicates **bit-identical** to `e436`'s roll,
  which shares this run's order. **Falsifier**: any other field differing, an arm missing or short, a suite that is not
  the reversal, or any shared replicate's record differing.
- **BX2 -- and the anchor pays the newest task here too.** `ewc-block` minus `naive` on the last-taught task is at most
  **zero**. **Falsifier**: above **+0.05**; **null**: between.
- **BX3 -- and that price resolves.** The same contrast is negative at **two** sigma or more. **Falsifier**: under two
  sigma.
- **BX4 -- and the price is the position's and not the task's.** The new roll's newest-task cost is within **0.05** of
  the as-built one's. **Falsifier**: **0.10** or more apart; **null**: between. *This is the claim with the unit's
  question in it: the last position holds `loop_odour_input` in every roll the card carries and holds
  `loop_odour_identity` here, so this is the measurement the card's clause has been missing.*
- **BX5 -- and the anchor's whole-diagonal standing is still not there.** Its mean diagonal over the baseline does not
  reach two sigma. **Falsifier**: at or above two sigma.

**What it can do beyond that.** If the price is where it was, then the card's one clause about the anchor is a statement
about the position and a reader may carry it without naming a task; if the price moves with the task, then the clause is
about `loop_odour_input` and the card should say so. Either way the card's clause stops resting on a single task's
having held the last position in all four of its rolls.

**What it cannot do.** *One more order* of the suite's six, so `loop_odour_identity` is the only other task the price is
asked of and four positions are still unread. *And one cell*: the card's world at twenty replicates, so the other five
draws and the three streams are not in the reading. *And one anchor*: `ewc-block-rand` is absent, though `e439` found
the two anchors **0.0042** apart at the last position as-built. *And a price is not a purchase*: this measures what the
anchor gives up at the newest task and not what it buys with it, which `e440`'s forgetting contrast is where the corpus
looks for it.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the anchor under the reverse order, the roll it is read against, and the buffer's own reverse roll as the control
RUNS = {
    "new": Path("runs/e446_earned_label_anchor_reverse_20reps.json"),
    "asbuilt": Path("runs/e438_earned_label_three_arms_20reps.json"),
    "control": Path("runs/e436_earned_label_cue0_reverse_20reps.json"),
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
SIGMA = 2.0
MOVES = 0.05
MOVES_FIRES = 0.10
#: the as-built roll's newest-task cost, which `e438` read and BX4 is registered against
AS_BUILT_LAST = -0.1177
CLAIMS = (
    ("BX1", f"and the run is one configuration with the order reversed, at {MIN_REPS} replicates",
     "The three arms at twenty replicates, every recorded field agreeing with e438's except task_order, the output path "
     "and the saved weights, the new suite the as-built suite reversed, and the new run's naive and replay "
     "bit-identical to e436's roll",
     "falsifier: any other field differing, an arm missing or short, a suite that is not the reversal, or any shared "
     "replicate's record differing"),
    ("BX2", "and the anchor pays the newest task here too",
     "ewc-block minus naive on the last-taught task is at most zero",
     f"falsifier: above {LAST_FIRES:+.2f}; null: between"),
    ("BX3", f"and that price resolves, at {SIGMA:.0f} sigma",
     "The same contrast is negative at two sigma or more",
     "falsifier: under two sigma"),
    ("BX4", f"and the price is the position's and not the task's, within {MOVES:.2f}",
     f"The new roll's newest-task cost is within 0.05 of the as-built one's",
     f"falsifier: {MOVES_FIRES:.2f} or more apart; null: between"),
    ("BX5", f"and the anchor's whole-diagonal standing is still not there, under {SIGMA:.0f} sigma",
     "Its mean diagonal over the baseline does not reach two sigma",
     "falsifier: at or above two sigma"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _arm(got: dict) -> dict | None:
    reps = (got or {}).get("replicates") or []
    if not reps:
        return None
    return {"replicates": len(reps),
            "final": [statistics.fmean([r["final_per_task"][k] for r in reps]) for k in range(N_TASKS)],
            "diagonal": [statistics.fmean(r["final_per_task"]) for r in reps],
            "last": [r["final_per_task"][-1] for r in reps],
            "records": [{"final_per_task": list(r["final_per_task"]),
                         "mean_forgetting": r["mean_forgetting"]} for r in reps]}


def _roll(path: Path) -> dict | None:
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    arms = {}
    for arm in ARMS:
        if arm not in methods:
            continue
        got = _arm(methods[arm])
        if got is None:
            return None
        arms[arm] = got
    ed = doc.get("env_draw") or {}
    cfg = doc.get("config") or {}
    return {"artifact": path.name,
            "tasks": [t.get("name") if isinstance(t, dict) else t for t in (doc.get("tasks") or [])],
            "arms": arms, "task_order": cfg.get(ORDER), "shared": {k: doc.get(k) for k in SHARED},
            "draws": {k: ed.get(k) for k in DRAW_FIELDS},
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


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def reading(runs: dict = RUNS) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "identical": {}, "reversed": {}, "contrasts": {},
           "spans": {}}
    for label, path in runs.items():
        got = _roll(path)
        if got is None:
            return {**out, "ok": False, "reason": f"roll {label}: {path} is absent or carries no arm"}
        out["runs"][label] = got
    new, asbuilt, control = out["runs"]["new"], out["runs"]["asbuilt"], out["runs"]["control"]
    missing = [a for a in ARMS if a not in new["arms"]]
    if missing:
        return {**out, "ok": False, "reason": f"the new roll carries no arm for {missing}"}
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
    out["reversed"] = {"new": new["tasks"], "asbuilt": asbuilt["tasks"],
                       "is_the_reversal": list(reversed(asbuilt["tasks"])) == list(new["tasks"]),
                       "orders": {label: roll["task_order"] for label, roll in out["runs"].items()}}
    #: the two arms this run shares with `e436`'s reverse roll, checked record for record
    for arm in SHARED_ARMS:
        if arm not in control["arms"]:
            out["identical"][f"new/control:{arm}"] = {"equal": False, "n": 0, "first_differing": None, "fields": []}
            continue
        out["identical"][f"new/control:{arm}"] = _identical(new["arms"][arm]["records"],
                                                            control["arms"][arm]["records"])
    for label, roll in out["runs"].items():
        if ANCHOR not in roll["arms"] or BASELINE not in roll["arms"]:
            continue
        out["contrasts"][label] = {
            "anchor_diagonal": _paired(roll["arms"][ANCHOR]["diagonal"], roll["arms"][BASELINE]["diagonal"]),
            "anchor_last": _paired(roll["arms"][ANCHOR]["last"], roll["arms"][BASELINE]["last"]),
            "anchor_gain": [roll["arms"][ANCHOR]["final"][k] - roll["arms"][BASELINE]["final"][k]
                            for k in range(N_TASKS)]}
        if BUFFER in roll["arms"]:
            out["contrasts"][label]["buffer_gain"] = [roll["arms"][BUFFER]["final"][k] - roll["arms"][BASELINE]["final"][k]
                                                      for k in range(N_TASKS)]
    last_new = out["contrasts"]["new"]["anchor_last"]["mean"]
    last_base = out["contrasts"]["asbuilt"]["anchor_last"]["mean"]
    out["spans"] = {"replicates": sorted({v["replicates"] for roll in out["runs"].values()
                                         for v in roll["arms"].values()}),
                    "arms": {label: len(roll["arms"]) for label, roll in out["runs"].items()},
                    "same_fields": len(same), "orders": out["reversed"]["orders"],
                    "last": {"new": last_new, "asbuilt": last_base, "move": last_new - last_base,
                             "new_sigma": out["contrasts"]["new"]["anchor_last"]["sigma"],
                             "last_tasks": {"new": new["tasks"][-1], "asbuilt": asbuilt["tasks"][-1]}},
                    "standing": {"new": out["contrasts"]["new"]["anchor_diagonal"]["mean"],
                                 "new_sigma": out["contrasts"]["new"]["anchor_diagonal"]["sigma"],
                                 "asbuilt": out["contrasts"]["asbuilt"]["anchor_diagonal"]["mean"],
                                 "asbuilt_sigma": out["contrasts"]["asbuilt"]["anchor_diagonal"]["sigma"]}}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no arm"} for c in CLAIMS]
    differ = sorted(k for k, v in r["same"].items() if not v)
    not_identical = sorted(k for k, v in r["identical"].items() if not v["equal"])
    thin = {f"{lbl}.{a}": v["replicates"] for lbl, roll in r["runs"].items() for a, v in roll["arms"].items()
            if v["replicates"] < MIN_REPS}
    short = {} if len(r["runs"]["new"]["arms"]) >= N_ARMS else {"new": sorted(r["runs"]["new"]["arms"])}
    reversed_ok = r["reversed"]["is_the_reversal"]
    j1 = {"id": "BX1",
          "measured": f"the new roll carries {len(r['runs']['new']['arms'])} arms at {r['spans']['replicates']} "
                      f"replicates over {r['spans']['same_fields']} compared fields, the orders {r['spans']['orders']}, "
                      f"the suite the as-built one reversed {reversed_ok}, the shared arms bit-identical "
                      f"{len(r['identical']) - len(not_identical)} of {len(r['identical'])}",
          "verdict": "MET -- one configuration with the order reversed, the suite the as-built one reversed, and the "
                     "two shared arms reproducing e436's roll at the same order" if
                     (not short and not differ and not not_identical and reversed_ok and not thin) else
                     f"FALSIFIER FIRED -- differing {differ}, not bit-identical {not_identical}, reversal "
                     f"{reversed_ok}, thin {thin}, short {short}"}
    last = r["spans"]["last"]["new"]
    j2 = {"id": "BX2",
          "measured": f"on the new roll's last-taught task `{r['spans']['last']['last_tasks']['new']}` ewc-block over "
                      f"naive is {last:+.4f}, against the as-built roll's {r['spans']['last']['asbuilt']:+.4f} on "
                      f"`{r['spans']['last']['last_tasks']['asbuilt']}`",
          "verdict": f"MET -- the anchor pays the newest task here too, {last:+.4f}" if last <= LAST_BAR else
                     f"FALSIFIER FIRED -- {last:+.4f} is above the bar" if last > LAST_FIRES else
                     f"NULL -- {last:+.4f} between {LAST_BAR:+.2f} and {LAST_FIRES:+.2f}"}
    sigma = abs(r["spans"]["last"]["new_sigma"])
    j3 = {"id": "BX3",
          "measured": f"that contrast is {last:+.4f} at {sigma:.2f} sigma over "
                      f"{r['contrasts']['new']['anchor_last']['n']} paired replicates",
          "verdict": f"MET -- the anchor's newest-task price resolves at {sigma:.2f} sigma" if
                     (last < 0 and sigma >= SIGMA) else
                     f"FALSIFIER FIRED -- the price does not resolve here at {sigma:.2f} sigma"}
    move = abs(r["spans"]["last"]["move"])
    j4 = {"id": "BX4",
          "measured": f"the newest-task cost is {last:+.4f} with `{r['spans']['last']['last_tasks']['new']}` last and "
                      f"{r['spans']['last']['asbuilt']:+.4f} with "
                      f"`{r['spans']['last']['last_tasks']['asbuilt']}` last, {move:.4f} apart",
          "verdict": f"MET -- the price is the position's and not the task's, {move:.4f} apart" if move <= MOVES else
                     f"FALSIFIER FIRED -- the move is {move:.4f}" if move >= MOVES_FIRES else
                     f"NULL -- the move is {move:.4f}, between {MOVES:.2f} and {MOVES_FIRES:.2f}"}
    st = r["spans"]["standing"]
    j5 = {"id": "BX5",
          "measured": f"on the new roll the anchor's mean diagonal over the baseline is {st['new']:+.4f} at "
                      f"{abs(st['new_sigma']):.2f} sigma, against the as-built roll's {st['asbuilt']:+.4f} at "
                      f"{abs(st['asbuilt_sigma']):.2f}",
          "verdict": f"MET -- the anchor's whole-diagonal standing is still not there, {abs(st['new_sigma']):.2f} "
                     f"sigma" if abs(st["new_sigma"]) < SIGMA else
                     f"FALSIFIER FIRED -- the standing resolves here at {abs(st['new_sigma']):.2f} sigma"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the anchor's price at another position ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source and the earned label, as-built and reversed, twenty")
    print("   replicates; the last position holds `loop_odour_input` in the as-built roll and `loop_odour_identity` here")
    print(f"\n   {'roll':>9} {'order':>9} {'tasks in the order trained':>62}")
    for label, roll in r["runs"].items():
        print(f"   {label:>9} {str(roll['task_order']):>9} {'>'.join(roll['tasks'])[:62]:>62}")
    print("\n   the gain over naive, by position:")
    for label in ("asbuilt", "new"):
        for name in ("anchor_gain", "buffer_gain"):
            key = f"{label}.{name}"
            vals = r["contrasts"].get(label, {}).get(name)
            if vals:
                print(f"      {key:>18}: " + " ".join(f"{x:+.4f}" for x in vals))
    for label, got in r["contrasts"].items():
        p, q = got["anchor_last"], got["anchor_diagonal"]
        print(f"\n   {label:>9} the anchor's newest task {p['mean']:+.4f} at {abs(p['sigma']):.2f} sigma, its whole "
              f"diagonal {q['mean']:+.4f} at {abs(q['sigma']):.2f}")
    print(f"   the shared arms against e436's reverse roll: " +
          ", ".join(f"{k} {v['equal']}" for k, v in r["identical"].items()))
    print("\n== the registered claims, BX1-BX5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (every roll the card's eighth revision carries puts `loop_odour_input` last; this is the first with")
    print("    another task there, which is what the clause that names the anchor's price could not settle)")
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
