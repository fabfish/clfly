"""E490 -- the game card's seventeenth revision: the episode, and an absent list with nothing left in it.

`e489` gave the environment an **episode** -- a pass that holds `--loop-episode` trials, one cue each and the world's
state the episode's -- and the episode a **boundary** channel, and read both runs: the earlier trials move the
world's state at the read step by **0.7601** at **12.62** sigma where at one trial they move it by exactly zero, the
boundary carries `+1` at the opening and `-1` at every continuing trial and zero elsewhere, and every arm's accuracy
sits at the four-class chance, because the read step is the pass's last one and the label is a small part of what the
head reads.

**This unit writes revision 17.** One clause is added, the **episode**, carrying `e489`'s measurements recomputed
rather than quoted, and the `absent` list loses its **last** entry -- the list has carried **an episode boundary**
since the card's first revision, `e470` having removed the held-out task, `e482` the policy and `e486` the reward.
Four claims, registered before this unit's pass over the card and the runs.

- **UA1 -- and the sixteenth revision is carried unchanged where it is not rewritten, and the absent list is
  empty.** Every field of `e486`'s card except the revision, the new clause and `absent` is equal to the revision-16
  card, with the revision now **17**, and `absent` is revision 16's with **an episode boundary** removed and nothing
  else added or removed, so the list is **empty**. **Falsifier**: any other field differing, the revision not 17, or
  an absent list that differs by anything but that one entry or that is not empty; refused when `e486`'s artifact is
  absent.
- **UA2 -- and the clause's numbers come out of the runs and the measurement, to the tolerance.** Every number the
  clause carries -- each arm's boundary and plain diagonals with their paired contrast and sigma, the replicate count,
  the episode's trials and steps, the boundary's neurons and gain, and the carry's difference, sigma, episode count,
  scale and single-trial zero -- equals the runs and the measurement recomputed **and** equals `e489`'s reading and
  measurement on disk, to a thousandth of a point. **Falsifier**: any number disagreeing past the tolerance, or an
  arm, a replicate count or a trial count differing; refused when a run or the reading is absent.
- **UA3 -- and the clause's bearing is that the episode is carried and its opening marked.** The clause carries the
  carry's difference **above zero and resolved at two sigma** beside the single-trial value **exactly zero**, and the
  boundary's marks as `+gain` at the step the episode opens, `-gain` at every trial that continues it and **zero**
  elsewhere, out of the three populations and inside the task's input set. **Falsifier**: a reason of zero at the
  episode, one that does not resolve, a single-trial difference that is not zero, a mark that is not the declared
  sign or is non-zero where it should be zero, an overlap with the three populations, or a channel outside the input.
- **UA4 -- and the clause carries what the episode costs rather than only what it can do.** The clause records every
  arm's boundary and plain diagonals within **0.05** of the run's own four-class chance, and the boundary's paired
  contrast unresolved on every arm. **Falsifier**: an arm more than **0.05** from chance, or a contrast resolving at
  **two** sigma in either direction. *What `e489`'s fourth claim fired on is not a defect of the clause but the
  clause's content, and a card that carried the episode and not that would be reporting a capability the benchmark
  cannot use.*

**What it can do beyond that.** It closes the card: the game now has a substrate, a loop, a protocol, arms, metrics
and a stream, a world, a held-out task, a policy, a reward **and an episode**, and its `absent` list -- which has been
the card's own account of what is missing since `e392` -- is **empty**. Read with `e486` it is the third revision in
a row that removes a capability the environment gained one or two units earlier.

**What it cannot do.** *One revision of one world*: the clause is read from one pair of runs at one budget, one
episode length and one seed stream. *And a clause is not a result*: UA1 shows revision 16 survives into revision 17
and not that revision 16 was right. *And the clause carries a cost it cannot explain*: that the episode's task sits
at chance is `e489`'s measurement of the read step, and a clause is a record. *And an empty absent list is not
completeness*: it says the card names nothing absent, and a card ages -- `e392`'s own M5 measured its absences over
the corpus once and every one of them has since been closed by a unit.
"""

from __future__ import annotations

import argparse
import copy
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e489_the_benchmark_has_an_episode as e489

