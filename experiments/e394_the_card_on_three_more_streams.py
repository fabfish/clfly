"""E394 -- the card on three more streams: the other half of the absence, with the draws pinned.

`e392` measured two absences in the card's cell. `e393` discharged the first -- the world -- by reseeding the
environment four times. The second is the **seed stream**: `seed0` takes **one** value over every closed-loop
artifact, and `e339` measured that `--seed0` draws **three** things at once -- the training seeds, the read-out draw
and the environment's populations -- so the clean stream `e340` established is the one where the read-out and the
environment are held by `--readout-seed 0 --loop-seed 0` and only the training seeds move.

**This unit runs that stream three times.** `seed0` = **1**, **2**, **3**, with `--readout-seed 0 --loop-seed 0`, at
the card's canonical near point -- the wide step, cue at 0, the action source, 20 updates, 20 replicates -- against
the card's own 20-update artifact, whose flags default to `seed0 = 0` and whose draws this unit verified are
identical: the probe at `seed0 = 1` reproduces the read-out subset `59926518137c` and all six environment
fingerprints exactly.

Five claims, registered before any of the new runs' readings was opened.

- **O1 -- one configuration except the stream, and the draws are pinned.** Every recorded field is in one of two
  lists: the **pinned** set -- the read-out draw's fingerprint, the six environment fingerprints, the circuit, the
  tasks and their widths, and the card's placed settings -- which must be identical across the four runs, and the
  **stream** set, which is `seed0` and the two flags made explicit to hold the draws. **Falsifier**: a pinned field
  differing between two streams, or a field in neither list.
- **O2 -- and the streams are four streams.** `seed0` takes four distinct values, and the pinned set takes one value
  each. **Falsifier**: two streams sharing `seed0`, or a pinned field taking more than one value.
- **O3 -- and the drawn draws are the card's.** The read-out subset and all six environment fingerprints equal the
  card's own, so the streams differ in the training seeds and in nothing else. **Falsifier**: any of the seven
  differing from the card's.
- **O4 -- and the connectome's own reading does not move, and neither does the body's.** Across the four streams the
  connectome's own reading of task 0 has a spread of at most **0.10** and so does the trained body's. **Falsifier**:
  either spread over **0.15**. **Null**: between. *The first half is the control's own check -- the initial reading
  depends on the initial body, the pinned world and the task's own examples, and the stream moves none of them -- and
  the second is what the unit is for.*
- **O5 -- and the headline replicates on every stream.** On **every** one of the three new streams the body after
  twenty updates reads below the connectome's own weights on the same stream by at least **0.05**. **Falsifier**: any
  stream where it is not below by 0.05.

**What it can do beyond that.** With `e393` it discharges both halves of the card's own worst clause: the world four
times over, and the training stream three times over, at the same cell and the same instrument. Together they turn
*"every number the line has published is conditional on one world and one stream"* into a measurement of how much of
it is the game.

**What it cannot do.** *Three streams are three samples*, drawn at one budget, at the card's near point. *And the
stream is not a redraw of everything*: `--support-seed` and `--partition-seed` default to `seed0`, so a run that set
neither while moving `seed0` would move more than the training seeds -- this unit's own probe is the check that they
did not, and the check is a fingerprint and not an argument. *And the invariance `e393` reported is not explained
here*: the connectome's own reading was 0.6875 on five worlds, and this unit shows it is also 0.6875 on four streams,
which says the reading does not depend on the draw on either axis and still does not say why the value is what it is.
*And a probe is not a mechanism.*
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
#: the card's own 20-update artifact, and the three clean streams this unit draws
CARD = {"run": Path("runs/e389_earned_label_iters20_cue0_actionsource_20reps.json"),
        "theta": Path("runs/e389_theta_20")}
RUNS = {s: {"run": Path(f"runs/e394_earned_label_stream{s}_iters20_20reps.json"),
            "theta": Path(f"runs/e394_theta_{s}")} for s in (1, 2, 3)}
#: what the stream must not move: the drawn identities and the card's placed settings
PINNED = ("circuit", "circuit_size", "readout_subset", "readout_size", "basis", "support", "task_names",
          "task_readout_widths", "loop_cue_at", "loop_world_dims", "loop_world_leak", "loop_world_modes",
          "loop_world_nonlinear", "readout_from_world", "closed_loop", "lr", "batch", "iters", "repeats",
          "cue_sha1", "feedback_sha1", "n_cue", "action_sha1", "n_action", "drive_from_cue", "loop_drive_from_cue",
          "world_drive_sha1", "world_read_sha1", "world_coupling_sha1")
#: and what it moves: the stream, and the two flags e339 named as the control that holds the other two draws
STREAM = ("seed0", "readout_seed", "loop_seed")
DRAWN_IDENTITY = ("readout_subset", "cue_sha1", "feedback_sha1", "action_sha1", "world_drive_sha1", "world_read_sha1",
                  "world_coupling_sha1")
STABLE = 0.10
UNSTABLE = 0.15
COST = 0.05
CLAIMS = (
    ("O1", "one configuration except the stream, and the draws are pinned",
     "Every recorded field is in the pinned set, which must be identical across the four runs, or in the stream set",
     "falsifier: a pinned field differing between two streams, or a field in neither list"),
    ("O2", "and the streams are four streams",
     "`seed0` takes four distinct values and every pinned field takes one value",
     "falsifier: two streams sharing `seed0`, or a pinned field taking more than one value"),
    ("O3", "and the draws are the card's own",
     "The read-out draw's fingerprint and all six environment fingerprints equal the card's",
     "falsifier: any of the seven differing from the card's"),
    ("O4", f"and neither the connectome's reading nor the body's moves, within {STABLE:.2f}",
     f"Across the four streams the connectome's own reading of task 0 and the trained body's reading each have a "
     f"spread of at most {STABLE:.2f}",
     f"falsifier: either spread over {UNSTABLE:.2f}; null: between"),
    ("O5", f"and the headline replicates, by {COST:.2f}",
     "On every one of the three new streams the body after twenty updates reads below the connectome's own weights "
     "on the same stream by at least 0.05",
     "falsifier: any stream where it is not below by 0.05"),
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
            "lr": cfg.get("lr"), "batch": cfg.get("batch")}


def reading(card: dict = CARD, runs: dict = RUNS, arm: str = NAIVE, reps: int = REPS) -> dict:
    from clfly.network.model import RateConfig, build_net

    circ, rs, loop_env, tasks = setup_wide()
    model = build_net(circ, RateConfig(tau=TAU)).torch_model()
    ctx = (model, loop_env, tasks, circ.n_neurons)
    out = {"ok": True, "reason": None, "streams": {}, "settings": {}, "arm": arm, "reps": reps}
    for name, spec in [("card", card)] + [(str(s), r) for s, r in runs.items()]:
        doc = load(spec["run"])
        if not doc:
            return {**out, "ok": False, "reason": f"stream {name}: the artifact is absent"}
        got = one_budget(doc, spec["theta"], ctx, arm=arm, reps=reps)
        if not got.get("ok"):
            return {**out, "ok": False, "reason": f"stream {name}: {got['reason']}"}
        cell = got["cell"]
        out["streams"][name] = {"artifact": spec["run"].name,
                                "initial_task_0": statistics.fmean(cell[("initial", 0)]),
                                "body_task_0": statistics.fmean(cell[("after_task_0", 0)]),
                                "head_task_0": float(doc["methods"][arm]["replicates"][0]["learned"][0])}
        out["settings"][name] = _settings(doc)
    initials = [s["initial_task_0"] for s in out["streams"].values()]
    bodies = [s["body_task_0"] for s in out["streams"].values()]
    out["spread"] = {"initial": max(initials) - min(initials), "body": max(bodies) - min(bodies)}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a run or its weights is absent"}
                for c in CLAIMS]
    settings = r["settings"]
    keys = sorted({k for s in settings.values() for k in s})
    unknown = [k for k in keys if k not in PINNED and k not in STREAM]
    pinned = {k: sorted({json.dumps(s.get(k)) for s in settings.values()}) for k in keys if k in PINNED}
    moved = {k: v for k, v in pinned.items() if len(v) > 1}
    j1 = {"id": "O1", "measured": f"{len(keys)} fields recorded across the four streams: "
                                  f"{len([k for k in keys if k in PINNED])} pinned and "
                                  f"{len([k for k in keys if k in STREAM])} of the stream, with {unknown} in neither "
                                  f"list and {sorted(moved)} of the pinned fields moved",
          "verdict": "MET -- one configuration, and the training stream is the only thing that moves" if
                     (not unknown and not moved) else
          f"FALSIFIER FIRED -- {unknown} in neither list, or {moved} of the pinned fields moved"}

    seeds = sorted({s.get("seed0") for s in settings.values()})
    j2 = {"id": "O2", "measured": f"`seed0` takes the values {seeds} across the four streams, and the "
                                  f"{len(pinned) - len(moved)} pinned fields that are recorded take one value each",
          "verdict": "MET -- the streams are four streams" if len(seeds) == 4 and not moved else
          f"FALSIFIER FIRED -- {seeds} is not four values, or {moved} of the pinned fields moved"}

    card_value = {f: settings["card"].get(f) for f in DRAWN_IDENTITY}
    bad3 = {f: [card_value[f]] + sorted({s.get(f) for s in settings.values() if s.get(f) != card_value[f]})
            for f in DRAWN_IDENTITY if {s.get(f) for s in settings.values()} != {card_value[f]}}
    j3 = {"id": "O3", "measured": f"the read-out draw and the six environment fingerprints take "
                                  f"{len({json.dumps([s.get(f) for f in DRAWN_IDENTITY]) for s in settings.values()})} "
                                  f"distinct value(s) across the four streams",
          "verdict": "MET -- the draws are the card's own, so the streams differ in the training seeds alone" if
                     not bad3 else f"FALSIFIER FIRED -- {bad3} differ from the card's"}

    def band(key):
        spread = r["spread"][key]
        return (f"MET -- within {STABLE:.2f}" if spread <= STABLE else
                f"FALSIFIER FIRED -- a spread of {spread:.4f}" if spread > UNSTABLE else
                f"NULL -- {spread:.4f}, between {STABLE:.2f} and {UNSTABLE:.2f}")

    j4 = {"id": "O4", "measured": f"the connectome's own readings are "
                                  f"{[round(s['initial_task_0'], 4) for s in r['streams'].values()]} (spread "
                                  f"{r['spread']['initial']:.4f}) and the bodies' are "
                                  f"{[round(s['body_task_0'], 4) for s in r['streams'].values()]} (spread "
                                  f"{r['spread']['body']:.4f})",
          "verdict": f"MET -- neither moves, the initial {band('initial')} and the body {band('body')}" if
                     band("initial").startswith("MET") and band("body").startswith("MET") else
          f"FALSIFIER FIRED -- the initial {band('initial')} and the body {band('body')}" if
          band("initial").startswith("FALSIFIER") or band("body").startswith("FALSIFIER") else
          f"NULL -- the initial {band('initial')} and the body {band('body')}"}

    costs = {w: r["streams"][w]["initial_task_0"] - r["streams"][w]["body_task_0"] for w in ("1", "2", "3")}
    short = {w: round(v, 4) for w, v in costs.items() if v < COST}
    card_cost = r["streams"]["card"]["initial_task_0"] - r["streams"]["card"]["body_task_0"]
    j5 = {"id": "O5", "measured": f"the cost of twenty updates on each stream is "
                                  f"{ {w: round(v, 4) for w, v in costs.items()} }, against the card's own "
                                  f"{card_cost:.4f}",
          "verdict": f"MET -- the headline replicates on all three new streams, by {COST:.2f} or more" if not short
          else f"FALSIFIER FIRED -- {short} is not below its own initial by {COST:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the card on three more streams ==")
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the card on three more streams ==")
    print(f"   the card's 20-update cell at `--seed0` 1 to 3 with `--readout-seed 0 --loop-seed 0`, {r['reps']} "
          f"replicates on the `{r['arm']}` arm, read through the same probe")
    print(f"\n   {'stream':>8} {'initial':>9} {'body@20':>9} {'cost':>8} {'head':>8}  {'artifact':>50}")
    for name in ("card", "1", "2", "3"):
        w = r["streams"][name]
        print(f"   {name:>8} {w['initial_task_0']:9.4f} {w['body_task_0']:9.4f} "
              f"{w['initial_task_0'] - w['body_task_0']:8.4f} {w['head_task_0']:8.4f}  {w['artifact']:>50}")

    print("\n== the registered claims, O1-O5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e393` discharged the world half of `e392`'s M5 absence; this is the stream half, with the "
          "read-out")
    print("    draw and the environment pinned by the two seeds `e339` named)")
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
