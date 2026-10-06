"""E449 -- the ledger at a narrower world: whether the anchor's price, which `e448` found does not survive a widening, grows at the other end.

`e448` doubled the card's world's width and found the two arms separating: the buffer's ledger held at **+0.2500**,
**+0.2135** and **-0.0667** with its margins where they were, while the anchor's newest-task cost fell from **-0.1177**
at **3.71** sigma to **-0.0292** at **1.68** and its mean diagonal and forgetting purchase fell under two sigma with it.
That unit named its own first gap: *one width against the card's one, so a width of 16 is one point on an axis*. The
corpus has a direction for the other end of it -- `e292` found the share of the variance the read-out explains rising
from a median of **0.637** to **1.160** between the narrow and wide ends of the ladder and `e286` framed the width as
what the spread falls with -- so a world at **four** columns is where the anchor's effect should be **larger** if the
narrow end amplifies and smaller again if eight columns is its own peak.

**This unit narrows the world.** `e438`'s configuration with `--loop-world-dims 4` alone differing, at the same three
arms and twenty replicates, so the state the decoder reads is **four** numbers. Five claims, registered before the new
run's reading was opened.

- **CA1 -- and the run is one configuration with the world narrowed.** The three arms at **20** replicates, every
  recorded config field agreeing with `e438`'s except `loop_world_dims`, the output path and the saved weights, the three
  task names equal, and each task's own read-out **4** wide against the card's **8**. **Falsifier**: any other config
  field differing, an arm missing or short, a task name or a task count differing, or a task whose read-out is not the
  world's own width.
- **CA2 -- and the world is still learnable.** `naive`'s mean diagonal is at least **0.10** above the **0.25** chance.
  **Falsifier**: within **0.05** of chance; **null**: between. *A world too narrow to hold the task would make every
  claim below a statement about noise, so this is the unit's floor and it is registered before the others.*
- **CA3 -- and the buffer's ledger holds at the first position.** `replay` minus `naive` at the first position is at
  least **+0.05**. **Falsifier**: at or below **zero**; **null**: between. *The card reads **+0.2896**.*
- **CA4 -- and the anchor's price is larger at four columns than at eight.** `ewc-block` minus `naive` at the
  last-taught task is negative and at least **0.1177** in magnitude, that being the card's own cost. **Falsifier**:
  positive, or under **0.06** in magnitude; **null**: between. *This is the unit's question: `e448` found the price does
  not survive a widening, and this is the other end.*
- **CA5 -- and the anchor's whole-diagonal standing still does not resolve.** Its mean diagonal over the baseline is
  under **two** sigma. **Falsifier**: at or above two sigma.

**What it can do beyond that.** It turns `e448`'s single point into a trend over the widths the card has been played at:
if the price is largest at four columns, where the corpus says the read-out explains least, and gone at sixteen, then
the anchor's whole ledger is a function of how much of the task the world's own state carries -- which is `e286`'s axis
stated as a monotone rather than as an effect. If it is smaller at four than at eight as well, then eight columns is a
peak and the card's clause is a statement about that column count and not about the axis.

**What it cannot do.** *Three widths* -- four, eight and sixteen -- so a trend is three points and the monotonicity
`e292` failed to find across its ladder is not established here. *And a width is not a decoder*: narrowing the world
changes what the three tasks are as well as how many columns the decoder has. *And one cell*: the card's world at twenty
replicates, so the other five draws and the three streams are not in the reading. *And one run*: no second order, no
redraw and no matched-random arm at four columns, so whether the basis contrast survives a narrowing is not measured.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the card's world at half the width, and the card's own roll
RUNS = {
    "new": Path("runs/e449_earned_label_worlddims4_20reps.json"),
    "card": Path("runs/e438_earned_label_three_arms_20reps.json"),
}
ARMS = ("naive", "ewc-block", "replay")
BASELINE = "naive"
BUFFER = "replay"
ANCHOR = "ewc-block"
WIDTH_FIELD = "loop_world_dims"
SHARED = ("circuit", "tasks")
DRAW_FIELDS = ("cue_sha1", "action_sha1", "feedback_sha1", "world_read_sha1", "world_drive_sha1", "world_coupling_sha1")
#: the three the world's own drawing produces and the three it does not
WORLD_FIELDS = ("world_read_sha1", "world_drive_sha1", "world_coupling_sha1")
IGNORED = ("json_out", "save_theta", "methods", WIDTH_FIELD)
N_TASKS = 3
N_ARMS = 3
MIN_REPS = 20
BASE_WIDTH = 8
NARROW_WIDTH = 4
CHANCE = 0.25
LEARN_BAR = 0.10
LEARN_FLOOR = 0.05
FIRST_BAR = 0.05
FIRST_FLOOR = 0.0
#: the card's own newest-task cost, which CA4 is registered against
CARD_PRICE = 0.1177
PRICE_FLOOR = 0.06
SIGMA = 2.0
CLAIMS = (
    ("CA1", f"and the run is one configuration with the world narrowed, at {MIN_REPS} replicates",
     "The three arms at twenty replicates, every recorded config field agreeing with e438's except loop_world_dims, the "
     "output path and the saved weights, the three task names equal, and each task's own read-out 4 wide against the "
     "card's 8",
     "falsifier: any other config field differing, an arm missing or short, a task name or a task count differing, or a "
     "task whose read-out is not the world's own width"),
    ("CA2", f"and the world is still learnable, at least {LEARN_BAR:+.2f} above chance",
     f"naive's mean diagonal is at least 0.10 above the {CHANCE:.2f} chance",
     f"falsifier: within {LEARN_FLOOR:.2f} of chance; null: between"),
    ("CA3", f"and the buffer's ledger holds at the first position, at least {FIRST_BAR:+.2f}",
     "replay minus naive at the first position is at least +0.05",
     f"falsifier: at or below {FIRST_FLOOR:+.2f}; null: between"),
    ("CA4", f"and the anchor's price is larger at four columns than at eight, at least {CARD_PRICE:.4f}",
     "ewc-block minus naive at the last-taught task is negative and at least 0.1177 in magnitude",
     f"falsifier: positive, or under {PRICE_FLOOR:.2f} in magnitude; null: between"),
    ("CA5", f"and the anchor's whole-diagonal standing still does not resolve, under {SIGMA:.0f} sigma",
     "Its mean diagonal over the baseline is under two sigma",
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
    out["widths"] = {"new": {"width": new["width"], "readouts": new["readouts"],
                             "own": all(r == new["width"] for r in new["readouts"])},
                     "card": {"width": card["width"], "readouts": card["readouts"],
                              "own": all(r == card["width"] for r in card["readouts"])},
                     "world_moved": {k: (new["draws"].get(k) != card["draws"].get(k)) for k in WORLD_FIELDS},
                     "held": {k: (new["draws"].get(k) == card["draws"].get(k)) for k in DRAW_FIELDS
                              if k not in WORLD_FIELDS}}
    for label, roll in out["runs"].items():
        out["contrasts"][label] = {
            "buffer_gain": [roll["arms"][BUFFER]["final"][k] - roll["arms"][BASELINE]["final"][k]
                            for k in range(N_TASKS)],
            "anchor_gain": [roll["arms"][ANCHOR]["final"][k] - roll["arms"][BASELINE]["final"][k]
                            for k in range(N_TASKS)],
            "buffer_diagonal": _paired(roll["arms"][BUFFER]["diagonal"], roll["arms"][BASELINE]["diagonal"]),
            "anchor_last": _paired(roll["arms"][ANCHOR]["last"], roll["arms"][BASELINE]["last"]),
            "anchor_diagonal": _paired(roll["arms"][ANCHOR]["diagonal"], roll["arms"][BASELINE]["diagonal"]),
            "naive_diagonal": statistics.fmean(roll["arms"][BASELINE]["diagonal"]),
            "forgetting": {a: roll["arms"][a]["forgetting"] for a in roll["arms"]}}
    gain = out["contrasts"]["new"]["buffer_gain"]
    out["spans"] = {"replicates": sorted({v["replicates"] for roll in out["runs"].values()
                                         for v in roll["arms"].values()}),
                    "arms": {label: len(roll["arms"]) for label, roll in out["runs"].items()},
                    "same_fields": len(same),
                    "widths": {label: out["widths"][label]["width"] for label in ("new", "card")},
                    "naive_diagonal": {"new": out["contrasts"]["new"]["naive_diagonal"],
                                       "card": out["contrasts"]["card"]["naive_diagonal"],
                                       "over_chance": out["contrasts"]["new"]["naive_diagonal"] - CHANCE},
                    "margin": {"new": gain[0] - gain[-1], "card": out["contrasts"]["card"]["buffer_gain"][0]
                               - out["contrasts"]["card"]["buffer_gain"][-1]},
                    "last": {"buffer": gain[-1],
                             "anchor": out["contrasts"]["new"]["anchor_gain"][-1],
                             "anchor_sigma": out["contrasts"]["new"]["anchor_last"]["sigma"],
                             "card_anchor": out["contrasts"]["card"]["anchor_gain"][-1]}}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no arm"} for c in CLAIMS]
    differ = sorted(k for k, v in r["same"].items() if not v)
    thin = {f"{lbl}.{a}": v["replicates"] for lbl, roll in r["runs"].items() for a, v in roll["arms"].items()
            if v["replicates"] < MIN_REPS}
    short = {} if len(r["runs"]["new"]["arms"]) >= N_ARMS else {"new": sorted(r["runs"]["new"]["arms"])}
    w = r["widths"]
    j1 = {"id": "CA1",
          "measured": f"the new roll carries {len(r['runs']['new']['arms'])} arms at {r['spans']['replicates']} "
                      f"replicates over {r['spans']['same_fields']} compared fields, the widths "
                      f"{r['spans']['widths']}, each task's own read-out the world's {w['new']['own']} and "
                      f"{w['card']['own']}, the task names equal {r['same']['task_names']}",
          "verdict": f"MET -- one configuration with `{WIDTH_FIELD}` moved from {BASE_WIDTH} to {NARROW_WIDTH}, the "
                     f"three task names held, and every task's read-out the world's own width" if
                     (not short and not differ and not thin and w["new"]["own"] and w["card"]["own"] and
                      w["new"]["width"] == NARROW_WIDTH and w["card"]["width"] == BASE_WIDTH and
                      w["new"]["width"] != w["card"]["width"]) else
                     f"FALSIFIER FIRED -- differing {differ}, thin {thin}, short {short}, own widths "
                     f"{w['new']['own']} and {w['card']['own']}, the widths {w['new']['width']} and "
                     f"{w['card']['width']}"}
    over = r["spans"]["naive_diagonal"]["over_chance"]
    j2 = {"id": "CA2",
          "measured": f"the baseline's mean diagonal is {r['spans']['naive_diagonal']['new']:.4f}, "
                      f"{over:+.4f} over the {CHANCE:.2f} chance, against the card's "
                      f"{r['spans']['naive_diagonal']['card']:.4f}",
          "verdict": f"MET -- the narrower world is still learnable, the baseline {over:+.4f} over chance" if
                     over >= LEARN_BAR else
                     f"FALSIFIER FIRED -- the baseline is {over:+.4f} over chance" if over <= LEARN_FLOOR else
                     f"NULL -- the baseline is {over:+.4f} over chance, between {LEARN_FLOOR:.2f} and "
                     f"{LEARN_BAR:.2f}"}
    first = r["contrasts"]["new"]["buffer_gain"][0]
    j3 = {"id": "CA3",
          "measured": f"at the narrower world replay over naive at the first position is {first:+.4f}, against the "
                      f"card's {r['contrasts']['card']['buffer_gain'][0]:+.4f}",
          "verdict": f"MET -- the buffer's first-position gain holds at the narrower world, {first:+.4f}" if
                     first >= FIRST_BAR else
                     f"FALSIFIER FIRED -- {first:+.4f} at or below zero" if first <= FIRST_FLOOR else
                     f"NULL -- {first:+.4f} between {FIRST_FLOOR:+.2f} and {FIRST_BAR:+.2f}"}
    price, sigma = r["spans"]["last"]["anchor"], abs(r["spans"]["last"]["anchor_sigma"])
    amt = abs(price)
    j4 = {"id": "CA4",
          "measured": f"at the narrower world ewc-block over naive at the last position is {price:+.4f} at "
                      f"{sigma:.2f} sigma, against the card's {r['spans']['last']['card_anchor']:+.4f}, and the card's "
                      f"own magnitude is {CARD_PRICE:.4f}",
          "verdict": f"MET -- the price is larger at four columns than at eight, {amt:.4f} at {sigma:.2f} sigma" if
                     (price < 0 and amt >= CARD_PRICE) else
                     f"FALSIFIER FIRED -- {price:+.4f} of magnitude {amt:.4f}" if (price >= 0 or amt < PRICE_FLOOR)
                     else f"NULL -- the magnitude is {amt:.4f}, between {PRICE_FLOOR:.2f} and {CARD_PRICE:.4f}"}
    st = r["contrasts"]["new"]["anchor_diagonal"]
    j5 = {"id": "CA5",
          "measured": f"at the narrower world the anchor's mean diagonal over the baseline is {st['mean']:+.4f} at "
                      f"{abs(st['sigma']):.2f} sigma",
          "verdict": f"MET -- the anchor's whole-diagonal standing still does not resolve, {abs(st['sigma']):.2f} "
                     f"sigma" if abs(st["sigma"]) < SIGMA else
                     f"FALSIFIER FIRED -- the standing resolves here at {abs(st['sigma']):.2f} sigma"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the ledger at a narrower world ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source and the earned label, at eight columns and four,")
    print("   three arms and twenty replicates")
    print(f"\n   {'roll':>6} {'world dims':>11} {'each readout':>13} {'baseline diagonal':>18} {'tasks':>50}")
    for label, roll in r["runs"].items():
        print(f"   {label:>6} {str(roll['width']):>11} "
              f"{str(roll['readouts'][0] if roll['readouts'] else None):>13} "
              f"{r['contrasts'][label]['naive_diagonal']:18.4f} {'>'.join(roll['task_names'])[:50]:>50}")
    print("\n   the gain over naive, by position:")
    for label in ("card", "new"):
        for name in ("buffer_gain", "anchor_gain"):
            print(f"      {label + '.' + name:>22}: " + " ".join(f"{x:+.4f}" for x in r["contrasts"][label][name]))
    print("\n   mean forgetting, arm by arm:")
    for label in ("card", "new"):
        print(f"      {label:>6}: " +
              ", ".join(f"{a} {v:.4f}" for a, v in r["contrasts"][label]["forgetting"].items()))
    for label in ("card", "new"):
        p, q = r["contrasts"][label]["buffer_diagonal"], r["contrasts"][label]["anchor_last"]
        print(f"   {label:>6} the buffer's mean diagonal {p['mean']:+.4f} at {abs(p['sigma']):.2f} sigma; the anchor's "
              f"newest task {q['mean']:+.4f} at {abs(q['sigma']):.2f}")
    print(f"\n   the environment the width moved: the world's "
          f"{ {k: v for k, v in r['widths']['world_moved'].items()} }, the held "
          f"{ {k: v for k, v in r['widths']['held'].items()} }")
    print("\n== the registered claims, CA1-CA5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e448` doubled this world's width and found the anchor's price gone at sixteen; `e292` found the share")
    print("    the read-out explains rising toward the narrow end, so this is where the price should be larger)")
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
