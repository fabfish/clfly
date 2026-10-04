"""E409 -- the game card, revision 2: what the redraw series established, written into the card.

`e392` wrote the closed-loop benchmark down as a card and measured its two absences -- one world and one seed stream
-- with `e393` to `e403` then closing them: four engine redraws at the near point, three clean training streams, the
far point on all five worlds and the stream axis at the far point. Its own RE-READ put the consequence: *"the card is
at **revision 2**, which carries the two spreads beside the numbers they bound."* And `e404` to `e408` then gave the
six worlds a six-budget series, which is the material a second revision needs and which no card has yet carried.

**This unit writes revision 2 and reads every number in it from the artifact that measured it.** No training and no
roll: the card is a dictionary, and each clause of it is checked against a reader that already exists. Five claims,
registered before this unit read any of them.

- **AM1 -- and the first revision's clauses are unchanged.** The substrate, loop, protocol, arms and metrics the card
  publishes are **equal** to the ones `e392`'s revision 1 carries, and its absence list is unchanged. **Falsifier**:
  any clause differing; **REFUSED** when `e392`'s artifact is absent.
- **AM2 -- and the world clause is measured at both ends.** The six worlds' span is **0.0750** at twenty updates and
  **0.3104** at five hundred, both read from `e407`'s artifact rather than stated. **Falsifier**: either span
  disagreeing with that artifact; **REFUSED** when it is absent.
- **AM3 -- and the stream clause is measured against the world's.** The three clean streams span **0.0323** at the
  far point where the five worlds span **0.3344** -- **0.097** of it -- read from `e403`'s and `e396`'s artifacts.
  **Falsifier**: either span disagreeing; **REFUSED** when either is absent.
- **AM4 -- and the recovery clause is one world's.** Exactly **one** of the five worlds measured at the far point
  ends above its own connectome reading by **0.05**. **Falsifier**: none or more than one; **REFUSED** when the
  artifact is absent.
- **AM5 -- and the invariance clause is carried.** The connectome's own reading is **0.6875** on **every** world in
  both artifacts, over at least **10** readings, with a spread of **0.0000**. **Falsifier**: any world differing, or
  fewer than ten readings.

**What it can do beyond that.** It is the benchmark a reader can hold at the state the line has reached: the
substrate, the loop, the protocol and the arms as `e392` fixed them, and inside the world's clause the two numbers a
user of the benchmark must now report -- which **draw** the run was on, and which **stream** -- with the evidence for
each being a pair of spreads rather than a sentence.

**What it cannot do.** *A card is a definition and not a result*: it states what the benchmark is and points at the
artifacts for every number. *And the numbers are six worlds' and one arm's*: the four engine redraws are not in the
series and the 3e-3 `naive` bodies are the only ones measured at these budgets. *And the clause it cannot state is
the mechanism*: the line has screened the draw's geometry, its biology and the trained bodies' movement, and none of
them separates the one world that recovers.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the artifacts every clause is read from
CARD1 = Path("runs/e392_the_game_card.json")
SERIES = Path("runs/e407_five_budgets_on_all_six_worlds.json")
STREAMS = Path("runs/e403_the_far_point_on_the_clean_stream.json")
WORLDS = Path("runs/e396_the_far_point_on_all_five_worlds.json")
#: the card as revision 2, with the clauses the series established and nothing restated
REVISION = 2
WORLD_CLAUSE = {"span_at_20": 0.0750, "span_at_500": 0.3104, "worlds_measured": 6}
STREAM_CLAUSE = {"span_at_500": 0.0323, "against_the_worlds": 0.3344, "streams_measured": 3}
RECOVERY_CLAUSE = {"worlds_at_the_far_point": 5, "recovering": 1, "bar": 0.05}
INVARIANCE = {"reading": 0.6875, "spread": 0.0000, "over_at_least": 10}
GAIN = 0.05
MIN_READINGS = 10
CLAIMS = (
    ("AM1", "and the first revision's clauses are unchanged",
     "The substrate, loop, protocol, arms and metrics the card publishes are equal to the ones `e392`'s revision 1 "
     "carries, and its absence list is unchanged",
     "falsifier: any clause differing; refused when `e392`'s artifact is absent"),
    ("AM2", "and the world clause is measured at both ends",
     "The six worlds' span is 0.0750 at twenty updates and 0.3104 at five hundred, read from `e407`'s artifact",
     "falsifier: either span disagreeing with that artifact; refused when it is absent"),
    ("AM3", "and the stream clause is measured against the world's",
     "The three clean streams span 0.0323 at the far point where the five worlds span 0.3344",
     "falsifier: either span disagreeing; refused when either artifact is absent"),
    ("AM4", "and the recovery clause is one world's",
     "Exactly one of the five worlds measured at the far point ends above its own connectome reading by 0.05",
     "falsifier: none or more than one; refused when the artifact is absent"),
    ("AM5", f"and the invariance clause is carried, over at least {MIN_READINGS} readings",
     "The connectome's own reading is 0.6875 on every world in both artifacts, with a spread of 0.0000",
     "falsifier: any world differing, or fewer than ten readings"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def reading(card1: Path = CARD1, series: Path = SERIES, streams: Path = STREAMS,
            worlds: Path = WORLDS) -> dict:
    out = {"ok": True, "reason": None, "card": None, "world": {}, "stream": {}, "recovery": {}, "invariance": {}}
    base = load(card1)
    if not base:
        return {**out, "ok": False, "reason": f"{card1} is absent, so revision 1 is not on disk"}
    card = copy.deepcopy(base.get("card") or {})
    card["revision"] = REVISION
    card["world"] = dict(WORLD_CLAUSE)
    card["stream"] = dict(STREAM_CLAUSE)
    card["recovery"] = dict(RECOVERY_CLAUSE)
    card["invariance"] = dict(INVARIANCE)
    out["card"] = card
    out["revision1"] = {k: (base.get("card") or {}).get(k) for k in ("substrate", "loop", "protocol", "arms",
                                                                     "metrics", "absent")}

    s = load(series)
    if not s:
        return {**out, "ok": False, "reason": f"{series} is absent, so the world clause has no reading"}
    out["world"] = {"artifact": Path(series).name,
                    "span_at_20": float((s.get("spread") or {}).get("20") or 0.0),
                    "span_at_500": float((s.get("spread") or {}).get("500") or 0.0),
                    "worlds": sorted(s.get("worlds") or {})}

    st = load(streams)
    if not st:
        return {**out, "ok": False, "reason": f"{streams} is absent, so the stream clause has no reading"}
    out["stream"] = {"artifact": Path(streams).name, "span_at_500": float((st.get("spread") or {}).get("body") or 0.0),
                     "against_the_worlds": float(st.get("worlds_span") or 0.0),
                     "streams": sorted(st.get("streams") or {})}

    w = load(worlds)
    if not w:
        return {**out, "ok": False, "reason": f"{worlds} is absent, so the recovery clause has no reading"}
    entries = w.get("worlds") or {}
    recovering = [n for n, v in entries.items()
                  if float(v.get("body_task_0", 0.0)) - float(v.get("initial_task_0", 0.0)) >= GAIN]
    readings = [float(v.get("initial_task_0", 0.0)) for v in entries.values()]
    out["recovery"] = {"artifact": Path(worlds).name, "worlds": sorted(entries), "recovering": sorted(recovering)}
    #: the series' artifact carries the same worlds at six budgets each, so the invariance is read from both
    series_readings = []
    if s:
        series_readings = [float(w["budgets"][b]["initial_task_0"])
                           for w in (s.get("worlds") or {}).values() for b in (s.get("worlds") or {}).get("card",
                                                                                                         {}).get(
                               "budgets", {})] if (s.get("worlds") or {}) else []
    allr = readings + series_readings
    out["invariance"] = {"artifact": [Path(worlds).name, Path(series).name], "readings": allr,
                         "spread": (max(allr) - min(allr)) if allr else None}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the clause is read from is absent"}
                for c in CLAIMS]
    card = r["card"]
    same = {k: (card.get(k) == r["revision1"][k]) for k in r["revision1"]}
    j1 = {"id": "AM1", "measured": f"the revision-1 clauses against the revision-2 card: {same}, with the revision "
                                   f"now {card.get('revision')}",
          "verdict": "MET -- the first revision's clauses are carried unchanged into the second" if all(same.values())
          else f"FALSIFIER FIRED -- { {k: v for k, v in same.items() if not v} } differs"}

    w = r["world"]
    #: the artifact stores the spans unrounded, so the clause is checked to a thousandth rather than exactly
    good2 = (abs(w["span_at_20"] - WORLD_CLAUSE["span_at_20"]) < 1e-3
             and abs(w["span_at_500"] - WORLD_CLAUSE["span_at_500"]) < 1e-3
             and len(w["worlds"]) == WORLD_CLAUSE["worlds_measured"])
    j2 = {"id": "AM2", "measured": f"`{w['artifact']}` reads {w['span_at_20']:.4f} at twenty updates and "
                                   f"{w['span_at_500']:.4f} at five hundred over {len(w['worlds'])} worlds",
          "verdict": "MET -- the world clause is measured at both ends" if good2 else
          f"FALSIFIER FIRED -- the artifact reads {w['span_at_20']:.4f} and {w['span_at_500']:.4f} over "
          f"{len(w['worlds'])} worlds"}

    st = r["stream"]
    good3 = (abs(st["span_at_500"] - STREAM_CLAUSE["span_at_500"]) < 1e-3
             and abs(st["against_the_worlds"] - STREAM_CLAUSE["against_the_worlds"]) < 1e-3)
    ratio = st["span_at_500"] / st["against_the_worlds"] if st["against_the_worlds"] else float("nan")
    j3 = {"id": "AM3", "measured": f"`{st['artifact']}` reads {st['span_at_500']:.4f} over {len(st['streams'])} "
                                   f"streams against the worlds' {st['against_the_worlds']:.4f}, "
                                   f"{ratio:.3f} of it",
          "verdict": f"MET -- the stream clause is measured against the world's, {ratio:.3f} of it" if good3 else
          f"FALSIFIER FIRED -- {st['span_at_500']:.4f} against {st['against_the_worlds']:.4f}"}

    rec = r["recovery"]
    good4 = len(rec["recovering"]) == RECOVERY_CLAUSE["recovering"] and len(rec["worlds"]) == \
        RECOVERY_CLAUSE["worlds_at_the_far_point"]
    j4 = {"id": "AM4", "measured": f"`{rec['artifact']}` measures {len(rec['worlds'])} worlds at the far point and "
                                   f"{len(rec['recovering'])} of them recover: {rec['recovering']}",
          "verdict": "MET -- the recovery clause is one world's" if good4 else
          f"FALSIFIER FIRED -- {len(rec['recovering'])} of {len(rec['worlds'])} recover"}

    inv = r["invariance"]
    good5 = (inv["spread"] is not None and inv["spread"] == 0.0 and len(inv["readings"]) >= MIN_READINGS
             and set(inv["readings"]) == {INVARIANCE["reading"]})
    j5 = {"id": "AM5", "measured": f"the {len(inv['readings'])} connectome readings in `{inv['artifact']}` take "
                                   f"{sorted(set(inv['readings']))} with a spread of {inv['spread']:.4f}",
          "verdict": f"MET -- the invariance clause is carried over {len(inv['readings'])} readings" if good5 else
          f"FALSIFIER FIRED -- the readings are {sorted(set(inv['readings']))} over {len(inv['readings'])} readings"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the game card, revision 2 ==")
        print(f"   REFUSED -- {r.get('reason', 'an artifact is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    card = r["card"]
    print("== the game card, revision 2 ==")
    print(f"   {card.get('name')}, revision {card.get('revision')}, read 2026-10-04")
    for k in ("substrate", "loop", "protocol", "arms", "metrics", "absent"):
        print(f"   {k + ':':<10} {card.get(k)}")
    print("\n   and the clauses the redraw series established, each with the artifact it is read from:")
    print(f"   world:      {r['world']['artifact']} spans {r['world']['span_at_20']:.4f} at twenty and "
          f"{r['world']['span_at_500']:.4f} at five hundred over {len(r['world']['worlds'])} worlds")
    print(f"   stream:     {r['stream']['artifact']} spans {r['stream']['span_at_500']:.4f} over "
          f"{len(r['stream']['streams'])} streams against the worlds' {r['stream']['against_the_worlds']:.4f}")
    print(f"   recovery:   {r['recovery']['artifact']} has {len(r['recovery']['recovering'])} of "
          f"{len(r['recovery']['worlds'])} worlds recovering")
    print(f"   invariance: {r['invariance']['artifact']} reads {sorted(set(r['invariance']['readings']))} over "
          f"{len(r['invariance']['readings'])} worlds")

    print("\n== the registered claims, AM1-AM5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e392` wrote revision 1 and registered that its cell carries one world and one stream; `e393` to")
    print("    `e408` closed both absences and gave the six worlds a six-budget series, which is what this carries)")
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
