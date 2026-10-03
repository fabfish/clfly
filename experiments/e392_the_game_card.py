"""E392 -- the game card: the closed-loop benchmark written down and checked, clause by clause.

`e387` read the window as one setting and published the fields that define it and the fields the line moves. It
stopped at consistency: *"it audits consistency and not correctness -- two dozen units agreeing on a field says the
corpus is one setting and says nothing about whether the setting is the right one."* And the plan's own benchmark
block, **FlyCL v0**, was written on 2026-09-25 and describes the three sustained classification tasks; the closed
loop, the world, the earned label and thirty units of setting work are all newer than it. What the repository has
never had is the game **written down as a thing a reader can hold** -- the substrate, the loop, the protocol, the
arms, the metrics and, just as load-bearing, what it does not have.

**This unit writes it down and checks every clause against the corpus.** The card is a dictionary in this module;
each of its clauses is either carried by artifacts that exist or is an absence measured over the whole corpus. No
training is run.

Five claims, registered before this unit read the corpus for them.

- **M1 -- and the substrate clause is carried and constant.** Over every closed-loop artifact under `runs/` the
  circuit, the read-out draw, the basis, the circuit's size, the class count and the seed stream each take exactly
  one value, and each of those values is the card's. **Falsifier**: any of them differing between two artifacts, or
  disagreeing with the card. **Bound**: the window holds at least **30** artifacts, a count that grows with the
  corpus and is asserted as a bound.
- **M2 -- and the loop clause is carried by a cell.** At least **20** artifacts realise the card's loop clause --
  the cue at step **0**, the world's drive reading the **action** population, the world at **8** dimensions, coupled
  with leak **0.35**, linear, and the head reading the world. **Falsifier**: fewer, which would say the card
  describes a cell the corpus barely ran.
- **M3 -- and the protocol clause is carried by that cell.** Every artifact of the cell ran the card's three tasks
  **in the card's order**, at the card's split and the card's class count. **Falsifier**: any ordering, split or
  class count differing.
- **M4 -- and every metric the card names is computable in every artifact of the cell.** Each of them ran both of
  the card's arms and carries a retention matrix for each, so the accuracy, the matrix's diagonal, its last row and
  their difference are all readable in each one. **Falsifier**: an artifact of the cell missing an arm or a matrix,
  which would say a metric the card names cannot be computed where the card says it can.
- **M5 -- and the card's absent list is measured, in two halves.** Over the cell the world's three draws each take
  exactly **one** value, so every number the card's cell reports is conditional on **one world**; and no
  configuration key anywhere under `runs/` names a reward, a policy, an episode, a goal or a return, so the card's
  absent list is of things the corpus **cannot express** rather than of things it chose not to. **Falsifier**: a
  second world draw in the cell, or a configuration key matching one of those names. **Bound**: the scan covers at
  least **500** artifacts, a count that grows with the corpus.

**What it can do beyond that.** It is the benchmark the repository has been asked to grow toward, stated once, with
every clause tied to an artifact or to a scan: a reader can hold the card and re-derive each of its numbers from
`runs/`. The two absent clauses are the honest half -- a game with no reward and no held-out task is a benchmark of
**retention** and not of **behaviour**, and the card says so where a reader will meet it.

**What it cannot do.** *A card is a definition and not a result*: it says what the benchmark is, and every number it
publishes about performance belongs to the units that measured it. *And the cell is a choice*: the loop clause is
the wide step and the linear world, so the tight step, the cue source, the nonlinear world and the frozen bodies are
outside it and their readings are not covered by M3 and M4. *And the absences are the corpus's, not the theory's*:
no key names a reward, which does not say a reward could not be added, only that nothing in the corpus has one. *And
a card ages*: the plan's own FlyCL v0 became wrong in a month, so this one names the revision and the date it was
read.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e387_the_window_as_one_setting import load, window

RUNS = Path("runs")
#: the game, written down. Every clause is checked by a claim; the values are what the corpus carries.
CARD = {
    "name": "the closed-loop earned-label game",
    "revision": 1,
    "read": "2026-10-04",
    "substrate": {"circuit": "mb+cx+al@n952", "circuit_size": 300, "readout_subset": "59926518137c",
                  "basis": "cell_class", "support": 80, "seed0": 0, "classes_per_task": 4},
    "loop": {"cue_at": 0, "drive": "action", "world_dims": 8, "coupled": True, "leak": 0.35, "nonlinear": False,
             "readout": "world"},
    "protocol": {"tasks": ["loop_odour_identity", "loop_heading", "loop_odour_input"], "train": 96, "test": 48,
                 "lr": 0.003, "schedule": "iteration budget"},
    "arms": ["naive", "replay"],
    "metrics": ["accuracy", "the retention matrix's diagonal", "its last row", "their difference",
                "backward transfer"],
    "absent": ["a reward", "a policy", "an episode boundary", "a held-out task", "a second world", "a second draw"],
}
#: the names a configuration key would have to carry to be a reward or a policy; the card says the corpus has none
ABSENT_PATTERN = re.compile(r"reward|policy|episode|return|goal|temperature|reflex|motor", re.I)
WORLD_FIELDS = ("world_drive_sha1", "world_read_sha1", "world_coupling_sha1")
MIN_WINDOW = 30
MIN_CELL = 20
MIN_SCAN = 500
CLAIMS = (
    ("M1", f"and the substrate clause is carried and constant, over at least {MIN_WINDOW} artifacts",
     "Over every closed-loop artifact the circuit, the read-out draw, the basis, the circuit's size, the class count "
     "and the seed stream each take exactly one value, and each of those values is the card's",
     "falsifier: any of them differing between two artifacts, or disagreeing with the card"),
    ("M2", f"and the loop clause is carried by a cell of at least {MIN_CELL}",
     f"At least {MIN_CELL} artifacts realise the card's loop clause -- cue at 0, the action population driving the "
     "world, 8 dimensions, coupled with leak 0.35, linear, and the head reading the world",
     f"falsifier: fewer than {MIN_CELL}"),
    ("M3", "and the protocol clause is carried by that cell",
     "Every artifact of the cell ran the card's three tasks in the card's order, at the card's split and the card's "
     "class count",
     "falsifier: any ordering, split or class count differing"),
    ("M4", "and every metric the card names is computable in every artifact of the cell",
     "Each artifact of the cell ran both of the card's arms and carries a retention matrix for each",
     "falsifier: an artifact of the cell missing an arm or a matrix"),
    ("M5", f"and the card's absent list is measured, over at least {MIN_SCAN} artifacts",
     "Over the cell the world's three draws each take exactly one value, and no configuration key anywhere under "
     "runs/ names a reward, a policy, an episode, a goal or a return",
     "falsifier: a second world draw in the cell, or a configuration key matching one of those names"),
)


def _config(path: Path) -> dict:
    doc = load(path) or {}
    return doc.get("config") or {}


def _realises(cfg: dict, loop: dict) -> bool:
    return (int(cfg.get("loop_cue_at") or 0) == loop["cue_at"]
            and bool(cfg.get("loop_drive_from_cue")) == (loop["drive"] == "cue")
            and int(cfg.get("loop_world_dims") or 0) == loop["world_dims"]
            and bool(cfg.get("loop_world_coupled")) == loop["coupled"]
            and abs(float(cfg.get("loop_world_leak") or 0.0) - loop["leak"]) < 1e-9
            and bool(cfg.get("loop_world_nonlinear")) == loop["nonlinear"]
            and bool(cfg.get("readout_from_world"))
            and abs(float(cfg.get("lr") or 0.0) - CARD["protocol"]["lr"]) < 1e-12)


def scan(root: Path = RUNS) -> dict:
    """Every JSON under `runs/`, its configuration keys, and whether any of them names one of the absent things."""
    files, keys, hits = 0, set(), {}
    for p in sorted(Path(root).glob("*.json")):
        doc = load(p)
        if not isinstance(doc, dict):
            continue
        files += 1
        cfg = doc.get("config") or {}
        keys |= set(cfg)
        for k in cfg:
            if ABSENT_PATTERN.search(k):
                hits[k] = hits.get(k, 0) + 1
    return {"files": files, "config_keys": sorted(keys), "n_config_keys": len(keys), "absent_hits": hits}


def reading(root: Path = RUNS) -> dict:
    rows = window(root)
    invariants = {}
    for field, want in (("circuit", CARD["substrate"]["circuit"]),
                        ("readout_subset", CARD["substrate"]["readout_subset"]),
                        ("basis", CARD["substrate"]["basis"]),
                        ("circuit_size", CARD["substrate"]["circuit_size"]),
                        ("seed0", CARD["substrate"]["seed0"])):
        seen = sorted({json.dumps(r.get(field)) for r in rows})
        invariants[field] = {"values": seen, "card": want, "agrees": seen == [json.dumps(want)]}
    classes = sorted({json.dumps(r.get("n_classes")) for r in rows})
    invariants["n_classes"] = {"values": classes, "card": CARD["substrate"]["classes_per_task"],
                               "agrees": classes == [json.dumps([CARD["substrate"]["classes_per_task"]])]}

    cell = []
    for r in rows:
        p = Path(root) / r["artifact"]
        cfg = _config(p)
        if not _realises(cfg, CARD["loop"]):
            continue
        doc = load(p) or {}
        methods = doc.get("methods") or {}
        cell.append({"artifact": r["artifact"], "iters": r.get("iters"), "repeats": r.get("repeats"),
                     "lr": r.get("lr"), "task_names": r.get("task_names"), "n_classes": r.get("n_classes"),
                     "train": cfg.get("train"), "test": cfg.get("test"),
                     "arms": sorted(methods), "matrix_arms": sorted(m for m, v in methods.items()
                                                                   if (v.get("replicates") or [{}])[0].get(
                                                                       "retention") is not None),
                     "world_drive_sha1": r.get("world_drive_sha1"), "world_read_sha1": r.get("world_read_sha1"),
                     "world_coupling_sha1": r.get("world_coupling_sha1")})
    draws = {f: sorted({json.dumps(c.get(f)) for c in cell}) for f in WORLD_FIELDS}
    return {"ok": True, "reason": None, "card": CARD, "n_window": len(rows), "invariants": invariants,
            "cell": cell, "n_cell": len(cell), "draws": draws, "scan": scan(root)}


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the corpus is not readable"}
                for c in CLAIMS]
    inv = r["invariants"]
    bad = {k: v["values"] for k, v in inv.items() if len(v["values"]) > 1 or not v["agrees"]}
    j1 = {"id": "M1", "measured": f"over {r['n_window']} closed-loop artifacts: "
                                  + "; ".join(f"{k} takes {len(v['values'])} value(s), card {v['agrees']}"
                                              for k, v in inv.items()),
          "verdict": f"MET -- the substrate clause is carried and constant, over {r['n_window']} artifacts" if
                     (not bad and r["n_window"] >= MIN_WINDOW) else
                     f"FALSIFIER FIRED -- {bad} differ between artifacts or disagree with the card, or the window "
                     f"holds {r['n_window']} artifacts"}

    cfg = r["card"]["protocol"]
    per_task = r["card"]["substrate"]["classes_per_task"]
    cell = r["cell"]
    j2 = {"id": "M2", "measured": f"{r['n_cell']} of {r['n_window']} closed-loop artifacts realise the card's loop "
                                  f"clause",
          "verdict": f"MET -- the loop clause is carried by a cell of {r['n_cell']}" if r["n_cell"] >= MIN_CELL else
          f"FALSIFIER FIRED -- only {r['n_cell']} artifacts realise it"}

    wrong = {c["artifact"]: {"tasks": c["task_names"], "classes": c["n_classes"], "split": [c["train"], c["test"]]}
             for c in cell if c["task_names"] != cfg["tasks"] or c["n_classes"] != [per_task]
             or [c["train"], c["test"]] != [cfg["train"], cfg["test"]]}
    j3 = {"id": "M3", "measured": f"over the cell's {r['n_cell']} artifacts: "
                                  f"{len(set(tuple(c['task_names']) for c in cell))} distinct task order(s), "
                                  f"{len({(c['train'], c['test']) for c in cell})} distinct split(s), "
                                  f"{len(set(tuple(c['n_classes']) for c in cell))} distinct class count(s)",
          "verdict": "MET -- the protocol clause is carried by the cell" if not wrong else
          f"FALSIFIER FIRED -- {wrong} differ from the card"}

    short = {c["artifact"]: {"arms": c["arms"], "matrices": c["matrix_arms"]}
             for c in cell if not set(r["card"]["arms"]) <= set(c["arms"])
             or not set(r["card"]["arms"]) <= set(c["matrix_arms"])}
    j4 = {"id": "M4", "measured": f"every one of the cell's {r['n_cell']} artifacts ran "
                                  f"{sorted({tuple(c['arms']) for c in cell})} and carries matrices for "
                                  f"{sorted({tuple(c['matrix_arms']) for c in cell})}",
          "verdict": "MET -- every metric the card names is computable in every artifact of the cell" if not short
          else f"FALSIFIER FIRED -- {short} is missing an arm or a matrix"}

    draws = r["draws"]
    multi = {k: v for k, v in draws.items() if len(v) != 1}
    hits = r["scan"]["absent_hits"]
    ok5 = not multi and not hits and r["scan"]["files"] >= MIN_SCAN
    j5 = {"id": "M5", "measured": f"over the cell's {r['n_cell']} artifacts the world's draws take "
                                  f"{ {k: len(v) for k, v in draws.items()} } value(s); and across "
                                  f"{r['scan']['files']} artifacts carrying {r['scan']['n_config_keys']} distinct "
                                  f"configuration keys, {len(hits)} name a reward, a policy, an episode, a goal or "
                                  f"a return",
          "verdict": f"MET -- one world, and no configuration key names a reward: the absent list is of things the "
                     f"corpus cannot express" if ok5 else
          f"FALSIFIER FIRED -- {multi} carry more than one world draw, or {hits} name one of the absent things, or "
          f"the scan covers {r['scan']['files']} artifacts"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the game card ==")
        print(f"   REFUSED -- {r.get('reason', 'the corpus is not readable')}")
        return len(CLAIMS)

    card = r["card"]
    print("== the game card ==")
    print(f"   {card['name']}, revision {card['revision']}, read {card['read']}")
    print(f"   substrate: {card['substrate']}")
    print(f"   loop:      {card['loop']}")
    print(f"   protocol:  {card['protocol']}")
    print(f"   arms:      {card['arms']}")
    print(f"   metrics:   {card['metrics']}")
    print(f"   absent:    {card['absent']}")
    print(f"\n   the window holds {r['n_window']} closed-loop artifacts and the cell {r['n_cell']} of them; the "
          f"corpus scan covers {r['scan']['files']} artifacts with {r['scan']['n_config_keys']} distinct "
          f"configuration keys")

    print("\n== the registered claims, M1-M5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e387` published the setting's fields but stopped at consistency; this writes the game down and")
    print("    checks each clause against artifacts, with the absent clauses measured over the whole corpus)")
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
