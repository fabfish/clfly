"""E227 -- the `real` cell's **input fingerprint**: is a difference between two artifacts in the inputs or in the method?

`e225` compared the analytic excess across the corpus and classified one pair as FLOATING -- "the same runner at two
epochs, and the arithmetic moved by less than a millionth". That reading has a hole, and this audit is the hole:

- the excess is a **difference of two larger numbers** (`ewc_mean - oracle_mean`, 0.0771 - 0.0624), so its relative
  spread is **5.2x** the relative spread of the quantities it is made of, and a difference cannot say which side moved;
- every artifact carrying a `real` block also carries `analytic.oracle_mean`, the Kalman/RTS reference line, which is
  **independent of the basis and of the method**: within one artifact it is the same float in all 17 bases (this
  audit checks that, and it is what makes it a fingerprint). Across artifacts it is therefore a fingerprint of the
  **tasks** alone.

So grouping the corpus by the fields that determine the circuit and the tasks -- `circuit_size`, `support`, `seeds`,
`seed0`, `q`, as `e225` does -- the fingerprint has to agree **to the bit**, and where the excess differs the
fingerprint says whether the inputs moved. Bits, not relative differences: a 1-ulp spread and a 5e-7 spread are two
different findings and a ratio column hides the difference.

    python -m experiments.e227_oracle_fingerprint_census                     # seconds, JSON only
    python -m experiments.e227_oracle_fingerprint_census --rebuild           # rebuild one group's oracle (~4 min)
    python -m experiments.e227_oracle_fingerprint_census --thread-sweep 1,4  # spawn itself at each thread count

The exit code is the number of groups whose fingerprint disagrees and whose disagreement the `DECLARED_DRIFT` table
does not account for.

**What `--thread-sweep` measures.** The oracle is `sum_k R_kj pinv(J_j) R_kj^T` over d = 1874 matrices, and this
environment's numpy is scipy-openblas 0.3.34 (24 threads): changing `OMP_NUM_THREADS` changes the reduction order
inside the BLAS, and this sweep prints the per-task values at each setting. It is the mechanism the declared drift
names, measured rather than asserted, and its size is what bounds what any "the analytic path is exact" claim can
mean on this machine.

**What it cannot do**: it sees only artifacts that carry a `real` block with an `analytic` block; it compares one
number per artifact, so a task change that leaves the oracle's mean unchanged is invisible; and a fingerprint that
agrees says the inputs agree, **not** that the artifacts' methods agree.
"""

from __future__ import annotations

import argparse
import glob
import json
import struct
import subprocess
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e103_reproducibility_audit import load_artifacts

RUNS = Path("runs")
KEY_FIELDS = ("circuit_size", "support", "seeds", "seed0", "q")
#: groups whose fingerprint drifts, each with what the drift is attributed to. Two kinds of entry, and the
#: difference is printed: an **attributed** drift names a measured mechanism, an **open** one names the candidate and
#: the measurement that rules the others out -- an unattributed drift must not be able to hide behind the table.
DECLARED_DRIFT: dict[str, dict] = {
    "circuit_size=1500, support=150, seeds=12, seed0=0, q=0.02": {
        "status": "attributed",
        "measured_rel": 3.11e-07,
        "why": "the pooling pair `e9_ladder_d1874` / `e79_ladder_d1874_perseed`. Rebuilt today the 12-seed oracle mean "
               "reproduces `e9`'s stored value TO THE LAST BIT, so the older run is the reproducible one and the "
               "deviation is in the newer run's arithmetic, not in a code change: `clfly/` and the runner have no "
               "commits between the two epochs. The deviation (3.1e-7 relative) sits INSIDE the class this module's "
               "own `--thread-sweep` measures (4.8e-7 to 1.1e-6 per seed at this size), so the thread count of the "
               "process's BLAS is the mechanism",
    },
    "circuit_size=300, support=30, seeds=3, seed0=0, q=0.02": {
        "status": "OPEN -- not attributed",
        "measured_rel": 6.27e-04,
        "why": "`e13_control3_d952` (09-22 16:09) against `e217_ladder_cs300` (09-26 03:59): the newer artifact's "
               "tasks differ from the reproducible ones by 6.3e-4. Rebuilt today the oracle reproduces **e13**'s "
               "value to the last bit -- the older one again -- and the thread sweep at this size spans only "
               "3.5e-6 to 7.1e-6 per seed, i.e. this deviation is **100x the whole measured thread class**, so the "
               "thread count is ruled out. The code path is not the candidate either: every commit between the two "
               "epochs that touches the task or circuit path is a comment or an added function, and the cs-800 group "
               "straddling the same window agrees to the bit. What is left is the SUBSTRATE this run saw -- which "
               "neurons the tight cs-300 budget admits, or the shared support draw -- and it is recorded as open with "
               "that candidate list rather than attributed to a mechanism nothing has measured",
    },
}


def bits(value: float) -> int:
    """The float's bit pattern, so a spread can be stated in ulps rather than in a ratio that hides its class."""
    return struct.unpack("<q", struct.pack("<d", float(value)))[0]


def ulps(a: float, b: float) -> int:
    return abs(bits(a) - bits(b))


