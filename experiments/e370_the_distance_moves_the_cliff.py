"""E370 -- the distance moves the cliff: sixteen population draws, where the cue source's cliff stays and the
action source's does not.

`e369` measured the cue population's directed distance to the action population in the circuit's own mask, found
**2**, and registered the formula that follows: a population at distance `d` from the cue holds the trial's trace at
cue steps up to **`tau - 2 - d`**, which predicts the cue source's cliff at **10** and the action source's at **8**,
both of which `e368` had measured. It checked the formula at a second circuit size and reported a **null**: that
size drew the same distance, so the same number was predicted twice and what was checked was the arithmetic rather
than the mechanism. It named the unit it was pointing at: *"a configuration whose distance is **not 2**"*.

**This unit draws sixteen configurations and does not choose the distance.** The distance is a property of three
populations drawn from one mask, so the way to vary it is to vary the draw: eight population seeds at each of two
circuit sizes, every draw's distance measured in the mask before its curve is rolled, and both drive sources rolled
at every step of every draw. The **cue source is the control**: its distance is **0** by construction in every draw,
because the environment makes the drive population the cue population itself, so its cliff is the formula's maximum
**10** in every one of the sixteen and nothing about a draw should move it.

Four claims, registered before any distance and any curve was read.

- **Q1 -- and the sweep moves the distance.** The sixteen configurations' action distances take at least **two**
  distinct values. **Falsifier**: every configuration at one distance, in which case this unit cannot test the
  formula and says so rather than reporting sixteen confirmations of one number.
- **Q2 -- and every cliff is its own draw's distance.** For every configuration, the action source's measured last
  clearing step equals `tau - 2 - d`, and a configuration whose action population is unreachable from the cue
  predicts **no** clearing step and shows one. **Falsifier**: any configuration where measured and predicted differ.
- **Q3 -- and a shorter walk buys exactly the step it saves.** Configurations at distance **1** clear at **9** and
  those at distance **2** clear at **8**, so the measured step is **strictly decreasing** in the distance. This is
  Q2's content read as a comparison rather than as sixteen equalities, and it is stated separately because a
  formula can match every configuration by accident when there are only two values to match. **Falsifier**: two
  distances sharing a measured step, or the order reversed.
- **Q4 -- and the control does not move.** The cue source's measured last clearing step is **10** in every one of
  the sixteen configurations, so what the sweep moves is the action population's own walk and not the draw.
  **Falsifier**: any configuration where the cue source's step differs from 10.

**What it can do beyond that.** It reports the count of **direct cue-to-action edges** in each draw, which is the
quantity the distance is one when it is zero and two when it is not: the sweep turns "the cue is two hops from the
action" from a fact about one draw into a distribution over draws, and that distribution is what a game built on
this world has to expect.

**What it cannot do.** *Two circuit sizes and sixteen draws*: the distances are read off one connectome's mask and
one extraction per size, so a hop count of three or more is possible in principle and is not what this sweep
produced. *And it inherits `e369`'s split*: the formula is about the trace **existing**, and the measurement is
about a least-squares probe at 512 examples **clearing chance**, so the two can agree while saying different
things -- which is why Q2 is registered as an equality of numbers rather than as a derivation. *And the cue source
is a control and not an experiment*: its distance is zero because `drive_from_cue` sets the drive population to the
cue population, so Q4 tests the instrument's stability rather than the connectome.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e322_the_benchmark_has_no_time_in_it import probe
from experiments.e369_why_the_cliff_is_where_it_is import distance, predicted_last

SIZES = (300, 600)
DRAWS = 8
READOUT_SIZE = 32
SEED = 0
TAU = 12
N_SYMBOLS = 4
N_EXAMPLES = 512
SCALE = 1.0
GAIN = 1.0
NOISE = 1.0
WORLD_LEAK = 0.35
WORLD_DIMS = 8
SOURCES = ("cue", "action")
STEPS = tuple(range(TAU))
CLEARS = 0.05
CLAIMS = (
    ("Q1", "and the sweep moves the distance",
     "The sixteen configurations' action distances take at least two distinct values",
     "falsifier: every configuration at one distance"),
    ("Q2", "and every cliff is its own draw's distance",
     "For every configuration the action source's measured last clearing step equals `tau - 2 - d`, and an "
     "unreachable action population predicts no step and shows one",
     "falsifier: any configuration where measured and predicted differ"),
    ("Q3", "and a shorter walk buys exactly the step it saves",
     "Configurations at distance 1 clear at 9 and those at distance 2 at 8, so the measured step is strictly "
     "decreasing in the distance",
     "falsifier: two distances sharing a step, or the order reversed"),
    ("Q4", "and the control does not move",
     "The cue source's measured last clearing step is 10 in every configuration",
     "falsifier: any configuration where the cue source's step differs from 10"),
)


def _env(circ, rs, source: str, seed: int):
    from clfly.network import env as fly_env
    return fly_env.build(circ, readout_subset=rs, seed=seed, n_symbols=N_SYMBOLS, tau=TAU, scale=SCALE, gain=GAIN,
                         noise=NOISE, world_modes=0, world_leak=WORLD_LEAK, world_dims=WORLD_DIMS,
                         world_coupled=True, cue_at=0, drive_from_cue=(source == "cue"))


def _roll(model, e, y: np.ndarray) -> np.ndarray:
    import torch
    fn = e.feedback()
    with torch.no_grad():
        model(torch.from_numpy(np.asarray(e.cue_input(y), dtype=np.float32)), feedback=fn)
    return fn.last_world.detach().numpy()


def _curve(model, e, y_tr, y_te) -> dict:
    """One env and one body over every cue step: the world's final state is a function of `cue_at` alone."""
    acc = {}
    for step in STEPS:
        e.cue_at = int(step)
        world = _roll(model, e, np.concatenate([y_tr, y_te]))
        acc[step] = float(probe(world[:, None, :][:len(y_tr)], y_tr, world[:, None, :][len(y_tr):], y_te,
                                list(range(WORLD_DIMS)))[-1])
    return acc


