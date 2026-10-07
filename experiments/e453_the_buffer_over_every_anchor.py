"""E453 -- the buffer over every anchor: the corpus's other headline across the ten rolls of the card's world.

`e276` read the corpus's **method** contrast -- `replay` against the penalty -- at **3.30** to **11.84** sigma on the
state read-out, and the register has quoted it ever since. On the card's world the line has since driven **ten** rolls:
seven that carry `naive`, `ewc-block` and `replay`, and three that carry `naive`, `ewc-block-rand` and `replay`. Each
of the ten moves **one** thing -- nothing, the order, the environment's draw, the decoder's draw, or the world's width --
and no unit has read the method contrast across them. `e438` read it at **10.89** sigma as-built and each later unit read
it inside its own roll; what the ten say together has not been said.

**This unit reads all ten.** No training and no probe: each roll's replicate lists are paired, the buffer's mean diagonal
over each anchor's is taken with its sigma, and the same contrast on mean forgetting beside it. Five claims, registered
before this unit's pass over the ten rolls.

- **CZ1 -- and the ledger is carried.** The seven biological rolls carry `naive`, `ewc-block` and `replay` at **20**
  replicates each, the three matched-random rolls carry `naive`, `ewc-block-rand` and `replay`, and every roll records
  the manipulation that distinguishes it. **Falsifier**: any arm missing or short, or a roll absent.
- **CZ2 -- and the buffer is ahead of the biological anchor on every one of the seven.** The paired mean-diagonal
  contrast is positive at **two** sigma or more on each. **Falsifier**: any roll where it is not.
- **CZ3 -- and ahead of the matched-random anchor on every one of the three.** **Falsifier**: any roll where it is not.
- **CZ4 -- and the smallest of the ten is well clear of the bar.** The least sigma across the ten is at least **five**.
  **Falsifier**: under **two**; **null**: between. *`e276`'s range was 3.30 to 11.84 on another read-out; this asks
  whether the contrast's weakest instance on this world is anywhere near the bar.*
- **CZ5 -- and the size of the contrast is not the manipulation's.** The span of the ten mean-diagonal contrasts is at
  most **0.10**. **Falsifier**: **0.20** or more; **null**: between. *The ten manipulations are an order's, two draws'
  and a width's, and `e448` and `e449` found those move the **anchors'** effects; this asks whether they move the
  **buffer's advantage over them**.*

**What it can do beyond that.** It is thread (a) answered on this world rather than on the state read-out: if the buffer
is ahead at two sigma on all ten and its weakest instance is well clear of the bar, then the corpus's method contrast is
the card's **robust** headline while its basis contrast is the null one -- which would be the sentence the card's own
`ledger` and `width` clauses together imply and neither states. If instead some roll comes within the bar, then the
method contrast's *size* is the manipulation's and `e276`'s range is reproduced here for a reason.

**What it cannot do.** *Ten rolls of one world*: the card's own, so other worlds are not in the reading and neither are
the corpus's other suites, where `e276` took its three configurations. *And one pair per roll*: each roll pairs the
buffer against one anchor, so the two anchors are compared through the buffer and not directly -- `e439`, `e447` and
`e451` do that and found the two **0.0042** to **0.0101** apart. *And one arm pair*: `naive` and an anchor, so the
penalty's strength and the frozen controls are not in it. *And two same-seed runs*: each contrast pairs replicate against
replicate by the runner's `seed0 + 100 * r` schedule, which is a same-seed pairing and not the same run.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the seven rolls carrying the biological anchor, by the manipulation each moves
BIO = {
    "as_built": Path("runs/e438_earned_label_three_arms_20reps.json"),
    "rotated": Path("runs/e441_earned_label_anchor_order102_20reps.json"),
    "env_redrawn": Path("runs/e443_earned_label_worldseed1_20reps.json"),
    "decoder_redrawn": Path("runs/e444_earned_label_readoutseed1_20reps.json"),
    "reversed": Path("runs/e446_earned_label_anchor_reverse_20reps.json"),
    "wide_16": Path("runs/e448_earned_label_worlddims16_20reps.json"),
    "narrow_4": Path("runs/e449_earned_label_worlddims4_20reps.json"),
}
#: the three carrying the size-matched random partition
RAND = {
    "as_built": Path("runs/e439_earned_label_rand_20reps.json"),
    "reversed": Path("runs/e447_earned_label_rand_reverse_20reps.json"),
    "narrow_4": Path("runs/e451_earned_label_rand_worlddims4_20reps.json"),
}
BASELINE = "naive"
BUFFER = "replay"
BIO_ANCHOR = "ewc-block"
RAND_ANCHOR = "ewc-block-rand"
#: the fields that say which manipulation a roll is
MANIPULATIONS = ("task_order", "loop_seed", "readout_seed", "loop_world_dims")
N_TASKS = 3
MIN_REPS = 20
SIGMA = 2.0
LEAST_SIGMA = 5.0
LEAST_FLOOR = 2.0
SPAN = 0.10
SPAN_FIRES = 0.20
CLAIMS = (
    ("CZ1", f"and the ledger is carried, at {MIN_REPS} replicates",
     "The seven biological rolls carry naive, ewc-block and replay at twenty replicates each, the three matched-random "
     "rolls carry naive, ewc-block-rand and replay, and every roll records the manipulation that distinguishes it",
     "falsifier: any arm missing or short, or a roll absent"),
    ("CZ2", f"and the buffer is ahead of the biological anchor on every one of the seven, at {SIGMA:.0f} sigma",
     "The paired mean-diagonal contrast is positive at two sigma or more on each",
     "falsifier: any roll where it is not"),
    ("CZ3", f"and ahead of the matched-random anchor on every one of the three, at {SIGMA:.0f} sigma",
     "The paired mean-diagonal contrast is positive at two sigma or more on each",
     "falsifier: any roll where it is not"),
    ("CZ4", f"and the smallest of the ten is well clear of the bar, at least {LEAST_SIGMA:.0f} sigma",
     "The least sigma across the ten is at least five",
     f"falsifier: under {LEAST_FLOOR:.2f}; null: between"),
    ("CZ5", f"and the size of the contrast is not the manipulation's, within {SPAN:.2f}",
     "The span of the ten mean-diagonal contrasts is at most 0.10",
     f"falsifier: {SPAN_FIRES:.2f} or more; null: between"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _arm(got: dict) -> dict | None:
    reps = (got or {}).get("replicates") or []
    if not reps:
        return None
    return {"replicates": len(reps),
            "final": [statistics.fmean([r["final_per_task"][k] for r in reps]) for k in range(N_TASKS)],
            "diagonal": [statistics.fmean(r["final_per_task"]) for r in reps],
            "forgetting": [r["mean_forgetting"] for r in reps]}


def _roll(path: Path, anchor: str) -> dict | None:
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    arms = {}
    for arm in (BASELINE, anchor, BUFFER):
        if arm not in methods:
            return None
        got = _arm(methods[arm])
        if got is None:
            return None
        arms[arm] = got
    cfg = doc.get("config") or {}
    return {"artifact": path.name, "anchor": anchor, "arms": arms,
            "replicates": _replicates(arms),
            "manipulation": {k: cfg.get(k) for k in MANIPULATIONS}}


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def _replicates(arms: dict) -> int:
    return min(v["replicates"] for v in arms.values())


def reading(bio: dict = BIO, rand: dict = RAND) -> dict:
    out = {"ok": True, "reason": None, "rolls": {}, "cells": [], "spans": {}}
    for family, rolls, anchor in (("biological", bio, BIO_ANCHOR), ("matched_random", rand, RAND_ANCHOR)):
        for label, path in rolls.items():
            got = _roll(path, anchor)
            if got is None:
                return {**out, "ok": False, "reason": f"{path} is absent or carries no {anchor} arm"}
            cell = {"family": family, "roll": label, "artifact": got["artifact"], "anchor": anchor,
                    "manipulation": got["manipulation"],
                    "replicates": _replicates(got["arms"]),
                    "accuracy": _paired(got["arms"][BUFFER]["diagonal"], got["arms"][anchor]["diagonal"]),
                    "forgetting": _paired(got["arms"][BUFFER]["forgetting"], got["arms"][anchor]["forgetting"]),
                    "buffer_gain": [got["arms"][BUFFER]["final"][k] - got["arms"][anchor]["final"][k]
                                    for k in range(N_TASKS)]}
            out["rolls"][f"{family}/{label}"] = got
            out["cells"].append(cell)
    acc = [c["accuracy"]["mean"] for c in out["cells"]]
    sig = [abs(c["accuracy"]["sigma"]) for c in out["cells"]]
    out["spans"] = {
        "cells": len(out["cells"]), "biological": sum(1 for c in out["cells"] if c["family"] == "biological"),
        "matched_random": sum(1 for c in out["cells"] if c["family"] == "matched_random"),
        "replicates": sorted({c["replicates"] for c in out["cells"]}),
        "accuracy": {f"{c['family']}/{c['roll']}": c["accuracy"]["mean"] for c in out["cells"]},
        "sigma": {f"{c['family']}/{c['roll']}": c["accuracy"]["sigma"] for c in out["cells"]},
        "accuracy_min": min(acc), "accuracy_max": max(acc), "span": max(acc) - min(acc),
        "least_sigma": min(sig), "greatest_sigma": max(sig),
        "forgetting": {f"{c['family']}/{c['roll']}": c["forgetting"]["mean"] for c in out["cells"]},
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no such arm"}
                for c in CLAIMS]
    s = r["spans"]
    thin = {k: v["replicates"] for k, v in r["rolls"].items()
            if min(a["replicates"] for a in v["arms"].values()) < MIN_REPS}
    anchors_ok = all(v["anchor"] in v["arms"] for v in r["rolls"].values())
    j1 = {"id": "CZ1",
          "measured": f"{s['cells']} rolls -- {s['biological']} biological and {s['matched_random']} matched-random -- "
                      f"at {s['replicates']} replicates, with the manipulations "
                      f"{ {c['family'] + '/' + c['roll']: c['manipulation'] for c in r['cells']} }",
          "verdict": f"MET -- all {s['cells']} rolls carry the baseline, the buffer and their anchor at "
                     f"{s['replicates']} replicates" if (not thin and anchors_ok) else
                     f"FALSIFIER FIRED -- thin {thin}, anchors {anchors_ok}"}
    bio_off = {f"{c['roll']}": round(c["accuracy"]["mean"], 4) for c in r["cells"]
               if c["family"] == "biological" and not (c["accuracy"]["mean"] > 0 and
                                                       abs(c["accuracy"]["sigma"]) >= SIGMA)}
    j2 = {"id": "CZ2",
          "measured": f"the buffer's mean diagonal over the biological anchor is "
                      f"{ {c['roll']: round(c['accuracy']['mean'], 4) for c in r['cells'] if c['family'] == 'biological'} }"
                      f" at { {c['roll']: round(abs(c['accuracy']['sigma']), 2) for c in r['cells'] if c['family'] == 'biological'} }"
                      f" sigma",
          "verdict": f"MET -- the buffer is ahead at two sigma or more on all {s['biological']} biological rolls" if
                     not bio_off else f"FALSIFIER FIRED -- {bio_off}"}
    rand_off = {f"{c['roll']}": round(c["accuracy"]["mean"], 4) for c in r["cells"]
                if c["family"] == "matched_random" and not (c["accuracy"]["mean"] > 0 and
                                                            abs(c["accuracy"]["sigma"]) >= SIGMA)}
    j3 = {"id": "CZ3",
          "measured": f"the buffer's mean diagonal over the matched-random anchor is "
                      f"{ {c['roll']: round(c['accuracy']['mean'], 4) for c in r['cells'] if c['family'] == 'matched_random'} }"
                      f" at { {c['roll']: round(abs(c['accuracy']['sigma']), 2) for c in r['cells'] if c['family'] == 'matched_random'} }"
                      f" sigma",
          "verdict": f"MET -- the buffer is ahead at two sigma or more on all {s['matched_random']} matched-random "
                     f"rolls" if not rand_off else f"FALSIFIER FIRED -- {rand_off}"}
    least = s["least_sigma"]
    j4 = {"id": "CZ4",
          "measured": f"the ten contrasts run {s['accuracy_min']:+.4f} to {s['accuracy_max']:+.4f}, their sigmas "
                      f"{least:.2f} to {s['greatest_sigma']:.2f}",
          "verdict": f"MET -- the weakest of the ten is resolved at {least:.2f} sigma, well clear of the bar" if
                     least >= LEAST_SIGMA else
                     f"FALSIFIER FIRED -- the least sigma is {least:.2f}" if least < LEAST_FLOOR else
                     f"NULL -- the least sigma is {least:.2f}, between {LEAST_FLOOR:.2f} and {LEAST_SIGMA:.2f}"}
    span = s["span"]
    j5 = {"id": "CZ5",
          "measured": f"the ten contrasts span {span:.4f}, from {s['accuracy_min']:+.4f} to {s['accuracy_max']:+.4f}",
          "verdict": f"MET -- the size of the contrast is not the manipulation's, a span of {span:.4f}" if
                     span <= SPAN else
                     f"FALSIFIER FIRED -- the span is {span:.4f}" if span >= SPAN_FIRES else
                     f"NULL -- the span is {span:.4f}, between {SPAN:.2f} and {SPAN_FIRES:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the buffer over every anchor ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source and the earned label, ten rolls, twenty replicates each")
    print(f"\n   {'family':>15} {'roll':>16} {'anchor':>15} {'order':>9} {'wd':>4} {'loopseed':>9} {'roseed':>7} "
          f"{'contrast':>10} {'sigma':>7} {'forgetting':>11}")
    for c in r["cells"]:
        m = c["manipulation"]
        print(f"   {c['family']:>15} {c['roll']:>16} {c['anchor']:>15} {str(m['task_order']):>9} "
              f"{str(m['loop_world_dims']):>4} {str(m['loop_seed']):>9} {str(m['readout_seed']):>7} "
              f"{c['accuracy']['mean']:+10.4f} {abs(c['accuracy']['sigma']):7.2f} "
              f"{c['forgetting']['mean']:+11.4f}")
    s = r["spans"]
    print(f"\n   the ten contrasts span {s['span']:.4f}; their least sigma is {s['least_sigma']:.2f} and their greatest "
          f"{s['greatest_sigma']:.2f}")
    print("\n== the registered claims, CZ1-CZ5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e276` read this contrast at 3.30 to 11.84 sigma on the state read-out and the register has quoted it")
    print("    since; this is the same contrast on every manipulation of the card's own world)")
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
