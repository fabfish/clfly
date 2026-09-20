"""Reproduce every published LGCL number from the ported package.

``reference/lgcl_source/`` holds the original materials -- paper drafts v2-v8,
the technical memo, ``lgcl_toy.py`` and ``lgcl_results.json``.  Those report a
set of Monte Carlo numbers.  This module recomputes them and reports the worst
absolute deviation, which is the project's Phase-1 gate: if the port does not
reproduce the published numbers, nothing built on top of it is trustworthy.

    python -m clfly.lgcl.repro              # gated anchors
    python -m clfly.lgcl.repro --json       # the metric-loop entry point
    python -m clfly.lgcl.repro --explore    # also the unverified configurations
    python -m clfly.lgcl.repro --quick      # fewer runs, for a fast smoke test

**Which anchors are gated, and why only these.** ``exp1`` reproduces bit-for-bit
(``repro_max_abs_err`` ~5e-5 at 200 runs) because its generating configuration is
fully pinned down: ``lgcl_toy.py`` ships the driver with every parameter.

The other published numbers are a different story.  ``lgcl_toy.py`` contains only
*helpers* for the exp3/exp4/exp5 families -- the scripts that produced those
numbers were not included in the materials, so their configurations (observation
model, error convention, run count) are not recoverable.  Reconstructing a
configuration by searching until a number matches would be fitting, not
reproducing, so those are computed only under ``--explore`` and are reported
against the published values *without* being allowed to gate.

What that exploration found is itself a result worth keeping -- see
:mod:`clfly.lgcl.probes` and ``docs/findings/`` -- and it is one of the reasons
this project needs a real connectome rather than another synthetic task family.
"""

from __future__ import annotations

import argparse
import json

import numpy as np

from .methods import Replay, run, spectral_truncation
from .model import error_tensor, sample_full, sample_partial, summarize

# --------------------------------------------------------------------------
# published values (reference/lgcl_source/lgcl_results.json)
# --------------------------------------------------------------------------
EXP1_FINAL = {"naive": 2.4979, "ewc": 1.2013, "replay": 0.9881, "sketch": 1.1989, "kalman": 1.1915}
EXP1_FORGET = {"naive": 2.2173, "ewc": 1.0399, "replay": 0.7481, "sketch": 1.0400, "kalman": 1.0343}
EXP1_CFG = dict(d=20, T=10, n=40, sigma2=1.0, q=0.05, rotation="random")

EXP3 = {"rel_excess": 0.84749, "at_deg": 12.0}
EXP3_CFG = dict(d=2, T=10, n=40, sigma2=1.0, q=0.05)

EXP4_CURVE = {
    1: 0.087650, 2: 0.080894, 3: 0.075812, 4: 0.071402, 6: 0.063818,
    8: 0.057567, 10: 0.050163, 12: 0.042592, 16: 0.041991, 20: 0.041900,
}
EXP4_CFG = dict(d=20, T=10, n=40, sigma2=1.0, q=0.02, obs_dim=8)

EXP5_MEASURED = {1: -0.28, 2: -0.10, 3: 0.02, 4: 0.11, 6: 0.26, 8: 0.37, 11: 0.47}
EXP5_CFG = dict(d=20, T=12, n=40, sigma2=1.0, q=0.02, obs_dim=8)

METHODS = ("naive", "ewc", "replay", "sketch", "kalman")
REPLAY_BUDGET = 3
SKETCH_R = 4


# --------------------------------------------------------------------------
# gated experiment
# --------------------------------------------------------------------------
def exp1_main(runs: int = 200, seed0: int = 0) -> dict:
    """The headline comparison: does EWC match the Kalman oracle in d=20?

    Published result, reproduced here to ~5e-5: EWC and full Kalman differ by
    <1%, and even a 4-of-20 spectral truncation loses nothing.  This is the
    "high-dimensional blessing" -- random task rotations wash the posterior
    covariance toward isotropy, so the diagonal approximation looks free.
    It is the assumption the rest of this project exists to stress-test.
    """
    fin = {m: [] for m in METHODS}
    fgt = {m: [] for m in METHODS}
    for r in range(runs):
        rng = np.random.default_rng(seed0 + r)
        seq = sample_full(rng=rng, **EXP1_CFG)
        for m in METHODS:
            ests = run(m, seq, budget=REPLAY_BUDGET, r=SKETCH_R)
            s = summarize(error_tensor(ests, seq))
            fin[m].append(s["final_avg_error"])
            fgt[m].append(s["forgetting"])
    out = {f"exp1.final_avg_error.{m}": float(np.mean(fin[m])) for m in METHODS}
    out |= {f"exp1.forgetting.{m}": float(np.mean(fgt[m])) for m in METHODS}
    return out


