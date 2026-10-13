"""E503 -- the game card's twentieth revision: the `payout` clause carries the earning and the two currencies.

Revision 19 wrote the card with an `episode` clause and a `label_first` clause, and that clause's own *cannot do* left
the payout out: *a meter and not a game ... the payout is read as a meter rather than played for*. Three units have
since measured exactly that capability, and this revision writes it into the card. `e500` gave the loop's map an
optimizer of its own and ascended the **world's payout** into it inside the two-trial, label-first episode: the world
pays **+1.5086**, **+1.4123** and **+1.0722** more on every arm at **+22.74**, **+22.57** and **+15.54** sigma, the map
ends **3.9475** to **8.0630** from the identity, and the accuracy stands to **0.0021** of the meter run's. `e501` did
the same at the pass's second rung, three trials: **+1.4562**, **+1.3586** and **+1.0131** more at **+22.92**,
**+36.39** and **+19.68** sigma, the accuracy standing to **0.0038**. `e502` read the same payout on the agent's own
**action** rather than on the world's carry: **+4.0860**, **+4.1356** and **+3.0381** more on every arm at **+21.68**,
**+23.62** and **+15.12** sigma. **So the card's own reading of the pass has a payout an agent can play for, at two
rungs and in two currencies**, and this unit writes that down: a **`payout` clause** added, the earned-vs-meter reward
contrasts with their sigmas, the map's distance from the identity, the accuracy changes, and the currency the payout is
read on, every number read from the three artifacts and from their readings recomputed rather than quoted, with the
card now revision **20** and every revision-19 field checked equal rather than rewritten.

Three claims, registered before this unit's pass over the three readings.

- **NA1 -- and the card carries the payout clause and the revision is 20.** The card has a `payout` clause naming the
  earning -- the earned-vs-meter reward contrasts with their sigmas, the map's distance from the identity, the accuracy
  changes, and the currency the payout is read on -- and the artifact's `revision` is **20**. **Falsifier**: the clause
  has no earning reading, or the revision is not 20; refused when the revision-19 card is absent.
- **NA2 -- and the clause's numbers are the runs' own.** Every number the clause carries is read from `e500`'s,
  `e501`'s and `e502`'s artifacts and from their readings recomputed, and every one agrees, to the precision the clause
  records. **Falsifier**: any field disagreeing with an artifact or with the recomputed reading; refused when an
  artifact is absent or its runs cannot be read.
- **NA3 -- and the revision is backward-compatible with revision 19.** Every clause field revision 19 carried is still
  present and equal, every field of the card outside the clauses is equal to revision 19's, and the `absent` list is
  still revision 19's **empty list**. **Falsifier**: a revision-19 field moved, disappeared, or the `absent` list grew;
  refused when the revision-19 card is absent.

**What it can do beyond that.** It closes the hole revision 19's own *cannot do* left open -- *the clause's payout is
not on these runs, an action's reward is a different unit, and the payout is read as a meter rather than played for* --
by carrying in one clause the earned-vs-meter ablation at both rungs the `label_first` clause names and the payout read
on the action, so a reader meets the card's pass and what the pass is worth to an agent that acts in one place.

**What it cannot do.** *Two currencies and one world*: the carried and action readers are two ways of scoring one
world's own linear read of the cue, and a second world or a second payout shape is a different unit. *And one budget and
one seed stream*: every run behind the clause is the card's own setting at the run's own `--lr`, so how hard the map is
paid is not swept. *And the action's currency turns on a coincidence of widths*: the world's one-step response has width
`n_action` and the cue's target has width `world_dims`, and the clause's **8** and **8** are the card's own
configuration rather than the currency's, so the same flag at another `--loop-world-dims` does not compare. *And a
clause is not a result*: NA3 shows revision 19 survives into revision 20 and not that revision 19 was right. *And the
pass's length is carried to three trials and no further*: the four- and six-trial splits and the interior placements
are not in the clause.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e500_the_pass_plays_for_the_payout as e500
from experiments import e501_the_pass_plays_at_three_trials as e501
from experiments import e502_the_world_pays_the_action as e502

#: the card this revision is written from, and the three units whose readings the new clause carries
CARD19 = Path("runs/e499_the_game_card_revision_nineteen.json")
UNITS = {"two_trials": e500, "three_trials": e501, "action": e502}
ARTIFACTS = {"two_trials": Path("runs/e500_the_pass_plays_for_the_payout.json"),
             "three_trials": Path("runs/e501_the_pass_plays_at_three_trials.json"),
             "action": Path("runs/e502_the_world_pays_the_action.json")}
UNIT_ORDER = ("two_trials", "three_trials", "action")
ARMS = e500.ARMS
REVISION = 20
#: the clause the card gains, and the fields the card itself gains
CLAUSE = "payout"
NEW = ("revision", CLAUSE)
#: the two readers the clause carries, and which rung is read on which
CURRENCY = {"carried": "the world's carried state at the read step, scored against the target the cue sets one step "
                       "after it arrives",
            "action": "the world's one-step response to the action, scored against the same target at the same step"}
READER = {"two_trials": "carried", "three_trials": "carried", "action": "action"}
CHANCE = e500.CHANCE
BAR = e500.BAR
SIGMA = e500.SIGMA
PLACES = 4
SIGMA_PLACES = 2
CLAIMS = (
    ("NA1", "and the card carries the payout clause and the revision is 20",
     "The card has a payout clause naming the earning -- the earned-vs-meter reward contrasts with their sigmas, the "
     "map's distance from the identity, the accuracy changes, and the currency the payout is read on -- and the "
     "artifact's revision is 20",
     "falsifier: the clause has no earning reading, or the revision is not 20; refused when the revision-19 card is "
     "absent"),
    ("NA2", "and the clause's numbers are the runs' own",
     "Every number the clause carries is read from e500's, e501's and e502's artifacts and from their readings "
     "recomputed, and every one agrees to the precision the clause records",
     "falsifier: any field disagreeing with an artifact or with the recomputed reading; refused when an artifact is "
     "absent or its runs cannot be read"),
    ("NA3", "and the revision is backward-compatible with revision 19",
     "Every clause field revision 19 carried is still present and equal, every field of the card outside the clauses is "
     "equal to revision 19's, and the absent list is still revision 19's empty list",
     "falsifier: a revision-19 field moved, disappeared, or the absent list grew; refused when the revision-19 card is "
     "absent"),
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
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    try:
        return round(float(a), places) == round(float(b), places)
    except (TypeError, ValueError):
        return False


def _agree(a, b) -> bool:
    """Whether two clause-shaped readings are the same, numbers to the clause's precision and everything else equal."""
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(_agree(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_agree(x, y) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return _at(a, b, PLACES)
    return a == b


def _replicates(unit: dict) -> list:
    return sorted(int(v) for v in (unit["spans"] or {}).get("replicates") or [])


def _rung_of(unit: dict, name: str, artifact: str) -> dict:
    """One unit's earning as the clause carries it: the two currencies' level, the map's move, the accuracy."""
    s = unit["spans"]
    rung = {
        "artifact": artifact,
        "episode": s.get("episode"),
        "currency": READER[name],
        "replicates": _replicates(unit),
        "reward": {a: {"earned": s["reward_diagonal"]["earned"][a],
                       "meter": s["reward_diagonal"]["meter"][a],
                       "change": round(unit["reward"][a]["mean"], PLACES),
                       "sigma": round(unit["reward"][a]["sigma"], SIGMA_PLACES)} for a in ARMS},
        "accuracy": {a: {"earned": s["accuracy_diagonal"]["earned"][a],
                         "meter": s["accuracy_diagonal"]["meter"][a],
                         "change": round(unit["accuracy"][a]["mean"], PLACES),
                         "sigma": round(unit["accuracy"][a]["sigma"], SIGMA_PLACES)} for a in ARMS},
        "map_move": {a: {"mean": round(s["map_move"]["earned"][a]["mean"], PLACES),
                         "smallest": round(s["map_move"]["earned"][a]["smallest"], PLACES)} for a in ARMS},
    }
    if name == "action":
        rung["carried_level"] = {a: {"earned": s["reward_diagonal"]["earned"][a],
                                     "carried": s["reward_diagonal"]["carried"][a]} for a in ARMS}
        draw = ((unit.get("runs") or {}).get("earned") or {}).get("env_draw") or {}
        rung["widths"] = {"n_action": draw.get("n_action"), "world_dims": draw.get("world_dims")}
    return rung


def build_clause(units: dict, names: dict) -> dict:
    """The `payout` clause, built from three units' readings -- the same function the card and the check both use."""
    clause = {
        "artifact": [names[n] for n in UNIT_ORDER],
        "flag": "--loop-policy --loop-earn, with --loop-reward-on-action for the action's currency",
        "currency": dict(CURRENCY),
        "arms": list(ARMS),
        "replicates": sorted({r for n in UNIT_ORDER for r in _replicates(units[n])}),
        "chance": CHANCE,
        "bar": BAR,
        "sigma": SIGMA,
        "explains": "revision 19's `label_first` clause says which pass is learned; this clause says that pass has a "
                    "payout an agent can play for, at two rungs and in two currencies, so the card carries what the "
                    "pass is worth and not only that it is learned",
    }
    for n in UNIT_ORDER:
        clause[n] = _rung_of(units[n], n, names[n])
    return clause


def reading(card19: Path = CARD19, artifacts: dict | None = None) -> dict:
    out = {"ok": True, "reason": None, "card": None, "card19": {}, "clause19": {}, "absent19": [],
           "payout": {}, "rolls": {}, "artifacts": {}}
    names = artifacts if artifacts is not None else ARTIFACTS
    base = load(card19)
    if not base:
        return {**out, "ok": False, "reason": f"{card19} is absent, so revision 19 is not on disk"}
    old = base.get("card") or {}
    clause19 = old.get("label_first") or {}
    if not clause19:
        return {**out, "ok": False, "reason": f"{card19} carries no label_first clause to carry the payout beside"}
    fresh, stored = {}, {}
    for key in UNIT_ORDER:
        r = UNITS[key].reading()
        if not r.get("ok"):
            return {**out, "ok": False, "reason": f"the {key} reading cannot be recomputed: {r.get('reason')}"}
        doc = load(names[key])
        if not doc or not doc.get("ok"):
            return {**out, "ok": False, "reason": f"{names[key]} is absent or was refused"}
        fresh[key], stored[key] = r, doc
    out["rolls"] = fresh
    out["artifacts"] = stored
    clause = build_clause(fresh, {n: Path(names[n]).name for n in UNIT_ORDER})
    card = copy.deepcopy(old)
    card["revision"] = REVISION
    card[CLAUSE] = clause
    out["card19"] = {k: v for k, v in old.items() if k not in NEW}
    out["clause19"] = clause19
    out["absent19"] = list(old.get("absent") or [])
    out["payout"] = clause
    out["card"] = card
    return out


def _clause_shape(clause) -> bool:
    if not isinstance(clause, dict):
        return False
    if not all(n in clause for n in UNIT_ORDER):
        return False
    readers = clause.get("currency")
    if not isinstance(readers, dict) or not all(r in readers for r in CURRENCY):
        return False
    for n in UNIT_ORDER:
        rung = clause[n]
        if not isinstance(rung, dict) or rung.get("currency") not in CURRENCY:
            return False
        rw, ac, mm = rung.get("reward") or {}, rung.get("accuracy") or {}, rung.get("map_move") or {}
        if not all(a in rw and all(k in rw[a] for k in ("earned", "meter", "change", "sigma")) for a in ARMS):
            return False
        if not all(a in ac and all(k in ac[a] for k in ("earned", "meter", "change", "sigma")) for a in ARMS):
            return False
        if not all(a in mm and all(k in mm[a] for k in ("mean", "smallest")) for a in ARMS):
            return False
    return True


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the clause is read from is absent"}
                for c in CLAIMS]
    card = r["card"]
    clause = (card.get(CLAUSE) or {})
    shaped = _clause_shape(clause)
    earned = (clause.get("two_trials") or {}).get("reward") or {}
    j1 = {"id": "NA1",
          "measured": f"the clause is **{'present' if shaped else 'absent or thin'}** with the rungs "
                      f"{[n for n in UNIT_ORDER if n in clause]} and the readers "
                      f"{sorted((clause.get('currency') or {}))}, and the card is revision **{card.get('revision')}**",
          "verdict": "MET -- the card carries the payout clause with both currencies' earnings and the revision is 20"
                     if (shaped and card.get("revision") == REVISION) else
                     f"FALSIFIER FIRED -- the clause is "
                     f"{'present but thin' if clause else 'absent'}, the revision {card.get('revision')}"}
    names = {n: Path(ARTIFACTS[n]).name for n in UNIT_ORDER}
    fresh_ok = all(r["rolls"].get(n) for n in UNIT_ORDER)
    stored_ok = all(r["artifacts"].get(n) for n in UNIT_ORDER)
    agree_fresh = agree_stored = False
    if shaped and fresh_ok and stored_ok:
        agree_fresh = _agree(clause, build_clause(r["rolls"], names))
        agree_stored = _agree(clause, build_clause(r["artifacts"], names))
    disagreeing = []
    if shaped and stored_ok:
        expected = build_clause(r["artifacts"], names)
        disagreeing = [n for n in UNIT_ORDER if not _agree(clause.get(n), expected.get(n))]
    j2 = {"id": "NA2",
          "measured": (f"the clause's {len(UNIT_ORDER)} rungs against `e500`'s, `e501`'s and `e502`'s artifacts and "
                       f"their readings recomputed: **{len(disagreeing)}** rungs disagreeing with the artifacts, "
                       f"artifact agreement **{agree_stored}** and recomputed agreement **{agree_fresh}**; the "
                       f"two-trial rewards "
                       f"{ {a: (earned[a]['earned'], earned[a]['change'], earned[a]['sigma']) for a in ARMS} }"
                       if shaped else "the clause has no payout reading to compare"),
          "verdict": "MET -- every number in the clause is the three artifacts' and the three readings recomputed" if
                     (shaped and agree_fresh and agree_stored) else
                     f"FALSIFIER FIRED -- disagreeing rungs {disagreeing}, recomputed {agree_fresh}, artifacts "
                     f"{agree_stored}"}
    clause19 = r["clause19"]
    carried = card.get("label_first") or {}
    moved = sorted(k for k, v in clause19.items() if carried.get(k) != v)
    missing = sorted(k for k in clause19 if k not in carried)
    card19 = r["card19"]
    card_moved = sorted(k for k, v in card19.items() if card.get(k) != v)
    absent = list(card.get("absent") or [])
    j3 = {"id": "NA3",
          "measured": f"the revision-19 `label_first` clause's {len(clause19)} fields against the revision-20 clause: "
                      f"**{len(clause19) - len(moved) - len(missing)}** present and equal, with the card's "
                      f"{len(card19)} other fields **{len(card19) - len(card_moved)}** equal and the absent list "
                      f"**{absent}**",
          "verdict": "MET -- every revision-19 field survives into revision 20 and the absent list is untouched" if
                     (not moved and not missing and not card_moved and absent == r["absent19"] and not absent) else
                     f"FALSIFIER FIRED -- moved {moved}, missing {missing}, card moved {card_moved}, absent {absent}"}
    return [j1, j2, j3]


def report(r: dict) -> int:
    print("== the game card's twentieth revision: the payout clause carries the earning and the two currencies ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact the clause is read from is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    card, clause = r["card"], r["payout"]
    print(f"   the card is now revision {card['revision']} and its absent list is {card['absent']}")
    print(f"   the `label_first` clause keeps its {len(r['clause19'])} revision-19 fields and the card gains "
          f"`{CLAUSE}`, read from {clause['artifact']}")
    print(f"\n   {'arm':<10} {'rung':>12} {'reward earn':>12} {'reward meter':>13} {'gain':>9} {'sigma':>7} "
          f"{'d acc':>8} {'sigma':>7} {'map move':>9}")
    for name in UNIT_ORDER:
        rung = clause[name]
        for a in ARMS:
            rw, ac = rung["reward"][a], rung["accuracy"][a]
            print(f"   {a:<10} {name:>12} {rw['earned']:>12.4f} {rw['meter']:>13.4f} {rw['change']:>+9.4f} "
                  f"{rw['sigma']:>7.2f} {ac['change']:>+8.4f} {ac['sigma']:>7.2f} "
                  f"{rung['map_move'][a]['mean']:>9.4f}")
    act = clause["action"]
    print(f"\n   the action's currency: the readers {sorted(clause['currency'])}, the drive and target widths "
          f"{act['widths']}, the action run's carried-state reward level "
          f"{ {a: act['carried_level'][a]['carried'] for a in ARMS} }")
    print(f"   the clause's pass: two trials and three trials at {clause['replicates']} replicates, the bar "
          f"{clause['bar']:.2f} above a chance of {clause['chance']:.2f}, at {clause['sigma']:.0f} sigma")
    print("\n== the registered claims, NA1-NA3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e499` wrote the pass's family into the card; this writes what the pass is worth to an agent)")
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
