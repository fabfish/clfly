"""E443 -- the ledger on a second world: whether the position effect `e437`, `e438`, `e439` and `e441` read is the world's or one draw's.

Every number this line has published about the card's arms is conditional on **one** world. `e393` redrew the card's
environment four times -- its own closing line was that *every number the line has published is conditional on one
world* -- but it redrew it at **twenty updates** with `naive` and `replay`, so the ledger `e437` measured (**+0.2896**,
**+0.2490**, **-0.0604** by position, a first-over-last margin of **+0.3500**) and that `e438` extended to an anchor
(**+0.0625**, **-0.0354**, **-0.1177**) have never been read on a second world at the card's own horizon. `e339`'s
calibration is what makes that a question rather than a formality: a redraw dominates a configuration-against-
configuration comparison in this corpus, so a ledger read once is a ledger read at one draw.

**This unit redraws the world and drives the same three arms on it.** `e438`'s configuration with `--loop-seed 1` alone
differing, at the same twenty replicates on the same as-built order, so the environment's three populations and its
drive and answer maps are drawn afresh while the circuit, the read-out subset, the tasks, the arm list and the training
seeds are held. Five claims, registered before the new run's reading was opened.

- **BU1 -- and the two rolls are one configuration with the world redrawn.** The three arms at **20** replicates, every
  recorded field agreeing with `e438`'s except `loop_seed`, the output path and the saved weights, the task sets equal,
  and the environment's three **world** fingerprints differing from the card's. **Falsifier**: any other field differing,
  an arm missing or short, or any of the three world fingerprints matching the card's.
- **BU2 -- and the buffer's ledger replicates at the first position.** `replay` minus `naive` at the first position is at
  least **+0.05**. **Falsifier**: at or below **zero**; **null**: between. *The card reads **+0.2896**.*
- **BU3 -- and the last position is cost on the new world too.** `replay` minus `naive` at the last position is at most
  **zero**. **Falsifier**: above **+0.05**; **null**: between. *The card reads **-0.0604**.*
- **BU4 -- and the first-taught task is ahead of the last-taught one.** `replay`'s first-position gain over `naive`'s
  last-position gain is at least **+0.05**. **Falsifier**: below **+0.02**; **null**: between. *The card reads
  **+0.3500**.*
- **BU5 -- and the size of the position effect is the world's.** The new world's first-over-last margin is within **0.15**
  of the card's **+0.3500**. **Falsifier**: **0.25** or more apart; **null**: between. *This is the claim with the unit's
  question in it: the shape replicating is one thing and the size replicating is another, and `e393` found the card's own
  world to be the mildest of five on its own reading.*

**What it can do beyond that.** It says whether the card's headline is a property of the benchmark or of one draw of it.
If the shape holds and the size does too, the ledger can be quoted without naming a world; if the shape holds and the
size does not, the card should carry the number as a range over worlds; and if the shape does not hold, `e439`'s and
`e441`'s sentences about which arm is a buffer on *this* world are sentences about one draw.

**What it cannot do.** *Two worlds*: one redraw, so a spread between two draws cannot be told from a spread between two
arms. *And one cell*: the card's horizon and twenty replicates, one order, three arms, so the four more worlds `e393`
drew are at another horizon and the anchor's second order is not here. *And one manipulation*: `--loop-seed` reseeds the
environment's populations and its maps together, so this is a redraw and not an axis. *And the read-out subset is held*:
`--readout-seed` defaults to `--seed0`, which does not move here, so the decoder's draw is the card's on both worlds.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the card's world with all three arms, and the same configuration with the environment redrawn
RUNS = {
    "new": Path("runs/e443_earned_label_worldseed1_20reps.json"),
    "card": Path("runs/e438_earned_label_three_arms_20reps.json"),
}
ARMS = ("naive", "ewc-block", "replay")
BASELINE = "naive"
BUFFER = "replay"
ANCHOR = "ewc-block"
DRAW_FIELD = "loop_seed"
SHARED = ("circuit", "readout", "tasks")
DRAW_FIELDS = ("cue_sha1", "action_sha1", "world_read_sha1", "world_drive_sha1", "world_coupling_sha1")
#: the three the world's own drawing produces, which a redraw must move
WORLD_FIELDS = ("world_read_sha1", "world_drive_sha1", "world_coupling_sha1")
IGNORED = ("json_out", "save_theta", "methods", DRAW_FIELD)
N_TASKS = 3
N_ARMS = 3
MIN_REPS = 20
FIRST_BAR = 0.05
FIRST_FLOOR = 0.0
LAST_BAR = 0.0
LAST_FIRES = 0.05
MARGIN_BAR = 0.05
MARGIN_FLOOR = 0.02
#: the card's own first-over-last margin, which `e437` and `e436` read and BU5 is registered against
CARD_MARGIN = 0.3500
MARGIN_MOVES = 0.15
MARGIN_FIRES = 0.25
CLAIMS = (
    ("BU1", f"and the two rolls are one configuration with the world redrawn, at {MIN_REPS} replicates",
     "The three arms at twenty replicates, every recorded field agreeing with e438's except loop_seed, the output path "
     "and the saved weights, the task sets equal, and the environment's three world fingerprints differing from the "
     "card's",
     "falsifier: any other field differing, an arm missing or short, or any of the three world fingerprints matching "
     "the card's"),
    ("BU2", f"and the buffer's ledger replicates at the first position, at least {FIRST_BAR:+.2f}",
     "replay minus naive at the first position is at least +0.05",
     f"falsifier: at or below {FIRST_FLOOR:+.2f}; null: between"),
    ("BU3", "and the last position is cost on the new world too",
     "replay minus naive at the last position is at most zero",
     f"falsifier: above {LAST_FIRES:+.2f}; null: between"),
    ("BU4", f"and the first-taught task is ahead of the last-taught one, at least {MARGIN_BAR:+.2f}",
     "replay's first-position gain over naive's last-position gain is at least +0.05",
     f"falsifier: below {MARGIN_FLOOR:+.2f}; null: between"),
    ("BU5", f"and the size of the position effect is the world's, within {MARGIN_MOVES:.2f}",
     f"The new world's first-over-last margin is within 0.15 of the card's {CARD_MARGIN:+.4f}",
     f"falsifier: {MARGIN_FIRES:.2f} or more apart; null: between"),
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
    tasks = [t.get("name") if isinstance(t, dict) else t for t in (doc.get("tasks") or [])]
    methods = doc.get("methods") or {}
    got = {}
    for arm in ARMS:
        if arm not in methods:
            continue
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        got[arm] = {"replicates": len(reps),
                    "final": [statistics.fmean([r["final_per_task"][k] for r in reps]) for k in range(len(tasks))],
                    "forgetting": statistics.fmean([r["mean_forgetting"] for r in reps])}
    ed = doc.get("env_draw") or {}
    cfg = doc.get("config") or {}
    return {"artifact": path.name, "tasks": tasks, "arms": got, "loop_seed": cfg.get(DRAW_FIELD),
            "shared": {k: doc.get(k) for k in SHARED}, "draws": {k: ed.get(k) for k in DRAW_FIELDS},
            "config": {k: cfg.get(k) for k in sorted(set(cfg) - set(IGNORED))}}


def reading(runs: dict = RUNS) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "redrawn": {}, "gains": {}, "spans": {}}
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
    for k in DRAW_FIELDS:
        same[f"env_draw.{k}"] = new["draws"].get(k) == card["draws"].get(k)
    same["circuit"] = new["shared"].get("circuit") == card["shared"].get("circuit")
    same["readout"] = new["shared"].get("readout") == card["shared"].get("readout")
    same["tasks"] = set(new["tasks"]) == set(card["tasks"])
    out["same"] = same
    #: the environment's own drawing, which the redraw must move and the held fields must not
    out["redrawn"] = {"world": {k: (new["draws"].get(k) != card["draws"].get(k)) for k in WORLD_FIELDS},
                      "held": {k: (new["draws"].get(k) == card["draws"].get(k)) for k in DRAW_FIELDS
                               if k not in WORLD_FIELDS},
                      "seed": {"new": new["loop_seed"], "card": card["loop_seed"]}}
    for label, roll in out["runs"].items():
        for name, (a, b) in (("replay-naive", (BUFFER, BASELINE)), ("ewc-naive", (ANCHOR, BASELINE)),
                             ("ewc-replay", (ANCHOR, BUFFER))):
            if a in roll["arms"] and b in roll["arms"]:
                out["gains"][f"{label}.{name}"] = [roll["arms"][a]["final"][k] - roll["arms"][b]["final"][k]
                                                   for k in range(N_TASKS)]
    def _margin(label):
        g = out["gains"][f"{label}.replay-naive"]
        return g[0] - g[-1]
    out["spans"] = {"replicates": sorted({v["replicates"] for roll in out["runs"].values()
                                         for v in roll["arms"].values()}),
                    "arms": {label: len(roll["arms"]) for label, roll in out["runs"].items()},
                    "same_fields": len(same), "runs": len(out["runs"]),
                    "margins": {label: _margin(label) for label in out["runs"]},
                    "card_margin": CARD_MARGIN,
                    "move": _margin("new") - CARD_MARGIN,
                    "forgetting": {label: {a: roll["arms"][a]["forgetting"] for a in roll["arms"]}
                                   for label, roll in out["runs"].items()}}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no arm"} for c in CLAIMS]
    differ = sorted(k for k, v in r["same"].items() if not v)
    #: the seed, the three world fingerprints and the held fields are the differences BU1 allows and requires
    allowed = {"env_draw." + k for k in WORLD_FIELDS}
    unexpected = [k for k in differ if k not in allowed]
    matched = sorted(k for k, v in r["redrawn"]["world"].items() if not v)
    thin = {f"{lbl}.{a}": v["replicates"] for lbl, roll in r["runs"].items() for a, v in roll["arms"].items()
            if v["replicates"] < MIN_REPS}
    short = {} if len(r["runs"]["new"]["arms"]) >= N_ARMS else {"new": sorted(r["runs"]["new"]["arms"])}
    j1 = {"id": "BU1",
          "measured": f"the new roll carries {len(r['runs']['new']['arms'])} arms at {r['spans']['replicates']} "
                      f"replicates over {r['spans']['same_fields']} compared fields, the seeds "
                      f"{r['redrawn']['seed']}, the world's three fingerprints redrawn "
                      f"{ {k: v for k, v in r['redrawn']['world'].items()} }, the held draws "
                      f"{ {k: v for k, v in r['redrawn']['held'].items()} }",
          "verdict": "MET -- one configuration with `loop_seed` moved, the environment's three world fingerprints "
                     "redrawn and none of them the card's" if
                     (not short and not unexpected and not matched and not thin) else
                     f"FALSIFIER FIRED -- unexpected differences {unexpected}, fingerprints matching the card's "
                     f"{matched}, thin {thin}, short {short}"}
    first = r["gains"]["new.replay-naive"][0]
    j2 = {"id": "BU2",
          "measured": f"on the new world replay over naive at the first position is {first:+.4f}, against the "
                      f"last position's {r['gains']['new.replay-naive'][-1]:+.4f}",
          "verdict": f"MET -- the buffer's first-position gain replicates at {first:+.4f}" if first >= FIRST_BAR else
                     f"FALSIFIER FIRED -- {first:+.4f} at or below zero" if first <= FIRST_FLOOR else
                     f"NULL -- {first:+.4f} between {FIRST_FLOOR:+.2f} and {FIRST_BAR:+.2f}"}
    last = r["gains"]["new.replay-naive"][-1]
    j3 = {"id": "BU3",
          "measured": f"on the new world replay over naive at the last position is {last:+.4f}",
          "verdict": f"MET -- the last position is cost on the new world too, {last:+.4f}" if last <= LAST_BAR else
                     f"FALSIFIER FIRED -- {last:+.4f} is above the bar" if last > LAST_FIRES else
                     f"NULL -- {last:+.4f} between {LAST_BAR:+.2f} and {LAST_FIRES:+.2f}"}
    margin = r["spans"]["margins"]["new"]
    j4 = {"id": "BU4",
          "measured": f"the new world's first-over-last margin is {margin:+.4f}",
          "verdict": f"MET -- the first-taught task is ahead of the last-taught one by {margin:+.4f}" if
                     margin >= MARGIN_BAR else
                     f"FALSIFIER FIRED -- {margin:+.4f} below {MARGIN_FLOOR:+.2f}" if margin < MARGIN_FLOOR else
                     f"NULL -- {margin:+.4f} between {MARGIN_FLOOR:+.2f} and {MARGIN_BAR:+.2f}"}
    move = abs(r["spans"]["move"])
    j5 = {"id": "BU5",
          "measured": f"the new world's margin is {margin:+.4f} against the card's {CARD_MARGIN:+.4f}, "
                      f"{move:.4f} apart",
          "verdict": f"MET -- the size of the position effect is the world's, {move:.4f} apart" if move <= MARGIN_MOVES
                     else f"FALSIFIER FIRED -- the move is {move:.4f}" if move >= MARGIN_FIRES else
                     f"NULL -- the move is {move:.4f}, between {MARGIN_MOVES:.2f} and {MARGIN_FIRES:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the ledger on a second world ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source and the earned label, and the same configuration with")
    print("   the environment redrawn by `--loop-seed 1`, as-built order, twenty replicates")
    print(f"\n   {'roll':>6} {'loop seed':>10} {'world read':>12} {'drive':>12} {'coupling':>12}")
    for label, roll in r["runs"].items():
        d = roll["draws"]
        print(f"   {label:>6} {str(roll['loop_seed']):>10} {str(d.get('world_read_sha1')):>12} "
              f"{str(d.get('world_drive_sha1')):>12} {str(d.get('world_coupling_sha1')):>12}")
    print("\n   the gain over naive, by position:")
    for label in ("card", "new"):
        for name in ("replay-naive", "ewc-naive", "ewc-replay"):
            key = f"{label}.{name}"
            if key in r["gains"]:
                print(f"      {key:>16}: " + " ".join(f"{x:+.4f}" for x in r["gains"][key]))
    print("\n   mean forgetting, arm by arm:")
    for label, got in r["spans"]["forgetting"].items():
        print(f"      {label:>6}: " + ", ".join(f"{a} {v:.4f}" for a, v in got.items()))
    m = r["spans"]["margins"]
    print(f"\n   the first-over-last margin: card {m['card']:+.4f}, new {m['new']:+.4f}, "
          f"{m['new'] - m['card']:+.4f} apart")
    print("\n== the registered claims, BU1-BU5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e393` redrew this world four times at twenty updates and said every published number is conditional")
    print("    on one world; the ledger has been read at the card's horizon on one draw only)")
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