# --------------------------------------------------------------------------
# exploratory: published numbers whose driver scripts are not in the materials
# --------------------------------------------------------------------------
def exp4_rate_distortion(runs: int = 200, seed0: int = 0) -> dict:
    """Memory budget vs error under partial observation.

    Published result: with only 8 of 20 directions observable, error falls
    monotonically in the spectral budget and saturates near r=12.  Our
    reconstruction reproduces the *shape* -- monotone decrease saturating around
    r=12 -- but sits at a different level (0.157 -> 0.119 against a published
    0.088 -> 0.042), so the observation model or error convention differs from
    the original.  The qualitative claim is confirmed; the numbers are not
    comparable.
    """
    rs = sorted(EXP4_CURVE)
    errs = {r: [] for r in rs}
    for i in range(runs):
        rng = np.random.default_rng(seed0 + i)
        seq = sample_partial(rng=rng, **EXP4_CFG)
        for r in rs:
            errs[r].append(summarize(error_tensor(spectral_truncation(seq, r), seq))["final_avg_error"])
    return {f"exp4.curve.{r}": float(np.mean(errs[r])) for r in rs}


def exp3_misalignment(runs: int = 200, seed0: int = 0, step_deg: float = 6.0,
                      n: int | None = None) -> dict:
    """Excess EWC cost as a function of per-task basis rotation.

    Published result: unimodal, peaking near 12 deg per task and vanishing at
    both 0 deg (aligned) and 90 deg (an axis swap in 2-D is still diagonal) --
    the endpoints tell us the rotation is *cumulative* per task, not a fixed
    offset.  We find no such peak in the coordinate basis; see
    :mod:`clfly.lgcl.probes` for the sweep and ``docs/findings/`` for the
    reading.  The 0/90 deg endpoints do vanish, confirming the geometry is set
    up correctly.
    """
    cfg = dict(EXP3_CFG)
    if n is not None:
        cfg["n"] = n
    grid = np.arange(0.0, 90.0 + 1e-9, step_deg)
    excess = []
    for a_deg in grid:
        alpha = np.deg2rad(a_deg)
        e_ewc, e_kal = [], []
        for i in range(runs):
            rng = np.random.default_rng(seed0 + i)
            seq = sample_full(rng=rng, alpha=alpha, rotation="cumulative", **cfg)
            e_ewc.append(summarize(error_tensor(run("ewc", seq), seq))["final_avg_error"])
            e_kal.append(summarize(error_tensor(run("kalman", seq), seq))["final_avg_error"])
        m_ewc, m_kal = float(np.mean(e_ewc)), float(np.mean(e_kal))
        excess.append((m_ewc - m_kal) / m_kal if m_kal > 0 else 0.0)
    excess = np.array(excess)
    i = int(np.argmax(excess))
    return {"exp3.rel_excess": float(excess[i]), "exp3.at_deg": float(grid[i])}


def exp5_replay_recovery(runs: int = 200, seed0: int = 0) -> dict:
    """Replay's recovery of the memory-structure gap, vs budget.

    Published result: negative recovery at b=1 (replay *hurts*), crossing zero
    near b=3, saturating around 47%.  Our reconstruction of that convention does
    not line up, so this stays exploratory.
    """
    from .kalman import rts_smoother

    budgets = sorted(EXP5_MEASURED)

    def old_task_err(ests, seq):
        E = error_tensor(ests, seq)
        T = seq.T
        return float(np.mean([E[T - 1, j] - E[j, j] for j in range(T - 1)]))

    e_filt, e_smooth, e_rep = [], [], {b: [] for b in budgets}
    for i in range(runs):
        rng = np.random.default_rng(seed0 + i)
        seq = sample_partial(rng=rng, **EXP5_CFG)
        e_filt.append(old_task_err(run("kalman", seq), seq))
        e_smooth.append(old_task_err(rts_smoother(seq)[0], seq))
        for b in budgets:
            e_rep[b].append(old_task_err(Replay(budget=b).run(seq), seq))

    f0, s0 = float(np.mean(e_filt)), float(np.mean(e_smooth))
    gap = f0 - s0
    out = {"exp5.e_filter": f0, "exp5.e_smoother": s0}
    for b in budgets:
        eb = float(np.mean(e_rep[b]))
        out[f"exp5.recovery.b{b}"] = (f0 - eb) / gap if gap else 0.0
    return out


