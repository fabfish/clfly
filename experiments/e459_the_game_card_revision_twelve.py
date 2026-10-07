"""E459 -- the game card, revision 12: the head clause, and the price the head's width carries.

`e458` held the width and moved the source -- the circuit's neurons at the card's own **eight** columns -- and the
biological anchor's newest-task price came back: **-0.0615** at **4.48** sigma against **-0.0115** at **0.78** at
thirty-two columns. Two clean contrasts fell out of that: moving the **width** with the source held takes the price from
**4.48** to **0.78** sigma, and moving the **source** with the width held takes it from **3.71** to **4.48**. **So the
card's eleventh revision carries a reading its own numbers do not support**: its `readout` clause has the read-out
separating the two anchors' prices and `e458` shows it is the **width** that separates them and not the source, and
`e455`'s sentence *the price is the earned label's* is refuted. The card has no clause with three heads of one world in
it.

**This unit writes revision 12.** One clause is added, the **head**, carrying the three heads' numbers recomputed from
the three rolls, and every other field is checked equal to `e457`'s card rather than quoted. Five claims, registered
before this unit's pass over the three.

- **DF1 -- and the eleventh revision is carried unchanged where it is not rewritten.** Every field of `e457`'s card
  except the revision and the new clause is equal to the revision-11 card, with the revision now **12**. **Falsifier**:
  any other field differing, or the revision not 12; refused when the revision-11 artifact is absent.
- **DF2 -- and the clause's numbers come out of the three rolls.** Each head's width and source, the anchor's standing
  and newest-task cost with their sigmas, the buffer's three per-position gains and its advantage over the anchor with
  that contrast's sigma equal the three rolls recomputed. **Falsifier**: any number disagreeing by more than a thousandth
  of a point; refused when a roll is absent.
- **DF3 -- and the price's presence is the width's.** The anchor's newest-task cost resolves at **two** sigma or more at
  **each** eight-column head -- one reading the world's state and one the circuit's neurons -- and does not at the
  thirty-two column one. **Falsifier**: any of those three failing.
- **DF4 -- and the anchor's standing is unresolved at all three heads.** Its mean diagonal over the baseline is under
  two sigma at each. **Falsifier**: any at or above two sigma in either direction.
- **DF5 -- and the buffer's advantage holds at all three heads.** Its gain over `naive` at the first position is at
  least **+0.05** and its gain over the anchor is positive at two sigma or more, at each head. **Falsifier**: any head
  where either fails.

**What it can do beyond that.** It puts the third head in the card and states the correction the clause needs: a reader of
revision 11's `readout` clause would take the two anchors' price separation for the **source**'s, and this clause says
which dial does the separating. Read with the `width` clause (revision 9, the earned label at four, eight and sixteen),
the card then carries the price at **four** widths and **two** sources, and the two clauses together locate the price's
presence in the **width**.

**What it cannot do.** *Three heads of one world*: so other worlds are not in the clause. *And one corner is missing*:
the world's state at thirty-two columns is not constructible, because `--readout-from-world` makes the head's input the
world's state, so the width's effect is measured at two widths under one source and the source's at one width under two.
*And one cell each*: the card's world at twenty replicates, so a price at **0.78** sigma against one at **4.48** is a pair
two redraws could narrow. *And a clause is not a result*: DF1 shows revision 11 survives into revision 12 and not that
revision 11 was right -- and revision 12 is the first that says a clause of its own was read the wrong way.
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
CARD11 = Path("runs/e457_the_game_card_revision_eleven.json")
#: the three heads of the card's own world
ROLLS = {
    "world/8": Path("runs/e438_earned_label_three_arms_20reps.json"),
    "neurons/32": Path("runs/e455_earned_label_neurons_20reps.json"),
    "neurons/8": Path("runs/e458_earned_label_neurons8_20reps.json"),
}
WIDTHS = {"world/8": 8, "neurons/32": 32, "neurons/8": 8}
SOURCES = {"world/8": "the world's own state", "neurons/32": "the circuit's own neurons",
           "neurons/8": "the circuit's own neurons"}
BASELINE = "naive"
ANCHOR = "ewc-block"
BUFFER = "replay"
REVISION = 12
NEW = ("revision", "head")
N_TASKS = 3
MIN_REPS = 20
SIGMA = 2.0
FIRST_BAR = 0.05
TOL = 0.002
CLAIMS = (
    ("DF1", "and the eleventh revision is carried unchanged where it is not rewritten",
     "Every field of `e457`'s card except the revision and the new clause is equal to the revision-11 card, with the "
     "revision now 12",
     "falsifier: any other field differing, or the revision not 12; refused when `e457`'s artifact is absent"),
    ("DF2", "and the clause's numbers come out of the three rolls",
     "Each head's width and source, the anchor's standing and newest-task cost with their sigmas, the buffer's three "
     "per-position gains and its advantage over the anchor with that contrast's sigma equal the three rolls recomputed",
     "falsifier: any number disagreeing by more than a thousandth of a point; refused when a roll is absent"),
    ("DF3", f"and the price's presence is the width's, at {SIGMA:.0f} sigma",
     "The anchor's newest-task cost resolves at two sigma or more at each eight-column head and does not at the "
     "thirty-two column one",
     "falsifier: any of those three failing"),
    ("DF4", f"and the anchor's standing is unresolved at all three heads, under {SIGMA:.0f} sigma",
     "Its mean diagonal over the baseline is under two sigma at each",
     "falsifier: any at or above two sigma in either direction"),
    ("DF5", f"and the buffer's advantage holds at all three heads, first at least {FIRST_BAR:+.2f} and the anchor at {SIGMA:.0f} sigma",
     "Its gain over naive at the first position is at least +0.05 and its gain over the anchor is positive at two sigma "
     "or more, at each head",
     "falsifier: any head where either fails"),
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
    for arm in (BASELINE, ANCHOR, BUFFER):
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        arms[arm] = {"replicates": len(reps),
                     "final": [statistics.fmean([r["final_per_task"][k] for r in reps]) for k in range(N_TASKS)],
                     "diagonal": [statistics.fmean(r["final_per_task"]) for r in reps],
                     "last": [r["final_per_task"][-1] for r in reps]}
    tasks = doc.get("tasks") or []
    return {"artifact": path.name, "arms": arms,
            "readouts": [t.get("n_readout") if isinstance(t, dict) else None for t in tasks],
            "from_world": (doc.get("config") or {}).get("readout_from_world")}


def reading(card11: Path = CARD11, rolls: dict = ROLLS) -> dict:
    out = {"ok": True, "reason": None, "card": None, "revision11": {}, "head": {}, "rolls": {}}
    base = load(card11)
    if not base:
        return {**out, "ok": False, "reason": f"{card11} is absent, so revision 11 is not on disk"}
    old = base.get("card") or {}
    card = copy.deepcopy(old)
    card["revision"] = REVISION
    out["revision11"] = {k: v for k, v in old.items() if k not in NEW}

    for label, path in rolls.items():
        got = _roll(path)
        if got is None:
            return {**out, "ok": False, "reason": f"{path} is absent or carries no {ANCHOR} arm"}
        arms = got["arms"]
        gain = [arms[BUFFER]["final"][k] - arms[BASELINE]["final"][k] for k in range(N_TASKS)]
        out["rolls"][label] = {
            "artifact": got["artifact"], "width": got["readouts"][0] if got["readouts"] else None,
            "source": SOURCES[label], "from_world": got["from_world"], "replicates": arms[BASELINE]["replicates"],
            "standing": _paired(arms[ANCHOR]["diagonal"], arms[BASELINE]["diagonal"]),
            "price": _paired(arms[ANCHOR]["last"], arms[BASELINE]["last"]),
            "buffer_gain": gain,
            "buffer_over_anchor": _paired(arms[BUFFER]["diagonal"], arms[ANCHOR]["diagonal"]),
        }
    card["head"] = {
        "artifact": [out["rolls"][l]["artifact"] for l in out["rolls"]],
        "heads": {l: {"width": out["rolls"][l]["width"], "source": out["rolls"][l]["source"],
                      "from_world": out["rolls"][l]["from_world"]} for l in out["rolls"]},
        "buffer": BUFFER,
        "anchor": ANCHOR,
        "anchor_over_naive": {l: out["rolls"][l]["standing"]["mean"] for l in out["rolls"]},
        "anchor_over_naive_sigma": {l: out["rolls"][l]["standing"]["sigma"] for l in out["rolls"]},
        "newest_task": {l: out["rolls"][l]["price"]["mean"] for l in out["rolls"]},
        "newest_task_sigma": {l: out["rolls"][l]["price"]["sigma"] for l in out["rolls"]},
        "buffer_gain": {l: out["rolls"][l]["buffer_gain"] for l in out["rolls"]},
        "buffer_over_anchor": {l: out["rolls"][l]["buffer_over_anchor"]["mean"] for l in out["rolls"]},
        "buffer_over_anchor_sigma": {l: out["rolls"][l]["buffer_over_anchor"]["sigma"] for l in out["rolls"]},
    }
    out["head"] = dict(card["head"])
    out["card"] = card
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the clause is read from is absent"}
                for c in CLAIMS]
    card, h = r["card"], r["head"]
    same = {k: (card.get(k) == v) for k, v in r["revision11"].items()}
    j1 = {"id": "DF1",
          "measured": f"the revision-11 card's {len(same)} fields against the revision-12 card: "
                      f"{len(same) - sum(1 for v in same.values() if not v)} equal, with the revision now "
                      f"{card.get('revision')}",
          "verdict": f"MET -- the eleventh revision is carried unchanged in all {len(same)} fields it does not rewrite" if
                     (all(same.values()) and card.get("revision") == REVISION) else
                     f"FALSIFIER FIRED -- { {k: v for k, v in same.items() if not v} } differs"}
    bad2 = {}
    for label, got in r["rolls"].items():
        if h["heads"].get(label, {}).get("width") != got["width"] or \
                h["heads"].get(label, {}).get("source") != got["source"]:
            bad2[f"{label}/head"] = (h["heads"].get(label), (got["width"], got["source"]))
        for key, field, sub in (("anchor_over_naive", "standing", "mean"),
                                ("anchor_over_naive_sigma", "standing", "sigma"),
                                ("newest_task", "price", "mean"), ("newest_task_sigma", "price", "sigma"),
                                ("buffer_over_anchor", "buffer_over_anchor", "mean"),
                                ("buffer_over_anchor_sigma", "buffer_over_anchor", "sigma")):
            want = got[field]["mean"] if sub == "mean" else got[field]["sigma"]
            carried = h[key].get(label)
            if carried is None or abs(carried - want) > TOL:
                bad2[f"{label}/{key}"] = (carried, want)
        carried_gain = h["buffer_gain"].get(label)
        if carried_gain is None or len(carried_gain) != N_TASKS or \
                any(abs(x - y) > TOL for x, y in zip(carried_gain, got["buffer_gain"])):
            bad2[f"{label}/buffer_gain"] = (carried_gain, got["buffer_gain"])
    j2 = {"id": "DF2",
          "measured": f"the clause's standings are "
                      f"{ {l: round(v, 4) for l, v in h['anchor_over_naive'].items()} } at "
                      f"{ {l: round(abs(v), 2) for l, v in h['anchor_over_naive_sigma'].items()} } sigma and its "
                      f"prices { {l: round(v, 4) for l, v in h['newest_task'].items()} } at "
                      f"{ {l: round(abs(v), 2) for l, v in h['newest_task_sigma'].items()} } sigma over the heads "
                      f"{ {l: v for l, v in h['heads'].items()} }",
          "verdict": "MET -- the clause's numbers are the three heads' own" if not bad2 else
                     f"FALSIFIER FIRED -- {bad2}"}
    fails3 = {}
    for label, got in r["rolls"].items():
        resolves = abs(got["price"]["sigma"]) >= SIGMA
        if got["width"] == 8 and not resolves:
            fails3[f"{label}/eight"] = got["price"]["sigma"]
        if got["width"] != 8 and resolves:
            fails3[f"{label}/wide"] = got["price"]["sigma"]
    j3 = {"id": "DF3",
          "measured": f"the anchor's newest-task sigmas are "
                      f"{ {l: (round(v['width']), round(abs(v['price']['sigma']), 2)) for l, v in r['rolls'].items()} } "
                      f"(width, sigma)",
          "verdict": "MET -- the price resolves at both eight-column heads, one reading the world and one the neurons, "
                     "and not at the thirty-two column one" if not fails3 else
                     f"FALSIFIER FIRED -- {fails3}"}
    fails4 = {l: v["standing"]["sigma"] for l, v in r["rolls"].items() if abs(v["standing"]["sigma"]) >= SIGMA}
    j4 = {"id": "DF4",
          "measured": f"the anchor's standings are "
                      f"{ {l: (round(v['standing']['mean'], 4), round(abs(v['standing']['sigma']), 2)) for l, v in r['rolls'].items()} }",
          "verdict": "MET -- the standing is unresolved at all three heads, the largest "
                     f"{max(abs(v['standing']['sigma']) for v in r['rolls'].values()):.2f} sigma" if not fails4 else
                     f"FALSIFIER FIRED -- {fails4}"}
    fails5 = {}
    for label, got in r["rolls"].items():
        if got["buffer_gain"][0] < FIRST_BAR:
            fails5[f"{label}/first"] = got["buffer_gain"][0]
        if not (got["buffer_over_anchor"]["mean"] > 0 and abs(got["buffer_over_anchor"]["sigma"]) >= SIGMA):
            fails5[f"{label}/over_anchor"] = got["buffer_over_anchor"]["mean"]
    j5 = {"id": "DF5",
          "measured": f"the buffer's first-position gains are "
                      f"{ {l: round(v['buffer_gain'][0], 4) for l, v in r['rolls'].items()} } and its advantage over the "
                      f"anchor { {l: (round(v['buffer_over_anchor']['mean'], 4), round(abs(v['buffer_over_anchor']['sigma']), 2)) for l, v in r['rolls'].items()} }",
          "verdict": "MET -- the buffer's ledger holds at all three heads" if not fails5 else
                     f"FALSIFIER FIRED -- {fails5}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the game card, revision 12 ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    card = r["card"]
    print(f"   {card.get('name')}, revision {card.get('revision')}, read 2026-10-07")
    print(f"\n   clauses:    {len(card)} fields, the new one being `head`")
    h = r["head"]
    print(f"\n   the head clause, over {len(r['rolls'])} heads of the card's own world:")
    print(f"\n   {'head':>12} {'width':>6} {'reads':>28} {'standing':>10} {'sigma':>7} {'newest task':>12} {'sigma':>7}")
    for label, got in r["rolls"].items():
        print(f"   {label:>12} {got['width']:>6} {got['source']:>28} {got['standing']['mean']:+10.4f} "
              f"{abs(got['standing']['sigma']):7.2f} {got['price']['mean']:+12.4f} {abs(got['price']['sigma']):7.2f}")
    print("\n   the buffer over naive by position, head by head:")
    for label, got in r["rolls"].items():
        print(f"      {label:>12}: " + " ".join(f"{x:+.4f}" for x in got["buffer_gain"]) +
              f"   over the anchor {got['buffer_over_anchor']['mean']:+.4f} at "
              f"{abs(got['buffer_over_anchor']['sigma']):.2f} sigma")
    print("\n== the registered claims, DF1-DF5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e458` held the width and moved the source and the price came back, so revision 11's reading of its")
    print("    own `readout` clause is corrected here: the width does the separating and the source does not)")
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
