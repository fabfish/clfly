"""E398 -- the cue population alone: the field the two-hop world is about, moved by itself.

`e397` measured the cue's distance to the action population on the card's five worlds and found a perfect
separation: the one draw at distance **2** is the one whose body keeps the cue at five hundred updates, and the four
at distance **1** are the ones that lose it. It registered what that leaves -- *"a redraw that moved the cue
population alone ... is what would turn it into one"* -- and the engine could not do it, because `--loop-seed` moves
the three populations and the three maps together.

**This unit adds the engine's missing seed and asks the question again with one field under it.** `cue_seed` draws
the cue's twelve neurons from a second generator and consumes nothing from the environment's, so the action and
feedback populations and the world's three maps stay exactly the ones the card's world has. The selection of which
cue draws to train is a **geometric criterion registered before any training**: the first of sixteen cue draws whose
cue-to-action distance is 2, and the first whose distance is 1. Both are then run at the card's two ends, twenty
updates and five hundred, twenty replicates.

Five claims, registered before any run's reading was opened.

- **T1 -- and only the cue population moved.** Each of the two trained draws reproduces the card's action and
  feedback fingerprints and its three world fingerprints, and differs from the card's in the cue's. **Falsifier**:
  any of those six differing, or the cue's agreeing.
- **T2 -- and the search found both geometries.** Over the sixteen cue draws examined, at least one has a cue-to-
  action distance of **2** and at least one of **1**, and the two chosen are the first of each. **Falsifier**: one
  of the two absent. **Bound**: at least **8** draws examined, a count that grows with the search.
- **T3 -- and the outcome follows the distance.** The chosen distance-**2** draw's body reads at five hundred updates
  at least **0.05 above** its own connectome reading, and the chosen distance-**1** draw's reads at least **0.05
  below** its own. **Falsifier**: either draw on the other side of its bar, which would say the distance `e397`
  separated the card's five worlds by is not what decides it.
- **T4 -- and the initial reading does not move.** Across the three worlds -- the card's, the distance-2 draw and
  the distance-1 draw -- the connectome's own reading of task 0 has a spread of at most **0.05**. **Falsifier**: over
  **0.10**. **Null**: between.
- **T5 -- and the near point does not separate them.** The two draws' readings at **twenty** updates differ from
  each other by less than **0.05**, while their readings at **five hundred** differ by at least **0.10**.
  **Falsifier**: the near gap at or above 0.05, or the far gap under 0.10. *This is `e396`'s R5 made a comparison:
  the draw is invisible before the weights move and worth a third of the reading after.*

**What it can do beyond that.** It turns `e397`'s association into an experiment on the field it named: one engine,
one circuit, one world, and the cue population the only thing that differs between the two runs -- so if the outcome
follows the distance here, the distance is not a marker of a redraw that happened to carry it. It also gives the
benchmark engine the seed its redraw series has been missing since `e339` found that `--seed0` draws three things at
once.

**What it cannot do.** *Two draws are two points*: one at each distance, so the claim is that the two chosen draws
behave as the distance says and not that every draw at that distance does; the other fourteen cue draws are measured
for their distance and not trained. *And the criterion is a selection*: the draws were chosen by their distance, so
what a training run would show without that choice is not measured. *And one cue population of the same size*: the
field moved is *which* twelve neurons carry the cue and not how many, so a cue population of another width is a
different question. *And a probe is not a mechanism.*
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e369_why_the_cliff_is_where_it_is import distance
from experiments.e379_what_the_body_did import NAIVE, TAU
from experiments.e380_what_the_training_built import setup as setup_wide
from experiments.e382_when_the_world_loses_it import one_budget

REPS = 20
#: the cue draws whose distance this unit measures, and the two it trains
SEARCH = tuple(range(1, 17))
WANT = (2, 1)
#: the card's two ends, so the instrument is one probe on all the worlds
CARD = {"near": {"run": Path("runs/e389_earned_label_iters20_cue0_actionsource_20reps.json"),
                 "theta": Path("runs/e389_theta_20")},
        "far": {"run": Path("runs/e380_earned_label_cue0_actionsource_20reps.json"),
                "theta": Path("runs/e380_theta")}}
#: the engine's own parameters, which are what makes an environment here the one a run had
ENGINE = {"n_symbols": 12, "tau": TAU, "scale": 1.0, "gain": 1.0, "noise": 1.0, "world_modes": 0,
          "world_leak": 0.35, "world_dims": 8, "world_coupled": True, "cue_at": 0, "drive_from_cue": False}
DRIVEN = ("action_sha1", "feedback_sha1", "world_drive_sha1", "world_read_sha1", "world_coupling_sha1")
GAIN = 0.05
STABLE = 0.05
UNSTABLE = 0.10
NEAR_SAME = 0.05
FAR_SPLIT = 0.10
MIN_SEARCH = 8
CLAIMS = (
    ("T1", "and only the cue population moved",
     "Each of the two trained draws reproduces the card's action and feedback fingerprints and its three world "
     "fingerprints, and differs from the card's in the cue's",
     "falsifier: any of those six differing, or the cue's agreeing"),
    ("T2", f"and the search found both geometries, over at least {MIN_SEARCH} draws",
     "At least one of the sixteen cue draws has a cue-to-action distance of 2 and at least one of 1, and the two "
     "chosen are the first of each",
     "falsifier: one of the two absent"),
    ("T3", f"and the outcome follows the distance, by {GAIN:.2f}",
     "The chosen distance-2 draw reads at least 0.05 above its own connectome reading at 500 updates and the chosen "
     "distance-1 draw at least 0.05 below it",
     "falsifier: either draw on the other side of its bar"),
    ("T4", f"and the initial reading does not move, within {STABLE:.2f}",
     "Across the card's world and the two chosen cue draws the connectome's own reading of task 0 has a spread of at "
     "most 0.05",
     f"falsifier: over {UNSTABLE:.2f}; null: between"),
    ("T5", "and the near point does not separate them",
     "The two draws' twenty-update readings differ by less than 0.05 while their five-hundred-update readings differ "
     "by at least 0.10",
     "falsifier: the near gap at or above 0.05, or the far gap under 0.10"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def reading(search=SEARCH, card=CARD, engine=dict(ENGINE), arm: str = NAIVE, reps: int = REPS) -> dict:
    from clfly.connectome.graph import WEIGHT_SCALE
    from clfly.network import env as fly_env
    from clfly.network.model import RateConfig, build_net

    circ, rs, loop_env, tasks = setup_wide()
    mask = np.asarray((circ.net.weights(WEIGHT_SCALE) != 0).todense(), dtype=bool)
    model = build_net(circ, RateConfig(tau=TAU)).torch_model()
    ctx = (model, loop_env, tasks, circ.n_neurons)
    base = fly_env.build(circ, readout_subset=rs, seed=0, **engine)
    out = {"ok": True, "reason": None, "circuit": circ.name, "edges": int(mask.sum()),
           "card_draw": base.summary(), "search": {}, "chosen": {}, "worlds": {}, "arm": arm, "reps": reps}
    for seed in search:
        e = fly_env.build(circ, readout_subset=rs, seed=0, cue_seed=seed, **engine)
        out["search"][str(seed)] = {"cue_to_action": distance(mask, np.asarray(e.cue_neurons),
                                                             np.asarray(e.action_neurons)),
                                    "cue_sha1": e.summary()["cue_sha1"]}
    for want in WANT:
        hit = [int(s) for s in sorted(out["search"], key=int) if out["search"][s]["cue_to_action"] == want]
        if not hit:
            return {**out, "ok": False, "reason": f"no cue draw in the search has a distance of {want}"}
        out["chosen"][str(want)] = hit[0]
    for c in WANT:
        seed = out["chosen"][str(c)]
        for b in (20, 500):
            run = Path(f"runs/e398_earned_label_cueseed{seed}_iters{b}_20reps.json")
            theta = Path(f"runs/e398_theta_cue{seed}_iters{b}")
            doc = load(run)
            if not doc:
                return {**out, "ok": False, "reason": f"cue draw {seed} (distance {c}) at {b}: the artifact is "
                                                      f"absent"}
            got = one_budget(doc, theta, ctx, arm=arm, reps=reps)
            if not got.get("ok"):
                return {**out, "ok": False, "reason": f"cue draw {seed} (distance {c}) at {b}: {got['reason']}"}
            cell = got["cell"]
            out["worlds"].setdefault(f"cue{c}", {})[str(b)] = {
                "artifact": run.name, "cueseed": seed, "iters": doc["config"].get("iters"),
                "initial_task_0": statistics.fmean(cell[("initial", 0)]),
                "body_task_0": statistics.fmean(cell[("after_task_0", 0)]),
                "head_task_0": float(doc["methods"][arm]["replicates"][0]["learned"][0]),
                "draw": {f: (doc.get("env_draw") or {}).get(f) for f in ("cue_sha1",) + DRIVEN}}
    for name, spec in card.items():
        doc = load(spec["run"])
        if not doc:
            return {**out, "ok": False, "reason": f"the card's {name} end is absent"}
        got = one_budget(doc, spec["theta"], ctx, arm=arm, reps=reps)
        if not got.get("ok"):
            return {**out, "ok": False, "reason": f"the card's {name} end: {got['reason']}"}
        cell = got["cell"]
        out["worlds"].setdefault("card", {})[str(20 if name == "near" else 500)] = {
            "artifact": spec["run"].name, "iters": doc["config"].get("iters"),
            "initial_task_0": statistics.fmean(cell[("initial", 0)]),
            "body_task_0": statistics.fmean(cell[("after_task_0", 0)]),
            "head_task_0": float(doc["methods"][arm]["replicates"][0]["learned"][0]),
            "draw": {f: (doc.get("env_draw") or {}).get(f) for f in ("cue_sha1",) + DRIVEN}}
    initials = [w["20"]["initial_task_0"] for w in out["worlds"].values()]
    out["spread"] = {"initial": max(initials) - min(initials)}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the search, a run or its weights is absent"}
                for c in CLAIMS]
    base = r["card_draw"]
    bad = {}
    for name, w in r["worlds"].items():
        if name == "card":
            continue
        draw = w["20"]["draw"]
        differs = {f: [base.get(f), draw.get(f)] for f in DRIVEN if draw.get(f) != base.get(f)}
        if differs or draw["cue_sha1"] == base["cue_sha1"]:
            bad[name] = {"driven fields that moved": differs, "cue is the card's": draw["cue_sha1"] == base["cue_sha1"]}
    j1 = {"id": "T1", "measured": f"each of the two chosen draws against the card's own draw: "
                                  f"{len(bad)} of them moved a field other than the cue's, or kept the card's cue",
          "verdict": "MET -- the cue population is the only field that moved" if not bad else
          f"FALSIFIER FIRED -- {bad}"}

    seen = len(r["search"])
    found2 = [s for s, v in r["search"].items() if v["cue_to_action"] == 2]
    found1 = [s for s, v in r["search"].items() if v["cue_to_action"] == 1]
    first = {str(w): (sorted([int(s) for s in r["search"] if r["search"][s]["cue_to_action"] == w])[0]
                      if any(r["search"][s]["cue_to_action"] == w for s in r["search"]) else None) for w in WANT}
    good2 = bool(found2) and bool(found1) and seen >= MIN_SEARCH and all(r["chosen"][str(w)] == first[str(w)]
                                                                         for w in WANT)
    j2 = {"id": "T2", "measured": f"over {seen} cue draws, {len(found2)} have a distance of 2 and {len(found1)} a "
                                  f"distance of 1; the chosen are {r['chosen']} against the first of each {first}",
          "verdict": f"MET -- both geometries are in the search, over {seen} draws" if good2 else
          f"FALSIFIER FIRED -- {len(found2)} at distance 2 and {len(found1)} at 1 over {seen} draws"}

    if any(f"cue{c}" not in r["worlds"] for c in WANT):
        j3 = {"id": "T3", "measured": "a chosen draw was not measured", "verdict": "REFUSED"}
    else:
        gains = {}
        for c in WANT:
            w = r["worlds"][f"cue{c}"]
            gains[c] = w["500"]["body_task_0"] - w["500"]["initial_task_0"]
        good3 = gains[2] >= GAIN and gains[1] <= -GAIN
        j3 = {"id": "T3", "measured": f"the distance-2 draw's gain over its own connectome reading is {gains[2]:+.4f} "
                                      f"and the distance-1 draw's is {gains[1]:+.4f}",
              "verdict": f"MET -- the outcome follows the distance, {gains[2]:+.4f} against {gains[1]:+.4f}" if good3
              else f"FALSIFIER FIRED -- {gains[2]:+.4f} and {gains[1]:+.4f} do not sit on opposite sides of the bar"}

    spread = r["spread"]["initial"]
    j4 = {"id": "T4", "measured": f"the three worlds' connectome readings are "
                                  f"{[round(w['20']['initial_task_0'], 4) for w in r['worlds'].values()]}, a spread of "
                                  f"{spread:.4f}",
          "verdict": f"MET -- the initial reading does not move, within {STABLE:.2f}" if spread <= STABLE else
          f"FALSIFIER FIRED -- a spread of {spread:.4f}" if spread > UNSTABLE else
          f"NULL -- {spread:.4f}, between {STABLE:.2f} and {UNSTABLE:.2f}"}

    if any(f"cue{c}" not in r["worlds"] for c in WANT):
        j5 = {"id": "T5", "measured": "a chosen draw was not measured", "verdict": "REFUSED"}
    else:
        near = abs(r["worlds"]["cue2"]["20"]["body_task_0"] - r["worlds"]["cue1"]["20"]["body_task_0"])
        far = abs(r["worlds"]["cue2"]["500"]["body_task_0"] - r["worlds"]["cue1"]["500"]["body_task_0"])
        good5 = near < NEAR_SAME and far >= FAR_SPLIT
        j5 = {"id": "T5", "measured": f"the two chosen draws read {near:.4f} apart at twenty updates and {far:.4f} "
                                      f"apart at five hundred",
              "verdict": f"MET -- the near point does not separate them and the far point does, {near:.4f} against "
                         f"{far:.4f}" if good5 else
              f"FALSIFIER FIRED -- {near:.4f} apart at twenty and {far:.4f} at five hundred"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the cue population alone ==")
        print(f"   REFUSED -- {r.get('reason', 'the search or a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the cue population alone ==")
    print(f"   {len(r['search'])} cue draws on `{r['circuit']}`'s own mask of {r['edges']} edges, with the action and "
          f"feedback populations and the world's three maps held at the card's; the chosen are {r['chosen']}")
    dist = {s: r["search"][s]["cue_to_action"] for s in sorted(r["search"], key=int)}
    print(f"\n   the search's cue-to-action distances: {dist}")
    print(f"\n   {'world':>8} {'cue seed':>9} {'initial':>9} {'body@20':>9} {'body@500':>10} {'far gain':>9} {'head@500':>9}")
    for name, w in r["worlds"].items():
        seed = "-" if name == "card" else r["chosen"][name.replace("cue", "")]
        far = w.get("500", {})
        print(f"   {name:>8} {str(seed):>9} {w['20']['initial_task_0']:9.4f} {w['20']['body_task_0']:9.4f} "
              f"{far.get('body_task_0', float('nan')):10.4f} "
              f"{far.get('body_task_0', float('nan')) - far.get('initial_task_0', float('nan')):9.4f} "
              f"{far.get('head_task_0', float('nan')):9.4f}")

    print("\n== the registered claims, T1-T5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e397` found the cue's distance to the action population separated the one world that keeps the cue")
    print("    from the four that lose it on a redraw that moved eleven fields; this engine seed moves the cue's")
    print("    twelve neurons and nothing else)")
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
