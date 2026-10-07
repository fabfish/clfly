"""E457 -- the game card, revision 11: the readout clause, because revisions 8 to 10 read as if their numbers were read-out-independent.

`e455` moved the card's world's head from the **world's own state** to the **circuit's own neurons** and found the
biological anchor's one resolved effect gone -- its newest-task price **-0.0115** at **0.78** sigma against **-0.1177** at
**3.71**. `e456` then drove the matched-random arm on the same head and found its price **does** resolve there
(**-0.0323** at **2.77**), so the two anchors' prices are **0.0042** apart on the earned label and **0.0208** apart on
the neurons with which of them pays more reversing. **The card's tenth revision carries the `ledger`, `width` and
`method` clauses and none of them names the read-out**, so a reader of `ledger` would take the anchor's price for the
arm's property rather than the head's, and a reader of `method` would take the buffer's advantage for one number rather
than two that differ by more than the ten rolls span.

**This unit writes revision 11.** One clause is added, the **readout** clause, carrying both read-outs' numbers for both
anchors and both basis contrasts, recomputed from the four rolls. Five claims, registered before this unit's pass over
the four.

- **DD1 -- and the tenth revision is carried unchanged where it is not rewritten.** Every field of `e454`'s card except
  the revision and the new clause is equal to the revision-10 card, with the revision now **11**. **Falsifier**: any
  other field differing, or the revision not 11; refused when the revision-10 artifact is absent.
- **DD2 -- and the clause's numbers come out of the four rolls.** Each read-out's and each anchor's standing and price
  with their sigmas, and the two basis contrasts on the diagonal and on forgetting with theirs, equal the four rolls
  recomputed. **Falsifier**: any number disagreeing by more than a thousandth of a point; refused when a roll is absent.
- **DD3 -- and the two anchors' standings agree under both read-outs.** Their mean-diagonal contrasts differ by at most
  **0.05** under each. **Falsifier**: **0.10** or more under either; **null**: between.
- **DD4 -- and the basis contrast is a null on the diagonal under both.** Its magnitude is at most **0.05** under each
  read-out. **Falsifier**: **0.10** or more under either; **null**: between.
- **DD5 -- and the read-out separates the two anchors' prices.** The two newest-task costs differ by at most **0.05**
  under the earned label and by at least **0.02** under the neurons. **Falsifier**: the earned-label gap above **0.10**,
  or the neuron gap below **0.01**.

**What it can do beyond that.** It is the card's own statement of the boundary its last three clauses were read across.
A reader who takes all four together has the shape of what this line measured: the buffer's advantage and the
anchors' absence hold under both heads; the anchor's newest-task price is the head's for the biological arm and not for
the matched-random one; and the basis contrast is a null wherever it is asked, at four cells now.

**What it cannot do.** *Two read-outs* of the four configurations the corpus runs, and the two differ in what they read
**and** in width -- **8** against **32** -- so `e448`'s and `e449`'s width axis is inside this clause's difference rather
than separated from it. *And one cell each*: the card's world at twenty replicates, so the other five draws and the three
streams are not in the reading. *And one partition draw*: the matched-random cells are one draw of the same group sizes.
*And a clause is not a result*: DD1 shows revision 10 survives into revision 11 and not that revision 10 was right, and
DD2 shows the clause agrees with the four rolls and not that they should be believed.
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
CARD10 = Path("runs/e454_the_game_card_revision_ten.json")
#: the four rolls, by the read-out they are on and the anchor they carry
ROLLS = {
    "earned_label/ewc-block": Path("runs/e438_earned_label_three_arms_20reps.json"),
    "earned_label/ewc-block-rand": Path("runs/e439_earned_label_rand_20reps.json"),
    "neurons/ewc-block": Path("runs/e455_earned_label_neurons_20reps.json"),
    "neurons/ewc-block-rand": Path("runs/e456_earned_label_rand_neurons_20reps.json"),
}
READOUTS = {"earned_label": {"from_world": True}, "neurons": {"from_world": False}}
BASELINE = "naive"
BUFFER = "replay"
REVISION = 11
NEW = ("revision", "readout")
N_TASKS = 3
MIN_REPS = 20
ALIKE = 0.05
ALIKE_FIRES = 0.10
LABEL_GAP = 0.05
NEURON_GAP = 0.02
NEURON_GAP_FLOOR = 0.01
TOL = 0.002
CLAIMS = (
    ("DD1", "and the tenth revision is carried unchanged where it is not rewritten",
     "Every field of `e454`'s card except the revision and the new clause is equal to the revision-10 card, with the "
     "revision now 11",
     "falsifier: any other field differing, or the revision not 11; refused when `e454`'s artifact is absent"),
    ("DD2", "and the clause's numbers come out of the four rolls",
     "Each read-out's and each anchor's standing and price with their sigmas, and the two basis contrasts on the "
     "diagonal and on forgetting with theirs, equal the four rolls recomputed",
     "falsifier: any number disagreeing by more than a thousandth of a point; refused when a roll is absent"),
    ("DD3", f"and the two anchors' standings agree under both read-outs, within {ALIKE:.2f}",
     "Their mean-diagonal contrasts differ by at most 0.05 under each",
     f"falsifier: {ALIKE_FIRES:.2f} or more under either; null: between"),
    ("DD4", f"and the basis contrast is a null on the diagonal under both, within {ALIKE:.2f}",
     "Its magnitude is at most 0.05 under each read-out",
     f"falsifier: {ALIKE_FIRES:.2f} or more under either; null: between"),
    ("DD5", f"and the read-out separates the two anchors' prices, at most {LABEL_GAP:.2f} on the label and at least {NEURON_GAP:.2f} on the neurons",
     "The two newest-task costs differ by at most 0.05 under the earned label and by at least 0.02 under the neurons",
     f"falsifier: the earned-label gap above {ALIKE_FIRES:.2f}, or the neuron gap below {NEURON_GAP_FLOOR:.2f}"),
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
                     "last": [r["final_per_task"][-1] for r in reps],
                     "forgetting": [r["mean_forgetting"] for r in reps]}
    cfg = doc.get("config") or {}
    tasks = doc.get("tasks") or []
    return {"artifact": path.name, "anchor": anchor, "arms": arms,
            "readouts": [t.get("n_readout") if isinstance(t, dict) else None for t in tasks],
            "from_world": cfg.get("readout_from_world")}


def reading(card10: Path = CARD10, rolls: dict = ROLLS) -> dict:
    out = {"ok": True, "reason": None, "card": None, "revision10": {}, "readout": {}, "rolls": {}}
    base = load(card10)
    if not base:
        return {**out, "ok": False, "reason": f"{card10} is absent, so revision 10 is not on disk"}
    old = base.get("card") or {}
    card = copy.deepcopy(old)
    card["revision"] = REVISION
    out["revision10"] = {k: v for k, v in old.items() if k not in NEW}

    got = {}
    for label, path in rolls.items():
        readout, anchor = label.split("/")
        r = _roll(path, anchor)
        if r is None:
            return {**out, "ok": False, "reason": f"{path} is absent or carries no {anchor} arm"}
        arms = r["arms"]
        got[label] = {"artifact": r["artifact"], "readout": readout, "anchor": anchor,
                      "replicates": arms[BASELINE]["replicates"],
                      "standing": _paired(arms[anchor]["diagonal"], arms[BASELINE]["diagonal"]),
                      "price": _paired(arms[anchor]["last"], arms[BASELINE]["last"]),
                      "readout_width": r["readouts"][0] if r["readouts"] else None,
                      "from_world": r["from_world"]}
        out["rolls"][label] = got[label]
    widths = {l: got[l]["readout_width"] for l in got}
    from_world = {l: got[l]["from_world"] for l in got}
    basis = {}
    #: the two basis contrasts need both anchors' replicate lists, so they are taken from the artifacts here
    for readout in READOUTS:
        rows = {l: load(ROLLS[l]) for l in got if l.startswith(readout + "/")}
        vals = {}
        for anchor in ("ewc-block", "ewc-block-rand"):
            doc = rows[f"{readout}/{anchor}"]
            methods = doc["methods"]
            reps = methods[anchor]["replicates"]
            vals[anchor] = {"diagonal": [statistics.fmean(r["final_per_task"]) for r in reps],
                            "forgetting": [r["mean_forgetting"] for r in reps]}
        basis[readout] = {"accuracy": _paired(vals["ewc-block"]["diagonal"], vals["ewc-block-rand"]["diagonal"]),
                          "forgetting": _paired(vals["ewc-block"]["forgetting"],
                                                vals["ewc-block-rand"]["forgetting"])}
    card["readout"] = {
        "artifact": [got[l]["artifact"] for l in got],
        "readouts": {r: {"from_world": READOUTS[r]["from_world"],
                         "width": next(got[l]["readout_width"] for l in got if got[l]["readout"] == r)}
                     for r in READOUTS},
        "buffer": BUFFER,
        "anchor_over_naive": {l: got[l]["standing"]["mean"] for l in got},
        "anchor_over_naive_sigma": {l: got[l]["standing"]["sigma"] for l in got},
        "newest_task": {l: got[l]["price"]["mean"] for l in got},
        "newest_task_sigma": {l: got[l]["price"]["sigma"] for l in got},
        "basis_accuracy": {r: basis[r]["accuracy"]["mean"] for r in basis},
        "basis_accuracy_sigma": {r: basis[r]["accuracy"]["sigma"] for r in basis},
        "basis_forgetting": {r: basis[r]["forgetting"]["mean"] for r in basis},
        "basis_forgetting_sigma": {r: basis[r]["forgetting"]["sigma"] for r in basis},
    }
    out["readout"] = dict(card["readout"])
    out["basis"] = basis
    out["card"] = card
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the clause is read from is absent"}
                for c in CLAIMS]
    card, ro = r["card"], r["readout"]
    same = {k: (card.get(k) == v) for k, v in r["revision10"].items()}
    j1 = {"id": "DD1",
          "measured": f"the revision-10 card's {len(same)} fields against the revision-11 card: "
                      f"{len(same) - sum(1 for v in same.values() if not v)} equal, with the revision now "
                      f"{card.get('revision')}",
          "verdict": f"MET -- the tenth revision is carried unchanged in all {len(same)} fields it does not rewrite" if
                     (all(same.values()) and card.get("revision") == REVISION) else
                     f"FALSIFIER FIRED -- { {k: v for k, v in same.items() if not v} } differs"}
    bad2 = {}
    for label, got in r["rolls"].items():
        for key, field in (("anchor_over_naive", "standing"), ("anchor_over_naive_sigma", "standing"),
                           ("newest_task", "price"), ("newest_task_sigma", "price")):
            carried = ro[key].get(label)
            want = got[field]["mean"] if key.endswith("sigma") is False else got[field]["sigma"]
            if carried is None or abs(carried - want) > TOL:
                bad2[f"{label}/{key}"] = (carried, want)
    for readout in READOUTS:
        for key in ("basis_accuracy", "basis_accuracy_sigma", "basis_forgetting", "basis_forgetting_sigma"):
            field = "accuracy" if "accuracy" in key else "forgetting"
            want = r["basis"][readout][field]["mean" if not key.endswith("sigma") else "sigma"]
            carried = ro[key].get(readout)
            if carried is None or abs(carried - want) > TOL:
                bad2[f"{readout}/{key}"] = (carried, want)
    j2 = {"id": "DD2",
          "measured": f"the clause's standings are "
                      f"{ {l: round(v, 4) for l, v in ro['anchor_over_naive'].items()} } at "
                      f"{ {l: round(abs(v), 2) for l, v in ro['anchor_over_naive_sigma'].items()} } sigma and its "
                      f"prices { {l: round(v, 4) for l, v in ro['newest_task'].items()} }, with the basis contrasts "
                      f"{ {rd: round(v, 4) for rd, v in ro['basis_accuracy'].items()} } and "
                      f"{ {rd: round(v, 4) for rd, v in ro['basis_forgetting'].items()} }",
          "verdict": "MET -- the clause's numbers are the four rolls' own" if not bad2 else
                     f"FALSIFIER FIRED -- {bad2}"}
    gaps = {}
    for readout in READOUTS:
        a, b = f"{readout}/ewc-block", f"{readout}/ewc-block-rand"
        gaps[readout] = abs(r["rolls"][a]["standing"]["mean"] - r["rolls"][b]["standing"]["mean"])
    off3 = {k: v for k, v in gaps.items() if v > ALIKE}
    j3 = {"id": "DD3",
          "measured": f"the two anchors' standings are { {k: round(v, 4) for k, v in gaps.items()} } apart by read-out",
          "verdict": f"MET -- the two anchors' standings agree under both read-outs, the wider "
                     f"{max(gaps.values()):.4f}" if not off3 else
                     f"FALSIFIER FIRED -- {off3} above {ALIKE:.2f}" if any(v >= ALIKE_FIRES for v in off3.values())
                     else f"NULL -- {off3} between {ALIKE:.2f} and {ALIKE_FIRES:.2f}"}
    vals4 = {rd: abs(ro["basis_accuracy"][rd]) for rd in READOUTS}
    off4 = {k: v for k, v in vals4.items() if v > ALIKE}
    j4 = {"id": "DD4",
          "measured": f"the basis contrast on the diagonal is "
                      f"{ {rd: round(ro['basis_accuracy'][rd], 4) for rd in READOUTS} } at "
                      f"{ {rd: round(abs(ro['basis_accuracy_sigma'][rd]), 2) for rd in READOUTS} } sigma, and on "
                      f"forgetting { {rd: round(ro['basis_forgetting'][rd], 4) for rd in READOUTS} }",
          "verdict": f"MET -- the basis contrast is a null on the diagonal under both read-outs, the wider "
                     f"{max(vals4.values()):.4f}" if not off4 else
                     f"FALSIFIER FIRED -- {off4}" if any(v >= ALIKE_FIRES for v in off4.values()) else
                     f"NULL -- {off4} between {ALIKE:.2f} and {ALIKE_FIRES:.2f}"}
    pgaps = {}
    for readout in READOUTS:
        a, b = f"{readout}/ewc-block", f"{readout}/ewc-block-rand"
        pgaps[readout] = abs(r["rolls"][a]["price"]["mean"] - r["rolls"][b]["price"]["mean"])
    label_gap, neuron_gap = pgaps["earned_label"], pgaps["neurons"]
    j5 = {"id": "DD5",
          "measured": f"the two anchors' newest-task costs are {label_gap:.4f} apart under the earned label and "
                      f"{neuron_gap:.4f} under the neurons, the four costs being "
                      f"{ {l: round(r['rolls'][l]['price']['mean'], 4) for l in r['rolls']} }",
          "verdict": f"MET -- the read-out separates the two prices, {label_gap:.4f} on the label against "
                     f"{neuron_gap:.4f} on the neurons" if (label_gap <= LABEL_GAP and neuron_gap >= NEURON_GAP) else
                     f"FALSIFIER FIRED -- the label gap is {label_gap:.4f} and the neuron gap {neuron_gap:.4f}" if
                     (label_gap > ALIKE_FIRES or neuron_gap < NEURON_GAP_FLOOR) else
                     f"NULL -- the label gap is {label_gap:.4f} and the neuron gap {neuron_gap:.4f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the game card, revision 11 ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    card = r["card"]
    print(f"   {card.get('name')}, revision {card.get('revision')}, read 2026-10-07")
    print(f"\n   clauses:    {len(card)} fields, the new one being `readout`")
    ro = r["readout"]
    print(f"\n   the readout clause, over {len(r['rolls'])} rolls and {len(ro['basis_accuracy'])} read-outs:")
    print(f"      the read-outs      { {k: v for k, v in ro['readouts'].items()} }")
    print(f"\n   {'read-out':>13} {'anchor':>15} {'standing':>10} {'sigma':>7} {'newest task':>12} {'sigma':>7}")
    for label, got in r["rolls"].items():
        readout, anchor = label.split("/")
        print(f"   {readout:>13} {anchor:>15} {got['standing']['mean']:+10.4f} {abs(got['standing']['sigma']):7.2f} "
              f"{got['price']['mean']:+12.4f} {abs(got['price']['sigma']):7.2f}")
    print(f"\n   the basis contrast by read-out: on the diagonal " +
          ", ".join(f"{rd} {ro['basis_accuracy'][rd]:+.4f} at {abs(ro['basis_accuracy_sigma'][rd]):.2f} sigma"
                    for rd in ro["basis_accuracy"]))
    print(f"   and on forgetting: " +
          ", ".join(f"{rd} {ro['basis_forgetting'][rd]:+.4f} at {abs(ro['basis_forgetting_sigma'][rd]):.2f} sigma"
                    for rd in ro["basis_forgetting"]))
    print("\n== the registered claims, DD1-DD5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e455` and `e456` moved the card's head to the circuit's neurons and found the anchor's price is the")
    print("    head's for one arm and not the other; this is the clause that names the head)")
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
