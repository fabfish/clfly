"""E508 -- the game card's twenty-first revision: the `label_first` clause carries the window its placement names.

Revision 20 wrote the card's `label_first` clause around the label's **placement** -- where in the pass the label's
cue sits -- because that is what `e495` moved. Two units since have shown the clause carries the **wrong variable**.
`e506` measured eight placements -- two trials at trial **0** and **1**, three trials at trial **0**, **1** and
**2**, four trials at trial **0**, **1** and **2** -- and found the pass is ordered by the **window** in drive
steps, the distance between the label's cue and the read, `11 - i * 12/N` for the label at trial `i` of an `N`-trial
pass, and not by the position: the two placements at window **5**, at different pass lengths and different trials,
agree to **0.0128**, inside the window-eleven family's own spread of **0.0312**, and the four-trial window-**8**
point sits above the three-trial window-**7** point, the same position in the pass's order, by **+0.0379** to
**+0.0511**. `e505` measured the three-trial placements and their windows **11**, **7** and **3**. **So the card's
`label_first` clause should carry the window**, and this unit writes it down: a **`windows`** field added inside
that clause, carrying the eight placements the corpus holds with their pass lengths, trial indices, windows, each
arm's accuracy diagonal and the label's own share of the read, read from `e495`'s, `e497`'s, `e505`'s and `e506`'s
artifacts and from their readings recomputed rather than quoted, along with the two comparisons that decide the
variable, with the card now revision **21** and every revision-20 field checked equal rather than rewritten.

Four claims, registered before this unit's pass over the four readings.

- **NA1 -- the card carries the window and the revision is 21.** The `label_first` clause carries a **`windows`**
  structure naming, for every placement the corpus holds, its pass length, its trial index, its window, each arm's
  accuracy diagonal and the label's own share of the read; and the artifact's `revision` is **21**. **Falsifier**:
  the clause carries no window, or the revision is not 21; refused when the revision-20 card is absent.
- **NA2 -- the window table is the runs' own.** Every accuracy and every share the clause carries is read from
  `e495`'s, `e497`'s, `e505`'s and `e506`'s artifacts and from their readings recomputed, and every one agrees to
  the precision the clause records. **Falsifier**: any field disagreeing with an artifact or with the recomputed
  reading; refused when an artifact is absent or a reading cannot be recomputed.
- **NA3 -- the revision is backward-compatible with revision 20.** Every clause field revision 20 carried is still
  present and equal, every field of the card outside the clauses is equal to revision 20's, and `absent` is still
  the empty list. **Falsifier**: a revision-20 field moved or disappeared, or an `absent` list that grew; refused
  when the revision-20 card is absent.
- **NA4 -- the clause says which variable orders the pass.** The clause records, beside the table, the two
  comparisons that decide it -- the placements that share a **window** across different pass lengths and read alike
  within the registered spread, and the placements that share a **position** across different pass lengths and do
  not -- with the numbers both comparisons carry. **Falsifier**: the clause carries the table without either
  comparison, or carries a spread or a difference disagreeing with the readings.

**What it can do beyond that.** It puts the variable `e506` separated into the clause `e495`, `e496` and `e499`
each wrote around the placement, so a reader meets not a name for where the label sits but the quantity that name
stands for, the drive steps between the label's cue and the read, together with the two comparisons that say so:
the same-window placements agreeing across pass lengths and the same-position placements not agreeing. It is the
first revision of this card whose clause carries a **unit** rather than a setting, and it closes the revision-20
finding's own *the pass's length is carried to three trials and no further* on the four-trial split's side.

**What it cannot do.** *A clause is not a result*: NA3 shows revision 20 survives into revision 21 and not that
revision 20 was right, and the table's numbers are four units' readings rather than an independent draw. *And the
table is eight placements over three pass lengths*: two, three and four trials, with window **11** carried by three
of them and window **5** by two, so window **8**, window **7** and window **3** are each a single pass length -- a
placement and not a test -- and the six-trial split and the placements beyond each pass's own trials are not in it.
*And the pass's length and the trial's length move together*: the pass is twelve steps, so the label at trial `i` of
`N` trials leaves `11 - i * 12/N` drive steps and one more trial is one more **cue** and a shorter **trial** at
once; what would separate a step's worth of window from a trial's is a twelve-step pass with a fixed trial length,
and that is not measured here. *And the payout is not on the placement runs*: the eight runs behind the table carry
no `--loop-reward`, so nothing in the window it carries is read against the world's currency; `e507` put the payout
on one placement, the three-trial label-at-1, and that is a different reading. *And one world, budget and seed
stream*: every run behind the table is the card's own setting with `--seed0 0`, so a second world and a second
stream are not in it.
"""

