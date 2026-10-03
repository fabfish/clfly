"""E393 -- the card on four more worlds: does its headline replicate across the draw?

`e392` wrote the closed-loop benchmark down as a card and measured its two absences. One of them is load-bearing:
over the card's cell -- thirty-six artifacts -- the world's three fingerprints each take exactly **one** value, so
*"every number the line has published is conditional on one world."* A benchmark whose headline is one draw is a
demonstration; a benchmark whose headline survives a redraw is a result.

**This unit redraws the world four times.** `--loop-seed` reseeds the environment's own draw -- the cue, action and
feedback populations and the three maps that follow them -- and nothing else: `e392`'s probe at `loop-seed 1` differs
from the card's cell in that one field and in the six fingerprints it moves, with the circuit, the read-out draw, the
basis and every task identical. Four such worlds at the card's canonical near point -- the wide step, cue at 0, the
action source, 20 updates, 20 replicates -- each compared with the card's own 20-update artifact read through the
same probe, so the five worlds are one instrument.

Five claims, registered before any of the new runs' readings was opened.

- **N1 -- one configuration except the draw.** Every recorded field is in one of two lists: the fields the card
  **placed**, which must be identical in all five runs, and the fields the **draw** moves. **Falsifier**: a field in
  neither list, or a placed field differing between two runs.
- **N2 -- and the four are four different worlds.** Each of the world's three fingerprints takes **four** distinct
  values across the new draws, and none of them equals the card's. **Falsifier**: two new worlds sharing a
  fingerprint, or one of them matching the card's.
- **N3 -- and the connectome's own reading is a property of the brain and not of the world.** Across the five worlds
  the connectome's own weights read task 0 with a spread of at most **0.10**. **Falsifier**: a spread over **0.15**,
  which would say the redraw moves the substrate rather than the interface. **Null**: between.
- **N4 -- and the body after twenty updates replicates.** Across the five worlds the trained body's reading of task 0
  has a spread of at most **0.10**. **Falsifier**: over **0.15**. **Null**: between. *The card's own reading is
  **0.5740** after twenty updates against **0.6875** from the connectome, so the band is a fifth of the effect the
  next claim is about and half of the distance the training leaves.*
- **N5 -- and the headline itself replicates.** On **every** one of the four new worlds, as on the card's, the body
  after twenty updates reads **below** the connectome's own weights on the same world by at least **0.05** -- the
  valley, on five draws rather than one. **Falsifier**: any world where it is not below by 0.05, which would say the
  card's headline is a property of the card's world. *This is the claim the unit exists for: not that a number is
  stable, but that the **effect** is.*

**What it can do beyond that.** It turns the card's own worst clause -- one world -- into a measured statement: how
much of the benchmark's headline is the world and how much is the game. It also moves the card toward its second
revision, where a benchmark that reports one draw's number has to report the draw.

**What it cannot do.** *Four redraws are four samples*, and they move the populations as well as the maps, so a
world here is the environment's whole draw and not one map in isolation; nothing separates which of the seven moved
fields carries an effect. *And it redraws at one budget*: twenty updates is the card's near point, so whether the
far point at five hundred replicates across worlds is not measured. *And it holds the circuit, the read-out draw,
the basis, the task set and the seed stream fixed*, which is half of `e392`'s M5 -- the seed stream is still one.
*And a probe is not a mechanism*: a reading says how much of the label a linear fit recovers from the world's eight
numbers.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e367_the_world_the_agent_drives import _facts
from experiments.e379_what_the_body_did import NAIVE, TAU  # noqa: F401  (the same instrument)
from experiments.e380_what_the_training_built import setup as setup_wide
from experiments.e382_when_the_world_loses_it import one_budget

REPS = 20
ITERS = 20
#: the card's own 20-update artifact, and the four worlds this unit draws
CARD = {"run": Path("runs/e389_earned_label_iters20_cue0_actionsource_20reps.json"),
        "theta": Path("runs/e389_theta_20")}
RUNS = {s: {"run": Path(f"runs/e393_earned_label_worldseed{s}_iters20_20reps.json"),
            "theta": Path(f"runs/e393_theta_{s}")} for s in (1, 2, 3, 4)}
#: the fields the card placed, which a redraw of the environment must not move
PLACED = ("loop_world_leak", "readout_from_world", "loop_world_dims", "closed_loop", "loop_world_modes",
          "loop_world_nonlinear", "repeats", "circuit_size", "readout_size", "basis", "seed0", "task_names",
          "task_readout_widths", "iters", "lr", "batch")
#: and the fields the environment's own draw moves: the seed, the three populations and the three maps after them
DRAWN = ("loop_seed", "cue_sha1", "feedback_sha1", "n_cue", "action_sha1", "n_action", "drive_from_cue",
         "loop_drive_from_cue", "world_drive_sha1", "world_read_sha1", "world_coupling_sha1")
WORLD_FIELDS = ("world_drive_sha1", "world_read_sha1", "world_coupling_sha1")
CARD_INITIAL = 0.6875
CARD_BODY = 0.5740
STABLE = 0.10
UNSTABLE = 0.15
COST = 0.05
CLAIMS = (
    ("N1", "one configuration except the draw",
     "Every recorded field is in the placed list, which must be identical in all five runs, or in the drawn list",
     "falsifier: a field in neither list, or a placed field differing between two runs"),
    ("N2", "and the four are four different worlds",
     "Each of the world's three fingerprints takes four distinct values across the new draws and none equals the "
     "card's",
     "falsifier: two new worlds sharing a fingerprint, or one matching the card's"),
    ("N3", f"and the connectome's own reading is not the world's, within {STABLE:.2f}",
     f"Across the five worlds the connectome's own weights read task 0 with a spread of at most {STABLE:.2f}",
     f"falsifier: a spread over {UNSTABLE:.2f}; null: between"),
    ("N4", f"and the body after twenty updates replicates, within {STABLE:.2f}",
     f"Across the five worlds the trained body's reading has a spread of at most {STABLE:.2f}",
     f"falsifier: over {UNSTABLE:.2f}; null: between"),
    ("N5", f"and the headline itself replicates, by {COST:.2f}",
     "On every one of the four new worlds the body after twenty updates reads below the connectome's own weights on "
     "the same world by at least 0.05",
     "falsifier: any world where it is not below by 0.05"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _settings(doc: dict) -> dict:
    cfg = doc.get("config") or {}
    return {**_facts(doc), "loop_seed": cfg.get("loop_seed"), "lr": cfg.get("lr"), "batch": cfg.get("batch")}


def reading(card: dict = CARD, runs: dict = RUNS, arm: str = NAIVE, reps: int = REPS) -> dict:
    from clfly.network.model import RateConfig, build_net

    circ, rs, loop_env, tasks = setup_wide()
    model = build_net(circ, RateConfig(tau=TAU)).torch_model()
    ctx = (model, loop_env, tasks, circ.n_neurons)
    out = {"ok": True, "reason": None, "worlds": {}, "settings": {}, "arm": arm, "reps": reps}
    for name, spec in [("card", card)] + [(str(s), r) for s, r in runs.items()]:
        doc = load(spec["run"])
        if not doc:
            return {**out, "ok": False, "reason": f"world {name}: the artifact is absent"}
        got = one_budget(doc, spec["theta"], ctx, arm=arm, reps=reps)
        if not got.get("ok"):
            return {**out, "ok": False, "reason": f"world {name}: {got['reason']}"}
        cell = got["cell"]
        out["worlds"][name] = {"artifact": spec["run"].name, "iters": doc["config"].get("iters"),
                               "repeats": doc["config"].get("repeats"),
                               "initial_task_0": statistics.fmean(cell[("initial", 0)]),
                               "body_task_0": statistics.fmean(cell[("after_task_0", 0)]),
                               "head_task_0": float(doc["methods"][arm]["replicates"][0]["learned"][0])}
        out["settings"][name] = _settings(doc)
    draws = {f: sorted({s.get(f) for s in out["settings"].values()}) for f in WORLD_FIELDS}
    initials = [w["initial_task_0"] for w in out["worlds"].values()]
    bodies = [w["body_task_0"] for w in out["worlds"].values()]
    out["spread"] = {"initial": max(initials) - min(initials), "body": max(bodies) - min(bodies)}
    out["draws"] = {k: [str(v) for v in vs] for k, vs in draws.items()}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a run or its weights is absent"}
                for c in CLAIMS]
    settings = r["settings"]
    keys = sorted({k for s in settings.values() for k in s})
    unknown = [k for k in keys if k not in PLACED and k not in DRAWN]
    placed = {k: sorted({json.dumps(s.get(k)) for s in settings.values()}) for k in keys if k in PLACED}
    moved = {k: v for k, v in placed.items() if len(v) > 1}
    drawn_moved = {k: sorted({json.dumps(s.get(k)) for s in settings.values()}) for k in keys if k in DRAWN}
    drawn_fixed = {k: v for k, v in drawn_moved.items() if len(v) == 1}
    j1 = {"id": "N1", "measured": f"{len(keys)} fields recorded across the five worlds: "
                                  f"{len([k for k in keys if k in PLACED])} placed and "
                                  f"{len([k for k in keys if k in DRAWN])} drawn, with {unknown} in neither list, "
                                  f"{sorted(drawn_fixed)} of the drawn fields fixed and {sorted(moved)} of the "
                                  f"placed fields moved",
          "verdict": "MET -- one configuration, and the environment's own draw is the only thing that moves" if
                     (not unknown and not moved) else
          f"FALSIFIER FIRED -- {unknown} in neither list, or {moved} of the placed fields moved"}

    new = {w: r["settings"][w] for w in ("1", "2", "3", "4")}
    counts = {f: len({s.get(f) for s in new.values()}) for f in WORLD_FIELDS}
    #: the card's own fingerprint on each of the three maps, and how many of the four redraws reproduce it
    card_value = {f: settings["card"].get(f) for f in WORLD_FIELDS}
    clashes = {f: len([1 for s in new.values() if s.get(f) == card_value[f]]) for f in WORLD_FIELDS}
    good2 = all(c == 4 for c in counts.values()) and all(c == 0 for c in clashes.values())
    j2 = {"id": "N2", "measured": f"the four new draws take {counts} distinct fingerprint(s) and "
                                  f"{clashes} of them coincide with the card's",
          "verdict": "MET -- the four are four different worlds, none of them the card's" if good2 else
          f"FALSIFIER FIRED -- {counts} distinct fingerprints, {clashes} coinciding with the card's"}

    j3 = {"id": "N3", "measured": f"the connectome's own readings over the five worlds are "
                                  f"{[round(w['initial_task_0'], 4) for w in r['worlds'].values()]}, a spread of "
                                  f"{r['spread']['initial']:.4f}",
          "verdict": f"MET -- the substrate's own reading is not the world's, within {STABLE:.2f}" if
                     r["spread"]["initial"] <= STABLE else
          f"FALSIFIER FIRED -- a spread of {r['spread']['initial']:.4f}: the redraw moves the substrate" if
          r["spread"]["initial"] > UNSTABLE else
          f"NULL -- {r['spread']['initial']:.4f}, between {STABLE:.2f} and {UNSTABLE:.2f}"}

    j4 = {"id": "N4", "measured": f"the trained bodies' readings over the five worlds are "
                                  f"{[round(w['body_task_0'], 4) for w in r['worlds'].values()]}, a spread of "
                                  f"{r['spread']['body']:.4f}",
          "verdict": f"MET -- the body after twenty updates replicates, within {STABLE:.2f}" if
                     r["spread"]["body"] <= STABLE else
          f"FALSIFIER FIRED -- a spread of {r['spread']['body']:.4f}" if r["spread"]["body"] > UNSTABLE else
          f"NULL -- {r['spread']['body']:.4f}, between {STABLE:.2f} and {UNSTABLE:.2f}"}

    costs = {w: [r["worlds"][w]["initial_task_0"] - r["worlds"][w]["body_task_0"],
                 r["worlds"][w]["artifact"]] for w in ("1", "2", "3", "4")}
    short = {w: round(v[0], 4) for w, v in costs.items() if v[0] < COST}
    card_cost = r["worlds"]["card"]["initial_task_0"] - r["worlds"]["card"]["body_task_0"]
    j5 = {"id": "N5", "measured": f"the cost of twenty updates on each world is "
                                  f"{ {w: round(v[0], 4) for w, v in costs.items()} }, against the card's own "
                                  f"{card_cost:.4f}",
          "verdict": f"MET -- the headline replicates on all four new worlds, by {COST:.2f} or more" if not short
          else f"FALSIFIER FIRED -- {short} is not below its own initial by {COST:.2f}: the card's headline is a "
               f"property of the card's world"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the card on four more worlds ==")
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the card on four more worlds ==")
    print(f"   the card's 20-update cell at `--loop-seed` 1 to 4, {r['reps']} replicates on the `{r['arm']}` arm, "
          f"read through the same probe")
    print(f"\n   {'world':>7} {'initial':>9} {'body@20':>9} {'cost':>8} {'head':>8}  {'artifact':>44}")
    for name in ("card", "1", "2", "3", "4"):
        w = r["worlds"][name]
        print(f"   {name:>7} {w['initial_task_0']:9.4f} {w['body_task_0']:9.4f} "
              f"{w['initial_task_0'] - w['body_task_0']:8.4f} {w['head_task_0']:8.4f}  {w['artifact']:>44}")

    print("\n== the registered claims, N1-N5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e392` measured that the card's cell carries one world and registered that every number the line")
    print("    published is conditional on it; this redraws the world four times at the card's near point)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reps", type=int, default=REPS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(reps=args.reps)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
