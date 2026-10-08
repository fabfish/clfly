"""E466 -- the width ladder at another budget: whether the far point's ladder is the far point's.

The whole ladder this line has built -- the card's world's head on the circuit's own neurons at **8**, **16**, **24** and
**32** columns, both anchors, with the block penalty -- is measured at **500 updates**. `e438`'s configuration is the one
every rung inherits, and its `--iters` is 500, which is the card's **far point**: the near point `e393` and `e394` use is
**20 updates**, and the corpus's budget series (`e389`, `e390`, `e391`) walks the earned label from 30 to 425 at twenty
replicates. **Every one of those runs carries `naive` and `replay` on the world's own state and not one of them carries a
penalty arm or a neuron head**, so what the ledger of widths says is what 500 updates say, and nothing in the corpus
measures the ladder at another budget.

**This unit moves the budget and holds the ladder.** Six rolls of the far point's configuration at **100 updates** -- the
budget `e390` and `e408` use for the earned label, since something is learned there and nothing at twenty is -- at three
widths and both anchors, twenty replicates each, with the six far-point rolls read beside them. Four claims, registered
before any new roll's reading was opened.

- **SA1 -- and the new rolls are one configuration with the budget moved.** Three arms each at **20** replicates, every
  recorded config field agreeing with the far-point roll of the same width and side except `iters` and the output path,
  the read-out the circuit's own at that width, and the task names equal. **Falsifier**: any other field differing, an
  arm missing or short, or a read-out that is the world's or another width.
- **SA2 -- and the price's magnitude falls with the width at the middle point for both arms.** For each anchor its
  newest-task cost's magnitude is at or above the next rung's at every step from eight to thirty-two. **Falsifier**: for
  either arm a magnitude that rises as the head widens. *This is the far point's first ladder claim, asked at a budget a
  fifth of the way there.*
- **SA3 -- and the pair's prices agree at the middle point.** The two anchors' newest-task costs differ by at most
  **0.05** at every width. **Falsifier**: **0.10** or more at any width; **null**: between. *This is `e462`'s and
  `e463`'s finding -- that the pair is alike at the narrow rungs and apart at the wide one -- asked where the corpus
  has never asked it.*
- **SA4 -- and the buffer is ahead of both anchors at the middle point.** `replay` minus each anchor on the mean
  diagonal is positive at **two** sigma or more at every width. **Falsifier**: any width or arm where it is not
  positive or is under two sigma.

**What it can do beyond that.** It separates the ladder from the budget: if the price falls with the width and the pair
agrees at a hundred updates as they do at five hundred, the shape is a property of the head and not of a trained body;
if they do not, then what this line has been calling *the width's grip on the price* is the far point's reading, and
`e462`'s and `e463`'s findings are scoped to 500 updates rather than to the world.

**What it cannot do.** *Two budgets are not a curve*: **100** and **500** are one pair, the corpus's budget series
carries no penalty arm to compare against, and nothing here says where between them the shape would change. *And one
cell each*: twenty replicates, so a gap at the third decimal place is what a redraw could move. *And one partition draw*:
the matched-random cells are one draw of the same group sizes. *And the widths are three of the four this line carries*:
**24** is left out so that the two points are compared on the same rungs, so a difference at that rung is not measured.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the six far-point rolls and the six this unit drove, by budget, width and anchor
FAR = {
    "8/bio": Path("runs/e458_earned_label_neurons8_20reps.json"),
    "8/rand": Path("runs/e460_earned_label_rand_neurons8_20reps.json"),
    "16/bio": Path("runs/e462_earned_label_neurons16_20reps.json"),
    "16/rand": Path("runs/e462_earned_label_rand_neurons16_20reps.json"),
    "32/bio": Path("runs/e455_earned_label_neurons_20reps.json"),
    "32/rand": Path("runs/e456_earned_label_rand_neurons_20reps.json"),
}
MID = {
    "8/bio": Path("runs/e466_earned_label_neurons8_iters100_20reps.json"),
    "8/rand": Path("runs/e466_earned_label_rand_neurons8_iters100_20reps.json"),
    "16/bio": Path("runs/e466_earned_label_neurons16_iters100_20reps.json"),
    "16/rand": Path("runs/e466_earned_label_rand_neurons16_iters100_20reps.json"),
    "32/bio": Path("runs/e466_earned_label_neurons32_iters100_20reps.json"),
    "32/rand": Path("runs/e466_earned_label_rand_neurons32_iters100_20reps.json"),
}
POINTS = {"far": FAR, "mid": MID}
BUDGET = {"far": 500, "mid": 100}
WIDTHS = (8, 16, 32)
#: the widths as the artifact's own keys carry them: `json` stringifies an integer key, so the gaps are keyed by text
WK = tuple(str(w) for w in WIDTHS)
CELLS = tuple(f"{w}/{s}" for w in WIDTHS for s in ("bio", "rand"))
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
    ("SA1", f"and the new rolls are one configuration with the budget moved, at {MIN_REPS} replicates",
     "Three arms each at twenty replicates, every recorded config field agreeing with the far-point roll of the same "
     "width and side except iters and the output path, the read-out the circuit's own at that width, and the task "
     "names equal",
     "falsifier: any other field differing, an arm missing or short, or a read-out that is the world's or another "
     "width"),
    ("SA2", "and the price's magnitude falls with the width at the middle point for both arms",
     "For each anchor its newest-task cost's magnitude is at or above the next rung's at every step from eight to "
     "thirty-two",
     "falsifier: for either arm a magnitude that rises as the head widens"),
    ("SA3", f"and the pair's prices agree at the middle point, within {ALIKE:.2f}",
     "The two anchors' newest-task costs differ by at most 0.05 at every width",
     f"falsifier: {ALIKE_FIRES:.2f} or more at any width; null: between"),
    ("SA4", f"and the buffer is ahead of both anchors at the middle point, at {SIGMA:.0f} sigma",
     "replay minus each anchor on the mean diagonal is positive at two sigma or more at every width",
     "falsifier: any width or arm where it is not positive or is under two sigma"),
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
            "last": [r["final_per_task"][-1] for r in reps],
            "final": [statistics.fmean([r["final_per_task"][k] for r in reps]) for k in range(N_TASKS)]}


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


def reading(far: dict = FAR, mid: dict = MID) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "readouts": {}, "table": {}, "gaps": {}, "spans": {}}
    for point, runs in (("far", far), ("mid", mid)):
        for cell, path in runs.items():
            got = _roll(path, ANCHOR_OF[cell.split("/")[1]])
            if got is None:
                return {**out, "ok": False,
                        "reason": f"roll {point} {cell}: {path} is absent or carries no "
                                  f"{ANCHOR_OF[cell.split('/')[1]]} arm"}
            out["runs"][f"{point}/{cell}"] = got
    for cell in CELLS:
        a, b = out["runs"][f"far/{cell}"], out["runs"][f"mid/{cell}"]
        fields = sorted(set(a["config"]) | set(b["config"]))
        for k in fields:
            out["same"][f"{cell}.{k}"] = a["config"].get(k) == b["config"].get(k)
        out["same"][f"{cell}.circuit"] = a["shared"].get("circuit") == b["shared"].get("circuit")
        out["same"][f"{cell}.tasks"] = a["shared"].get("tasks") == b["shared"].get("tasks")
    out["readouts"] = {label: {"readouts": roll["readouts"], "from_world": roll["from_world"]}
                       for label, roll in out["runs"].items()}
    for point in ("far", "mid"):
        out["table"][point] = {}
        for w in WIDTHS:
            for side in ("bio", "rand"):
                cell = f"{w}/{side}"
                roll = out["runs"][f"{point}/{cell}"]
                over = _paired(roll["arms"][roll["anchor"]]["diagonal"], roll["arms"][BASELINE]["diagonal"])
                last = _paired(roll["arms"][roll["anchor"]]["last"], roll["arms"][BASELINE]["last"])
                buf = _paired(roll["arms"][BUFFER]["diagonal"], roll["arms"][roll["anchor"]]["diagonal"])
                out["table"][point][cell] = {
                    "width": w, "side": side, "anchor": roll["anchor"],
                    "standing": over["mean"], "standing_sigma": abs(over["sigma"]),
                    "price": last["mean"], "price_sigma": abs(last["sigma"]),
                    "buffer_over_anchor": buf["mean"], "buffer_over_anchor_sigma": abs(buf["sigma"])}
        out["gaps"][point] = {str(w): {"price": abs(out["table"][point][f"{w}/bio"]["price"] -
                                                        out["table"][point][f"{w}/rand"]["price"]),
                                       "standing": abs(out["table"][point][f"{w}/bio"]["standing"] -
                                                       out["table"][point][f"{w}/rand"]["standing"])}
                              for w in WIDTHS}
    thin = {label: v["replicates"] for label, roll in out["runs"].items() for k, v in roll["arms"].items()
            if v["replicates"] < MIN_REPS}
    short = {label: sorted(roll["arms"]) for label, roll in out["runs"].items() if len(roll["arms"]) < N_ARMS}
    out["spans"] = {
        "cells": len(CELLS), "runs": len(out["runs"]),
        "replicates": sorted({v["replicates"] for roll in out["runs"].values() for v in roll["arms"].values()}),
        "same_fields": len(out["same"]),
        "thin": thin, "short": short,
        "mid_readout": {cell: (out["runs"][f"mid/{cell}"]["readouts"] or [None])[0] for cell in CELLS},
        "far_readout": {cell: (out["runs"][f"far/{cell}"]["readouts"] or [None])[0] for cell in CELLS},
        "from_world": {label: roll["from_world"] for label, roll in out["runs"].items()},
        "mag": {side: [abs(out["table"]["mid"][f"{w}/{side}"]["price"]) for w in WIDTHS] for side in ("bio", "rand")},
        "mag_far": {side: [abs(out["table"]["far"][f"{w}/{side}"]["price"]) for w in WIDTHS] for side in ("bio", "rand")},
        "budget": dict(BUDGET),
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no arm"}
                for c in CLAIMS]
    s = r["spans"]
    differ = sorted(k for k, v in r["same"].items() if not v)
    ro = {"mid": s["mid_readout"], "far": s["far_readout"]}
    reads_ok = all(ro["mid"][cell] == int(cell.split("/")[0]) for cell in CELLS) and \
        all(ro["far"][cell] == int(cell.split("/")[0]) for cell in CELLS) and \
        all(v is False for v in s["from_world"].values())
    j1 = {"id": "SA1",
          "measured": f"the six new rolls carry {s['runs'] - 6} cells at {s['replicates']} replicates over "
                      f"{s['same_fields']} compared fields, the read-out {s['mid_readout']} against the far point's "
                      f"{s['far_readout']}, from the world "
                      f"{sorted(set(s['from_world'].values()))}",
          "verdict": "MET -- one configuration at three widths with the budget moved to a hundred updates" if
                     (not differ and reads_ok and not s["thin"] and not s["short"]) else
                     f"FALSIFIER FIRED -- differing {differ[:6]}, read-outs {ro}, thin {s['thin']}, short {s['short']}"}
    mag = s["mag"]
    falls = {side: all(mag[side][i] >= mag[side][i + 1] for i in range(len(WIDTHS) - 1)) for side in ("bio", "rand")}
    j2 = {"id": "SA2",
          "measured": f"at a hundred updates the price's magnitudes run {BIO} "
                      f"{'/'.join(f'{v:.4f}' for v in mag['bio'])} and {RAND} "
                      f"{'/'.join(f'{v:.4f}' for v in mag['rand'])} at {', '.join(str(w) for w in WIDTHS)} columns, "
                      f"against {BIO} {'/'.join(f'{v:.4f}' for v in s['mag_far']['bio'])} at the far point",
          "verdict": "MET -- both arms' magnitudes fall with the width at a hundred updates, as they do at five "
                     "hundred" if falls["bio"] and falls["rand"] else
                     f"FALSIFIER FIRED -- the ladder does not hold at a hundred updates: {falls}"}
    gaps = {w: r["gaps"]["mid"][str(w)]["price"] for w in WIDTHS}
    worst = max(gaps.values()) if gaps else 0.0
    j3 = {"id": "SA3",
          "measured": f"at a hundred updates the pair's newest-task costs are {gaps} apart at {WIDTHS}, against "
                      f"{ {w: round(r['gaps']['far'][str(w)]['price'], 4) for w in WIDTHS} } at the far point",
          "verdict": f"MET -- the pair's prices agree at every width at a hundred updates" if worst <= ALIKE else
                     f"FALSIFIER FIRED -- the widest gap is {worst:.4f}" if worst >= ALIKE_FIRES else
                     f"NULL -- the widest gap is {worst:.4f}, between {ALIKE:.2f} and {ALIKE_FIRES:.2f}"}
    buf = {cell: (r["table"]["mid"][cell]["buffer_over_anchor"], r["table"]["mid"][cell]["buffer_over_anchor_sigma"])
           for cell in CELLS}
    bad = sorted(c for c, (m, sg) in buf.items() if not (m > 0 and sg >= SIGMA))
    j4 = {"id": "SA4",
          "measured": f"at a hundred updates the buffer's advantage over its anchor runs "
                      f"{ {c: round(buf[c][0], 4) for c in CELLS} } at "
                      f"{ {c: round(buf[c][1], 2) for c in CELLS} } sigma",
          "verdict": "MET -- the buffer is ahead of both anchors at every width at a hundred updates" if not bad else
                     f"FALSIFIER FIRED -- {bad}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the width ladder at another budget ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source, coupled, twenty replicates, the head reading the")
    print("   circuit's own neurons -- at the far point (500 updates, which every rung of this line inherits) and at")
    print("   a hundred updates, which the corpus's budget series uses for the earned label and has never used here")
    for point in ("far", "mid"):
        print(f"\n   {point} ({BUDGET[point]} updates):")
        print(f"      {'columns':>8} {'anchor':>15} {'standing':>10} {'sigma':>6} {'price':>10} {'sigma':>6} "
              f"{'buffer-':>10} {'sigma':>6}")
        for w in WIDTHS:
            for side in ("bio", "rand"):
                c = r["table"][point][f"{w}/{side}"]
                print(f"      {w:>8} {c['anchor']:>15} {c['standing']:>+10.4f} {c['standing_sigma']:>6.2f} "
                      f"{c['price']:>+10.4f} {c['price_sigma']:>6.2f} {c['buffer_over_anchor']:>+10.4f} "
                      f"{c['buffer_over_anchor_sigma']:>6.2f}")
        print(f"      the pair apart: " + ", ".join(f"w{w} standing {r['gaps'][point][str(w)]['standing']:.4f} price "
                                                    f"{r['gaps'][point][str(w)]['price']:.4f}" for w in WIDTHS))
    print("\n== the registered claims, SA1-SA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (every rung of this line inherits `e438`'s configuration, whose budget is 500 updates; this asks the")
    print("    same question at a hundred, so the ladder is either the head's or the far point's)")
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
