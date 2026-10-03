"""E396 -- the far point on all five worlds: the recovery is a minority of them.

`e395` took two of the worlds `e393` drew at the near point to the far one and found the far-end headline **does not
replicate**: the card's world gains 0.0854 over the connectome's own reading by five hundred updates and the two
redraws *lose* 0.20, with the trained head carrying the task instead. It registered the first thing to run --
*"whether the other two of the four behave like 1 and 2 or like the card's world is not measured."*

**This unit runs them.** `--loop-seed 3` and `4` at 500 updates and twenty replicates, so all **five** worlds that
`e393` read at the near point now carry a reading at the far one, each through the same probe. The near readings are
`e393`'s own, read from its artifact, and the far readings are this unit's and `e395`'s, so the two ends of every
world are one instrument.

Five claims, registered before any of the new runs' readings was opened.

- **Q1 -- one configuration except the draw.** Every recorded field is in the placed list, which must be identical in
  all five runs, or in the drawn list. **Falsifier**: a field in neither list, or a placed field moving.
- **Q2 -- and the five runs are five worlds.** Each of the world's three fingerprints takes **five** distinct values.
  **Falsifier**: two of them sharing a fingerprint.
- **Q3 -- and the connectome's own reading does not move.** Across the five runs the connectome's own weights read
  task 0 with a spread of at most **0.10**. **Falsifier**: over **0.15**. **Null**: between. *Seventeen draws have
  read 0.6875 -- five worlds and four streams at the near point, three worlds at the far one -- and these are the
  eighteenth and nineteenth.*
- **Q4 -- and the far end is a minority of the worlds.** At most **two** of the five worlds end above their own
  connectome reading by **0.05** or more. **Falsifier**: three or more, which would say the recovery is ordinary
  rather than one world's. *`e395` found the card's world the only one of three; if 3 and 4 behave like 1 and 2 this
  reads one of five, and if either behaves like the card's it reads two.*
- **Q5 -- and the far end spreads where the near end does not.** The spread of the five worlds' 500-update readings is
  at least **twice** the spread of the same five worlds' **twenty**-update readings, the latter read from `e393`'s
  artifact. **Falsifier**: less than **1.25** times, which would say the two ends spread alike and `e395`'s finding
  was two unlucky draws. **Null**: between.

**What it can do beyond that.** It closes the far point on the same five worlds the near point was closed on, so the
contrast `e395` found is a five-world statement rather than a three-world one, and the card's own revision -- "the
near point is the game's and the far point is the world's" -- can be stated with its denominator.

**What it cannot do.** *Five worlds are five samples of one engine draw*: all five come from `--loop-seed`, so
nothing separates which of the eleven drawn fields makes a world one where the world keeps the cue. *And the near
readings are stored rather than rolled*: they are `e393`'s, made with the same instrument at the same budget, and
this unit recomputes none of them. *And one budget, one axis*: 500 updates is the far point, `seed0` is 0 and the
stream is not redrawn. *And a probe is not a mechanism.*
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
#: the card's far point, `e395`'s two redraws of it, and the two this unit adds
RUNS = {
    "card": {"run": Path("runs/e380_earned_label_cue0_actionsource_20reps.json"), "theta": Path("runs/e380_theta")},
    "1": {"run": Path("runs/e395_earned_label_worldseed1_iters500_20reps.json"), "theta": Path("runs/e395_theta_1")},
    "2": {"run": Path("runs/e395_earned_label_worldseed2_iters500_20reps.json"), "theta": Path("runs/e395_theta_2")},
    "3": {"run": Path("runs/e396_earned_label_worldseed3_iters500_20reps.json"), "theta": Path("runs/e396_theta_3")},
    "4": {"run": Path("runs/e396_earned_label_worldseed4_iters500_20reps.json"), "theta": Path("runs/e396_theta_4")},
}
#: `e393`'s artifact, which holds the same five worlds at twenty updates
NEAR = Path("runs/e393_the_card_on_four_more_worlds.json")
PLACED = ("loop_cue_at", "loop_world_leak", "readout_from_world", "loop_world_dims", "closed_loop",
          "loop_world_modes", "loop_world_nonlinear", "repeats", "circuit_size", "readout_size", "basis", "seed0",
          "task_names", "task_readout_widths", "iters", "lr", "batch")
DRAWN = ("loop_seed", "cue_sha1", "feedback_sha1", "n_cue", "action_sha1", "n_action", "drive_from_cue",
         "loop_drive_from_cue", "world_drive_sha1", "world_read_sha1", "world_coupling_sha1")
WORLD_FIELDS = ("world_drive_sha1", "world_read_sha1", "world_coupling_sha1")
STABLE = 0.10
UNSTABLE = 0.15
GAIN = 0.05
MINORITY = 2
SPREADS = 2.0
SPREADS_FIRES = 1.25
CLAIMS = (
    ("Q1", "one configuration except the draw",
     "Every recorded field is in the placed list, which must be identical in all five runs, or in the drawn list",
     "falsifier: a field in neither list, or a placed field differing between two runs"),
    ("Q2", "and the five runs are five worlds",
     "Each of the world's three fingerprints takes five distinct values",
     "falsifier: two of them sharing a fingerprint"),
    ("Q3", f"and the connectome's own reading does not move, within {STABLE:.2f}",
     f"Across the five runs the connectome's own weights read task 0 with a spread of at most {STABLE:.2f}",
     f"falsifier: a spread over {UNSTABLE:.2f}; null: between"),
    ("Q4", f"and the far end is a minority of the worlds, at most {MINORITY}",
     f"At most {MINORITY} of the five worlds end above their own connectome reading by {GAIN:.2f} or more",
     f"falsifier: three or more, which would say the recovery is ordinary rather than one world's"),
    ("Q5", f"and the far end spreads where the near end does not, by {SPREADS:.2f} times",
     "The spread of the five worlds' 500-update readings is at least twice the spread of the same five worlds' "
     "twenty-update readings, the latter read from `e393`'s artifact",
     f"falsifier: less than {SPREADS_FIRES:.2f} times; null: between; refused when that artifact is absent"),
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


def reading(runs: dict = RUNS, near: Path = NEAR, arm: str = NAIVE, reps: int = REPS) -> dict:
    from clfly.network.model import RateConfig, build_net

    circ, rs, loop_env, tasks = setup_wide()
    model = build_net(circ, RateConfig(tau=TAU)).torch_model()
    ctx = (model, loop_env, tasks, circ.n_neurons)
    out = {"ok": True, "reason": None, "worlds": {}, "settings": {}, "near": None, "arm": arm, "reps": reps}
    for name, spec in runs.items():
        doc = load(spec["run"])
        if not doc:
            return {**out, "ok": False, "reason": f"world {name}: the artifact is absent"}
        got = one_budget(doc, spec["theta"], ctx, arm=arm, reps=reps)
        if not got.get("ok"):
            return {**out, "ok": False, "reason": f"world {name}: {got['reason']}"}
        cell = got["cell"]
        out["worlds"][name] = {"artifact": spec["run"].name,
                               "initial_task_0": statistics.fmean(cell[("initial", 0)]),
                               "body_task_0": statistics.fmean(cell[("after_task_0", 0)]),
                               "head_task_0": float(doc["methods"][arm]["replicates"][0]["learned"][0])}
        out["settings"][name] = _settings(doc)
    near_doc = load(near)
    if not near_doc:
        return {**out, "ok": False, "reason": f"{near} is absent, so the near end of the five worlds is not on disk"}
    stored = near_doc.get("worlds") or {}
    missing = [w for w in out["worlds"] if w not in stored]
    if missing:
        return {**out, "ok": False, "reason": f"{near} does not carry the near reading of {missing}"}
    out["near"] = {"artifact": Path(near).name,
                   "readings": {w: float(stored[w]["body_task_0"]) for w in out["worlds"]}}
    draws = {f: sorted({str(s.get(f)) for s in out["settings"].values()}) for f in WORLD_FIELDS}
    initials = [w["initial_task_0"] for w in out["worlds"].values()]
    bodies = [w["body_task_0"] for w in out["worlds"].values()]
    nears = list(out["near"]["readings"].values())
    out["spread"] = {"initial": max(initials) - min(initials), "body": max(bodies) - min(bodies),
                     "near": max(nears) - min(nears)}
    out["draws"] = draws
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a run, its weights or the near readings is "
                                                        "absent"} for c in CLAIMS]
    settings = r["settings"]
    keys = sorted({k for s in settings.values() for k in s})
    unknown = [k for k in keys if k not in PLACED and k not in DRAWN]
    placed = {k: sorted({json.dumps(s.get(k)) for s in settings.values()}) for k in keys if k in PLACED}
    moved = {k: v for k, v in placed.items() if len(v) > 1}
    j1 = {"id": "Q1", "measured": f"{len(keys)} fields recorded across the five runs: "
                                  f"{len([k for k in keys if k in PLACED])} placed and "
                                  f"{len([k for k in keys if k in DRAWN])} drawn, with {unknown} in neither list and "
                                  f"{sorted(moved)} of the placed fields moved",
          "verdict": "MET -- one configuration, and the environment's own draw is the only thing that moves" if
                     (not unknown and not moved) else
          f"FALSIFIER FIRED -- {unknown} in neither list, or {moved} of the placed fields moved"}

    counts = {f: len(v) for f, v in r["draws"].items()}
    good2 = all(c == 5 for c in counts.values())
    j2 = {"id": "Q2", "measured": f"the five runs take {counts} distinct fingerprint(s)",
          "verdict": "MET -- the five runs are five worlds" if good2 else
          f"FALSIFIER FIRED -- {counts} is not five distinct values on every map"}

    j3 = {"id": "Q3", "measured": f"the connectome's own readings are "
                                  f"{[round(w['initial_task_0'], 4) for w in r['worlds'].values()]}, a spread of "
                                  f"{r['spread']['initial']:.4f}",
          "verdict": f"MET -- the connectome's own reading does not move, within {STABLE:.2f}" if
                     r["spread"]["initial"] <= STABLE else
          f"FALSIFIER FIRED -- a spread of {r['spread']['initial']:.4f}" if r["spread"]["initial"] > UNSTABLE else
          f"NULL -- {r['spread']['initial']:.4f}, between the bars"}

    gains = {w: r["worlds"][w]["body_task_0"] - r["worlds"][w]["initial_task_0"] for w in r["worlds"]}
    above = {w: round(v, 4) for w, v in gains.items() if v >= GAIN}
    j4 = {"id": "Q4", "measured": f"the gain over the connectome's own reading at 500 updates is "
                                  f"{ {w: round(v, 4) for w, v in gains.items()} }, so {len(above)} of the five "
                                  f"worlds end above it by the bar",
          "verdict": f"MET -- the far end is a minority of the worlds, {len(above)} of five" if len(above) <= MINORITY
          else f"FALSIFIER FIRED -- {len(above)} of the five worlds end above it: the recovery is not one world's"}

    near_spread = r["spread"]["near"]
    far_spread = r["spread"]["body"]
    ratio = far_spread / near_spread if near_spread else float("nan")
    j5 = {"id": "Q5", "measured": f"the five worlds' 500-update readings span {far_spread:.4f} against their "
                                  f"twenty-update span of {near_spread:.4f}, so the far end spreads {ratio:.2f} "
                                  f"times as much",
          "verdict": f"MET -- the far end spreads where the near end does not, {ratio:.2f} times" if ratio >= SPREADS
          else f"FALSIFIER FIRED -- only {ratio:.2f} times: the two ends spread alike" if ratio < SPREADS_FIRES else
          f"NULL -- {ratio:.2f}, between {SPREADS_FIRES:.2f} and {SPREADS:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the far point on all five worlds ==")
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the far point on all five worlds ==")
    print(f"   the card's five worlds at 500 updates, {r['reps']} replicates on the `{r['arm']}` arm, against "
          f"`e393`'s twenty-update readings of the same five")
    print(f"\n   {'world':>7} {'initial':>9} {'body@20':>9} {'body@500':>10} {'gain':>8} {'head':>8}  {'artifact':>46}")
    for name in ("card", "1", "2", "3", "4"):
        w = r["worlds"][name]
        print(f"   {name:>7} {w['initial_task_0']:9.4f} {r['near']['readings'][name]:9.4f} "
              f"{w['body_task_0']:10.4f} {w['body_task_0'] - w['initial_task_0']:8.4f} {w['head_task_0']:8.4f}  "
              f"{w['artifact']:>46}")

    print("\n== the registered claims, Q1-Q5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e395` found the far-end headline does not replicate on two worlds and registered that the other")
    print("    two of `e393`'s four were not measured; this runs them, so all five carry both ends)")
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