#: the card this revision is written from, its reading, and the two runs and the roll it is read against
CARD16 = Path("runs/e486_the_game_card_revision_sixteen.json")
READING = Path("runs/e489_the_benchmark_has_an_episode.json")
PLAIN = e489.PLAIN
BOUND = e489.BOUND
CARD = e489.CARD
ARMS = e489.ARMS
HELD = "an episode boundary"
REVISION = 17
NEW = ("revision", "episode", "absent")
TOL = 0.002
SIGMA = 2.0
#: how far above the run's own chance an arm may sit and still be "at chance" in the clause
BAND = 0.05
CLAIMS = (
    ("UA1", "and the sixteenth revision is carried unchanged where it is not rewritten, and the absent list is empty",
     "Every field of e486's card except the revision, the new clause and absent is equal to the revision-16 card, with "
     "the revision now 17, and absent is revision 16's with an episode boundary removed and nothing else added or "
     "removed, so the list is empty",
     "falsifier: any other field differing, the revision not 17, or an absent list that differs by anything but that "
     "one entry or that is not empty; refused when e486's artifact is absent"),
    ("UA2", f"and the clause's numbers come out of the runs and the measurement, to {TOL:.3f}",
     "Every number the clause carries equals the runs and the measurement recomputed and equals e489's reading and "
     "measurement on disk, to a thousandth of a point",
     "falsifier: any number disagreeing past the tolerance, or an arm, a replicate count or a trial count differing; "
     "refused when a run or the reading is absent"),
    ("UA3", f"and the clause's bearing is that the episode is carried and its opening marked, at {SIGMA:.0f} sigma",
     "The clause carries the carry's difference above zero and resolved at two sigma beside the single-trial value "
     "exactly zero, and the boundary's marks as +gain at the opening, -gain at every continuing trial and zero "
     "elsewhere, out of the three populations and inside the input set",
     "falsifier: a reason of zero at the episode, one that does not resolve, a single-trial difference that is not "
     "zero, a mark that is not the declared sign or is non-zero where it should be zero, an overlap with the three "
     "populations, or a channel outside the input"),
    ("UA4", f"and the clause carries what the episode costs, within {BAND:.2f} of chance",
     "The clause records every arm's boundary and plain diagonals within 0.05 of the run's own four-class chance, and "
     "the boundary's paired contrast unresolved on every arm",
     "falsifier: an arm more than 0.05 from chance, or a contrast resolving at two sigma in either direction"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _measure() -> dict | None:
    """`e489`'s two measurements run again: the episode the world carries, and the boundary channel."""
    try:
        from clfly.connectome import annotate, circuits, graph
        from clfly.network.model import RateConfig, build_net

        conn, ann = graph.build(), annotate.load_annotations()
        circ = circuits.extract(conn, ann, hops=0, max_neurons=e489.SIZE)
        net = build_net(circ, RateConfig(tau=e489.TAU)).torch_model()
        return {"endpoint": e489.endpoint(circ), "carry": e489.episode_states(circ, net),
                "boundary": e489.boundary_channel(circ)}
    except (ImportError, OSError, ValueError):
        return None


def reading(card16: Path = CARD16, reading_path: Path = READING) -> dict:
    out = {"ok": True, "reason": None, "card": None, "revision16": {}, "absent16": [], "episode": {},
           "rolls": {}, "reading": {}, "measure": {}}
    base = load(card16)
    if not base:
        return {**out, "ok": False, "reason": f"{card16} is absent, so revision 16 is not on disk"}
    old = base.get("card") or {}
    doc = load(reading_path)
    if not doc or not doc.get("ok"):
        return {**out, "ok": False, "reason": f"{reading_path} is absent or was refused"}
    out["reading"] = doc
    #: **recomputed from the two runs**, not copied from the reading: `e489.reading` is this corpus's own reader of
    #: exactly those two artifacts, and running it again here is what makes UA2 a check rather than a transcription
    fresh = e489.reading(bound=BOUND, plain=PLAIN)
    if not fresh.get("ok"):
        return {**out, "ok": False, "reason": f"the two runs cannot be read: {fresh.get('reason')}"}
    out["rolls"] = fresh
    #: and the episode and the channel measured again, which is the other half of the clause
    measured = _measure()
    if measured is None:
        return {**out, "ok": False, "reason": "the connectome could not be built, so the episode is not measured"}
    out["measure"] = measured
    run = {a: {"boundary": statistics.fmean(fresh["runs"]["bound"]["arms"][a]["accuracy_diagonal"]),
               "plain": statistics.fmean(fresh["runs"]["plain"]["arms"][a]["accuracy_diagonal"]),
               "last_boundary": statistics.fmean(fresh["runs"]["bound"]["arms"][a]["accuracy_last"]),
               "last_plain": statistics.fmean(fresh["runs"]["plain"]["arms"][a]["accuracy_last"]),
               "contrast": fresh["accuracy"][a]["mean"], "sigma": fresh["accuracy"][a]["sigma"]} for a in ARMS}
    carry, marks = measured["carry"], measured["boundary"]
    clause = {
        "artifact": [READING.name, PLAIN.name, BOUND.name, CARD.name],
        "flag": "--loop-episode",
        "trials": e489.EPISODE,
        "steps_per_trial": e489.TAU // e489.EPISODE,
        "state": "the episode's: the world carries the trials before the last one, so the read step sees the "
                 "episode and not the last trial",
        "carry": {"difference": carry["episode"]["pairing"]["mean"],
                  "sigma": carry["episode"]["pairing"]["sigma"],
                  "episodes": carry["episode"]["pairing"]["n"],
                  "scale": carry["episode"]["state_scale"],
                  "at_one_trial": carry["single"]["largest"]},
        "boundary_flag": "--loop-boundary",
        "boundary": {"neurons": marks["n_boundary"], "gain": marks["gain"], "marks": marks["marks"],
                     "disjoint": marks["overlap"] == 0, "in_input": bool(marks["in_input"]),
                     "at_the_endpoint": bool(marks["off_has_channel"])},
        "arms": list(ARMS),
        "replicates": sorted({v["replicates"] for roll in fresh["runs"].values()
                              for v in roll["arms"].values()}),
        "chance": e489.CHANCE,
        "accuracy": run,
        "read_step": "the pass's last, which is what the episode costs and what e489's fourth claim fired on",
    }
    card = copy.deepcopy(old)
    card["revision"] = REVISION
    card["absent"] = [a for a in (old.get("absent") or []) if a != HELD]
    card["episode"] = clause
    out["revision16"] = {k: v for k, v in old.items() if k not in NEW}
    out["absent16"] = list(old.get("absent") or [])
    out["episode"] = clause
    out["card"] = card
    return out


def _close(a, b) -> bool:
    return a is not None and b is not None and abs(float(a) - float(b)) <= TOL / 2


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the clause is read from is absent"}
                for c in CLAIMS]
    card, c = r["card"], r["episode"]
    same = {k: (card.get(k) == v) for k, v in r["revision16"].items()}
    differ = sorted(k for k, v in same.items() if not v)
    old_absent, new_absent = r["absent16"], card.get("absent") or []
    lost = sorted(set(old_absent) - set(new_absent))
    gained = sorted(set(new_absent) - set(old_absent))
    j1 = {"id": "UA1",
          "measured": f"the revision-16 card's {len(same)} fields against the revision-17 card: "
                      f"{len(same) - len(differ)} equal, with the revision now {card.get('revision')}, and the absent "
                      f"list going from {old_absent} to **{new_absent}**",
          "verdict": "MET -- revision 16 is carried where it is not rewritten, and the absent list is empty" if
                     (not differ and card.get("revision") == REVISION and lost == [HELD] and not gained
                      and new_absent == []) else
                     f"FALSIFIER FIRED -- differing {differ}, revision {card.get('revision')}, lost {lost}, "
                     f"gained {gained}, absent {new_absent}"}
    fresh, stored, meas = r["rolls"], r["reading"], r["measure"]
    off = []
    for a in ARMS:
        got = c["accuracy"][a]
        f_b = fresh["runs"]["bound"]["arms"][a]
        f_p = fresh["runs"]["plain"]["arms"][a]
        s = stored["accuracy"][a]
        checks = [_close(got["boundary"], statistics.fmean(f_b["accuracy_diagonal"])),
                  _close(got["plain"], statistics.fmean(f_p["accuracy_diagonal"])),
                  _close(got["contrast"], s["mean"]), _close(got["sigma"], s["sigma"]),
                  _close(got["boundary"], statistics.fmean(stored["runs"]["bound"]["arms"][a]["accuracy_diagonal"])),
                  _close(got["plain"], statistics.fmean(stored["runs"]["plain"]["arms"][a]["accuracy_diagonal"]))]
        if not all(checks):
            off.append(a)
    sc, ss = meas["carry"]["episode"], stored["carry"]["episode"]
    sb, st_b = meas["boundary"], stored["boundary"]
    numbers_ok = all([
        _close(c["carry"]["difference"], sc["pairing"]["mean"]), _close(c["carry"]["difference"], ss["pairing"]["mean"]),
        _close(c["carry"]["sigma"], sc["pairing"]["sigma"]), _close(c["carry"]["sigma"], ss["pairing"]["sigma"]),
        _close(c["carry"]["scale"], sc["state_scale"]), _close(c["carry"]["at_one_trial"], meas["carry"]["single"]["largest"]),
        _close(c["boundary"]["neurons"], sb["n_boundary"]), _close(c["boundary"]["gain"], sb["gain"]),
        c["boundary"]["marks"] == [round(x, 6) for x in st_b["marks"]],
        c["trials"] == e489.EPISODE and c["steps_per_trial"] == e489.TAU // e489.EPISODE,
        c["arms"] == list(ARMS), c["replicates"] == [int(stored["spans"]["replicates"][0])],
        _close(c["chance"], e489.CHANCE),
    ])
    j2 = {"id": "UA2",
          "measured": f"the clause carries {len(c['accuracy'])} arms' boundary and plain diagonals with their paired "
                      f"contrasts and sigmas at {c['replicates']} replicates with **{len(off)}** disagreeing past the "
                      f"tolerance, the carry { {k: round(v, 4) if isinstance(v, float) else v for k, v in c['carry'].items()} } "
                      f"and the boundary at {c['boundary']['neurons']} neurons and gain {c['boundary']['gain']}, "
                      f"{c['trials']} trials of {c['steps_per_trial']} steps",
          "verdict": "MET -- every number in the clause is the runs and the measurement recomputed and the "
                     "reading's" if (not off and numbers_ok) else
                     f"FALSIFIER FIRED -- disagreeing {off}, numbers ok {numbers_ok}"}
    carry_c, bound_c = c["carry"], c["boundary"]
    marks_ok = [round(m, 6) for m in meas["boundary"]["marks"]] == [round(w, 6) for w in meas["boundary"]["wanted"]]
    clause_marks_ok = [round(m, 6) for m in bound_c["marks"]] == [round(w, 6) for w in meas["boundary"]["wanted"]]
    j3 = {"id": "UA3",
          "measured": f"the clause's carry is {carry_c['difference']:.4f} at {carry_c['sigma']:.2f} sigma over "
                      f"{carry_c['episodes']} episodes against a state scale of {carry_c['scale']:.4f}, its "
                      f"single-trial value {carry_c['at_one_trial']:.4e}, and its marks "
                      f"{[round(m, 3) for m in bound_c['marks']]} disjoint {bound_c['disjoint']} in the input "
                      f"{bound_c['in_input']} and drawn at the endpoint {bound_c['at_the_endpoint']}",
          "verdict": "MET -- the episode is carried, resolved, absent at one trial, and the boundary's marks are the "
                     "declaration out of the three populations" if
                     (carry_c["difference"] > 0.0 and carry_c["sigma"] >= SIGMA
                      and carry_c["at_one_trial"] == 0.0 and marks_ok and clause_marks_ok and bound_c["disjoint"]
                      and bound_c["in_input"] and not bound_c["at_the_endpoint"]) else
                     f"FALSIFIER FIRED -- carry {carry_c}, marks ok {marks_ok and clause_marks_ok}, boundary {bound_c}"}
    far = [a for a in ARMS if abs(c["accuracy"][a]["boundary"] - c["chance"]) > BAND
           or abs(c["accuracy"][a]["plain"] - c["chance"]) > BAND]
    resolved = [a for a in ARMS if abs(c["accuracy"][a]["sigma"]) >= SIGMA]
    j4 = {"id": "UA4",
          "measured": f"the clause's diagonals are "
                      f"{ {a: (round(c['accuracy'][a]['boundary'], 4), round(c['accuracy'][a]['plain'], 4)) for a in ARMS} } "
                      f"against a chance of {c['chance']:.2f} with {len(far)} arms past the band, and its boundaried "
                      f"contrasts are "
                      f"{ {a: round(c['accuracy'][a]['sigma'], 2) for a in ARMS} } sigma with {len(resolved)} resolved",
          "verdict": "MET -- the clause carries the cost: every arm sits within the band of chance and the boundary's "
                     "contrast is unresolved on every arm" if (not far and not resolved) else
                     f"FALSIFIER FIRED -- past the band {far}, resolving {resolved}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the game card's seventeenth revision: the episode ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact the clause is read from is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    card, c = r["card"], r["episode"]
    print(f"   the card is now revision {card['revision']} and its absent list is {card['absent']}")
    print(f"   the new clause is `episode`, read from {c['artifact']}")
    print(f"\n   {'arm':<10} {'boundary diag':>14} {'plain diag':>11} {'contrast':>10} {'sigma':>7} "
          f"{'boundary last':>14} {'plain last':>11}")
    for a in ARMS:
        g = c["accuracy"][a]
        print(f"   {a:<10} {g['boundary']:>14.4f} {g['plain']:>11.4f} {g['contrast']:>+10.4f} "
              f"{g['sigma']:>7.2f} {g['last_boundary']:>14.4f} {g['last_plain']:>11.4f}")
    print(f"\n   the episode: {c['trials']} trials of {c['steps_per_trial']} steps, the carry "
          f"{c['carry']['difference']:.4f} at {c['carry']['sigma']:.2f} sigma over {c['carry']['episodes']} episodes "
          f"and {c['carry']['at_one_trial']:.1e} at one trial")
    print(f"   the boundary: {c['boundary']['neurons']} neurons at gain {c['boundary']['gain']}, marks "
          f"{[round(m, 3) for m in c['boundary']['marks']]}")
    print("\n== the registered claims, UA1-UA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e470` removed a held-out task, `e482` a policy and `e486` a reward; this removes the episode")
    print("    boundary, and the card names nothing absent)")
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
