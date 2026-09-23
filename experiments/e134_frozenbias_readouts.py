"""E134 -- the frozen-bias effect at each read-out, against its own 40-replicate plastic comparator.

`e125` measured one read-out: at **read-out 32**, holding the 800 per-neuron offsets at their initialisation takes
the naive forgetting from **+0.0750 to +0.0227** — **70%** removed, **5.90σ** over forty paired seeds — and raises
accuracy. Its own registration said in advance that read-out 32 was chosen **because it maximises the chance of
seeing the effect**, so the remaining question is generality, and `e134` runs the same arm at read-out 128 and
1307 against the plastic comparators already on disk.

    python -m experiments.e134_frozenbias_readouts --json-out runs/e134_readouts.json

**Two measures, and they do not have to agree.** The effect can be stated **absolutely** (the paired difference
in forgetting) or **as a fraction of the comparator's level**, and because the comparators' levels differ across
read-outs by more than the effects do, the two can order in opposite directions. `e123`'s cross-unit sd ratio and
rule 35's "factor below chance" were the same problem twice; this is its third costume, so **both are printed for
every read-out and neither is called "the" effect**.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

# (read-out label, the --frozen-bias arm, its 40-replicate plastic comparator)
DEFAULT_ARMS = [("32", "runs/e125_r32_frozenbias.json", "runs/e116_r32_40reps.json"),
                ("128", "runs/e134_r128_frozenbias.json", "runs/e116_r128_40reps.json"),
                ("1307", "runs/e134_r1307_frozenbias.json", "runs/e116_r1307_40reps.json")]


def forgetting(path: Path) -> np.ndarray:
    m = json.loads(Path(path).read_text(encoding="utf-8"))["methods"]["naive"]
    return np.array([r["mean_forgetting"] for r in m["replicates"]])


def one(label: str, arm: Path, comp: Path) -> dict:
    fb, nv = forgetting(arm), forgetting(comp)
    if len(fb) != len(nv):
        return {"readout": label, "usable": False,
                "reason": f"{len(fb)} replicates against {len(nv)}"}
    d = fb - nv
    sem = float(d.std(ddof=1) / np.sqrt(len(d)))
    out = {"readout": label, "usable": True, "n": len(d),
           "plastic_mean": float(nv.mean()), "frozen_bias_mean": float(fb.mean()),
           "absolute_difference": float(d.mean()), "sem": sem,
           "sigma": float(abs(d.mean()) / sem) if sem else float("nan"),
           "n_negative": int((d < 0).sum()),
           "fraction_removed": float(1.0 - fb.mean() / nv.mean()),
           "plastic_sd": float(nv.std(ddof=1)), "frozen_bias_sd": float(fb.std(ddof=1))}
    m = json.loads(Path(arm).read_text(encoding="utf-8"))["methods"]["naive"]
    out["accuracy_plastic"] = float(np.mean([r["final_accuracy"] for r in
                                             json.loads(Path(comp).read_text(encoding="utf-8"))["methods"]["naive"]["replicates"]]))
    out["accuracy_frozen_bias"] = float(np.mean([r["final_accuracy"] for r in m["replicates"]]))
    # C0a -- the flag's own control, per read-out
    reps = m["replicates"]
    out["bias_frozen_everywhere"] = all(all(b["step"] == 0.0 and b["from_zero"] == 0.0
                                            for b in r["bias_norms"]) for r in reps)
    out["theta_moves_everywhere"] = all(all(x > 0 for x in r["theta_drift"]) for r in reps)
    out["min_theta_drift"] = float(min(min(r["theta_drift"]) for r in reps))
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--arm", nargs=3, action="append", metavar=("READOUT", "FROZEN_BIAS", "PLASTIC"),
                   default=None, help="override the defaults")
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    arms = [tuple(a) for a in args.arm] if args.arm else DEFAULT_ARMS
    rows = []
    for label, a, c in arms:
        if not Path(a).is_file() or not Path(c).is_file():
            rows.append({"readout": label, "usable": False,
                         "reason": f"{'arm' if not Path(a).is_file() else 'comparator'} not on disk yet"})
            continue
        rows.append(one(label, Path(a), Path(c)))

    print(f"{'read-out':>9} {'plastic':>9} {'frozen':>9} {'abs diff':>10} {'sigma':>7} {'neg':>6} "
          f"{'fraction':>9} {'sd plast':>9} {'sd froz':>8} {'rel plast':>10} {'rel froz':>9}  {'C0a':>4}")
    for r in rows:
        if not r["usable"]:
            print(f"{r['readout']:>9}   -- {r['reason']}")
            continue
        rel_p = r['plastic_sd'] / abs(r['plastic_mean'])
        rel_f = r['frozen_bias_sd'] / abs(r['frozen_bias_mean'])
        print(f"{r['readout']:>9} {r['plastic_mean']:9.4f} {r['frozen_bias_mean']:9.4f} "
              f"{r['absolute_difference']:10.4f} {r['sigma']:7.2f} {r['n_negative']:3d}/{r['n']:<2d} "
              f"{100 * r['fraction_removed']:8.0f}% {r['plastic_sd']:9.4f} {r['frozen_bias_sd']:8.4f} "
              f"{100 * rel_p:9.0f}% {100 * rel_f:8.0f}%  "
              f"{'both' if r['bias_frozen_everywhere'] and r['theta_moves_everywhere'] else '**FAIL**':>4}")
    usable = [r for r in rows if r["usable"]]
    if len(usable) > 1:
        print("\n   the two orderings, which need not agree because the comparators' levels differ:")
        print("     by ABSOLUTE difference : " + " > ".join(
            f"{r['readout']} ({abs(r['absolute_difference']):.4f})"
            for r in sorted(usable, key=lambda r: -abs(r["absolute_difference"]))))
        print("     by FRACTION removed    : " + " > ".join(
            f"{r['readout']} ({100 * r['fraction_removed']:.0f}%)"
            for r in sorted(usable, key=lambda r: -r["fraction_removed"])))
    print("\nC0a columns: 'both' means every bias_norms entry is exactly 0.0 AND theta_drift is non-zero"
          "\neverywhere -- the first half alone would pass for a run that froze the whole body.")
    if args.json_out:
        write_json(args.json_out, {"rows": rows})
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
