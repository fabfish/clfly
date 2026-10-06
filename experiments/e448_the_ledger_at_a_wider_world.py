"""E448 -- the ledger at a wider world: whether the card's headline is the read-out width's.

`e286` named the **read-out width** as the real variable behind the corpus's numbers, `e292` found the share of the
variance the read-out explains rising from a median of **0.637** to **1.160** between the narrow and the wide end of the
corpus's ladder, and `e345` fitted four nested decoders to one roll and found no width seeing the loop's divergence. Every
reading this line has published about the card's world was taken at **one** width: `loop.world_dims` is **8** in the
card's own clause, `--readout-from-world` makes the read-out the world's own state, and the four rolls of revision 8, the
reversed one of `e446` and the matched-random one of `e447` are all **eight columns**. `e445`'s clause carries no width
and `e447` closed on *two of the three positions* rather than on this.

**This unit widens the world.** `e438`'s configuration with `--loop-world-dims 16` alone differing, at the same three
arms and twenty replicates, so the state the decoder reads is **sixteen** numbers instead of eight and every task's own
read-out is sixteen wide. Five claims, registered before the new run's reading was opened.

- **BZ1 -- and the run is one configuration with the world widened.** The three arms at **20** replicates, every recorded
  config field agreeing with `e438`'s except `loop_world_dims`, the output path and the saved weights, the three task
  names equal, and each task's own read-out **16** wide against the card's **8**. **Falsifier**: any other config field
  differing, an arm missing or short, a task name or a task count differing, or a task whose read-out is not the world's
  own width.
- **BZ2 -- and the buffer's ledger holds at the first position.** `replay` minus `naive` at the first position is at
  least **+0.05**. **Falsifier**: at or below **zero**; **null**: between. *The card reads **+0.2896**.*
- **BZ3 -- and the last position is cost at the wider world.** `replay` minus `naive` at the last position is at most
  **zero**. **Falsifier**: above **+0.05**; **null**: between. *The card reads **-0.0604**.*
- **BZ4 -- and the size of the position effect is the width's too.** The first-over-last margin is within **0.15** of the
  card's **+0.3500**. **Falsifier**: **0.25** or more apart; **null**: between.
- **BZ5 -- and the anchor pays there too.** `ewc-block` minus `naive` at the last-taught task is negative and resolves at
  **two** sigma or more. **Falsifier**: not negative, or under two sigma. *This is the one thing the card's eighth
  revision commits to about that arm, and it has been read at eight columns in five rolls.*

**What it can do beyond that.** It says whether the card's headline is a property of the game or of a game played at one
width. If the ledger holds and its size holds, the card's numbers can be quoted without naming a width and `e286`'s axis
is a statement about the corpus's other suites rather than about this world; if the ledger holds and its size moves, the
card should carry the width beside the number; and if the ledger does not hold, then the buffer's advantage is the
read-out's and `e286` is right about the card itself.

**What it cannot do.** *One width* against the card's one, so a width of **16** is one point on an axis and the ladder
that gave `e292` its medians is not here. *And one cell*: the card's world at twenty replicates, so the other five draws
and the three streams are not in the reading. *And a width is not a task*: widening the world's state changes what the
three tasks are as well as how many columns the decoder has, so this is a manipulation of the game and not of the
decoder alone -- which `--readout-size` would be, and which `--readout-from-world` makes inert. *And one run*: no second
order, no redraw, and `ewc-block-rand` absent.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the card's world at twice the width, and the card's own roll
RUNS = {
    "new": Path("runs/e448_earned_label_worlddims16_20reps.json"),
    "card": Path("runs/e438_earned_label_three_arms_20reps.json"),
}
ARMS = ("naive", "ewc-block", "replay")
BASELINE = "naive"
BUFFER = "replay"
ANCHOR = "ewc-block"
WIDTH_FIELD = "loop_world_dims"
SHARED = ("circuit", "tasks")
DRAW_FIELDS = ("cue_sha1", "action_sha1", "feedback_sha1", "world_read_sha1", "world_drive_sha1", "world_coupling_sha1")
IGNORED = ("json_out", "save_theta", "methods", WIDTH_FIELD)
N_TASKS = 3
N_ARMS = 3
MIN_REPS = 20
BASE_WIDTH = 8
WIDE_WIDTH = 16
FIRST_BAR = 0.05
FIRST_FLOOR = 0.0
LAST_BAR = 0.0
LAST_FIRES = 0.05
SIGMA = 2.0
#: the card's own first-over-last margin, which `e437` and `e436` read and BZ4 is registered against
CARD_MARGIN = 0.3500
MARGIN_MOVES = 0.15
MARGIN_FIRES = 0.25
CLAIMS = (
    ("BZ1", f"and the run is one configuration with the world widened, at {MIN_REPS} replicates",
     "The three arms at twenty replicates, every recorded config field agreeing with e438's except loop_world_dims, the "
     "output path and the saved weights, the three task names equal, and each task's own read-out 16 wide against the "
     "card's 8",
     "falsifier: any other config field differing, an arm missing or short, a task name or a task count differing, or a "
     "task whose read-out is not the world's own width"),
    ("BZ2", f"and the buffer's ledger holds at the first position, at least {FIRST_BAR:+.2f}",
     "replay minus naive at the first position is at least +0.05",
     f"falsifier: at or below {FIRST_FLOOR:+.2f}; null: between"),
    ("BZ3", "and the last position is cost at the wider world",
     "replay minus naive at the last position is at most zero",
     f"falsifier: above {LAST_FIRES:+.2f}; null: between"),
    ("BZ4", f"and the size of the position effect is the width's too, within {MARGIN_MOVES:.2f}",
     f"The first-over-last margin is within 0.15 of the card's {CARD_MARGIN:+.4f}",
     f"falsifier: {MARGIN_FIRES:.2f} or more apart; null: between"),
    ("BZ5", f"and the anchor pays there too, at {SIGMA:.0f} sigma",
     "ewc-block minus naive at the last-taught task is negative and resolves at two sigma or more",
     "falsifier: not negative, or under two sigma"),
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
    methods = doc.get("methods") or {}
    arms = {}
    for arm in ARMS:
        if arm not in methods:
            continue
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        arms[arm] = {"replicates": len(reps),
                     "final": [statistics.fmean([r["final_per_task"][k] for r in reps]) for k in range(N_TASKS)],
                     "diagonal": [statistics.fmean(r["final_per_task"]) for r in reps],
                     "last": [r["final_per_task"][-1] for r in reps],
                     "forgetting": statistics.fmean([r["mean_forgetting"] for r in reps])}
    ed = doc.get("env_draw") or {}
    cfg = doc.get("config") or {}
    tasks = doc.get("tasks") or []
    return {"artifact": path.name, "arms": arms,
            "task_names": [t.get("name") if isinstance(t, dict) else t for t in tasks],
            "readouts": [t.get("n_readout") if isinstance(t, dict) else None for t in tasks],
            "width": cfg.get(WIDTH_FIELD),
            "shared": {k: doc.get(k) for k in SHARED}, "draws": {k: ed.get(k) for k in DRAW_FIELDS},
            "config": {k: cfg.get(k) for k in sorted(set(cfg) - set(IGNORED))}}


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def reading(runs: dict = RUNS) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "widths": {}, "contrasts": {}, "spans": {}}
    for label, path in runs.items():
        got = _roll(path)
        if got is None:
            return {**out, "ok": False, "reason": f"roll {label}: {path} is absent or carries no arm"}
        out["runs"][label] = got
    new, card = out["runs"]["new"], out["runs"]["card"]
    missing = [a for a in ARMS if a not in new["arms"]]
    if missing:
        return {**out, "ok": False, "reason": f"the new roll carries no arm for {missing}"}
    same = {}
    fields = sorted(set(new["config"]) | set(card["config"]))
    for k in fields:
        same[f"config.{k}"] = new["config"].get(k) == card["config"].get(k)
    same["circuit"] = new["shared"].get("circuit") == card["shared"].get("circuit")
    same["task_names"] = new["task_names"] == card["task_names"]
    same["task_count"] = len(new["task_names"]) == len(card["task_names"])
    out["same"] = same
    #: each task's own read-out against its run's own width, which `--readout-from-world` makes the world's
    out["widths"] = {"new": {"width": new["width"], "readouts": new["readouts"],
                             "own": all(r == new["width"] for r in new["readouts"])},
                     "card": {"width": card["width"], "readouts": card["readouts"],
                              "own": all(r == card["width"] for r in card["readouts"])},
                     "drawn": {k: (new["draws"].get(k) != card["draws"].get(k)) for k in DRAW_FIELDS}}
    for label, roll in out["runs"].items():
        out["contrasts"][label] = {
            "buffer_gain": [roll["arms"][BUFFER]["final"][k] - roll["arms"][BASELINE]["final"][k]
                            for k in range(N_TASKS)],
            "anchor_gain": [roll["arms"][ANCHOR]["final"][k] - roll["arms"][BASELINE]["final"][k]
                            for k in range(N_TASKS)],
            "buffer_diagonal": _paired(roll["arms"][BUFFER]["diagonal"], roll["arms"][BASELINE]["diagonal"]),
            "anchor_last": _paired(roll["arms"][ANCHOR]["last"], roll["arms"][BASELINE]["last"]),
            "anchor_diagonal": _paired(roll["arms"][ANCHOR]["diagonal"], roll["arms"][BASELINE]["diagonal"]),
            "forgetting": {a: roll["arms"][a]["forgetting"] for a in roll["arms"]}}
    gain = out["contrasts"]["new"]["buffer_gain"]
    out["spans"] = {"replicates": sorted({v["replicates"] for roll in out["runs"].values()
                                         for v in roll["arms"].values()}),
                    "arms": {label: len(roll["arms"]) for label, roll in out["runs"].items()},
                    "same_fields": len(same),
                    "widths": {label: out["widths"][label]["width"] for label in ("new", "card")},
                    "margin": {"new": gain[0] - gain[-1], "card": CARD_MARGIN,
                               "move": gain[0] - gain[-1] - CARD_MARGIN},
                    "last": {"buffer": gain[-1], "anchor": out["contrasts"]["new"]["anchor_gain"][-1],
                             "anchor_sigma": out["contrasts"]["new"]["anchor_last"]["sigma"]},
                    "card_last": {"buffer": out["contrasts"]["card"]["buffer_gain"][-1],
                                  "anchor": out["contrasts"]["card"]["anchor_gain"][-1]}}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no arm"} for c in CLAIMS]
    differ = sorted(k for k, v in r["same"].items() if not v)
    thin = {f"{lbl}.{a}": v["replicates"] for lbl, roll in r["runs"].items() for a, v in roll["arms"].items()
            if v["replicates"] < MIN_REPS}
    short = {} if len(r["runs"]["new"]["arms"]) >= N_ARMS else {"new": sorted(r["runs"]["new"]["arms"])}
    w = r["widths"]
    j1 = {"id": "BZ1",
          "measured": f"the new roll carries {len(r['runs']['new']['arms'])} arms at {r['spans']['replicates']} "
                      f"replicates over {r['spans']['same_fields']} compared fields, the widths "
                      f"{r['spans']['widths']}, each task's own read-out the world's {w['new']['own']} and "
                      f"{w['card']['own']}, the task names equal {r['same']['task_names']}",
          "verdict": f"MET -- one configuration with `{WIDTH_FIELD}` moved from {BASE_WIDTH} to {WIDE_WIDTH}, the three "
                     f"task names held, and every task's read-out the world's own width" if
                     (not short and not differ and not thin and w["new"]["own"] and w["card"]["own"] and
                      w["new"]["width"] == WIDE_WIDTH and w["card"]["width"] == BASE_WIDTH and
                      w["new"]["width"] != w["card"]["width"]) else
                     f"FALSIFIER FIRED -- differing {differ}, thin {thin}, short {short}, own widths "
                     f"{w['new']['own']} and {w['card']['own']}, the widths {w['new']['width']} and "
                     f"{w['card']['width']}"}
    first = r["contrasts"]["new"]["buffer_gain"][0]
    j2 = {"id": "BZ2",
          "measured": f"at the wider world replay over naive at the first position is {first:+.4f}, against the card's "
                      f"{r['contrasts']['card']['buffer_gain'][0]:+.4f}",
          "verdict": f"MET -- the buffer's first-position gain holds at the wider world, {first:+.4f}" if
                     first >= FIRST_BAR else
                     f"FALSIFIER FIRED -- {first:+.4f} at or below zero" if first <= FIRST_FLOOR else
                     f"NULL -- {first:+.4f} between {FIRST_FLOOR:+.2f} and {FIRST_BAR:+.2f}"}
    last = r["spans"]["last"]["buffer"]
    j3 = {"id": "BZ3",
          "measured": f"at the wider world replay over naive at the last position is {last:+.4f}, against the card's "
                      f"{r['spans']['card_last']['buffer']:+.4f}",
          "verdict": f"MET -- the last position is cost at the wider world, {last:+.4f}" if last <= LAST_BAR else
                     f"FALSIFIER FIRED -- {last:+.4f} is above the bar" if last > LAST_FIRES else
                     f"NULL -- {last:+.4f} between {LAST_BAR:+.2f} and {LAST_FIRES:+.2f}"}
    margin = r["spans"]["margin"]["new"]
    move = abs(r["spans"]["margin"]["move"])
    j4 = {"id": "BZ4",
          "measured": f"the wider world's first-over-last margin is {margin:+.4f} against the card's "
                      f"{CARD_MARGIN:+.4f}, {move:.4f} apart",
          "verdict": f"MET -- the size of the position effect is the width's too, {move:.4f} apart" if move <= MARGIN_MOVES
                     else f"FALSIFIER FIRED -- the move is {move:.4f}" if move >= MARGIN_FIRES else
                     f"NULL -- the move is {move:.4f}, between {MARGIN_MOVES:.2f} and {MARGIN_FIRES:.2f}"}
    anchor_last = r["spans"]["last"]["anchor"]
    a_sigma = abs(r["spans"]["last"]["anchor_sigma"])
    j5 = {"id": "BZ5",
          "measured": f"at the wider world ewc-block over naive at the last position is {anchor_last:+.4f} at "
                      f"{a_sigma:.2f} sigma, against the card's {r['spans']['card_last']['anchor']:+.4f}",
          "verdict": f"MET -- the anchor pays the newest task at the wider world too, {anchor_last:+.4f} at "
                     f"{a_sigma:.2f} sigma" if (anchor_last < 0 and a_sigma >= SIGMA) else
                     f"FALSIFIER FIRED -- {anchor_last:+.4f} at {a_sigma:.2f} sigma"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the ledger at a wider world ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source and the earned label, at eight columns and sixteen,")
    print("   three arms and twenty replicates")
    print(f"\n   {'roll':>6} {'world dims':>11} {'readout width':>14} {'tasks':>52}")
    for label, roll in r["runs"].items():
        print(f"   {label:>6} {str(roll['width']):>11} {str(roll['readouts'][0] if roll['readouts'] else None):>14} "
              f"{'>'.join(roll['task_names'])[:52]:>52}")
    print("\n   the gain over naive, by position:")
    for label in ("card", "new"):
        for name in ("buffer_gain", "anchor_gain"):
            print(f"      {label + '.' + name:>22}: " + " ".join(f"{x:+.4f}" for x in r["contrasts"][label][name]))
    print("\n   mean forgetting, arm by arm:")
    for label, got in ((l, r["contrasts"][l]["forgetting"]) for l in ("card", "new")):
        print(f"      {label:>6}: " + ", ".join(f"{a} {v:.4f}" for a, v in got.items()))
    for label in ("card", "new"):
        p = r["contrasts"][label]["buffer_diagonal"]
        q = r["contrasts"][label]["anchor_last"]
        print(f"   {label:>6} the buffer's mean diagonal {p['mean']:+.4f} at {abs(p['sigma']):.2f} sigma; the anchor's "
              f"newest task {q['mean']:+.4f} at {abs(q['sigma']):.2f}")
    m = r["spans"]["margin"]
    print(f"\n   the first-over-last margin: card {m['card']:+.4f}, new {m['new']:+.4f}, {m['move']:+.4f} apart")
    print(f"   the environments drawn by the width: " +
          ", ".join(f"{k} {v}" for k, v in r["widths"]["drawn"].items()))
    print("\n== the registered claims, BZ1-BZ5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e286` named the read-out width as the real variable behind the corpus's numbers and `e292` found the")
    print("    share it explains rising across the ladder; every reading of this world has been at eight columns)")
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
