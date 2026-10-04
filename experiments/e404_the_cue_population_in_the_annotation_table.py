"""E404 -- the cue population in the annotation table: do the biological groupings separate the one?

`e400` screened five **geometric** properties of the cue population and `e401` retired the one that looked like a
lead. What was left unmeasured, the two units registered together, includes *"the cue's weighted spectrum, its
overlap with the read-out draw, the action population's own tree, and anything about the trained body"* -- and the
repository's whole reason for using a connectome is that it is **annotated**. So this unit asks the biological
version of the same question, and trains nothing: five properties read off the annotation table for the six cue
populations whose far-point readings exist. Five claims, registered before any annotation was read.

- **AE1 -- and the annotations are the circuit's.** Every neuron of the circuit carries a value in each of the five
  columns read here, so the join from the circuit's own `neuron_names` to the annotation table resolves rather than
  silently dropping neurons. **Falsifier**: any column covering fewer than all of the circuit's neurons. **Bound**:
  the circuit holds at least **500** neurons and the table at least **100,000** rows.
- **AE2 -- and the card's cue population is not an extreme on any of them.** For **every** one of the five
  properties the card's cue population's value lies inside the range the five failing cue populations span.
  **Falsifier**: a property on which its value is strictly outside that range. *This is `e400`'s X5 asked of the
  biological groupings rather than of the geometry, and the direction is registered as the prior: five units have
  now screened the draw and the body, and none separated the one.*
- **AE3 -- and the properties have power.** At least **three** of the five take at least two distinct values across
  the six populations. **Falsifier**: fewer than three vary, which would make the screen a formality.
- **AE4 -- and the readings are the ones already published.** The six populations' far-point gains are the ones
  `e398` to `e401` carry: the card's world positive and the other five negative by more than **0.10**. **Falsifier**:
  any of them on the other side of its sign.
- **AE5 -- and the biological groupings do not order them either.** No property is **strictly monotone** in the six
  gains. **Falsifier**: one is, which would name the property the geometric screen did not.

The five properties: how many distinct **cell types** the cue population's twelve neurons carry; how many distinct
**cell classes**; how many **hemilineages**; how many **supertypes**; and the **largest single cell class's share**
of the twelve.

**What it can do beyond that.** It is the last cheap screen the draw offers: the annotation ladder is the
repository's own reason for asking continual-learning questions of a connectome rather than of a random graph, and
if the one world that keeps the cue is distinguished by the biology of its cue population, this is where it would
show. If it does not, the screen is empty on the geometry, the weights and the biology, and what is left is the
training itself.

**What it cannot do.** *Five properties are five of many*: the table's other columns (`flow`, `side`,
`super_class`), the weighted spectrum of the cue's block and the action population's own tree are unmeasured. *And
six populations with one positive are six populations with one positive*: a property that separates them can do so by
chance, and the direction registered here is the prior rather than a finding. *And the properties are of the cue
population alone*: the action and feedback populations and the world's three maps are held at the card's, so a
difference that needs them is outside this screen. *And a probe is not a mechanism.*
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e379_what_the_body_did import NAIVE, TAU  # noqa: F401  (the same instrument)
from experiments.e380_what_the_training_built import setup as setup_wide
from experiments.e382_when_the_world_loses_it import one_budget

REPS = 20
#: the six worlds whose far-point bodies are on disk, with the cue seed each one's draw carries
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
    "cue6": {"cueseed": 6, "run": Path("runs/e401_earned_label_cueseed6_iters500_20reps.json"),
             "theta": Path("runs/e401_theta_cue6_iters500")},
}
#: the engine's own parameters, which are what makes an environment here the one a run had
ENGINE = {"n_symbols": 12, "tau": TAU, "scale": 1.0, "gain": 1.0, "noise": 1.0, "world_modes": 0,
          "world_leak": 0.35, "world_dims": 8, "world_coupled": True, "cue_at": 0, "drive_from_cue": False}
#: the annotation columns read, and the property each one gives
COLUMNS = {"cell_type": "cell_types", "cell_class": "cell_classes", "ito_lee_hemilineage": "hemilineages",
           "supertype": "supertypes"}
PROPERTIES = ("cell_types", "cell_classes", "hemilineages", "supertypes", "largest_class_share")
GAIN = 0.10
MIN_NEURONS = 500
MIN_ROWS = 100000
MIN_VARYING = 3
CLAIMS = (
    ("AE1", f"and the annotations are the circuit's, over at least {MIN_NEURONS} neurons",
     "Every neuron of the circuit carries a value in each of the four annotation columns read here, and the table "
     "holds at least 100,000 rows",
     "falsifier: any column covering fewer than all of the circuit's neurons"),
    ("AE2", "and the card's cue population is not an extreme on any of them",
     "For every property the card's cue population's value lies inside the range the five failing cue populations "
     "span",
     "falsifier: a property on which its value is strictly outside that range"),
    ("AE3", f"and the properties have power, over at least {MIN_VARYING}",
     "At least three of the five properties take at least two distinct values across the six populations",
     "falsifier: fewer than three vary"),
    ("AE4", f"and the readings are the ones already published, by {GAIN:.2f}",
     "The card's world's gain is positive and the other five are negative by more than 0.10",
     "falsifier: any of them on the other side of its sign"),
    ("AE5", "and the biological groupings do not order them either",
     "No property is strictly monotone in the six gains",
     "falsifier: one is, which would name the property the geometric screen did not"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def strictly_orders(values: list[float]) -> bool:
    """Whether a property's values are strictly increasing or decreasing along the readings' order."""
    return all(x < y for x, y in zip(values, values[1:])) or all(x > y for x, y in zip(values, values[1:]))


def reading(worlds: dict = WORLDS, engine: dict = ENGINE, arm: str = NAIVE, reps: int = REPS) -> dict:
    from clfly.connectome import annotate
    from clfly.network import env as fly_env
    from clfly.network.model import RateConfig, build_net

    circ, rs, loop_env, tasks = setup_wide()
    ann = annotate.load_annotations()
    model = build_net(circ, RateConfig(tau=TAU)).torch_model()
    ctx = (model, loop_env, tasks, circ.n_neurons)
    labels = {c: np.asarray(circ.labels[c]) for c in COLUMNS}
    names = {c: np.asarray(circ.neuron_names(c)) for c in COLUMNS}
    out = {"ok": True, "reason": None, "circuit": circ.name, "n_neurons": int(circ.n_neurons),
           "n_rows": int(ann.n_rows), "coverage": {}, "worlds": {}, "properties": {}, "order": None}
    for c in COLUMNS:
        out["coverage"][c] = float(np.mean([bool(np.asarray(n).size) for n in names[c]])) if names[c].size else 0.0
    gains = {}
    for name, spec in worlds.items():
        e = (fly_env.build(circ, readout_subset=rs, seed=0, **engine) if spec["cueseed"] is None
             else fly_env.build(circ, readout_subset=rs, seed=0, cue_seed=spec["cueseed"], **engine))
        cue = np.asarray(e.cue_neurons)
        doc = load(spec["run"])
        if not doc:
            return {**out, "ok": False, "reason": f"world {name}: the artifact is absent"}
        got = one_budget(doc, spec["theta"], ctx, arm=arm, reps=reps)
        if not got.get("ok"):
            return {**out, "ok": False, "reason": f"world {name}: {got['reason']}"}
        cell = got["cell"]
        initial = statistics.fmean(cell[("initial", 0)])
        body = statistics.fmean(cell[("after_task_0", 0)])
        gains[name] = body - initial
        cls = labels["cell_class"][cue]
        out["worlds"][name] = {
            "cueseed": spec["cueseed"], "artifact": spec["run"].name,
            "gain": gains[name], "initial_task_0": initial, "body_task_0": body,
            "cell_types": int(len(set(labels["cell_type"][cue].tolist()))),
            "cell_classes": int(len(set(cls.tolist()))),
            "hemilineages": int(len(set(labels["ito_lee_hemilineage"][cue].tolist()))),
            "supertypes": int(len(set(labels["supertype"][cue].tolist()))),
            "largest_class_share": (Counter(cls.tolist()).most_common(1)[0][1] / len(cue) if len(cue) else 0.0),
            "class_names": sorted({str(names["cell_class"][i]) for i in cue}),
        }
    order = sorted(gains, key=lambda n: gains[n])
    out["order"] = order
    for p in PROPERTIES:
        values = [out["worlds"][n][p] for n in order]
        losers = [out["worlds"][n][p] for n in order if n != "card"]
        out["properties"][p] = {
            "values": {n: out["worlds"][n][p] for n in order},
            "card_inside_the_losers": min(losers) <= out["worlds"]["card"][p] <= max(losers),
            "strictly_orders": strictly_orders(values),
        }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the corpus or a run is absent"} for c in CLAIMS]
    short = {c: round(v, 4) for c, v in r["coverage"].items() if v < 1.0}
    j1 = {"id": "AE1", "measured": f"{r['n_neurons']} neurons on `{r['circuit']}` and {r['n_rows']} rows in the "
                                  f"annotation table, with {short} of the four columns covering fewer than all of "
                                  f"them",
          "verdict": f"MET -- the annotations are the circuit's, over {r['n_neurons']} neurons" if
                     (not short and r["n_neurons"] >= MIN_NEURONS and r["n_rows"] >= MIN_ROWS) else
          f"FALSIFIER FIRED -- {short} does not cover the circuit, or the table holds {r['n_rows']} rows"}

    outside = {p: v["values"] for p, v in r["properties"].items() if not v["card_inside_the_losers"]}
    j2 = {"id": "AE2", "measured": f"the card's cue population's value lies inside the five failing populations' range "
                                  f"on {len(r['properties']) - len(outside)} of the {len(r['properties'])} properties",
          "verdict": "MET -- the biological groupings do not make the card's cue population an extreme" if not outside
          else f"FALSIFIER FIRED -- {outside} puts its value outside the failing populations' range"}

    varying = {p: len(set(v["values"].values())) for p, v in r["properties"].items()}
    j3 = {"id": "AE3", "measured": f"the properties take {varying} distinct values across the six populations",
          "verdict": f"MET -- {len([v for v in varying.values() if v >= 2])} of them vary, so the screen has power"
          if len([v for v in varying.values() if v >= 2]) >= MIN_VARYING else
          f"FALSIFIER FIRED -- only {len([v for v in varying.values() if v >= 2])} vary"}

    gains = {n: w["gain"] for n, w in r["worlds"].items()}
    bad4 = {n: round(g, 4) for n, g in gains.items() if (g <= 0 if n == "card" else g >= -GAIN)}
    j4 = {"id": "AE4", "measured": f"the six populations' gains are { {n: round(g, 4) for n, g in gains.items()} }",
          "verdict": "MET -- the card's world gains and the other five lose by more than the bar" if not bad4 else
          f"FALSIFIER FIRED -- {bad4} is not on its side of the sign"}

    perfect = {p: v["values"] for p, v in r["properties"].items() if v["strictly_orders"]}
    j5 = {"id": "AE5", "measured": f"the properties' values in the readings' order are "
                                  f"{ {p: [v['values'][n] for n in r['order']] for p, v in r['properties'].items()} }",
          "verdict": "MET -- the biological groupings do not order the six either" if not perfect else
          f"FALSIFIER FIRED -- {perfect} is strictly monotone in the readings"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the cue population in the annotation table ==")
        print(f"   REFUSED -- {r.get('reason', 'the corpus or a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the cue population in the annotation table ==")
    print(f"   five properties of the six cue populations, read off the annotation table against "
          f"`{r['circuit']}`'s {r['n_neurons']} neurons; worst reading first")
    print(f"\n   {'world':>7} {'cue seed':>9} {'gain':>9}  " + " ".join(f"{p[:16]:>16}" for p in PROPERTIES))
    for n in r["order"]:
        w = r["worlds"][n]
        print(f"   {n:>7} {str(w['cueseed']):>9} {w['gain']:9.4f}  " +
              " ".join(f"{w[p]:>16.4g}" for p in PROPERTIES))

    print("\n== the registered claims, AE1-AE5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e400` screened five geometric properties and `e401` retired the one that looked like a lead;")
    print("    this asks the biological version of the same question, training nothing)")
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
