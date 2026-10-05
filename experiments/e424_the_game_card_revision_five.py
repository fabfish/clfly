"""E424 -- the game card, revision 5: the trade written into the card, and what it is made of.

`e414` wrote revision 3 with the buffer's clause and `e418` revision 4 with the three arms. `e419` to `e423` then
measured what the buffer actually does: the two older tasks recovered and the newest cost on all twelve draws
(`e419`, `e420`), the same trade mixed at twenty updates (`e421`), the split into a learning term and a retention term
(`e422`), and the penalty's tenth of the same trade at the same price (`e423`). None of that is in the card.

**This unit writes revision 5.** Three clauses are added and every other field is checked equal to `e418`'s card
rather than restated: the **trade** at both ends of the budget, the **terms** it is made of, and the **arm terms** --
what the penalty buys beside the buffer. Every number is read from the artifact that measured it. No training and no
roll. Five claims, registered before this unit read any of them.

- **AZ1 -- and the fourth revision is carried unchanged where it is not rewritten.** Every field of `e418`'s card
  except the revision and the three new clauses -- the substrate, loop, protocol, metrics, its own buffer clause, draw
  terms and penalty clause, and the world, stream, recovery and invariance clauses -- is equal to the revision-4 card,
  with the revision now **5**. **Falsifier**: any other field differing; **REFUSED** when `e418`'s artifact is absent.
- **AZ2 -- and the trade clause is `e420`'s far point.** Twelve cells, the newest task cost in **all twelve**, the
  oldest recovered by at least **0.2333**, the coverage at least **5.48**. **Falsifier**: any number disagreeing with
  that artifact; **REFUSED** when it is absent.
- **AZ3 -- and its near point is `e421`'s.** At twenty updates the newest task is cost in **8** of **13** cells and
  the oldest recovered by at most **0.0750**. **Falsifier**: either number disagreeing; **REFUSED** when it is absent.
- **AZ4 -- and the terms clause is `e422`'s.** The learning term at the oldest task and the retention term at the
  newest are **exactly zero** on all twelve cells, and the middle task's retention is at least **3.99** times its
  learning price. **Falsifier**: any number disagreeing; **REFUSED** when it is absent.
- **AZ5 -- and the arm terms clause is `e423`'s.** The buffer's retention over the penalty's is at least **7.13**
  times and the two learning prices differ by at most **0.0344**. **Falsifier**: either number disagreeing;
  **REFUSED** when it is absent.

**What it can do beyond that.** It is the card a reader can act on: the benchmark's own two terms (`e414`'s buffer
clause, `e418`'s penalty clause), and now what an arm does inside them -- where its accuracy goes, which task pays,
and what happens to the same trade when the arm is a penalty instead of a buffer.

**What it cannot do.** *A card is a definition and not a result*: it states what the benchmark is and points at the
artifacts for every number. *And the trade is measured on one arm pair with one order*: the `naive`/`replay` pair at
five hundred and twenty updates in the as-built order, and the penalty only on one cell. *And the clauses are only
checked against each other*: AZ1 shows revision 4 survives into revision 5 and not that revision 4 was right.
*And a clause is not an experiment.*
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the artifacts every clause is read from
CARD4 = Path("runs/e418_the_game_card_revision_four.json")
TRADE_FAR = Path("runs/e420_the_trade_is_a_constant.json")
TRADE_NEAR = Path("runs/e421_the_trade_turns_on.json")
TERMS = Path("runs/e422_the_buffer_buys_retention.json")
ARM_TERMS = Path("runs/e423_the_penalty_buys_a_tenth.json")
REVISION = 5
NEW = ("revision", "trade", "terms", "arm_terms")
CLAIMS = (
    ("AZ1", "and the fourth revision is carried unchanged where it is not rewritten",
     "Every field of `e418`'s card except the revision and the three new clauses is equal to the revision-4 card, "
     "with the revision now 5",
     "falsifier: any other field differing; refused when `e418`'s artifact is absent"),
    ("AZ2", "and the trade clause is `e420`'s far point",
     "Twelve cells, the newest task cost in all twelve, the oldest recovered by at least 0.2333, the coverage at "
     "least 5.48",
     "falsifier: any number disagreeing with that artifact; refused when it is absent"),
    ("AZ3", "and its near point is `e421`'s",
     "At twenty updates the newest task is cost in 8 of 13 cells and the oldest recovered by at most 0.0750",
     "falsifier: either number disagreeing; refused when it is absent"),
    ("AZ4", "and the terms clause is `e422`'s",
     "The learning term at the oldest task and the retention term at the newest are exactly zero on all twelve cells, "
     "and the middle task's retention is at least 3.99 times its learning price",
     "falsifier: any number disagreeing; refused when it is absent"),
    ("AZ5", "and the arm terms clause is `e423`'s",
     "The buffer's retention over the penalty's is at least 7.13 times and the two learning prices differ by at most "
     "0.0344",
     "falsifier: either number disagreeing; refused when it is absent"),
)
TOL = 0.002
RATIO_TOL = 0.01
EXPECTED = {
    "far_cells": 12, "far_newest_cost": 12, "far_oldest_min": 0.2333, "far_coverage_min": 5.48,
    "near_cells": 13, "near_newest_cost": 8, "near_oldest_max": 0.0750,
    "terms_cells": 12, "oldest_learning": 0.0, "newest_retention": 0.0, "middle_ratio_min": 3.99,
    "retention_ratio_min": 7.13, "price_gap_max": 0.0344,
}


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def reading(card4: Path = CARD4, far: Path = TRADE_FAR, near: Path = TRADE_NEAR, terms: Path = TERMS,
            arm_terms: Path = ARM_TERMS) -> dict:
    out = {"ok": True, "reason": None, "card": None, "revision4": {}, "trade": {}, "terms": {}, "arm_terms": {}}
    base = load(card4)
    if not base:
        return {**out, "ok": False, "reason": f"{card4} is absent, so revision 4 is not on disk"}
    old = base.get("card") or {}
    card = copy.deepcopy(old)
    card["revision"] = REVISION
    out["revision4"] = {k: v for k, v in old.items() if k not in NEW}

    f = load(far)
    if not f:
        return {**out, "ok": False, "reason": f"{far} is absent, so the trade's far point has no reading"}
    fs = f.get("spans") or {}
    n = load(near)
    if not n:
        return {**out, "ok": False, "reason": f"{near} is absent, so the trade's near point has no reading"}
    ns = n.get("spans") or {}
    fc = list((f.get("cells") or {}).values())
    card["trade"] = {"artifact": [Path(far).name, Path(near).name],
                     "far_cells": len(fc), "far_newest_cost": sum(1 for c in fc if c["gain"][2] < 0),
                     "far_oldest_min": min(c["gain"][0] for c in fc),
                     "far_coverage_min": min(c["coverage"] for c in fc if c["coverage"] is not None),
                     "far_oldest_max": max(c["gain"][0] for c in fc),
                     "far_loss_min": min(c["newest_loss"] for c in fc),
                     "far_loss_max": max(c["newest_loss"] for c in fc),
                     "near_cells": len(n.get("cells") or {}) + (1 if n.get("unpaired") else 0),
                     "near_newest_cost": ns.get("near_negative"), "near_oldest_max": ns.get("near_oldest_max")}
    out["trade"] = dict(card["trade"])

    t = load(terms)
    if not t:
        return {**out, "ok": False, "reason": f"{terms} is absent, so the terms clause has no reading"}
    ts = t.get("spans") or {}
    card["terms"] = {"artifact": Path(terms).name, "cells": len(t.get("cells") or {}),
                     "oldest_learning": ts.get("oldest_learn_max"), "newest_retention": ts.get("newest_retain_max"),
                     "oldest_retention_min": ts.get("oldest_retain_min"),
                     "newest_learning_worst": ts.get("newest_learn_max"),
                     "middle_ratio_min": ts.get("middle_ratio_min")}
    out["terms"] = dict(card["terms"])

    a = load(arm_terms)
    if not a:
        return {**out, "ok": False, "reason": f"{arm_terms} is absent, so the arm terms clause has no reading"}
    as_ = a.get("spans") or {}
    ratios = [v for v in (as_.get("ratios") or {}).values() if v is not None]
    tm_terms = a.get("terms") or {}
    prices = [abs(tm_terms.get("ewc-block", {}).get("learned", [0] * 3)[k]
                  - tm_terms.get("replay", {}).get("learned", [0] * 3)[k]) for k in (1, 2)]
    card["arm_terms"] = {"artifact": Path(arm_terms).name, "retention_ratio_min": min(ratios) if ratios else None,
                         "retention_ratio_max": max(ratios) if ratios else None,
                         "price_gap_max": max(prices) if prices else None}
    out["arm_terms"] = dict(card["arm_terms"])
    out["card"] = card
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the clause is read from is absent"}
                for c in CLAIMS]
    card = r["card"]
    same = {k: (card.get(k) == v) for k, v in r["revision4"].items()}
    j1 = {"id": "AZ1",
          "measured": f"the revision-4 card's {len(same)} fields against the revision-5 card: "
                      f"{len(same) - sum(1 for v in same.values() if not v)} equal, with the revision now "
                      f"{card.get('revision')}",
          "verdict": f"MET -- the fourth revision is carried unchanged in all {len(same)} fields it does not rewrite" if
                     (all(same.values()) and card.get("revision") == REVISION) else
                     f"FALSIFIER FIRED -- { {k: v for k, v in same.items() if not v} } differs"}
    tr = r["trade"]
    e = EXPECTED
    good2 = (tr["far_cells"] == e["far_cells"] and tr["far_newest_cost"] == e["far_newest_cost"]
             and abs((tr["far_oldest_min"] or 0.0) - e["far_oldest_min"]) < TOL
             and abs((tr["far_coverage_min"] or 0.0) - e["far_coverage_min"]) < RATIO_TOL)
    j2 = {"id": "AZ2",
          "measured": f"`{tr['artifact'][0]}` reads {tr['far_cells']} cells with the newest task cost in "
                      f"{tr['far_newest_cost']}, the oldest recovered by {tr['far_oldest_min']:+.4f} to "
                      f"{tr['far_oldest_max']:+.4f} and the coverage at least {tr['far_coverage_min']:.2f}",
          "verdict": "MET -- the trade clause is the far-point artifact's own numbers" if good2 else
          f"FALSIFIER FIRED -- {tr}"}
    good3 = (tr["near_cells"] == e["near_cells"] and tr["near_newest_cost"] == e["near_newest_cost"]
             and abs((tr["near_oldest_max"] or 0.0) - e["near_oldest_max"]) < TOL)
    j3 = {"id": "AZ3",
          "measured": f"`{tr['artifact'][1]}` reads {tr['near_cells']} cells at twenty updates with the newest task "
                      f"cost in {tr['near_newest_cost']} and the oldest recovered by at most "
                      f"{tr['near_oldest_max']:+.4f}",
          "verdict": "MET -- the trade clause's near point is the artifact's own numbers" if good3 else
          f"FALSIFIER FIRED -- { {k: tr[k] for k in ('near_cells', 'near_newest_cost', 'near_oldest_max')} }"}
    tm = r["terms"]
    good4 = (tm["cells"] == e["terms_cells"] and abs((tm["oldest_learning"] or 0.0) - e["oldest_learning"]) < 1e-9
             and abs((tm["newest_retention"] or 0.0) - e["newest_retention"]) < 1e-9
             and abs((tm["middle_ratio_min"] or 0.0) - e["middle_ratio_min"]) < 0.01)
    j4 = {"id": "AZ4",
          "measured": f"`{tm['artifact']}` reads {tm['cells']} cells with the oldest task's learning term at "
                      f"{tm['oldest_learning']:.2e} and the newest task's retention term at "
                      f"{tm['newest_retention']:.2e}, the middle retention at least {tm['middle_ratio_min']:.2f} "
                      f"times the price",
          "verdict": "MET -- the terms clause is the artifact's own numbers, both structural zeros included" if good4
                     else f"FALSIFIER FIRED -- {tm}"}
    at = r["arm_terms"]
    good5 = (at["retention_ratio_min"] is not None
             and abs(at["retention_ratio_min"] - e["retention_ratio_min"]) < RATIO_TOL
             and abs(at["price_gap_max"] - e["price_gap_max"]) < TOL)
    j5 = {"id": "AZ5",
          "measured": f"`{at['artifact']}` reads the buffer's retention over the penalty's at "
                      f"{at['retention_ratio_min']:.2f} to {at['retention_ratio_max']:.2f} times with the two "
                      f"learning prices {at['price_gap_max']:.4f} apart",
          "verdict": "MET -- the arm terms clause is the artifact's own numbers" if good5 else
          f"FALSIFIER FIRED -- {at}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the game card, revision 5 ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    card = r["card"]
    print(f"   {card.get('name')}, revision {card.get('revision')}, read 2026-10-05")
    print(f"\n   arms:       {card.get('arms')}")
    print(f"   absent:     {card.get('absent')}")
    print(f"\n   and the clauses, each with the artifact it is read from:")
    for k in ("world", "stream", "recovery", "invariance", "arm", "draw_terms", "penalty"):
        print(f"   {k + ':':<12} {card.get(k)}")
    print(f"   trade:       {card.get('trade')}")
    print(f"   terms:       {card.get('terms')}")
    print(f"   arm_terms:   {card.get('arm_terms')}")
    print("\n== the registered claims, AZ1-AZ5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e414` wrote the buffer's clause and `e418` the three arms; `e419` to `e423` measured what the")
    print("    buffer does task by task and what it is made of, which is what this carries)")
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
