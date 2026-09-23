"""E136 -- is the barrier a property of the pair, or of the read-out? Three stored grids, three answers.

`e131` established that the **level** of the fit-task barrier is set by how much the body carries at that
read-out (median barrier/chance 0.1157 at read-out 32, 0.0361 at 128, 0.0054 at 1307, ordered like the
load-bearing gap and not like the per-repeat spread). Its own finding lists as a limitation that *"three read-outs
is still a curve on three points"*. **This script asks a question about the grids rather than about the curve: the
three runs used the SAME twelve seeds, so the same 66 pairs appear in all three — and "which pair is worst" can be
compared across them directly.**

    python -m experiments.e136_geometry_persistence --json-out runs/e136_geometry_persistence.json

Three questions, in increasing order of how much they assume:

1. **Do the per-pair barriers correlate across read-outs?** The grids are paired (66 shared pairs), so this is a
   correlation of two 66-vectors.
2. **Do the worst sets overlap?** This is combinatorial rather than statistical and needs no correlation model:
   how many of read-out A's worst ten are in read-out B's worst ten?
3. **Is it the seed rather than the pair?** Each seed appears in 11 pairs, so a seed's own level is the mean
   barrier over those eleven, and the twelve seeds give a 12-vector per read-out.

**What the answers cannot be**: 66 pairs from 12 seeds are heavily dependent, so the pair-level correlations have
an effective `n` of 12 and not 66, and any correlation here is a description of these grids rather than an
estimate of a population. The overlap counts have no such problem — they are exact for the three grids.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

# The three grids, all twelve seeds `0 + 100k`, checkpoint 2, and the read-out each was run at.
DEFAULT_GRIDS = {"32": "runs/e130_barrier_r32.json",
                 "128": "runs/e124_barrier_12seeds.json",
                 "1307": "runs/e131_barrier_r1307.json"}
CHECKPOINT = 2          # the checkpoint after the last task: where the barrier carries a signal


def barriers(path: Path, checkpoint: int = CHECKPOINT) -> dict[tuple[int, int], float]:
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return {(r["seed_a"], r["seed_b"]): r["barrier_over_chance"]
            for r in d["fit_tasks"] if r["checkpoint"] == checkpoint}


def rank_corr(x: np.ndarray, y: np.ndarray) -> float:
    return float(np.corrcoef(np.argsort(np.argsort(x)), np.argsort(np.argsort(y)))[0, 1])


def analyse(grids: dict[str, str], worst: int = 10) -> dict:
    V = {k: barriers(Path(p)) for k, p in grids.items()}
    keys = sorted(set.intersection(*[set(v) for v in V.values()]))

    pair_r, tops = [], {}
    for a, b in itertools.combinations(list(V), 2):
        x = np.array([V[a][k] for k in keys])
        y = np.array([V[b][k] for k in keys])
        pair_r.append({"readout_a": a, "readout_b": b, "pearson": float(np.corrcoef(x, y)[0, 1]),
                       "spearman": rank_corr(x, y), "n_pairs": len(keys)})
    for k in V:
        tops[k] = {p for p, _ in sorted(V[k].items(), key=lambda kv: -kv[1])[:worst]}

    seeds = sorted({s for v in V.values() for p in v for s in p})
    per_seed = {s: [float(np.mean([v for p, v in V[k].items() if s in p])) for k in V] for s in seeds}
    seed_r = []
    for a, b in itertools.combinations(list(V), 2):
        x = np.array([per_seed[s][list(V).index(a)] for s in seeds])
        y = np.array([per_seed[s][list(V).index(b)] for s in seeds])
        seed_r.append({"readout_a": a, "readout_b": b, "pearson": float(np.corrcoef(x, y)[0, 1]),
                       "spearman": rank_corr(x, y), "n_seeds": len(seeds)})

    concentration = {}
    for k in V:
        col = np.array([per_seed[s][list(V).index(k)] for s in seeds])
        concentration[k] = {"worst_seed": int(seeds[int(col.argmax())]), "worst": float(col.max()),
                            "median": float(np.median(col)), "ratio": float(col.max() / np.median(col))}

    return {"grids": grids, "n_shared_pairs": len(keys), "n_seeds": len(seeds),
            "pair_level_correlations": pair_r,
            "worst_overlaps": {f"{a}|{b}": len(tops[a] & tops[b]) for a, b in itertools.combinations(tops, 2)},
            "worst_all_three": len(set.intersection(*tops.values())) if len(tops) > 2 else None,
            "worst_of": {k: sorted(tops[k]) for k in tops},
            "per_seed_mean_barrier": {str(s): per_seed[s] for s in seeds},
            "seed_level_correlations": seed_r,
            "concentration": concentration}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--grid", nargs=2, action="append", metavar=("READOUT", "ARTIFACT"), default=None,
                   help=f"override the defaults ({', '.join(f'{k}={v}' for k, v in DEFAULT_GRIDS.items())})")
    p.add_argument("--worst", type=int, default=10)
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    grids = dict(args.grid) if args.grid else dict(DEFAULT_GRIDS)
    res = analyse(grids, worst=args.worst)
    print(f"shared pairs {res['n_shared_pairs']}, seeds {res['n_seeds']}\n")
    print("1. per-PAIR barriers across read-outs")
    for r in res["pair_level_correlations"]:
        print(f"   {r['readout_a']:>5} vs {r['readout_b']:<5}: pearson {r['pearson']:+.3f}  "
              f"spearman {r['spearman']:+.3f}   (n = {r['n_pairs']} dependent pairs)")
    print(f"\n2. the worst-{args.worst} SETS")
    for k, v in res["worst_overlaps"].items():
        print(f"   {k:>12}: {v} of {args.worst} shared")
    print(f"   all three  : {res['worst_all_three']} of {args.worst}")
    print(f"\n3. per-SEED mean barrier")
    for r in res["seed_level_correlations"]:
        print(f"   {r['readout_a']:>5} vs {r['readout_b']:<5}: pearson {r['pearson']:+.3f}  "
              f"spearman {r['spearman']:+.3f}   (n = {r['n_seeds']} seeds)")
    print("   concentration of the worst seed:")
    for k, c in res["concentration"].items():
        print(f"     read-out {k:>5}: seed {c['worst_seed']:5} at {c['worst']:.4f}, median seed "
              f"{c['median']:.4f}, ratio {c['ratio']:.2f}x")
    print("\nNOTE: the pair-level correlations describe these grids. 66 pairs from 12 seeds means an effective"
          "\n      n of 12, so they are not an estimate of a population; the overlap counts are exact for the"
          "\n      three grids as they stand.")
    if args.json_out:
        write_json(args.json_out, res)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
