"""E411 -- the rehearsal on the six worlds: the aid is the same on every one, and it swamps the draw.

`e410` read the retention the six worlds' five-hundred-update runs already carry and found them one population on the
benchmark's own metric -- a final accuracy spanning **0.0309** across six draws, against a task-0 world reading
spanning **0.3104** -- with the world's reading uncorrelated with the score. It registered what that leaves: *"the
`replay` arm's own retention is in the same artifacts and is outside this reading."*

**This unit reads it.** The same six runs carry a second arm, and the corpus's own rehearsal is the comparison a
continual-learning benchmark exists to make: the arm that stores and replays against the arm that does not, on every
world. No training, no probe. Five claims, registered before any of the second arm's matrices was read.

- **AP1 -- and the second arm's matrices are carried.** Each of the six worlds' runs carries, for the `replay` arm,
  the same **twenty** replicates with three-by-three retention matrices. **Falsifier**: any world missing them.
  **Bound**: at least **5** worlds and at least **20** replicates each.
- **AP2 -- and the rehearsal helps on every world.** The `replay` arm's mean final accuracy exceeds the `naive`
  arm's on **all six** worlds. **Falsifier**: any world where it does not, which would say the aid is a draw's
  property as much as the reading is.
- **AP3 -- and by at least a tenth.** Every world's gain is at least **0.10**. **Falsifier**: any world below
  **0.05**. **Null**: between.
- **AP4 -- and it cuts the forgetting on every world.** The `replay` arm's mean forgetting is below the `naive`
  arm's on all six, by at least **0.15**. **Falsifier**: any world below **0.10**; **null**: between.
- **AP5 -- and the aid swamps the draw.** The smallest of the six accuracy gains is more than **twice** the six
  worlds' own span on the `naive` arm, **0.0309**. **Falsifier**: the smallest gain at or below that span.
  **REFUSED** when `e410`'s artifact is absent. *This is the unit's own prediction: `e410` found the six draws to be
  one population and the arm is the term the corpus's own protocol changes, so what a benchmark of this setting
  measures is rehearsal and not the draw.*

**What it can do beyond that.** It completes the benchmark's own two-term comparison on the six worlds: the draw's
term is three hundredths and the arm's is thirteen to sixteen, measured on the same runs, so a user of this benchmark
can see which of the two the setting is about. It also puts `e371`'s rehearsal result -- a 0.2844 cut in the card's
world's forgetting -- beside the other five worlds' for the first time.

**What it cannot do.** *One rehearsal setting*: `--replay-per-task 16 --replay-batch 16`, so what is measured is the
corpus's own buffer and not the aid in general. *And the penalty arms are absent*: this cell was run with `naive` and
`replay` only, so `e276`'s replay-over-**penalty** contrast is not available here. *And the metric is the corpus's*:
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

#: the six worlds' 500-update runs, the same six `e410` read
RUNS = {
    "card": Path("runs/e380_earned_label_cue0_actionsource_20reps.json"),
    "cue1": Path("runs/e398_earned_label_cueseed1_iters500_20reps.json"),
    "cue3": Path("runs/e398_earned_label_cueseed3_iters500_20reps.json"),
    "cue6": Path("runs/e401_earned_label_cueseed6_iters500_20reps.json"),
    "cue9": Path("runs/e399_earned_label_cueseed9_iters500_20reps.json"),
    "cue14": Path("runs/e399_earned_label_cueseed14_iters500_20reps.json"),
}
#: `e410`'s artifact, which carries the `naive` arm's own span across the six worlds
PREVIOUS = Path("runs/e410_the_benchmarks_own_metric.json")
ARMS = ("naive", "replay")
N_TASKS = 3
MIN_WORLDS = 5
MIN_REPS = 20
GAIN = 0.10
GAIN_FIRES = 0.05
CUT = 0.15
CUT_FIRES = 0.10
SPAN_FALLBACK = 0.0309
TWICE = 2.0
CLAIMS = (
    ("AP1", f"and the second arm's matrices are carried, over at least {MIN_WORLDS} worlds and {MIN_REPS} replicates",
     "Each of the six worlds' runs carries, for the `replay` arm, twenty replicates with three-by-three retention "
     "matrices",
     "falsifier: any world missing them"),
    ("AP2", "and the rehearsal helps on every world",
     "The `replay` arm's mean final accuracy exceeds the `naive` arm's on all six worlds",
     "falsifier: any world where it does not"),
    ("AP3", f"and by at least a tenth, {GAIN:.2f}",
     "Every world's accuracy gain is at least 0.10",
     f"falsifier: any world below {GAIN_FIRES:.2f}; null: between"),
    ("AP4", f"and it cuts the forgetting on every world, by {CUT:.2f}",
     "The `replay` arm's mean forgetting is below the `naive` arm's on all six, by at least 0.15",
     f"falsifier: any world below {CUT_FIRES:.2f}; null: between"),
    ("AP5", f"and the aid swamps the draw, by {TWICE:.1f} times the naive span",
     "The smallest of the six accuracy gains is more than twice the six worlds' own span on the `naive` arm, 0.0309",
     "falsifier: the smallest gain at or below that span; refused when `e410`'s artifact is absent"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def reading(runs: dict = RUNS, previous: Path = PREVIOUS, arms=ARMS) -> dict:
    out = {"ok": True, "reason": None, "worlds": {}, "arms": list(arms), "previous": None}
    for name, path in runs.items():
        doc = load(path)
        if not doc:
            return {**out, "ok": False, "reason": f"world {name}: {path} is absent"}
        entry = {"artifact": path.name, "arms": {}}
        for arm in arms:
            reps = ((doc.get("methods") or {}).get(arm) or {}).get("replicates") or []
            if not reps:
                return {**out, "ok": False, "reason": f"world {name}: the {arm} arm carries no replicates"}
            matrices = [r.get("retention") for r in reps]
            complete = [m for m in matrices
                        if m and len(m) == N_TASKS and all(len(row) == N_TASKS for row in m)]
            if not complete:
                return {**out, "ok": False, "reason": f"world {name}: the {arm} arm carries no three-by-three "
                                                      f"matrix"}
            entry["arms"][arm] = {
                "replicates": len(reps), "matrices": len(complete),
                "final_accuracy": statistics.fmean([r["final_accuracy"] for r in reps]),
                "mean_forgetting": statistics.fmean([r["mean_forgetting"] for r in reps]),
                "final": [statistics.fmean([r["final_per_task"][k] for r in reps]) for k in range(N_TASKS)],
                "forgetting": [statistics.fmean([r["forgetting_per_task"][k] for r in reps])
                               for k in range(N_TASKS)],
            }
        entry["accuracy_gain"] = entry["arms"]["replay"]["final_accuracy"] - entry["arms"]["naive"]["final_accuracy"]
        entry["forgetting_cut"] = entry["arms"]["naive"]["mean_forgetting"] - entry["arms"]["replay"][
            "mean_forgetting"]
        out["worlds"][name] = entry
    naive = [out["worlds"][n]["arms"]["naive"]["final_accuracy"] for n in runs]
    out["spread"] = {"naive_accuracy": max(naive) - min(naive),
                     "replay_accuracy": max(out["worlds"][n]["arms"]["replay"]["final_accuracy"] for n in runs)
                     - min(out["worlds"][n]["arms"]["replay"]["final_accuracy"] for n in runs),
                     "accuracy_gain": max(out["worlds"][n]["accuracy_gain"] for n in runs)
                     - min(out["worlds"][n]["accuracy_gain"] for n in runs),
                     "forgetting_cut": max(out["worlds"][n]["forgetting_cut"] for n in runs)
                     - min(out["worlds"][n]["forgetting_cut"] for n in runs)}
    prev = load(previous)
    out["previous"] = ({"artifact": Path(previous).name,
                        "naive_span": float((prev.get("spread") or {}).get("final_accuracy"))} if prev else None)
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a world's run or its second arm is absent"}
                for c in CLAIMS]
    worlds = r["worlds"]
    short = {n: {"reps": w["arms"]["replay"]["replicates"], "matrices": w["arms"]["replay"]["matrices"]}
             for n, w in worlds.items()
             if w["arms"]["replay"]["replicates"] < MIN_REPS or w["arms"]["replay"]["matrices"] < MIN_REPS}
    j1 = {"id": "AP1", "measured": f"{len(worlds)} worlds, each carrying "
                                   f"{sorted({w['arms']['replay']['replicates'] for w in worlds.values()})} "
                                   f"replicates and "
                                   f"{sorted({w['arms']['replay']['matrices'] for w in worlds.values()})} "
                                   f"three-by-three matrices on the `replay` arm",
          "verdict": f"MET -- the second arm's matrices are carried on all {len(worlds)} worlds" if
                     (not short and len(worlds) >= MIN_WORLDS) else f"FALSIFIER FIRED -- {short}"}

    gain = {n: w["accuracy_gain"] for n, w in worlds.items()}
    worse = {n: round(v, 4) for n, v in gain.items() if v <= 0}
    j2 = {"id": "AP2", "measured": f"the replay-over-naive accuracy gains are "
                                   f"{ {n: round(v, 4) for n, v in sorted(gain.items(), key=lambda kv: kv[1])} }",
          "verdict": "MET -- the rehearsal helps on every world" if not worse else
          f"FALSIFIER FIRED -- {worse} gains nothing"}

    small = {n: round(v, 4) for n, v in gain.items() if v < GAIN}
    least = min(gain.values())
    j3 = {"id": "AP3", "measured": f"the smallest gain is {least:+.4f} on its world and the six gains span "
                                   f"{r['spread']['accuracy_gain']:.4f}",
          "verdict": f"MET -- every world gains at least a tenth, the least {least:+.4f}" if not small else
          f"FALSIFIER FIRED -- {small} is under the bar" if least < GAIN_FIRES else
          f"NULL -- {least:+.4f}, between {GAIN_FIRES:.2f} and {GAIN:.2f}"}

    cut = {n: w["forgetting_cut"] for n, w in worlds.items()}
    shallow = {n: round(v, 4) for n, v in cut.items() if v < CUT}
    least_cut = min(cut.values())
    j4 = {"id": "AP4", "measured": f"the forgetting cuts are "
                                   f"{ {n: round(v, 4) for n, v in sorted(cut.items(), key=lambda kv: kv[1])} }",
          "verdict": f"MET -- the rehearsal cuts the forgetting on every world, the least by {least_cut:.4f}" if
                     not shallow else
          f"FALSIFIER FIRED -- {shallow} is under the bar" if least_cut < CUT_FIRES else
          f"NULL -- {least_cut:.4f}, between {CUT_FIRES:.2f} and {CUT:.2f}"}

    if not r["previous"]:
        j5 = {"id": "AP5", "measured": "`e410`'s artifact is not on disk", "verdict": "REFUSED"}
    else:
        span = r["previous"]["naive_span"] or SPAN_FALLBACK
        good5 = least > TWICE * span
        j5 = {"id": "AP5", "measured": f"the smallest accuracy gain is {least:+.4f} against the six worlds' own span "
                                       f"of {span:.4f} on the `naive` arm, {least / span:.2f} times it",
              "verdict": f"MET -- the aid swamps the draw, {least / span:.2f} times the naive span" if good5 else
              f"FALSIFIER FIRED -- the smallest gain is {least / span:.2f} times the naive span"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the rehearsal on the six worlds ==")
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the rehearsal on the six worlds ==")
    print(f"   the `naive` and `replay` arms' retention on the six 500-update runs, {r['reps'] if 'reps' in r else 20} "
          f"replicates each")
    print(f"\n   {'world':>7} {'naive acc':>10} {'replay acc':>11} {'gain':>9} {'naive mf':>9} {'replay mf':>10} "
          f"{'cut':>8}")
    for n in sorted(r["worlds"], key=lambda x: -r["worlds"][x]["accuracy_gain"]):
        w = r["worlds"][n]
        print(f"   {n:>7} {w['arms']['naive']['final_accuracy']:10.4f} "
              f"{w['arms']['replay']['final_accuracy']:11.4f} {w['accuracy_gain']:+9.4f} "
              f"{w['arms']['naive']['mean_forgetting']:9.4f} {w['arms']['replay']['mean_forgetting']:10.4f} "
              f"{w['forgetting_cut']:+8.4f}")
    print(f"\n   the spans: { {k: round(v, 4) for k, v in r['spread'].items()} }")

    print("\n== the registered claims, AP1-AP5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e410` found the six worlds one population on the benchmark's own metric and registered that the")
    print("    second arm's retention was outside its reading; this reads it on the same runs)")
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
