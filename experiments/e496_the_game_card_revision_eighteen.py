"""E496 -- the game card's eighteenth revision: the label's placement, and the episode clause it explains.

`e490` wrote revision 17 with an `episode` clause read off `e489`'s runs -- the pass at three trials, the world
carrying it, the boundary channel drawn -- **and every arm at the four-class chance**, which its own fourth claim had
fired on. `e495` then moved the cue the label names from the episode's **last** trial to its **first** and the same
pass read **0.8299**, **0.8139** and **0.8267**. **So the card's chance reading is the label-last placement's and
not the episode's**, and this unit writes that down: one clause added, the **label-first pass**, carrying `e495`'s
measurements recomputed rather than quoted, with the `episode` clause and everything else of `e490`'s card checked
equal rather than rewritten.

Four claims, registered before this unit's pass over the runs and the reading.

- **NA1 -- and the seventeenth revision is carried unchanged, and nothing is removed.** Every field of `e490`'s card
  except the revision and the new clause is equal to the revision-17 card, with the revision now **18**, and the
  `absent` list is revision 17's **unchanged and still empty**. **Falsifier**: any other field differing, the revision
  not 18, or an absent list that differs; refused when `e490`'s artifact is absent.
- **NA2 -- and the clause's numbers come out of the runs and the measurement.** Every number the clause carries --
  each arm's label-first and label-last diagonals with their paired contrast and sigma, the replicate count, the two
  shares and the two windows -- equals `e495`'s reading recomputed **and** equals what that reading wrote to disk, to
  a thousandth of a point. **Falsifier**: any number disagreeing past the tolerance, or an arm, a replicate count or a
  window differing; refused when a run or the reading is absent.
- **NA3 -- and the clause's bearing is that the placement is what the episode's chance reading was paying.** The
  clause carries the label-first arms **above the four-class chance by the bar `e495` registered** with their paired
  contrasts **resolved at two sigma**, beside the label-last arms at the chance. **Falsifier**: an arm whose
  label-first diagonal is under chance plus the bar, or one whose contrast does not resolve.
- **NA4 -- and the clause carries the cost as well as the capability.** The clause records that the label-last
  placement's arms are **within the chance band** `e495` registers and that the shares order the placements, so a
  reader meets the episode's chance reading and its explanation in one clause. **Falsifier**: a label-last arm outside
  the band, or two shares that do not order the placements.

**What it can do beyond that.** It closes the loop `e489`, `e490` and `e495` opened: the card's `episode` clause says
what the pass is and `label_first` says where its label has to be for the pass to be learned, so the game's episodic
mode is written down as a **configuration that works** rather than as a capability the benchmark carries and cannot
use. It is the first revision this card has written in which the clause added is a **correction** of a reading an
earlier clause carries.

**What it cannot do.** *One revision of one world*: the clause is read from one pair of runs at one budget, one
episode length and one seed stream. *And a clause is not a result*: NA1 shows revision 17 survives into revision 18
and not that revision 17 was right. *And the correction is partial*: the `episode` clause's own numbers stand as the
label-last reading they are, and what a three-cue pass, a longer pass or a payout does with the placement is a
different unit. *And an empty `absent` list is still not completeness*: the list has named nothing since `e490` and a
card ages.
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

#: the card this revision is written from, its reading, and the two runs the clause is read off
CARD17 = Path("runs/e490_the_game_card_revision_seventeen.json")
READING = Path("runs/e495_the_label_first.json")
FIRST = e495.FIRST
LAST = e495.LAST
ARMS = e495.ARMS
REVISION = 18
NEW = ("revision", "label_first")
TOL = 0.002
SIGMA = 2.0
BAR = e495.BAR
CHANCE = e495.CHANCE
CLAIMS = (
    ("NA1", "and the seventeenth revision is carried unchanged, and nothing is removed",
     "Every field of e490's card except the revision and the new clause is equal to the revision-17 card, with the "
     "revision now 18, and the absent list is revision 17's unchanged and still empty",
     "falsifier: any other field differing, the revision not 18, or an absent list that differs; refused when e490's "
     "artifact is absent"),
    ("NA2", f"and the clause's numbers come out of the runs and the measurement, to {TOL:.3f}",
     "Every number the clause carries equals e495's reading recomputed and equals what that reading wrote to disk, to "
     "a thousandth of a point",
     "falsifier: any number disagreeing past the tolerance, or an arm, a replicate count or a window differing; "
     "refused when a run or the reading is absent"),
    ("NA3", f"and the clause's bearing is that the placement is what the chance reading paid, at {SIGMA:.0f} sigma",
     "The clause carries the label-first arms above the four-class chance by the bar e495 registered, with their "
     "paired contrasts resolved at two sigma, beside the label-last arms at the chance",
     "falsifier: an arm whose label-first diagonal is under chance plus the bar, or one whose contrast does not "
     "resolve"),
    ("NA4", "and the clause carries the cost as well as the capability",
     "The clause records that the label-last arms are within the chance band and that the shares order the placements",
     "falsifier: a label-last arm outside the band, or two shares that do not order the placements"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _windows() -> dict | None:
    """The two windows, from the environment's own arithmetic rather than from a sentence: the drive steps after the
    label's cue, at two trials of six, with the label first and with it last."""
    try:
        import numpy as np

        from clfly.connectome import annotate, circuits, graph
        from clfly.network import env as fly_env

        conn, ann = graph.build(), annotate.load_annotations()
        circ = circuits.extract(conn, ann, hops=0, max_neurons=e495.SIZE)
        rs = np.sort(np.random.default_rng(0).choice(circ.n_neurons, size=e495.READOUT_SIZE, replace=False))
        common = dict(readout_subset=rs, seed=0, n_symbols=e495.N_SYMBOLS, tau=e495.TAU, scale=1.0, gain=1.0,
                      noise=1.0, world_modes=0, world_leak=0.35, world_dims=8, world_coupled=True, cue_at=0,
                      boundary=True, episode=e495.EPISODE)
        out = {}
        for name, first in (("label_last", False), ("label_first", True)):
            env = fly_env.build(circ, **{**common, "label_first": first})
            cue_at = env.cue_at if first else env.last_cue_step
            out[name] = int(env.tau - 1 - cue_at)
        return out
    except (ImportError, OSError, ValueError):
        return None


