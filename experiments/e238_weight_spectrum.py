"""E238 -- the collapse's onset from `W`'s own spectrum: the eigencollapse is EXACTLY predictable, so the question is whether it is what we measured.

`stable_weights` ends in `return (W * (rho / radius)).tocsr()` -- a **pure scalar rescale**. So with
`Ŵ = W / radius` (spectral radius 1, independent of `rho`):

    W(rho) = rho * Ŵ,   G(rho) = (I - rho Ŵ)^-1,   eig(G(rho)) = 1 / (1 - rho λ̂_i)

which makes the **eigenvalue** side of the collapse exactly computable from `Ŵ`'s leading eigenvalues -- no tasks, no
seeds, no supports, no solves -- and turns `e237`'s measurement into a test rather than a description:

- **S1**: the predicted eigenvalue participation ratio `pr_eig(rho)` (over the k leading modes, `p_i ∝ |1/(1 - rho λ̂_i)|²`)
  falls with `rho` and **orders the four families the same way** the measured singular-value `pr_G` does at each `rho`
  where the leading modes dominate (`rho >= 0.9`). **Falsifier**: a different family ordering;
- **S2**: the family that keeps the largest measured `pr_G` at `rho` 0.99 (`erdos_renyi`, 4.14) has the **largest
  |λ̂_2|** -- the smallest eigenvalue gap -- and the family that collapses furthest (`real`, 1.04) has the smallest.
  **Falsifier**: the opposite ordering, which would say the residual rank is not the second eigenvalue's magnification.

`--verify` checks the scalar-rescale property itself: the same matrix read at two `rho` values must have eigenvalues in
exactly the ratio of the two `rho`s, so a failure there is a defect in this module rather than a finding.

    python -m experiments.e238_weight_spectrum --grid 0.7,0.9,0.95,0.99 --sizes 300,800
    python -m experiments.e238_weight_spectrum --json-out runs/e238_weight_spectrum.json

The exit code is the number of cells that could **not** be measured (a failed ARPACK call, a non-finite statistic).

**What it cannot do**: eigenvalues predict the *eigenvalue* participation ratio only. The measured `pr_G` is a
**singular-value** statistic, and for a non-normal operator (`sigma_1(Ŵ) > |λ_1|`, which this module reports) the two
need not agree -- that gap between them is exactly what S1 tests, and a failure of S1 is a statement about
non-normality rather than about the substrate. The prediction also uses only the `k` leading modes, so it cannot be
read at low `rho` where hundreds of modes matter.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
TOPOLOGIES = ("real", "alloy1", "inalloy1", "erdos_renyi")
SIZES = {300: 30, 400: 40, 800: 80, 1500: 150}
N_MODES = 40


def participation_ratio(values: np.ndarray) -> float:
    w = np.asarray(values, dtype=float)
    w = w[w > 1e-12 * max(1.0, float(w.max()))] if w.size else w
    if w.size == 0:
        return float("nan")
    w = w / w.sum()
    return float(1.0 / np.sum(w ** 2))


def normalised_spectrum(size: int, topologies=TOPOLOGIES, seed0: int = 0, k: int = N_MODES) -> dict:
    """`Ŵ`'s leading eigenvalues and its largest singular value, per topology -- the rho-independent object."""
    from clfly.connectome import annotate, circuits, graph, rewiring, tasks
    from scipy.sparse.linalg import eigs

    conn = graph.build()
    ann = annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    W0 = circ.net.weights()
    out = {"size": int(size), "neurons": int(circ.net.n_neurons), "topologies": {}}
    for topo in topologies:
        W = rewiring.apply_null(W0, topo, np.random.default_rng(seed0))
        circ.net = graph.Connectome(circ.net.n_neurons, circ.net.root_ids, W.tocsr())
        try:
            Wh = tasks.stable_weights(circ.net, rho=1.0)
            kk = min(k, Wh.shape[0] - 2)
            lam = eigs(Wh, k=kk, which="LM", return_eigenvectors=False, v0=np.ones(Wh.shape[0]), maxiter=5000)
            lam = lam[np.argsort(-np.abs(lam))]
            # the departure from normality: sigma_1 of a matrix is at least its spectral radius
            s1 = float(np.linalg.svd(Wh.toarray(), compute_uv=False)[0])
            out["topologies"][topo] = {
                "lambda_abs": [float(abs(x)) for x in lam],
                "lambda_top": [complex(x) for x in lam[:6]],
                "sigma_1": s1, "radius_measured": float(abs(lam).max()), "modes": int(kk)}
        except Exception as exc:
            out["topologies"][topo] = {"error": f"{type(exc).__name__}: {exc}"[:120]}
    return out


def predict(lam_abs: list[float], rho: float) -> float:
    """The predicted eigenvalue participation ratio of `G(rho)` from `Ŵ`'s leading eigenvalues.

    `eig(G) = 1 / (1 - rho λ̂)`, so the magnitudes are fixed by the leading modes and the whole rho dependence is the
    denominator -- which is what makes this a prediction rather than a restatement.
    """
    if not lam_abs:
        return float("nan")
    mags = np.array([abs(1.0 / (1.0 - rho * l)) for l in lam_abs])
    return participation_ratio(mags ** 2)


