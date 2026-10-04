"""E413 -- the aid turns on in every world: the rehearsal is worth nothing at twenty updates and a sixth at five hundred, on all six draws.

`e412` read the corpus's own budget ladder on the card's world -- twenty update budgets from 1 to 500, one
configuration, twenty replicates -- and found the aid worth nothing at or below 20 updates and ramping to **+0.1594**
at 500. It registered the reading's own scope as what it could not settle: *"one world and one arm pair: `cue0` with
the action source"*, so whether the turn-on is the setting's or that world's was open.

**This unit reads the other five worlds at the same three rungs.** `e405`, `e407` and the five-hundred-update runs
`e398`, `e399`, `e401` and `e380` roll **six** worlds -- the card's and five cue redraws -- at budgets **1**, **20**
and **500**, each at **twenty replicates** with both arms. No training, no probe. Five claims, registered before this
unit's pass over the eighteen runs.

- **AY1 -- and the eighteen runs are carried.** Six worlds at three budgets, each with both arms at **20** replicates,
  and each world's three runs one configuration. **Falsifier**: any missing, fewer replicates, or a shared field
  differing.
- **AY2 -- and at the two small budgets no world gains a twentieth.** At budgets **1** and **20**, every world's gain
  is below **0.05**. **Falsifier**: any at or above **0.10**; **null**: between. *This is the unit's own prediction:
  `e412`'s turn-on is the setting's, so at twenty updates no draw takes a tenth.*
- **AY3 -- and at five hundred every world gains a tenth.** Every world's gain at budget 500 is at least **0.10**.
  **Falsifier**: any below **0.05**; **null**: between.
- **AY4 -- and every world's rise clears a tenth.** The rise from budget 20 to 500 is at least **0.10** on all six.
  **Falsifier**: any below **0.05**; **null**: between.
- **AY5 -- and the aid's term beats the draw's.** The least world's rise is more than **twice** the six worlds' own
  span at budget 20. **Falsifier**: at or below twice that span.

**What it can do beyond that.** It turns `e412`'s one-world turn-on into the six draws' property, and it puts the
arm's term and the draw's term on the same axis for the first time: at budget 20 the six draws span
**0.0410** in the aid's gain, and every one of them rises by at least **+0.1142** to budget 500. It also gives the
small-budget band its own picture -- at twenty updates five of the six worlds gain up to **+0.0365** and the card's
world is the only one that loses, at **-0.0045**.

**What it cannot do.** *Three budgets are three points*: between 20 and 500 the corpus's budget axis has ten rungs on
the card's world alone, so the other five worlds' turn-on is located only between those two rungs. *And the arms are
the `naive`/`replay` pair*: the penalty arms are absent from all eighteen runs. *And the budget is not the level*: the
naive arm rises from about 0.25 at budget 1 to 0.52 to 0.55 at 500 along the same axis. *And the metric is the
corpus's*: `mean_forgetting` is the retention matrix's diagonal minus its last row, which `e305` showed cannot see the
part an arm never learned. *And a probe is not a mechanism.*
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: six worlds at three budgets, twenty replicates each: `e405` (1), `e407` (20) and the five-hundred-update runs
RUNS = {
    "card": {1: Path("runs/e405_earned_label_card_iters1_20reps.json"),
             20: Path("runs/e407_earned_label_card_iters20_20reps.json"),
             500: Path("runs/e380_earned_label_cue0_actionsource_20reps.json")},
    "cue1": {1: Path("runs/e405_earned_label_cue1_iters1_20reps.json"),
             20: Path("runs/e407_earned_label_cue1_iters20_20reps.json"),
             500: Path("runs/e398_earned_label_cueseed1_iters500_20reps.json")},
    "cue3": {1: Path("runs/e405_earned_label_cue3_iters1_20reps.json"),
             20: Path("runs/e407_earned_label_cue3_iters20_20reps.json"),
             500: Path("runs/e398_earned_label_cueseed3_iters500_20reps.json")},
    "cue6": {1: Path("runs/e405_earned_label_cue6_iters1_20reps.json"),
             20: Path("runs/e407_earned_label_cue6_iters20_20reps.json"),
             500: Path("runs/e401_earned_label_cueseed6_iters500_20reps.json")},
    "cue9": {1: Path("runs/e405_earned_label_cue9_iters1_20reps.json"),
             20: Path("runs/e407_earned_label_cue9_iters20_20reps.json"),
             500: Path("runs/e399_earned_label_cueseed9_iters500_20reps.json")},
    "cue14": {1: Path("runs/e405_earned_label_cue14_iters1_20reps.json"),
              20: Path("runs/e407_earned_label_cue14_iters20_20reps.json"),
              500: Path("runs/e399_earned_label_cueseed14_iters500_20reps.json")},
}
BUDGETS = (1, 20, 500)
SMALL = (1, 20)
ARMS = ("naive", "replay")
N_TASKS = 3
MIN_WORLDS = 5
MIN_REPS = 20
SMALL_GAIN = 0.05
SMALL_FIRES = 0.10
TOP = 0.10
TOP_FIRES = 0.05
RISE = 0.10
RISE_FIRES = 0.05
TWICE = 2.0
CLAIMS = (
    ("AY1", f"and the eighteen runs are carried, over at least {MIN_WORLDS} worlds and {MIN_REPS} replicates",
     "Six worlds at three budgets, each with both arms at twenty replicates, and each world's three runs one "
     "configuration",
     "falsifier: any missing, fewer replicates, or a shared field differing"),
    ("AY2", f"and at the two small budgets no world gains a twentieth, {SMALL_GAIN:.2f}",
     "At budgets 1 and 20 every world's accuracy gain is below 0.05",
     f"falsifier: any at or above {SMALL_FIRES:.2f}; null: between"),
    ("AY3", f"and at five hundred every world gains a tenth, {TOP:.2f}",
     "Every world's gain at budget 500 is at least 0.10",
     f"falsifier: any below {TOP_FIRES:.2f}; null: between"),
    ("AY4", f"and every world's rise clears a tenth, {RISE:.2f}",
     "The rise from budget 20 to 500 is at least 0.10 on all six",
     f"falsifier: any below {RISE_FIRES:.2f}; null: between"),
    ("AY5", f"and the aid's term beats the draw's, by {TWICE:.1f} times the six worlds' span at twenty",
     "The least world's rise is more than twice the six worlds' own span at budget 20",
     "falsifier: at or below twice that span"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _fingerprint(doc: dict) -> str:
    """The run's configuration: the circuit, the read-out draw, the environment draw and the task list."""
    return json.dumps({k: doc.get(k) for k in ("circuit", "readout", "env_draw", "tasks")}, sort_keys=True)