GATED = {"exp1": exp1_main}
EXPLORATORY = {"exp3": exp3_misalignment, "exp4": exp4_rate_distortion,
               "exp5": exp5_replay_recovery}


# --------------------------------------------------------------------------
# comparison
# --------------------------------------------------------------------------
def gated_anchors() -> dict[str, float]:
    """Published values whose generating configuration is fully pinned down."""
    out = {f"exp1.final_avg_error.{m}": v for m, v in EXP1_FINAL.items()}
    out |= {f"exp1.forgetting.{m}": v for m, v in EXP1_FORGET.items()}
    return out


def exploratory_anchors() -> dict[str, float]:
    out = {"exp3.rel_excess": EXP3["rel_excess"], "exp3.at_deg": EXP3["at_deg"]}
    out |= {f"exp4.curve.{r}": v for r, v in EXP4_CURVE.items()}
    return out


def compare(computed: dict, expected: dict) -> tuple[list[dict], float]:
    rows, worst = [], 0.0
    for name, exp in expected.items():
        if name not in computed:
            continue
        got = computed[name]
        err = abs(got - exp)
        worst = max(worst, err)
        rows.append({"name": name, "expected": exp, "got": got, "abs_err": err})
    return rows, worst


def _table(rows, width: int) -> None:
    print(f"{'anchor'.ljust(width)}  {'published':>12}  {'computed':>12}  {'|err|':>10}")
    print("-" * (width + 40))
    for r in rows:
        print(f"{r['name'].ljust(width)}  {r['expected']:12.6f}  {r['got']:12.6f}  {r['abs_err']:10.6f}")
    print("-" * (width + 40))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true", help="emit machine-readable output")
    p.add_argument("--quick", action="store_true", help="fewer Monte Carlo runs")
    p.add_argument("--runs", type=int, default=None)
    p.add_argument("--explore", action="store_true",
                   help="also run the configurations that are not recoverable")
    args = p.parse_args(argv)

    runs = args.runs or (20 if args.quick else 200)

    gated = {}
    for fn in GATED.values():
        gated |= fn(runs=runs)

    rows, worst = compare(gated, gated_anchors())

    exploratory_rows, exploratory = [], {}
    if args.explore:
        for fn in EXPLORATORY.values():
            exploratory |= fn(runs=runs)
        exploratory_rows, _ = compare(exploratory, exploratory_anchors())

    if args.json:
        print(json.dumps({
            "runs": runs,
            "repro_max_abs_err": worst,
            "n_gating_anchors": len(rows),
            "anchors": rows,
            "exploratory": [{"name": k, "value": v} for k, v in sorted(exploratory.items())],
        }, indent=1))
        return 0

    width = max((len(r["name"]) for r in rows), default=10)
    _table(rows, width)
    print(f"repro_max_abs_err = {worst:.6f}   runs={runs}   anchors={len(rows)}")

    if args.explore:
        print("\nEXPLORATORY -- driver configs absent from the reference materials,")
        print("reconstructed from prose.  Not comparable; shown for shape only.")
        width = max((len(r["name"]) for r in exploratory_rows), default=10)
        _table(exploratory_rows, width)
        prov = {k: v for k, v in exploratory.items() if not k.startswith("exp3.")
                and not k.startswith("exp4.")}
        if prov:
            print("\n  reconstructed reference lines:")
            for k, v in sorted(prov.items()):
                tail = ""
                if ".b" in k:
                    exp = EXP5_MEASURED.get(int(k.rsplit("b", 1)[-1]))
                    tail = f"   (published {exp:+.2f})" if exp is not None else ""
                print(f"    {k:24} {v:+9.4f}{tail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
