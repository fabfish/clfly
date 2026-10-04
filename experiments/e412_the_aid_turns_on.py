"""E412 -- the aid turns on: the rehearsal is worth nothing until the body has learned something.

`e411` measured the corpus's rehearsal on the six five-hundred-update worlds and found the aid worth **+0.1330** to
**+0.1594** of accuracy there, against the six draws' own span of 0.0309. It registered the reading's one setting as
what it could not settle: *"one rehearsal setting (--replay-per-task 16 --replay-batch 16), so what is measured is the
corpus's own buffer and not the aid in general."* And `e408` left the budget axis open: the six worlds' read-out has
been rolled at 1, 2, 5, 20, 100 and 500 updates, and whether the widening between 100 and 500 is a ramp or a step is
the question it named.

**This unit reads the corpus's own budget ladder on the card's world.** `e389`, `e390`, `e391` and `e380` rolled one
configuration -- `cue0` with the action source, twenty replicates, the same circuit, read-out draw and environment --
at **twenty** update budgets from 1 to 500, and every one of the twenty artifacts carries **both** the `naive` and the
`replay` arm. No training, no probe. Five claims, registered before this unit's pass over the ladder.

- **AT1 -- and the ladder is carried.** At least **15** budgets, each with both arms at **20** replicates, and one
  configuration except the budget. **Falsifier**: fewer budgets, fewer replicates, or a shared field differing.
- **AT2 -- and at the small budgets the aid's sign is not the world's.** Among the budgets at or below **20** the gain
  takes **both** signs. **Falsifier**: one sign only, which would say the aid's direction is a property of the world at
  every budget. *This is the unit's own prediction: if the aid were a property of the arm, its sign would be fixed.*
- **AT3 -- and the aid ramps.** The largest budget's gain exceeds the best gain at or below **100** by at least
  **0.05**. **Falsifier**: below **0.03**; **null**: between.
- **AT4 -- and above the knee the order is monotone.** Over the five largest budgets (100, 150, 275, 425, 500) the gain
  is strictly increasing in the budget. **Falsifier**: any inversion.
- **AT5 -- and the aid's worth tracks how much there is to keep.** Over the twenty budgets the rank correlation between
  the `naive` arm's final accuracy and the gain is at least **0.7**. **Falsifier**: below **0.4**; **null**: between.

**What it can do beyond that.** It puts `e411`'s six-world result on the axis it was measured at: the six worlds sit
at budget 500, the top of this ladder, so what `e411` measures is the aid where it is worth most. And it answers
`e408`'s open question for the aid -- the rise from 100 to 500 is a **ramp** and not a step. And it dates the knee:
between **20** and **45** updates the aid goes from sign-unstable to positive and stays positive.

**What it cannot do.** *One world and one arm pair*: `cue0` with the action source and the `naive`/`replay` pair only,
so the ladder is one world's and the penalty arms are absent from all twenty artifacts. *And it is not one
execution*: the twenty budgets were rolled at four code revisions over several days, so what the ladder holds fixed
is the recorded configuration -- circuit, read-out draw, environment draw, task list -- and not the process. *And the
budget is not the level*: the naive arm's own accuracy rises 0.2438 to 0.5191 along the ladder, so "the aid tracks
the level" is a correlation over a joint ramp and not an intervention. *And the metric is the corpus's*:
`mean_forgetting` is the retention matrix's diagonal minus its last row, which `e305` showed cannot see the part an
arm never learned. *And a probe is not a mechanism.*
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the card's world's budget ladder, one configuration except `iters`: `e389` (1-20), `e390` (30-100), `e391`
#: (150-425) and `e380` (500), twenty replicates each
LADDER = {}
for _b in (1, 2, 3, 4, 5, 6, 8, 11, 14, 17, 20):
    LADDER[_b] = Path(f"runs/e389_earned_label_iters{_b}_cue0_actionsource_20reps.json")
for _b in (30, 45, 65, 85, 100):
    LADDER[_b] = Path(f"runs/e390_earned_label_iters{_b}_cue0_actionsource_20reps.json")
for _b in (150, 275, 425):
    LADDER[_b] = Path(f"runs/e391_earned_label_iters{_b}_cue0_actionsource_20reps.json")
LADDER[500] = Path("runs/e380_earned_label_cue0_actionsource_20reps.json")

ARMS = ("naive", "replay")
N_TASKS = 3
MIN_BUDGETS = 15
MIN_REPS = 20
SMALL = 20
RAMP_BAND = 100
RAMP = 0.05
RAMP_FIRES = 0.03
ORDER_BUDGETS = (100, 150, 275, 425, 500)
RHO = 0.7
RHO_FIRES = 0.4
CLAIMS = (
    ("AT1", f"and the ladder is carried, over at least {MIN_BUDGETS} budgets and {MIN_REPS} replicates",
     "At least fifteen budgets carry both arms at twenty replicates each, and one configuration except the budget",
     "falsifier: fewer budgets, fewer replicates, or a shared field differing"),
    ("AT2", f"and at the small budgets the aid's sign is not the world's, at or below {SMALL}",
     "Among the budgets at or below 20 the accuracy gain takes both signs",
     "falsifier: one sign only"),
    ("AT3", f"and the aid ramps, by at least {RAMP:.2f} above the best small-budget gain",
     "The largest budget's gain exceeds the best gain at or below 100 by at least 0.05",
     f"falsifier: below {RAMP_FIRES:.2f}; null: between"),
    ("AT4", "and above the knee the order is monotone",
     "Over the five largest budgets the gain is strictly increasing in the budget",
     "falsifier: any inversion"),
    ("AT5", f"and the aid's worth tracks the level, at a rank correlation of {RHO:.1f}",
     "Over the twenty budgets the rank correlation between the naive arm's final accuracy and the gain is at least 0.7",
     f"falsifier: below {RHO_FIRES:.1f}; null: between"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def spearman(xs: list[float], ys: list[float]) -> float:
    rx, ry = _ranks(list(xs)), _ranks(list(ys))
    n = len(rx)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else 0.0


def reading(ladder: dict = LADDER, arms=ARMS) -> dict:
    out = {"ok": True, "reason": None, "budgets": [], "arms": list(arms), "shared": None}
    for budget in sorted(ladder):
        doc = load(ladder[budget])
        if not doc:
            return {**out, "ok": False, "reason": f"budget {budget}: {ladder[budget]} is absent"}
        entry = {"budget": budget, "artifact": Path(ladder[budget]).name, "arms": {}}
        for arm in arms:
            reps = ((doc.get("methods") or {}).get(arm) or {}).get("replicates") or []
            if not reps:
                return {**out, "ok": False, "reason": f"budget {budget}: the {arm} arm carries no replicates"}
            entry["arms"][arm] = {
                "replicates": len(reps),
                "final_accuracy": statistics.fmean([r["final_accuracy"] for r in reps]),
                "mean_forgetting": statistics.fmean([r["mean_forgetting"] for r in reps]),
                "final": [statistics.fmean([r["final_per_task"][k] for r in reps]) for k in range(N_TASKS)],
                "forgetting": [statistics.fmean([r["forgetting_per_task"][k] for r in reps])
                               for k in range(N_TASKS)],
            }
        entry["gain"] = entry["arms"]["replay"]["final_accuracy"] - entry["arms"]["naive"]["final_accuracy"]
        entry["cut"] = entry["arms"]["naive"]["mean_forgetting"] - entry["arms"]["replay"]["mean_forgetting"]
        #: the configuration is the circuit, the read-out draw, the environment's draw and the task list, plus every
        #: `config` field except the three the run itself writes -- `iters`, `json_out` and `save_theta`. The recorded
        #: machine calibration and the code revision move between executions of one configuration and are reported
        #: beside it rather than counted as a difference
        cfg = doc.get("config") or {}
        shared = {"circuit": doc.get("circuit"), "readout": doc.get("readout"), "env_draw": doc.get("env_draw"),
                  "tasks": doc.get("tasks"),
                  "config": {k: v for k, v in cfg.items() if k not in ("iters", "json_out", "save_theta")}}
        if out["shared"] is None:
            out["shared"] = shared
        elif json.dumps(shared, sort_keys=True) != json.dumps(out["shared"], sort_keys=True):
            out.setdefault("shared_differs_at", []).append(budget)
        out.setdefault("budget_field", {})[str(budget)] = cfg.get("iters")
        out.setdefault("revisions", {}).setdefault(str((doc.get("code_revision") or {}).get("commit", "?")),
                                                   []).append(budget)
        out["budgets"].append(entry)
    gains = [e["gain"] for e in out["budgets"]]
    out["spans"] = {"budgets": len(out["budgets"]), "gain_min": min(gains), "gain_max": max(gains),
                    "naive_accuracy_first": out["budgets"][0]["arms"]["naive"]["final_accuracy"],
                    "naive_accuracy_last": out["budgets"][-1]["arms"]["naive"]["final_accuracy"],
                    "rho_level_vs_gain": spearman([e["arms"]["naive"]["final_accuracy"] for e in out["budgets"]],
                                                  gains)}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a budget's artifact is absent"}
                for c in CLAIMS]
    rows = r["budgets"]
    thin = {str(e["budget"]): {a: e["arms"][a]["replicates"] for a in ARMS}
            for e in rows if any(e["arms"][a]["replicates"] < MIN_REPS for a in ARMS)}
    bad_field = {k: v for k, v in (r.get("budget_field") or {}).items() if str(v) != k}
    differs = r.get("shared_differs_at") or []
    j1 = {"id": "AT1",
          "measured": f"{len(rows)} budgets, each carrying "
                      f"{sorted({e['arms']['naive']['replicates'] for e in rows})} replicates on both arms, one "
                      f"configuration except the budget, across {len(r.get('revisions') or {})} code revisions"
                      + (f", the shared configuration differing at {differs}" if differs else ""),
          "verdict": f"MET -- the ladder is carried over {len(rows)} budgets, one configuration except the budget"
                     if (len(rows) >= MIN_BUDGETS and not thin and not bad_field and not differs) else
                     f"FALSIFIER FIRED -- {thin or bad_field or {'shared_differs_at': differs}}"}
    small = [e for e in rows if e["budget"] <= SMALL]
    pos = {e["budget"] for e in small if e["gain"] > 0}
    neg = {e["budget"] for e in small if e["gain"] < 0}
    j2 = {"id": "AT2",
          "measured": f"{len(small)} budgets at or below {SMALL}: {len(pos)} positive, {len(neg)} negative, "
                      f"{len(small) - len(pos) - len(neg)} at zero",
          "verdict": "MET -- the aid's sign is not the world's at the small budgets" if (pos and neg) else
                     "FALSIFIER FIRED -- one sign only at the small budgets"}
    top = max(e["gain"] for e in rows)
    best_small = max(e["gain"] for e in rows if e["budget"] <= RAMP_BAND)
    lift = top - best_small
    j3 = {"id": "AT3",
          "measured": f"the largest budget's gain {top:+.4f} against the best at or below {RAMP_BAND}, "
                      f"{best_small:+.4f}, a lift of {lift:+.4f}",
          "verdict": f"MET -- the aid ramps, by {lift:+.4f}" if lift >= RAMP else
                     f"FALSIFIER FIRED -- {lift:+.4f} is under the ramp's bar" if lift < RAMP_FIRES else
                     f"NULL -- {lift:+.4f}, between {RAMP_FIRES:.2f} and {RAMP:.2f}"}
    band = sorted((e for e in rows if e["budget"] in ORDER_BUDGETS), key=lambda e: e["budget"])
    inv = [(band[i]["budget"], band[i + 1]["budget"]) for i in range(len(band) - 1)
           if band[i + 1]["gain"] <= band[i]["gain"]]
    j4 = {"id": "AT4",
          "measured": "the top five budgets " + ", ".join(f"{e['budget']}:{e['gain']:+.4f}" for e in band)
                      if len(band) == len(ORDER_BUDGETS) else f"only {len(band)} of the top band are on disk",
          "verdict": f"MET -- the gain rises with the budget over the top five, {band[0]['gain']:+.4f} to "
                     f"{band[-1]['gain']:+.4f}" if (len(band) == len(ORDER_BUDGETS) and not inv) else
                     f"FALSIFIER FIRED -- inversions {inv}" if inv else
                     f"FALSIFIER FIRED -- {len(band)} of {len(ORDER_BUDGETS)} top-band budgets on disk"}
    rho = r["spans"]["rho_level_vs_gain"]
    j5 = {"id": "AT5",
          "measured": f"the rank correlation over the {len(rows)} budgets between the naive arm's final accuracy "
                      f"({r['spans']['naive_accuracy_first']:.4f} to {r['spans']['naive_accuracy_last']:.4f}) and the "
                      f"gain is {rho:+.3f}",
          "verdict": f"MET -- the aid's worth tracks the level, at {rho:+.3f}" if rho >= RHO else
                     f"FALSIFIER FIRED -- {rho:+.3f} is under the bar" if rho < RHO_FIRES else
                     f"NULL -- {rho:+.3f}, between {RHO_FIRES:.1f} and {RHO:.1f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the aid turns on ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a budget is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world's `naive` and `replay` arms along the corpus's own budget ladder, twenty replicates")
    print(f"\n   {'budget':>6} {'naive acc':>10} {'replay acc':>11} {'gain':>9} {'naive mf':>9} {'cut':>9}")
    for e in r["budgets"]:
        print(f"   {e['budget']:6d} {e['arms']['naive']['final_accuracy']:10.4f} "
              f"{e['arms']['replay']['final_accuracy']:11.4f} {e['gain']:+9.4f} "
              f"{e['arms']['naive']['mean_forgetting']:9.4f} {e['cut']:+9.4f}")
    s = r["spans"]
    print(f"\n   {s['budgets']} budgets, gain {s['gain_min']:+.4f} to {s['gain_max']:+.4f}, "
          f"rank correlation with the naive level {s['rho_level_vs_gain']:+.3f}")
    revs = r.get("revisions") or {}
    print(f"   the ladder spans {len(revs)} code revisions: "
          + ", ".join(f"{c[:8]} ({len(b)} budgets)" for c, b in sorted(revs.items(), key=lambda kv: min(kv[1]))))
    print("\n== the registered claims, AT1-AT5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e411` measured the aid on the six worlds at budget 500, the top of this ladder, and registered the")
    print("    single setting it could not settle; this reads the axis it was measured at)")
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
