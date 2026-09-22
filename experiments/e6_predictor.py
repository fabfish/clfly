"""E6 — does projection pressure predict the anchoring penalty?

C2's weak point has been that it had no *a-priori* predictor: the project could
measure that a biological partition beats a size-matched random one, but could not
say in advance which partition would be good, and the principal-angle scalar failed
at the job.

`clfly.bench.analytic.projection_pressure` is a candidate with the right pedigree:
it is the LGCL mechanism stated directly. Run the **exact** filter — whose prior
trajectory is basis-independent, so this is computable before any anchored filter
exists — and measure how much of each predicted prior the basis would discard,
weighted by the task's measurement information:

    pressure = sum_k  || J_k^{1/2} disc_k J_k^{1/2} ||_F^2 / || J_k^{1/2} P_pred,k J_k^{1/2} ||_F^2

On the real connectome it ranks 11 candidate bases against the analytic excess with
Spearman +0.99, and gets the biological-versus-random sign right at all five matched
pairs. That is promising and it is also *in sample*: the same data that suggested the
predictor. This script tests it out of sample, across circuit size, drift, task width
and topology — including the rewired graphs, where the task geometry is not the one
the predictor was first evaluated on.

The prediction is a ranking claim, so the test is rank correlation plus sign
agreement at matched pairs. A predictor that only recovers
`constrained_fraction` would fail the sign test, because matched pairs have
identical `constrained_fraction` by construction.

    python -m experiments.e6_predictor
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from clfly.bench.analytic import analytic_excess, projection_pressure, spearman
from clfly.connectome import annotate, circuits, graph, rewiring, tasks
from clfly.lgcl.bases import Diagonal, Partition, random_partition

REPO_ROOT = Path(__file__).resolve().parents[1]

#: The rungs tested.  Each contributes a biological basis and its size-matched
#: random control, so every condition carries five matched pairs.
RUNGS = ("side", "cell_class", "cell_type", "ito_lee_hemilineage", "supertype")

#: Out-of-sample conditions.  The predictor was first evaluated at the first row.
CONDITIONS = (
    dict(label="baseline", circuit_size=300, support=30, q=0.02, topology="real"),
    dict(label="wider-tasks", circuit_size=300, support=60, q=0.02, topology="real"),
    dict(label="faster-drift", circuit_size=300, support=30, q=0.10, topology="real"),
    dict(label="rewired-swap2", circuit_size=300, support=30, q=0.02, topology="swap2"),
    dict(label="larger-circuit", circuit_size=800, support=80, q=0.02, topology="real"),
)


def candidate_bases(circ, rng):
    out = {"diagonal(EWC)": Diagonal(circ.n_neurons)}
    for col in RUNGS:
        if col not in circ.labels:
            continue
        out[f"bio:{col}"] = Partition(circ.labels[col])
        out[f"rand:{col}"] = random_partition(circ.labels[col], rng)
    return out


def run_condition(cond, args, conn, ann) -> dict:
    circ = circuits.extract(conn, ann, hops=0, max_neurons=cond["circuit_size"])
    if cond["topology"] != "real":
        W0 = circ.net.weights()
        W = rewiring.apply_null(W0, cond["topology"], np.random.default_rng(args.seed0))
        circ.net = graph.Connectome(circ.net.n_neurons, circ.net.root_ids, W.tocsr())

    seqs = [tasks.build_tasks(circ, support_size=cond["support"], q=cond["q"],
                              seed=s).sequence
            for s in range(args.seed0, args.seed0 + args.seeds)]

    rng = np.random.default_rng(args.seed0)
    rows = []
    for name, b in candidate_bases(circ, rng).items():
        ex = analytic_excess(seqs, b)
        rows.append({
            "basis": name,
            "excess": ex["excess_mean"],
            "excess_sem": ex["excess_sem"],
            "pressure": float(np.mean([projection_pressure(s, b) for s in seqs])),
            #: Carried through so the matched pairs can be checked *per seed* rather than only on
            #: their pooled means.  Without it the run reproduces `e6_predictor_6` exactly and adds
            #: nothing, which is what the first launch of `e64` did: every basis in a condition sees
            #: the same task geometries in the same order, so the per-seed excesses are matched and
            #: the contrast between a biological basis and its control is a paired quantity.
            "excess_per_seed": ex.get("excess_per_seed"),
        })
    return {"condition": cond, "d": seqs[0].d, "n_seeds": len(seqs), "rows": rows}


def evaluate(rows) -> dict:
    """Rank correlation, plus sign agreement on every matched bio/random pair.

    Also reports each pair's **resolvability**: the standard error of the excess
    difference.  This matters because the predictor is sometimes asked to order
    differences far below what the excess metric can measure, and a "miss" on such a
    pair is not a failure of the predictor — no predictor can be scored on a quantity
    that is not there to order.
    """
    names = [r["basis"] for r in rows]
    excess = [r["excess"] for r in rows]
    sem = [r.get("excess_sem", 0.0) for r in rows]
    pressure = [r["pressure"] for r in rows]

    pairs, agree, resolvable_pairs = [], 0, 0
    for rung in RUNGS:
        b, r = f"bio:{rung}", f"rand:{rung}"
        if b not in names or r not in names:
            continue
        ib, ir = names.index(b), names.index(r)
        d_ex = excess[ib] - excess[ir]
        d_pr = pressure[ib] - pressure[ir]
        d_sem = float(np.hypot(sem[ib], sem[ir]))
        sigma = abs(d_ex) / d_sem if d_sem else float("inf")
        ok = (d_ex < 0) == (d_pr < 0)
        agree += bool(ok)
        resolvable_pairs += bool(sigma > 2.0)
        pairs.append({"rung": rung, "excess_delta": d_ex, "pressure_delta": d_pr,
                      "excess_sem": d_sem, "sigma": sigma,
                      "resolvable": bool(sigma > 2.0), "sign_ok": ok})
    return {
        "spearman": spearman(pressure, excess),
        "sign_agree": agree,
        "n_pairs": len(pairs),
        "n_resolvable_pairs": resolvable_pairs,
        "sign_agree_resolvable": sum(p["sign_ok"] for p in pairs if p["resolvable"]),
        "pairs": pairs,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seeds", type=int, default=2)
    p.add_argument("--seed0", type=int, default=0)
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    t0 = time.time()
    conn = graph.build()
    ann = annotate.load_annotations()

    out = {"config": vars(args), "conditions": []}
    print(f"{'condition':16} {'d':>6} {'rho':>7} {'sign':>6} {'resolv':>7}  per-pair")
    print("-" * 82)
    for cond in CONDITIONS:
        res = run_condition(cond, args, conn, ann)
        ev = evaluate(res["rows"])
        res["pairs"] = ev.pop("pairs")
        res["eval"] = ev
        out["conditions"].append(res)
        signs = "".join("+" if p["sign_ok"] else "-" for p in res["pairs"])
        print(f"{cond['label']:16} {res['d']:6d} {ev['spearman']:+7.3f} "
              f"{ev['sign_agree']}/{ev['n_pairs']:>2}   "
              f"{ev['sign_agree_resolvable']}/{ev['n_resolvable_pairs']:>2}    {signs}   "
              f"({time.time()-t0:.0f}s)")

    rhos = [c["eval"]["spearman"] for c in out["conditions"]]
    agree = sum(c["eval"]["sign_agree"] for c in out["conditions"])
    pairs = sum(c["eval"]["n_pairs"] for c in out["conditions"])
    print("-" * 76)
    print(f"mean Spearman {np.mean(rhos):+.3f}   "
          f"matched-pair sign agreement {agree}/{pairs}")
    print("  (a predictor that only recovers constrained_fraction scores 0 on the")
    print("   sign test, since matched pairs share constrained_fraction exactly)")
    out["summary"] = {"mean_spearman": float(np.mean(rhos)),
                      "sign_agree": int(agree), "n_pairs": int(pairs),
                      "time_s": time.time() - t0}

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(out, indent=1, default=str))
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
