"""E434 -- the game card, revision 7: the parameters clause, where each arm spends its movement.

`e427` found three quarters of the buffer's worth in the head's bias; `e430` read the bias trajectory on two cells;
`e431` pooled every paired cell's bias ratio and found the penalties leaving the bias furthest from where the sequence
started; `e432` read the corpus's own interference account and found it reading the penalised arms mostly through the
bias; `e433` read the weights beside the bias and found the two parameters ordering the arms oppositely. None of that
is in the card.

**This unit writes revision 7.** One clause is added and every other field is checked equal to `e428`'s card rather
than restated: the **parameters** clause, carrying each arm's bias ratio, its drift ratio, the share of cells in which
the two move opposite ways, the interference account's bias share, and the control's own zero. Every number is read
from the artifact that measured it. No training and no roll. Five claims, registered before this unit read any of them.

- **BJ1 -- and the sixth revision is carried unchanged where it is not rewritten.** Every field of `e428`'s card except
  the revision and the new clause is equal to the revision-6 card, with the revision now **7**. **Falsifier**: any
  other field differing; **REFUSED** when `e428`'s artifact is absent.
- **BJ2 -- and the clause's bias half is `e431`'s.** Each arm's mean bias ratio and the share of its cells below the
  baseline's equal the ledger's. **Falsifier**: any number disagreeing with that artifact; **REFUSED** when it is
  absent.
- **BJ3 -- and its weights half is `e433`'s.** Each arm's mean drift ratio equals that ledger's. **Falsifier**: any
  number disagreeing; **REFUSED** when it is absent.
- **BJ4 -- and its joint half is `e433`'s.** Each arm's share of cells in which the drift is below the baseline's and
  the bias above it equals that artifact's. **Falsifier**: any number disagreeing.
- **BJ5 -- and its channel half is `e432`'s.** Each arm's bias share of the interference account, on both live rolls,
  equals that artifact's, and the frozen side's maximum is its own **0.0**. **Falsifier**: any number disagreeing;
  **REFUSED** when it is absent.

**What it can do beyond that.** It is the card a reader can act on when asking what an arm changes: the bias ratio of
every arm over the corpus's **207** paired cells, the drift ratio beside it, the joint pattern, and the channel the
corpus's own interference account reads the arm through -- with the two ledgers agreeing cell for cell, so a revision
that moves either number turns the unit red.

**What it cannot do.** *A card is a definition and not a result*: it states what the benchmark is and points at the
artifacts for every number. *And the clause is the corpus's own aggregates*: the ratios are per cell over cells that
are not independent samples, and the drift is the runner's per-task reading. *And the clauses are only checked against
each other*: BJ1 shows revision 6 survives into revision 7 and not that revision 6 was right. *And the clause says
where the parameters go and not why.*
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the artifacts every clause is read from
CARD6 = Path("runs/e428_the_game_card_revision_six.json")
BIAS = Path("runs/e431_the_bias_ledger.json")
PARAMS = Path("runs/e433_the_penalties_hold_the_weights.json")
CHANNEL = Path("runs/e432_the_interference_runs_through_the_bias.json")
REVISION = 7
NEW = ("revision", "parameters")
ARMS = ("replay", "ewc", "ewc-block", "ewc-block-rand")
ROLLS = ("cell", "pair/plastic")
TOL = 0.002
SHARE_TOL = 0.005
EXPECTED = {"cells": 207, "frozen_max": 0.0}
CLAIMS = (
    ("BJ1", "and the sixth revision is carried unchanged where it is not rewritten",
     "Every field of `e428`'s card except the revision and the new clause is equal to the revision-6 card, with the "
     "revision now 7",
     "falsifier: any other field differing; refused when `e428`'s artifact is absent"),
    ("BJ2", "and the clause's bias half is `e431`'s",
     "Each arm's mean bias ratio and the share of its cells below the baseline's equal the ledger's",
     "falsifier: any number disagreeing with that artifact; refused when it is absent"),
    ("BJ3", "and its weights half is `e433`'s",
     "Each arm's mean drift ratio equals that ledger's",
     "falsifier: any number disagreeing; refused when it is absent"),
    ("BJ4", "and its joint half is `e433`'s",
     "Each arm's share of cells in which the drift is below the baseline's and the bias above it equals that "
     "artifact's",
     "falsifier: any number disagreeing"),
    ("BJ5", "and its channel half is `e432`'s",
     "Each arm's bias share of the interference account on both live rolls equals that artifact's, and the frozen "
     "side's maximum is its own 0.0",
     "falsifier: any number disagreeing; refused when it is absent"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def reading(card6: Path = CARD6, bias: Path = BIAS, params: Path = PARAMS, channel: Path = CHANNEL) -> dict:
    out = {"ok": True, "reason": None, "card": None, "revision6": {}, "parameters": {}}
    base = load(card6)
    if not base:
        return {**out, "ok": False, "reason": f"{card6} is absent, so revision 6 is not on disk"}
    old = base.get("card") or {}
    card = copy.deepcopy(old)
    card["revision"] = REVISION
    out["revision6"] = {k: v for k, v in old.items() if k not in NEW}

    b = load(bias)
    if not b:
        return {**out, "ok": False, "reason": f"{bias} is absent, so the bias half has no reading"}
    p = load(params)
    if not p:
        return {**out, "ok": False, "reason": f"{params} is absent, so the weights half has no reading"}
    c = load(channel)
    if not c:
        return {**out, "ok": False, "reason": f"{channel} is absent, so the channel half has no reading"}
    by_bias, by_par = b.get("by_arm") or {}, p.get("by_arm") or {}
    card["parameters"] = {
        "artifact": [Path(bias).name, Path(params).name, Path(channel).name],
        "cells": (b.get("spans") or {}).get("cells"),
        "bias_ratio": {a: by_bias[a]["mean_ratio"] for a in ARMS if a in by_bias},
        "bias_below_share": {a: by_bias[a]["below_share"] for a in ARMS if a in by_bias},
        "drift_ratio": {a: by_par[a]["mean_drift_ratio"] for a in ARMS if a in by_par},
        "joint_share": {a: by_par[a]["both_share"] for a in ARMS if a in by_par},
        "channel_bias_share": {lbl: {a: (c["rolls"][lbl]["arms"][a]["share"])
                                     for a in sorted(c["rolls"][lbl]["arms"])} for lbl in ROLLS},
        "frozen_bias_max": (c.get("spans") or {}).get("frozen_bias_max")}
    out["parameters"] = dict(card["parameters"])
    out["sources"] = {"bias": by_bias, "params": by_par,
                      "channel": {lbl: c["rolls"][lbl]["arms"] for lbl in ROLLS}}
    out["card"] = card
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the clause is read from is absent"}
                for c in CLAIMS]
    card, e = r["card"], EXPECTED
    same = {k: (card.get(k) == v) for k, v in r["revision6"].items()}
    j1 = {"id": "BJ1",
          "measured": f"the revision-6 card's {len(same)} fields against the revision-7 card: "
                      f"{len(same) - sum(1 for v in same.values() if not v)} equal, with the revision now "
                      f"{card.get('revision')}",
          "verdict": f"MET -- the sixth revision is carried unchanged in all {len(same)} fields it does not rewrite" if
                     (all(same.values()) and card.get("revision") == REVISION) else
                     f"FALSIFIER FIRED -- { {k: v for k, v in same.items() if not v} } differs"}
    par, src = card["parameters"], r["sources"]
    bad2 = {a: (par["bias_ratio"].get(a), src["bias"][a]["mean_ratio"]) for a in par["bias_ratio"]
            if abs(par["bias_ratio"][a] - src["bias"][a]["mean_ratio"]) > TOL}
    bad2.update({f"{a}/below": (par["bias_below_share"].get(a), src["bias"][a]["below_share"])
                 for a in par["bias_below_share"]
                 if abs(par["bias_below_share"][a] - src["bias"][a]["below_share"]) > SHARE_TOL})
    j2 = {"id": "BJ2",
          "measured": f"the clause's bias ratios are { {a: round(v, 4) for a, v in par['bias_ratio'].items()} } and "
                      f"its below-shares { {a: round(v, 4) for a, v in par['bias_below_share'].items()} }, over "
                      f"{par['cells']} cells",
          "verdict": "MET -- the clause's bias half is the ledger's own numbers" if not bad2 else
          f"FALSIFIER FIRED -- {bad2}"}
    bad3 = {a: (par["drift_ratio"].get(a), src["params"][a]["mean_drift_ratio"]) for a in par["drift_ratio"]
            if abs(par["drift_ratio"][a] - src["params"][a]["mean_drift_ratio"]) > TOL}
    j3 = {"id": "BJ3",
          "measured": f"the clause's drift ratios are { {a: round(v, 4) for a, v in par['drift_ratio'].items()} }",
          "verdict": "MET -- the clause's weights half is the ledger's own numbers" if not bad3 else
          f"FALSIFIER FIRED -- {bad3}"}
    bad4 = {a: (par["joint_share"].get(a), src["params"][a]["both_share"]) for a in par["joint_share"]
            if abs(par["joint_share"][a] - src["params"][a]["both_share"]) > SHARE_TOL}
    j4 = {"id": "BJ4",
          "measured": f"the clause's joint shares are { {a: round(v, 4) for a, v in par['joint_share'].items()} }",
          "verdict": "MET -- the clause's joint half is the artifact's own numbers" if not bad4 else
          f"FALSIFIER FIRED -- {bad4}"}
    bad5 = {}
    for lbl in ROLLS:
        for a, shares in (par["channel_bias_share"].get(lbl) or {}).items():
            got = src["channel"][lbl][a]["share"]
            if len(shares) != len(got) or any(abs(x - y) > TOL for x, y in zip(shares, got)):
                bad5[f"{lbl}/{a}"] = (shares, got)
    if abs((par["frozen_bias_max"] or 0.0) - e["frozen_max"]) > 1e-9:
        bad5["frozen_bias_max"] = (par["frozen_bias_max"], e["frozen_max"])
    j5 = {"id": "BJ5",
          "measured": f"the clause's channel shares are "
                      f"{ {lbl: {a: [round(x, 4) for x in v] for a, v in (par['channel_bias_share'].get(lbl) or {}).items()} for lbl in ROLLS} }"
                      f" with the frozen side at {par['frozen_bias_max']:.1e}",
          "verdict": "MET -- the clause's channel half is the artifact's own numbers, the control's zero included" if
                     not bad5 else f"FALSIFIER FIRED -- {bad5}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the game card, revision 7 ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    card = r["card"]
    print(f"   {card.get('name')}, revision {card.get('revision')}, read 2026-10-06")
    print(f"\n   arms:       {card.get('arms')}")
    print(f"   absent:     {card.get('absent')}")
    print("\n   and the clauses, each with the artifact it is read from:")
    for k in ("world", "stream", "recovery", "invariance", "arm", "draw_terms", "penalty", "trade", "terms",
              "arm_terms", "order", "controls"):
        print(f"   {k + ':':<12} {card.get(k)}")
    p = card["parameters"]
    print(f"\n   parameters: over {p['cells']} cells, {p['artifact']}")
    print(f"      bias ratio        { {a: round(v, 4) for a, v in p['bias_ratio'].items()} }")
    print(f"      drift ratio       { {a: round(v, 4) for a, v in p['drift_ratio'].items()} }")
    print(f"      joint share       { {a: round(v, 4) for a, v in p['joint_share'].items()} }")
    print(f"      channel shares    { {lbl: {a: [round(x, 4) for x in v] for a, v in arms.items()} for lbl, arms in p['channel_bias_share'].items()} }")
    print(f"      the frozen side   {p['frozen_bias_max']:.1e}")
    print("\n== the registered claims, BJ1-BJ5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e428` wrote the order and the controls into the card; `e431` to `e433` measured where each arm spends")
    print("    its movement, which is what this carries)")
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
