"""E438 -- the penalty arm on the card's world: the first three-arm roll, and the last position's cost read for the arm that anchors.

`e380` rolled the card's world -- the closed loop at cue 0 with the action source and the earned label -- with `naive`
and `replay` at twenty replicates, and `e436` and `e437` rolled it twice more to read the order. **No unit of the corpus
has ever put a penalty arm on that world**, so the position ledger `e437` reads as *the buffer's* gain over `naive` is a
ledger of one buffer, and the corpus's own headline method contrast -- `replay` against `ewc-block`, `e276`'s twelve-sigma
result -- has never been asked on a task whose answer is read from the environment under the closed loop.

**This unit drives the third arm.** The same configuration again, `--methods naive,ewc-block,replay` alone differing from
`e380`'s, at the same twenty replicates on the same as-built order, so that one run carries all three arms and the two it
shares with `e380` can be checked against it. Five claims, registered before the new run's reading was opened.

- **BN1 -- and the run is one configuration.** The three arms at **20** replicates, every recorded field agreeing with
  `e380`'s except `json_out`, `save_theta` and the arm list, the task set equal, and the two shared arms' replicates
  **bit-identical** to `e380`'s replicate for replicate. **Falsifier**: any other field differing, an arm missing or
  short, or any shared replicate's record differing.
- **BN2 -- and the penalty arm pays the last position too.** `ewc-block` minus `naive` on the last-taught task is at most
  **zero**. **Falsifier**: above **+0.05**; **null**: between.
- **BN3 -- and the two buffers pay it alike.** The last-taught task's `ewc-block`-minus-`naive` and
  `replay`-minus-`naive` differ by at most **0.05**. **Falsifier**: above **0.10**; **null**: between.
- **BN4 -- and the buffers' advantage is the earlier positions'.** `ewc-block`'s gain over `naive` is at least **+0.05**
  at each of the first two positions. **Falsifier**: any below **+0.02**; **null**: between.
- **BN5 -- and the corpus's method contrast holds on this substrate.** `replay`'s mean diagonal exceeds `ewc-block`'s,
  paired over the twenty replicates, at **2 sigma**. **Falsifier**: the contrast resolved the other way; **null**: the
  right direction under 2 sigma.

**What it can do beyond that.** It separates what `e437`'s cliff is *of*. If `ewc-block` pays the last position too and
pays it by about what `replay` pays, then the trade the ledger measures is the stability the arm buys and not the
mechanism that buys it, and the card's order clause can say so without naming an arm. If it does not, the cliff is
`replay`'s and the card should name the arm.

**What it cannot do.** *One order*: the as-built one, so `ewc-block` has no second position for any task. *And one cell*:
the card's world at twenty replicates, so the other five draws and the three streams are not in the reading. *And three
arms*: `ewc-block-rand`, the size-matched control the corpus's headline needs, is absent. *And an arm is not a
mechanism*: that the two buffers pay alike does not say the penalty and the buffer reach the last position by the same
route.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the card's world with all three arms, and the two-arm roll it is checked against
RUNS = {
    "run": Path("runs/e438_earned_label_three_arms_20reps.json"),
    "base": Path("runs/e380_earned_label_cue0_actionsource_20reps.json"),
}
ARMS = ("naive", "ewc-block", "replay")
SHARED_ARMS = ("naive", "replay")
ORDER = "task_order"
SHARED = ("circuit", "readout", "tasks")
DRAW_FIELDS = ("cue_sha1", "action_sha1", "world_read_sha1", "world_drive_sha1", "world_coupling_sha1")
#: the three fields the arm list legitimately moves, and the two the output path moves
IGNORED = ("json_out", "save_theta", "methods")
N_TASKS = 3
N_ARMS = 3
MIN_REPS = 20
LAST_BAR = 0.0
LAST_FIRES = 0.05
ALIKE = 0.05
ALIKE_FIRES = 0.10
EARLY_BAR = 0.05
EARLY_FLOOR = 0.02
SIGMA = 2.0
CLAIMS = (
    ("BN1", f"and the run is one configuration, at {MIN_REPS} replicates on all three arms",
     "The three arms at twenty replicates, every recorded field agreeing with e380's except the output path, the "
     "saved weights and the arm list, the task set equal, and the two shared arms' replicates bit-identical to e380's",
     "falsifier: any other field differing, an arm missing or short, or any shared replicate's record differing"),
    ("BN2", "and the penalty arm pays the last position too",
     "ewc-block minus naive on the last-taught task is at most zero",
     f"falsifier: above {LAST_FIRES:+.2f}; null: between"),
    ("BN3", "and the two buffers pay it alike",
     "the last-taught task's ewc-block-minus-naive and replay-minus-naive differ by at most 0.05",
     f"falsifier: above {ALIKE_FIRES:.2f}; null: between"),
    ("BN4", "and the buffers' advantage is the earlier positions'",
     "ewc-block's gain over naive is at least +0.05 at each of the first two positions",
     f"falsifier: any below {EARLY_FLOOR:+.2f}; null: between"),
    ("BN5", "and the corpus's method contrast holds on this substrate",
     "replay's mean diagonal exceeds ewc-block's, paired over the twenty replicates, at two sigma",
     "falsifier: the contrast resolved the other way; null: the right direction under two sigma"),
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
                    "forgetting": statistics.fmean([r["mean_forgetting"] for r in reps]),
                    "records": [{"final_per_task": list(r["final_per_task"]),
                                 "mean_forgetting": r["mean_forgetting"]} for r in reps]}
    ed = doc.get("env_draw") or {}
    cfg = doc.get("config") or {}
    return {"artifact": path.name, "tasks": tasks, "arms": got, "task_order": cfg.get(ORDER),
            "shared": {k: doc.get(k) for k in SHARED}, "draws": {k: ed.get(k) for k in DRAW_FIELDS},
            "config": {k: cfg.get(k) for k in sorted(set(cfg) - set(IGNORED))}}


def _identical(a: dict, b: dict) -> dict:
    """Whether two arms' replicate records are equal one for one, and the first index where they are not."""
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
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "identical": {}, "gains": {}, "positions": {},
           "paired": {}}
    for label, path in runs.items():
        got = _roll(path)
        if got is None:
            return {**out, "ok": False, "reason": f"run {label}: {path} is absent or carries no arm"}
        out["runs"][label] = got
    run, base = out["runs"]["run"], out["runs"]["base"]
    missing = [a for a in ARMS if a not in run["arms"]]
    if missing:
        return {**out, "ok": False, "reason": f"run carries no arm for {missing}"}
    #: every recorded field of the two runs, except the arm list and the output path
    same = {}
    fields = sorted(set(run["config"]) | set(base["config"]))
    for k in fields:
        same[f"config.{k}"] = run["config"].get(k) == base["config"].get(k)
    for k in DRAW_FIELDS:
        same[f"env_draw.{k}"] = run["draws"].get(k) == base["draws"].get(k)
    same["circuit"] = run["shared"].get("circuit") == base["shared"].get("circuit")
    same["readout"] = run["shared"].get("readout") == base["shared"].get("readout")
    same["tasks"] = set(run["tasks"]) == set(base["tasks"])
    out["same"] = same
    #: the arms the two runs share, checked replicate for replicate
    for arm in SHARED_ARMS:
        if arm not in base["arms"]:
            out["identical"][arm] = {"equal": False, "n": 0, "first_differing": None, "fields": []}
            continue
        out["identical"][arm] = _identical(run["arms"][arm]["records"], base["arms"][arm]["records"])
    for label, pair in (("replay-naive", ("replay", "naive")), ("ewc-naive", ("ewc-block", "naive")),
                        ("ewc-replay", ("ewc-block", "replay"))):
        out["gains"][label] = [run["arms"][pair[0]]["final"][k] - run["arms"][pair[1]]["final"][k]
                               for k in range(N_TASKS)]
    out["positions"] = {str(p): {arm: run["arms"][arm]["final"][p] for arm in ARMS} for p in range(N_TASKS)}
    out["paired"] = {arm: {"diagonal": run["arms"][arm]["diagonal"], "mean": run["arms"][arm]["final"],
                           "forgetting": run["arms"][arm]["forgetting"]} for arm in ARMS}
    out["paired"]["replay-minus-ewc-block"] = _paired(run["arms"]["replay"]["diagonal"],
                                                      run["arms"]["ewc-block"]["diagonal"])
    out["spans"] = {"replicates": sorted({run["arms"][a]["replicates"] for a in run["arms"]}),
                    "arms": len(run["arms"]), "same_fields": len(same),
                    "last": {label: out["gains"][label][-1] for label in out["gains"]},
                    "early": {label: out["gains"][label][:-1] for label in ("replay-naive", "ewc-naive")},
                    "last_tasks": run["tasks"][-1], "first_tasks": run["tasks"][0]}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a run is absent or carries no arm"} for c in CLAIMS]
    differ = sorted(k for k, v in r["same"].items() if not v)
    not_identical = {a: v for a, v in r["identical"].items() if not v["equal"]}
    thin = {a: v["replicates"] for a, v in r["runs"]["run"]["arms"].items() if v["replicates"] < MIN_REPS}
    arms_ok = len(r["runs"]["run"]["arms"]) >= N_ARMS
    j1 = {"id": "BN1",
          "measured": f"{len(r['runs']['run']['arms'])} arms at {r['spans']['replicates']} replicates over "
                      f"{r['spans']['same_fields']} compared fields, the shared arms bit-identical "
                      f"{ {a: v['equal'] for a, v in r['identical'].items()} }",
          "verdict": "MET -- the run carries all three arms, every recorded field agrees with e380's, and the two "
                     "shared arms reproduce it replicate for replicate" if
                     (arms_ok and not differ and not not_identical and not thin) else
                     f"FALSIFIER FIRED -- differing {differ}, not bit-identical {not_identical}, thin {thin}"}
    last = {k: round(v, 4) for k, v in r["spans"]["last"].items()}
    ewc_last = r["spans"]["last"]["ewc-naive"]
    j2 = {"id": "BN2",
          "measured": f"on the last-taught task `{r['spans']['last_tasks']}` ewc-block over naive is {ewc_last:+.4f}, "
                      f"against replay's {r['spans']['last']['replay-naive']:+.4f}",
          "verdict": f"MET -- the penalty arm pays the last position too, {ewc_last:+.4f}" if ewc_last <= LAST_BAR else
                     f"FALSIFIER FIRED -- {ewc_last:+.4f} is above the bar" if ewc_last > LAST_FIRES else
                     f"NULL -- {ewc_last:+.4f} between {LAST_BAR:+.2f} and {LAST_FIRES:+.2f}"}
    gap = abs(r["spans"]["last"]["ewc-naive"] - r["spans"]["last"]["replay-naive"])
    j3 = {"id": "BN3",
          "measured": f"the last position's two buffer gains are {ewc_last:+.4f} and "
                      f"{r['spans']['last']['replay-naive']:+.4f}, {gap:.4f} apart",
          "verdict": f"MET -- the two buffers pay the last position alike, {gap:.4f} apart" if gap <= ALIKE else
                     f"FALSIFIER FIRED -- the gap is {gap:.4f}" if gap > ALIKE_FIRES else
                     f"NULL -- the gap is {gap:.4f}, between {ALIKE:.2f} and {ALIKE_FIRES:.2f}"}
    early = [round(x, 4) for x in r["spans"]["early"]["ewc-naive"]]
    under = [x for x in early if x < EARLY_BAR]
    j4 = {"id": "BN4",
          "measured": f"ewc-block over naive at the first two positions is {early}, against replay's "
                      f"{[round(x, 4) for x in r['spans']['early']['replay-naive']]}",
          "verdict": f"MET -- the penalty arm's advantage is the earlier positions', {early}" if not under else
                     f"FALSIFIER FIRED -- {under} is below the bar" if any(x < EARLY_FLOOR for x in under) else
                     f"NULL -- {under} between {EARLY_FLOOR:+.2f} and {EARLY_BAR:+.2f}"}
    p = r["paired"]["replay-minus-ewc-block"]
    j5 = {"id": "BN5",
          "measured": f"replay minus ewc-block on the mean diagonal is {p['mean']:+.4f} at {abs(p['sigma']):.2f} "
                      f"sigma over {p['n']} paired replicates",
          "verdict": "MET -- replay is ahead of the penalty on the card's own world at two sigma" if
                     (p["mean"] > 0 and abs(p["sigma"]) >= SIGMA) else
                     "FALSIFIER FIRED -- the contrast resolves the other way" if (p["mean"] < 0 and abs(p["sigma"]) >= SIGMA)
                     else f"NULL -- the contrast is unresolved at {abs(p['sigma']):.2f} sigma"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the penalty arm on the card's world ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source and the earned label, as-built order, twenty replicates")
    run = r["runs"]["run"]
    print(f"\n   {'arm':>12} {'diagonal by position':>34} {'mean':>8} {'forgetting':>11}")
    for arm in ARMS:
        a = run["arms"][arm]
        print(f"   {arm:>12} " + " ".join(f"{x:+.4f}" for x in a["final"]) + f" {statistics.fmean(a['final']):+8.4f} "
              f"{a['forgetting']:11.4f}")
    print("\n   the gain over naive, by position:")
    for label in ("replay-naive", "ewc-naive", "ewc-replay"):
        print(f"      {label:>12}: " + " ".join(f"{x:+.4f}" for x in r["gains"][label]))
    p = r["paired"]["replay-minus-ewc-block"]
    print(f"\n   replay minus ewc-block, paired over {p['n']} replicates: {p['mean']:+.4f} at {abs(p['sigma']):.2f} sigma")
    print(f"   the shared arms against e380: " +
          ", ".join(f"{a} {v['equal']}" for a, v in r["identical"].items()))
    print("\n== the registered claims, BN1-BN5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e437` read the buffer's gain over `naive` on this world under three orders; this puts the penalty")
    print("    arm on it, so the ledger's cliff can be read for an arm that anchors rather than for one buffer)")
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
