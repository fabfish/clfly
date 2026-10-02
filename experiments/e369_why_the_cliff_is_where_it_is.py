"""E369 -- why the cliff is where it is: the cue population's distance to the population the world reads.

`e368` swept `e363`'s instrument over every cue step and both drive sources and found two cliffs one step apart:
the world listening to the **cue population** still reads the symbol with the cue at step **10**, and the world
listening to the agent's own **action population** stops at step **8**. It named what it could not do -- *"the cliff
is measured, not explained"* -- and pointed here: the shape is what a shortest path from the cue population to the
action population would produce.

**This unit measures that path in the circuit's own mask and registers the formula it implies.** With the cue
written into `u` at step `s`, the state entering step `t` is `x_t`, and a perturbation of `x` spreads one hop per
step: `x_{s+1}` is nonzero on the neurons the cue is written on, `x_{s+1+d}` on those at distance `d`. The world's
last readable state is `x_{tau - 1}`, so a source whose drive population sits at distance `d` from the cue can hold
the trial's trace only while `s + 1 + d <= tau - 1`, i.e. **at cue steps up to `tau - 2 - d`**. With `tau = 12` and
`d = 0` for the cue population -- the world listens to the neurons the cue is written on -- that is **10**, and for
the action population it is `10 - d`.

**And the distance is measured on two circuits, not one**, because a formula checked at the size it was invented at
is checked by coincidence: a second circuit size redraws the three populations from a different pool, and the
prediction moves with the measured distance or it does not.

Four claims, registered before any distance or any curve was read.

- **P1 -- and the cue is two hops from the action.** The directed distance from the cue population to the action
  population in the circuit's own mask is exactly **2** at the configuration `e363` and `e368` share. **Falsifier**:
  **1**, which would say a direct edge exists and the step-9 cliff needs another cause, or **3 or more**, which would
  put the cliff earlier than either unit measured.
- **P2 -- and the cliff follows from the distance.** For each source, the last cue step at which the population the
  world reads can hold the trace of the cue is `tau - 2 - d`, and the **measured** last clearing step of `e368`'s
  instrument equals it at both sources: **10** for the cue source and **8** for the action source. **Falsifier**:
  either measured step differing from the prediction.
- **P3 -- and it is the distance and not the draw.** At a second circuit size the populations are drawn afresh and
  the distance is what it is there; the measured last clearing step equals `tau - 2 - d` at **both** sources at that
  size too. **Falsifier**: either source's measured step differing from its prediction at the second size, or the
  second size reaching no step at all in a way the formula did not predict. **Null**: the second size's distances
  equal the first's, in which case the prediction is the same number twice and P3 is a check on the arithmetic
  rather than on the mechanism.
- **P4 -- and the world is not the limit.** Both of the world's own maps are **fully dense**: every entry of
  `world_drive` and of `world_read` is nonzero, so the world sees the whole drive population and answers through the
  whole feedback population, and the cliff cannot come from a sparse world map. **Falsifier**: any zero entry in
  either map, which would put a second candidate cause in the reading.

**What it can do beyond that.** The formula is the deliverable: it turns "how long the channel takes to fill" into a
number a game can compute from a circuit before rolling anything -- the shortest path from the population a cue is
written on to the population a read-out listens to, subtracted from `tau - 2`.

**What it cannot do.** *One hop count on one connectome's mask*: the distance is the circuit's, so a third circuit
size, a different seed and a different circuit extraction are not measured, and two sizes check the formula rather
than establish it for all of them. *And the formula is about the trace existing, not about a probe clearing chance*:
a population at distance `d` holds the cue's trace at exactly the steps the formula says, and whether that trace is
strong enough for a linear probe at 512 examples is a second question, which is why P2 and P3 compare the formula
with `e368`'s measured clearing steps rather than deriving them. *And the populations are disjoint by construction*:
`d = 0` for the cue source is the environment's design and not a fact about the connectome.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e322_the_benchmark_has_no_time_in_it import probe

SIZE = 300
SIZE_2 = 600
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
MAX_HOPS = 8
REFERENCE = Path("runs/e368_how_long_the_channel_takes_to_fill.json")
CLAIMS = (
    ("P1", "and the cue is two hops from the action",
     "The directed distance from the cue population to the action population in the circuit's own mask is exactly 2 "
     "at the shared configuration",
     "falsifier: 1, or 3 or more"),
    ("P2", "and the cliff follows from the distance",
     "For each source the last cue step that can hold the trace is `tau - 2 - d`, and the measured last clearing "
     "step equals it: 10 for the cue source and 8 for the action source",
     "falsifier: either measured step differing from the prediction"),
    ("P3", "and it is the distance and not the draw",
     "At a second circuit size the measured last clearing step equals `tau - 2 - d` for both sources",
     "falsifier: either source differing from its prediction; null: the distances unchanged from the first size"),
    ("P4", "and the world is not the limit",
     "Every entry of `world_drive` and of `world_read` is nonzero",
     "falsifier: any zero entry in either map"),
)


def _env(circ, rs, source: str, cue_at: int, seed: int = SEED):
    from clfly.network import env as fly_env
    return fly_env.build(circ, readout_subset=rs, seed=seed, n_symbols=N_SYMBOLS, tau=TAU, scale=SCALE, gain=GAIN,
                         noise=NOISE, world_modes=0, world_leak=WORLD_LEAK, world_dims=WORLD_DIMS,
                         world_coupled=True, cue_at=int(cue_at), drive_from_cue=(source == "cue"))


def _reachable(mask: np.ndarray, frontier: np.ndarray) -> np.ndarray:
    """One hop: the neurons a nonzero state on `frontier` writes to on the next step.

    The model's step is `x @ W.T`, so `W[i, j]` carries `j` into `i` and the targets of a set are the nonzero rows
    of its columns.
    """
    return np.flatnonzero(mask[:, frontier].any(axis=1))


def distance(mask: np.ndarray, sources, targets, max_hops: int = MAX_HOPS):
    """The shortest directed path from any source neuron to any target neuron, or None past `max_hops`."""
    src, tgt = np.asarray(sources), np.asarray(targets)
    if np.intersect1d(src, tgt).size:
        return 0
    seen = np.zeros(mask.shape[0], dtype=bool)
    seen[src] = True
    frontier = src
    for d in range(1, max_hops + 1):
        nxt = _reachable(mask, frontier)
        nxt = nxt[~seen[nxt]]
        if nxt.size == 0:
            return None
        if np.intersect1d(nxt, tgt).size:
            return d
        seen[nxt] = True
        frontier = nxt
    return None


def _roll(model, e, y: np.ndarray) -> np.ndarray:
    import torch
    fn = e.feedback()
    with torch.no_grad():
        model(torch.from_numpy(np.asarray(e.cue_input(y), dtype=np.float32)), feedback=fn)
    return fn.last_world.detach().numpy()


def _accuracy(model, circ, rs, source: str, cue_at: int, y_tr, y_te) -> float:
    e = _env(circ, rs, source, cue_at)
    world = _roll(model, e, np.concatenate([y_tr, y_te]))
    return float(probe(world[:, None, :][:len(y_tr)], y_tr, world[:, None, :][len(y_tr):], y_te,
                       list(range(WORLD_DIMS)))[-1])


def predicted_last(d: int | None, tau: int = TAU):
    """The last cue step a population at distance `d` can hold the trace, or None when it is unreachable."""
    return None if d is None else (tau - 2 - d)


def reading(sizes=(SIZE, SIZE_2), reference: Path = REFERENCE) -> dict:
    from clfly.connectome import annotate, circuits, graph
    from clfly.connectome.graph import WEIGHT_SCALE
    from clfly.network.model import RateConfig, build_net

    conn, ann = graph.build(), annotate.load_annotations()
    rng = np.random.default_rng(SEED + 7)
    y = rng.integers(0, N_SYMBOLS, size=N_EXAMPLES)
    y_tr, y_te = y[:N_EXAMPLES // 2], y[N_EXAMPLES // 2:]

    rows, maps = {}, {}
    for size in sizes:
        circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
        rs = np.sort(np.random.default_rng(SEED).choice(circ.n_neurons, size=READOUT_SIZE, replace=False))
        mask = np.asarray((circ.net.weights(WEIGHT_SCALE) != 0).todense(), dtype=bool)
        model = build_net(circ, RateConfig(tau=TAU)).torch_model()
        entry = {"circuit": circ.name, "size": circ.n_neurons, "sources": {}}
        for source in SOURCES:
            e = _env(circ, rs, source, 0)
            pop = e.cue_neurons if source == "cue" else e.action_neurons
            d = distance(mask, np.asarray(e.cue_neurons), np.asarray(pop))
            acc = {step: _accuracy(model, circ, rs, source, step, y_tr, y_te) for step in STEPS}
            good = [s for s in STEPS if acc[s] >= 1.0 / N_SYMBOLS + CLEARS]
            entry["sources"][source] = {
                "drive_population": int(len(pop)), "distance": d, "predicted_last": predicted_last(d),
                "accuracy": acc, "last_clearing": max(good) if good else None}
            maps[f"{size}:{source}"] = {"world_drive_size": int(e.world_drive.size) if e.world_drive is not None else 0,
                                        "world_drive_nonzero": int(np.count_nonzero(e.world_drive))
                                        if e.world_drive is not None else 0,
                                        "world_read_size": int(e.world_read.size) if e.world_read is not None else 0,
                                        "world_read_nonzero": int(np.count_nonzero(e.world_read))
                                        if e.world_read is not None else 0}
        entry["n_edges"] = int(mask.sum())
        rows[str(size)] = entry

    out = {"circuit": rows[str(sizes[0])]["circuit"], "sizes": [int(s) for s in sizes], "readout": READOUT_SIZE,
           "seed": SEED, "tau": TAU, "n_symbols": N_SYMBOLS, "n_examples": N_EXAMPLES, "chance": 1.0 / N_SYMBOLS,
           "steps": list(STEPS), "clears": CLEARS, "world_dims": WORLD_DIMS, "world_leak": WORLD_LEAK,
           "rows": rows, "maps": maps, "reference": None}
    import json
    if Path(reference).is_file():
        try:
            doc = json.loads(Path(reference).read_text(encoding="utf-8"))
            prev = doc.get("last_clearing") if isinstance(doc.get("last_clearing"), dict) else None
            out["reference"] = {"artifact": Path(reference).name,
                                "last_clearing": {s: (prev or {}).get(s) for s in SOURCES}}
        except (OSError, ValueError):
            out["reference"] = None
    return out


def judge(r: dict) -> list[dict]:
    rows = r.get("rows") or {}
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no circuit was walked"} for c in CLAIMS]
    first = rows[str((r.get("sizes") or [SIZE])[0])]
    act = (first.get("sources") or {}).get("action") or {}
    d = act.get("distance")

    j1 = {"id": "P1", "measured": f"on `{first.get('circuit')}` ({first.get('size')} neurons, "
                                  f"{first.get('n_edges')} edges) the cue population's distance to the action "
                                  f"population is {d}",
          "verdict": "MET -- the cue is two hops from the action" if d == 2 else
          f"FALSIFIER FIRED -- the distance is {d}: a direct edge would leave the step-9 cliff unexplained and "
          f"three or more hops would put the cliff earlier than either unit measured"}

    def _pair(entry):
        return {s: ((entry.get("sources") or {}).get(s) or {}).get("last_clearing") for s in SOURCES}

    def _pred(entry):
        return {s: ((entry.get("sources") or {}).get(s) or {}).get("predicted_last") for s in SOURCES}

    meas, pred = _pair(first), _pred(first)
    ref = (r.get("reference") or {}).get("last_clearing") if isinstance(r.get("reference"), dict) else None
    ok2 = all(meas[s] is not None and meas[s] == pred[s] for s in SOURCES)
    j2 = {"id": "P2", "measured": f"the distances are { {s: ((first['sources'].get(s)) or {}).get('distance') for s in SOURCES} }, so "
                                  f"`tau - 2 - d` predicts {pred} and the curve reads {meas}"
                                  + (f", against `{(r.get('reference') or {}).get('artifact')}`'s {ref}" if ref else
                                     ", with no previous reading on disk to compare against"),
          "verdict": "MET -- both measured steps are the distances' own" if ok2 else
          f"FALSIFIER FIRED -- predicted {pred}, measured {meas}"}

    sizes = [str(s) for s in (r.get("sizes") or [])]
    if len(sizes) < 2:
        j3 = {"id": "P3", "measured": "a second circuit size was not walked",
              "verdict": "REFUSED -- one size is not a check on a formula"}
    else:
        sec = rows[sizes[1]]
        m2, p2 = _pair(sec), _pred(sec)
        d1 = {s: (first["sources"].get(s) or {}).get("distance") for s in SOURCES}
        d2 = {s: (sec["sources"].get(s) or {}).get("distance") for s in SOURCES}
        same = d1 == d2
        ok3 = all(m2[s] is not None and m2[s] == p2[s] for s in SOURCES)
        j3 = {"id": "P3", "measured": f"at `{sec.get('circuit')}` ({sec.get('size')} neurons, {sec.get('n_edges')} "
                                      f"edges) the distances are {d2} against the first size's {d1}, so the formula "
                                      f"predicts {p2} and the curve reads {m2}",
              "verdict": ("MET -- the prediction moved with the distance and held" if ok3 and not same else
                          "NULL -- the second size's distances are the first's, so the same number was predicted "
                          "twice" if ok3 else
                          f"FALSIFIER FIRED -- predicted {p2}, measured {m2}")}

    maps = r.get("maps") or {}
    zero = {k: v for k, v in maps.items() if v.get("world_drive_nonzero") != v.get("world_drive_size")
            or v.get("world_read_nonzero") != v.get("world_read_size")}
    j4 = {"id": "P4", "measured": f"across {len(maps)} maps, `world_drive` and `world_read` carry "
                                  f"{sorted({(v['world_drive_nonzero'], v['world_drive_size']) for v in maps.values()})} "
                                  f"and {sorted({(v['world_read_nonzero'], v['world_read_size']) for v in maps.values()})} "
                                  f"nonzero over size",
          "verdict": "MET -- both maps are dense, so the world is not the limit" if not zero else
          f"FALSIFIER FIRED -- {zero} carries a zero entry"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    if not r.get("rows"):
        print("== why the cliff is where it is ==\n   REFUSED -- no circuit was walked")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== why the cliff is where it is ==")
    print(f"   `tau` {r['tau']}: a population at distance `d` from the cue holds the trace at cue steps up to "
          f"`tau - 2 - d`")
    for size, entry in r["rows"].items():
        print(f"\n   {entry['circuit']} ({entry['size']} neurons, {entry['n_edges']} edges)")
        print(f"   {'source':>8} {'drive pop':>10} {'distance':>9} {'predicts':>9} {'clears to':>10}")
        for source in SOURCES:
            s = entry["sources"][source]
            print(f"   {source:>8} {s['drive_population']:10d} {str(s['distance']):>9} "
                  f"{str(s['predicted_last']):>9} {str(s['last_clearing']):>10}")
        print(f"   {'cue at':>8} " + " ".join(f"{('cue@' + str(t)):>8}" for t in r["steps"]))
        for source in SOURCES:
            print(f"   {source:>8} " + " ".join(f"{entry['sources'][source]['accuracy'][t]:8.4f}"
                                                for t in r["steps"]))

    print("\n== the registered claims, P1-P4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e368` found the two cliffs one step apart and named the shortest path as the explanation; this")
    print("    measures the path in the mask and turns it into the formula that predicts the cliff)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sizes", type=int, nargs="+", default=[SIZE, SIZE_2])
    ap.add_argument("--reference", type=Path, default=REFERENCE)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(sizes=tuple(args.sizes), reference=args.reference)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
