"""E77 -- is the project reproducible across runs, and across thread counts?  The network line is not; the analytic line is.

`e54` established that the `naive` arm is bit-identical across runs, which made it the project's
determinism control and a free way to accumulate seeds; the census verified agreement **by value**
between every artifact pair it grouped.  That check is necessary and it was not sufficient: it held
every artefact's *environment* fixed, and the census never varied one.

The discovery that forced this script: `e61` (launched with no `OMP_NUM_THREADS`) and `e68` (launched
with `OMP_NUM_THREADS=4`) are the same configuration in **every** field except `repeats` -- 5 against
16 -- and their `naive` arms disagree from the very first replicate, where a run of 5 and a run of 16
should share their first five exactly.

Two probes, because the project has two substrates and they need not behave alike:

* **the network line** (`experiments.e8_rate_network`, torch): `repeats` is inert, the thread count is
  not, so the same command under a different `OMP_NUM_THREADS` trains to a different result;
* **the analytic line** (`experiments.e12_control_spread`, numpy: the Kalman/RTS oracle and the
  projection arithmetic): this is the substrate every reproduction claim in the paper rests on -- "the
  cs = 800 column reproduces bit-for-bit" -- so whether *it* is thread-sensitive decides how much of the
  record is at risk.

    python -m experiments.e77_thread_determinism_probe
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

#: Small enough to run three times in a couple of minutes, but with `iters` large enough that the
#: recurrent body has actually moved off its initialisation -- at `iters` 2 the arm is near chance and
#: every replicate looks alike, which would hide a difference rather than show one.
BASE = ["-m", "experiments.e8_rate_network", "--circuit-size", "300", "--iters", "100",
        "--methods", "naive", "--shared-head", "--readout-size", "32", "--input-overlap", "0.0",
        "--classes", "4", "--noise", "1.0", "--support", "80"]

#: The analytic probe: `e12` exercises the oracle, the projection arithmetic and the matched random
#: control, at a size that runs in seconds.
ANALYTIC = ["-m", "experiments.e12_control_spread", "--circuit-size", "300", "--support", "30",
            "--seeds", "2", "--draws", "2", "--column", "cell_type", "--min-size", "4"]


def run(args: list[str], env_overrides: dict, out: Path, label: str) -> dict:
    env = dict(os.environ)
    for k, v in env_overrides.items():
        if v is None:
            env.pop(k, None)
        else:
            env[k] = v
    cmd = [sys.executable, "-u", *args, "--json-out", str(out)]
    print(f"   running {label} ...", flush=True)
    subprocess.run(cmd, check=True, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    with open(out, encoding="utf-8") as fh:
        return json.load(fh)


def run_network(repeats: int, threads: int | None, out: Path) -> list[float]:
    env = {"OMP_NUM_THREADS": (None if threads is None else str(threads))}
    d = run([*BASE, "--repeats", str(repeats)], env, out,
            f"network repeats={repeats}, OMP_NUM_THREADS={threads}")
    return [r["final_accuracy"] for r in d["methods"]["naive"]["replicates"]]


def run_analytic(threads: int | None, out: Path) -> dict:
    env = {"OMP_NUM_THREADS": (None if threads is None else str(threads))}
    d = run(ANALYTIC, env, out, f"analytic, OMP_NUM_THREADS={threads}")
    return {"biological_excess_mean": d["biological"]["excess_mean"],
            "biological_excess_per_seed": d["biological"].get("excess_per_seed"),
            "control_means": d["control_means"],
            "control_sd_across_draws": d["control_sd_across_draws"],
            "delta": d["delta"]}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-out", default="runs/e77_thread_determinism_probe.json")
    ap.add_argument("--skip-network", action="store_true")
    args = ap.parse_args()

    tmp = Path(tempfile.mkdtemp(prefix="e77_"))
    out: dict = {"network_command": " ".join(BASE), "analytic_command": " ".join(ANALYTIC)}

    if not args.skip_network:
        print("three runs of one network configuration, one variable at a time\n")
        a = run_network(3, None, tmp / "a.json")
        b = run_network(4, None, tmp / "b.json")
        c = run_network(3, 4, tmp / "c.json")

        print()
        print("=" * 100)
        print("1. IS `repeats` INERT?")
        print("=" * 100)
        print(f"   repeats 3, default threads: {[round(x, 6) for x in a]}")
        print(f"   repeats 4, default threads: {[round(x, 6) for x in b]}")
        repeats_inert = a == b[:3]
        print(f"   the first three agree: ** {repeats_inert} **")
        print("   -> " + ("`repeats` changes only how many replicates exist, not their values"
                          if repeats_inert else
                          "`repeats` CHANGES the replicate values, which nothing in the code says"))

        print()
        print("=" * 100)
        print("2. IS THE THREAD COUNT INERT, ON THE NETWORK LINE?")
        print("=" * 100)
        print(f"   repeats 3, default threads:   {[round(x, 6) for x in a]}")
        print(f"   repeats 3, OMP_NUM_THREADS=4: {[round(x, 6) for x in c]}")
        threads_inert = a == c
        print(f"   identical: ** {threads_inert} **")
        print(f"   distinct accuracy values shared between them: {len(set(a) & set(c))} of {len(set(a))}")
        print("   -> " + ("the thread count is inert here" if threads_inert else
                          "THE THREAD COUNT IS NOT INERT: the same command under a different OMP setting "
                          "trains to a different result"))
        out.update(network=dict(repeats_inert=bool(repeats_inert), threads_inert=bool(threads_inert),
                                repeats3_default=a, repeats4_default=b, repeats3_omp4=c))

    print()
    print("=" * 100)
    print("3. IS THE THREAD COUNT INERT, ON THE ANALYTIC LINE?")
    print("=" * 100)
    print("   this is the substrate every reproduction claim rests on, so the answer decides how")
    print("   much of the record is at risk rather than just the network line's\n")
    a2 = run_analytic(None, tmp / "an_a.json")
    b2 = run_analytic(4, tmp / "an_b.json")
    for k in ("biological_excess_mean", "control_sd_across_draws", "delta"):
        same = a2[k] == b2[k]
        print(f"   {k:<28} default {a2[k]!r:>24}   OMP=4 {b2[k]!r:>24}   identical {same}")
    same_ps = a2["biological_excess_per_seed"] == b2["biological_excess_per_seed"]
    same_cm = a2["control_means"] == b2["control_means"]
    print(f"   {'per-seed excesses (2 seeds)':<28} identical ** {same_ps} **")
    print(f"   {'control means (2 draws)':<28} identical ** {same_cm} **")
    analytic_inert = all(a2[k] == b2[k] for k in
                         ("biological_excess_mean", "control_sd_across_draws", "delta")) and same_ps and same_cm
    print(f"\n   -> the analytic path is {'THREAD-INERT on this probe' if analytic_inert else 'THREAD-SENSITIVE'}")
    out["analytic"] = dict(a=a2, b=b2, inert=bool(analytic_inert))

    print()
    print("=" * 100)
    print("4. WHAT EACH ANSWER IMPLIES")
    print("=" * 100)
    if out.get("network", {}).get("repeats_inert") and not out.get("network", {}).get("threads_inert"):
        print("   The network line is deterministic given an environment and not across environments.")
        print("   `e54`'s census is not wrong -- its pairs really do agree by value -- but its scope is")
        print("   narrower than it says: the `naive` arm is a determinism control **within a thread")
        print("   setting**, and no artifact records one. The consequence for `e61`/`e68` is that the")
        print("   16-replicate run is a **separate sample of the same configuration**, not an extension")
        print("   of the 5-replicate one -- so it answers 'does the effect hold at sixteen' but not")
        print("   'does the effect shrink as n grows', which `e46`'s nested comparison answered.")
    if out.get("analytic", {}).get("inert"):
        print("\n   The analytic line is unaffected on this probe, so the reproductions the paper leans")
        print("   on -- the cs = 800 column to six decimals, `e65`'s realization 0 against `e48` -- are")
        print("   not explained away by an environment change. One probe at one size is a demonstration")
        print("   and not a guarantee: numpy's own reductions are still order-dependent in principle.")
    else:
        print("\n   The analytic line IS thread-sensitive, which puts every cross-artifact numerical")
        print("   comparison in the project at risk rather than just the network line's.")

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()