def fingerprints(root: Path = RUNS) -> dict:
    """Per artifact: the oracle fingerprint, and whether it is one value across every base that states it."""
    out = {}
    for a in load_artifacts(root):
        cfg = a.get("config") or {}
        for topo, block in (a["payload"].get("topologies") or {}).items():
            if topo != "real" or not isinstance(block, dict):
                continue
            vals, bases = set(), 0
            for name, cell in block.items():
                if not isinstance(cell, dict):
                    continue
                v = (cell.get("analytic") or {}).get("oracle_mean")
                if isinstance(v, (int, float)):
                    vals.add(float(v))
                    bases += 1
            if not vals:
                continue
            excess = ((block.get("diagonal(EWC)") or {}).get("analytic") or {}).get("excess_mean")
            out[a["name"]] = {
                "key": ", ".join(f"{f}={cfg.get(f)!r}" for f in KEY_FIELDS),
                "topology": topo,
                "oracle": sorted(vals),
                "bases_stating_it": bases,
                "excess": float(excess) if isinstance(excess, (int, float)) else None,
            }
    return out


def census(root: Path = RUNS) -> dict:
    fp = fingerprints(root)
    groups: dict[str, list[dict]] = {}
    for name, row in fp.items():
        groups.setdefault(row["key"], []).append({**row, "artifact": name})
    out = []
    for key, rows in sorted(groups.items()):
        one = sorted({v for r in rows for v in r["oracle"]})
        multi_base = [r["artifact"] for r in rows if len(r["oracle"]) > 1]
        out.append({
            "key": key, "artifacts": sorted(r["artifact"] for r in rows), "n": len(rows),
            "oracle_values": one, "ulp_spread": max(ulps(one[0], v) for v in one),
            "rel_spread": (max(one) - min(one)) / abs(one[0]) if len(one) > 1 else 0.0,
            "artifacts_with_more_than_one_oracle_in_their_own_bases": multi_base,
            "excess_values": sorted({r["excess"] for r in rows if r["excess"] is not None}),
        })
    drifts = [g for g in out if g["ulp_spread"] > 0]
    undeclared = [g for g in drifts if g["key"] not in DECLARED_DRIFT]
    return {"groups": out, "drifts": drifts, "undeclared_drifts": undeclared,
            "artifacts": len(fp), "declared_without_a_drift": sorted(set(DECLARED_DRIFT) - {g["key"] for g in drifts})}


def report(res: dict) -> int:
    print("== the `real` cell's input fingerprint (analytic.oracle_mean), by the fields that fix the tasks ==")
    print(f"   artifacts carrying it: {res['artifacts']} in {len(res['groups'])} group(s)")
    multi = [g for g in res["groups"] if g["artifacts_with_more_than_one_oracle_in_their_own_bases"]]
    print(f"   artifacts whose OWN bases disagree on it: {len(multi)}  (it must be one value: the oracle sees no basis)")
    for g in res["groups"]:
        if g["n"] < 2:
            continue
        tag = "EXACT" if g["ulp_spread"] == 0 else f"DRIFT {g['ulp_spread']} ulp, {g['rel_spread']:.2e} rel"
        print(f"\n   {tag:24} {g['key']}   ({g['n']} artifacts)")
        for name in g["artifacts"]:
            print(f"      {name:44}")
        if len(g["oracle_values"]) > 1:
            for v in g["oracle_values"]:
                print(f"      oracle {v!r}")
            ex = g["excess_values"]
            if len(ex) > 1:
                print(f"      and the EXCESS differs by {(max(ex) - min(ex)) / abs(ex[0]):.2e} relative "
                      f"({(max(ex) - min(ex)) / abs(ex[0]) / g['rel_spread']:.1f}x the fingerprint's own spread)")
    for g in res["drifts"]:
        d = DECLARED_DRIFT.get(g["key"])
        if d:
            print(f"   DECLARED [{d['status']}] {g['key']}  {g['rel_spread']:.2e} relative")
            print(f"      {d['why']}")
    for g in res["undeclared_drifts"]:
        print(f"   DRIFT NOT DECLARED: {g['key']}  {g['rel_spread']:.2e} relative")
        print("      (a group whose inputs moved is a finding about the inputs; declare it with the mechanism measured)")
    if res["declared_without_a_drift"]:
        print(f"   NOTE: declared drift with no drift in the corpus: {res['declared_without_a_drift']}")
    if not res["drifts"]:
        print("   (a zero here is the claim: every group of artifacts that must share a task set does -- to the bit.")
        print("    One group does not; it is declared with its mechanism, and the census prints ulps rather than a")
        print("    ratio so that a 1-ulp class and a 5e-7 class cannot be read as the same finding.)")
    return len(res["undeclared_drifts"])