def reading(card17: Path = CARD17, reading_path: Path = READING) -> dict:
    out = {"ok": True, "reason": None, "card": None, "revision17": {}, "absent17": [], "label_first": {},
           "rolls": {}, "reading": {}, "windows": {}}
    base = load(card17)
    if not base:
        return {**out, "ok": False, "reason": f"{card17} is absent, so revision 17 is not on disk"}
    old = base.get("card") or {}
    doc = load(reading_path)
    if not doc or not doc.get("ok"):
        return {**out, "ok": False, "reason": f"{reading_path} is absent or was refused"}
    out["reading"] = doc
    #: **recomputed from the two runs**, not copied from the reading
    fresh = e495.reading(first=FIRST, last=LAST)
    if not fresh.get("ok"):
        return {**out, "ok": False, "reason": f"the two runs cannot be read: {fresh.get('reason')}"}
    out["rolls"] = fresh
    windows = _windows()
    if windows is None:
        return {**out, "ok": False, "reason": "the connectome could not be built, so the two windows are not measured"}
    out["windows"] = windows
    shares = {name: fresh["share"][name]["share"] for name in ("last", "first")}
    clause = {
        "artifact": [READING.name, FIRST.name, LAST.name],
        "flag": "--loop-label-first",
        "placement": "the cue the task's label names at the episode's first trial and the episode's other symbols "
                     "after it, so the label's window is the whole pass",
        "window": {"label_last": windows["label_last"], "label_first": windows["label_first"]},
        "shares": {name: shares[name] for name in ("last", "first")},
        "arms": list(ARMS),
        "replicates": sorted({v["replicates"] for roll in fresh["runs"].values()
                              for v in roll["arms"].values()}),
        "chance": CHANCE,
        "accuracy": {a: {"first": fresh["spans"]["accuracy_diagonal"]["first"][a],
                         "last": fresh["spans"]["accuracy_diagonal"]["last"][a],
                         "contrast": fresh["recovery"][a]["mean"],
                         "sigma": fresh["recovery"][a]["sigma"]} for a in ARMS},
        "bar": BAR,
        "explains": "the `episode` clause's reading -- every arm short of the bar on the label-last placement -- is "
                    "this clause's starting point, and what the placement costs is measured here",
    }
    card = copy.deepcopy(old)
    card["revision"] = REVISION
    card["label_first"] = clause
    out["revision17"] = {k: v for k, v in old.items() if k not in NEW}
    out["absent17"] = list(old.get("absent") or [])
    out["label_first"] = clause
    out["card"] = card
    return out


