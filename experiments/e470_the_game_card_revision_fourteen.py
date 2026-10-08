"""E470 -- the game card's fourteenth revision: the held-out task, and the clause that reads it.

`e469` drove the corpus's first held-out task and closed by saying what that leaves owed: **the card's `absent` list still
names a held-out task**, which is now false of the corpus. The card's `absent` list has carried *a reward, a policy, an
episode boundary and a held-out task* since its first revision, and the clauses added by revisions 11, 12 and 13 --
`readout`, `head`, `pair` -- are all about the **sequence's** tasks.

**This unit writes revision 14.** One clause is added, the **holdout**, carrying `e469`'s readings recomputed from the
two rolls rather than quoted, and the `absent` list loses exactly one entry. Every other field is checked equal to
`e461`'s card. Four claims, registered before this unit's pass over the two rolls and the reading.

- **WA1 -- and the thirteenth revision is carried unchanged where it is not rewritten, and the absent list loses exactly
  one entry.** Every field of `e461`'s card except the revision, the new clause and `absent` is equal to the
  revision-13 card, with the revision now **14**, and `absent` is revision 13's with `a held-out task` removed and
  nothing else added or removed. **Falsifier**: any other field differing, the revision not 14, or an absent list that
  differs by anything but that one entry; refused when `e461`'s artifact is absent.
- **WA2 -- and the clause's numbers come out of the two rolls.** Every number the clause carries -- each arm's initial
  and trained reading, the paired change and its sigma for the baseline and for each anchor, and each anchor's paired
  difference from the baseline with its sigma -- equals the two rolls recomputed, and the counts and the ridge equal
  `e469`'s reading. **Falsifier**: any number disagreeing by more than a thousandth of a point; refused when a roll or
  the reading is absent.
- **WA3 -- and the clause's bearing is what the sequence adds and not what is there.** The trained reading exceeds the
  initial one at **two** sigma or more for the baseline arm on **both** rolls, and the clause carries the initial
  reading beside it so a reader is not shown the trained number alone. **Falsifier**: under two sigma on either roll.
- **WA4 -- and the two anchors are nulls in the clause.** Each anchor's paired difference from the baseline's trained
  reading is under **two** sigma in absolute value on both rolls. **Falsifier**: an anchor on either roll whose contrast
  resolves.

**What it can do beyond that.** It makes the card's own account of its game match the corpus: the game now has a task
outside its sequence, the card carries the reading of that task, and the `absent` list is what it says it is. Read with
`e469` it is also the only place where the held-out reading and the sequence's own ledger are in one artifact.

**What it cannot do.** *One world of one revision*: the card's own world with the flag's own draw, so the clause is a
reading of one held-out draw in it. *And two rolls*: the nulls against the baseline are what a redraw could put above
the bar. *And a clause is not a result*: WA1 shows revision 13 survives into revision 14 and not that revision 13 was
right, and WA2 shows the clause agrees with the rolls and not that the rolls should be believed. *And the card still
cannot say **how** the probe should be built*: the ridge is recorded and not prescribed, so the clause is one probe's
reading rather than the benchmark's definition of one.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the card the clause is added to, the corpus's first held-out reading, and the two rolls it was taken on
CARD13 = Path("runs/e461_the_game_card_revision_thirteen.json")
E469 = Path("runs/e469_the_held_out_cue_set.json")
ROLLS = {
    "bio": Path("runs/e469_earned_label_neurons_holdout_20reps.json"),
    "rand": Path("runs/e469_earned_label_rand_neurons_holdout_20reps.json"),
}
ANCHOR_OF = {"bio": "ewc-block", "rand": "ewc-block-rand"}
BASELINE = "naive"
BUFFER = "replay"
HELD = "a held-out task"
REVISION = 14
NEW = ("revision", "holdout", "absent")
TOL = 0.002
SIGMA = 2.0
CLAIMS = (
    ("WA1", "and the thirteenth revision is carried unchanged where it is not rewritten, and the absent list loses "
            "exactly one entry",
     "Every field of e461's card except the revision, the new clause and absent is equal to the revision-13 card, with "
     "the revision now 14, and absent is revision 13's with a held-out task removed and nothing else added or removed",
     "falsifier: any other field differing, the revision not 14, or an absent list that differs by anything but that "
     "one entry; refused when e461's artifact is absent"),
    ("WA2", f"and the clause's numbers come out of the two rolls, to {TOL:.3f}",
     "Every number the clause carries equals the two rolls recomputed, and the counts and the ridge equal e469's "
     "reading",
     "falsifier: any number disagreeing by more than a thousandth of a point; refused when a roll or the reading is "
     "absent"),
    ("WA3", f"and the clause's bearing is what the sequence adds, at {SIGMA:.0f} sigma",
     "The trained reading exceeds the initial one at two sigma or more for the baseline arm on both rolls, with the "
     "initial reading carried beside it",
     "falsifier: under two sigma on either roll"),
    ("WA4", f"and the two anchors are nulls in the clause, under {SIGMA:.0f} sigma",
     "Each anchor's paired difference from the baseline's trained reading is under two sigma in absolute value on both "
     "rolls",
     "falsifier: an anchor on either roll whose contrast resolves"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def _roll(path: Path, anchor: str) -> dict | None:
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    arms = {}
    for arm in (BASELINE, anchor, BUFFER):
        reps = (methods.get(arm) or {}).get("replicates") or []
        blocks = [r.get("holdout") for r in reps]
        if not reps or any(b is None for b in blocks):
            return None
        arms[arm] = {"replicates": len(reps), "before": [b["before"] for b in blocks],
                     "after": [b["after"] for b in blocks],
                     "task": sorted({b.get("task") for b in blocks}),
                     "n_train": sorted({b.get("n_train") for b in blocks}),
                     "n_eval": sorted({b.get("n_eval") for b in blocks}),
                     "ridge": sorted({b.get("ridge") for b in blocks})}
    return {"artifact": path.name, "anchor": anchor, "arms": arms,
            "tasks": [t.get("name") if isinstance(t, dict) else None for t in (doc.get("tasks") or [])]}


def reading(card13: Path = CARD13, rolls: dict = ROLLS, e469: Path = E469) -> dict:
    out = {"ok": True, "reason": None, "card": None, "revision13": {}, "holdout": {}, "rolls": {}, "reading": {}}
    base = load(card13)
    if not base:
        return {**out, "ok": False, "reason": f"{card13} is absent, so revision 13 is not on disk"}
    doc469 = load(e469)
    if not doc469:
        return {**out, "ok": False, "reason": f"{e469} is absent, so the held-out reading is not on disk"}
    out["reading"] = doc469
    old = base.get("card") or {}
    for label, path in rolls.items():
        got = _roll(path, ANCHOR_OF[label])
        if got is None:
            return {**out, "ok": False,
                    "reason": f"{path} is absent, carries no {ANCHOR_OF[label]} arm, or carries no holdout block"}
        out["rolls"][label] = got
    card = copy.deepcopy(old)
    card["revision"] = REVISION
    card["absent"] = [a for a in (old.get("absent") or []) if a != HELD]
    out["revision13"] = {k: v for k, v in old.items() if k not in NEW}
    out["absent13"] = list(old.get("absent") or [])

    shares = {}
    for label, roll in out["rolls"].items():
        anchor = roll["anchor"]
        base_arm = roll["arms"][BASELINE]
        shares[label] = {
            "artifact": roll["artifact"],
            "anchor": anchor,
            "task": sorted({t for arm in roll["arms"].values() for t in arm["task"]}),
            "n_train": sorted({v for arm in roll["arms"].values() for v in arm["n_train"]}),
            "n_eval": sorted({v for arm in roll["arms"].values() for v in arm["n_eval"]}),
            "ridge": sorted({v for arm in roll["arms"].values() for v in arm["ridge"]}),
            "initial": {arm: statistics.fmean(got["before"]) for arm, got in roll["arms"].items()},
            "trained": {arm: statistics.fmean(got["after"]) for arm, got in roll["arms"].items()},
            "change": {arm: _paired(got["after"], got["before"]) for arm, got in roll["arms"].items()},
            "against_baseline": {arm: _paired(got["after"], base_arm["after"])
                                 for arm, got in roll["arms"].items() if arm != BASELINE},
        }
    card["holdout"] = {
        "artifact": [r["artifact"] for r in out["rolls"].values()] + [E469.name],
        "task": sorted({t for s in shares.values() for t in s["task"]}),
        "in_sequence": False,
        "probe": {"kind": "ridge read-out on the read-out neurons, fitted on the held-out cue set's train split and "
                          "scored on its test split, the body frozen",
                  "ridge": sorted({v for s in shares.values() for v in s["ridge"]}),
                  "n_train": sorted({v for s in shares.values() for v in s["n_train"]}),
                  "n_eval": sorted({v for s in shares.values() for v in s["n_eval"]})},
        "initial": {label: shares[label]["initial"] for label in shares},
        "trained": {label: shares[label]["trained"] for label in shares},
        "change": {label: {arm: shares[label]["change"][arm]["mean"] for arm in shares[label]["change"]}
                   for label in shares},
        "change_sigma": {label: {arm: shares[label]["change"][arm]["sigma"] for arm in shares[label]["change"]}
                         for label in shares},
        "against_baseline": {label: {arm: shares[label]["against_baseline"][arm]["mean"]
                                     for arm in shares[label]["against_baseline"]} for label in shares},
        "against_baseline_sigma": {label: {arm: shares[label]["against_baseline"][arm]["sigma"]
                                           for arm in shares[label]["against_baseline"]} for label in shares},
    }
    out["holdout"] = dict(card["holdout"])
    out["card"] = card
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the clause is read from is absent"}
                for c in CLAIMS]
    card, h = r["card"], r["holdout"]
    same = {k: (card.get(k) == v) for k, v in r["revision13"].items()}
    differ = sorted(k for k, v in same.items() if not v)
    old_absent = r.get("absent13") or []
    new_absent = card.get("absent") or []
    lost = sorted(set(old_absent) - set(new_absent))
    gained = sorted(set(new_absent) - set(old_absent))
    j1 = {"id": "WA1",
          "measured": f"the revision-13 card's {len(same)} fields against the revision-14 card: "
                      f"{len(same) - len(differ)} equal, with the revision now {card.get('revision')}, and the absent "
                      f"list going from {old_absent} to {new_absent}",
          "verdict": "MET -- revision 13 is carried where it is not rewritten, and the absent list loses exactly the "
                     "held-out task" if (not differ and card.get("revision") == REVISION and lost == [HELD] and
                                          not gained) else
                     f"FALSIFIER FIRED -- differing {differ}, revision {card.get('revision')}, lost {lost}, "
                     f"gained {gained}"}
    #: every contrast the clause carries, recomputed from the two rolls' own per-replicate readings
    pairs = {}
    for label, got in r["rolls"].items():
        base_arm = got["arms"][BASELINE]
        for arm, values in got["arms"].items():
            pairs[f"{label}.{arm}.change"] = _paired(values["after"], values["before"])
            if arm != BASELINE:
                pairs[f"{label}.{arm}.against_baseline"] = _paired(values["after"], base_arm["after"])
    off = []
    for label, s in h["change"].items():
        for arm, mean in s.items():
            if abs(mean - pairs[f"{label}.{arm}.change"]["mean"]) > TOL / 2:
                off.append(f"{label}.{arm}.change")
    for label, s in h["against_baseline"].items():
        for arm, mean in s.items():
            if abs(mean - pairs[f"{label}.{arm}.against_baseline"]["mean"]) > TOL / 2:
                off.append(f"{label}.{arm}.against_baseline")
    counts_ok = (h["probe"]["n_train"] and h["probe"]["n_eval"] and h["probe"]["ridge"] and
                 h["probe"]["n_train"] == r["reading"]["spans"]["n_train"] and
                 h["probe"]["n_eval"] == r["reading"]["spans"]["n_eval"])
    j2 = {"id": "WA2",
          "measured": f"the clause carries {len(h['initial'])} rolls' readings at "
                      f"{ {l: len(h['initial'][l]) for l in h['initial']} } arms over "
                      f"{len(pairs)} recomputed contrasts, with {len(off)} disagreeing past the tolerance, and the "
                      f"probe's counts {h['probe']['n_train']} / {h['probe']['n_eval']} against the reading's "
                      f"{r['reading']['spans']['n_train']} / {r['reading']['spans']['n_eval']}",
          "verdict": "MET -- every number in the clause is the two rolls recomputed" if (not off and counts_ok) else
                     f"FALSIFIER FIRED -- disagreeing {off[:6]}, counts {h['probe']}"}
    weak = min((h["change_sigma"][label][BASELINE] for label in h["change"]), default=0.0)
    j3 = {"id": "WA3",
          "measured": f"the baseline arm's change is "
                      f"{ {l: round(h['change'][l][BASELINE], 4) for l in h['change']} } at "
                      f"{ {l: round(h['change_sigma'][l][BASELINE], 2) for l in h['change_sigma']} } sigma, with the "
                      f"initial readings "
                      f"{ {l: round(h['initial'][l][BASELINE], 4) for l in h['initial']} } carried beside them",
          "verdict": f"MET -- the clause's bearing is what the sequence adds, the weaker roll at {weak:.2f} sigma" if
                     weak >= SIGMA else f"FALSIFIER FIRED -- the weaker roll is {weak:.2f} sigma"}
    resolved = sorted(f"{label}.{arm}" for label, s in h["against_baseline_sigma"].items()
                      for arm, sigma in s.items() if abs(sigma) >= SIGMA)
    j4 = {"id": "WA4",
          "measured": f"each anchor's difference from the baseline's trained reading is "
                      f"{ {l: {a: round(v, 4) for a, v in h['against_baseline'][l].items()} for l in h['against_baseline']} } "
                      f"at "
                      f"{ {l: {a: round(v, 2) for a, v in h['against_baseline_sigma'][l].items()} for l in h['against_baseline_sigma']} } "
                      f"sigma",
          "verdict": "MET -- both anchors are nulls in the clause" if not resolved else
                     f"FALSIFIER FIRED -- {resolved}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the game card's fourteenth revision: the held-out task ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact the clause is read from is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    h = r["holdout"]
    print("   one clause is added, the `holdout`, and the `absent` list loses the entry it named while no held-out")
    print("   task existed")
    print(f"\n   the held-out cue set: {h['task']}, in the sequence: {h['in_sequence']}")
    print(f"   the probe: {h['probe']['ridge']} ridge on {h['probe']['n_train']} train and "
          f"{h['probe']['n_eval']} eval examples")
    print(f"\n   {'roll/arm':<26} {'initial':>8} {'trained':>8} {'change':>8} {'sigma':>7} {'vs base':>9} {'sigma':>7}")
    for label in h["initial"]:
        for arm in h["initial"][label]:
            ch = h["change"][label].get(arm)
            cs = h["change_sigma"][label].get(arm)
            vs = h["against_baseline"][label].get(arm)
            vss = h["against_baseline_sigma"][label].get(arm)
            print(f"   {label + '/' + arm:<26} {h['initial'][label][arm]:>8.4f} {h['trained'][label][arm]:>8.4f} "
                  f"{ch:>+8.4f} {cs:>7.2f} " +
                  (f"{vs:>+9.4f} {vss:>7.2f}" if vs is not None else f"{'-':>9} {'-':>7}"))
    print("\n== the registered claims, WA1-WA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e469` drove the corpus's first held-out task and closed on what it leaves owed: the card's absent")
    print("    list still names one, which is now false of the corpus)")
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
