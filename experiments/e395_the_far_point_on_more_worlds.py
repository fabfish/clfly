"""E395 -- the far point on two more worlds: the recovery, redrawn.

`e393` redrew the card's world four times at its **near** point -- twenty updates -- and found the headline
replicates there, with the card's own world the mildest of the five. It registered exactly what that leaves: *"one
budget. Twenty updates is the card's near point. Whether the far point at five hundred replicates across worlds is
not measured, and the valley's depth is where the redraws differ most, so the far point is the next thing to
redraw."* And `e394` redrew the other axis, the training stream, and left the budget where it was.

**This unit runs the far point on two of those same worlds.** `--loop-seed 1` and `2` at **500** updates and twenty
replicates, against `e380`'s own 500-update run as the card's world, so two of the five worlds carry a reading at
each end of the trajectory and the near and far points are the same draws. The reading there is not the valley but
its mirror: `e380`'s world reads **0.7729** against the connectome's own **0.6875**, so 500 updates leave the body
**above** where it started where twenty leave it below.

Five claims, registered before any of the new runs' readings was opened.

- **P1 -- one configuration except the draw.** Every recorded field is in the placed list, which must be identical in
  all three runs, or in the drawn list. **Falsifier**: a field in neither list, or a placed field moving. *The
  placed list carries `loop_cue_at`, which `e393`'s did not: that unit fired its own N1 on the field's absence, so
  the fourth unit to pay for an incomplete field list is the reason this one names it.*
- **P2 -- and the three runs are three worlds.** Each of the world's three fingerprints takes **three** distinct
  values across the card's world and the two redraws. **Falsifier**: two of them sharing a fingerprint.
- **P3 -- and the connectome's own reading does not move.** Across the three runs the connectome's own weights read
  task 0 with a spread of at most **0.10**. **Falsifier**: a spread over **0.15**. **Null**: between. *Eleven draws
  have read 0.6875 so far -- four worlds and three streams at `e393` and `e394`, plus the near points -- so this is
  the twelfth, thirteenth and fourteenth, at the other end of the trajectory.*
- **P4 -- and the far point replicates.** Across the three runs the body's reading of task 0 after 500 updates has a
  spread of at most **0.10**. **Falsifier**: over **0.15**. **Null**: between.
- **P5 -- and the far-end headline replicates.** On **every** one of the two redraws the body after 500 updates reads
  **above** the connectome's own weights on the same world by at least **0.05**, which is what the card's own world
  does by 0.0854. **Falsifier**: any world where it is not above by 0.05. *This is the mirror of `e393`'s N5: the
  near point loses the cue and the far point has it back, and this asks whether the recovery is the draw's property
  or the game's.*

**What it can do beyond that.** It closes the budget the two redraws left open and puts two worlds on both ends of
the trajectory at once, so the line's own question -- does the interface cost you and do you get it back -- is
answered on five draws at the near end and three at the far one, at one cell and one instrument.

**What it cannot do.** *Two redraws are two samples*, and they are two of `e393`'s four, so the far end is measured
on a subset of the near end's worlds and not on a fresh draw. *And it redraws the world and not the stream*: `seed0`
is 0 and `--readout-seed`/`--loop-seed` are the draw, so the far point's four streams are not measured. *And 500 is
one budget*: the trajectory between 20 and 500 is sampled at the card's own points and not redrawn. *And a probe is
not a mechanism.*
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
ITERS = 500
#: the card's own 500-update artifact, and the two worlds this unit redraws at the same budget
CARD = {"run": Path("runs/e380_earned_label_cue0_actionsource_20reps.json"), "theta": Path("runs/e380_theta")}
RUNS = {s: {"run": Path(f"runs/e395_earned_label_worldseed{s}_iters500_20reps.json"),
            "theta": Path(f"runs/e395_theta_{s}")} for s in (1, 2)}
#: the fields the card placed, which a redraw of the environment must not move. `loop_cue_at` is here because
#: `e393`'s list omitted it and its own N1 fired on the omission.
PLACED = ("loop_cue_at", "loop_world_leak", "readout_from_world", "loop_world_dims", "closed_loop",
          "loop_world_modes", "loop_world_nonlinear", "repeats", "circuit_size", "readout_size", "basis", "seed0",
          "task_names", "task_readout_widths", "iters", "lr", "batch")
#: and the fields the environment's own draw moves
DRAWN = ("loop_seed", "cue_sha1", "feedback_sha1", "n_cue", "action_sha1", "n_action", "drive_from_cue",
         "loop_drive_from_cue", "world_drive_sha1", "world_read_sha1", "world_coupling_sha1")
WORLD_FIELDS = ("world_drive_sha1", "world_read_sha1", "world_coupling_sha1")
STABLE = 0.10
UNSTABLE = 0.15
GAIN = 0.05
CLAIMS = (
    ("P1", "one configuration except the draw",
     "Every recorded field is in the placed list, which must be identical in all three runs, or in the drawn list",
     "falsifier: a field in neither list, or a placed field differing between two runs"),
    ("P2", "and the three runs are three worlds",
     "Each of the world's three fingerprints takes three distinct values across the card's world and the two "
     "redraws",
     "falsifier: two of them sharing a fingerprint"),
    ("P3", f"and the connectome's own reading does not move, within {STABLE:.2f}",
     f"Across the three runs the connectome's own weights read task 0 with a spread of at most {STABLE:.2f}",
     f"falsifier: a spread over {UNSTABLE:.2f}; null: between"),
    ("P4", f"and the far point replicates, within {STABLE:.2f}",
     f"Across the three runs the body's reading after 500 updates has a spread of at most {STABLE:.2f}",
     f"falsifier: over {UNSTABLE:.2f}; null: between"),
    ("P5", f"and the far-end headline replicates, by {GAIN:.2f}",
     "On every one of the two redraws the body after 500 updates reads above the connectome's own weights on the "
     "same world by at least 0.05",
     "falsifier: any world where it is not above by 0.05"),
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
    draws = {f: sorted({str(s.get(f)) for s in out["settings"].values()}) for f in WORLD_FIELDS}
    initials = [w["initial_task_0"] for w in out["worlds"].values()]
    bodies = [w["body_task_0"] for w in out["worlds"].values()]
    out["spread"] = {"initial": max(initials) - min(initials), "body": max(bodies) - min(bodies)}
    out["draws"] = draws
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
    j1 = {"id": "P1", "measured": f"{len(keys)} fields recorded across the three runs: "
                                  f"{len([k for k in keys if k in PLACED])} placed and "
                                  f"{len([k for k in keys if k in DRAWN])} drawn, with {unknown} in neither list and "
                                  f"{sorted(moved)} of the placed fields moved",
          "verdict": "MET -- one configuration, and the environment's own draw is the only thing that moves" if
                     (not unknown and not moved) else
          f"FALSIFIER FIRED -- {unknown} in neither list, or {moved} of the placed fields moved"}

    counts = {f: len(v) for f, v in r["draws"].items()}
    good2 = all(c == 3 for c in counts.values())
    j2 = {"id": "P2", "measured": f"the card's world and the two redraws take {counts} distinct fingerprint(s)",
          "verdict": "MET -- the three runs are three worlds" if good2 else
          f"FALSIFIER FIRED -- {counts} is not three distinct values on every map"}

    def band(key):
        spread = r["spread"][key]
        return (f"within {STABLE:.2f}" if spread <= STABLE else
                f"a spread of {spread:.4f}" if spread > UNSTABLE else f"{spread:.4f}, between the bars")

    j3 = {"id": "P3", "measured": f"the connectome's own readings are "
                                  f"{[round(w['initial_task_0'], 4) for w in r['worlds'].values()]}, a spread of "
                                  f"{r['spread']['initial']:.4f}",
          "verdict": f"MET -- the connectome's own reading does not move: {band('initial')}" if
                     r["spread"]["initial"] <= STABLE else
          f"FALSIFIER FIRED -- {band('initial')}" if r["spread"]["initial"] > UNSTABLE else
          f"NULL -- {band('initial')}"}

    j4 = {"id": "P4", "measured": f"the bodies' readings at 500 updates are "
                                  f"{[round(w['body_task_0'], 4) for w in r['worlds'].values()]}, a spread of "
                                  f"{r['spread']['body']:.4f}",
          "verdict": f"MET -- the far point replicates: {band('body')}" if r["spread"]["body"] <= STABLE else
          f"FALSIFIER FIRED -- {band('body')}" if r["spread"]["body"] > UNSTABLE else f"NULL -- {band('body')}"}

    gains = {w: r["worlds"][w]["body_task_0"] - r["worlds"][w]["initial_task_0"] for w in ("1", "2")}
    short = {w: round(v, 4) for w, v in gains.items() if v < GAIN}
    card_gain = r["worlds"]["card"]["body_task_0"] - r["worlds"]["card"]["initial_task_0"]
    j5 = {"id": "P5", "measured": f"the gain over the connectome's own reading at 500 updates is "
                                  f"{ {w: round(v, 4) for w, v in gains.items()} }, against the card's own "
                                  f"{card_gain:.4f}",
          "verdict": f"MET -- the far-end headline replicates on both redraws, by {GAIN:.2f} or more" if not short
          else f"FALSIFIER FIRED -- {short} is not above its own initial by {GAIN:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the far point on two more worlds ==")
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the far point on two more worlds ==")
    print(f"   the card's 500-update cell at `--loop-seed` 1 and 2, {r['reps']} replicates on the `{r['arm']}` arm, "
          f"read through the same probe")
    print(f"\n   {'world':>7} {'initial':>9} {'body@500':>9} {'gain':>8} {'head':>8}  {'artifact':>46}")
    for name in ("card", "1", "2"):
        w = r["worlds"][name]
        print(f"   {name:>7} {w['initial_task_0']:9.4f} {w['body_task_0']:9.4f} "
              f"{w['body_task_0'] - w['initial_task_0']:8.4f} {w['head_task_0']:8.4f}  {w['artifact']:>46}")

    print("\n== the registered claims, P1-P5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e393` redrew the card's world at its near point and registered that the far point was not")
    print("    measured; this redraws two of those same worlds at 500 updates)")
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
