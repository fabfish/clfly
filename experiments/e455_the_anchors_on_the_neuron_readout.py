"""E455 -- the anchors on the neuron read-out: whether the earned label is what stopped them.

Every reading this line has published about the card's world was taken with the head reading the **world's own state** --
`--readout-from-world`, the earned label, which `e355` built so that the answer lives in the environment and the head's
input width is `loop-world-dims`. On that world `e438` found the anchor is **not a buffer**: `ewc-block` reads **-0.0302**
below the baseline on the mean diagonal, unresolved at **1.77** sigma, and its one resolved effect is a **price** at the
newest task (**-0.1177** at **3.71**). `e440` then found it holding the recurrent weights harder than the corpus's
typical penalty cell, and `e442` found that parameter stable while the effect moved. **None of that has been asked with
the head reading the circuit's neurons instead**, which is the read-out every other suite in the corpus uses and the one
the corpus's eleven basis audits were taken on.

**This unit moves the read-out and nothing else.** `e438`'s configuration with `--readout-from-world` **omitted** alone
differing, at the same three arms and twenty replicates on the same coupled world, so each task's read-out is the
circuit's own `--readout-size 32` columns instead of the world's **8**. Five claims, registered before the new run's
reading was opened.

- **DB1 -- and the run is one configuration with the read-out moved.** The three arms at **20** replicates, every recorded
  config field agreeing with `e438`'s except `readout_from_world`, the output path and the saved weights, the three task
  names equal, and each task's own read-out **32** wide against the card's **8**. **Falsifier**: any other config field
  differing, an arm missing or short, a task name differing, or a read-out that is not the circuit's own width.
- **DB2 -- and the anchor's standing is unresolved on the neuron read-out too.** Its mean diagonal over the baseline is
  under **two** sigma. **Falsifier**: at or above two sigma in either direction. *This is the unit's question: if the
  earned label is what removed the anchor's standing, this fires.*
- **DB3 -- and the buffer is ahead of the anchor here too.** `replay` minus `ewc-block` on the mean diagonal is positive
  at **two** sigma or more. **Falsifier**: not positive, or under two sigma.
- **DB4 -- and the buffer's own ledger holds.** `replay` minus `naive` at the first position is at least **+0.05**.
  **Falsifier**: at or below **zero**; **null**: between. *The card reads **+0.2896** on the earned label.*
- **DB5 -- and the anchor's newest-task price does not resolve here.** Its cost at the last-taught task is under
  **two** sigma. **Falsifier**: at or above two sigma. *On the earned label this is the arm's one resolved effect, at
  **3.71** sigma; if the read-out is what makes it, this fires.*

**What it can do beyond that.** It asks whether the line's central sentence about the anchors -- that they have no
standard and only a price -- is a property of **anchoring** or of the **earned label**. If both readings come back with
the anchor unresolved and the buffer ahead, the sentence is the anchoring's and the card's clauses travel to the corpus's
other read-out; if either of the two nulls fires, then the one thing this line has found about the anchor is the head's
reading of the world, which is a smaller and much more specific claim than the card now carries.

**What it cannot do.** *One read-out*: the circuit's 32 neurons against the world's 8, so the two differ in width as well
as in what they read, and the **8** to **32** is `e286`'s axis as much as it is the earned label's -- which `e448` and
`e449` measured separately on the earned label. *And one cell*: the card's world at twenty replicates, so the other five
draws and the three streams are not in the reading. *And one anchor*: `ewc-block-rand` is absent, though `e439` found the
two **0.0042** apart at the last position and `e440` found them holding the weights **0.0046** apart. *And a read-out is
not a mechanism*: that the anchor's standing is unresolved under both heads does not say that the body's regularisation
does nothing -- only that the diagonal does not resolve it.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the card's world on the neuron read-out, and the earned-label roll it is read against
RUNS = {
    "new": Path("runs/e455_earned_label_neurons_20reps.json"),
    "card": Path("runs/e438_earned_label_three_arms_20reps.json"),
}
ARMS = ("naive", "ewc-block", "replay")
BASELINE = "naive"
ANCHOR = "ewc-block"
BUFFER = "replay"
READOUT_FIELD = "readout_from_world"
SHARED = ("circuit", "tasks")
IGNORED = ("json_out", "save_theta", "methods", READOUT_FIELD)
N_TASKS = 3
N_ARMS = 3
MIN_REPS = 20
CARD_READOUT = 8
NEURON_READOUT = 32
SIGMA = 2.0
FIRST_BAR = 0.05
FIRST_FLOOR = 0.0
#: the earned label's own readings, which DB4 and DB5 are registered against
CARD_FIRST = 0.2896
CARD_PRICE = -0.1177
CARD_PRICE_SIGMA = 3.71
CLAIMS = (
    ("DB1", f"and the run is one configuration with the read-out moved, at {MIN_REPS} replicates",
     "The three arms at twenty replicates, every recorded config field agreeing with e438's except readout_from_world, "
     "the output path and the saved weights, the three task names equal, and each task's own read-out 32 wide against "
     "the card's 8",
     "falsifier: any other config field differing, an arm missing or short, a task name differing, or a read-out that is "
     "not the circuit's own width"),
    ("DB2", f"and the anchor's standing is unresolved on the neuron read-out too, under {SIGMA:.0f} sigma",
     "Its mean diagonal over the baseline is under two sigma",
     "falsifier: at or above two sigma in either direction"),
    ("DB3", f"and the buffer is ahead of the anchor here too, at {SIGMA:.0f} sigma",
     "replay minus ewc-block on the mean diagonal is positive at two sigma or more",
     "falsifier: not positive, or under two sigma"),
    ("DB4", f"and the buffer's own ledger holds, at least {FIRST_BAR:+.2f}",
     "replay minus naive at the first position is at least +0.05",
     f"falsifier: at or below {FIRST_FLOOR:+.2f}; null: between"),
    ("DB5", f"and the anchor's newest-task price does not resolve here, under {SIGMA:.0f} sigma",
     "Its cost at the last-taught task is under two sigma",
     "falsifier: at or above two sigma"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _roll(path: Path) -> dict | None:
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    arms = {}
    for arm in ARMS:
        if arm not in methods:
            continue
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        arms[arm] = {"replicates": len(reps),
                     "final": [statistics.fmean([r["final_per_task"][k] for r in reps]) for k in range(N_TASKS)],
                     "diagonal": [statistics.fmean(r["final_per_task"]) for r in reps],
                     "last": [r["final_per_task"][-1] for r in reps],
                     "forgetting": statistics.fmean([r["mean_forgetting"] for r in reps])}
    cfg = doc.get("config") or {}
    tasks = doc.get("tasks") or []
    return {"artifact": path.name, "arms": arms,
            "task_names": [t.get("name") if isinstance(t, dict) else t for t in tasks],
            "readouts": [t.get("n_readout") if isinstance(t, dict) else None for t in tasks],
            "readout_from_world": cfg.get(READOUT_FIELD),
            "shared": {k: doc.get(k) for k in SHARED},
            "config": {k: cfg.get(k) for k in sorted(set(cfg) - set(IGNORED))}}


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def reading(runs: dict = RUNS) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "readouts": {}, "contrasts": {}, "spans": {}}
    for label, path in runs.items():
        got = _roll(path)
        if got is None:
            return {**out, "ok": False, "reason": f"roll {label}: {path} is absent or carries no arm"}
        out["runs"][label] = got
    new, card = out["runs"]["new"], out["runs"]["card"]
    missing = [a for a in ARMS if a not in new["arms"]]
    if missing:
        return {**out, "ok": False, "reason": f"the new roll carries no arm for {missing}"}
    same = {}
    fields = sorted(set(new["config"]) | set(card["config"]))
    for k in fields:
        same[f"config.{k}"] = new["config"].get(k) == card["config"].get(k)
    same["circuit"] = new["shared"].get("circuit") == card["shared"].get("circuit")
    same["task_names"] = new["task_names"] == card["task_names"]
    out["same"] = same
    out["readouts"] = {"new": {"readouts": new["readouts"], "from_world": new["readout_from_world"]},
                       "card": {"readouts": card["readouts"], "from_world": card["readout_from_world"]}}
    for label, roll in out["runs"].items():
        out["contrasts"][label] = {
            "anchor_diagonal": _paired(roll["arms"][ANCHOR]["diagonal"], roll["arms"][BASELINE]["diagonal"]),
            "anchor_last": _paired(roll["arms"][ANCHOR]["last"], roll["arms"][BASELINE]["last"]),
            "buffer_diagonal": _paired(roll["arms"][BUFFER]["diagonal"], roll["arms"][BASELINE]["diagonal"]),
            "buffer_over_anchor": _paired(roll["arms"][BUFFER]["diagonal"], roll["arms"][ANCHOR]["diagonal"]),
            "buffer_gain": [roll["arms"][BUFFER]["final"][k] - roll["arms"][BASELINE]["final"][k]
                            for k in range(N_TASKS)],
            "forgetting": {a: roll["arms"][a]["forgetting"] for a in roll["arms"]}}
    n = out["contrasts"]["new"]
    out["spans"] = {"replicates": sorted({v["replicates"] for roll in out["runs"].values()
                                         for v in roll["arms"].values()}),
                    "arms": {label: len(roll["arms"]) for label, roll in out["runs"].items()},
                    "same_fields": len(same),
                    "readout": {"new": new["readouts"][0] if new["readouts"] else None,
                                "card": card["readouts"][0] if card["readouts"] else None,
                                "from_world": {"new": new["readout_from_world"], "card": card["readout_from_world"]}},
                    "anchor": {"diagonal": n["anchor_diagonal"]["mean"], "sigma": n["anchor_diagonal"]["sigma"],
                               "last": n["anchor_last"]["mean"], "last_sigma": n["anchor_last"]["sigma"],
                               "card_diagonal": out["contrasts"]["card"]["anchor_diagonal"]["mean"],
                               "card_sigma": out["contrasts"]["card"]["anchor_diagonal"]["sigma"],
                               "card_last": out["contrasts"]["card"]["anchor_last"]["mean"]},
                    "buffer": {"over_anchor": n["buffer_over_anchor"]["mean"],
                               "over_anchor_sigma": n["buffer_over_anchor"]["sigma"],
                               "first": n["buffer_gain"][0],
                               "first_sigma": _paired(out["runs"]["new"]["arms"][BUFFER]["diagonal"],
                                                      out["runs"]["new"]["arms"][BASELINE]["diagonal"])["sigma"]},
                    "known": {"card_first": CARD_FIRST, "card_price": CARD_PRICE,
                              "card_price_sigma": CARD_PRICE_SIGMA}}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no arm"} for c in CLAIMS]
    differ = sorted(k for k, v in r["same"].items() if not v)
    thin = {f"{lbl}.{a}": v["replicates"] for lbl, roll in r["runs"].items() for a, v in roll["arms"].items()
            if v["replicates"] < MIN_REPS}
    short = {} if len(r["runs"]["new"]["arms"]) >= N_ARMS else {"new": sorted(r["runs"]["new"]["arms"])}
    ro = r["spans"]["readout"]
    reads_ok = (ro["new"] == NEURON_READOUT and ro["card"] == CARD_READOUT and
                ro["from_world"]["new"] is False and ro["from_world"]["card"] is True and
                all(x == NEURON_READOUT for x in r["runs"]["new"]["readouts"]))
    j1 = {"id": "DB1",
          "measured": f"the new roll carries {len(r['runs']['new']['arms'])} arms at {r['spans']['replicates']} "
                      f"replicates over {r['spans']['same_fields']} compared fields, the read-out {ro['new']} against "
                      f"the card's {ro['card']}, from the world {ro['from_world']}",
          "verdict": "MET -- one configuration with `readout_from_world` omitted, the task names held, and every task's "
                     "read-out the circuit's own width" if
                     (not short and not differ and not thin and reads_ok) else
                     f"FALSIFIER FIRED -- differing {differ}, thin {thin}, short {short}, read-outs {ro}"}
    a = r["spans"]["anchor"]
    j2 = {"id": "DB2",
          "measured": f"on the neuron read-out the anchor's mean diagonal over the baseline is {a['diagonal']:+.4f} at "
                      f"{abs(a['sigma']):.2f} sigma, against the card's {a['card_diagonal']:+.4f} at "
                      f"{abs(a['card_sigma']):.2f}",
          "verdict": f"MET -- the anchor's standing is unresolved on the neuron read-out too, "
                     f"{abs(a['sigma']):.2f} sigma" if abs(a["sigma"]) < SIGMA else
                     f"FALSIFIER FIRED -- the standing resolves here at {abs(a['sigma']):.2f} sigma"}
    b = r["spans"]["buffer"]
    j3 = {"id": "DB3",
          "measured": f"on the neuron read-out the buffer is {b['over_anchor']:+.4f} ahead of the anchor on the mean "
                      f"diagonal at {abs(b['over_anchor_sigma']):.2f} sigma",
          "verdict": f"MET -- the buffer is ahead of the anchor here too, {b['over_anchor']:+.4f} at "
                     f"{abs(b['over_anchor_sigma']):.2f} sigma" if
                     (b["over_anchor"] > 0 and abs(b["over_anchor_sigma"]) >= SIGMA) else
                     f"FALSIFIER FIRED -- {b['over_anchor']:+.4f} at {abs(b['over_anchor_sigma']):.2f} sigma"}
    first = b["first"]
    j4 = {"id": "DB4",
          "measured": f"on the neuron read-out the buffer over naive at the first position is {first:+.4f}, against the "
                      f"card's {CARD_FIRST:+.4f}",
          "verdict": f"MET -- the buffer's first-position gain holds under the neuron read-out, {first:+.4f}" if
                     first >= FIRST_BAR else
                     f"FALSIFIER FIRED -- {first:+.4f} at or below zero" if first <= FIRST_FLOOR else
                     f"NULL -- {first:+.4f} between {FIRST_FLOOR:+.2f} and {FIRST_BAR:+.2f}"}
    last, lsig = a["last"], abs(a["last_sigma"])
    j5 = {"id": "DB5",
          "measured": f"on the neuron read-out the anchor's newest-task cost is {last:+.4f} at {lsig:.2f} sigma, against "
                      f"the card's {CARD_PRICE:+.4f} at {CARD_PRICE_SIGMA:.2f}",
          "verdict": f"MET -- the anchor's newest-task price does not resolve here, {lsig:.2f} sigma" if
                     lsig < SIGMA else
                     f"FALSIFIER FIRED -- the price resolves here at {lsig:.2f} sigma"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the anchors on the neuron read-out ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source, coupled, twenty replicates -- the head reading the")
    print("   circuit's own neurons here and the world's own state on the card")
    print(f"\n   {'roll':>6} {'read-out':>9} {'from world':>11} {'tasks':>52}")
    for label, roll in r["runs"].items():
        print(f"   {label:>6} {str(roll['readouts'][0] if roll['readouts'] else None):>9} "
              f"{str(roll['readout_from_world']):>11} {'>'.join(roll['task_names'])[:52]:>52}")
    print("\n   the contrasts, both read-outs:")
    for label in ("card", "new"):
        c = r["contrasts"][label]
        print(f"      {label:>5} anchor over naive {c['anchor_diagonal']['mean']:+.4f} at "
              f"{abs(c['anchor_diagonal']['sigma']):.2f} sigma; its newest task {c['anchor_last']['mean']:+.4f} at "
              f"{abs(c['anchor_last']['sigma']):.2f}; the buffer over the anchor "
              f"{c['buffer_over_anchor']['mean']:+.4f} at {abs(c['buffer_over_anchor']['sigma']):.2f}")
    print("\n   mean forgetting, arm by arm:")
    for label in ("card", "new"):
        print(f"      {label:>5}: " +
              ", ".join(f"{a} {v:.4f}" for a, v in r["contrasts"][label]["forgetting"].items()))
    b = r["spans"]["buffer"]
    print(f"   the buffer over naive by position on the neuron read-out: " +
          " ".join(f"{x:+.4f}" for x in r["contrasts"]["new"]["buffer_gain"]))
    print("\n== the registered claims, DB1-DB5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (every reading of this world has been on the earned label, which `e355` built; the corpus's other")
    print("    suites and its eleven basis audits read the circuit's neurons, which is what this unit moves)")
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
