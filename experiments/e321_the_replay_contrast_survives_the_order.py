"""E321 -- the replay-over-penalty contrast under the order inversion: the sign survives and the size does not.

`e276` read the line's **strongest method contrast** -- `replay` against the penalty arms, paired over the same
forty replicates -- and found it on accuracy at 3.30, 9.09 and 11.84 sigma and on forgetting at up to 8.42, every
one of its contrasts favouring replay. Eleven fires of audit have left the **basis** contrast a null; the method
contrast is the one that has always resolved. **Nothing has ever varied a knob under it.**

`e315` to `e319` built the knob: the corpus now holds two orders of the assembly suite at this circuit, with all five
arms trained on the same seeds. `e317` used those runs to show that the **block-against-diagonal** comparison flips
sign with the order. This unit asks the same of `replay`'s three contrasts, which are the ones the line quotes.

Four claims, registered before the reading below was taken:

- **T1 -- the two runs are one configuration in two orders.** Same circuit, same read-out subset, same seeds, one task
  list the other reversed. **Falsifier**: a differing circuit or read-out, or a list that is not a reversal.
- **T2 -- and `replay` beats every penalty arm on accuracy in both orders.** All six contrasts (three arms, two
  orders) favour `replay`, each resolved at two sigma. **Falsifier**: one that does not.
- **T3 -- and on forgetting likewise.** All six favour `replay` again, since a lower forgetting is the better one.
  **Falsifier**: one that does not.
- **T4 -- and the size does not survive: the magnitudes are order-dependent.** At least one contrast's magnitude
  differs between the two orders by a factor of **2 or more**. **Falsifier**: every contrast within a factor of two.

**What it cannot do.** *One configuration and five replicates per arm*, so the sigmas are this circuit's and not
`e276`'s: that unit's 3.30, 9.09 and 11.84 sigma are the read-out-32 frozen-bias family at forty replicates, and
nothing here re-measures them. *The two runs are not the same trained models*, since the sequence changes the
gradients, so a magnitude difference is the order's effect on the whole trajectory. *Six contrasts over three arms
are not independent*: they share `replay`'s replicates, so a single unusual `replay` arm moves all six together. *And
T4's factor of two is a convention*: what the run shows is a factor of about three on `ewc-block` and much less on
the other two.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
FORWARDS = RUNS / "e317_five_as_built.json"
BACKWARDS = RUNS / "e317_five_reverse.json"
#: The arm the contrast is about, and the three it is drawn against.
REPLAY = "replay"
PENALTIES = ("ewc", "ewc-block", "ewc-block-rand")
#: T2's and T3's threshold, and T4's factor.
SIGMA = 2.0
FACTOR = 2.0
CLAIMS = (
    ("T1", "the two runs are one configuration in two orders",
     "Same circuit, same read-out subset, same seeds, and one task list the other reversed",
     "falsifier: a differing circuit or read-out, or a list that is not a reversal"),
    ("T2", "and `replay` beats every penalty arm on accuracy in both orders",
     f"All six accuracy contrasts favour `{REPLAY}`, each resolved at {SIGMA} sigma",
     "falsifier: one that does not"),
    ("T3", "and on forgetting likewise",
     f"All six forgetting contrasts favour `{REPLAY}`, each resolved at {SIGMA} sigma",
     "falsifier: one that does not"),
    ("T4", "and the size does not survive: the magnitudes are order-dependent",
     f"At least one contrast's magnitude differs between the orders by a factor of {FACTOR} or more",
     "falsifier: every contrast within a factor of two"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def paired(one: list[float], two: list[float], higher_is_better: bool) -> dict:
    diffs = [a - b for a, b in zip(one, two)]
    if len(diffs) < 2:
        return {"n": len(diffs), "delta": None, "sigma": None, "favours_replay": None}
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / math.sqrt(len(diffs))
    sigma = abs(mean) / sem if sem else float("inf")
    #: the delta is replay minus the penalty arm, so replay is ahead when a *higher* accuracy or a *lower*
    #: forgetting is on its side
    return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": sigma,
            "favours_replay": (mean > 0) if higher_is_better else (mean < 0)}


def contrasts(run: dict) -> dict:
    out = {}
    for other in PENALTIES:
        a, b = run["methods"].get(REPLAY), run["methods"].get(other)
        if not isinstance(a, dict) or not isinstance(b, dict):
            continue
        for metric, higher in (("final_accuracy", True), ("mean_forgetting", False)):
            out[f"{REPLAY}-{other}/{metric}"] = paired(
                [r[metric] for r in a["replicates"]], [r[metric] for r in b["replicates"]], higher)
    return out


def reading(fwd: Path = FORWARDS, bwd: Path = BACKWARDS) -> dict:
    a, b = load(fwd), load(bwd)
    if not a or not b:
        return {"runs": 0}
    names_a = [str(t["name"]) for t in a["tasks"]]
    names_b = [str(t["name"]) for t in b["tasks"]]
    ca, cb = contrasts(a), contrasts(b)
    keys = sorted(set(ca) & set(cb))
    return {"runs": 2, "circuits": [a.get("circuit"), b.get("circuit")],
            "same_circuit": a.get("circuit") == b.get("circuit"),
            "readout": [a.get("readout", {}).get("subset_sha1"), b.get("readout", {}).get("subset_sha1")],
            "orders": [a.get("config", {}).get("task_order"), b.get("config", {}).get("task_order")],
            "reversed_names": names_b == names_a[::-1] and names_a != names_b,
            "n": len(a["methods"][REPLAY]["replicates"]),
            "contrasts": {k: {"forward": ca[k], "backward": cb[k],
                              "ratio": (abs(ca[k]["delta"]) / abs(cb[k]["delta"]))
                              if cb[k]["delta"] else None} for k in keys},
            #: **The check the first version of this unit did not make.** The replicates carry `method`, `losses`,
            #: `final_accuracy` and the rest, and **no seed field** -- so a comparison of `r.get("seed")` across
            #: the two runs was `[None] * n == [None] * n` and could not fail, whatever the runs' seeds were.
            #: `e324` found it while writing the same check for its own pair of runs. What is recorded is the
            #: config's `seed0` and `repeats`, which is what identifies the seed schedule, so those are compared
            #: and the replicate counts are compared with them.
            "seeds": {"seed0": [a.get("config", {}).get("seed0"), b.get("config", {}).get("seed0")],
                      "repeats": [a.get("config", {}).get("repeats"), b.get("config", {}).get("repeats")]},
            "same_seeds": (a.get("config", {}).get("seed0") is not None
                           and a.get("config", {}).get("seed0") == b.get("config", {}).get("seed0")
                           and a.get("config", {}).get("repeats") == b.get("config", {}).get("repeats")
                           and len(a["methods"][REPLAY]["replicates"])
                           == len(b["methods"][REPLAY]["replicates"]))}


def judge(r: dict) -> list[dict]:
    if not r.get("runs"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the two runs are not both on disk"}
                for c in CLAIMS]
    out = [{"id": "T1", "measured": f"circuits {r['circuits']}, read-out {r['readout']}, orders {r['orders']}, "
                                    f"reversed task lists {r['reversed_names']}, same seeds {r['same_seeds']}, "
                                    f"{r['n']} replicates per arm",
            "verdict": "MET -- one configuration in two orders" if
            r["same_circuit"] and r["readout"][0] == r["readout"][1] and r["reversed_names"] and r["same_seeds"]
            else f"FALSIFIER FIRED -- {r['circuits']}, {r['readout']}, {r['reversed_names']}"}]

    for cid, metric in (("T2", "final_accuracy"), ("T3", "mean_forgetting")):
        rows = [(k, v) for k, v in r["contrasts"].items() if k.endswith(metric)]
        against = [(k, v) for k, v in rows if not v["forward"]["favours_replay"] or not v["backward"]["favours_replay"]]
        detail = "; ".join(f"{k.split('/')[0]} fwd {v['forward']['delta']:+.4f} at {v['forward']['sigma']:.2f}, "
                           f"bwd {v['backward']['delta']:+.4f} at {v['backward']['sigma']:.2f}"
                           for k, v in rows)
        weak = [(k, v) for k, v in rows
                if min(v["forward"]["sigma"], v["backward"]["sigma"]) < SIGMA]
        out.append({"id": cid, "measured": f"{len(rows) - len(against)} of {len(rows)} {metric} contrasts favour "
                                           f"`{REPLAY}` in both orders; {len(weak)} fall below {SIGMA} sigma in "
                                           f"one of them: {detail}",
                    "verdict": f"MET -- `{REPLAY}` is ahead on {metric} in every contrast and both orders"
                    if rows and not against and not weak else
                    f"FALSIFIER FIRED -- {[k for k, _ in against]} against, {[k for k, _ in weak]} unresolved"})

    big = [(k, v) for k, v in r["contrasts"].items() if v["ratio"] is not None and v["ratio"] >= FACTOR]
    detail = "; ".join(f"{k} {v['forward']['delta']:+.4f} against {v['backward']['delta']:+.4f} (x{v['ratio']:.2f})"
                       for k, v in sorted(r["contrasts"].items()))
    out.append({"id": "T4", "measured": f"{len(big)} of {len(r['contrasts'])} contrasts differ between the orders by "
                                        f"a factor of {FACTOR} or more: {detail}",
                "verdict": "MET -- the contrast's size is the order's even though its sign is not" if big else
                           f"FALSIFIER FIRED -- every contrast within a factor of {FACTOR}"})
    return out


def report(r: dict) -> int:
    print("== `replay` against the penalty arms, in two orders ==")
    print(f"   circuits {r['circuits']}, read-out {r['readout']}, orders {r['orders']}, same seeds {r['same_seeds']}")
    print(f"\n   {'contrast':38} {'fwd delta':>12} {'sigma':>7} {'bwd delta':>12} {'sigma':>7} {'ratio':>7}")
    for k, v in sorted(r["contrasts"].items()):
        print(f"   {k:38} {v['forward']['delta']:+12.5f} {v['forward']['sigma']:7.2f} "
              f"{v['backward']['delta']:+12.5f} {v['backward']['sigma']:7.2f} "
              f"{(v['ratio'] if v['ratio'] else float('nan')):7.2f}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e276` read this contrast as the line's strongest and nobody had varied a knob under it; `e317`")
    print("    showed the block-against-diagonal comparison flips sign with the order, and this asks the same)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--forward", type=Path, default=FORWARDS)
    ap.add_argument("--backward", type=Path, default=BACKWARDS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(args.forward, args.backward)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