def _close(a, b) -> bool:
    return a is not None and b is not None and abs(float(a) - float(b)) <= TOL / 2


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the clause is read from is absent"}
                for c in CLAIMS]
    card, c = r["card"], r["label_first"]
    same = {k: (card.get(k) == v) for k, v in r["revision17"].items()}
    differ = sorted(k for k, v in same.items() if not v)
    absent = card.get("absent") or []
    j1 = {"id": "NA1",
          "measured": f"the revision-17 card's {len(same)} fields against the revision-18 card: "
                      f"{len(same) - len(differ)} equal, with the revision now {card.get('revision')} and the absent "
                      f"list **{absent}**",
          "verdict": "MET -- revision 17 is carried unchanged and the absent list is untouched" if
                     (not differ and card.get("revision") == REVISION and absent == r["absent17"] and not absent)
                     else f"FALSIFIER FIRED -- differing {differ}, revision {card.get('revision')}, absent {absent}"}
    fresh, stored = r["rolls"], r["reading"]
    off = []
    for a in ARMS:
        got = c["accuracy"][a]
        checks = [_close(got["first"], fresh["spans"]["accuracy_diagonal"]["first"][a]),
                  _close(got["last"], fresh["spans"]["accuracy_diagonal"]["last"][a]),
                  _close(got["first"], stored["spans"]["accuracy_diagonal"]["first"][a]),
                  _close(got["last"], stored["spans"]["accuracy_diagonal"]["last"][a]),
                  _close(got["contrast"], stored["recovery"][a]["mean"]),
                  _close(got["sigma"], stored["recovery"][a]["sigma"])]
        if not all(checks):
            off.append(a)
    numbers_ok = all([
        _close(c["shares"]["last"], stored["share"]["last"]["share"]),
        _close(c["shares"]["first"], stored["share"]["first"]["share"]),
        _close(c["shares"]["last"], fresh["share"]["last"]["share"]),
        _close(c["shares"]["first"], fresh["share"]["first"]["share"]),
        c["window"] == {k: v for k, v in r["windows"].items()},
        c["arms"] == list(ARMS),
        c["replicates"] == [int(stored["spans"]["replicates"][0])],
        _close(c["bar"], BAR) and _close(c["chance"], CHANCE),
    ])
    j2 = {"id": "NA2",
          "measured": f"the clause carries {len(c['accuracy'])} arms' two diagonals with their paired contrasts and "
                      f"sigmas at {c['replicates']} replicates with **{len(off)}** disagreeing past the tolerance, the "
                      f"shares { {k: round(v, 4) for k, v in c['shares'].items()} } and the windows {c['window']}",
          "verdict": "MET -- every number in the clause is the runs and the measurement recomputed and the "
                     "reading's" if (not off and numbers_ok) else
                     f"FALSIFIER FIRED -- disagreeing {off}, numbers ok {numbers_ok}"}
    up = [a for a in ARMS if c["accuracy"][a]["first"] >= CHANCE + BAR
          and c["accuracy"][a]["sigma"] >= SIGMA]
    j3 = {"id": "NA3",
          "measured": f"the label-first diagonals are "
                      f"{ {a: round(c['accuracy'][a]['first'], 4) for a in ARMS} } against a chance of {CHANCE:.2f} and "
                      f"a bar of {BAR:.2f} above it, with the contrasts "
                      f"{ {a: round(c['accuracy'][a]['sigma'], 2) for a in ARMS} } sigma, and the label-last "
                      f"diagonals { {a: round(c['accuracy'][a]['last'], 4) for a in ARMS} }",
          "verdict": f"MET -- the placement is what the chance reading paid, on **{len(up)}** of three arms ({up})" if
                     len(up) == len(ARMS) else
                     f"FALSIFIER FIRED -- {len(up)} of {len(ARMS)} arms over the bar and two sigma ({up})"}
    band = [a for a in ARMS if abs(c["accuracy"][a]["last"] - CHANCE) <= 0.05]
    ordered = c["shares"]["first"] > c["shares"]["last"]
    j4 = {"id": "NA4",
          "measured": f"the label-last diagonals are "
                      f"{ {a: round(c['accuracy'][a]['last'], 4) for a in ARMS} } against a chance of {CHANCE:.2f}, "
                      f"with {len(band)} of three arms inside the band, and the shares are "
                      f"{ {k: round(v, 4) for k, v in c['shares'].items()} }",
          "verdict": "MET -- the clause carries the cost beside the capability and the shares order the placements" if
                     (len(band) == len(ARMS) and ordered) else
                     f"FALSIFIER FIRED -- inside the band {band}, shares ordered {ordered}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the game card's eighteenth revision: the label's placement ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact the clause is read from is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    card, c = r["card"], r["label_first"]
    print(f"   the card is now revision {card['revision']} and its absent list is {card['absent']}")
    print(f"   the new clause is `label_first`, read from {c['artifact']}")
    print(f"\n   {'arm':<10} {'label first':>11} {'label last':>11} {'contrast':>10} {'sigma':>7}")
    for a in ARMS:
        g = c["accuracy"][a]
        print(f"   {a:<10} {g['first']:>11.4f} {g['last']:>11.4f} {g['contrast']:>+10.4f} {g['sigma']:>7.2f}")
    print(f"\n   the windows: {c['window']} drive steps after the label's cue; the shares: "
          f"{ {k: round(v, 4) for k, v in c['shares'].items()} }")
    print("\n== the registered claims, NA1-NA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e490` recorded the episode and every arm at chance; this records where its label has to be)")
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
