"""E467 -- the budget curve at eight columns: where the biological anchor's diagonal effect changes sign.

`e466` found that the far point's ladder and its null are the far point's: at a hundred updates both anchors' standings
are **negative** at all three widths and two of them resolve, where at five hundred every standing is between
**-0.0271** and **+0.0215** and none does. It closed with the gap it could not fill -- *two budgets are not a curve, and
nothing here says where between them the sign would change*.

**This unit walks the axis.** Four more rolls of the same configuration at **eight columns** -- both anchors, twenty
replicates each -- at **200** and **350** updates, read beside `e466`'s **100** and the far point's **500**, so the
biological anchor's standing is a **four-point curve** and the pair's gap is measured at four budgets rather than two.
Four claims, registered before any new roll's reading was opened.

- **TA1 -- and the new rolls are one configuration with the budget moved.** Three arms each at **20** replicates, every
  recorded config field agreeing with the hundred-update roll of the same side except `iters` and the output path, the
  read-out **8** and the circuit's own, and the task names equal. **Falsifier**: any other field differing, an arm
  missing or short, or a read-out that is the world's or another width.
- **TA2 -- and the biological anchor's standing changes sign once along the axis.** Its sign at a hundred updates is
  negative and at five hundred is positive, and the four-point sequence of signs carries **at most one** change.
  **Falsifier**: two changes in the sequence, which would say the axis crosses twice and the ends are not one fact.
  *A sequence of four signs is the smallest object a crossing can be located in.*
- **TA3 -- and the pair's prices are alike at eight columns at every budget.** The two anchors' newest-task costs differ
  by at most **0.05** at each of the four budgets. **Falsifier**: **0.10** or more at any budget; **null**: between.
  *At a hundred updates the gap is **0.0448**, twenty times the far point's **0.0021**, so this is the bar it is
  closest to.*
- **TA4 -- and the buffer is ahead of both anchors at every budget.** `replay` minus each anchor on the mean diagonal is
  positive at **two** sigma or more at each of the four budgets. **Falsifier**: any budget or anchor where it is not
  positive or is under two sigma.

**What it can do beyond that.** It turns `e466`'s pair of budgets into a curve on the one rung where the sign flip was
seen, so *the basis's diagonal effect is a null at five hundred updates* becomes a statement with a place in it, and the
buffer's advantage and the pair's likeness are read at four budgets instead of two.

**What it cannot do.** *One width*: **eight** columns is the rung the flip was seen on, and nothing here says the curve
at sixteen or thirty-two crosses in the same place. *And four budgets are still not a mechanism*: the axis is the number
of updates and the corpus carries no run that separates it from the training it buys, so a crossing is a place on a dial
and not a cause. *And one cell each*: twenty replicates, so a standing at two sigma is what a redraw could put under the
bar. *And one partition draw*: the matched-random cells are one draw of the same group sizes.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the four budgets at eight columns, both anchors, by budget and side
RUNS = {
    "100/bio": Path("runs/e466_earned_label_neurons8_iters100_20reps.json"),
    "100/rand": Path("runs/e466_earned_label_rand_neurons8_iters100_20reps.json"),
    "200/bio": Path("runs/e467_earned_label_neurons8_iters200_20reps.json"),
    "200/rand": Path("runs/e467_earned_label_rand_neurons8_iters200_20reps.json"),
    "350/bio": Path("runs/e467_earned_label_neurons8_iters350_20reps.json"),
    "350/rand": Path("runs/e467_earned_label_rand_neurons8_iters350_20reps.json"),
    "500/bio": Path("runs/e458_earned_label_neurons8_20reps.json"),
    "500/rand": Path("runs/e460_earned_label_rand_neurons8_20reps.json"),
}
BUDGETS = (100, 200, 350, 500)
#: the budgets as the artifact's own keys carry them: `json` stringifies an integer key
BK = tuple(str(b) for b in BUDGETS)
NEW = ("200", "350")
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
    ("TA1", f"and the new rolls are one configuration with the budget moved, at {MIN_REPS} replicates",
     "Three arms each at twenty replicates, every recorded config field agreeing with the hundred-update roll of the "
     "same side except iters and the output path, the read-out 8 and the circuit's own, and the task names equal",
     "falsifier: any other field differing, an arm missing or short, or a read-out that is the world's or another "
     "width"),
    ("TA2", "and the biological anchor's standing changes sign once along the axis",
     "Its sign at a hundred updates is negative and at five hundred is positive, and the four-point sequence carries at "
     "most one change",
     "falsifier: two changes in the sequence, which would say the axis crosses twice"),
    ("TA3", f"and the pair's prices are alike at eight columns at every budget, within {ALIKE:.2f}",
     "The two anchors' newest-task costs differ by at most 0.05 at each of the four budgets",
     f"falsifier: {ALIKE_FIRES:.2f} or more at any budget; null: between"),
    ("TA4", f"and the buffer is ahead of both anchors at every budget, at {SIGMA:.0f} sigma",
     "replay minus each anchor on the mean diagonal is positive at two sigma or more at each of the four budgets",
     "falsifier: any budget or anchor where it is not positive or is under two sigma"),
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


def reading(runs: dict = RUNS) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "readouts": {}, "curve": {}, "gaps": {}, "spans": {}}
    for label, path in runs.items():
        got = _roll(path, ANCHOR_OF[label.split("/")[1]])
        if got is None:
            return {**out, "ok": False,
                    "reason": f"roll {label}: {path} is absent or carries no {ANCHOR_OF[label.split('/')[1]]} arm"}
        out["runs"][label] = got
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
                "budget": int(b), "side": side, "anchor": roll["anchor"],
                "standing": over["mean"], "standing_sigma": abs(over["sigma"]),
                "price": last["mean"], "price_sigma": abs(last["sigma"]),
                "buffer_over_anchor": buf["mean"], "buffer_over_anchor_sigma": abs(buf["sigma"])}
    out["gaps"] = {b: {"price": abs(out["curve"][b]["bio"]["price"] - out["curve"][b]["rand"]["price"]),
                       "standing": abs(out["curve"][b]["bio"]["standing"] - out["curve"][b]["rand"]["standing"])}
                   for b in BK}
    thin = {label: v["replicates"] for label, roll in out["runs"].items() for k, v in roll["arms"].items()
            if v["replicates"] < MIN_REPS}
    short = {label: sorted(roll["arms"]) for label, roll in out["runs"].items() if len(roll["arms"]) < N_ARMS}
    out["spans"] = {
        "budgets": list(BUDGETS), "runs": len(out["runs"]), "same_fields": len(out["same"]),
        "replicates": sorted({v["replicates"] for roll in out["runs"].values() for v in roll["arms"].values()}),
        "thin": thin, "short": short,
        "readout": {label: (roll["readouts"] or [None])[0] for label, roll in out["runs"].items()},
        "from_world": {label: roll["from_world"] for label, roll in out["runs"].items()},
        "sign": {side: [(1 if out["curve"][str(b)][side]["standing"] > 0 else -1) for b in BUDGETS]
                 for side in ("bio", "rand")},
        "sign_changes": {side: sum(1 for i in range(len(BUDGETS) - 1)
                                   if (out["curve"][str(BUDGETS[i])][side]["standing"] > 0) !=
                                   (out["curve"][str(BUDGETS[i + 1])][side]["standing"] > 0))
                         for side in ("bio", "rand")},
        "budget": list(BUDGETS),
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no arm"} for c in CLAIMS]
    s = r["spans"]
    differ = sorted(k for k, v in r["same"].items() if not v)
    reads_ok = all(s["readout"][f"{b}/{side}"] == 8 for b in NEW for side in ("bio", "rand")) and \
        all(v is False for v in s["from_world"].values())
    j1 = {"id": "TA1",
          "measured": f"the four new rolls carry {len(NEW) * 2} cells at {s['replicates']} replicates over "
                      f"{s['same_fields']} compared fields, the read-out "
                      f"{ {k: v for k, v in s['readout'].items() if k.split('/')[0] in NEW} } against the hundred "
                      f"updates' 8, from the world {sorted(set(s['from_world'].values()))}",
          "verdict": "MET -- one configuration at eight columns with the budget moved to two hundred and three "
                     "hundred and fifty updates" if (not differ and reads_ok and not s["thin"] and not s["short"]) else
                     f"FALSIFIER FIRED -- differing {differ[:6]}, read-outs "
                     f"{ {k: v for k, v in s['readout'].items() if k.split('/')[0] in NEW} }, thin {s['thin']}, "
                     f"short {s['short']}"}
    signs = s["sign"]["bio"]
    j2 = {"id": "TA2",
          "measured": f"the biological anchor's standing at {BUDGETS} updates is "
                      f"{[round(r['curve'][str(b)]['bio']['standing'], 4) for b in BUDGETS]} at "
                      f"{[round(r['curve'][str(b)]['bio']['standing_sigma'], 2) for b in BUDGETS]} sigma, a sign "
                      f"sequence of {signs} with {s['sign_changes']['bio']} change(s), against the random anchor's "
                      f"{s['sign']['rand']} with {s['sign_changes']['rand']}",
          "verdict": "MET -- the sign changes once between a hundred updates and five hundred, and the two "
                     "intermediate budgets place it" if
                     (signs[0] < 0 and signs[-1] > 0 and s["sign_changes"]["bio"] <= 1) else
                     f"FALSIFIER FIRED -- the ends are {signs[0]} and {signs[-1]} with "
                     f"{s['sign_changes']['bio']} change(s)"}
    gaps = {b: r["gaps"][str(b)]["price"] for b in BUDGETS}
    worst = max(gaps.values()) if gaps else 0.0
    j3 = {"id": "TA3",
          "measured": f"the pair's newest-task costs at eight columns are { {k: round(v, 4) for k, v in gaps.items()} } "
                      f"apart at {BUDGETS} updates",
          "verdict": f"MET -- the pair's prices are alike at every budget, the widest gap {worst:.4f}" if
                     worst <= ALIKE else
                     f"FALSIFIER FIRED -- the widest gap is {worst:.4f}" if worst >= ALIKE_FIRES else
                     f"NULL -- the widest gap is {worst:.4f}, between {ALIKE:.2f} and {ALIKE_FIRES:.2f}"}
    buf = {(b, side): (r["curve"][str(b)][side]["buffer_over_anchor"],
                       r["curve"][str(b)][side]["buffer_over_anchor_sigma"])
           for b in BUDGETS for side in ("bio", "rand")}
    bad = sorted(f"{b}/{side}" for (b, side), (m, sg) in buf.items() if not (m > 0 and sg >= SIGMA))
    j4 = {"id": "TA4",
          "measured": f"the buffer's advantage over its anchor runs "
                      f"{ {f'{b}/{s_}': round(buf[(b, s_)][0], 4) for b in BUDGETS for s_ in ('bio', 'rand')} } at "
                      f"{ {f'{b}/{s_}': round(buf[(b, s_)][1], 2) for b in BUDGETS for s_ in ('bio', 'rand')} } sigma",
          "verdict": "MET -- the buffer is ahead of both anchors at every budget" if not bad else
                     f"FALSIFIER FIRED -- {bad}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the budget curve at eight columns ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source, coupled, twenty replicates, the head reading the")
    print("   circuit's own neurons at eight columns, at four budgets -- so the biological anchor's standing is a")
    print("   four-point curve rather than the pair of budgets `e466` left the sign flip between")
    print(f"\n   {'updates':>8} {'anchor':>15} {'standing':>10} {'sigma':>6} {'price':>10} {'sigma':>6} "
          f"{'buffer-':>10} {'sigma':>6}")
    for b in BUDGETS:
        for side in ("bio", "rand"):
            c = r["curve"][str(b)][side]
            print(f"   {b:>8} {c['anchor']:>15} {c['standing']:>+10.4f} {c['standing_sigma']:>6.2f} "
                  f"{c['price']:>+10.4f} {c['price_sigma']:>6.2f} {c['buffer_over_anchor']:>+10.4f} "
                  f"{c['buffer_over_anchor_sigma']:>6.2f}")
    print("\n   the pair apart at eight columns, by budget:")
    for b in BUDGETS:
        print(f"      {b:>8} updates  standing gap {r['gaps'][str(b)]['standing']:.4f}  price gap "
              f"{r['gaps'][str(b)]['price']:.4f}")
    print("\n== the registered claims, TA1-TA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e466` found the sign at a hundred updates negative and at five hundred positive on six rolls; this")
    print("    walks the axis between them on the one rung where the flip was seen)")
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
