"""E482 -- the game card's fifteenth revision: the policy, and the clause that reads it.

`e481` gave the runner `--loop-policy` and read its first run, and its finding closed on *"the card's `absent` list
still names a policy, since the benchmark's own runs do not carry one by default; a card revision is a different
unit."* The list has carried **a policy** since the card's first revision.

**This unit writes revision 15.** One clause is added, the **policy**, carrying `e481`'s readings recomputed from the
two runs rather than quoted, and the `absent` list loses exactly one entry. Every other field is checked equal to
`e470`'s card. Four claims, registered before this unit's pass over the runs and the reading.

- **VA1 -- and the fourteenth revision is carried unchanged where it is not rewritten, and the absent list loses
  exactly one entry.** Every field of `e470`'s card except the revision, the new clause and `absent` is equal to the
  revision-14 card, with the revision now **15**, and `absent` is revision 14's with `a policy` removed and nothing
  else added or removed. **Falsifier**: any other field differing, the revision not 15, or an absent list that
  differs by anything but that one entry; refused when `e470`'s artifact is absent.
- **VA2 -- and the clause's numbers come out of the runs.** Every number the clause carries -- the policy's
  movements, each arm's diagonal and last row on both runs, and every paired contrast with its sigma -- equals the
  two runs recomputed, and equals `e481`'s reading of them on disk, to a thousandth of a point. **Falsifier**: any
  number disagreeing past the tolerance, or an arm or a replicate count differing; refused when a run or the reading
  is absent.
- **VA3 -- and the clause's bearing is that the freedom is used and the game is still learned.** The policy's distance
  from the identity is above zero on **every** replicate of the new run, and the `naive` arm's diagonal on it is at
  least **0.10** above the four-class chance of **0.25**. **Falsifier**: a replicate whose movement is zero or
  unrecorded, or a diagonal within **0.05** of chance.
- **VA4 -- and the clause carries what resolved rather than only what did not.** The clause records the contrasts at
  or past **two** sigma exactly as `e481`'s reading reports them, so the one that fired is in the card beside the
  five nulls. **Falsifier**: the clause's resolved list differing from the reading's, or a resolved contrast the
  clause does not record.

**What it can do beyond that.** It makes the card's own account of its game match the corpus: the game now has an
agent that chooses its action through something the benchmark trained, and the `absent` list is what it says it is.

**What it cannot do.** *One revision of one world*: the clause is read from one run at one budget and one seed
stream, so it is one configuration's. *And a clause is not a result*: VA1 shows revision 14 survives into revision 15
and not that revision 14 was right, and VA2 shows the clause agrees with the runs and not that the runs should be
believed. *And the card still cannot say what a policy is for*: the reward half of `e325`'s sentence is untouched, so
the `absent` list still names **a reward** and **an episode boundary**. *And the firing is carried and not
explained*: the clause says which contrast resolved and the finding beside it says the chance of one such firing in
six tests under the null is about **9%**, which is a caveat a clause cannot hold.
"""

from __future__ import annotations

import argparse
import copy
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e481_the_benchmark_carries_a_policy as e481

