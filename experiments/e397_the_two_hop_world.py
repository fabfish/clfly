"""E397 -- the two-hop world: the cue's distance to the action population on all five draws.

`e396` put all five of the card's worlds at both ends of the trajectory and found that **one of them** recovers by
five hundred updates while four end between 0.166 and 0.249 **below** an untrained body. It registered what that
leaves: *"nothing separates which of the eleven drawn fields makes a world one where the body keeps the cue; `e369`'s
distance and `e368`'s horizon are the candidates and neither is varied here."*

**This unit measures the first candidate on all five worlds, and it needs no training at all.** `e369`'s instrument
computes the shortest directed path from the cue population to the action population in the circuit's own mask, and
the environment's draw is a seed, so the five worlds' paths are five calls. Each environment built here reproduces
the six fingerprints its run recorded, which is what makes the measurement the geometry those runs had.

Five claims, registered before any distance or any reading was opened.

- **R1 -- and the geometry is the runs'.** Each of the five environments built here reproduces the six fingerprints
  its run recorded -- the cue's, the action's, the feedback's and the world's three -- as `e393`'s and `e389`'s
  artifacts carry them. **Falsifier**: any fingerprint differing; **REFUSED** when either artifact is absent.
- **R2 -- and the card's world reproduces `e369`'s distance.** The directed distance from the cue population to the
  action population on the card's world is exactly **2**, the value `e369` measured on the same circuit with the same
  instrument. **Falsifier**: **1**, which would say this unit's environment is not that one, or **3 or more**.
- **R3 -- and the draw moves the distance.** The five worlds' cue-to-action distances take at least **two** distinct
  values. **Falsifier**: all five equal, which would say the path is the circuit's and not the draw's.
- **R4 -- and the distance separates the one that recovers from the four that do not.** The world that keeps the cue
  at the far point -- the card's, **+0.0854** at five hundred updates -- has a **strictly longer** cue-to-action path
  than **every** one of the four that lose it. **Falsifier**: any failing world whose distance is at least the
  card's. *This is the unit's own prediction and it is the opposite of the horizon story: `e369`'s formula,
  `tau - 2 - d`, makes the card's world the one with the **shortest** horizon of the five, so if the recovery
  tracked the horizon it would be the four redraws that recover.*
- **R5 -- and the draw is invisible until training.** The spread of the five worlds' **initial** readings is at most
  a **tenth** of the spread of their five-hundred-update readings. **Falsifier**: more than a **third**. **Null**:
  between. **REFUSED** when `e396`'s artifact is absent.

**What it can do beyond that.** It names a graph property, computable from a circuit before anything is rolled, that
separates the world that keeps the cue from the four that do not -- and it puts that property against the horizon
formula the line already published, in the direction the formula does not predict. It also states the asymmetry the
whole redraw series has been circling: the five worlds are identical in what an untrained body can read and differ
by a third of the reading once trained.

**What it cannot do.** *Five points are five points*: the separation is on five draws, one of which recovers, so it
is an association and not a mechanism, and the cue-to-action distance is one of eleven fields the draw moves, so a
world that differs in its path differs in its populations and its maps too. *And it is the near geometry*: the
distance is a property of the circuit and the draw and not of the trained body, so it cannot say how an update uses
the extra hop. *And it measures one distance*: the cue-to-feedback path is measured and reported, and the
action-to-feedback and cue-to-read-out paths are not. *And a probe is not a mechanism.*
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e369_why_the_cliff_is_where_it_is import distance
from experiments.e379_what_the_body_did import TAU
from experiments.e380_what_the_training_built import setup as setup_wide

#: the five worlds, the run that records each one's own draw, and the seed the environment is built from
WORLDS = {
    "card": {"record": Path("runs/e389_earned_label_iters20_cue0_actionsource_20reps.json"), "seed": 0},
    "1": {"record": Path("runs/e393_earned_label_worldseed1_iters20_20reps.json"), "seed": 1},
    "2": {"record": Path("runs/e393_earned_label_worldseed2_iters20_20reps.json"), "seed": 2},
    "3": {"record": Path("runs/e393_earned_label_worldseed3_iters20_20reps.json"), "seed": 3},
    "4": {"record": Path("runs/e393_earned_label_worldseed4_iters20_20reps.json"), "seed": 4},
}
#: `e396`'s artifact, which holds the same five worlds' readings at both ends
READINGS = Path("runs/e396_the_far_point_on_all_five_worlds.json")
#: the engine's own parameters, which are what makes an environment here the one a run had
ENGINE = {"n_symbols": 12, "tau": TAU, "scale": 1.0, "gain": 1.0, "noise": 1.0, "world_modes": 0,
          "world_leak": 0.35, "world_dims": 8, "world_coupled": True, "cue_at": 0, "drive_from_cue": False}
FINGERPRINTS = ("cue_sha1", "action_sha1", "feedback_sha1", "world_drive_sha1", "world_read_sha1",
                "world_coupling_sha1")
GAIN = 0.05
TENTH = 0.10
THIRD = 0.33
CLAIMS = (
    ("R1", "and the geometry is the runs'",
     "Each of the five environments built here reproduces the six fingerprints its run recorded",
     "falsifier: any fingerprint differing; refused when either artifact is absent"),
    ("R2", "and the card's world reproduces `e369`'s distance",
     "The directed distance from the cue population to the action population on the card's world is exactly 2",
     "falsifier: 1, or 3 or more"),
    ("R3", "and the draw moves the distance",
     "The five worlds' cue-to-action distances take at least two distinct values",
     "falsifier: all five equal"),
    ("R4", "and the distance separates the one that recovers from the four that do not",
     "The world that keeps the cue at the far point has a strictly longer cue-to-action path than every one of the "
     "four that lose it",
     "falsifier: any failing world whose distance is at least the card's"),
    ("R5", f"and the draw is invisible until training, within {TENTH:.2f} of the far spread",
     "The spread of the five worlds' initial readings is at most a tenth of the spread of their five-hundred-update "
     "readings",
     f"falsifier: more than {THIRD:.2f}; null: between; refused when that artifact is absent"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def reading(worlds: dict = WORLDS, readings: Path = READINGS, engine: dict = ENGINE) -> dict:
    from clfly.connectome.graph import WEIGHT_SCALE
    from clfly.network import env as fly_env

    circ, rs, loop_env, tasks = setup_wide()
    mask = np.asarray((circ.net.weights(WEIGHT_SCALE) != 0).todense(), dtype=bool)
    readings_doc = load(readings)
    if not readings_doc:
        return {"ok": False, "reason": f"{readings} is absent, so the five worlds' readings are not on disk",
                "worlds": {}, "draws": {}, "spread": {}}
    stored = readings_doc.get("worlds") or {}
    out = {"ok": True, "reason": None, "circuit": circ.name, "edges": int(mask.sum()), "worlds": {},
           "draws": {}, "spread": {}}
    for name, spec in worlds.items():
        record = load(spec["record"])
        if not record:
            return {**out, "ok": False, "reason": f"world {name}: the run that records its draw is absent"}
        if name not in stored:
            return {**out, "ok": False, "reason": f"{readings} does not carry world {name}"}
        e = fly_env.build(circ, readout_subset=rs, seed=spec["seed"], **engine)
        s = e.summary()
        ref = record.get("env_draw") or {}
        out["draws"][name] = {"seed": spec["seed"], "record": spec["record"].name,
                              "fingerprints": {f: s.get(f) for f in FINGERPRINTS},
                              "recorded": {f: ref.get(f) for f in FINGERPRINTS},
                              "agrees": all(s.get(f) == ref.get(f) for f in FINGERPRINTS)}
        out["worlds"][name] = {
            "seed": spec["seed"],
            "cue_to_action": distance(mask, np.asarray(e.cue_neurons), np.asarray(e.action_neurons)),
            "cue_to_feedback": distance(mask, np.asarray(e.cue_neurons), np.asarray(e.feedback_neurons)),
            "n_cue": int(len(e.cue_neurons)), "n_action": int(len(e.action_neurons)),
            "initial_task_0": float(stored[name]["initial_task_0"]),
            "far_task_0": float(stored[name]["body_task_0"]),
        }
    initials = [w["initial_task_0"] for w in out["worlds"].values()]
    fars = [w["far_task_0"] for w in out["worlds"].values()]
    out["spread"] = {"initial": max(initials) - min(initials), "far": max(fars) - min(fars)}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the geometry or the readings are not on disk"}
                for c in CLAIMS]
    bad = {n: {f: [d["fingerprints"][f], d["recorded"][f]] for f in FINGERPRINTS
               if d["fingerprints"][f] != d["recorded"][f]} for n, d in r["draws"].items()}
    bad = {n: v for n, v in bad.items() if v}
    j1 = {"id": "R1", "measured": f"{len(r['draws'])} environments built from the circuit's mask of "
                                  f"{r['edges']} edges, each checked against the six fingerprints its run recorded: "
                                  f"{len(bad)} disagree",
          "verdict": "MET -- the geometry measured here is the geometry the five runs had" if not bad else
          f"FALSIFIER FIRED -- {bad}"}

    card = r["worlds"]["card"]["cue_to_action"]
    j2 = {"id": "R2", "measured": f"the card's world's cue-to-action distance, on the circuit's own mask, is {card}",
          "verdict": "MET -- the card's world reproduces `e369`'s measured 2" if card == 2 else
          f"FALSIFIER FIRED -- the distance is {card} and not 2"}

    values = {n: w["cue_to_action"] for n, w in r["worlds"].items()}
    j3 = {"id": "R3", "measured": f"the five worlds' cue-to-action distances are {values}",
          "verdict": "MET -- the draw moves the distance" if len(set(values.values())) >= 2 else
          f"FALSIFIER FIRED -- every world's distance is {values}"}

    failing = {n: v for n, v in values.items() if n != "card"}
    losers = {n: r["worlds"][n]["far_task_0"] - r["worlds"][n]["initial_task_0"] for n in failing}
    lose = {n: v for n, v in losers.items() if v < GAIN}
    ok4 = bool(lose) and all(values["card"] > values[n] for n in lose)
    j4 = {"id": "R4", "measured": f"the card's world's distance is {values['card']} and the four that lose the cue "
                                  f"have { {n: values[n] for n in failing} }, with the losers' far-point gains "
                                  f"{ {n: round(v, 4) for n, v in losers.items()} }",
          "verdict": "MET -- the one that keeps the cue has the strictly longer path" if ok4 else
          f"FALSIFIER FIRED -- { {n: values[n] for n in lose} } is at least the card's {values['card']}"}

    near, far = r["spread"]["initial"], r["spread"]["far"]
    ratio = near / far if far else float("nan")
    j5 = {"id": "R5", "measured": f"the five worlds' initial readings span {near:.4f} against their "
                                  f"five-hundred-update span of {far:.4f}, so the draw's visible spread before "
                                  f"training is {ratio:.3f} of its spread after",
          "verdict": f"MET -- the draw is invisible until training, {ratio:.3f} of the far spread" if ratio <= TENTH
          else f"FALSIFIER FIRED -- {ratio:.3f} of the far spread is already visible before training" if ratio > THIRD
          else f"NULL -- {ratio:.3f}, between {TENTH:.2f} and {THIRD:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the two-hop world ==")
        print(f"   REFUSED -- {r.get('reason', 'the geometry or the readings are not on disk')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the two-hop world ==")
    print(f"   the five worlds' cue-to-action distance on `{r['circuit']}`'s own mask of {r['edges']} edges, against "
          f"their readings at both ends")
    print(f"\n   {'world':>7} {'seed':>5} {'cue->action':>12} {'cue->feedback':>14} {'initial':>9} {'far':>8} {'gain':>8}")
    for name in ("card", "1", "2", "3", "4"):
        w = r["worlds"][name]
        print(f"   {name:>7} {w['seed']:>5} {str(w['cue_to_action']):>12} {str(w['cue_to_feedback']):>14} "
              f"{w['initial_task_0']:9.4f} {w['far_task_0']:8.4f} "
              f"{w['far_task_0'] - w['initial_task_0']:8.4f}")

    print("\n== the registered claims, R1-R5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e396` found one world in five recovers and registered that nothing separated it from the four;")
    print("    this measures the cue's path to the action population on all five, rolling nothing)")
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
