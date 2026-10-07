"""E461 -- the game card, revision 13: the pair clause, because revision 12's `head` clause carries one arm and the pair is now measured.

`e458` and `e460` completed the fifth cell of the card's world's head table and the pair is now measured at **all three
heads**: `ewc-block` and `ewc-block-rand` at the world's own state in eight columns, at the circuit's neurons in
thirty-two, and at the neurons in eight. Revision 12's `head` clause carries **one** arm's standing and price at the three
heads, and `e460` said what that leaves out: the two anchors' prices agree at **both** eight-column heads (**0.0042** apart
on the world's state and **0.0021** at the neurons) and separate at the wide one (**0.0208**), while their **standings**
separate at the narrow *neuron* head (**0.0288**) and not at the wide one (**0.0083**). **So the card's own account of its
headline question is one arm's**, and the pair is what the question is about.

**This unit writes revision 13.** One clause is added, the **pair**, carrying the six cells recomputed from the six
rolls, and every other field is checked equal to `e459`'s card rather than quoted. Five claims, registered before this
unit's pass over the six.

- **DH1 -- and the twelfth revision is carried unchanged where it is not rewritten.** Every field of `e459`'s card except
  the revision and the new clause is equal to the revision-12 card, with the revision now **13**. **Falsifier**: any other
  field differing, or the revision not 13; refused when the revision-12 artifact is absent.
- **DH2 -- and the clause's numbers come out of the six rolls.** Each head's width and source, each anchor's standing and
  price with their sigmas at each head, and the three basis contrasts on the diagonal with theirs equal the six rolls
  recomputed. **Falsifier**: any number disagreeing by more than a thousandth of a point; refused when a roll is absent.
- **DH3 -- and the pair's prices agree at the eight-column heads and not at the wide one.** The two anchors' newest-task
  costs differ by at most **0.05** at each eight-column head and by at least **0.02** at the thirty-two column one.
  **Falsifier**: an eight-column gap above **0.10**, or the wide gap below **0.01**.
- **DH4 -- and the pair's standings separate at the narrow neuron head and not at the wide one.** The standing gap is at
  least **0.02** at the neurons' eight and at most **0.05** at the neurons' thirty-two. **Falsifier**: the narrow gap
  below **0.01**, or the wide gap above **0.10**.
- **DH5 -- and the basis contrast is a null on the diagonal at all three heads.** Its magnitude is at most **0.05** at
  each. **Falsifier**: **0.10** or more at either; **null**: between.

**What it can do beyond that.** It is the card's own statement of the pair across the heads, and it makes the two
corrections revisions 11 and 12 had to make unnecessary for a reader who starts here: the **price** is the head's
**width**'s for the pair, the **standing** is unresolved for both arms at four of the six cells, and which head separates
the pair depends on which of the two numbers is read -- the prices at thirty-two columns, the standings at the eight
neuron ones. Read with the `readout` and `head` clauses it is the whole of what this line has measured about the pair's
dependence on the head.

**What it cannot do.** *Six cells of one world*, so other worlds are not in the clause. *And two heads are not a width
ladder*: the eight-column heads differ from the thirty-two column one by a factor of four, and the widths between them are
not measured. *And one cell each*: the card's world at twenty replicates, so a gap at **0.0021** against one at **0.0208**
is a pair two redraws could narrow. *And a clause is not a result*: DH1 shows revision 12 survives into revision 13 and
not that revision 12 was right, and DH2 shows the clause agrees with the six rolls and not that the six should be
believed.
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
CARD12 = Path("runs/e459_the_game_card_revision_twelve.json")
#: the six rolls, by head and anchor
ROLLS = {
    "world_eight/ewc-block": Path("runs/e438_earned_label_three_arms_20reps.json"),
    "world_eight/ewc-block-rand": Path("runs/e439_earned_label_rand_20reps.json"),
    "neurons_thirty_two/ewc-block": Path("runs/e455_earned_label_neurons_20reps.json"),
    "neurons_thirty_two/ewc-block-rand": Path("runs/e456_earned_label_rand_neurons_20reps.json"),
    "neurons_eight/ewc-block": Path("runs/e458_earned_label_neurons8_20reps.json"),
    "neurons_eight/ewc-block-rand": Path("runs/e460_earned_label_rand_neurons8_20reps.json"),
}
HEADS = {
    "world_eight": {"width": 8, "source": "the world's own state", "from_world": True},
    "neurons_thirty_two": {"width": 32, "source": "the circuit's own neurons", "from_world": False},
    "neurons_eight": {"width": 8, "source": "the circuit's own neurons", "from_world": False},
}
ANCHORS = ("ewc-block", "ewc-block-rand")
BASELINE = "naive"
BUFFER = "replay"
REVISION = 13
NEW = ("revision", "pair")
N_TASKS = 3
MIN_REPS = 20
ALIKE = 0.05
ALIKE_FIRES = 0.10
WIDE_GAP = 0.02
WIDE_GAP_FLOOR = 0.01
TOL = 0.002
CLAIMS = (
    ("DH1", "and the twelfth revision is carried unchanged where it is not rewritten",
     "Every field of `e459`'s card except the revision and the new clause is equal to the revision-12 card, with the "
     "revision now 13",
     "falsifier: any other field differing, or the revision not 13; refused when `e459`'s artifact is absent"),
    ("DH2", "and the clause's numbers come out of the six rolls",
     "Each head's width and source, each anchor's standing and price with their sigmas at each head, and the three basis "
     "contrasts on the diagonal with theirs equal the six rolls recomputed",
     "falsifier: any number disagreeing by more than a thousandth of a point; refused when a roll is absent"),
    ("DH3", f"and the pair's prices agree at the eight-column heads and not at the wide one, within {ALIKE:.2f} against at least {WIDE_GAP:.2f}",
     "The two anchors' newest-task costs differ by at most 0.05 at each eight-column head and by at least 0.02 at the "
     "thirty-two column one",
     f"falsifier: an eight-column gap above {ALIKE_FIRES:.2f}, or the wide gap below {WIDE_GAP_FLOOR:.2f}"),
    ("DH4", "and the pair's standings separate at the narrow neuron head and not at the wide one",
     "The standing gap is at least 0.02 at the neurons' eight and at most 0.05 at the neurons' thirty-two",
     f"falsifier: the narrow gap below {WIDE_GAP_FLOOR:.2f}, or the wide gap above {ALIKE_FIRES:.2f}"),
    ("DH5", f"and the basis contrast is a null on the diagonal at all three heads, within {ALIKE:.2f}",
     "Its magnitude is at most 0.05 at each",
     f"falsifier: {ALIKE_FIRES:.2f} or more at either; null: between"),
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
    reps = (methods.get(anchor) or {}).get("replicates") or []
    base = (methods.get(BASELINE) or {}).get("replicates") or []
    if not reps or not base:
        return None
    arms = {anchor: {"diagonal": [statistics.fmean(r["final_per_task"]) for r in reps],
                     "last": [r["final_per_task"][-1] for r in reps], "replicates": len(reps)},
            BASELINE: {"diagonal": [statistics.fmean(r["final_per_task"]) for r in base],
                       "last": [r["final_per_task"][-1] for r in base], "replicates": len(base)}}
    tasks = doc.get("tasks") or []
    return {"artifact": path.name, "anchor": anchor, "arms": arms,
            "readouts": [t.get("n_readout") if isinstance(t, dict) else None for t in tasks],
            "from_world": (doc.get("config") or {}).get("readout_from_world")}


def reading(card12: Path = CARD12, rolls: dict = ROLLS) -> dict:
    out = {"ok": True, "reason": None, "card": None, "revision12": {}, "pair": {}, "rolls": {}}
    base = load(card12)
    if not base:
        return {**out, "ok": False, "reason": f"{card12} is absent, so revision 12 is not on disk"}
    old = base.get("card") or {}
    card = copy.deepcopy(old)
    card["revision"] = REVISION
    out["revision12"] = {k: v for k, v in old.items() if k not in NEW}

    for label, path in rolls.items():
        head, anchor = label.split("/")
        got = _roll(path, anchor)
        if got is None:
            return {**out, "ok": False, "reason": f"{path} is absent or carries no {anchor} arm"}
        arms = got["arms"]
        out["rolls"][label] = {"artifact": got["artifact"], "head": head, "anchor": anchor,
                               "replicates": min(v["replicates"] for v in arms.values()),
                               "standing": _paired(arms[anchor]["diagonal"], arms[BASELINE]["diagonal"]),
                               "price": _paired(arms[anchor]["last"], arms[BASELINE]["last"]),
                               "width": got["readouts"][0] if got["readouts"] else None,
                               "from_world": got["from_world"]}
    basis = {}
    for head in HEADS:
        a, b = f"{head}/ewc-block", f"{head}/ewc-block-rand"
        if a not in out["rolls"] or b not in out["rolls"]:
            return {**out, "ok": False, "reason": f"the {head} head carries only one anchor"}
        da = load(ROLLS[a])["methods"]["ewc-block"]["replicates"]
        db = load(ROLLS[b])["methods"]["ewc-block-rand"]["replicates"]
        basis[head] = {"accuracy": _paired([statistics.fmean(r["final_per_task"]) for r in da],
                                           [statistics.fmean(r["final_per_task"]) for r in db])}
    card["pair"] = {
        "artifact": [out["rolls"][l]["artifact"] for l in out["rolls"]],
        "heads": {h: dict(HEADS[h]) for h in HEADS},
        "buffer": BUFFER,
        "anchors": list(ANCHORS),
        "anchor_over_naive": {l: out["rolls"][l]["standing"]["mean"] for l in out["rolls"]},
        "anchor_over_naive_sigma": {l: out["rolls"][l]["standing"]["sigma"] for l in out["rolls"]},
        "newest_task": {l: out["rolls"][l]["price"]["mean"] for l in out["rolls"]},
        "newest_task_sigma": {l: out["rolls"][l]["price"]["sigma"] for l in out["rolls"]},
        "basis_accuracy": {h: basis[h]["accuracy"]["mean"] for h in basis},
        "basis_accuracy_sigma": {h: basis[h]["accuracy"]["sigma"] for h in basis},
    }
    out["pair"] = dict(card["pair"])
    out["basis"] = basis
    out["card"] = card
    return out



def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the clause is read from is absent"}
                for c in CLAIMS]
    card, p = r["card"], r["pair"]
    same = {k: (card.get(k) == v) for k, v in r["revision12"].items()}
    j1 = {"id": "DH1",
          "measured": f"the revision-12 card's {len(same)} fields against the revision-13 card: "
                      f"{len(same) - sum(1 for v in same.values() if not v)} equal, with the revision now "
                      f"{card.get('revision')}",
          "verdict": f"MET -- the twelfth revision is carried unchanged in all {len(same)} fields it does not rewrite" if
                     (all(same.values()) and card.get("revision") == REVISION) else
                     f"FALSIFIER FIRED -- { {k: v for k, v in same.items() if not v} } differs"}
    bad2 = {}
    for label, got in r["rolls"].items():
        if p["heads"].get(got["head"], {}).get("width") != got["width"]:
            bad2[f"{label}/width"] = (p["heads"].get(got["head"]), got["width"])
        for key, field in (("anchor_over_naive", "standing"), ("anchor_over_naive_sigma", "standing"),
                           ("newest_task", "price"), ("newest_task_sigma", "price")):
            want = got[field]["mean"] if not key.endswith("sigma") else got[field]["sigma"]
            carried = p[key].get(label)
            if carried is None or abs(carried - want) > TOL:
                bad2[f"{label}/{key}"] = (carried, want)
    for head, got in r["basis"].items():
        for key, field in (("basis_accuracy", "accuracy"), ("basis_accuracy_sigma", "accuracy")):
            want = got[field]["mean"] if not key.endswith("sigma") else got[field]["sigma"]
            carried = p[key].get(head)
            if carried is None or abs(carried - want) > TOL:
                bad2[f"{head}/{key}"] = (carried, want)
    j2 = {"id": "DH2",
          "measured": f"the clause's prices are "
                      f"{ {l: round(v, 4) for l, v in p['newest_task'].items()} } at "
                      f"{ {l: round(abs(v), 2) for l, v in p['newest_task_sigma'].items()} } sigma and its standings "
                      f"{ {l: round(v, 4) for l, v in p['anchor_over_naive'].items()} }, with the basis contrasts "
                      f"{ {h: round(v, 4) for h, v in p['basis_accuracy'].items()} }",
          "verdict": "MET -- the clause's numbers are the six rolls' own" if not bad2 else
                     f"FALSIFIER FIRED -- {bad2}"}
    pgaps = {}
    for head in HEADS:
        a, b = f"{head}/ewc-block", f"{head}/ewc-block-rand"
        pgaps[head] = abs(r["rolls"][a]["price"]["mean"] - r["rolls"][b]["price"]["mean"])
    eight_ok = all(v <= ALIKE for k, v in pgaps.items() if HEADS[k]["width"] == 8)
    wide_ok = pgaps["neurons_thirty_two"] >= WIDE_GAP
    j3 = {"id": "DH3",
          "measured": f"the pair's newest-task costs are { {k: round(v, 4) for k, v in pgaps.items()} } apart by head, "
                      f"the four costs being { {l: round(r['rolls'][l]['price']['mean'], 4) for l in r['rolls']} }",
          "verdict": f"MET -- the prices agree at both eight-column heads (the wider "
                     f"{max(v for k, v in pgaps.items() if HEADS[k]['width'] == 8):.4f}) and separate at the wide one "
                     f"({pgaps['neurons_thirty_two']:.4f})" if (eight_ok and wide_ok) else
                     f"FALSIFIER FIRED -- eight-column gaps { {k: v for k, v in pgaps.items() if HEADS[k]['width'] == 8} }, "
                     f"wide {pgaps['neurons_thirty_two']:.4f}" if
                     (any(v > ALIKE_FIRES for k, v in pgaps.items() if HEADS[k]["width"] == 8) or
                      pgaps["neurons_thirty_two"] < WIDE_GAP_FLOOR) else
                     f"NULL -- the gaps are { {k: round(v, 4) for k, v in pgaps.items()} }"}
    sgaps = {}
    for head in HEADS:
        a, b = f"{head}/ewc-block", f"{head}/ewc-block-rand"
        sgaps[head] = abs(r["rolls"][a]["standing"]["mean"] - r["rolls"][b]["standing"]["mean"])
    narrow_ok = sgaps["neurons_eight"] >= WIDE_GAP
    wide_ok2 = sgaps["neurons_thirty_two"] <= ALIKE
    j4 = {"id": "DH4",
          "measured": f"the pair's standings are { {k: round(v, 4) for k, v in sgaps.items()} } apart by head, the six "
                      f"standings being "
                      f"{ {l: round(r['rolls'][l]['standing']['mean'], 4) for l in r['rolls']} }",
          "verdict": f"MET -- the standings separate at the neurons' eight ({sgaps['neurons_eight']:.4f}) and not at the "
                     f"neurons' thirty-two ({sgaps['neurons_thirty_two']:.4f})" if (narrow_ok and wide_ok2) else
                     f"FALSIFIER FIRED -- the narrow gap is {sgaps['neurons_eight']:.4f} and the wide one "
                     f"{sgaps['neurons_thirty_two']:.4f}" if
                     (sgaps["neurons_eight"] < WIDE_GAP_FLOOR or sgaps["neurons_thirty_two"] > ALIKE_FIRES) else
                     f"NULL -- the gaps are { {k: round(v, 4) for k, v in sgaps.items()} }"}
    vals = {h: abs(v) for h, v in p["basis_accuracy"].items()}
    over = {k: v for k, v in vals.items() if v > ALIKE}
    j5 = {"id": "DH5",
          "measured": f"the basis contrast on the diagonal is "
                      f"{ {h: round(p['basis_accuracy'][h], 4) for h in p['basis_accuracy']} } at "
                      f"{ {h: round(abs(p['basis_accuracy_sigma'][h]), 2) for h in p['basis_accuracy_sigma']} } sigma",
          "verdict": f"MET -- the basis contrast is a null at all three heads, the wider {max(vals.values()):.4f}" if
                     not over else
                     f"FALSIFIER FIRED -- {over}" if any(v >= ALIKE_FIRES for v in over.values()) else
                     f"NULL -- {over} between {ALIKE:.2f} and {ALIKE_FIRES:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the game card, revision 13 ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    card = r["card"]
    print(f"   {card.get('name')}, revision {card.get('revision')}, read 2026-10-07")
    print(f"\n   clauses:    {len(card)} fields, the new one being `pair`")
    p = r["pair"]
    print(f"\n   the pair clause, over {len(r['rolls'])} cells of the card's own world's head table:")
    print(f"\n   {'head':>20} {'width':>6} {'reads':>28} {'anchor':>15} {'standing':>10} {'sigma':>7} "
          f"{'newest task':>12} {'sigma':>7}")
    for label, got in r["rolls"].items():
        head = got["head"]
        print(f"   {head:>20} {got['width']:>6} {HEADS[head]['source']:>28} {got['anchor']:>15} "
              f"{got['standing']['mean']:+10.4f} {abs(got['standing']['sigma']):7.2f} "
              f"{got['price']['mean']:+12.4f} {abs(got['price']['sigma']):7.2f}")
    print(f"\n   the basis contrast by head: " +
          ", ".join(f"{h} {p['basis_accuracy'][h]:+.4f} at {abs(p['basis_accuracy_sigma'][h]):.2f} sigma"
                    for h in p["basis_accuracy"]))
    pg, sg = {}, {}
    for head in HEADS:
        a, b = f"{head}/ewc-block", f"{head}/ewc-block-rand"
        pg[head] = abs(r["rolls"][a]["price"]["mean"] - r["rolls"][b]["price"]["mean"])
        sg[head] = abs(r["rolls"][a]["standing"]["mean"] - r["rolls"][b]["standing"]["mean"])
    print(f"\n   the pair apart by head -- prices { {k: round(v, 4) for k, v in pg.items()} }, standings "
          f"{ {k: round(v, 4) for k, v in sg.items()} }")
    print("\n== the registered claims, DH1-DH5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e460` completed the fifth cell and said the card's `head` clause is one arm's while the question is the")
    print("    pair's; this is the clause that carries the pair across all three heads)")
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