def last_clearing(acc: dict, chance: float = 1.0 / N_SYMBOLS, clears: float = CLEARS):
    good = [s for s in STEPS if acc.get(s, 0.0) >= chance + clears]
    return max(good) if good else None


def reading(sizes=SIZES, draws: int = DRAWS, seed: int = SEED) -> dict:
    from clfly.connectome import annotate, circuits, graph
    from clfly.connectome.graph import WEIGHT_SCALE
    from clfly.network.model import RateConfig, build_net

    conn, ann = graph.build(), annotate.load_annotations()
    y = np.random.default_rng(seed + 7).integers(0, N_SYMBOLS, size=N_EXAMPLES)
    y_tr, y_te = y[:N_EXAMPLES // 2], y[N_EXAMPLES // 2:]

    rows = {}
    for size in sizes:
        circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
        rs = np.sort(np.random.default_rng(seed).choice(circ.n_neurons, size=READOUT_SIZE, replace=False))
        mask = np.asarray((circ.net.weights(WEIGHT_SCALE) != 0).todense(), dtype=bool)
        model = build_net(circ, RateConfig(tau=TAU)).torch_model()
        for draw in range(draws):
            entry = {"circuit": circ.name, "size": circ.n_neurons, "draw_seed": int(draw), "sources": {}}
            for source in SOURCES:
                e = _env(circ, rs, source, draw)
                cue, drive = np.asarray(e.cue_neurons), np.asarray(e.action_neurons)
                d = distance(mask, cue, drive)
                acc = _curve(model, e, y_tr, y_te)
                entry["sources"][source] = {
                    "distance": d, "predicted_last": predicted_last(d), "accuracy": acc,
                    "last_clearing": last_clearing(acc),
                    #: the count of direct edges from the cue population into the drive population: one when the
                    #: distance is one, zero when the walk has to go through a third population
                    "direct_edges": int(mask[np.ix_(drive, cue)].sum())}
            rows[f"{size}:{draw}"] = entry

    out = {"circuit": rows[f"{sizes[0]}:0"]["circuit"], "sizes": [int(s) for s in sizes], "draws": int(draws),
           "readout": READOUT_SIZE, "seed": seed, "tau": TAU, "n_symbols": N_SYMBOLS, "n_examples": N_EXAMPLES,
           "chance": 1.0 / N_SYMBOLS, "steps": list(STEPS), "clears": CLEARS,
           "world_dims": WORLD_DIMS, "world_leak": WORLD_LEAK, "rows": rows}
    return out


def judge(r: dict) -> list[dict]:
    rows = r.get("rows") or {}
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no configuration was drawn"} for c in CLAIMS]

    def _d(entry):
        return (entry.get("sources") or {}).get("action", {}).get("distance")

    def _m(entry, source="action"):
        return (entry.get("sources") or {}).get(source, {}).get("last_clearing")

    ds = {k: _d(v) for k, v in rows.items()}
    distinct = sorted({d for d in ds.values() if d is not None})
    unreachable = [k for k, d in ds.items() if d is None]
    j1 = {"id": "Q1", "measured": f"the action source's distance across the {len(rows)} configurations is "
                                  f"{sorted(ds.values(), key=lambda d: (d is None, d))}, taking the distinct values "
                                  f"{distinct} with {len(unreachable)} unreachable",
          "verdict": "MET -- the sweep moves the distance" if len(distinct) + (1 if unreachable else 0) >= 2 else
          f"FALSIFIER FIRED -- every configuration is at distance {distinct}, so this unit cannot test the formula "
          f"and reports that it does not"}

    bad = {k: (_m(v), v["sources"]["action"]["predicted_last"]) for k, v in rows.items()
           if _m(v) != v["sources"]["action"]["predicted_last"]}
    j2 = {"id": "Q2", "measured": f"measured against predicted over the {len(rows)} configurations: "
                                  f"{ {k: [_m(v), v['sources']['action']['predicted_last']] for k, v in list(rows.items())[:4]} } "
                                  f"(first four), with {len(bad)} differing",
          "verdict": "MET -- every cliff is its own draw's distance" if not bad else
          f"FALSIFIER FIRED -- measured against predicted differs in {bad}"}

    by_d = {}
    for k, v in rows.items():
        by_d.setdefault(v["sources"]["action"]["distance"], set()).add(_m(v))
    steps = {d: sorted(s) for d, s in by_d.items() if d is not None}
    ordered = sorted(steps)
    dec = all(len(steps[d]) == 1 for d in ordered) and all(
        steps[ordered[i + 1]][0] < steps[ordered[i]][0] for i in range(len(ordered) - 1))
    j3 = {"id": "Q3", "measured": f"the measured step by distance is { {d: steps[d] for d in ordered} }, over "
                                  f"{ {d: sum(1 for v in rows.values() if v['sources']['action']['distance'] == d) for d in ordered} } "
                                  f"configurations each",
          "verdict": "MET -- a shorter walk buys exactly the step it saves" if dec and len(ordered) >= 2 else
          f"FALSIFIER FIRED -- steps { {d: steps[d] for d in ordered} }: two distances share a step or the order "
          f"is reversed"}

    cue = {k: _m(v, "cue") for k, v in rows.items()}
    moved = {k: v for k, v in cue.items() if v != predicted_last(0)}
    j4 = {"id": "Q4", "measured": f"the cue source's last clearing step across the {len(rows)} configurations is "
                                  f"{sorted(set(cue.values()), key=lambda x: (x is None, x))} against the "
                                  f"formula's {predicted_last(0)} for a distance of zero",
          "verdict": "MET -- the control does not move" if not moved else
          f"FALSIFIER FIRED -- the cue source's step is not {predicted_last(0)} in {moved}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    if not r.get("rows"):
        print("== the distance moves the cliff ==\n   REFUSED -- no configuration was drawn")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the distance moves the cliff ==")
    print(f"   `tau` {r['tau']}, so `tau - 2 - d` is the last cue step a population at distance `d` can hold the "
          f"trace; {len(r['rows'])} configurations over the sizes {r['sizes']}")
    print(f"\n   {'config':>10} {'circuit':>16} {'source':>7} {'distance':>9} {'direct':>7} {'predicts':>9} "
          f"{'clears to':>10}")
    for key, entry in r["rows"].items():
        for source in SOURCES:
            s = entry["sources"][source]
            print(f"   {key:>10} {entry['circuit']:>16} {source:>7} {str(s['distance']):>9} {s['direct_edges']:>7} "
                  f"{str(s['predicted_last']):>9} {str(s['last_clearing']):>10}")
    dist = {}
    for entry in r["rows"].values():
        dist.setdefault(entry["sources"]["action"]["distance"], []).append(
            (entry["sources"]["action"]["direct_edges"], entry["sources"]["action"]["last_clearing"]))
    print(f"\n   by distance: " + "; ".join(
        f"d={d} over {len(v)} draws, direct edges {sorted({x[0] for x in v})}, clears to "
        f"{sorted({x[1] for x in v}, key=lambda x: (x is None, x))}" for d, v in sorted(dist.items(),
                                                                                      key=lambda kv: (kv[0] is None, kv[0]))))

    print("\n== the registered claims, Q1-Q4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e369` found the distance is what puts the cliff where it is and could only check it at one "
          "distance; this draws sixteen and lets the distance fall where it falls)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sizes", type=int, nargs="+", default=list(SIZES))
    ap.add_argument("--draws", type=int, default=DRAWS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(sizes=tuple(args.sizes), draws=args.draws)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
