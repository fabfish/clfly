"""E186 -- this project has two task lines, and they do not name the same five assemblies.

`clfly/connectome/tasks.py`'s `TASK_ASSEMBLIES` is the **analytic** line's five assemblies -- odour identity, odour
valence, heading, odour input, innate odour -- and `clfly/network/tasks.py`'s `SUITE_SPECS` is the **network**
line's three tasks. `e185` found the network suite covers three of the analytic line's five; this checks the
comparison value by value, which is where the small defects are, and it measures the one thing the network line's
read-out choice actually does.

**Three differences, each of a different size and only one of them a mistake:**

1. **Two assemblies the network suite does not have at all** -- `odour_valence` and `innate_odour`, whose
   populations are already in the circuit (measured below). This is the extension `e185` registered as being a
   spec away rather than a circuit away.
2. **One value the network spec drops**: `odour_input` is `("ALPN", "ALLN")` in the network and
   `("ALPN", "ALLN", "ALIN")` in the analytic line. `ALIN` is 24 neurons whole-brain and 10 in the circuit, so the
   two lines' odour-input assemblies are not the same population.
3. **One value that names nothing, in either column of either line**: the analytic `heading` assembly ends with
   `"NO"`, and the annotation has **no** `NO` -- it has `Nod1`, `Nod2`, `Nod3`, `Nod5` (10 neurons whole brain).
   `startswith` is case-sensitive, so `"NO"` matches zero. **The defect is inert and this is checkable rather than
   argued**: the assemblies are resolved against a *circuit* (`assembly_support(circ, asm, ...)`), and the noduli
   are **0 in the mb+cx+al circuit under either spelling**, so no artifact's support changes when the spelling is
   fixed. The same inertness holds in `CX_SEEDS`, which also lists `NO`.

**And the read-out census, which is why the input/read-out overlap matters less than it looks.** A network task's
read-out is the spec's population only when the suite is built with per-task heads. With `--shared-head`, the
read-out is one shared decoder over either the whole state or a random draw, so the tasks differ **only in where
the stimulus enters**. Read from every artifact's `config` that carries `shared_head`:

- **117 runs** read out through a shared **draw** (`--readout-size` nonzero), 11 through the **whole state**, and
  **17 with per-task heads** -- the only runs in which the spec populations are the read-outs. The `heading` spec's
  read-out is `cell_class = CX`, which **contains its own input population** (the input is 55 neurons of
  `EPG`/`PFN`/`PEN`/`ER`/`PB` and all 55 are inside `CX`): in those 17 runs the stimulus is injected into the
  decoder's own inputs, by construction.

    python -m experiments.e186_task_lines_compared                    # value-level and corpus checks, seconds
    python -m experiments.e186_task_lines_compared --circuit          # plus the circuit census and reachability
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
from pathlib import Path

RUNS = Path("runs")


def annotation_values(frame, column: str) -> set[str]:
    return {str(v) for v in frame[column]}


def value_census(assemblies, frame, columns=("cell_type", "cell_class")) -> list[dict]:
    """Every assembly value, whether it names neurons, and the value it most likely meant.

    A value that matches nowhere **in any column** is not a naming difference between two lines: it is a value that
    cannot select a neuron at all, whichever line asks for it. The `near_miss` field is the measurement that turns
    the flag into an edit -- the annotation's own value whose first two letters agree with the value's, case aside,
    which is what finds `Nod1` behind a misspelled `NO`.
    """
    out = []
    for asm in assemblies:
        for value in asm.values:
            counts, near = {}, []
            for col in columns:
                if col not in frame.columns:
                    continue
                labels = [str(v) for v in frame[col]]
                counts[col] = sum(1 for v in labels if v.startswith(value))
                if counts[col] == 0 and len(value) >= 2:
                    near += sorted({v for v in labels if v.lower().startswith(value[:2].lower())})[:4]
            out.append({"assembly": asm.name, "asked_in": asm.column, "value": value, "counts": counts,
                        "matches_nowhere": sum(counts.values()) == 0, "near_miss": near})
    return out


def line_differences(specs, assemblies) -> dict:
    """Which assemblies the network suite lacks, and which of their values it drops.

    The two lines name populations, and a *value* difference inside a shared assembly name is the quiet kind: the
    analytic `odour_input` includes `ALIN` and the network `odour_input` does not, so two results that both say
    "odour input" are about different populations.
    """
    spec_by_name = {s[0]: s for s in specs}
    missing, dropped = [], []
    for asm in assemblies:
        spec = spec_by_name.get(asm.name)
        if spec is None:
            missing.append(asm.name)
            continue
        _, (col, values), _ = spec
        if col != asm.column:
            dropped.append({"assembly": asm.name, "why": "column differs", "analytic": asm.column,
                            "network": col, "values": list(asm.values)})
            continue
        left = [v for v in asm.values if v not in values]
        if left:
            dropped.append({"assembly": asm.name, "why": "values the network spec omits",
                            "analytic": list(asm.values), "network": list(values), "values": left})
    return {"assemblies_missing_from_the_network_suite": missing, "value_differences": dropped}


def readout_modes(runs_dir: Path = RUNS) -> dict:
    """Which read-out the corpus actually trained: a shared draw, the whole state, or per-task heads.

    This is the difference between "the tasks differ in where the stimulus enters" and "the tasks differ in their
    read-out population too", and it is a property of the *runs*, not of the specs.
    """
    c: collections.Counter = collections.Counter()
    for p in glob.glob(str(runs_dir / "*.json")):
        try:
            cfg = (json.loads(Path(p).read_text(encoding="utf-8")) or {}).get("config") or {}
        except (json.JSONDecodeError, OSError):
            continue
        if "shared_head" not in cfg:
            continue
        if not cfg.get("shared_head"):
            c["per-task heads (the spec populations ARE the read-outs)"] += 1
        elif cfg.get("readout_size"):
            c["one shared draw of --readout-size neurons"] += 1
        else:
            c["the whole state, one shared head"] += 1
    return dict(c)


def circuit_census(circ, specs, assemblies, columns=("cell_type", "cell_class")) -> dict:
    """The populations in the circuit: sizes, input/read-out overlaps, and what each assembly can reach."""
    import numpy as np

    def pop(col, values):
        names = circ.neuron_names(col)
        return np.array([i for i, n in enumerate(names) if any(str(n).startswith(v) for v in values)])

    assemblies_out = {a.name: pop(a.column, a.values) for a in assemblies}
    specs_out = []
    for name, inspec, outspec in specs:
        i_in, i_out = pop(*inspec), pop(*outspec)
        specs_out.append({"name": name, "n_in": len(i_in), "n_out": len(i_out),
                          "overlap": int(len(np.intersect1d(i_in, i_out)))})
    W = (circ.net.weights() > 0).astype(np.int64)
    W2 = (W @ W > 0).astype(np.int64)

    def reach(a, b, M):
        if len(a) == 0 or len(b) == 0:
            return 0
        sub = M[np.ix_(a, b)]
        sub = sub.todense() if hasattr(sub, "todense") else sub
        return int((np.asarray(sub) > 0).any(axis=0).sum())

    names = list(assemblies_out)
    return {"circuit": circ.name, "assemblies": {k: int(len(v)) for k, v in assemblies_out.items()},
            "specs": specs_out,
            "reachable_within_two_hops": {"from_" + a: {"to_" + b: reach(assemblies_out[a], assemblies_out[b], W2)
                                                        for b in names} for a in names},
            "reachable_in_one_hop": {"from_" + a: {"to_" + b: reach(assemblies_out[a], assemblies_out[b], W)
                                                   for b in names} for a in names}}


def audit(runs_dir: Path = RUNS, with_circuit: bool = False, circuit_size: int = 800) -> dict:
    from clfly.connectome.tasks import TASK_ASSEMBLIES
    from clfly.network.tasks import SUITE_SPECS
    from clfly.connectome import annotate
    ann = annotate.load_annotations()
    values = value_census(TASK_ASSEMBLIES, ann.frame)
    res = {"value_census": values, "values_matching_nowhere": [v for v in values if v["matches_nowhere"]],
           "lines": line_differences(SUITE_SPECS, TASK_ASSEMBLIES),
           "readout_modes": readout_modes(runs_dir),
           "n_analytic_assemblies": len(TASK_ASSEMBLIES), "n_network_specs": len(SUITE_SPECS)}
    if with_circuit:
        from clfly.connectome import circuits, graph
        conn = graph.build()
        circ = circuits.extract(conn, ann, hops=0, max_neurons=circuit_size)
        res["circuit_census"] = circuit_census(circ, SUITE_SPECS, TASK_ASSEMBLIES)
    return res


def report(res: dict) -> int:
    lines = res["lines"]
    print(f"   the analytic line   : {res['n_analytic_assemblies']} assemblies "
          f"(clfly/connectome/tasks.py's TASK_ASSEMBLIES)")
    print(f"   the network line    : {res['n_network_specs']} tasks (clfly/network/tasks.py's SUITE_SPECS)")
    print(f"   assemblies the network suite does not have : "
          f"{', '.join(lines['assemblies_missing_from_the_network_suite'])}")
    for d in lines["value_differences"]:
        print(f"   the same name, different population : {d['assembly']} -- {d['why']}: "
              f"analytic {d['analytic']} against network {d['network']}")
    print(f"   values that match NOTHING in any column of the annotation: "
          f"{len(res['values_matching_nowhere'])}")
    for v in res["values_matching_nowhere"]:
        print(f"        {v['assembly']}.{v['value']} asked in {v['asked_in']}, counts {v['counts']}"
              f"   likely meant: {', '.join(v['near_miss']) or '(nothing close)'}")
    print(f"   the registered extension, printed and NOT counted as a defect: the network suite lacks "
          f"{len(lines['assemblies_missing_from_the_network_suite'])} of the analytic line's assemblies "
          f"({', '.join(lines['assemblies_missing_from_the_network_suite'])})")
    print("   how the corpus actually read the tasks out (runs carrying `shared_head`):")
    for k, n in sorted(res["readout_modes"].items(), key=lambda kv: -kv[1]):
        print(f"        {n:4}  {k}")
    c = res.get("circuit_census")
    if c:
        print(f"   == {c['circuit']} ==")
        print(f"        assemblies: " + ", ".join(f"{k} {v}" for k, v in c["assemblies"].items()))
        for s in c["specs"]:
            print(f"        spec {s['name']:15} in {s['n_in']:4}  out {s['n_out']:4}  "
                  f"NEURONS IN BOTH (the read-out contains its own input): {s['overlap']}")
        print("        reached within two hops, from row's assembly to column's:")
        names = [k[5:] for k in c["reachable_within_two_hops"]]
        print("            " + "".join(f"{n[:9]:>11}" for n in names))
        for k, row in c["reachable_within_two_hops"].items():
            print(f"        {k[5:][:11]:12}" + "".join(f"{v:11}" for v in row.values()))
    # the exit code asks about DEFECTS and not about the registered extension: a value that names nothing is
    # a value that cannot select a neuron, while an assembly the network suite lacks is the extension e185
    # registered and this audit measures. Counting the second would make the check red until the benchmark is
    # extended, which is a fact about the plan rather than about the code.
    return len(res["values_matching_nowhere"])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--runs", type=Path, default=RUNS)
    p.add_argument("--circuit", action="store_true", help="also resolve the populations (loads the connectome)")
    p.add_argument("--circuit-size", type=int, default=800)
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    res = audit(args.runs, with_circuit=args.circuit, circuit_size=args.circuit_size)
    n = report(res)
    if args.json_out:
        from clfly.bench.artifacts import write_json
        write_json(args.json_out, res)
        print(f"wrote {args.json_out}")
    return 0 if n == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
