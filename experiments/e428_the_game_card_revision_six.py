"""E428 -- the game card, revision 6: the order clause and the controls clause.

`e418` gave the card its third arm and `e424` revision 5 the trade. `e425`, `e426` and `e427` then measured two things
the card still does not say: that the trade follows the **position** in the sequence and that reversing the order
costs the buffer (`e425`, `e426`), and what the corpus's own **controls** remove -- the aid is worth nothing on a
frozen body (`e417`) and under a frozen bias keeps a quarter of its worth (`e427`).

**This unit writes revision 6.** Two clauses are added and every other field is checked equal to `e424`'s card rather
than restated: the **order** clause, at both the buffer's level and every arm's, and the **controls** clause. Every
number is read from the artifact that measured it. No training and no roll. Five claims, registered before this unit
read any of them.

- **BD1 -- and the fifth revision is carried unchanged where it is not rewritten.** Every field of `e424`'s card
  except the revision and the two new clauses -- the substrate, loop, protocol, metrics, arms, absence list, the world,
  stream, recovery and invariance clauses, the buffer clause, the draw terms, the penalty clause, the trade and the
  terms -- is equal to the revision-5 card, with the revision now **6**. **Falsifier**: any other field differing;
  **REFUSED** when `e424`'s artifact is absent.
- **BD2 -- and the order clause is `e425`'s and `e426`'s.** Three configurations rolled both ways, the same task
  taught first against taught last at least **+0.0583** in all six contrasts, the reversal costing the buffer
  **-0.0028**, **-0.0618** and **-0.0694**, and over the sixteen arm-rolls the first position ahead in **all sixteen**
  with the buffer's mean positive in **6 of 6** against the penalties' negative in **10 of 10**. **Falsifier**: any
  number disagreeing with either artifact; **REFUSED** when either is absent.
- **BD3 -- and the clause carries where each arm's damage falls.** The buffer's worst position is the last in **6 of
  6** rolls and the penalties' worst the middle in **9 of 10**. **Falsifier**: either number disagreeing with
  `e426`'s artifact.
- **BD4 -- and the controls clause's first half is `e417`'s.** The corpus's frozen-body cells are **3**, the largest of
  their gains in absolute value **0.0017** and their forgetting cuts **exactly zero**. **Falsifier**: any number
  disagreeing; **REFUSED** when it is absent.
- **BD5 -- and its second half is `e427`'s.** With the bias frozen the buffer's gain and cut are **0.27** of the
  plastic pair's and the `naive` arm's own forgetting falls by **0.0523**. **Falsifier**: any number disagreeing;
  **REFUSED** when it is absent.

**What it can do beyond that.** It is the card a reader can act on, with the two things a user of a fixed-order
benchmark needs: that the credit and the damage follow the position rather than the task, so a comparison across
suites is a comparison of orders as much as of tasks; and how much of an arm's worth the corpus's own controls remove,
so a headline number can be read against what is left when the body or the bias is frozen.

**What it cannot do.** *A card is a definition and not a result*: it states what the benchmark is and points at the
artifacts for every number. *And the clauses are one protocol's*: three tasks with the middle left in place, so a full
permutation is not measured. *And the controls are the corpus's two flags*: a frozen body and a frozen bias, not a
frozen head or a frozen input. *And the clauses are only checked against each other*: BD1 shows revision 5 survives
into revision 6 and not that revision 5 was right. *And a clause is not an experiment.*
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the artifacts every clause is read from
CARD5 = Path("runs/e424_the_game_card_revision_five.json")
POSITION = Path("runs/e425_the_trade_follows_the_position.json")
ARMS = Path("runs/e426_the_damage_lands_by_arm.json")
BODY = Path("runs/e417_the_aid_needs_a_plastic_body.json")
BIAS = Path("runs/e427_most_of_the_aid_needs_a_plastic_bias.json")
REVISION = 6
NEW = ("revision", "order", "controls")
TOL = 0.002
RATIO_TOL = 0.01
EXPECTED = {
    "rolls": 16, "configs": 3, "position_contrast_min": 0.0583, "drops": (-0.0694, -0.0618, -0.0028),
    "first_ahead": 16, "first_positive": 15, "buffer_positive_means": 6, "buffer_rolls": 6,
    "penalty_negative_means": 10, "penalty_rolls": 10, "buffer_worst_last": 6, "penalty_worst_middle": 9,
    "frozen_cells": 3, "frozen_worst_gain": 0.0017, "gain_ratio": 0.27, "cut_ratio": 0.27,
    "naive_drop": 0.0523,
}
CLAIMS = (
    ("BD1", "and the fifth revision is carried unchanged where it is not rewritten",
     "Every field of `e424`'s card except the revision and the two new clauses is equal to the revision-5 card, with "
     "the revision now 6",
     "falsifier: any other field differing; refused when `e424`'s artifact is absent"),
    ("BD2", "and the order clause is `e425`'s and `e426`'s",
     "Three configurations rolled both ways with the same task's first-against-last margin at least 0.0583 in all six "
     "contrasts, the reversal costing the buffer 0.0028, 0.0618 and 0.0694, and over sixteen arm-rolls the first "
     "position ahead in all sixteen with the buffer's mean positive in 6 of 6 against the penalties' 10 of 10 negative",
     "falsifier: any number disagreeing with either artifact; refused when either is absent"),
    ("BD3", "and the clause carries where each arm's damage falls",
     "The buffer's worst position is the last in 6 of 6 rolls and the penalties' worst the middle in 9 of 10",
     "falsifier: either number disagreeing with `e426`'s artifact"),
    ("BD4", "and the controls clause's first half is `e417`'s",
     "The corpus's frozen-body cells are 3, the largest of their gains in absolute value 0.0017 and their forgetting "
     "cuts exactly zero",
     "falsifier: any number disagreeing; refused when it is absent"),
    ("BD5", "and its second half is `e427`'s",
     "With the bias frozen the buffer's gain and cut are 0.27 of the plastic pair's and the naive arm's own forgetting "
     "falls by 0.0523",
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


def reading(card5: Path = CARD5, position: Path = POSITION, arms: Path = ARMS, body: Path = BODY,
            bias: Path = BIAS) -> dict:
    out = {"ok": True, "reason": None, "card": None, "revision5": {}, "order": {}, "controls": {}}
    base = load(card5)
    if not base:
        return {**out, "ok": False, "reason": f"{card5} is absent, so revision 5 is not on disk"}
    old = base.get("card") or {}
    card = copy.deepcopy(old)
    card["revision"] = REVISION
    out["revision5"] = {k: v for k, v in old.items() if k not in NEW}

    pos = load(position)
    if not pos:
        return {**out, "ok": False, "reason": f"{position} is absent, so the order clause has no reading"}
    pspans = pos.get("spans") or {}
    ar = load(arms)
    if not ar:
        return {**out, "ok": False, "reason": f"{arms} is absent, so the order clause has no arm reading"}
    aspans = ar.get("spans") or {}
    drops = pspans.get("mean_drops") or {}
    card["order"] = {"artifact": [Path(position).name, Path(arms).name],
                     "configs": len(pos.get("configs") or {}), "rolls": aspans.get("rolls"),
                     "position_contrast_min": pspans.get("smallest_position_contrast"),
                     "reversal_costs": sorted(round(v, 4) for v in drops.values()),
                     "first_ahead": aspans.get("first_ahead"), "first_positive": aspans.get("first_positive"),
                     "buffer_positive_means": aspans.get("buffer_positive_means"),
                     "buffer_rolls": aspans.get("buffer_rolls"),
                     "penalty_negative_means": aspans.get("penalty_negative_means"),
                     "penalty_rolls": aspans.get("penalty_rolls"),
                     "buffer_worst_last": aspans.get("buffer_worst_last"),
                     "penalty_worst_middle": aspans.get("penalty_worst_middle")}
    out["order"] = dict(card["order"])

    b = load(body)
    if not b:
        return {**out, "ok": False, "reason": f"{body} is absent, so the frozen-body half has no reading"}
    frozen = b.get("frozen") or []
    bi = load(bias)
    if not bi:
        return {**out, "ok": False, "reason": f"{bias} is absent, so the frozen-bias half has no reading"}
    bspans = bi.get("spans") or {}
    card["controls"] = {"artifact": [Path(body).name, Path(bias).name],
                        "frozen_body_cells": len(frozen),
                        "frozen_body_worst_gain": max((abs(c["gain"]) for c in frozen), default=None),
                        "frozen_body_worst_cut": max((abs(c["cut"]) for c in frozen), default=None),
                        "frozen_bias_gain_ratio": bspans.get("gain_ratio"),
                        "frozen_bias_cut_ratio": bspans.get("cut_ratio"),
                        "frozen_bias_naive_forgetting_drop": (
                            (bspans.get("plastic_naive_mf") or 0.0) - (bspans.get("frozen_naive_mf") or 0.0))}
    out["controls"] = dict(card["controls"])
    out["card"] = card
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the clause is read from is absent"}
                for c in CLAIMS]
    card, e = r["card"], EXPECTED
    same = {k: (card.get(k) == v) for k, v in r["revision5"].items()}
    j1 = {"id": "BD1",
          "measured": f"the revision-5 card's {len(same)} fields against the revision-6 card: "
                      f"{len(same) - sum(1 for v in same.values() if not v)} equal, with the revision now "
                      f"{card.get('revision')}",
          "verdict": f"MET -- the fifth revision is carried unchanged in all {len(same)} fields it does not rewrite" if
                     (all(same.values()) and card.get("revision") == REVISION) else
                     f"FALSIFIER FIRED -- { {k: v for k, v in same.items() if not v} } differs"}
    od = r["order"]
    drops = od["reversal_costs"]
    good2 = (od["configs"] == e["configs"] and od["rolls"] == e["rolls"]
             and abs((od["position_contrast_min"] or 0.0) - e["position_contrast_min"]) < TOL
             and len(drops) == len(e["drops"])
             and all(abs(a - b) < TOL for a, b in zip(drops, e["drops"]))
             and od["first_ahead"] == e["first_ahead"] and od["first_positive"] == e["first_positive"]
             and od["buffer_positive_means"] == e["buffer_positive_means"] and od["buffer_rolls"] == e["buffer_rolls"]
             and od["penalty_negative_means"] == e["penalty_negative_means"]
             and od["penalty_rolls"] == e["penalty_rolls"])
    j2 = {"id": "BD2",
          "measured": f"`{'` and `'.join(od['artifact'])}` read {od['configs']} configurations rolled both ways, the "
                      f"weakest position contrast {od['position_contrast_min']:+.4f}, the reversal's costs "
                      f"{drops}, and {od['first_ahead']} of {od['rolls']} arm-rolls with the first position ahead, the "
                      f"buffer's mean positive in {od['buffer_positive_means']} of {od['buffer_rolls']} against the "
                      f"penalties' {od['penalty_negative_means']} of {od['penalty_rolls']} negative",
          "verdict": "MET -- the order clause is the two artifacts' own numbers" if good2 else
          f"FALSIFIER FIRED -- { {k: od[k] for k in ('configs', 'rolls', 'position_contrast_min', 'first_ahead')} }"}
    good3 = (od["buffer_worst_last"] == e["buffer_worst_last"]
             and od["penalty_worst_middle"] == e["penalty_worst_middle"]
             and od["buffer_rolls"] == e["buffer_rolls"] and od["penalty_rolls"] == e["penalty_rolls"])
    j3 = {"id": "BD3",
          "measured": f"the buffer's worst position is the last in {od['buffer_worst_last']} of {od['buffer_rolls']} "
                      f"rolls and the penalties' worst is the middle in {od['penalty_worst_middle']} of "
                      f"{od['penalty_rolls']}",
          "verdict": "MET -- the clause carries where each arm's damage falls" if good3 else
          f"FALSIFIER FIRED -- {od['buffer_worst_last']} and {od['penalty_worst_middle']}"}
    c = r["controls"]
    good4 = (c["frozen_body_cells"] == e["frozen_cells"]
             and abs((c["frozen_body_worst_gain"] or 0.0) - e["frozen_worst_gain"]) < TOL
             and abs((c["frozen_body_worst_cut"] or 0.0)) < 1e-9)
    j4 = {"id": "BD4",
          "measured": f"`{c['artifact'][0]}` reads {c['frozen_body_cells']} frozen-body cells, the largest gain in "
                      f"absolute value {c['frozen_body_worst_gain']:.4f} and the largest cut "
                      f"{c['frozen_body_worst_cut']:.4f}",
          "verdict": "MET -- the controls clause's frozen-body half is the artifact's own numbers" if good4 else
          f"FALSIFIER FIRED -- frozen-body { {k: c[k] for k in ('frozen_body_cells', 'frozen_body_worst_gain')} }"}
    good5 = (abs((c["frozen_bias_gain_ratio"] or 0.0) - e["gain_ratio"]) < RATIO_TOL
             and abs((c["frozen_bias_cut_ratio"] or 0.0) - e["cut_ratio"]) < RATIO_TOL
             and abs(c["frozen_bias_naive_forgetting_drop"] - e["naive_drop"]) < TOL)
    j5 = {"id": "BD5",
          "measured": f"`{c['artifact'][1]}` reads the frozen bias's gain and cut at "
                      f"{c['frozen_bias_gain_ratio']:.2f} and {c['frozen_bias_cut_ratio']:.2f} of the plastic pair's "
                      f"with the naive arm's forgetting falling {c['frozen_bias_naive_forgetting_drop']:+.4f}",
          "verdict": "MET -- the controls clause's frozen-bias half is the artifact's own numbers" if good5 else
          f"FALSIFIER FIRED -- { {k: c[k] for k in ('frozen_bias_gain_ratio', 'frozen_bias_cut_ratio', 'frozen_bias_naive_forgetting_drop')} }"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the game card, revision 6 ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    card = r["card"]
    print(f"   {card.get('name')}, revision {card.get('revision')}, read 2026-10-05")
    print(f"\n   arms:     {card.get('arms')}")
    print(f"   absent:   {card.get('absent')}")
    print("\n   and the clauses, each with the artifact it is read from:")
    for k in ("world", "stream", "recovery", "invariance", "arm", "draw_terms", "penalty", "trade", "terms",
              "arm_terms"):
        print(f"   {k + ':':<13} {card.get(k)}")
    print(f"   order:        {card.get('order')}")
    print(f"   controls:     {card.get('controls')}")
    print("\n== the registered claims, BD1-BD5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e424` wrote the trade into the card; `e425` to `e427` measured the order and the corpus's own")
    print("    controls, which is what this carries)")
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
