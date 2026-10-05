"""E430 -- where the bias goes: the buffer holds it down and the penalty pushes it up.

`e427` measured that three quarters of the buffer's worth lives in the head's **bias** -- freeze it and the aid keeps
0.27 of its gain -- and `e415` and `e423` measured the two arms' trade on one cell. Every arm's artifact carries the
bias's own trajectory beside its accuracies: the distance from zero after each task and the step each task costs, per
arm, so the trade can be read on the parameter the controls point at.

**This unit reads it.** The card's world at twenty replicates with `naive`, `ewc-block` and `replay` in one run, and
the plastic/frozen-bias pair at forty replicates whose frozen side is the control's own definition. No training, no
probe. Five claims, registered before this unit's pass over the runs.

- **BF1 -- and the ledger is carried.** The three-arm run at **20** replicates and the plastic/frozen-bias pair at
  **40**, each arm carrying a per-task distance-from-zero and step. **Falsifier**: any arm or entry missing, or fewer
  replicates.
- **BF2 -- and after the first task the arms are one arm.** On the three-arm run all three arms' distance from zero
  after task 0 is the same to a thousandth, the ground the arms start from. **Falsifier**: any arm differing.
- **BF3 -- and the buffer ends closest to zero.** `replay`'s distance after the last task is below **both** `naive`'s
  and `ewc-block`'s. **Falsifier**: not below either.
- **BF4 -- and the penalty ends furthest.** `ewc-block`'s distance after the last task is above both the others.
  **Falsifier**: not the largest. *BF3 and BF4 together are the unit's own prediction: an arm that regularises toward
  a basis should push the bias further from where the sequence started than the arm that replays, and the arm that does
  nothing should sit between them.*
- **BF5 -- and the control's own reading is zero.** On the frozen-bias side of the pair every arm's distance from zero
  and every step is **exactly 0.0000**, at 40 replicates, beside a plastic side whose readings are non-zero.
  **Falsifier**: any non-zero reading on the frozen side at that depth, or an all-zero plastic side.

**What it can do beyond that.** It reads the trade on the parameter `e427` found the aid living in. On the card's world
the three arms start at **+1.4010** together, and after the third task the buffer's bias sits at **+2.2946** where the
arm that does nothing is at **+2.7453** and the basis-matched penalty at **+4.0809** -- so the arm that forgets least
also holds the bias closest to where the sequence started, and the penalty's regularisation costs it the largest
displacement of the three. And the corpus's own frozen-bias control reads exactly zero on every arm at forty
replicates, which is the ground the pair's plastic side is measured against.

**What it cannot do.** *Two cells and one bias definition*: the three-arm reading is the card's world at `lam = 1.0`,
whose world predates `e359`'s coupling, and the pair is one overlap-suite configuration, so the corpus's other
configurations are not in this reading. *And a displacement is not a mechanism*: where the bias goes and what the arm
forgets are two readings of one trajectory, and this unit does not intervene on either. *And the distance is from the
initialisation, not from the connectome's own bias*: the corpus records the distance from zero, which for a
zero-initialised bias is the same thing and for any other is not. *And the metric is the corpus's*: `mean_forgetting`
is the diagonal minus the last row, which `e305` showed cannot see the part an arm never learned.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the three-arm cell `e415` and `e423` read, and the plastic/frozen-bias pair `e427` read
CELL = Path("runs/e356_earned_label_r32_20reps.json")
PAIR = (Path("runs/e140_r32_methods_frozenbias_40reps.json"), Path("runs/e140_r32_methods_plastic_40reps.json"))
BASELINE = "naive"
BUFFER = "replay"
N_TASKS = 3
MIN_REPS = 20
PAIR_REPS = 40
ZERO = 1e-3
CLAIMS = (
    ("BF1", f"and the ledger is carried, at {MIN_REPS} and {PAIR_REPS} replicates",
     "The three-arm run at twenty replicates and the plastic/frozen-bias pair at forty, each arm carrying a per-task "
     "distance from zero and a per-task step",
     "falsifier: any arm or entry missing, or fewer replicates"),
    ("BF2", "and after the first task the arms are one arm",
     "On the three-arm run all three arms' distance from zero after task 0 is the same to a thousandth",
     "falsifier: any arm differing"),
    ("BF3", "and the buffer ends closest to zero",
     "replay's distance after the last task is below both naive's and ewc-block's",
     "falsifier: not below either"),
    ("BF4", "and the penalty ends furthest",
     "ewc-block's distance after the last task is above both the others",
     "falsifier: not the largest"),
    ("BF5", "and the control's own reading is zero",
     "On the frozen-bias side of the pair every arm's distance from zero and every step is exactly 0.0000 at forty "
     "replicates, beside a plastic side whose readings are non-zero",
     "falsifier: any non-zero reading on the frozen side, or an all-zero plastic side"),
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
    for arm in sorted(methods):
        got = methods[arm] or {}
        reps = got.get("replicates") or []
        if not reps:
            continue
        from_zero = got.get("bias_from_zero")
        step = got.get("bias_step")
        if from_zero is None or step is None:
            continue
        arms[arm] = {"replicates": len(reps), "from_zero": list(from_zero), "step": list(step),
                     "final_from_zero": float(from_zero[-1]) if from_zero else None}
    return arms or None


def reading(cell: Path = CELL, pair=PAIR) -> dict:
    out = {"ok": True, "reason": None, "cell": None, "pair": {}}
    c = _roll(cell)
    if not c:
        return {**out, "ok": False, "reason": f"{cell} is absent or carries no bias reading"}
    out["cell"] = {"artifact": cell.name, "arms": c}
    for label, path in zip(("frozen", "plastic"), pair):
        got = _roll(path)
        if not got:
            return {**out, "ok": False, "reason": f"{path} is absent or carries no bias reading"}
        out["pair"][label] = {"artifact": path.name, "arms": got}
    frozen_arms = out["pair"]["frozen"]["arms"]
    plastic_arms = out["pair"]["plastic"]["arms"]
    ordered = sorted(c, key=lambda a: c[a]["final_from_zero"] or 0.0)
    out["spans"] = {"cell_arms": sorted(c), "replicates": sorted({v["replicates"] for v in c.values()}),
                    "pair_replicates": sorted({v["replicates"] for v in list(frozen_arms.values())
                                               + list(plastic_arms.values())}),
                    "cell_by_final": {a: round(c[a]["final_from_zero"], 4) for a in ordered},
                    "cell_first": {a: round(c[a]["from_zero"][0], 4) for a in sorted(c)},
                    "frozen_nonzero": {a: [v for v in (frozen_arms[a]["from_zero"] + frozen_arms[a]["step"])
                                           if abs(v) > 0] for a in sorted(frozen_arms)},
                    "plastic_first": {a: round(plastic_arms[a]["from_zero"][0], 4) for a in sorted(plastic_arms)}}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a run is absent or carries no bias reading"}
                for c in CLAIMS]
    cell, s = r["cell"], r["spans"]
    arms = cell["arms"]
    missing = sorted(a for a in (BASELINE, "ewc-block", BUFFER) if a not in arms)
    thin = {a: v["replicates"] for a, v in arms.items() if v["replicates"] < MIN_REPS}
    thin_pair = {lbl: {a: v["replicates"] for a, v in r["pair"][lbl]["arms"].items()
                       if v["replicates"] < PAIR_REPS} for lbl in ("frozen", "plastic")}
    thin_pair = {k: v for k, v in thin_pair.items() if v}
    j1 = {"id": "BF1",
          "measured": f"`{cell['artifact']}` carries {sorted(arms)} at {s['replicates']} replicates and "
                      f"{s['pair_replicates']} are carried by the pair, each with a per-task distance and step",
          "verdict": f"MET -- the ledger is carried at {MIN_REPS} and {PAIR_REPS} replicates" if
                     (not missing and not thin and not thin_pair and len(arms) >= 3) else
                     f"FALSIFIER FIRED -- missing {missing}, thin {thin or thin_pair}"}
    firsts = {a: round(arms[a]["from_zero"][0], 6) for a in sorted(arms)}
    distinct = len(set(firsts.values()))
    j2 = {"id": "BF2",
          "measured": f"the three arms' distance from zero after task 0 is {firsts}",
          "verdict": f"MET -- the arms are one arm after the first task, all at {arms[sorted(arms)[0]]['from_zero'][0]:+.4f}"
                     if distinct == 1 else f"FALSIFIER FIRED -- {firsts}"}
    finals = {a: arms[a]["final_from_zero"] for a in sorted(arms)}
    buf = finals.get(BUFFER)
    others = {a: v for a, v in finals.items() if a != BUFFER}
    j3 = {"id": "BF3",
          "measured": f"the arms' distance after the last task is "
                      f"{ {a: round(v, 4) for a, v in sorted(finals.items(), key=lambda kv: kv[1])} }",
          "verdict": f"MET -- the buffer ends closest to zero, {buf:+.4f} against "
                     f"{ {a: round(v, 4) for a, v in others.items()} }" if
                     (buf is not None and all(buf < v for v in others.values())) else
                     f"FALSIFIER FIRED -- {buf} is not below { {a: round(v, 4) for a, v in others.items()} }"}
    j4 = {"id": "BF4",
          "measured": f"the penalty's distance after the last task is {finals.get('ewc-block', float('nan')):+.4f} "
                      f"against the others' { {a: round(v, 4) for a, v in finals.items() if a != 'ewc-block'} }",
          "verdict": f"MET -- the penalty ends furthest, {finals['ewc-block']:+.4f}" if
                     (finals.get("ewc-block") is not None
                      and all(finals["ewc-block"] > v for a, v in finals.items() if a != "ewc-block")) else
                     f"FALSIFIER FIRED -- { {a: round(v, 4) for a, v in finals.items()} }"}
    nonzero = {a: v for a, v in s["frozen_nonzero"].items() if v}
    plastic_flat = all(abs(v) < ZERO for a in r["pair"]["plastic"]["arms"]
                       for v in (r["pair"]["plastic"]["arms"][a]["from_zero"]
                                 + r["pair"]["plastic"]["arms"][a]["step"]))
    j5 = {"id": "BF5",
          "measured": f"the frozen side's readings are "
                      f"{ {a: r['pair']['frozen']['arms'][a]['from_zero'] for a in sorted(r['pair']['frozen']['arms'])} } "
                      f"and the plastic side starts at {s['plastic_first']}",
          "verdict": f"MET -- the frozen-bias control reads exactly zero on every arm at {PAIR_REPS} replicates, "
                     f"beside a plastic side that does not" if (not nonzero and not plastic_flat) else
                     f"FALSIFIER FIRED -- non-zero on the frozen side {nonzero} or a flat plastic side "
                     f"{plastic_flat}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== where the bias goes ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print(f"   the bias's own trajectory, per arm: `{r['cell']['artifact']}` and the pair")
    print(f"\n   {'roll':>26} {'arm':>16} {'from zero 0/1/2':>28} {'step 0/1/2':>28}")
    for label, roll in [("cell", r["cell"])] + [(f"pair/{lbl}", v) for lbl, v in r["pair"].items()]:
        for arm in sorted(roll["arms"]):
            a = roll["arms"][arm]
            print(f"   {label:>26} {arm:>16} " + " ".join(f"{x:+.4f}" for x in a["from_zero"]) + "  "
                  + " ".join(f"{x:+.4f}" for x in a["step"]))
    s = r["spans"]
    print(f"\n   the three-arm run's distance after the last task, nearest first: {s['cell_by_final']}")
    print("\n== the registered claims, BF1-BF5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e427` found three quarters of the buffer's worth in the bias; this reads where each arm leaves it)")
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
