"""E486 -- the game card's sixteenth revision: the reward, and the clause that reads it.

`e485` gave the runner `--loop-reward`, read its first run, and closed on *"what remains for the card is the revision
that takes a reward off its absent list, and the episode boundary."* The list has carried **a reward** since the
card's first revision, and `e482`'s fifteenth took the **policy** off it one revision ago by the same route.

**This unit writes revision 16.** One clause is added, the **reward**, carrying `e485`'s readings recomputed from the
two runs rather than quoted, and the `absent` list loses exactly one entry. Every other field is checked equal to
`e482`'s card. Four claims, registered before this unit's pass over the runs and the reading.

- **TA1 -- and the fifteenth revision is carried unchanged where it is not rewritten, and the absent list loses
  exactly one entry.** Every field of `e482`'s card except the revision, the new clause and `absent` is equal to the
  revision-15 card, with the revision now **16**, and `absent` is revision 15's with `a reward` removed and nothing
  else added or removed. **Falsifier**: any other field differing, the revision not 16, or an absent list that
  differs by anything but that one entry; refused when `e482`'s artifact is absent.
- **TA2 -- and the clause's numbers come out of the runs.** Every number the clause carries -- each arm's reward
  diagonal and last row with the paired contrast and its sigma, each arm's accuracy diagonal, and the replicate count
  -- equals the two runs recomputed, and equals `e485`'s reading of them on disk, to a thousandth of a point.
  **Falsifier**: any number disagreeing past the tolerance, or an arm or a replicate count differing; refused when a
  run or the reading is absent.
- **TA3 -- and the clause's bearing is that the two currencies disagree.** The clause carries the reward's diagonal
  **below** its last row on every arm, resolved at **two** sigma, beside the accuracy's diagonal **above** its last
  row. **Falsifier**: an arm whose reward contrast does not resolve, or one whose accuracy diagonal is not above its
  last row.
- **TA4 -- and the clause carries the reversal rather than hiding it.** The clause records **both** orderings of the
  three arms -- the accuracy's and the reward's -- and they disagree on at least one pair. **Falsifier**: either
  ordering missing from the clause, or the two agreeing.

**What it can do beyond that.** It makes the card's own account of its game match the corpus: the game now **pays**
an agent that chooses its action, and the `absent` list drops to **one** entry. Read with `e482` it is the second
revision in a row that removes a capability the environment has had for one or two units.

**What it cannot do.** *One revision of one world*: the clause is read from one run at one budget and one seed stream.
*And a clause is not a result*: TA1 shows revision 15 survives into revision 16 and not that revision 15 was right.
*And the clause carries a disagreement it cannot explain*: the reward's currency is the body's and the accuracy's is
the head's, which is the finding beside this unit and not something the card's shape holds. *And the reward is the
corpus's noisiest currency*: `e484` found its cue-share under its own scatter, so the clause's sigmas are large
numbers about small differences. *And the card still cannot say what an episode is*: the `absent` list's one
remaining entry is **an episode boundary**.
"""

from __future__ import annotations

import argparse
import copy
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e485_the_benchmark_pays_a_reward as e485

