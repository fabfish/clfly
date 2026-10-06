"""E451 -- the basis contrast where the effect is: the matched-random anchor at four columns.

`e449` halved the card's world's width, found the ledger peaks at **eight** columns, and found the one roll in eight
where the anchor's whole-diagonal standing clears two sigma: at four columns `ewc-block` reads **-0.0271** over the
baseline at **2.29** sigma, a **resolved deficit**. `e450` wrote that into the card's ninth revision. Every reading of
the corpus's own headline pair -- the biological cell-class basis against its size-matched random partition -- has been
taken at a width where the pair is a **null**: **+0.0063** at **0.36** sigma as-built (`e439`), **+0.0108** at **0.54**
under the reversed order (`e447`), and eleven audits of the state read-out before them. **The pair has never been read at
a width where one of its arms has a resolved effect at all.**

**This unit drives the matched-random arm at four columns.** `e449`'s configuration with
`--methods naive,ewc-block-rand,replay` alone differing, at the same twenty replicates, the same width and the same
order, so the two arms this run shares with `e449` are the control and the pair can be read where the biological arm's
deficit lives. Five claims, registered before the new run's reading was opened.

- **CX1 -- and the run is one configuration with the arm list moved.** The three arms at **20** replicates, every
  recorded config field agreeing with `e449`'s except `methods`, the output path and the saved weights, the width **4**,
  and the new run's `naive` and `replay` replicates **bit-identical** to `e449`'s. **Falsifier**: any other field
  differing, an arm missing or short, a width that is not 4, or any shared replicate's record differing.
- **CX2 -- and the matched-random arm has a resolved deficit here too.** Its mean diagonal over the baseline is negative
  at **two** sigma or more. **Falsifier**: not negative, or under two sigma. *The biological arm reads **-0.0271** at
  **2.29** sigma at this width.*
- **CX3 -- and the two anchors' deficits agree in size.** Their mean-diagonal contrasts differ by at most **0.05**.
  **Falsifier**: **0.10** or more apart; **null**: between.
- **CX4 -- and the basis contrast is a null at the width where the effect is.** The paired
  `ewc-block`-minus-`ewc-block-rand` on the mean diagonal is within **0.05**. **Falsifier**: **0.10** or more; **null**:
  between. *This is the corpus's headline asked where it can be informative: at sixteen columns both arms are absent, so
  a null there would say nothing about the basis, while here one arm has a resolved effect.*
- **CX5 -- and the matched-random arm's newest-task price resolves here too.** Its cost at the last-taught task is
  negative at **two** sigma or more. **Falsifier**: not negative, or under two sigma.

**What it can do beyond that.** It separates two readings the corpus has not had to tell apart. If the matched-random
arm has the same deficit and the pair is still a null, then the narrow end's deficit is the penalty's -- the third width
at which the basis makes no difference on this world -- and the corpus's eleven nulls are joined by a twelfth taken
where one of the arms is doing something. If the matched-random arm has no deficit where the biological one has one,
then the deficit `e449` found is the **basis's** and the card's ninth revision should say so, which would be the first
time on this world that a basis contrast has resolved.

**What it cannot do.** *One width*: four columns, so the pair is read where one arm has a deficit and not at eight or
sixteen. *And one cell*: the card's world at twenty replicates, so the other five draws and the three streams are not in
the reading. *And one partition draw*: the matched-random partition is a draw of the same group sizes and not the family
of them. *And the two rolls are two runs*: the pair pairs replicate against replicate by the runner's `seed0 + 100 * r`
schedule, which is a same-seed pairing and not the same run.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the matched-random arm at four columns, and the biological arm's roll at that width
RUNS = {
    "new": Path("runs/e451_earned_label_rand_worlddims4_20reps.json"),
    "biological": Path("runs/e449_earned_label_worlddims4_20reps.json"),
}
ARMS = ("naive", "ewc-block", "ewc-block-rand", "replay")
BASELINE = "naive"
BIO = "ewc-block"
RAND = "ewc-block-rand"
BUFFER = "replay"
SHARED_ARMS = ("naive", "replay")
WIDTH_FIELD = "loop_world_dims"
SHARED = ("circuit", "tasks")
IGNORED = ("json_out", "save_theta", "methods")
N_TASKS = 3
N_ARMS = 3
MIN_REPS = 20
WIDTH = 4
ALIKE = 0.05
ALIKE_FIRES = 0.10
SIGMA = 2.0
#: the biological arm's deficit at this width, which `e449` read and CX2 is registered against
BIO_STANDING = -0.0271
BIO_SIGMA = 2.29
CLAIMS = (
    ("CX1", f"and the run is one configuration with the arm list moved, at {MIN_REPS} replicates",
     "The three arms at twenty replicates, every recorded config field agreeing with e449's except methods, the output "
     "path and the saved weights, the width 4, and the new run's naive and replay bit-identical to e449's",
     "falsifier: any other field differing, an arm missing or short, a width that is not 4, or any shared replicate's "
     "record differing"),
    ("CX2", f"and the matched-random arm has a resolved deficit here too, at {SIGMA:.0f} sigma",
     "Its mean diagonal over the baseline is negative at two sigma or more",
     "falsifier: not negative, or under two sigma"),
    ("CX3", f"and the two anchors' deficits agree in size, within {ALIKE:.2f}",
     "Their mean-diagonal contrasts differ by at most 0.05",
     f"falsifier: {ALIKE_FIRES:.2f} or more apart; null: between"),
    ("CX4", f"and the basis contrast is a null at the width where the effect is, within {ALIKE:.2f}",
     "The paired ewc-block-minus-ewc-block-rand on the mean diagonal is within 0.05",
     f"falsifier: {ALIKE_FIRES:.2f} or more; null: between"),
    ("CX5", f"and the matched-random arm's newest-task price resolves here too, at {SIGMA:.0f} sigma",
     "Its cost at the last-taught task is negative at two sigma or more",
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
    cfg = doc.get("config") or {}
    return {"artifact": path.name, "arms": arms,
            "task_names": [t.get("name") if isinstance(t, dict) else t for t in (doc.get("tasks") or [])],
            "width": cfg.get(WIDTH_FIELD),
            "shared": {k: doc.get(k) for k in SHARED},
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
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "identical": {}, "widths": {}, "contrasts": {},
           "spans": {}}
    for label, path in runs.items():
        got = _roll(path)
        if got is None:
            return {**out, "ok": False, "reason": f"roll {label}: {path} is absent or carries no arm"}
        out["runs"][label] = got
    new, bio = out["runs"]["new"], out["runs"]["biological"]
    missing = [a for a in (BASELINE, RAND, BUFFER) if a not in new["arms"]]
    if missing:
        return {**out, "ok": False, "reason": f"the new roll carries no arm for {missing}"}
    if BIO not in bio["arms"] or BASELINE not in bio["arms"]:
        return {**out, "ok": False, "reason": "the biological arm's roll carries no anchor or no baseline"}
    same = {}
    fields = sorted(set(new["config"]) | set(bio["config"]))
    for k in fields:
        same[f"config.{k}"] = new["config"].get(k) == bio["config"].get(k)
    same["circuit"] = new["shared"].get("circuit") == bio["shared"].get("circuit")
    same["task_names"] = new["task_names"] == bio["task_names"]
    out["same"] = same
    out["widths"] = {"new": new["width"], "biological": bio["width"]}
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
    out["spans"] = {"replicates": sorted({v["replicates"] for roll in out["runs"].values()
                                         for v in roll["arms"].values()}),
                    "arms": {label: len(roll["arms"]) for label, roll in out["runs"].items()},
                    "same_fields": len(same), "widths": out["widths"],
                    "standing": {"rand": out["contrasts"]["rand_over_naive"]["mean"],
                                 "rand_sigma": out["contrasts"]["rand_over_naive"]["sigma"],
                                 "bio": out["contrasts"]["bio_over_naive"]["mean"],
                                 "bio_sigma": out["contrasts"]["bio_over_naive"]["sigma"]},
                    "last": {"rand": out["contrasts"]["rand_last"]["mean"],
                             "rand_sigma": out["contrasts"]["rand_last"]["sigma"],
                             "bio": out["contrasts"]["bio_last"]["mean"],
                             "bio_sigma": out["contrasts"]["bio_last"]["sigma"]},
                    "known": {"bio_standing": BIO_STANDING, "bio_sigma": BIO_SIGMA}}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no arm"} for c in CLAIMS]
    differ = sorted(k for k, v in r["same"].items() if not v)
    not_identical = sorted(k for k, v in r["identical"].items() if not v["equal"])
    thin = {f"{lbl}.{a}": v["replicates"] for lbl, roll in r["runs"].items() for a, v in roll["arms"].items()
            if v["replicates"] < MIN_REPS}
    short = {} if len(r["runs"]["new"]["arms"]) >= N_ARMS else {"new": sorted(r["runs"]["new"]["arms"])}
    width_ok = r["widths"]["new"] == WIDTH and r["widths"]["biological"] == WIDTH
    j1 = {"id": "CX1",
          "measured": f"the new roll carries {len(r['runs']['new']['arms'])} arms at {r['spans']['replicates']} "
                      f"replicates over {r['spans']['same_fields']} compared fields, the widths {r['spans']['widths']}, "
                      f"the shared arms bit-identical {len(r['identical']) - len(not_identical)} of "
                      f"{len(r['identical'])}",
          "verdict": "MET -- one configuration with the arm list moved, both rolls at four columns, and the two shared "
                     "arms reproducing the biological arm's roll" if
                     (not short and not differ and not not_identical and width_ok and not thin) else
                     f"FALSIFIER FIRED -- differing {differ}, not bit-identical {not_identical}, widths "
                     f"{r['spans']['widths']}, thin {thin}, short {short}"}
    st = r["spans"]["standing"]
    j2 = {"id": "CX2",
          "measured": f"at four columns {RAND} over {BASELINE} on the mean diagonal is {st['rand']:+.4f} at "
                      f"{abs(st['rand_sigma']):.2f} sigma, against the biological arm's {st['bio']:+.4f} at "
                      f"{abs(st['bio_sigma']):.2f}",
          "verdict": f"MET -- the matched-random arm has a resolved deficit here too, {st['rand']:+.4f} at "
                     f"{abs(st['rand_sigma']):.2f} sigma" if (st["rand"] < 0 and abs(st["rand_sigma"]) >= SIGMA) else
                     f"FALSIFIER FIRED -- {st['rand']:+.4f} at {abs(st['rand_sigma']):.2f} sigma"}
    gap = abs(st["rand"] - st["bio"])
    j3 = {"id": "CX3",
          "measured": f"the two anchors' deficits are {st['rand']:+.4f} and {st['bio']:+.4f}, {gap:.4f} apart",
          "verdict": f"MET -- the two anchors' deficits agree in size, {gap:.4f} apart" if gap <= ALIKE else
                     f"FALSIFIER FIRED -- the gap is {gap:.4f}" if gap >= ALIKE_FIRES else
                     f"NULL -- the gap is {gap:.4f}, between {ALIKE:.2f} and {ALIKE_FIRES:.2f}"}
    b = r["contrasts"]["basis_accuracy"]
    amt = abs(b["mean"])
    j4 = {"id": "CX4",
          "measured": f"{BIO} minus {RAND} on the mean diagonal is {b['mean']:+.4f} at {abs(b['sigma']):.2f} sigma over "
                      f"{b['n']} paired replicates, at the width where the biological arm reads "
                      f"{st['bio']:+.4f} at {abs(st['bio_sigma']):.2f}",
          "verdict": f"MET -- the basis contrast is a null at the width where the effect is, {amt:.4f}" if amt <= ALIKE
                     else f"FALSIFIER FIRED -- the contrast is {amt:.4f}" if amt >= ALIKE_FIRES else
                     f"NULL -- the contrast is {amt:.4f}, between {ALIKE:.2f} and {ALIKE_FIRES:.2f}"}
    last = r["spans"]["last"]
    j5 = {"id": "CX5",
          "measured": f"at four columns {RAND}'s newest-task cost is {last['rand']:+.4f} at "
                      f"{abs(last['rand_sigma']):.2f} sigma, against the biological arm's {last['bio']:+.4f} at "
                      f"{abs(last['bio_sigma']):.2f}",
          "verdict": f"MET -- the matched-random arm's price resolves here too, {last['rand']:+.4f} at "
                     f"{abs(last['rand_sigma']):.2f} sigma" if (last["rand"] < 0 and abs(last["rand_sigma"]) >= SIGMA)
                     else f"FALSIFIER FIRED -- {last['rand']:+.4f} at {abs(last['rand_sigma']):.2f} sigma"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the basis contrast where the effect is ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source and the earned label, at **four columns**, twenty replicates")
    print(f"\n   {'roll':>11} {'width':>6} {'arms':>34} {'tasks':>50}")
    for label, roll in r["runs"].items():
        print(f"   {label:>11} {str(roll['width']):>6} {','.join(sorted(roll['arms'])):>34} "
              f"{'>'.join(roll['task_names'])[:50]:>50}")
    st, last = r["spans"]["standing"], r["spans"]["last"]
    print(f"\n   the two anchors over the baseline on the mean diagonal: {RAND} {st['rand']:+.4f} at "
          f"{abs(st['rand_sigma']):.2f} sigma, {BIO} {st['bio']:+.4f} at {abs(st['bio_sigma']):.2f}")
    print(f"   their newest-task costs: {RAND} {last['rand']:+.4f} at {abs(last['rand_sigma']):.2f} sigma, {BIO} "
          f"{last['bio']:+.4f} at {abs(last['bio_sigma']):.2f}")
    for name in ("basis_accuracy", "basis_forgetting"):
        p = r["contrasts"][name]
        print(f"   the basis contrast on {name.split('_')[1]:>10}: {p['mean']:+.4f} at {abs(p['sigma']):.2f} sigma")
    print(f"   the shared arms against e449's roll: " +
          ", ".join(f"{k} {v['equal']}" for k, v in r["identical"].items()))
    print("\n== the registered claims, CX1-CX5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e439` read the pair at 0.36 sigma as-built, `e447` at 0.54 under the reverse order, and fourteen")
    print("    audits before them; `e449` put one of the two arms at a resolved effect, which is this unit's width)")
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