def reading(runs: dict = RUNS, arms=ARMS) -> dict:
    out = {"ok": True, "reason": None, "budgets": list(BUDGETS), "arms": list(arms), "worlds": {}}
    for name, by_budget in runs.items():
        entry = {"runs": {}, "configurations": 0}
        marks = set()
        for budget in BUDGETS:
            path = by_budget[budget]
            doc = load(path)
            if not doc:
                return {**out, "ok": False, "reason": f"world {name} at budget {budget}: {path} is absent"}
            marks.add(_fingerprint(doc))
            arms_out = {}
            for arm in arms:
                reps = ((doc.get("methods") or {}).get(arm) or {}).get("replicates") or []
                if not reps:
                    return {**out, "ok": False,
                            "reason": f"world {name} at budget {budget}: the {arm} arm carries no replicates"}
                arms_out[arm] = {
                    "replicates": len(reps),
                    "final_accuracy": statistics.fmean([r["final_accuracy"] for r in reps]),
                    "mean_forgetting": statistics.fmean([r["mean_forgetting"] for r in reps]),
                    "final": [statistics.fmean([r["final_per_task"][k] for r in reps]) for k in range(N_TASKS)],
                    "forgetting": [statistics.fmean([r["forgetting_per_task"][k] for r in reps])
                                   for k in range(N_TASKS)],
                }
            entry["runs"][str(budget)] = {"artifact": path.name, "arms": arms_out,
                                          "gain": arms_out["replay"]["final_accuracy"]
                                          - arms_out["naive"]["final_accuracy"],
                                          "cut": arms_out["naive"]["mean_forgetting"]
                                          - arms_out["replay"]["mean_forgetting"]}
        entry["configurations"] = len(marks)
        entry["gain_rise"] = entry["runs"]["500"]["gain"] - entry["runs"]["20"]["gain"]
        out["worlds"][name] = entry
    small = [w["runs"][str(b)]["gain"] for w in out["worlds"].values() for b in SMALL]
    at20 = [w["runs"]["20"]["gain"] for w in out["worlds"].values()]
    rises = [w["gain_rise"] for w in out["worlds"].values()]
    out["spans"] = {"worlds": len(out["worlds"]), "small_max": max(small), "small_min": min(small),
                    "span_at_20": max(at20) - min(at20), "least_top": min(w["runs"]["500"]["gain"]
                                                                          for w in out["worlds"].values()),
                    "least_rise": min(rises)}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a world's run is absent"}
                for c in CLAIMS]
    worlds = r["worlds"]
    thin = {n: {str(b): w["runs"][str(b)]["arms"]["naive"]["replicates"] for b in BUDGETS}
            for n, w in worlds.items()
            if any(w["runs"][str(b)]["arms"][a]["replicates"] < MIN_REPS for b in BUDGETS for a in ARMS)}
    split = {n: w["configurations"] for n, w in worlds.items() if w["configurations"] != 1}
    reps_seen = sorted({w["runs"][str(b)]["arms"]["naive"]["replicates"]
                        for w in worlds.values() for b in BUDGETS})
    j1 = {"id": "AY1",
          "measured": f"{len(worlds)} worlds at {len(BUDGETS)} budgets each, {reps_seen} replicates on both arms, "
                      f"and each world's three runs one configuration",
          "verdict": f"MET -- the eighteen runs are carried over {len(worlds)} worlds, one configuration each"
                     if (len(worlds) >= MIN_WORLDS and not thin and not split) else
                     f"FALSIFIER FIRED -- {thin or {'configurations': split}}"}
    worst = max((w["runs"][str(b)]["gain"], n, b) for n, w in worlds.items() for b in SMALL)
    j2 = {"id": "AY2",
          "measured": f"over the {len(worlds) * len(SMALL)} runs at budgets {SMALL} the largest gain is "
                      f"{worst[0]:+.4f} on {worst[1]} at {worst[2]}, the smallest {r['spans']['small_min']:+.4f}",
          "verdict": f"MET -- no world gains a twentieth at the small budgets, the most {worst[0]:+.4f}"
                     if worst[0] < SMALL_GAIN else
                     f"FALSIFIER FIRED -- {worst[0]:+.4f} is under the small-budget bar" if worst[0] >= SMALL_FIRES
                     else f"NULL -- {worst[0]:+.4f}, between {SMALL_GAIN:.2f} and {SMALL_FIRES:.2f}"}
    tops = {n: w["runs"]["500"]["gain"] for n, w in worlds.items()}
    least = min(tops.values())
    j3 = {"id": "AY3",
          "measured": f"at budget 500 the gains are "
                      f"{ {n: round(v, 4) for n, v in sorted(tops.items(), key=lambda kv: kv[1])} }",
          "verdict": f"MET -- every world gains a tenth at five hundred, the least {least:+.4f}" if least >= TOP
                     else f"FALSIFIER FIRED -- {least:+.4f} is under the bar" if least < TOP_FIRES
                     else f"NULL -- {least:+.4f}, between {TOP_FIRES:.2f} and {TOP:.2f}"}
    rises = {n: w["gain_rise"] for n, w in worlds.items()}
    least_rise = min(rises.values())
    j4 = {"id": "AY4",
          "measured": f"the rises from budget 20 to 500 are "
                      f"{ {n: round(v, 4) for n, v in sorted(rises.items(), key=lambda kv: kv[1])} }",
          "verdict": f"MET -- every world's rise clears a tenth, the least {least_rise:+.4f}" if least_rise >= RISE
                     else f"FALSIFIER FIRED -- {least_rise:+.4f} is under the bar" if least_rise < RISE_FIRES
                     else f"NULL -- {least_rise:+.4f}, between {RISE_FIRES:.2f} and {RISE:.2f}"}
    span = r["spans"]["span_at_20"]
    j5 = {"id": "AY5",
          "measured": f"the least rise {least_rise:+.4f} against the six worlds' own span at twenty, "
                      f"{span:.4f}, {least_rise / span:.2f} times it" if span else
                      "the six worlds' gains at twenty are one value, so their span is zero",
          "verdict": f"MET -- the aid's term beats the draw's, {least_rise / span:.2f} times the twenty-update span"
                     if (span and least_rise > TWICE * span) else
                     f"FALSIFIER FIRED -- the least rise is {least_rise / span:.2f} times the twenty-update span"
                     if span else "FALSIFIER FIRED -- the twenty-update span is zero"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the aid turns on in every world ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a world is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the six worlds' `naive` and `replay` arms at budgets 1, 20 and 500, twenty replicates each")
    print(f"\n   {'world':>7} {'naive 1':>8} {'naive 20':>9} {'naive 500':>10} {'gain 1':>8} {'gain 20':>9} "
          f"{'gain 500':>9} {'rise':>8} {'cuts 1/20/500':>22}")
    for n in sorted(r["worlds"], key=lambda x: -r["worlds"][x]["gain_rise"]):
        w = r["worlds"][n]
        accs = [w["runs"][str(b)]["arms"]["naive"]["final_accuracy"] for b in BUDGETS]
        gs = [w["runs"][str(b)]["gain"] for b in BUDGETS]
        cuts = "/".join(f"{w['runs'][str(b)]['cut']:+.3f}" for b in BUDGETS)
        print(f"   {n:>7} {accs[0]:8.4f} {accs[1]:9.4f} {accs[2]:10.4f} {gs[0]:+8.4f} {gs[1]:+9.4f} "
              f"{gs[2]:+9.4f} {w['gain_rise']:+8.4f} {cuts:>22}")
    s = r["spans"]
    print(f"\n   the small-budget band {s['small_min']:+.4f} to {s['small_max']:+.4f}, the six worlds' span at "
          f"twenty {s['span_at_20']:.4f}, the least top gain {s['least_top']:+.4f}, the least rise "
          f"{s['least_rise']:+.4f}")
    print("\n== the registered claims, AY1-AY5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e412` read the card's world's twenty-rung ladder and named one world as what it could not settle;")
    print("    this reads the other five at the ladder's two ends)")
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
