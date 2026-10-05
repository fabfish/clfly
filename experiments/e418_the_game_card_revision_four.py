"""E418 -- the game card, revision 4: the absence list rewritten, and the third arm carried.

`e409` wrote revision 2 with the draw's clauses and `e414` revision 3 with the buffer's. Both carried the **absence
list** `e392` wrote at revision 1 unchanged, and by revision 3 that list was stale: it still read *a second world* and
*a second draw* while the card's own world clause measures **six** worlds and its stream clause **three** streams.
`e415` then measured a **penalty** arm on the card's own world at eleven sigma, so the card's `arms` clause -- *naive*
and *replay* -- is one short as well.

**This unit writes revision 4.** Two clauses change, and both are checked against the artifact that closed the gap: the
absence list loses the two items the card's own clauses already cover, and the arms clause gains the penalty, with its
ordering read from `e415`. Every other clause is carried unchanged, and the revision is checked against the artifact
rather than restated. No training and no roll. Five claims, registered before this unit read any of them.

- **AP1 -- and the third revision is carried unchanged where it is not rewritten.** Every field of `e414`'s card
  except `revision`, `arms` and `absent` -- the substrate, loop, protocol, metrics, its own buffer clause and its draw
  terms, and the world, stream, recovery and invariance clauses -- is equal to the revision-3 card, with the revision
  now **4**. **Falsifier**: any other field differing; **REFUSED** when `e414`'s artifact is absent.
- **AP2 -- and the absence list loses exactly the two items a clause covers.** The new list is the old one minus
  exactly *a second world* and *a second draw*, each of which a clause the card already carries measures: the world
  clause's **six** worlds and the stream clause's **three** streams, both read from `e409`'s artifact. **Falsifier**: a
  different set struck, or a struck item no carried clause covers; **REFUSED** when `e409`'s artifact is absent.
- **AP3 -- and the arms clause gains the penalty.** The card's `arms` reads three names and its third is the arm
  `e415`'s cell carries beside `naive` and `replay`. **Falsifier**: the third name not being that artifact's penalty
  arm; **REFUSED** when `e415`'s artifact is absent.
- **AP4 -- and the penalty clause is the artifact's.** The card carries `e415`'s ordering: **+0.1764** of accuracy at
  **11.50 sigma** and **-0.2521** of forgetting at **11.65 sigma**, and the penalty is not resolved against the naive
  arm, **-0.0274** at **-1.95 sigma**. **Falsifier**: any number disagreeing with that artifact.
- **AP5 -- and the clause carries the rule it was measured on.** `e415` reported that its cell agrees with the card's
  world's run on twenty-one shared fields but that the world's **coupling** is recorded in one and not the other, so
  the penalty clause states the measurement's rule. **Falsifier**: the caveat absent, or the artifact recording the
  coupling in the measured cell.

**What it can do beyond that.** It makes the card a reader can hold without being misled: the two absences the line
closed are struck with the clause that closed them, the two penalties the corpus runs are named, and the penalty's own
ordering and the rule it was measured on are carried beside the buffer's.

**What it cannot do.** *A card is a definition and not a result*: it states what the benchmark is and points at the
artifacts for every number. *And the struck items are struck by the card's own clauses*: this revision does not
re-derive the six worlds or the three streams, it reads the clauses that measured them. *And the penalty clause is one
world's and one strength's*: the card's world at `lam = 1.0` with `ewc-block`, on the uncoupled rule. *And the other
four absences stand*: no reward, no policy, no episode boundary and no held-out task has been added, and the list's
remaining items are the benchmark's own statement of what it is not.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the artifacts every clause is read from
CARD3 = Path("runs/e414_the_game_card_revision_three.json")
PENALTY = Path("runs/e415_the_penalty_on_the_cards_world.json")
DRAWS = Path("runs/e409_the_game_card_revision_two.json")
REVISION = 4
#: the fields a revision 4 is allowed to change, and the two absences a carried clause already covers
REWRITTEN = ("revision", "arms", "absent", "penalty")
STRIKE = ("a second world", "a second draw")
COVERED_BY = {"a second world": "world", "a second draw": "stream"}
#: the arm the penalty clause is read from, and the numbers `e415` measured
THIRD_ARM = "ewc-block"
PENALTY_CLAUSE = {"arm": "ewc-block", "lam": 1.0, "replicates": 20,
                  "accuracy_gain": 0.1764, "accuracy_sigma": 11.50,
                  "forgetting_cut": 0.2521, "forgetting_sigma": -11.65,
                  "over_naive": {"accuracy": -0.0274, "sigma": -1.95},
                  "measured_on": "the uncoupled world rule that predates e359"}
TOL = 0.005
SIGMA_TOL = 0.05
CLAIMS = (
    ("AP1", "and the third revision is carried unchanged where it is not rewritten",
     "Every field of `e414`'s card except the revision, the arms and the absence list -- including its own buffer "
     "clause and draw terms and the world, stream, recovery and invariance clauses -- is equal to the revision-3 "
     "card, with the revision now 4",
     "falsifier: any other field differing; refused when `e414`'s artifact is absent"),
    ("AP2", "and the absence list loses exactly the two items a clause covers",
     "The new list is the old one minus exactly a second world and a second draw, each covered by a clause the card "
     "already carries: the world clause's six worlds and the stream clause's three streams",
     "falsifier: a different set struck, or a struck item no carried clause covers; refused when `e409`'s artifact is "
     "absent"),
    ("AP3", "and the arms clause gains the penalty",
     "The card's arms read three names and its third is the arm `e415`'s cell carries beside naive and replay",
     "falsifier: the third name not being that artifact's penalty arm; refused when `e415`'s artifact is absent"),
    ("AP4", "and the penalty clause is the artifact's",
     "The card carries `e415`'s ordering: +0.1764 of accuracy at 11.50 sigma and -0.2521 of forgetting at 11.65 "
     "sigma, with the penalty unresolved against the naive arm at -0.0274 and -1.95 sigma",
     "falsifier: any number disagreeing with that artifact"),
    ("AP5", "and the clause carries the rule it was measured on",
     "`e415` reported that the coupling is recorded in the card's world's run and not in the measured cell, so the "
     "penalty clause states the measurement's rule",
     "falsifier: the caveat absent, or the artifact recording the coupling in the measured cell"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def reading(card3: Path = CARD3, penalty: Path = PENALTY, draws: Path = DRAWS) -> dict:
    out = {"ok": True, "reason": None, "card": None, "revision3": {}, "closed": {}, "arms": {}, "penalty": {},
           "rule": {}}
    base = load(card3)
    if not base:
        return {**out, "ok": False, "reason": f"{card3} is absent, so revision 3 is not on disk"}
    old = base.get("card") or {}
    absent = list(old.get("absent") or [])
    card = copy.deepcopy(old)
    card["revision"] = REVISION
    card["absent"] = [a for a in absent if a not in STRIKE]
    out["revision3"] = {k: v for k, v in old.items() if k not in REWRITTEN}
    out["old_absent"] = absent
    out["struck"] = [a for a in absent if a in STRIKE]

    d = load(draws)
    if not d:
        return {**out, "ok": False, "reason": f"{draws} is absent, so the struck items have no covering clause"}
    clauses = d.get("card") or {}
    out["closed"] = {"artifact": Path(draws).name, "object": clauses.get("world"), "stream": clauses.get("stream"),
                     "covers": {k: clauses.get(COVERED_BY[k]) for k in STRIKE}}

    p = load(penalty)
    if not p:
        return {**out, "ok": False, "reason": f"{penalty} is absent, so the penalty clause has no reading"}
    arms = sorted(p.get("arms") or {})
    contrasts = p.get("contrasts") or {}
    acc = (contrasts.get("replay_minus_ewc-block") or {}).get("accuracy") or {}
    cut = (contrasts.get("replay_minus_ewc-block") or {}).get("forgetting") or {}
    over = (contrasts.get("ewc-block_minus_naive") or {}).get("accuracy") or {}
    out["arms"] = {"artifact": Path(penalty).name, "arms": arms,
                   "third": THIRD_ARM if THIRD_ARM in arms else None,
                   "replicates": min((v.get("replicates") or 0) for v in (p.get("arms") or {}).values())
                   if p.get("arms") else 0}
    card["arms"] = ["naive", "replay"] + ([THIRD_ARM] if THIRD_ARM in arms else [])
    out["penalty"] = {"artifact": Path(penalty).name,
                      "accuracy_gain": acc.get("difference"), "accuracy_sigma": acc.get("sigma"),
                      "forgetting_cut": -cut.get("difference") if cut.get("difference") is not None else None,
                      "forgetting_sigma": cut.get("sigma"),
                      "over_naive": {"accuracy": over.get("difference"), "sigma": over.get("sigma")}}
    card["penalty"] = {"arm": card["arms"][-1], "lam": 1.0, "replicates": out["arms"]["replicates"],
                       "accuracy_gain": PENALTY_CLAUSE["accuracy_gain"],
                       "accuracy_sigma": PENALTY_CLAUSE["accuracy_sigma"],
                       "forgetting_cut": PENALTY_CLAUSE["forgetting_cut"],
                       "forgetting_sigma": PENALTY_CLAUSE["forgetting_sigma"],
                       "over_naive": dict(PENALTY_CLAUSE["over_naive"]),
                       "measured_on": PENALTY_CLAUSE["measured_on"]}
    cell = p.get("cell") or {}
    out["rule"] = {"artifact": Path(penalty).name, "reference": cell.get("reference"),
                   "coupling_recorded_in_reference": bool(cell.get("coupling_recorded")),
                   "coupling_in_measured_cell": bool(cell.get("coupling_in_this_artifact")),
                   "stated": card["penalty"]["measured_on"]}
    out["card"] = card
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the clause is read from is absent"}
                for c in CLAIMS]
    card = r["card"]
    same = {k: (card.get(k) == v) for k, v in r["revision3"].items()}
    good1 = all(same.values()) and card.get("revision") == REVISION
    j1 = {"id": "AP1",
          "measured": f"the revision-3 card's {len(same)} fields against the revision-4 card: "
                      f"{len(same) - sum(1 for v in same.values() if not v)} equal, with the revision now "
                      f"{card.get('revision')}",
          "verdict": f"MET -- the third revision is carried unchanged in all {len(same)} fields it does not rewrite"
                     if good1 else
                     f"FALSIFIER FIRED -- { {k: v for k, v in same.items() if not v} } differs"}
    struck, kept = set(r["struck"]), card.get("absent") or []
    covers = r.get("closed") or {}
    covered = covers.get("covers") or {}
    good2 = (set(STRIKE) == struck and set(r["old_absent"]) - struck == set(kept)
             and all(covered.get(k) for k in STRIKE))
    j2 = {"id": "AP2",
          "measured": f"the list goes from {len(r['old_absent'])} items to {len(kept)}, losing {sorted(struck)}, each "
                      f"covered by a clause `{covers.get('artifact')}` carries: the world clause reads "
                      f"{(covers.get('object') or {}).get('worlds_measured')} worlds and the stream clause "
                      f"{(covers.get('stream') or {}).get('streams_measured')} streams",
          "verdict": "MET -- the absence list loses exactly the two items a carried clause covers" if good2 else
          f"FALSIFIER FIRED -- struck {sorted(struck)} of {sorted(STRIKE)}, kept {kept}, covers "
          f"{ {k: bool(v) for k, v in covers.get('covers', {}).items()} }"}
    a = r["arms"]
    good3 = (a["third"] == THIRD_ARM and card.get("arms") == ["naive", "replay", THIRD_ARM]
             and a["replicates"] >= 20)
    j3 = {"id": "AP3",
          "measured": f"`{a['artifact']}` carries {a['arms']} at {a['replicates']} replicates and the card's arms "
                      f"read {card.get('arms')}",
          "verdict": f"MET -- the arms clause gains {THIRD_ARM}, the arm that artifact carries" if good3 else
          f"FALSIFIER FIRED -- the third arm is {a['third']} against a card reading {card.get('arms')}"}
    pen, got = card.get("penalty") or {}, r["penalty"]
    def _close(x, y, tol=TOL):
        return x is not None and y is not None and abs(float(x) - float(y)) < tol
    good4 = (_close(pen.get("accuracy_gain"), got["accuracy_gain"]) and
             _close(pen.get("accuracy_sigma"), got["accuracy_sigma"], SIGMA_TOL) and
             _close(pen.get("forgetting_cut"), got["forgetting_cut"]) and
             _close(pen.get("forgetting_sigma"), got["forgetting_sigma"], SIGMA_TOL) and
             _close((pen.get("over_naive") or {}).get("accuracy"), (got.get("over_naive") or {}).get("accuracy")) and
             _close((pen.get("over_naive") or {}).get("sigma"), (got.get("over_naive") or {}).get("sigma"), SIGMA_TOL))
    j4 = {"id": "AP4",
          "measured": f"`{got['artifact']}` reads accuracy {got['accuracy_gain']:+.4f} at {got['accuracy_sigma']:+.2f} "
                      f"sigma and a forgetting cut {got['forgetting_cut']:+.4f} at {got['forgetting_sigma']:+.2f} "
                      f"sigma, with the penalty over the naive arm at "
                      f"{(got.get('over_naive') or {}).get('accuracy'):+.4f}",
          "verdict": "MET -- the penalty clause is the artifact's own numbers" if good4 else
          f"FALSIFIER FIRED -- the card reads {pen.get('accuracy_gain')} and "
          f"{(pen.get('over_naive') or {}).get('accuracy')}"}
    rule = r["rule"]
    good5 = (rule["coupling_recorded_in_reference"] and not rule["coupling_in_measured_cell"]
             and isinstance(rule.get("stated"), str) and "uncoupled" in rule["stated"])
    j5 = {"id": "AP5",
          "measured": f"`{rule['artifact']}` records the coupling in `{rule['reference']}` "
                      f"({rule['coupling_recorded_in_reference']}) and not in the measured cell "
                      f"({rule['coupling_in_measured_cell']}), and the card states "
                      f"{rule.get('stated')!r}",
          "verdict": "MET -- the clause carries the rule it was measured on" if good5 else
          f"FALSIFIER FIRED -- the coupling is recorded in the measured cell "
          f"{rule['coupling_in_measured_cell']} or the caveat is absent"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the game card, revision 4 ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    card = r["card"]
    print(f"   {card.get('name')}, revision {card.get('revision')}, read 2026-10-05")
    print(f"\n   arms:    {card.get('arms')}")
    print(f"   absent:  was {r['old_absent']}")
    print(f"            now {card.get('absent')}")
    print(f"\n   penalty: {card.get('penalty')}")
    print(f"   the drawn clauses the revision-3 card carries are unchanged: world, stream, recovery, invariance and")
    print(f"   its own buffer clause and draw terms")
    print("\n== the registered claims, AP1-AP5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e409` wrote the draw's clauses and `e414` the buffer's, both carrying `e392`'s absence list")
    print("    unchanged; `e415` then measured a penalty arm on the card's own world)")
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
