"""E450 -- the game card, revision 9: the width clause, and the three widths the card has been played at.

Revision 8 carried the **ledger** clause: the buffer's three-position gain over the baseline and the anchor's newest-task
price, over the four rolls of the card's own world that `e437` to `e444` drove. Every one of those rolls, and `e446`'s
and `e447`'s with them, was taken at **eight columns**. `e448` then doubled the world's width and found the two arms
separating -- the buffer's ledger held while the anchor's price fell from **-0.1177** at **3.71** sigma to **-0.0292**
at **1.68** -- and `e449` halved it and found that **eight columns is a peak**: of the six numbers across the three
widths, five are largest there, and the anchor's whole-diagonal standing clears two sigma for the first time at four
columns. Both units named the same gap: *the card's clause is a statement about the width the card is played at and not
about a range of them*.

**This unit writes revision 9.** One clause is added, the **width** clause, and every other field is checked equal to
`e445`'s card rather than quoted. The clause carries the three widths' own numbers, recomputed here from the three rolls,
with the sigmas that separate them. Five claims, registered before this unit's pass over the three rolls -- and as `e440`
stated his, **CW2 and CW3 are confirmatory**, the three rolls' numbers being published in `e448`'s and `e449`'s findings
already; CW1, CW4 and CW5 are structural.

- **CW1 -- and the eighth revision is carried unchanged where it is not rewritten.** Every field of `e445`'s card except
  the revision and the new clause is equal to the revision-8 card, with the revision now **9**. **Falsifier**: any other
  field differing, or the revision not 9; refused when the revision-8 artifact is absent.
- **CW2 -- and the clause's numbers come out of the three rolls.** Each width's baseline diagonal, the buffer's
  first-position gain and first-over-last margin, and the anchor's mean diagonal and newest-task cost, each beside its
  own sigma, equal the three rolls recomputed here. **Falsifier**: any number disagreeing by more than a thousandth of a
  point; refused when a roll is absent.
- **CW3 -- and five of the six numbers are largest at the card's own width.** The buffer's first-position gain, its
  margin and its mean-diagonal magnitude, and the anchor's newest-task magnitude and that contrast's sigma, each take
  their largest value at **8** of the three widths. **Falsifier**: any of the five largest at another width.
- **CW4 -- and the sigmas separate the two ends.** The anchor's newest-task cost clears **two** sigma at four and at
  eight columns and does not at sixteen, and its whole-diagonal standing clears two sigma only at four. **Falsifier**:
  any of those five readings failing.
- **CW5 -- and the clause names the widths and the rolls it was measured on.** It carries **4**, **8** and **16** as the
  widths with **8** the card's own, the three rolls' artifacts, and a baseline diagonal that is those rolls' own.
  **Falsifier**: another width or another count, a missing artifact, or a baseline that is not the rolls'.

**What it can do beyond that.** It is the card's own statement of how much of its headline is a width's. A reader who
takes the `ledger` clause and this one together sees that the buffer's ledger and the anchor's price were measured at the
width where both are largest, that a doubling removes the anchor's only resolved effect, and that a halving gives the
anchor the one resolved deficit it has anywhere -- which is what `e286`'s axis amounts to on this world.

**What it cannot do.** *Three widths*: four, eight and sixteen are three points and not a curve, so the clause carries a
peak at eight and not the shape of one. *And the card's clause is still the card's*: CW1 shows revision 8 survives into
revision 9 and not that revision 8 was right, and CW2 shows the clause agrees with the three rolls and not that the three
rolls should be believed. *And the width is a manipulation of the game*: narrowing the world changes what the three tasks
are as well as how many columns the decoder has, so the clause's numbers carry the task's own change with them. *And one
arm pair*: no matched-random arm at four or sixteen columns, so whether the corpus's headline basis contrast survives a
widening or a narrowing is not in this clause.
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

#: the card the clause is added to
CARD8 = Path("runs/e445_the_game_card_revision_eight.json")
#: the three rolls of the card's own world, at the three widths the line has driven
ROLLS = {
    "four": Path("runs/e449_earned_label_worlddims4_20reps.json"),
    "eight": Path("runs/e438_earned_label_three_arms_20reps.json"),
    "sixteen": Path("runs/e448_earned_label_worlddims16_20reps.json"),
}
WIDTHS = {"four": 4, "eight": 8, "sixteen": 16}
CARD_WIDTH = 8
BASELINE = "naive"
BUFFER = "replay"
ANCHOR = "ewc-block"
REVISION = 9
NEW = ("revision", "width")
MIN_REPS = 20
N_TASKS = 3
SIGMA = 2.0
TOL = 0.002
CLAIMS = (
    ("CW1", "and the eighth revision is carried unchanged where it is not rewritten",
     "Every field of `e445`'s card except the revision and the new clause is equal to the revision-8 card, with the "
     "revision now 9",
     "falsifier: any other field differing, or the revision not 9; refused when `e445`'s artifact is absent"),
    ("CW2", "and the clause's numbers come out of the three rolls",
     "Each width's baseline diagonal, the buffer's first-position gain and first-over-last margin, and the anchor's mean "
     "diagonal and newest-task cost, each beside its own sigma, equal the three rolls recomputed",
     "falsifier: any number disagreeing by more than a thousandth of a point; refused when a roll is absent"),
    ("CW3", "and five of the six numbers are largest at the card's own width",
     "The buffer's first-position gain, its margin and its mean-diagonal magnitude, and the anchor's newest-task "
     "magnitude and that contrast's sigma, each take their largest value at 8 of the three widths",
     "falsifier: any of the five largest at another width"),
    ("CW4", "and the sigmas separate the two ends",
     "The anchor's newest-task cost clears two sigma at four and at eight columns and does not at sixteen, and its "
     "whole-diagonal standing clears two sigma only at four",
     "falsifier: any of those five readings failing"),
    ("CW5", "and the clause names the widths and the rolls it was measured on",
     "It carries 4, 8 and 16 as the widths with 8 the card's own, the three rolls' artifacts, and a baseline diagonal "
     "that is those rolls' own",
     "falsifier: another width or another count, a missing artifact, or a baseline that is not the rolls'"),
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


def _roll(path: Path) -> dict | None:
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    arms = {}
    for arm in (BASELINE, BUFFER, ANCHOR):
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        arms[arm] = {"replicates": len(reps),
                     "final": [statistics.fmean([r["final_per_task"][k] for r in reps]) for k in range(N_TASKS)],
                     "diagonal": [statistics.fmean(r["final_per_task"]) for r in reps],
                     "last": [r["final_per_task"][-1] for r in reps]}
    return {"artifact": path.name, "arms": arms, "width": (doc.get("config") or {}).get("loop_world_dims")}


def _numbers(got: dict) -> dict:
    arms = got["arms"]
    gain = [arms[BUFFER]["final"][k] - arms[BASELINE]["final"][k] for k in range(N_TASKS)]
    return {"artifact": got["artifact"], "width": got["width"], "replicates": arms[BASELINE]["replicates"],
            "baseline_diagonal": statistics.fmean(arms[BASELINE]["diagonal"]),
            "buffer_first": gain[0], "buffer_margin": gain[0] - gain[-1],
            "buffer_diagonal": _paired(arms[BUFFER]["diagonal"], arms[BASELINE]["diagonal"]),
            "anchor_diagonal": _paired(arms[ANCHOR]["diagonal"], arms[BASELINE]["diagonal"]),
            "anchor_last": _paired(arms[ANCHOR]["last"], arms[BASELINE]["last"])}


def reading(card8: Path = CARD8, rolls: dict = ROLLS) -> dict:
    out = {"ok": True, "reason": None, "card": None, "revision8": {}, "width": {}, "rolls": {}}
    base = load(card8)
    if not base:
        return {**out, "ok": False, "reason": f"{card8} is absent, so revision 8 is not on disk"}
    old = base.get("card") or {}
    card = copy.deepcopy(old)
    card["revision"] = REVISION
    out["revision8"] = {k: v for k, v in old.items() if k not in NEW}

    numbers = {}
    for label, path in rolls.items():
        got = _roll(path)
        if got is None:
            return {**out, "ok": False, "reason": f"{path} is absent or carries no arm, so the clause has no reading"}
        numbers[label] = _numbers(got)
        out["rolls"][label] = numbers[label]
    card["width"] = {
        "artifact": [numbers[l]["artifact"] for l in numbers],
        "widths": {l: numbers[l]["width"] for l in numbers},
        "card_width": CARD_WIDTH,
        "baseline_diagonal": {l: numbers[l]["baseline_diagonal"] for l in numbers},
        "buffer_first": {l: numbers[l]["buffer_first"] for l in numbers},
        "buffer_margin": {l: numbers[l]["buffer_margin"] for l in numbers},
        "buffer_diagonal": {l: numbers[l]["buffer_diagonal"]["mean"] for l in numbers},
        "buffer_diagonal_sigma": {l: numbers[l]["buffer_diagonal"]["sigma"] for l in numbers},
        "anchor_diagonal": {l: numbers[l]["anchor_diagonal"]["mean"] for l in numbers},
        "anchor_diagonal_sigma": {l: numbers[l]["anchor_diagonal"]["sigma"] for l in numbers},
        "anchor_last": {l: numbers[l]["anchor_last"]["mean"] for l in numbers},
        "anchor_last_sigma": {l: numbers[l]["anchor_last"]["sigma"] for l in numbers},
    }
    out["width"] = dict(card["width"])
    out["card"] = card
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the clause is read from is absent"}
                for c in CLAIMS]
    card, w = r["card"], r["width"]
    same = {k: (card.get(k) == v) for k, v in r["revision8"].items()}
    j1 = {"id": "CW1",
          "measured": f"the revision-8 card's {len(same)} fields against the revision-9 card: "
                      f"{len(same) - sum(1 for v in same.values() if not v)} equal, with the revision now "
                      f"{card.get('revision')}",
          "verdict": f"MET -- the eighth revision is carried unchanged in all {len(same)} fields it does not rewrite" if
                     (all(same.values()) and card.get("revision") == REVISION) else
                     f"FALSIFIER FIRED -- { {k: v for k, v in same.items() if not v} } differs"}
    carried = {"baseline_diagonal": w["baseline_diagonal"], "buffer_first": w["buffer_first"],
               "buffer_margin": w["buffer_margin"], "buffer_diagonal": w["buffer_diagonal"],
               "buffer_diagonal_sigma": w["buffer_diagonal_sigma"], "anchor_diagonal": w["anchor_diagonal"],
               "anchor_diagonal_sigma": w["anchor_diagonal_sigma"], "anchor_last": w["anchor_last"],
               "anchor_last_sigma": w["anchor_last_sigma"]}
    recomputed = {"baseline_diagonal": {l: v["baseline_diagonal"] for l, v in r["rolls"].items()},
                  "buffer_first": {l: v["buffer_first"] for l, v in r["rolls"].items()},
                  "buffer_margin": {l: v["buffer_margin"] for l, v in r["rolls"].items()},
                  "buffer_diagonal": {l: v["buffer_diagonal"]["mean"] for l, v in r["rolls"].items()},
                  "buffer_diagonal_sigma": {l: v["buffer_diagonal"]["sigma"] for l, v in r["rolls"].items()},
                  "anchor_diagonal": {l: v["anchor_diagonal"]["mean"] for l, v in r["rolls"].items()},
                  "anchor_diagonal_sigma": {l: v["anchor_diagonal"]["sigma"] for l, v in r["rolls"].items()},
                  "anchor_last": {l: v["anchor_last"]["mean"] for l, v in r["rolls"].items()},
                  "anchor_last_sigma": {l: v["anchor_last"]["sigma"] for l, v in r["rolls"].items()}}
    bad2 = {}
    for key, got in carried.items():
        for label, value in got.items():
            want = recomputed[key].get(label)
            if want is None or abs(value - want) > TOL:
                bad2[f"{key}/{label}"] = (value, want)
    j2 = {"id": "CW2",
          "measured": f"the clause's baseline diagonals are { {l: round(v, 4) for l, v in w['baseline_diagonal'].items()} },"
                      f" the buffer's first-position gains { {l: round(v, 4) for l, v in w['buffer_first'].items()} }, "
                      f"its margins { {l: round(v, 4) for l, v in w['buffer_margin'].items()} } and the anchor's newest "
                      f"tasks { {l: round(v, 4) for l, v in w['anchor_last'].items()} }",
          "verdict": "MET -- the clause's numbers are the three rolls' own" if not bad2 else
                     f"FALSIFIER FIRED -- {bad2}"}
    #: the five the finding says peak at the card's own width
    peaks = {"buffer_first": w["buffer_first"], "buffer_margin": w["buffer_margin"],
             "buffer_diagonal_magnitude": {l: abs(v) for l, v in w["buffer_diagonal"].items()},
             "anchor_last_magnitude": {l: abs(v) for l, v in w["anchor_last"].items()},
             "anchor_last_sigma_magnitude": {l: abs(v) for l, v in w["anchor_last_sigma"].items()}}
    at_peak = {}
    for key, got in peaks.items():
        best = max(got, key=lambda l: got[l])
        at_peak[key] = {"peak": best, "at_card_width": w["widths"][best] == CARD_WIDTH}
    off = {k: v for k, v in at_peak.items() if not v["at_card_width"]}
    j3 = {"id": "CW3",
          "measured": f"of the five the widths they peak at are "
                      f"{ {k: (w['widths'][v['peak']], round(max(peaks[k].values()), 4)) for k, v in at_peak.items()} }",
          "verdict": "MET -- all five of the clause's numbers are largest at the card's own width" if not off else
                     f"FALSIFIER FIRED -- {off}"}
    st = w["anchor_last_sigma"]
    dst = w["anchor_diagonal_sigma"]
    fails = {}
    for label in ("four", "eight", "sixteen"):
        clears_last = abs(st[label]) >= SIGMA
        clears_diag = abs(dst[label]) >= SIGMA
        if label in ("four", "eight") and not clears_last:
            fails[f"{label}/anchor_last"] = st[label]
        if label == "sixteen" and clears_last:
            fails["sixteen/anchor_last"] = st[label]
        if label == "four" and not clears_diag:
            fails["four/anchor_diagonal"] = dst[label]
        if label in ("eight", "sixteen") and clears_diag:
            fails[f"{label}/anchor_diagonal"] = dst[label]
    j4 = {"id": "CW4",
          "measured": f"the anchor's newest-task sigmas are "
                      f"{ {l: round(abs(v), 2) for l, v in st.items()} } and its standing's "
                      f"{ {l: round(abs(v), 2) for l, v in dst.items()} }",
          "verdict": "MET -- the price clears two sigma at four and eight and not at sixteen, and the standing only at "
                     "four" if not fails else f"FALSIFIER FIRED -- {fails}"}
    named = (set(w["widths"].values()) == {4, 8, 16} and w["card_width"] == CARD_WIDTH)
    artifacts_ok = sorted(w["artifact"]) == sorted(v["artifact"] for v in r["rolls"].values())
    baseline_ok = all(abs(w["baseline_diagonal"][l] - v["baseline_diagonal"]) <= TOL for l, v in r["rolls"].items())
    j5 = {"id": "CW5",
          "measured": f"the clause names the widths {sorted(w['widths'].values())} with {w['card_width']} the card's "
                      f"own, {artifacts_ok} artifacts, and a baseline that is the rolls' own {baseline_ok}",
          "verdict": "MET -- the clause names the three widths, the card's own among them, the three rolls' artifacts "
                     "and their own baselines" if (named and artifacts_ok and baseline_ok) else
                     f"FALSIFIER FIRED -- named {named}, artifacts {artifacts_ok}, baseline {baseline_ok}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the game card, revision 9 ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    card = r["card"]
    print(f"   {card.get('name')}, revision {card.get('revision')}, read 2026-10-07")
    print(f"\n   arms:       {card.get('arms')}")
    print(f"   clauses:    {len(card)} fields, the new one being `width`")
    w = r["width"]
    print(f"\n   the three widths the card has been played at: {sorted(w['widths'].values())}, the card's own "
          f"{w['card_width']}")
    print(f"\n   {'width':>8} {'baseline':>10} {'buffer first':>13} {'its margin':>11} {'buffer diag':>12} "
          f"{'anchor diag':>12} {'its last':>10}")
    for label in ("four", "eight", "sixteen"):
        print(f"   {w['widths'][label]:>8} {w['baseline_diagonal'][label]:10.4f} {w['buffer_first'][label]:+13.4f} "
              f"{w['buffer_margin'][label]:+11.4f} {w['buffer_diagonal'][label]:+12.4f} "
              f"{w['anchor_diagonal'][label]:+12.4f} {w['anchor_last'][label]:+10.4f}")
    print(f"\n   and the sigmas that separate them:")
    print(f"      the buffer's mean diagonal  " + "  ".join(f"{l} {abs(w['buffer_diagonal_sigma'][l]):.2f}"
                                                              for l in ("four", "eight", "sixteen")))
    print(f"      the anchor's mean diagonal  " + "  ".join(f"{l} {abs(w['anchor_diagonal_sigma'][l]):.2f}"
                                                              for l in ("four", "eight", "sixteen")))
    print(f"      the anchor's newest task    " + "  ".join(f"{l} {abs(w['anchor_last_sigma'][l]):.2f}"
                                                              for l in ("four", "eight", "sixteen")))
    print("\n== the registered claims, CW1-CW5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e445` wrote revision 8, the ledger clause, from four rolls all at eight columns; `e448` and `e449`")
    print("    then doubled and halved the width, and this is what the three widths put in the card)")
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
