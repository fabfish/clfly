"""E403 -- the far point on the clean stream: does the recovery replicate where the world's did not?

`e394` drew the card's world at three clean training streams -- `--seed0` with `--readout-seed 0 --loop-seed 0`, so the
read-out draw and the environment stay the card's -- and found the stream moves the body **0.0396** where `e393`'s
four engine redraws move it **0.0906**. It registered what that left, and `e395` registered the same gap from the
other side: both were at the **near** point, twenty updates. `e396` then measured the world axis at the **far** point
and found it does not replicate there -- one of five worlds recovers and four end below an untrained body.

**This unit puts the stream axis at the far point.** The card's environment and read-out, two more training streams,
five hundred updates and twenty replicates, against the card's own 500-update run. Five claims, registered before any
of the new runs' readings was opened.

- **AC1 -- one configuration except the stream.** Every recorded field is in the pinned set, which must be identical
  across the three runs, or in the stream set -- `seed0` and the two flags `e339` named as the control that holds the
  other two draws. **Falsifier**: a pinned field differing between two runs, or a field in neither list.
- **AC2 -- and the draws are the card's.** The read-out draw's fingerprint and all six environment fingerprints take
  one value across the three runs. **Falsifier**: any of the seven differing.
- **AC3 -- and the recovery replicates on every stream.** Each of the two new streams' bodies reads at five hundred
  updates at least **0.05 above** its own connectome reading. **Falsifier**: either at or below zero, which would say
  the recovery `e396` found to be one world's is not even that world's property but its stream's.
- **AC4 -- and the initial reading does not move.** Across the three streams the connectome's own reading of task 0
  has a spread of at most **0.05**. **Falsifier**: over **0.10**. **Null**: between.
- **AC5 -- and the stream axis is small at the far point too.** The three streams' 500-update readings span at most
  **a third** of the five worlds' span at the same budget, which `e396` measured as **0.3344**. **Falsifier**: more
  than **two thirds** of it; **REFUSED** when that artifact is absent. *At the near point the stream was 0.0396
  against the world's 0.0906, a third of it; this asks whether the far point, where the world axis spread four times
  wider, keeps the stream small.*

**What it can do beyond that.** With `e394` it closes the stream axis at both ends of the trajectory, and with
`e396` it says which of the card's two axes the far point's failure belongs to: if the stream replicates and the
world does not, then the one world that keeps the cue is distinguished by the world it is and not by the seeds it was
run with.

**What it cannot do.** *Two streams are two samples*, both at one budget and one arm. *And the stream is not a
redraw of everything*: `--support-seed` and `--partition-seed` default to `seed0`, so the claim that only the
training seeds moved rests on the seven fingerprints being identical, which is evidence and not a proof. *And the
world axis is not redrawn here*: the card's world is the one world, so a stream that failed would not say whether
another world's stream would too. *And a probe is not a mechanism.*
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
#: the card's own 500-update run and the two clean streams this unit draws
CARD = {"run": Path("runs/e380_earned_label_cue0_actionsource_20reps.json"), "theta": Path("runs/e380_theta")}
RUNS = {s: {"run": Path(f"runs/e403_earned_label_stream{s}_iters500_20reps.json"),
            "theta": Path(f"runs/e403_theta_stream{s}")} for s in (1, 2)}
#: `e396`'s artifact, which holds the five worlds' far-point span the stream's is measured against
WORLDS = Path("runs/e396_the_far_point_on_all_five_worlds.json")
PINNED = ("circuit", "circuit_size", "readout_subset", "readout_size", "basis", "support", "task_names",
          "task_readout_widths", "loop_cue_at", "loop_world_dims", "loop_world_leak", "loop_world_modes",
          "loop_world_nonlinear", "readout_from_world", "closed_loop", "lr", "batch", "iters", "repeats",
          "cue_sha1", "feedback_sha1", "n_cue", "action_sha1", "n_action", "drive_from_cue", "loop_drive_from_cue",
          "world_drive_sha1", "world_read_sha1", "world_coupling_sha1", "cue_seed")
STREAM = ("seed0", "readout_seed", "loop_seed")
DRAWN = ("readout_subset", "cue_sha1", "feedback_sha1", "action_sha1", "world_drive_sha1", "world_read_sha1",
         "world_coupling_sha1")
GAIN = 0.05
STABLE = 0.05
UNSTABLE = 0.10
SMALL = 1.0 / 3.0
LARGE = 2.0 / 3.0
CLAIMS = (
    ("AC1", "one configuration except the stream",
     "Every recorded field is in the pinned set, which must be identical across the three runs, or in the stream set",
     "falsifier: a pinned field differing between two runs, or a field in neither list"),
    ("AC2", "and the draws are the card's",
     "The read-out draw's fingerprint and all six environment fingerprints take one value across the three runs",
     "falsifier: any of the seven differing"),
    ("AC3", f"and the recovery replicates on every stream, by {GAIN:.2f}",
     "Each new stream's body reads at 500 updates at least 0.05 above its own connectome reading",
     "falsifier: either at or below zero"),
    ("AC4", f"and the initial reading does not move, within {STABLE:.2f}",
     "Across the three streams the connectome's own reading of task 0 has a spread of at most 0.05",
     f"falsifier: over {UNSTABLE:.2f}; null: between"),
    ("AC5", f"and the stream axis is small at the far point too, within {SMALL:.2f} of the worlds' span",
     "The three streams' 500-update readings span at most a third of the five worlds' span, 0.3344",
     f"falsifier: more than {LARGE:.2f} of it; refused when that artifact is absent"),
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
    return {**_facts(doc), "circuit": doc.get("circuit"), "support": cfg.get("support"),
            "readout_subset": (doc.get("readout") or {}).get("subset_sha1"),
            "seed0": cfg.get("seed0"), "readout_seed": cfg.get("readout_seed"), "loop_seed": cfg.get("loop_seed"),
            "cue_seed": cfg.get("cue_seed"), "lr": cfg.get("lr"), "batch": cfg.get("batch")}


def reading(card: dict = CARD, runs: dict = RUNS, worlds: Path = WORLDS, arm: str = NAIVE, reps: int = REPS) -> dict:
    from clfly.network.model import RateConfig, build_net

    circ, rs, loop_env, tasks = setup_wide()
    model = build_net(circ, RateConfig(tau=TAU)).torch_model()
    ctx = (model, loop_env, tasks, circ.n_neurons)
    out = {"ok": True, "reason": None, "streams": {}, "settings": {}, "worlds_span": None, "arm": arm, "reps": reps}
    for name, spec in [("card", card)] + [(str(s), r) for s, r in runs.items()]:
        doc = load(spec["run"])
        if not doc:
            return {**out, "ok": False, "reason": f"stream {name}: the artifact is absent"}
        got = one_budget(doc, spec["theta"], ctx, arm=arm, reps=reps)
        if not got.get("ok"):
            return {**out, "ok": False, "reason": f"stream {name}: {got['reason']}"}
        cell = got["cell"]
        out["streams"][name] = {"artifact": spec["run"].name, "iters": doc["config"].get("iters"),
                                "initial_task_0": statistics.fmean(cell[("initial", 0)]),
                                "body_task_0": statistics.fmean(cell[("after_task_0", 0)]),
                                "head_task_0": float(doc["methods"][arm]["replicates"][0]["learned"][0])}
        out["settings"][name] = _settings(doc)
    initials = [s["initial_task_0"] for s in out["streams"].values()]
    bodies = [s["body_task_0"] for s in out["streams"].values()]
    out["spread"] = {"initial": max(initials) - min(initials), "body": max(bodies) - min(bodies)}
    worlds_doc = load(worlds)
    out["worlds_span"] = (float((worlds_doc.get("spread") or {}).get("body"))
                          if worlds_doc and (worlds_doc.get("spread") or {}).get("body") is not None else None)
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a run or its weights is absent"} for c in CLAIMS]
    settings = r["settings"]
    keys = sorted({k for s in settings.values() for k in s})
    unknown = [k for k in keys if k not in PINNED and k not in STREAM]
    pinned = {k: sorted({json.dumps(s.get(k)) for s in settings.values()}) for k in keys if k in PINNED}
    moved = {k: v for k, v in pinned.items() if len(v) > 1}
    j1 = {"id": "AC1", "measured": f"{len(keys)} fields recorded across the three streams: "
                                  f"{len([k for k in keys if k in PINNED])} pinned and "
                                  f"{len([k for k in keys if k in STREAM])} of the stream, with {unknown} in neither "
                                  f"list and {sorted(moved)} of the pinned fields moved",
          "verdict": "MET -- one configuration, and the training stream is the only thing that moves" if
                     (not unknown and not moved) else
          f"FALSIFIER FIRED -- {unknown} in neither list, or {moved} of the pinned fields moved"}

    card_value = {f: settings["card"].get(f) for f in DRAWN}
    bad2 = {f: sorted({s.get(f) for s in settings.values()}) for f in DRAWN
            if {s.get(f) for s in settings.values()} != {card_value[f]}}
    j2 = {"id": "AC2", "measured": f"the read-out draw and the six environment fingerprints take "
                                   f"{len({json.dumps([s.get(f) for f in DRAWN]) for s in settings.values()})} "
                                   f"distinct value(s) across the three streams",
          "verdict": "MET -- the draws are the card's own, so the streams differ in the training seeds alone" if
                     not bad2 else f"FALSIFIER FIRED -- {bad2} differ from the card's"}

    gains = {n: r["streams"][n]["body_task_0"] - r["streams"][n]["initial_task_0"] for n in ("1", "2")}
    short = {n: round(v, 4) for n, v in gains.items() if v < GAIN}
    j3 = {"id": "AC3", "measured": f"the two new streams' gains over their own connectome readings are "
                                   f"{ {n: round(v, 4) for n, v in gains.items()} }",
          "verdict": f"MET -- the recovery replicates on every stream, { {n: round(v, 4) for n, v in gains.items()} }"
          if not short else
          f"FALSIFIER FIRED -- {short} is at or below zero: the recovery is the stream's and not the world's"}

    spread = r["spread"]["initial"]
    j4 = {"id": "AC4", "measured": f"the three streams' connectome readings are "
                                   f"{[round(s['initial_task_0'], 4) for s in r['streams'].values()]}, a spread of "
                                   f"{spread:.4f}",
          "verdict": f"MET -- the initial reading does not move, within {STABLE:.2f}" if spread <= STABLE else
          f"FALSIFIER FIRED -- a spread of {spread:.4f}" if spread > UNSTABLE else
          f"NULL -- {spread:.4f}, between {STABLE:.2f} and {UNSTABLE:.2f}"}

    span = r["spread"]["body"]
    worlds_span = r["worlds_span"]
    if not worlds_span:
        j5 = {"id": "AC5", "measured": "the five worlds' span is not on disk", "verdict": "REFUSED"}
    else:
        ratio = span / worlds_span
        j5 = {"id": "AC5", "measured": f"the three streams' 500-update readings span {span:.4f} against the five "
                                       f"worlds' {worlds_span:.4f}, so the stream axis is {ratio:.3f} of the world's",
              "verdict": f"MET -- the stream axis is small at the far point too, {ratio:.3f} of the worlds' span" if
                         ratio <= SMALL else
              f"FALSIFIER FIRED -- {ratio:.3f} of the worlds' span" if ratio > LARGE else
              f"NULL -- {ratio:.3f}, between {SMALL:.2f} and {LARGE:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the far point on the clean stream ==")
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the far point on the clean stream ==")
    print(f"   the card's world and read-out at `--seed0` 1 and 2, `--readout-seed 0 --loop-seed 0`, 500 updates and "
          f"{r['reps']} replicates on the `{r['arm']}` arm")
    print(f"\n   {'stream':>8} {'initial':>9} {'body@500':>10} {'gain':>9} {'head':>8}  {'artifact':>46}")
    for name in ("card", "1", "2"):
        w = r["streams"][name]
        print(f"   {name:>8} {w['initial_task_0']:9.4f} {w['body_task_0']:10.4f} "
              f"{w['body_task_0'] - w['initial_task_0']:9.4f} {w['head_task_0']:8.4f}  {w['artifact']:>46}")

    print("\n== the registered claims, AC1-AC5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e394` found the stream moves the body a third as much as the world at the near point and `e396`")
    print("    found the world axis failing at the far one; this puts the stream axis at the far point)")
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
