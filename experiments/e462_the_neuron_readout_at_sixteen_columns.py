"""E462 -- the neuron read-out at sixteen columns: the middle rung, and whether the width's grip on the price is a ladder.

`e458` and `e455` put the card's world's head on the circuit's own neurons at **eight** and **thirty-two** columns and the
two arms' newest-task prices came out

  * `ewc-block`: **-0.0615** at **4.48** sigma at eight, **-0.0115** at **0.78** at thirty-two;
  * `ewc-block-rand`: **-0.0594** at **4.18** sigma at eight, **-0.0323** at **2.77** at thirty-two,

and `e461`'s thirteenth revision says what the card cannot do with them: *the eight-column heads differ from the
thirty-two column one by a factor of four and the widths between them are not measured*, so **the width separates the
pair's prices is one step and not a trend**. **This unit drives the middle rung.** Two rolls of `e458`'s configuration at
**sixteen** columns -- the biological arm and the matched-random arm, twenty replicates each, `--readout-from-world`
omitted so the head reads the circuit's own neurons -- so each arm's price is read at three widths and the pair at four
heads.

Five claims, registered before either new roll's reading was opened.

- **DI1 -- and the two rolls are one configuration at the middle rung with the arm list moved.** Three arms each at
  **20** replicates, every recorded config field agreeing between the two rolls except `methods`, the output path and the
  saved weights, the read-out **16** and not the world's, the three task names equal, and the two rolls' `naive` and
  `replay` replicates **bit-identical** to one another. **Falsifier**: any other config field differing, an arm missing
  or short, a read-out that is the world's or another width, or any shared replicate differing.
- **DI2 -- and both anchors' prices resolve at the middle rung.** Each arm's cost at the last-taught task is negative at
  **two** sigma or more. **Falsifier**: either arm not negative, or under two sigma. *They read **-0.0615** at **4.48**
  and **-0.0594** at **4.18** at eight columns and **-0.0115** at **0.78** and **-0.0323** at **2.77** at thirty-two.*
- **DI3 -- and the pair's prices agree at the middle rung.** The two arms' newest-task costs differ by at most **0.05**.
  **Falsifier**: **0.10** or more apart; **null**: between.
- **DI4 -- and the width's grip on each arm's price is a ladder and not one step.** For **each** arm the price's
  magnitude at sixteen columns is at or below its eight-column value and at or above its thirty-two column value -- so
  the fall is ordered across both rungs and not a single jump between the ends. **Falsifier**: for either arm the
  sixteen-column magnitude above its eight-column one, or below its thirty-two column one.
- **DI5 -- and the buffer is ahead of both anchors at the middle rung.** `replay` minus each anchor on the mean diagonal
  is positive at **two** sigma or more. **Falsifier**: for either arm not positive, or under two sigma.

**What it can do beyond that.** It turns the width axis from two readings into three for both arms at once, so `e461`'s
own sentence about the ladder can be replaced by a measurement, and it settles whether the pair's prices agree at the
middle rung as they do at both eight-column heads (`e460`) or separate as they do at the wide one (`e456`). Read with
`e458`, `e455`, `e456` and `e460` it is the whole of what this line has measured about the head's width on this pair.

**What it cannot do.** *Three widths are not a mechanism*: **8**, **16** and **32** are one octave and a half of a dial
whose setting also moves the head's parameter count, so a ladder is a shape and not a cause. *And one cell each*: the
card's world at twenty replicates, so a price at two sigma is what a redraw could put under the bar. *And one partition
draw*: the matched-random partition is a draw of the same group sizes and not the family of them. *And a claim about a
pair is not a claim about the head*: the two arms share the baseline and the buffer, so the three widths are read once
each and not crossed with anything else this line has varied.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the two new rolls at sixteen columns and the four rolls the ladder is read against, by rung and anchor
RUNS = {
    "narrow/bio": Path("runs/e458_earned_label_neurons8_20reps.json"),
    "narrow/rand": Path("runs/e460_earned_label_rand_neurons8_20reps.json"),
    "mid/bio": Path("runs/e462_earned_label_neurons16_20reps.json"),
    "mid/rand": Path("runs/e462_earned_label_rand_neurons16_20reps.json"),
    "wide/bio": Path("runs/e455_earned_label_neurons_20reps.json"),
    "wide/rand": Path("runs/e456_earned_label_rand_neurons_20reps.json"),
}
#: the width each rung's head reads, and the arm each roll's second method is
WIDTHS = {"narrow": 8, "mid": 16, "wide": 32}
ANCHOR_OF = {"bio": "ewc-block", "rand": "ewc-block-rand"}
RUNGS = ("narrow", "mid", "wide")
BASELINE = "naive"
BIO = "ewc-block"
RAND = "ewc-block-rand"
BUFFER = "replay"
SHARED_ARMS = ("naive", "replay")
SHARED = ("circuit", "tasks")
IGNORED = ("json_out", "save_theta", "methods")
N_TASKS = 3
N_ARMS = 3
MIN_REPS = 20
SIGMA = 2.0
ALIKE = 0.05
ALIKE_FIRES = 0.10
CLAIMS = (
    ("DI1", f"and the two rolls are one configuration at the middle rung with the arm list moved, at {MIN_REPS} replicates",
     "Three arms each at twenty replicates, every recorded config field agreeing between the two rolls except methods, "
     "the output path and the saved weights, the read-out 16 and not the world's, the three task names equal, and the "
     "two rolls' naive and replay bit-identical to one another",
     "falsifier: any other config field differing, an arm missing or short, a read-out that is the world's or another "
     "width, or any shared replicate differing"),
    ("DI2", f"and both anchors' prices resolve at the middle rung, at {SIGMA:.0f} sigma",
     "Each arm's cost at the last-taught task is negative at two sigma or more",
     "falsifier: either arm not negative, or under two sigma"),
    ("DI3", f"and the pair's prices agree at the middle rung, within {ALIKE:.2f}",
     "The two arms' newest-task costs differ by at most 0.05",
     f"falsifier: {ALIKE_FIRES:.2f} or more apart; null: between"),
    ("DI4", "and the width's grip on each arm's price is a ladder and not one step",
     "For each arm the price's magnitude at sixteen columns is at or below its eight-column value and at or above its "
     "thirty-two column value",
     "falsifier: for either arm the sixteen-column magnitude above its eight-column one, or below its thirty-two "
     "column one"),
    ("DI5", f"and the buffer is ahead of both anchors at the middle rung, at {SIGMA:.0f} sigma",
     "replay minus each anchor on the mean diagonal is positive at two sigma or more",
     "falsifier: for either arm not positive, or under two sigma"),
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
            "forgetting": statistics.fmean([r["mean_forgetting"] for r in reps]),
            "records": [{"final_per_task": list(r["final_per_task"]),
                         "mean_forgetting": r["mean_forgetting"]} for r in reps]}


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
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "identical": {}, "readouts": {}, "contrasts": {},
           "ladder": {}, "spans": {}}
    for label, path in runs.items():
        anchor = ANCHOR_OF[label.split("/")[1]]
        got = _roll(path, anchor)
        if got is None:
            return {**out, "ok": False, "reason": f"roll {label}: {path} is absent or carries no {anchor} arm"}
        out["runs"][label] = got
    mid_bio, mid_rand = out["runs"]["mid/bio"], out["runs"]["mid/rand"]
    same = {}
    fields = sorted(set(mid_bio["config"]) | set(mid_rand["config"]))
    for k in fields:
        same[f"config.{k}"] = mid_bio["config"].get(k) == mid_rand["config"].get(k)
    same["circuit"] = mid_bio["shared"].get("circuit") == mid_rand["shared"].get("circuit")
    same["tasks"] = mid_bio["shared"].get("tasks") == mid_rand["shared"].get("tasks")
    out["same"] = same
    out["readouts"] = {label: {"readouts": roll["readouts"], "from_world": roll["from_world"]}
                       for label, roll in out["runs"].items()}
    for arm in SHARED_ARMS:
        out["identical"][f"mid/bio-mid/rand:{arm}"] = _identical(mid_bio["arms"][arm]["records"],
                                                                mid_rand["arms"][arm]["records"])
    for label, roll in out["runs"].items():
        out["contrasts"][label] = {
            "anchor_over_naive": _paired(roll["arms"][roll["anchor"]]["diagonal"],
                                         roll["arms"][BASELINE]["diagonal"]),
            "anchor_last": _paired(roll["arms"][roll["anchor"]]["last"], roll["arms"][BASELINE]["last"]),
            "buffer_over_anchor": _paired(roll["arms"][BUFFER]["diagonal"],
                                          roll["arms"][roll["anchor"]]["diagonal"]),
            "anchor_forgetting": _paired(roll["arms"][roll["anchor"]]["final"],
                                         roll["arms"][BASELINE]["final"]),
        }
    for side in ("bio", "rand"):
        out["ladder"][side] = {rung: {"width": WIDTHS[rung],
                                      "standing": out["contrasts"][f"{rung}/{side}"]["anchor_over_naive"]["mean"],
                                      "standing_sigma": abs(out["contrasts"][f"{rung}/{side}"]["anchor_over_naive"]["sigma"]),
                                      "price": out["contrasts"][f"{rung}/{side}"]["anchor_last"]["mean"],
                                      "price_sigma": abs(out["contrasts"][f"{rung}/{side}"]["anchor_last"]["sigma"]),
                                      "buffer_over_anchor": out["contrasts"][f"{rung}/{side}"]["buffer_over_anchor"]["mean"],
                                      "buffer_over_anchor_sigma":
                                          abs(out["contrasts"][f"{rung}/{side}"]["buffer_over_anchor"]["sigma"])}
                                 for rung in RUNGS}
    out["spans"] = {"replicates": sorted({v["replicates"] for roll in out["runs"].values()
                                         for v in roll["arms"].values()}),
                    "arms": {label: len(roll["arms"]) for label, roll in out["runs"].items()},
                    "same_fields": len(same),
                    "readout": {"mid_bio": (mid_bio["readouts"] or [None])[0],
                                "mid_rand": (mid_rand["readouts"] or [None])[0],
                                "from_world": {label: roll["from_world"] for label, roll in out["runs"].items()}},
                    "mid": {"standing": {side: out["ladder"][side]["mid"]["standing"] for side in ("bio", "rand")},
                            "standing_sigma": {side: out["ladder"][side]["mid"]["standing_sigma"]
                                               for side in ("bio", "rand")},
                            "price": {side: out["ladder"][side]["mid"]["price"] for side in ("bio", "rand")},
                            "price_sigma": {side: out["ladder"][side]["mid"]["price_sigma"]
                                            for side in ("bio", "rand")}}}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no arm"} for c in CLAIMS]
    differ = sorted(k for k, v in r["same"].items() if not v)
    not_identical = sorted(k for k, v in r["identical"].items() if not v["equal"])
    thin = {lbl: v["replicates"] for lbl, a in r["runs"].items() for k, v in a["arms"].items()
            if v["replicates"] < MIN_REPS}
    short = {lbl: sorted(a["arms"]) for lbl, a in r["runs"].items() if len(a["arms"]) < N_ARMS}
    ro = r["spans"]["readout"]
    reads_ok = (ro["mid_bio"] == WIDTHS["mid"] and ro["mid_rand"] == WIDTHS["mid"] and
                ro["from_world"]["mid/bio"] is False and ro["from_world"]["mid/rand"] is False and
                all(x == WIDTHS["mid"] for x in r["runs"]["mid/bio"]["readouts"]) and
                all(x == WIDTHS["mid"] for x in r["runs"]["mid/rand"]["readouts"]))
    j1 = {"id": "DI1",
          "measured": f"the two middle rolls carry {len(r['runs']['mid/bio']['arms'])} and "
                      f"{len(r['runs']['mid/rand']['arms'])} arms at {r['spans']['replicates']} replicates over "
                      f"{r['spans']['same_fields']} compared fields, the read-out {ro['mid_bio']} and {ro['mid_rand']} "
                      f"against the narrow rung's {WIDTHS['narrow']} and the wide one's {WIDTHS['wide']}, from the world "
                      f"{ {k: v for k, v in ro['from_world'].items()} }, the shared arms bit-identical "
                      f"{len(r['identical']) - len(not_identical)} of {len(r['identical'])}",
          "verdict": "MET -- one configuration at sixteen neuron columns with the arm list moved, and the two shared "
                     "arms reproducing one another" if
                     (not short and not differ and not not_identical and reads_ok and not thin) else
                     f"FALSIFIER FIRED -- differing {differ}, not bit-identical {not_identical}, read-outs {ro}, "
                     f"thin {thin}, short {short}"}
    p = r["spans"]["mid"]["price"]
    ps = r["spans"]["mid"]["price_sigma"]
    j2 = {"id": "DI2",
          "measured": f"at sixteen neuron columns the two anchors' newest-task costs are {BIO} {p['bio']:+.4f} at "
                      f"{ps['bio']:.2f} sigma and {RAND} {p['rand']:+.4f} at {ps['rand']:.2f}",
          "verdict": f"MET -- both prices resolve at the middle rung, {ps['bio']:.2f} and {ps['rand']:.2f} sigma" if
                     (p["bio"] < 0 and ps["bio"] >= SIGMA and p["rand"] < 0 and ps["rand"] >= SIGMA) else
                     f"FALSIFIER FIRED -- {BIO} {p['bio']:+.4f} at {ps['bio']:.2f} and {RAND} {p['rand']:+.4f} at "
                     f"{ps['rand']:.2f}"}
    gap = abs(p["bio"] - p["rand"])
    j3 = {"id": "DI3",
          "measured": f"the pair's newest-task costs at sixteen columns are {p['bio']:+.4f} and {p['rand']:+.4f}, "
                      f"{gap:.4f} apart",
          "verdict": f"MET -- the pair's prices agree at the middle rung, {gap:.4f} apart" if gap <= ALIKE else
                     f"FALSIFIER FIRED -- the gap is {gap:.4f}" if gap >= ALIKE_FIRES else
                     f"NULL -- the gap is {gap:.4f}, between {ALIKE:.2f} and {ALIKE_FIRES:.2f}"}
    lad = r["ladder"]
    ordered = {side: (abs(lad[side]["mid"]["price"]) <= abs(lad[side]["narrow"]["price"]) and
                      abs(lad[side]["mid"]["price"]) >= abs(lad[side]["wide"]["price"])) for side in ("bio", "rand")}
    j4 = {"id": "DI4",
          "measured": f"the price's magnitudes run {BIO} {abs(lad['bio']['narrow']['price']):.4f} then "
                      f"{abs(lad['bio']['mid']['price']):.4f} then {abs(lad['bio']['wide']['price']):.4f}, and {RAND} "
                      f"{abs(lad['rand']['narrow']['price']):.4f} then {abs(lad['rand']['mid']['price']):.4f} then "
                      f"{abs(lad['rand']['wide']['price']):.4f} at eight, sixteen and thirty-two columns",
          "verdict": "MET -- both arms' magnitudes are ordered across the two rungs, so the width's grip falls as a "
                     "ladder" if ordered["bio"] and ordered["rand"] else
                     f"FALSIFIER FIRED -- ordered {ordered} across the rungs"}
    b = {side: lad[side]["mid"]["buffer_over_anchor"] for side in ("bio", "rand")}
    bs = {side: lad[side]["mid"]["buffer_over_anchor_sigma"] for side in ("bio", "rand")}
    j5 = {"id": "DI5",
          "measured": f"at sixteen columns the buffer is {b['bio']:+.4f} ahead of {BIO} at {bs['bio']:.2f} sigma and "
                      f"{b['rand']:+.4f} ahead of {RAND} at {bs['rand']:.2f}",
          "verdict": f"MET -- the buffer is ahead of both anchors at the middle rung, {bs['bio']:.2f} and "
                     f"{bs['rand']:.2f} sigma" if (b["bio"] > 0 and bs["bio"] >= SIGMA and
                                                   b["rand"] > 0 and bs["rand"] >= SIGMA) else
                     f"FALSIFIER FIRED -- {b['bio']:+.4f} at {bs['bio']:.2f} and {b['rand']:+.4f} at {bs['rand']:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the neuron read-out at sixteen columns ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source, coupled, twenty replicates, the head reading the")
    print("   circuit's own neurons -- eight columns (`e458`, `e460`), sixteen (this unit) and thirty-two (`e455`,")
    print("   `e456`), so each arm's price is read at three widths and the pair at four heads")
    print(f"\n   {'roll':>12} {'read-out':>9} {'from world':>11} {'anchor':>15} {'arms':>34}")
    for label, roll in r["runs"].items():
        print(f"   {label:>12} {str(roll['readouts'][0] if roll['readouts'] else None):>9} "
              f"{str(roll['from_world']):>11} {roll['anchor']:>15} {','.join(sorted(roll['arms'])):>34}")
    print("\n   the width ladder, both arms read out of the circuit's own neurons:")
    print(f"      {'columns':>8} {'anchor':>15} {'standing':>10} {'sigma':>6} {'price':>10} {'sigma':>6} "
          f"{'buffer-':>10} {'sigma':>6}")
    for rung in ("narrow", "mid", "wide"):
        for side in ("bio", "rand"):
            cell = r["ladder"][side][rung]
            print(f"      {cell['width']:>8} {ANCHOR_OF[side]:>15} {cell['standing']:>+10.4f} "
                  f"{cell['standing_sigma']:>6.2f} {cell['price']:>+10.4f} {cell['price_sigma']:>6.2f} "
                  f"{cell['buffer_over_anchor']:>+10.4f} {cell['buffer_over_anchor_sigma']:>6.2f}")
    p = r["spans"]["mid"]["price"]
    ps = r["spans"]["mid"]["price_sigma"]
    gap = abs(p["bio"] - p["rand"])
    print(f"\n   the pair at the middle rung: {gap:.4f} apart ({p['bio']:+.4f} at {ps['bio']:.2f} sigma against "
          f"{p['rand']:+.4f} at {ps['rand']:.2f}), against 0.0021 at the narrow rung and 0.0208 at the wide one")
    print(f"   the shared arms against one another: " +
          ", ".join(f"{k} {v['equal']}" for k, v in r["identical"].items()))
    print("\n== the registered claims, DI1-DI5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the middle rung is here because `e461` said its own ladder is two points; this asks whether the")
    print("    width's grip on the pair's prices is ordered between them or a single jump)")
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