def rebuild(circuit_size: int, support: int, seeds: int, seed0: int, q: float) -> dict:
    """Rebuild one group's tasks from the connectome and return the oracle's per-seed values -- deterministic here."""
    import numpy as np

    from clfly.bench import analytic
    from clfly.connectome import annotate, circuits, graph, tasks

    conn = graph.build()
    ann = annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=circuit_size)
    vals = []
    for seed in range(seed0, seed0 + seeds):
        seq = tasks.build_tasks(circ, support_size=support, q=q, seed=seed).sequence
        vals.append(float(analytic.expected_oracle(seq, 1.0)["final_avg_error"]))
    return {"neurons": int(circ.net.n_neurons), "seeds": seeds, "per_seed": vals,
            "mean": float(np.mean(vals)), "repeat_of_first": float(analytic.expected_oracle(
                tasks.build_tasks(circ, support_size=support, q=q, seed=seed0).sequence, 1.0)["final_avg_error"])}


def oracle_at(circuit_size: int, support: int, seeds: int, seed0: int, q: float) -> int:
    """The child mode of `--thread-sweep`: print the per-seed oracle values of the process it runs in."""
    import os

    import numpy as np

    from clfly.bench import analytic
    from clfly.connectome import annotate, circuits, graph, tasks

    conn = graph.build()
    ann = annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=circuit_size)
    vals = [float(analytic.expected_oracle(tasks.build_tasks(circ, support_size=support, q=q, seed=s).sequence,
                                          1.0)["final_avg_error"]) for s in range(seed0, seed0 + seeds)]
    print(json.dumps({"threads": os.environ.get("OMP_NUM_THREADS"), "per_seed": vals,
                      "mean": float(np.mean(vals))}))
    return 0


def thread_sweep(counts: list[str], circuit_size: int, support: int, seeds: int, seed0: int, q: float) -> int:
    """Run this module at each thread count and compare the per-seed values -- the mechanism, measured."""
    runs = {}
    for c in counts:
        env = None if c == "default" else {"OMP_NUM_THREADS": c}
        import os

        full = dict(os.environ)
        if env:
            full.update(env)
        else:
            full.pop("OMP_NUM_THREADS", None)
        out = subprocess.run([sys.executable, "-m", "experiments.e227_oracle_fingerprint_census", "--oracle-at",
                              "--circuit-size", str(circuit_size), "--support", str(support), "--seeds", str(seeds),
                              "--seed0", str(seed0), "--q", str(q)],
                             capture_output=True, text=True, env=full, check=True)
        line = [ln for ln in out.stdout.splitlines() if ln.startswith("{")][-1]
        runs[c] = json.loads(line)
        print(f"   OMP_NUM_THREADS={c:>7}  mean {runs[c]['mean']!r}")
        for s, v in zip(range(seed0, seed0 + seeds), runs[c]["per_seed"]):
            print(f"      seed {s}: {v!r}")
    base = next(iter(runs))
    for other in list(runs)[1:]:
        ds = [abs(a - b) for a, b in zip(runs[base]["per_seed"], runs[other]["per_seed"])]
        rs = [d / abs(a) for d, a in zip(ds, runs[base]["per_seed"])]
        print(f"   {base} vs {other}: per-seed absolute {min(ds):.2e}-{max(ds):.2e}, "
              f"relative {min(rs):.2e}-{max(rs):.2e}")
    print("   (one task's oracle error moves in the seventh digit from the thread count alone: the analytic path is")
    print("    exact arithmetic in principle and this is what bounds 'exact' on this machine.)")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--runs", type=Path, default=RUNS)
    p.add_argument("--json-out", type=Path, default=None)
    p.add_argument("--rebuild", action="store_true", help="rebuild the declared group's oracle (loads the connectome)")
    p.add_argument("--thread-sweep", default=None,
                   help="comma-separated OMP_NUM_THREADS values (or `default`) to run the oracle under, in children")
    p.add_argument("--oracle-at", action="store_true", help="child mode: print this process's per-seed oracle values")
    p.add_argument("--circuit-size", type=int, default=1500)
    p.add_argument("--support", type=int, default=150)
    p.add_argument("--seeds", type=int, default=4)
    p.add_argument("--seed0", type=int, default=0)
    p.add_argument("--q", type=float, default=0.02)
    args = p.parse_args(argv)

    if args.oracle_at:
        return oracle_at(args.circuit_size, args.support, args.seeds, args.seed0, args.q)

    res = census(args.runs)
    n = report(res)
    if args.thread_sweep:
        print("\n== the mechanism: the oracle's own arithmetic, by thread count ==")
        n += thread_sweep([c.strip() for c in args.thread_sweep.split(",")],
                          args.circuit_size, args.support, args.seeds, args.seed0, args.q)
    if args.rebuild:
        print("\n== the declared group's tasks, rebuilt from the connectome ==")
        r = rebuild(args.circuit_size, args.support, args.seeds, args.seed0, args.q)
        print(f"   circuit {r['neurons']} neurons, {r['seeds']} seeds, oracle mean {r['mean']!r}")
        for g in res["groups"]:
            if g["key"] not in DECLARED_DRIFT:
                continue
            for v in g["oracle_values"]:
                print(f"   vs the stored value {v!r}: {ulps(r['mean'], v)} ulp(s)")
        res["rebuild"] = {k: v for k, v in r.items() if k != "per_seed"}
    if args.json_out:
        write_json(args.json_out, res)
        print(f"wrote {args.json_out}")
    return 0 if n == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
