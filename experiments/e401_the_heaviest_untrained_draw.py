"""E401 -- the heaviest untrained draw: does the path weight's lead survive a fresh cue population?

`e400` put five properties of the cue population against the four measured outcomes and found **one** that makes the
card's world an extreme: the total absolute weight of the edges from its one-hop frontier into the action population,
**77.34** against a largest loser of 48.78, with a rank correlation of 0.9. It registered what that leaves -- *"five
points with one positive, so the path weight is a lead for a later unit rather than evidence, and what would test it
is a fresh cue draw with a high path weight"*.

**This unit runs that test.** A search over **32** cue draws measures each one's path weight and its cue-to-action
distance without rolling anything, and the criterion -- registered before any training -- is the **heaviest draw that
`e398` and `e399` did not train**. That draw is run at the card's two ends, twenty updates and five hundred, twenty
replicates. Five claims, registered before any of the new runs' readings was opened.

- **Y1 -- and the selection is the heaviest untrained draw.** Over the 32 cue draws the chosen one carries the
  largest path weight among those outside the four already trained, and the search is at least **16** draws wide.
  **Falsifier**: a heavier untrained draw in the search, or fewer than 16 examined.
- **Y2 -- and it is heavier than the card's world.** Its path weight exceeds the card's **77.34**. **Falsifier**:
  below it, which would say the heaviest draw measured is the one that already recovered and the lead has no fresh
  test.
- **Y3 -- and the lead's prediction is that it recovers.** Its body reads at five hundred updates at least **0.05
  above** its own connectome reading. **Falsifier**: at or below zero, which would say the path weight is not
  sufficient either and the lead `e400` produced is dead.
- **Y4 -- and the initial reading does not move.** Across the six measured worlds the connectome's own reading of
  task 0 has a spread of at most **0.05**. **Falsifier**: over **0.10**. **Null**: between.
- **Y5 -- and the weight still tracks the outcomes.** Over the six worlds the path weight's rank correlation with
  the far-point gain stays at an absolute value of at least **0.7**, against the **0.9** it had over five.
  **Falsifier**: below **0.5**, which would say the sixth world broke the ordering the fifth produced.

**What it can do beyond that.** It is the test `e400` asked for: one fresh cue population, chosen by the property
alone, measured at the end where the worlds differ. A recovery here makes the path weight a candidate mechanism for
the one world that keeps the cue; a failure retires it, and either answer is a result about a property that can be
computed from a circuit before anything is rolled.

**What it cannot do.** *One fresh draw*: the criterion picks the heaviest, so a single failure retires the weight for
the heavy end of its range and not for the property in general, and a single recovery is one point added to five.
*And the weight is one of many*: `e400`'s other four properties are unretested, and the cue's weighted spectrum and
its overlap with the read-out draw are unmeasured. *And the search is 32 draws*, so a heavier population outside it
is not seen. *And it is near geometry*: the weight is the circuit's and the draw's, and nothing here says how a
gradient update uses it. *And a probe is not a mechanism.*
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e369_why_the_cliff_is_where_it_is import _reachable, distance
from experiments.e379_what_the_body_did import NAIVE, TAU
from experiments.e380_what_the_training_built import setup as setup_wide
from experiments.e382_when_the_world_loses_it import one_budget

REPS = 20
SEARCH = tuple(range(1, 33))
#: the cue draws `e398` and `e399` already trained, which the criterion excludes
TRAINED = (1, 3, 9, 14)
#: the six worlds: the card's, the four `e398`/`e399` ran, and the heaviest untrained draw
WORLDS = {
    "card": {"cueseed": None, "run": Path("runs/e380_earned_label_cue0_actionsource_20reps.json"),
             "theta": Path("runs/e380_theta")},
    "cue3": {"cueseed": 3, "run": Path("runs/e398_earned_label_cueseed3_iters500_20reps.json"),
             "theta": Path("runs/e398_theta_cue3_iters500")},
    "cue9": {"cueseed": 9, "run": Path("runs/e399_earned_label_cueseed9_iters500_20reps.json"),
             "theta": Path("runs/e399_theta_cue9_iters500")},
    "cue14": {"cueseed": 14, "run": Path("runs/e399_earned_label_cueseed14_iters500_20reps.json"),
              "theta": Path("runs/e399_theta_cue14_iters500")},
    "cue1": {"cueseed": 1, "run": Path("runs/e398_earned_label_cueseed1_iters500_20reps.json"),
             "theta": Path("runs/e398_theta_cue1_iters500")},
    "chosen": {"cueseed": None, "run": None, "theta": None},
}
ENGINE = {"n_symbols": 12, "tau": TAU, "scale": 1.0, "gain": 1.0, "noise": 1.0, "world_modes": 0,
          "world_leak": 0.35, "world_dims": 8, "world_coupled": True, "cue_at": 0, "drive_from_cue": False}
CARD_WEIGHT = 77.3429355527635
GAIN = 0.05
STABLE = 0.05
UNSTABLE = 0.10
KEEPS = 0.7
BREAKS = 0.5
MIN_SEARCH = 16
CLAIMS = (
    ("Y1", f"and the selection is the heaviest untrained draw, over at least {MIN_SEARCH}",
     "Over the 32 cue draws the chosen one carries the largest path weight among those outside the four already "
     "trained",
     "falsifier: a heavier untrained draw in the search, or fewer than 16 examined"),
    ("Y2", "and it is heavier than the card's world",
     "Its path weight exceeds the card's 77.34",
     "falsifier: below it, which would leave the lead with no fresh test"),
    ("Y3", f"and the lead's prediction is that it recovers, by {GAIN:.2f}",
     "Its body reads at 500 updates at least 0.05 above its own connectome reading",
     "falsifier: at or below zero"),
    ("Y4", f"and the initial reading does not move, within {STABLE:.2f}",
     "Across the six measured worlds the connectome's own reading of task 0 has a spread of at most 0.05",
     f"falsifier: over {UNSTABLE:.2f}; null: between"),
    ("Y5", f"and the weight still tracks the outcomes, at an absolute {KEEPS:.1f}",
     "Over the six worlds the path weight's rank correlation with the far-point gain has an absolute value of at "
     "least 0.7",
     f"falsifier: below {BREAKS:.1f}"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _rank(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    for r, i in enumerate(order):
        ranks[i] = float(r)
    return ranks


def _spearman(a: list[float], b: list[float]) -> float:
    ra, rb = _rank(a), _rank(b)
    ma, mb = statistics.fmean(ra), statistics.fmean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = sum((x - ma) ** 2 for x in ra) ** 0.5
    db = sum((y - mb) ** 2 for y in rb) ** 0.5
    return num / (da * db) if da and db else 0.0


def reading(search=SEARCH, worlds=dict(WORLDS), engine=dict(ENGINE), arm: str = NAIVE, reps: int = REPS) -> dict:
    from clfly.connectome.graph import WEIGHT_SCALE
    from clfly.network import env as fly_env
    from clfly.network.model import RateConfig, build_net

    circ, rs, loop_env, tasks = setup_wide()
    w = np.asarray(circ.net.weights(WEIGHT_SCALE).todense(), dtype=np.float64)
    mask = w != 0
    model = build_net(circ, RateConfig(tau=TAU)).torch_model()
    ctx = (model, loop_env, tasks, circ.n_neurons)
    out = {"ok": True, "reason": None, "circuit": circ.name, "edges": int(mask.sum()), "search": {},
           "chosen_seed": None, "worlds": {}, "arm": arm, "reps": reps}
    for seed in search:
        e = fly_env.build(circ, readout_subset=rs, seed=0, cue_seed=seed, **engine)
        cue = np.asarray(e.cue_neurons)
        act = np.asarray(e.action_neurons)
        one = _reachable(mask, cue)
        out["search"][str(seed)] = {"path_weight": float(np.abs(w[np.ix_(act, one)]).sum()),
                                    "cue_to_action": distance(mask, cue, act)}
    pool = {s: v for s, v in out["search"].items() if int(s) not in TRAINED}
    if not pool:
        return {**out, "ok": False, "reason": "the search holds no draw outside the four already trained"}
    chosen = max(pool, key=lambda s: pool[s]["path_weight"])
    out["chosen_seed"] = int(chosen)
    worlds = dict(worlds)
    worlds["chosen"] = {"cueseed": int(chosen),
                        "run": Path(f"runs/e401_earned_label_cueseed{chosen}_iters500_20reps.json"),
                        "theta": Path(f"runs/e401_theta_cue{chosen}_iters500")}
    out["near"] = Path(f"runs/e401_earned_label_cueseed{chosen}_iters20_20reps.json")
    out["near_theta"] = Path(f"runs/e401_theta_cue{chosen}_iters20")
    for name, spec in worlds.items():
        doc = load(spec["run"])
        if not doc:
            return {**out, "ok": False, "reason": f"world {name}: the artifact is absent"}
        got = one_budget(doc, spec["theta"], ctx, arm=arm, reps=reps)
        if not got.get("ok"):
            return {**out, "ok": False, "reason": f"world {name}: {got['reason']}"}
        cell = got["cell"]
        initial = statistics.fmean(cell[("initial", 0)])
        body = statistics.fmean(cell[("after_task_0", 0)])
        out["worlds"][name] = {"cueseed": spec["cueseed"], "artifact": spec["run"].name,
                               "initial_task_0": initial, "body_task_0": body, "gain": body - initial,
                               "head_task_0": float(doc["methods"][arm]["replicates"][0]["learned"][0])}
    order = sorted(out["worlds"], key=lambda n: out["worlds"][n]["gain"])
    out["order"] = order
    gains = [out["worlds"][n]["gain"] for n in order]
    weights = [out["search"][str(out["worlds"][n]["cueseed"])]["path_weight"] if n != "card" else CARD_WEIGHT
               for n in order]
    out["correlation"] = _spearman(weights, gains)
    out["weight_values"] = {n: w_v for n, w_v in zip(order, weights)}
    initials = [v["initial_task_0"] for v in out["worlds"].values()]
    out["spread"] = {"initial": max(initials) - min(initials)}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the search or a run is absent"} for c in CLAIMS]
    pool = {s: v for s, v in r["search"].items() if int(s) not in TRAINED}
    heaviest = max(pool, key=lambda s: pool[s]["path_weight"])
    good1 = (int(heaviest) == r["chosen_seed"] and len(r["search"]) >= MIN_SEARCH)
    j1 = {"id": "Y1", "measured": f"over {len(r['search'])} cue draws the heaviest untrained is seed {heaviest} at "
                                  f"{pool[heaviest]['path_weight']:.2f}, and the chosen seed is {r['chosen_seed']}",
          "verdict": f"MET -- the selection is the heaviest untrained draw, over {len(r['search'])} draws" if good1
          else f"FALSIFIER FIRED -- the heaviest untrained is {heaviest} over {len(r['search'])} draws"}

    weight = r["weight_values"].get("chosen", pool[str(r["chosen_seed"])]["path_weight"])
    j2 = {"id": "Y2", "measured": f"the chosen draw's path weight is {weight:.2f} against the card's "
                                  f"{CARD_WEIGHT:.2f}",
          "verdict": f"MET -- the heaviest draw measured is untrained and gets a fresh test, {weight:.2f}" if
                     weight > CARD_WEIGHT else
          f"FALSIFIER FIRED -- {weight:.2f} is not above the card's and the lead has no fresh test"}

    w = r["worlds"].get("chosen")
    if not w:
        j3 = {"id": "Y3", "measured": "the chosen draw was not measured", "verdict": "REFUSED"}
    else:
        j3 = {"id": "Y3", "measured": f"the chosen draw's gain over its own connectome reading is {w['gain']:+.4f} "
                                      f"(initial {w['initial_task_0']:.4f}, body {w['body_task_0']:.4f})",
              "verdict": f"MET -- the lead's prediction holds, {w['gain']:+.4f}" if w["gain"] >= GAIN else
              f"FALSIFIER FIRED -- {w['gain']:+.4f} is at or below zero: the path weight is not sufficient either"}

    spread = r["spread"]["initial"]
    j4 = {"id": "Y4", "measured": f"the six worlds' connectome readings are "
                                  f"{[round(v['initial_task_0'], 4) for v in r['worlds'].values()]}, a spread of "
                                  f"{spread:.4f}",
          "verdict": f"MET -- the initial reading does not move, within {STABLE:.2f}" if spread <= STABLE else
          f"FALSIFIER FIRED -- a spread of {spread:.4f}" if spread > UNSTABLE else
          f"NULL -- {spread:.4f}, between {STABLE:.2f} and {UNSTABLE:.2f}"}

    rho = r["correlation"]
    j5 = {"id": "Y5", "measured": f"over the six worlds the path weight's rank correlation with the gain is "
                                  f"{rho:+.3f}, against 0.9 over five",
          "verdict": f"MET -- the weight still tracks the outcomes, {rho:+.3f}" if abs(rho) >= KEEPS else
          f"FALSIFIER FIRED -- {rho:+.3f}: the sixth world broke the ordering" if abs(rho) < BREAKS else
          f"NULL -- {rho:+.3f}, between {BREAKS:.1f} and {KEEPS:.1f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the heaviest untrained draw ==")
        print(f"   REFUSED -- {r.get('reason', 'the search or a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the heaviest untrained draw ==")
    print(f"   {len(r['search'])} cue draws measured for their path weight and distance without rolling anything; "
          f"the heaviest untrained is seed {r['chosen_seed']}")
    top = sorted(r["search"].items(), key=lambda kv: -kv[1]["path_weight"])[:5]
    print(f"   the search's five heaviest: " + ", ".join(f"seed {s} {v['path_weight']:.2f} (d={v['cue_to_action']})"
                                                         for s, v in top))
    print(f"\n   {'world':>8} {'cue seed':>9} {'gain':>9} {'path weight':>12} {'head':>7}")
    for name in r["order"]:
        v = r["worlds"][name]
        print(f"   {name:>8} {str(v['cueseed']):>9} {v['gain']:9.4f} {r['weight_values'][name]:12.2f} "
              f"{v['head_task_0']:7.4f}")

    print("\n== the registered claims, Y1-Y5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e400` found the path weight the one property that made the card's world an extreme and asked for a")
    print("    fresh draw with a high weight; this searches 32 draws, takes the heaviest untrained one and runs it)")
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
