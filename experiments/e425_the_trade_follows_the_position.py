"""E425 -- the trade follows the position, not the task: the same task is recovered first and cost last.

`e419` to `e422` read the buffer's per-task ledger on one order and found the oldest task recovered by a third and the
newest cost by a tenth, the recovery entirely retention and the cost entirely a learning term. `e424` wrote that into
the card. Every one of those units registered the same limit: *the corpus's three tasks in the as-built order*, so
whether the loss is the task's or the position's was open.

**This unit reads the corpus's own order axis.** Three configurations were rolled twice with `config.task_order` the
only field that differs, the second roll carrying the same three tasks in the reverse order: `e315` (`ov1_t0..t2`),
`e316` and `e317` (the assembly suite). Each roll has both arms. The question is one sentence: when the order moves,
does the gain move with the task or with the position? No training, no probe. Five claims, registered before this
unit's pass over the runs.

- **BA1 -- and the paired ledger is carried.** Three configurations, each rolled under both orders with `task_order`
  alone differing, the same task set in the other order, both arms present. **Falsifier**: any other field differing,
  a different task set, or a missing arm.
- **BA2 -- and the first-taught task gains more than the last-taught, in every roll.** Over the six rolls the gain at
  position 0 exceeds the gain at the last position. **Falsifier**: any roll where it does not.
- **BA3 -- and the last position is worth nothing, in every roll.** The last-taught task's gain is at most **+0.01**
  in every roll. **Falsifier**: any above **+0.05**. **Null**: between.
- **BA4 -- and the same task moves with its position.** For each configuration, take the task taught **first** in one
  roll and **last** in the other: its gain when taught first exceeds its gain when taught last by at least **0.05**,
  in both directions. **Falsifier**: any of the six contrasts below **0.02**. *This is the unit's own prediction: if
  the trade were the task's, the same task would gain the same under either order.*
- **BA5 -- and reversing the order costs the buffer.** The mean gain over the three tasks is lower under the reversed
  order in every configuration. **Falsifier**: any configuration where it rises.

**What it can do beyond that.** It settles the limit all four per-task units registered. `e316`'s `odour_identity` is
worth **+0.2333** when it is taught first and **-0.0104** when it is taught last; `e317`'s is worth **+0.2792** and
**-0.0208**; `e315`'s `ov1_t2` is worth **-0.0000** last and **+0.1042** first. So the trade is the sequence's and not
the task's, and the buffer's own worth is a property of where in the order its protection lands: reversing the suite
costs it **0.0028**, **0.0618** and **0.0694** of mean gain.

**What it cannot do.** *Three configurations and one protocol*: the `naive`/`replay` pair, the corpus's buffer and
`sizes` of three tasks where the middle one is left in place, so a full permutation is not in this reading. *And the
replicate counts are five, ten and five*: the assembly pair has ten replicates and the other two five, so the mean
gains carry the draws' own spread. *And the task sets are two*: the overlap suite's `ov1_t*` and the assembly suite's
three pathways, so the position effect is measured twice in one family and once in the other. *And the metric is the
corpus's*: the last task is never forgotten after it is taught, so its gain is a `learned` difference. *And a ledger
is not a mechanism.*
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: three configurations rolled under both orders, `task_order` the only field that differs
PAIRS = {
    "overlap": (Path("runs/e315_order_as_built.json"), Path("runs/e315_order_reverse.json")),
    "assembly": (Path("runs/e316_assembly_as_built.json"), Path("runs/e316_assembly_reverse.json")),
    "assembly-five": (Path("runs/e317_five_as_built.json"), Path("runs/e317_five_reverse.json")),
}
AS_BUILT, REVERSE = "as_built", "reverse"
ARMS = ("naive", "replay")
RUN_FIELDS = ("json_out", "save_theta")
MIN_CONFIGS = 3
MIN_REPS = 5
FIRST_OVER_LAST = 0.0
LAST_BAR = 0.01
LAST_FIRES = 0.05
POSITION = 0.05
POSITION_FIRES = 0.02
CLAIMS = (
    ("BA1", f"and the paired ledger is carried, over at least {MIN_CONFIGS} configurations",
     "Three configurations, each rolled under both orders with task_order alone differing, the same task set in the "
     "other order, both arms present",
     "falsifier: any other field differing, a different task set, or a missing arm"),
    ("BA2", "and the first-taught task gains more than the last-taught, in every roll",
     "Over the six rolls the gain at position 0 exceeds the gain at the last position",
     "falsifier: any roll where it does not"),
    ("BA3", f"and the last position is worth nothing, in every roll, {LAST_BAR:.2f}",
     "The last-taught task's gain is at most +0.01 in every roll",
     f"falsifier: any above {LAST_FIRES:+.2f}; null: between"),
    ("BA4", f"and the same task moves with its position, {POSITION:.2f}",
     "For each configuration the task taught first in one roll and last in the other gains at least 0.05 more when it "
     "is taught first, in both directions",
     f"falsifier: any of the six contrasts below {POSITION_FIRES:.2f}"),
    ("BA5", "and reversing the order costs the buffer",
     "The mean gain over the three tasks is lower under the reversed order in every configuration",
     "falsifier: any configuration where it rises"),
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
    got = {}
    for arm in ARMS:
        reps = ((doc.get("methods") or {}).get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        got[arm] = {"replicates": len(reps),
                    "final": [statistics.fmean([r["final_per_task"][k] for r in reps]) for k in range(len(tasks))]}
    gains = [got["replay"]["final"][k] - got["naive"]["final"][k] for k in range(len(tasks))]
    return {"artifact": path.name, "tasks": tasks, "per_task": dict(zip(tasks, gains)), "gain": gains,
            "replicates": min(got["naive"]["replicates"], got["replay"]["replicates"]), "doc": doc}


def reading(pairs: dict = PAIRS) -> dict:
    out = {"ok": True, "reason": None, "configs": {}}
    for name, (a_path, b_path) in pairs.items():
        a, b = _roll(a_path), _roll(b_path)
        if a is None:
            return {**out, "ok": False, "reason": f"configuration {name}: {a_path} is absent or carries no arm"}
        if b is None:
            return {**out, "ok": False, "reason": f"configuration {name}: {b_path} is absent or carries no arm"}
        ca, cb = (a["doc"].get("config") or {}), (b["doc"].get("config") or {})
        differing = sorted(k for k in set(ca) | set(cb) if k not in RUN_FIELDS and ca.get(k) != cb.get(k))
        first, last = a["tasks"][0], a["tasks"][-1]
        out["configs"][name] = {
            AS_BUILT: a, REVERSE: b, "differing_config": differing,
            "same_tasks": set(a["tasks"]) == set(b["tasks"]) and a["tasks"] == list(reversed(b["tasks"])),
            #: the same task taught first in one roll and last in the other, both ways
            "contrasts": {"first_then_last": {"task": first, "at_first": a["per_task"][first],
                                              "at_last": b["per_task"].get(first)},
                          "last_then_first": {"task": last, "at_last": a["per_task"][last],
                                              "at_first": b["per_task"].get(last)}}}
        for k, c in out["configs"][name]["contrasts"].items():
            c["difference"] = (c["at_first"] - c["at_last"]) if None not in (c["at_first"], c["at_last"]) else None
    rolls = [(n, o, c[o]) for n, c in out["configs"].items() for o in (AS_BUILT, REVERSE)]
    out["spans"] = {"configs": len(out["configs"]), "rolls": len(rolls),
                    "replicates": sorted({r["replicates"] for _, _, r in rolls}),
                    "worst_first_over_last": min(r["gain"][0] - r["gain"][-1] for _, _, r in rolls),
                    "worst_last": max(r["gain"][-1] for _, _, r in rolls),
                    "smallest_position_contrast": min(c["contrasts"][k]["difference"]
                                                      for c in out["configs"].values() for k in c["contrasts"]),
                    "mean_drops": {n: statistics.fmean(c[REVERSE]["gain"]) - statistics.fmean(c[AS_BUILT]["gain"])
                                   for n, c in out["configs"].items()}}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no arm"}
                for c in CLAIMS]
    cfg, s = r["configs"], r["spans"]
    broken = {n: {"differing": c["differing_config"], "same_tasks": c["same_tasks"]}
              for n, c in cfg.items() if c["differing_config"] != ["task_order"] or not c["same_tasks"]}
    thin = {n: {o: c[o]["replicates"] for o in (AS_BUILT, REVERSE)} for n, c in cfg.items()
            if any(c[o]["replicates"] < MIN_REPS for o in (AS_BUILT, REVERSE))}
    j1 = {"id": "BA1",
          "measured": f"{len(cfg)} configurations rolled under both orders at {s['replicates']} replicates, "
                      f"`task_order` the only differing field and the same tasks reversed",
          "verdict": f"MET -- the paired ledger is carried over {len(cfg)} configurations, {s['rolls']} rolls" if
                     (len(cfg) >= MIN_CONFIGS and not broken and not thin) else
                     f"FALSIFIER FIRED -- {broken or thin}"}
    rolls = [(n, o, c[o]) for n, c in cfg.items() for o in (AS_BUILT, REVERSE)]
    bad2 = {f"{n}/{o}": round(r["gain"][0] - r["gain"][-1], 4) for n, o, r in rolls if r["gain"][0] <= r["gain"][-1]}
    j2 = {"id": "BA2",
          "measured": f"the first-over-last margin runs {s['worst_first_over_last']:+.4f} to "
                      f"{max(r['gain'][0] - r['gain'][-1] for _, _, r in rolls):+.4f} over the {s['rolls']} rolls",
          "verdict": f"MET -- the first-taught task gains more than the last-taught in all {s['rolls']} rolls" if
                     not bad2 else f"FALSIFIER FIRED -- {bad2}"}
    last = {f"{n}/{o}": round(r["gain"][-1], 4) for n, o, r in rolls}
    j3 = {"id": "BA3",
          "measured": f"the last-taught task's gains are {dict(sorted(last.items(), key=lambda kv: -kv[1]))}",
          "verdict": f"MET -- the last position is worth at most {s['worst_last']:+.4f} in every roll" if
                     s["worst_last"] <= LAST_BAR else
                     f"FALSIFIER FIRED -- {s['worst_last']:+.4f} is over the bar" if s["worst_last"] > LAST_FIRES else
                     f"NULL -- {s['worst_last']:+.4f}, between {LAST_BAR:.2f} and {LAST_FIRES:.2f}"}
    contrasts = {f"{n}/{k}": round(c["contrasts"][k]["difference"], 4) for n, c in cfg.items() for k in c["contrasts"]}
    weak = {k: v for k, v in contrasts.items() if v < POSITION}
    j4 = {"id": "BA4",
          "measured": f"the six position contrasts -- the same task taught first against taught last -- are "
                      f"{dict(sorted(contrasts.items(), key=lambda kv: kv[1]))}",
          "verdict": f"MET -- the same task gains at least {s['smallest_position_contrast']:+.4f} more when it is "
                     f"taught first, in all six directions" if not weak else
                     f"FALSIFIER FIRED -- {weak}" if any(v < POSITION_FIRES for v in weak.values()) else
                     f"NULL -- {weak} between the bars"}
    drops = {k: round(v, 4) for k, v in s["mean_drops"].items()}
    j5 = {"id": "BA5",
          "measured": f"the reversed order's mean gain less the as-built one is {drops}",
          "verdict": f"MET -- reversing the order costs the buffer in every configuration, by "
                     f"{min(drops.values()):+.4f} to {max(drops.values()):+.4f}" if
                     all(v < 0 for v in drops.values()) else
                     f"FALSIFIER FIRED -- a configuration where it rises: { {k: v for k, v in drops.items() if v >= 0} }"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the trade follows the position, not the task ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   three configurations rolled under both orders, `task_order` the only field that differs")
    print(f"\n   {'configuration':>15} {'order':>10} {'tasks':>44} {'gain 0..2':>26} {'mean':>8}")
    for n, c in r["configs"].items():
        for o in (AS_BUILT, REVERSE):
            roll = c[o]
            print(f"   {n:>15} {o:>10} {'>'.join(roll['tasks'])[:44]:>44} "
                  + " ".join(f"{x:+.4f}" for x in roll["gain"])
                  + f" {statistics.fmean(roll['gain']):+8.4f}")
    print("\n   the same task, first against last:")
    for n, c in r["configs"].items():
        for k, con in c["contrasts"].items():
            print(f"      {n:>15} {k:>15}: {con['task']} at first {con['at_first']:+.4f} against at last "
                  f"{con['at_last']:+.4f}, a margin of {con['difference']:+.4f}")
    s = r["spans"]
    print(f"\n   {s['rolls']} rolls at {s['replicates']} replicates, the weakest position contrast "
          f"{s['smallest_position_contrast']:+.4f}, the mean drops { {k: round(v, 4) for k, v in s['mean_drops'].items()} }")
    print("\n== the registered claims, BA1-BA5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e419` to `e422` read the trade on one order and each registered that the order was fixed; `e315`,")
    print("    `e316` and `e317` rolled three configurations both ways)")
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
