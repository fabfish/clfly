"""E417 -- the aid needs a plastic body: the corpus's frozen-body cells are worth nothing, at any head.

`e412` found the aid turns on between twenty and forty-five updates and registered the confound under it: *"the budget
is not the level -- the naive arm's own accuracy rises 0.2438 to 0.5191 along the same axis, so 'the aid goes with
what was learned' is a reading over a joint ramp and not an intervention."* `e413` repeated the caveat on six worlds.

**This unit reads the corpus's own control for it.** Every artifact that carries `naive` and `replay` records
`config.frozen_body`, and the corpus holds cells at both settings, so the ledger splits itself: the plastic cells, and
the cells whose recurrent weights never moved. No training, no probe. Five claims, registered before this unit's pass
over the corpus.

- **AN1 -- and the ledger is carried.** At least **150** cells with both arms at at least **5** replicates, and at
  least **3** of them recording a frozen body at **20** replicates. **Falsifier**: fewer cells, fewer than three
  frozen, or fewer replicates.
- **AN2 -- and on a frozen body the buffer is worth nothing.** Every frozen cell's accuracy gain is within **0.01** of
  zero. **Falsifier**: any above **0.05** in absolute value; **null**: between.
- **AN3 -- and its forgetting cut is exactly zero.** Every frozen cell's mean forgetting is unchanged by the buffer,
  to a thousandth. **Falsifier**: any cut above **0.005**.
- **AN4 -- and the plastic cells are worth a tenth.** At least one cell that does not record a frozen body, and whose
  naive accuracy is below **0.58**, gains at least **0.10** from the buffer. **Falsifier**: none.
- **AN5 -- and the head's own fitting does not move it.** The corpus holds two frozen-body cells of one configuration
  differing only in the head's learning rate, and their naive accuracies are at least **0.05** apart while their gains
  are within **0.02** of each other. **Falsifier**: the accuracies closer than 0.05, or the gains more than 0.02
  apart; **REFUSED** when either artifact is absent.

**What it can do beyond that.** It answers the confound `e412` and `e413` both registered, in the direction the
corpus can see: the aid's worth is not the head's accuracy. The corpus's three frozen-body cells read **0.4490**,
**0.6146** and **0.6455** of naive accuracy -- two of them above every one of the six earned-label worlds' -- and the
buffer moves them by **-0.0017**, **+0.0003** and **+0.0007** with a forgetting cut of exactly **0.0000** on all
three, while thirty cells below 0.58 of accuracy gain a tenth or more. And it separates the aid from the head's
fitting: `e375` and `e376` are one cell whose head's step size is ten times larger, worth **0.1965** of accuracy, and
the aid is worth **0.0024** more on the better-fitted one.

**What it cannot do.** *One control and three cells*: the corpus's frozen-body setting is three runs of the
earned-label world, so the split is that world's and not the benchmark's. *And the ledger is not a design*: the cells
are one configuration each, at five to forty replicates, and the plastic cells differ from the frozen ones in many
fields besides the body. *And the arms are the corpus's*: `replay` is the corpus's buffer and the penalty arms are not
in this reading. *And the metric is the corpus's*: `mean_forgetting` is the retention matrix's diagonal minus its last
row, which `e305` showed cannot see the part an arm never learned.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench import corpus
from clfly.bench.artifacts import write_json

ROOT = Path("runs")
REQUIRED = ("naive", "replay")
#: the corpus's frozen-body pair: one configuration whose head's step size is the only field that differs
FROZEN_PAIR = (Path("runs/e375_earned_label_frozenbody_cue8_actionsource_20reps.json"),
               Path("runs/e376_earned_label_frozenbody_lr03_cue8_actionsource_20reps.json"))
PAIR_FIELDS = ("circuit", "readout", "tasks", "env_draw")
RUN_FIELDS = ("json_out", "save_theta")
MIN_REPS = 5
FROZEN_REPS = 20
MIN_CELLS = 150
MIN_FROZEN = 3
ZERO = 0.01
ZERO_FIRES = 0.05
CUT_ZERO = 0.005
PLASTIC = 0.10
LEVEL = 0.58
LEVEL_SPLIT = 0.05
LEVEL_GAIN_DIFF = 0.02
CLAIMS = (
    ("AN1", f"and the ledger is carried, over at least {MIN_CELLS} cells and {MIN_FROZEN} frozen bodies",
     f"At least 150 cells with both arms at at least {MIN_REPS} replicates, and at least 3 of them recording a "
     f"frozen body at {FROZEN_REPS} replicates",
     "falsifier: fewer cells, fewer than three frozen, or fewer replicates"),
    ("AN2", f"and on a frozen body the buffer is worth nothing, within {ZERO:.2f}",
     "Every frozen cell's accuracy gain is within 0.01 of zero",
     f"falsifier: any above {ZERO_FIRES:.2f} in absolute value; null: between"),
    ("AN3", "and its forgetting cut is exactly zero",
     "Every frozen cell's mean forgetting is unchanged by the buffer, to a thousandth",
     f"falsifier: any cut above {CUT_ZERO:.3f}"),
    ("AN4", f"and the plastic cells are worth a tenth, below {LEVEL:.2f} of accuracy",
     "At least one cell that does not record a frozen body, and whose naive accuracy is below 0.58, gains at least "
     "0.10 from the buffer",
     "falsifier: none"),
    ("AN5", f"and the head's own fitting does not move it, {LEVEL_SPLIT:.2f} apart and {LEVEL_GAIN_DIFF:.2f} together",
     "Two frozen-body cells of one configuration differing only in the head's learning rate have naive accuracies at "
     "least 0.05 apart and gains within 0.02 of each other",
     "falsifier: the accuracies closer than 0.05, or the gains more than 0.02 apart; refused when either artifact is "
     "absent"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _stats(doc: dict, arm: str):
    reps = ((doc.get("methods") or {}).get(arm) or {}).get("replicates") or []
    if not reps:
        return None
    return (statistics.fmean([r["final_accuracy"] for r in reps]),
            statistics.fmean([r["mean_forgetting"] for r in reps]), len(reps))


def _cell(path: Path, doc: dict) -> dict | None:
    base = {a: _stats(doc, a) for a in REQUIRED}
    if any(base[a] is None for a in REQUIRED):
        return None
    cfg = doc.get("config") or {}
    return {"artifact": path.name, "replicates": min(base["naive"][2], base["replay"][2]),
            "naive_accuracy": base["naive"][0], "gain": base["replay"][0] - base["naive"][0],
            "cut": base["naive"][1] - base["replay"][1],
            "frozen_body": bool(cfg.get("frozen_body")), "lr": cfg.get("lr"),
            "circuit_size": cfg.get("circuit_size")}


def reading(root: Path = ROOT, pair=FROZEN_PAIR) -> dict:
    out = {"ok": True, "reason": None, "cells": [], "frozen": [], "plastic": [], "pair": None, "collapsed": None}
    try:
        skip = corpus.repeat_paths(root)
    except Exception as exc:                                  # pragma: no cover - the corpus's own rule
        return {**out, "ok": False, "reason": f"the corpus's repeat rule did not run: {exc}"}
    out["collapsed"] = len(skip)
    for path in sorted(Path(root).glob("*.json")):
        if path.name in skip:
            continue
        doc = load(path)
        if not isinstance(doc, dict):
            continue
        methods = doc.get("methods")
        if not isinstance(methods, dict) or any(a not in methods for a in REQUIRED):
            continue
        cell = _cell(path, doc)
        if cell is None or cell["replicates"] < MIN_REPS:
            continue
        out["cells"].append(cell)
        (out["frozen"] if cell["frozen_body"] else out["plastic"]).append(cell)

    a, b = (load(p) for p in pair)
    if a is None or b is None:
        out["pair"] = {"artifacts": [p.name for p in pair], "absent": True}
        return out
    ca, cb = a.get("config") or {}, b.get("config") or {}
    differing = sorted(k for k in set(ca) | set(cb)
                       if k not in RUN_FIELDS and ca.get(k) != cb.get(k))
    def _stat(doc):
        got = {x: _stats(doc, x) for x in REQUIRED}
        return {"naive_accuracy": got["naive"][0],
                "gain": got["replay"][0] - got["naive"][0], "cut": got["naive"][1] - got["replay"][1],
                "replicates": min(got["naive"][2], got["replay"][2]),
                "frozen_body": bool((doc.get("config") or {}).get("frozen_body"))}
    out["pair"] = {"artifacts": [p.name for p in pair], "absent": False, "differing_config": differing,
                   "same_draws": all(json.dumps(a.get(k), sort_keys=True) == json.dumps(b.get(k), sort_keys=True)
                                     for k in PAIR_FIELDS),
                   "a": _stat(a), "b": _stat(b)}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the ledger could not be read"}
                for c in CLAIMS]
    cells, frozen = r["cells"], r["frozen"]
    thin = [c["artifact"] for c in cells if c["replicates"] < MIN_REPS]
    frozen_thin = [c["artifact"] for c in frozen if c["replicates"] < FROZEN_REPS]
    j1 = {"id": "AN1",
          "measured": f"{len(cells)} cells, {len(frozen)} of them recording a frozen body, at "
                      f"{sorted({c['replicates'] for c in cells})} replicates, with {r.get('collapsed')} second "
                      f"executions collapsed",
          "verdict": f"MET -- the ledger is carried, {len(cells)} cells and {len(frozen)} frozen bodies" if
                     (len(cells) >= MIN_CELLS and len(frozen) >= MIN_FROZEN and not thin and not frozen_thin) else
                     f"FALSIFIER FIRED -- {len(cells)} cells, {len(frozen)} frozen, thin {thin[:3] or frozen_thin}"}
    worst = max(((abs(c["gain"]), c["artifact"]) for c in frozen), default=(0.0, None))
    j2 = {"id": "AN2",
          "measured": f"the {len(frozen)} frozen cells' gains are "
                      f"{[round(c['gain'], 4) for c in frozen]}, the largest in absolute value {worst[0]:.4f} on "
                      f"{worst[1]}",
          "verdict": f"MET -- the buffer is worth nothing on a frozen body, the largest {worst[0]:.4f}" if
                     (frozen and worst[0] <= ZERO) else
                     f"FALSIFIER FIRED -- {worst[0]:.4f} on {worst[1]}" if worst[0] > ZERO_FIRES else
                     f"NULL -- {worst[0]:.4f}, between {ZERO:.2f} and {ZERO_FIRES:.2f}"}
    widest = max(((c["cut"], c["artifact"]) for c in frozen), default=(0.0, None))
    j3 = {"id": "AN3",
          "measured": f"the frozen cells' forgetting cuts are {[round(c['cut'], 4) for c in frozen]}, the largest "
                      f"{widest[0]:.4f} on {widest[1]}",
          "verdict": f"MET -- the cut is exactly zero on all {len(frozen)} frozen cells" if
                     (frozen and widest[0] <= CUT_ZERO) else
                     f"FALSIFIER FIRED -- a cut of {widest[0]:.4f} on {widest[1]}"}
    aided = [c for c in r["plastic"] if c["naive_accuracy"] < LEVEL and c["gain"] >= PLASTIC]
    best = max(((c["gain"], c["artifact"], c["naive_accuracy"]) for c in aided), default=None)
    j4 = {"id": "AN4",
          "measured": f"{len(aided)} of the {len(r['plastic'])} plastic cells have a naive accuracy below {LEVEL:.2f} "
                      f"and a gain of at least {PLASTIC:.2f}"
                      + (f", the largest {best[0]:+.4f} on {best[1]} at {best[2]:.4f}" if best else ""),
          "verdict": f"MET -- the plastic cells below {LEVEL:.2f} of accuracy are worth a tenth, {len(aided)} of them"
                     if aided else f"FALSIFIER FIRED -- no plastic cell below {LEVEL:.2f} gains {PLASTIC:.2f}"}
    p = r.get("pair") or {}
    if not p or p.get("absent"):
        j5 = {"id": "AN5", "measured": "one of the frozen-body pair is absent", "verdict": "REFUSED"}
    else:
        a, b = p["a"], p["b"]
        apart = abs(a["naive_accuracy"] - b["naive_accuracy"])
        together = abs(a["gain"] - b["gain"])
        good5 = (apart >= LEVEL_SPLIT and together <= LEVEL_GAIN_DIFF and p["same_draws"]
                 and p["differing_config"] == ["lr"] and a["frozen_body"] and b["frozen_body"])
        j5 = {"id": "AN5",
              "measured": f"the pair's naive accuracies are {a['naive_accuracy']:.4f} and {b['naive_accuracy']:.4f}, "
                          f"{apart:.4f} apart, and their gains {a['gain']:+.4f} and {b['gain']:+.4f}, "
                          f"{together:.4f} apart, with `config` differing in {p['differing_config']} alone",
              "verdict": f"MET -- the head's step size moves the level by {apart:.4f} and the aid by {together:.4f}"
                         if good5 else
                         f"FALSIFIER FIRED -- {apart:.4f} apart on the level and {together:.4f} on the aid, "
                         f"differing in {p['differing_config']}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the aid needs a plastic body ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'the corpus did not read')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print(f"   {len(r['cells'])} cells at five replicates or more, {len(r['frozen'])} of them recording a frozen "
          f"body, {r.get('collapsed')} second executions collapsed")
    print(f"\n   {'frozen':>7} {'artifact':52} {'naive acc':>10} {'gain':>9} {'cut':>9} {'n':>4}")
    for label, band in (("yes", r["frozen"]), ("no", r["plastic"])):
        if label == "no":
            band = sorted(band, key=lambda c: -c["gain"])[:6]
        for c in band:
            print(f"   {label:>7} {c['artifact'][:52]:52} {c['naive_accuracy']:10.4f} {c['gain']:+9.4f} "
                  f"{c['cut']:+9.4f} {c['replicates']:4d}")
    p = r.get("pair") or {}
    if p and not p.get("absent"):
        print(f"\n   the frozen-body pair: `{p['artifacts'][0]}` and `{p['artifacts'][1]}`, `config` differing in "
              f"{p['differing_config']}, the draws identical: {p['same_draws']}")
        print(f"   naive accuracy {p['a']['naive_accuracy']:.4f} and {p['b']['naive_accuracy']:.4f}, gains "
              f"{p['a']['gain']:+.4f} and {p['b']['gain']:+.4f}, cuts {p['a']['cut']:+.4f} and {p['b']['cut']:+.4f}")
    print("\n== the registered claims, AN1-AN5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e412` and `e413` both registered that the budget is not the level; the corpus's own frozen-body")
    print("    setting is the control for it)")
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