def rescale_check(size: int, topo: str, rhos=(0.9, 0.99), seed0: int = 0) -> dict:
    """The property the prediction rests on, measured: the same matrix's leading eigenvalue at two `rho` values must
    be in exactly the ratio of the two `rho`s -- `stable_weights` is `W * (rho / radius)` and nothing else."""
    from scipy.sparse.linalg import eigs

    from clfly.connectome import annotate, circuits, graph, rewiring, tasks

    conn = graph.build()
    ann = annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    W = rewiring.apply_null(circ.net.weights(), topo, np.random.default_rng(seed0))
    circ.net = graph.Connectome(circ.net.n_neurons, circ.net.root_ids, W.tocsr())
    out = {"size": size, "topology": topo, "rhos": list(rhos)}
    for r in rhos:
        Ws = tasks.stable_weights(circ.net, rho=r)
        lam = eigs(Ws, k=2, which="LM", return_eigenvectors=False, v0=np.ones(Ws.shape[0]))
        out[f"lambda_max_at_{r}"] = float(np.abs(lam).max())
    vals = [out[f"lambda_max_at_{r}"] for r in rhos]
    out["ratio"] = vals[0] / vals[1]
    out["expected"] = rhos[0] / rhos[1]
    return out


def measured_whole_matrix(runs: Path = RUNS) -> dict:
    """`e237`'s whole-matrix rank, keyed by (size, topology, rho) -- what the prediction is tested against."""
    out = {}
    try:
        d = json.loads((runs / "e237_propagator_spectrum.json").read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return out
    for r in d.get("rows", []):
        for topo, cell in (r.get("topologies") or {}).items():
            if isinstance(cell.get("pr_G"), (int, float)):
                out[(r["size"], topo, round(r["rho"], 4))] = float(cell["pr_G"])
    return out


def report(spectra: list[dict], grid: list[float], measured: dict | None = None,
           verify: list[dict] | None = None) -> int:
    print("== W's own leading spectrum (rho-independent: `stable_weights` is a scalar rescale) ==")
    for s in spectra:
        print(f"\n   cs {s['size']}  ({s['neurons']} neurons)")
        print(f"      {'topology':12} {'|lam1|':>8} {'|lam2|':>8} {'|lam3|':>8} {'gap 1-2':>8} {'sigma1':>8} "
              f"{'sigma1/|lam1|':>14}")
        for topo in TOPOLOGIES:
            c = s["topologies"].get(topo, {})
            la = c.get("lambda_abs") or []
            if not la:
                print(f"      {topo:12}   UNMEASURABLE {c.get('error') or ''}")
                continue
            g = 1.0 - (la[1] if len(la) > 1 else float("nan"))
            print(f"      {topo:12} {la[0]:>8.4f} {(la[1] if len(la) > 1 else float('nan')):>8.4f} "
                  f"{(la[2] if len(la) > 2 else float('nan')):>8.4f} {g:>8.4f} {c['sigma_1']:>8.3f} "
                  f"{c['sigma_1'] / la[0]:>14.3f}")
    print("\n== the prediction: the eigencollapse of G(rho) = (I - rho Wh)^-1, from the modes above ==")
    for s in spectra:
        print(f"\n   cs {s['size']}")
        print(f"      {'topology':12} " + " ".join(f"{rho:>8.3g}" for rho in grid) + "   (predicted pr_eig)")
        for topo in TOPOLOGIES:
            la = (s["topologies"].get(topo) or {}).get("lambda_abs") or []
            if not la:
                continue
            row = [predict(la, rho) for rho in grid]
            print(f"      {topo:12} " + " ".join(f"{v:>8.2f}" for v in row))
            if measured:
                mv = [measured.get((s["size"], topo, round(rho, 4))) for rho in grid]
                print(f"      {'':12} " + " ".join("      -" if v is None else f"{v:>8.2f}" for v in mv)
                      + "   (measured pr_G, e237)")
    if verify:
        print("\n== the scalar-rescale property this prediction rests on ==")
        bad = 0
        for v in verify:
            ok = abs(v["ratio"] - v["expected"]) < 1e-6 * max(v["expected"], 1e-12)
            bad += 0 if ok else 1
            print(f"      cs {v['size']} {v['topology']:12} |lam| ratio {v['ratio']:.6f} against the rho ratio "
                  f"{v['expected']:.6f}  {'ok' if ok else 'MISMATCH'}")
        if bad:
            print(f"   {bad} mismatch(es): this module reads the rescale wrongly, and the prediction is void")
    bad_cells = sum(1 for s in spectra for c in s["topologies"].values() if not c.get("lambda_abs"))
    print(f"\n   unmeasurable cells: {bad_cells}")
    return bad_cells


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grid", default="0.7,0.8,0.9,0.95,0.98,0.99")
    ap.add_argument("--sizes", default="300,800")
    ap.add_argument("--seed0", type=int, default=0)
    ap.add_argument("--modes", type=int, default=N_MODES)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    grid = [float(x) for x in args.grid.split(",") if x.strip()]
    sizes = [int(s) for s in args.sizes.split(",") if s.strip()]
    spectra = []
    for size in sizes:
        s = normalised_spectrum(size, seed0=args.seed0, k=args.modes)
        spectra.append(s)
        print(f"   cs {size} done: " + "  ".join(
            f"{t} |lam| {[round(x, 3) for x in ((s['topologies'].get(t) or {}).get('lambda_abs') or [])[:3]]}"
            for t in TOPOLOGIES), flush=True)
    checks = [rescale_check(sizes[0], t, seed0=args.seed0) for t in TOPOLOGIES[:2]]
    if args.json_out:
        write_json(args.json_out, {"spectra": spectra, "grid": grid, "rescale_check": checks})
        print(f"wrote {args.json_out}")
    return report(spectra, grid, measured_whole_matrix(), checks)


if __name__ == "__main__":
    sys.exit(main())
