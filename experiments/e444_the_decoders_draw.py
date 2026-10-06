"""E444 -- the decoder's draw: what the second of `--seed0`'s three draws does to the ledger.

`e339` found that `--seed0` is **three draws at once** -- the training replicates, the read-out subset and the
environment's populations -- and that is why no clean seed-stream pair exists in the corpus. This line has since taken
two of the three apart: `e443` drove `--loop-seed 1` and found that the manipulation redraws the **environment's six
fingerprints** -- the cue, action and feedback populations and the world's three maps -- while this line had been calling
three of them "the world's", and its own closing line named what it could not reach: *the read-out subset is held, so
the decoder's own draw is the card's on both worlds*.

**This unit drives the third draw.** `e438`'s configuration with `--readout-seed 1` alone differing, at the same three
arms, twenty replicates and as-built order, so the decoder's subset is drawn afresh while the environment's are held --
the mirror of `e443`, which moved the environment and held the decoder. Five claims, registered before the new run's
reading was opened.

- **BV1 -- and the two rolls are one configuration with the read-out draw moved.** The three arms at **20** replicates,
  every recorded config field agreeing with `e438`'s except `readout_seed`, the output path and the saved weights, the
  circuit and the task sets equal, the environment's **six** fingerprints all **held**, and the read-out subset's
  fingerprint **differing**. **Falsifier**: any other field differing, an arm missing or short, any of the six
  environment fingerprints moving, or the read-out fingerprint not moving.
- **BV2 -- and the buffer's ledger replicates under a second decoder.** `replay` minus `naive` at the first position is
  at least **+0.05**. **Falsifier**: at or below **zero**; **null**: between. *The card reads **+0.2896**.*
- **BV3 -- and the last position is cost under it too.** `replay` minus `naive` at the last position is at most
  **zero**. **Falsifier**: above **+0.05**; **null**: between. *The card reads **-0.0604**.*
- **BV4 -- and the size of the position effect is the decoder's too.** The first-over-last margin is within **0.15** of
  the card's **+0.3500**. **Falsifier**: **0.25** or more apart; **null**: between. *`e443` found the margin moving
  **0.0177** when the environment was redrawn; this asks the same of the other draw.*
- **BV5 -- and the buffer's advantage on the whole diagonal survives it.** `replay` minus `naive` on the mean diagonal is
  at least **+0.10**. **Falsifier**: at or below **+0.02**; **null**: between. *The card reads **+0.1594** at
  **11.97** sigma.*

**What it can do beyond that.** Together with `e443` it decomposes `--seed0`'s three draws by what each one does to the
card's headline: `e443` moved the environment and found the buffer's margin moving **0.0177** and the anchor's standing
moving sign, and this moves the decoder and can say whether the headline is likewise indifferent to which neurons it is
read on. If both draws leave the ledger where it was then the ledger is a property of the circuit, the tasks and the
arm list, which is what a benchmark's headline should be; if the decoder's draw moves it, then `e339`'s sentence about
`--seed0` applies to the ledger and every reading this line has published carries it.

**What it cannot do.** *One draw of each kind*: one redraw apiece, so a spread between two draws cannot be told from a
spread between two arms. *And one seed for both*: the decoder's draw and the environment's are moved one at a time here
and never together, so a reading of `--seed0` as a whole is not this. *And one cell*: the card's horizon, one order,
three arms, twenty replicates. *And a draw is not an axis*: `--readout-size` is held at 32, so this is which neurons and
not how many, which is `e286`'s axis and not this unit's.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the card's world with all three arms, and the same configuration with the decoder redrawn
RUNS = {
    "new": Path("runs/e444_earned_label_readoutseed1_20reps.json"),
    "card": Path("runs/e438_earned_label_three_arms_20reps.json"),
}
ARMS = ("naive", "ewc-block", "replay")
BASELINE = "naive"
BUFFER = "replay"
ANCHOR = "ewc-block"
DRAW_FIELD = "readout_seed"
SHARED = ("circuit", "tasks")
#: the six the environment's own drawing produces, which `e443` corrected this line's field list to
DRAW_FIELDS = ("cue_sha1", "action_sha1", "feedback_sha1", "world_read_sha1", "world_drive_sha1", "world_coupling_sha1")
CIRCUIT_FIELD = "circuit_sha1"
IGNORED = ("json_out", "save_theta", "methods", DRAW_FIELD)
N_TASKS = 3
N_ARMS = 3
MIN_REPS = 20
FIRST_BAR = 0.05
FIRST_FLOOR = 0.0
LAST_BAR = 0.0
LAST_FIRES = 0.05
MEAN_BAR = 0.10
MEAN_FLOOR = 0.02
#: the card's own first-over-last margin, which `e437` and `e436` read and BV4 is registered against
CARD_MARGIN = 0.3500
MARGIN_MOVES = 0.15
MARGIN_FIRES = 0.25
CLAIMS = (
    ("BV1", f"and the two rolls are one configuration with the read-out draw moved, at {MIN_REPS} replicates",
     "The three arms at twenty replicates, every recorded config field agreeing with e438's except readout_seed, the "
     "output path and the saved weights, the circuit and the task sets equal, the environment's six fingerprints all "
     "held, and the read-out subset's fingerprint differing",
     "falsifier: any other field differing, an arm missing or short, any of the six environment fingerprints moving, or "
     "the read-out fingerprint not moving"),
    ("BV2", f"and the buffer's ledger replicates under a second decoder, at least {FIRST_BAR:+.2f}",
     "replay minus naive at the first position is at least +0.05",
     f"falsifier: at or below {FIRST_FLOOR:+.2f}; null: between"),
    ("BV3", "and the last position is cost under it too",
     "replay minus naive at the last position is at most zero",
     f"falsifier: above {LAST_FIRES:+.2f}; null: between"),
    ("BV4", f"and the size of the position effect is the decoder's too, within {MARGIN_MOVES:.2f}",
     f"The first-over-last margin is within 0.15 of the card's {CARD_MARGIN:+.4f}",
     f"falsifier: {MARGIN_FIRES:.2f} or more apart; null: between"),
    ("BV5", f"and the buffer's advantage on the whole diagonal survives it, at least {MEAN_BAR:+.2f}",
     "replay minus naive on the mean diagonal is at least +0.10",
     f"falsifier: at or below {MEAN_FLOOR:+.2f}; null: between"),
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
                    "diagonal": [statistics.fmean(r["final_per_task"]) for r in reps],
                    "forgetting": statistics.fmean([r["mean_forgetting"] for r in reps])}
    ed = doc.get("env_draw") or {}
    cfg = doc.get("config") or {}
    ro = doc.get("readout") or {}
    return {"artifact": path.name, "tasks": tasks, "arms": got, "readout_seed": cfg.get(DRAW_FIELD),
            "shared": {k: doc.get(k) for k in SHARED}, "draws": {k: ed.get(k) for k in DRAW_FIELDS},
            "readout": {"subset_sha1": ro.get("subset_sha1"), "size": ro.get("size")},
            "config": {k: cfg.get(k) for k in sorted(set(cfg) - set(IGNORED))}}


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def reading(runs: dict = RUNS) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "moved": {}, "gains": {}, "paired": {}, "spans": {}}
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
    same["tasks"] = set(new["tasks"]) == set(card["tasks"])
    same["readout.size"] = new["readout"].get("size") == card["readout"].get("size")
    out["same"] = same
    out["moved"] = {"environment": {k: (new["draws"].get(k) != card["draws"].get(k)) for k in DRAW_FIELDS},
                    "readout": {"subset_sha1": new["readout"].get("subset_sha1"),
                                "card": card["readout"].get("subset_sha1"),
                                "moved": new["readout"].get("subset_sha1") != card["readout"].get("subset_sha1"),
                                "size": new["readout"].get("size")},
                    "seed": {"new": new["readout_seed"], "card": card["readout_seed"]}}
    for label, roll in out["runs"].items():
        for name, (a, b) in (("replay-naive", (BUFFER, BASELINE)), ("ewc-naive", (ANCHOR, BASELINE)),
                             ("ewc-replay", (ANCHOR, BUFFER))):
            if a in roll["arms"] and b in roll["arms"]:
                out["gains"][f"{label}.{name}"] = [roll["arms"][a]["final"][k] - roll["arms"][b]["final"][k]
                                                   for k in range(N_TASKS)]
    out["paired"] = {label: {"replay-naive": _paired(roll["arms"][BUFFER]["diagonal"], roll["arms"][BASELINE]["diagonal"]),
                             "ewc-naive": _paired(roll["arms"][ANCHOR]["diagonal"], roll["arms"][BASELINE]["diagonal"])
                             if ANCHOR in roll["arms"] else None}
                     for label, roll in out["runs"].items()}
    def _margin(label):
        g = out["gains"][f"{label}.replay-naive"]
        return g[0] - g[-1]
    out["spans"] = {"replicates": sorted({v["replicates"] for roll in out["runs"].values()
                                         for v in roll["arms"].values()}),
                    "arms": {label: len(roll["arms"]) for label, roll in out["runs"].items()},
                    "same_fields": len(same), "runs": len(out["runs"]),
                    "margins": {label: _margin(label) for label in out["runs"]},
                    "card_margin": CARD_MARGIN, "move": _margin("new") - CARD_MARGIN,
                    "forgetting": {label: {a: roll["arms"][a]["forgetting"] for a in roll["arms"]}
                                   for label, roll in out["runs"].items()}}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no arm"} for c in CLAIMS]
    #: the seed and the read-out fingerprint are what BV1 allows to differ; the six environment draws are not
    differ = sorted(k for k, v in r["same"].items() if not v)
    moved_env = sorted(k for k, v in r["moved"]["environment"].items() if v)
    readout_moved = r["moved"]["readout"]["moved"]
    thin = {f"{lbl}.{a}": v["replicates"] for lbl, roll in r["runs"].items() for a, v in roll["arms"].items()
            if v["replicates"] < MIN_REPS}
    short = {} if len(r["runs"]["new"]["arms"]) >= N_ARMS else {"new": sorted(r["runs"]["new"]["arms"])}
    j1 = {"id": "BV1",
          "measured": f"the new roll carries {len(r['runs']['new']['arms'])} arms at {r['spans']['replicates']} "
                      f"replicates over {r['spans']['same_fields']} compared fields, the seeds "
                      f"{r['moved']['seed']}, the read-out subset {r['moved']['readout']['card']} -> "
                      f"{r['moved']['readout']['subset_sha1']} at size {r['moved']['readout']['size']}, the "
                      f"environment's six fingerprints moved {len(moved_env)}",
          "verdict": "MET -- one configuration with the decoder's draw moved and the environment's six fingerprints "
                     "held" if (not short and not differ and not moved_env and readout_moved and not thin) else
                     f"FALSIFIER FIRED -- differing {differ}, environment moved {moved_env}, read-out moved "
                     f"{readout_moved}, thin {thin}, short {short}"}
    first = r["gains"]["new.replay-naive"][0]
    j2 = {"id": "BV2",
          "measured": f"under the second decoder replay over naive at the first position is {first:+.4f}, against the "
                      f"last position's {r['gains']['new.replay-naive'][-1]:+.4f}",
          "verdict": f"MET -- the buffer's first-position gain replicates at {first:+.4f}" if first >= FIRST_BAR else
                     f"FALSIFIER FIRED -- {first:+.4f} at or below zero" if first <= FIRST_FLOOR else
                     f"NULL -- {first:+.4f} between {FIRST_FLOOR:+.2f} and {FIRST_BAR:+.2f}"}
    last = r["gains"]["new.replay-naive"][-1]
    j3 = {"id": "BV3",
          "measured": f"under the second decoder replay over naive at the last position is {last:+.4f}",
          "verdict": f"MET -- the last position is cost under it too, {last:+.4f}" if last <= LAST_BAR else
                     f"FALSIFIER FIRED -- {last:+.4f} is above the bar" if last > LAST_FIRES else
                     f"NULL -- {last:+.4f} between {LAST_BAR:+.2f} and {LAST_FIRES:+.2f}"}
    margin = r["spans"]["margins"]["new"]
    move = abs(r["spans"]["move"])
    j4 = {"id": "BV4",
          "measured": f"the second decoder's first-over-last margin is {margin:+.4f} against the card's "
                      f"{CARD_MARGIN:+.4f}, {move:.4f} apart",
          "verdict": f"MET -- the size of the position effect is the decoder's too, {move:.4f} apart" if
                     move <= MARGIN_MOVES else
                     f"FALSIFIER FIRED -- the move is {move:.4f}" if move >= MARGIN_FIRES else
                     f"NULL -- the move is {move:.4f}, between {MARGIN_MOVES:.2f} and {MARGIN_FIRES:.2f}"}
    p = r["paired"]["new"]["replay-naive"]
    j5 = {"id": "BV5",
          "measured": f"under the second decoder replay minus naive on the mean diagonal is {p['mean']:+.4f} at "
                      f"{abs(p['sigma']):.2f} sigma over {p['n']} paired replicates",
          "verdict": f"MET -- the buffer's whole-diagonal advantage survives the redraw, {p['mean']:+.4f}" if
                     p["mean"] >= MEAN_BAR else
                     f"FALSIFIER FIRED -- {p['mean']:+.4f} at or below {MEAN_FLOOR:+.2f}" if p["mean"] <= MEAN_FLOOR
                     else f"NULL -- {p['mean']:+.4f} between {MEAN_FLOOR:+.2f} and {MEAN_BAR:+.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the decoder's draw ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source and the earned label, and the same configuration with")
    print("   the decoder's subset redrawn by `--readout-seed 1`, as-built order, twenty replicates")
    print(f"\n   {'roll':>6} {'read-out':>12} {'size':>5} {'cue':>14} {'action':>14} {'world read':>12}")
    for label, roll in r["runs"].items():
        d = roll["draws"]
        print(f"   {label:>6} {str(roll['readout']['subset_sha1']):>12} {str(roll['readout']['size']):>5} "
              f"{str(d.get('cue_sha1')):>14} {str(d.get('action_sha1')):>14} "
              f"{str(d.get('world_read_sha1')):>12}")
    print("\n   the gain over naive, by position:")
    for label in ("card", "new"):
        for name in ("replay-naive", "ewc-naive", "ewc-replay"):
            key = f"{label}.{name}"
            if key in r["gains"]:
                print(f"      {key:>16}: " + " ".join(f"{x:+.4f}" for x in r["gains"][key]))
    print("\n   mean forgetting, arm by arm:")
    for label, got in r["spans"]["forgetting"].items():
        print(f"      {label:>6}: " + ", ".join(f"{a} {v:.4f}" for a, v in got.items()))
    for label, got in r["paired"].items():
        p = got["replay-naive"]
        print(f"   {label:>6} replay minus naive on the mean diagonal: {p['mean']:+.4f} at {abs(p['sigma']):.2f} sigma")
    m = r["spans"]["margins"]
    print(f"\n   the first-over-last margin: card {m['card']:+.4f}, new {m['new']:+.4f}, "
          f"{m['new'] - m['card']:+.4f} apart")
    print("\n== the registered claims, BV1-BV5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e339` found `--seed0` is three draws at once and `e443` took the environment's apart; this takes the")
    print("    decoder's, so the ledger can be asked which of the two it is the draw's)")
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
