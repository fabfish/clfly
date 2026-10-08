"""E468 -- the budget curve at thirty-two columns: whether the width moves the crossing.

`e467` walked the budget axis at **eight columns** and put the biological anchor's change of sign **between 350 and 500
updates** -- its standing running **-0.0483**, **-0.0378**, **-0.0243** then **+0.0017** -- and closed on *one width:
nothing here says a curve at sixteen or thirty-two crosses in the same place*. **The far point already carries the other
end of that rung**: at thirty-two columns `e466` read **-0.0243** at a hundred updates and `e455` reads **+0.0187** at
five hundred, so the sign changes there too and only the place is unmeasured.

**This unit measures it.** Four more rolls of the same configuration at **thirty-two columns** -- both anchors, twenty
replicates each -- at **200** and **350** updates, read beside `e466`'s **100** and `e455`'s and `e456`'s **500**, so the
two rungs carry the same four-point sequence and the crossing can be compared across the width. Four claims, registered
before any new roll's reading was opened.

- **UA1 -- and the new rolls are one configuration with the budget moved.** Three arms each at **20** replicates, every
  recorded config field agreeing with the hundred-update roll of the same side except `iters` and the output path, the
  read-out **32** and the circuit's own, and the task names equal. **Falsifier**: any other field differing, an arm
  missing or short, or a read-out that is the world's or another width.
- **UA2 -- and the biological anchor's standing changes sign once at thirty-two columns too.** Its sign at a hundred
  updates is negative and at five hundred is positive, and the four-point sequence carries **at most one** change.
  **Falsifier**: two changes in the sequence.
- **UA3 -- and the width does not move the crossing.** The thirty-two column sign sequence is **the same** as the
  eight-column one at every budget, so the change of sign sits between the same two budgets on both rungs.
  **Falsifier**: the two sequences differing at any budget. *The claim is the null: a narrower head and a fourfold wider
  one cross in the same place, which is what a mechanism behind the width would predict.*
- **UA4 -- and the pair's prices are alike at thirty-two columns at every budget.** The two anchors' newest-task costs
  differ by at most **0.05** at each of the four budgets. **Falsifier**: **0.10** or more at any budget; **null**:
  between.

**What it can do beyond that.** It turns `e467`'s crossing from a place on one rung into a place on two, so *the far
point's null is the end of a decay* is a statement about the head and not about eight columns, and the two rungs'
price gaps are read at four budgets each.

**What it cannot do.** *Two rungs are not the ladder*: **8** and **32** are fourfold apart and **16**, **24** and
everything between are not measured, so *the width does not move the crossing* is two points of a curve and not a
constant. *And four budgets are still not a mechanism*: the corpus carries no run that separates the update count from
the training it buys. *And one cell each*: twenty replicates, so a crossing's neighbours are what a redraw could move.
*And one partition draw*: the matched-random cells are one draw of the same group sizes.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the four budgets at thirty-two columns, both anchors, by budget and side
RUNS = {
    "100/bio": Path("runs/e466_earned_label_neurons32_iters100_20reps.json"),
    "100/rand": Path("runs/e466_earned_label_rand_neurons32_iters100_20reps.json"),
    "200/bio": Path("runs/e468_earned_label_neurons32_iters200_20reps.json"),
    "200/rand": Path("runs/e468_earned_label_rand_neurons32_iters200_20reps.json"),
    "350/bio": Path("runs/e468_earned_label_neurons32_iters350_20reps.json"),
    "350/rand": Path("runs/e468_earned_label_rand_neurons32_iters350_20reps.json"),
    "500/bio": Path("runs/e455_earned_label_neurons_20reps.json"),
    "500/rand": Path("runs/e456_earned_label_rand_neurons_20reps.json"),
}
#: the eight-column curve this one is compared against, which `e467` drove rather than quoted here
NARROW = Path("runs/e467_the_budget_curve_at_eight_columns.json")
BUDGETS = (100, 200, 350, 500)
#: the budgets as the artifact's own keys carry them: `json` stringifies an integer key
BK = tuple(str(b) for b in BUDGETS)
NEW = ("200", "350")
WIDTH = 32
NARROW_WIDTH = 8
ANCHOR_OF = {"bio": "ewc-block", "rand": "ewc-block-rand"}
BASELINE = "naive"
BIO = "ewc-block"
RAND = "ewc-block-rand"
BUFFER = "replay"
SHARED = ("circuit", "tasks")
IGNORED = ("json_out", "iters")
N_TASKS = 3
N_ARMS = 3
MIN_REPS = 20
SIGMA = 2.0
ALIKE = 0.05
ALIKE_FIRES = 0.10
CLAIMS = (
    ("UA1", f"and the new rolls are one configuration with the budget moved, at {MIN_REPS} replicates",
     "Three arms each at twenty replicates, every recorded config field agreeing with the hundred-update roll of the "
     "same side except iters and the output path, the read-out 32 and the circuit's own, and the task names equal",
     "falsifier: any other field differing, an arm missing or short, or a read-out that is the world's or another "
     "width"),
    ("UA2", "and the biological anchor's standing changes sign once at thirty-two columns too",
     "Its sign at a hundred updates is negative and at five hundred is positive, and the four-point sequence carries at "
     "most one change",
     "falsifier: two changes in the sequence"),
    ("UA3", "and the width does not move the crossing",
     "The thirty-two column sign sequence is the same as the eight-column one at every budget",
     "falsifier: the two sequences differing at any budget"),
    ("UA4", f"and the pair's prices are alike at thirty-two columns at every budget, within {ALIKE:.2f}",
     "The two anchors' newest-task costs differ by at most 0.05 at each of the four budgets",
     f"falsifier: {ALIKE_FIRES:.2f} or more at any budget; null: between"),
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
            "diagonal": [statistics.fmean(r["final_per_task"]) for r in reps],
            "last": [r["final_per_task"][-1] for r in reps]}


def _roll(path: Path, anchor: str) -> dict | None:
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    arms = {}
    for arm in (BASELINE, anchor, BUFFER):
        if arm not in methods:
            return None
        got = _arm(methods[arm])
        if got is None:
            return None
        arms[arm] = got
    return {"artifact": path.name, "anchor": anchor, "arms": arms,
            "readouts": [t.get("n_readout") if isinstance(t, dict) else None for t in (doc.get("tasks") or [])],
            "from_world": (doc.get("config") or {}).get("readout_from_world"),
            "shared": {k: doc.get(k) for k in SHARED},
            "config": {k: (doc.get("config") or {}).get(k)
                       for k in sorted(set(doc.get("config") or {}) - set(IGNORED))}}


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def _sign(mean: float) -> int:
    return 1 if mean > 0 else -1


def _changes(signs: list) -> int:
    return sum(1 for i in range(len(signs) - 1) if signs[i] != signs[i + 1])


def reading(runs: dict = RUNS, narrow: Path = NARROW) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "readouts": {}, "curve": {}, "gaps": {},
           "narrow": {}, "spans": {}}
    for label, path in runs.items():
        got = _roll(path, ANCHOR_OF[label.split("/")[1]])
        if got is None:
            return {**out, "ok": False,
                    "reason": f"roll {label}: {path} is absent or carries no {ANCHOR_OF[label.split('/')[1]]} arm"}
        out["runs"][label] = got
    doc = load(narrow)
    if doc is None:
        return {**out, "ok": False, "reason": f"{narrow} is not there, so there is no eight-column curve to compare"}
    out["narrow"] = {"budgets": (doc.get("spans") or {}).get("budget"),
                     "sign": ((doc.get("spans") or {}).get("sign") or {}).get("bio"),
                     "standing": {str(b): doc["curve"][str(b)]["bio"]["standing"] for b in BUDGETS
                                  if str(b) in (doc.get("curve") or {})}}
    if len(out["narrow"]["sign"] or []) != len(BUDGETS):
        return {**out, "ok": False, "reason": f"{narrow} carries no four-point sign sequence for the biological anchor"}
    base = {side: out["runs"][f"{BUDGETS[0]}/{side}"] for side in ("bio", "rand")}
    for side in ("bio", "rand"):
        for b in NEW:
            roll = out["runs"][f"{b}/{side}"]
            fields = sorted(set(roll["config"]) | set(base[side]["config"]))
            for k in fields:
                out["same"][f"{side}.{k}"] = out["same"].get(f"{side}.{k}", True) and \
                    roll["config"].get(k) == base[side]["config"].get(k)
            out["same"][f"{side}.circuit"] = out["same"].get(f"{side}.circuit", True) and \
                roll["shared"].get("circuit") == base[side]["shared"].get("circuit")
            out["same"][f"{side}.tasks"] = out["same"].get(f"{side}.tasks", True) and \
                roll["shared"].get("tasks") == base[side]["shared"].get("tasks")
    out["readouts"] = {label: {"readouts": roll["readouts"], "from_world": roll["from_world"]}
                       for label, roll in out["runs"].items()}
    for b in BK:
        out["curve"][b] = {}
        for side in ("bio", "rand"):
            roll = out["runs"][f"{b}/{side}"]
            over = _paired(roll["arms"][roll["anchor"]]["diagonal"], roll["arms"][BASELINE]["diagonal"])
            last = _paired(roll["arms"][roll["anchor"]]["last"], roll["arms"][BASELINE]["last"])
            buf = _paired(roll["arms"][BUFFER]["diagonal"], roll["arms"][roll["anchor"]]["diagonal"])
            out["curve"][b][side] = {
                "budget": int(b), "side": side, "anchor": roll["anchor"], "width": WIDTH,
                "standing": over["mean"], "standing_sigma": abs(over["sigma"]),
                "price": last["mean"], "price_sigma": abs(last["sigma"]),
                "buffer_over_anchor": buf["mean"], "buffer_over_anchor_sigma": abs(buf["sigma"])}
    out["gaps"] = {b: {"price": abs(out["curve"][b]["bio"]["price"] - out["curve"][b]["rand"]["price"]),
                       "standing": abs(out["curve"][b]["bio"]["standing"] - out["curve"][b]["rand"]["standing"])}
                   for b in BK}
    thin = {label: v["replicates"] for label, roll in out["runs"].items() for k, v in roll["arms"].items()
            if v["replicates"] < MIN_REPS}
    short = {label: sorted(roll["arms"]) for label, roll in out["runs"].items() if len(roll["arms"]) < N_ARMS}
    signs = [_sign(out["curve"][str(b)]["bio"]["standing"]) for b in BUDGETS]
    out["spans"] = {
        "width": WIDTH, "narrow_width": NARROW_WIDTH, "budgets": list(BUDGETS), "runs": len(out["runs"]),
        "same_fields": len(out["same"]),
        "replicates": sorted({v["replicates"] for roll in out["runs"].values() for v in roll["arms"].values()}),
        "thin": thin, "short": short,
        "readout": {label: (roll["readouts"] or [None])[0] for label, roll in out["runs"].items()},
        "from_world": {label: roll["from_world"] for label, roll in out["runs"].items()},
        "sign": signs, "sign_changes": _changes(signs),
        "narrow_sign": out["narrow"]["sign"], "narrow_changes": _changes(out["narrow"]["sign"]),
        "standing": {str(b): out["curve"][str(b)]["bio"]["standing"] for b in BUDGETS},
        "standing_sigma": {str(b): out["curve"][str(b)]["bio"]["standing_sigma"] for b in BUDGETS},
        "narrow_standing": out["narrow"]["standing"],
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll or the narrow curve is not there"}
                for c in CLAIMS]
    s = r["spans"]
    differ = sorted(k for k, v in r["same"].items() if not v)
    reads_ok = all(s["readout"][f"{b}/{side}"] == WIDTH for b in NEW for side in ("bio", "rand")) and \
        all(v is False for v in s["from_world"].values())
    j1 = {"id": "UA1",
          "measured": f"the four new rolls carry {len(NEW) * 2} cells at {s['replicates']} replicates over "
                      f"{s['same_fields']} compared fields, the read-out "
                      f"{ {k: v for k, v in s['readout'].items() if k.split('/')[0] in NEW} } against the hundred "
                      f"updates' {WIDTH}, from the world {sorted(set(s['from_world'].values()))}",
          "verdict": f"MET -- one configuration at {WIDTH} columns with the budget moved to two hundred and three "
                     "hundred and fifty updates" if (not differ and reads_ok and not s["thin"] and not s["short"]) else
                     f"FALSIFIER FIRED -- differing {differ[:6]}, read-outs "
                     f"{ {k: v for k, v in s['readout'].items() if k.split('/')[0] in NEW} }, thin {s['thin']}, "
                     f"short {s['short']}"}
    signs = s["sign"]
    j2 = {"id": "UA2",
          "measured": f"the biological anchor's standing at {BUDGETS} updates at {WIDTH} columns is "
                      f"{[round(r['curve'][str(b)]['bio']['standing'], 4) for b in BUDGETS]} at "
                      f"{[round(r['curve'][str(b)]['bio']['standing_sigma'], 2) for b in BUDGETS]} sigma, a sign "
                      f"sequence of {signs} with {s['sign_changes']} change(s)",
          "verdict": "MET -- the sign changes once at thirty-two columns, as it does at eight" if
                     (signs[0] < 0 and signs[-1] > 0 and s["sign_changes"] <= 1) else
                     f"FALSIFIER FIRED -- the ends are {signs[0]} and {signs[-1]} with {s['sign_changes']} change(s)"}
    same = s["sign"] == s["narrow_sign"]
    j3 = {"id": "UA3",
          "measured": f"at {WIDTH} columns the sign sequence is {signs} and at {NARROW_WIDTH} it is "
                      f"{s['narrow_sign']}, with standings {[round(s['standing'][str(b)], 4) for b in BUDGETS]} against "
                      f"{[round(s['narrow_standing'].get(str(b), float('nan')), 4) for b in BUDGETS]}",
          "verdict": "MET -- the two rungs' sign sequences are the same, so the width does not move the crossing" if
                     same else
                     f"FALSIFIER FIRED -- {WIDTH} gives {signs} against {NARROW_WIDTH}'s {s['narrow_sign']}"}
    gaps = {b: r["gaps"][str(b)]["price"] for b in BUDGETS}
    worst = max(gaps.values()) if gaps else 0.0
    j4 = {"id": "UA4",
          "measured": f"the pair's newest-task costs at {WIDTH} columns are "
                      f"{ {k: round(v, 4) for k, v in gaps.items()} } apart at {BUDGETS} updates",
          "verdict": f"MET -- the pair's prices are alike at every budget at thirty-two columns, the widest gap "
                     f"{worst:.4f}" if worst <= ALIKE else
                     f"FALSIFIER FIRED -- the widest gap is {worst:.4f}" if worst >= ALIKE_FIRES else
                     f"NULL -- the widest gap is {worst:.4f}, between {ALIKE:.2f} and {ALIKE_FIRES:.2f}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the budget curve at thirty-two columns ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll or the narrow curve is not there')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source, coupled, twenty replicates, the head reading the")
    print(f"   circuit's own neurons at {WIDTH} columns, at four budgets -- the same four `e467` walked at")
    print(f"   {NARROW_WIDTH}, so the crossing can be compared across a fourfold width")
    print(f"\n   {'updates':>8} {'anchor':>15} {'standing':>10} {'sigma':>6} {'price':>10} {'sigma':>6} "
          f"{'buffer-':>10} {'sigma':>6}")
    for b in BUDGETS:
        for side in ("bio", "rand"):
            c = r["curve"][str(b)][side]
            print(f"   {b:>8} {c['anchor']:>15} {c['standing']:>+10.4f} {c['standing_sigma']:>6.2f} "
                  f"{c['price']:>+10.4f} {c['price_sigma']:>6.2f} {c['buffer_over_anchor']:>+10.4f} "
                  f"{c['buffer_over_anchor_sigma']:>6.2f}")
    print(f"\n   the biological anchor's standing, by width:")
    print(f"      {WIDTH:>2} columns  " + ", ".join(f"{b}: {r['curve'][str(b)]['bio']['standing']:+.4f} "
                                                    f"({r['curve'][str(b)]['bio']['standing_sigma']:.2f}s)"
                                                    for b in BUDGETS))
    print(f"      {NARROW_WIDTH:>2} columns  " + ", ".join(
        f"{b}: {r['narrow']['standing'].get(str(b), float('nan')):+.4f}" for b in BUDGETS))
    print("\n== the registered claims, UA1-UA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print(f"\n   (`e467` put the crossing at eight columns between 350 and 500 updates; this asks whether a fourfold")
    print("    wider head crosses in the same place)")
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
