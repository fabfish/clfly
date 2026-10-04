"""E399 -- the rest of the two-hop class: the other two cue draws at distance 2, at the far point.

`e398` moved the cue population alone and found that the distance does not decide: the card's world is at distance
**2** and recovers by **+0.0854**, while a *different* cue population at the same distance 2 loses by **−0.1635**. It
registered what that leaves -- the distance-2 set *"contains at least one of each behaviour and the next question is
what separates them"* -- and it trained one draw of each class, so the distance-2 class's membership was three draws
(the card's, 3, 9, 14) with one of them measured.

**This unit measures the other two.** Cue seeds **9** and **14** -- the remaining distance-2 draws of the same
sixteen-draw search -- at the card's far point, five hundred updates and twenty replicates, with the card's world and
cue seed 3 read from `e380`'s and `e398`'s artifacts through the same probe. Five claims, registered before any of
the new runs' readings was opened.

- **V1 -- and only the cue population moved.** Each of the four cue-population runs reproduces the card's action and
  feedback fingerprints and its three world fingerprints, and differs from the card's in the cue's. **Falsifier**:
  any of those six differing, or the cue's agreeing.
- **V2 -- and the two new draws are the other two at distance 2.** Over the sixteen cue draws the distance-2 seeds
  are exactly **3, 9 and 14**, and the two new runs are seeds 9 and 14. **Falsifier**: the set differing, or a new
  run at another distance. **Bound**: at least **8** draws examined.
- **V3 -- and neither of them recovers.** Both new draws' bodies read at five hundred updates at least **0.05
  below** their own connectome reading. **Falsifier**: either at or above −0.05, which would say the distance-2 class
  has more than one recovering member and `e398`'s result was one draw's.
- **V4 -- and the initial reading does not move.** Across the card's world, the two new draws and the two `e398`
  already ran, the connectome's own reading of task 0 has a spread of at most **0.05**. **Falsifier**: over **0.10**.
  **Null**: between.
- **V5 -- and the two-hop class is not the recovering class.** Of the **four** cue draws at distance 2 -- the card's,
  3, 9 and 14 -- at most **one** ends above its own connectome reading by 0.05. **Falsifier**: two or more, which
  would say the two-hop geometry carries more than a coincidence.

**What it can do beyond that.** It closes the class `e398` opened: with the card's world and cue seed 3 already
measured, two more draws make all three of the search's distance-2 cue populations measured at the far point, so the
question *"is the distance what decides it"* is answered on the whole class rather than on a sample of it.

**What it cannot do.** *One draw of the distance-1 class is trained* (seed 1, from `e398`), so the contrast is four
two-hop draws against one one-hop one. *And the search is sixteen draws*: a distance-2 population outside it is not
measured, and the thirteen one-hop ones are measured for their distance and not trained. *And it names no property of
the cue population*: if the class is not uniform, what separates the member that recovers from the others is still
unmeasured. *And a probe is not a mechanism.*
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
SEARCH = tuple(range(1, 17))
TWO_HOP = 2
NEW_SEEDS = (9, 14)
#: the five trained worlds: the card's, the two `e398` ran, and the two this unit adds
WORLDS = {
    "card": {"run": Path("runs/e380_earned_label_cue0_actionsource_20reps.json"), "theta": Path("runs/e380_theta"),
             "cueseed": None},
    "cue3": {"run": Path("runs/e398_earned_label_cueseed3_iters500_20reps.json"),
             "theta": Path("runs/e398_theta_cue3_iters500"), "cueseed": 3},
    "cue9": {"run": Path("runs/e399_earned_label_cueseed9_iters500_20reps.json"),
             "theta": Path("runs/e399_theta_cue9_iters500"), "cueseed": 9},
    "cue14": {"run": Path("runs/e399_earned_label_cueseed14_iters500_20reps.json"),
              "theta": Path("runs/e399_theta_cue14_iters500"), "cueseed": 14},
    "cue1": {"run": Path("runs/e398_earned_label_cueseed1_iters500_20reps.json"),
             "theta": Path("runs/e398_theta_cue1_iters500"), "cueseed": 1},
}
#: the engine's own parameters, which are what makes an environment here the one a run had
ENGINE = {"n_symbols": 12, "tau": TAU, "scale": 1.0, "gain": 1.0, "noise": 1.0, "world_modes": 0,
          "world_leak": 0.35, "world_dims": 8, "world_coupled": True, "cue_at": 0, "drive_from_cue": False}
DRIVEN = ("action_sha1", "feedback_sha1", "world_drive_sha1", "world_read_sha1", "world_coupling_sha1")
GAIN = 0.05
STABLE = 0.05
UNSTABLE = 0.10
MINORITY = 1
MIN_SEARCH = 8
CLAIMS = (
    ("V1", "and only the cue population moved",
     "Each of the four cue-population runs reproduces the card's action and feedback fingerprints and its three "
     "world fingerprints, and differs from the card's in the cue's",
     "falsifier: any of those six differing, or the cue's agreeing"),
    ("V2", f"and the two new draws are the other two at distance {TWO_HOP}, over at least {MIN_SEARCH} draws",
     f"Over the sixteen cue draws the distance-2 seeds are exactly 3, 9 and 14, and the two new runs are 9 and 14",
     "falsifier: the set differing, or a new run at another distance"),
    ("V3", f"and neither of them recovers, by {GAIN:.2f}",
     "Both new draws' bodies read at 500 updates at least 0.05 below their own connectome reading",
     "falsifier: either at or above -0.05"),
    ("V4", f"and the initial reading does not move, within {STABLE:.2f}",
     "Across the five trained worlds the connectome's own reading of task 0 has a spread of at most 0.05",
     f"falsifier: over {UNSTABLE:.2f}; null: between"),
    ("V5", f"and the two-hop class is not the recovering class, at most {MINORITY} of four",
     "Of the four cue draws at distance 2 at most one ends above its own connectome reading by 0.05",
     "falsifier: two or more, which would say the two-hop geometry carries more than a coincidence"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def reading(search=SEARCH, worlds=WORLDS, engine=dict(ENGINE), arm: str = NAIVE, reps: int = REPS) -> dict:
    from clfly.connectome.graph import WEIGHT_SCALE
    from clfly.network import env as fly_env
    from clfly.network.model import RateConfig, build_net

    circ, rs, loop_env, tasks = setup_wide()
    mask = np.asarray((circ.net.weights(WEIGHT_SCALE) != 0).todense(), dtype=bool)
    model = build_net(circ, RateConfig(tau=TAU)).torch_model()
    ctx = (model, loop_env, tasks, circ.n_neurons)
    base = fly_env.build(circ, readout_subset=rs, seed=0, **engine)
    out = {"ok": True, "reason": None, "circuit": circ.name, "edges": int(mask.sum()),
           "card_draw": base.summary(), "search": {}, "two_hop": {}, "worlds": {}, "arm": arm, "reps": reps}
    for seed in search:
        e = fly_env.build(circ, readout_subset=rs, seed=0, cue_seed=seed, **engine)
        out["search"][str(seed)] = {"cue_to_action": distance(mask, np.asarray(e.cue_neurons),
                                                             np.asarray(e.action_neurons)),
                                    "cue_sha1": e.summary()["cue_sha1"]}
    out["two_hop"] = sorted(int(s) for s in out["search"] if out["search"][s]["cue_to_action"] == TWO_HOP)
    for name, spec in worlds.items():
        doc = load(spec["run"])
        if not doc:
            return {**out, "ok": False, "reason": f"world {name}: the artifact is absent"}
        got = one_budget(doc, spec["theta"], ctx, arm=arm, reps=reps)
        if not got.get("ok"):
            return {**out, "ok": False, "reason": f"world {name}: {got['reason']}"}
        cell = got["cell"]
        out["worlds"][name] = {"artifact": spec["run"].name, "cueseed": spec["cueseed"],
                               "iters": doc["config"].get("iters"),
                               "initial_task_0": statistics.fmean(cell[("initial", 0)]),
                               "body_task_0": statistics.fmean(cell[("after_task_0", 0)]),
                               "head_task_0": float(doc["methods"][arm]["replicates"][0]["learned"][0]),
                               "draw": {f: (doc.get("env_draw") or {}).get(f) for f in ("cue_sha1",) + DRIVEN}}
    initials = [w["initial_task_0"] for w in out["worlds"].values()]
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
        draw = w["draw"]
        differs = {f: [base.get(f), draw.get(f)] for f in DRIVEN if draw.get(f) != base.get(f)}
        if differs or draw["cue_sha1"] == base["cue_sha1"]:
            bad[name] = {"driven fields that moved": differs,
                         "cue is the card's": draw["cue_sha1"] == base["cue_sha1"]}
    j1 = {"id": "V1", "measured": f"each of the four cue-population runs against the card's own draw: {len(bad)} of "
                                  f"them moved a field other than the cue's, or kept the card's cue",
          "verdict": "MET -- the cue population is the only field that moved" if not bad else
          f"FALSIFIER FIRED -- {bad}"}

    seen = len(r["search"])
    good2 = (r["two_hop"] == [3, 9, 14] and seen >= MIN_SEARCH
             and all(r["worlds"][f"cue{s}"]["cueseed"] == s for s in NEW_SEEDS))
    j2 = {"id": "V2", "measured": f"over {seen} cue draws the distance-2 seeds are {r['two_hop']}, and the new runs "
                                  f"carry cue seeds {[r['worlds'][f'cue{s}']['cueseed'] for s in NEW_SEEDS]}",
          "verdict": f"MET -- the two new draws are the other two at distance {TWO_HOP}" if good2 else
          f"FALSIFIER FIRED -- the distance-2 seeds are {r['two_hop']} over {seen} draws"}

    if any(f"cue{s}" not in r["worlds"] for s in NEW_SEEDS):
        j3 = {"id": "V3", "measured": "a new draw was not measured", "verdict": "REFUSED"}
    else:
        gains = {s: r["worlds"][f"cue{s}"]["body_task_0"] - r["worlds"][f"cue{s}"]["initial_task_0"]
                 for s in NEW_SEEDS}
        good3 = all(g <= -GAIN for g in gains.values())
        j3 = {"id": "V3", "measured": f"the new draws' gains over their own connectome readings are "
                                      f"{ {s: round(g, 4) for s, g in gains.items()} }",
              "verdict": f"MET -- neither recovers, { {s: round(g, 4) for s, g in gains.items()} }" if good3 else
              f"FALSIFIER FIRED -- { {s: round(g, 4) for s, g in gains.items()} } is not below the bar"}

    spread = r["spread"]["initial"]
    j4 = {"id": "V4", "measured": f"the five worlds' connectome readings are "
                                  f"{[round(w['initial_task_0'], 4) for w in r['worlds'].values()]}, a spread of "
                                  f"{spread:.4f}",
          "verdict": f"MET -- the initial reading does not move, within {STABLE:.2f}" if spread <= STABLE else
          f"FALSIFIER FIRED -- a spread of {spread:.4f}" if spread > UNSTABLE else
          f"NULL -- {spread:.4f}, between {STABLE:.2f} and {UNSTABLE:.2f}"}

    class_members = ["card"] + [f"cue{s}" for s in r["two_hop"] if f"cue{s}" in r["worlds"]]
    gains = {n: r["worlds"][n]["body_task_0"] - r["worlds"][n]["initial_task_0"] for n in class_members}
    above = {n: round(v, 4) for n, v in gains.items() if v >= GAIN}
    j5 = {"id": "V5", "measured": f"over the {len(class_members)} distance-2 draws measured at the far point the "
                                  f"gains are { {n: round(v, 4) for n, v in gains.items()} }, so {len(above)} of "
                                  f"them recover",
          "verdict": f"MET -- the two-hop class is not the recovering class, {len(above)} of {len(class_members)}"
          if len(above) <= MINORITY else
          f"FALSIFIER FIRED -- {len(above)} of {len(class_members)} distance-2 draws recover"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the rest of the two-hop class ==")
        print(f"   REFUSED -- {r.get('reason', 'the search or a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the rest of the two-hop class ==")
    print(f"   {len(r['search'])} cue draws on `{r['circuit']}`'s own mask of {r['edges']} edges, with the action and "
          f"feedback populations and the world's three maps held at the card's; the distance-2 seeds are "
          f"{r['two_hop']}")
    print(f"\n   {'world':>7} {'cue seed':>9} {'distance':>9} {'initial':>9} {'body@500':>10} {'gain':>9} {'head':>7}")
    for name, w in r["worlds"].items():
        seed = w["cueseed"]
        d = "-" if seed is None else (r["search"][str(seed)]["cue_to_action"] if str(seed) in r["search"] else "-")
        print(f"   {name:>7} {str(seed):>9} {str(d):>9} {w['initial_task_0']:9.4f} {w['body_task_0']:10.4f} "
              f"{w['body_task_0'] - w['initial_task_0']:9.4f} {w['head_task_0']:7.4f}")

    print("\n== the registered claims, V1-V5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e398` found the cue's distance did not decide and measured one of the three distance-2 draws;")
    print("    this runs the other two, so the whole class is measured at the far point)")
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
