"""E447 -- the two anchors at another position: whether the price `e446` found is the penalty's or the basis's.

`e439` put the size-matched random partition on the card's world beside the biological one and found the two **0.0063**
apart on the mean diagonal and **0.0042** apart at the newest task, so the trade `e438` measured is the penalty's and not
the basis's. `e446` then moved the anchor to the **reversed** order and found its newest-task price is the position's and
not the task's -- **-0.0917** at **3.38** sigma with `loop_odour_identity` last against **-0.1177** at **3.71** with
`loop_odour_input` last. **Both of those readings are about one anchor each**, and neither has been put beside the other
at a second position.

**This unit drives the matched-random arm under the reversed order.** `e446`'s configuration with
`--methods naive,ewc-block-rand,replay` alone differing, at the same twenty replicates and the same order, so the basis
contrast -- `ewc-block` against its size-matched random partition, paired over the replicates -- can be read where the
position's price is known and the price can be read for the second anchor. `e446`'s roll is the biological arm's at that
order and the two arms this run shares with it are the control. Five claims, registered before the new run's reading was
opened.

- **BY1 -- and the run is one configuration under the reversed order.** The three arms at **20** replicates, every
  recorded field agreeing with `e438`'s except `task_order`, `methods`, the output path and the saved weights, the new
  suite the as-built suite **reversed**, and the new run's `naive` and `replay` replicates **bit-identical** to
  `e446`'s roll, which shares this run's order. **Falsifier**: any other field differing, an arm missing or short, a
  suite that is not the reversal, or any shared replicate's record differing.
- **BY2 -- and the matched-random arm pays the newest task here too.** `ewc-block-rand` minus `naive` on the last-taught
  task is at most **zero**. **Falsifier**: above **+0.05**; **null**: between.
- **BY3 -- and it pays about what the biological arm pays.** The two anchors' newest-task costs under this order differ
  by at most **0.05**. **Falsifier**: **0.10** or more apart; **null**: between. *`e439` read this pair as-built and
  found them **0.0042** apart; this asks it where the position's price is known.*
- **BY4 -- and the basis contrast on the mean diagonal is a null here.** The paired `ewc-block`-minus-`ewc-block-rand`
  on the mean diagonal is within **0.05**. **Falsifier**: **0.10** or more; **null**: between. *The corpus's headline
  pair, eleven audits a null on the state read-out and `e357` and `e439` nulls elsewhere.*
- **BY5 -- and neither anchor's standing resolves.** On this order each anchor's mean diagonal over the baseline is
  under **two** sigma. **Falsifier**: either at or above two sigma.

**What it can do beyond that.** It puts the two halves of the card's own account of the anchor together: `e446` said the
price is the position's, `e439` said the trade is the penalty's, and this asks both at once. If the matched-random arm
pays the newest task about what the biological one pays and neither standing resolves, then the card's ledger clause is
about **anchoring** and a reader may carry it without naming an arm or a basis; if the two arms separate here, then the
position's price is the biological basis's after all and the clause should name it.

**What it cannot do.** *One more order* of the suite's six, and the second position the price is asked at, so the
position's price has three of its points at `loop_odour_input` and two at `loop_odour_identity`. *And one cell*: the
card's world at twenty replicates, so the other five draws and the three streams are not in the reading. *And one
partition draw*: the matched-random partition is a draw of the same group sizes and not the family of them. *And the two
rolls are two runs*: the basis contrast pairs replicate against replicate by the runner's `seed0 + 100 * r` schedule,
which is a same-seed pairing and not the same run.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the matched-random arm under the reversed order, the biological arm's roll at that order, and the card's own roll
RUNS = {
    "new": Path("runs/e447_earned_label_rand_reverse_20reps.json"),
    "biological": Path("runs/e446_earned_label_anchor_reverse_20reps.json"),
    "card": Path("runs/e438_earned_label_three_arms_20reps.json"),
}
ARMS = ("naive", "ewc-block", "ewc-block-rand", "replay")
RAND = "ewc-block-rand"
BIO = "ewc-block"
BASELINE = "naive"
BUFFER = "replay"
SHARED_ARMS = ("naive", "replay")
ORDER = "task_order"
SHARED = ("circuit", "readout", "tasks")
DRAW_FIELDS = ("cue_sha1", "action_sha1", "world_read_sha1", "world_drive_sha1", "world_coupling_sha1")
IGNORED = ("json_out", "save_theta", "methods", ORDER)
N_TASKS = 3
N_ARMS = 3
MIN_REPS = 20
LAST_BAR = 0.0
LAST_FIRES = 0.05
ALIKE = 0.05
ALIKE_FIRES = 0.10
SIGMA = 2.0
#: the as-built pair `e439` read, which BY3 and BY4 are registered against
AS_BUILT_LAST_GAP = 0.0042
AS_BUILT_BASIS = 0.0063
CLAIMS = (
    ("BY1", f"and the run is one configuration under the reversed order, at {MIN_REPS} replicates",
     "The three arms at twenty replicates, every recorded field agreeing with e438's except task_order, methods, the "
     "output path and the saved weights, the new suite the as-built suite reversed, and the new run's naive and replay "
     "bit-identical to e446's roll",
     "falsifier: any other field differing, an arm missing or short, a suite that is not the reversal, or any shared "
     "replicate's record differing"),
    ("BY2", "and the matched-random arm pays the newest task here too",
     "ewc-block-rand minus naive on the last-taught task is at most zero",
     f"falsifier: above {LAST_FIRES:+.2f}; null: between"),
    ("BY3", f"and it pays about what the biological arm pays, within {ALIKE:.2f}",
     "The two anchors' newest-task costs under this order differ by at most 0.05",
     f"falsifier: {ALIKE_FIRES:.2f} or more apart; null: between"),
    ("BY4", f"and the basis contrast on the mean diagonal is a null here, within {ALIKE:.2f}",
     "The paired ewc-block-minus-ewc-block-rand on the mean diagonal is within 0.05",
     f"falsifier: {ALIKE_FIRES:.2f} or more; null: between"),
    ("BY5", f"and neither anchor's standing resolves, under {SIGMA:.0f} sigma",
     "On this order each anchor's mean diagonal over the baseline is under two sigma",
     "falsifier: either at or above two sigma"),
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
    new, bio, card = out["runs"]["new"], out["runs"]["biological"], out["runs"]["card"]
    missing = [a for a in (BASELINE, RAND, BUFFER) if a not in new["arms"]]
    if missing:
        return {**out, "ok": False, "reason": f"the new roll carries no arm for {missing}"}
    if BIO not in bio["arms"] or BASELINE not in bio["arms"]:
        return {**out, "ok": False, "reason": "the biological arm's roll carries no anchor or no baseline"}
    same = {}
    fields = sorted(set(new["config"]) | set(card["config"]))
    for k in fields:
        same[f"config.{k}"] = new["config"].get(k) == card["config"].get(k)
    for k in DRAW_FIELDS:
        same[f"env_draw.{k}"] = new["draws"].get(k) == card["draws"].get(k)
    same["circuit"] = new["shared"].get("circuit") == card["shared"].get("circuit")
    same["readout"] = new["shared"].get("readout") == card["shared"].get("readout")
    same["tasks"] = set(new["tasks"]) == set(card["tasks"])
    out["same"] = same
    out["reversed"] = {"new": new["tasks"], "card": card["tasks"],
                       "is_the_reversal": list(reversed(card["tasks"])) == list(new["tasks"]),
                       "orders": {label: roll["task_order"] for label, roll in out["runs"].items()}}
    for arm in SHARED_ARMS:
        if arm not in bio["arms"]:
            out["identical"][f"new/biological:{arm}"] = {"equal": False, "n": 0, "first_differing": None, "fields": []}
            continue
        out["identical"][f"new/biological:{arm}"] = _identical(new["arms"][arm]["records"],
                                                               bio["arms"][arm]["records"])
    out["contrasts"] = {
        "rand_over_naive": _paired(new["arms"][RAND]["diagonal"], new["arms"][BASELINE]["diagonal"]),
        "rand_last": _paired(new["arms"][RAND]["last"], new["arms"][BASELINE]["last"]),
        "bio_over_naive": _paired(bio["arms"][BIO]["diagonal"], bio["arms"][BASELINE]["diagonal"]),
        "bio_last": _paired(bio["arms"][BIO]["last"], bio["arms"][BASELINE]["last"]),
        "basis_accuracy": _paired(bio["arms"][BIO]["diagonal"], new["arms"][RAND]["diagonal"]),
        "basis_forgetting": _paired([r["mean_forgetting"] for r in bio["arms"][BIO]["records"]],
                                    [r["mean_forgetting"] for r in new["arms"][RAND]["records"]]),
    }
    for label, roll in (("new", new), ("biological", bio)):
        if BUFFER in roll["arms"]:
            out["contrasts"][f"buffer_gain_{label}"] = [
                roll["arms"][BUFFER]["final"][k] - roll["arms"][BASELINE]["final"][k] for k in range(N_TASKS)]
    out["spans"] = {"replicates": sorted({v["replicates"] for roll in out["runs"].values()
                                         for v in roll["arms"].values()}),
                    "arms": {label: len(roll["arms"]) for label, roll in out["runs"].items()},
                    "same_fields": len(same), "orders": out["reversed"]["orders"],
                    "last": {"rand": out["contrasts"]["rand_last"]["mean"], "bio": out["contrasts"]["bio_last"]["mean"],
                             "rand_sigma": out["contrasts"]["rand_last"]["sigma"],
                             "bio_sigma": out["contrasts"]["bio_last"]["sigma"],
                             "last_task": new["tasks"][-1]},
                    "standing": {"rand": out["contrasts"]["rand_over_naive"]["mean"],
                                 "rand_sigma": out["contrasts"]["rand_over_naive"]["sigma"],
                                 "bio": out["contrasts"]["bio_over_naive"]["mean"],
                                 "bio_sigma": out["contrasts"]["bio_over_naive"]["sigma"]},
                    "as_built_last_gap": AS_BUILT_LAST_GAP, "as_built_basis": AS_BUILT_BASIS}
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
    j1 = {"id": "BY1",
          "measured": f"the new roll carries {len(r['runs']['new']['arms'])} arms at {r['spans']['replicates']} "
                      f"replicates over {r['spans']['same_fields']} compared fields, the orders {r['spans']['orders']}, "
                      f"the suite the as-built one reversed {reversed_ok}, the shared arms bit-identical "
                      f"{len(r['identical']) - len(not_identical)} of {len(r['identical'])}",
          "verdict": "MET -- one configuration under the reversed order, the suite the as-built one reversed, and the "
                     "two shared arms reproducing the biological arm's roll at that order" if
                     (not short and not differ and not not_identical and reversed_ok and not thin) else
                     f"FALSIFIER FIRED -- differing {differ}, not bit-identical {not_identical}, reversal "
                     f"{reversed_ok}, thin {thin}, short {short}"}
    last_rand = r["spans"]["last"]["rand"]
    last_bio = r["spans"]["last"]["bio"]
    j2 = {"id": "BY2",
          "measured": f"with `{r['spans']['last']['last_task']}` last, {RAND} over {BASELINE} is {last_rand:+.4f} at "
                      f"{abs(r['spans']['last']['rand_sigma']):.2f} sigma, against {BIO}'s {last_bio:+.4f} at "
                      f"{abs(r['spans']['last']['bio_sigma']):.2f}",
          "verdict": f"MET -- the matched-random arm pays the newest task here too, {last_rand:+.4f}" if
                     last_rand <= LAST_BAR else
                     f"FALSIFIER FIRED -- {last_rand:+.4f} is above the bar" if last_rand > LAST_FIRES else
                     f"NULL -- {last_rand:+.4f} between {LAST_BAR:+.2f} and {LAST_FIRES:+.2f}"}
    gap = abs(last_rand - last_bio)
    j3 = {"id": "BY3",
          "measured": f"the two anchors' newest-task costs are {last_rand:+.4f} and {last_bio:+.4f}, {gap:.4f} apart, "
                      f"against the as-built pair's {AS_BUILT_LAST_GAP:.4f}",
          "verdict": f"MET -- the two anchors pay the newest task alike here, {gap:.4f} apart" if gap <= ALIKE else
                     f"FALSIFIER FIRED -- the gap is {gap:.4f}" if gap >= ALIKE_FIRES else
                     f"NULL -- the gap is {gap:.4f}, between {ALIKE:.2f} and {ALIKE_FIRES:.2f}"}
    b = r["contrasts"]["basis_accuracy"]
    amt = abs(b["mean"])
    j4 = {"id": "BY4",
          "measured": f"{BIO} minus {RAND} on the mean diagonal is {b['mean']:+.4f} at {abs(b['sigma']):.2f} sigma over "
                      f"{b['n']} paired replicates, against the as-built {AS_BUILT_BASIS:.4f}",
          "verdict": f"MET -- the basis contrast is a null here at {amt:.4f}" if amt <= ALIKE else
                     f"FALSIFIER FIRED -- the contrast is {amt:.4f}" if amt >= ALIKE_FIRES else
                     f"NULL -- the contrast is {amt:.4f}, between {ALIKE:.2f} and {ALIKE_FIRES:.2f}"}
    st = r["spans"]["standing"]
    over = {k: v for k, v in (("rand", st["rand_sigma"]), ("bio", st["bio_sigma"])) if abs(v) >= SIGMA}
    j5 = {"id": "BY5",
          "measured": f"on this order {RAND}'s mean diagonal over the baseline is {st['rand']:+.4f} at "
                      f"{abs(st['rand_sigma']):.2f} sigma and {BIO}'s {st['bio']:+.4f} at "
                      f"{abs(st['bio_sigma']):.2f}",
          "verdict": f"MET -- neither anchor's standing resolves here, the larger at "
                     f"{max(abs(st['rand_sigma']), abs(st['bio_sigma'])):.2f} sigma" if not over else
                     f"FALSIFIER FIRED -- {over} at or above two sigma"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the two anchors at another position ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source and the earned label, **reversed**, twenty replicates")
    print(f"\n   {'roll':>11} {'order':>9} {'arms':>34} {'tasks in the order trained':>56}")
    for label, roll in r["runs"].items():
        print(f"   {label:>11} {str(roll['task_order']):>9} {','.join(sorted(roll['arms'])):>34} "
              f"{'>'.join(roll['tasks'])[:56]:>56}")
    print("\n   the gain over naive, by position:")
    for label in ("biological", "new"):
        vals = r["contrasts"].get(f"buffer_gain_{label}")
        if vals:
            print(f"      {label:>10} buffer : " + " ".join(f"{x:+.4f}" for x in vals))
    for name, got in (("rand/naive", r["contrasts"]["rand_over_naive"]), ("bio/naive", r["contrasts"]["bio_over_naive"]),
                      ("basis", r["contrasts"]["basis_accuracy"]),
                      ("basis/forgetting", r["contrasts"]["basis_forgetting"])):
        print(f"      {name:>18} on the mean/first-order: {got['mean']:+.4f} at {abs(got['sigma']):.2f} sigma")
    print(f"   the newest task `{r['spans']['last']['last_task']}`: {RAND} {r['spans']['last']['rand']:+.4f} at "
          f"{abs(r['spans']['last']['rand_sigma']):.2f} sigma, {BIO} {r['spans']['last']['bio']:+.4f} at "
          f"{abs(r['spans']['last']['bio_sigma']):.2f}")
    print(f"   the shared arms against the biological arm's roll: " +
          ", ".join(f"{k} {v['equal']}" for k, v in r["identical"].items()))
    print("\n== the registered claims, BY1-BY5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e439` found the two anchors read alike as-built and `e446` found the price is the position's; this")
    print("    asks the pair at the position whose price is known, so the card's clause can name an arm or not)")
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
