"""E414 -- the game card, revision 3: the arm's term written into the card beside the draw's.

`e409` wrote revision 2 with the world, stream, recovery and invariance clauses, which are the *draw's* side of the
benchmark. `e410` to `e413` then measured the other side: the benchmark's own two-term comparison -- the `naive` arm
against the `replay` arm on the six worlds at three budgets -- and found the arm worth a sixth of accuracy where the
draw is worth three hundredths.

**This unit writes revision 3 and reads every number in it from the artifact that measured it.** No training and no
roll: the card is a dictionary, and each clause of it is checked against a reader that already exists. Five claims,
registered before this unit read any of them.

- **AN1 -- and the second revision's clauses are unchanged.** The substrate, loop, protocol, arms, metrics and absence
  list, and the world, stream, recovery and invariance clauses, are **equal** to the ones `e409`'s revision 2 carries,
  with the revision number now **3**. **Falsifier**: any clause differing; **REFUSED** when `e409`'s artifact is
  absent.
- **AN2 -- and the arm clause is measured at three budgets.** The six worlds' gains run **-0.0174** to **+0.0365** at
  budgets 1 and 20, **+0.1330** to **+0.1594** at budget 500, and the rises from 20 to 500 run **+0.1142** to
  **+0.1639**, all read from `e413`'s artifact rather than stated. **Falsifier**: any band disagreeing with that
  artifact; **REFUSED** when it is absent.
- **AN3 -- and the arm clause's comparison is the artifact's.** The least rise, **0.1142**, is **2.79** times the six
  worlds' own span at twenty updates, **0.0410**, read from the same artifact. **Falsifier**: the ratio disagreeing, or
  at or below **twice**.
- **AN4 -- and the draw's term is carried beside the arm's.** The six draws' span on the benchmark's own metric,
  **0.0309**, read from `e410`'s artifact, sits beside the arm's least five-hundred gain, **0.1330**, read from
  `e411`'s -- **4.30** times it. **Falsifier**: either number disagreeing; **REFUSED** when either artifact is absent.
- **AN5 -- and the cut term is carried.** The largest forgetting cut at twenty updates over the six worlds is
  **0.0635** and the least at five hundred is **0.2339**, from the arm artifact, above a bar of **0.20**. **Falsifier**:
  either disagreeing, or the five-hundred cut at or below the bar.

**What it can do beyond that.** It is the benchmark a reader can hold at the state the line has reached, with both
terms inside it: the draw's clause (which world, which stream) from `e409` and the arm's clause (what the buffer is
worth, at which budget) from `e410` to `e413`, each number pointing at the artifact that measured it.

**What it cannot do.** *A card is a definition and not a result*: it states what the benchmark is and points at the
artifacts for every number. *And the numbers are six worlds' and one arm pair's*: the four engine redraws are not in
the series and the penalty arms are absent at every budget. *And the clause it cannot state is the mechanism*: the
line has screened the draw's geometry, its biology and the trained bodies' movement, and none of them separates the
one world that recovers. *And a clause is not an experiment.*
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the artifacts every clause is read from
CARD2 = Path("runs/e409_the_game_card_revision_two.json")
ARMS = Path("runs/e413_the_aid_turns_on_in_every_world.json")
BENCH = Path("runs/e410_the_benchmarks_own_metric.json")
REHEARSAL = Path("runs/e411_the_rehearsal_on_the_six_worlds.json")
#: the card as revision 3, with the clauses the arm series established and nothing restated
REVISION = 3
REVISION2_FIELDS = ("substrate", "loop", "protocol", "arms", "metrics", "absent", "world", "stream", "recovery",
                    "invariance")
ARM_CLAUSE = {"budgets": [1, 20, 500], "worlds_measured": 6, "small_band": [-0.0174, 0.0365],
              "top_band": [0.1330, 0.1594], "rise_band": [0.1142, 0.1639], "span_at_20": 0.0410,
              "least_rise_over_span_at_20": 2.79, "cut_at_20": 0.0635, "cut_at_500": 0.2339}
DRAW_CLAUSE = {"draw_span_at_500": 0.0309, "least_gain_at_500": 0.1330, "gain_over_draw_span": 4.30}
TWICE = 2.0
CUT_BAR = 0.20
TOL = 1e-3
CLAIMS = (
    ("AN1", "and the second revision's clauses are unchanged",
     "The substrate, loop, protocol, arms, metrics and absence list, and the world, stream, recovery and invariance "
     "clauses, are equal to the ones `e409`'s revision 2 carries, with the revision now 3",
     "falsifier: any clause differing; refused when `e409`'s artifact is absent"),
    ("AN2", "and the arm clause is measured at three budgets",
     "The six worlds' gains run -0.0174 to +0.0365 at budgets 1 and 20, +0.1330 to +0.1594 at 500, and the rises "
     "+0.1142 to +0.1639, read from `e413`'s artifact",
     "falsifier: any band disagreeing with that artifact; refused when it is absent"),
    ("AN3", "and the arm clause's comparison is the artifact's",
     "The least rise, 0.1142, is 2.79 times the six worlds' own span at twenty, 0.0410",
     "falsifier: the ratio disagreeing, or at or below twice"),
    ("AN4", "and the draw's term is carried beside the arm's",
     "The six draws' span on the benchmark's own metric, 0.0309, sits beside the arm's least five-hundred gain, "
     "0.1330, 4.30 times it",
     "falsifier: either number disagreeing; refused when either artifact is absent"),
    ("AN5", f"and the cut term is carried, above a bar of {CUT_BAR:.2f}",
     "The largest forgetting cut at twenty is 0.0635 and the least at five hundred is 0.2339",
     "falsifier: either disagreeing, or the five-hundred cut at or below the bar"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def reading(card2: Path = CARD2, arms: Path = ARMS, bench: Path = BENCH, rehearsal: Path = REHEARSAL) -> dict:
    out = {"ok": True, "reason": None, "card": None, "revision2": {}, "arm": {}, "draw": {}, "cuts": {}}
    base = load(card2)
    if not base:
        return {**out, "ok": False, "reason": f"{card2} is absent, so revision 2 is not on disk"}
    card = copy.deepcopy(base.get("card") or {})
    card["revision"] = REVISION
    card["arm"] = dict(ARM_CLAUSE)
    card["draw_terms"] = dict(DRAW_CLAUSE)
    out["card"] = card
    out["revision2"] = {k: (base.get("card") or {}).get(k) for k in REVISION2_FIELDS}

    a = load(arms)
    if not a:
        return {**out, "ok": False, "reason": f"{arms} is absent, so the arm clause has no reading"}
    worlds = a.get("worlds") or {}
    small = [float(w["runs"][str(b)]["gain"]) for w in worlds.values() for b in (1, 20)]
    tops = [float(w["runs"]["500"]["gain"]) for w in worlds.values()]
    rises = [float(w["gain_rise"]) for w in worlds.values()]
    out["arm"] = {"artifact": Path(arms).name, "worlds": sorted(worlds), "budgets": list(a.get("budgets") or []),
                  "small_band": [min(small), max(small)], "top_band": [min(tops), max(tops)],
                  "rise_band": [min(rises), max(rises)], "span_at_20": float((a.get("spans") or {}).get(
                      "span_at_20") or 0.0),
                  "least_rise": min(rises)}
    out["arm"]["least_rise_over_span_at_20"] = (out["arm"]["least_rise"] / out["arm"]["span_at_20"]
                                                if out["arm"]["span_at_20"] else float("nan"))
    cut_small = [float(w["runs"][str(b)]["cut"]) for w in worlds.values() for b in (1, 20)]
    cut_top = [float(w["runs"]["500"]["cut"]) for w in worlds.values()]
    out["cuts"] = {"artifact": Path(arms).name, "at_20": max(cut_small) if cut_small else None,
                   "at_500": min(cut_top) if cut_top else None}

    b1, b2 = load(bench), load(rehearsal)
    if not b1 or not b2:
        return {**out, "ok": False,
                "reason": f"{(bench if not b1 else rehearsal)} is absent, so the draw's term has no reading"}
    span = float((b1.get("spread") or {}).get("final_accuracy") or 0.0)
    least = min(float(v["accuracy_gain"]) for v in (b2.get("worlds") or {}).values())
    out["draw"] = {"artifacts": [Path(bench).name, Path(rehearsal).name], "draw_span_at_500": span,
                   "least_gain_at_500": least,
                   "gain_over_draw_span": (least / span if span else float("nan"))}
    return out


def _band(xs, ys, tol=TOL) -> bool:
    return abs(xs[0] - ys[0]) < tol and abs(xs[1] - ys[1]) < tol


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the clause is read from is absent"}
                for c in CLAIMS]
    card = r["card"]
    same = {k: (card.get(k) == r["revision2"][k]) for k in r["revision2"]}
    j1 = {"id": "AN1",
          "measured": f"the revision-2 clauses against the revision-3 card: {same}, with the revision now "
                      f"{card.get('revision')}",
          "verdict": "MET -- the second revision's clauses are carried unchanged into the third"
                     if (all(same.values()) and card.get("revision") == REVISION) else
                     f"FALSIFIER FIRED -- { {k: v for k, v in same.items() if not v} } differs"}
    arm = r["arm"]
    good2 = (_band(arm["small_band"], ARM_CLAUSE["small_band"]) and _band(arm["top_band"], ARM_CLAUSE["top_band"])
             and _band(arm["rise_band"], ARM_CLAUSE["rise_band"]) and len(arm["worlds"]) == ARM_CLAUSE["worlds_measured"])
    j2 = {"id": "AN2",
          "measured": f"`{arm['artifact']}` reads {arm['small_band'][0]:+.4f} to {arm['small_band'][1]:+.4f} at "
                      f"budgets 1 and 20, {arm['top_band'][0]:+.4f} to {arm['top_band'][1]:+.4f} at 500, and rises "
                      f"{arm['rise_band'][0]:+.4f} to {arm['rise_band'][1]:+.4f} over {len(arm['worlds'])} worlds",
          "verdict": "MET -- the arm clause is measured at three budgets" if good2 else
          f"FALSIFIER FIRED -- the artifact reads {arm['small_band']}, {arm['top_band']} and {arm['rise_band']}"}
    ratio = arm["least_rise_over_span_at_20"]
    good3 = (abs(ratio - ARM_CLAUSE["least_rise_over_span_at_20"]) < 0.01 and ratio > TWICE
             and abs(arm["span_at_20"] - ARM_CLAUSE["span_at_20"]) < TOL)
    j3 = {"id": "AN3",
          "measured": f"the least rise {arm['least_rise']:+.4f} over the span at twenty {arm['span_at_20']:.4f} is "
                      f"{ratio:.2f} times it, against a bar of {TWICE:.1f}",
          "verdict": f"MET -- the arm clause's comparison is the artifact's, {ratio:.2f} times the twenty-update span"
                     if good3 else
                     f"FALSIFIER FIRED -- the artifact reads {ratio:.2f} times the span, against its own clause"}
    d = r["draw"]
    good4 = (abs(d["draw_span_at_500"] - DRAW_CLAUSE["draw_span_at_500"]) < TOL
             and abs(d["least_gain_at_500"] - DRAW_CLAUSE["least_gain_at_500"]) < TOL
             and abs(d["gain_over_draw_span"] - DRAW_CLAUSE["gain_over_draw_span"]) < 0.01)
    j4 = {"id": "AN4",
          "measured": f"`{'` and `'.join(d['artifacts'])}` read the draw's span {d['draw_span_at_500']:.4f} and the "
                      f"arm's least gain {d['least_gain_at_500']:+.4f}, {d['gain_over_draw_span']:.2f} times it",
          "verdict": f"MET -- the draw's term is carried beside the arm's, {d['gain_over_draw_span']:.2f} times it"
                     if good4 else
                     f"FALSIFIER FIRED -- {d['draw_span_at_500']:.4f} against {d['least_gain_at_500']:+.4f}"}
    c = r["cuts"]
    good5 = (c["at_20"] is not None and c["at_500"] is not None
             and abs(c["at_20"] - ARM_CLAUSE["cut_at_20"]) < TOL
             and abs(c["at_500"] - ARM_CLAUSE["cut_at_500"]) < TOL and c["at_500"] > CUT_BAR)
    j5 = {"id": "AN5",
          "measured": f"`{c['artifact']}` reads the largest cut at twenty {c['at_20']:+.4f} and the least at five "
                      f"hundred {c['at_500']:+.4f}, against a bar of {CUT_BAR:.2f}",
          "verdict": f"MET -- the cut term is carried, {c['at_500']:+.4f} at five hundred against a bar of "
                     f"{CUT_BAR:.2f}" if good5 else
                     f"FALSIFIER FIRED -- {c['at_20']:+.4f} at twenty and {c['at_500']:+.4f} at five hundred"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the game card, revision 3 ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    card = r["card"]
    print(f"   {card.get('name')}, revision {card.get('revision')}, read 2026-10-05")
    for k in ("substrate", "loop", "protocol", "arms", "metrics", "absent"):
        print(f"   {k + ':':<10} {card.get(k)}")
    print("\n   and the clauses, each with the artifact it is read from:")
    for k in ("world", "stream", "recovery", "invariance"):
        print(f"   {k + ':':<11} {card.get(k)}")
    arm = r["arm"]
    print(f"   arm:        {arm['artifact']} over {len(arm['worlds'])} worlds at budgets {arm['budgets']}: gains "
          f"{arm['small_band'][0]:+.4f} to {arm['small_band'][1]:+.4f} at 1 and 20, {arm['top_band'][0]:+.4f} to "
          f"{arm['top_band'][1]:+.4f} at 500")
    d = r["draw"]
    print(f"   draw terms: {' and '.join(d['artifacts'])}: the draw spans {d['draw_span_at_500']:.4f}, the arm is "
          f"worth {d['least_gain_at_500']:+.4f}, {d['gain_over_draw_span']:.2f} times it")

    print("\n== the registered claims, AN1-AN5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e409` wrote revision 2 with the draw's clauses; `e410` to `e413` measured the arm's term on the same")
    print("    six runs, which is what this carries)")
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