from __future__ import annotations

import argparse
import copy
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e495_the_label_first as e495
from experiments import e497_the_label_first_at_three_trials as e497
from experiments import e505_where_in_the_pass_the_label_sits as e505
from experiments import e506_the_window_or_the_position as e506

#: the card this revision is written from, and the four units whose readings the new field carries
CARD20 = Path("runs/e503_the_game_card_revision_twenty.json")
UNITS = ("e495", "e497", "e505", "e506")
READINGS = {"e495": e495.reading, "e497": e497.reading, "e505": e505.reading, "e506": e506.reading}
ARTIFACTS = {"e495": Path("runs/e495_the_label_first.json"),
             "e497": Path("runs/e497_the_label_first_at_three_trials.json"),
             "e505": Path("runs/e505_where_in_the_pass_the_label_sits.json"),
             "e506": Path("runs/e506_the_window_or_the_position.json")}
ARMS = e506.ARMS
TAU = e506.TAU
CHANCE = e506.CHANCE
BAR = e495.BAR
#: the revision this unit writes, the clause the window goes in, and the field the clause gains
REVISION = 21
CLAUSE = "label_first"
FIELD = "windows"
NEW = ("revision", CLAUSE)
#: how many places of the numbers the clause records are compared at
PLACES = 4
SIGMA_PLACES = 2
#: every placement the corpus holds: the key, the pass's length in trials, the 0-based trial index of the cue the
#: label names, and the readings that carry it -- the first source is the one the clause records and every other is
#: a cross-check, so the same placement is read out of more than one artifact wherever the corpus holds it twice
PLACEMENTS = (
    ("two_at0", 2, 0, (("e495", "first"), ("e497", "two"), ("e506", "two_at0"))),
    ("two_at1", 2, 1, (("e495", "last"), ("e506", "two_at1"))),
    ("three_at0", 3, 0, (("e497", "three"), ("e505", "at0"), ("e506", "three_at0"))),
    ("three_at1", 3, 1, (("e505", "at1"), ("e506", "three_at1"))),
    ("three_at2", 3, 2, (("e505", "at2"), ("e506", "three_at2"))),
    ("four_at0", 4, 0, (("e506", "four_at0"),)),
    ("four_at1", 4, 1, (("e506", "four_at1"),)),
    ("four_at2", 4, 2, (("e506", "four_at2"),)),
)