#: the card the clause is added to, its reading of the reward run, and the two runs it is read from
CARD15 = Path("runs/e482_the_game_card_revision_fifteen.json")
READING = Path("runs/e485_the_benchmark_pays_a_reward.json")
NEW_RUN = e485.NEW
BASE_RUN = e485.BASE
ARMS = e485.ARMS
HELD = "a reward"
REVISION = 16
NEW = ("revision", "reward", "absent")
TOL = 0.002
SIGMA = 2.0
CLAIMS = (
    ("TA1", "and the fifteenth revision is carried unchanged where it is not rewritten, and the absent list loses "
            "exactly one entry",
     "Every field of e482's card except the revision, the new clause and absent is equal to the revision-15 card, with "
     "the revision now 16, and absent is revision 15's with a reward removed and nothing else added or removed",
     "falsifier: any other field differing, the revision not 16, or an absent list that differs by anything but that "
     "one entry; refused when e482's artifact is absent"),
    ("TA2", f"and the clause's numbers come out of the runs, to {TOL:.3f}",
     "Every number the clause carries equals the two runs recomputed, and equals e485's reading of them on disk, to a "
     "thousandth of a point",
     "falsifier: any number disagreeing past the tolerance, or an arm or a replicate count differing; refused when a "
     "run or the reading is absent"),
    ("TA3", f"and the clause's bearing is that the two currencies disagree, at {SIGMA:.0f} sigma",
     "The clause carries the reward's diagonal below its last row on every arm, resolved at two sigma, beside the "
     "accuracy's diagonal above its last row",
     "falsifier: an arm whose reward contrast does not resolve, or one whose accuracy diagonal is not above its last "
     "row"),
    ("TA4", "and the clause carries the reversal rather than hiding it",
     "The clause records both orderings of the three arms, the accuracy's and the reward's, and they disagree on at "
     "least one pair",
     "falsifier: either ordering missing from the clause, or the two agreeing"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def reading(card15: Path = CARD15, reading_path: Path = READING) -> dict:
    out = {"ok": True, "reason": None, "card": None, "revision15": {}, "absent15": [], "reward": {},
           "rolls": {}, "reading": {}}
    base = load(card15)
    if not base:
        return {**out, "ok": False, "reason": f"{card15} is absent, so revision 15 is not on disk"}
    old = base.get("card") or {}
    doc = load(reading_path)
    if not doc or not doc.get("ok"):
        return {**out, "ok": False, "reason": f"{reading_path} is absent or was refused"}
    out["reading"] = doc
    #: **recomputed from the two runs**, not copied from the reading: `e485.reading` is this corpus's own reader of
    #: exactly those two artifacts, and running it again here is what makes TA2 a check rather than a transcription
    fresh = e485.reading(new=NEW_RUN, base=BASE_RUN)
    if not fresh.get("ok"):
        return {**out, "ok": False, "reason": f"the two runs cannot be read: {fresh.get('reason')}"}
    out["rolls"] = fresh
    #: the card's roll carries no reward matrix, so its accuracy last row is read here and carried beside the new
    #: run's -- the comparison TA3's bearing needs
    base_doc = load(BASE_RUN) or {}
    acc_last = {}
    for a in ARMS:
        reps = ((base_doc.get("methods") or {}).get(a) or {}).get("replicates") or []
        if reps:
            acc_last[a] = statistics.fmean([statistics.fmean(x["final_per_task"]) for x in reps])
    out["acc_last"] = {a: acc_last.get(a) for a in ARMS}
    d = fresh["diagonal"]
    clause = {
        "artifact": [READING.name, NEW_RUN.name, BASE_RUN.name],
        "flag": "--loop-reward",
        "paid_by": "the world, against the target the cue itself sets one step after it arrives",
        "not_the_label": True,
        "arms": list(ARMS),
        "replicates": sorted({v["replicates"] for v in fresh["runs"]["reward"]["arms"].values()}),
        "reward": {a: {"diagonal": statistics.fmean(fresh["runs"]["reward"]["arms"][a]["reward_diagonal"]),
                       "last_row": statistics.fmean(fresh["runs"]["reward"]["arms"][a]["reward_last"]),
                       "contrast": d[a]["reward"]["mean"], "sigma": d[a]["reward"]["sigma"]} for a in ARMS},
        "accuracy": {a: {"diagonal": d[a]["accuracy_diagonal"], "last_row": out["acc_last"][a]} for a in ARMS},
        "orderings": {"accuracy": list(fresh["order"]["accuracy"]), "reward": list(fresh["order"]["reward"]),
                      "agree": bool(fresh["order"]["agrees"])},
        "first_task_one_training": bool(fresh["first"]["identical"]),
    }
    card = copy.deepcopy(old)
    card["revision"] = REVISION
    card["absent"] = [a for a in (old.get("absent") or []) if a != HELD]
    card["reward"] = clause
    out["revision15"] = {k: v for k, v in old.items() if k not in NEW}
    out["absent15"] = list(old.get("absent") or [])
    out["reward"] = clause
    out["card"] = card
    return out


def _close(a, b) -> bool:
    return a is not None and b is not None and abs(float(a) - float(b)) <= TOL / 2


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the clause is read from is absent"}
                for c in CLAIMS]
    card, c = r["card"], r["reward"]
    same = {k: (card.get(k) == v) for k, v in r["revision15"].items()}
    differ = sorted(k for k, v in same.items() if not v)
    old_absent, new_absent = r["absent15"], card.get("absent") or []
    lost = sorted(set(old_absent) - set(new_absent))
    gained = sorted(set(new_absent) - set(old_absent))
    j1 = {"id": "TA1",
          "measured": f"the revision-15 card's {len(same)} fields against the revision-16 card: "
                      f"{len(same) - len(differ)} equal, with the revision now {card.get('revision')}, and the absent "
                      f"list going from {old_absent} to {new_absent}",
          "verdict": "MET -- revision 15 is carried where it is not rewritten, and the absent list loses exactly the "
                     "reward" if (not differ and card.get("revision") == REVISION and lost == [HELD] and not gained)
                     else f"FALSIFIER FIRED -- differing {differ}, revision {card.get('revision')}, lost {lost}, "
                          f"gained {gained}"}
    fresh, stored = r["rolls"], r["reading"]
    off = []
    for a in ARMS:
        got = c["reward"][a]
        f = fresh["runs"]["reward"]["arms"][a]
        s = stored["diagonal"][a]["reward"]
        if not (_close(got["diagonal"], statistics.fmean(f["reward_diagonal"]))
                and _close(got["last_row"], statistics.fmean(f["reward_last"]))
                and _close(got["contrast"], s["mean"]) and _close(got["sigma"], s["sigma"])
                and _close(got["contrast"], fresh["diagonal"][a]["reward"]["mean"])
                and _close(c["accuracy"][a]["diagonal"], stored["diagonal"][a]["accuracy_diagonal"])):
            off.append(a)
    counts_ok = (c["arms"] == list(ARMS)
                 and c["replicates"] == [int(stored["spans"]["replicates"][0])]
                 and c["first_task_one_training"] == bool(stored["first"]["identical"]))
    j2 = {"id": "TA2",
          "measured": f"the clause carries {len(c['reward'])} arms' reward cells and accuracy diagonals at "
                      f"{c['replicates']} replicates with **{len(off)}** disagreeing past the tolerance, its "
                      f"replicates {c['replicates']} against the reading's {stored['spans']['replicates']}, and its "
                      f"first-task flag {c['first_task_one_training']}",
          "verdict": "MET -- every number in the clause is the two runs recomputed and the reading's" if
                     (not off and counts_ok) else
                     f"FALSIFIER FIRED -- disagreeing {off}, counts ok {counts_ok}"}
    below = [a for a in ARMS if c["reward"][a]["contrast"] < 0.0 and c["reward"][a]["sigma"] <= -SIGMA]
    above = [a for a in ARMS if c["accuracy"][a]["last_row"] is not None and
             c["accuracy"][a]["diagonal"] > c["accuracy"][a]["last_row"]]
    j3 = {"id": "TA3",
          "measured": f"the reward's diagonal less its last row is "
                      f"{ {a: round(c['reward'][a]['contrast'], 4) for a in ARMS} } at "
                      f"{ {a: round(c['reward'][a]['sigma'], 2) for a in ARMS} } sigma and the accuracy's is "
                      f"{ {a: round(c['accuracy'][a]['diagonal'] - c['accuracy'][a]['last_row'], 4) if c['accuracy'][a]['last_row'] is not None else None for a in ARMS} }",
          "verdict": "MET -- the reward's diagonal is below its last row on every arm, resolved, beside an accuracy "
                     "whose diagonal is above it" if (len(below) == len(ARMS) and len(above) == len(ARMS)) else
                     f"FALSIFIER FIRED -- resolving below on {below}, above on {above}"}
    o = c["orderings"]
    j4 = {"id": "TA4",
          "measured": f"the clause records the accuracy ordering {o['accuracy']} and the reward ordering "
                      f"{o['reward']}, and its own agreement flag is {o['agree']}",
          "verdict": "MET -- both orderings are in the clause and they disagree" if
                     (len(o["accuracy"]) == len(ARMS) and len(o["reward"]) == len(ARMS) and
                      o["accuracy"] != o["reward"] and o["agree"] is False) else
                     f"FALSIFIER FIRED -- {o}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the game card's sixteenth revision: the reward ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact the clause is read from is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    card, c = r["card"], r["reward"]
    print(f"   the card is now revision {card['revision']} and its absent list is {card['absent']}")
    print(f"   the new clause is `reward`, read from {c['artifact']}")
    print(f"\n   {'arm':<10} {'reward diagonal':>16} {'reward last row':>16} {'contrast':>10} {'sigma':>7} "
          f"{'accuracy diag':>14}")
    for a in ARMS:
        g = c["reward"][a]
        print(f"   {a:<10} {g['diagonal']:>16.4f} {g['last_row']:>16.4f} {g['contrast']:>+10.4f} {g['sigma']:>7.2f} "
              f"{c['accuracy'][a]['diagonal']:>14.4f}")
    print(f"\n   the clause's orderings: accuracy {c['orderings']['accuracy']} against reward "
          f"{c['orderings']['reward']}, agreeing {c['orderings']['agree']}")
    print("\n== the registered claims, TA1-TA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e482` removed a policy from the list when the runner first carried one;")
    print("    this unit removes a reward, and leaves the episode boundary where it is)")
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
