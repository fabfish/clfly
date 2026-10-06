"""E445 -- the game card, revision 8: the ledger clause, and which of the two arms' effects is there at all.

The card carries the benchmark's clauses and each revision has added one. `e434` wrote revision 7, the **parameters**
clause: where each arm spends its movement. Since then `e437` to `e444` have driven the card's own world **four times**
-- as-built, under the rotated order, with the environment redrawn and with the decoder redrawn -- and what those four
rolls say together has never been written into the card, though `e438` fired a claim on exactly that (*a card that says
`the buffer's gain` should say which arm it means*) and `e444` closed by reading all four at once.

**This unit writes revision 8.** One clause is added, the **ledger** clause, and every other field is checked equal to
`e434`'s card rather than quoted. The clause carries what the four rolls of the card's own world put in it: the buffer's
three-position gain over the baseline on each roll with its first-over-last margin, the anchor's mean diagonal with the
sigma that does *not* clear two, and the anchor's newest-task cost with the sigma that does. Five claims, registered
before this unit's pass over the four rolls.

- **BW1 -- and the seventh revision is carried unchanged where it is not rewritten.** Every field of `e434`'s card except
  the revision and the new clause is equal to the revision-7 card, with the revision now **8**. **Falsifier**: any other
  field differing, or the revision not 8; refused when the revision-7 artifact is absent.
- **BW2 -- and the clause's buffer half is the four rolls'.** The buffer's mean diagonal over the baseline, the sigma of
  that contrast, the four rolls' first-over-last margins and the margin's range all equal the four rolls recomputed
  here. **Falsifier**: any number disagreeing by more than a thousandth of a point; refused when a roll is absent.
- **BW3 -- and its anchor half is the four rolls' too.** The anchor's mean diagonal over the baseline, the sigma of that
  contrast, its four newest-task costs and that cost's range all equal the recomputation. **Falsifier**: any number
  disagreeing; refused when a roll is absent.
- **BW4 -- and the clause's reading holds on every one of the four.** On each roll the buffer's mean diagonal over the
  baseline resolves at **two** sigma or more; on none of them does the anchor's reach two sigma; and on every one the
  anchor's newest-task cost is negative and resolves at two sigma or more. **Falsifier**: any roll where any of the
  three fails.
- **BW5 -- and the clause names the arms and the rolls it was measured on.** It carries `replay` as the buffer,
  `ewc-block` as the anchor, the four rolls' artifacts, the count **4**, and a margin range that is those four margins'
  own. **Falsifier**: another arm or another count, a missing artifact, or a range that is not the four rolls' own.

**What it can do beyond that.** It is the card's own statement of the one thing this line has measured on the card's
world that is not a draw: which of the two arms' whole-diagonal effects is there. If a reader takes the `order` clause
and this one together they see that the position effect is the sequence's, that the buffer's ledger survives a redraw of
either kind, and that the anchor's standing does not survive anything because it is not there.

**What it cannot do.** *Four rolls*: four points and not a distribution, so the ranges the clause carries are four rolls'
own and not intervals. *And one world's card*: the four rolls are the card's own world under three manipulations and not
other worlds. *And a clause is not a result*: BW1 shows revision 7 survives into revision 8 and not that revision 7 was
right, and BW2 and BW3 show the clause agrees with the four rolls and not that the four rolls should be believed.
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
CARD7 = Path("runs/e434_the_game_card_revision_seven.json")
#: the four rolls of the card's own world the clause is read from, in the order the line drove them
ROLLS = {
    "as_built": Path("runs/e438_earned_label_three_arms_20reps.json"),
    "rotated": Path("runs/e441_earned_label_anchor_order102_20reps.json"),
    "env_redrawn": Path("runs/e443_earned_label_worldseed1_20reps.json"),
    "decoder_redrawn": Path("runs/e444_earned_label_readoutseed1_20reps.json"),
}
BASELINE = "naive"
BUFFER = "replay"
ANCHOR = "ewc-block"
REVISION = 8
NEW = ("revision", "ledger")
MIN_REPS = 20
N_TASKS = 3
SIGMA = 2.0
TOL = 0.002
CLAIMS = (
    ("BW1", "and the seventh revision is carried unchanged where it is not rewritten",
     "Every field of `e434`'s card except the revision and the new clause is equal to the revision-7 card, with the "
     "revision now 8",
     "falsifier: any other field differing, or the revision not 8; refused when `e434`'s artifact is absent"),
    ("BW2", "and the clause's buffer half is the four rolls'",
     "The buffer's mean diagonal over the baseline, the sigma of that contrast, the four rolls' first-over-last margins "
     "and the margin's range all equal the four rolls recomputed",
     "falsifier: any number disagreeing by more than a thousandth of a point; refused when a roll is absent"),
    ("BW3", "and its anchor half is the four rolls' too",
     "The anchor's mean diagonal over the baseline, the sigma of that contrast, its four newest-task costs and that "
     "cost's range all equal the recomputation",
     "falsifier: any number disagreeing; refused when a roll is absent"),
    ("BW4", "and the clause's reading holds on every one of the four",
     "On each roll the buffer's mean diagonal over the baseline resolves at two sigma or more; on none does the "
     "anchor's reach two sigma; and on every one the anchor's newest-task cost is negative and resolves at two sigma or "
     "more",
     "falsifier: any roll where any of the three fails"),
    ("BW5", "and the clause names the arms and the rolls it was measured on",
     "It carries replay as the buffer, ewc-block as the anchor, the four rolls' artifacts, the count 4, and a margin "
     "range that is those four margins' own",
     "falsifier: another arm or another count, a missing artifact, or a range that is not the four rolls' own"),
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
    return {"artifact": path.name, "arms": arms}


def _roll_numbers(got: dict) -> dict:
    arms = got["arms"]
    buffer_diag = _paired(arms[BUFFER]["diagonal"], arms[BASELINE]["diagonal"])
    anchor_diag = _paired(arms[ANCHOR]["diagonal"], arms[BASELINE]["diagonal"])
    anchor_last = _paired(arms[ANCHOR]["last"], arms[BASELINE]["last"])
    gain = [arms[BUFFER]["final"][k] - arms[BASELINE]["final"][k] for k in range(N_TASKS)]
    return {"replicates": arms[BASELINE]["replicates"],
            "buffer_mean": buffer_diag["mean"], "buffer_sigma": buffer_diag["sigma"],
            "buffer_gain": gain, "margin": gain[0] - gain[-1],
            "anchor_mean": anchor_diag["mean"], "anchor_sigma": anchor_diag["sigma"],
            "anchor_last": anchor_last["mean"], "anchor_last_sigma": anchor_last["sigma"]}


def reading(card7: Path = CARD7, rolls: dict = ROLLS) -> dict:
    out = {"ok": True, "reason": None, "card": None, "revision7": {}, "ledger": {}, "rolls": {}}
    base = load(card7)
    if not base:
        return {**out, "ok": False, "reason": f"{card7} is absent, so revision 7 is not on disk"}
    old = base.get("card") or {}
    card = copy.deepcopy(old)
    card["revision"] = REVISION
    out["revision7"] = {k: v for k, v in old.items() if k not in NEW}

    numbers = {}
    for label, path in rolls.items():
        got = _roll(path)
        if got is None:
            return {**out, "ok": False, "reason": f"{path} is absent or carries no arm, so the clause has no reading"}
        numbers[label] = _roll_numbers(got)
        out["rolls"][label] = {"artifact": got["artifact"], **numbers[label]}
    buffers = [numbers[l]["buffer_mean"] for l in numbers]
    b_sigmas = [numbers[l]["buffer_sigma"] for l in numbers]
    margins = {l: numbers[l]["margin"] for l in numbers}
    anchors = [numbers[l]["anchor_mean"] for l in numbers]
    a_sigmas = [numbers[l]["anchor_sigma"] for l in numbers]
    lasts = {l: numbers[l]["anchor_last"] for l in numbers}
    last_sigmas = [abs(numbers[l]["anchor_last_sigma"]) for l in numbers]
    card["ledger"] = {
        "artifact": [out["rolls"][l]["artifact"] for l in numbers],
        "rolls": len(numbers),
        "buffer": BUFFER,
        "anchor": ANCHOR,
        "buffer_mean": {"min": min(buffers), "max": max(buffers)},
        "buffer_least_sigma": min(abs(s) for s in b_sigmas),
        "buffer_margin": margins,
        "buffer_margin_min": min(margins.values()),
        "buffer_margin_max": max(margins.values()),
        "anchor_mean": {"min": min(anchors), "max": max(anchors)},
        "anchor_greatest_sigma": max(abs(s) for s in a_sigmas),
        "anchor_last": lasts,
        "anchor_last_min": min(lasts.values()),
        "anchor_last_max": max(lasts.values()),
        "anchor_last_least_sigma": min(last_sigmas),
    }
    out["ledger"] = dict(card["ledger"])
    out["card"] = card
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the clause is read from is absent"}
                for c in CLAIMS]
    card, led = r["card"], r["ledger"]
    same = {k: (card.get(k) == v) for k, v in r["revision7"].items()}
    j1 = {"id": "BW1",
          "measured": f"the revision-7 card's {len(same)} fields against the revision-8 card: "
                      f"{len(same) - sum(1 for v in same.values() if not v)} equal, with the revision now "
                      f"{card.get('revision')}",
          "verdict": f"MET -- the seventh revision is carried unchanged in all {len(same)} fields it does not rewrite" if
                     (all(same.values()) and card.get("revision") == REVISION) else
                     f"FALSIFIER FIRED -- { {k: v for k, v in same.items() if not v} } differs"}
    recomputed = {"buffer_mean_min": min(v["buffer_mean"] for v in r["rolls"].values()),
                  "buffer_mean_max": max(v["buffer_mean"] for v in r["rolls"].values()),
                  "buffer_least_sigma": min(abs(v["buffer_sigma"]) for v in r["rolls"].values()),
                  "buffer_margin_min": min(v["margin"] for v in r["rolls"].values()),
                  "buffer_margin_max": max(v["margin"] for v in r["rolls"].values())}
    carried = {"buffer_mean_min": led["buffer_mean"]["min"], "buffer_mean_max": led["buffer_mean"]["max"],
               "buffer_least_sigma": led["buffer_least_sigma"], "buffer_margin_min": led["buffer_margin_min"],
               "buffer_margin_max": led["buffer_margin_max"]}
    bad2 = {k: (carried[k], recomputed[k]) for k in carried if abs(carried[k] - recomputed[k]) > TOL}
    bad2.update({f"margin/{l}": (led["buffer_margin"].get(l), v["margin"]) for l, v in r["rolls"].items()
                 if l not in led["buffer_margin"] or abs(led["buffer_margin"][l] - v["margin"]) > TOL})
    j2 = {"id": "BW2",
          "measured": f"the clause's buffer mean diagonal is {led['buffer_mean']['min']:+.4f} to "
                      f"{led['buffer_mean']['max']:+.4f} at least {led['buffer_least_sigma']:.2f} sigma, its margins "
                      f"{ {l: round(v, 4) for l, v in led['buffer_margin'].items()} }",
          "verdict": "MET -- the clause's buffer half is the four rolls' own numbers" if not bad2 else
                     f"FALSIFIER FIRED -- {bad2}"}
    recomputed3 = {"anchor_mean_min": min(v["anchor_mean"] for v in r["rolls"].values()),
                   "anchor_mean_max": max(v["anchor_mean"] for v in r["rolls"].values()),
                   "anchor_greatest_sigma": max(abs(v["anchor_sigma"]) for v in r["rolls"].values()),
                   "anchor_last_min": min(v["anchor_last"] for v in r["rolls"].values()),
                   "anchor_last_max": max(v["anchor_last"] for v in r["rolls"].values()),
                   "anchor_last_least_sigma": min(abs(v["anchor_last_sigma"]) for v in r["rolls"].values())}
    carried3 = {"anchor_mean_min": led["anchor_mean"]["min"], "anchor_mean_max": led["anchor_mean"]["max"],
                "anchor_greatest_sigma": led["anchor_greatest_sigma"], "anchor_last_min": led["anchor_last_min"],
                "anchor_last_max": led["anchor_last_max"], "anchor_last_least_sigma": led["anchor_last_least_sigma"]}
    bad3 = {k: (carried3[k], recomputed3[k]) for k in carried3 if abs(carried3[k] - recomputed3[k]) > TOL}
    bad3.update({f"last/{l}": (led["anchor_last"].get(l), v["anchor_last"]) for l, v in r["rolls"].items()
                 if l not in led["anchor_last"] or abs(led["anchor_last"][l] - v["anchor_last"]) > TOL})
    j3 = {"id": "BW3",
          "measured": f"the clause's anchor mean diagonal is {led['anchor_mean']['min']:+.4f} to "
                      f"{led['anchor_mean']['max']:+.4f} at most {led['anchor_greatest_sigma']:.2f} sigma, its "
                      f"newest-task costs { {l: round(v, 4) for l, v in led['anchor_last'].items()} } at least "
                      f"{led['anchor_last_least_sigma']:.2f} sigma",
          "verdict": "MET -- the clause's anchor half is the four rolls' own numbers" if not bad3 else
                     f"FALSIFIER FIRED -- {bad3}"}
    fails = {}
    for label, v in r["rolls"].items():
        if abs(v["buffer_sigma"]) < SIGMA:
            fails[f"{label}/buffer"] = v["buffer_sigma"]
        if abs(v["anchor_sigma"]) >= SIGMA:
            fails[f"{label}/anchor"] = v["anchor_sigma"]
        if not (v["anchor_last"] < 0 and abs(v["anchor_last_sigma"]) >= SIGMA):
            fails[f"{label}/anchor_last"] = (v["anchor_last"], v["anchor_last_sigma"])
    j4 = {"id": "BW4",
          "measured": f"the buffer's mean-diagonal sigmas are "
                      f"{ {l: round(abs(v['buffer_sigma']), 2) for l, v in r['rolls'].items()} }, the anchor's "
                      f"{ {l: round(abs(v['anchor_sigma']), 2) for l, v in r['rolls'].items()} }, and its "
                      f"newest-task sigmas { {l: round(abs(v['anchor_last_sigma']), 2) for l, v in r['rolls'].items()} }",
          "verdict": "MET -- the buffer's standing resolves on all four rolls, the anchor's on none, and the anchor's "
                     "newest-task price on all four" if not fails else f"FALSIFIER FIRED -- {fails}"}
    named = (led["buffer"] == BUFFER and led["anchor"] == ANCHOR and led["rolls"] == len(r["rolls"]))
    artifacts_ok = sorted(led["artifact"]) == sorted(v["artifact"] for v in r["rolls"].values())
    range_ok = (abs(led["buffer_margin_min"] - min(v["margin"] for v in r["rolls"].values())) <= TOL and
                abs(led["buffer_margin_max"] - max(v["margin"] for v in r["rolls"].values())) <= TOL)
    j5 = {"id": "BW5",
          "measured": f"the clause names {led['buffer']} as the buffer and {led['anchor']} as the anchor over "
                      f"{led['rolls']} rolls, {artifacts_ok} artifacts, its margin range "
                      f"{led['buffer_margin_min']:.4f} to {led['buffer_margin_max']:.4f}",
          "verdict": "MET -- the clause names the arms, the four rolls' artifacts and their own margin range" if
                     (named and artifacts_ok and range_ok) else
                     f"FALSIFIER FIRED -- named {named}, artifacts {artifacts_ok}, range {range_ok}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the game card, revision 8 ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    card = r["card"]
    print(f"   {card.get('name')}, revision {card.get('revision')}, read 2026-10-06")
    print(f"\n   arms:       {card.get('arms')}")
    print(f"   absent:     {card.get('absent')}")
    print("\n   the card's own world's ledger, over the four rolls this line has driven:")
    print(f"\n   {'roll':>16} {'buffer mean':>12} {'sigma':>7} {'margin':>9} {'anchor mean':>12} {'sigma':>7} "
          f"{'its last':>10} {'sigma':>7}")
    for label, v in r["rolls"].items():
        print(f"   {label:>16} {v['buffer_mean']:+12.4f} {abs(v['buffer_sigma']):7.2f} {v['margin']:+9.4f} "
              f"{v['anchor_mean']:+12.4f} {abs(v['anchor_sigma']):7.2f} {v['anchor_last']:+10.4f} "
              f"{abs(v['anchor_last_sigma']):7.2f}")
    led = r["ledger"]
    print(f"\n   ledger: over {led['rolls']} rolls of {[Path(a).name for a in led['artifact']]}")
    print(f"      the {led['buffer']}     {led['buffer_mean']['min']:+.4f} to {led['buffer_mean']['max']:+.4f} "
          f"at least {led['buffer_least_sigma']:.2f} sigma, margins {led['buffer_margin_min']:.4f} to "
          f"{led['buffer_margin_max']:.4f}")
    print(f"      the {led['anchor']}  {led['anchor_mean']['min']:+.4f} to {led['anchor_mean']['max']:+.4f} "
          f"at most {led['anchor_greatest_sigma']:.2f} sigma, newest task {led['anchor_last_min']:+.4f} to "
          f"{led['anchor_last_max']:+.4f} at least {led['anchor_last_least_sigma']:.2f} sigma")
    print("\n== the registered claims, BW1-BW5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e434` wrote revision 7, the parameters clause; `e437` to `e444` then drove the card's own world four")
    print("    times, and this is what those four rolls put in the card)")
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