def window(trials: int, at: int) -> int:
    """The drive steps between the label's cue and the read at the pass's last step.

    The pass is twelve steps of ``tau // trials`` each, so the label at trial ``at`` of ``trials`` trials leaves
    ``tau - 1 - at * (tau // trials)`` drive steps. **The pass's length and the trial's length move together here**,
    and a trial's worth of window is not separated from a step's.
    """
    return (TAU - 1) - at * (TAU // trials)


#: each placement's window in drive steps
WINDOW = {key: window(trials, at) for key, trials, at, _ in PLACEMENTS}
#: the windows carried by more than one pass length, which are the tests NA4's window comparison reads
SHARED = {w: [k for k, _, _, _ in PLACEMENTS if WINDOW[k] == w] for w in sorted(set(WINDOW.values()), reverse=True)}
SHARED = {w: keys for w, keys in SHARED.items() if len(keys) > 1}
#: the largest window, whose family's own spread is the registered bound
BIG_WINDOW = max(SHARED)
#: the pair NA4's second comparison holds at one position across two pass lengths: the pass's second trial
POSITION = ("four_at1", "three_at1")
CLAIMS = (
    ("NA1", "the card carries the window and the revision is 21",
     "The label_first clause carries a windows structure naming, for every placement the corpus holds, its pass "
     "length, its trial index, its window, each arm's accuracy diagonal and the label's own share of the read, and "
     "the artifact's revision is 21",
     "falsifier: the clause carries no window, or the revision is not 21; refused when the revision-20 card is "
     "absent"),
    ("NA2", "the window table is the runs' own",
     "Every accuracy and every share the clause carries is read from e495's, e497's, e505's and e506's artifacts and "
     "from their readings recomputed, and every one agrees to the precision the clause records",
     "falsifier: any field disagreeing with an artifact or with the recomputed reading; refused when an artifact is "
     "absent or a reading cannot be recomputed"),
    ("NA3", "the revision is backward-compatible with revision 20",
     "Every clause field revision 20 carried is still present and equal, every field of the card outside the clauses "
     "is equal to revision 20's, and absent is still the empty list",
     "falsifier: a revision-20 field moved or disappeared, or an absent list that grew; refused when the revision-20 "
     "card is absent"),
    ("NA4", "the clause says which variable orders the pass",
     "The clause records, beside the table, the two comparisons that decide it -- the placements that share a window "
     "across different pass lengths and read alike within the registered spread, and the placements that share a "
     "position across different pass lengths and do not -- with the numbers both comparisons carry",
     "falsifier: the clause carries the table without either comparison, or carries a spread or a difference "
     "disagreeing with the readings"),
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


def _pair(roll: dict, share) -> dict:
    """One placement's accuracies from a roll of replicates: the means unrounded for the comparisons, rounded for
    the table, beside the label's own share of the read."""
    means = {a: float(statistics.fmean(roll["arms"][a]["accuracy_diagonal"])) for a in ARMS}
    return {"exact": means, "accuracy": {a: round(means[a], PLACES) for a in ARMS}, "share": float(share)}


def _extract_e495(unit: dict) -> dict:
    """The two-trial placements, keyed by the labels `e495`'s own runs carry them under."""
    rolls, sh = unit["runs"], unit["share"]
    return {"first": _pair(rolls["first"], sh["first"]["share"]),
            "last": _pair(rolls["last"], sh["last"]["share"])}


def _extract_e497(unit: dict) -> dict:
    """The two- and three-trial label-first placements, keyed by `e497`'s own labels."""
    rolls, sh = unit["runs"], unit["share"]
    return {"two": _pair(rolls["two"], sh["two"]["share"]),
            "three": _pair(rolls["three"], sh["three"]["share"])}


def _extract_e505(unit: dict) -> dict:
    """The three-trial placements, keyed by `e505`'s own labels."""
    rolls, sh = unit["runs"], unit["share"]
    return {f"at{at}": _pair(rolls[f"at{at}"], sh[f"at{at}"]["share"]) for at in (0, 1, 2)}


def _extract_e506(unit: dict) -> dict:
    """All eight placements, keyed by the table's own placement keys."""
    rolls, sh = unit["placements"], unit["share"]
    return {key: _pair(rolls[key], sh[key]["share"]) for key, _, _, _ in PLACEMENTS}


#: how each unit's reading -- and the artifact that reading wrote, which carries the same rolls -- is read into the
#: placements it carries, keyed by the label that unit's own run uses
EXTRACT = {"e495": _extract_e495, "e497": _extract_e497, "e505": _extract_e505, "e506": _extract_e506}


def _replicates(unit: dict) -> list:
    return sorted(int(v) for v in ((unit or {}).get("spans") or {}).get("replicates") or [])


def _exact(units: dict) -> dict:
    """Each placement's unrounded accuracies, its share and every source that carries it: the first source's numbers
    and the names of all of them, which is what the table records and the comparisons differ."""
    out = {}
    for key, _, _, sources in PLACEMENTS:
        picks = []
        for unit, where in sources:
            got = EXTRACT[unit](units[unit])
            if where in got:
                picks.append((f"{unit}:{where}", got[where]))
        if picks:
            out[key] = {**picks[0][1], "read_from": [name for name, _ in picks]}
    return out


#: how many (placement, source) readings the table's eight placements carry in all
SOURCES = sum(len(sources) for _, _, _, sources in PLACEMENTS)


def _source_disagreements(rows: dict, units: dict) -> list:
    """Every source's own accuracy and share against the row the table records, at the clause's precision.

    The table records one source per placement and names the rest in `read_from`; this reads each of them, so a
    placement the corpus holds twice is checked twice rather than once.
    """
    bad = []
    for key, _, _, sources in PLACEMENTS:
        row = rows.get(key) or {}
        for unit, where in sources:
            got = EXTRACT[unit](units[unit]).get(where)
            if got is None:
                bad.append(f"{key}:{unit}:{where}: absent")
                continue
            if not all(_at((row.get("accuracy") or {}).get(a), got["accuracy"][a], PLACES) for a in ARMS):
                bad.append(f"{key}:{unit}:{where}: accuracy")
            if not _at(row.get("share"), got["share"], PLACES):
                bad.append(f"{key}:{unit}:{where}: share")
    return bad


def build_comparisons(exact: dict) -> dict:
    """The two comparisons that decide the variable, built from the placements' own accuracies.

    The **window** comparison groups the placements by window, so the families carried by more than one pass length
    are the tests, and reads each family's spread against the registered bound, which is the largest window's own
    family spread. The **position** comparison holds the pass's second trial -- one cue before the label -- at two
    pass lengths and reads the difference between the two placements there. The same function builds the clause and
    the check: a family's spread is taken from the unrounded means, so it is the runs' own rather than a difference
    of the table's recorded places, and the pair's difference is read off the two endpoints as the table records
    them, with the unrounded difference carried beside it.
    """
    families = {}
    for w, keys in SHARED.items():
        here = [k for k in keys if k in exact]
        if len(here) < 2:
            continue
        spread = {a: round(max(exact[k]["exact"][a] for k in here)
                           - min(exact[k]["exact"][a] for k in here), PLACES) for a in ARMS}
        families[str(w)] = {"window": w, "placements": here, "spread": spread, "largest": max(spread.values())}
    bound = families[str(BIG_WINDOW)]["largest"] if str(BIG_WINDOW) in families else None
    alike = bool(families) and bound is not None and all(f["largest"] <= bound + 1e-9 for f in families.values())
    same_window = {"bound": bound, "bound_window": BIG_WINDOW, "families": families, "alike": alike}
    a, b = POSITION
    if a in exact and b in exact:
        difference = {arm: round(exact[a]["accuracy"][arm] - exact[b]["accuracy"][arm], PLACES) for arm in ARMS}
        unrounded = {arm: round(exact[a]["exact"][arm] - exact[b]["exact"][arm], PLACES) for arm in ARMS}
        smallest = round(min(abs(v) for v in difference.values()), PLACES)
        same_position = {"position": "the label at the pass's second trial, one cue before it",
                         "placements": [a, b], "windows": [WINDOW[a], WINDOW[b]],
                         "difference": difference, "difference_unrounded": unrounded,
                         "smallest": smallest, "bound": bound,
                         "alike": (smallest <= bound + 1e-9) if bound is not None else None}
    else:
        same_position = {}
    return {"same_window": same_window, "same_position": same_position}


def build_windows(units: dict, names: dict) -> dict:
    """The `windows` field of the `label_first` clause, built from the four units' readings -- the one function the
    card and the check both use. Each placement's numbers come from the first source that carries it, and every
    other source is a cross-check NA2's own judge makes."""
    exact = _exact(units)
    table = {}
    for key, trials, at, sources in PLACEMENTS:
        got = exact.get(key)
        if got is None:
            continue
        table[key] = {"trials": trials, "trial": at, "window": WINDOW[key],
                      "accuracy": {a: round(got["accuracy"][a], PLACES) for a in ARMS},
                      "share": round(got["share"], PLACES),
                      "read_from": list(got["read_from"])}
    return {
        "artifact": [names[u] for u in UNITS],
        "flag": "--loop-episode N with --loop-label-at i, the label's cue at trial i of an N-trial pass",
        "arms": list(ARMS),
        "chance": CHANCE,
        "bar": BAR,
        "replicates": sorted({v for u in UNITS for v in _replicates(units[u])}),
        "tau": TAU,
        "formula": "the window is the drive steps between the label's cue and the read, 11 - i * 12/N for the label "
                   "at trial i of an N-trial pass",
        "placements": table,
        "comparisons": build_comparisons(exact),
        "explains": "revision 20's `label_first` clause names the label's placement, where in the pass its cue sits; "
                    "this field names what that placement is a name for, the drive steps between the label's cue and "
                    "the read, and the eight placements the corpus holds, with the two comparisons that decide it",
    }


def reading(card20: Path = CARD20, artifacts: dict | None = None) -> dict:
    out = {"ok": True, "reason": None, "card": None, "card20": {}, "clause20": {}, "absent20": [],
           "windows": {}, "rolls": {}, "artifacts": {}}
    names = artifacts if artifacts is not None else ARTIFACTS
    base = load(card20)
    if not base:
        return {**out, "ok": False, "reason": f"{card20} is absent, so revision 20 is not on disk"}
    old = base.get("card") or {}
    clause20 = old.get(CLAUSE) or {}
    if not clause20:
        return {**out, "ok": False, "reason": f"{card20} carries no label_first clause to carry the window in"}
    fresh, stored = {}, {}
    for unit in UNITS:
        doc = load(names[unit])
        if not doc or not doc.get("ok"):
            return {**out, "ok": False, "reason": f"{names[unit]} is absent or was refused"}
        try:
            recomputed = READINGS[unit]()
        except (ImportError, OSError, ValueError) as exc:
            return {**out, "ok": False, "reason": f"the {unit} reading cannot be recomputed: {exc}"}
        if not recomputed.get("ok"):
            return {**out, "ok": False,
                    "reason": f"the {unit} reading cannot be recomputed: {recomputed.get('reason')}"}
        stored[unit], fresh[unit] = doc, recomputed
    out["rolls"], out["artifacts"] = fresh, stored
    windows = build_windows(fresh, {u: Path(names[u]).name for u in UNITS})
    clause = copy.deepcopy(clause20)
    clause[FIELD] = windows
    card = copy.deepcopy(old)
    card["revision"] = REVISION
    card[CLAUSE] = clause
    out["card20"] = {k: v for k, v in old.items() if k not in NEW}
    out["clause20"] = clause20
    out["absent20"] = list(old.get("absent") or [])
    out["windows"] = windows
    out["card"] = card
    return out


def _windows_shape(field) -> bool:
    if not isinstance(field, dict):
        return False
    table = field.get("placements")
    if not isinstance(table, dict):
        return False
    for key, trials, at, _ in PLACEMENTS:
        row = table.get(key)
        if not isinstance(row, dict):
            return False
        if row.get("trials") != trials or row.get("trial") != at or row.get("window") != WINDOW[key]:
            return False
        acc = row.get("accuracy")
        if not isinstance(acc, dict) or not all(a in acc for a in ARMS):
            return False
        if not isinstance(row.get("share"), (int, float)) or isinstance(row.get("share"), bool):
            return False
    return True


def _comparison_shape(comp) -> bool:
    if not isinstance(comp, dict):
        return False
    sw, sp = comp.get("same_window"), comp.get("same_position")
    if not isinstance(sw, dict) or not isinstance(sw.get("families"), dict) or not sw["families"]:
        return False
    if "bound" not in sw or "alike" not in sw:
        return False
    if not isinstance(sp, dict) or "difference" not in sp or "smallest" not in sp or "placements" not in sp:
        return False
    return True


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the clause is read from is absent"}
                for c in CLAIMS]
    card = r["card"]
    clause = card.get(CLAUSE) or {}
    field = clause.get(FIELD)
    shaped = _windows_shape(field)
    rows = (field or {}).get("placements") or {}
    #: NA1 -- the card carries the window and the revision is 21
    j1 = {"id": "NA1",
          "measured": f"the `label_first` clause carries a **{'windows' if shaped else 'thin'}** field naming "
                      f"**{len(rows)}** of the **{len(PLACEMENTS)}** placements with their pass lengths, trials and "
                      f"windows, and the card is revision **{card.get('revision')}**",
          "verdict": "MET -- the label_first clause carries the window table for every placement the corpus holds "
                     "and the revision is 21" if (shaped and card.get("revision") == REVISION) else
                     f"FALSIFIER FIRED -- the window field is "
                     f"{'present but thin' if field else 'absent'}, the revision {card.get('revision')}"}
    #: NA2 -- the window table is the runs' own
    names = {u: Path(ARTIFACTS[u]).name for u in UNITS}
    fresh_ok = all(r["rolls"].get(u) for u in UNITS)
    stored_ok = all(r["artifacts"].get(u) for u in UNITS)
    agree_fresh = agree_stored = False
    disagreeing = []
    source_bad = []
    if shaped and fresh_ok and stored_ok:
        agree_fresh = _agree(field, build_windows(r["rolls"], names))
        expected = build_windows(r["artifacts"], names)
        agree_stored = _agree(field, expected)
        disagreeing = [k for k, _, _, _ in PLACEMENTS
                       if not _agree(rows.get(k), expected.get("placements", {}).get(k))]
        #: every source the table names, and not only the one it records, read against the row it records
        source_bad = (_source_disagreements(rows, r["artifacts"])
                      + _source_disagreements(rows, r["rolls"]))
    ladder = {str(w): [rows[k]["share"] for k in keys if k in rows] for w, keys in
              sorted(SHARED.items(), reverse=True)} if shaped else {}
    j2 = {"id": "NA2",
          "measured": (f"the table's **{len(rows)}** placements, and every one of the **{SOURCES}** source readings "
                       f"they are carried in, against `e495`'s, `e497`'s, `e505`'s and `e506`'s artifacts and their "
                       f"four readings recomputed: **{len(disagreeing)}** placements disagreeing with the artifacts "
                       f"and **{len(source_bad)}** source readings disagreeing ({source_bad}), artifact agreement "
                       f"**{agree_stored}** and recomputed agreement **{agree_fresh}**; the shares by window "
                       f"{ {w: [round(x, PLACES) for x in v] for w, v in ladder.items()} }"
                       if shaped else "the clause has no window table to compare"),
          "verdict": "MET -- every accuracy and every share in the table is the four artifacts' and the four "
                     "readings recomputed, at every source each placement is carried in" if
                     (shaped and agree_fresh and agree_stored and not disagreeing and not source_bad) else
                     f"FALSIFIER FIRED -- disagreeing placements {disagreeing}, source readings {source_bad}, "
                     f"recomputed {agree_fresh}, artifacts {agree_stored}"}
    #: NA3 -- the revision is backward-compatible with revision 20
    clause20 = r["clause20"]
    carried = card.get(CLAUSE) or {}
    moved = sorted(k for k, v in clause20.items() if carried.get(k) != v)
    missing = sorted(k for k in clause20 if k not in carried)
    card20 = r["card20"]
    card_moved = sorted(k for k, v in card20.items() if card.get(k) != v)
    absent = list(card.get("absent") or [])
    j3 = {"id": "NA3",
          "measured": f"the revision-20 `label_first` clause's {len(clause20)} fields against the revision-21 "
                      f"clause: **{len(clause20) - len(moved) - len(missing)}** present and equal, with the card's "
                      f"{len(card20)} other fields **{len(card20) - len(card_moved)}** equal and the absent list "
                      f"**{absent}**",
          "verdict": "MET -- every revision-20 field survives into revision 21 and the absent list is untouched" if
                     (not moved and not missing and not card_moved and absent == r["absent20"] and not absent) else
                     f"FALSIFIER FIRED -- moved {moved}, missing {missing}, card moved {card_moved}, absent {absent}"}
    #: NA4 -- the clause says which variable orders the pass
    comp = (field or {}).get("comparisons") or {}
    comp_shaped = _comparison_shape(comp)
    #: the comparisons recomputed from the units' own rolls, not from the table's recorded places
    expected_comp = {}
    comp_agree = False
    if comp_shaped and stored_ok:
        expected_comp = build_comparisons(_exact(r["artifacts"]))
        comp_agree = _agree(comp, expected_comp)
        if comp_agree and fresh_ok:
            comp_agree = _agree(comp, build_comparisons(_exact(r["rolls"])))
    sw = comp.get("same_window") or {}
    sp = comp.get("same_position") or {}
    families = sw.get("families") or {}
    j4 = {"id": "NA4",
          "measured": (f"the comparisons beside the table: the same-window families "
                        f"{ {w: (f['placements'], f['largest']) for w, f in families.items()} } against the "
                        f"registered bound **{sw.get('bound')}** (window {sw.get('bound_window')}'s own), and the "
                        f"same-position pair {sp.get('placements')} at windows {sp.get('windows')} differing "
                        f"{sp.get('difference')} with **{sp.get('smallest')}** the smallest, against the same bound; "
                        f"agreement with the recomputed comparisons **{comp_agree}**"
                        if comp_shaped else "the clause carries the table without both comparisons"),
          "verdict": "MET -- the clause carries both comparisons: the same-window families read alike inside the "
                     "registered bound and the same-position pair does not inside it" if
                     (comp_shaped and comp_agree and sw.get("alike") and sp.get("alike") is False) else
                     f"FALSIFIER FIRED -- the comparisons are "
                     f"{'present but disagreeing with the readings' if comp_shaped else 'absent or thin'}, "
                     f"same-window alike {sw.get('alike')}, same-position alike {sp.get('alike')}, "
                     f"agreement {comp_agree}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the game card's twenty-first revision: the label_first clause carries the window ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact the clause is read from is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    card, field = r["card"], r["windows"]
    print(f"   the card is now revision {card['revision']} and its absent list is {card['absent']}")
    print(f"   the `label_first` clause keeps its {len(r['clause20'])} revision-20 fields and gains `{FIELD}`, "
          f"read from {field['artifact']}")
    print(f"\n   {'placement':<11} {'pass':>4} {'trial':>5} {'window':>6} {'share':>8}  "
          + "  ".join(f"{a:>9}" for a in ARMS))
    for key, trials, at, _ in PLACEMENTS:
        row = field["placements"].get(key)
        if row is None:
            print(f"   {key:<11} {trials:>4} {at:>5} {WINDOW[key]:>6} {'-':>8}  "
                  + "  ".join(f"{'-':>9}" for _ in ARMS))
            continue
        print(f"   {key:<11} {trials:>4} {at:>5} {WINDOW[key]:>6} {row['share']:>8.4f}  "
              + "  ".join(f"{row['accuracy'][a]:>9.4f}" for a in ARMS))
    comp = field["comparisons"]
    sw, sp = comp["same_window"], comp["same_position"]
    print(f"\n   the same-window families against the registered bound of {sw['bound']} (window "
          f"{sw['bound_window']}'s own): "
          + "; ".join(f"window {w}: {f['placements']} spread {f['spread']}" for w, f in sw["families"].items()))
    print(f"   the same-position pair {sp['placements']} at windows {sp['windows']}: difference {sp['difference']} "
          f"(smallest {sp['smallest']}), against the same bound")
    print("\n== the registered claims, NA1-NA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e495` moved the label and `e496` wrote where it sits; this writes the drive steps that name it)")
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
