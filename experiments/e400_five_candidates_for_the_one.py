"""E400 -- five candidates for the one: does any near geometry order the four measured outcomes?

`e399` closed the distance-2 class: one of its four cue populations keeps the cue at five hundred updates and three
lose it by as much as the one-hop world does, so `e397`'s separation was one member's. It registered what that
leaves -- *"what makes the card's cue population the one is still open: not its size, not its distance, and not its
head"* -- and named no property in the distance's place.

**This unit puts five candidate properties against the four measured outcomes, and trains nothing.** Every candidate
is computed from the circuit's own mask and the drawn populations, so the whole question costs five environment
builds. Four of the five worlds whose far-point readings exist are at the same distance and one is not, so a
property has to do more than the distance does: it is asked to **order all five** the way their readings order them.

Five claims, registered before any property was computed.

- **X1 -- and the distance cannot order them.** The five worlds' cue-to-action distances take **two** values -- 2 for
  the card's world and for cue seeds 3, 9 and 14, and 1 for seed 1 -- so the distance assigns the card's world and
  the three failing two-hop draws the same value and **cannot** order the five. **Falsifier**: the distances taking
  five distinct values, which would make the rest of this unit's question the distance's.
- **X2 -- and no candidate orders them perfectly.** None of the five properties below is monotone in the five
  readings (a rank correlation of exactly +1 or -1). **Falsifier**: one or more is, which would name the property
  `e399` left unnamed. **Bound**: at least **5** candidates and at least **5** worlds.
- **X3 -- and the candidates are not all constant.** At least **three** of the five take at least two distinct values
  across the five worlds, so the ordering test has power. **Falsifier**: fewer than three vary.
- **X4 -- and the readings are the ones already published.** The five worlds' gains are the ones `e398`'s and
  `e399`'s artifacts carry, recomputed through this unit's own probe: the card's positive and the other four negative
  by more than **0.10**. **Falsifier**: any of them on the other side of its sign.
- **X5 -- and no candidate makes the card's world an extreme.** For **every** one of the five properties the card's
  world's value lies inside the range of the four failing worlds' values. **Falsifier**: a property on which the
  card's value is strictly outside that range, which would be a candidate for the one even without perfect ordering.

The five properties: how many neurons the cue population reaches in one hop (**fan-out**); how many it reaches in
exactly two (**two-hop frontier**); how many of the action population it reaches within two (**action overlap**); how
many outgoing edges its twelve neurons carry (**cue out-degree**); and the total absolute weight of the edges running
from its one-hop frontier into the action population (**path weight**).

**What it can do beyond that.** It turns a question into a list: if a property orders the four measured outcomes and
the card's, it is the one to test on a fresh draw, and if none does then the near geometry is not where the answer
is and a later unit has to look at the training rather than at the draw.

**What it cannot do.** *Five points, one positive*: a property that orders them can do so by chance, and the ordering
is a screen for a later experiment and not evidence on its own. *And the candidates are five of many*: the weighted
spectrum of the cue's block, the overlap with the read-out draw and the depth of the action population's tree are all
unmeasured. *And the properties are near geometry*: none of them sees the trained body, so a property that predicts
the outcome is a correlate of the draw until a mechanism names it. *And a probe is not a mechanism.*
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
#: the five worlds whose far-point readings exist, and the cue seed each one's draw carries
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
}
#: the engine's own parameters, which are what makes an environment here the one a run had
ENGINE = {"n_symbols": 12, "tau": TAU, "scale": 1.0, "gain": 1.0, "noise": 1.0, "world_modes": 0,
          "world_leak": 0.35, "world_dims": 8, "world_coupled": True, "cue_at": 0, "drive_from_cue": False}
#: the candidates, in the order the docstring names them
PROPERTIES = ("fan_out", "two_hop_frontier", "action_overlap", "cue_out_degree", "path_weight")
GAIN = 0.10
MIN_WORLDS = 5
MIN_PROPERTIES = 5
MIN_VARYING = 3
CLAIMS = (
    ("X1", "and the distance cannot order them",
     "The five worlds' cue-to-action distances take two values, so the distance assigns the card's world and the "
     "three failing two-hop draws the same one",
     "falsifier: the distances taking five distinct values"),
    ("X2", f"and no candidate orders them perfectly, over at least {MIN_PROPERTIES} candidates and {MIN_WORLDS} worlds",
     "None of the five properties is monotone in the five readings, at a rank correlation of exactly +1 or -1",
     "falsifier: one or more is, which would name the property the previous unit left unnamed"),
    ("X3", f"and the candidates are not all constant, over at least {MIN_VARYING}",
     "At least three of the five properties take at least two distinct values across the five worlds",
     "falsifier: fewer than three vary"),
    ("X4", f"and the readings are the ones already published, by {GAIN:.2f}",
     "The card's world's gain is positive and the other four are negative by more than 0.10",
     "falsifier: any of them on the other side of its sign"),
    ("X5", "and no candidate makes the card's world an extreme",
     "For every property the card's world's value lies inside the range of the four failing worlds' values",
     "falsifier: a property on which the card's value is strictly outside that range"),
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


def strictly_orders(values: list[float]) -> bool:
    """Whether a property's values are strictly increasing or strictly decreasing along the readings' order.

    The claim's word is **monotone**, and a rank correlation is not that: with ties the correlation depends on how
    the ties were broken, and `action_overlap` takes two values over five worlds, so its +1.0 is the tie-breaking's
    and not the property's. A property with a tie cannot order the worlds it ties.
    """
    return all(x < y for x, y in zip(values, values[1:])) or all(x > y for x, y in zip(values, values[1:]))


def _spearman(a: list[float], b: list[float]) -> float:
    ra, rb = _rank(a), _rank(b)
    ma, mb = statistics.fmean(ra), statistics.fmean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = sum((x - ma) ** 2 for x in ra) ** 0.5
    db = sum((y - mb) ** 2 for y in rb) ** 0.5
    return num / (da * db) if da and db else 0.0


def reading(worlds: dict = WORLDS, engine=dict(ENGINE), arm: str = NAIVE, reps: int = REPS) -> dict:
    from clfly.connectome.graph import WEIGHT_SCALE
    from clfly.network import env as fly_env
    from clfly.network.model import RateConfig, build_net

    circ, rs, loop_env, tasks = setup_wide()
    weights = circ.net.weights(WEIGHT_SCALE)
    w = np.asarray(weights.todense(), dtype=np.float64)
    mask = w != 0
    model = build_net(circ, RateConfig(tau=TAU)).torch_model()
    ctx = (model, loop_env, tasks, circ.n_neurons)
    out = {"ok": True, "reason": None, "circuit": circ.name, "edges": int(mask.sum()),
           "worlds": {}, "properties": {}, "order": None}
    gains, props = {}, {p: {} for p in PROPERTIES}
    for name, spec in worlds.items():
        e = (fly_env.build(circ, readout_subset=rs, seed=0, **engine) if spec["cueseed"] is None
             else fly_env.build(circ, readout_subset=rs, seed=0, cue_seed=spec["cueseed"], **engine))
        cue = np.asarray(e.cue_neurons)
        act = np.asarray(e.action_neurons)
        one = _reachable(mask, cue)
        two = np.setdiff1d(_reachable(mask, one), np.concatenate([cue, one]))
        doc = load(spec["run"])
        if not doc:
            return {**out, "ok": False, "reason": f"world {name}: the artifact is absent"}
        got = one_budget(doc, spec["theta"], ctx, arm=arm, reps=reps)
        if not got.get("ok"):
            return {**out, "ok": False, "reason": f"world {name}: {got['reason']}"}
        cell = got["cell"]
        initial = statistics.fmean(cell[("initial", 0)])
        body = statistics.fmean(cell[("after_task_0", 0)])
        props["fan_out"][name] = int(one.size)
        props["two_hop_frontier"][name] = int(two.size)
        props["action_overlap"][name] = int(np.intersect1d(np.concatenate([one, two]), act).size)
        props["cue_out_degree"][name] = int(mask[:, cue].sum())
        props["path_weight"][name] = float(np.abs(w[np.ix_(act, one)]).sum())
        gains[name] = body - initial
        out["worlds"][name] = {"cueseed": spec["cueseed"], "artifact": spec["run"].name,
                               "cue_to_action": distance(mask, cue, act),
                               "initial_task_0": initial, "body_task_0": body, "gain": gains[name]}
    order = sorted(gains, key=lambda n: gains[n])
    out["order"] = order
    for p in PROPERTIES:
        values = [props[p][n] for n in order]
        out["properties"][p] = {
            "values": {n: props[p][n] for n in order},
            "rank_correlation_with_the_gain": _spearman(values, [gains[n] for n in order]),
            "strictly_orders": strictly_orders(values),
            "card_inside_the_losers": (min(props[p][n] for n in order if n != "card")
                                       <= props[p]["card"]
                                       <= max(props[p][n] for n in order if n != "card")),
        }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the corpus or a run is absent"}
                for c in CLAIMS]
    dists = {n: w["cue_to_action"] for n, w in r["worlds"].items()}
    j1 = {"id": "X1", "measured": f"the five worlds' cue-to-action distances are {dists}, taking "
                                  f"{len(set(dists.values()))} value(s)",
          "verdict": "MET -- the distance assigns the card's world and the three failing two-hop draws the same "
                     "value and cannot order them" if len(set(dists.values())) < len(dists) else
          f"FALSIFIER FIRED -- the distances take {len(set(dists.values()))} values and can order them"}

    perfect = {p: round(v["rank_correlation_with_the_gain"], 3) for p, v in r["properties"].items()
               if v["strictly_orders"]}
    j2 = {"id": "X2", "measured": f"over {len(r['properties'])} properties and {len(r['worlds'])} worlds the rank "
                                  f"correlations with the gain are "
                                  f"{ {p: round(v['rank_correlation_with_the_gain'], 3) for p, v in r['properties'].items()} }",
          "verdict": "MET -- no candidate orders the five, so the one is not among them" if
                     (not perfect and len(r["properties"]) >= MIN_PROPERTIES and len(r["worlds"]) >= MIN_WORLDS) else
          f"FALSIFIER FIRED -- {perfect} orders the five perfectly"}

    varying = {p: len(set(v["values"].values())) for p, v in r["properties"].items()}
    j3 = {"id": "X3", "measured": f"the properties take {varying} distinct values across the five worlds",
          "verdict": f"MET -- {len([v for v in varying.values() if v >= 2])} of them vary, so the ordering test has "
                     f"power" if len([v for v in varying.values() if v >= 2]) >= MIN_VARYING else
          f"FALSIFIER FIRED -- only {len([v for v in varying.values() if v >= 2])} vary"}

    gains = {n: w["gain"] for n, w in r["worlds"].items()}
    bad4 = {n: round(g, 4) for n, g in gains.items()
            if (g <= 0 if n == "card" else g >= -GAIN)}
    j4 = {"id": "X4", "measured": f"the five worlds' gains are { {n: round(g, 4) for n, g in gains.items()} }",
          "verdict": "MET -- the card's world gains and the other four lose by more than the bar" if not bad4 else
          f"FALSIFIER FIRED -- {bad4} is not on its side of the sign"}

    outside = {p: v["values"] for p, v in r["properties"].items() if not v["card_inside_the_losers"]}
    j5 = {"id": "X5", "measured": f"the card's world's value lies inside the four failing worlds' range on "
                                  f"{len(r['properties']) - len(outside)} of the {len(r['properties'])} properties",
          "verdict": "MET -- no candidate makes the card's world an extreme" if not outside else
          f"FALSIFIER FIRED -- {outside} puts the card's value outside the losers' range"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== five candidates for the one ==")
        print(f"   REFUSED -- {r.get('reason', 'the corpus or a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== five candidates for the one ==")
    print(f"   five properties of the cue population on `{r['circuit']}`'s mask of {r['edges']} edges, against the "
          f"five worlds' far-point gains, worst first: {r['order']}")
    print(f"\n   {'world':>7} {'cue seed':>9} {'distance':>9} {'gain':>9}  " +
          " ".join(f"{p[:14]:>14}" for p in PROPERTIES))
    for n in r["order"]:
        w = r["worlds"][n]
        print(f"   {n:>7} {str(w['cueseed']):>9} {str(w['cue_to_action']):>9} {w['gain']:9.4f}  " +
              " ".join(f"{r['properties'][p]['values'][n]:>14.4g}" for p in PROPERTIES))

    print("\n== the registered claims, X1-X5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e399` found the distance did not decide and named no property in its place; this puts five near "
          "geometries")
    print("    against the four measured outcomes, training nothing)")
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
