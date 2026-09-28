"""E276 -- replay against the penalty on the trained network: the line's strongest method contrast, and its own is a null.

The network line's headline is the **basis** contrast -- a biological anchoring partition against its size-matched
random control -- and eleven fires of audit have left it a null at every budget the corpus has. Beside it, every
forty-replicate run on the `r32` line trains a **replay** arm as well, and nobody has quoted the contrast between the
two *methods* the way the basis contrast is quoted: paired, over the same seeds, with a sigma.

Four artifacts carry both arms at forty replicates -- `e140_r32_methods_frozenbias_40reps`,
`e140_r32_methods_plastic_40reps`, `e153_r32_overlap1_methods_40reps` and its rerun
`e159_r32_overlap1_methods_rerun` -- so the contrast is a read of the register:

| configuration | replay minus `ewc-block`, accuracy | `ewc-block` minus `naive`, accuracy |
|---|---|---|
| frozen bias | **+0.0090 (3.30 sigma)** | +0.0040 (1.74 sigma) |
| plastic | **+0.0441 (9.09 sigma)** | +0.0043 (0.80 sigma) |
| overlap 1.0, lambda 1.0 | **+0.0618 (11.84 sigma)** | +0.0052 (0.81 sigma) |

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **V1 -- replay beats the penalty on accuracy at every one of the three configurations, and by a lot.** 3.30, 9.09
  and 11.84 sigma. **Falsifier**: a configuration at or under 2 sigma.
- **V2 -- and it does not pay for it in forgetting.** Replay forgets **less** in all three (-0.0044, -0.0607,
  -0.0549), resolved at two of them (8.42 and 7.12 sigma) and unresolved at the frozen-bias one (1.26 sigma).
  **Falsifier**: a configuration where replay forgets more.
- **V3 -- while the penalty's own gain over the naive baseline is unresolved on accuracy at all three.** 1.74, 0.80
  and 0.81 sigma. **Falsifier**: resolved at two or more of them.
- **V4 -- and the contrast is not a draw.** `e153` and `e159` are the same configuration run twice and carry
  **bit-identical** replicate lists, so the sigmas above are exact for that configuration rather than one sample of a
  distribution. **Falsifier**: any difference between the two.

**The scope is the substrate and the paper says why.** Its analytic line records the ordering *inverting* when the
unpenalised channel is removed from every arm -- `ewc` minus `replay` at 1.04 sigma there against 9.40 with the channel
free -- so "replay is the stronger method" is conditional on what the baseline is allowed, and nothing here says the
`r32` line's ordering travels to another substrate. What it does say is that **on this line the strongest method
contrast is replay against the penalty, while the line's headline contrast is a null**, and that the register has been
quoting the second and not the first.

**What it cannot do**: three configurations are not the line, and only the frozen-bias one carries five arms; the r32
line's readout is a 32-wide shared head, which is exactly the "channel" the paper's analytic caveat is about, so the
scope is narrow by construction; `frozen_bias` removes most of the training variance and so makes its contrast the
smallest of the three; the comparison is paired over seeds but the arms are trained in one process, so an arm-order
effect is not excluded; and no run is made.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: The configurations carrying the two arms at forty replicates, and the rerun that checks one of them.
RUNS = (("frozen bias", "runs/e140_r32_methods_frozenbias_40reps.json"),
        ("plastic", "runs/e140_r32_methods_plastic_40reps.json"),
        ("overlap 1.0", "runs/e153_r32_overlap1_methods_40reps.json"))
RERUN = ("runs/e153_r32_overlap1_methods_40reps.json", "runs/e159_r32_overlap1_methods_rerun.json")
METRICS = ("final_accuracy", "mean_forgetting")
#: The two method contrasts, and the baseline one.
CONTRASTS = (("replay", "ewc-block"), ("ewc-block", "naive"), ("replay", "naive"))
CLAIMS = (
    ("V1", "replay beats the penalty on accuracy at every configuration, and by a lot",
     "Every one of the three forty-replicate configurations reads at least 2 sigma for replay minus ewc-block on "
     "accuracy",
     "falsifier: a configuration at or under 2 sigma"),
    ("V2", "and it does not pay for it in forgetting",
     "Replay forgets less in every configuration, resolved at two of the three",
     "falsifier: a configuration where replay forgets more"),
    ("V3", "while the penalty's own gain over the baseline is unresolved on accuracy at all three",
     "ewc-block minus naive is under 2 sigma on accuracy at every configuration",
     "falsifier: resolved at two or more"),
    ("V4", "and the contrast is not a draw",
     "The configuration the corpus ran twice carries bit-identical replicate lists, so its sigma is exact",
     "falsifier: any difference between the two runs"),
)


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def paired(a: list[float], b: list[float]) -> dict:
    """The paired difference `a - b` over replicates, its sem and its sigma."""
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = sum(d) / n
    sd = math.sqrt(sum((v - mean) ** 2 for v in d) / (n - 1)) if n > 1 else float("nan")
    sem = sd / math.sqrt(n)
    return {"n": n, "delta": mean, "sem": sem, "sigma": (abs(mean) / sem if sem else float("inf"))}


def contrasts(d: dict, metric: str) -> dict:
    arms = d["methods"]
    return {f"{x}-{y}": paired([r[metric] for r in arms[x]["replicates"]],
                               [r[metric] for r in arms[y]["replicates"]])
            for x, y in CONTRASTS if x in arms and y in arms}


def readings() -> dict:
    out = {}
    for label, path in RUNS:
        d = load(path)
        if d is None or "replay" not in (d.get("methods") or {}):
            continue
        out[label] = {"artifact": Path(path).name, "n": len(d["methods"]["replay"]["replicates"]),
                      "contrasts": {m: contrasts(d, m) for m in METRICS},
                      "config": {k: d["config"].get(k) for k in ("circuit_size", "lam", "readout_size",
                                                                "shared_head", "frozen_bias", "input_overlap")}}
    return out


def rerun_check() -> dict | None:
    a, b = load(RERUN[0]), load(RERUN[1])
    if a is None or b is None:
        return None
    return {"same_replicates": a["methods"] == b["methods"],
            "configs_differ_in": [k for k in set(a["config"]) | set(b["config"])
                                  if a["config"].get(k) != b["config"].get(k)]}


def judge(rows: dict, rerun: dict | None) -> list[dict]:
    out: list[dict] = []
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the forty-replicate artifacts are absent"}
                for c in CLAIMS]

    v1 = {label: r["contrasts"]["final_accuracy"]["replay-ewc-block"]["sigma"] for label, r in rows.items()}
    out.append({"id": "V1", "measured": "; ".join(f"{k}: {v:.2f} sigma" for k, v in sorted(v1.items())),
                "verdict": "MET -- replay wins on accuracy everywhere, by 3.3 to 11.8 sigma"
                if all(v > 2 for v in v1.values()) else f"FALSIFIER FIRED -- {v1}"})

    forget = {label: r["contrasts"]["mean_forgetting"]["replay-ewc-block"] for label, r in rows.items()}
    worse = [k for k, c in forget.items() if c["delta"] > 0]
    resolved = [k for k, c in forget.items() if c["delta"] < 0 and c["sigma"] > 2]
    out.append({"id": "V2", "measured": "; ".join(f"{k}: {c['delta']:+.4f} ({c['sigma']:.2f} sigma)"
                                                  for k, c in sorted(forget.items())),
                "verdict": "MET -- replay forgets less everywhere, resolved at two of three"
                if not worse and len(resolved) >= 2 else
                f"FALSIFIER FIRED -- it forgets more at {worse}"})

    pen = {label: r["contrasts"]["final_accuracy"]["ewc-block-naive"]["sigma"] for label, r in rows.items()}
    resolved_pen = [k for k, v in pen.items() if v >= 2.0]
    out.append({"id": "V3", "measured": "; ".join(f"{k}: {v:.2f} sigma" for k, v in sorted(pen.items())),
                "verdict": "MET -- the penalty's own gain is unresolved on accuracy everywhere"
                if not resolved_pen else f"FALSIFIER FIRED -- resolved at {resolved_pen}"})

    if rerun is None:
        out.append({"id": "V4", "measured": "", "verdict": "REFUSED -- the rerun pair is absent"})
    else:
        out.append({"id": "V4", "measured": f"the rerun carries bit-identical replicate lists: "
                                            f"{rerun['same_replicates']}; the two configurations differ in "
                                            f"{rerun['configs_differ_in']}",
                    "verdict": "MET -- the contrast's sigma is exact for that configuration" if rerun["same_replicates"]
                    else "FALSIFIER FIRED -- the rerun differs, so the sigma is a draw"})
    return out


def report(rows: dict, rerun: dict | None) -> int:
    print("== the three forty-replicate configurations, replay against the penalty ==")
    for label, r in sorted(rows.items()):
        print(f"\n   {label}  ({r['artifact']}, {r['n']} replicates)")
        print("      " + ", ".join(f"{k}={v}" for k, v in r["config"].items()))
        for metric in METRICS:
            print(f"      {metric}")
            for name, c in sorted(r["contrasts"][metric].items()):
                print(f"         {name:24} delta {c['delta']:+.4f}  sem {c['sem']:.4f}  {c['sigma']:5.2f} sigma")

    print("\n== the registered claims, V1-V4 ==")
    j = judge(rows, rerun)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (the line's headline contrast is the biological anchoring and it is a null; the strongest contrast on "
          "the same")
    print("    runs is the method one, and the register has been quoting the first and not the second)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    rows = readings()
    if not rows:
        raise SystemExit("need the forty-replicate artifacts -- they are what carries both arms")
    rerun = rerun_check()
    if args.json_out:
        write_json(args.json_out, {"runs": [list(r) for r in RUNS], "contrasts": [list(c) for c in CONTRASTS],
                                   "readings": rows, "rerun": rerun, "claims": judge(rows, rerun)})
        print(f"wrote {args.json_out}")
    return report(rows, rerun)


if __name__ == "__main__":
    sys.exit(main())
