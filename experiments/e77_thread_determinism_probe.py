"""E77 -- is the rate-network benchmark reproducible across runs, and across thread counts?

`e54` established that the `naive` arm is bit-identical across runs, which made it the project's
determinism control and a free way to accumulate seeds; the census verified agreement **by value**
between every artifact pair it grouped.  That check is necessary and it was not sufficient: it held
every artefact's *environment* fixed, and the census never varied one.

The discovery that forced this script: `e61` (launched with no `OMP_NUM_THREADS`) and `e68` (launched
with `OMP_NUM_THREADS=4`) are the same configuration in **every** field except `repeats` -- 5 against
16 -- and their `naive` arms disagree from the very first replicate, where a run of 5 and a run of 16
should share their first five exactly.

So there are two candidate explanations and this script separates them by running the smallest
configuration that shows any variation:

* **`repeats` is not inert** -- the number of replicates changes the replicates themselves;
* **the thread count is not inert** -- PyTorch's CPU reductions are order-dependent, so a different
  thread count gives a different training trajectory.

Three runs, one variable at a time:

    repeats 3, default threads      |
    repeats 4, default threads      |  must agree on their first three replicates if `repeats` is inert
    repeats 3, OMP_NUM_THREADS=4    |  must agree with the first if the thread count is inert

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


def run(repeats: int, threads: int | None, out: Path) -> list[float]:
    env = dict(os.environ)
    if threads is None:
        env.pop("OMP_NUM_THREADS", None)
    else:
        env["OMP_NUM_THREADS"] = str(threads)
    cmd = [sys.executable, "-u", *BASE, "--repeats", str(repeats), "--json-out", str(out)]
    print(f"   running repeats={repeats}, OMP_NUM_THREADS={threads} ...", flush=True)
    subprocess.run(cmd, check=True, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    with open(out, encoding="utf-8") as fh:
        d = json.load(fh)
    return [r["final_accuracy"] for r in d["methods"]["naive"]["replicates"]]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-out", default="runs/e77_thread_determinism_probe.json")
    args = ap.parse_args()

    tmp = Path(tempfile.mkdtemp(prefix="e77_"))
    print("three runs of the same configuration, one variable at a time\n")
    a = run(3, None, tmp / "a.json")
    b = run(4, None, tmp / "b.json")
    c = run(3, 4, tmp / "c.json")

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
    print("2. IS THE THREAD COUNT INERT?")
    print("=" * 100)
    print(f"   repeats 3, default threads:   {[round(x, 6) for x in a]}")
    print(f"   repeats 3, OMP_NUM_THREADS=4: {[round(x, 6) for x in c]}")
    threads_inert = a == c
    print(f"   identical: ** {threads_inert} **")
    overlap = len(set(a) & set(c))
    print(f"   distinct accuracy values shared between them: {overlap} of {len(set(a))}")
    print("   -> " + ("the thread count is inert here" if threads_inert else
                      "THE THREAD COUNT IS NOT INERT: the same command under a different OMP setting "
                      "trains to a different result"))

    print()
    print("=" * 100)
    print("3. WHAT EACH ANSWER IMPLIES FOR THE PROJECT")
    print("=" * 100)
    if repeats_inert and not threads_inert:
        print("   `e54`'s census is not wrong -- its pairs really do agree by value -- but its scope is")
        print("   narrower than it says: the `naive` arm is a determinism control **within a thread")
        print("   setting**, not across environments. Every artefact comparison the project has made")
        print("   inherited an environment it never recorded, and `OMP_NUM_THREADS` was set on some of")
        print("   these runs and not others. The consequence for `e61`/`e68` is that the 16-replicate run")
        print("   is a **separate sample of the same configuration**, not an extension of the 5-replicate")
        print("   one -- so it answers 'does the effect hold at sixteen' but not 'does the effect shrink")
        print("   as n grows', which is the question `e46`'s nested comparison answered.")
    print("   Two things the probe does NOT show: whether the *analytic* (numpy) experiments in this")
    print("   project are also thread-sensitive -- `e65`'s realization 0 reproduced `e48`'s published")
    print("   value to six decimals under a different OMP setting, which suggests they are not -- and")
    print("   whether the sensitivity is the thread count itself or something correlated with it.")

    out = {"repeats_inert": bool(repeats_inert), "threads_inert": bool(threads_inert),
           "repeats3_default": a, "repeats4_default": b, "repeats3_omp4": c,
           "command": " ".join(BASE)}
    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