#: the card the clause is added to, its reading of the policy run, and the two runs it is read from
CARD14 = Path("runs/e470_the_game_card_revision_fourteen.json")
READING = Path("runs/e481_the_benchmark_carries_a_policy.json")
NEW_RUN = Path("runs/e481_earned_label_policy_20reps.json")
BASE_RUN = Path("runs/e438_earned_label_three_arms_20reps.json")
ARMS = ("naive", "ewc-block", "replay")
HELD = "a policy"
REVISION = 15
NEW = ("revision", "policy", "absent")
TOL = 0.002
SIGMA = 2.0
CHANCE = 0.25
LEARNS = 0.10
FLAT = 0.05
CLAIMS = (
    ("VA1", "and the fourteenth revision is carried unchanged where it is not rewritten, and the absent list loses "
            "exactly one entry",
     "Every field of e470's card except the revision, the new clause and absent is equal to the revision-14 card, with "
     "the revision now 15, and absent is revision 14's with a policy removed and nothing else added or removed",
     "falsifier: any other field differing, the revision not 15, or an absent list that differs by anything but that "
     "one entry; refused when e470's artifact is absent"),
    ("VA2", f"and the clause's numbers come out of the runs, to {TOL:.3f}",
     "Every number the clause carries equals the two runs recomputed, and equals e481's reading of them on disk, to a "
     "thousandth of a point",
     "falsifier: any number disagreeing past the tolerance, or an arm or a replicate count differing; refused when a "
     "run or the reading is absent"),
    ("VA3", f"and the clause's bearing is that the freedom is used and the game is still learned, at {LEARNS:.2f}",
     "The policy's distance from the identity is above zero on every replicate of the new run, and the naive arm's "
     "diagonal on it is at least 0.10 above the four-class chance of 0.25",
     f"falsifier: a replicate whose movement is zero or unrecorded, or a diagonal within {FLAT:.2f} of chance"),
    ("VA4", f"and the clause carries what resolved rather than only what did not, at {SIGMA:.0f} sigma",
     "The clause records the contrasts at or past two sigma exactly as e481's reading reports them",
     "falsifier: the clause's resolved list differing from the reading's, or a resolved contrast the clause does not "
     "record"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def reading(card14: Path = CARD14, reading_path: Path = READING) -> dict:
    out = {"ok": True, "reason": None, "card": None, "revision14": {}, "absent14": [], "policy": {},
           "rolls": {}, "reading": {}}
    base = load(card14)
    if not base:
        return {**out, "ok": False, "reason": f"{card14} is absent, so revision 14 is not on disk"}
    old = base.get("card") or {}
    doc = load(reading_path)
    if not doc or not doc.get("ok"):
        return {**out, "ok": False, "reason": f"{reading_path} is absent or was refused"}
    out["reading"] = doc
    #: **recomputed from the two runs**, not copied from the reading: `e481.reading` is this corpus's own reader of
    #: exactly those two artifacts, and running it again here is what makes VA2 a check rather than a transcription
    fresh = e481.reading(new=NEW_RUN, base=BASE_RUN)
    if not fresh.get("ok"):
        return {**out, "ok": False, "reason": f"the two runs cannot be read: {fresh.get('reason')}"}
    out["rolls"] = fresh
    s = fresh["spans"]
    moves = [m for a in ARMS for m in fresh["moves"][a]]
    resolved = sorted(f"{a}/{q}" for a in ARMS
                      for q, tbl in (("diagonal", fresh["diagonal"]), ("last_row", fresh["last_row"]))
                      if abs(tbl[a]["contrast"]["sigma"]) >= SIGMA)
    clause = {
        "artifact": [READING.name, NEW_RUN.name, BASE_RUN.name],
        "flag": "--loop-policy",
        "initialization": "the identity, which is the environment's own action rule, checked bit for bit by e477",
        "trained_by": "the task loss through the loop, in the same optimizer as the body and the head",
        "covered_by_a_penalty": False,
        "arms": list(ARMS),
        "replicates": sorted({v[0] for v in s["replicates"].values()}),
        "moves": {"recorded": s["moves_recorded"], "total": s["moves_total"], "min": s["move_min"],
                  "mean": s["move_mean"]},
        "chance": CHANCE,
        "diagonal": {a: {"policy": statistics.fmean(fresh["diagonal"][a]["policy"]),
                         "against": statistics.fmean(fresh["diagonal"][a]["card"]),
                         "contrast": fresh["diagonal"][a]["contrast"]["mean"],
                         "sigma": fresh["diagonal"][a]["contrast"]["sigma"]} for a in ARMS},
        "last_row": {a: {"policy": statistics.fmean(fresh["last_row"][a]["policy"]),
                         "against": statistics.fmean(fresh["last_row"][a]["card"]),
                         "contrast": fresh["last_row"][a]["contrast"]["mean"],
                         "sigma": fresh["last_row"][a]["contrast"]["sigma"]} for a in ARMS},
        "resolved": resolved,
    }
    card = copy.deepcopy(old)
    card["revision"] = REVISION
    card["absent"] = [a for a in (old.get("absent") or []) if a != HELD]
    card["policy"] = clause
    out["revision14"] = {k: v for k, v in old.items() if k not in NEW}
    out["absent14"] = list(old.get("absent") or [])
    out["policy"] = clause
    out["card"] = card
    return out


def _close(a, b) -> bool:
    return a is not None and b is not None and abs(float(a) - float(b)) <= TOL / 2


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the clause is read from is absent"}
                for c in CLAIMS]
    card, c = r["card"], r["policy"]
    same = {k: (card.get(k) == v) for k, v in r["revision14"].items()}
    differ = sorted(k for k, v in same.items() if not v)
    old_absent, new_absent = r["absent14"], card.get("absent") or []
    lost = sorted(set(old_absent) - set(new_absent))
    gained = sorted(set(new_absent) - set(old_absent))
    j1 = {"id": "VA1",
          "measured": f"the revision-14 card's {len(same)} fields against the revision-15 card: "
                      f"{len(same) - len(differ)} equal, with the revision now {card.get('revision')}, and the absent "
                      f"list going from {old_absent} to {new_absent}",
          "verdict": "MET -- revision 14 is carried where it is not rewritten, and the absent list loses exactly the "
                     "policy" if (not differ and card.get("revision") == REVISION and lost == [HELD] and not gained)
                     else f"FALSIFIER FIRED -- differing {differ}, revision {card.get('revision')}, lost {lost}, "
                          f"gained {gained}"}
    fresh = r["rolls"]
    stored = r["reading"]
    off = []
    for a in ARMS:
        for q, key in (("diagonal", "diagonal"), ("last_row", "last_row")):
            got = c[key][a]
            if not (_close(got["contrast"], fresh[key][a]["contrast"]["mean"]) and
                    _close(got["sigma"], fresh[key][a]["contrast"]["sigma"]) and
                    _close(got["policy"], statistics.fmean(fresh[key][a]["policy"])) and
                    _close(got["contrast"], stored[key][a]["contrast"]["mean"])):
                off.append(f"{a}.{q}")
    counts_ok = (c["arms"] == list(ARMS) and c["replicates"] == [int(stored["spans"]["replicates"]["card"][0])]
                 and c["moves"]["recorded"] == stored["spans"]["moves_recorded"]
                 and c["moves"]["total"] == stored["spans"]["moves_total"])
    j2 = {"id": "VA2",
          "measured": f"the clause carries {len(c['diagonal']) + len(c['last_row'])} contrasts over "
                      f"{c['replicates']} replicates with {len(off)} disagreeing past the tolerance, its movement "
                      f"counts {c['moves']['recorded']} of {c['moves']['total']} against the reading's "
                      f"{stored['spans']['moves_recorded']} of {stored['spans']['moves_total']}, and its arms "
                      f"{c['arms']}",
          "verdict": "MET -- every number in the clause is the two runs recomputed and the reading's" if
                     (not off and counts_ok) else
                     f"FALSIFIER FIRED -- disagreeing {off[:6]}, counts ok {counts_ok}"}
    moves = [m for a in ARMS for m in fresh["moves"][a]]
    got = [m for m in moves if m is not None]
    zeroed = sum(1 for m in moves if m is None or m <= 0.0)
    spread = (f"{min(got):.4f} to {max(got):.4f} with a mean of {statistics.fmean(got):.4f}" if got
              else "not recorded at all")
    learn = statistics.fmean(fresh["diagonal"]["naive"]["policy"]) - CHANCE
    j3 = {"id": "VA3",
          "measured": f"the policy's distance from the identity runs {spread} over {len(moves)} replicates, {zeroed} "
                      f"of them at or below zero or unrecorded, and the naive arm's diagonal is "
                      f"{statistics.fmean(fresh['diagonal']['naive']['policy']):.4f}"
                      f", {learn:+.4f} above a chance of {CHANCE:.2f}",
          "verdict": f"MET -- the freedom is used on every replicate and the game is learned {learn:+.4f} above chance"
                     if (zeroed == 0 and learn >= LEARNS) else
                     f"FALSIFIER FIRED -- {zeroed} replicates at or below zero, the diagonal {learn:+.4f} above chance"
                     if (zeroed > 0 or learn <= FLAT) else
                     f"NULL -- the diagonal is {learn:+.4f} above chance, between {FLAT:.2f} and {LEARNS:.2f}"}
    got_resolved = sorted(c["resolved"])
    want = sorted(f"{a}/{q}" for a in ARMS
                  for q, tbl in (("diagonal", stored["diagonal"]), ("last_row", stored["last_row"]))
                  if abs(tbl[a]["contrast"]["sigma"]) >= SIGMA)
    j4 = {"id": "VA4",
          "measured": f"the clause resolves {got_resolved} and the reading resolves {want}, out of "
                      f"{2 * len(ARMS)} contrasts over the three arms and the two quantities",
          "verdict": "MET -- the clause carries the contrast that fired beside the nulls" if got_resolved == want else
                     f"FALSIFIER FIRED -- the clause carries {got_resolved} and the reading {want}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the game card's fifteenth revision: the policy ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact the clause is read from is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    card, c = r["card"], r["policy"]
    print(f"   the card is now revision {card['revision']} and its absent list is {card['absent']}")
    print(f"   the new clause is `policy`, read from {c['artifact']}")
    print(f"\n   the policy's distance from the identity: {c['moves']['recorded']} of {c['moves']['total']} recorded, "
          f"the smallest {c['moves']['min']:.4f} and the mean {c['moves']['mean']:.4f}")
    print(f"\n   {'arm':<10} {'diagonal':>9} {'against':>9} {'contrast':>10} {'sigma':>7} "
          f"{'last row':>9} {'against':>9} {'contrast':>10} {'sigma':>7}")
    for a in ARMS:
        d, l = c["diagonal"][a], c["last_row"][a]
        print(f"   {a:<10} {d['policy']:>9.4f} {d['against']:>9.4f} {d['contrast']:>+10.4f} {d['sigma']:>7.2f} "
              f"{l['policy']:>9.4f} {l['against']:>9.4f} {l['contrast']:>+10.4f} {l['sigma']:>7.2f}")
    print(f"\n   the clause resolves {c['resolved']} out of {2 * len(ARMS)} contrasts")
    print("\n== the registered claims, VA1-VA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e470` removed a held-out task from the list when the corpus first had one;")
    print("    this unit removes a policy, and leaves the reward and the episode boundary where they are)")
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
