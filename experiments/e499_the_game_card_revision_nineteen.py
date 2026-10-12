"""E499 -- the game card's nineteenth revision: the label-first clause carries the pass's family, two rungs and not one.

`e496` wrote revision 18 with a `label_first` clause read off `e495`'s two-trial runs -- the placement, the two windows,
the two shares and each arm's label-first and label-last diagonals -- and `e497` then put a **second** distractor in
that pass: three trials of four steps, the label at step **0** and its cues at steps **4** and **8**, the read at step
**11** as before. The same pass read **0.8538**, **0.8392** and **0.8580** where the two-trial pass reads **0.8299**,
**0.8139** and **0.8267**, every arm **higher**, with the label's own part of the read unchanged. **So the clause
revision 18 carries is a point and the runs say a family**, and this unit writes that down: the clause keeps every
field revision 18 gave it and gains a **second rung**, the three-trial reading recomputed rather than quoted, with the
card now revision **19** and every revision-18 field checked equal rather than rewritten.

Three claims, registered before this unit's pass over the reading.

- **NA1 -- and the clause carries the second rung.** The `label_first` clause names the three-trial readings beside the
  two-trial ones -- each arm's three-trial diagonal, its change from the two-trial run with the change's sigma, and the
  label's share of the read at three trials against two -- and the artifact's `revision` is **19**. **Falsifier**: the
  clause has no field for three trials, or the revision is not 19; refused when the revision-18 card is absent.
- **NA2 -- and the clause's three-trial numbers are `e497`'s own.** The three diagonals, the three changes with their
  sigmas, and the label's share at three trials against two are read from `e497`'s artifact and from `e497`'s reading
  recomputed, and every one of them agrees, to the precision the clause records. **Falsifier**: any field disagreeing
  with `e497`'s artifact or with the recomputed reading; refused when `e497`'s artifact is absent or its runs cannot be
  read.
- **NA3 -- and the revision is backward-compatible with revision 18.** Every clause field revision 18 carried is still
  present and equal, every field of the card outside the clause is equal to revision 18's, and the `absent` list is
  still revision 18's **empty list**. **Falsifier**: a revision-18 field moved, disappeared, or the `absent` list grew;
  refused when the revision-18 card is absent.

**What it can do beyond that.** It makes the card's `label_first` clause a **family** rather than a point: revision 18
says where the label has to be and this revision says the same clause holds over the pass's own split, so a reader
meets the placement and the rungs the runs have measured in one clause, and the card's `episode` clause and
`label_first` clause are now one reading of one pass with its length a free parameter at least to three trials.

**What it cannot do.** *Two rungs and not a sweep*: the clause carries two and three trials and the four- and six-trial
splits are not in it. *And the split moves two things*: one more trial is one more **cue** and a shorter **trial**, and
no split of a fixed twelve-step pass separates them, so the clause's second rung is the pass's shape and not a crowding
constant. *And one placement pair*: the label is first or last and the passes with it at an interior trial are a
different unit. *And a meter and not a game*: the clause's payout is not on these runs, an action's reward is a
different unit, and the payout is read as a meter rather than played for. *And one world*: two runs at one budget, one
episode length and one seed stream, so a clause that grows is still a record and not a result.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e497_the_label_first_at_three_trials as e497

#: the card this revision is written from, its reading, and the two runs the new rung is read off
CARD18 = Path("runs/e496_the_game_card_revision_eighteen.json")
READING = Path("runs/e497_the_label_first_at_three_trials.json")
THREE = e497.THREE
TWO = e497.TWO
ARMS = e497.ARMS
REVISION = 19
#: the field the clause gains, and the fields the card itself gains
RUNG = "three_trials"
NEW = ("revision", "label_first")
#: how many places of the numbers the clause records are compared at
PLACES = 4
SIGMA_PLACES = 2
CHANCE = e497.CHANCE
BAR = e497.BAR
CLAIMS = (
    ("NA1", "and the clause carries the second rung",
     "The label_first clause names the three-trial readings beside the two-trial ones -- each arm's three-trial "
     "diagonal, its change from the two-trial run with the change's sigma, and the label's share at three trials "
     "against two -- and the revision is 19",
     "falsifier: the clause has no field for three trials, or the revision is not 19; refused when the revision-18 "
     "card is absent"),
    ("NA2", "and the clause's three-trial numbers are e497's own",
     "The three diagonals, the three changes with their sigmas, and the label's share at three trials against two are "
     "read from e497's artifact and from e497's reading recomputed, and every one agrees to the precision the clause "
     "records",
     "falsifier: any field disagreeing with e497's artifact or with the recomputed reading; refused when e497's "
     "artifact is absent or its runs cannot be read"),
    ("NA3", "and the revision is backward-compatible with revision 18",
     "Every clause field revision 18 carried is still present and equal, every field of the card outside the clause "
     "is equal to revision 18's, and the absent list is still revision 18's empty list",
     "falsifier: a revision-18 field moved, disappeared, or the absent list grew; refused when the revision-18 card "
     "is absent"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _at(a, b, places: int) -> bool:
    """Whether two numbers agree to the precision the clause records, both rounded to that many places."""
    if a is None or b is None:
        return False
    try:
        return round(float(a), places) == round(float(b), places)
    except (TypeError, ValueError):
        return False


def reading(card18: Path = CARD18, reading_path: Path = READING) -> dict:
    out = {"ok": True, "reason": None, "card": None, "card18": {}, "clause18": {}, "absent18": [],
           "three_trials": {}, "reading": {}, "rolls": {}}
    base = load(card18)
    if not base:
        return {**out, "ok": False, "reason": f"{card18} is absent, so revision 18 is not on disk"}
    old = base.get("card") or {}
    clause18 = old.get("label_first") or {}
    if not clause18:
        return {**out, "ok": False, "reason": f"{card18} carries no label_first clause to extend"}
    doc = load(reading_path)
    if not doc or not doc.get("ok"):
        return {**out, "ok": False, "reason": f"{reading_path} is absent or was refused"}
    out["reading"] = doc
    #: **recomputed from the two runs**, not copied from the reading
    fresh = e497.reading(three=THREE, two=TWO)
    if not fresh.get("ok"):
        return {**out, "ok": False, "reason": f"the three-trial reading cannot be recomputed: {fresh.get('reason')}"}
    out["rolls"] = fresh
    d3 = fresh["spans"]["accuracy_diagonal"]["three"]
    d2 = fresh["spans"]["accuracy_diagonal"]["two"]
    rec = fresh["recovery"]
    share = fresh["share"]
    rung = {
        "artifact": [READING.name, THREE.name],
        "flag": "--loop-label-first --loop-episode 3",
        "trials": 3,
        "two_trials": 2,
        "replicates": sorted(int(v) for v in fresh["spans"]["replicates"]),
        "chance": CHANCE,
        "bar": BAR,
        "accuracy": {a: {"diagonal": round(d3[a], PLACES),
                         "two_trials": round(d2[a], PLACES),
                         "change": round(rec[a]["mean"], PLACES),
                         "sigma": round(rec[a]["sigma"], SIGMA_PLACES)} for a in ARMS},
        "shares": {"two": round(share["two"]["share"], PLACES),
                   "three": round(share["three"]["share"], PLACES),
                   "spreads": {"two": round(share["two"]["across"], PLACES),
                               "three": round(share["three"]["across"], PLACES)}},
        "explains": "the `label_first` clause's two-trial reading is this rung's starting point: the same read, the "
                    "same placement and the same world with a second distractor in the same window, and every arm "
                    "reads higher",
    }
    clause = copy.deepcopy(clause18)
    clause[RUNG] = rung
    card = copy.deepcopy(old)
    card["revision"] = REVISION
    card["label_first"] = clause
    out["card18"] = {k: v for k, v in old.items() if k not in NEW}
    out["clause18"] = clause18
    out["absent18"] = list(old.get("absent") or [])
    out["three_trials"] = rung
    out["card"] = card
    return out


def _rung_shape(rung) -> bool:
    if not isinstance(rung, dict):
        return False
    acc = rung.get("accuracy") or {}
    shares = rung.get("shares") or {}
    return (all(a in acc for a in ARMS) and "two" in shares and "three" in shares
            and rung.get("trials") == 3 and rung.get("two_trials") == 2
            and all("diagonal" in acc[a] and "two_trials" in acc[a] and "change" in acc[a] and "sigma" in acc[a]
                    for a in ARMS))


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the clause is read from is absent"}
                for c in CLAIMS]
    card = r["card"]
    clause = (card.get("label_first") or {})
    rung = clause.get(RUNG)
    shaped = _rung_shape(rung)
    j1 = {"id": "NA1",
          "measured": f"the clause carries a **{'three_trials' if shaped else 'no three-trial'}** field, its arms "
                      f"{sorted((rung or {}).get('accuracy') or {})}, and the card is revision **{card.get('revision')}**",
          "verdict": "MET -- the clause carries the second rung beside the two-trial readings and the revision is 19" if
                     (shaped and card.get("revision") == REVISION) else
                     f"FALSIFIER FIRED -- the clause's three-trial field is "
                     f"{'present but thin' if rung is not None else 'absent'}, the revision {card.get('revision')}"}
    fresh, stored = r["rolls"], r["reading"]
    off = []
    if shaped:
        acc = rung["accuracy"]
        for a in ARMS:
            checks = [_at(acc[a]["diagonal"], fresh["spans"]["accuracy_diagonal"]["three"][a], PLACES),
                      _at(acc[a]["two_trials"], fresh["spans"]["accuracy_diagonal"]["two"][a], PLACES),
                      _at(acc[a]["change"], fresh["recovery"][a]["mean"], PLACES),
                      _at(acc[a]["sigma"], fresh["recovery"][a]["sigma"], SIGMA_PLACES),
                      _at(acc[a]["diagonal"], stored["spans"]["accuracy_diagonal"]["three"][a], PLACES),
                      _at(acc[a]["two_trials"], stored["spans"]["accuracy_diagonal"]["two"][a], PLACES),
                      _at(acc[a]["change"], stored["recovery"][a]["mean"], PLACES),
                      _at(acc[a]["sigma"], stored["recovery"][a]["sigma"], SIGMA_PLACES)]
            if not all(checks):
                off.append(a)
        sh = rung["shares"]
        numbers_ok = all([
            _at(sh["two"], fresh["share"]["two"]["share"], PLACES),
            _at(sh["three"], fresh["share"]["three"]["share"], PLACES),
            _at(sh["spreads"]["two"], fresh["share"]["two"]["across"], PLACES),
            _at(sh["spreads"]["three"], fresh["share"]["three"]["across"], PLACES),
            _at(sh["two"], stored["share"]["two"]["share"], PLACES),
            _at(sh["three"], stored["share"]["three"]["share"], PLACES),
            _at(sh["spreads"]["two"], stored["share"]["two"]["across"], PLACES),
            _at(sh["spreads"]["three"], stored["share"]["three"]["across"], PLACES),
            rung.get("replicates") == sorted(int(v) for v in stored["spans"]["replicates"]),
            _at(rung.get("chance"), CHANCE, PLACES) and _at(rung.get("bar"), BAR, PLACES),
        ])
    else:
        numbers_ok = False
    j2 = {"id": "NA2",
          "measured": (f"the rung carries {len(rung['accuracy'])} arms' three-trial diagonals "
                       f"{ {a: rung['accuracy'][a]['diagonal'] for a in ARMS} } with changes "
                       f"{ {a: (rung['accuracy'][a]['change'], rung['accuracy'][a]['sigma']) for a in ARMS} } and the "
                       f"label's share two trials **{rung['shares']['two']}** against three "
                       f"**{rung['shares']['three']}** (spreads {rung['shares']['spreads']}), with **{len(off)}** "
                       f"arms disagreeing" if shaped else "the clause has no three-trial field to compare"),
          "verdict": "MET -- every three-trial number is e497's artifact and e497's reading recomputed" if
                     (shaped and not off and numbers_ok) else
                     f"FALSIFIER FIRED -- disagreeing {off}, numbers ok {numbers_ok}"}
    clause18 = r["clause18"]
    moved = sorted(k for k, v in clause18.items() if clause.get(k) != v)
    missing = sorted(k for k in clause18 if k not in clause)
    card18 = r["card18"]
    card_moved = sorted(k for k, v in card18.items() if card.get(k) != v)
    absent = list(card.get("absent") or [])
    j3 = {"id": "NA3",
          "measured": f"the revision-18 clause's {len(clause18)} fields against the revision-19 clause: "
                      f"**{len(clause18) - len(moved)}** equal, with the card's {len(card18)} other fields "
                      f"**{len(card18) - len(card_moved)}** equal and the absent list **{absent}**",
          "verdict": "MET -- every revision-18 field survives into revision 19 and the absent list is untouched" if
                     (not moved and not missing and not card_moved and absent == r["absent18"] and not absent) else
                     f"FALSIFIER FIRED -- moved {moved}, missing {missing}, card moved {card_moved}, absent {absent}"}
    return [j1, j2, j3]


def report(r: dict) -> int:
    print("== the game card's nineteenth revision: the label-first clause carries the pass's family ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact the clause is read from is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    card, rung = r["card"], r["three_trials"]
    print(f"   the card is now revision {card['revision']} and its absent list is {card['absent']}")
    print(f"   the `label_first` clause keeps its {len(r['clause18'])} revision-18 fields and gains `{RUNG}`, "
          f"read from {rung['artifact']}")
    print(f"\n   {'arm':<10} {'three trials':>12} {'two trials':>11} {'change':>9} {'sigma':>7}")
    for a in ARMS:
        g = rung["accuracy"][a]
        print(f"   {a:<10} {g['diagonal']:>12.4f} {g['two_trials']:>11.4f} {g['change']:>+9.4f} {g['sigma']:>7.2f}")
    print(f"\n   the label's own part of the read: two trials {rung['shares']['two']:.4f} against three "
          f"{rung['shares']['three']:.4f} (spreads {rung['shares']['spreads']['two']:.4f} and "
          f"{rung['shares']['spreads']['three']:.4f})")
    print("\n== the registered claims, NA1-NA3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e496` wrote the two-trial point; this writes it down as the family the runs measured)")
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
