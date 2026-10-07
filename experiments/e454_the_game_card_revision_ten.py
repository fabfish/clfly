"""E454 -- the game card, revision 10: the method clause, and the one headline this world has that resolves everywhere.

`e453` read the corpus's method contrast -- `replay` against an anchor -- across the **ten** rolls of the card's own
world and found it positive at **8.27** to **15.33** sigma on every one, spanning **0.0708** across five manipulations,
while the **basis** contrast never resolves. The card's ninth revision carries the `ledger` clause (the buffer's
per-position ledger and the anchor's newest-task price) and the `width` clause (three widths' numbers with the peak at
eight), and **neither states what the ten rolls say together**: that this world has one headline that resolves
everywhere and it is the method's. `e453` closed on exactly that.

**This unit writes revision 10.** One clause is added, the **method** clause, and every other field is checked equal to
`e450`'s card rather than quoted, with every number recomputed from the ten rolls as `e445`'s and `e450`'s were. Five
claims, registered before this unit's pass over the ten.

- **DA1 -- and the ninth revision is carried unchanged where it is not rewritten.** Every field of `e450`'s card except
  the revision and the new clause is equal to the revision-9 card, with the revision now **10**. **Falsifier**: any other
  field differing, or the revision not 10; refused when the revision-9 artifact is absent.
- **DA2 -- and the clause's numbers come out of the ten rolls.** Every contrast and every sigma, the range, the span and
  the least and greatest sigma equal the ten rolls recomputed here, and each roll's forgetting contrast equals its own
  recomputation. **Falsifier**: any number disagreeing by more than a thousandth of a point; refused when a roll is
  absent.
- **DA3 -- and the clause's reading holds on all ten.** On each roll the buffer's mean diagonal over its anchor is
  positive at **two** sigma or more. **Falsifier**: any roll where it is not.
- **DA4 -- and the clause's weakest instance is well clear of the bar.** The least sigma across the ten is at least
  **five** and the span of the ten contrasts at most **0.10**. **Falsifier**: a least sigma under **two** or a span of
  **0.20** or more; **null**: between.
- **DA5 -- and the clause names the arms and the rolls.** It carries `replay` as the buffer, the two anchors
  distinguished, the count **10** with **7** and **3**, and the ten rolls' artifacts. **Falsifier**: another buffer or
  another count, a missing artifact, or a roll outside the ten.

**What it can do beyond that.** It is the card's own statement of which of its two headline contrasts resolves. A reader
who takes the `ledger`, `width` and `method` clauses together has the whole of what this line has measured on the card's
world: the buffer's advantage is the sequence's at the first position and the storage's everywhere else, the anchors have
no standing and a price, the width peaks at eight, and the **method** contrast is the one that holds at every order, both
redraws and all three widths. The **basis** contrast, which is the paper's question, is not in any of the three and has
never resolved.

**What it cannot do.** *Ten rolls of one world*: the card's own, so other worlds and the corpus's other suites -- where
`e276` took its **3.30** to **11.84** range -- are not in the clause. *And one pair per roll*: each roll pairs the buffer
against one anchor, so the clause compares the two anchors through the buffer and not directly. *And a clause is not a
result*: DA1 shows revision 9 survives into revision 10 and not that revision 9 was right, and DA2 shows the clause
agrees with the ten rolls and not that the ten should be believed. *And ten rows are not ten cells*: three of the ten are
matched-random rolls and the two anchors have been found **0.0042** to **0.0108** apart, so the clause's **10** is a count
of rolls and not of independent readings.
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
CARD9 = Path("runs/e450_the_game_card_revision_nine.json")
#: the ten rolls of the card's own world, by the family whose anchor each carries
ROLLS = {
    "biological/as_built": Path("runs/e438_earned_label_three_arms_20reps.json"),
    "biological/rotated": Path("runs/e441_earned_label_anchor_order102_20reps.json"),
    "biological/env_redrawn": Path("runs/e443_earned_label_worldseed1_20reps.json"),
    "biological/decoder_redrawn": Path("runs/e444_earned_label_readoutseed1_20reps.json"),
    "biological/reversed": Path("runs/e446_earned_label_anchor_reverse_20reps.json"),
    "biological/wide_16": Path("runs/e448_earned_label_worlddims16_20reps.json"),
    "biological/narrow_4": Path("runs/e449_earned_label_worlddims4_20reps.json"),
    "matched_random/as_built": Path("runs/e439_earned_label_rand_20reps.json"),
    "matched_random/reversed": Path("runs/e447_earned_label_rand_reverse_20reps.json"),
    "matched_random/narrow_4": Path("runs/e451_earned_label_rand_worlddims4_20reps.json"),
}
FAMILIES = {"biological": "ewc-block", "matched_random": "ewc-block-rand"}
BASELINE = "naive"
BUFFER = "replay"
REVISION = 10
NEW = ("revision", "method")
N_TASKS = 3
MIN_REPS = 20
SIGMA = 2.0
LEAST_SIGMA = 5.0
LEAST_FLOOR = 2.0
SPAN = 0.10
SPAN_FIRES = 0.20
TOL = 0.002
CLAIMS = (
    ("DA1", "and the ninth revision is carried unchanged where it is not rewritten",
     "Every field of `e450`'s card except the revision and the new clause is equal to the revision-9 card, with the "
     "revision now 10",
     "falsifier: any other field differing, or the revision not 10; refused when `e450`'s artifact is absent"),
    ("DA2", "and the clause's numbers come out of the ten rolls",
     "Every contrast and every sigma, the range, the span and the least and greatest sigma equal the ten rolls "
     "recomputed, and each roll's forgetting contrast equals its own recomputation",
     "falsifier: any number disagreeing by more than a thousandth of a point; refused when a roll is absent"),
    ("DA3", f"and the clause's reading holds on all ten, at {SIGMA:.0f} sigma",
     "On each roll the buffer's mean diagonal over its anchor is positive at two sigma or more",
     "falsifier: any roll where it is not"),
    ("DA4", f"and the clause's weakest instance is clear of the bar, at least {LEAST_SIGMA:.0f} sigma within {SPAN:.2f}",
     "The least sigma across the ten is at least five and the span of the ten contrasts at most 0.10",
     f"falsifier: a least sigma under {LEAST_FLOOR:.2f} or a span of {SPAN_FIRES:.2f} or more; null: between"),
    ("DA5", "and the clause names the arms and the rolls",
     "It carries replay as the buffer, the two anchors distinguished, the count 10 with 7 and 3, and the ten rolls' "
     "artifacts",
     "falsifier: another buffer or another count, a missing artifact, or a roll outside the ten"),
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
        if not reps:
            return None
        arms[arm] = {"replicates": len(reps),
                     "diagonal": [statistics.fmean(r["final_per_task"]) for r in reps],
                     "forgetting": [r["mean_forgetting"] for r in reps]}
    return {"artifact": path.name, "anchor": anchor, "arms": arms}


def reading(card9: Path = CARD9, rolls: dict = ROLLS) -> dict:
    out = {"ok": True, "reason": None, "card": None, "revision9": {}, "method": {}, "rolls": {}}
    base = load(card9)
    if not base:
        return {**out, "ok": False, "reason": f"{card9} is absent, so revision 9 is not on disk"}
    old = base.get("card") or {}
    card = copy.deepcopy(old)
    card["revision"] = REVISION
    out["revision9"] = {k: v for k, v in old.items() if k not in NEW}

    for label, path in rolls.items():
        family = label.split("/")[0]
        anchor = FAMILIES.get(family)
        if anchor is None:
            return {**out, "ok": False, "reason": f"{label} names no family the clause knows"}
        got = _roll(path, anchor)
        if got is None:
            return {**out, "ok": False, "reason": f"{path} is absent or carries no {anchor} arm"}
        arms = got["arms"]
        out["rolls"][label] = {
            "artifact": got["artifact"], "anchor": anchor, "replicates": arms[BASELINE]["replicates"],
            "accuracy": _paired(arms[BUFFER]["diagonal"], arms[anchor]["diagonal"]),
            "forgetting": _paired(arms[BUFFER]["forgetting"], arms[anchor]["forgetting"])}
    acc = {l: v["accuracy"]["mean"] for l, v in out["rolls"].items()}
    sig = {l: v["accuracy"]["sigma"] for l, v in out["rolls"].items()}
    frg = {l: v["forgetting"]["mean"] for l, v in out["rolls"].items()}
    families = {}
    for label in out["rolls"]:
        families[label.split("/")[0]] = families.get(label.split("/")[0], 0) + 1
    card["method"] = {
        "artifact": [out["rolls"][l]["artifact"] for l in out["rolls"]],
        "rolls": len(out["rolls"]),
        "families": families,
        "buffer": BUFFER,
        "anchors": dict(FAMILIES),
        "accuracy": acc, "accuracy_sigma": sig,
        "accuracy_min": min(acc.values()), "accuracy_max": max(acc.values()),
        "span": max(acc.values()) - min(acc.values()),
        "least_sigma": min(abs(s) for s in sig.values()),
        "greatest_sigma": max(abs(s) for s in sig.values()),
        "forgetting": frg,
    }
    out["method"] = dict(card["method"])
    out["card"] = card
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the clause is read from is absent"}
                for c in CLAIMS]
    card, m = r["card"], r["method"]
    same = {k: (card.get(k) == v) for k, v in r["revision9"].items()}
    j1 = {"id": "DA1",
          "measured": f"the revision-9 card's {len(same)} fields against the revision-10 card: "
                      f"{len(same) - sum(1 for v in same.values() if not v)} equal, with the revision now "
                      f"{card.get('revision')}",
          "verdict": f"MET -- the ninth revision is carried unchanged in all {len(same)} fields it does not rewrite" if
                     (all(same.values()) and card.get("revision") == REVISION) else
                     f"FALSIFIER FIRED -- { {k: v for k, v in same.items() if not v} } differs"}
    want = {l: {"accuracy": v["accuracy"]["mean"], "accuracy_sigma": v["accuracy"]["sigma"],
                "forgetting": v["forgetting"]["mean"]} for l, v in r["rolls"].items()}
    bad2 = {}
    for label, got in want.items():
        for key, field in (("accuracy", "accuracy"), ("accuracy_sigma", "accuracy_sigma"),
                           ("forgetting", "forgetting")):
            carried = m[key].get(label)
            if carried is None or abs(carried - got[field]) > TOL:
                bad2[f"{label}/{key}"] = (carried, got[field])
    derived = {"accuracy_min": min(want[l]["accuracy"] for l in want),
               "accuracy_max": max(want[l]["accuracy"] for l in want),
               "least_sigma": min(abs(want[l]["accuracy_sigma"]) for l in want),
               "greatest_sigma": max(abs(want[l]["accuracy_sigma"]) for l in want)}
    derived["span"] = derived["accuracy_max"] - derived["accuracy_min"]
    for key, value in derived.items():
        if abs(m[key] - value) > TOL:
            bad2[key] = (m[key], value)
    j2 = {"id": "DA2",
          "measured": f"the clause's ten contrasts run {m['accuracy_min']:+.4f} to {m['accuracy_max']:+.4f} at "
                      f"{m['least_sigma']:.2f} to {m['greatest_sigma']:.2f} sigma and span {m['span']:.4f}",
          "verdict": "MET -- the clause's numbers are the ten rolls' own, forgetting included" if not bad2 else
                     f"FALSIFIER FIRED -- {bad2}"}
    off = {l: (round(v["accuracy"]["mean"], 4), round(v["accuracy"]["sigma"], 2)) for l, v in r["rolls"].items()
           if not (v["accuracy"]["mean"] > 0 and abs(v["accuracy"]["sigma"]) >= SIGMA)}
    j3 = {"id": "DA3",
          "measured": f"the ten contrasts at their sigmas are "
                      f"{ {l: (round(v['accuracy']['mean'], 4), round(abs(v['accuracy']['sigma']), 2)) for l, v in r['rolls'].items()} }",
          "verdict": f"MET -- the buffer is ahead at two sigma or more on all {len(r['rolls'])} rolls" if not off else
                     f"FALSIFIER FIRED -- {off}"}
    least, span = m["least_sigma"], m["span"]
    j4 = {"id": "DA4",
          "measured": f"the clause's least sigma is {least:.2f} and its span {span:.4f}",
          "verdict": f"MET -- the weakest instance is {least:.2f} sigma and the ten span {span:.4f}" if
                     (least >= LEAST_SIGMA and span <= SPAN) else
                     f"FALSIFIER FIRED -- least {least:.2f}, span {span:.4f}" if
                     (least < LEAST_FLOOR or span >= SPAN_FIRES) else
                     f"NULL -- least {least:.2f}, span {span:.4f}, between the bars"}
    named = (m["buffer"] == BUFFER and m["anchors"] == FAMILIES and m["rolls"] == len(r["rolls"]) and
             m["families"] == {"biological": 7, "matched_random": 3})
    artifacts_ok = sorted(m["artifact"]) == sorted(v["artifact"] for v in r["rolls"].values())
    j5 = {"id": "DA5",
          "measured": f"the clause names {m['buffer']} as the buffer, {m['anchors']} as the anchors, "
                      f"{m['rolls']} rolls in {m['families']}, {artifacts_ok} artifacts",
          "verdict": "MET -- the clause names the buffer, the two anchors, the ten rolls and their artifacts" if
                     (named and artifacts_ok) else
                     f"FALSIFIER FIRED -- named {named}, artifacts {artifacts_ok}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the game card, revision 10 ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    card = r["card"]
    print(f"   {card.get('name')}, revision {card.get('revision')}, read 2026-10-07")
    print(f"\n   clauses:    {len(card)} fields, the new one being `method`")
    m = r["method"]
    print(f"\n   the method clause, over {m['rolls']} rolls of the card's own world:")
    print(f"\n   {'family':>15} {'roll':>16} {'anchor':>15} {'contrast':>10} {'sigma':>7} {'forgetting':>11}")
    for label, v in r["rolls"].items():
        fam, roll = label.split("/")
        print(f"   {fam:>15} {roll:>16} {v['anchor']:>15} {v['accuracy']['mean']:+10.4f} "
              f"{abs(v['accuracy']['sigma']):7.2f} {v['forgetting']['mean']:+11.4f}")
    print(f"\n   the clause: {m['buffer']} over {m['anchors']}, {m['accuracy_min']:+.4f} to {m['accuracy_max']:+.4f} "
          f"at {m['least_sigma']:.2f} to {m['greatest_sigma']:.2f} sigma, span {m['span']:.4f}")
    print("\n== the registered claims, DA1-DA5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e450` wrote revision 9, the width clause; `e453` then read the method contrast across all ten rolls")
    print("    of this world and this is what the ten put in the card)")
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
