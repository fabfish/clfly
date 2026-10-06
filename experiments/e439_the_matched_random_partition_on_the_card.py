"""E439 -- the matched-random partition on the card's world: whether the trade `e438` measured is the penalty's or the basis's.

`e438` put the first penalty arm on the card's world and found it **is not a buffer there**: `ewc-block` over `naive` is
**+0.0625**, **-0.0354** and **-0.1177** by position, its mean diagonal **-0.0302** below the baseline's, and it buys a
resolved **-0.0474** of forgetting for it. That unit named its own gap: `ewc-block-rand`, the size-matched random
partition that is the corpus's actual headline control, is absent, so `e438` says the *penalty* is not a buffer here and
not whether the *basis* is what makes it one.

**This unit drives that arm.** The same configuration again, `--methods naive,ewc-block-rand,replay` alone differing from
`e438`'s, at the same twenty replicates on the same as-built order, so that one run carries the matched-random arm beside
the two arms it shares with `e438` -- which are checked against it and against `e380` record for record. The basis
contrast is then paired over the twenty replicates by index, which the runner's `seed0 + 100 * r` schedule makes a
same-seed pairing. Five claims, registered before the new run's reading was opened.

- **BQ1 -- and the run is one configuration.** The three arms at **20** replicates, every recorded field agreeing with
  `e380`'s across all three runs except the output path and the arm list, the task sets equal, and the new run's two
  shared arms' replicates **bit-identical** to `e438`'s and to `e380`'s. **Falsifier**: any other field differing, an arm
  missing or short, or any shared replicate's record differing.
- **BQ2 -- and the basis contrast is a null on this world.** The paired `ewc-block`-minus-`ewc-block-rand` on the mean
  diagonal is within **0.05**. **Falsifier**: **0.10** or more; **null**: between. *This is the corpus's headline read
  again -- eleven audits left it a null on the state read-out and `e357` left it a null on the earned label -- and the
  falsifier is a resolved difference rather than an unresolved one.*
- **BQ3 -- and the matched-random arm pays the last position too.** `ewc-block-rand` minus `naive` on the last-taught
  task is at most **zero**. **Falsifier**: above **+0.05**; **null**: between.
- **BQ4 -- and the two penalty arms pay it alike.** The two arms' last-taught gains over `naive` differ by at most
  **0.05**. **Falsifier**: above **0.10**; **null**: between.
- **BQ5 -- and the matched-random arm's stability is the penalty's too.** The paired `ewc-block`-minus-`ewc-block-rand`
  on mean forgetting is within **0.05**. **Falsifier**: **0.10** or more; **null**: between.

**What it can do beyond that.** It answers which of the two things `e438` measured is a property of *anchoring* and which
of *the basis*. If both penalty arms pay the newest task and buy back the oldest, the trade is the penalty's and the card
can say so while naming a matched control rather than a basis; if the matched-random arm behaves like `replay`, then the
card's headline is about the basis after all and `e438`'s reading belongs to one arm.

**What it cannot do.** *One order*: the as-built one, so no penalty arm has a second position for any task. *And one
cell*: the card's world at twenty replicates, so the other five draws and the three streams are not in the reading.
*And the partition is one draw*: the matched-random partition is a draw of the same group sizes and not the family of
them, so a null is a null at that draw. *And an arm is not a mechanism*: that the two penalty arms read alike does not
say the penalty reaches the last position by the same route, which `e432`'s split of interference into its weight and
bias halves has not been asked of this world.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the card's world with the matched-random arm, and the two rolls it is checked against
RUNS = {
    "run": Path("runs/e439_earned_label_rand_20reps.json"),
    "penalty": Path("runs/e438_earned_label_three_arms_20reps.json"),
    "base": Path("runs/e380_earned_label_cue0_actionsource_20reps.json"),
}
ARMS = ("naive", "ewc-block", "ewc-block-rand", "replay")
NEW_ARMS = ("naive", "ewc-block-rand", "replay")
SHARED_ARMS = ("naive", "replay")
REFERENCE = "base"
ORDER = "task_order"
SHARED = ("circuit", "readout", "tasks")
DRAW_FIELDS = ("cue_sha1", "action_sha1", "world_read_sha1", "world_drive_sha1", "world_coupling_sha1")
IGNORED = ("json_out", "save_theta", "methods")
N_TASKS = 3
N_ARMS = 3
MIN_REPS = 20
LAST_BAR = 0.0
LAST_FIRES = 0.05
NULL_BAR = 0.05
NULL_FIRES = 0.10
ALIKE = 0.05
ALIKE_FIRES = 0.10
CLAIMS = (
    ("BQ1", f"and the run is one configuration, at {MIN_REPS} replicates on all three arms",
     "The three arms at twenty replicates, every recorded field agreeing with e380's across all three runs except the "
     "output path and the arm list, the task sets equal, and the new run's two shared arms' replicates bit-identical "
     "to e438's and to e380's",
     "falsifier: any other field differing, an arm missing or short, or any shared replicate's record differing"),
    ("BQ2", f"and the basis contrast is a null on this world, within {NULL_BAR:.2f}",
     "The paired ewc-block-minus-ewc-block-rand on the mean diagonal is within 0.05",
     f"falsifier: {NULL_FIRES:.2f} or more; null: between"),
    ("BQ3", "and the matched-random arm pays the last position too",
     "ewc-block-rand minus naive on the last-taught task is at most zero",
     f"falsifier: above {LAST_FIRES:+.2f}; null: between"),
    ("BQ4", "and the two penalty arms pay it alike",
     "The two arms' last-taught gains over naive differ by at most 0.05",
     f"falsifier: above {ALIKE_FIRES:.2f}; null: between"),
    ("BQ5", "and the matched-random arm's stability is the penalty's too",
     "The paired ewc-block-minus-ewc-block-rand on mean forgetting is within 0.05",
     f"falsifier: {NULL_FIRES:.2f} or more; null: between"),
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
    got = {}
    for arm in ARMS:
        if arm not in methods:
            continue
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        got[arm] = {"replicates": len(reps),
                    "final": [statistics.fmean([r["final_per_task"][k] for r in reps]) for k in range(len(tasks))],
                    "diagonal": [statistics.fmean(r["final_per_task"]) for r in reps],
                    "forgetting": [r["mean_forgetting"] for r in reps],
                    "mean_forgetting": statistics.fmean([r["mean_forgetting"] for r in reps]),
                    "records": [{"final_per_task": list(r["final_per_task"]),
                                 "mean_forgetting": r["mean_forgetting"]} for r in reps]}
    ed = doc.get("env_draw") or {}
    cfg = doc.get("config") or {}
    return {"artifact": path.name, "tasks": tasks, "arms": got, "task_order": cfg.get(ORDER),
            "shared": {k: doc.get(k) for k in SHARED}, "draws": {k: ed.get(k) for k in DRAW_FIELDS},
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
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "identical": {}, "gains": {}, "paired": {},
           "spans": {}}
    for label, path in runs.items():
        got = _roll(path)
        if got is None:
            return {**out, "ok": False, "reason": f"run {label}: {path} is absent or carries no arm"}
        out["runs"][label] = got
    run, penalty, base = out["runs"]["run"], out["runs"]["penalty"], out["runs"]["base"]
    missing = [a for a in NEW_ARMS if a not in run["arms"]]
    if missing:
        return {**out, "ok": False, "reason": f"run carries no arm for {missing}"}
    if "ewc-block" not in penalty["arms"]:
        return {**out, "ok": False, "reason": "the penalty roll carries no ewc-block arm"}
    ref = out["runs"][REFERENCE]
    #: every recorded field of every run, except the arm list and the output path
    same = {}
    fields = sorted({k for lbl in out["runs"].values() for k in lbl["config"]})
    for label, roll in out["runs"].items():
        for k in fields:
            same[f"{label}.config.{k}"] = roll["config"].get(k) == ref["config"].get(k)
        for k in DRAW_FIELDS:
            same[f"{label}.env_draw.{k}"] = roll["draws"].get(k) == ref["draws"].get(k)
        same[f"{label}.circuit"] = roll["shared"].get("circuit") == ref["shared"].get("circuit")
        same[f"{label}.readout"] = roll["shared"].get("readout") == ref["shared"].get("readout")
        same[f"{label}.tasks"] = set(roll["tasks"]) == set(ref["tasks"])
    out["same"] = same
    #: the arms each pair of rolls shares, checked replicate for replicate
    for a, b in (("run", "penalty"), ("run", "base"), ("penalty", "base")):
        for arm in SHARED_ARMS:
            if arm not in out["runs"][a]["arms"] or arm not in out["runs"][b]["arms"]:
                continue
            out["identical"][f"{a}/{b}:{arm}"] = _identical(out["runs"][a]["arms"][arm]["records"],
                                                            out["runs"][b]["arms"][arm]["records"])
    for label, source, a, b in (("ewc-naive", "penalty", "ewc-block", "naive"),
                                ("ewcrand-naive", "run", "ewc-block-rand", "naive"),
                                ("replay-naive", "penalty", "replay", "naive"),
                                ("replay-naive-run", "run", "replay", "naive"),
                                ("ewc-replay", "penalty", "ewc-block", "replay")):
        roll = out["runs"][source]
        if a not in roll["arms"] or b not in roll["arms"]:
            continue
        out["gains"][label] = [roll["arms"][a]["final"][k] - roll["arms"][b]["final"][k] for k in range(N_TASKS)]
    out["paired"] = {
        "basis-accuracy": _paired(penalty["arms"]["ewc-block"]["diagonal"], run["arms"]["ewc-block-rand"]["diagonal"]),
        "basis-forgetting": _paired(penalty["arms"]["ewc-block"]["forgetting"],
                                    run["arms"]["ewc-block-rand"]["forgetting"]),
        "replay-ewc": _paired(run["arms"]["replay"]["diagonal"], penalty["arms"]["ewc-block"]["diagonal"]),
        "diagonals": {arm: statistics.fmean(penalty["arms"][arm]["diagonal"]) if arm in penalty["arms"]
                      else statistics.fmean(run["arms"][arm]["diagonal"]) for arm in ARMS},
        "forgetting": {arm: penalty["arms"][arm]["mean_forgetting"] if arm in penalty["arms"]
                       else run["arms"][arm]["mean_forgetting"] for arm in ARMS if arm in penalty["arms"]
                       or arm in run["arms"]},
    }
    out["positions"] = {str(p): {arm: (penalty["arms"][arm]["final"][p] if arm in penalty["arms"]
                                       else run["arms"][arm]["final"][p]) for arm in ARMS if arm in penalty["arms"]
                                 or arm in run["arms"]} for p in range(N_TASKS)}
    out["readings"] = {arm: (penalty["arms"][arm]["final"] if arm in penalty["arms"] else run["arms"][arm]["final"])
                       for arm in ARMS if arm in penalty["arms"] or arm in run["arms"]}
    out["spans"] = {"replicates": sorted({v["replicates"] for roll in out["runs"].values()
                                         for v in roll["arms"].values()}),
                    "arms": {label: len(roll["arms"]) for label, roll in out["runs"].items()},
                    "same_fields": len(same),
                    "last": {k: v[-1] for k, v in out["gains"].items()},
                    "last_tasks": ref["tasks"][-1], "runs": len(out["runs"])}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no arm"} for c in CLAIMS]
    differ = sorted(k for k, v in r["same"].items() if not v)
    not_identical = sorted(k for k, v in r["identical"].items() if not v["equal"])
    thin = {f"{lbl}.{a}": v["replicates"] for lbl, roll in r["runs"].items() for a, v in roll["arms"].items()
            if v["replicates"] < MIN_REPS}
    short = {} if len(r["runs"]["run"]["arms"]) >= N_ARMS else {"run": sorted(r["runs"]["run"]["arms"])}
    j1 = {"id": "BQ1",
          "measured": f"the runs carry {r['spans']['arms']} arms at {r['spans']['replicates']} replicates over "
                      f"{r['spans']['same_fields']} compared fields, the shared arms bit-identical "
                      f"{len(r['identical']) - len(not_identical)} of {len(r['identical'])}",
          "verdict": "MET -- three arms on one configuration, every recorded field agreeing across the three rolls and "
                     "the shared arms reproducing each other replicate for replicate" if
                     (not short and not differ and not not_identical and not thin) else
                     f"FALSIFIER FIRED -- differing {differ}, not bit-identical {not_identical}, thin {thin}, "
                     f"short {short}"}
    b = r["paired"]["basis-accuracy"]
    amt = abs(b["mean"])
    j2 = {"id": "BQ2",
          "measured": f"ewc-block minus ewc-block-rand on the mean diagonal is {b['mean']:+.4f} at {abs(b['sigma']):.2f} "
                      f"sigma over {b['n']} paired replicates",
          "verdict": f"MET -- the basis contrast is a null at {amt:.4f}, unresolved at {abs(b['sigma']):.2f} sigma" if
                     amt <= NULL_BAR else
                     f"FALSIFIER FIRED -- the contrast is {amt:.4f}, at or above {NULL_FIRES:.2f}" if
                     amt >= NULL_FIRES else
                     f"NULL -- the contrast is {amt:.4f}, between {NULL_BAR:.2f} and {NULL_FIRES:.2f}"}
    last_rand = r["spans"]["last"]["ewcrand-naive"]
    j3 = {"id": "BQ3",
          "measured": f"on the last-taught task `{r['spans']['last_tasks']}` ewc-block-rand over naive is "
                      f"{last_rand:+.4f}, against ewc-block's {r['spans']['last']['ewc-naive']:+.4f} and replay's "
                      f"{r['spans']['last']['ewc-replay']:+.4f}",
          "verdict": f"MET -- the matched-random arm pays the last position too, {last_rand:+.4f}" if last_rand <= LAST_BAR
                     else f"FALSIFIER FIRED -- {last_rand:+.4f} is above the bar" if last_rand > LAST_FIRES else
                     f"NULL -- {last_rand:+.4f} between {LAST_BAR:+.2f} and {LAST_FIRES:+.2f}"}
    gap = abs(last_rand - r["spans"]["last"]["ewc-naive"])
    j4 = {"id": "BQ4",
          "measured": f"the two penalty arms' last-position costs are {last_rand:+.4f} and "
                      f"{r['spans']['last']['ewc-naive']:+.4f}, {gap:.4f} apart",
          "verdict": f"MET -- the two penalty arms pay the last position alike, {gap:.4f} apart" if gap <= ALIKE else
                     f"FALSIFIER FIRED -- the gap is {gap:.4f}" if gap > ALIKE_FIRES else
                     f"NULL -- the gap is {gap:.4f}, between {ALIKE:.2f} and {ALIKE_FIRES:.2f}"}
    f = r["paired"]["basis-forgetting"]
    amt_f = abs(f["mean"])
    j5 = {"id": "BQ5",
          "measured": f"ewc-block minus ewc-block-rand on mean forgetting is {f['mean']:+.4f} at {abs(f['sigma']):.2f} "
                      f"sigma over {f['n']} paired replicates",
          "verdict": f"MET -- the stability the penalty buys is the penalty's and not the basis's, {amt_f:.4f} apart" if
                     amt_f <= NULL_BAR else
                     f"FALSIFIER FIRED -- the forgetting contrast is {amt_f:.4f}, at or above {NULL_FIRES:.2f}" if
                     amt_f >= NULL_FIRES else
                     f"NULL -- the forgetting contrast is {amt_f:.4f}, between {NULL_BAR:.2f} and {NULL_FIRES:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the matched-random partition on the card's world ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source and the earned label, as-built order, twenty replicates")
    print(f"\n   {'arm':>15} {'diagonal by position':>34} {'mean':>8} {'forgetting':>11}")
    for arm in ARMS:
        if arm not in r["readings"]:
            continue
        print(f"   {arm:>15} " + " ".join(f"{x:+.4f}" for x in r["readings"][arm])
              + f" {r['paired']['diagonals'][arm]:+8.4f} {r['paired']['forgetting'][arm]:11.4f}")
    print("\n   the gain over naive, by position:")
    for label in ("ewc-naive", "ewcrand-naive", "replay-naive", "replay-naive-run", "ewc-replay"):
        if label in r["gains"]:
            print(f"      {label:>15}: " + " ".join(f"{x:+.4f}" for x in r["gains"][label]))
    for label in ("basis-accuracy", "basis-forgetting"):
        p = r["paired"][label]
        print(f"\n   {label:>16} paired over {p['n']} replicates: {p['mean']:+.4f} at {abs(p['sigma']):.2f} sigma")
    print(f"   the shared arms against e438 and e380: "
          + ", ".join(f"{k} {v['equal']}" for k, v in r["identical"].items()))
    print("\n== the registered claims, BQ1-BQ5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e438` found the penalty arm is not a buffer on this world and named `ewc-block-rand` as the arm it")
    print("    could not put beside it; this puts it there, so the trade can be read as the penalty's or the basis's)")
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
