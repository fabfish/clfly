"""E473 -- the held-out task at a second draw: whether the reading is the task's or the sample's.

Every unit of this line has closed on the same sentence: **one held-out draw**, since the fourth cue set is the flag's own
draw and a redraw of it is not measured. `e469` read **0.6875** to **0.7719** on it, `e471` found the reading bought
early, `e472` walked the budget between those points -- and all four findings carry the same bullet, because there is
nothing in the corpus that separates the **task** from the **sample** of it.

**This unit separates them.** The runner's held-out cue set is built with a seed of its own (`--loop-holdout-seed`,
defaulting to the suite's own length, which is what every artifact written before the flag carries), so a second value
draws the held-out task's **examples and cue noise** again and nothing else: the world, the three trained cue sets and
every other field are the same draw. Two more rolls at the same hundred updates and the same head, one per anchor, read
beside `e471`'s two. Four claims, registered before either new roll's reading was opened.

- **ZA1 -- and the new flag draws the held-out task and nothing else.** Every recorded config field agrees between the
  two draws except the held-out seed, the output path and the saved weights; the held-out seed is **7** on the new rolls
  against **3**; and the three trained tasks' replicates are **bit-identical** to the other draw's, record for record,
  on every arm. **Falsifier**: any other field differing, the seeds not being 7 and 3, or any trained replicate
  differing.
- **ZA2 -- and the sequence raises the unseen cue set's decodability at the second draw too.** At each draw the baseline
  arm's paired trained minus initial reading is positive at **two** sigma or more. **Falsifier**: under two sigma, or
  negative, at either draw.
- **ZA3 -- and the two draws agree.** The two draws' baseline changes differ by under **two** sigma, paired across the
  replicates the two rolls share. **Falsifier**: the difference resolving. *This is the sentence the line's four
  findings have been missing: the reading is the task's and not the sample's.*
- **ZA4 -- and the anchoring does not move it at either draw.** Each anchor's paired difference from its own baseline's
  trained reading is under **two** sigma in absolute value at both draws. **Falsifier**: an anchor at either draw whose
  contrast resolves.

**What it can do beyond that.** It makes the held-out reading a **two-draw** measurement, so *the sequence raises the
decodability* and *the anchoring does not move it* are properties of the task as drawn twice rather than of one draw of
it, and it pins the flag's own semantics: a redraw of the held-out task leaves the sequence's own replicates untouched.

**What it cannot do.** *Two draws are not a population*: the reading's spread over the family of fourth cue sets is
estimated from two of them, and a third draw could sit anywhere the two do not. *And a probe is not a task*: both draws
are of **linear readability** from the frozen body. *And one ridge*: **1e-2** is `e469`'s. *And one budget*: both draws
are at a hundred updates, so the separations `e467` and `e468` found on the sequence's own diagonal are not measured
here.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the two draws of the held-out task, by draw and side, at the same hundred updates and the same head
RUNS = {
    "draw3/bio": Path("runs/e471_earned_label_neurons_holdout_iters100_20reps.json"),
    "draw3/rand": Path("runs/e471_earned_label_rand_neurons_holdout_iters100_20reps.json"),
    "draw7/bio": Path("runs/e473_earned_label_neurons_holdout_iters100_seed7_20reps.json"),
    "draw7/rand": Path("runs/e473_earned_label_rand_neurons_holdout_iters100_seed7_20reps.json"),
}
DRAWS = {"draw3": 3, "draw7": 7}
SIDES = ("bio", "rand")
ANCHOR_OF = {"bio": "ewc-block", "rand": "ewc-block-rand"}
BASELINE = "naive"
BUFFER = "replay"
TRAINED_ARMS = ("naive", "ewc-block", "ewc-block-rand", "replay")
SHARED = ("circuit", "tasks")
IGNORED = ("loop_holdout_seed", "json_out", "save_theta")
N_TASKS = 3
N_ARMS = 3
MIN_REPS = 20
SIGMA = 2.0
CLAIMS = (
    ("ZA1", f"and the new flag draws the held-out task and nothing else, at {MIN_REPS} replicates",
     "Every recorded config field agrees between the two draws except the held-out seed, the output path and the saved "
     "weights; the held-out seed is 7 on the new rolls against 3; and the three trained tasks' replicates are "
     "bit-identical between the draws, record for record, on every arm",
     "falsifier: any other field differing, the seeds not being 7 and 3, or any trained replicate differing"),
    ("ZA2", f"and the sequence raises the decodability at the second draw too, at {SIGMA:.0f} sigma",
     "At each draw the baseline arm's paired trained minus initial reading is positive at two sigma or more",
     "falsifier: under two sigma, or negative, at either draw"),
    ("ZA3", f"and the two draws agree, under {SIGMA:.0f} sigma",
     "The two draws' baseline changes differ by under two sigma, paired across the replicates the two rolls share",
     "falsifier: the difference resolving"),
    ("ZA4", f"and the anchoring does not move it at either draw, under {SIGMA:.0f} sigma",
     "Each anchor's paired difference from its own baseline's trained reading is under two sigma in absolute value at "
     "both draws",
     "falsifier: an anchor at either draw whose contrast resolves"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def _records(got: dict) -> list:
    return [{"final_per_task": list(r["final_per_task"]), "mean_forgetting": r["mean_forgetting"]}
            for r in (got or {}).get("replicates") or []]


def _identical(a: list, b: list) -> dict:
    out = {"equal": True, "n": min(len(a), len(b)), "first_differing": None, "fields": []}
    if len(a) != len(b):
        return {**out, "equal": False}
    for i, (x, y) in enumerate(zip(a, b)):
        if x == y:
            continue
        out["equal"] = False
        out["first_differing"] = i
        out["fields"] = sorted(k for k in set(x) | set(y) if x.get(k) != y.get(k))
        break
    return out


def _roll(path: Path, anchor: str) -> dict | None:
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    arms = {}
    for arm in (BASELINE, anchor, BUFFER):
        reps = (methods.get(arm) or {}).get("replicates") or []
        blocks = [r.get("holdout") for r in reps]
        if not reps or any(b is None for b in blocks):
            return None
        arms[arm] = {"replicates": len(reps), "before": [b["before"] for b in blocks],
                     "after": [b["after"] for b in blocks],
                     "task": sorted({b.get("task") for b in blocks}),
                     "n_train": sorted({b.get("n_train") for b in blocks}),
                     "n_eval": sorted({b.get("n_eval") for b in blocks}),
                     "records": _records(methods[arm])}
    return {"artifact": path.name, "anchor": anchor, "arms": arms,
            #: the held-out seed as the run *used* it: the config's own value when the flag was passed, and the
            #: suite's length when it was not, which is the default the flag carries
            "seed": ((doc.get("config") or {}).get("loop_holdout_seed")
                     if (doc.get("config") or {}).get("loop_holdout_seed") is not None else N_TASKS),
            "shared": {k: doc.get(k) for k in SHARED},
            "config": {k: (doc.get("config") or {}).get(k)
                       for k in sorted(set(doc.get("config") or {}) - set(IGNORED))}}


def reading(runs: dict = RUNS) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "identical": {}, "curve": {}, "draws": {},
           "spans": {}}
    for label, path in runs.items():
        got = _roll(path, ANCHOR_OF[label.split("/")[1]])
        if got is None:
            return {**out, "ok": False,
                    "reason": f"roll {label}: {path} is absent, carries no {ANCHOR_OF[label.split('/')[1]]} arm, or "
                              f"carries no holdout block"}
        out["runs"][label] = got
    for side in SIDES:
        a, b = out["runs"][f"draw3/{side}"], out["runs"][f"draw7/{side}"]
        fields = sorted(set(a["config"]) | set(b["config"]))
        for k in fields:
            out["same"][f"{side}.{k}"] = a["config"].get(k) == b["config"].get(k)
        out["same"][f"{side}.circuit"] = a["shared"].get("circuit") == b["shared"].get("circuit")
        out["same"][f"{side}.tasks"] = a["shared"].get("tasks") == b["shared"].get("tasks")
        for arm in TRAINED_ARMS:
            #: only the arms both draws actually ran: each roll carries `naive`, ONE anchor and `replay`, so the
            #: other anchor is absent from both and comparing it would report a missing arm as a differing one
            if arm not in a["arms"] or arm not in b["arms"]:
                continue
            out["identical"][f"{side}:{arm}"] = _identical(a["arms"][arm]["records"], b["arms"][arm]["records"])
    counts = sorted({tuple(got["arms"][arm][k]) for got in out["runs"].values()
                     for arm in got["arms"] for k in ("task", "n_train", "n_eval")}, key=repr)
    seeds = sorted({label.split("/")[0]: got["seed"] for label, got in out["runs"].items()}.items())
    for draw in DRAWS:
        out["curve"][draw] = {}
        for side in SIDES:
            roll = out["runs"][f"{draw}/{side}"]
            base = roll["arms"][BASELINE]
            out["curve"][draw][side] = {
                "draw": DRAWS[draw], "side": side, "anchor": roll["anchor"],
                "initial": statistics.fmean(base["before"]), "trained": statistics.fmean(base["after"]),
                "change": _paired(base["after"], base["before"]),
                "arms": {arm: {"initial": statistics.fmean(got["before"]),
                               "trained": statistics.fmean(got["after"]),
                               "change": _paired(got["after"], got["before"]),
                               "against_baseline": _paired(got["after"], base["after"])}
                         for arm, got in roll["arms"].items()},
            }
    for side in SIDES:
        a = out["runs"][f"draw3/{side}"]["arms"][BASELINE]
        b = out["runs"][f"draw7/{side}"]["arms"][BASELINE]
        out["draws"][side] = {"initial": _paired(b["before"], a["before"]),
                              "trained": _paired(b["after"], a["after"]),
                              "change": _paired([y - x for x, y in zip(b["before"], b["after"])],
                                                [y - x for x, y in zip(a["before"], a["after"])])}
    thin = {label: v["replicates"] for label, roll in out["runs"].items()
            for arm, v in roll["arms"].items() if v["replicates"] < MIN_REPS}
    out["spans"] = {
        "draws": list(DRAWS), "sides": list(SIDES), "runs": len(out["runs"]), "same_fields": len(out["same"]),
        "seeds": dict(seeds), "identical": len(out["identical"]),
        "identical_equal": sum(1 for v in out["identical"].values() if v["equal"]),
        "counts": counts, "thin": thin,
        "replicates": sorted({v["replicates"] for roll in out["runs"].values() for v in roll["arms"].values()}),
        "tasks": {label: roll["arms"][roll["anchor"]]["task"] for label, roll in out["runs"].items()},
        "short": {label: sorted(roll["arms"]) for label, roll in out["runs"].items() if len(roll["arms"]) < N_ARMS},
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no holdout block"}
                for c in CLAIMS]
    s = r["spans"]
    differ = sorted(k for k, v in r["same"].items() if not v)
    not_id = sorted(k for k, v in r["identical"].items() if not v["equal"])
    seeds_ok = sorted(set(s["seeds"].values())) == sorted(set(DRAWS.values()))
    j1 = {"id": "ZA1",
          "measured": f"{s['runs']} rolls at {s['replicates']} replicates over {s['same_fields']} compared fields, the "
                      f"held-out seed {s['seeds']}, and {s['identical_equal']} of {s['identical']} trained arms the two "
                      f"draws both ran bit-identical between them",
          "verdict": "MET -- the flag redraws the held-out task's own examples and leaves the sequence's replicates "
                     "untouched" if (not differ and seeds_ok and not not_id and not s["thin"] and not s["short"]) else
                     f"FALSIFIER FIRED -- differing {differ[:6]}, seeds {s['seeds']}, not identical {not_id[:4]}, "
                     f"thin {s['thin']}, short {s['short']}"}
    ch = {draw: {side: r["curve"][draw][side]["change"] for side in SIDES} for draw in DRAWS}
    worst = min((ch[d][side]["sigma"] for d in ch for side in SIDES), default=0.0)
    j2 = {"id": "ZA2",
          "measured": f"the baseline's change at the two draws is "
                      f"{ {d: {side: round(ch[d][side]['mean'], 4) for side in SIDES} for d in ch} } at "
                      f"{ {d: {side: round(ch[d][side]['sigma'], 2) for side in SIDES} for d in ch} } sigma, from "
                      f"{ {d: {side: round(r['curve'][d][side]['initial'], 4) for side in SIDES} for d in ch} }",
          "verdict": f"MET -- the sequence raises the unseen cue set's decodability at both draws, the weaker at "
                     f"{worst:.2f} sigma" if worst >= SIGMA else
                     f"FALSIFIER FIRED -- the weaker draw is {worst:.2f} sigma"}
    dd = r["draws"]
    weak = min((dd[side]["change"]["sigma"] for side in SIDES), default=0.0)
    resolved = sorted(side for side in SIDES if abs(dd[side]["change"]["sigma"]) >= SIGMA)
    j3 = {"id": "ZA3",
          "measured": f"the two draws' changes differ by "
                      f"{ {side: round(dd[side]['change']['mean'], 4) for side in SIDES} } at "
                      f"{ {side: round(dd[side]['change']['sigma'], 2) for side in SIDES} } sigma, against changes of "
                      f"{ {d: {side: round(ch[d][side]['mean'], 4) for side in SIDES} for d in ch} }",
          "verdict": "MET -- the two draws agree, so the reading is the task's and not the sample's" if not resolved
                     else f"FALSIFIER FIRED -- the difference resolves on {resolved} at {weak:.2f} sigma and beyond"}
    bad = sorted(f"{d}/{side}/{anchor}" for d in DRAWS for side in SIDES
                 for anchor, got in r["curve"][d][side]["arms"].items()
                 if anchor != BASELINE and abs(got["against_baseline"]["sigma"]) >= SIGMA)
    j4 = {"id": "ZA4",
          "measured": f"each anchor against its own baseline at each draw: "
                      f"{ {f'{d}/{side}': {a: (round(v['against_baseline']['mean'], 4),
                                                round(v['against_baseline']['sigma'], 2))
                                          for a, v in r['curve'][d][side]['arms'].items() if a != BASELINE}
                          for d in DRAWS for side in SIDES} }",
          "verdict": "MET -- the anchoring does not move the held-out reading at either draw" if not bad else
                     f"FALSIFIER FIRED -- {bad}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the held-out task at a second draw ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the same world and the same hundred updates, with the held-out cue set's own seed moved from 3 to 7: the")
    print("   sequence's three cue sets and every other field are the same draw")
    print(f"\n   {'draw/roll/arm':<26} {'initial':>8} {'trained':>8} {'change':>8} {'sigma':>7} {'vs base':>9} {'sigma':>7}")
    for d in DRAWS:
        for side in SIDES:
            cell = r["curve"][d][side]
            for arm in (BASELINE, cell["anchor"], BUFFER):
                got = cell["arms"][arm]
                vs = got["against_baseline"]
                print(f"   {d + '/' + side + '/' + arm:<26} {got['initial']:>8.4f} {got['trained']:>8.4f} "
                      f"{got['change']['mean']:>+8.4f} {got['change']['sigma']:>7.2f} " +
                      (f"{vs['mean']:>+9.4f} {vs['sigma']:>7.2f}" if arm != BASELINE else f"{'-':>9} {'-':>7}"))
    print(f"\n   the trained tasks bit-identical between the draws: {r['spans']['identical_equal']} of "
          f"{r['spans']['identical']} arms")
    print("   the held-out seed by draw: " + ", ".join(f"{k} {v}" for k, v in r["spans"]["seeds"].items()))
    print("\n== the registered claims, ZA1-ZA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (every finding of this line closes on *one held-out draw*; the flag's own seed is what separates the")
    print("    task from the sample of it, and it draws nothing else)")
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
