"""E463 -- the neuron read-out at twenty-four columns: the rung between the two the parting was left between.

`e462` read the card's world's neuron head at **sixteen** columns and found the pair's prices still agreeing there
(**0.0010** apart) while they separate at thirty-two (**0.0208**), and it found the two arms moving together from eight
to sixteen (**0.0209** and **0.0198**) and parting from sixteen to thirty-two (**0.0291** against **0.0073**). **So the
parting is somewhere in the second half of the ladder and two rungs do not say where.** It also found the pair's
**standings** running a clean monotone ladder in the width -- their gap **0.0288**, **0.0173** then **0.0083** at eight,
sixteen and thirty-two -- and one monotone run of three is not a trend.

**This unit drives the rung between them.** Two rolls of `e462`'s configuration at **twenty-four** columns -- the
biological arm and the matched-random arm, twenty replicates each, `--readout-from-world` omitted -- so the price
ladder has a fourth point between sixteen and thirty-two and the standing gap a fourth value to be ordered against its
neighbours. **Twenty-four is the geometric midpoint of sixteen and thirty-two** (their mean in the log of the width is
**22.6**), which is where a gap linear in the log of the width would put a quarter of the way from **0.0173** toward
**0.0083**. Five claims, registered before either new roll's reading was opened.

- **DJ1 -- and the two rolls are one configuration at the new rung with the arm list moved.** Three arms each at
  **20** replicates, every recorded config field agreeing between the two rolls except `methods`, the output path and the
  saved weights, the read-out **24** and not the world's, the three task names equal, and the two rolls' `naive` and
  `replay` replicates **bit-identical** to one another. **Falsifier**: any other config field differing, an arm missing
  or short, a read-out that is the world's or another width, or any shared replicate differing.
- **DJ2 -- and both anchors' prices resolve at the new rung.** Each arm's cost at the last-taught task is negative at
  **two** sigma or more. **Falsifier**: either arm not negative, or under two sigma.
- **DJ3 -- and the pair's prices still agree at the new rung.** The two arms' newest-task costs differ by at most
  **0.05**. **Falsifier**: **0.10** or more apart; **null**: between. *If they separate here, the parting begins between
  sixteen and twenty-four rather than between twenty-four and thirty-two.*
- **DJ4 -- and the price magnitude ladder holds at the new rung for both arms.** For each arm the price's magnitude at
  twenty-four columns is at or below its sixteen-column value and at or above its thirty-two column value.
  **Falsifier**: for either arm the twenty-four column magnitude above its sixteen-column one, or below its
  thirty-two column one.
- **DJ5 -- and the pair's standing gap is ordered at the new rung.** It is at most its sixteen-column value and at least
  its thirty-two column value. **Falsifier**: above the sixteen-column gap, or below the thirty-two column one.

**What it can do beyond that.** It makes the price ladder four points and the standing ladder four values, so
`e462`'s monotone run of three is either extended or broken at a rung that sits inside the interval the parting was
bracketed to, and it says whether the two arms' prices part at a threshold in the width or as a smooth fall.

**What it cannot do.** *Four widths are not a mechanism*, and the dial also moves the head's parameter count, so a
four-point ladder is a shape and not a cause. *And one cell each*: the card's world at twenty replicates, so a gap at
the third decimal place is what a redraw could move. *And one partition draw*: the matched-random cells are one draw of
the same group sizes and not the family of them. *And the source's axis stays one rung*: the world's own state is only
constructible at eight columns, so the whole ladder is the circuit's neurons.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the two new rolls at twenty-four columns and the six rolls the ladder is read against, by width and anchor
RUNS = {
    "8/bio": Path("runs/e458_earned_label_neurons8_20reps.json"),
    "8/rand": Path("runs/e460_earned_label_rand_neurons8_20reps.json"),
    "16/bio": Path("runs/e462_earned_label_neurons16_20reps.json"),
    "16/rand": Path("runs/e462_earned_label_rand_neurons16_20reps.json"),
    "24/bio": Path("runs/e463_earned_label_neurons24_20reps.json"),
    "24/rand": Path("runs/e463_earned_label_rand_neurons24_20reps.json"),
    "32/bio": Path("runs/e455_earned_label_neurons_20reps.json"),
    "32/rand": Path("runs/e456_earned_label_rand_neurons_20reps.json"),
}
#: the four rungs, the new one, and the two it is ordered against. The rungs are **strings**, because the ladder is
#: keyed by them and a reading written as JSON comes back with its keys stringified -- an integer key would be a
#: `KeyError` on the artifact and a silent one in memory, so the reader, the artifact and the judge agree on the text
RUNGS = ("8", "16", "24", "32")
NEW_WIDTH = 24
BELOW = 16
ABOVE = 32
#: the same three as the ladder's keys
NEWK, BELOWK, ABOVEK = str(NEW_WIDTH), str(BELOW), str(ABOVE)
ANCHOR_OF = {"bio": "ewc-block", "rand": "ewc-block-rand"}
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
    ("DJ1", f"and the two rolls are one configuration at the new rung with the arm list moved, at {MIN_REPS} replicates",
     "Three arms each at twenty replicates, every recorded config field agreeing between the two rolls except methods, "
     "the output path and the saved weights, the read-out 24 and not the world's, the three task names equal, and the "
     "two rolls' naive and replay bit-identical to one another",
     "falsifier: any other config field differing, an arm missing or short, a read-out that is the world's or another "
     "width, or any shared replicate differing"),
    ("DJ2", f"and both anchors' prices resolve at the new rung, at {SIGMA:.0f} sigma",
     "Each arm's cost at the last-taught task is negative at two sigma or more",
     "falsifier: either arm not negative, or under two sigma"),
    ("DJ3", f"and the pair's prices still agree at the new rung, within {ALIKE:.2f}",
     "The two arms' newest-task costs differ by at most 0.05",
     f"falsifier: {ALIKE_FIRES:.2f} or more apart; null: between"),
    ("DJ4", "and the price magnitude ladder holds at the new rung for both arms",
     "For each arm the price's magnitude at twenty-four columns is at or below its sixteen-column value and at or above "
     "its thirty-two column value",
     "falsifier: for either arm the twenty-four column magnitude above its sixteen-column one, or below its "
     "thirty-two column one"),
    ("DJ5", "and the pair's standing gap is ordered at the new rung",
     "The gap at twenty-four columns is at most its sixteen-column value and at least its thirty-two column value",
     "falsifier: above the sixteen-column gap, or below the thirty-two column one"),
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
           "ladder": {}, "gaps": {}, "spans": {}}
    for label, path in runs.items():
        anchor = ANCHOR_OF[label.split("/")[1]]
        got = _roll(path, anchor)
        if got is None:
            return {**out, "ok": False, "reason": f"roll {label}: {path} is absent or carries no {anchor} arm"}
        out["runs"][label] = got
    new_bio, new_rand = out["runs"][f"{NEW_WIDTH}/bio"], out["runs"][f"{NEW_WIDTH}/rand"]
    same = {}
    fields = sorted(set(new_bio["config"]) | set(new_rand["config"]))
    for k in fields:
        same[f"config.{k}"] = new_bio["config"].get(k) == new_rand["config"].get(k)
    same["circuit"] = new_bio["shared"].get("circuit") == new_rand["shared"].get("circuit")
    same["tasks"] = new_bio["shared"].get("tasks") == new_rand["shared"].get("tasks")
    out["same"] = same
    out["readouts"] = {label: {"readouts": roll["readouts"], "from_world": roll["from_world"]}
                       for label, roll in out["runs"].items()}
    for arm in SHARED_ARMS:
        out["identical"][f"new:bio-rand/{arm}"] = _identical(new_bio["arms"][arm]["records"],
                                                            new_rand["arms"][arm]["records"])
    for label, roll in out["runs"].items():
        out["contrasts"][label] = {
            "anchor_over_naive": _paired(roll["arms"][roll["anchor"]]["diagonal"],
                                         roll["arms"][BASELINE]["diagonal"]),
            "anchor_last": _paired(roll["arms"][roll["anchor"]]["last"], roll["arms"][BASELINE]["last"]),
            "buffer_over_anchor": _paired(roll["arms"][BUFFER]["diagonal"],
                                          roll["arms"][roll["anchor"]]["diagonal"]),
        }
    for side in ("bio", "rand"):
        out["ladder"][side] = {w: {"width": int(w),
                                   "standing": out["contrasts"][f"{w}/{side}"]["anchor_over_naive"]["mean"],
                                   "standing_sigma":
                                       abs(out["contrasts"][f"{w}/{side}"]["anchor_over_naive"]["sigma"]),
                                   "price": out["contrasts"][f"{w}/{side}"]["anchor_last"]["mean"],
                                   "price_sigma": abs(out["contrasts"][f"{w}/{side}"]["anchor_last"]["sigma"]),
                                   "buffer_over_anchor":
                                       out["contrasts"][f"{w}/{side}"]["buffer_over_anchor"]["mean"],
                                   "buffer_over_anchor_sigma":
                                       abs(out["contrasts"][f"{w}/{side}"]["buffer_over_anchor"]["sigma"])}
                               for w in RUNGS}
    out["gaps"] = {w: {"price": abs(out["ladder"]["bio"][w]["price"] - out["ladder"]["rand"][w]["price"]),
                       "standing": abs(out["ladder"]["bio"][w]["standing"] - out["ladder"]["rand"][w]["standing"])}
                   for w in RUNGS}
    out["spans"] = {"replicates": sorted({v["replicates"] for roll in out["runs"].values()
                                         for v in roll["arms"].values()}),
                    "arms": {label: len(roll["arms"]) for label, roll in out["runs"].items()},
                    "same_fields": len(same),
                    "readout": {"new_bio": (new_bio["readouts"] or [None])[0],
                                "new_rand": (new_rand["readouts"] or [None])[0],
                                "from_world": {label: roll["from_world"] for label, roll in out["runs"].items()}},
                    "new": {"standing": {side: out["ladder"][side][NEWK]["standing"] for side in ("bio", "rand")},
                            "standing_sigma": {side: out["ladder"][side][NEWK]["standing_sigma"]
                                               for side in ("bio", "rand")},
                            "price": {side: out["ladder"][side][NEWK]["price"] for side in ("bio", "rand")},
                            "price_sigma": {side: out["ladder"][side][NEWK]["price_sigma"]
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
    reads_ok = (ro["new_bio"] == NEW_WIDTH and ro["new_rand"] == NEW_WIDTH and
                ro["from_world"][f"{NEW_WIDTH}/bio"] is False and
                ro["from_world"][f"{NEW_WIDTH}/rand"] is False and
                all(x == NEW_WIDTH for x in r["runs"][f"{NEW_WIDTH}/bio"]["readouts"]) and
                all(x == NEW_WIDTH for x in r["runs"][f"{NEW_WIDTH}/rand"]["readouts"]))
    j1 = {"id": "DJ1",
          "measured": f"the two new rolls carry {len(r['runs'][f'{NEW_WIDTH}/bio']['arms'])} and "
                      f"{len(r['runs'][f'{NEW_WIDTH}/rand']['arms'])} arms at {r['spans']['replicates']} replicates "
                      f"over {r['spans']['same_fields']} compared fields, the read-out {ro['new_bio']} and "
                      f"{ro['new_rand']}, from the world "
                      f"{ {k: v for k, v in ro['from_world'].items()} }, the shared arms bit-identical "
                      f"{len(r['identical']) - len(not_identical)} of {len(r['identical'])}",
          "verdict": f"MET -- one configuration at {NEW_WIDTH} neuron columns with the arm list moved, and the two "
                     "shared arms reproducing one another" if
                     (not short and not differ and not not_identical and reads_ok and not thin) else
                     f"FALSIFIER FIRED -- differing {differ}, not bit-identical {not_identical}, read-outs {ro}, "
                     f"thin {thin}, short {short}"}
    p = r["spans"]["new"]["price"]
    ps = r["spans"]["new"]["price_sigma"]
    j2 = {"id": "DJ2",
          "measured": f"at {NEW_WIDTH} neuron columns the two anchors' newest-task costs are {BIO} {p['bio']:+.4f} at "
                      f"{ps['bio']:.2f} sigma and {RAND} {p['rand']:+.4f} at {ps['rand']:.2f}",
          "verdict": f"MET -- both prices resolve at the new rung, {ps['bio']:.2f} and {ps['rand']:.2f} sigma" if
                     (p["bio"] < 0 and ps["bio"] >= SIGMA and p["rand"] < 0 and ps["rand"] >= SIGMA) else
                     f"FALSIFIER FIRED -- {BIO} {p['bio']:+.4f} at {ps['bio']:.2f} and {RAND} {p['rand']:+.4f} at "
                     f"{ps['rand']:.2f}"}
    g = r["gaps"][NEWK]["price"]
    j3 = {"id": "DJ3",
          "measured": f"the pair's newest-task costs at {NEW_WIDTH} columns are {p['bio']:+.4f} and {p['rand']:+.4f}, "
                      f"{g:.4f} apart, against {r['gaps'][BELOWK]['price']:.4f} at {BELOW} columns and "
                      f"{r['gaps'][ABOVEK]['price']:.4f} at {ABOVE}",
          "verdict": f"MET -- the pair's prices still agree at the new rung, {g:.4f} apart" if g <= ALIKE else
                     f"FALSIFIER FIRED -- the gap is {g:.4f}" if g >= ALIKE_FIRES else
                     f"NULL -- the gap is {g:.4f}, between {ALIKE:.2f} and {ALIKE_FIRES:.2f}"}
    lad = r["ladder"]
    ordered = {side: (abs(lad[side][NEWK]["price"]) <= abs(lad[side][BELOWK]["price"]) and
                      abs(lad[side][NEWK]["price"]) >= abs(lad[side][ABOVEK]["price"])) for side in ("bio", "rand")}
    j4 = {"id": "DJ4",
          "measured": f"the price's magnitudes run {BIO} {abs(lad['bio'][BELOWK]['price']):.4f} then "
                      f"{abs(lad['bio'][NEWK]['price']):.4f} then {abs(lad['bio'][ABOVEK]['price']):.4f}, and {RAND} "
                      f"{abs(lad['rand'][BELOWK]['price']):.4f} then {abs(lad['rand'][NEWK]['price']):.4f} then "
                      f"{abs(lad['rand'][ABOVEK]['price']):.4f} at {BELOW}, {NEW_WIDTH} and {ABOVE} columns",
          "verdict": "MET -- both arms' magnitudes are ordered at the new rung, so the ladder is four points" if
                     ordered["bio"] and ordered["rand"] else
                     f"FALSIFIER FIRED -- ordered {ordered} at the new rung"}
    sg = r["gaps"][NEWK]["standing"]
    ordered_gap = (sg <= r["gaps"][BELOWK]["standing"] and sg >= r["gaps"][ABOVEK]["standing"])
    j5 = {"id": "DJ5",
          "measured": f"the pair's standing gaps run {r['gaps'][RUNGS[0]]['standing']:.4f}, "
                      f"{r['gaps'][BELOWK]['standing']:.4f}, {sg:.4f} and {r['gaps'][ABOVEK]['standing']:.4f} at "
                      f"{', '.join(RUNGS)} columns",
          "verdict": "MET -- the standing gap is ordered at the new rung, so the ladder survives a fourth point" if
                     ordered_gap else
                     f"FALSIFIER FIRED -- the gap at {NEW_WIDTH} columns is not between its neighbours' values"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the neuron read-out at twenty-four columns ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source, coupled, twenty replicates, the head reading the")
    print("   circuit's own neurons at eight, sixteen, twenty-four and thirty-two columns, so the price ladder has a")
    print("   fourth point inside the interval `e462` left the parting in")
    print(f"\n   {'roll':>8} {'read-out':>9} {'from world':>11} {'anchor':>15} {'arms':>34}")
    for label, roll in r["runs"].items():
        print(f"   {label:>8} {str(roll['readouts'][0] if roll['readouts'] else None):>9} "
              f"{str(roll['from_world']):>11} {roll['anchor']:>15} {','.join(sorted(roll['arms'])):>34}")
    print("\n   the width ladder, both arms read out of the circuit's own neurons:")
    print(f"      {'columns':>8} {'anchor':>15} {'standing':>10} {'sigma':>6} {'price':>10} {'sigma':>6} "
          f"{'buffer-':>10} {'sigma':>6}")
    for w in RUNGS:
        for side in ("bio", "rand"):
            cell = r["ladder"][side][w]
            print(f"      {w:>8} {ANCHOR_OF[side]:>15} {cell['standing']:>+10.4f} {cell['standing_sigma']:>6.2f} "
                  f"{cell['price']:>+10.4f} {cell['price_sigma']:>6.2f} {cell['buffer_over_anchor']:>+10.4f} "
                  f"{cell['buffer_over_anchor_sigma']:>6.2f}")
    print("\n   the pair apart by rung:")
    print(f"      {'columns':>8} {'standing gap':>13} {'price gap':>10}")
    for w in RUNGS:
        print(f"      {w:>8} {r['gaps'][w]['standing']:>13.4f} {r['gaps'][w]['price']:>10.4f}")
    print(f"\n   the shared arms against one another: " +
          ", ".join(f"{k} {v['equal']}" for k, v in r["identical"].items()))
    print("\n== the registered claims, DJ1-DJ5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print(f"\n   (twenty-four is the geometric midpoint of sixteen and thirty-two, so a standing gap linear in the log")
    print("    of the width would sit about a quarter of the way from the sixteen-column value toward the thirty-two)")
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
